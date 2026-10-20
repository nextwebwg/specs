import test from 'node:test';import assert from 'node:assert/strict';
import {projectReadable} from './readable-projection.mjs';import {validateEnvelopeShape} from './event-envelope.mjs';
const p='enp0:'+'1'.repeat(64),check=s=>s===p,conversation='1'.repeat(32);
const ref=id=>({principal:p,conversation,event:id.repeat(32)});
const wrap=(id,operation)=>({version:'0',purpose:'contribution',...ref(id),audience:[p],operation});
const target=wrap('2',{kind:'message',text:'PRIVATE HISTORY <script>',replyTo:[]});
const reaction=wrap('3',{kind:'reaction',target:ref('2'),emoji:'👍'});
const withdrawal=wrap('4',{kind:'reaction-withdraw',target:ref('2'),reactions:[ref('3')]});
const resolve=r=>({state:'valid',event:r.event===target.event?target:reaction});
test('envelope dispatch accepts reaction and withdrawal without widening schemas',()=>{
 assert.equal(validateEnvelopeShape(reaction,check),true);assert.equal(validateEnvelopeShape(withdrawal,check),true);
 assert.equal(validateEnvelopeShape({...reaction,operation:{...reaction.operation,extra:true}},check),false);
});
test('reaction and withdrawal projection resolve dependencies without copying history',()=>{
 for(const event of [reaction,withdrawal]){const out=projectReadable(event,resolve,check);
 assert.equal(out.state,'projected');assert.ok(out.text.includes(target.event));
 assert.ok(!out.text.includes('PRIVATE'));assert.ok(!out.html.includes('<script>'));
 }
 assert.match(projectReadable(reaction,resolve,check).text,/not an answer or approval/);
});
test('pending, conflicted and invalid history cannot produce a validated projection',()=>{
 for(const state of ['pending','conflict','invalid'])assert.equal(projectReadable(reaction,()=>({state}),check).state,state);
 assert.equal(projectReadable(reaction,()=>({state:'valid',event:{...target,audience:[]}}),check).state,'invalid');
 assert.equal(projectReadable(withdrawal,r=>r.event===target.event?resolve(r):{state:'pending'},check).state,'pending');
});
