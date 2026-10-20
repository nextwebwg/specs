import {test} from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {LiveDOMParser} from './live-dom.mjs';

test('a fostered text/element batch precedes its existing table anchor',async()=>{
 const {window}=new JSDOM();
 try{
  const runtime=new LiveDOMParser(window.document,{executeScripts:false});
  await runtime.write('<!doctype html PUBLIC "next"><body><table>text<div/>',true);
  assert.deepEqual([...window.document.body.childNodes].map(n=>n.nodeName),['#text','DIV','TABLE']);
  assert.equal(window.document.body.firstChild.data,'text');
 }finally{window.close();}
});

test('frameset recovery preserves script-moved nodes and detached subtree ownership',async()=>{
 const {window}=new JSDOM('',{runScripts:'dangerously',url:'http://localhost/'});
 try{
  const runtime=new LiveDOMParser(window.document);
  await runtime.write(`<!doctype html PUBLIC "next"><input type="hidden" id="keep"><script>
   window.savedBody=document.body;window.savedScript=document.currentScript;
   document.head.append(document.getElementById('keep'));
  </script><frameset></frameset>`,true);
  assert.equal(window.document.body.localName,'frameset');
  assert.equal(window.document.getElementById('keep')?.parentNode,window.document.head);
  assert.equal(window.savedScript.parentNode,window.savedBody);
 }finally{window.close();}
});
