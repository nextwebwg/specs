import test from 'node:test';
import assert from 'node:assert/strict';
import {generateKeyPairSync,sign} from 'node:crypto';
import {signBindingBytes,verifyBindingBytes} from './binding-signature.mjs';
const key=generateKeyPairSync('ed25519');
const raw=k=>k.export({format:'der',type:'spki'}).subarray(-32).toString('hex');
const payload=Buffer.from('{"purpose":"device-binding","version":"0"}');
test('exact binding bytes verify under the signing key',()=>{
 assert.equal(verifyBindingBytes(payload,signBindingBytes(payload,key.privateKey),raw(key.publicKey)),'signature-valid');
});
test('byte change and equivalent JSON reserialization invalidate proof',()=>{
 const signature=signBindingBytes(payload,key.privateKey);
 for(const altered of [Buffer.from(payload.toString().replace('"0"','"1"')),Buffer.from(JSON.stringify(JSON.parse(payload),null,2))])assert.equal(verifyBindingBytes(altered,signature,raw(key.publicKey)),'invalid-proof');
});
test('wrong signer and missing domain context fail',()=>{
 const other=generateKeyPairSync('ed25519');
 assert.equal(verifyBindingBytes(payload,signBindingBytes(payload,key.privateKey),raw(other.publicKey)),'invalid-proof');
 assert.equal(verifyBindingBytes(payload,sign(null,payload,key.privateKey).toString('hex'),raw(key.publicKey)),'invalid-proof');
});
test('proof encodings and payload limits are strict',()=>{
 const signature=signBindingBytes(payload,key.privateKey);
 assert.equal(verifyBindingBytes(payload,signature.toUpperCase(),raw(key.publicKey)),'invalid-proof');
 assert.equal(verifyBindingBytes(new Uint8Array(1048577),signature,raw(key.publicKey)),'invalid-proof');
 assert.throws(()=>signBindingBytes(new Uint8Array(1048577),key.privateKey));
});
