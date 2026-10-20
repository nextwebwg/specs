// Sequential actual-host geometry checks; no full UBA or painted-pixel conformance claim.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createServer} from 'node:http';
import {spawnSync} from 'node:child_process';
import {pathToFileURL,fileURLToPath} from 'node:url';
import path from 'node:path';
const here=path.dirname(fileURLToPath(import.meta.url));
if(!process.env.EMAIL_NEXT_PYTHON||!process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE)throw Error('Set EMAIL_NEXT_PYTHON and EMAIL_NEXT_PLAYWRIGHT_MODULE to existing runtimes');
const result=spawnSync(process.env.EMAIL_NEXT_PYTHON,[path.join(here,'browser-render-fixture.py')],{encoding:'utf8'});assert.equal(result.status,0,result.stderr);const config=JSON.parse(result.stdout);
const {chromium}=await import(pathToFileURL(process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE));
const server=createServer(async(req,res)=>{if(req.url==='/'){res.setHeader('Content-Type','text/html');res.end('<!doctype html><main></main><script type="module">import{mountMessage}from"/browser-render-host.mjs";window.mountMessage=mountMessage;</script>');return;}const file=req.url.slice(1);if(!['browser-render-host.mjs','browser-render-runtime.mjs','navigation-url.mjs'].includes(file))return res.writeHead(404).end();res.setHeader('Content-Type','text/javascript');res.end(await readFile(path.join(here,file)));});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const browser=await chromium.launch({headless:true});const records=[];
try{const page=await browser.newPage();await page.goto(`http://127.0.0.1:${server.address().port}`);await page.waitForFunction(()=>window.mountMessage);
for(const width of [150,260])for(const direction of ['ltr','rtl']){
 const opposite=direction==='ltr'?'rtl':'ltr';let id=0;const n=(element,children,attributes={})=>({element,children,attributes,nodeId:String(++id)});
 const tree=[n('p',[n('span',['alpha beta gamma delta epsilon zeta eta theta iota kappa'],{style:'padding-left:1rem;padding-right:1rem;border-style:solid'})],{dir:direction}),n('p',[n('span',['אבג abc אבג abc אבג abc אבג abc'],{dir:opposite,style:'padding-left:1rem;padding-right:1rem;border-style:solid'})],{dir:direction}),n('p',['L ',n('bdi',['אבג']), ' : R'],{dir:'ltr'}),n('p',[n('span',['a\u0301 a\u0301 a\u0301 a\u0301 a\u0301 a\u0301 a\u0301 a\u0301 a\u0301 a\u0301'])],{dir:direction})];
 await page.evaluate(async({tree,config,width})=>{document.querySelector('main').style.width=width+'px';window.c=await window.mountMessage(document.querySelector('main'),{tree,images:{}},{...config,fontFamily:'monospace'});},{tree,config,width});const frame=page.frames().find(f=>f.parentFrame());
 const metrics=await frame.evaluate(()=>{const ps=[...document.querySelectorAll('p')];const rect=r=>({x:r.x,y:r.y,w:r.width,h:r.height});const chars=e=>{const t=e.firstChild;return Array.from({length:t.length},(_,i)=>{const r=document.createRange();r.setStart(t,i);r.setEnd(t,i+1);return rect(r.getBoundingClientRect());});};return {width:innerWidth,plain:{boxes:[...ps[0].firstChild.getClientRects()].map(rect),chars:chars(ps[0].firstChild),padding:getComputedStyle(ps[0].firstChild).paddingLeft,border:getComputedStyle(ps[0].firstChild).borderLeftWidth,slice:getComputedStyle(ps[0].firstChild).boxDecorationBreak},mixed:{boxes:[...ps[1].firstChild.getClientRects()].map(rect),direction:getComputedStyle(ps[1].firstChild).direction},isolate:{chars:chars(ps[2].querySelector('bdi')),text:ps[2].textContent,unicodeBidi:getComputedStyle(ps[2].querySelector('bdi')).unicodeBidi},marks:chars(ps[3].firstChild)};});
 assert.ok(metrics.plain.boxes.length>1);assert.equal(metrics.plain.slice,'slice');assert.equal(metrics.mixed.direction,opposite);assert.ok(metrics.mixed.boxes.length>1);
 // Logical first Hebrew character is rightmost in the isolated RTL run; surrounding LTR text stays unchanged.
 assert.ok(metrics.isolate.chars[0].x>metrics.isolate.chars[1].x);assert.ok(metrics.isolate.chars[1].x>metrics.isolate.chars[2].x);assert.equal(metrics.isolate.unicodeBidi,'isolate');assert.equal(metrics.isolate.text,'L אבג : R');
 // A base and its combining accent occupy the same line even at wrap boundaries.
 for(let i=0;i<metrics.marks.length;i+=3){assert.equal(metrics.marks[i].y,metrics.marks[i+1].y);}
 // Slice adds inline-start/end edges only once, not fresh horizontal padding on every fragment.
 const edge=parseFloat(metrics.plain.padding)+parseFloat(metrics.plain.border);const boxes=metrics.plain.boxes;const cs=metrics.plain.chars;
 const first=cs.find(c=>c.w>0),last=[...cs].reverse().find(c=>c.w>0);
 if(direction==='ltr'){assert.ok(Math.abs(first.x-boxes[0].x-edge)<1);assert.ok(Math.abs(boxes.at(-1).x+boxes.at(-1).w-(last.x+last.w)-edge)<1);}
 else {assert.ok(Math.abs(boxes[0].x+boxes[0].w-(cs.filter(c=>c.y>=boxes[0].y&&c.y<boxes[0].y+boxes[0].h).reduce((v,c)=>Math.max(v,c.x+c.w),0))-edge)<1);}
 if(boxes.length>2){const middle=boxes[1];const glyph=cs.find(c=>c.y>=middle.y&&c.y<middle.y+middle.h&&c.w>0);assert.ok(glyph);assert.ok(Math.abs(glyph.x-middle.x)<1);}
 records.push({width,direction,...metrics});
}
assert.ok(records[0].plain.boxes.length>records[2].plain.boxes.length);if(process.env.EMAIL_NEXT_GEOMETRY_REPORT)await writeFile(process.env.EMAIL_NEXT_GEOMETRY_REPORT,JSON.stringify({browser:browser.version(),cases:records},null,2));console.log('4 host geometry cases passed',browser.version());
}finally{await browser.close();await new Promise(r=>server.close(r));}
