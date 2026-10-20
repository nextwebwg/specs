import {isObjectId} from './event-identifiers.mjs';
import {isPrincipalId,isDeviceId} from './principal-identifiers.mjs';
const hex=value=>typeof value==='string' && /^[0-9a-f]{64}$/.test(value);
const shape=(v,keys)=>v && typeof v==='object' && !Array.isArray(v) && Object.keys(v).sort().join(',')===keys.split(' ').sort().join(',');
const u64=v=>typeof v==='string' && /^(0|[1-9][0-9]{0,19})$/.test(v) && BigInt(v)<(1n<<64n);
const ROLES=new Set(['send','receive','enroll','revoke','recover']);
export function validateDeviceBinding(value) {
 if(!shape(value,'version purpose record principal device signingKey roles notBefore notAfter authority') ||
    value.version!=='0' || value.purpose!=='device-binding' || !isObjectId(value.record) ||
    !isPrincipalId(value.principal) || !isDeviceId(value.device) || !hex(value.signingKey) ||
    !Array.isArray(value.roles) || value.roles.length===0 || new Set(value.roles).size!==value.roles.length ||
    !value.roles.every(r=>ROLES.has(r)) || !u64(value.notBefore) || !u64(value.notAfter) ||
    BigInt(value.notAfter)<BigInt(value.notBefore))return false;
 const authority=value.authority;
 return (shape(authority,'kind') && authority.kind==='first-contact') ||
  (shape(authority,'kind digest') && authority.kind==='state' && hex(authority.digest));
}
