import test from 'node:test';
import assert from 'node:assert/strict';
import {projectReadable} from './readable-projection.mjs';
import {validateEnvelopeShape,checkEnvelopeContext} from './event-envelope.mjs';
const principal=x=>['alice','bob'].includes(x);
const ref={principal:'alice',conversation:'1'.repeat(32),event:'2'.repeat(32)};
const root={...ref,operation:{kind:'message',text:'PRIVATE EARLIER TEXT',replyTo:[]}};
const event=()=>({version:'0',purpose:'contribution',...ref,event:'3'.repeat(32),audience:['alice','bob'],operation:{kind:'edit',root:ref,predecessors:[ref],text:'Meet at 4 <script>alert(1)</script>'}});
const resolve=()=>({state:'valid',event:root});
test('edit fits envelope while protection context remains required',()=>{
 const e=event();assert.equal(validateEnvelopeShape(e,principal),true);
 assert.equal(checkEnvelopeContext(e,{},principal),'unverified');
 assert.equal(checkEnvelopeContext(e,{...e,status:'verified',principal:'bob'},principal),'context-mismatch');
});
test('fallback names exact root and predecessors without quoting earlier secrets',()=>{
 const result=projectReadable(event(),resolve,principal);
 assert.equal(result.state,'projected');
 for(const text of ['Correction to an earlier message',ref.event,ref.principal,ref.conversation,'Meet at 4','Replaces version:'])assert.ok(result.text.includes(text));
 assert.ok(!result.text.includes(root.operation.text));
 assert.ok(!result.html.includes('<script>'));assert.ok(result.html.includes('&lt;script&gt;'));
});
test('empty replacement is explicit and not omitted',()=>{
 const e=event();e.operation.text='';assert.ok(projectReadable(e,resolve,principal).text.includes('[empty text]'));
});
test('unresolved and invalid targets cannot produce an authorized-looking generated correction',()=>{
 for(const state of ['pending','conflict','invalid'])
  assert.equal(projectReadable(event(),()=>({state}),principal).state,state);
 const e=event();e.operation.root={...ref,principal:'bob'};
 assert.equal(projectReadable(e,resolve,principal).state,'invalid');
});

test('readable correction refuses invalid later references before lookup',()=>{
 const e=event();e.operation.predecessors.push({...ref,principal:'bob'});
 assert.equal(projectReadable(e,()=>assert.fail('No retrieval'),principal).state,'invalid');
});
