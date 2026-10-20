import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import {pathToFileURL,fileURLToPath} from 'node:url';
if(!process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE||!process.env.EMAIL_NEXT_PYTHON)throw Error('Existing runtimes required');
const child=spawn(process.env.EMAIL_NEXT_PYTHON,[fileURLToPath(new URL('./hosted-browser-fixture.py',import.meta.url))],{stdio:['pipe','pipe','inherit']});
const lines=createInterface({input:child.stdout});const fixture=JSON.parse(await new Promise(resolve=>lines.once('line',resolve)));
const {chromium}=await import(pathToFileURL(process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE));
// Pin only this ephemeral fixture certificate. This is not public CA validation evidence.
const browser=await chromium.launch({headless:true,...(process.env.EMAIL_NEXT_CHROMIUM_EXECUTABLE?{executablePath:process.env.EMAIL_NEXT_CHROMIUM_EXECUTABLE}:{}),args:['--host-resolver-rules=MAP host.example 127.0.0.1, MAP other.example 127.0.0.1','--ignore-certificate-errors-spki-list='+fixture.spki,'--no-proxy-server']});
try{
 const context=await browser.newContext();const page=await context.newPage();const requests=[];page.on('request',r=>requests.push(r));
 await page.goto(fixture.url);await page.waitForFunction(()=>location.hash==='');
 assert.equal(requests.filter(r=>r.url().includes('/content')).length,0);
 assert.deepEqual(await page.evaluate(()=>[localStorage.length,sessionStorage.length]),[0,0]);
 await page.getByRole('button',{name:'Open contribution',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#content').textContent.includes('CONFIDENTIAL_CONTENT_MARKER'));
 if(fixture.question){
  const text=await page.locator('#content').textContent();
  for(const expected of ['日本語','1. <img src=x onerror=alert(1)> 朝','2. Evening & late','Opening this message submits nothing.','Author-declared external sharing:'])assert.ok(text.includes(expected));
  assert.equal(await page.locator('#content img').count(),0);assert.equal(await page.locator('#content script').count(),0);
 }
 const fetch=requests.find(r=>r.url().endsWith('/content'));assert.equal(fetch.headers().authorization,'Bearer '+fixture.url.split('#')[1]);assert.ok(!fetch.headers().referer);
 await page.route('**/replies',route=>route.fulfill({status:413,body:''}));
 await page.getByRole('textbox',{name:'Reply'}).fill('Keep this oversized draft');await page.getByRole('button',{name:'Send holder reply'}).click();
 await page.waitForFunction(()=>document.querySelector('#status').textContent==='Reply is too large. Shorten it and try again.');
 assert.equal(await page.getByRole('textbox',{name:'Reply'}).inputValue(),'Keep this oversized draft');
 await page.unroute('**/replies');
 await page.getByRole('textbox',{name:'Reply'}).fill('Browser holder reply');await page.getByRole('button',{name:'Send holder reply'}).click();await page.waitForFunction(()=>document.querySelector('#status').textContent==='Reply stored from grant holder');
 assert.equal(requests.filter(r=>r.url().endsWith('/replies')).length,2);
 assert.ok(requests.every(r=>r.url().startsWith(fixture.origin)));assert.ok(requests.every(r=>!r.url().includes(fixture.url.split('#')[1])));
 await page.reload();assert.equal(await page.getByRole('button',{name:'Open contribution',exact:true}).isDisabled(),true);
 // Browser navigation regression: deliberately broken entry deployments leak/inherit
 // fragments before application code. Intercepted fixture responses use no external network.
 for(const cross of [false,true])for(const fragment of ['', '#', '#replacement']){
  const probe=await context.newPage();const destination=(cross?'https://other.example:'+new URL(fixture.origin).port:fixture.origin)+'/destination'+fragment;
  await probe.route('**/*',route=>route.request().url().includes('/g/')?route.fulfill({status:302,headers:{location:destination},body:''}):route.fulfill({status:200,contentType:'text/html',body:'<title>Destination fixture</title>'}));
  await probe.goto(fixture.url);
  assert.equal(await probe.evaluate(()=>location.hash),fragment===''?'#'+fixture.url.split('#')[1]:fragment==='#'?'':fragment);
  await probe.close();
 }
 const rejected=await context.newPage();const redirected=[];
 await rejected.route('**/*',route=>{const url=route.request().url();if(url.endsWith('/content'))return route.fulfill({status:307,headers:{location:fixture.origin+'/capture'},body:''});if(url.endsWith('/capture'))redirected.push(url);return route.continue();});
 await rejected.goto(fixture.url);await rejected.getByRole('button',{name:'Open contribution',exact:true}).click();await rejected.waitForFunction(()=>document.querySelector('#status').textContent==='Access unavailable');assert.deepEqual(redirected,[]);await rejected.close();
 console.log('Hosted HTTPS browser: entry inert, fragment removed, no persistent secret, deliberate retrieval/reply, no referrer, reload held; six broken-entry redirect cases and rejected fetch redirect.');
}finally{await browser.close();child.stdin.write('stop\n');await new Promise(resolve=>child.once('exit',resolve));lines.close();}
