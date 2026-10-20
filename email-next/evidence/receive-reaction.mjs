import {validateEnvelopeShape} from './event-envelope.mjs';
import {checkConversationContext} from './conversation-context.mjs';
import {evaluateReactions} from './reaction-state.mjs';
import {projectReadable} from './readable-projection.mjs';
import {isPrincipalId} from './principal-identifiers.mjs';
import {isEventReference} from './event-identifiers.mjs';
const key=r=>JSON.stringify([r.principal,r.conversation,r.event]);

// The caller independently authenticates this candidate and authorizes all
// resolved history under its original instance/context. This is not crypto.
export function prepareReceivedReaction(reference,sender,context,members,resolve,budget,options={}) {
 if(!isEventReference(reference,isPrincipalId))return {state:'invalid-reference'};
 const selected=resolve(reference);
 if(!selected || selected.state==='pending')return {state:'pending'};
 if(selected.state==='conflict')return {state:'conflict'};
 if(selected.state!=='valid' || !selected.event || key(selected.event)!==key(reference))return {state:'invalid'};
 const event=selected.event;
 if(event.version!=='1' || !['2','3','4'].includes(context?.version))return {state:'application-mismatch'};
 const checked=checkConversationContext(event,sender,context,members,options);
 if(checked!=='context-matched')return {state:checked};
 if(!['reaction','reaction-withdraw'].includes(event.operation.kind))return {state:'wrong-operation'};
 const snapshot=ref=>{
  const found=key(ref)===key(reference)?selected:resolve(ref);
  if(found?.state==='valid' && !validateEnvelopeShape(found.event,isPrincipalId))return {state:'invalid'};
  return found;
 };
 const graph=evaluateReactions(event.operation.target,[reference],snapshot,isPrincipalId,budget);
 if(graph.state==='incomplete')return graph;
 const candidate=graph.results.find(result=>key(result.ref)===key(reference));
 if(candidate.state!=='valid')return {state:candidate.state};
 const validated=new Map(graph.results.map(result=>[key(result.ref),result]));
 const projection=projectReadable(event,ref=>validated.get(key(ref)),isPrincipalId);
 return projection.state==='projected'?{state:'prepared',projection}:{state:projection.state};
}
