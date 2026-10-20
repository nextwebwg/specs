"""Recompute a button view from one journal snapshot; no durable view or effects."""
import json
from pathlib import Path
import subprocess
from event_encoding import decode_event

HERE = Path(__file__).resolve().parent

def derive_button_view(journal, question):
    snapshot = journal.snapshot_with_token(question['conversation'])
    records = []
    for row in snapshot['records']:
        record = dict(reference=row['reference'], state=row['state'])
        if row['state']=='recorded':
            record['event']=decode_event(row['octets'][0])['value']
        records.append(record)
    script = '''import {evaluateButtonAnswers} from './button-state.mjs';
import {validateEnvelopeShape} from './event-envelope.mjs';
import {isPrincipalId} from './principal-identifiers.mjs';
let input='';for await(const chunk of process.stdin)input+=chunk;
const {question,records}=JSON.parse(input);
const key=r=>JSON.stringify([r.principal,r.conversation,r.event]);
const index=new Map(records.map(r=>[key(r.reference),r]));
const resolve=ref=>{
 const row=index.get(key(ref));
 if(!row)return {state:'pending'};
 if(row.state==='conflict')return {state:'conflict'};
 if(!validateEnvelopeShape(row.event,isPrincipalId))return {state:'invalid'};
 const target=index.get(key(question));
 if(row.event.operation.kind==='answer' && target?.state==='recorded' &&
    validateEnvelopeShape(target.event,isPrincipalId) &&
    !row.event.audience.every(p=>target.event.audience.includes(p)))return {state:'invalid'};
 return {state:'valid',event:row.event};
};
const candidates=records.filter(r=>key(r.reference)!==key(question)).map(r=>r.reference);
process.stdout.write(JSON.stringify(evaluateButtonAnswers(question,candidates,resolve,isPrincipalId)));
'''
    result=subprocess.run(['node','--input-type=module','-e',script],cwd=HERE,
        input=json.dumps(dict(question=question,records=records)),text=True,
        capture_output=True,check=True)
    view=json.loads(result.stdout)
    view['sourceToken']=snapshot['token']
    return view
