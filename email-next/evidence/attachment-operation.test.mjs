import test from 'node:test';
import assert from 'node:assert/strict';
import {validateEnvelopeShape} from './event-envelope.mjs';
import {projectReadable} from './readable-projection.mjs';
const id='1'.repeat(32);
const make=()=>({version:'0',purpose:'contribution',event:'2'.repeat(32),conversation:'3'.repeat(32),principal:'alice',audience:['alice'],operation:{kind:'attachment-message',text:'Here it is',replyTo:[],manifest:[{id,size:'0',sha256:'a'.repeat(64)}],attachments:[{resource:id,name:'<script>name</script>',description:'A description',mediaType:'application/pdf'}]}});
const principal=p=>p==='alice';
test('attachment contribution passes envelope and produces inert readable metadata',()=>{
 const event=make();assert.equal(validateEnvelopeShape(event,principal),true);
 const projected=projectReadable(event,()=>assert.fail(),principal);
 assert.equal(projected.state,'projected');assert.ok(projected.text.includes('<script>name</script>'));
 assert.ok(!projected.html.includes('<script>'));assert.ok(projected.html.includes('&lt;script&gt;'));
 assert.ok(projected.text.includes('do not confirm'));
});
test('unused or absent resources cannot hide in attachment messages',()=>{
 const event=make();event.operation.manifest.push({...event.operation.manifest[0],id:'4'.repeat(32)});
 assert.equal(validateEnvelopeShape(event,principal),false);
 event.operation.manifest=[];assert.equal(validateEnvelopeShape(event,principal),false);
 event.operation.attachments=[];assert.equal(validateEnvelopeShape(event,principal),false);
});
test('operation kind and exact members prevent implicit message upgrade',()=>{
 const event=make();event.operation.kind='message';assert.equal(validateEnvelopeShape(event,principal),false);
 event.operation.kind='attachment-message';event.operation.html='<p>extra</p>';assert.equal(validateEnvelopeShape(event,principal),false);
});
