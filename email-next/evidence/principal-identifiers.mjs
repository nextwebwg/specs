import {randomBytes} from 'node:crypto';
function valid(value,prefix) {
 return typeof value==='string' && value.startsWith(prefix) &&
  /^[0-9a-f]{64}$/.test(value.slice(prefix.length)) && value.slice(prefix.length)!=='0'.repeat(64);
}
export const isPrincipalId=value=>valid(value,'enp0:');
export const isDeviceId=value=>valid(value,'end0:');
function generate(prefix) {
 let bytes;do {bytes=randomBytes(32);} while(bytes.every(n=>n===0));
 return prefix+bytes.toString('hex');
}
export const newPrincipalId=()=>generate('enp0:');
export const newDeviceId=()=>generate('end0:');
