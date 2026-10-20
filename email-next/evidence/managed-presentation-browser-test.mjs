// Run sequentially with an explicitly configured existing Playwright installation.
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import assert from 'node:assert/strict';
if(!process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE||!process.env.EMAIL_NEXT_PYTHON)throw Error('Configure EMAIL_NEXT_PLAYWRIGHT_MODULE and EMAIL_NEXT_PYTHON');
const result=spawnSync(process.env.EMAIL_NEXT_PYTHON,['-c',`import json
from test_managed_presentation_lifecycle import ManagedPresentation
from managed_presentation import describe,provisional
t=ManagedPresentation();t.setUp()
try:
 e,w,r,c=t.deliver()
 print(json.dumps(dict(accepted=describe(t.peer_sender.receiver,r,carrier=c,transport_wire=w),provisional=provisional(w))))
finally:t.tearDown()`],{encoding:'utf8',env:{...process.env,PYTHONPATH:new URL('.',import.meta.url).pathname},timeout:120000,maxBuffer:2000000});
if(result.status!==0)throw Error(result.stderr||'Fixture failed');
const fixture=JSON.parse(result.stdout);const source=await readFile(new URL('./managed-presentation-ui.mjs',import.meta.url));
const server=createServer((req,res)=>{if(req.url==='/ui.mjs'){res.setHeader('Content-Type','text/javascript');res.end(source);}else if(req.url==='/'){res.setHeader('Content-Type','text/html');res.end('<!doctype html><main id="view"></main>');}else{res.statusCode=404;res.end();}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const {chromium}=await import(process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE);let browser;
try{
 browser=await chromium.launch({headless:true});const page=await browser.newPage();await page.goto(`http://127.0.0.1:${server.address().port}/`);
 const render=async value=>page.evaluate(async value=>{const {mountPresentation}=await import('/ui.mjs');mountPresentation(document.querySelector('main'),value);},value);
 await render(fixture.accepted);assert.equal(await page.locator('h2').textContent(),'Confidential roadmap 📨');assert.match(await page.locator('main').textContent(),/18446744073709551615/);assert.equal(await page.locator('details').getAttribute('open'),null);
 const injected=structuredClone(fixture.accepted);injected.subject='<img src="/leak" onerror="alert(1)">';await render(injected);assert.equal(await page.locator('h2').textContent(),injected.subject);assert.equal(await page.locator('img').count(),0);
 await page.locator('summary').focus();await page.keyboard.press('Enter');assert.notEqual(await page.locator('details').getAttribute('open'),null);
 await render(fixture.provisional);assert.equal(await page.locator('h2').count(),0);assert.match(await page.locator('main').textContent(),/no reply or action/);
 console.log('4 managed presentation browser groups passed; fixture used actual SMTP acceptance. No assistive-technology certification.');
}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
