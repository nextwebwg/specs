import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {resourceContentId,bindResource} from './resource-binding.mjs';
const event='1'.repeat(32),id='2'.repeat(32),other='3'.repeat(32);
const bytes=new TextEncoder().encode('attachment');
const manifest=[{id,size:String(bytes.length),sha256:createHash('sha256').update(bytes).digest('hex')}];
const part={contentId:resourceContentId(event,id),bytes};
const limits={maxBytes:1024,maxChunks:1,maxInputBytes:1024};
const run=parts=>bindResource(event,manifest,id,parts,limits);
test('one scoped transfer-decoded part validates complete bytes',()=>assert.deepEqual(run([part]),{state:'complete',bytes}));
test('identical duplicate parts remain ambiguous',()=>assert.deepEqual(run([part,part]),{state:'ambiguous'}));
test('another event and noncanonical casing cannot satisfy lookup',()=>{
 for(const contentId of [resourceContentId(other,id),part.contentId.toUpperCase(),`<${part.contentId}>`])assert.deepEqual(run([{...part,contentId}]),{state:'missing'});
});
test('substituted bytes never inherit manifest protection',()=>{
 const altered=bytes.slice();altered[0]^=1;
 assert.deepEqual(run([{...part,bytes:altered}]),{state:'digest-mismatch'});
 assert.deepEqual(run([{...part,bytes:bytes.slice(1)}]),{state:'incomplete'});
});
test('unknown manifest identity and local limits remain failures',()=>{
 assert.deepEqual(bindResource(event,manifest,other,[part],limits),{state:'missing'});
 assert.deepEqual(bindResource(event,manifest,id,[part],{...limits,maxBytes:1}),{state:'limit-exceeded'});
});
