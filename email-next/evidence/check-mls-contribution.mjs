// Internal bridge: strict Python decoding precedes authenticated epoch checks.
import {readFileSync} from 'node:fs';
import {isPrincipalId} from './principal-identifiers.mjs';
import {checkConversationContext} from './conversation-context.mjs';
import {prepareReceivedEdit} from './receive-edit.mjs';
import {prepareReceivedAnswer} from './receive-answer.mjs';
import {prepareReceivedReaction} from './receive-reaction.mjs';
import {projectReadable} from './readable-projection.mjs';
const {event,credential,context,members,configuredEndpointOrdering=false,configuredQuorumOrdering=false,configuredApplication=null,records=[]}=JSON.parse(readFileSync(0,'utf8'));
const result=checkConversationContext(event,Buffer.from(credential,'hex'),context,members.map(m=>Buffer.from(m,'hex')),{configuredEndpointOrdering,configuredQuorumOrdering,configuredApplication});
if(result!=='context-matched')process.stdout.write(result);
else {
 const key=r=>JSON.stringify([r.principal,r.conversation,r.event]);
 const index=new Map(records.map(r=>[key(r.reference),r]));
 const own={principal:event.principal,conversation:event.conversation,event:event.event};
 index.set(key(own),{state:'valid',event});
 const resolve=r=>index.get(key(r))??{state:'pending'};
 const prepare=event.operation.kind==='edit'?prepareReceivedEdit:event.operation.kind==='answer'?prepareReceivedAnswer:['reaction','reaction-withdraw'].includes(event.operation.kind)?prepareReceivedReaction:null;
 const prepared=prepare?prepare(own,Buffer.from(credential,'hex'),context,members.map(m=>Buffer.from(m,'hex')),resolve,{maxRecords:4096,maxReferences:16384},{configuredEndpointOrdering,configuredQuorumOrdering,configuredApplication}):null;
 const projection=prepared?(prepared.state==='prepared'?prepared.projection:prepared):projectReadable(event,resolve,isPrincipalId);
 process.stdout.write(projection.state==='projected'?'projected-context-matched':projection.state);
}
