// Internal bridge: identity_bundle.py constructs values from strict original bytes.
// acceptedDigest is trusted local input, never taken from an advertisement.
import {readFileSync} from 'node:fs';
import {validateIdentityState} from './identity-state.mjs';
import {validateDeviceBinding} from './device-binding.mjs';
import {checkIdentityTransition} from './identity-transition.mjs';
import {verifyBindingBytes,verifyBindingPossession,verifyIdentityState} from './binding-signature.mjs';
const input=JSON.parse(readFileSync(0,'utf8'));
function check(){
 const fail=reason=>({status:'invalid',reason}),pending=reason=>({status:'pending',reason});
 const states=new Map(input.states.map(s=>[s.digest,s])),bindings=new Map(input.bindings.map(b=>[b.digest,b]));
 const prev=states.get(input.acceptedDigest),next=states.get(input.candidateDigest);
 if(!prev || !next)return pending('state');
 if(!validateIdentityState(prev.value) || !validateIdentityState(next.value))return fail('state-schema');
 if(next.value.previous[0]!==input.acceptedDigest || next.value.principal!==prev.value.principal)return fail('predecessor');
 const signerRef=prev.value.bindings.find(b=>b.device===next.value.signer);
 if(!signerRef)return fail('signer');
 for(const ref of [...prev.value.bindings,...next.value.bindings]){
  const b=bindings.get(ref.digest);
  if(!b)return pending('binding');
  if(!validateDeviceBinding(b.value) || b.value.device!==ref.device || b.value.principal!==prev.value.principal)return fail('binding-schema');
 }
 const key=bindings.get(signerRef.digest).value.signingKey;
 if(verifyIdentityState(Buffer.from(next.base64,'base64'),next.signature,key)!=='signature-valid')return fail('state-proof');
 const old=new Map(prev.value.bindings.map(b=>[b.device,b.digest]));
 for(const ref of next.value.bindings){
  if(old.get(ref.device)===ref.digest)continue;
  const b=bindings.get(ref.digest),bytes=Buffer.from(b.base64,'base64');
  if(verifyBindingPossession(bytes,b.possession,b.value.signingKey)!=='signature-valid')return fail('possession');
  if(verifyBindingBytes(bytes,b.authorization,key)!=='signature-valid')return fail('binding-proof');
 }
 const decimal=v=>typeof v==='string' && /^(0|[1-9][0-9]{0,19})$/.test(v) && BigInt(v)<(1n<<64n);
 if(!decimal(input.time?.earliest) || !decimal(input.time?.latest) || BigInt(input.time.earliest)>BigInt(input.time.latest))return pending('time');
 const resolved=new Map([...bindings].map(([digest,b])=>[digest,b.value]));
 for(const instant of [input.time.earliest,input.time.latest]){
  const result=checkIdentityTransition(prev.value,next.value,input.acceptedDigest,resolved,BigInt(instant));
  if(result.status!=='policy-valid')return result;
 }
 const fullIntervalAdmin=next.value.bindings.some(ref=>{const b=bindings.get(ref.digest).value;return b.roles.includes('enroll') && b.roles.includes('revoke') && BigInt(b.notBefore)<=BigInt(input.time.earliest) && BigInt(b.notAfter)>=BigInt(input.time.latest);});
 if(!fullIntervalAdmin)return pending('administrator-time');
 return {status:'transition-valid-uncommitted',principal:next.value.principal,previous:input.acceptedDigest,candidate:input.candidateDigest};
}
process.stdout.write(JSON.stringify(check()));
