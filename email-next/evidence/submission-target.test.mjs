import {test} from 'node:test';
import assert from 'node:assert/strict';
import {validateSubmissionTarget as check} from './submission-target.mjs';
const id=n=>String(n).padStart(32,'0');
const isPrincipal=p=>['author','respondent'].includes(p);
const reference={principal:'author',event:id(1),conversation:id(2)};
const revision={principal:'author',id:id(1),conversation:id(2),operation:{kind:'form',form:id(3),title:'Day?',supersedes:[],fields:[{field:id(4),label:'Day',required:true,type:'single-choice',choices:[{choice:id(5),label:'Thursday'}]}]}};
const event={principal:'respondent',id:id(6),conversation:id(2),operation:{kind:'submit',form:id(3),revision:reference,supersedes:[],answers:[{field:id(4),value:id(5)}]}};
const resolve=()=>({state:'valid',event:revision});
test('exact authenticated form revision supports answer target validation',()=>{
 assert.equal(check(event,resolve,isPrincipal).state,'target-valid');
});
test('missing, conflicted and invalid revisions retain distinct states',()=>{
 for(const state of ['pending','conflict','invalid'])assert.equal(check(event,()=>({state}),isPrincipal).state,state);
});
test('resolver cannot substitute newer revision or another principal',()=>{
 for(const patch of [{id:id(9)},{principal:'respondent'},{conversation:id(8)}])
  assert.equal(check(event,()=>({state:'valid',event:{...revision,...patch}}),isPrincipal).reason,'reference-mismatch');
});
test('cross-conversation reference fails without invoking resolver',()=>{
 const cross={...event,conversation:id(9)};
 assert.equal(check(cross,()=>{throw new Error('must not resolve');},isPrincipal).reason,'cross-conversation');
});
test('wrong form and partial invalid answers cannot yield target-valid',()=>{
 assert.equal(check({...event,operation:{...event.operation,form:id(9)}},resolve,isPrincipal).reason,'wrong-form');
 assert.equal(check({...event,operation:{...event.operation,answers:[...event.operation.answers,{field:id(9),value:'extra'}]}},resolve,isPrincipal).reason,'answer-values');
});
test('newer available definition does not change old choice meaning',()=>{
 const newer={...revision,id:id(7),operation:{...revision.operation,fields:[{...revision.operation.fields[0],choices:[{choice:id(5),label:'Friday'}]}]}};
 const records=[newer,revision];
 const lookup=ref=>({state:'valid',event:records.find(r=>r.id===ref.event)});
 assert.equal(check(event,lookup,isPrincipal).state,'target-valid');
 assert.equal(lookup(reference).event.operation.fields[0].choices[0].label,'Thursday');
});
test('undefined resolver outcomes fail closed rather than authorizing effects',()=>{
 for(const result of [undefined,{state:'unknown'},{state:'valid'}])assert.equal(check(event,()=>result,isPrincipal).state,'invalid');
});
