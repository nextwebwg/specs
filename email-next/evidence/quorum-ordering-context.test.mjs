import test from 'node:test';
import assert from 'node:assert/strict';
import {validateConversationContext} from './conversation-context.mjs';
const p='enp0:'+'1'.repeat(64);
const application={envelopeVersion:'3',payload:'mime-rich-v0',operations:['message']};
const value={version:'7',purpose:'conversation-context',conversation:'1'.repeat(32),profile:'mls-1-0001',administrators:[p],application,delivery:{kind:'ordinary-v0'},ordering:{kind:'endpoint-quorum-v0',generation:'0',faultBound:'0',witnesses:[{principal:p,device:'end0:'+'2'.repeat(64),signingKey:'3'.repeat(64),state:'4'.repeat(64),binding:'5'.repeat(64)}]}};
const opts={configuredQuorumOrdering:true,configuredApplication:application};
test('context7 exact tuple and explicit opt in',()=>{
 assert.equal(validateConversationContext(value,opts),true);
 assert.equal(validateConversationContext(value,{configuredApplication:application}),false);
 for(const application of [{...value.application,envelopeVersion:'2'},{...value.application,payload:'raw-event-v0'}])assert.equal(validateConversationContext({...value,application},{...opts,configuredApplication:application}),false);
});
test('witness fault bound and duplicate principals',()=>{
 assert.equal(validateConversationContext({...value,ordering:{...value.ordering,faultBound:'1'}},opts),false);
 assert.equal(validateConversationContext({...value,ordering:{...value.ordering,witnesses:[...value.ordering.witnesses,...value.ordering.witnesses]}},opts),false);
});
