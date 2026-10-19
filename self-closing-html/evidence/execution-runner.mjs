import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';

const root=fileURLToPath(new URL('.',import.meta.url));
const packagePath=process.env.PLAYWRIGHT_MODULE??'playwright';
const {chromium,firefox,webkit}=await import(packagePath.startsWith('/')?pathToFileURL(packagePath).href:packagePath);
const requests=[];
const server=http.createServer(async(req,res)=>{
 const url=new URL(req.url,'http://localhost');
 requests.push({path:url.pathname,query:url.search,time:Date.now()});
 if(url.pathname==='/delayed-script'){
  await new Promise(resolve=>setTimeout(resolve,80));
  res.writeHead(200,{'content-type':'text/javascript'});
  res.end('trace.push({external:true,later:!!document.querySelector("#later")})');return;
 }
 if(url.pathname==='/streamed-source'){
  res.writeHead(200,{'content-type':'text/html; charset=utf-8'});
  const bytes=Buffer.from('<!doctype html PUBLIC "next"><body><div id="empty"/>😀<script>trace.push({stream:true,later:!!document.querySelector("#later")})</script><span id="later">tail</span>');
  const emoji=bytes.indexOf(Buffer.from('😀'));
  let start=0;
  for(const boundary of [emoji+1,emoji+2,emoji+3,bytes.length]){
   res.write(bytes.subarray(start,boundary));start=boundary;
   await new Promise(resolve=>setTimeout(resolve,20));
  }
  res.end();return;
 }
 if(url.pathname==='/probe'){res.writeHead(404);res.end();return;}
 if(url.pathname==='/'){
  res.writeHead(200,{'content-type':'text/html'});
  res.end(`<!doctype html><title>Incremental HTML Next execution evidence</title><script type="importmap">{"imports":{"parse5":"/node_modules/parse5/dist/index.js","entities/decode":"/node_modules/entities/dist/decode.js","entities/escape":"/node_modules/entities/dist/escape.js"}}</script><body><script type="module">import {runExecutionCases} from '/execution-browser.mjs';window.runExecutionCases=runExecutionCases;</script>`);return;
 }
 try{
  const filename=path.resolve(root,'.'+decodeURIComponent(url.pathname));
  if(!filename.startsWith(root))throw new Error('outside root');
  const data=await fs.readFile(filename);
  res.writeHead(200,{'content-type':filename.endsWith('.js')||filename.endsWith('.mjs')?'text/javascript':'text/plain'});res.end(data);
 }catch{res.writeHead(404);res.end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin=`http://127.0.0.1:${server.address().port}`;
const reports=[];
try{
 // One browser at a time: no overlapping local browser runners.
 for(const [name,type] of [['chromium',chromium],['firefox',firefox],['webkit',webkit]]){
  if(process.env.BROWSER_ENGINES&&!process.env.BROWSER_ENGINES.split(',').includes(name))continue;
  let browser;
  try{
   const executablePath=process.env[`${name.toUpperCase()}_EXECUTABLE`];
   browser=await type.launch({headless:true,...(executablePath?{executablePath}:{})});
   const page=await browser.newPage();const errors=[];
   page.on('pageerror',error=>errors.push(String(error)));
   await page.goto(origin);await page.waitForFunction(()=>typeof window.runExecutionCases==='function');
   const start=requests.length;
   const cases=await page.evaluate(caseFilter=>window.runExecutionCases({caseFilter}),process.env.EXECUTION_CASE??null);
   const observed=requests.slice(start);
   const resourceIsolation=cases.some(c=>c.name==='resource request positive control')&&cases.some(c=>c.name==='namespace recovery never creates executable image')?!observed.some(r=>r.path==='/probe'&&r.query.includes('namespace'))&&observed.some(r=>r.path==='/probe'&&r.query.includes('positive')):null;
   reports.push({engine:name,version:browser.version(),cases,errors,requests:observed,resourceIsolation,pass:cases.length>0&&cases.every(c=>c.pass)&&errors.length===0&&resourceIsolation!==false});
  }catch(error){reports.push({engine:name,pass:false,error:String(error.stack??error)});}
  finally{await browser?.close();}
 }
}finally{await new Promise(resolve=>server.close(resolve));}
const sourceDigests=Object.fromEntries(await Promise.all(['live-dom.mjs','streaming-parser.mjs','recognition-parser.mjs','model.mjs','execution-browser.mjs','execution-runner.mjs','package-lock.json'].map(async name=>[name,createHash('sha256').update(await fs.readFile(new URL(name,import.meta.url))).digest('hex')])));
const report={recordedAt:new Date().toISOString(),runtime:process.version,scope:'parse5 incremental recognition + real browser DOM and classic script execution; not a patched native navigation parser',caseFilter:process.env.EXECUTION_CASE??null,sourceDigests,reports};
await fs.writeFile(new URL('./execution-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
if(reports.some(r=>!r.pass))process.exitCode=1;
