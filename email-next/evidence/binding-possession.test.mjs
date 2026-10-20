import test from 'node:test';
import assert from 'node:assert/strict';
import {generateKeyPairSync} from 'node:crypto';
import {signBindingBytes,verifyBindingBytes,signBindingPossession,verifyBindingPossession} from './binding-signature.mjs';
const key=()=>{const pair=generateKeyPairSync('ed25519');return {...pair,hex:pair.publicKey.export({format:'der',type:'spki'}).subarray(-32).toString('hex')};};
const bytes=Buffer.from('{"purpose":"device-binding"}');
test('possession and authorization cannot substitute for each other even with the same key',()=>{
 const k=key(),possession=signBindingPossession(bytes,k.privateKey),authorization=signBindingBytes(bytes,k.privateKey);
 assert.equal(verifyBindingPossession(bytes,possession,k.hex),'signature-valid');
 assert.equal(verifyBindingBytes(bytes,authorization,k.hex),'signature-valid');
 assert.equal(verifyBindingBytes(bytes,possession,k.hex),'invalid-proof');
 assert.equal(verifyBindingPossession(bytes,authorization,k.hex),'invalid-proof');
});
test('enrolling authority cannot prove possession of a different device key',()=>{
 const authority=key(),device=key();
 assert.equal(verifyBindingPossession(bytes,signBindingPossession(bytes,authority.privateKey),device.hex),'invalid-proof');
 assert.equal(verifyBindingPossession(bytes,signBindingPossession(bytes,device.privateKey),device.hex),'signature-valid');
});
test('possession binds original bytes and rejects malformed proof encoding',()=>{
 const k=key(),proof=signBindingPossession(bytes,k.privateKey);
 assert.equal(verifyBindingPossession(Buffer.concat([bytes,Buffer.from(' ')]),proof,k.hex),'invalid-proof');
 assert.equal(verifyBindingPossession(bytes,proof.toUpperCase(),k.hex),'invalid-proof');
 assert.equal(verifyBindingPossession(bytes,proof,k.hex.slice(2)),'invalid-proof');
});
