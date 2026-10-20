import test from 'node:test';
import assert from 'node:assert/strict';
import {validateDisclosures,validateEnvelopeShape} from './event-envelope.mjs';
import {checkConversationContext,validateConversationContext} from './conversation-context.mjs';
import {encodeCredentialIdentity} from './credential-identity.mjs';
import {isPrincipalId} from './principal-identifiers.mjs';
const a='enp0:'+'1'.repeat(64),b='enp0:'+'2'.repeat(64),c='enp0:'+'3'.repeat(64);
const leaf=(p,n)=>encodeCredentialIdentity(p,'end0:'+n.repeat(64));
const application={envelopeVersion:'2',payload:'mime-rich-v0',operations:['message','question']};
const context={version:'5',purpose:'conversation-context',conversation:'1'.repeat(32),profile:'mls-1-0001',administrators:[a],application,ordering:{kind:'fixed-roster-v0'},delivery:{kind:'private-copy-v0',originator:a,recipient:b}};
const event={version:'2',purpose:'contribution',event:'2'.repeat(32),conversation:context.conversation,principal:a,audience:[a,b],operation:{kind:'message',text:'Hello',replyTo:[]},disclosures:[{kind:'separate-protected-copy'}]};
const opts={configuredApplication:application};
test('new disclosure is versioned exact and canonically ordered',()=>{
 assert.equal(validateEnvelopeShape(event,isPrincipalId),true);
 assert.equal(validateEnvelopeShape({...event,version:'1'},isPrincipalId),false);
 for(const d of [[{kind:'separate-protected-copy',count:'1'}],[...event.disclosures,...event.disclosures],[{kind:'plaintext-email'},...event.disclosures]])assert.equal(validateDisclosures(d,'2'),false);
 assert.equal(validateDisclosures([...event.disclosures,{kind:'plaintext-email'}],'2'),true);
});
test('private context admits exactly two principals including multiple devices',()=>{
 assert.equal(checkConversationContext(event,leaf(a,'4'),context,[leaf(a,'4'),leaf(a,'5'),leaf(b,'6')],opts),'context-matched');
 assert.equal(checkConversationContext({...event,audience:[a,b,c]},leaf(a,'4'),context,[leaf(a,'4'),leaf(b,'6'),leaf(c,'7')],opts),'private-copy-roster-mismatch');
 assert.equal(checkConversationContext({...event,audience:[a]},leaf(a,'4'),context,[leaf(a,'4')],opts),'private-copy-roster-mismatch');
});
test('old context and missing or malformed private role cannot activate new envelope',()=>{
 assert.equal(validateConversationContext(context),false);
 for(const delivery of [null,{kind:'private-copy-v0',originator:a,recipient:a},{...context.delivery,count:'1'}])assert.equal(validateConversationContext({...context,delivery},opts),false);
 assert.equal(validateConversationContext({...context,version:'4'},opts),false);
 assert.equal(validateConversationContext({...context,application:{...application,payload:'raw-event-v0'}},{configuredApplication:{...application,payload:'raw-event-v0'}}),false);
});
