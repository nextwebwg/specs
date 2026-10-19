import fs from 'node:fs';
import {parse} from 'parse5';
import {parseProjected} from './projection-candidate.mjs';

const signature=node=>{
 if(node.nodeName==='#documentType')return ['doctype',node.name,node.publicId,node.systemId];
 if(node.nodeName==='#text')return ['text',node.value];
 if(node.nodeName==='#comment')return ['comment',node.data];
 return [node.tagName??node.nodeName,node.namespaceURI??null,
  node.attrs?.map(a=>[a.prefix?`${a.prefix}:${a.name}`:a.name,a.value])??[],
  (node.childNodes??[]).map(signature),node.content?signature(node.content):null];
};
let state=0x4e415456;const random=()=>{state^=state<<13;state^=state>>>17;state^=state<<5;return state>>>0;};
const parts=['<div/>','</div>','<x-box/>','</x-box>','<span/>','</span>','<b>','</b>','<i>','</i>','<p>','</p>','<table>','<tr>','<td>','</table>','<template>','</template>','<svg>','</svg>','<math>','<mtext>','</math>','text','&amp;','<!--comment-->'];
const sources=[
 '<div popover/><button>control</button>',
 '<table><div/>A<span>B</span><tr><td>C</table>',
 '<div/><svg></div><style><img data-probe></style></svg>',
 '<h1/><svg></h2><style><img data-probe></style></svg>',
 '<b><x-box/>text</b>after',
 '<div><x-box/></div><svg></x-box><title><style></title><img data-probe></style>',
];
while(sources.length<200){let source='';for(let i=0,n=1+random()%25;i<n;i++)source+=parts[random()%parts.length];sources.push(source);}
const cases=sources.map(body=>{
 const source='<!doctype html PUBLIC "next"><body>'+body;
 const projected=parseProjected(source);
 return {source,baseline:signature(parse(source)),projected:signature(projected.tree),activations:projected.activations.length};
});
const report={seed:'0x4e415456',cases,scope:'Native navigation output versus the static model; compare only inputs whose native legacy DOMParser baseline agrees with parse5, and report skips separately'};
fs.writeFileSync(new URL('./native-corpus.json',import.meta.url),JSON.stringify(report)+'\n');
console.log(JSON.stringify({seed:report.seed,cases:cases.length,activations:cases.reduce((n,c)=>n+c.activations,0)}));
