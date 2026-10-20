import {test} from 'node:test';
import assert from 'node:assert/strict';
import {validateAnswers} from './form-values.mjs';
const id=n=>String(n).padStart(32,'0');
const text={field:id(1),type:'text',required:true};
const single={field:id(2),type:'single-choice',required:false,choices:[{choice:id(5)},{choice:id(6)}]};
const multi={...single,field:id(3),type:'multiple-choice',required:true};
const fields=[text,single,multi];
const baseline=[{field:id(1),value:''},{field:id(3),value:[]}];
test('intentional empty answers satisfy presence while omission does not',()=>{
 assert.ok(validateAnswers(baseline,fields));
 assert.equal(validateAnswers(baseline.slice(1),fields),false);
});
test('unknown field invalidates an otherwise valid atomic answer set',()=>{
 assert.equal(validateAnswers([...baseline,{field:id(9),value:'extra'}],fields),false);
});
test('choice membership, type and uniqueness follow exact revision',()=>{
 for(const value of [[id(5),id(6)],[id(6),id(5)]]) assert.ok(validateAnswers([{field:id(1),value:'yes'},{field:id(3),value}],fields));
 for(const value of [[id(5),id(5)],[id(8)],id(5),null]) assert.equal(validateAnswers([{field:id(1),value:'yes'},{field:id(3),value}],fields),false);
 assert.equal(validateAnswers([...baseline,{field:id(2),value:[id(5)]}],fields),false);
 assert.ok(validateAnswers([...baseline,{field:id(2),value:id(5)}],fields));
});
test('duplicate fields and misspelled or extra members fail',()=>{
 for(const extra of [baseline[0],{field:id(2),value:id(5),label:'hidden'},{field:id(2),values:id(5)}]) assert.equal(validateAnswers([...baseline,extra],fields),false);
});
test('empty form still admits only an empty answer set',()=>{
 assert.ok(validateAnswers([],[]));assert.equal(validateAnswers(baseline,[]),false);
});
