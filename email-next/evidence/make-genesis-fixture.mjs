import {generateKeyPairSync,createHash} from 'node:crypto';
import {signBindingBytes,signBindingPossession,signIdentityState} from './binding-signature.mjs';
const {privateKey,publicKey}=generateKeyPairSync('ed25519');
const binding={version:'0',purpose:'device-binding',record:'1'.repeat(32),principal:'enp0:'+'a'.repeat(64),device:'end0:'+'b'.repeat(64),signingKey:publicKey.export({format:'der',type:'spki'}).subarray(-32).toString('hex'),roles:['send','receive','enroll','revoke'],notBefore:'10',notAfter:'100',authority:{kind:'first-contact'}};
const bytes=Buffer.from(JSON.stringify(binding));
const state={version:'0',purpose:'identity-state',principal:binding.principal,record:'2'.repeat(32),revision:'0',previous:[],issuedAt:'10',bindings:[{device:binding.device,digest:createHash('sha256').update(bytes).digest('hex')}],revoked:[],signer:binding.device};
const stateBytes=Buffer.from(JSON.stringify(state));
process.stdout.write(JSON.stringify({binding:bytes.toString('base64'),state:stateBytes.toString('base64'),possession:signBindingPossession(bytes,privateKey),authorization:signBindingBytes(bytes,privateKey),stateProof:signIdentityState(stateBytes,privateKey),time:{earliest:'10',latest:'100'}}));
