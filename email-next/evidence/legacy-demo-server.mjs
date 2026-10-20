import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const here=path.dirname(fileURLToPath(import.meta.url));
export async function startDemo(port=0){
 if(!process.env.EMAIL_NEXT_PYTHON)throw Error('Set EMAIL_NEXT_PYTHON to configured Python runtime');
 const child=spawnSync(process.env.EMAIL_NEXT_PYTHON,[path.join(here,'legacy-demo-fixture.py')],{encoding:'utf8',maxBuffer:4*1024*1024,timeout:10000});
 if(child.status!==0)throw Error(child.stderr);const fixture=JSON.parse(child.stdout);
 const assets=new Set(['legacy-demo.html','legacy-demo.css','legacy-demo.mjs','legacy-quotes.mjs','flowed-quotes.mjs','flowed-text.mjs','html-quotes.mjs']);
 const server=createServer(async(req,res)=>{
  try{
   if(req.method!=='GET'){res.writeHead(405).end();return;}
   res.setHeader('Content-Security-Policy',"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'");res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Referrer-Policy','no-referrer');
   if(req.url==='/fixtures.json'){res.setHeader('Content-Type','application/json');res.end(child.stdout);return;}
   const match=/^\/messages\/([a-z-]+)\.eml$/.exec(req.url);
   if(match&&fixture.messages[match[1]]){res.setHeader('Content-Type','message/rfc822');res.setHeader('Content-Disposition','attachment; filename="'+match[1]+'.eml"');res.end(Buffer.from(fixture.messages[match[1]].base64,'base64'));return;}
   const file=req.url==='/'?'legacy-demo.html':req.url.slice(1);
   if(!assets.has(file)){res.writeHead(404).end();return;}
   res.setHeader('Content-Type',file.endsWith('.mjs')?'text/javascript':file.endsWith('.css')?'text/css':'text/html');res.end(await readFile(path.join(here,file)));
  }catch{res.writeHead(500).end('Local fixture error');}
 });
 await new Promise(resolve=>server.listen(port,'127.0.0.1',resolve));return {server,fixture,url:'http://127.0.0.1:'+server.address().port+'/'};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){const {url}=await startDemo(Number(process.env.PORT||0));console.log(url);}
