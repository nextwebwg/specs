import {isEventReference} from './event-identifiers.mjs';
import {validateReactionOperation,reactionHasLocalScope,reactionTargetKinds} from './reaction-operations.mjs';
const key=r=>JSON.stringify([r.principal,r.conversation,r.event]);
const ordered=map=>[...map.entries()].sort(([a],[b])=>a<b?-1:a>b?1:0);
// Resolver supplies a single authenticated, authorized and full-schema-validated
// snapshot, including exact-byte conflicts. This evaluator never authenticates,
// fetches, writes or declares that the supplied candidates are globally complete.
export function evaluateReactions(target,candidates,resolve,isPrincipal,{maxRecords=Infinity,maxReferences=Infinity}={}) {
 if(!isEventReference(target,isPrincipal) || !Array.isArray(candidates) ||
    !candidates.every(r=>isEventReference(r,isPrincipal)))throw new TypeError('Expected exact references');
 for(const limit of [maxRecords,maxReferences])
  if(limit!==Infinity && (!Number.isSafeInteger(limit)||limit<0))throw new TypeError('Invalid work budget');
 let references=candidates.length+1;
 if(references>maxReferences)return {state:'incomplete',reason:'reference-budget'};
 const refs=new Map([[key(target),target],...candidates.map(r=>[key(r),r])]);
 if(refs.size>maxRecords)return {state:'incomplete',reason:'record-budget'};
 const records=new Map(),queue=[...refs.values()];
 for(let i=0;i<queue.length;i++) {
  const ref=queue[i],found=resolve(ref);records.set(key(ref),found);
  const event=found?.event;
  if(found?.state!=='valid'||!event||key(event)!==key(ref)||
     !validateReactionOperation(event.operation,isPrincipal)||!reactionHasLocalScope(event)||
     key(event.operation.target)!==key(target))continue;
  const deps=event.operation.kind==='reaction-withdraw'?event.operation.reactions:[];
  references+=1+deps.length;
  if(references>maxReferences)return {state:'incomplete',reason:'reference-budget'};
  for(const dependency of deps)if(!refs.has(key(dependency))) {
   if(refs.size>=maxRecords)return {state:'incomplete',reason:'record-budget'};
   refs.set(key(dependency),dependency);queue.push(dependency);
  }
 }
 const states=new Map();
 for(const [id,ref] of refs) {
  const found=records.get(id),event=found?.event;
  if(!found||found.state==='pending')states.set(id,{state:'pending'});
  else if(found.state==='conflict')states.set(id,{state:'conflict'});
  else if(found.state!=='valid'||!event||key(event)!==id)states.set(id,{state:'invalid'});
  else if(id===key(target))states.set(id,reactionTargetKinds.includes(event.operation?.kind)?{state:'valid',event}:{state:'invalid'});
  else if(!validateReactionOperation(event.operation,isPrincipal)||!reactionHasLocalScope(event)||
          key(event.operation.target)!==key(target))states.set(id,{state:'invalid'});
 }
 const combine=results=>results.some(r=>r.state==='invalid')?'invalid':
  results.some(r=>r.state==='conflict')?'conflict':results.some(r=>r.state!=='valid')?'pending':'valid';
 for(const [id] of refs)if(!states.has(id)) {
  const event=records.get(id).event;
  if(event.operation.kind==='reaction') {
   const state=combine([states.get(key(target))]);states.set(id,{state,...(state==='valid'?{event}:{})});
  }
 }
 for(const [id] of refs)if(!states.has(id)) {
  const event=records.get(id).event;
  const dependencies=event.operation.reactions.map(ref=>{
   const found=records.get(key(ref));
   // A withdrawal may only reference reactions, never another withdrawal.
   if(found?.state==='valid' && found.event?.operation?.kind!=='reaction')return {state:'invalid'};
   return states.get(key(ref))??{state:'invalid'};
  });
  const state=combine([states.get(key(target)),...dependencies]);
  states.set(id,{state,...(state==='valid'?{event}:{})});
 }
 const removed=new Set();
 for(const result of states.values())if(result.state==='valid'&&result.event.operation.kind==='reaction-withdraw')
  for(const ref of result.event.operation.reactions)removed.add(key(ref));
 const results=ordered(refs).map(([id,ref])=>({ref,...states.get(id)}));
 return {state:'evaluated',results,active:results.filter(r=>r.state==='valid'&&
  r.event.operation.kind==='reaction'&&!removed.has(key(r.ref))).map(r=>r.ref)};
}
