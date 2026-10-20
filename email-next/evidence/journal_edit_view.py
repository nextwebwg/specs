"""Immutable accepted edits, with separately revalidated supersession eligibility."""
import base64,hashlib,json,subprocess
from pathlib import Path
from event_encoding import decode_event
from identity_bundle import decode_identity_bundle

def effect_authority(receiver,credential,*,budget,states):
    try:raw=bytes.fromhex(credential)
    except (ValueError,TypeError):return dict(state='pending',reason='missing-author-evidence')
    if len(raw)!=85 or raw[:21]!=b'email-next/device/v0\0':return dict(state='pending',reason='missing-author-evidence')
    principal='enp0:'+raw[21:53].hex();device='end0:'+raw[53:].hex();current=receiver.identity.current_state(principal)
    result=dict(principal=principal,device=device,head=current['head'])
    if current['conflicted']:return dict(result,state='conflict',reason='identity-conflict')
    if current['head'] is None:return dict(result,state='pending',reason='unknown-identity')
    cache=(principal,current['head'])
    if cache in states:state=states[cache]
    else:
        source=receiver.db.execute('SELECT length(bundle) FROM identity_transitions WHERE principal=? AND digest=? AND accepted=1',cache).fetchone()
        if source:
            budget[0]-=source[0]
            if budget[0]<0:raise EditSnapshotBudget('byte-budget')
            row=receiver.db.execute('SELECT bundle FROM identity_transitions WHERE principal=? AND digest=? AND accepted=1',cache).fetchone()
            state=next((s['value'] for s in decode_identity_bundle(row[0])['states'] if s['digest']==current['head']),None)
        else:
            source=receiver.db.execute('SELECT length(cast(record AS BLOB)) FROM claims WHERE principal=? AND digest=?',cache).fetchone()
            if source:
                budget[0]-=source[0]
                if budget[0]<0:raise EditSnapshotBudget('byte-budget')
                row=receiver.db.execute('SELECT record FROM claims WHERE principal=? AND digest=?',cache).fetchone()
                state=decode_event(base64.b64decode(json.loads(row[0])['state']))['value']
            else:state=None
        states[cache]=state
    if state is None:return dict(result,state='pending',reason='unknown-state')
    # Neither expiry nor superseded binding/roles is an explicit revocation.
    return dict(result,state='invalid' if device in state['revoked'] else 'valid',reason='device-revoked' if device in state['revoked'] else 'accepted-history')

class EditSnapshotBudget(ValueError):
    pass

def _limit(value):
    if type(value) is not int or not 0<=value<=2**53-1:raise ValueError('Finite nonnegative edit budget required')

def records_locked(receiver,conversation,*,max_records=4096,max_bytes=16*1024*1024):
    for limit in (max_records,max_bytes):_limit(limit)
    db=receiver.db;owned=not db.in_transaction
    if owned:db.execute('BEGIN')
    try:
        count,size=db.execute('SELECT count(*),coalesce(sum(length(octets)),0) FROM contributions WHERE conversation=?',(conversation,)).fetchone()
        if count>max_records:raise EditSnapshotBudget('record-budget')
        if size>max_bytes:raise EditSnapshotBudget('byte-budget')
        # Count/length checks and fetch share one SQLite snapshot. Provenance is
        # selected by relevant exact digest, never materialized across accounts.
        records=[];budget=[max_bytes-size];states={};local=bool(db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='local_author_evidence'").fetchone())
        for row in receiver.journal.snapshot(conversation):
            item=dict(reference=row['reference'],state='conflict' if row['state']=='conflict' else 'valid')
            if row['state']=='recorded':
                raw=row['octets'][0];item['event']=decode_event(raw)['value']
                if item['event']['operation']['kind']=='edit':
                    digest=hashlib.sha256(raw).hexdigest();credential=None
                    length=db.execute('SELECT length(credential) FROM mls_edit_sources WHERE digest=?',(digest,)).fetchone()
                    if length:
                        budget[0]-=length[0]
                        if budget[0]<0:raise EditSnapshotBudget('byte-budget')
                        credential=db.execute('SELECT credential FROM mls_edit_sources WHERE digest=?',(digest,)).fetchone()[0]
                    elif local:
                        length=db.execute('SELECT length(cast(metadata AS BLOB)) FROM local_author_evidence WHERE digest=?',(digest,)).fetchone()
                        if length:
                            budget[0]-=length[0]
                            if budget[0]<0:raise EditSnapshotBudget('byte-budget')
                            credential=json.loads(db.execute('SELECT metadata FROM local_author_evidence WHERE digest=?',(digest,)).fetchone()[0])['senderIdentity']
                    authority=effect_authority(receiver,credential,budget=budget,states=states)
                    item.update(state=authority['state'],authority=authority)
            records.append(item)
        if owned:db.execute('COMMIT')
        return records
    except BaseException:
        if owned and db.in_transaction:db.execute('ROLLBACK')
        raise

def derive_locked(receiver,root,*,max_records=4096,max_references=16384,max_bytes=16*1024*1024):
    for limit in (max_records,max_references,max_bytes):_limit(limit)
    try:records=records_locked(receiver,root['conversation'],max_records=max_records,max_bytes=max_bytes)
    except EditSnapshotBudget as error:return dict(state='incomplete',reason=str(error),sourceToken=None)
    token=hashlib.sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if len(records)>max_records:return dict(state='incomplete',reason='record-budget',sourceToken=token)
    relevant=[r for r in records if r.get('event',{}).get('operation',{}).get('kind')=='edit' and r['event']['operation']['root']==root]
    if any(r['state']=='pending' for r in relevant):return dict(state='incomplete',reason='unknown-authority',sourceToken=token)
    request=json.dumps(dict(root=root,records=records,budget=dict(maxRecords=max_records,maxReferences=max_references)))
    if len(request.encode())>max_bytes:return dict(state='incomplete',reason='byte-budget',sourceToken=token)
    script="import {deriveEditSnapshot} from './edit-snapshot.mjs';let s='';for await(const c of process.stdin)s+=c;const v=JSON.parse(s);process.stdout.write(JSON.stringify(deriveEditSnapshot(v.root,v.records,v.budget)));"
    result=subprocess.run(['node','--input-type=module','-e',script],cwd=Path(__file__).parent,input=request,text=True,capture_output=True,check=True,timeout=10)
    view=json.loads(result.stdout);view.update(sourceToken=token,eligibility=[dict(reference=r['reference'],**r['authority']) for r in relevant]);return view

def view(receiver,root,**limits):
    """Recheck authority on every trusted read; transaction excludes stale installs."""
    db=receiver.db;owned=not db.in_transaction
    if owned:db.execute('BEGIN IMMEDIATE')
    try:
        result=derive_locked(receiver,root,**limits);name='edit:'+root['principal']+':'+root['event']
        if result['state']=='evaluated':db.execute('INSERT INTO derived_views VALUES(?,?,?,?) ON CONFLICT(conversation,name) DO UPDATE SET source_token=excluded.source_token,payload=excluded.payload',(root['conversation'],name,result['sourceToken'],json.dumps(result,sort_keys=True)))
        else:
            old=db.execute('SELECT payload FROM derived_views WHERE conversation=? AND name=?',(root['conversation'],name)).fetchone()
            if old:result['lastCommitted']=dict(json.loads(old[0]),stale=True)
        if owned:db.execute('COMMIT')
        return result
    except BaseException:
        if owned and db.in_transaction:db.execute('ROLLBACK')
        raise
