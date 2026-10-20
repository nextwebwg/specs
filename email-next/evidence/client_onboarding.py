"""Local human-mail bootstrap. No network, provider authority or ownership claim."""
import base64,hashlib,json,uuid
from email import policy
from email.parser import BytesParser
from discovery_mime import extract_discovery
from event_encoding import encode_event
from passive_discovery import decode_passive_discovery,mailbox_syntax,uint64
from passive_discovery_verify import verify_passive_discovery_locked
from mailbox_association_store import MailboxAssociationStore

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'))

class ClientOnboarding:
    def __init__(self,identity):
        self.identity=identity;self.db=identity.db;self.associations=MailboxAssociationStore(identity)
        self.db.executescript('''CREATE TABLE IF NOT EXISTS onboarding_ingestion(id TEXT PRIMARY KEY,request TEXT NOT NULL,result TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS onboarding_sources(digest TEXT PRIMARY KEY,wire BLOB NOT NULL);''')
    def _install_identity(self,decoded,time):
        bundle=decoded['identity'];principal=bundle['principal']
        roots=[s for s in bundle['states'] if s['value'].get('revision')=='0']
        for root in roots:
            pinned=self.db.execute('SELECT digest FROM pins WHERE principal=?',(principal,)).fetchone()
            if pinned and pinned[0]==root['digest']:continue
            refs=root['value'].get('bindings',[])
            binding=next((b for b in bundle['bindings'] if b['digest'] in [r['digest'] for r in refs]),None)
            if not binding:raise ValueError('Genesis binding missing')
            record=dict(state=base64.b64encode(root['octets']).decode(),binding=base64.b64encode(binding['octets']).decode(),stateProof=root['signature'],authorization=binding['authorization'],possession=binding['possession'],time=time)
            result=self.identity._observe_locked(record,first_contact_policy='allow-unverified')
            if result['status'] not in ('pinned-unverified','unlinked-claim'):raise ValueError('Genesis not eligible')
        for state in sorted(bundle['states'],key=lambda s:int(s['value'].get('revision','0'))):
            if state['value'].get('revision')!='0':self.identity._accept_locked(bundle['octets'],principal,state,time)

    def _install(self,decoded,time):
        self._install_identity(decoded,time)
        return verify_passive_discovery_locked(decoded['octets'],self.identity,time=time,trust_policy='allow-unverified')
    def ingest(self,request_id,messages,*,mode,target_policy,policy_revision,time,crash=None,max_wire_bytes=2097152,max_parts=64,max_messages=32,max_total_bytes=8388608):
        if mode not in ('automatic-unverified-continuity','verification-required') or target_policy not in ('evidenced-devices','all-authorized-devices'):raise ValueError('Explicit onboarding policies required')
        if not isinstance(request_id,str) or not request_id or not isinstance(policy_revision,str) or not policy_revision:raise ValueError('Local decision identity required')
        if not isinstance(time,dict) or set(time)!={'earliest','latest'} or uint64(time['earliest'])>uint64(time['latest']):raise ValueError('Credible clock interval required')
        if not isinstance(messages,list) or not messages or any(not isinstance(m,bytes) for m in messages):raise ValueError('Original messages required')
        if any(type(v) is not int or v<1 for v in (max_wire_bytes,max_parts,max_messages,max_total_bytes)) or len(messages)>max_messages or sum(map(len,messages))>max_total_bytes:raise ValueError('Local ingestion bounds')
        request=canonical(dict(messages=[hashlib.sha256(m).hexdigest() for m in messages],mode=mode,targetPolicy=target_policy,policyRevision=policy_revision,time=time,maxWireBytes=max_wire_bytes,maxParts=max_parts,maxMessages=max_messages,maxTotalBytes=max_total_bytes))
        self.db.execute('BEGIN IMMEDIATE')
        try:
            prior=self.db.execute('SELECT request,result FROM onboarding_ingestion WHERE id=?',(request_id,)).fetchone()
            if prior:
                if prior[0]!=request:raise ValueError('Immutable ingestion conflict')
                self.db.execute('COMMIT');return json.loads(prior[1])
            candidates=[];diagnostics=[];known_identity_updates=[]
            for wire in messages:
                digest=hashlib.sha256(wire).hexdigest();retained=self.db.execute('SELECT wire FROM onboarding_sources WHERE digest=?',(digest,)).fetchone()
                if retained and retained[0]!=wire:raise ValueError('Source digest collision')
                self.db.execute('INSERT OR IGNORE INTO onboarding_sources VALUES(?,?)',(digest,wire))
                selected=extract_discovery(wire,max_wire_bytes=max_wire_bytes,max_parts=max_parts)
                if selected['state']!='candidate':diagnostics.append(dict(source=digest,state=selected['state']));continue
                self.db.execute('SAVEPOINT candidate')
                try:
                    parsed=BytesParser(policy=policy.default).parsebytes(wire);headers=parsed.get_all('From',[])
                    if len(headers)!=1 or headers[0].defects or len(headers[0].addresses)!=1:raise ValueError('Sole From required')
                    address=headers[0].addresses[0];mailbox=address.username+'@'+address.domain.lower()
                    if mailbox_syntax(mailbox)!='syntax-valid':raise ValueError('Mailbox spelling unsupported')
                    decoded=decode_passive_discovery(selected['octets']);assertion=decoded['assertion']['value']
                    if assertion['mailbox']!=mailbox:raise ValueError('From mismatch')
                    known=self.identity.current_state(assertion['principal'])['head'] is not None
                    self._install_identity(decoded,time)
                    if known:known_identity_updates.append(decoded)
                    checked=verify_passive_discovery_locked(decoded['octets'],self.identity,time=time,trust_policy='allow-unverified')
                    if checked['status']!='snapshot-authorized-unverified':raise ValueError('Evidence not current and authorized')
                    candidates.append((digest,decoded,mailbox))
                except ValueError as error:diagnostics.append(dict(source=digest,state='held',reason=str(error)))
                finally:self.db.execute('ROLLBACK TO candidate');self.db.execute('RELEASE candidate')
            # Valid existing-principal transitions have authority independently of
            # whether their accompanying advertisement is usable or current.
            for decoded in known_identity_updates:self._install_identity(decoded,time)
            outcomes=[]
            for mailbox in sorted({c[2] for c in candidates}):
                batch=[c for c in candidates if c[2]==mailbox];principals={c[1]['assertion']['value']['principal'] for c in batch}
                current=self.associations._current(mailbox)
                if not current and len(principals)>1:outcomes.append(dict(mailbox=mailbox,status='ambiguous'));continue
                if mode=='verification-required':outcomes.append(dict(mailbox=mailbox,status='verification-required'));continue
                selected=[c for c in batch if not current or c[1]['assertion']['value']['principal']==current['principal']]
                if not selected:outcomes.append(dict(mailbox=mailbox,status='unlinked-claim'));continue
                # A first-contact batch with divergent genesis for one principal is ambiguous too.
                roots={s['digest'] for c in selected for s in c[1]['identity']['states'] if s['value'].get('revision')=='0'}
                if not current and len(roots)>1:outcomes.append(dict(mailbox=mailbox,status='ambiguous'));continue
                self.db.execute('SAVEPOINT selection')
                try:
                    for digest,decoded,_ in selected:
                        checked=self._install(decoded,time)
                        if checked['status']!='snapshot-authorized-unverified':raise ValueError('Changed authority')
                        v=decoded['assertion']['value'];binding=next(b for b in decoded['identity']['bindings'] if b['digest']==v['binding'])
                        self.associations._observe_validated_batch_locked([dict(assertion=decoded['assertion']['octets'],signature=decoded['signature'],signingKey=bytes.fromhex(binding['value']['signingKey']),outerFrom=[mailbox],sourceId=digest,parserRevision='python-email-passive-v0',observedAt=time['earliest'])])
                    if crash:crash('before-association')
                    result=self.associations._decide_locked(decision_id=uuid.uuid4().hex,mailbox=mailbox,expected_generation=current['generation'] if current else None,kind='first-contact',principal=selected[0][1]['assertion']['value']['principal'],actor='configured-policy',policy_revision=policy_revision,trust_policy='allow-unverified',time=time)
                    outcomes.append(dict(mailbox=mailbox,**result))
                    self.db.execute('RELEASE selection')
                except ValueError as error:
                    self.db.execute('ROLLBACK TO selection');self.db.execute('RELEASE selection')
                    outcomes.append(dict(mailbox=mailbox,status='held',reason=str(error)))
            result=dict(outcomes=outcomes,diagnostics=diagnostics,identityVerified=False,targetPolicy=target_policy)
            self.db.execute('INSERT INTO onboarding_ingestion VALUES(?,?,?)',(request_id,request,canonical(result)));self.db.execute('COMMIT');return result
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def targets(self,mailbox,*,target_policy,time,mode):
        """Snapshot target plan; invitation/release must independently recheck it."""
        if target_policy not in ('evidenced-devices','all-authorized-devices') or mode not in ('automatic-unverified-continuity','verification-required'):raise ValueError('Explicit policies required')
        self.db.execute('BEGIN')
        try:
            association=self.associations._current(mailbox)
            if not association or not association['enabled']:result=dict(status='pending',reason='association')
            else:
                verification=None
                if mode=='verification-required':
                    from human_verification import resolve_locked
                    verification=resolve_locked(self.identity,mailbox,association['principal'],time)
                    if verification['status']!='verified-for-use':
                        self.db.execute('COMMIT');return verification
                principal=association['principal'];current=self.identity.current_state(principal);head=current['head']
                if current['conflicted']:raise ValueError('Identity conflict')
                transition=self.db.execute('SELECT bundle FROM identity_transitions WHERE principal=? AND digest=? AND accepted=1',(principal,head)).fetchone()
                if transition:
                    from identity_bundle import decode_identity_bundle
                    bundle=decode_identity_bundle(transition[0]);state=next(s['value'] for s in bundle['states'] if s['digest']==head);bindings={b['digest']:b['value'] for b in bundle['bindings']}
                else:
                    record=json.loads(self.db.execute('SELECT record FROM claims WHERE principal=? AND digest=?',(principal,head)).fetchone()[0]);state=json.loads(base64.b64decode(record['state']));raw=base64.b64decode(record['binding']);bindings={hashlib.sha256(raw).hexdigest():json.loads(raw)}
                required=[]
                for ref in state['bindings']:
                    binding=bindings.get(ref['digest'])
                    if binding is None:raise ValueError('Incomplete current roster evidence')
                    if 'receive' in binding['roles'] and ref['device'] not in state['revoked']:required.append(ref['device'])
                choices={}
                for (digest,) in self.db.execute('SELECT digest FROM mailbox_observations WHERE mailbox=?',(mailbox,)):
                    evidence=self.associations.eligible_observation_locked(mailbox,digest,time)
                    if not evidence or evidence['assertion']['principal']!=principal:continue
                    for (wire,) in self.db.execute('SELECT wire FROM onboarding_sources ORDER BY digest'):
                        extracted=extract_discovery(wire,max_wire_bytes=len(wire),max_parts=64)
                        if extracted['state']!='candidate':continue
                        decoded=decode_passive_discovery(extracted['octets'])
                        if decoded['assertion']['digest']==digest and decoded['assertion']['key_package_octets'] is not None and verify_passive_discovery_locked(extracted['octets'],self.identity,time=time,trust_policy='allow-unverified')['status']=='snapshot-authorized-unverified':
                            device=decoded['assertion']['value']['device'];choices.setdefault(device,[]).append(dict(wrapper=extracted['octets'],mailbox=mailbox,generation=association['generation'],digest=digest))
                # Several independent usable packages are not resolved by arrival time.
                selected=[sorted({c['digest']:c for c in options}.values(),key=lambda c:c['digest'])[0] for device,options in sorted(choices.items()) if device in required]
                included=sorted(d for d in choices if d in required);missing=sorted(set(required)-set(included))
                result=dict(status=('ready-verified' if verification else 'ready-unverified') if included and (not missing or target_policy=='evidenced-devices') else 'pending',principal=principal,head=head,devices=included,missingDevices=missing,allAuthorizedDevicesIncluded=not missing,selected=selected,targetPolicy=target_policy,identityVerified=verification is not None)
                if verification:result['verification']=verification
            self.db.execute('COMMIT');return result
        except BaseException:
            self.db.execute('ROLLBACK');raise
