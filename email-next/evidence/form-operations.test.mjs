import {test} from 'node:test';
import assert from 'node:assert/strict';
import {validateOperationShape as valid} from './form-operations.mjs';
import {validateAnswers} from './form-values.mjs';
const id=n=>String(n).padStart(32,'0');
const principal=p=>p==='fixture-author';
const ref={principal:'fixture-author',event:id(2),conversation:id(3)};
const text={field:id(4),label:'Answer',type:'text',required:true};
const form={kind:'form',form:id(1),title:'Question',fields:[text],supersedes:[]};
const submit={kind:'submit',form:id(1),revision:ref,answers:[{field:id(4),value:''}],supersedes:[]};
const withdrawal={kind:'withdraw',form:id(1),revision:ref,submissions:[{...ref,event:id(5)}]};
test('form, submission and withdrawal shapes compose with value validation',()=>{
 for(const value of [form,submit,withdrawal])assert.ok(valid(value,principal));
 assert.ok(validateAnswers(submit.answers,form.fields));
});
test('exact members reject extras and missing fields on every operation',()=>{
 for(const original of [form,submit,withdrawal]) {
  assert.equal(valid({...original,extra:false},principal),false);
  for(const key of Object.keys(original)) {
   const copy={...original};delete copy[key];assert.equal(valid(copy,principal),false);
  }
 }
});
test('text fields cannot have choices and choice fields need unique nonempty choices',()=>{
 const choice={...text,type:'single-choice',choices:[{choice:id(6),label:'Thursday'}]};
 assert.ok(valid({...form,fields:[choice]},principal));
 for(const field of [{...text,choices:[]},{...choice,choices:[]},{...choice,choices:[...choice.choices,...choice.choices]},{...text,required:'true'}])assert.equal(valid({...form,fields:[field]},principal),false);
});
test('duplicate field identifiers and malformed scalar labels fail',()=>{
 assert.equal(valid({...form,fields:[text,text]},principal),false);
 assert.equal(valid({...form,title:'\ud800'},principal),false);
 assert.ok(valid({...form,title:'\ud83d\ude00'},principal));
});
test('reference sets compare decoded fields independently of member order',()=>{
 const reordered={conversation:ref.conversation,event:ref.event,principal:ref.principal};
 assert.equal(valid({...form,supersedes:[ref,reordered]},principal),false);
 assert.equal(valid({...withdrawal,submissions:[]},principal),false);
 assert.equal(valid(withdrawal,()=>false),false);
});
test('shape validity does not claim resolved field membership or authority',()=>{
 const unknown={...submit,answers:[{field:id(9),value:'unknown'}]};
 assert.ok(valid(unknown,principal));
 assert.equal(validateAnswers(unknown.answers,form.fields),false);
});
test('nonbaseline values and duplicate answers fail before target resolution',()=>{
 for(const value of [null,true,4,{},[id(6),id(6)]])assert.equal(valid({...submit,answers:[{field:id(4),value}]},principal),false);
 assert.equal(valid({...submit,answers:[...submit.answers,...submit.answers]},principal),false);
});
