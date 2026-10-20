import {evaluateReactions} from './reaction-state.mjs';
import {validateEnvelopeShape} from './event-envelope.mjs';
import {isPrincipalId} from './principal-identifiers.mjs';
const key=r=>JSON.stringify([r.principal,r.conversation,r.event]);

// Pure presentation derivation. Records come from one already authorized journal
// snapshot, never from MIME claims or a merely decrypted candidate index.
export function deriveReactionSnapshot(target,records,budget={maxRecords:4096,maxReferences:16384}) {
 const index=new Map();
 for(const row of records){
  const id=key(row.reference);
  if(index.has(id))throw new TypeError('Snapshot requires one conflict-aware row per reference');
  index.set(id,row);
 }
 const resolve=reference=>{
  const row=index.get(key(reference));
  if(!row || row.state==='pending')return {state:'pending'};
  if(row.state==='conflict')return {state:'conflict'};
  if(row.state!=='recorded' || !row.event || key(row.event)!==key(reference) || !validateEnvelopeShape(row.event,isPrincipalId))return {state:'invalid'};
  return {state:'valid',event:row.event};
 };
 const candidates=records.filter(row=>row.state==='conflict'||
  (row.event && ['reaction','reaction-withdraw'].includes(row.event.operation?.kind) && key(row.event.operation.target)===key(target))).map(row=>row.reference);
 return evaluateReactions(target,candidates,resolve,isPrincipalId,budget);
}
