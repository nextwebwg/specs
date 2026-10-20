// Internal accepted-journal bridge. Callers supply only independently admitted records.
import {readFileSync} from 'node:fs';
import {evaluateEdit} from './edit-state.mjs';
import {projectReadable} from './readable-projection.mjs';
import {validateEnvelopeShape} from './event-envelope.mjs';
import {isPrincipalId} from './principal-identifiers.mjs';
const {event,records}=JSON.parse(readFileSync(0,'utf8'));
const key=r=>JSON.stringify([r.principal,r.conversation,r.event]);
const index=new Map(records.map(r=>[key(r.reference),r]));
const used=new Set();
const resolve=ref=>{
 const k=key(ref);used.add(k);const row=index.get(k);
 if(!row)return {state:'pending'};
 if(row.state!=='recorded')return {state:'conflict'};
 return validateEnvelopeShape(row.event,isPrincipalId)?{state:'valid',event:row.event}:{state:'invalid'};
};
let projection={state:'invalid'};
if(validateEnvelopeShape(event,isPrincipalId)){
 if(event.operation.kind==='edit'){
  const own={principal:event.principal,conversation:event.conversation,event:event.event};
  const graph=evaluateEdit(event.operation.root,[own],ref=>key(ref)===key(own)?{state:'valid',event}:resolve(ref),isPrincipalId,{maxRecords:4096,maxReferences:16384});
  const checked=graph.results?.find(r=>key(r.ref)===key(own));
  const validated=new Map((graph.results??[]).map(r=>[key(r.ref),r]));
  projection=checked?.state==='valid'?projectReadable(event,ref=>validated.get(key(ref)),isPrincipalId):{state:graph.state==='incomplete'?'incomplete':checked?.state??'invalid'};
 }else projection=projectReadable(event,resolve,isPrincipalId);
}
process.stdout.write(JSON.stringify({projection,dependencies:[...used].sort().map(k=>index.get(k)).filter(Boolean).map(r=>({reference:r.reference,digest:r.digest}))}));
