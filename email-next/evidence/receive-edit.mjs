import {checkConversationContext} from './conversation-context.mjs';
import {evaluateEdit} from './edit-state.mjs';
import {projectReadable} from './readable-projection.mjs';
import {isPrincipalId} from './principal-identifiers.mjs';
import {isEventReference} from './event-identifiers.mjs';
const key=r=>JSON.stringify([r.principal,r.conversation,r.event]);

// Caller stores exact authenticated bytes and conflict evidence first. All inputs
// describe one verified epoch/storage snapshot; this function performs no crypto.
export function prepareReceivedEdit(reference, sender, context, members, resolve, budget, options={}) {
 if(!isEventReference(reference,isPrincipalId))return {state:'invalid-reference'};
 const selected=resolve(reference);
 if(!selected || selected.state==='pending')return {state:'pending'};
 if(selected.state==='conflict')return {state:'conflict'};
 if(selected.state!=='valid' || !selected.event || key(selected.event)!==key(reference))return {state:'invalid'};
 const event=selected.event;
 const checked=checkConversationContext(event,sender,context,members,options);
 if(checked!=='context-matched')return {state:checked};
 if(event.operation.kind!=='edit')return {state:'wrong-operation'};
 const snapshot=ref=>key(ref)===key(reference)?selected:resolve(ref);
 const graph=evaluateEdit(event.operation.root,[reference],snapshot,isPrincipalId,budget);
 if(graph.state==='incomplete')return graph;
 const candidate=graph.results.find(result=>key(result.ref)===key(reference));
 if(candidate.state!=='valid')return {state:candidate.state};
 const validated=new Map(graph.results.map(result=>[key(result.ref),result]));
 const projection=projectReadable(event,ref=>validated.get(key(ref)),isPrincipalId);
 if(projection.state!=='projected')return {state:projection.state};
 // Only this event's ancestor closure was examined, not all concurrent branches.
 return {state:'prepared',projection};
}
