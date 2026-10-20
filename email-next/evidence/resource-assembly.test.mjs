import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {assembleResource} from './resource-assembly.mjs';
const source=new TextEncoder().encode('hello 世界');
const expected=bytes=>({size:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')});
const limits={maxBytes:1024,maxChunks:16,maxInputBytes:4096};
const run=chunks=>assembleResource(expected(source),chunks,limits);
test('out-of-order ranges and identical overlaps reconstruct exact bytes',()=>{
 const chunks=[{offset:5,bytes:source.slice(5)},{offset:0,bytes:source.slice(0,7)}];
 for(const order of [chunks,[...chunks].reverse(),[...chunks,chunks[0]]])assert.deepEqual(run(order),{state:'complete',bytes:source});
});
test('gaps and conflicting overlaps expose no output bytes',()=>{
 assert.deepEqual(run([{offset:1,bytes:source.slice(1)}]),{state:'incomplete'});
 assert.deepEqual(run([{offset:0,bytes:source},{offset:0,bytes:new Uint8Array([0])}]),{state:'conflict'});
});
test('full range with wrong digest remains unusable',()=>{
 const changed=source.slice();changed[0]^=1;
 assert.deepEqual(run([{offset:0,bytes:changed}]),{state:'digest-mismatch'});
});
test('out-of-range and invalid offsets do not clamp',()=>{
 for(const offset of [-1,0.5,Number.MAX_SAFE_INTEGER,source.length+1])assert.equal(run([{offset,bytes:new Uint8Array([1])}]).state,'invalid');
 assert.equal(run([{offset:source.length,bytes:new Uint8Array([1])}]).state,'invalid');
});
test('caller limit applies before assembly and empty resources are explicit',()=>{
 assert.deepEqual(assembleResource(expected(source),[],{...limits,maxBytes:source.length-1}),{state:'limit-exceeded'});
 const empty=new Uint8Array();assert.deepEqual(assembleResource(expected(empty),[],{maxBytes:0,maxChunks:0,maxInputBytes:0}),{state:'complete',bytes:empty});
});
test('partial UTF-8 byte boundaries are preserved without text repair',()=>{
 const result=run([{offset:0,bytes:source.slice(0,8)},{offset:8,bytes:source.slice(8)}]);
 assert.equal(result.state,'complete');assert.equal(new TextDecoder('utf-8',{fatal:true}).decode(result.bytes),'hello 世界');
});

test('duplicate work and zero-length chunk floods have separate limits',()=>{
 const whole={offset:0,bytes:source};
 assert.equal(assembleResource(expected(source),[whole,whole],{...limits,maxInputBytes:source.length}).state,'limit-exceeded');
 assert.equal(assembleResource(expected(source),[whole,whole],{...limits,maxInputBytes:source.length*2}).state,'complete');
 const empty=Array.from({length:17},()=>({offset:0,bytes:new Uint8Array()}));
 assert.equal(assembleResource(expected(source),empty,limits).state,'limit-exceeded');
});
test('invalid and absent caller limits never imply unlimited processing',()=>{
 for(const policy of [undefined,{}, {...limits,maxChunks:-1},{...limits,maxInputBytes:Infinity}])assert.equal(assembleResource(expected(source),[],policy).state,'invalid');
});
