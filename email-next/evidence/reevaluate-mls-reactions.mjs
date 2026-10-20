// Trusted authorized-history snapshot adapter; no cryptography or effects.
import {readFileSync} from 'node:fs';
import {prepareReceivedReaction} from './receive-reaction.mjs';
const {records,candidates}=JSON.parse(readFileSync(0,'utf8'));
const key=r=>JSON.stringify([r.principal,r.conversation,r.event]);
const index=new Map(records.map(r=>[key(r.reference),r]));
process.stdout.write(JSON.stringify(candidates.map(c=>{
 const own=key(c.reference);
 const resolve=r=>key(r)===own?{state:'valid',event:c.event}:index.get(key(r))??{state:'pending'};
 return {digest:c.digest,result:prepareReceivedReaction(c.reference,Buffer.from(c.credential,'hex'),c.context,
  c.members.map(m=>Buffer.from(m,'hex')),resolve,{maxRecords:4096,maxReferences:16384},c.options??{})};
})));
