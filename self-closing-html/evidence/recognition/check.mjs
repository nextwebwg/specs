import fs from 'node:fs';
import assert from 'node:assert/strict';
import {parse, parseFragment, defaultTreeAdapter, html, serialize} from 'parse5';
import {RecognitionPreservingParser, parseRecognition} from './parser.mjs';
function signature(root, projected = false) {
  const ids = new Map();
  const output = [];
  const walk = (node, barriers = []) => {
    const key = projected ? node.recognitionNode : node;
    if (!ids.has(key)) ids.set(key, ids.size);
    const id = ids.get(key);
    output.push({id, name:node.nodeName, ns:node.namespaceURI, attrs:node.attrs,
      value:node.value, data:node.data, barriers});
    const boundary = node.content || (node.namespaceURI && node.namespaceURI !== html.NS.HTML) || node.attrs?.some(a=>a.name==='inert');
    const inner = boundary ? [...barriers, id] : barriers;
    for (const child of node.childNodes??[]) walk(child, inner);
    if (node.content) walk(node.content, inner);
  };
  walk(root);
  // The identity map must be shared between the two inventories; attach it to
  // the returned list for the comparison below, rather than renumbering nodes.
  return {output, ids};
}
function verify(parser, root) {
  const baseline = signature(root);
  const projected = parser.output(root);
  const seen = [];
  const walk = (node, barriers = []) => {
    const id = baseline.ids.get(node.recognitionNode);
    assert.notEqual(id, undefined);
    seen.push({id,name:node.nodeName,ns:node.namespaceURI,attrs:node.attrs,value:node.value,data:node.data,barriers});
    const boundary=node.content||(node.namespaceURI&&node.namespaceURI!==html.NS.HTML)||node.attrs?.some(a=>a.name==='inert');
    const inner=boundary?[...barriers,id]:barriers;
    for(const child of node.childNodes??[])walk(child,inner);
    if(node.content)walk(node.content,inner);
  };
  walk(projected);
  assert.deepEqual(seen,baseline.output);
}
const atoms=['<small/>','<a/>','<b/>','<p/>','<button/>','<form/>','<table/>','<tr/>','<td/>','<select/>','<option/>','<div/>','<x-box/>','</small>','</b>','</a>','</div>','</x-box>','</table>','</select>','</form>','<svg>','</svg>','<math>','<mtext>','</mtext>','</math>','<foreignObject>','</foreignObject>','<style/>','<style>','</style>','<script/>','<script>','</script>','<textarea/>','</textarea>','<template/>','<template>','</template>','<noscript/>','</noscript>','<plaintext/>','<img src=x onerror="probe()">','text','😀&amp;','<div inert/>','<div hidden/>'];
const contexts=[null,'div','table','select','template','svg'];
let seed=0x72656332;
const rand=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return seed>>>0;};
const report={seed:'0x72656332',inputs:10000,comparisons:0,failures:[],authoring:[],limits:['Reference parser shares parse5 recognition; this is not an independent native engine.','Identity/text/namespace/attribute and template/foreign/inert ancestry preservation; not equivalence of arbitrary scripts, CSS or application behavior.','Table and formatting recovery can differ from literal immediate empty-pair expansion.']};
for(let n=0;n<report.inputs;n++){
  let source='';for(let i=0,count=1+rand()%18;i<count;i++)source+=atoms[rand()%atoms.length];
  for(const scriptingEnabled of [true,false])for(const context of contexts){
    const options={scriptingEnabled,sourceCodeLocationInfo:true};
    const makeContext=()=>context?defaultTreeAdapter.createElement(context,context==='svg'?html.NS.SVG:html.NS.HTML,[]):null;
    const parser=context?RecognitionPreservingParser.getFragmentParser(makeContext(),options):new RecognitionPreservingParser(options);
    parser.write(source,true);
    const root=context?parser.getFragment():parser.document;
    const baseline=context?parseFragment(makeContext(),source,options):parse(source,options);
    report.comparisons++;
    try{assert.equal(serialize(root),serialize(baseline));verify(parser,root);}
    catch(error){if(report.failures.length<8)report.failures.push({source,context,scriptingEnabled,error:error.message.slice(0,600)});}
  }
}
for(const name of Object.values(html.TAG_NAMES)){
  const source=`<!doctype html><body><${name}/><span>tail</span>`;
  const {parser,tree,html:actual}=parseRecognition(source);
  let eligible=false;const walk=n=>{if(n.tagName===name&&parser.eligible(n.recognitionNode))eligible=true;for(const c of n.childNodes??[])walk(c);if(n.content)walk(n.content);};walk(tree);
  report.authoring.push({name,eligible,equalsEmptyPair:actual===serialize(parse(`<!doctype html><body><${name}></${name}><span>tail</span>`))});
}
fs.writeFileSync(new URL('./results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({comparisons:report.comparisons,failures:report.failures,eligible:report.authoring.filter(x=>x.eligible).length,eligiblePairDifferences:report.authoring.filter(x=>x.eligible&&!x.equalsEmptyPair)},null,2));
if(report.failures.length)process.exitCode=1;
