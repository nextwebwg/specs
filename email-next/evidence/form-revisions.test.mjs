import {test} from 'node:test';
import assert from 'node:assert/strict';
import {deriveFormRevisions as derive} from './form-revisions.mjs';
const id=n=>String(n).padStart(32,'0');
const principal=p=>['alice','bob'].includes(p);
const field={field:id(80),type:'text',label:'Answer',required:true};
const ref=n=>({principal:'alice',event:id(n),conversation:id(90)});
function record(n,parents=[],patch={}) {
 const r={principal:'alice',id:id(n),conversation:id(90),operation:{kind:'form',form:id(70),title:'Q',fields:[field],supersedes:parents.map(ref)},...patch};
 r.octets=Buffer.from(JSON.stringify(r));return r;
}
const key=(n,p='alice')=>JSON.stringify([p,id(n)]);
function allOrders(records) {
 function permutations(a){return a.length?a.flatMap((v,i)=>permutations(a.filter((_,j)=>j!==i)).map(t=>[v,...t])):[[]];}
 const expected=derive(records,principal);
 for(const order of permutations(records))assert.deepEqual(derive(order,principal),expected);
 return expected;
}
test('concurrent revisions persist until explicit merge under every arrival order',()=>{
 const r=allOrders([record(1),record(2,[1]),record(3,[1])]);assert.deepEqual(r.heads,[key(2),key(3)]);
 assert.deepEqual(allOrders([record(1),record(2,[1]),record(3,[1]),record(4,[2,3])]).heads,[key(4)]);
});
test('missing parent stays pending and cannot suppress known root',()=>{
 const r=allOrders([record(1),record(3,[2])]);assert.equal(r.status[key(3)],'pending');assert.deepEqual(r.heads,[key(1)]);
});
test('cross-author revision cannot acquire form authority',()=>{
 const r=allOrders([record(1),record(2,[1],{principal:'bob'})]);assert.equal(r.status[key(2,'bob')],'invalid');assert.deepEqual(r.heads,[key(1)]);
});
test('changed type under same identifier fails even after field removal',()=>{
 const removed=record(2,[1]);removed.operation.fields=[];removed.octets=Buffer.from(JSON.stringify({...removed,octets:undefined}));
 const changed=record(3,[2]);changed.operation.fields=[{...field,type:'single-choice',choices:[{choice:id(81),label:'Yes'}]}];changed.octets=Buffer.from(JSON.stringify({...changed,octets:undefined}));
 const r=allOrders([record(1),removed,changed]);assert.equal(r.status[key(3)],'invalid');assert.deepEqual(r.heads,[key(2)]);
});
test('cycles and self references never select a head',()=>{
 assert.deepEqual(allOrders([record(1,[2]),record(2,[1])]).heads,[]);
 assert.equal(derive([record(1,[1])],principal).status[key(1)],'invalid');
});
test('two initial definitions conflict rather than selecting first arrival',()=>{
 const r=allOrders([record(1),record(2)]);assert.equal(r.status[key(1)],'conflict');assert.equal(r.status[key(2)],'conflict');assert.deepEqual(r.heads,[]);
});
test('exact duplicate coalesces while distinct authenticated bytes conflict',()=>{
 const one=record(1);assert.deepEqual(derive([one,one],principal).heads,[key(1)]);
 const other={...one,octets:Buffer.concat([one.octets,Buffer.from(' ')])};
 const r=allOrders([one,other,record(2,[1])]);assert.equal(r.status[key(1)],'conflict');assert.equal(r.status[key(2)],'invalid');
});
test('different authors may create forms with the same opaque identifier',()=>{
 assert.deepEqual(allOrders([record(1),record(1,[],{principal:'bob'})]).heads,[key(1),key(1,'bob')].sort());
});
