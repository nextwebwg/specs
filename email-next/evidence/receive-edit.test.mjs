import test from 'node:test';
import assert from 'node:assert/strict';
import {prepareReceivedEdit} from './receive-edit.mjs';
import {encodeCredentialIdentity} from './credential-identity.mjs';
const a='enp0:'+'01'.repeat(32),b='enp0:'+'03'.repeat(32);
const alice=encodeCredentialIdentity(a,'end0:'+'02'.repeat(32));
const bob=encodeCredentialIdentity(b,'end0:'+'04'.repeat(32));
const context={version:'0',purpose:'conversation-context',conversation:'2'.repeat(32),profile:'mls-1-0001',administrators:[a]};
const ref=n=>({principal:a,conversation:context.conversation,event:n.repeat(32)});
const root={...ref('1'),operation:{kind:'message',text:'3',replyTo:[]}};
const edit={...ref('3'),version:'0',purpose:'contribution',audience:[a,b],operation:{kind:'edit',root:ref('1'),predecessors:[ref('1')],text:'4'}};
const lookup=r=>({state:'valid',event:r.event===edit.event?edit:root});
const run=(resolve=lookup,credential=alice,budget)=>prepareReceivedEdit(ref('3'),credential,context,[alice,bob],resolve,budget);
test('context matched edit resolves history and prepares correction without current-head claims',()=>{
 const result=run();assert.equal(result.state,'prepared');assert.ok(result.projection.text.includes('Replacement text:\n4'));assert.equal(Object.hasOwn(result,'heads'),false);
});
test('matched protection context does not authorize missing conflicted or invalid history',()=>{
 for(const state of ['pending','conflict','invalid'])assert.equal(run(r=>r.event===edit.event?lookup(r):{state}).state,state);
});
test('sender mismatch stops before history resolution',()=>{
 assert.equal(run(r=>{assert.equal(r.event,edit.event);return lookup(r);},bob).state,'sender-mismatch');
});
test('identity conflict and exhausted local work cannot prepare effects',()=>{
 assert.equal(run(()=>({state:'conflict'})).state,'conflict');
 assert.equal(run(lookup,alice,{maxRecords:1}).state,'incomplete');
});
