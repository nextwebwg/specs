"""Atomic recovery-only quorum sequence; publishes only a currently authorized tip."""
import base64,hashlib,json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from admitted_quorum import AdmittedQuorum
from ordering_carrier import select_object
from ordering_certificates import encode
from ordering_mls import candidate_id,snapshot
from ordering_scope import decision_identity
from quorum_join import verify_recovery_path
from quorum_recovery_identity import check_witness
from provider_mls import call
from passive_discovery import decode_passive_discovery
from passive_discovery_verify import verify_passive_discovery
from application_support import supports
from application_agreement import profile
from initial_roster import credential
from mls_receive import LockedIdentity,MlsReceive
from remediation_chain import POLICY
import group_instances
import membership_episodes as episodes
import secret_retention as retention

class QuorumRecovery:
    def __init__(self,group,*,max_steps=16,max_bytes=8*1024*1024):
        if type(group) is not AdmittedQuorum or any(type(n) is not int or n<1 for n in (max_steps,max_bytes)):raise ValueError('Fixed quorum recovery/local bounds')
        self.group=group;self.db=group.db;self.max_steps=max_steps;self.max_bytes=max_bytes
        retention.initialize(self.db)
        self.db.executescript('''CREATE TABLE IF NOT EXISTS qo_recovery_receipt(id TEXT PRIMARY KEY,request BLOB NOT NULL,result BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS qo_recovery_step(decision TEXT PRIMARY KEY,chain TEXT NOT NULL,record BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS mls_remediation_epoch_hold(instance TEXT NOT NULL,group_id TEXT NOT NULL,epoch TEXT NOT NULL,chain TEXT NOT NULL,PRIMARY KEY(instance,group_id,epoch));''')
    def _status(self,pair,role,time):
        return LockedIdentity(self.group.identity).check_device(bytes.fromhex(pair[0]),bytes.fromhex(pair[1]),role=role,time=time,trust_policy='allow-unverified')
    def receive(self,carriers,*,expected_predecessor,allowed,time,policy=None,final_support=(),crash=None):
        MlsReceive._policy(time,'allow-unverified')
        if policy!=POLICY:return dict(status='held',reason='explicit-secret-retirement-policy-required')
        if not isinstance(carriers,list) or not 1<=len(carriers)<=self.max_steps or any(not isinstance(c,bytes) for c in carriers) or sum(map(len,carriers))>self.max_bytes:raise ValueError('Local recovery limits')
        if not isinstance(allowed,set) or any(not isinstance(p,tuple) or len(p)!=2 for p in allowed):raise ValueError('Exact locally permitted addition pairs')
        if not isinstance(final_support,(tuple,list)) or any(not isinstance(w,bytes) for w in final_support) or sum(map(len,final_support))>self.max_bytes:raise ValueError('Support bounds')
        request=encode(dict(carriers=[c.hex() for c in carriers],predecessor=expected_predecessor,allowed=sorted(allowed),policy=policy,finalSupport=[w.hex() for w in final_support]));ident=hashlib.sha256(request).hexdigest()
        db=self.db;db.execute('BEGIN IMMEDIATE')
        try:
            old=db.execute('SELECT request,result FROM qo_recovery_receipt WHERE id=?',(ident,)).fetchone()
            if old:
                if old[0]!=request:raise ValueError('Recovery collision')
                db.execute('COMMIT');return json.loads(old[1])
            tip,state=self.group.live();start=state['snapshot'];instance=group_instances.current(db,start['group'])['instance']
            if start['predecessor']!=expected_predecessor:raise ValueError('Predecessor changed')
            roster=json.loads(db.execute('SELECT roster FROM qo_genesis WHERE instance=?',(instance,)).fetchone()[0]);prefix=[];seen=set();cursor=tip;total=0
            while cursor!='genesis':
                if cursor in seen:raise ValueError('History cycle')
                seen.add(cursor);row=db.execute('SELECT carrier FROM qo_history WHERE decision=?',(cursor,)).fetchone()
                if not row:
                    recovery=db.execute('SELECT record FROM qo_recovery_step WHERE decision=?',(cursor,)).fetchone()
                    if not recovery:raise ValueError('Recovery ancestry gap')
                    row=(encode(json.loads(recovery[0])['carrier']),)
                total+=len(row[0])
                if total+sum(map(len,carriers))>self.max_bytes:raise ValueError('Local ancestry limit')
                value=json.loads(row[0]);prefix.append(dict(candidate=value['candidate'],proof=base64.b64encode(bytes.fromhex(value['proof'])).decode()));cursor=value['candidate']['plan']['scope']['previousDecision']
            path=list(reversed(prefix));values=[select_object(raw) for raw in carriers]
            signed_mode=roster['version']=='4'
            if any(v['version']!=('2' if signed_mode else '1') for v in values):raise ValueError('Exact selected recovery carrier required')
            if signed_mode:
                from quorum_exchange_support import historical_edge
                for v in values:historical_edge(dict(candidate=v['candidate'],proof=base64.b64encode(bytes.fromhex(v['proof'])).decode(),applicationAssertions=v['applicationAssertions'],witnessAssertions=v['witnessAssertions']))
            path.extend(dict(candidate=v['candidate'],proof=base64.b64encode(bytes.fromhex(v['proof'])).decode()) for v in values)
            certified=verify_recovery_path(self.group.identity,roster,path,time=time)
            local=(self.group.device['identity'],self.group.device['key']);initial={(m['identity'],m['key']) for m in start['members']};all_seen=set(initial);removed=set();staged=[];current_previous=tip
            for value in values:
                candidate=value['candidate'];plan=candidate['plan'];scope=plan['scope']
                if scope['previousDecision']!=current_previous or scope['predecessor']!=state['snapshot']['predecessor']:raise ValueError('Exact recovery predecessor')
                result=call(self.group.binary,op='receive-quorum',checkpoint=state['checkpoint'],group=start['group'],key=self.group.device['key'],wire=plan['commit'])
                if result.get('unsupported') or result.get('selfRemoved') or result['before']!=state['snapshot'] or snapshot(result['after'])!=plan['result']:raise ValueError('Actual retained MLS recovery transition')
                before={(m['identity'],m['key']) for m in result['before']['members']};after={(m['identity'],m['key']) for m in result['after']['members']};added=after-before
                if local not in before or local not in after or added&removed or not added.issubset(allowed):raise ValueError('Recovery membership continuity/selection')
                signer=[p for p in before if p[0]==result['sender']]
                if len(signer)!=1 or signer[0] not in after or self._status(signer[0],'send',time).get('status')!='authorized-unverified':raise ValueError('Current recovery committer')
                wrappers=value['applicationAssertions'];decoded=[decode_passive_discovery(encode(w)) for w in wrappers]
                if [credential(d['assertion']['value']) for d in decoded]!=sorted(p[0] for p in added):raise ValueError('Exact recovery added support')
                refs=[];keys=dict(added);application=json.loads(bytes.fromhex(result['after']['context']))['application']
                for d in decoded:
                    a=d['assertion'];v=a['value'];key=keys[credential(v)]
                    binding=next((b['value'] for b in d['identity']['bindings'] if b['digest']==v['binding']),None)
                    if not binding or binding['signingKey']!=key or not supports(v,application,'endpoint-quorum-v0'):raise ValueError('Historical package/tuple binding')
                    try:Ed25519PublicKey.from_public_bytes(bytes.fromhex(key)).verify(d['signature'],(b'email-next/passive-discovery/v7\0' if signed_mode else b'email-next/passive-discovery/v6\0')+len(a['octets']).to_bytes(4,'big')+a['octets'])
                    except Exception as error:raise ValueError('Historical assertion signature') from error
                    refs.append(call(Path(self.group.binary).with_name('provider-mls'),op='package-reference',checkpoint=state['checkpoint'],key=self.group.device['key'],package=a['key_package_octets'].hex())['reference'])
                if sorted(refs)!=result.get('additions',[]) or len(refs)!=len(set(refs)):raise ValueError('Actual recovery Add package refs')
                decision=decision_identity(scope,candidate_id(candidate));result['wire']=plan['commit'];staged.append((decision,result));current_previous=decision;removed|=before-after;all_seen|=after;state=dict(checkpoint=result['checkpoint'],snapshot=result['after'])
            final=state['snapshot'];now={(m['identity'],m['key']) for m in final['members']};ctx=json.loads(bytes.fromhex(final['context']))
            if certified['decision']!=current_previous or certified['candidate']['plan']['result']!=snapshot(final):raise ValueError('Recovery certified tip')
            for pair in now:
                if self._status(pair,'receive',time).get('status')!='authorized-unverified':raise ValueError('Current final roster authority')
            for pair in all_seen-now:
                status=self._status(pair,'receive',time)
                if status.get('status')!='authorized-unverified' and (status.get('status'),status.get('reason'))!=('unauthorized','revoked'):raise ValueError('Unresolved temporary authority')
            for w in ctx['ordering']['witnesses']:check_witness(self.group.identity,w,time)
            records=[];covered=set();witness_pairs={(credential(w),w['signingKey']):w for w in ctx['ordering']['witnesses']}
            required=(now-initial)|set(witness_pairs) if signed_mode else now-initial
            witness_wrappers=[];witness_digests=[]
            for raw in final_support:
                d=decode_passive_discovery(raw);v=d['assertion']['value'];b=next(b['value'] for b in d['identity']['bindings'] if b['digest']==v['binding']);pair=(credential(v),b['signingKey'])
                if pair not in required or pair in covered or v['version']!=('7' if signed_mode else '6') or not supports(v,ctx['application'],'endpoint-quorum-v0'):raise ValueError('Exact current final support')
                if verify_passive_discovery(raw,LockedIdentity(self.group.identity),time=time,trust_policy='allow-unverified').get('status')!='snapshot-authorized-unverified':raise ValueError('Current final assertion')
                covered.add(pair)
                if pair in now-initial:records.append(pair)
                if signed_mode and pair in witness_pairs:
                    from quorum_exchange_support import check
                    witness=witness_pairs[pair]
                    # Recovery permits an accepted descendant head with the same
                    # binding; check_witness above proves that historical link.
                    if v['binding']!=witness['binding']:raise ValueError('Current unchanged witness support')
                    witness_digests.append(check(self.group.identity,json.loads(raw),ctx,dict(witness,state=v['state']),time=time));witness_wrappers.append(json.loads(raw))
            if signed_mode and covered!=required:raise ValueError('Complete current recovery support')
            for member in final['members']:
                if (member['identity'],member['key']) not in covered and self.group.receiver.application_agreement.resolve(final['group'],[member],instance=instance)!=ctx['application']:raise ValueError('Final application agreement')
            if signed_mode:
                from quorum_exchange_support import retain_locked
                retain_locked(db,final['group'],witness_wrappers,witness_digests)
            clean=call(self.group.binary,op='discard-past',checkpoint=state['checkpoint'],group=final['group'],key=self.group.device['key'])
            if clean['snapshot']!=final:raise ValueError('Secret retirement context')
            for (decision,result),carrier in zip(staged,values):
                episodes.transition(db,result,decision)
                public={k:result[k] for k in ('before','after','sender','wire')};public['provenance']='quorum-recovery-only';public['carrier']=carrier
                db.execute('INSERT INTO qo_recovery_step VALUES(?,?,?)',(decision,ident,encode(public)))
            for _,result in staged[:-1]:db.execute('INSERT INTO mls_remediation_epoch_hold VALUES(?,?,?,?)',(instance,final['group'],result['after']['epoch'],ident))
            for identity,key in records:db.execute('INSERT INTO mls_instance_agreements VALUES(?,?,?,?,?,?)',(instance,identity,key,profile(ctx['application']),'signed-quorum-recovery-current',ident))
            db.execute('UPDATE mls_checkpoint SET revision=revision+1,snapshot=? WHERE id=1',(encode(clean['checkpoint']),))
            db.execute('UPDATE mls_quorum_admission SET previous=?,context=?,commitment=? WHERE instance=?',(current_previous,final['context'],final['predecessor'],instance))
            retention.retire_copies(db,final['group'],'quorum-atomic-recovery',retire_candidates=True)
            for cid,raw in db.execute('SELECT candidate,state FROM qo_staged').fetchall():
                if json.loads(raw).get('before',{}).get('group')==final['group']:
                    db.execute('DELETE FROM qo_staged WHERE candidate=?',(cid,));db.execute('DELETE FROM qo_stage_revision WHERE candidate=?',(cid,))
            response=dict(status='accepted-quorum-recovery',chain=ident,epoch=final['epoch'],steps=len(staged),pastEpochSecrets='deleted',forwarding='held-recovery-only')
            db.execute('INSERT INTO qo_recovery_receipt VALUES(?,?,?)',(ident,request,encode(response)))
            if crash:crash('before-commit')
            db.execute('COMMIT')
            if crash:crash('after-commit')
            return response
        except BaseException:
            if db.in_transaction:db.execute('ROLLBACK')
            raise
