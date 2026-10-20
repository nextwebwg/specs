"""Retained terminal-control route only; never current device authorization."""
import base64
import json
import subprocess
from pathlib import Path
from group_transitions import ids
from passive_discovery import decode_assertion

def check_terminal_route_locked(store,target,identity,key,time,trust_policy):
    if not store.db.in_transaction:raise ValueError('Caller transaction required')
    if trust_policy!='allow-unverified':raise ValueError('Terminal route verification required')
    principal,device=ids(identity);current=store._current(target['mailbox'])
    if not current or not current['enabled'] or current['generation']!=target['generation'] or current['principal']!=target['principal'] or principal!=target['principal']:raise ValueError('Changed terminal route')
    row=store.db.execute('SELECT assertion,signature,signing_key FROM mailbox_observations WHERE mailbox=? AND digest=?',(target['mailbox'],target['observation'])).fetchone()
    if not row:raise ValueError('Missing retained terminal evidence')
    raw,signature,signing_key=row;parsed=decode_assertion(raw);v=parsed['value']
    if parsed['digest']!=target['observation'] or v['mailbox']!=target['mailbox'] or (v['principal'],v['device'])!=(principal,device) or signing_key.hex()!=key:raise ValueError('Terminal target mismatch')
    records=store.db.execute('SELECT digest FROM mailbox_authenticated_records WHERE principal=? AND device=? AND record=?',(principal,device,v['record'])).fetchall()
    if records!=[(target['observation'],)]:raise ValueError('Missing or collided historical authentication')
    if int(time['earliest'])<int(v['notBefore']) or int(time['latest'])>int(v['notAfter']):raise ValueError('Terminal observation expired/uncertain')
    result=subprocess.run(['node',str(Path(__file__).with_name('check-passive-discovery.mjs'))],input=json.dumps(dict(version=v['version'],payload=base64.b64encode(raw).decode(),signature=signature.hex(),key=key)),text=True,capture_output=True,check=True,timeout=10)
    if json.loads(result.stdout).get('status')!='signature-valid':raise ValueError('Terminal observation proof')
    return dict(kind='terminal-routing-only',mailbox=target['mailbox'],generation=target['generation'],principal=principal,device=device,key=key,decision=current['decisionId'],identityAnchor=current['identityAnchor'],observation=target['observation'],assertion=raw.hex(),signature=signature.hex(),state=v['state'],binding=v['binding'])
