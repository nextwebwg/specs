import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
import path from 'node:path';
const here=path.dirname(fileURLToPath(import.meta.url));
if(!process.env.EMAIL_NEXT_PYTHON||!process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE)throw Error('Existing Python and Playwright runtimes required');
const child=spawn(process.env.EMAIL_NEXT_PYTHON,[path.join(here,'service_question_demo.py')],{env:process.env,stdio:['ignore','pipe','pipe']});let stderr='';child.stderr.on('data',c=>stderr+=c);
let browser;
try{
 const url=await new Promise((resolve,reject)=>{let buffer='';const timer=setTimeout(()=>reject(Error('Fixture timeout '+stderr)),60000);child.once('exit',()=>{clearTimeout(timer);reject(Error(stderr));});child.stdout.on('data',c=>{buffer+=c;if(buffer.includes('\n')){clearTimeout(timer);resolve(JSON.parse(buffer.split('\n')[0]).url);}});});
 const {chromium}=await import(pathToFileURL(process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE));browser=await chromium.launch({headless:true});const page=await browser.newPage();await page.goto(url);
 assert.equal(await page.getByRole('heading',{name:'Reserve a seat?'}).count(),1);
 assert.equal((await page.request.post(url+'/activate',{data:{}})).status(),403);
 let request;page.on('request',r=>{if(r.url()===url+'/activate'&&r.headers()['x-session'])request=r;});
 await page.getByRole('button',{name:'Reserve',exact:true}).click();await page.getByRole('status').filter({hasText:'Service result: confirmed'}).waitFor();
 const body=request.postData();assert.deepEqual(Object.keys(JSON.parse(body)).sort(),['option','sourceToken']);
 const repeated=await page.request.post(url+'/activate',{headers:{'X-Session':request.headers()['x-session'],'Content-Type':'application/json'},data:body});assert.equal(repeated.status(),200);assert.equal((await repeated.json()).effects,1);
 const injected=await page.request.post(url+'/activate',{headers:{'X-Session':request.headers()['x-session'],'Content-Type':'application/json'},data:JSON.stringify({...JSON.parse(body),service:'https://wrong.example'})});assert.equal(injected.status(),409);
 console.log('Signed SMTP service question → trusted click → HTTPS receipt browser flow passed',browser.version());
}finally{if(browser)await browser.close();child.kill('SIGTERM');await new Promise(r=>child.exitCode!==null?r():child.once('exit',r));}
