import test from 'node:test';
import assert from 'node:assert/strict';
import {evaluateButtonAnswers} from './button-state.mjs';
const id = n => n.toString(16).padStart(32,'0');
const principal = p => ['alice','bob'].includes(p);
const question = {principal:'alice', conversation:id(1), event:id(2)};
const ref = n => ({principal:'bob', conversation:id(1), event:id(n)});
const q = {...question, operation:{kind:'question',text:'When?',options:[{id:id(3),label:'Tuesday'}]}};
const answer = (n, previous=[]) => ({...ref(n),operation:{kind:'answer',question,option:id(3),replaces:previous.map(ref)}});
const key = r => JSON.stringify([r.principal,r.conversation,r.event]);
function evaluate(events, candidates=events.map(e=>ref(Number.parseInt(e.event,16))), limits) {
 const records=new Map([q,...events].map(e=>[key(e),{state:'valid',event:e}]));
 return evaluateButtonAnswers(question,candidates,r=>records.get(key(r)),principal,limits);
}
test('replacement result does not depend on delivery order and includes discovered ancestors',()=>{
 const first=answer(4), next=answer(5,[4]);
 for(const events of [[first,next],[next,first]]) {
  assert.deepEqual(evaluate(events,[ref(5)]).heads,[ref(5)]);
 }
});
test('concurrent answers remain visible until explicitly replaced together',()=>{
 const a=answer(4), b=answer(5);
 assert.equal(evaluate([a,b]).heads.length,2);
 assert.deepEqual(evaluate([a,b,answer(6,[4,5])]).heads,[ref(6)]);
});
test('missing ancestors and cycles never suppress a valid answer',()=>{
 const a=answer(4), pending=answer(5,[4,9]);
 assert.deepEqual(evaluate([a,pending]).heads,[ref(4)]);
 const cyclic=evaluate([a,answer(5,[6]),answer(6,[5]),answer(7,[5])]);
 assert.deepEqual(cyclic.heads,[ref(4)]);
 for(const n of [5,6,7]) assert.equal(cyclic.results.find(r=>r.ref.event===id(n)).state,'invalid');
});
test('invalid ancestor choice prevents a descendant from becoming current',()=>{
 const bad=answer(4);bad.operation.option=id(90);
 assert.deepEqual(evaluate([bad,answer(5,[4])]).heads,[]);
});
test('budget exhaustion yields no partial current-answer result',()=>{
 assert.deepEqual(evaluate([answer(4),answer(5,[4])],[ref(5)],{maxRecords:2}),{state:'incomplete',reason:'record-budget'});
});
test('long answer chains use iterative traversal',()=>{
 const events=Array.from({length:3000},(_,i)=>answer(i+4,i?[i+3]:[]));
 assert.deepEqual(evaluate(events,[ref(3003)]).heads,[ref(3003)]);
});
test('conflicted exact identity blocks dependent answers',()=>{
 const a=answer(5,[4]);
 const result=evaluateButtonAnswers(question,[ref(5)],r=>r.event===question.event?{state:'valid',event:q}:
  r.event===id(4)?{state:'conflict'}:{state:'valid',event:a},principal);
 assert.deepEqual(result.heads,[]);
 assert.equal(result.results.find(r=>r.ref.event===id(5)).state,'conflict');
});
