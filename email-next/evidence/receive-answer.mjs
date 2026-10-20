import {validateEnvelopeShape} from './event-envelope.mjs';
import {checkConversationContext} from './conversation-context.mjs';
import {evaluateButtonAnswers} from './button-state.mjs';
import {projectReadable} from './readable-projection.mjs';
import {isPrincipalId} from './principal-identifiers.mjs';
import {isEventReference} from './event-identifiers.mjs';
const key=r=>JSON.stringify([r.principal,r.conversation,r.event]);

// Caller stores exact authenticated bytes and conflict evidence first. All inputs
// use one consistent storage snapshot. Historical records must already be authorized
// under their own authenticated contexts, not retroactively under the current epoch.
// This function performs no crypto.
export function prepareReceivedAnswer(reference, sender, context, members, resolve, budget, options={}) {
 if(!isEventReference(reference,isPrincipalId))return {state:'invalid-reference'};
 const selected=resolve(reference);
 if(!selected || selected.state==='pending')return {state:'pending'};
 if(selected.state==='conflict')return {state:'conflict'};
 if(selected.state!=='valid' || !selected.event || key(selected.event)!==key(reference))return {state:'invalid'};
 const event=selected.event;
 const checked=checkConversationContext(event,sender,context,members,options);
 if(checked!=='context-matched')return {state:checked};
 if(event.operation.kind!=='answer')return {state:'wrong-operation'};
 const snapshot=ref=>{
  const found=key(ref)===key(reference)?selected:resolve(ref);
  // Even an authenticated record must satisfy the complete envelope contract.
  // Graph validation alone checks operations, not audience/version/purpose fields.
  if(found?.state==='valid' && !validateEnvelopeShape(found.event,isPrincipalId))
   return {state:'invalid'};
  return found;
 };
 const graph=evaluateButtonAnswers(event.operation.question,[reference],snapshot,isPrincipalId,budget);
 if(graph.state==='incomplete')return graph;
 const candidate=graph.results.find(result=>key(result.ref)===key(reference));
 if(candidate.state!=='valid')return {state:candidate.state};
 const validated=new Map(graph.results.map(result=>[key(result.ref),result]));
 const projection=projectReadable(event,ref=>validated.get(key(ref)),isPrincipalId);
 if(projection.state!=='projected')return {state:projection.state};
 // Only this event's ancestor closure was examined, not all concurrent branches.
 return {state:'prepared',projection};
}
