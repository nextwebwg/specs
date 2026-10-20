import {readFileSync} from 'node:fs';
import {isEventReference} from './event-identifiers.mjs';
const vocabulary=new Set(JSON.parse(readFileSync(new URL('./unicode-17/fully-qualified.json',import.meta.url),'utf8')));
const key=r=>JSON.stringify([r.principal,r.conversation,r.event]);
const exact=(v,keys)=>v!==null && typeof v==='object' && !Array.isArray(v) &&
 Object.keys(v).length===keys.length && keys.every(k=>Object.hasOwn(v,k));
export const reactionTargetKinds=Object.freeze(['message','attachment-message','question','service-question','answer','edit']);
export function validateReactionOperation(op,isPrincipal) {
 if(exact(op,['kind','target','emoji']) && op.kind==='reaction')
  return isEventReference(op.target,isPrincipal) && typeof op.emoji==='string' && vocabulary.has(op.emoji);
 return exact(op,['kind','target','reactions']) && op.kind==='reaction-withdraw' &&
  isEventReference(op.target,isPrincipal) && Array.isArray(op.reactions) && op.reactions.length>0 &&
  op.reactions.every(r=>isEventReference(r,isPrincipal)) && new Set(op.reactions.map(key)).size===op.reactions.length;
}
export function reactionHasLocalScope(event) {
 const op=event.operation;
 return op.target.conversation===event.conversation && key(op.target)!==key(event) &&
  (op.kind==='reaction' || op.reactions.every(r=>r.principal===event.principal &&
   r.conversation===event.conversation && key(r)!==key(event)));
}
