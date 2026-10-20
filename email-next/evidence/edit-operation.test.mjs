import test from 'node:test';
import assert from 'node:assert/strict';
import {validateEditShape, resolveEditTargets} from './edit-operation.mjs';
const principal = p => ['alice','bob'].includes(p);
const ref = n => ({principal:'alice', conversation:'c'.repeat(32), event:n.repeat(32)});
const root = {...ref('1'), operation:{kind:'message',text:'Meet at 3',replyTo:[]}};
const edit = () => ({...ref('2'), operation:{kind:'edit',root:ref('1'),predecessors:[ref('1')],text:'Meet at 4'}});
const resolve = r => r.event === root.event ? {state:'valid',event:root} : {state:'pending'};
test('complete replacement text is literal and may be empty', () => {
 const e=edit(); for(const text of ['', '<b>literal</b>', '明日']) {
  e.operation.text=text; assert.equal(resolveEditTargets(e,resolve,principal).state,'target-matched');
 }
});
test('shape rejects extra fields, duplicate references, empty predecessors and malformed text', () => {
 const op=edit().operation;
 for(const patch of [{extra:true},{predecessors:[]},{predecessors:[ref('1'),ref('1')]},{text:'\ud800'},{root:null},{kind:'message'}])
  assert.equal(validateEditShape({...op,...patch},principal),false);
});
test('cross-author, cross-conversation and self references cannot change a message', () => {
 for(const patch of [{principal:'bob'},{conversation:'d'.repeat(32)},{event:'2'.repeat(32)}]) {
  const e=edit(); e.operation.root={...ref('1'),...patch};
  assert.equal(resolveEditTargets(e,resolve,principal).state,'invalid');
 }
});
test('resolver must return the exact authenticated target and message kind', () => {
 for(const patch of [{principal:'bob'},{event:'9'.repeat(32)},{conversation:'d'.repeat(32)},{operation:edit().operation}])
  assert.equal(resolveEditTargets(edit(),()=>({state:'valid',event:{...root,...patch}}),principal).state,'invalid');
});
test('edit predecessors must share the root', () => {
 const e=edit();e.event='3'.repeat(32);e.operation.predecessors=[ref('2')];
 const predecessor=edit();
 const lookup=r=>r.event===root.event?resolve(r):{state:'valid',event:predecessor};
 assert.equal(resolveEditTargets(e,lookup,principal).state,'target-matched');
 predecessor.operation.root=ref('9');
 assert.equal(resolveEditTargets(e,lookup,principal).state,'invalid');
});
test('aggregate failures are order independent and never partially match', () => {
 const e=edit();e.operation.predecessors=[ref('4'),ref('5')];
 for(const states of [['pending','conflict'],['invalid','pending'],['conflict','invalid']]) {
  const lookup=r=>r.event===root.event?resolve(r):{state:r.event===ref('4').event?states[0]:states[1]};
  const expected=states.includes('invalid')?'invalid':'conflict';
  assert.equal(resolveEditTargets(e,lookup,principal).state,expected);
  e.operation.predecessors.reverse();
  assert.equal(resolveEditTargets(e,lookup,principal).state,expected);
 }
});

test('invalid scope anywhere prevents all target lookups',()=>{
 for(const part of ['root','predecessors']) for(const patch of [{principal:'bob'},{conversation:'d'.repeat(32)},{event:'2'.repeat(32)}]) {
  const e=edit();const invalid={...ref('1'),...patch};
  if(part==='root')e.operation.root=invalid;
  else e.operation.predecessors=[ref('1'),invalid];
  assert.equal(resolveEditTargets(e,()=>assert.fail('No lookup for an already invalid edit'),principal).state,'invalid');
 }
});
