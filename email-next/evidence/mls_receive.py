"""Single-database staged receive experiment; no external effects or networking.

Checkpoint is secret-bearing local storage. Never log worker requests/responses.
Only pre-established current-epoch groups; admission and handshake excluded.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from contribution_journal import ContributionJournal
from application_agreement import ApplicationAgreement
import membership_episodes as episodes
import group_instances as instances
import secret_retention as retention
from event_encoding import decode_event
from mls_contribution import check
from passive_discovery import uint64
from journal_button_view import derive_button_view
from journal_reaction_view import derive_reaction_view
MAX=16*1024*1024
FORMAT='openmls-0.9.1-map-0'

def worker_call(binary,request,timeout=10):
    payload=json.dumps(request,separators=(',',':')).encode()
    if len(payload)>MAX:raise ValueError('Worker input bound')
    # Pinned worker bounds output before writing. File keeps secret stdout out of
    # logs and bounds memory; size is checked before parsing. Not an arbitrary CLI.
    with tempfile.TemporaryFile() as output:
        try:
            result=subprocess.run([str(binary)],input=payload,stdout=output,stderr=subprocess.DEVNULL,timeout=timeout,check=False)
        except subprocess.TimeoutExpired:raise RuntimeError('Worker timeout') from None
        if result.returncode or output.tell()>MAX:raise RuntimeError('Worker failed or output bound')
        output.seek(0);raw=output.read(MAX+1)
    return json.loads(raw)

class LockedIdentity:
    def __init__(self,identity):self.identity=identity
    def check_device(self,credential,key,*,role,time,trust_policy):
        if len(credential)!=85 or credential[:21]!=b'email-next/device/v0\0':return {'status':'invalid'}
        return self.identity._check_device_locked('enp0:'+credential[21:53].hex(),'end0:'+credential[53:].hex(),key,role,time,trust_policy)

class MlsReceive:
    def __init__(self,identity,binary,*,verification_mechanism=None):
        if verification_mechanism not in (None,'human-comparison-v0'):raise ValueError('Verification mechanism')
        self.verification_mechanism=verification_mechanism
        self.identity=identity;self.db=identity.db;self.binary=Path(binary)
        if self.db.in_transaction:raise ValueError('Initialize outside transaction')
        episodes.initialize(self.db)
        import quorum_admission
        quorum_admission.initialize(self.db)
        retention.initialize(self.db)
        self.journal=ContributionJournal(connection=self.db)
        self.application_agreement=ApplicationAgreement(self.db)
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS mls_configured_context(group_id TEXT PRIMARY KEY, mode TEXT NOT NULL CHECK(mode='configured-endpoint-v0'));
          CREATE TABLE IF NOT EXISTS mls_edit_sources(digest TEXT PRIMARY KEY,credential TEXT NOT NULL,origin TEXT,carrier TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS mls_checkpoint(id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL, format TEXT NOT NULL, group_id TEXT NOT NULL, snapshot BLOB NOT NULL);
          CREATE TABLE IF NOT EXISTS mls_application_acceptance(digest TEXT PRIMARY KEY, state TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS mls_received_resource_roles(digest TEXT NOT NULL,position INTEGER NOT NULL,role TEXT NOT NULL,media_type TEXT,PRIMARY KEY(digest,position));
          CREATE TABLE IF NOT EXISTS mls_received_resources(digest TEXT NOT NULL,position INTEGER NOT NULL,cid TEXT NOT NULL,bytes BLOB NOT NULL,PRIMARY KEY(digest,position));
          CREATE TABLE IF NOT EXISTS mls_received_payloads(digest TEXT PRIMARY KEY,payload BLOB NOT NULL,representation TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS mls_receives(digest TEXT PRIMARY KEY, wire BLOB NOT NULL, revision INTEGER NOT NULL, application BLOB NOT NULL, evidence BLOB NOT NULL, result TEXT NOT NULL);
        ''')
    def configured_endpoint_ordering(self,group):
        return self.db.execute("SELECT 1 FROM mls_configured_context WHERE group_id=? AND mode='configured-endpoint-v0'",(group,)).fetchone() is not None

    def configured_quorum_ordering(self,group,context=None):
        from quorum_admission import accepted
        return accepted(self.db,group,context)

    def configured_application(self,group,members,*,instance=None):
        roster=[dict(identity=m.split(':')[1],key=m.split(':')[2]) for m in members]
        if instance is None:
            current=instances.optional_current(self.db,group)
            if current:instance=current['instance']
        return self.application_agreement.resolve(group,roster,instance=instance)

    def install_fixture(self,group,checkpoint):
        """Explicit trusted test setup only; does not admit a network invitation."""
        raw=json.dumps(checkpoint).encode()
        if len(raw)>MAX:raise ValueError('Checkpoint bound')
        self.db.execute('INSERT INTO mls_checkpoint VALUES(1,0,?,?,?)',(FORMAT,group,raw))
    def _identity_authority(self):
        if self.verification_mechanism=='human-comparison-v0':
            from human_verification import HumanVerifiedIdentity
            return HumanVerifiedIdentity(self.identity)
        return LockedIdentity(self.identity)

    def reevaluate(self,*,time,trust_policy):
        """Reconsider retained plaintext evidence, never rerun MLS or release effects."""
        self._policy(time,trust_policy)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            result=self._reevaluate_locked(dict(time),trust_policy)
            self.db.execute('COMMIT');return result
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise

    @staticmethod
    def _policy(time,trust_policy):
        if trust_policy not in ('allow-unverified','require-verification'):raise ValueError('Explicit policy required')
        if not isinstance(time,dict) or set(time)!={'earliest','latest'} or uint64(time['earliest'])>uint64(time['latest']):
            raise ValueError('Valid local time interval required')

    def _reevaluate_locked(self,time,trust_policy):
        rows=self.db.execute('SELECT digest,application,evidence,result FROM mls_receives ORDER BY revision').fetchmany(4097)
        if len(rows)>4096 or sum(len(r[1])+len(r[2]) for r in rows)>MAX:return {'status':'incomplete','reason':'record-budget'}
        candidates={};groups={};states={}
        previous=dict(self.db.execute('SELECT digest,state FROM mls_application_acceptance'))
        for received_digest,raw,evidence,original in rows:
            digest=hashlib.sha256(raw).hexdigest()
            if digest in candidates:continue
            try:event=decode_event(raw)['value']
            except ValueError:continue
            if not isinstance(event.get('operation'),dict) or event['operation'].get('kind') not in ('message','question','answer','hosted-holder-observation','reaction','reaction-withdraw','attachment-message','rich-message','service-question','edit'):continue
            e=json.loads(evidence);p=e['processed'];snap=e['snapshot']
            # Accepted history is not retroactively revoked. Every promotion from
            # pending still uses current identity authority inside this transaction.
            historical=previous.get(digest)=='accepted'
            origin=instances.receive_origin(self.db,received_digest,p['group'])
            present=instances.optional_current(self.db,p['group'])
            if not historical and present and (present['status']!='active' or origin!=present['instance']):
                states[digest]='held:membership-instance';continue
            e['instance']=origin
            if not historical and not episodes.permits_processed(self.db,p,snap):
                states[digest]='held:membership-episode';continue
            outcome=check(raw,p['group'],p['epoch'],p['sender'],p['credential'],p['aad'],snap['group'],snap['epoch'],snap['context'],snap['members'],
                identity_store=None if historical else self._identity_authority(),time=time,trust_policy=trust_policy,configured_endpoint_ordering=self.configured_endpoint_ordering(p['group']),configured_quorum_ordering=self.configured_quorum_ordering(p['group']),configured_application=self.configured_application(p['group'],snap['members'],instance=origin))
            if outcome not in ('projected-context-matched','pending'):
                states[digest]='held:'+outcome
                continue
            ref={k:event[k] for k in ('conversation','principal','event')}
            key=tuple(ref[k] for k in ('conversation','principal','event'))
            candidates[digest]=dict(raw=raw,event=event,reference=ref,proof=e,historical=historical)
            groups.setdefault(key,[]).append(digest)
        records=[];answer_candidates=[];questions={}
        # Existing journal history participates in reference resolution. Its
        # exact variants also prevent a late candidate hiding a known collision.
        conversations={c['event']['conversation'] for c in candidates.values()}
        indexed={}
        for conversation in conversations:
            for record in self.journal.snapshot(conversation):
                key=tuple(record['reference'][k] for k in ('conversation','principal','event'))
                indexed[key]={'reference':record['reference'],'state':'conflict' if record['state']=='conflict' else 'valid'}
                if record['state']=='recorded':indexed[key]['event']=decode_event(record['octets'][0])['value']
        for key,digests in groups.items():
            c=candidates[digests[0]];existing=indexed.get(key)
            collision=len(digests)>1 or (existing and existing['state']=='conflict')
            if existing and existing['state']=='valid':
                stored=self.db.execute('SELECT octets FROM contributions WHERE conversation=? AND principal=? AND event=?',key).fetchall()
                collision=collision or any(row[0]!=c['raw'] for row in stored)
            if collision:
                indexed[key]={'reference':c['reference'],'state':'conflict'}
                for digest in digests:
                    states[digest]='conflict';item=candidates[digest]
                    self.journal.append_validated_in_transaction(item['raw'],item['reference'])
                if c['event']['operation']['kind']=='question':questions[key]=c['reference']
                continue
            indexed[key]={'reference':c['reference'],'state':'valid','event':c['event']}
            kind=c['event']['operation']['kind'];digest=digests[0]
            if kind in ('message','question','attachment-message','rich-message','service-question') or c['historical']:
                self.journal.append_validated_in_transaction(c['raw'],c['reference']);states[digest]='accepted'
                if kind=='question':questions[key]=c['reference']
            if kind=='answer' and not c['historical']:
                p=c['proof']['processed'];snap=c['proof']['snapshot']
                answer_candidates.append(dict(digest=digest,reference=c['reference'],credential=p['credential'],context=decode_event(bytes.fromhex(snap['context']))['value'],members=[m.split(':')[1] for m in snap['members']],options=dict(configuredEndpointOrdering=self.configured_endpoint_ordering(p['group']),configuredQuorumOrdering=self.configured_quorum_ordering(p['group']),configuredApplication=self.configured_application(p['group'],snap['members'],instance=c['proof'].get('instance')))))
        if answer_candidates:
            request=json.dumps({'records':list(indexed.values()),'candidates':answer_candidates})
            if len(request.encode())>MAX:raise ValueError('Application snapshot bound')
            result=subprocess.run(['node',str(Path(__file__).with_name('reevaluate-mls-answers.mjs'))],input=request,text=True,capture_output=True,check=True,timeout=10)
            for row in json.loads(result.stdout):
                digest=row['digest'];state=row['result']['state'];c=candidates[digest]
                states[digest]='accepted' if state=='prepared' else state
                if state=='prepared':self.journal.append_validated_in_transaction(c['raw'],c['reference'])
        # Edit graph evaluation sees authenticated candidates together, but roots
        # and historical dependencies come only from accepted/local-author history.
        from journal_edit_view import records_locked,view as edit_view,EditSnapshotBudget
        pending=[];edit_records={};edit_blocked=set()
        for digest,c in candidates.items():
            if c['event']['operation']['kind']!='edit':continue
            try:edit_history=records_locked(self,c['event']['conversation'])
            except EditSnapshotBudget:edit_blocked.add(c['event']['conversation']);continue
            for record in edit_history:
                key=tuple(record['reference'][k] for k in ('conversation','principal','event'));edit_records[key]=record
        for digest,c in candidates.items():
            if c['event']['operation']['kind']!='edit' or c['historical'] or states.get(digest)=='conflict':continue
            if c['event']['conversation'] in edit_blocked:states[digest]='incomplete';continue
            key=tuple(c['reference'][k] for k in ('conversation','principal','event'))
            edit_records[key]=dict(reference=c['reference'],state='valid',event=c['event'])
            p=c['proof']['processed'];snap=c['proof']['snapshot']
            pending.append(dict(digest=digest,reference=c['reference'],credential=p['credential'],context=decode_event(bytes.fromhex(snap['context']))['value'],members=[m.split(':')[1] for m in snap['members']],options=dict(configuredEndpointOrdering=self.configured_endpoint_ordering(p['group']),configuredQuorumOrdering=self.configured_quorum_ordering(p['group']),configuredApplication=self.configured_application(p['group'],snap['members'],instance=c['proof'].get('instance')))))
        if pending:
            request=json.dumps(dict(records=list(edit_records.values()),candidates=pending))
            if len(request.encode())>MAX:raise ValueError('Edit snapshot bound')
            result=subprocess.run(['node',str(Path(__file__).with_name('reevaluate-mls-edits.mjs'))],input=request,text=True,capture_output=True,check=True,timeout=10)
            for row in json.loads(result.stdout):
                digest=row['digest'];state=row['result']['state'];c=candidates[digest]
                states[digest]='accepted' if state=='prepared' else state
                if state=='prepared':
                    self.journal.append_validated_in_transaction(c['raw'],c['reference'])
                    self.db.execute('INSERT OR IGNORE INTO mls_edit_sources VALUES(?,?,?,?)',(digest,c['proof']['processed']['credential'],c['proof'].get('instance'),json.dumps(c['proof'],sort_keys=True)))
        roots={}
        for c in candidates.values():
            if c['event']['operation']['kind']=='edit':
                root=c['event']['operation']['root'];roots[json.dumps(root,sort_keys=True)]=root
        for root in roots.values():edit_view(self,root)
        # Reactions resolve only fully accepted history, never the intermediate
        # answer candidate index. Admit additions before withdrawals so delivery
        # order does not prevent a complete withdrawal in this same transaction.
        for reaction_kind in ('reaction','reaction-withdraw'):
            pending=[];history={}
            for digest,c in candidates.items():
                if c['event']['operation']['kind']!=reaction_kind or c['historical'] or states.get(digest)=='conflict':continue
                for record in self.journal.snapshot(c['event']['conversation']):
                    ref=record['reference'];key=tuple(ref[k] for k in ('conversation','principal','event'))
                    row=dict(reference=ref,state='conflict' if record['state']=='conflict' else 'valid')
                    if record['state']=='recorded':row['event']=decode_event(record['octets'][0])['value']
                    history[key]=row
                p=c['proof']['processed'];snap=c['proof']['snapshot']
                pending.append(dict(digest=digest,event=c['event'],reference=c['reference'],credential=p['credential'],context=decode_event(bytes.fromhex(snap['context']))['value'],members=[m.split(':')[1] for m in snap['members']],options=dict(configuredEndpointOrdering=self.configured_endpoint_ordering(p['group']),configuredQuorumOrdering=self.configured_quorum_ordering(p['group']),configuredApplication=self.configured_application(p['group'],snap['members'],instance=c['proof'].get('instance')))))
            if pending:
                request=json.dumps(dict(records=list(history.values()),candidates=pending))
                if len(request.encode())>MAX:raise ValueError('Application snapshot bound')
                result=subprocess.run(['node',str(Path(__file__).with_name('reevaluate-mls-reactions.mjs'))],input=request,text=True,capture_output=True,check=True,timeout=10)
                for row in json.loads(result.stdout):
                    digest=row['digest'];state=row['result']['state'];c=candidates[digest]
                    states[digest]='accepted' if state=='prepared' else state
                    if state=='prepared':self.journal.append_validated_in_transaction(c['raw'],c['reference'])
        # Holder observations resolve only already accepted/local-author journal targets.
        for digest,c in candidates.items():
            if c['event']['operation']['kind']!='hosted-holder-observation' or c['historical'] or states.get(digest)=='conflict':continue
            records=[]
            for record in self.journal.snapshot(c['event']['conversation']):
                item={'reference':record['reference'],'state':'conflict' if record['state']=='conflict' else 'valid'}
                if record['state']=='recorded':item['event']=decode_event(record['octets'][0])['value']
                records.append(item)
            p=c['proof']['processed'];snap=c['proof']['snapshot']
            request={'event':c['event'],'credential':p['credential'],'context':decode_event(bytes.fromhex(snap['context']))['value'],'members':[m.split(':')[1] for m in snap['members']],'configuredEndpointOrdering':self.configured_endpoint_ordering(p['group']),'configuredQuorumOrdering':self.configured_quorum_ordering(p['group']),'configuredApplication':self.configured_application(p['group'],snap['members'],instance=c['proof'].get('instance')),'records':records}
            encoded=json.dumps(request)
            if len(encoded.encode())>MAX:
                states[digest]='incomplete';continue
            projected=subprocess.run(['node',str(Path(__file__).with_name('check-mls-contribution.mjs'))],input=encoded,text=True,capture_output=True,check=True,timeout=10).stdout
            states[digest]='accepted' if projected=='projected-context-matched' else projected
            if states[digest]=='accepted':self.journal.append_validated_in_transaction(c['raw'],c['reference'])
        for digest,state in states.items():
            self.db.execute('INSERT INTO mls_application_acceptance VALUES(?,?) ON CONFLICT(digest) DO UPDATE SET state=excluded.state',(digest,state))
        # Projection consistency belongs to each wire representation, not the
        # event identity. Reordered dependencies can make this check possible later.
        from application_payload import projection_diagnostic
        for received_digest,raw,evidence,original in rows:
            if states.get(hashlib.sha256(raw).hexdigest())!='accepted':continue
            retained=self.db.execute('SELECT representation FROM mls_received_payloads WHERE digest=?',(received_digest,)).fetchone()
            if not retained:continue
            representation=json.loads(retained[0])
            if representation.get('projection') in ('matched','mismatch'):continue
            if decode_event(raw)['value']['operation']['kind'] in ('attachment-message','rich-message'):
                from received_attachments import validate_resources
                representation['attachments']=validate_resources(self,received_digest,raw,representation)
            diagnostic=projection_diagnostic(self,raw,representation)
            if diagnostic:
                representation['projection']=diagnostic
                self.db.execute('UPDATE mls_received_payloads SET representation=? WHERE digest=?',(json.dumps(representation),received_digest))
                receipt=json.loads(original);receipt['projection']=diagnostic
                self.db.execute('UPDATE mls_receives SET result=? WHERE digest=?',(json.dumps(receipt),received_digest))
        # Materialized local views only. Stable source tokens make repeated
        # reevaluation/replay idempotent; no action dispatcher exists here.
        changed=0
        for ref in questions.values():
            view=derive_button_view(self.journal,ref);payload=json.dumps(view,sort_keys=True)
            name='mls-question:'+ref['principal']+':'+ref['event']
            prior=self.db.execute('SELECT source_token,payload FROM derived_views WHERE conversation=? AND name=?',(ref['conversation'],name)).fetchone()
            if prior!=(view['sourceToken'],payload):
                self.db.execute('INSERT INTO derived_views VALUES(?,?,?,?) ON CONFLICT(conversation,name) DO UPDATE SET source_token=excluded.source_token,payload=excluded.payload',(ref['conversation'],name,view['sourceToken'],payload));changed+=1
        targets={}
        for c in candidates.values():
            if c['event']['operation']['kind'] in ('reaction','reaction-withdraw'):
                ref=c['event']['operation']['target'];targets[tuple(ref[k] for k in ('conversation','principal','event'))]=ref
        for ref in targets.values():
            view=derive_reaction_view(self.journal,ref)
            if view['state']!='evaluated':continue
            payload=json.dumps(view,sort_keys=True);name='reaction:'+ref['principal']+':'+ref['event']
            prior=self.db.execute('SELECT source_token,payload FROM derived_views WHERE conversation=? AND name=?',(ref['conversation'],name)).fetchone()
            if prior!=(view['sourceToken'],payload):
                self.db.execute('INSERT INTO derived_views VALUES(?,?,?,?) ON CONFLICT(conversation,name) DO UPDATE SET source_token=excluded.source_token,payload=excluded.payload',(ref['conversation'],name,view['sourceToken'],payload));changed+=1
        return {'status':'evaluated','states':states,'viewsChanged':changed,'effectsApplied':False}

    def receive(self,wire,*,time,trust_policy,fail_at=None):
        if not isinstance(wire,bytes) or len(wire)>1024*1024:raise ValueError('Wire bound')
        if trust_policy not in ('allow-unverified','require-verification'):raise ValueError('Explicit policy required')
        if not isinstance(time,dict) or set(time)!={'earliest','latest'} or uint64(time['earliest'])>uint64(time['latest']):
            raise ValueError('Valid local time interval required')
        time=dict(time)
        if self.db.execute('SELECT 1 FROM mls_retention_policy').fetchone():retention.SecretRetention(self).maintain(time=time)
        digest=hashlib.sha256(wire).hexdigest()
        def fault(point):
            if fail_at==point:raise RuntimeError('Injected failure')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            previous=self.db.execute('SELECT wire,result FROM mls_receives WHERE digest=?',(digest,)).fetchone()
            if previous:
                if previous[0]!=wire:raise ValueError('Ciphertext digest collision')
                self.db.execute('COMMIT');return json.loads(previous[1])
            row=self.db.execute('SELECT revision,format,group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
            if row is None or row[1]!=FORMAT:raise ValueError('Missing/unsupported checkpoint')
            if self.db.execute('SELECT 1 FROM mls_group_inactive WHERE group_id=?',(row[2],)).fetchone():
                self.db.execute('ROLLBACK');return {'status':'inactive-group','effectsApplied':False}
            if retention._has(self.db,'mls_retention_retired') and self.db.execute('SELECT 1 FROM mls_retention_retired WHERE group_id=?',(row[2],)).fetchone():
                self.db.execute('ROLLBACK');return {'status':'retention-retired','effectsApplied':False}
            enabled=self.db.execute('SELECT 1 FROM mls_retention_policy WHERE group_id=?',(row[2],)).fetchone() is not None
            staged=worker_call(self.binary,dict(format=FORMAT,group=row[2],checkpoint=json.loads(row[3]),wire=wire.hex(),allowHistorical=enabled))
            fault('worker')
            if staged['status']!='authenticated-application':
                if enabled:
                    self.db.execute('CREATE TABLE IF NOT EXISTS mls_retention_held(digest TEXT PRIMARY KEY,wire BLOB NOT NULL,reason TEXT NOT NULL)')
                    self.db.execute('INSERT OR IGNORE INTO mls_retention_held VALUES(?,?,?)',(digest,wire,staged.get('reason','worker')))
                    self.db.execute('COMMIT')
                else:self.db.execute('ROLLBACK')
                return {'status':'crypto-not-accepted','reason':staged.get('reason','worker')}
            raw=bytes.fromhex(staged['application']);p=staged['processed'];s=staged['snapshot']
            maintained=retention.maintain_locked(self.db,self.binary,time,checkpoint=staged['checkpoint']) if enabled else None
            if maintained:staged['checkpoint']=maintained['checkpoint']
            if s is None:s=retention.historical_snapshot(self.db,p['group'],p['epoch'])
            if s is None or (maintained and maintained['status']=='retired'):
                self.db.execute('CREATE TABLE IF NOT EXISTS mls_retention_held(digest TEXT PRIMARY KEY,wire BLOB NOT NULL,reason TEXT NOT NULL)')
                reason='historical-context-unavailable' if s is None else 'storage-budget'
                self.db.execute('INSERT OR IGNORE INTO mls_retention_held VALUES(?,?,?)',(digest,wire,reason))
                self.db.execute('COMMIT');return {'status':'retention-held','reason':reason,'effectsApplied':False}
            payload=raw;representation={};resources=[]
            try:
                from application_payload import decode as decode_payload
                context=decode_event(bytes.fromhex(s['context']))['value']
                raw,representation=decode_payload(payload,context,self.configured_application(p['group'],s['members']),configured_ordering=self.configured_endpoint_ordering(p['group']),configured_quorum_ordering=self.configured_quorum_ordering(p['group']))
                resources=representation.pop('resources',[])
            except ValueError:
                raw=b'';representation={'status':'invalid-carriage'};outcome='invalid-application-encoding'
            else:
                outcome=check(raw,p['group'],p['epoch'],p['sender'],p['credential'],p['aad'],s['group'],s['epoch'],s['context'],s['members'],identity_store=self._identity_authority(),time=time,trust_policy=trust_policy,configured_endpoint_ordering=self.configured_endpoint_ordering(p['group']),configured_quorum_ordering=self.configured_quorum_ordering(p['group']),configured_application=self.configured_application(p['group'],s['members']))
            if not episodes.permits_processed(self.db,p,s):outcome='membership-episode'
            result={'status':outcome,'revision':row[0]+1,'effectsApplied':False}
            # Only plain-message projection is journaled in this bounded stage.
            # Operations requiring references/effect authorization remain retained.
            if outcome=='projected-context-matched':
                event=decode_event(raw)['value']
                if event['operation']['kind']=='message':
                    result['journal']=self.journal.append_validated_in_transaction(raw,{k:event[k] for k in ('conversation','principal','event')})['state']
                    if result['journal']=='conflict':
                        result['status']='event-conflict'
                else:result['status']='pending-operation-authorization'
            fault('journal')
            self.db.execute('UPDATE mls_checkpoint SET revision=revision+1,snapshot=? WHERE id=1',(json.dumps(staged['checkpoint']).encode(),))
            fault('checkpoint')
            for position,resource in enumerate(resources):
                self.db.execute('INSERT INTO mls_received_resources VALUES(?,?,?,?)',(digest,position,resource['contentId'],resource['bytes']))
                self.db.execute('INSERT INTO mls_received_resource_roles VALUES(?,?,?,?)',(digest,position,resource.get('role','attachment'),resource.get('mediaType')))
            self.db.execute('INSERT INTO mls_received_payloads VALUES(?,?,?)',(digest,payload,json.dumps(representation)))
            self.db.execute('INSERT INTO mls_receives VALUES(?,?,?,?,?,?)',(digest,wire,row[0]+1,raw,json.dumps({'processed':p,'snapshot':s}).encode(),json.dumps(result)))
            instances.record_receive(self.db,digest,p['group'])
            self._reevaluate_locked(time,trust_policy)
            application=self.db.execute('SELECT state FROM mls_application_acceptance WHERE digest=?',(hashlib.sha256(raw).hexdigest(),)).fetchone()
            if application:
                result['applicationState']=application[0]
                retained=self.db.execute('SELECT representation FROM mls_received_payloads WHERE digest=?',(digest,)).fetchone()
                diagnostic=json.loads(retained[0]).get('projection') if retained else None
                if diagnostic:result['projection']=diagnostic
                self.db.execute('UPDATE mls_receives SET result=? WHERE digest=?',(json.dumps(result),digest))
            fault('receive')
            self.db.execute('COMMIT')
            return result
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
