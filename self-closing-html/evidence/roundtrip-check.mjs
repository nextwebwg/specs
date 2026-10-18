import fs from 'node:fs';
import {parseProjected} from './projection-candidate.mjs';
import {run,contextElement} from './model.mjs';
import {serialize,html} from 'parse5';
const parts=['<div/>','</div>','<x-box/>','</x-box>','<span/>','</span>','<p/>','</p>','<b/>','</b>','<form/>','</form>','<table/>','</table>','<select/>','</select>','<template/>','</template>','<svg>','</svg>','<math>','</math>','<mtext>','</mtext>','<mglyph>','</mglyph>','<style>','</style>','<textarea>','</textarea>','<noscript>','</noscript>','<foreignObject>','</foreignObject>','<img data-probe>','<script>','</script>','<!--','-->','<title>','</title>','<iframe>','</iframe>','<plaintext>','<xmp>','<div inert/>','<details/>','</details>','<dialog/>','</dialog>','<datalist/>','</datalist>','<audio/>','</audio>','<video/>','</video>','<canvas/>','</canvas>','<object/>','</object>'];
function markers(root){const out=[];function visit(n,inTemplate=false){inTemplate ||= n.tagName==='template'&&n.namespaceURI===html.NS.HTML;const id=n.attrs?.find(a=>a.name==='data-probe')?.value;if(id!==undefined)out.push({id,tag:n.tagName,ns:n.namespaceURI,inTemplate});for(const c of n.childNodes??[])visit(c,inTemplate);if(n.content)visit(n.content,true);}visit(root);return out;}
let state=0x52545250;const rand=()=>{state^=state<<13;state^=state>>>17;state^=state<<5;return state>>>0;};
const report={seed:'0x52545250',inputs:20000,contexts:['document','div','table','template','select'],scripting:[true,false],comparisons:0,changedMarkerClassifications:0,newlyActiveMarkers:0,witnesses:[],caveats:['Finite model search, not proof of serialization safety','Marker classification covers only the searched parser mechanism','Actual insertion contexts must match; select model differs from Chromium']};
for(let i=0;i<report.inputs;i++){
 let source='';for(let j=0,n=1+rand()%24;j<n;j++)source+=parts[rand()%parts.length];let id=0;source=source.replaceAll('<img data-probe>',()=>`<img data-probe="${id++}">`);
 for(const name of report.contexts)for(const scripting of report.scripting){
  const context=()=>name==='document'?null:contextElement(name);
  const legacy=run(source,'legacy',context(),scripting);const projected=parseProjected(source,context(),scripting);
  const old=markers(run(serialize(legacy.tree),'legacy',context(),scripting).tree);
  const next=markers(run(projected.html,'legacy',context(),scripting).tree);
  report.comparisons++;
  const changed=next.filter(n=>!old.some(o=>JSON.stringify(o)===JSON.stringify(n)));
  if(changed.length)report.changedMarkerClassifications++;
  const newlyActive=next.filter(n=>!n.inTemplate&&!old.some(o=>o.id===n.id&&!o.inTemplate&&o.ns===n.ns&&o.tag===n.tag));
  if(newlyActive.length){report.newlyActiveMarkers++;if(report.witnesses.length<20)report.witnesses.push({source,name,scripting,legacy:legacy.serialized,projected:projected.html,old,next});}
 }
}
fs.writeFileSync('roundtrip-results.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));

if (report.changedMarkerClassifications || report.newlyActiveMarkers) process.exitCode = 1;
