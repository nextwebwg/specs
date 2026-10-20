"""Signed current confirmations; historical selection is never inferred from cache."""
import hashlib
import json
from event_encoding import encode_event
from passive_discovery import decode_passive_discovery
from passive_discovery_verify import verify_passive_discovery
from mls_receive import LockedIdentity,MlsReceive
from application_agreement import profile
from application_support import supports
import group_instances as instances

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def initialize(db):
    if db.in_transaction:raise ValueError('Initialize outside transaction')
    db.executescript('''CREATE TABLE IF NOT EXISTS mls_support_records(id TEXT PRIMARY KEY,record BLOB NOT NULL);
    CREATE TABLE IF NOT EXISTS mls_support_selected(group_id TEXT NOT NULL,credential TEXT NOT NULL,record TEXT NOT NULL,PRIMARY KEY(group_id,credential));
    CREATE TABLE IF NOT EXISTS mls_support_episodes(group_id TEXT NOT NULL,credential TEXT NOT NULL,key TEXT NOT NULL,admission TEXT NOT NULL,record TEXT NOT NULL,PRIMARY KEY(group_id,credential,key,admission));''')
def load(db,ident):
    row=db.execute('SELECT record FROM mls_support_records WHERE id=?',(ident,)).fetchone()
    if not row or hashlib.sha256(row[0]).hexdigest()!=ident:raise ValueError('Missing immutable support record')
    return json.loads(row[0])
def episode(db,group,credential,key):
    current=instances.optional_current(db,group)
    if current:
        rows=db.execute('SELECT e.admission FROM mls_membership_episode e JOIN mls_episode_instance i USING(group_id,identity,key,admission) WHERE e.group_id=? AND e.identity=? AND e.key=? AND e.end_epoch IS NULL AND i.instance=?',(group,credential,key,current['instance'])).fetchall()
    else:rows=db.execute('SELECT admission FROM mls_membership_episode WHERE group_id=? AND identity=? AND key=? AND end_epoch IS NULL',(group,credential,key)).fetchall()
    if len(rows)!=1:raise ValueError('Unique current support episode required')
    return rows[0][0]
class TransitionSupport:
    def __init__(self,coordinator):self.g=coordinator;self.db=coordinator.db;initialize(self.db)
    def confirm(self,wrapper,*,time,trust_policy='allow-unverified'):
        MlsReceive._policy(time,trust_policy)
        d=decode_passive_discovery(wrapper);a=d['assertion'];v=a['value']
        if v['version'] not in ('1','2','3','4','5'):raise ValueError('Signed application support required')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            state=self.g.live()['snapshot'];ctx=json.loads(bytes.fromhex(state['context']))
            if ctx.get('version') not in ('2','3','4','5','6') or ctx['ordering']['kind']!='designated-member-v0':raise ValueError('Designated application context required')
            checked=verify_passive_discovery(wrapper,LockedIdentity(self.g.identity),time=time,trust_policy=trust_policy)
            if checked.get('status')!='snapshot-authorized-unverified':raise ValueError('Current support authority')
            key=next(b['value']['signingKey'] for b in d['identity']['bindings'] if b['digest']==v['binding'])
            credential=(b'email-next/device/v0\0'+bytes.fromhex(v['principal'][5:])+bytes.fromhex(v['device'][5:])).hex()
            if not supports(v,ctx['application'],'designated-member-v0'):raise ValueError('Exact selected profile support')
            existing=any(m['identity']==credential and m['key']==key for m in state['members'])
            origin=instances.optional_current(self.db,state['group'])
            if existing and self.g.receiver.application_agreement.resolve(state['group'],[dict(identity=credential,key=key)],instance=origin['instance'] if origin else None)!=ctx['application']:raise ValueError('Existing immutable agreement required')
            if not existing and a['key_package_octets'] is None:raise ValueError('Fresh target package required')
            record=dict(group=state['group'],credential=credential,key=key,context=state['context'],episode=episode(self.db,state['group'],credential,key) if existing else None,kind='signed-current-confirmation' if existing else 'signed-target-candidate',epoch=state['epoch'],predecessor=state['predecessor'],time=dict(time),wrapper=wrapper.hex(),application=ctx['application'])
            raw=canonical(record);ident=hashlib.sha256(raw).hexdigest();self.db.execute('INSERT OR IGNORE INTO mls_support_records VALUES(?,?)',(ident,raw))
            self.db.execute('INSERT INTO mls_support_selected VALUES(?,?,?) ON CONFLICT(group_id,credential) DO UPDATE SET record=excluded.record',(state['group'],credential,ident));self.db.execute('COMMIT');return ident
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise

def selected(db,result,*,time=None):
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='mls_support_selected'").fetchone():return None
    before=result['before'];old={(m['identity'],m['key']) for m in before['members']};added=[m for m in result['after']['members'] if (m['identity'],m['key']) not in old]
    if not added or not all(db.execute('SELECT 1 FROM mls_support_selected WHERE group_id=? AND credential=?',(before['group'],m['identity'])).fetchone() for m in added):return None
    refs=[]
    for m in result['after']['members']:
        row=db.execute('SELECT record FROM mls_support_selected WHERE group_id=? AND credential=?',(before['group'],m['identity'])).fetchone()
        if not row and (m['identity'],m['key']) in old:
            from initial_roster_support import bootstrap_locked
            source=bootstrap_established_locked(db,before,m) or bootstrap_initial_locked(db,before,m) or bootstrap_locked(db,before,m)
            if source:row=(source,)
        if not row:raise ValueError('Missing signed predecessor support')
        r=load(db,row[0])
        if (r['group'],r['credential'],r['key'],r['context'])!=(before['group'],m['identity'],m['key'],before['context']):raise ValueError('Support scope')
        if (m['identity'],m['key']) in old:
            active=episode(db,before['group'],m['identity'],m['key'])
            linked=db.execute('SELECT record FROM mls_support_episodes WHERE group_id=? AND credential=? AND key=? AND admission=?',(before['group'],m['identity'],m['key'],active)).fetchone()
            if r['episode']!=active and linked!=(row[0],):raise ValueError('Support belongs to old membership episode')
        elif r['kind']!='signed-target-candidate' or r['predecessor']!=before['predecessor']:raise ValueError('Stale target support candidate')
        refs.append(dict(credential=m['identity'],key=m['key'],record=row[0]))
    return refs

def wrappers(db,result):
    proof=result.get('authorization',{}).get('applicationAgreement',{})
    if proof.get('version')!='signed-device-support-v1':raise ValueError('Accepted signed support decision required')
    refs=proof['devices'];expected={(m['identity'],m['key']) for m in result['after']['members']}
    if {(r['credential'],r['key']) for r in refs}!=expected or len(refs)!=len(expected):raise ValueError('Support decision coverage')
    records=[load(db,r['record']) for r in refs]
    for r,ref in zip(records,refs):
        if (r['credential'],r['key'],r['group'],r['context'])!=(ref['credential'],ref['key'],result['after']['group'],result['after']['context']):raise ValueError('Historical support scope')
    return records


def bootstrap_established_locked(db,before,member):
    """Reuse accepted invitation evidence only within its continuous instance."""
    if not db.in_transaction:raise ValueError('Caller transaction required')
    from established_invitation import sha
    from established_support import proofs
    from provider_control import verify_signature
    from passive_discovery import canonical_base64
    current=instances.optional_current(db,before['group'])
    if not current:return None
    if current['status']!='active':raise ValueError('Accepted support instance ended')
    context=json.loads(bytes.fromhex(before['context']))
    if context.get('version') not in ('2','3','4','5','6') or context.get('ordering',{}).get('kind')!='designated-member-v0':raise ValueError('Established support requires unchanged designated context')
    instance=current['instance'];credential=member['identity'];key=member['key']
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='mls_established_support'").fetchone():return None
    row=db.execute('SELECT evidence FROM mls_established_support WHERE instance=? AND credential=?',(instance,credential)).fetchone()
    if not row:return None
    receipt=db.execute('SELECT payload,signature FROM membership_invitation_acceptance WHERE instance=?',(instance,)).fetchall()
    if len(receipt)!=1:raise ValueError('Unique accepted established source required')
    raw,signature=receipt[0];value=json.loads(raw)
    if value.get('version') not in ('1','2','3','4','5') or canonical_base64(value['context']).hex()!=before['context'] or canonical_base64(value['group']).hex()!=before['group'] or instances.admission_instance(raw,bytes.fromhex(signature))!=instance:raise ValueError('Accepted support instance/context mismatch')
    admission='established:'+sha(raw)
    if episode(db,before['group'],credential,key)!=admission:raise ValueError('Accepted support membership ended')
    agreement=db.execute('SELECT signature_key,application,provenance_kind,admission_ref FROM mls_instance_agreements WHERE instance=? AND credential=?',(instance,credential)).fetchone()
    if agreement!=(key,profile(context['application']),'signed-established-inviter-selection',value['decision']):raise ValueError('Accepted support key/profile provenance mismatch')
    allproofs=[]
    for named in value['members']:
        ident=(b'email-next/device/v0\0'+bytes.fromhex(named['principal'][5:])+bytes.fromhex(named['device'][5:])).hex()
        source=db.execute('SELECT evidence FROM mls_established_support WHERE instance=? AND credential=?',(instance,ident)).fetchone()
        if not source:raise ValueError('Incomplete accepted support provenance')
        evidence=json.loads(source[0])
        if evidence.get('selectionAuthority')!='inviter-attested-historical-selection' or evidence.get('invitation')!=value['invitation'] or evidence.get('decision')!=value['decision'] or evidence.get('application')!=context['application']:raise ValueError('Accepted support provenance mismatch')
        allproofs.append(evidence['wrapper'])
    creator=next(m for m in value['members'] if (m['principal'],m['device'])==(value['creator']['principal'],value['creator']['device']))
    verify_signature(raw,signature,creator['signingKey'],('email-next/mls-established-membership-invitation/v'+value['version']).encode()+b'\0')
    proofs(dict(applicationAssertions=allproofs),value,context)
    selected=json.loads(row[0])['wrapper'];decoded=decode_passive_discovery(encode_event(selected));v=decoded['assertion']['value']
    expected=(b'email-next/device/v0\0'+bytes.fromhex(v['principal'][5:])+bytes.fromhex(v['device'][5:])).hex()
    named=next((m for m in value['members'] if (m['principal'],m['device'])==(v['principal'],v['device'])),None)
    if expected!=credential or not named or named['signingKey']!=key:raise ValueError('Accepted support device key mismatch')
    record=dict(group=before['group'],credential=credential,key=key,context=before['context'],episode=admission,kind='signed-established-admission',epoch=value['epoch'],instance=instance,source=sha(raw),wrapper=encode_event(selected).hex(),application=context['application'])
    encoded=canonical(record);ident=hashlib.sha256(encoded).hexdigest()
    db.execute('INSERT OR IGNORE INTO mls_support_records VALUES(?,?)',(ident,encoded))
    db.execute('INSERT INTO mls_support_selected VALUES(?,?,?) ON CONFLICT(group_id,credential) DO UPDATE SET record=excluded.record',(before['group'],credential,ident))
    return ident


def bootstrap_initial_locked(db,before,member):
    """Only actual initial2 designated admission, never fixed-roster reinterpretation."""
    if not db.in_transaction:raise ValueError('Caller transaction required')
    from signed_initial_instances import _source,_evidence,credential
    from application_invitation import parse
    from invitation_mime import select
    current=instances.optional_current(db,before['group'])
    if not current or current['status']!='active':return None
    origin=db.execute('SELECT provenance FROM mls_group_instances WHERE instance=?',(current['instance'],)).fetchone()
    if origin not in [('signed-initial-admission',),('signed-initial-creation',)]:return None
    source=_source(db,before['group']);e=_evidence(db,source,before['group']);value=e['value']
    if value['version']!='2' or e['context'].hex()!=before['context'] or json.loads(e['context'])['ordering']['kind']!='designated-member-v0':raise ValueError('Initial support mode/context mismatch')
    if instances.admission_instance(e['raw'],bytes.fromhex(e['signature']))!=current['instance']:raise ValueError('Initial support instance mismatch')
    if episode(db,before['group'],member['identity'],member['key'])!=e['admission']:raise ValueError('Initial support membership ended')
    agreement=next((a for a in e['agreements'] if a['credential']==member['identity']),None)
    actual=db.execute('SELECT signature_key,application,provenance_kind,admission_ref FROM mls_instance_agreements WHERE instance=? AND credential=?',(current['instance'],member['identity'])).fetchone()
    if not agreement or member['key']!=agreement['key'] or actual!=(agreement['key'],agreement['application'],agreement['kind'],agreement['reference']):raise ValueError('Initial support key/profile source mismatch')
    if source[0]=='signed-initial-creation':
        wire=db.execute('SELECT wire FROM initial_invitation_prepared WHERE id=?',(source[1],)).fetchone()[0];outer=select(wire)
    else:
        row=db.execute('SELECT wrapper FROM initial_invitation_proofs WHERE principal=? AND id=?',(value['creator']['principal'],value['invitation'])).fetchone()
        if not row:raise ValueError('Missing original initial proof wrapper')
        outer=row[0]
    wrapper,raw,_,_,_,_=parse(outer)
    if raw!=e['raw'] or wrapper['signature']!=e['signature']:raise ValueError('Initial original proof mismatch')
    proof=next(p for p in wrapper['applicationAssertions'] if credential(decode_passive_discovery(encode_event(p))['assertion']['value'])==member['identity'])
    record=dict(group=before['group'],credential=member['identity'],key=member['key'],context=before['context'],episode=e['admission'],kind='signed-initial-admission',epoch=value['epoch'],instance=current['instance'],source=hashlib.sha256(raw).hexdigest(),wrapper=encode_event(proof).hex(),application=json.loads(e['context'])['application'])
    encoded=canonical(record);ident=hashlib.sha256(encoded).hexdigest();db.execute('INSERT OR IGNORE INTO mls_support_records VALUES(?,?)',(ident,encoded));db.execute('INSERT INTO mls_support_selected VALUES(?,?,?)',(before['group'],member['identity'],ident));return ident
