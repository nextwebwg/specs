import {isObjectId} from './event-identifiers.mjs';
import {isPrincipalId,isDeviceId} from './principal-identifiers.mjs';
const shape=(v,keys)=>v && typeof v==='object' && !Array.isArray(v) && Object.keys(v).sort().join(',')===keys.split(' ').sort().join(',');
const digest=v=>typeof v==='string' && /^[0-9a-f]{64}$/.test(v);
const counter=v=>typeof v==='string' && /^(0|[1-9][0-9]{0,19})$/.test(v) && BigInt(v)<(1n<<64n);
const ordered=values=>values.every((v,i)=>i===0 || values[i-1]<v);
// Shape validation never resolves a predecessor or grants device authority.
export function validateIdentityState(v) {
 if(!shape(v,'version purpose principal record revision previous issuedAt bindings revoked signer') ||
    v.version!=='0' || v.purpose!=='identity-state' || !isPrincipalId(v.principal) || !isObjectId(v.record) ||
    !counter(v.revision) || !counter(v.issuedAt) || !isDeviceId(v.signer) ||
    !Array.isArray(v.previous) || !Array.isArray(v.bindings) || !v.bindings.length ||
    !Array.isArray(v.revoked))return false;
 if(!v.bindings.every(b=>shape(b,'device digest') && isDeviceId(b.device) && digest(b.digest)) ||
    !ordered(v.bindings.map(b=>b.device)) || !v.revoked.every(isDeviceId) || !ordered(v.revoked))return false;
 const removed=new Set(v.revoked);
 if(v.bindings.some(b=>removed.has(b.device)))return false;
 if(v.revision==='0')return v.previous.length===0 && v.revoked.length===0 && v.bindings.length===1 && v.bindings[0].device===v.signer;
 return v.previous.length===1 && digest(v.previous[0]);
}
