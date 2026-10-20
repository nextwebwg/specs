"""Trusted accepted/local-author journal projection; no caller-supplied authority."""
import hashlib
import json
from pathlib import Path
import subprocess
from event_encoding import decode_event

def project(sender, application):
    event=decode_event(application)['value'];records=[]
    for row in sender.receiver.journal.snapshot(event['conversation']):
        item=dict(reference=row['reference'],state=row['state'])
        if row['state']=='recorded':
            item.update(event=decode_event(row['octets'][0])['value'],digest=hashlib.sha256(row['octets'][0]).hexdigest())
        records.append(item)
    if event['operation']['kind']=='edit':
        from journal_edit_view import records_locked
        authority={tuple(r['reference'][k] for k in ('principal','conversation','event')):r['state'] for r in records_locked(sender.receiver,event['conversation'])}
        for r in records:
            state=authority.get(tuple(r['reference'][k] for k in ('principal','conversation','event')))
            if state!='valid':r['state']=state
    result=subprocess.run(['node',str(Path(__file__).with_suffix('.mjs'))],input=json.dumps(dict(event=event,records=records)),text=True,capture_output=True,check=True,timeout=10)
    result=json.loads(result.stdout)
    if result['projection'].get('state')!='projected':raise ValueError('Readable dependencies unavailable')
    return result
