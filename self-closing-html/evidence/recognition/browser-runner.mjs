import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium,firefox,webkit} from 'playwright';
const root=path.resolve(fileURLToPath(new URL('..',import.meta.url)));
const requests=[];
const server=http.createServer(async(req,res)=>{
  const url=new URL(req.url,'http://localhost');
  if(url.pathname==='/probe'){requests.push(url.search);res.writeHead(404);res.end();return;}
  if(url.pathname==='/'){
    res.writeHead(200,{'content-type':'text/html'});
    res.end(`<!doctype html><script type="importmap">{"imports":{"parse5":"/node_modules/parse5/dist/index.js","entities/decode":"/node_modules/entities/dist/decode.js","entities/escape":"/node_modules/entities/dist/escape.js"}}</script><body>`);return;
  }
  try{
    const filename=path.resolve(root,'.'+decodeURIComponent(url.pathname));
    if(!filename.startsWith(root+path.sep))throw new Error('outside root');
    const bytes=await fs.readFile(filename);
    res.writeHead(200,{'content-type':'text/javascript'});res.end(bytes);
  }catch{res.writeHead(404);res.end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin=`http://127.0.0.1:${server.address().port}`;
const reports=[];
try{
  for(const [name,type]of [['chromium',chromium],['firefox',firefox],['webkit',webkit]]){
    let browser;
    try{
      const options={headless:true};
      if(process.env[`${name.toUpperCase()}_EXECUTABLE`])options.executablePath=process.env[`${name.toUpperCase()}_EXECUTABLE`];
      browser=await type.launch(options);
      const page=await browser.newPage();
      await page.goto(origin);
      requests.length=0;
      const cases=await page.evaluate(async origin=>{
        const {runCases}=await import('/recognition/browser-cases.mjs');return runCases(origin);
      },origin);
      const resourceBoundary=requests.includes('?positive')&&!requests.some(query=>query!=='?positive');
      reports.push({engine:name,version:browser.version(),cases,requests:[...requests],resourceBoundary});
    }catch(error){reports.push({engine:name,error:String(error)});}
    finally{await browser?.close();}
  }
}finally{server.close();}
await fs.writeFile(new URL('./browser-results.json',import.meta.url),JSON.stringify({reports,scope:'Browser DOM adapters share parse5 recognition; no native navigation-parser implementation or universal execution-safety proof.'},null,2)+'\n');
console.log(JSON.stringify(reports,null,2));
if(reports.some(r=>r.error||!r.resourceBoundary||r.cases.some(c=>!c.pass)))process.exitCode=1;
