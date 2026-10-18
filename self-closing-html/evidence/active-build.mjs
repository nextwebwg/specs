import fs from 'node:fs';
import {parseProjected, STATEFUL} from './projection-candidate.mjs';
const withoutNativeExemptions = process.argv.includes('--without-native-exemptions');
if (withoutNativeExemptions) {
 for (const name of ['details','dialog','datalist','audio','video','canvas','object','applet']) STATEFUL.delete(name);
}
const output = withoutNativeExemptions ? 'active-unprotected-browser.html' : 'active-browser.html';
const signal="window.__auditSignals=[]; window.signal=value=>window.__auditSignals.push(value); customElements.define('x-observer',class extends HTMLElement{connectedCallback(){signal('connected:'+this.parentNode?.nodeName)}});";
const image='<img data-probe src="data:image/png;base64,aW52YWxpZA==" onerror="window.signal(\'image-error\')">';
const input='<input id="target" onfocus="window.signal(\'focus\')">';
const cases=[
 ['positive-control',image+input],
 ['style',`<style/>${image}<style></style>`],
 ['textarea',`<textarea/>${image}<textarea></textarea>`],
 ['math',`<math><mtext><x-box/><mglyph><style>${image}</style></mglyph></mtext></math>`],
 ['svg-ancestor',`<div/><svg></div><style>${image}</style></svg>`],
 ['template',`<template/>${image}</template>`],
 ['expired-frame',`<div><x-box/></div><svg></x-box><title><style></title>${image}</style>`],
 ['details',`<details/>${input}`], ['dialog',`<dialog/>${input}`], ['datalist',`<datalist/>${input}`],
 ['audio',`<audio/>${input}`], ['video',`<video/>${input}`], ['canvas',`<canvas/>${input}`],
 ['script-mutation',`<div id="empty"/><script>signal('script-parent:'+document.currentScript.parentNode.nodeName);document.getElementById('empty').append('added');</script><span id="following">following</span>`],
 ['custom-reaction','<div id="empty"/><x-observer></x-observer>'],
 ['shadow-owner','<x-host id="host"/><template shadowrootmode="open"><span id="shadow-child">shadow</span></template><span>following</span>']
];
const finish=`<script>addEventListener('DOMContentLoaded',()=>setTimeout(()=>{document.getElementById('target')?.focus();setTimeout(()=>parent.postMessage({audit:'next-active',key:window.name,signals:window.__auditSignals,targetVisible:document.getElementById('target')?.checkVisibility({checkVisibilityCSS:true}),activeTarget:document.activeElement?.id,images:document.querySelectorAll('img[data-probe]').length,shadowHost:!!document.getElementById('host')?.shadowRoot,bodyShadow:!!document.body.shadowRoot,emptyChildren:document.getElementById('empty')?.childNodes.length,followingParent:document.getElementById('following')?.parentNode.nodeName},'*'),50)},50));</script>`;
const fixtures=[];
for(const[name,body]of cases){const source='<!doctype html><html><head><script>'+signal+'</script></head><body>'+body+finish+'</body></html>';fixtures.push({name,version:'legacy',html:source});fixtures.push({name,version:'serialized-projection',html:parseProjected(source).html});}

const script=`const fixtures=${JSON.stringify(fixtures).replaceAll('<','\\u003c')}; const results=[];let index=0;let frame;function next(){if(index===fixtures.length){document.getElementById('status').textContent='COMPLETE: '+results.length+' active document observations.';return;}const fixture=fixtures[index++];frame=document.createElement('iframe');frame.sandbox='allow-scripts';frame.name=fixture.name+':'+fixture.version;frame.srcdoc=fixture.html;document.getElementById('frames').replaceChildren(frame);}addEventListener('message',event=>{if(event.source!==frame?.contentWindow||event.data?.audit!=='next-active')return;results.push(event.data);document.getElementById('results').textContent=JSON.stringify(results,null,2);next();});next();`;
const page='<!doctype html><meta charset="utf-8"><title>Active HTML boundary audit</title><h1>Active HTML boundary audit</h1><p>Sandboxed local fixtures. Signals are harmless messages; no external resources are fetched. Serialized projection is an experimental lowering, not a native Next implementation. Shadow-root ownership intentionally tests a known unsupported lowering boundary.</p><p id="status">Running…</p><div id="frames"></div><pre id="results"></pre><script>'+script+'</script>';
fs.writeFileSync(output,page);
console.log('Wrote ' + output + '; serve this directory and open the page in a browser.');
