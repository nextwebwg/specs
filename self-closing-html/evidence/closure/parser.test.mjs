import {test} from 'node:test';
import assert from 'node:assert/strict';
import {parse,serialize,parseFragment,defaultTreeAdapter,html} from 'parse5';
import {ClosureParser,parseClosure,VOID} from './parser.mjs';
const wrappers=[['body','',''],['div','<div>','</div>'],['bold','<b>','</b>'],['link','<a href="#">','</a>'],['form','<form>','</form>'],['list','<ul><li>','</li></ul>'],['table','<table>','</table>'],['row','<table><tbody><tr>','</tr></tbody></table>'],['cell','<table><tr><td>','</td></tr></table>'],['select','<select>','</select>']];
for(const tag of Object.values(html.TAG_NAMES).filter(name=>name!=='plaintext'))test(`explicit-pair behavior for ${tag}`,()=>{
 for(const scriptingEnabled of [true,false])for(const [name,open,close] of wrappers){
  const token=`<${tag} id="empty" />`;const source='<!doctype html><body>'+open+token+'<span>Following</span>'+close;
  // Foreign elements already self-close; void end tags are not an expansion.
  const expanded=VOID.has(tag)||tag==='svg'||tag==='math'?source:source.replace(token,`<${tag} id="empty"></${tag}>`);
  assert.equal(parseClosure(source,{scriptingEnabled}).html,serialize(parse(expanded,{scriptingEnabled})),`${name}, scripting ${scriptingEnabled}`);
 }
});
const witnesses=['<small/><span>tail</span>','<table/><span>tail</span>','<select/><span>tail</span>','<b><p/>text</b>','<svg><div/><span>tail</span>','<svg><foreignObject><small/>tail</foreignObject></svg>','<template/><span>tail</span>','<script/><p>tail</p>','<style/><p>tail</p>','<textarea/>\ntext','<plaintext/><p>tail</p>','<div hidden/><span>tail</span>','<div inert/><span>tail</span>','<div popover/><button>tail</button>','<div data-path=assets/>tail','<script>const s="<small/>";</script><small/>tail'];
for(const source of witnesses)test(`all two-chunk splits: ${source}`,()=>{
 const expected=parseClosure(source).html;
 for(let split=0;split<=source.length;split++){const p=new ClosureParser();p.write(source.slice(0,split));p.write(source.slice(split),true);assert.equal(serialize(p.document),expected,`split ${split}`);}
});
test('script checkpoint sees a closed script and pauses later source',()=>{
 const seen=[];const p=new ClosureParser({onScript(node,parser){seen.push({tag:node.tagName,html:serialize(parser.document)});parser.pause();}});
 p.write('<body><script src="example.js"/><p>later</p>',true);
 assert.equal(seen.length,1);assert.equal(seen[0].tag,'script');assert.doesNotMatch(seen[0].html,/<p>/);p.resume();assert.match(serialize(p.document),/<p>later<\/p>/);
});
for(const name of ['div','table','select','template'])test(`fragment context ${name}`,()=>{
 const ctx=defaultTreeAdapter.createElement(name,html.NS.HTML,[]);const source='<small/><span>tail</span>';
 assert.equal(parseClosure(source,{context:ctx}).html,serialize(parseFragment(ctx,'<small></small><span>tail</span>')));
});

test('plaintext slash closes before plaintext tokenization consumes following source',()=>{
 const result=parseClosure('<body><plaintext/><p>Following</p>');
 assert.match(result.html,/<plaintext><\/plaintext><p>Following<\/p>/);
 // A literal legacy </plaintext> is itself plaintext, so it is not an oracle.
});

for(const [source,expanded] of [
 ['<SmAlL/><span>tail</span>','<small></small><span>tail</span>'],
 ['<form id=outer><form id=inner /><input id=keep></form>','<form id=outer><form id=inner></form><input id=keep></form>'],
 ['<button id=outer><button id=inner /><span>tail</span></button>','<button id=outer><button id=inner></button><span>tail</span></button>'],
 ['<div data-example="<small/>"/><span>tail</span>','<div data-example="<small/>"></div><span>tail</span>'],
 ['<!-- <script/> --><p/>tail','<!-- <script/> --><p></p>tail'],
])test(`one token-boundary operation: ${source}`,()=>assert.equal(parseClosure(source).html,serialize(parse(expanded))));
