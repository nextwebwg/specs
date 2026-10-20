import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
import path from 'node:path';
const here=path.dirname(fileURLToPath(import.meta.url));
if(!process.env.EMAIL_NEXT_PYTHON||!process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE)throw Error('Existing Python and Playwright required');
const child=spawn(process.env.EMAIL_NEXT_PYTHON,[path.join(here,'edit_demo.py')],{env:process.env,stdio:['ignore','pipe','pipe']});let errors='';child.stderr.on('data',c=>errors+=c);let browser;
try{
 const url=await new Promise((resolve,reject)=>{let s='';const t=setTimeout(()=>reject(Error('Fixture timeout '+errors)),60000);child.once('exit',()=>{clearTimeout(t);reject(Error(errors));});child.stdout.on('data',c=>{s+=c;if(s.includes('\n')){clearTimeout(t);resolve(JSON.parse(s.split('\n')[0]).url);}});});
 const {chromium}=await import(pathToFileURL(process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE));browser=await chromium.launch({headless:true});const page=await browser.newPage();await page.goto(url);
 await page.getByRole('status').filter({hasText:'Original'}).waitFor();assert.equal((await page.request.post(url+'/edit',{data:{text:'forged'}})).status(),403);
 await page.getByLabel('Replacement text').fill('Meet Wednesday <img src=x>');await page.getByRole('button',{name:'Send correction',exact:true}).click();await page.getByRole('status').filter({hasText:'Edited'}).waitFor();assert.ok((await page.locator('#versions').textContent()).includes('Meet Tuesday — Earlier version'));assert.equal(await page.locator('#versions img').count(),0);
 await page.getByLabel('Replacement text').fill('Meet Thursday');await page.getByRole('button',{name:'Send competing correction'}).click();await page.getByRole('status').filter({hasText:'Conflict'}).waitFor();assert.equal((await page.locator('#versions').textContent()).match(/Current version/g).length,2);
 await page.getByLabel('Replacement text').fill('Meet Friday');await page.getByRole('button',{name:'Resolve all shown versions'}).click();await page.getByRole('status').filter({hasText:'Edited'}).waitFor();const text=await page.locator('#versions').textContent();assert.ok(text.includes('Meet Friday — Current version'));assert.ok(text.includes('Meet Tuesday — Earlier version'));assert.equal(text.match(/Current version/g).length,1);
 console.log('Signed SMTP correction, inert replacement, concurrent heads and explicit resolution passed',browser.version());
}finally{if(browser)await browser.close();child.kill('SIGTERM');await new Promise(r=>child.exitCode!==null?r():child.once('exit',r));}
