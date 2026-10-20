import test from 'node:test';
import assert from 'node:assert/strict';
import {isServiceOrigin,isServiceEndpoint,validateServiceQuestion} from './service-question.mjs';
import {validateEnvelopeShape,checkEnvelopeContext} from './event-envelope.mjs';
import {projectReadable} from './readable-projection.mjs';
import {resolveButtonAnswer} from './button-operations.mjs';
import {evaluateButtonAnswers} from './button-state.mjs';
import {prepareReceivedAnswer} from './receive-answer.mjs';
import {encodeCredentialIdentity} from './credential-identity.mjs';
import {isPrincipalId} from './principal-identifiers.mjs';
const a='enp0:'+'01'.repeat(32),b='enp0:'+'02'.repeat(32),id=n=>String(n).repeat(32);
const ref=(n,principal=a)=>({principal,conversation:id(1),event:id(n)});
const make=()=>({version:'0',purpose:'contribution',...ref(2),audience:[a,b],operation:{kind:'service-question',text:'Which <day>?',options:[{id:id(3),label:'Tuesday & Wednesday'},{id:id(4),label:'Thursday'}],serviceAction:{version:'0',purpose:'service-answer-action',action:id(5),question:ref(2),service:'https://answers.example',submit:'https://answers.example/submit',statusPrefix:'https://answers.example/status/',notBefore:'0',retryUntil:'18446744073709551615'}}});
test('exact operation and self-binding remain distinct from authenticated context',()=>{
 const q=make();assert.equal(validateServiceQuestion(q.operation,isPrincipalId),true);assert.equal(validateEnvelopeShape(q,isPrincipalId),true);
 assert.equal(checkEnvelopeContext(q,null,isPrincipalId),'unverified');
 for(const field of ['principal','conversation','event']) {
  const changed=make();changed.operation.serviceAction.question[field]=field==='principal'?b:id(9);
  assert.equal(validateServiceQuestion(changed.operation,isPrincipalId),true);
  assert.equal(validateEnvelopeShape(changed,isPrincipalId),false);
 }
});
test('rejects schema additions, duplicate options, invalid scalar text and lifetime',()=>{
 for(const mutate of [q=>q.operation.extra=true,q=>q.operation.serviceAction.token='secret',q=>q.operation.options.push(q.operation.options[0]),q=>q.operation.text='\ud800',q=>q.operation.serviceAction.retryUntil='18446744073709551616',q=>q.operation.serviceAction.notBefore='01',q=>q.operation.serviceAction.notBefore='1\n',q=>{q.operation.serviceAction.notBefore='2';q.operation.serviceAction.retryUntil='1';}]) {
  const q=make();mutate(q);assert.equal(validateEnvelopeShape(q,isPrincipalId),false);
 }
});
test('origin grammar refuses normalization, literals and unsupported A-labels',()=>{
 for(const value of ['https://answers.example','https://a-b.example:1','https://answers.example:65535'])assert.equal(isServiceOrigin(value),true,value);
 for(const value of ['http://answers.example','https://Answers.example','https://answers.example/','https://answers.example.','https://answers.example:443','https://answers.example:0443','https://answers.example:0','https://answers.example:65536','https://user@answers.example','https://127.0.0.1','https://127.1','https://0x7f000001','https://[::1]','https://xn--bcher-kva.example','https://bücher.example','https://a_.example','https://-a.example','https://a-.example','https://answers.example\n'])assert.equal(isServiceOrigin(value),false,value);
});
test('endpoint grammar preserves exact paths without URL normalization',()=>{
 const origin='https://answers.example';
 for(const path of ['/','/submit','/a-b_~.c/%C3%A9','/a//b/'])assert.equal(isServiceEndpoint(origin+path,origin),true,path);
 for(const path of ['', '/a/../b','/./','/%2E','/%61','/%2F','/%5C','/%c3%A9','/%GG','/a?x=1','/a#b','/a\\b','/é','/a\n','/a b'])assert.equal(isServiceEndpoint(origin+path,origin),false,path);
 assert.equal(isServiceEndpoint(origin+'/status',origin,{prefix:true}),false);
 assert.equal(isServiceEndpoint('https://answers.example.evil/submit',origin),false);
});
test('projection is escaped inert wording, with no endpoints or resolver calls',()=>{
 const q=make(),p=projectReadable(q,()=>assert.fail('No history lookup'),isPrincipalId);
 assert.equal(p.state,'projected');assert.match(p.text,/Tuesday & Wednesday/);assert.match(p.text,/Thursday/);
 assert.match(p.text,/https:\/\/answers.example/);assert.match(p.text,/ordinary email reply contacts the sender/);
 assert.match(p.text,/Opening this message submits nothing/);assert.match(p.html,/&lt;day&gt;/);
 assert.doesNotMatch(p.html,/<(?:a|button|form|script)\b|href=|\/submit|\/status/);
});
test('conversation resolver, graph and received-answer path reject service targets',()=>{
 const question=make(),answer={version:'0',purpose:'contribution',...ref(6,b),audience:[a,b],operation:{kind:'answer',question:ref(2),option:id(3),replaces:[]}};
 const lookup=r=>({state:'valid',event:r.event===answer.event?answer:question});
 assert.equal(resolveButtonAnswer(answer,lookup,isPrincipalId).state,'invalid');
 const graph=evaluateButtonAnswers(ref(2),[ref(6,b)],lookup,isPrincipalId);
 assert.equal(graph.results.find(r=>r.ref.event===answer.event).state,'invalid');
 const alice=encodeCredentialIdentity(a,'end0:'+'03'.repeat(32)),bob=encodeCredentialIdentity(b,'end0:'+'04'.repeat(32));
 const context={version:'0',purpose:'conversation-context',conversation:id(1),profile:'mls-1-0001',administrators:[a]};
 assert.equal(prepareReceivedAnswer(ref(6,b),bob,context,[alice,bob],lookup).state,'invalid');
});
