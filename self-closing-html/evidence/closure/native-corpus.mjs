import fs from 'node:fs';
import {html,parse} from 'parse5';
import {parseClosure,VOID} from './parser.mjs';
const signature=n=>n.nodeName==='#documentType'?['doctype',n.name,n.publicId,n.systemId]:n.nodeName==='#text'?['text',n.value]:n.nodeName==='#comment'?['comment',n.data]:[n.tagName??n.nodeName,n.namespaceURI??null,n.attrs?.map(a=>[a.prefix?`${a.prefix}:${a.name}`:a.name,a.value])??[],(n.childNodes??[]).map(signature),n.content?signature(n.content):null];
const wrappers=[['body','',''],['div','<div>','</div>'],['bold','<b>','</b>'],['cell','<table><tr><td>','</td></tr></table>'],['select','<select>','</select>']];
const cases=[];
for(const tag of Object.values(html.TAG_NAMES))for(const [context,open,close] of wrappers){
 if(tag==='plaintext')continue;
 const token=`<${tag} id="empty" />`;const source='<!doctype html PUBLIC "self-closing"><body>'+open+token+'<span>Following</span>'+close;
 const expanded=VOID.has(tag)||tag==='svg'||tag==='math'?source:source.replace(token,`<${tag} id="empty"></${tag}>`);
 cases.push({tag,context,source,expanded,expected:signature(parseClosure(source).tree),baseline:signature(parse(expanded))});
}
let state=0x434c4e41;const rand=()=>{state^=state<<13;state^=state>>>17;state^=state<<5;return state>>>0;};
const parts=['<div/>','</div>','<small/>','</small>','<a/>','</a>','<button/>','</button>','<p/>','</p>','<form/>','</form>','<table/>','<tr/>','<td/>','</table>','<select/>','<option/>','</select>','<template/>','</template>','<svg>','<path/>','</svg>','<math>','<mtext>','</mtext>','</math>','text','&amp;'];
for(let i=0;i<200;i++){let source='<!doctype html PUBLIC "self-closing"><body>';for(let j=0,n=1+rand()%18;j<n;j++)source+=parts[rand()%parts.length];cases.push({source,expected:signature(parseClosure(source).tree)});}
const result={scope:'Named immediate-pair comparisons plus seeded new-parser differential cases; no script payloads. Source grammar selected by navigation, DOMParser remains legacy.',seed:'0x434c4e41',cases};fs.writeFileSync(new URL('./native-corpus.json',import.meta.url),JSON.stringify(result)+'\n');console.log(cases.length);
