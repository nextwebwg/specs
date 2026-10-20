// One sequential browser; deliberately small parser differential corpus, not full conformance.
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
import path from 'node:path';
if(!process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE||!process.env.EMAIL_NEXT_PYTHON)throw Error('Set existing Playwright and Python runtimes');
const {chromium}=await import(pathToFileURL(process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE));
const fixtures=[
 ['select-retained-internal','<select><div><b>hidden</b></div><option>hidden option</option></select><p>visible</p>'],
 ['select-table','<select><table><tr><td>inside</td></tr></table></select><p>after</p>'],
 ['select-input-exit','<select><option>A<input><b>B</b></select><p>C</p>'],
 ['select-nested','<select><select><b>A</b></select><p>B</p>'],
 ['select-hr','<select><hr><option>A</select><p>B</p>'],
 ['pi-basic','<?marker key="value"><p>visible</p>'],
 ['pi-quoted-close','<?marker key=">"><p>visible</p>'],
 ['pi-unclosed','<?marker key="unterminated <p>visible</p>'],
 ['pi-xml','<?xml version="1.0"><p>visible</p>'],
 ['pi-table','<table><?marker x="y"><tr><td>A</td></tr></table>'],
 ['title-boundaries','<html title="document"><body><section title=""><p>A</p></section><p>B</p></body></html>']
].map(([name,source])=>({name,source}));
const browser=await chromium.launch({headless:true});
try{
 const context=await browser.newContext();let requests=0;await context.route('**/*',route=>{requests++;return route.abort();});
 const page=await context.newPage();
 const captured=await page.evaluate(fixtures=>fixtures.map(f=>{
  const doc=new DOMParser().parseFromString(f.source,'text/html');
  function convert(n){
   if(n.nodeType===3)return n.data;
   if(n.nodeType!==1)return {tag:'#other',children:[]};
   return {tag:`{${n.namespaceURI}}${n.localName}`,attributes:Object.fromEntries([...n.attributes].map(a=>[a.namespaceURI?`{${a.namespaceURI}}${a.localName}`:a.name,a.value])),children:[...n.childNodes].map(convert)};
  }
  return {...f,root:convert(doc.documentElement)};
 }),fixtures);
 const py=spawnSync(process.env.EMAIL_NEXT_PYTHON,[path.join(path.dirname(fileURLToPath(import.meta.url)),'html-parser-differential.py')],{input:JSON.stringify(captured),encoding:'utf8'});
 assert.equal(py.status,0,py.stderr);assert.equal(requests,0);
 const results=JSON.parse(py.stdout);
 console.log(JSON.stringify({browser:browser.version(),html5lib:'1.1',fixtures:results,networkRequests:requests},null,2));
 // Differences are the purpose of this experiment: report all rather than asserting equivalence.
}finally{await browser.close();}
