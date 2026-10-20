"""Configured endpoint ordering comparison; not distributed ordering or mail delivery.

All checkpoints/Welcome objects are private local state. The configured comparison shares one checkpoint with application send/receive.
"""
import hashlib
import json
from provider_mls import call
from mls_receive import LockedIdentity, MlsReceive, FORMAT
from pathlib import Path
from commit_history import retain_decision_locked
import membership_episodes as episodes
import transition_application
import secret_retention as retention


def digest(value):return hashlib.sha256(value).hexdigest()
def encode(value):return json.dumps(value,separators=(',',':')).encode()
def ids(identity):
    raw=bytes.fromhex(identity)
    if len(raw)!=85 or raw[:21]!=b'email-next/device/v0\0':raise ValueError('Credential')
    return 'enp0:'+raw[21:53].hex(),'end0:'+raw[53:].hex()


class GroupTransitions:
    def __init__(self,identity,binary,device):
        self.identity=identity;self.db=identity.db;self.binary=binary;self.device=device
        self.receiver=MlsReceive(identity,Path(binary).with_name('receive-staged'))
        episodes.initialize(self.db)
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS gt_abandoned(digest TEXT PRIMARY KEY, predecessor TEXT NOT NULL, reason TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS gt_candidate(digest TEXT PRIMARY KEY, predecessor TEXT UNIQUE NOT NULL, packages BLOB NOT NULL, state BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS gt_decision(predecessor TEXT PRIMARY KEY, digest TEXT UNIQUE NOT NULL, state BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS gt_outbox(digest TEXT PRIMARY KEY, state BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS gt_receive(digest TEXT PRIMARY KEY, result TEXT NOT NULL, evidence BLOB NOT NULL, wire BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS gt_pending(digest TEXT PRIMARY KEY, wire BLOB NOT NULL, carrier BLOB);
        ''')
    def install_configured_fixture(self,state):
        self.receiver.install_fixture(state['snapshot']['group'],state['checkpoint'])
        episodes.install(self.db,state['snapshot'],'configured-install:'+digest(encode(state['snapshot'])))
        self.db.execute('INSERT INTO mls_configured_context VALUES(?,?)',(state['snapshot']['group'],'configured-endpoint-v0'))
    def live(self):
        row=self.db.execute('SELECT revision,format,group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
        if row is None or row[1]!=FORMAT:raise ValueError('Checkpoint')
        if not self.receiver.configured_endpoint_ordering(row[2]):raise ValueError('Ordering not configured')
        if not self.db.execute('SELECT 1 FROM mls_membership_episode WHERE group_id=?',(row[2],)).fetchone():raise ValueError('Membership episode migration required')
        if self.db.execute('SELECT 1 FROM mls_group_inactive WHERE group_id=?',(row[2],)).fetchone():raise ValueError('Inactive group')
        inspected=call(self.binary,op='inspect',checkpoint=json.loads(row[3]),group=row[2],key=self.device['key'])
        return {'revision':row[0],'checkpoint':inspected['checkpoint'],'snapshot':inspected['snapshot']}
    def _install(self,state):
        self.db.execute('UPDATE mls_checkpoint SET revision=revision+1,snapshot=? WHERE id=1',(json.dumps(state['checkpoint']).encode(),))
    def retire(self,identifier,*,allowed,time):
        """Explicit retirement of an unreleased candidate; no automatic rebasing."""
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row=self.db.execute('SELECT state FROM gt_candidate WHERE digest=?',(identifier,)).fetchone()
            if row is None:raise ValueError('Unknown candidate')
            result=json.loads(row[0])
            if self.db.execute('SELECT 1 FROM gt_decision WHERE digest=?',(identifier,)).fetchone():raise ValueError('Already decided')
            if self.live()['snapshot']['predecessor']!=result['before']['predecessor']:raise ValueError('Membership changed')
            self._authorize(result,allowed,time)
            self.db.execute('INSERT INTO gt_abandoned VALUES(?,?,?)',(identifier,result['before']['predecessor'],'explicit-unreleased-retirement'))
            self.db.execute('DELETE FROM gt_candidate WHERE digest=?',(identifier,))
            self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def _maintain(self,time=None):
        if self.db.execute('SELECT 1 FROM mls_retention_policy').fetchone():
            if time is None:
                import time as local_clock
                time=dict.fromkeys(('earliest','latest'),str(int(local_clock.time())))
            result=retention.SecretRetention(self.receiver).maintain(time=time)
            if result and result['status']=='retired':raise ValueError('Retention retired group')

    def invoke(self,op,state,**kwargs):
        return call(self.binary,op=op,checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.device['key'],**kwargs)
    def _authorize(self,result,allowed,time,*,historical=False):
        if result.get('unsupported'):raise ValueError('Unsupported authenticated control')
        before=result['before'];after=result['after'];ctx=json.loads(bytes.fromhex(before['context']))
        application_proof=None
        if ctx.get('version') in ('2','3','4','5','6'):
            application_proof=transition_application.authorize(self,result,ctx,historical=historical,time=time)
        elif set(ctx)!={'version','purpose','conversation','profile','administrators','ordering'} or ctx['version']!='1' or ctx['purpose']!='conversation-context' or ctx['profile']!='mls-1-0001':raise ValueError('Context')
        ordering=ctx['ordering'];admins=ctx['administrators']
        if set(ordering)!={'kind','principal','device'} or ordering['kind']!='designated-member-v0' or ordering['principal'] not in admins or admins!=sorted(set(admins)):raise ValueError('Ordering configuration')
        if ids(result['sender'])!=(ordering['principal'],ordering['device']):raise ValueError('Wrong writer')
        if before['context']!=after['context'] or before['group']!=after['group'] or int(after['epoch'])!=int(before['epoch'])+1:raise ValueError('Unexpected context')
        from private_copy import check_roster
        check_roster(ctx,[ids(m['identity'])[0] for m in after['members']])
        old={(m['identity'],m['key']) for m in before['members']};new={(m['identity'],m['key']) for m in after['members']}
        removed=old-new;added=new-old
        if (removed and added) or not added.issubset(allowed):raise ValueError('Unauthorized addition or mixed change')
        if removed and result.get('targets') is not None and removed!={tuple(v) for v in result['targets']}:raise ValueError('Removal target mismatch')
        if result['sender'] not in {i for i,k in new}:raise ValueError('Cannot remove configured writer')
        if len(new)!=len(after['members']) or len({ids(i) for i,k in new})!=len(new):raise ValueError('Duplicate device')
        if not set(admins).issubset({ids(i)[0] for i,k in new}):raise ValueError('Administrator absent')
        sender=[m for m in before['members'] if m['identity']==result['sender']]
        if len(sender)!=1:raise ValueError('Sender')
        signer=sender[0]
        if historical:
            evidence=result.get('authorization')
            expected={(i,k,'receive') for i,k in new}|{(signer['identity'],signer['key'],'send')}
            if not isinstance(evidence,dict) or evidence.get('version')!='configured-accepted-v0' or evidence.get('additions')!=[list(v) for v in sorted(added)] or evidence.get('removals')!=[list(v) for v in sorted(removed)] or {(v['identity'],v['key'],v['role']) for v in evidence['checks']}!=expected or any(v['status']!='authorized-unverified' or not v['head'] or not v['binding'] for v in evidence['checks']):raise ValueError('Missing accepted historical authority')
            return evidence
        authority=LockedIdentity(self.identity).check_device(bytes.fromhex(signer['identity']),bytes.fromhex(signer['key']),role='send',time=time,trust_policy='allow-unverified')
        if authority.get('status')!='authorized-unverified':raise ValueError('Current committer send authority')
        checks=[dict(identity=signer['identity'],key=signer['key'],role='send',**{k:authority[k] for k in ('status','head','binding')})]
        heads=[]
        for identity,key in new:
            checked=LockedIdentity(self.identity).check_device(bytes.fromhex(identity),bytes.fromhex(key),role='receive',time=time,trust_policy='allow-unverified')
            if checked.get('status')!='authorized-unverified':raise ValueError('Current identity')
            heads.append((identity,checked['head'],checked['binding']))
            checks.append(dict(identity=identity,key=key,role='receive',**{k:checked[k] for k in ('status','head','binding')}))
        return {'version':'configured-accepted-v0','time':dict(time),'checks':checks,'additions':[list(v) for v in sorted(added)],'removals':[list(v) for v in sorted(removed)],**({'applicationAgreement':application_proof} if application_proof else {})}
    def prepare(self,packages,*,time=None):
        self._maintain(time)
        # Candidate and Welcome remain private until an atomic decision exists.
        self.db.execute('BEGIN IMMEDIATE')
        try:
            state=self.live();predecessor=state['snapshot']['predecessor']
            prior=self.db.execute('SELECT digest,packages FROM gt_candidate WHERE predecessor=?',(predecessor,)).fetchone()
            if prior:
                if prior[1]!=encode(packages):raise ValueError('Candidate already reserved')
                self.db.execute('COMMIT');return prior[0]
            result=self.invoke('candidate',state,packages=packages)
            result['sourceDigest']=digest(encode(state))
            identifier=digest(bytes.fromhex(result['wire']))
            self.db.execute('INSERT INTO gt_candidate VALUES(?,?,?,?)',(identifier,predecessor,encode(packages),encode(result)))
            self.db.execute('COMMIT');return identifier
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def prepare_removal(self,targets,*,time=None):
        self._maintain(time)
        if not isinstance(targets,list) or not targets or any(not isinstance(t,dict) or set(t)!={'identity','key'} for t in targets):raise ValueError('Exact removal targets')
        pairs={(t['identity'],t['key']) for t in targets}
        if len(pairs)!=len(targets):raise ValueError('Duplicate removal target')
        request=encode({'remove':sorted(pairs)})
        self.db.execute('BEGIN IMMEDIATE')
        try:
            state=self.live();before=state['snapshot'];members=before['members']
            if any(sum((m['identity'],m['key'])==pair for m in members)!=1 for pair in pairs):raise ValueError('Missing unique target')
            if any(i==self.device['identity'] for i,k in pairs):raise ValueError('Cannot remove configured writer')
            prior=self.db.execute('SELECT digest,packages FROM gt_candidate WHERE predecessor=?',(before['predecessor'],)).fetchone()
            if prior:
                if prior[1]!=request:raise ValueError('Candidate already reserved')
                self.db.execute('COMMIT');return prior[0]
            result=self.invoke('remove',state,indices=[m['index'] for m in members if (m['identity'],m['key']) in pairs])
            result['targets']=sorted(pairs);result['sourceDigest']=digest(encode(state));identifier=digest(bytes.fromhex(result['wire']))
            self.db.execute('INSERT INTO gt_candidate VALUES(?,?,?,?)',(identifier,before['predecessor'],request,encode(result)))
            self.db.execute('COMMIT');return identifier
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def decide(self,identifier,*,allowed,time,crash=None):
        self._maintain(time)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            prior=self.db.execute('SELECT digest FROM gt_decision WHERE digest=?',(identifier,)).fetchone()
            if prior:self.db.execute('COMMIT');return 'accepted'
            row=self.db.execute('SELECT state FROM gt_candidate WHERE digest=?',(identifier,)).fetchone()
            if row is None:raise ValueError('Unknown private candidate')
            result=json.loads(row[0]);state=self.live()
            if state['snapshot']['predecessor']!=result['before']['predecessor'] or digest(encode(state))!=result['sourceDigest']:raise ValueError('Predecessor changed')
            result['authorization']=self._authorize(result,allowed,time)
            transition_application.install(self,result,identifier)
            episodes.transition(self.db,result,identifier)
            retain_decision_locked(self.db,result)
            self.db.execute('INSERT INTO gt_decision VALUES(?,?,?)',(result['before']['predecessor'],identifier,encode(result)))
            self._install({'checkpoint':result['checkpoint']})
            self.db.execute('INSERT INTO gt_outbox VALUES(?,?)',(identifier,encode(result)))
            retention.maintain_locked(self.db,self.binary,time)
            if crash:crash('before-commit')
            self.db.execute('COMMIT')
            if crash:crash('after-commit')
            return 'accepted'
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def release(self,identifier,*,allowed,time):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row=self.db.execute('SELECT state FROM gt_outbox WHERE digest=?',(identifier,)).fetchone()
            if row is None:raise ValueError('Welcome withheld')
            result=json.loads(row[0]);self._authorize(result,allowed,time)
            if self.live()['snapshot']['predecessor']!=result['after']['predecessor']:raise ValueError('Release state changed')
            self.db.execute('COMMIT');return {'wire':result['wire'],'welcome':result['welcome'],'before':result['before']}
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def receive(self,wire,*,allowed,time,crash=None,carrier=None,carrier_octets=None):
        self._maintain(time)
        if not isinstance(wire,bytes) or len(wire)>1024*1024:raise ValueError('Wire limit')
        if carrier_octets is not None:
            from transition_carrier import parse
            parsed,embedded=parse(carrier_octets)
            if parsed!=carrier or embedded!=wire:raise ValueError('Carrier bytes mismatch')
        identifier=digest(wire);self.db.execute('BEGIN IMMEDIATE')
        try:
            prior=self.db.execute('SELECT result,evidence,wire FROM gt_receive WHERE digest=?',(identifier,)).fetchone()
            if prior:
                if prior[2]!=wire:raise ValueError('Ciphertext digest collision')
                if carrier is not None:
                    from transition_carrier import check_binding
                    check_binding(carrier,json.loads(prior[1]))
                self.db.execute('COMMIT');return prior[0]
            pending=self.db.execute('SELECT wire,carrier FROM gt_pending WHERE digest=?',(identifier,)).fetchone()
            if pending:
                if pending[0]!=wire:raise ValueError('Pending digest collision')
                retained=json.loads(pending[1]) if pending[1] is not None else None
                if retained is not None:
                    if carrier is None:
                        carrier=retained;carrier_octets=pending[1]  # Bare retry cannot strip the binding.
            state=self.live();frame=self.invoke('frame',state,wire=wire.hex())
            if frame['group']!=state['snapshot']['group']:raise ValueError('Group')
            if carrier is not None:
                import base64
                if base64.b64decode(carrier['group']).hex()!=frame['group'] or carrier['previousEpoch']!=frame['epoch']:raise ValueError('Carrier frame mismatch')
                if frame['epoch']==state['snapshot']['epoch']:
                    from transition_carrier import check_binding
                    check_binding(carrier,state['snapshot'])
            if int(frame['epoch'])>int(state['snapshot']['epoch']):
                if pending and pending[1] is not None and carrier!=json.loads(pending[1]):raise ValueError('Different pending carrier requires later explicit retry')
                if len(wire)>1024*1024 or self.db.execute('SELECT count(*) FROM gt_pending').fetchone()[0]>=16:raise ValueError('Pending limit')
                if pending and pending[1] is None and carrier is not None:
                    self.db.execute('UPDATE gt_pending SET carrier=? WHERE digest=?',(carrier_octets if carrier_octets is not None else encode(carrier),identifier))
                else:self.db.execute('INSERT OR IGNORE INTO gt_pending VALUES(?,?,?)',(identifier,wire,(carrier_octets if carrier_octets is not None else encode(carrier)) if carrier is not None else None))
                self.db.execute('COMMIT');return 'pending'
            result=self.invoke('receive',state,wire=wire.hex())
            from remediation_chain import should_hold
            if should_hold(self,result,allowed,time):
                # Retain the exact input without consuming the Commit ratchet.
                # Recovery must authenticate a complete chain before installation.
                if self.db.execute('SELECT count(*) FROM gt_pending').fetchone()[0]>=16 and not pending:raise ValueError('Pending limit')
                retained=(carrier_octets if carrier_octets is not None else encode(carrier)) if carrier is not None else None
                self.db.execute('INSERT OR REPLACE INTO gt_pending VALUES(?,?,?)',(identifier,wire,retained))
                self.db.execute('COMMIT');return 'pending-remediation'
            try:result['authorization']=self._authorize(result,allowed,time);status='accepted'
            except ValueError:status='rejected-policy'
            if status=='accepted':
                result['wire']=wire.hex()
                transition_application.install(self,result,identifier)
                episodes.transition(self.db,result,identifier)
                # Evicted endpoints cannot attest the survivor's finalized context.
                # Keep terminal receipt/tombstone, not reusable ancestry evidence.
                if not result.get('selfRemoved'):
                    retain_decision_locked(self.db,result)
                    self.db.execute('INSERT INTO gt_decision VALUES(?,?,?)',(result['before']['predecessor'],identifier,encode(result)))
                next_state={'checkpoint':result['checkpoint'],'snapshot':result['after']}
            else:next_state={'checkpoint':result['unmerged'],'snapshot':result['before']}
            self._install(next_state)
            self.db.execute('INSERT INTO gt_receive VALUES(?,?,?,?)',(identifier,status,encode(result['before']),wire))
            self.db.execute('DELETE FROM gt_pending WHERE digest=?',(identifier,))
            retention.maintain_locked(self.db,self.binary,time)
            if crash:crash('before-commit')
            self.db.execute('COMMIT')
            if crash:crash('after-commit')
            return status
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise

    def reprocess_pending(self,identifier,*,allowed,time,crash=None):
        """Reprocess retained wire and binding; never reconstruct a stripped control."""
        row=self.db.execute('SELECT wire,carrier FROM gt_pending WHERE digest=?',(identifier,)).fetchone()
        if row is None:raise ValueError('Unknown pending control')
        return self.receive(row[0],carrier=json.loads(row[1]) if row[1] is not None else None,carrier_octets=row[1],allowed=allowed,time=time,crash=crash)
