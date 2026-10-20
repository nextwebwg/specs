"""Qualify actual public-v1 initial admission evidence; never restore old secrets."""
import hashlib
import base64
import json
from pathlib import Path
from application_agreement import profile
from application_support import supports
from event_encoding import encode_event
from provider_control import decode,exact,verify_signature
from passive_discovery import canonical_base64,decode_assertion,APPLICATION_DOMAIN,TUPLE_DOMAIN,uint64
from provider_mls import call
import group_instances as instances

DOMAIN=b'email-next/mls-new-conversation-invitation/v1\0'
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def has(db,table):return bool(db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone())
def credential(who):return (b'email-next/device/v0\0'+bytes.fromhex(who['principal'][5:])+bytes.fromhex(who['device'][5:])).hex()
def initialize(db):
    instances.initialize(db)
    db.execute('CREATE TABLE IF NOT EXISTS mls_instance_migration(instance TEXT PRIMARY KEY,source_kind TEXT NOT NULL,source_id TEXT NOT NULL,source_digest TEXT NOT NULL,version INTEGER NOT NULL)')

def _source(db,group):
    sources=[]
    if has(db,'application_invitation_acceptance'):
        for principal,ident,raw,sig,result in db.execute('SELECT principal,id,payload,signature,result FROM application_invitation_acceptance'):
            value=decode(raw,max_bytes=2*1024*1024,max_depth=32)
            if canonical_base64(value['group']).hex()==group:sources.append(('signed-initial-admission',ident,raw,sig,json.loads(result),principal))
    if has(db,'initial_invitation_prepared'):
        from application_invitation import parse
        from invitation_mime import select
        for ident,wire in db.execute('SELECT id,wire FROM initial_invitation_prepared'):
            wrapper,raw,value,binary,_,_=parse(select(wire))
            if binary['group'].hex()==group:sources.append(('signed-initial-creation',ident,raw,wrapper['signature'],None,value['creator']['principal']))
    if len(sources)!=1:raise ValueError('Unique signed initial source required')
    return sources[0]

def _evidence(db,source,group):
    from mls_invitation import FIELDS
    kind,source_id,raw,signature,receipt,principal=source
    value=decode(raw,max_bytes=2*1024*1024,max_depth=32);exact(value,FIELDS|{'applicationAssertions'})
    context_raw=canonical_base64(value['context']);context=decode(context_raw,max_bytes=1048576,max_depth=32)
    exact(context,{'version','purpose','conversation','profile','administrators','application','ordering'})
    if value['version'] not in ('1','2') or (value['purpose'],value['profile'],value['epoch'])!=('mls-new-conversation-invitation','mls-1-0001','1') or value['creator']['principal']!=principal:raise ValueError('Signed initial profile')
    ordering={'kind':'fixed-roster-v0'} if value['version']=='1' or context.get('ordering')=={'kind':'fixed-roster-v0'} else dict(kind='designated-member-v0',principal=value['creator']['principal'],device=value['creator']['device'])
    allowed=(value['version']=='1' and context['version']=='2' and ordering['kind']=='fixed-roster-v0') or (value['version']=='2' and (context['version']=='3' or (context['version']=='2' and ordering['kind']=='designated-member-v0')))
    if not allowed or (context['purpose'],context['conversation'],context['profile'],context['administrators'],context['ordering'])!=('conversation-context',value['conversation'],'mls-1-0001',[principal],ordering):raise ValueError('Public initial context mismatch')
    application=profile(context['application']);reference=canonical_base64(value['keyPackageRef']).hex();pair={'payload':base64.b64encode(raw).decode(),'signature':signature}
    expected=sorted(credential(value[k]) for k in ('creator','target'))
    if len(set(expected))!=2:raise ValueError('Initial device coverage')
    if kind=='signed-initial-admission':
        if receipt!={'status':'admitted-unverified','group':group,'invitation':source_id,'mailbox_verified':False} or value['invitation']!=source_id:raise ValueError('Accepted public receipt')
        row=db.execute('SELECT request,context,evidence,result FROM application_admissions WHERE reference=?',(reference,)).fetchone()
        if not row:raise ValueError('Missing accepted application source')
        request=json.loads(row[0]);evidence=json.loads(row[2]);joined=json.loads(row[3])
        if request['reference']!=reference or request['invitation']!=encode_event(pair).hex() or request['group']!=group or request['context']!=context_raw.hex() or request['creator']!=credential(value['creator']) or request['ordering'] is not (ordering['kind']=='designated-member-v0') or row[1]!=context_raw:raise ValueError('Accepted application source mismatch')
        proof_rows=[json.loads(r[0]) for r in db.execute('SELECT evidence FROM application_admission_devices WHERE reference=? ORDER BY credential',(reference,))]
        if proof_rows!=evidence['devices']:raise ValueError('Accepted device evidence mismatch')
        selections=[dict(mailbox=p['mailbox'],generation=p['generation'],payload=p['assertion'],signature=p['signature']) for p in proof_rows]
        if request['selections']!=selections:raise ValueError('Accepted selection mismatch')
        consumed=db.execute('SELECT device,invitation,joined FROM provider_mls_admission WHERE reference=?',(reference,)).fetchone()
        if not consumed or consumed[1] is None or json.loads(consumed[1])!=pair:raise ValueError('Consumed invitation mismatch')
        device=json.loads(consumed[0]);other=json.loads(consumed[2])
        if device['identity']!=credential(value['target']) or device['reference']!=reference or not any(m['identity']==device['identity'] and m['key']==device['key'] for m in joined['members']):raise ValueError('Consumed package device')
        for key in ('group','epoch','context','members','signerIdentity','signerKey'):
            if other[key]!=joined[key]:raise ValueError('Public admission metadata mismatch')
        if (joined['group'],joined['epoch'],joined['context'],joined['signerIdentity'])!=(group,'1',context_raw.hex(),credential(value['creator'])):raise ValueError('Authenticated initial group')
        source_detail=dict(request=request,evidence=evidence,receipt=receipt)
        admission='signed-application:'+reference;provenance_kind='signed-admission';provenance_ref=reference
    else:
        from application_invitation import parse
        from invitation_mime import select
        row=db.execute('SELECT wire,metadata,proofs,request FROM initial_invitation_prepared WHERE id=?',(source_id,)).fetchone()
        wrapper,_,_,_,_,decoded=parse(select(row[0]));metadata=json.loads(row[1]);proofs=json.loads(row[2]);request=json.loads(row[3])
        if db.execute('SELECT delivery FROM initial_application_packages WHERE reference=?',(reference,)).fetchone()!=(source_id,):raise ValueError('Creator package binding')
        if (metadata['group'],metadata['epoch'],metadata['context'],metadata['senderIdentity'])!=(group,'1',context_raw.hex(),credential(value['creator'])):raise ValueError('Creator installed metadata')
        if proofs['creator']!=credential(value['creator']) or profile(proofs['application'])!=application or proofs['notBefore']!=value['notBefore'] or proofs['notAfter']!=value['notAfter']:raise ValueError('Creator selected profile')
        selected=proofs['selected']
        if selected!=request['selected'] or len(selected)!=2:raise ValueError('Creator selected evidence')
        proof_rows=[]
        choices={choice['digest']:choice for choice in selected}
        if len(choices)!=len(selected):raise ValueError('Duplicate creator assertion selection')
        for d in decoded:
            choice=choices.get(d['assertion']['digest'])
            if choice is None:raise ValueError('Missing creator assertion selection')
            actual=json.loads(bytes.fromhex(choice['wrapper']))
            if actual!=wrapper['applicationAssertions'][len(proof_rows)] or choice['digest']!=d['assertion']['digest']:raise ValueError('Creator assertion mismatch')
            a=d['assertion'];v=a['value'];ident=credential(v);key=next(m['key'] for m in metadata['members'] if m['identity']==ident)
            proof_rows.append(dict(credential=ident,signatureKey=key,assertion=a['octets'].hex(),digest=a['digest'],signature=d['signature'].hex(),head=v['state'],binding=v['binding'],application=context['application'],ordering=ordering['kind'],mailbox=choice['mailbox'],generation=choice['generation']))
        joined=dict(metadata,signerIdentity=metadata['senderIdentity'],signerKey=metadata['senderKey'])
        source_detail=dict(request=request,proofs=proofs,metadata=metadata)
        admission='signed-initial-creation:'+sha(raw);provenance_kind='signed-initial-creation';provenance_ref=source_id
    if sorted(p['credential'] for p in proof_rows)!=expected or sorted(m['identity'] for m in joined['members'])!=expected:raise ValueError('Accepted roster coverage')
    refs=value['applicationAssertions']
    if len(refs)!=2:raise ValueError('Signed reference coverage')
    normalized=[]
    for proof,ref in zip(proof_rows,refs):
        assertion=decode_assertion(bytes.fromhex(proof['assertion']));v=assertion['value'];ident=credential(v)
        if ident!=proof['credential'] or (v['principal'],v['device'],assertion['digest'],proof['signature'])!=(ref['principal'],ref['device'],ref['digest'],ref['signature']) or proof['digest']!=assertion['digest'] or v['state']!=proof['head'] or v['binding']!=proof['binding']:raise ValueError('Historical signed proof binding')
        named=value['creator'] if ident==credential(value['creator']) else value['target']
        if named['state']!=proof['head'] or named['binding']!=proof['binding'] or ('mailbox' in named and named['mailbox']!=v['mailbox']):raise ValueError('Signed named member binding')
        if not uint64(v['notBefore'])<=uint64(value['notBefore'])<=uint64(value['notAfter'])<=uint64(v['notAfter']):raise ValueError('Historical interval mismatch')
        verify_signature(assertion['octets'],proof['signature'],proof['signatureKey'],TUPLE_DOMAIN if context['version']=='3' else APPLICATION_DOMAIN)
        if not supports(v,context['application'],ordering['kind']) or profile(proof['application'])!=application or proof['ordering']!=ordering['kind']:raise ValueError('Historical application agreement')
        if not any(m['identity']==ident and m['key']==proof['signatureKey'] for m in joined['members']):raise ValueError('Historical roster key')
        agreement=db.execute('SELECT signature_key,application FROM mls_application_agreement WHERE group_id=? AND credential=?',(group,ident)).fetchone()
        provenance=db.execute('SELECT kind,admission FROM mls_application_agreement_provenance WHERE group_id=? AND credential=?',(group,ident)).fetchone()
        if agreement!=(proof['signatureKey'],application) or provenance!=(provenance_kind,provenance_ref):raise ValueError('Historical agreement source mismatch')
        normalized.append(dict(credential=ident,key=proof['signatureKey'],application=application,kind=provenance_kind,reference=provenance_ref))
    if db.execute('SELECT count(*) FROM mls_application_agreement WHERE group_id=?',(group,)).fetchone()[0]!=2:raise ValueError('Extra application agreement')
    signer=next(p for p in proof_rows if p['credential']==credential(value['creator']))
    if joined['signerKey']!=signer['signatureKey']:raise ValueError('Historical signer key')
    verify_signature(raw,signature,signer['signatureKey'],DOMAIN if value['version']=='1' else b'email-next/mls-new-conversation-invitation/v2\0')
    return dict(raw=raw,signature=signature,value=value,context=context_raw,agreements=normalized,admission=admission,source_detail=source_detail,joined=joined)

def qualify_signed_initial_locked(db,binary,*,local_key,crash=None):
    if not db.in_transaction:raise ValueError('Caller transaction required')
    cp=db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
    if not cp:raise ValueError('Active checkpoint required')
    group=cp[0];source=_source(db,group);e=_evidence(db,source,group);kind,source_id=source[:2]
    instance=instances.admission_instance(e['raw'],bytes.fromhex(e['signature']))
    digest=sha(canonical(dict(kind=kind,id=source_id,payload=e['raw'].hex(),signature=e['signature'],details=e['source_detail'],agreements=e['agreements'],admission=e['admission'])))
    snapshot=call(Path(binary).with_name('group-transitions'),op='inspect',checkpoint=json.loads(cp[1]),group=group,key=local_key)['snapshot']
    if snapshot['epoch']!='1' or snapshot['context']!=e['context'].hex() or sorted((m['identity'],m['key']) for m in snapshot['members'])!=sorted((m['identity'],m['key']) for m in e['joined']['members']):raise ValueError('Unsupported advanced initial history')
    for table in ('gt_decision','gt_receive','gt_pending','mls_group_inactive'):
        if has(db,table) and db.execute('SELECT 1 FROM '+table).fetchone():raise ValueError('Unsupported transition history')
    expected={(m['identity'],m['key']) for m in snapshot['members']}
    periods=db.execute('SELECT identity,key,start_epoch,end_epoch,admission,removal FROM mls_membership_episode WHERE group_id=?',(group,)).fetchall()
    if len(periods)!=2 or {(p[0],p[1]) for p in periods}!=expected or any(p[2:]!=('1',None,e['admission'],None) for p in periods):raise ValueError('Initial episode source mismatch')
    prior=db.execute('SELECT source_kind,source_id,source_digest,version FROM mls_instance_migration WHERE instance=?',(instance,)).fetchone()
    pointer=db.execute('SELECT instance FROM mls_checkpoint_instance WHERE id=1').fetchone()
    if prior:
        if prior!=(kind,source_id,digest,1) or pointer!=(instance,):raise ValueError('Migration source conflict')
    elif pointer or db.execute('SELECT 1 FROM mls_group_instances').fetchone():raise ValueError('Existing unrelated qualification')
    else:
        db.execute('INSERT INTO mls_group_instances VALUES(?,?,?,?,?,NULL)',(instance,group,e['admission'],kind,'active'))
        db.execute('INSERT INTO mls_checkpoint_instance VALUES(1,?)',(instance,))
        for a in e['agreements']:db.execute('INSERT INTO mls_instance_agreements VALUES(?,?,?,?,?,?)',(instance,a['credential'],a['key'],a['application'],a['kind'],a['reference']))
        for identity,key,*_ in periods:db.execute('INSERT INTO mls_episode_instance VALUES(?,?,?,?,?)',(group,identity,key,e['admission'],instance))
        if crash:crash('after-instance')
    expected_instance=(group,e['admission'],kind,'active')
    if db.execute('SELECT group_id,admission_digest,provenance,status FROM mls_group_instances WHERE instance=?',(instance,)).fetchone()!=expected_instance:raise ValueError('Conflicting instance record')
    expected_agreements=sorted((a['credential'],a['key'],a['application'],a['kind'],a['reference']) for a in e['agreements'])
    if sorted(db.execute('SELECT credential,signature_key,application,provenance_kind,admission_ref FROM mls_instance_agreements WHERE instance=?',(instance,)))!=expected_agreements:raise ValueError('Conflicting instance agreements')
    if set(db.execute('SELECT identity,key,admission FROM mls_episode_instance WHERE instance=?',(instance,)))!={(i,k,e['admission']) for i,k in expected}:raise ValueError('Conflicting episode qualification')
    members=[str(m['index'])+':'+m['identity']+':'+m['key'] for m in snapshot['members']]
    for received_digest,wire,stored in db.execute('SELECT digest,wire,evidence FROM mls_receives'):
        evidence=json.loads(stored);p=evidence['processed'];s=evidence['snapshot']
        if sha(wire)!=received_digest or p['group']!=group or p['epoch']!='1' or s['group']!=group or s['epoch']!='1' or s['context']!=snapshot['context'] or s['members']!=members:raise ValueError('Ambiguous original receive instance')
        if 'predecessor' in s and s['predecessor']!=snapshot['predecessor']:raise ValueError('Historical GroupContext mismatch')
        if not any(str(m['index'])==p['sender'] and m['identity']==p['credential'] for m in snapshot['members']):raise ValueError('Original receive sender')
        existing=db.execute('SELECT instance FROM mls_receive_instance WHERE digest=?',(received_digest,)).fetchone()
        if existing and existing!=(instance,):raise ValueError('Conflicting receive instance')
        db.execute('INSERT OR IGNORE INTO mls_receive_instance VALUES(?,?)',(received_digest,instance))
    if has(db,'mls_retained_epoch'):
        expected_snapshot=canonical(dict(snapshot,members=members))
        for origin,epoch,stored in db.execute('SELECT instance,epoch,snapshot FROM mls_retained_epoch WHERE group_id=?',(group,)).fetchall():
            if origin not in ('configured:'+group,instance) or epoch!='1' or canonical(json.loads(stored))!=expected_snapshot:raise ValueError('Conflicting retained epoch source')
            existing=db.execute('SELECT snapshot FROM mls_retained_epoch WHERE instance=? AND group_id=? AND epoch=?',(instance,group,epoch)).fetchone()
            if existing and canonical(json.loads(existing[0]))!=expected_snapshot:raise ValueError('Conflicting target epoch')
            db.execute('INSERT OR IGNORE INTO mls_retained_epoch VALUES(?,?,?,?)',(instance,group,epoch,stored))
            if origin!=instance:db.execute('DELETE FROM mls_retained_epoch WHERE instance=? AND group_id=? AND epoch=?',(origin,group,epoch))
    db.execute('INSERT OR IGNORE INTO mls_instance_migration VALUES(?,?,?,?,1)',(instance,kind,source_id,digest))
    db.execute('INSERT INTO mls_instance_schema VALUES(1,1) ON CONFLICT(id) DO UPDATE SET version=1')
    if crash:crash('before-commit')
    return dict(instance=instance,group=group,status='active',provenance=kind)

def migrate_signed_initial(identity,binary,*,local_key,crash=None):
    db=identity.db;initialize(db);db.execute('BEGIN IMMEDIATE')
    try:
        result=qualify_signed_initial_locked(db,binary,local_key=local_key,crash=crash);db.execute('COMMIT')
        if crash:crash('after-commit')
        return result
    except BaseException:
        if db.in_transaction:db.execute('ROLLBACK')
        raise
