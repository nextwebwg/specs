import {LiveDOMParser} from './live-dom.mjs';

export async function runExecutionCases({caseFilter=null}={}){
 const results=[];
 const check=(condition,message)=>{if(!condition)throw new Error(message);};
 async function run(name,source,verify,{chunk=0,setup=null,network=false}={}){
  if(caseFilter&&!name.includes(caseFilter))return;
  const frame=document.createElement('iframe');document.body.append(frame);
  const w=frame.contentWindow;w.trace=[];
  try{
   setup?.(w);
   const runtime=new LiveDOMParser(w.document);
   w.nextRuntime=runtime;
   if(network){
    const response=await fetch('/streamed-source');
    const reader=response.body.getReader();const decoder=new TextDecoder();let chunks=0;
    while(true){const {done,value}=await reader.read();if(done)break;chunks++;await runtime.write(decoder.decode(value,{stream:true}));}
    await runtime.write(decoder.decode(),true);w.trace.push({networkChunks:chunks});
   }
   else if(chunk)for(let i=0;i<source.length;i+=chunk)await runtime.write(source.slice(i,i+chunk),i+chunk>=source.length);
   else await runtime.write(source,true);
   await new Promise(resolve=>setTimeout(resolve,20));
   await verify(w,check,runtime);
   results.push({name,pass:true,trace:w.trace});
  }catch(error){results.push({name,pass:false,error:String(error.stack??error),trace:w.trace});}
  finally{
   for(const popover of w.document.querySelectorAll(':popover-open'))popover.hidePopover();
   w.document.activeElement?.blur();
   frame.remove();
   await new Promise(resolve=>requestAnimationFrame(resolve));
  }
 }
 const prefix='<!doctype html PUBLIC "next"><body>';
 for(const chunk of [0,1,7,31]){
  await run(`script checkpoint, chunk ${chunk}`,prefix+`<div id="empty"/><script>
   trace.push({parent:document.currentScript.parentNode.tagName,empty:document.querySelector('#empty').childNodes.length,later:!!document.querySelector('#later')});
   const b=document.createElement('b');b.id='added';document.querySelector('#empty').append(b);
   queueMicrotask(()=>trace.push({microtask:!!document.querySelector('#later')}));
  </script><span id="later">later</span>`,(w,c)=>{
   c(w.trace[0].parent==='BODY'&&w.trace[0].empty===0&&!w.trace[0].later,'script sees projected DOM before later tokens');
   c(w.trace[1].microtask===false,'microtask precedes parser resume');
   c(w.document.querySelector('#added').parentNode.id==='empty','script child survives resume');
   c(w.document.querySelector('#later').parentNode.tagName==='BODY','following sibling');
  },{chunk});
 }
 await run('custom element callbacks and script-added child',prefix+`<x-probe id="host"/><script>trace.push({atScript:document.querySelector('#host').children.length})</script><span id="later">later</span>`,(w,c)=>{
  c(w.trace.filter(x=>x.connected).length===1,'connectedCallback occurs exactly once');
  c(w.trace.filter(x=>x.disconnected).length===0,'parser never reconnects stable node');
  c(w.trace.find(x=>x.connected).parent==='BODY','connected parent is projected parent');
  c(w.document.querySelector('#host').firstElementChild.tagName==='B','callback mutation retained');
 },{setup:w=>w.customElements.define('x-probe',class extends w.HTMLElement{
  constructor(){super();w.trace.push({constructor:true,connected:this.isConnected});}
  connectedCallback(){w.trace.push({connected:true,parent:this.parentNode.tagName});this.append(w.document.createElement('b'));}
  disconnectedCallback(){w.trace.push({disconnected:true});}
 })});
 await run('script detaches ordinary open ancestor',prefix+`<section id="open"><div id="empty"/><script>document.querySelector('#open').remove()</script><span id="after">after</span></section><p id="tail">tail</p>`,(w,c,r)=>{
  c(!w.document.querySelector('#open'),'removed ancestor stays removed');
  const removed=[...r.nodes.values()].find(n=>n.id==='open');
  c(removed.querySelector('#after')?.parentNode===removed,'future tokens enter detached ordinary ancestor');
  c(removed.querySelector('#empty').children.length===0,'shorthand remains empty');
  c(!!w.document.querySelector('#tail'),'parsing continues outside removed ancestor');
 });
 await run('script moves shorthand node',prefix+`<aside id="target"></aside><div id="empty"/><script>document.querySelector('#target').append(document.querySelector('#empty'))</script><span id="after">after</span>`,(w,c)=>{
  c(w.document.querySelector('#empty').parentNode.id==='target','parser preserves script reparenting');
  c(w.document.querySelector('#after').parentNode.tagName==='BODY','recognition containment projection remains at original parent');
 });
 await run('namespace recovery never creates executable image',prefix+`<div/><svg></div><style><img src="/probe?name=namespace" onerror="trace.push('BAD')"></style></svg><script>trace.push({images:document.images.length})</script>`,(w,c)=>{
  c(w.document.images.length===0,'image-looking text remains text');
  c(w.trace.length===1&&w.trace[0].images===0,'handler never executes');
 });
 await run('legacy innerHTML grammar remains independent',prefix+`<div id="empty"/><script>document.querySelector('#empty').innerHTML='<x-legacy/><span id="nested">inside</span>';trace.push(document.querySelector('#nested').parentNode.tagName)</script>`,(w,c)=>{
  c(w.trace[0]==='X-LEGACY','native legacy insertion ignores ordinary slash');
  c(w.document.querySelector('#nested').parentNode.tagName==='X-LEGACY','parser does not reproject script-inserted markup');
 });
 await run('external classic script blocks later parsing',prefix+`<div/><script src="/delayed-script"></script><span id="later">later</span>`,(w,c)=>{
  c(w.trace[0]?.external===true&&!w.trace[0].later,'external script executes before later source');
  c(!!w.document.querySelector('#later'),'resume after external script');
 });
 await run('mutation observer callback before resume',prefix+`<div id="empty"/><script>
   new MutationObserver(()=>trace.push({observed:true,later:!!document.querySelector('#later')})).observe(document.querySelector('#empty'),{childList:true});
   document.querySelector('#empty').append(document.createElement('b'));
  </script><span id="later">later</span>`,(w,c)=>{
  c(w.trace.length===1&&w.trace[0].observed&&!w.trace[0].later,'observer runs before next token');
 });
 await run('document writing rejects before mutation',prefix+`<div id="empty"/><script>
  for(const method of ['write','writeln','open']){try{document[method]('<img id="bad">');trace.push({method,rejected:false});}catch(error){trace.push({method,rejected:error.name==='NotSupportedError'});}}
 </script><span id="later">later</span>`,(w,c)=>{
  c(w.trace.length===3&&w.trace.every(x=>x.rejected),'all legacy writing entry points reject');
  c(!w.document.querySelector('#bad')&&!!w.document.querySelector('#later'),'rejection precedes mutation and parsing resumes');
 });
 await run('reentrant prototype input rejects',prefix+`<div/><script>nextRuntime.write('<img id="bad">').catch(error=>trace.push(error.name));</script><span id="later">later</span>`,(w,c)=>{
  c(w.trace[0]==='InvalidStateError','nested write rejects');
  c(!w.document.querySelector('#bad')&&!!w.document.querySelector('#later'),'nested input never consumed');
 });
 await run('custom element upgrades during parsing',prefix+`<x-late id="host"/><script>
 customElements.define('x-late',class extends HTMLElement{connectedCallback(){trace.push({upgraded:true,parent:this.parentNode.tagName,later:!!document.querySelector('#later')});this.append(document.createElement('b'));}});
 </script><span id="later">later</span>`,(w,c)=>{
  c(w.trace.length===1&&w.trace[0].upgraded&&w.trace[0].parent==='BODY'&&!w.trace[0].later,'upgrade sees projected tree before following tokens');
  c(w.document.querySelector('#host').children.length===1,'upgrade mutation preserved');
 });
 await run('doctype DOM mutation cannot switch the active profile',prefix+`<script>document.replaceChild(document.implementation.createDocumentType('html','',''),document.doctype);</script><div id="empty"/><span id="later">tail</span>`,(w,c)=>{
  c(w.document.doctype.publicId==='','application doctype replacement retained');
  c(w.document.querySelector('#empty').children.length===0&&w.document.querySelector('#later').parentNode===w.document.body,'profile remains fixed for the parse');
 });
 await run('frameset recovery preserves script-moved nodes','<!doctype html PUBLIC "next"><input type="hidden" id="keep"><script>window.savedBody=document.body;window.savedScript=document.currentScript;document.head.append(document.getElementById("keep"));</script><frameset></frameset>',(w,c)=>{
  c(w.document.body.localName==='frameset','recovery actually replaces the implicit body');
  c(w.document.getElementById('keep')?.parentNode===w.document.head,'script-moved node survives recovery');
  c(w.savedScript.parentNode===w.savedBody,'detached subtree retains its children');
 });
 await run('real network stream with split UTF-8 character','',(w,c)=>{
  c(w.trace[0].stream&&!w.trace[0].later,'stream script checkpoint');
  c(w.trace[1].networkChunks>1,'multiple network input chunks observed');
  c(w.document.body.textContent.includes('😀'),'stream decoder preserves split UTF-8');
  c(w.document.querySelector('#empty').children.length===0,'streamed shorthand empty');
 },{network:true});
 await run('resource request positive control',prefix+'<div/><img src="/probe?name=positive">',(w,c)=>{
  c(w.document.images.length===1,'real connected image exists');
 });
 for(const value of ['', 'invalid'])await run(`closed popover containment (${value||'empty'})`,prefix+`<div id="popover" popover="${value}"/><button id="control">control</button>`,(w,c)=>{
  const popover=w.document.getElementById('popover');const control=w.document.getElementById('control');
  control.focus();
  w.trace.push({contained:control.parentNode===popover,closedRects:control.getClientRects().length,closedFocus:w.document.activeElement===control});
  c(control.parentNode===popover,'popover boundary retained');
  c(control.getClientRects().length===0&&w.document.activeElement!==control,'closed popover control is hidden and unfocusable');
  popover.showPopover();const openRects=control.getClientRects().length;control.focus();
  const opened={openRects,openFocus:w.document.activeElement===control};w.trace.push(opened);
  const baseline=w.document.createElementNS('http://www.w3.org/1999/xhtml','div');baseline.setAttributeNS(null,'popover',value);w.document.body.append(baseline);
  const baselineControl=w.document.createElementNS('http://www.w3.org/1999/xhtml','button');baseline.append(baselineControl);baselineControl.append(w.document.createTextNode('native control'));
  baselineControl.focus();const baselineClosedFocus=w.document.activeElement===baselineControl;
  baseline.showPopover();const baselineOpenRects=baselineControl.getClientRects().length;baselineControl.focus();
  const baselineOpenFocus=w.document.activeElement===baselineControl;
  w.trace.push({baselineClosedFocus,baselineOpenRects,baselineOpenFocus});
  c(opened.openRects>0&&baselineOpenRects>0,'opening both popovers is a positive visibility control');
  c(!baselineClosedFocus&&opened.openFocus===baselineOpenFocus,'focus behavior matches the independent native control with the same call history');
 });
 await run('generated live-DOM refinement',prefix,async(w,c)=>{
  const fromNative=node=>{
   if(node.nodeType===10)return ['doctype',node.name,node.publicId,node.systemId];
   if(node.nodeType===3)return ['text',node.data];
   if(node.nodeType===8)return ['comment',node.data];
   return [node.localName??node.nodeName,node.namespaceURI??null,
    node.attributes?[...node.attributes].map(a=>[a.name,a.value]):[],
    [...node.childNodes].map(fromNative),node.content?fromNative(node.content):null];
  };
  const fromModel=node=>{
   if(node.nodeName==='#documentType')return ['doctype',node.name,node.publicId,node.systemId];
   if(node.nodeName==='#text')return ['text',node.value];
   if(node.nodeName==='#comment')return ['comment',node.data];
   return [node.tagName??node.nodeName,node.namespaceURI??null,
    node.attrs?.map(a=>[a.prefix?`${a.prefix}:${a.name}`:a.name,a.value])??[],
    (node.childNodes??[]).map(fromModel),node.content?fromModel(node.content):null];
  };
  let state=0x444f4d52;const random=()=>{state^=state<<13;state^=state>>>17;state^=state<<5;return state>>>0;};
  const tokens=['<div/>','</div>','<x-box/>','</x-box>','<span/>','</span>','<b>','</b>','<p>','</p>','<table>','<tr>','<td>','</table>','<template>','</template>','<svg>','</svg>','<math>','</math>','text','&amp;','<!--comment-->'];
  for(let i=0;i<500;i++){
   let source=prefix;for(let j=0,n=1+random()%25;j<n;j++)source+=tokens[random()%tokens.length];
   const runtime=new LiveDOMParser(w.document,{executeScripts:false});
   await runtime.write(source,true);
   const actual=JSON.stringify(fromNative(w.document));const expected=JSON.stringify(fromModel(runtime.parser.output()));
   c(actual===expected,`DOM refinement case ${i}: ${source}\nACTUAL ${actual}\nEXPECTED ${expected}`);
  }
  w.trace.push({seed:'0x444f4d52',comparisons:500});
 });
 return results;
}
