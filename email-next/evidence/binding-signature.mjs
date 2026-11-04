import {createPublicKey,sign,verify} from 'node:crypto';
const BINDING=Buffer.from('email-next/device-binding/v0\0','ascii');
const POSSESSION=Buffer.from('email-next/device-possession/v0\0','ascii');
const STATE=Buffer.from('email-next/identity-state/v0\0','ascii');
const SPKI=Buffer.from('302a300506032b6570032100','hex');
const MAX_BYTES=1048576;
function signingInput(payload,domain) {
 if(!(payload instanceof Uint8Array) || payload.length>MAX_BYTES)throw new TypeError('invalid payload');
 const size=Buffer.alloc(4);size.writeUInt32BE(payload.length);
 return Buffer.concat([domain,size,Buffer.from(payload)]);
}
function signPayload(payload,privateKey,domain) {
 if(privateKey?.asymmetricKeyType!=='ed25519')throw new TypeError('Ed25519 key required');
 return sign(null,signingInput(payload,domain),privateKey).toString('hex');
}
function verifyPayload(payload,signature,publicKeyHex,domain) {
 if(typeof signature!=='string' || !/^[0-9a-f]{128}$/.test(signature) ||
    typeof publicKeyHex!=='string' || !/^[0-9a-f]{64}$/.test(publicKeyHex))return 'invalid-proof';
 try {
  const key=createPublicKey({key:Buffer.concat([SPKI,Buffer.from(publicKeyHex,'hex')]),format:'der',type:'spki'});
  return verify(null,signingInput(payload,domain),key,Buffer.from(signature,'hex'))?'signature-valid':'invalid-proof';
 } catch {return 'invalid-proof';}
}
// Fixed-purpose entry points prevent caller-supplied context confusion.
// Proof validity alone never establishes the signer's authority.
export const signBindingBytes=(payload,key)=>signPayload(payload,key,BINDING);
export const verifyBindingBytes=(payload,signature,key)=>verifyPayload(payload,signature,key,BINDING);
export const signBindingPossession=(payload,key)=>signPayload(payload,key,POSSESSION);
export const verifyBindingPossession=(payload,signature,key)=>verifyPayload(payload,signature,key,POSSESSION);
export const signIdentityState=(payload,key)=>signPayload(payload,key,STATE);
export const verifyIdentityState=(payload,signature,key)=>verifyPayload(payload,signature,key,STATE);
const DISCOVERY=Buffer.from('email-next/passive-discovery/v0\0','ascii');
export const signPassiveDiscovery=(payload,key)=>signPayload(payload,key,DISCOVERY);
export const verifyPassiveDiscovery=(payload,signature,key)=>verifyPayload(payload,signature,key,DISCOVERY);

const APPLICATION_DISCOVERY=Buffer.from('email-next/passive-discovery/v1\0','ascii');
export const signApplicationDiscovery=(payload,key)=>signPayload(payload,key,APPLICATION_DISCOVERY);
export const verifyApplicationDiscovery=(payload,signature,key)=>verifyPayload(payload,signature,key,APPLICATION_DISCOVERY);

const TUPLE_DISCOVERY=Buffer.from('email-next/passive-discovery/v2\0','ascii');
export const signTupleDiscovery=(payload,key)=>signPayload(payload,key,TUPLE_DISCOVERY);
export const verifyTupleDiscovery=(payload,signature,key)=>verifyPayload(payload,signature,key,TUPLE_DISCOVERY);

const RICH_DISCOVERY=Buffer.from('email-next/passive-discovery/v3\0','ascii');
export const signRichDiscovery=(payload,key)=>signPayload(payload,key,RICH_DISCOVERY);
export const verifyRichDiscovery=(payload,signature,key)=>verifyPayload(payload,signature,key,RICH_DISCOVERY);

export const verifyPresentationDiscovery=(payload,signature,key)=>verifyPayload(payload,signature,key,Buffer.from('email-next/passive-discovery/v5\0'));
export const verifyPrivateCopyDiscovery=(payload,signature,key)=>verifyPayload(payload,signature,key,Buffer.from('email-next/passive-discovery/v4\0'));

export const verifyQuorumDiscovery=(payload,signature,key)=>verifyPayload(payload,signature,key,Buffer.from('email-next/passive-discovery/v6\0'));

export const verifyQuorumExchangeDiscovery=(payload,signature,key)=>verifyPayload(payload,signature,key,Buffer.from('email-next/passive-discovery/v7\0'));

export const verifySuiteDiscovery=(payload,signature,key)=>verifyPayload(payload,signature,key,Buffer.from('email-next/passive-discovery/v8\0'));

export const verifyReplyDiscovery=(payload,signature,key)=>verifyPayload(payload,signature,key,Buffer.from('mail/passive-discovery/v9\0'));
