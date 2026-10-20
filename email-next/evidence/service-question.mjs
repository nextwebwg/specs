import {isIP} from 'node:net';
import {isObjectId, isEventReference} from './event-identifiers.mjs';
import {validateButtonOperation} from './button-operations.mjs';
const exact=(v,keys)=>v!==null && typeof v==='object' && !Array.isArray(v) &&
  Object.keys(v).length===keys.length && keys.every(k=>Object.hasOwn(v,k));
const u64=v=>typeof v==='string' && v===v.trim() && /^(0|[1-9][0-9]{0,19})$/.test(v) && BigInt(v)<2n**64n;

// Exact experiment spelling only. No networking, URL repair or IDNA claim.
// A-labels remain unsupported until a complete IDNA profile is selected.
export function isServiceOrigin(value) {
  if(typeof value!=='string')return false;
  const match=/^https:\/\/([a-z0-9.-]+)(?::([1-9][0-9]{0,4}))?$/.exec(value);
  if(!match)return false;
  const [,host,port]=match;
  if(host.length>253 || isIP(host) || (port && (port==='443' || Number(port)>65535)))return false;
  const labels=host.split('.');
  if(!labels.every(l=>l.length<=63 && /^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/.test(l) && !l.startsWith('xn--')))return false;
  try {
    const parsed=new URL(value);
    return !isIP(parsed.hostname) && parsed.hostname===host && parsed.origin===value;
  } catch {return false;}
}

export function isServiceEndpoint(value,origin,{prefix=false}={}) {
  if(!isServiceOrigin(origin) || typeof value!=='string' || /[^\x21-\x7e]/.test(value) || !value.startsWith(origin+'/'))return false;
  const path=value.slice(origin.length);
  if(!/^\/(?:[A-Za-z0-9._~/-]|%[0-9A-F]{2})*$/.test(path) || (prefix && !path.endsWith('/')))return false;
  if(path.split('/').some(p=>p==='.' || p==='..'))return false;
  for(const m of path.matchAll(/%([0-9A-F]{2})/g)) {
    const c=String.fromCharCode(parseInt(m[1],16));
    if(/[A-Za-z0-9._~\/\\-]/.test(c))return false;
  }
  return true;
}

export function validateServiceAction(value,isPrincipal) {
  return exact(value,['version','purpose','action','question','service','submit','statusPrefix','notBefore','retryUntil']) &&
    value.version==='0' && value.purpose==='service-answer-action' && isObjectId(value.action) &&
    isEventReference(value.question,isPrincipal) && isServiceOrigin(value.service) &&
    isServiceEndpoint(value.submit,value.service) && isServiceEndpoint(value.statusPrefix,value.service,{prefix:true}) &&
    u64(value.notBefore) && u64(value.retryUntil) && BigInt(value.retryUntil)>=BigInt(value.notBefore);
}

// Shape only; signature, service configuration and execution authority remain separate.
export function validateServiceQuestion(value,isPrincipal) {
  return exact(value,['kind','text','options','serviceAction']) && value.kind==='service-question' &&
    validateButtonOperation({kind:'question',text:value.text,options:value.options},isPrincipal) &&
    validateServiceAction(value.serviceAction,isPrincipal);
}

export function validateServiceQuestionBinding(envelope,isPrincipal) {
  if(!envelope || !validateServiceQuestion(envelope.operation,isPrincipal))return false;
  const ref=envelope.operation.serviceAction.question;
  return ref.principal===envelope.principal && ref.conversation===envelope.conversation && ref.event===envelope.event;
}
