import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {serialize} from 'parse5';
import {ClosureParser,parseClosure} from './parser.mjs';
import {createSafeParser} from './safe-parse.mjs';
const parts=['<div/>','</div>','<small/>','</small>','<a/>','</a>','<button/>','</button>','<p/>','</p>','<form/>','</form>','<table/>','<tr/>','<td/>','</table>','<select/>','<option/>','</select>','<template/>','</template>','<svg>','<path/>','</svg>','<math>','<mtext>','</mtext>','</math>','<style/>','</style>','<textarea/>','</textarea>','<script/>','</script>','<img src=x onerror="probe()">','<a href="javascript:probe()">link</a>','text','&amp;','😀','<!--comment-->','<div hidden/>','<div inert/>','<div popover/>'];
let state=0x434c4f53;function rand(){state^=state<<13;state^=state>>>17;state^=state<<5;return state>>>0;}
const safe=createSafeParser();
const report={scope:'Seeded static/incremental equivalence and target-grammar in-place sanitization. Not independent parsing proof, browser execution, native implementation, or universal sanitization guarantee.',seed:'0x434c4f53',inputs:10000,chunkComparisons:0,chunkMismatches:[],safeInputs:1000,safeFailures:[],sourceDigests:{}};
try{
 for(let i=0;i<report.inputs;i++){
  let source='<!doctype html><body>';for(let j=0,n=1+rand()%22;j<n;j++)source+=parts[rand()%parts.length];
  const expected=parseClosure(source).html;
  for(const size of [1,7,31]){const p=new ClosureParser();for(let j=0;j<source.length;j+=size)p.write(source.slice(j,j+size),j+size>=source.length);const actual=serialize(p.document);report.chunkComparisons++;if(actual!==expected&&report.chunkMismatches.length<10)report.chunkMismatches.push({source,size,expected,actual});}
  if(i<report.safeInputs){
   const {document}=safe.parse(source,{profile:'self-closing'});
   const bad=[...document.querySelectorAll('*')].filter(n=>n.localName==='script'||[...n.attributes].some(a=>/^on/i.test(a.name)||['href','src','xlink:href','action','formaction'].includes(a.name)&&/^\s*javascript:/i.test(a.value)));
   if(bad.length&&report.safeFailures.length<10)report.safeFailures.push({source,elements:bad.map(n=>n.outerHTML)});
  }
 }
}finally{safe.close();}
for(const name of ['parser.mjs','safe-dom.mjs','safe-parse.mjs','check.mjs','parser.test.mjs','safe-parse.test.mjs'])report.sourceDigests[name]=createHash('sha256').update(fs.readFileSync(new URL(name,import.meta.url))).digest('hex');
fs.writeFileSync(new URL('./check-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));if(report.chunkMismatches.length||report.safeFailures.length)process.exitCode=1;
