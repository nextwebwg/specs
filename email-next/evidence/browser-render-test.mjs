// Sequential, one Chromium instance. Reuses an explicit existing Playwright install.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createServer} from 'node:http';
import {spawnSync} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
import path from 'node:path';
const here=path.dirname(fileURLToPath(import.meta.url));
if(!process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE||!process.env.EMAIL_NEXT_PYTHON)throw Error('Set EMAIL_NEXT_PLAYWRIGHT_MODULE and EMAIL_NEXT_PYTHON to existing runtimes');
const {chromium}=await import(pathToFileURL(process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE));
const generated=spawnSync(process.env.EMAIL_NEXT_PYTHON,[path.join(here,'browser-render-fixture.py')],{encoding:'utf8',maxBuffer:2*1024*1024});
assert.equal(generated.status,0,generated.stderr);const fixture=JSON.parse(generated.stdout);
const requests=[];
const server=createServer(async(req,res)=>{
 requests.push({url:req.url,referer:req.headers.referer});
 if(req.url==='/'){res.setHeader('Content-Type','text/html');res.end('<!doctype html><html lang="en"><title>Client UI title</title><main id="host"></main><script type="module">import{mountMessage}from"/browser-render-host.mjs";window.mountMessage=mountMessage;</script>');return;}
 if(req.url==='/capture'){res.setHeader('Content-Type','text/html');res.end('<!doctype html><title>Destination</title>Opened');return;}
 const file=String(req.url).slice(1);
 if(!['browser-render-host.mjs','browser-render-runtime.mjs','navigation-url.mjs'].includes(file)){res.writeHead(404).end();return;}
 res.setHeader('Content-Type','text/javascript');res.end(await readFile(path.join(here,file)));
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const origin=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({headless:true});
let checks=0;
try{
 const context=await browser.newContext();const network=[];context.on('request',r=>network.push(r.url()));
 await context.route('**/*',route=>route.request().url().startsWith(origin+'/')?route.continue():route.abort());
 const page=await context.newPage();
 await page.goto(origin);await page.waitForFunction(()=>typeof window.mountMessage==='function');
 function alter(nodes){for(const n of nodes){if(typeof n==='string')continue;if(n.navigation)n.navigation={href:origin+'/capture',origin};alter(n.children);}}alter(fixture.tree);
 requests.length=0;network.length=0;
 await page.evaluate(async data=>{window.renderInput=data;window.controller=await window.mountMessage(document.querySelector('#host'),{tree:data.tree,images:data.images},{policy:data.policy,baseline:data.baseline,limits:data.limits});},fixture);
 assert.equal(await page.evaluate(()=>window.controller.state),'rendered');
 const frame=page.frames().find(f=>f.parentFrame());assert.ok(frame);
 assert.equal(await frame.locator('h2').textContent(),'Meeting <script>bad()</script>');
 assert.equal(await frame.evaluate(()=>window.senderExecuted),undefined);
 assert.equal(await frame.locator('script').count(),0); // runtime removes its own bootstrap on render
 assert.equal(await frame.locator('img,svg,iframe').count(),0);
 assert.deepEqual(requests,[]);assert.deepEqual(network,[]);checks++;
 assert.equal(await frame.locator('canvas[role=img]').getAttribute('aria-label'),'Blue square');
 assert.deepEqual(await frame.locator('canvas').evaluate(c=>Array.from(c.getContext('2d').getImageData(0,0,1,1).data)),[0,0,255,255]);
 assert.ok((await frame.locator('body').textContent()).includes('Missing picture'));
 assert.equal(await frame.locator('canvas').evaluate(c=>c.getBoundingClientRect().width<=document.documentElement.clientWidth),true);checks++;
 assert.equal(await frame.locator('ol').getAttribute('start'),'3');assert.equal(await frame.locator('th').getAttribute('scope'),'col');
 assert.equal(await frame.locator('body').getAttribute('dir'),'ltr');assert.equal(await frame.locator('div[lang=fr]').getAttribute('dir'),'rtl');
 const semantics=await frame.locator('body').ariaSnapshot();assert.ok(semantics.includes('heading'));assert.ok(semantics.includes('Blue square'));assert.ok(semantics.includes('columnheader'));
 if(process.env.EMAIL_NEXT_BROWSER_SCREENSHOT)await page.screenshot({path:process.env.EMAIL_NEXT_BROWSER_SCREENSHOT});
 assert.equal(await frame.locator('p').last().evaluate(e=>getComputedStyle(e).fontSize),'24px');checks++;
 const link=frame.getByRole('link');assert.equal(await link.getAttribute('href'),null);
 assert.equal(await link.evaluate(e=>getComputedStyle(e).textDecorationLine),'underline');
 await link.evaluate(e=>e.click());assert.equal(await page.getByLabel('Link destination').isVisible(),false);
 await page.evaluate(()=>{const c=new MessageChannel();window.controller.frame.contentWindow.postMessage({token:'wrong'},'*',[c.port2]);c.port1.postMessage({kind:'render',token:'wrong',tree:[]});c.port1.close();});
 assert.equal(await frame.locator('h2').count(),1);
 await link.focus();await page.keyboard.press('Enter');await page.getByRole('button',{name:'Open destination'}).waitFor();
 assert.ok(await page.getByLabel('Link destination').isVisible());assert.deepEqual(requests,[]);assert.deepEqual(network,[]);
 const newPagePromise=context.waitForEvent('page');await page.getByRole('button',{name:'Open destination'}).click();const opened=await newPagePromise;await opened.waitForLoadState();
 assert.equal(await opened.evaluate(()=>window.opener),null);assert.equal(await opened.evaluate(()=>document.referrer),'');
 assert.equal(requests.find(r=>r.url==='/capture')?.referer,undefined);await opened.close();checks++;
 await page.emulateMedia({forcedColors:'active'});assert.notEqual(await link.evaluate(e=>getComputedStyle(e).color),'rgb(255, 255, 255)');assert.equal(await link.evaluate(e=>getComputedStyle(e).textDecorationLine),'underline');
 await frame.locator('html').evaluate(e=>e.style.fontSize='200%');assert.equal(await frame.locator('h2').evaluate(e=>getComputedStyle(e).fontSize),'48px');
 assert.equal(await frame.locator('.client-table').getAttribute('tabindex'),'0');checks++;
 await page.evaluate(()=>window.postMessage({kind:'navigate',renderId:'forged',linkId:'forged'},'*'));
 const bad=structuredClone(fixture);bad.tree.push({element:'script',nodeId:'bad',children:['window.senderExecuted=true']});
 await page.evaluate(async data=>{window.oldFrame=window.controller.frame;try{window.controller=await window.mountMessage(document.querySelector('#host'),{tree:data.tree,images:data.images},{policy:data.policy,baseline:data.baseline,limits:data.limits});}catch{window.badRejected=true;}},bad);
 assert.equal(await page.evaluate(()=>window.badRejected),true);assert.equal(await page.evaluate(()=>window.oldFrame.isConnected),true);checks++;
 // Valid finite CSS values are sourced from the authoritative Python table.
 const allStyles=structuredClone(fixture);allStyles.tree=Object.entries(fixture.policy.keywords).flatMap(([k,v])=>v.split(' ').map((value,i)=>({element:'p',nodeId:k+i,children:['CSS contract'],attributes:{style:k+':'+value}})));
 await page.evaluate(async data=>{window.controller=await window.mountMessage(document.querySelector('#host'),{tree:data.tree,images:data.images},{policy:data.policy,baseline:data.baseline,limits:data.limits});},allStyles);
 assert.equal(await page.evaluate(()=>window.controller.state),'rendered');checks++;
 const direction=structuredClone(fixture);direction.tree=fixture.directionTree;
 await page.evaluate(async data=>{window.controller=await window.mountMessage(document.querySelector('#host'),{tree:data.tree,images:data.images},{policy:data.policy,baseline:data.baseline,limits:data.limits});},direction);
 const directional=page.frames().find(f=>f.parentFrame());
 assert.equal(await directional.locator('bdi').getAttribute('dir'),null);
 assert.equal(await directional.locator('bdi').evaluate(e=>getComputedStyle(e).direction),'ltr');
 const auto=directional.locator('div[dir=auto]');
 assert.equal(await auto.first().evaluate(e=>getComputedStyle(e).direction),'rtl');
 assert.equal(await auto.last().evaluate(e=>getComputedStyle(e).direction),'ltr');checks++;
 const defaultDirection=structuredClone(fixture);
 defaultDirection.tree=[{element:'p',nodeId:'unspecified',children:['שלום']},{element:'p',nodeId:'explicit',attributes:{dir:'auto'},children:['שלום']}];
 await page.evaluate(async data=>{window.controller=await window.mountMessage(document.querySelector('#host'),{tree:data.tree,images:data.images},{policy:data.policy,baseline:data.baseline,limits:data.limits});},defaultDirection);
 const defaults=page.frames().find(f=>f.parentFrame());
 assert.equal(await defaults.locator('p').first().evaluate(e=>getComputedStyle(e).direction),'ltr');
 assert.equal(await defaults.locator('p').last().evaluate(e=>getComputedStyle(e).direction),'rtl');checks++;
 // Actual glyph positions test paragraph-level pre direction, not just a CSS flag.
 const paragraphs=structuredClone(fixture);
 paragraphs.tree=[{element:'pre',nodeId:'paragraph-directions',attributes:{dir:'auto'},children:['שלום\nabc']}];
 await page.evaluate(async data=>{window.controller=await window.mountMessage(document.querySelector('#host'),{tree:data.tree,images:{}},{policy:data.policy,baseline:data.baseline,limits:data.limits});},paragraphs);
 const paragraphFrame=page.frames().find(f=>f.parentFrame());
 const positions=await paragraphFrame.locator('pre').evaluate(element=>{
   const text=element.firstChild;
   const position=index=>{const range=document.createRange();range.setStart(text,index);range.setEnd(text,index+1);const rect=range.getBoundingClientRect();return {x:rect.x,y:rect.y};};
   return [position(0),position(3),position(5),position(7)];
 });
 assert.ok(positions[0].x>positions[1].x,'Hebrew paragraph reads right to left');
 assert.ok(positions[2].x<positions[3].x,'Latin paragraph reads left to right');
 assert.ok(positions[2].y>positions[0].y,'Newline retains a separate paragraph');checks++;
 // A wide native table remains a named, keyboard-scrollable region.
 const wideTable=structuredClone(fixture);
 wideTable.tree=[{element:'table',nodeId:'keyboard-table',children:[{element:'tbody',nodeId:'keyboard-body',children:[{element:'tr',nodeId:'keyboard-row',children:Array.from({length:120},(_,i)=>({element:'td',nodeId:'keyboard-cell-'+i,children:['Column '+i]}))}]}]}];
 await page.evaluate(async data=>{window.controller=await window.mountMessage(document.querySelector('#host'),{tree:data.tree,images:{}},{policy:data.policy,baseline:data.baseline,limits:data.limits});},wideTable);
 const tableFrame=page.frames().find(f=>f.parentFrame());
 const region=tableFrame.getByRole('region',{name:'Message table'});
 assert.ok(await region.evaluate(e=>e.scrollWidth>e.clientWidth));
 await region.focus();await page.keyboard.press('ArrowRight');
 await tableFrame.waitForFunction(()=>document.querySelector('.client-table').scrollLeft>0);
 assert.ok(await region.evaluate(e=>e===document.activeElement));
 assert.equal(await tableFrame.locator('table').count(),1);checks++;
 // An optional client preference overrides sender descendant fonts, including code.
 const fonts=structuredClone(fixture);
 fonts.tree=[{element:'div',nodeId:'font-parent',attributes:{style:'font-family:serif'},children:[{element:'span',nodeId:'font-child',attributes:{style:'font-family:sans-serif'},children:['Readable text']},{element:'code',nodeId:'font-code',children:['code']}]}];
 async function renderFonts(preference){await page.evaluate(async({data,preference})=>{window.controller=await window.mountMessage(document.querySelector('#host'),{tree:data.tree,images:{}},{policy:data.policy,baseline:data.baseline,limits:data.limits,...preference});},{data:fonts,preference});return page.frames().find(f=>f.parentFrame());}
 const noPreference=await renderFonts({});
 assert.equal(await noPreference.locator('div').evaluate(e=>getComputedStyle(e).fontFamily),'serif');
 assert.equal(await noPreference.locator('span').evaluate(e=>getComputedStyle(e).fontFamily),'sans-serif');
 assert.equal(await noPreference.locator('code').evaluate(e=>getComputedStyle(e).fontFamily),'monospace');
 const preferred=await renderFonts({fontFamily:'system-ui'});
 for(const tag of ['body','div','span','code'])assert.equal(await preferred.locator(tag).evaluate(e=>getComputedStyle(e).fontFamily),'system-ui');
 // The override stays in an author stylesheet, never inline important.
 assert.equal(await preferred.locator('span').evaluate(e=>e.style.getPropertyPriority('font-family')),'');
 for(const value of ['serif; color:red','url(https://example.test/font)',null,{},'Arial'])await assert.rejects(()=>renderFonts({fontFamily:value}));
 assert.equal(await preferred.locator('span').evaluate(e=>getComputedStyle(e).fontFamily),'system-ui');
 const restored=await renderFonts({});assert.equal(await restored.locator('span').evaluate(e=>getComputedStyle(e).fontFamily),'sans-serif');checks++;
 // Root-size preference belongs to the client; nested rem values share that root.
 const rootInput=structuredClone(fixture);
 rootInput.tree=[{element:'div',nodeId:'sized-parent',attributes:{style:'font-size:2rem;padding-left:2rem'},children:[{element:'div',nodeId:'sized-child',attributes:{style:'font-size:2rem;padding-left:2rem'},children:[{element:'span',nodeId:'inherited',children:['Nested '+ 'longtext'.repeat(100)]}]},{element:'h2',nodeId:'sized-heading',children:['Heading']}]}];
 const parentMetrics=await page.evaluate(()=>({font:getComputedStyle(document.documentElement).fontSize,width:document.documentElement.scrollWidth}));
 async function renderRoot(preference){await page.evaluate(async({data,preference})=>{window.controller=await window.mountMessage(document.querySelector('#host'),{tree:data.tree,images:{}},{policy:data.policy,baseline:data.baseline,limits:data.limits,...preference});},{data:rootInput,preference});return page.frames().find(f=>f.parentFrame());}
 const initialRoot=await renderRoot({});const browserRoot=await initialRoot.locator('html').evaluate(e=>getComputedStyle(e).fontSize);
 for(const size of [16,24,40,64]){
  const sized=await renderRoot({rootFontSizePx:size});
  assert.equal(await sized.locator('html').evaluate(e=>getComputedStyle(e).fontSize),size+'px');
  for(const item of await sized.locator('div').all()){
   assert.equal(await item.evaluate(e=>getComputedStyle(e).fontSize),size*2+'px');
   assert.equal(await item.evaluate(e=>getComputedStyle(e).paddingLeft),size*2+'px');
  }
  assert.equal(await sized.locator('span').evaluate(e=>getComputedStyle(e).fontSize),size*2+'px');
  assert.equal(await sized.locator('h2').evaluate(e=>getComputedStyle(e).fontSize),size*1.5+'px');
  assert.equal(await sized.locator('html').evaluate(e=>e.style.getPropertyPriority('font-size')),'');
 }
 checks++;
 // Invalid preference never replaces the current frame; trusted clients may adjust defaults.
 const oldRootFrame=await page.evaluate(()=>window.controller.frame.getAttribute('srcdoc'));
 for(const value of [0,-1,7,65,NaN,Infinity,'24',null,{},'24px;display:none'])await assert.rejects(()=>renderRoot({rootFontSizePx:value}));
 for(const range of [{min:0,max:64},{min:40,max:20},{min:8,max:Infinity},{min:8,max:64,extra:true}])await assert.rejects(()=>renderRoot({rootFontSizePx:24,rootFontSizeRange:range}));
 assert.equal(await page.evaluate(()=>window.controller.frame.getAttribute('srcdoc')),oldRootFrame);
 const adjusted=await renderRoot({rootFontSizePx:80,rootFontSizeRange:{min:8,max:96}});
 assert.equal(await adjusted.locator('html').evaluate(e=>getComputedStyle(e).fontSize),'80px');
 const outer=await page.evaluate(()=>({font:getComputedStyle(document.documentElement).fontSize,width:document.documentElement.scrollWidth,height:window.controller.frame.getBoundingClientRect().height,sandbox:window.controller.frame.getAttribute('sandbox')}));
 assert.equal(outer.font,parentMetrics.font);assert.equal(outer.width,parentMetrics.width);assert.equal(outer.height,422);assert.equal(outer.sandbox,'allow-scripts');
 assert.ok(['content','layout paint style'].includes(await adjusted.locator('body').evaluate(e=>getComputedStyle(e).contain)));
 assert.equal(await adjusted.locator('script,iframe').count(),0);
 assert.equal(await adjusted.evaluate(()=>document.documentElement.scrollHeight>innerHeight),true);
 const resetRoot=await renderRoot({});assert.equal(await resetRoot.locator('html').evaluate(e=>getComputedStyle(e).fontSize),browserRoot);checks++;
 // Unitless line height inherits as a ratio, and a client preference wins on descendants.
 const lineInput=structuredClone(fixture);
 lineInput.tree=[{element:'div',nodeId:'line-parent',attributes:{style:'font-size:1rem;line-height:1.25'},children:[{element:'span',nodeId:'line-inherit',attributes:{style:'font-size:2rem'},children:['Larger text']},{element:'p',nodeId:'line-own',attributes:{style:'font-size:1rem;line-height:1'},children:['Tight sender spacing']}]}];
 async function renderLines(preference){await page.evaluate(async({data,preference})=>{window.controller=await window.mountMessage(document.querySelector('#host'),{tree:data.tree,images:{}},{policy:data.policy,baseline:data.baseline,limits:data.limits,rootFontSizePx:16,...preference});},{data:lineInput,preference});return page.frames().find(f=>f.parentFrame());}
 const ordinaryLines=await renderLines({});
 assert.equal(await ordinaryLines.locator('div').evaluate(e=>getComputedStyle(e).lineHeight),'20px');
 assert.equal(await ordinaryLines.locator('span').evaluate(e=>getComputedStyle(e).lineHeight),'40px');
 assert.equal(await ordinaryLines.locator('p').evaluate(e=>getComputedStyle(e).lineHeight),'16px');
 const spaced=await renderLines({lineHeightRatio:2});
 for(const tag of ['body','div','p'])assert.equal(await spaced.locator(tag).evaluate(e=>getComputedStyle(e).lineHeight),'32px');
 assert.equal(await spaced.locator('span').evaluate(e=>getComputedStyle(e).lineHeight),'64px');
 assert.equal(await spaced.locator('p').evaluate(e=>e.style.getPropertyPriority('line-height')),'');
 const lineFrame=await page.evaluate(()=>window.controller.frame.getAttribute('srcdoc'));
 for(const value of [0,-1,4,NaN,Infinity,'2',null,{},'2;display:none'])await assert.rejects(()=>renderLines({lineHeightRatio:value}));
 for(const range of [{min:0,max:3},{min:3,max:1},{min:1,max:Infinity},{min:1,max:3,extra:true}])await assert.rejects(()=>renderLines({lineHeightRange:range}));
 assert.equal(await page.evaluate(()=>window.controller.frame.getAttribute('srcdoc')),lineFrame);
 const largerLines=await renderLines({lineHeightRatio:4,lineHeightRange:{min:1,max:4}});
 assert.equal(await largerLines.locator('span').evaluate(e=>getComputedStyle(e).lineHeight),'128px');
 const resetLines=await renderLines({});assert.equal(await resetLines.locator('p').evaluate(e=>getComputedStyle(e).lineHeight),'16px');checks++;
 const palette=structuredClone(fixture);palette.tree=[{element:'blockquote',nodeId:'palette',attributes:{style:'color:#abc;background-color:#abcdef;border-color:#123456'},children:[{element:'span',nodeId:'transparent',attributes:{style:'background-color:transparent'},children:['Palette']}]}];
 await page.emulateMedia({forcedColors:'none',colorScheme:'light'});
 await page.evaluate(async data=>{window.controller=await window.mountMessage(document.querySelector('#host'),{tree:data.tree,images:{}},{policy:data.policy,baseline:data.baseline,limits:data.limits});},palette);
 assert.equal(await page.evaluate(()=>window.controller.state),'rendered');
 const paletteFrame=page.frames().find(f=>f.parentFrame());
 for(const colorScheme of ['light','dark']){
  await page.emulateMedia({forcedColors:'none',colorScheme});
  const colors=await paletteFrame.evaluate(()=>{const e=getComputedStyle(document.querySelector('blockquote')),b=getComputedStyle(document.body);return [e.color,e.backgroundColor,e.borderLeftColor,getComputedStyle(document.querySelector('span')).backgroundColor,b.color===b.backgroundColor];});
  assert.deepEqual(colors,['rgb(170, 187, 204)','rgb(171, 205, 239)','rgb(18, 52, 86)','rgba(0, 0, 0, 0)',false]);
 }
 await page.emulateMedia({forcedColors:'active'});
 assert.equal(await paletteFrame.evaluate(()=>getComputedStyle(document.querySelector('blockquote')).color===getComputedStyle(document.body).color),true);
 checks++;
 const wrapping=structuredClone(fixture);wrapping.tree=[{element:'p',nodeId:'wrap',attributes:{style:'overflow-wrap:anywhere'},children:['x'.repeat(300)]},{element:'p',nodeId:'no-wrap',attributes:{style:'overflow-wrap:normal'},children:['y'.repeat(300)]},{element:'pre',nodeId:'pre-text',children:['a  b\nc\td']}];
 await page.evaluate(async data=>{window.controller=await window.mountMessage(document.querySelector('#host'),{tree:data.tree,images:{}},{policy:data.policy,baseline:data.baseline,limits:data.limits});window.controller.frame.style.width='160px';},wrapping);
 const wrapFrame=page.frames().find(f=>f.parentFrame());
 const wrapObserved=await wrapFrame.evaluate(()=>{const [a,b]=document.querySelectorAll('p'),body=document.body;return {wrapped:a.scrollWidth<=a.clientWidth,normalOverflows:b.scrollWidth>b.clientWidth,pre:document.querySelector('pre').textContent,overflow:getComputedStyle(body).overflow,contain:getComputedStyle(body).contain};});
 assert.deepEqual(wrapObserved,{wrapped:true,normalOverflows:true,pre:'a  b\nc\td',overflow:'auto',contain:'content'});
 await wrapFrame.getByRole('region',{name:'Message content',exact:true}).focus();
 await page.keyboard.press('ArrowRight');
 await wrapFrame.waitForFunction(()=>document.body.scrollLeft>0);
 assert.equal(await page.evaluate(()=>document.querySelector('#host iframe').clientWidth),160);checks++;
 const lifecycle=await page.evaluate(async()=>{
  const data=window.renderInput;const config={policy:data.policy,baseline:data.baseline,limits:data.limits};
  const input={tree:data.tree,images:data.images};const container=document.querySelector('#host');
  const one=window.mountMessage(container,input,config);const two=window.mountMessage(container,input,config);
  const result=await Promise.allSettled([one,two]);
  window.controller=result[1].value;
  let root={element:'div',nodeId:'deep',children:[]},cursor=root;
  for(let i=0;i<1500;i++){const next={element:'div',nodeId:String(i),children:[]};cursor.children.push(next);cursor=next;}
  let deep=false,pixels=false;
  try{await window.mountMessage(container,{tree:[root],images:{}},config);}catch{deep=true;}
  try{await window.mountMessage(container,{tree:[],images:{bad:{state:'pixels',width:999999,height:999999,rgba:[]}}},config);}catch{pixels=true;}
  return {states:result.map(r=>r.status),deep,pixels,frames:container.querySelectorAll('iframe').length};
 });
 assert.deepEqual(lifecycle,{states:['rejected','fulfilled'],deep:true,pixels:true,frames:1});checks++;
 const timeoutCleanup=await page.evaluate(async()=>{
  const original=Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype,'srcdoc');
  Object.defineProperty(HTMLIFrameElement.prototype,'srcdoc',{...original,set(){}});
  try{
   const data=window.renderInput;let rejected=false;
   try{await window.mountMessage(document.querySelector('#host'),{tree:data.tree,images:data.images},{policy:data.policy,baseline:data.baseline,limits:data.limits,renderTimeoutMs:30});}catch{rejected=true;}
   return {rejected,frames:document.querySelectorAll('#host iframe').length};
  }finally{Object.defineProperty(HTMLIFrameElement.prototype,'srcdoc',original);}
 });
 assert.deepEqual(timeoutCleanup,{rejected:true,frames:0});checks++;
 const handshake=await page.evaluate(async()=>{
  const data=window.renderInput,host=document.querySelector('#host'),closed=new Set(),originalClose=MessagePort.prototype.close;
  MessagePort.prototype.close=function(){closed.add(this);return originalClose.call(this);};
  const attempted=[];let observed;
  const attack=(ready,overrides={},count=1)=>{
   const channels=Array.from({length:count},()=>new MessageChannel());const ports=channels.map(c=>c.port2);attempted.push(...ports);
   window.dispatchEvent(new MessageEvent('message',{data:ready.data,origin:ready.origin,source:ready.source,ports,...overrides}));
   for(const c of channels)c.port1.close();
  };
  const observe=event=>{
   if(event.data?.kind!=='email-next-render-ready'||observed)return;observed=event;
   attack(event,{source:window});attack(event,{origin:location.origin});attack(event,{data:{kind:event.data.kind,token:'wrong'}});
   attack(event,{data:{...event.data,extra:true}});attack(event,{},2);
  };
  window.addEventListener('message',observe);
  try{
   const controller=await window.mountMessage(host,{tree:data.tree,images:data.images},{policy:data.policy,baseline:data.baseline,limits:data.limits});
   attack(observed);const repeatedClosed=attempted.every(p=>closed.has(p));
   const old=observed;observed=undefined;
   window.removeEventListener('message',observe);
   const stale=event=>{if(event.isTrusted&&event.data?.kind==='email-next-render-ready')attack(old);};window.addEventListener('message',stale);
   const replacement=await window.mountMessage(host,{tree:data.tree,images:data.images},{policy:data.policy,baseline:data.baseline,limits:data.limits});window.removeEventListener('message',stale);
   const staleClosed=attempted.every(p=>closed.has(p));replacement.dispose();
   return {state:controller.state,replacement:replacement.state,repeatedClosed,staleClosed,frames:host.querySelectorAll('iframe').length};
  }finally{window.removeEventListener('message',observe);MessagePort.prototype.close=originalClose;}
 });
 assert.deepEqual(handshake,{state:'rendered',replacement:'rendered',repeatedClosed:true,staleClosed:true,frames:0});checks++;
 const navigation=await page.evaluate(async()=>{
  const data=window.renderInput,host=document.querySelector('#host'),config={policy:data.policy,baseline:data.baseline,limits:data.limits,renderTimeoutMs:150};
  const controller=await window.mountMessage(host,{tree:data.tree,images:data.images},config);
  controller.frame.srcdoc='<p>Replacement document</p>';await new Promise(resolve=>setTimeout(resolve,60));const after=!controller.frame.isConnected;
  let diverted=false;const intercept=event=>{if(event.data?.kind!=='email-next-render-ready'||diverted)return;diverted=true;event.stopImmediatePropagation();for(const port of event.ports)port.close();host.querySelector('iframe').srcdoc='<p>No message content here</p>';};
  window.addEventListener('message',intercept);let before=false;
  try{await window.mountMessage(host,{tree:data.tree,images:data.images},config);}catch{before=true;}finally{window.removeEventListener('message',intercept);}
  return {after,before,frames:host.querySelectorAll('iframe').length};
 });
 assert.deepEqual(navigation,{after:true,before:true,frames:0});checks++;
 console.log(JSON.stringify({browser:browser.version(),checks,workers:1,screenReaderTested:false,nativeZoomTested:false}));
 await context.close();
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
