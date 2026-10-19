import fs from 'node:fs';
import {serialize} from 'parse5';
import {parseProjected} from './projection-candidate.mjs';
import {IncrementalParser} from './streaming-parser.mjs';

let seed=0x5354524d;
const random=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return seed>>>0;};
const parts=['<div/>','</div>','<x-box/>','</x-box>','<span/>','</span>','<p/>','</p>','<b/>','</b>','<table>','<tr>','<td>','</table>','<template>','</template>','<svg>','</svg>','<math>','<mtext>','</math>','<style>','</style>','<textarea>','</textarea>','<script>','</script>','<select>','<option>','</select>','<!--','-->','&amp;','&#x1f600;','😀','\r\n','<div inert/>','<div popover/>','<div data-a="a>b"/>','<div data-a=assets/ />','<details/>','</details>','<h1/>','</h2>','<img data-probe>'];
const report={seed:'0x5354524d',inputs:10000,comparisons:0,failures:[],schedules:['one-code-unit','random-1-to-17','random-1-to-73'],scripting:[true,false],scope:'Chunk invariance against the shared static reference; not an independent recognition implementation'};
for(let i=0;i<report.inputs;i++){
 let source='<!doctype html PUBLIC "next"><body>';
 for(let j=0,n=1+random()%30;j<n;j++)source+=parts[random()%parts.length];
 for(const scriptingEnabled of report.scripting){
  const expected=parseProjected(source,null,scriptingEnabled).html;
  for(const width of [1,17,73]){
   const parser=new IncrementalParser({requireOptIn:true,scriptingEnabled});
   for(let offset=0;offset<source.length;){const count=width===1?1:1+random()%width;parser.write(source.slice(offset,offset+count));offset+=count;}
   parser.write('',true);report.comparisons++;
   const actual=serialize(parser.output());
   if(actual!==expected&&report.failures.length<20)report.failures.push({source,scriptingEnabled,width,expected,actual});
  }
 }
}
fs.writeFileSync(new URL('./streaming-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
if(report.failures.length)process.exitCode=1;
