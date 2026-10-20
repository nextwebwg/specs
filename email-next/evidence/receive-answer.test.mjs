import test from 'node:test';
import assert from 'node:assert/strict';
import {prepareReceivedAnswer} from './receive-answer.mjs';
import {encodeCredentialIdentity} from './credential-identity.mjs';
const a='enp0:'+'01'.repeat(32),b='enp0:'+'03'.repeat(32);
const alice=encodeCredentialIdentity(a,'end0:'+'02'.repeat(32));
const bob=encodeCredentialIdentity(b,'end0:'+'04'.repeat(32));
const context={version:'0',purpose:'conversation-context',conversation:'2'.repeat(32),profile:'mls-1-0001',administrators:[a]};
const ref=(n,principal=a)=>({principal,conversation:context.conversation,event:n.repeat(32)});
const base={version:'0',purpose:'contribution',audience:[a,b]};
const question={...base,...ref('1'),operation:{kind:'question',text:'Which day?',options:[{id:'4'.repeat(32),label:'Thursday'}]}};
const answer={...base,...ref('3',b),operation:{kind:'answer',question:ref('1'),option:'4'.repeat(32),replaces:[]}};
const lookup=r=>({state:'valid',event:r.event===answer.event?answer:question});
const run=(resolve=lookup,credential=bob,budget)=>prepareReceivedAnswer(ref('3',b),credential,context,[alice,bob],resolve,budget);
test('verified snapshot prepares answer wording without claiming final conversation state',()=>{
 const result=run();assert.equal(result.state,'prepared');assert.ok(result.projection.text.includes('Answer: Thursday'));
 assert.equal(Object.hasOwn(result,'heads'),false);
});
test('missing or conflicted question never prepares an answer',()=>{
 for(const state of ['pending','conflict','invalid']) assert.equal(run(r=>r.event===answer.event?lookup(r):{state}).state,state);
});
test('sender mismatch does not read conversation history',()=>{
 assert.equal(run(r=>{assert.equal(r.event,answer.event);return lookup(r);},alice).state,'sender-mismatch');
});
test('question audience boundary applies after graph resolution',()=>{
 const narrow={...question,audience:[a]};
 assert.equal(run(r=>r.event===answer.event?lookup(r):{state:'valid',event:narrow}).state,'audience-mismatch');
});
test('invalid transitive replacement prevents preparation',()=>{
 const old={...answer,...ref('5',b),operation:{...answer.operation,option:'6'.repeat(32)}};
 const newer={...answer,operation:{...answer.operation,replaces:[ref('5',b)]}};
 assert.equal(run(r=>({state:'valid',event:r.event===newer.event?newer:r.event===old.event?old:question})).state,'invalid');
});
test('conflicts and budget exhaustion do not yield a partial projection',()=>{
 assert.equal(run(()=>({state:'conflict'})).state,'conflict');
 assert.equal(run(lookup,bob,{maxRecords:1}).state,'incomplete');
});

test('authenticated but malformed predecessor envelope cannot supply replacement authority',()=>{
 const newer={...answer,operation:{...answer.operation,replaces:[ref('5',b)]}};
 const old={...answer,...ref('5',b)};
 delete old.audience;
 assert.equal(run(r=>({state:'valid',event:r.event===newer.event?newer:r.event===old.event?old:question})).state,'invalid');
});
