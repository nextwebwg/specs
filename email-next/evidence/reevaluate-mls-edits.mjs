import {readFileSync} from 'node:fs';
import {prepareReceivedEdit} from './receive-edit.mjs';
const {records,candidates}=JSON.parse(readFileSync(0,'utf8'));
const key=r=>JSON.stringify([r.principal,r.conversation,r.event]);
const index=new Map(records.map(r=>[key(r.reference),r]));
process.stdout.write(JSON.stringify(candidates.map(c=>({digest:c.digest,result:prepareReceivedEdit(c.reference,Buffer.from(c.credential,'hex'),c.context,c.members.map(m=>Buffer.from(m,'hex')),r=>index.get(key(r))??{state:'pending'},{maxRecords:4096,maxReferences:16384},c.options)}))));
