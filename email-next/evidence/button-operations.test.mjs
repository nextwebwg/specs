import test from 'node:test';
import assert from 'node:assert/strict';
import {validateButtonOperation as shape, resolveButtonAnswer as resolve} from './button-operations.mjs';
const id = n => String(n).repeat(32);
const principal = p => ['alice', 'bob'].includes(p);
const ref = {principal:'alice', conversation:id(1), event:id(2)};
const question = {kind:'question', text:'Which day works?', options:[{id:id(3),label:'Tuesday'},{id:id(4),label:'Thursday'}]};
const answer = () => ({principal:'bob',conversation:id(1),event:id(5),operation:{kind:'answer',question:ref,option:id(4),replaces:[]}});
const lookup = () => ({state:'valid',event:{...ref,operation:question}});
test('button answer resolves exact question and option without a form', () => {
 assert.equal(shape(question,principal),true);
 assert.deepEqual(resolve(answer(),lookup,principal),{state:'references-matched',question:'Which day works?',answer:'Thursday'});
});
test('invalid vocabulary and malformed controls are refused', () => {
 for (const q of [{...question,options:[]},{...question,text:' '},{...question,text:'\ud800'},
 {...question,options:[question.options[0],question.options[0]]},{...question,callback:'https://example.test'},
 {...question,options:[{...question.options[0],label:''}]}]) assert.equal(shape(q,principal),false);
});
test('unknown choice is invalid and missing question stays pending', () => {
 const a=answer();a.operation.option=id(6);
 assert.equal(resolve(a,lookup,principal).state,'invalid');
 assert.equal(resolve(answer(),()=>null,principal).state,'pending');
 assert.equal(resolve(answer(),()=>({state:'conflict'}),principal).state,'conflict');
});
test('cross-conversation and cross-author replacements never call resolver', () => {
 const a=answer();a.operation.replaces=[{...ref}];
 assert.equal(resolve(a,()=>assert.fail(),principal).state,'invalid');
 a.operation.replaces=[];a.operation.question={...ref,conversation:id(7)};
 assert.equal(resolve(a,()=>assert.fail(),principal).state,'invalid');
});
test('replacement must name same question and exact resolved identity', () => {
 const a=answer();const prior={principal:'bob',conversation:id(1),event:id(8)};
 a.operation.replaces=[prior];
 const old={...prior,operation:{...answer().operation}};
 const get=r=>r.event===ref.event?lookup():{state:'valid',event:old};
 assert.equal(resolve(a,get,principal).state,'references-matched');
 old.operation.question={...ref,event:id(9)};
 assert.equal(resolve(a,get,principal).state,'invalid');
 old.operation.question=ref;old.principal='alice';
 assert.equal(resolve(a,get,principal).state,'invalid');
});
test('duplicate and self replacements are rejected', () => {
 const a=answer();const r={principal:'bob',conversation:id(1),event:id(8)};
 a.operation.replaces=[r,r];assert.equal(shape(a.operation,principal),false);
 a.operation.replaces=[{...r,event:a.event}];assert.equal(resolve(a,()=>assert.fail(),principal).state,'invalid');
});
