import test from 'node:test';
import assert from 'node:assert/strict';
import {isPrincipalId,isDeviceId,newPrincipalId,newDeviceId} from './principal-identifiers.mjs';
import {validateEnvelopeShape,checkEnvelopeContext} from './event-envelope.mjs';
const principal='enp0:'+'a'.repeat(64);
test('account and device encodings are distinct exact domains',()=>{
 assert.equal(isPrincipalId(principal),true);assert.equal(isDeviceId(principal),false);
 assert.equal(isDeviceId('end0:'+'a'.repeat(64)),true);
 for(const value of [principal.toUpperCase(),principal+' ',principal.slice(0,-1),'enp0:'+'0'.repeat(64),'alice@example.test','enp1:'+'a'.repeat(64)])assert.equal(isPrincipalId(value),false);
});
test('generated identifiers use the selected encodings',()=>{
 assert.equal(isPrincipalId(newPrincipalId()),true);assert.equal(isDeviceId(newDeviceId()),true);
});
test('wire principal encoding integrates without granting authentication',()=>{
 const event={version:'0',purpose:'contribution',event:'1'.repeat(32),conversation:'2'.repeat(32),principal,audience:[principal],operation:{kind:'message',text:'Hello',replyTo:[]}};
 assert.equal(validateEnvelopeShape(event,isPrincipalId),true);
 assert.equal(checkEnvelopeContext(event,null,isPrincipalId),'unverified');
 assert.equal(validateEnvelopeShape({...event,principal:'alice@example.test'},isPrincipalId),false);
});
