import {isPrincipalId} from './principal-identifiers.mjs';
const digest=v=>typeof v==='string'&&/^[0-9a-f]{64}$/.test(v);
const uint=v=>typeof v==='string'&&/^(0|[1-9][0-9]{0,19})$/.test(v)&&BigInt(v)<2n**64n;
export function validateQuorumOrdering(value){
 if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).length!==4||value.kind!=='endpoint-quorum-v0'||!uint(value.generation)||!uint(value.faultBound)||!Array.isArray(value.witnesses)||!value.witnesses.length)return false;
 if(BigInt(value.witnesses.length)<3n*BigInt(value.faultBound)+1n)return false;
 return value.witnesses.every((w,i)=>w&&typeof w==='object'&&!Array.isArray(w)&&Object.keys(w).length===5&&['principal','device','signingKey','state','binding'].every(k=>Object.hasOwn(w,k))&&isPrincipalId(w.principal)&&typeof w.device==='string'&&/^end0:[0-9a-f]{64}$/.test(w.device)&&w.device!=='end0:'+'0'.repeat(64)&&['signingKey','state','binding'].every(k=>digest(w[k]))&&(i===0||value.witnesses[i-1].principal<w.principal));
}
