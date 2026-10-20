import test from 'node:test';
import assert from 'node:assert/strict';
import {projectReadable} from './readable-projection.mjs';
import {validateEnvelopeShape,checkEnvelopeContext} from './event-envelope.mjs';
const id=n=>String(n).repeat(32);
const principal=p=>['alice','bob','carol'].includes(p);
const base={version:'0',purpose:'contribution',conversation:id(1),audience:['alice','bob']};
const question={...base,principal:'alice',event:id(2),operation:{kind:'question',text:'Which <day>?',options:[{id:id(3),label:'Tuesday'},{id:id(4),label:'Thursday & Friday'}]}};
const answer=()=>({...base,principal:'bob',event:id(5),operation:{kind:'answer',question:{principal:'alice',event:id(2),conversation:id(1)},option:id(4),replaces:[]}});
const lookup=()=>({state:'valid',event:question});
test('question projection is readable and inert without target lookup',()=>{
 assert.equal(validateEnvelopeShape(question,principal),true);
 const p=projectReadable(question,()=>assert.fail(),principal);
 assert.equal(p.state,'projected');assert.match(p.text,/1\. Tuesday\n2\. Thursday & Friday/);
 assert.match(p.html,/Which &lt;day&gt;\?/);assert.doesNotMatch(p.html,/<button|<form|<script/);
});
test('answer projection uses exact target labels and no transcript',()=>{
 const p=projectReadable(answer(),lookup,principal);
 assert.equal(p.state,'projected');assert.match(p.text,/Answer: Thursday & Friday/);
 assert.doesNotMatch(p.text,/Tuesday/);assert.match(p.html,/Thursday &amp; Friday/);
});
test('unresolved and invalid options produce no readable projection',()=>{
 assert.deepEqual(projectReadable(answer(),()=>null,principal),{state:'pending'});
 const a=answer();a.operation.option=id(9);
 assert.deepEqual(projectReadable(a,lookup,principal),{state:'invalid'});
});
test('automatic context copying refuses expanded audience or unsigned target shape',()=>{
 const a=answer();a.audience=[...base.audience,'carol'];
 assert.deepEqual(projectReadable(a,lookup,principal),{state:'audience-mismatch'});
 assert.deepEqual(projectReadable(answer(),()=>({state:'valid',event:{...question,audience:undefined}}),principal),{state:'audience-mismatch'});
});
test('button envelope still requires independently verified context',()=>{
 const a=answer();assert.equal(checkEnvelopeContext(a,null,principal),'unverified');
 const context={...base,status:'verified',principal:'bob'};
 assert.equal(checkEnvelopeContext(a,context,principal),'context-matched');
 assert.equal(checkEnvelopeContext(a,{...context,audience:['bob','carol']},principal),'context-mismatch');
});
