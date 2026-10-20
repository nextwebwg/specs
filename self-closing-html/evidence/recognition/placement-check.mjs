import fs from 'node:fs';
import assert from 'node:assert/strict';
import {parse,parseFragment,defaultTreeAdapter,html,serialize} from 'parse5';
import {PlacementParser} from './placement.mjs';
import {auditPlacement} from './audit-placement.mjs';
const atoms=['<small/>','<a/>','<b/>','<p/>','<button/>','<form/>','<table/>','<tr/>','<td/>','<select/>','<option/>','<div/>','<x-box/>','</small>','</b>','</a>','</div>','</x-box>','</table>','</select>','</form>','<svg>','</svg>','<math>','<mtext>','</mtext>','</math>','<foreignObject>','</foreignObject>','<style/>','<style>','</style>','<script/>','<script>','</script>','<textarea/>','</textarea>','<template/>','<template>','</template>','<noscript/>','</noscript>','<plaintext/>','<img src=x onerror="probe()">','text','😀&amp;','<div inert/>','<div hidden/>','<pre/>','\n'];
const contexts=[null,'div','table','select','template','svg'];
let seed=0x44585032;const rand=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return seed>>>0;};
const report={seed:'0x44585032',inputs:10000,comparisons:0,checkpointAudits:0,failures:[],placements:{},scope:'Authorized source elements/data, protected contexts, unchanged source recognition; finite shared-recognizer evidence, not universal browser safety.'};
for(let n=0;n<report.inputs;n++){
  let source='';for(let i=0,count=1+rand()%18;i<count;i++)source+=atoms[rand()%atoms.length];
  for(const scriptingEnabled of [true,false])for(const context of contexts){
    const options={scriptingEnabled,sourceCodeLocationInfo:true};
    const makeContext=()=>context?defaultTreeAdapter.createElement(context,context==='svg'?html.NS.SVG:html.NS.HTML,[]):null;
    if(n<200)options.onCheckpoint=(_t,p)=>{auditPlacement(p);report.checkpointAudits++;};
    let parser;
    try{
      parser=context?PlacementParser.getFragmentParser(makeContext(),options):new PlacementParser(options);
      parser.write(source,true);
      const root=context?parser.getFragment():parser.document;
      const baseline=context?parseFragment(makeContext(),source,{scriptingEnabled}):parse(source,{scriptingEnabled});
      assert.equal(serialize(root),serialize(baseline),'source recognition changed');
      auditPlacement(parser,root);
      const reason=parser.lastDecision.placement==='normal-html'?'normal-html':parser.lastDecision.reason;
      report.placements[reason]=(report.placements[reason]??0)+1;
    }catch(error){if(report.failures.length<12)report.failures.push({source,context,scriptingEnabled,error:error.message.slice(0,800)});}
    report.comparisons++;
  }
}
fs.writeFileSync(new URL('./placement-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
if(report.failures.length)process.exitCode=1;
