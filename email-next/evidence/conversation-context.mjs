import {validateQuorumOrdering} from './quorum-ordering-context.mjs';
import {validateDelivery,deliveryMatchesRoster} from './private-copy-context.mjs';
import {isPrincipalId} from './principal-identifiers.mjs';
import {isObjectId} from './event-identifiers.mjs';
import {decodeCredentialIdentity} from './credential-identity.mjs';
import {validateEnvelopeShape} from './event-envelope.mjs';
const selectedOperations=new Set(['answer','hosted-holder-observation','message','question','reaction','reaction-withdraw']);
function optionsAgreementInvalid(value,agreement){
 const a=value.application;
 if(!a || typeof a!=='object' || Array.isArray(a) || Object.keys(a).length!==2 ||
    a.envelopeVersion!=='1' || !Array.isArray(a.operations) || !a.operations.length ||
    !a.operations.every((op,i)=>selectedOperations.has(op) && (i===0 || a.operations[i-1]<op)))return true;
 return !agreement || agreement.envelopeVersion!=='1' || !Array.isArray(agreement.operations) ||
   agreement.operations.length!==a.operations.length || agreement.operations.some((op,i)=>op!==a.operations[i]);
}
function tupleAgreementInvalid(value,agreement){
 const a=value.application;
 const keys=['envelopeVersion','payload','operations'];
 if(!a || typeof a!=='object' || Array.isArray(a) || Object.keys(a).length!==3 || !keys.every(k=>Object.hasOwn(a,k)) || a.envelopeVersion!==(value.version==='6'?'3':value.version==='5'?'2':'1') || !(['4','5','6'].includes(value.version)?['mime-rich-v0']:['raw-event-v0','mime-contribution-v0']).includes(a.payload))return true;
 const ops=new Set(['answer','message','question','reaction','reaction-withdraw',...(['mime-contribution-v0','mime-rich-v0'].includes(a.payload)?['attachment-message']:[]),...(a.payload==='mime-rich-v0'?['rich-message']:[]),...(value.version==='6'?['service-question','edit']:[])]);
 if(!Array.isArray(a.operations) || !a.operations.length || !a.operations.every((op,i)=>ops.has(op)&&(i===0 || a.operations[i-1]<op)))return true;
 return !agreement || typeof agreement!=='object' || Array.isArray(agreement) || Object.keys(agreement).length!==3 || !keys.every(k=>Object.hasOwn(agreement,k)) || agreement.envelopeVersion!==a.envelopeVersion || agreement.payload!==a.payload || !Array.isArray(agreement.operations) || agreement.operations.length!==a.operations.length || agreement.operations.some((op,i)=>op!==a.operations[i]);
}
export function validateConversationContext(value, {configuredEndpointOrdering=false,configuredQuorumOrdering=false,configuredApplication=null}={}){
 if(value?.version==='7'){
  if(!configuredQuorumOrdering||!validateQuorumOrdering(value.ordering)||value.application?.operations?.some(op=>['service-question','edit'].includes(op)))return false;
  const comparable={...value,version:'6',ordering:{kind:'fixed-roster-v0'}};
  return validateConversationContext(comparable,{configuredApplication});
 }
 if(value?.version==='2' || value?.version==='3' || value?.version==='4' || value?.version==='5' || value?.version==='6'){
  const keys=['version','purpose','conversation','profile','administrators','application','ordering'];
  if(['5','6'].includes(value.version)){keys.push('delivery');if(!validateDelivery(value.delivery))return false;}
  if(['3','4','5','6'].includes(value.version)?tupleAgreementInvalid(value,configuredApplication):optionsAgreementInvalid(value,configuredApplication))return false;
  if(Object.keys(value).length!==keys.length || !keys.every(k=>Object.hasOwn(value,k)))return false;
  const base=Object.fromEntries(Object.entries({...value,version:'0'}).filter(([k])=>!['application','ordering','delivery'].includes(k)));
  if(value.ordering && typeof value.ordering==='object' && !Array.isArray(value.ordering) && Object.keys(value.ordering).length===1 && value.ordering.kind==='fixed-roster-v0')return validateConversationContext(base);
  return validateConversationContext({...base,version:'1',ordering:value.ordering},{configuredEndpointOrdering});
 }
 if(value?.version==='1'){
  if(configuredEndpointOrdering!==true || Object.keys(value).length!==6 || !Object.hasOwn(value,'ordering'))return false;
  const o=value.ordering;
  return o && typeof o==='object' && !Array.isArray(o) && Object.keys(o).length===3 && o.kind==='designated-member-v0' && isPrincipalId(o.principal) && /^end0:[0-9a-f]{64}$/.test(o.device) && o.device!=='end0:'+'0'.repeat(64) && Array.isArray(value.administrators) && value.administrators.includes(o.principal) && validateConversationContext(Object.fromEntries(Object.entries({...value,version:'0'}).filter(([k])=>k!=='ordering')));
 }
 const keys=['version','purpose','conversation','profile','administrators'];
 return value && typeof value==='object' && !Array.isArray(value) && Object.keys(value).length===keys.length && keys.every(k=>Object.hasOwn(value,k)) &&
  value.version==='0' && value.purpose==='conversation-context' && isObjectId(value.conversation) && value.profile==='mls-1-0001' &&
  Array.isArray(value.administrators) && value.administrators.length>0 && value.administrators.every((p,i)=>isPrincipalId(p) && (i===0 || value.administrators[i-1]<p));
}
// Context and members must come from the authenticated epoch, never outer mail headers.
export function checkConversationContext(event,sender,context,members,options={}){
 if(!validateEnvelopeShape(event,isPrincipalId) || !validateConversationContext(context,options))return 'invalid-shape';
 let author,roster;
 try {author=decodeCredentialIdentity(sender);roster=members.map(decodeCredentialIdentity);}catch{return 'invalid-credential';}
 if(['2','3','4','5','6','7'].includes(context.version) ? (event.version!==context.application.envelopeVersion || !context.application.operations.includes(event.operation.kind)) : event.version!=='0')return 'application-mismatch';
 if(context.version==='7'&&!context.ordering.witnesses.every(w=>roster.some(m=>m.principal===w.principal&&m.device===w.device)))return 'ordering-device-not-member';
 if(context.ordering?.kind==='designated-member-v0' && !roster.some(m=>m.principal===context.ordering.principal && m.device===context.ordering.device))return 'ordering-device-not-member';
 if(!roster.length || new Set(roster.map(m=>m.principal+'|'+m.device)).size!==roster.length)return 'invalid-roster';
 if(!roster.some(m=>m.principal===author.principal && m.device===author.device))return 'sender-not-member';
 if(author.principal!==event.principal)return 'sender-mismatch';
 if(context.conversation!==event.conversation)return 'conversation-mismatch';
 const audience=new Set(roster.map(m=>m.principal));
 if(['5','6','7'].includes(context.version)&&!deliveryMatchesRoster(context.delivery,[...audience]))return 'private-copy-roster-mismatch';
 if(context.administrators.some(p=>!audience.has(p)))return 'administrator-not-member';
 if(audience.size!==event.audience.length || event.audience.some(p=>!audience.has(p)))return 'audience-mismatch';
 return 'context-matched';
}
