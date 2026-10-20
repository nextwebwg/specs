import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createSafeParser} from './safe-parse.mjs';
const parser=createSafeParser();
process.on('exit',()=>parser.close());
const witness='<svg><mtext><style><table/><style/><img data-probe src=x onerror="probe()"></style></mtext></svg>';
test('sanitize the target-grammar tree, not a differently parsed source string',()=>{
 const {document,root}=parser.parse(witness,{profile:'self-closing'});
 assert.equal(document.documentElement,root);
 assert.equal(document.querySelectorAll('[onerror],script').length,0);
});
for(const source of ['<script/>alert(1)<p>tail</p>','<style/><img src=x onerror=probe()>','<select/><img src=x onerror=probe()>','<template/><script>probe()</script>','<div hidden/><img src=x onerror=probe()>','<svg><foreignObject><a href="javascript:probe()">link</a></foreignObject></svg>'])test(`safe target parsing: ${source}`,()=>{
 const {document}=parser.parse(source,{profile:'self-closing'});
 assert.equal(document.querySelectorAll('script,[onerror],[onclick]').length,0);
 for(const node of document.querySelectorAll('[href],[src]'))for(const name of ['href','src'])assert.doesNotMatch(node.getAttribute(name)??'',/^\s*javascript:/i);
});
test('omitted profile retains legacy behavior and explicit closure preserves following markup',()=>{
 const legacy=parser.parse('<div/><span>tail</span>').document;
 const next=parser.parse('<div/><span>tail</span>',{profile:'self-closing'}).document;
 assert.equal(legacy.querySelector('span').parentElement.tagName,'DIV');
 assert.equal(next.querySelector('span').parentElement.tagName,'BODY');
});
test('unsafe profile names fail instead of selecting a fallback',()=>assert.throws(()=>parser.parse('',{profile:'typo'}),{name:'NotSupportedError'}));

test('malformed HTML names and colon attributes stay inert without reparsing',()=>{
 const {document}=parser.parse('<x=bad><img src=x onerror=probe()></x=bad><div a:b=c>tail</div>',{profile:'self-closing'});
 assert.equal(document.querySelectorAll('[onerror],script').length,0);
 assert.match(document.body.textContent,/tail/);
});

test('target-tree sanitization does not invoke an HTML string sink',async()=>{
 const {JSDOM}=await import('jsdom');const {createDOMSafeParser}=await import('./safe-dom.mjs');
 const {window}=new JSDOM('');
 try{
  const safe=createDOMSafeParser(window);
  window.DOMParser.prototype.parseFromString=()=>{throw new Error('Unexpected string reparse');};
  Object.defineProperty(window.Element.prototype,'innerHTML',{configurable:true,set(){throw new Error('Unexpected innerHTML sink');}});
  const {document}=safe.parse('<select/><img src=x onerror=probe()>',{profile:'self-closing'});
  assert.equal(document.querySelectorAll('[onerror]').length,0);
  assert.equal(document.querySelectorAll('img').length,1);
 }finally{window.close();}
});

test('next selects supported family features and inherit uses an explicit caller snapshot',()=>{
 const active=parser.parse('<small/><span>tail</span>',{profile:'next'});
 assert.equal(active.document.querySelector('span').parentNode.tagName,'BODY');
 const inherited=createSafeParser({callerProfile:active.profile});
 try{
  const explicit=inherited.parse('<small/><span>tail</span>',{profile:'inherit'});
  assert.equal(explicit.document.querySelector('span').parentNode.tagName,'BODY');
  const ordinary=inherited.parse('<small/><span>tail</span>');
  assert.equal(ordinary.document.querySelector('span').parentNode.tagName,'SMALL');
 }finally{inherited.close();}
});
