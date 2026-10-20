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
const server=createServer(async(req,res)=>{
 if(req.url==='/'){res.setHeader('Content-Type','text/html');res.end('<!doctype html><html lang="en"><title>Client UI title</title><main id="host"></main><script type="module">import{mountMessage}from"/browser-render-host.mjs";window.mountMessage=mountMessage;</script>');return;}
 const file=String(req.url).slice(1);
 if(!['browser-render-host.mjs','browser-render-runtime.mjs','navigation-url.mjs'].includes(file)){res.writeHead(404).end();return;}
 res.setHeader('Content-Type','text/javascript');res.end(await readFile(path.join(here,file)));
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const origin=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({headless:true});
let report=[];
try {
 const page=await browser.newPage({viewport:{width:320,height:800}});await page.goto(origin);await page.waitForFunction(()=>typeof window.mountMessage==='function');
 const item=(text,attributes={},children=[])=>({element:'li',attributes,children:[text,...children]});
 const list=(attributes,children,element='ol')=>({element,attributes,children});
 const cases=[
 ['ascending',list({},[item('one'),item('two')]),['1. ','2. ']],
 ['start-value',list({start:'7'},[item('seven'),item('minus',{value:'-2'}),item('minus one')]),['7. ','-2. ','-1. ']],
 ['reversed',list({reversed:''},[item('three'),item('two'),item('one')]),['3. ','2. ','1. ']],
 ['reversed-start',list({reversed:'',start:'-1'},[item('minus one'),item('value',{value:'4'}),item('three')]),['-1. ','4. ','3. ']],
 ['nested',list({},[item('outer',{},[list({},[item('inner')])]),item('next')]),['1. ','1. ','2. ']],
 ['bullets',list({},[item('disc',{},[list({},[item('circle',{},[list({},[item('square')],'ul')])],'ul')])],'ul'),['• ','◦ ','■ ']],
 ['upper-bound',list({start:'2147483647'},[item('largest')]),['2147483647. ']],
 ['lower-bound',list({start:'-2147483648'},[item('smallest')]),['-2147483648. ']],
 ['rtl-upper-bound',list({dir:'rtl',start:'2147483647'},[item('שלום')]),['. 2147483647']],
 ['rtl-lower-bound',list({dir:'rtl',start:'-2147483648'},[item('שלום')]),['. 2147483648-']],
 ['wrapped',list({},[item('A long line of readable text '.repeat(20))]),['1. ']],
 ['block-empty',list({},[item('',{},[{element:'p',children:['Block child']}]),item('')]),['1.','2.']],
 ['rtl',list({dir:'rtl',start:'123'},[item('שלום')]),['. 123']],
 ];
 for(const [name,tree,expected] of cases){
  let counter=0;function ids(n){n.nodeId=String(++counter);for(const x of n.children)if(typeof x!=='string')ids(x)}ids(tree);
  await page.evaluate(async({fixture,tree})=>{window.controller=await window.mountMessage(document.querySelector('#host'),{tree:[tree],images:{}},{policy:fixture.policy,baseline:fixture.baseline,limits:fixture.limits})},{fixture,tree});
  const frame=page.frames().find(f=>f.parentFrame());
  for(const enlarged of [false,true])for(const forcedColors of [false,true]){
   await page.emulateMedia({forcedColors:forcedColors?'active':'none'});
   await frame.locator('html').evaluate((e,large)=>e.style.fontSize=large?'200%':'100%',enlarged);
   const c=await page.context().newCDPSession(page);const ft=await c.send('Page.getFrameTree');const child=ft.frameTree.childFrames[0].frame.id;
   const ax=await c.send('Accessibility.getFullAXTree',{frameId:child});const byId=new Map(ax.nodes.map(n=>[n.nodeId,n]));const markers=[];function walk(id){const n=byId.get(id);if(!n)return;if(n.role?.value==='ListMarker')markers.push(n);for(const child of n.childIds||[])walk(child)}walk(ax.nodes[0].nodeId);
   const names=markers.map(n=>n.name.value); // Native generated marker content, not guessed from attributes.
   // AX text omits collapsible suffix space at a line boundary (before digits in RTL).
   assert.deepEqual(names.map(x=>x.replaceAll(' ','')),expected.map(x=>x.replaceAll(' ','')),name);
   const boxes=[];for(const n of markers){const {model}=await c.send('DOM.getBoxModel',{backendNodeId:n.backendDOMNodeId});boxes.push(model.border)}
   const bounds=await frame.locator('body').evaluate(e=>{const r=e.getBoundingClientRect();return {left:r.left,right:r.right,width:document.documentElement.clientWidth}});
   const frameBox=await page.locator('iframe').boundingBox();
   for(const box of boxes){assert.ok(Math.min(box[0],box[2],box[4],box[6])>=frameBox.x+bounds.left-1,name+' marker left clipping');assert.ok(Math.max(box[0],box[2],box[4],box[6])<=frameBox.x+bounds.right+1,name+' marker right clipping');}
   const styles=await frame.locator('li').evaluateAll(es=>es.map(e=>({marker:getComputedStyle(e,'::marker').color,text:getComputedStyle(e).color,background:getComputedStyle(document.body).backgroundColor,position:getComputedStyle(e).listStylePosition})));
   for(const style of styles){assert.equal(style.position,'inside');assert.equal(style.marker,style.text);assert.notEqual(style.marker,style.background);}
   if(name==='wrapped'){const r=await frame.locator('li').evaluate(e=>({height:e.getBoundingClientRect().height,line:parseFloat(getComputedStyle(e).lineHeight)}));assert.ok(r.height>r.line*2,'text actually wraps');}
   if(name==='block-empty'){const p=await frame.locator('p').boundingBox();assert.ok(p.y>=boxes[0][5]-1,'block child follows marker line');assert.ok(boxes[1][2]>boxes[1][0],'empty item retains nonempty marker box');}
   report.push({name,enlarged,forcedColors,names,boxes,bounds,styles});await c.detach();
  }
 }
 console.log(JSON.stringify({browser:browser.version(),report},null,2));
} finally {await browser.close();await new Promise(r=>server.close(r));}
