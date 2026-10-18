import {parseProjected} from './projection-candidate.mjs';
import {run} from './model.mjs';
import fs from 'node:fs';
const wrappers=[['body','',''],['div','<div>','</div>'],['section','<section>','</section>'],['link','<a href="#">','</a>'],['bold','<b>','</b>'],['emphasis','<em>','</em>'],['form','<form>','</form>'],['template','<template>','</template>'],['list-item','<ul><li>','</li></ul>'],['table-cell','<table><tr><td>','</td></tr></table>']];
const cases=[];
for(const [context,open,close] of wrappers)for(const tag of ['div','span','x-box','h1']){
 const input='<!doctype html><body>'+open+`<${tag} id="empty" />`+'<span>Following</span>'+close;
 const next=parseProjected(input);
 // Only the one intentionally constructed empty token is replaced; not a lowering algorithm.
 const expanded=next.activations.length ? input.replace(`<${tag} id="empty" />`,`<${tag} id="empty"></${tag}>`) : input;
 const expected=run(expanded).serialized;
 cases.push({context,tag,activated:next.activations.length>0,equal:next.html===expected,...(next.html===expected?{}:{input,next:next.html,expected})});
}
const report={cases:cases.length,failures:cases.filter(c=>!c.equal),results:cases};fs.writeFileSync('sugar-results.json',JSON.stringify(report,null,2)+'\n');console.log(report);if(report.failures.length)process.exitCode=1;
