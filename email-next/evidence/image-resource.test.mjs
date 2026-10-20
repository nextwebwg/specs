import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {resolveImageCandidate} from './image-resource.mjs';
import {resourceContentId} from './resource-binding.mjs';
const event='1'.repeat(32),id='2'.repeat(32);
const bytes=new TextEncoder().encode('not actually a decoded image');
const manifest=[{id,size:String(bytes.length),sha256:createHash('sha256').update(bytes).digest('hex')}];
const part={contentId:resourceContentId(event,id),bytes};
const limits={maxBytes:1024,maxChunks:1,maxInputBytes:1024};
const run=(candidate,parts=[part],bound=limits)=>resolveImageCandidate(candidate,event,manifest,parts,bound);
const source='cid:'+part.contentId;
test('CID escapes decode once and successful binding is not image conformance',()=>{
  for(const candidate of [source,source.replace('@','%40'),'CID:'+part.contentId]) {
    assert.deepEqual(run(candidate),{state:'encoded-resource',id,bytes});
  }
});
test('external URLs, double escapes and cross-event references are rejected',()=>{
  for(const candidate of ['https://example.test/pixel','data:image/png;base64,AA==',
    source.replace('@','%2540'),source.replace(event,'3'.repeat(32)),
    source+'#fragment',source+'?query',source+'%',source.replace('cid:','cid:<')+'>']) {
    assert.deepEqual(run(candidate),{state:'invalid'});
  }
});
test('missing and ambiguous parts do not release bytes',()=>{
  assert.deepEqual(run(source,[]),{state:'missing'});
  assert.deepEqual(run(source,[part,part]),{state:'ambiguous'});
});
test('digest substitution and resource limits survive CID resolution',()=>{
  const altered=bytes.slice();altered[0]^=1;
  assert.deepEqual(run(source,[{...part,bytes:altered}]),{state:'digest-mismatch'});
  assert.deepEqual(run(source,[part],{...limits,maxBytes:1}),{state:'limit-exceeded'});
});
