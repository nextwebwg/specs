"""Atomic local recovery through revoked intermediate leaves; no historical authority grant."""
import hashlib
import json
from group_transitions import ids,encode,digest
from mls_receive import LockedIdentity,MlsReceive
import group_instances as instances
import membership_episodes as episodes
import secret_retention as retention
from transition_carrier import parse,check_binding

POLICY='delete-all-past-for-remediation'

def members(snapshot):return {(m['identity'],m['key']) for m in snapshot['members']}

class RemediationChain:
    def __init__(self,coordinator,*,max_steps=16,max_bytes=8*1024*1024):
        self.g=coordinator;self.db=coordinator.db
        if self.db.in_transaction:raise ValueError('Initialize outside transaction')
        if any(type(v)!=int or v<1 for v in (max_steps,max_bytes)):raise ValueError('Local limits')
        self.max_steps=max_steps;self.max_bytes=max_bytes
        retention.initialize(self.db)
        import transition_support
        transition_support.initialize(self.db)
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS mls_remediation_receipt(digest TEXT PRIMARY KEY,request BLOB NOT NULL,result BLOB NOT NULL);
          CREATE TABLE IF NOT EXISTS mls_remediation_epoch_hold(instance TEXT NOT NULL,group_id TEXT NOT NULL,epoch TEXT NOT NULL,chain TEXT NOT NULL,PRIMARY KEY(instance,group_id,epoch));
          CREATE TABLE IF NOT EXISTS mls_remediation_step(digest TEXT PRIMARY KEY,chain TEXT NOT NULL,record BLOB NOT NULL);
        ''')

    def _current(self,pair,role,time):
        return LockedIdentity(self.g.identity).check_device(bytes.fromhex(pair[0]),bytes.fromhex(pair[1]),role=role,time=time,trust_policy='allow-unverified')

    def _structure(self,result,allowed,time):
        if result.get('unsupported') or result.get('selfRemoved'):raise ValueError('Unsupported remediation control')
        before,after=result['before'],result['after'];ctx=json.loads(bytes.fromhex(before['context']))
        if ctx.get('version') not in ('1','2','3','4','5','6') or ctx.get('purpose')!='conversation-context' or ctx.get('profile')!='mls-1-0001':raise ValueError('Context')
        expected={'version','purpose','conversation','profile','administrators','ordering'}|({'application'} if ctx['version']!='1' else set())|({'delivery'} if ctx['version'] in ('5','6') else set())
        if set(ctx)!=expected:raise ValueError('Context fields')
        ordering=ctx['ordering'];admins=ctx['administrators']
        if set(ordering)!={'kind','principal','device'} or ordering['kind']!='designated-member-v0' or admins!=sorted(set(admins)) or ordering['principal'] not in admins:raise ValueError('Ordering')
        if ids(result['sender'])!=(ordering['principal'],ordering['device']):raise ValueError('Writer')
        if before['context']!=after['context'] or before['group']!=after['group'] or int(after['epoch'])!=int(before['epoch'])+1:raise ValueError('Context continuity')
        old,new=members(before),members(after);added=new-old;removed=old-new
        from private_copy import check_roster
        check_roster(ctx,{ids(i)[0] for i,k in old})
        check_roster(ctx,{ids(i)[0] for i,k in new})
        if added and removed or not added.issubset(allowed):raise ValueError('Unauthorized addition')
        if len(new)!=len(after['members']) or len({ids(i) for i,k in new})!=len(new):raise ValueError('Duplicate device')
        if not set(admins).issubset({ids(i)[0] for i,k in new}):raise ValueError('Administrator absent')
        signer=[p for p in old if p[0]==result['sender']]
        if len(signer)!=1 or signer[0] not in new or self._current(signer[0],'send',time).get('status')!='authorized-unverified':raise ValueError('Current committer authority')
        local=(self.g.device['identity'],self.g.device['key'])
        if local not in old or local not in new:raise ValueError('Local membership discontinuity')
        return ctx,added,removed

    def receive(self,carriers,*,allowed,time,expected_predecessor,policy=None,final_support=(),crash=None,_in_transaction=False):
        """carriers are exact existing transition-carrier JSON bytes, after MIME selection.

        Explicit policy loses late ciphertext decryptability, never accepted plaintext.
        No caller historical-authority object is accepted. No network effects occur.
        """
        MlsReceive._policy(time,'allow-unverified')
        if policy!=POLICY:return {'status':'held','reason':'explicit-secret-retirement-policy-required'}
        if not isinstance(carriers,list) or not 1<=len(carriers)<=self.max_steps or any(not isinstance(c,bytes) for c in carriers) or sum(map(len,carriers))>self.max_bytes:raise ValueError('Local chain limits')
        if not isinstance(final_support,(list,tuple)) or any(not isinstance(w,bytes) for w in final_support) or sum(map(len,final_support))>self.max_bytes:raise ValueError('Support input limits')
        request=encode(dict(finalSupport=[w.hex() for w in final_support],carriers=[c.hex() for c in carriers],allowed=sorted(allowed),predecessor=expected_predecessor,policy=policy))
        identifier=digest(request);db=self.db
        if _in_transaction:
            if not db.in_transaction:raise ValueError('Caller transaction required')
        else:db.execute('BEGIN IMMEDIATE')
        try:
            prior=db.execute('SELECT request,result FROM mls_remediation_receipt WHERE digest=?',(identifier,)).fetchone()
            if prior:
                if prior[0]!=request:raise ValueError('Request collision')
                if not _in_transaction:db.execute('COMMIT')
                return json.loads(prior[1])
            state=self.g.live();start=state['snapshot'];group=start['group']
            if start['predecessor']!=expected_predecessor:raise ValueError('Predecessor changed')
            current=instances.optional_current(db,group);origin=current['instance'] if current else None
            staged=[];removed_ever=set();all_seen=members(start);seen=set()
            for raw in carriers:
                carrier,wire=parse(raw);step=digest(wire)
                if step in seen:raise ValueError('Duplicate Commit')
                seen.add(step)
                prior_control=db.execute('SELECT result FROM gt_receive WHERE digest=?',(step,)).fetchone()
                if prior_control:raise ValueError('Legacy rejected state requires recovery' if prior_control[0]=='rejected-policy' else 'Already processed control')
                check_binding(carrier,state['snapshot'])
                result=self.g.invoke('receive',state,wire=wire.hex())
                if result['before']!=state['snapshot']:raise ValueError('Full predecessor mismatch')
                ctx,added,removed=self._structure(result,allowed,time)
                if added & removed_ever:raise ValueError('Removal and rejoin need separate admission')
                removed_ever|=removed;all_seen|=members(result['after'])
                result['wire']=wire.hex();staged.append((step,result))
                state={'checkpoint':result['checkpoint'],'snapshot':result['after']}
            final=state['snapshot'];final_members=members(final);temporary=all_seen-final_members
            for pair in final_members:
                if self._current(pair,'receive',time).get('status')!='authorized-unverified':raise ValueError('Current final roster authority')
            for pair in temporary:
                checked=self._current(pair,'receive',time)
                if checked.get('status')!='authorized-unverified' and (checked.get('status'),checked.get('reason'))!=('unauthorized','revoked'):raise ValueError('Unresolved intermediate authority')
                # Revocation is not proof of the old signing key. Exact temporary
                # additions remain an explicit local permitted-pair input.
            import remediation_support
            confirmed=remediation_support.validate(self.g,final_support,final,start,origin,time)
            if ctx['version']!='1':
                application=ctx['application']
                import subprocess
                from pathlib import Path
                checked=subprocess.run(['node',str(Path(__file__).with_name('check-transition-context.mjs'))],input=json.dumps(dict(context=ctx,application=application)),text=True,capture_output=True,timeout=10,check=True)
                if checked.stdout!='valid':raise ValueError('Application context')
            clean=self.g.invoke('discard-past',state)
            if clean['snapshot']!=final:raise ValueError('Secret retirement changed context')
            # Public receipts only. Never turn structural recovery into accepted
            # historical role/support evidence or a forwardable decision ledger.
            for step,result in staged:
                episodes.transition(db,result,step)
                public={k:result[k] for k in ('before','after','sender','wire')}
                public['provenance']='recovery-only-no-historical-authority'
                db.execute('INSERT INTO mls_remediation_step VALUES(?,?,?)',(step,identifier,encode(public)))
                db.execute('INSERT INTO gt_receive VALUES(?,?,?,?)',(step,'accepted-remediation',encode(result['before']),bytes.fromhex(result['wire'])))
                db.execute('DELETE FROM gt_pending WHERE digest=?',(step,))
            for _,intermediate in staged[:-1]:
                db.execute('INSERT INTO mls_remediation_epoch_hold VALUES(?,?,?,?)',(origin or '',group,intermediate['after']['epoch'],identifier))
            remediation_support.install(self.g,confirmed,final,origin,time,identifier)
            self.g._install(clean)
            retention.retire_copies(db,group,'atomic-remediation',retire_candidates=True)
            response=dict(status='accepted-remediation',chain=identifier,epoch=final['epoch'],pastEpochSecrets='deleted',acceptedHistory='preserved',forwarding='held-no-historical-authority',steps=len(staged))
            db.execute('INSERT INTO mls_remediation_receipt VALUES(?,?,?)',(identifier,request,encode(response)))
            if crash:crash('before-commit')
            if not _in_transaction:db.execute('COMMIT')
            if crash and not _in_transaction:crash('after-commit')
            return response
        except BaseException:
            if not _in_transaction and db.in_transaction:db.execute('ROLLBACK')
            raise


def should_hold(coordinator,result,allowed,time):
    """A structurally valid Commit awaiting removal, never a role authorization.

    Caller is inside receive's transaction. Staged crypto must be discarded.
    Only explicit accepted revocation can enter this path; ordinary policy
    failures retain their existing behavior.
    """
    probe=object.__new__(RemediationChain);probe.g=coordinator;probe.db=coordinator.db
    try:
        probe._structure(result,allowed,time)
        checked=[probe._current(pair,'receive',time) for pair in members(result['after'])]
        return any(v.get('reason')=='revoked' for v in checked) and all(v.get('status')=='authorized-unverified' or (v.get('status'),v.get('reason'))==('unauthorized','revoked') for v in checked)
    except (ValueError,KeyError,TypeError):return False
