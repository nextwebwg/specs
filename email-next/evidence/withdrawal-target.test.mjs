import test from 'node:test';
import assert from 'node:assert/strict';
import {validateWithdrawalTargets} from './withdrawal-target.mjs';
const id=n=>String(n).repeat(32),p=x=>['a','b'].includes(x);
const revision={principal:'b',event:id(1),conversation:id(2)};
const target={principal:'a',event:id(3),conversation:id(2)};
const event=()=>({principal:'a',conversation:id(2),operation:{kind:'withdraw',form:id(4),revision,submissions:[target]}});
const form={kind:'form',form:id(4),title:'Question',fields:[],supersedes:[]};
const submit={kind:'submit',form:id(4),revision,answers:[],supersedes:[]};
const resolver=ref=>({state:'valid',event:{principal:ref.principal,id:ref.event,conversation:ref.conversation,operation:ref.event===revision.event?form:submit}});
test('same-author exact submissions and form revision match',()=>assert.equal(validateWithdrawalTargets(event(),resolver,p).state,'targets-matched'));
test('another author and conversation fail before resolution',()=>{
 for(const patch of [{principal:'b'},{conversation:id(5)}]){
 const e=event();e.operation.submissions=[{...target,...patch}];assert.equal(validateWithdrawalTargets(e,()=>assert.fail(),p).state,'invalid');}
});
test('substituted identity revision or form cannot match',()=>{
 for(const patch of [{id:id(5)},{operation:{...submit,revision:{...revision,event:id(6)}}},{operation:{...submit,form:id(7)}}]){
 assert.equal(validateWithdrawalTargets(event(),r=>r.event===target.event?{state:'valid',event:{...resolver(r).event,...patch}}:resolver(r),p).state,'invalid');}
});
test('pending conflict invalid states remain distinct',()=>{
 for(const state of ['pending','conflict','invalid'])assert.equal(validateWithdrawalTargets(event(),r=>r.event===target.event?{state}:resolver(r),p).state,state);
});
test('aggregate outcome is independent of target order',()=>{
 const e=event(),second={...target,event:id(8)};e.operation.submissions=[target,second];
 const resolve=r=>r.event===target.event?{state:'pending'}:r.event===second.event?{state:'conflict'}:resolver(r);
 assert.equal(validateWithdrawalTargets(e,resolve,p).state,'conflict');e.operation.submissions.reverse();assert.equal(validateWithdrawalTargets(e,resolve,p).state,'conflict');
});
