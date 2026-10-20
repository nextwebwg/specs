import {test} from 'node:test';
import assert from 'node:assert/strict';
import {parse,serialize} from 'parse5';
import {PlacementParser,parsePlacement} from './placement.mjs';

const cases = [
  ['nested same-name wrappers','<nav><nav/></nav><p>outside</p>','<nav><nav></nav></nav><p>outside</p>'],
  ['reconstructed formatting','<h2><small/></h2><h1>tail</h1>','<h2><small></small></h2><h1>tail</h1>'],
  ['nested formatting','<p><strong><em/><span>tail</span></strong></p>','<p><strong><em></em><span>tail</span></strong></p>'],
  ['table followed by paragraph','<table/><p>tail</p>','<table></table><p>tail</p>'],
  ['empty table cell','<table><tr><td/><td>two</td></tr></table>','<table><tr><td></td><td>two</td></tr></table>'],
  ['empty table row','<table><tbody><tr/><tr><td>two</td></tr></tbody></table>','<table><tbody><tr></tr><tr><td>two</td></tr></tbody></table>'],
  ['pre LF','<pre/>\n<span>tail</span>','<pre></pre>\n<span>tail</span>'],
  ['pre CRLF','<pre/>\r\n<span>tail</span>','<pre></pre>\r\n<span>tail</span>'],
  ['listing LF','<listing/>\n<span>tail</span>','<listing></listing>\n<span>tail</span>'],
  ['hidden attribute','<div hidden/><span>tail</span>','<div hidden></div><span>tail</span>'],
  ['inert attribute','<div inert/><span>tail</span>','<div inert></div><span>tail</span>'],
  ['disabled attribute','<button disabled/><span>tail</span>','<button disabled></button><span>tail</span>'],
  ['template-owned output','<template><small/><p>one</p></template>','<template><small></small><p>one</p></template>'],
];
for (const [name,source,expanded] of cases) test(`ordinary HTML placement: ${name}`,()=>{
  const full='<!doctype html><body>'+source;
  const result=parsePlacement(full);
  assert.equal(result.html,serialize(parse('<!doctype html><body>'+expanded)));
  assert.equal(result.parser.lastDecision.placement,'normal-html');
});
for(const source of [
  '<style/><img src=x onerror=attack()></style>',
  '<textarea/><img src=x onerror=attack()></textarea>',
  '<div/><svg></div><style><img src=x onerror=attack()></style></svg>',
  '<h1/><svg></h2><style><img src=x onerror=attack()></style></svg>',
  '<div><x-box/></div><svg></x-box><title><style></title><img src=x onerror=attack()></style>',
])test('source interpretation wins: '+source,()=>{
  const result=parsePlacement('<!doctype html><body>'+source);
  const images=[];const walk=n=>{if(n.tagName==='img')images.push(n);for(const c of n.childNodes??[])walk(c);if(n.content)walk(n.content);};walk(result.tree);
  assert.equal(images.length,0);
});
test('form and select retain their source-reader boundaries',()=>{
  for(const source of ['<form/><form><input></form>','<select/><select><option>x</option></select>','<select/><img src=x onerror=attack()>']) {
    assert.equal(parsePlacement(source).html,serialize(parse(source)));
  }
});
test('placement does not introduce a source-reader-ignored element',()=>{
  const source='<select><div/><img src=x onerror=attack()></select>';
  const result=parsePlacement(source);
  assert.doesNotMatch(result.html,/<img|<div/);
});
test('every split preserves the chosen final placement',()=>{
  for(const [,body]of cases){
    const source='<!doctype html><body>'+body;
    const expected=parsePlacement(source).html;
    for(let split=0;split<=source.length;split++){
      const parser=new PlacementParser();parser.write(source.slice(0,split));parser.output();parser.write(source.slice(split),true);
      assert.equal(serialize(parser.output()),expected,`${body} split ${split}`);
    }
  }
});

test('recovery placement keeps reconstructed nodes inside code/text owners unchanged',async()=>{
  const {auditPlacement}=await import('./audit-placement.mjs');
  const {defaultTreeAdapter,html}=await import('parse5');
  for(const [context,namespace,source]of [
    ['table',html.NS.HTML,'</math><b/><tr/></math></foreignObject><plaintext/><template></div><template/></b><button/>😀&amp;'],
    ['svg',html.NS.SVG,'text<tr/><x-box/><script><x-box/><math><foreignObject><b/><mtext><select/><td/><a/></foreignObject>\n</foreignObject></template></b><select/>'],
  ]){
    const parser=PlacementParser.getFragmentParser(defaultTreeAdapter.createElement(context,namespace,[]),{
      onCheckpoint(_t,p){auditPlacement(p);},
    });
    parser.write(source,true);
    auditPlacement(parser,parser.getFragment());
  }
});

test('form/select exceptions follow from source-reader-suppressed elements',()=>{
  for(const [source,expected]of [['<form/><form onsubmit="attack()"><input></form>','form'],['<select/><img src=x onerror=attack()>','img']]){
    const parser=new PlacementParser();
    parser.planner.canClose=token=>parser.marked.has(token.location?.startOffset)&&!parser.textStarts.has(token.location?.startOffset);
    parser.write(source,true);parser.output();
    assert.equal(parser.lastDecision.placement,'recognition-recovery');
    assert.equal(parser.lastDecision.reason,`unrecognized element ${expected}`);
  }
});

test('an invalid recovery projection cannot bypass source authorization',async()=>{
  const {auditPlacement}=await import('./audit-placement.mjs');
  const source='<div/><svg></div><style><img src=x onerror=attack()></style></svg>';
  const parser=new PlacementParser();
  const normalEligible=parser.eligible.bind(parser);
  parser.eligible=node=>node.tagName==='style'||normalEligible(node);
  parser.write(source,true);
  const output=parser.output();
  assert.equal(parser.lastDecision.placement,'source-recovery');
  assert.equal(serialize(output),serialize(parse(source)));
  auditPlacement(parser,parser.document,output);
});

test('select boundary retains a nested start ignored by source reading',()=>{
  const source='<select/><select><option>x</option></select>';
  const parser=new PlacementParser();
  parser.planner.canClose=token=>parser.marked.has(token.location?.startOffset)&&!parser.textStarts.has(token.location?.startOffset);
  parser.write(source,true);parser.output();
  assert.equal(parser.lastDecision.placement,'recognition-recovery');
  assert.equal(parser.lastDecision.reason,'unrecognized element select');
});
