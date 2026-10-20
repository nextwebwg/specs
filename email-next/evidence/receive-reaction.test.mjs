import test from 'node:test';
import assert from 'node:assert/strict';
import {prepareReceivedReaction} from './receive-reaction.mjs';
import {encodeCredentialIdentity} from './credential-identity.mjs';
const a='enp0:'+'01'.repeat(32),b='enp0:'+'03'.repeat(32);
const alice=encodeCredentialIdentity(a,'end0:'+'02'.repeat(32)),bob=encodeCredentialIdentity(b,'end0:'+'04'.repeat(32));
const application={envelopeVersion:'1',operations:['message','reaction','reaction-withdraw']};
const context={version:'2',purpose:'conversation-context',conversation:'2'.repeat(32),profile:'mls-1-0001',administrators:[a],application,ordering:{kind:'fixed-roster-v0'}};
const ref=(n,principal=a)=>({principal,conversation:context.conversation,event:n.repeat(32)});
const base={version:'1',purpose:'contribution',audience:[a,b],disclosures:[]};
const message={...base,...ref('1'),operation:{kind:'message',text:'Hello',replyTo:[]}};
const reaction={...base,...ref('3',b),operation:{kind:'reaction',target:ref('1'),emoji:'👍'}};
const withdrawal={...base,...ref('4',b),operation:{kind:'reaction-withdraw',target:ref('1'),reactions:[ref('3',b)]}};
// References are exact three-field records rather than complete envelopes.
const invoke=(event=reaction,records=[message,reaction],options={configuredApplication:application})=>prepareReceivedReaction({principal:event.principal,conversation:event.conversation,event:event.event},bob,context,[alice,bob],r=>{
 const found=records.find(e=>e.event===r.event&&e.principal===r.principal);return found?{state:'valid',event:found}:{state:'pending'};
},undefined,options);
test('selected context prepares reaction and complete withdrawal',()=>{
 assert.equal(invoke().state,'prepared');assert.equal(invoke(withdrawal,[message,reaction,withdrawal]).state,'prepared');
});
test('unresolved history cannot supply target or withdrawal authority',()=>{
 assert.equal(invoke(reaction,[reaction]).state,'pending');
 assert.equal(invoke(withdrawal,[message,withdrawal]).state,'pending');
 const malformed={...message};delete malformed.audience;
 assert.equal(invoke(reaction,[malformed,reaction]).state,'invalid');
});
test('missing or narrower durable agreement does not enable operations',()=>{
 assert.equal(invoke(reaction,[message,reaction],{}).state,'invalid-shape');
 assert.equal(invoke(reaction,[message,reaction],{configuredApplication:{...application,operations:['message']}}).state,'invalid-shape');
});
test('cross-author withdrawal cannot suppress a reaction',()=>{
 const wrong={...withdrawal,operation:{...withdrawal.operation,reactions:[ref('3',a)]}};
 assert.notEqual(invoke(wrong,[message,{...reaction,principal:a},wrong]).state,'prepared');
});
