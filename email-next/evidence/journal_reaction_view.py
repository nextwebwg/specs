"""One trusted journal snapshot to presentation; no authentication or external effects."""
import json
from pathlib import Path
import subprocess
from event_encoding import decode_event


def derive_reaction_view(journal,target,*,max_records=4096,max_references=16384):
    snapshot=journal.snapshot_with_token(target['conversation'])
    if len(snapshot['records'])>max_records:return dict(state='incomplete',reason='record-budget',sourceToken=snapshot['token'])
    records=[]
    for row in snapshot['records']:
        record=dict(reference=row['reference'],state=row['state'])
        if row['state']=='recorded':record['event']=decode_event(row['octets'][0])['value']
        records.append(record)
    script="import {deriveReactionSnapshot} from './reaction-snapshot.mjs';let s='';for await(const c of process.stdin)s+=c;const v=JSON.parse(s);process.stdout.write(JSON.stringify(deriveReactionSnapshot(v.target,v.records,v.budget)));"
    result=subprocess.run(['node','--input-type=module','-e',script],cwd=Path(__file__).parent,
        input=json.dumps(dict(target=target,records=records,budget=dict(maxRecords=max_records,maxReferences=max_references))),capture_output=True,text=True,check=True,timeout=10)
    view=json.loads(result.stdout);view['sourceToken']=snapshot['token'];return view


def install_reaction_view(journal,target,view):
    """Commit a complete presentation only if its exact source snapshot still exists."""
    if view.get('state')!='evaluated':return {'state':'incomplete'}
    name='reaction:'+target['principal']+':'+target['event']
    return journal.install_view(target['conversation'],name,view['sourceToken'],view)
