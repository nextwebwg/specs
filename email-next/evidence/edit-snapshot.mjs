// Authenticated records and explicit current effect eligibility, not a crypto API.
import {evaluateEdit} from './edit-state.mjs';
import {isPrincipalId} from './principal-identifiers.mjs';
const key=r=>JSON.stringify([r.principal,r.conversation,r.event]);
export function deriveEditSnapshot(root,records,budget={}){
 const index=new Map(records.map(r=>[key(r.reference),r]));
 const candidates=records.filter(r=>r.event?.operation?.kind==='edit'&&key(r.event.operation.root)===key(root)).map(r=>r.reference);
 const resolve=ref=>{const row=index.get(key(ref));if(!row)return {state:'pending'};if(row.state==='conflict')return {state:'conflict'};if(row.state!=='valid')return {state:row.state??'pending'};return row;};
 return evaluateEdit(root,candidates,resolve,isPrincipalId,budget);
}
