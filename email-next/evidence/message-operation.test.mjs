import test from 'node:test';
import assert from 'node:assert/strict';
import {validateMessageShape,resolveMessageReply} from './message-operation.mjs';
import {validateEnvelopeShape} from './event-envelope.mjs';
const p=x=>['alice','bob'].includes(x);
const ref={principal:'bob',event:'1'.repeat(32),conversation:'2'.repeat(32)};
const envelope=()=>({version:'0',purpose:'contribution',principal:'alice',event:'3'.repeat(32),conversation:ref.conversation,audience:['alice','bob'],operation:{kind:'message',text:'Hello',replyTo:[ref]}});
test('message passes common envelope and preserves literal text',()=>{
 const e=envelope();e.operation.text='<script>literal text</script>\nこんにちは';
 assert.equal(validateEnvelopeShape(e,p),true);
 assert.equal(validateMessageShape({kind:'message',text:'',replyTo:[]},p),true);
});
test('shape excludes extra fields malformed strings and multiple reply targets',()=>{
 const m=envelope().operation;
 for(const v of [{...m,html:'x'},{...m,text:'\ud800'},{...m,replyTo:[ref,ref]},{...m,replyTo:null},{...m,kind:'edit'}])assert.equal(validateMessageShape(v,p),false);
});
test('missing target stays pending without suppressing message text',()=>{
 const e=envelope();assert.deepEqual(resolveMessageReply(e,()=>({state:'pending'})),{state:'pending'});assert.equal(e.operation.text,'Hello');
});
test('cross conversation reply never calls resolver',()=>{
 const e=envelope();e.operation.replyTo=[{...ref,conversation:'4'.repeat(32)}];
 assert.equal(resolveMessageReply(e,()=>assert.fail()).state,'invalid');
});
test('resolved identity must match all three reference fields',()=>{
 const e=envelope();assert.equal(resolveMessageReply(e,()=>({state:'valid',event:ref})).state,'target-matched');
 for(const patch of [{principal:'alice'},{event:'5'.repeat(32)},{conversation:'6'.repeat(32)}])assert.equal(resolveMessageReply(e,()=>({state:'valid',event:{...ref,...patch}})).state,'invalid');
});
test('conflict invalid and no target remain distinct',()=>{
 const e=envelope();for(const state of ['conflict','invalid'])assert.equal(resolveMessageReply(e,()=>({state})).state,state);
 e.operation.replyTo=[];assert.equal(resolveMessageReply(e,()=>assert.fail()).state,'no-target');
});
