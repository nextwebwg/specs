import test from 'node:test';
import assert from 'node:assert/strict';
import {projectReadable} from './readable-projection.mjs';
const id=n=>String(n).repeat(32),p=x=>['a','b'].includes(x);
const form={kind:'form',form:id(3),title:'<img src=x>',fields:[{field:id(4),label:'Name',type:'text',required:false},{field:id(5),label:'Pick',type:'multiple-choice',required:false,choices:[{choice:id(6),label:'First & one'},{choice:id(7),label:'Second'}]}],supersedes:[]};
const env=operation=>({version:'0',purpose:'contribution',event:id(1),conversation:id(2),principal:'a',audience:['a','b'],operation});
const ref={principal:'b',event:id(8),conversation:id(2)};
const resolve=()=>({state:'valid',event:{principal:'b',id:id(8),conversation:id(2),operation:form}});
const submit=()=>({kind:'submit',form:id(3),revision:ref,answers:[],supersedes:[]});
test('form fallback includes labels choices and no active controls',()=>{
 const result=projectReadable(env(form),resolve,p);
 assert.equal(result.state,'projected');assert.ok(result.text.includes('<img src=x>'));
 assert.ok(result.html.includes('&lt;img src=x&gt;'));assert.ok(result.html.includes('First &amp; one'));
 assert.equal(result.html.includes('<input'),false);assert.equal(result.html.includes('<img'),false);
});
test('message preserves newlines and markup as text',()=>{
 const text='Hello\n<script>alert(1)</script>';
 const result=projectReadable(env({kind:'message',text,replyTo:[]}),resolve,p);
 assert.equal(result.text,text);assert.ok(result.html.includes('&lt;script&gt;'));
});
test('empty and unanswered answers remain distinct',()=>{
 const op=submit();op.answers=[{field:id(4),value:''},{field:id(5),value:[]}];
 const result=projectReadable(env(op),resolve,p);
 assert.ok(result.text.includes('[empty text]'));assert.ok(result.text.includes('[no choices selected]'));
 assert.ok(projectReadable(env(submit()),resolve,p).text.includes('[unanswered]'));
});
test('choice order follows exact revision and includes selected labels only',()=>{
 const op=submit();op.answers=[{field:id(5),value:[id(7),id(6)]}];
 const result=projectReadable(env(op),resolve,p);assert.ok(result.text.indexOf('- First')<result.text.indexOf('- Second'));
});
test('unavailable or substituted revision cannot produce guessed fallback',()=>{
 for(const state of ['pending','conflict','invalid'])assert.equal(projectReadable(env(submit()),()=>({state}),p).state,state);
 assert.equal(projectReadable(env(submit()),()=>({state:'valid',event:{...resolve().event,id:id(9)}}),p).state,'invalid');
});
test('invalid answer prevents entire projection',()=>{
 const op=submit();op.answers=[{field:id(4),value:'valid'},{field:id(5),value:[id(9)]}];
 assert.deepEqual(projectReadable(env(op),resolve,p),{state:'invalid'});
});

test('withdrawal fallback names exact responses without claiming reversal',()=>{
 const target={principal:'a',event:id(9),conversation:id(2)};
 const op={kind:'withdraw',form:id(3),revision:ref,submissions:[target]};
 const resolver=r=>r.event===id(9)?{state:'valid',event:{principal:'a',id:id(9),conversation:id(2),operation:submit()}}:resolve(r);
 const result=projectReadable(env(op),resolver,p);
 assert.equal(result.state,'projected');assert.ok(result.text.includes(id(9)));
 assert.ok(result.text.includes('does not erase'));assert.ok(result.text.includes('reverse an external action'));
});
test('authenticated-v1 projection makes declared external sharing visible without recipient metadata',()=>{
 const value={...env({kind:'message',text:'A message',replyTo:[]}),version:'1',disclosures:[{kind:'plaintext-email'},{kind:'provider-hosted',service:'https://host.example',model:'bearer'}]};
 const result=projectReadable(value,resolve,p);
 assert.equal(result.state,'projected');assert.match(result.text,/Author-declared external sharing/);
 assert.match(result.text,/Readable email outside/);assert.match(result.text,/Provider-hosted bearer access at https:\/\/host.example/);
 assert.match(result.text,/does not prove current availability/);assert.equal(result.text.includes('recipient'),false);
});
