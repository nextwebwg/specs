// Trusted snapshot adapter; cryptographic and current-authority checks occur in Python.
import {readFileSync} from 'node:fs';
import {prepareReceivedAnswer} from './receive-answer.mjs';
const {records,candidates}=JSON.parse(readFileSync(0,'utf8'));
const key=r=>JSON.stringify([r.principal,r.conversation,r.event]);
const index=new Map(records.map(r=>[key(r.reference),r]));
const resolve=r=>index.get(key(r))??{state:'pending'};
process.stdout.write(JSON.stringify(candidates.map(c=>({digest:c.digest,result:prepareReceivedAnswer(
 c.reference,Buffer.from(c.credential,'hex'),c.context,c.members.map(m=>Buffer.from(m,'hex')),
 resolve,{maxRecords:4096,maxReferences:16384},c.options??{})}))));
