import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
import path from 'node:path';
const here=path.dirname(fileURLToPath(import.meta.url));
if(!process.env.EMAIL_NEXT_PYTHON||!process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE)throw Error('Existing Python and Playwright runtimes required');
const child=spawn(process.env.EMAIL_NEXT_PYTHON,[path.join(here,'service_connect_demo.py')],{env:process.env,stdio:['ignore','pipe','pipe']});let stderr='';child.stderr.on('data',c=>stderr+=c);
let browser;
try{
 const url=await new Promise((resolve,reject)=>{let buffer='';const timer=setTimeout(()=>reject(Error('Fixture timeout '+stderr)),60000);child.once('exit',()=>{clearTimeout(timer);reject(Error(stderr));});child.stdout.on('data',c=>{buffer+=c;if(buffer.includes('\n')){clearTimeout(timer);resolve(JSON.parse(buffer.split('\n')[0]).url);}});});
 const {chromium}=await import(pathToFileURL(process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE));browser=await chromium.launch({headless:true,args:['--host-resolver-rules=MAP service.example 127.0.0.1','--no-proxy-server']});const page=await browser.newPage();await page.goto(url);
 assert.equal((await page.request.post(url+'/link',{data:{}})).status(),403);
 await page.getByRole('button',{name:'Connect service',exact:true}).click();const link=page.getByRole('link',{name:'Open service in external browser'});await link.waitFor();
 const authorizationUrl=await link.getAttribute('href');assert.equal(new URL(authorizationUrl).hostname,'service.example');assert.notEqual(new URL(authorizationUrl).origin,new URL(url).origin);
 // The browser-side synthetic service uses a fixture CA. Only this separate
 // test context ignores its trust error; native token/link TLS validates the CA.
 const external=await browser.newContext({ignoreHTTPSErrors:true});const consent=await external.newPage();for(const redirect of ['http://attacker.example/email-next/oauth/callback','http://127.0.0.1:12345/wrong-path']){const invalid=new URL(authorizationUrl);invalid.searchParams.set('redirect_uri',redirect);assert.equal((await consent.goto(invalid.href)).status(),400);}const responses=[];const errors=[];consent.on('console',m=>{if(m.type()==='error')errors.push(m.text().replace(/https?:[^\s"']+/g,'[URL]'));});consent.on('response',r=>responses.push({status:r.status(),path:new URL(r.url()).pathname}));await consent.goto(authorizationUrl);
 assert.ok((await consent.locator('body').textContent()).includes('simulated account authentication'));assert.equal(await page.locator('iframe').count(),0);
 await consent.getByRole('button',{name:'Authorize demo account'}).click();try{await consent.getByText('You may return to your email client.').waitFor({timeout:10000});}catch{throw Error('Callback navigation: '+JSON.stringify({responses,errors,state:await(await page.request.get(url+'/state')).json()}));}
 await page.getByRole('button',{name:'Link my Email Next principal'}).waitFor();assert.equal(await page.getByRole('button',{name:'Reserve seat'}).isVisible(),false);
 await page.getByRole('button',{name:'Link my Email Next principal'}).click();try{await page.getByRole('status').filter({hasText:'Principal linked. Protected question received over SMTP.'}).waitFor({timeout:10000});}catch{throw Error('Link held: '+JSON.stringify(await(await page.request.get(url+'/state')).json())+' '+stderr);}
 await page.getByRole('button',{name:'Reserve seat'}).click();await page.getByRole('status').filter({hasText:'Service result: confirmed; effects: 1'}).waitFor();
 await page.getByRole('button',{name:'Reserve seat'}).click();await page.getByRole('status').filter({hasText:'Service result: confirmed; effects: 1'}).waitFor();
 await external.close();console.log('Separate synthetic service consent → loopback/PKCE → explicit signed link → SMTP question → HTTPS effect passed',browser.version());
}finally{if(browser)await browser.close();child.kill('SIGTERM');await new Promise(r=>child.exitCode!==null?r():child.once('exit',r));}
