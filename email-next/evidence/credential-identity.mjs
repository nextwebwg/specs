import {isPrincipalId,isDeviceId} from './principal-identifiers.mjs';
const PREFIX=Buffer.from('email-next/device/v0\0','ascii');
// Encodes only BasicCredential.identity, NOT the surrounding MLS wire structure.
export function encodeCredentialIdentity(principal,device) {
 if(!isPrincipalId(principal)||!isDeviceId(device))throw new TypeError('invalid identifier');
 return Buffer.concat([PREFIX,Buffer.from(principal.slice(5),'hex'),Buffer.from(device.slice(5),'hex')]);
}
export function decodeCredentialIdentity(bytes) {
 if(!(bytes instanceof Uint8Array))throw new TypeError('bytes required');
 const input=Buffer.from(bytes);
 if(input.length!==PREFIX.length+64 || !input.subarray(0,PREFIX.length).equals(PREFIX))throw new TypeError('invalid credential identity');
 const principal='enp0:'+input.subarray(PREFIX.length,PREFIX.length+32).toString('hex');
 const device='end0:'+input.subarray(PREFIX.length+32).toString('hex');
 if(!isPrincipalId(principal)||!isDeviceId(device))throw new TypeError('zero identifier');
 return {principal,device};
}
