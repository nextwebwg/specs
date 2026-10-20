import test from 'node:test';
import assert from 'node:assert/strict';
import {rendererNonce} from './browser-render-host.mjs';
test('default nonce preserves every bit of sixteen random bytes',t=>{
 let calls=0;t.mock.method(crypto,'getRandomValues',bytes=>{calls++;assert.equal(bytes.length,16);for(let i=0;i<16;i++)bytes[i]=i*17;return bytes;});
 assert.equal(rendererNonce(),'00112233445566778899aabbccddeeff');assert.equal(calls,1);
});
test('real default uses accepted alphabet and fresh generation',()=>{
 const a=rendererNonce(),b=rendererNonce();assert.match(a,/^[0-9a-f]{32}$/);assert.match(b,/^[0-9a-f]{32}$/);assert.notEqual(a,b);
});
test('trusted override remains explicit syntax-only configuration',t=>{
 t.mock.method(crypto,'getRandomValues',()=>{throw Error('override should not generate');});
 assert.equal(rendererNonce('fixed_test_nonce_123'),'fixed_test_nonce_123');
 for(const value of ['',1,'<script>abcdefghijk','x'.repeat(129)])assert.throws(()=>rendererNonce(value),/sandbox-nonce/);
});
