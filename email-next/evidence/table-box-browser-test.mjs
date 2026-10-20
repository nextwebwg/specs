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
let checks=0;const observations=[];
try {
 const page=await browser.newPage({viewport:{width:480,height:800},deviceScaleFactor:1});await page.goto(origin);await page.waitForFunction(()=>typeof window.mountMessage==='function');
 const n=(element,children=[],style='',attributes={})=>({element,children,attributes:{...attributes,...(style?{style}:{})}});
 const cell=(text,style='',attrs={})=>n('td',[text],style,attrs);
 async function mount(tree){let i=0;function ids(n){n.nodeId=String(++i);for(const c of n.children)if(typeof c!=='string')ids(c)}tree.forEach(ids);await page.evaluate(async({fixture,tree})=>{window.controller=await window.mountMessage(document.querySelector('#host'),{tree,images:{}},{policy:fixture.policy,baseline:fixture.baseline,limits:fixture.limits})},{fixture,tree});assert.equal(await page.evaluate(()=>window.controller.state),'rendered');return page.frames().find(f=>f.parentFrame());}
 const rect=async locator=>locator.evaluate(e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}});
 const near=(a,b,label)=>assert.ok(Math.abs(a-b)<0.1,label+': '+a+' vs '+b);
 // Adjacent positive margins collapse to their maximum; padding+border are additive.
 let frame=await mount([n('div',[n('p',['First'],'margin-bottom:1rem'),n('p',['Second'],'margin-top:1.5rem')]),n('div',['Box'],'padding-top:0.5rem;padding-bottom:0.5rem;border-width:3px;border-style:solid;border-color:#f00')]);
 let a=await rect(frame.locator('p').nth(0)),b=await rect(frame.locator('p').nth(1));near(b.y-a.bottom,24,'collapsed margins');
 const box=frame.locator('body>div').last();near((await rect(box)).height,46,'24px line plus padding and borders');checks++;
 // A child margin cannot collapse through parent padding/border.
 frame=await mount([n('div',[n('p',['Child'],'margin-top:1rem;margin-bottom:0')],'padding-top:0.5rem;border-width:2px;border-style:solid')]);
 near((await rect(frame.locator('p'))).y-(await rect(frame.locator('body>div'))).y,26,'blocked parent collapse');checks++;
 // Compare geometry with ignored internal-table margins/row padding and model-specific table padding.
 const table=(mode,extra='')=>n('table',[n('caption',['Caption']),n('tbody',[n('tr',[cell('A','border-width:1px;border-style:solid'),cell('B','border-width:1px;border-style:solid')],extra)])],'border-collapse:'+mode+';padding-left:1rem;padding-top:1rem');
 for(const mode of ['separate','collapse']){
  frame=await mount([table(mode)]);const before={table:await rect(frame.locator('table')),cells:await frame.locator('td').evaluateAll(es=>es.map(e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right}}))};
  frame=await mount([table(mode,'margin-top:2rem;margin-left:2rem;padding-top:2rem;padding-left:2rem')]);const after={table:await rect(frame.locator('table')),cells:await frame.locator('td').evaluateAll(es=>es.map(e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right}}))};assert.deepEqual(after,before,'row margins/padding do not change layout');
  near(after.cells[1].x-after.cells[0].right,mode==='separate'?2:0,'cell gap');
  const caption=await rect(frame.locator('caption'));assert.ok(caption.bottom<=after.cells[0].y,'caption above cells');
  near(after.cells[0].x-after.table.x,mode==='separate'?18:0.5,'table padding plus spacing / half collapsed border');
  near(after.cells[0].y-caption.bottom,mode==='separate'?18:0.5,'table top padding model');
  observations.push({mode,...after});checks++;
 }
 // Cell margins have no layout effect; retained spans occupy actual row/column grid space.
 frame=await mount([n('table',[n('tbody',[n('tr',[cell('A','', {rowspan:'2'}),cell('B')]),n('tr',[cell('C')]),n('tr',[cell('Across','',{colspan:'2'})])])])]);
 let cells=await frame.locator('td').all();const rs=await Promise.all(cells.map(rect));near(rs[0].x,rs[3].x,'span start');near(rs[1].right,rs[3].right,'colspan end');assert.ok(rs[0].height>rs[1].height);near(rs[1].x,rs[2].x,'rowspan displaces next-row cell');
 await cells[0].evaluate(e=>{for(const side of ['top','right','bottom','left'])e.style.setProperty('margin-'+side,'2rem')});assert.deepEqual(await Promise.all(cells.map(rect)),rs,'cell margins ignored');checks++;
 // Cell alignment applies to content, not inline middle's x-height rule.
 frame=await mount([n('table',[n('tbody',[n('tr',[n('td',['Tall',n('br'), 'second',n('br'),'third']),...['top','middle','bottom'].map(v=>n('td',[n('span',[v])],'vertical-align:'+v))])])])]);
 const aligned=await frame.locator('td span').all();const ys=await Promise.all(aligned.map(rect));assert.ok(ys[0].y<ys[1].y&&ys[1].y<ys[2].y,'actual top/middle/bottom text positions');near(ys[1].y-ys[0].y,ys[2].y-ys[1].y,'middle centered between top and bottom');checks++;
 // Painted collapsed edge uses the wider border, not merely the later declaration.
 for(const mode of ['collapse','separate']){
  frame=await mount([n('table',[n('tbody',[n('tr',[cell('A','border-width:3px;border-style:solid;border-color:#f00'),cell('B','border-width:1px;border-style:solid;border-color:#00f')])])],'border-collapse:'+mode)]);
  const left=await frame.locator('td').nth(0).boundingBox(),right=await frame.locator('td').nth(1).boundingBox();
  const point={x:Math.round(mode==='collapse'?right.x:right.x+0.25),y:Math.floor(right.y+right.height/2)};
  const png=await page.screenshot();const sample=spawnSync(process.env.EMAIL_NEXT_PYTHON,['-c','from PIL import Image;import io,sys,json; im=Image.open(io.BytesIO(sys.stdin.buffer.read())).convert("RGB"); print(json.dumps(im.getpixel((int(sys.argv[1]),int(sys.argv[2])))))',String(point.x),String(point.y)],{input:png});assert.equal(sample.status,0,sample.stderr.toString());const rgb=JSON.parse(sample.stdout);assert.deepEqual(rgb,mode==='collapse'?[255,0,0]:[0,0,255],'actual shared/right border pixel');observations.push({mode,point,rgb,left,right});checks++;
 }
 console.log(JSON.stringify({browser:browser.version(),checks,observations,screenReaderTested:false},null,2));
}finally{await browser.close();await new Promise(r=>server.close(r));}
