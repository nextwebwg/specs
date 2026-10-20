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
const observations=[];
try {
 const page=await browser.newPage();await page.goto(origin);await page.waitForFunction(()=>window.mountMessage);
 for(const width of [240,320])for(const dir of ['ltr','rtl'])for(const size of [16,32]){
 const image=structuredClone(fixture.tree[0].children.find(n=>n.element==='img'));
 image.attributes.style='padding-left:2rem;padding-right:2rem;border-width:3px;border-style:solid';
 await page.evaluate(async({fixture,image,width,dir,size})=>{
 window.controller=await window.mountMessage(document.querySelector('#host'),{tree:[{element:'div',nodeId:'900',attributes:{dir},children:[image]}],images:fixture.images},{policy:fixture.policy,baseline:fixture.baseline,limits:fixture.limits,rootFontSizePx:size});window.controller.frame.style.width=width+'px';
 },{fixture,image,width,dir,size});
 const frame=page.frames().find(f=>f.parentFrame());
 const result=await frame.locator('canvas').evaluate(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {left:r.left,right:r.right,width:r.width,viewport:document.documentElement.clientWidth,padding:parseFloat(s.paddingLeft),border:parseFloat(s.borderLeftWidth)}});
 observations.push({frameWidth:width,dir,size,...result});
 assert.equal(result.padding,2*size);assert.equal(result.border,3);
 if(!process.env.EMAIL_NEXT_OBSERVE_ONLY){assert.ok(result.left>=-0.5&&result.right<=result.viewport+0.5,JSON.stringify(observations.at(-1)));}
 }
 console.log(JSON.stringify({browser:browser.version(),cases:observations.length,observations},null,2));
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
