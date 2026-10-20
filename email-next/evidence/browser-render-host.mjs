import {renderRuntime} from './browser-render-runtime.mjs';
import {validateNavigationUrl} from './navigation-url.mjs';
// Override is trusted embedding/test configuration; syntax does not prove entropy or freshness.
export function rendererNonce(configured) {
 const nonce=configured??Array.from(crypto.getRandomValues(new Uint8Array(16)),b=>b.toString(16).padStart(2,'0')).join('');
 if(typeof nonce!=='string'||! /^[A-Za-z0-9_-]{16,128}$/.test(nonce))throw Error('sandbox-nonce');
 return nonce;
}
let active;
export async function mountMessage(container,input,configuration) {
 // Configuration is owned by the client, separately from projected message data.
 const {policy,baseline,limits,renderTimeoutMs=5000,fontFamily,rootFontSizePx,rootFontSizeRange={min:8,max:64},lineHeightRatio,lineHeightRange={min:1,max:3}}=configuration??{};
 // Experimental client preference: generic families only; no font downloads or CSS text.
 if(fontFamily!==undefined&&!['serif','sans-serif','monospace','system-ui'].includes(fontFamily))throw Error('font-preference');
 // Client-owned adjustable experiment bounds, not sender CSS or protocol limits.
 if(!rootFontSizeRange||Object.keys(rootFontSizeRange).length!==2||!Number.isFinite(rootFontSizeRange.min)||!Number.isFinite(rootFontSizeRange.max)||rootFontSizeRange.min<=0||rootFontSizeRange.max<rootFontSizeRange.min)throw Error('root-font-range');
 if(rootFontSizePx!==undefined&&(!Number.isFinite(rootFontSizePx)||rootFontSizePx<rootFontSizeRange.min||rootFontSizePx>rootFontSizeRange.max))throw Error('root-font-preference');
 if(!lineHeightRange||Object.keys(lineHeightRange).length!==2||!Number.isFinite(lineHeightRange.min)||!Number.isFinite(lineHeightRange.max)||lineHeightRange.min<=0||lineHeightRange.max<lineHeightRange.min)throw Error('line-height-range');
 if(lineHeightRatio!==undefined&&(!Number.isFinite(lineHeightRatio)||lineHeightRatio<lineHeightRange.min||lineHeightRatio>lineHeightRange.max))throw Error('line-height-preference');
 if(!Number.isSafeInteger(renderTimeoutMs)||renderTimeoutMs<1)throw Error('render-timeout-policy');
 if(!policy||typeof baseline!=='string'||!limits||['maxNodes','maxDepth','maxText','maxWidth','maxHeight','maxPixels','maxTotalPixels','maxImages'].some(k=>!Number.isSafeInteger(limits[k])||limits[k]<1))throw Error('client-configuration');
 if(!input||!Array.isArray(input.tree)||!input.images||Object.keys(input).some(k=>!['tree','images'].includes(k)))throw Error('render-input');
 const nonce=rendererNonce(configuration?.sandboxNonce);
 const token=crypto.randomUUID(),renderId=crypto.randomUUID();const links=new Map();
 const tree=[];let nodes=0,text=0;
 const stack=[{source:input.tree,target:tree,depth:0}];
 while(stack.length){
  const item=stack.pop();
  if(item.depth>limits.maxDepth)throw Error('tree-depth');
  for(const node of item.source){
   if(++nodes>limits.maxNodes)throw Error('tree-nodes');
   if(typeof node==='string'){text+=node.length;if(text>limits.maxText)throw Error('tree-text');item.target.push(node);continue;}
   if(!node||!policy.elements.includes(node.element)||!Array.isArray(node.children)||typeof node.nodeId!=='string'||Object.keys(node).some(k=>!['element','attributes','children','nodeId','navigation'].includes(k)))throw Error('tree-contract');
   text+=node.nodeId.length;
   if(node.attributes!==undefined&&(node.attributes===null||typeof node.attributes!=='object'||Array.isArray(node.attributes)))throw Error('attribute-contract');
   for(const [key,value]of Object.entries(node.attributes??{})){if(typeof value!=='string')throw Error('attribute-contract');text+=key.length+value.length;}
   if(node.navigation!==undefined){if(!node.navigation||typeof node.navigation.href!=='string')throw Error('navigation-contract');text+=node.navigation.href.length;}
   if(text>limits.maxText)throw Error('tree-text');
   const {navigation,...rest}=node;const output={...rest,children:[]};item.target.push(output);
   if(navigation){const valid=validateNavigationUrl(navigation.href);if(valid.state==='destination'){const id=crypto.randomUUID();links.set(id,valid);output.linkId=id;}}
   stack.push({source:node.children,target:output.children,depth:item.depth+1});
  }
 }
 let totalPixels=0,imageCount=0;
 for(const image of Object.values(input.images)){
  if(++imageCount>limits.maxImages)throw Error('image-count');
  if(image?.state!=='pixels'){if(image?.state!=='alt')throw Error('image-contract');continue;}
  const {width,height,rgba}=image;totalPixels+=width*height;
  if(!Number.isSafeInteger(width)||!Number.isSafeInteger(height)||width<1||height<1||width>limits.maxWidth||height>limits.maxHeight||width*height>limits.maxPixels||totalPixels>limits.maxTotalPixels||!Array.isArray(rgba)||rgba.length!==width*height*4||rgba.some(b=>!Number.isInteger(b)||b<0||b>255))throw Error('pixel-contract');
 }
 active?.dispose();
 const frame=document.createElement('iframe');frame.title='Message content';frame.sandbox='allow-scripts';frame.referrerPolicy='no-referrer';frame.style.cssText='width:100%;height:420px;border:1px solid;';
 const panel=document.createElement('section');panel.hidden=true;panel.setAttribute('aria-label','Link destination');
 const destination=document.createElement('p');const open=document.createElement('button');open.textContent='Open destination';
 const copyButton=document.createElement('button');copyButton.textContent='Copy destination';
 panel.append(destination,open,copyButton);
 let chosen,disposed=false,port,connected=false,loadCount=0;
 open.addEventListener('click',event=>{if(!event.isTrusted||!chosen)return;const valid=validateNavigationUrl(chosen.href);if(valid.state==='destination')window.open(valid.href,'_blank','noopener,noreferrer');});
 copyButton.addEventListener('click',()=>{if(chosen)navigator.clipboard?.writeText(chosen.href);});
 let loadResolve,loadReject,completeReject,timer;
 const loaded=new Promise((resolve,reject)=>{loadResolve=resolve;loadReject=reject;frame.onload=()=>{if(++loadCount>1){controller.dispose();return;}resolve();};frame.onerror=()=>reject(Error('frame-load'));});
 // Attach handlers immediately so disposal cannot create an unhandled rejection.
 loaded.catch(()=>{});
 // srcdoc consists entirely of client code/styles. Never interpolate the tree.
 const overrides='canvas.client-image{box-sizing:border-box!important;max-inline-size:100%!important;height:auto!important;display:inline-block}a[role=link]{color:LinkText!important;text-decoration-line:underline!important;cursor:pointer}.client-table{max-width:100%;overflow:auto}body{contain:layout paint style;isolation:isolate;overflow:auto} @media(forced-colors:active){*{color:CanvasText!important;background-color:Canvas!important}a[role=link]{color:LinkText!important}}';
 // Author-important beats permitted sender inline declarations, but remains below
 // genuine user-important rules in the browser cascade. No inline important styling.
 const fontOverride=fontFamily===undefined?'':`body,body *{font-family:${fontFamily}!important}`;
 const rootOverride=rootFontSizePx===undefined?'':`html{font-size:${rootFontSizePx}px!important}`;
 const lineOverride=lineHeightRatio===undefined?'':`body,body *{line-height:${lineHeightRatio}!important}`;
 const script='('+renderRuntime.toString()+')('+JSON.stringify(token)+');';
 const escapeStyle=s=>s.replace(/<\/style/gi,'<\\/style');
 frame.srcdoc=`<!doctype html><html lang=""><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none';script-src 'nonce-${nonce}';style-src 'unsafe-inline';connect-src 'none';img-src 'none';font-src 'none';media-src 'none';object-src 'none';frame-src 'none';worker-src 'none';base-uri 'none';form-action 'none'"><style nonce="${nonce}">${escapeStyle(baseline)}${overrides}${fontOverride}${rootOverride}${lineOverride}</style></head><body dir="ltr" tabindex="0" role="region" aria-label="Message content"><script nonce="${nonce}">${script}</script></body></html>`;
 let receiveReady;
 const completion=new Promise((resolve,reject)=>{
  completeReject=reject;timer=setTimeout(()=>{loadReject(Error('render-timeout'));reject(Error('render-timeout'));},renderTimeoutMs);
  receiveReady=event=>{
   const data=event.data;
   if(data?.kind!=='email-next-render-ready')return;
   const valid=!disposed&&!connected&&event.source===frame.contentWindow&&event.origin==='null'&&data.token===token&&Object.keys(data).length===2&&event.ports.length===1;
   if(!valid){for(const rejected of event.ports)rejected.close();return;}
   connected=true;port=event.ports[0];
   port.onmessage=({data})=>{
    if(disposed||!data)return;
    if(data.renderId===renderId&&['rendered','rejected'].includes(data.kind)){clearTimeout(timer);resolve(data.kind);}
    else if(data.renderId===renderId&&data.kind==='navigate'&&links.has(data.linkId)){
     chosen=links.get(data.linkId);destination.textContent=chosen.href+' — '+chosen.origin;panel.hidden=false;open.focus();
    }
   };port.start();
   const images={},transfers=[];for(const [id,image]of Object.entries(input.images)){
    images[id]={...image};if(image.state==='pixels'){const buffer=Uint8Array.from(image.rgba).buffer;images[id].rgba=buffer;transfers.push(buffer);}
   }
   port.postMessage({kind:'render',token,renderId,tree,images,policy,limits},transfers);
  };
  window.addEventListener('message',receiveReady);
 });
 completion.catch(()=>{});
 const controller={frame,panel,dispose(){if(disposed)return;disposed=true;clearTimeout(timer);loadReject(Error('disposed'));completeReject(Error('disposed'));frame.onload=null;frame.onerror=null;window.removeEventListener('message',receiveReady);port?.close();links.clear();frame.remove();panel.remove();}};
 active=controller;
 try{container.replaceChildren(frame,panel);await loaded;if(disposed)throw Error('disposed');controller.state=await completion;return controller;}
 catch(error){controller.dispose();throw error;}
}
