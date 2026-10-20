// Internal test bridge: Python has strictly decoded each original byte string.
// This stdin format is not a wire protocol and must not accept untrusted decoded values.
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {validateIdentityState} from './identity-state.mjs';
import {validateDeviceBinding} from './device-binding.mjs';
import {verifyBindingBytes,verifyBindingPossession,verifyIdentityState} from './binding-signature.mjs';
const input=JSON.parse(readFileSync(0,'utf8'));
function check() {
 const state=input.state.value,binding=input.binding.value;
 const stateBytes=Buffer.from(input.state.base64,'base64'),bindingBytes=Buffer.from(input.binding.base64,'base64');
 const invalid=reason=>({status:'invalid',reason});
 if(!validateIdentityState(state) || state.revision!=='0' || !validateDeviceBinding(binding))return invalid('schema');
 if(binding.authority.kind!=='first-contact' || state.principal!==binding.principal || state.signer!==binding.device ||
    state.bindings[0].device!==binding.device || !binding.roles.includes('enroll') || !binding.roles.includes('revoke'))return invalid('genesis-binding');
 const digest=createHash('sha256').update(bindingBytes).digest('hex');
 if(state.bindings[0].digest!==digest)return invalid('binding-digest');
 const key=binding.signingKey;
 if(verifyBindingPossession(bindingBytes,input.possession,key)!=='signature-valid')return invalid('possession');
 if(verifyBindingBytes(bindingBytes,input.authorization,key)!=='signature-valid')return invalid('binding-proof');
 if(verifyIdentityState(stateBytes,input.stateProof,key)!=='signature-valid')return invalid('state-proof');
 const decimal=v=>typeof v==='string' && /^(0|[1-9][0-9]{0,19})$/.test(v) && BigInt(v)<(1n<<64n);
 if(!decimal(input.time?.earliest) || !decimal(input.time?.latest) || BigInt(input.time.latest)<BigInt(input.time.earliest))return {status:'pending',reason:'time'};
 if(BigInt(input.time.earliest)>BigInt(binding.notAfter))return {status:'not-current',reason:'expired'};
 if(BigInt(input.time.latest)<BigInt(binding.notBefore))return {status:'not-current',reason:'not-yet-valid'};
 if(BigInt(input.time.earliest)<BigInt(binding.notBefore) || BigInt(input.time.latest)>BigInt(binding.notAfter))return {status:'pending',reason:'binding-validity'};
 return {status:'claim-valid-unverified',principal:state.principal,device:binding.device,stateDigest:createHash('sha256').update(stateBytes).digest('hex')};
}
process.stdout.write(JSON.stringify(check()));
