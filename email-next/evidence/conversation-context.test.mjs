import test from 'node:test';
import assert from 'node:assert/strict';
import {encodeCredentialIdentity} from './credential-identity.mjs';
import {checkConversationContext,validateConversationContext} from './conversation-context.mjs';
const a='enp0:'+'01'.repeat(32),b='enp0:'+'03'.repeat(32),device=n=>'end0:'+n.repeat(64);
const alice=encodeCredentialIdentity(a,device('2')),bob=encodeCredentialIdentity(b,device('4'));
const context={version:'0',purpose:'conversation-context',conversation:'2'.repeat(32),profile:'mls-1-0001',administrators:[a]};
const event={version:'0',purpose:'contribution',event:'1'.repeat(32),conversation:context.conversation,principal:a,audience:[a,b],operation:{kind:'message',text:'Hello',replyTo:[]}};
test('authenticated roster yields a deduplicated account audience across devices',()=>{
 assert.equal(checkConversationContext(event,alice,context,[alice,bob,encodeCredentialIdentity(a,device('5'))]),'context-matched');
});
test('conversation audience and claimed sender cannot disagree with context',()=>{
 assert.equal(checkConversationContext({...event,conversation:'3'.repeat(32)},alice,context,[alice,bob]),'conversation-mismatch');
 assert.equal(checkConversationContext({...event,audience:[a]},alice,context,[alice,bob]),'audience-mismatch');
 assert.equal(checkConversationContext({...event,principal:b},alice,context,[alice,bob]),'sender-mismatch');
});
test('duplicate devices absent sender and absent administrators fail',()=>{
 assert.equal(checkConversationContext(event,alice,context,[alice,alice,bob]),'invalid-roster');
 assert.equal(checkConversationContext(event,alice,context,[bob]),'sender-not-member');
 assert.equal(checkConversationContext(event,alice,{...context,administrators:['enp0:'+'f'.repeat(64)]},[alice,bob]),'administrator-not-member');
});
test('context fields and administrator ordering are exact',()=>{
 for(const patch of [{extra:true},{profile:'unknown'},{administrators:[]},{administrators:[b,a]},{administrators:[a,a]}])assert.equal(validateConversationContext({...context,...patch}),false);
});
test('v2 requires explicit exact configured application agreement and binds operation/version',()=>{
 const application={envelopeVersion:'1',operations:['answer','message','question']};
 const c={...context,version:'2',application,ordering:{kind:'fixed-roster-v0'}};
 const e={...event,version:'1',disclosures:[]};
 const opts={configuredApplication:application};
 assert.equal(validateConversationContext(c),false);
 assert.equal(validateConversationContext(c,opts),true);
 for(const ordering of [null,{}, {kind:'fixed-roster-v0',extra:true},{kind:'unknown'}])assert.equal(validateConversationContext({...c,ordering},opts),false);
 assert.equal(checkConversationContext(e,alice,c,[alice,bob],opts),'context-matched');
 assert.equal(checkConversationContext(event,alice,c,[alice,bob],opts),'application-mismatch');
 assert.equal(checkConversationContext(e,alice,context,[alice,bob]),'application-mismatch');
 for(const application of [{envelopeVersion:'1',operations:['message','question','answer']},{envelopeVersion:'1',operations:['message','message']},{envelopeVersion:'1',operations:['unknown-observation']},{envelopeVersion:'0',operations:['message']},{envelopeVersion:'1',operations:[]}])assert.equal(validateConversationContext({...c,application},{configuredApplication:application}),false);
 assert.equal(validateConversationContext(c,{configuredApplication:{envelopeVersion:'1',operations:['message']}}),false);
 assert.equal(validateConversationContext({...c,extra:true},opts),false);
 const onlyQuestion={envelopeVersion:'1',operations:['question']};
 assert.equal(checkConversationContext(e,alice,{...c,application:onlyQuestion},[alice,bob],{configuredApplication:onlyQuestion}),'application-mismatch');
});
test('v2 ordering retains separate configured authorization and roster check',()=>{
 const application={envelopeVersion:'1',operations:['message']};
 const ordering={kind:'designated-member-v0',principal:a,device:device('2')};
 const c={...context,version:'2',application,ordering};
 const options={configuredApplication:application,configuredEndpointOrdering:true};
 assert.equal(validateConversationContext(c,{configuredApplication:application}),false);
 assert.equal(checkConversationContext({...event,version:'1',disclosures:[]},alice,c,[alice,bob],options),'context-matched');
 assert.equal(checkConversationContext({...event,version:'1',disclosures:[]},alice,{...c,ordering:{...ordering,device:device('6')}},[alice,bob],options),'ordering-device-not-member');
 const v1={...context,version:'1',ordering};
 assert.equal(validateConversationContext(v1),false);
 assert.equal(checkConversationContext({...event,version:'1',disclosures:[]},alice,v1,[alice,bob],options),'application-mismatch');
});
