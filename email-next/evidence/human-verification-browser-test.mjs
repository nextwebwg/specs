import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import {fileURLToPath,pathToFileURL} from 'node:url';
if(!process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE||!process.env.EMAIL_NEXT_PYTHON)throw Error('Existing Python/Playwright runtime required');
const {chromium}=await import(pathToFileURL(process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE));
const child=spawn(process.env.EMAIL_NEXT_PYTHON,[fileURLToPath(new URL('./human-verification-browser-fixture.py',import.meta.url))],{stdio:['pipe','pipe','inherit']});
const lines=createInterface({input:child.stdout})[Symbol.asyncIterator]();
let browser;
try{
 const first=await lines.next();if(first.done)throw Error('Fixture failed');const fixture=JSON.parse(first.value),url=new URL(fixture.url);
 const denied=await fetch(url.origin+'/confirm',{method:'POST',headers:{'Content-Type':'application/json','Origin':'https://untrusted.invalid'},body:'{}'});assert.equal(denied.status,403);
 browser=await chromium.launch({headless:true});const page=await browser.newPage();await page.goto(fixture.url);await page.locator('#observed').filter({hasText:fixture.comparison.principal}).waitFor();
 assert.equal(await page.locator('button').isDisabled(),true);
 await page.locator('#independent').fill(JSON.stringify(fixture.comparison));assert.equal(await page.locator('button').isDisabled(),true);
 await page.locator('#confirmed').check();await page.locator('#independent').fill(JSON.stringify({...fixture.comparison,stateDigest:'0'.repeat(64)}));await page.locator('button').click();await page.getByRole('status').filter({hasText:'Full comparison mismatch'}).waitFor();
 child.stdin.write('status\n');assert.equal(JSON.parse((await lines.next()).value).evidence,0);
 await page.locator('#independent').fill(JSON.stringify(fixture.comparison));await page.locator('button').click();await page.getByRole('status').filter({hasText:'Comparison recorded'}).waitFor();
 child.stdin.write('status\n');assert.equal(JSON.parse((await lines.next()).value).evidence,1);
 assert.equal(new URL(page.url()).hash,'');
 console.log('Trusted comparison UI: independent confirmation, complete mismatch, atomic success, no token in history, cross-origin denial passed');
}finally{if(browser)await browser.close();child.stdin.end('stop\n');await new Promise(resolve=>{if(child.exitCode!==null)resolve();else child.once('exit',resolve);});}
