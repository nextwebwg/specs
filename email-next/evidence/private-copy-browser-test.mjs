import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
import path from 'node:path';
const here=path.dirname(fileURLToPath(import.meta.url));
if(!process.env.EMAIL_NEXT_PYTHON||!process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE)throw Error('Existing Python and Playwright runtimes required');
const child=spawn(process.env.EMAIL_NEXT_PYTHON,[path.join(here,'private_copy_demo.py')],{env:process.env,stdio:['ignore','pipe','pipe']});let stderr='';child.stderr.on('data',c=>stderr+=c);
let browser;
try{
 const url=await new Promise((resolve,reject)=>{let buffer='';const timer=setTimeout(()=>reject(Error('Fixture timeout '+stderr)),60000);child.once('exit',()=>{clearTimeout(timer);reject(Error(stderr));});child.stdout.on('data',c=>{buffer+=c;if(buffer.includes('\n')){clearTimeout(timer);resolve(JSON.parse(buffer.split('\n')[0]).url);}});});
 const {chromium}=await import(pathToFileURL(process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE));browser=await chromium.launch({headless:true});const page=await browser.newPage();await page.goto(url);
 assert.equal(await page.getByRole('heading',{name:'Private copy'}).count(),1);assert.ok((await page.locator('main').textContent()).includes('can reveal your participation'));
 assert.equal((await page.request.post(url+'/reply',{data:{}})).status(),403);
 let request;page.on('request',r=>{if(r.url()===url+'/reply'&&r.headers()['x-session'])request=r;});
 await page.getByRole('button',{name:'Reply privately: Friday'}).click();await page.getByRole('status').filter({hasText:'Private answer delivered. Visible conversation answers: 0.'}).waitFor();
 assert.equal(await page.locator('button').isDisabled(),true);
 const repeated=await page.request.post(url+'/reply',{headers:{'X-Session':request.headers()['x-session'],'Content-Type':'application/json'},data:'{}'});assert.equal(repeated.status(),200);assert.equal((await repeated.json()).visibleAnswers,0);console.log('Private-copy signed SMTP browser flow passed',browser.version());
}finally{if(browser)await browser.close();child.kill('SIGTERM');await new Promise(r=>child.exitCode!==null?r():child.once('exit',r));}
