import {parse} from '../../self-closing-html/evidence/node_modules/parse5/dist/index.js';
import assert from 'node:assert/strict';
import {writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
const cases=[
 {name:'unmarked custom host in table',body:'<table><some-component id="host"></some-component></table>',expected:{host:'body'}},
 {name:'proposed marker has no native grammar in legacy parser',body:'<table><div id="host" contentmodel="table-rows"><tr id="row"><td>Cell</td></tr></div></table>',expected:{host:'body',row:'tbody'}},
 {name:'list wrapper preserved without direct list-item parentage',body:'<ul><div id="host" contentmodel="list-items"><li id="item">Item</li></div></ul>',expected:{host:'ul',item:'div'}},
];
const find=(node,id)=>node.attrs?.some(a=>a.name==='id'&&a.value===id)?node:(node.childNodes??[]).map(c=>find(c,id)).find(Boolean);
const results=cases.map(({name,body,expected})=>{
 const source='<!DOCTYPE html PUBLIC "next">'+body;const document=parse(source);
 const observed=Object.fromEntries(Object.keys(expected).map(id=>[id,find(document,id)?.parentNode?.tagName??null]));
 assert.deepEqual(observed,expected);return {name,source,observed,pass:true};
});
const report={parser:'parse5 8.0.1',runtime:process.version,scope:'Legacy source parsing only; no implementation of flexible nesting, layout, shadow participation or accessibility.',sourceSHA256:createHash('sha256').update(readFileSync(new URL('./baseline.mjs',import.meta.url))).digest('hex'),results};
writeFileSync(new URL('./baseline-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({cases:results.length,passed:results.length,scope:report.scope}));
