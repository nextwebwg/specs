import test from 'node:test';
import assert from 'node:assert/strict';
import {generateKeyPairSync} from 'node:crypto';
import {validateDeviceBinding} from './device-binding.mjs';
import {signBindingBytes,verifyBindingBytes} from './binding-signature.mjs';
const make=()=>({version:'0',purpose:'device-binding',record:'1'.repeat(32),principal:'enp0:'+'a'.repeat(64),device:'end0:'+'b'.repeat(64),signingKey:'c'.repeat(64),roles:['send','receive'],notBefore:'0',notAfter:'18446744073709551615',authority:{kind:'first-contact'}});
test('first-contact and established authority have distinct exact shapes',()=>{
 const record=make();assert.equal(validateDeviceBinding(record),true);
 record.authority={kind:'state',digest:'d'.repeat(64)};assert.equal(validateDeviceBinding(record),true);
 for(const authority of [{kind:'state'},{kind:'first-contact',digest:'d'.repeat(64)},{kind:'provider-login'}])assert.equal(validateDeviceBinding({...record,authority}),false);
});
test('roles times and identifiers cannot be silently repaired',()=>{
 const record=make();
 for(const patch of [{roles:[]},{roles:['send','send']},{roles:['admin']},{notBefore:'01'},{notAfter:'18446744073709551616'},{notBefore:'10',notAfter:'9'},{principal:record.device},{extra:true}])assert.equal(validateDeviceBinding({...record,...patch}),false);
});
test('real signed record remains byte-specific without becoming authorized',()=>{
 const {privateKey,publicKey}=generateKeyPairSync('ed25519');
 const signingKey=publicKey.export({format:'der',type:'spki'}).subarray(-32).toString('hex');
 const record={...make(),signingKey};assert.equal(validateDeviceBinding(record),true);
 const bytes=Buffer.from(JSON.stringify(record)),signature=signBindingBytes(bytes,privateKey);
 assert.equal(verifyBindingBytes(bytes,signature,signingKey),'signature-valid');
 record.roles.push('enroll');
 assert.equal(verifyBindingBytes(Buffer.from(JSON.stringify(record)),signature,signingKey),'invalid-proof');
});
