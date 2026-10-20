"""Local own-account public evidence coordination, not a remote pairing protocol.

Trusted configuration supplies the existing account anchor and exact mailbox set.
Mailbox login and received data cannot enable publication or enroll a device.
Private device material and conversation checkpoints never enter this outbox.
"""
import base64,hashlib,json,re,sqlite3
from event_encoding import encode_event
from identity_bundle import decode_identity_bundle
from passive_discovery import decode_passive_discovery,mailbox_syntax
from passive_discovery_verify import verify_passive_discovery_locked
from client_onboarding import ClientOnboarding
from discovery_mime import extract_discovery,MEDIA_TYPE
from mls_receive import MlsReceive

def digest(raw):return hashlib.sha256(raw).hexdigest()
def packed(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()

class PublicSpool:
    """Configured local public-record channel, not provider ownership evidence."""
    def __init__(self,path):
        self.db=sqlite3.connect(path,isolation_level=None)
        self.db.execute('CREATE TABLE IF NOT EXISTS records(position INTEGER PRIMARY KEY AUTOINCREMENT,digest TEXT UNIQUE NOT NULL,kind TEXT NOT NULL,bytes BLOB NOT NULL)')
    def put(self,publications):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            for item in publications:
                if item['kind'] not in ('identity','discovery') or digest(item['bytes'])!=item['digest']:raise ValueError('Public record')
                prior=self.db.execute('SELECT kind,bytes FROM records WHERE digest=?',(item['digest'],)).fetchone()
                if prior and prior!=(item['kind'],item['bytes']):raise ValueError('Public digest conflict')
                self.db.execute('INSERT OR IGNORE INTO records(digest,kind,bytes) VALUES(?,?,?)',(item['digest'],item['kind'],item['bytes']))
            self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise
    def scan(self,after,*,max_records,max_bytes):
        values=[];size=0
        for position,kind,raw in self.db.execute('SELECT position,kind,bytes FROM records WHERE position>? ORDER BY position LIMIT ?',(after,max_records)):
            if len(raw)>max_bytes:raise ValueError('Record byte limit')
            if size+len(raw)>max_bytes:break
            values.append((position,kind,raw));size+=len(raw)
        return values
    def close(self):self.db.close()

class OwnDevices:
    def __init__(self,identity,*,account,principal,local_device,mailboxes,max_records=128,max_bytes=8*1024*1024):
        self.identity=identity;self.db=identity.db
        if self.db.in_transaction:raise ValueError('Initialize outside transaction')
        if not isinstance(account,str) or not account or not isinstance(mailboxes,list) or not mailboxes or mailboxes!=sorted(set(mailboxes)):raise ValueError('Trusted account configuration')
        for mailbox in mailboxes:mailbox_syntax(mailbox)
        if not identity.current_state(principal)['head']:raise ValueError('Trusted accepted anchor required')
        if any(type(x)!=int or x<1 for x in (max_records,max_bytes)):raise ValueError('Local resource limits')
        if not isinstance(local_device,str) or not re.fullmatch(r'end0:[0-9a-f]{64}',local_device) or local_device=='end0:'+'0'*64:raise ValueError('Local device identifier')
        self.max_records=max_records;self.max_bytes=max_bytes;self.client=ClientOnboarding(identity)
        self.config=dict(account=account,principal=principal,localDevice=local_device,mailboxes=mailboxes)
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS own_account(id INTEGER PRIMARY KEY CHECK(id=1),configuration BLOB NOT NULL,publication INTEGER NOT NULL,revision INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS own_approval(id TEXT PRIMARY KEY,head TEXT NOT NULL,binding BLOB NOT NULL,result BLOB);
          CREATE TABLE IF NOT EXISTS own_outbox(digest TEXT PRIMARY KEY,kind TEXT NOT NULL,bytes BLOB NOT NULL,head TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS own_received(source TEXT NOT NULL,position INTEGER NOT NULL,digest TEXT NOT NULL,kind TEXT NOT NULL,bytes BLOB NOT NULL,PRIMARY KEY(source,position));
          CREATE TABLE IF NOT EXISTS own_cursor(source TEXT PRIMARY KEY,position INTEGER NOT NULL);
        ''')
        old=self.db.execute('SELECT configuration FROM own_account WHERE id=1').fetchone()
        if old and old[0]!=packed(self.config):raise ValueError('Different local account configuration')
        self.db.execute('INSERT OR IGNORE INTO own_account VALUES(1,?,0,0)',(packed(self.config),))
    def publication(self,*,expected_revision,enabled):
        if type(enabled)!=bool:raise ValueError('Local setting boolean')
        changed=self.db.execute('UPDATE own_account SET publication=?,revision=revision+1 WHERE id=1 AND revision=?',(int(enabled),expected_revision)).rowcount
        if changed!=1:raise ValueError('Configuration changed')
        return expected_revision+1
    def _state(self):
        current=self.identity.current_state(self.config['principal'])
        if current['conflicted']:raise ValueError('Identity conflict')
        row=self.db.execute('SELECT bundle FROM identity_transitions WHERE principal=? AND digest=? AND accepted=1',(self.config['principal'],current['head'])).fetchone()
        if row:
            bundle=decode_identity_bundle(row[0]);state=next(s['value'] for s in bundle['states'] if s['digest']==current['head']);bindings={b['digest']:b['value'] for b in bundle['bindings']}
        else:
            record=json.loads(self.db.execute('SELECT record FROM claims WHERE principal=? AND digest=?',(self.config['principal'],current['head'])).fetchone()[0]);state=json.loads(base64.b64decode(record['state']));raw=base64.b64decode(record['binding']);bindings={digest(raw):json.loads(raw)}
        return current['head'],state,bindings
    def approve(self,identifier,binding,*,expected_head):
        """Trusted local comparison/approval input; never called by ingestion.

        binding is exact proposed public device-binding payload. Actual possession,
        authorization and signing authority are verified on commit, not inferred
        from this local intent. UI/remote pairing transport is outside this API.
        """
        from event_encoding import decode_event
        value=decode_event(binding)['value']
        if value.get('principal')!=self.config['principal'] or value.get('authority')!={'kind':'state','digest':expected_head}:raise ValueError('Proposed binding account/anchor')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            head,state,_=self._state()
            if head!=expected_head:raise ValueError('Head changed')
            if value['device'] in [b['device'] for b in state['bindings']] or value['device'] in state['revoked']:raise ValueError('New device required')
            old=self.db.execute('SELECT head,binding FROM own_approval WHERE id=?',(identifier,)).fetchone()
            if old and old!=(head,binding):raise ValueError('Approval ID conflict')
            self.db.execute('INSERT OR IGNORE INTO own_approval VALUES(?,?,?,NULL)',(identifier,head,binding));self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise
    def _outbox(self,kind,raw,head):
        count,size=self.db.execute('SELECT count(*),coalesce(sum(length(bytes)),0) FROM own_outbox').fetchone()
        if not self.db.execute('SELECT 1 FROM own_outbox WHERE digest=?',(digest(raw),)).fetchone() and (count>=self.max_records or size+len(raw)>self.max_bytes):raise ValueError('Publication retention budget')
        self.db.execute('INSERT OR IGNORE INTO own_outbox VALUES(?,?,?,?)',(digest(raw),kind,raw,head))
    def commit_enrollment(self,identifier,bundle,*,candidate_digest,time,crash=None):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            result=self._commit_enrollment_locked(identifier,bundle,candidate_digest=candidate_digest,time=time,crash=crash)
            self.db.execute('COMMIT');return result
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def _commit_enrollment_locked(self,identifier,bundle,*,candidate_digest,time,crash=None):
        """Caller owns the transaction, including any pairing receipt/outbox."""
        if not self.db.in_transaction:raise ValueError('Caller transaction required')
        MlsReceive._policy(time,'allow-unverified');decoded=decode_identity_bundle(bundle)
        if decoded['principal']!=self.config['principal']:raise ValueError('Account mismatch')
        candidate=next((s for s in decoded['states'] if s['digest']==candidate_digest),None)
        if not candidate:raise ValueError('Candidate missing')
        approval=self.db.execute('SELECT head,binding,result FROM own_approval WHERE id=?',(identifier,)).fetchone()
        if not approval:raise ValueError('Trusted approval required')
        if approval[2]:
            prior=json.loads(approval[2])
            if prior['bundle']!=digest(bundle):raise ValueError('Enrollment retry conflict')
            return prior
        head,old,_=self._state();new=candidate['value'];binding=json.loads(approval[1])
        if head!=approval[0] or new['previous']!=[head]:raise ValueError('Approval head changed')
        expected=sorted(old['bindings']+[{'device':binding['device'],'digest':digest(approval[1])}],key=lambda r:r['device'])
        if new['bindings']!=expected or new['revoked']!=old['revoked'] or new['signer']!=self.config['localDevice']:raise ValueError('Exact approved enrollment required')
        match=next((b for b in decoded['bindings'] if b['digest']==digest(approval[1])),None)
        if not match or match['octets']!=approval[1]:raise ValueError('Approved binding bytes')
        result=self.identity._accept_locked(bundle,self.config['principal'],candidate,time)
        if result['status']!='accepted-unverified':raise ValueError('Enrollment not accepted: '+result['status'])
        result=dict(result,bundle=digest(bundle),publication='queued',historyTransferred=False)
        self._outbox('identity',bundle,candidate_digest)
        self.db.execute('UPDATE own_approval SET result=? WHERE id=?',(packed(result),identifier))
        if crash:crash('before-commit')
        return result
    def publish_device(self,wire,*,time):
        """Queue this device's original ordinary-mail discovery only."""
        extraction=extract_discovery(wire,max_wire_bytes=self.max_bytes,max_parts=self.max_records)
        if extraction['state']!='candidate':raise ValueError('One direct discovery required')
        d=decode_passive_discovery(extraction['octets']);v=d['assertion']['value']
        if (v['principal'],v['device'])!=(self.config['principal'],self.config['localDevice']) or v['mailbox'] not in self.config['mailboxes']:raise ValueError('Own device/exact mailbox only')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            checked=verify_passive_discovery_locked(extraction['octets'],self.identity,time=time,trust_policy='allow-unverified')
            if checked['status']!='snapshot-authorized-unverified':raise ValueError('Current self evidence required')
            # Only public signed discovery is distributed. Never copy unrelated
            # source body/attachments into an own-device publication channel.
            from email.message import EmailMessage
            from email import policy
            public=EmailMessage(policy=policy.SMTP);public['From']=v['mailbox'];public.set_content('Own-device public capability evidence.')
            public.add_attachment(extraction['octets'],maintype='application',subtype=MEDIA_TYPE.split('/')[1],cte='base64')
            public.set_boundary('own-discovery-'+digest(extraction['octets']))
            octets=public.as_bytes();self._outbox('discovery',octets,checked['head']);self.db.execute('COMMIT');return digest(octets)
        except BaseException:self.db.execute('ROLLBACK');raise
    def publications(self,*,time):
        """Explicit configured-channel handoff, no network and no private state."""
        self.db.execute('BEGIN')
        try:
            enabled,revision=self.db.execute('SELECT publication,revision FROM own_account').fetchone();head,_,_=self._state()
            result=[]
            if enabled:
                for ident,kind,raw,record_head in self.db.execute('SELECT digest,kind,bytes,head FROM own_outbox ORDER BY digest'):
                    if kind=='discovery':
                        if record_head!=head:continue
                        extracted=extract_discovery(raw,max_wire_bytes=self.max_bytes,max_parts=self.max_records)
                        if verify_passive_discovery_locked(extracted['octets'],self.identity,time=time,trust_policy='allow-unverified')['status']!='snapshot-authorized-unverified':continue
                    result.append(dict(digest=ident,kind=kind,bytes=raw,configurationRevision=revision))
            self.db.execute('COMMIT');return result
        except BaseException:self.db.execute('ROLLBACK');raise
    def ingest(self,source,records,*,time,crash=None):
        """Local source records: (monotone position, identity|discovery, bytes).

        This envelope is a local adapter API, not a new network wire format.
        All received identity evidence must trace to the preconfigured anchor.
        """
        MlsReceive._policy(time,'allow-unverified')
        if not isinstance(source,str) or not source or len(records)>self.max_records or sum(len(r[2]) for r in records)>self.max_bytes:raise ValueError('Source/batch limit')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            cursor=self.db.execute('SELECT position FROM own_cursor WHERE source=?',(source,)).fetchone();cursor=cursor[0] if cursor else 0
            for pos,kind,raw in records:
                if type(pos)!=int or pos<1 or kind not in ('identity','discovery') or not isinstance(raw,bytes):raise ValueError('Local source record')
                previous=self.db.execute('SELECT digest,kind FROM own_received WHERE source=? AND position=?',(source,pos)).fetchone()
                if previous:
                    if previous!=(digest(raw),kind):raise ValueError('Source position collision')
                    continue
                if pos<=cursor:raise ValueError('Source cursor order')
                if kind=='identity':bundle=decode_identity_bundle(raw)
                else:
                    extraction=extract_discovery(raw,max_wire_bytes=self.max_bytes,max_parts=self.max_records)
                    if extraction['state']!='candidate':raise ValueError('Discovery source')
                    d=decode_passive_discovery(extraction['octets']);bundle=d['identity']
                if bundle['principal']!=self.config['principal']:raise ValueError('Own-account source mismatch')
                # Accepted trust anchor is never installed from source input.
                for state in sorted(bundle['states'],key=lambda s:int(s['value']['revision'])):
                    if state['value']['revision']=='0':continue
                    outcome=self.identity._accept_locked(bundle['octets'],bundle['principal'],state,time)
                    if outcome['status'] not in ('accepted-unverified','already-recorded','conflicted'):raise ValueError('Identity evidence unresolved')
                if kind=='discovery':
                    v=d['assertion']['value']
                    if v['mailbox'] not in self.config['mailboxes']:raise ValueError('Unconfigured own mailbox')
                    # Reuse the normal observation authority/collision boundary.
                    checked=verify_passive_discovery_locked(extraction['octets'],self.identity,time=time,trust_policy='allow-unverified')
                    if checked['status']=='snapshot-authorized-unverified':
                        b=next(b['value'] for b in d['identity']['bindings'] if b['digest']==v['binding'])
                        self.client.associations._observe_validated_batch_locked([dict(assertion=d['assertion']['octets'],signature=d['signature'],signingKey=bytes.fromhex(b['signingKey']),outerFrom=[v['mailbox']],sourceId=digest(raw),parserRevision='own-source-v0',observedAt=time['earliest'])])
                        association=self.client.associations._current(v['mailbox'])
                        if not association:
                            self.client.associations._decide_locked(decision_id=digest(raw)[:32],mailbox=v['mailbox'],expected_generation=None,kind='first-contact',principal=self.config['principal'],actor='configured-policy',policy_revision='own-account-v0',trust_policy='allow-unverified',time=time)
                        self.db.execute('INSERT OR IGNORE INTO onboarding_sources VALUES(?,?)',(digest(raw),raw))
                count,size=self.db.execute('SELECT count(*),coalesce(sum(length(bytes)),0) FROM own_received').fetchone()
                if count>=self.max_records or size+len(raw)>self.max_bytes:raise ValueError('Source retention budget')
                self.db.execute('INSERT INTO own_received VALUES(?,?,?,?,?)',(source,pos,digest(raw),kind,raw));cursor=pos
            self.db.execute('INSERT INTO own_cursor VALUES(?,?) ON CONFLICT(source) DO UPDATE SET position=excluded.position',(source,cursor))
            if crash:crash('before-commit')
            self.db.execute('COMMIT');return self.identity.current_state(self.config['principal'])
        except BaseException:self.db.execute('ROLLBACK');raise
    def sync_from(self,source,spool,*,time,crash=None):
        row=self.db.execute('SELECT position FROM own_cursor WHERE source=?',(source,)).fetchone()
        records=spool.scan(row[0] if row else 0,max_records=self.max_records,max_bytes=self.max_bytes)
        return self.ingest(source,records,time=time,crash=crash)

    def snapshot(self,*,time,application=None,ordering=None):
        """Complete relative to accepted head, not proof of global freshness.

        Existing target planners recheck exact routing/evidence. This display
        snapshot is explicitly not a send authorization or membership grant.
        """
        before=self.identity.current_state(self.config['principal']);plans=[]
        for mailbox in self.config['mailboxes']:
            plans.append(self.client.targets(mailbox,target_policy='all-authorized-devices',time=time,mode='automatic-unverified-continuity'))
        self.db.execute('BEGIN')
        try:
            head,state,bindings=self._state()
            if head!=before['head']:raise ValueError('Snapshot head changed')
            required=[]
            for ref in state['bindings']:
                b=bindings.get(ref['digest'])
                if not b:raise ValueError('Incomplete binding inventory')
                if 'receive' in b['roles']:required.append(ref['device'])
            chosen={}
            for plan in plans:
                if plan.get('principal') not in (None,self.config['principal']):raise ValueError('Own mailbox associated with another principal')
                if plan.get('head') not in (None,head):raise ValueError('Snapshot head changed')
                for entry in plan.get('selected',[]):
                    decoded=decode_passive_discovery(entry['wrapper']);value=decoded['assertion']['value']
                    association=self.client.associations._current(entry['mailbox'])
                    eligible=self.client.associations.eligible_observation_locked(entry['mailbox'],entry['digest'],time)
                    if not association or not association['enabled'] or association['generation']!=entry['generation'] or association['principal']!=self.config['principal'] or not eligible:raise ValueError('Snapshot association changed')
                    if verify_passive_discovery_locked(entry['wrapper'],self.identity,time=time,trust_policy='allow-unverified')['status']!='snapshot-authorized-unverified':raise ValueError('Snapshot evidence changed')
                    if application is not None:
                        from application_support import supports
                        if not supports(value,application,ordering):continue
                    device=value['device'];chosen.setdefault(device,entry)
            missing=sorted(set(required)-set(chosen));selected=[chosen[d] for d in sorted(chosen)]
            public=dict(account=self.config['account'],principal=self.config['principal'],head=head,required=sorted(required),missing=missing,revoked=state['revoked'],freshness='cached-continuity',packageValidation='required-at-admission',completeRelativeToHead=not missing,mailboxOwnershipVerified=False,sendAuthorized=False)
            token=digest(packed(dict(public,evidence=[dict(digest=e['digest'],mailbox=e['mailbox'],generation=e['generation']) for e in selected])))
            self.db.execute('COMMIT');return dict(public,snapshot=token,selected=selected)
        except BaseException:self.db.execute('ROLLBACK');raise
