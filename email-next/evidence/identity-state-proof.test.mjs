import test from 'node:test';
import assert from 'node:assert/strict';
import {generateKeyPairSync,createHash} from 'node:crypto';
import {signIdentityState,verifyIdentityState,signBindingBytes,verifyBindingBytes,signBindingPossession,verifyBindingPossession} from './binding-signature.mjs';
import {validateIdentityState} from './identity-state.mjs';
const pair=()=>{const k=generateKeyPairSync('ed25519');return {...k,hex:k.publicKey.export({format:'der',type:'spki'}).subarray(-32).toString('hex')};};
const state=()=>({version:'0',purpose:'identity-state',principal:'enp0:'+'a'.repeat(64),record:'1'.repeat(32),revision:'0',previous:[],issuedAt:'0',bindings:[{device:'end0:'+'b'.repeat(64),digest:'c'.repeat(64)}],revoked:[],signer:'end0:'+'b'.repeat(64)});
test('actual state payload has a byte-specific signature and digest',()=>{
 const k=pair(),value=state();assert.equal(validateIdentityState(value),true);
 const bytes=Buffer.from(JSON.stringify(value)),proof=signIdentityState(bytes,k.privateKey);
 assert.equal(verifyIdentityState(bytes,proof,k.hex),'signature-valid');
 const respelled=Buffer.from(JSON.stringify(value,null,2));
 assert.equal(verifyIdentityState(respelled,proof,k.hex),'invalid-proof');
 assert.notEqual(createHash('sha256').update(bytes).digest('hex'),createHash('sha256').update(respelled).digest('hex'));
});
test('all three proof purposes reject each other with identical key and payload',()=>{
 const k=pair(),bytes=Buffer.from(JSON.stringify(state()));
 const signs=[signBindingBytes,signBindingPossession,signIdentityState],verifies=[verifyBindingBytes,verifyBindingPossession,verifyIdentityState];
 for(let i=0;i<3;i++)for(let j=0;j<3;j++)assert.equal(verifies[j](bytes,signs[i](bytes,k.privateKey),k.hex),i===j?'signature-valid':'invalid-proof');
});
test('state modification wrong key and noncanonical proof encodings fail',()=>{
 const k=pair(),v=state(),bytes=Buffer.from(JSON.stringify(v)),proof=signIdentityState(bytes,k.privateKey);
 v.revoked=['end0:'+'d'.repeat(64)];
 assert.equal(verifyIdentityState(Buffer.from(JSON.stringify(v)),proof,k.hex),'invalid-proof');
 assert.equal(verifyIdentityState(bytes,proof,pair().hex),'invalid-proof');
 assert.equal(verifyIdentityState(bytes,proof.toUpperCase(),k.hex),'invalid-proof');
});
