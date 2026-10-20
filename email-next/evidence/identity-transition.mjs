import {validateIdentityState} from './identity-state.mjs';
import {validateDeviceBinding} from './device-binding.mjs';
// Inputs are already authenticated, digest-resolved records. This policy model
// does not establish that prerequisite or commit a durable state change.
export function checkIdentityTransition(previous,next,previousDigest,bindings,now) {
 const fail=reason=>({status:'invalid',reason});
 if(!validateIdentityState(previous) || !validateIdentityState(next) ||
    typeof previousDigest!=='string' || !/^[0-9a-f]{64}$/.test(previousDigest) ||
    !(bindings instanceof Map) || typeof now!=='bigint' || now<0n || now>=(1n<<64n))return fail('input');
 if(next.principal!==previous.principal || next.previous[0]!==previousDigest ||
    BigInt(next.revision)!==BigInt(previous.revision)+1n || BigInt(next.issuedAt)<BigInt(previous.issuedAt))return fail('predecessor');
 const resolve=ref=>{
  const b=bindings.get(ref.digest);
  return validateDeviceBinding(b) && b.device===ref.device && b.principal===next.principal ? b : undefined;
 };
 const prior=new Map(previous.bindings.map(r=>[r.device,r]));
 const current=new Map(next.bindings.map(r=>[r.device,r]));
 const signerRef=prior.get(next.signer),signer=signerRef && resolve(signerRef);
 const valid=b=>b && BigInt(b.notBefore)<=now && now<=BigInt(b.notAfter);
 if(!valid(signer))return fail('signer');
 const revoked=new Set(next.revoked);
 if(previous.revoked.some(d=>!revoked.has(d)))return fail('revocation-rollback');
 if(previous.revoked.some(d=>current.has(d)))return fail('revoked-device');
 let changed=false;
 for(const [device] of prior)if(!current.has(device)) {
  changed=true;
  if(!signer.roles.includes('revoke') || !revoked.has(device))return fail('removal');
 }
 // No tombstone for an unrelated unseen device: revocation targets the old roster.
 if(next.revoked.some(d=>!previous.revoked.includes(d) && !prior.has(d)))return fail('unknown-revocation');
 let administrator=false;
 for(const ref of next.bindings) {
  const binding=resolve(ref);
  if(!binding)return fail('binding');
  if(valid(binding) && binding.roles.includes('enroll') && binding.roles.includes('revoke'))administrator=true;
  if(prior.get(ref.device)?.digest===ref.digest)continue;
  changed=true;
  if(!valid(binding) || !signer.roles.includes('enroll') || binding.roles.some(r=>!signer.roles.includes(r)))return fail('delegation');
  if(binding.authority.kind!=='state' || binding.authority.digest!==previousDigest)return fail('binding-authority');
 }
 if(!administrator)return fail('last-administrator');
 if(!changed && !signer.roles.includes('enroll'))return fail('checkpoint-authority');
 return {status:'policy-valid'};
}
