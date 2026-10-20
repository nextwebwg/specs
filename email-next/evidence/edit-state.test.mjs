import test from 'node:test';
import assert from 'node:assert/strict';
import {evaluateEdit} from './edit-state.mjs';
const p=x=>x==='alice';
const ref=n=>({principal:'alice',conversation:'c'.repeat(32),event:n.repeat(32)});
const root={...ref('1'),operation:{kind:'message',text:'3',replyTo:[]}};
const edit=(n,parents)=>({...ref(n),operation:{kind:'edit',root:ref('1'),predecessors:parents.map(ref),text:n}});
function run(events, candidates, overrides={}) {
 const map=new Map(events.map(e=>[e.event,e]));
 return evaluateEdit(ref('1'),candidates.map(ref),r=>overrides[r.event] ?? (map.has(r.event)?{state:'valid',event:map.get(r.event)}:{state:'pending'}),p);
}
const heads=r=>r.heads.map(x=>x.event[0]).sort();
test('concurrent edits and explicit merge converge for representative delivery orderings',()=>{
 const events=[root,edit('2',['1']),edit('3',['1']),edit('4',['2','3'])];
 for(const ordered of [events,[...events].reverse(),[events[2],events[0],events[3],events[1]]])
  assert.deepEqual(heads(run(ordered,['4','3','2','4'])),['4']);
 assert.deepEqual(heads(run(events.slice(0,3),['3','2'])),['2','3']);
});
test('partial merge leaves other branch current',()=>{
 assert.deepEqual(heads(run([root,edit('2',['1']),edit('3',['1']),edit('4',['2'])],['4','3'])),['3','4']);
});
test('missing ancestor leaves edit pending while root remains current',()=>{
 const r=run([root,edit('3',['2'])],['3']);
 assert.deepEqual(heads(r),['1']);assert.equal(r.results.find(x=>x.ref.event===ref('3').event).state,'pending');
});
test('cycles and their descendants have no supersession effect',()=>{
 const r=run([root,edit('2',['3']),edit('3',['2']),edit('4',['2'])],['4']);
 assert.deepEqual(heads(r),['1']);
 for(const x of r.results.filter(x=>x.ref.event!==root.event)) assert.equal(x.state,'invalid');
});
test('changed authentication evidence restores valid predecessors',()=>{
 const events=[root,edit('2',['1']),edit('3',['2'])];
 assert.deepEqual(heads(run(events,['3'])),['3']);
 const r=run(events,['2','3'],{[ref('3').event]:{state:'conflict'}});
 assert.deepEqual(heads(r),['2']);
});
test('pending multi-parent edit preserves known valid predecessor',()=>{
 assert.deepEqual(heads(run([root,edit('2',['1']),edit('4',['2','3'])],['4'])),['2']);
});
test('long histories use one resolver read per distinct identity without recursion',()=>{
 const id=n=>n.toString(16).padStart(32,'0');
 const r=n=>({...ref('1'),event:id(n)});
 const events=new Map([[id(1),{...r(1),operation:root.operation}]]);
 for(let n=2;n<=12000;n++) events.set(id(n),{...r(n),operation:{kind:'edit',root:r(1),predecessors:[r(n-1)],text:'corrected'}});
 let reads=0;
 const result=evaluateEdit(r(1),[r(12000)],target=>{reads++;return {state:'valid',event:events.get(target.event)};},p);
 assert.equal(reads,12000);assert.deepEqual(result.heads,[r(12000)]);
});
test('local work exhaustion returns no partial heads and can be retried',()=>{
 const events=[root,edit('2',['1']),edit('3',['2'])];
 const lookup=r=>({state:'valid',event:events.find(e=>e.event===r.event)});
 for(const budget of [{maxRecords:2},{maxReferences:2}]) {
  const result=evaluateEdit(ref('1'),[ref('3')],lookup,p,budget);
  assert.equal(result.state,'incomplete');assert.equal(Object.hasOwn(result,'heads'),false);
 }
 assert.deepEqual(heads(evaluateEdit(ref('1'),[ref('3')],lookup,p,{maxRecords:3,maxReferences:6})),['3']);
});
test('invalid local budgets fail before history access',()=>{
 for(const maxRecords of [-1,1.5,NaN]) assert.throws(()=>evaluateEdit(ref('1'),[],()=>assert.fail(),p,{maxRecords}),TypeError);
});
test('impossible authority edges fail without resolving unrelated history',()=>{
 for(const patch of [{principal:'bob'},{conversation:'d'.repeat(32)},{event:ref('2').event}]) {
  const candidate=edit('2',['1']);candidate.operation.predecessors=[{...ref('1'),...patch}];
  const seen=[];
  const result=evaluateEdit(ref('1'),[ref('2')],r=>{
   seen.push(r);assert.ok(r.event===root.event || r.event===candidate.event);
   assert.equal(r.principal,'alice');assert.equal(r.conversation,root.conversation);
   return {state:'valid',event:r.event===root.event?root:candidate};
  },x=>['alice','bob'].includes(x));
  assert.equal(seen.length,2);assert.deepEqual(heads(result),['1']);
  assert.equal(result.results.find(x=>x.ref.event===candidate.event).state,'invalid');
 }
});
