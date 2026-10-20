import test from 'node:test';import assert from 'node:assert/strict';import {evaluateReactions} from './reaction-state.mjs';
const isPrincipal=s=>['alice','bob'].includes(s),conversation='1'.repeat(32);
const ref=(event,principal='alice')=>({event:event.repeat(32),principal,conversation});
const target=ref('2'),r1=ref('3'),r2=ref('4'),w=ref('5');
const event=(r,operation)=>({...r,operation});
const reaction=r=>event(r,{kind:'reaction',target,emoji:'👍'});
const withdrawal=(reactions=[r1])=>event(w,{kind:'reaction-withdraw',target,reactions});
const key=r=>JSON.stringify([r.principal,r.conversation,r.event]);
function run(records,candidates=[r1,r2,w],budget){const map=new Map(records.map(e=>[key(e),{state:'valid',event:e}]));
 return evaluateReactions(target,candidates,r=>map.get(key(r)),isPrincipal,budget);}
const root=event(target,{kind:'message',text:'hello',replyTo:[]});
test('duplicates do not duplicate events; intentional equal emoji events survive',()=>{
 assert.deepEqual(run([root,reaction(r1),reaction(r2)],[r1,r1,r2]).active,[r1,r2]);
});
test('withdrawal and referenced reaction arrival order has deterministic results',()=>{
 const records=[root,reaction(r1),reaction(r2),withdrawal()];
 const expected=run(records);
 assert.deepEqual(expected.active,[r2]);
 assert.deepEqual(run([...records].reverse(),[w,r2,r1]),expected);
 // An explicitly referenced valid reaction is resolved even if absent from initial candidates.
 assert.deepEqual(run(records,[w]).active,[]);
});
test('missing withdrawal dependency suppresses nothing; older removal cannot remove later equal reaction',()=>{
 const out=run([root,reaction(r1),reaction(r2),withdrawal([r1,ref('6')])]);
 assert.deepEqual(out.active,[r1,r2]);assert.equal(out.results.find(r=>key(r.ref)===key(w)).state,'pending');
 assert.deepEqual(run([root,reaction(r1),reaction(r2),withdrawal()]).active,[r2]);
});
test('wrong author, target, self-reference and withdrawal chains are invalid',()=>{
 for(const bad of [event({...w,principal:'bob'},{kind:'reaction-withdraw',target,reactions:[r1]}),
  withdrawal([w]),withdrawal([ref('6')])]){
 const other=event(ref('6'),{kind:'reaction-withdraw',target,reactions:[r1]});
 const out=run([root,reaction(r1),bad,other],[{...bad,operation:undefined}].map(({principal,conversation,event})=>({principal,conversation,event})));
 assert.equal(out.results.find(r=>key(r.ref)===key(bad)).state,'invalid');
 }
 const wrong=reaction(r1);wrong.operation.target=ref('7');
 assert.equal(run([root,wrong],[r1]).results.find(r=>key(r.ref)===key(r1)).state,'invalid');
});
test('target missing or conflicted never yields a current badge; exact edit version is eligible',()=>{
 assert.deepEqual(run([reaction(r1)],[r1]).active,[]);
 const out=evaluateReactions(target,[r1],r=>key(r)===key(target)?{state:'conflict'}:{state:'valid',event:reaction(r1)},isPrincipal);
 assert.equal(out.results.find(r=>key(r.ref)===key(r1)).state,'conflict');assert.deepEqual(out.active,[]);
 assert.deepEqual(run([event(target,{kind:'edit'}),reaction(r1)],[r1]).active,[r1]);
});
test('local budgets return no prefix view and invalid limits fail',()=>{
 assert.deepEqual(run([root,reaction(r1)],[r1],{maxRecords:1}),{state:'incomplete',reason:'record-budget'});
 assert.deepEqual(run([root,reaction(r1)],[r1],{maxReferences:1}),{state:'incomplete',reason:'reference-budget'});
 assert.throws(()=>run([],[],{maxRecords:-1}),TypeError);
});
