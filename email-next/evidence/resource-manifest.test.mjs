import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {validateResourceManifest,resourceExpectation} from './resource-manifest.mjs';
import {assembleResource} from './resource-assembly.mjs';
const id='1'.repeat(32),sha256='a'.repeat(64);
const entry={id,size:'0',sha256};
test('empty manifest and zero-length entries are explicit',()=>{
 assert.equal(validateResourceManifest([]).state,'shape-valid');
 assert.deepEqual(resourceExpectation([entry],id,0),{state:'bounded',expected:{size:0,sha256}});
});
test('wire sizes are canonical unsigned decimal strings',()=>{
 for(const size of [0,null,'','00','01','+1','-1','1.0','1e3',' 1','18446744073709551616','9'.repeat(100)])
  assert.equal(validateResourceManifest([{...entry,size}]).state,'invalid');
 assert.equal(validateResourceManifest([{...entry,size:'18446744073709551615'}]).state,'shape-valid');
});
test('large valid lengths fail local limits without rounding',()=>{
 assert.equal(resourceExpectation([{...entry,size:'9007199254740993'}],id,Number.MAX_SAFE_INTEGER).state,'limit-exceeded');
 assert.equal(resourceExpectation([entry],id,Infinity).state,'invalid');
});
test('identities are unique and digest spelling is exact',()=>{
 assert.equal(validateResourceManifest([entry,entry]).state,'invalid');
 for(const change of [{id:'0'.repeat(32)},{sha256:sha256.toUpperCase()},{sha256:'a'.repeat(63)},{url:'https://example.test/'}])
  assert.equal(validateResourceManifest([{...entry,...change}]).state,'invalid');
 assert.equal(resourceExpectation([entry],'2'.repeat(32),10).state,'missing');
});
test('bounded manifest expectation feeds exact-byte assembly',()=>{
 const bytes=new TextEncoder().encode('resource');
 const manifest=[{id,size:String(bytes.length),sha256:createHash('sha256').update(bytes).digest('hex')}];
 const result=resourceExpectation(manifest,id,1024);
 assert.equal(result.state,'bounded');
 assert.deepEqual(assembleResource(result.expected,[{offset:0,bytes}],{maxBytes:1024,maxChunks:2,maxInputBytes:1024}),{state:'complete',bytes});
 const altered=bytes.slice();altered[0]^=1;
 assert.equal(assembleResource(result.expected,[{offset:0,bytes:altered}],{maxBytes:1024,maxChunks:2,maxInputBytes:1024}).state,'digest-mismatch');
});
