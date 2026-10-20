import test from 'node:test';import assert from 'node:assert/strict';
import {validateConversationContext} from './conversation-context.mjs';
const principal='enp0:'+'a'.repeat(64),application={envelopeVersion:'3',payload:'mime-rich-v0',operations:['edit','message']};
const context={version:'6',purpose:'conversation-context',conversation:'a'.repeat(32),profile:'mls-1-0001',administrators:[principal],application,ordering:{kind:'fixed-roster-v0'},delivery:{kind:'ordinary-v0'}};
test('edit requires exact explicit context6 agreement; old contexts stay unchanged',()=>{
 assert.equal(validateConversationContext(context,{configuredApplication:application}),true);
 assert.equal(validateConversationContext(context,{configuredApplication:{...application,operations:['message']}}),false);
 assert.equal(validateConversationContext({...context,version:'5',application:{...application,envelopeVersion:'2'}},{configuredApplication:{...application,envelopeVersion:'2'}}),false);
});
test('context7 cannot inherit edit through comparable context6',()=>{
 const ordering={kind:'endpoint-quorum-v0',generation:'0',faultBound:'0',witnesses:[{principal,device:'end0:'+'b'.repeat(64),signingKey:'c'.repeat(64),state:'d'.repeat(64),binding:'e'.repeat(64)}]};
 assert.equal(validateConversationContext({...context,version:'7',ordering},{configuredQuorumOrdering:true,configuredApplication:application}),false);
 const plain={...application,operations:['message']};assert.equal(validateConversationContext({...context,version:'7',ordering,application:plain},{configuredQuorumOrdering:true,configuredApplication:plain}),true);
});
