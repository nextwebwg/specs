import test from 'node:test';
import assert from 'node:assert/strict';
import {encodeCredentialIdentity as encode,decodeCredentialIdentity as decode} from './credential-identity.mjs';
const principal='enp0:'+'a'.repeat(64),device='end0:'+'b'.repeat(64);
test('identity bytes have fixed domain prefix and account/device order',()=>{
 const bytes=encode(principal,device);
 assert.equal(bytes.length,85);
 assert.equal(bytes.subarray(0,21).toString('ascii'),'email-next/device/v0\0');
 assert.deepEqual(decode(bytes),{principal,device});
});
test('trailing bytes truncation and other versions cannot alias',()=>{
 const bytes=encode(principal,device);
 for(const input of [bytes.subarray(0,-1),Buffer.concat([bytes,Buffer.from([0])]),Buffer.from(bytes).fill(1,0,1)])assert.throws(()=>decode(input));
});
test('zero and cross-domain identifiers fail',()=>{
 assert.throws(()=>encode(device,principal));
 assert.throws(()=>encode('enp0:'+'0'.repeat(64),device));
 const bytes=encode(principal,device);bytes.fill(0,21,53);assert.throws(()=>decode(bytes));
});
test('decoded identity does not contain mailbox or authorization claims',()=>{
 assert.deepEqual(Object.keys(decode(encode(principal,device))),['principal','device']);
});
