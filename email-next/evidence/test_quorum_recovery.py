import base64,copy,hashlib,json,unittest
import test_admitted_quorum as fixtures
from ordering_mls import ProviderKey
from ordering_carrier import package,receive
from provider_mls import sign
from event_encoding import encode_event
from quorum_recovery import QuorumRecovery,POLICY
from quorum_recovery_identity import check_witness

class QuorumRecoveryTests(unittest.TestCase):
    setUp=fixtures.AdmittedQuorumTests.setUp;tearDown=fixtures.AdmittedQuorumTests.tearDown
    endpoint=fixtures.AdmittedQuorumTests.endpoint;prepare=fixtures.AdmittedQuorumTests.prepare;join=fixtures.AdmittedQuorumTests.join;certify=fixtures.AdmittedQuorumTests.certify;event=fixtures.AdmittedQuorumTests.event
    def setup_chain(self,add=False):
        self.join();self.target=self.groups[2];self.start=self.target.live()[1]['snapshot']['predecessor'];self.carriers=[]
        self.extra=None
        if add:
            from provider_mls import make_device,advertisement
            from quorum_join_support import confirm
            self.extra=make_device(self.provider,7,8)
            for store in self.stores:store.observe(self.extra['record'],first_contact_policy='allow-unverified')
            wrapper=advertisement(self.provider,self.extra,'extra@example.invalid');value=json.loads(base64.b64decode(wrapper['payload']));value.update(version='6',applications=[dict(self.f.context['application'],ordering='endpoint-quorum-v0')]);raw=encode_event(value);wrapper.update(payload=base64.b64encode(raw).decode(),signature=sign(self.provider,self.extra,'email-next/passive-discovery/v6',raw));self.extra_proof=encode_event(wrapper)
            for group in self.groups[:2]:confirm(group,self.extra_proof,time=self.time)
        for remove in (False,True):
            indices=[int(m['index']) for m in self.author_group.live()[1]['snapshot']['members'] if m['identity']==self.removed['identity']] if remove else []
            candidate=self.author_group.stage(ProviderKey(self.provider,self.f.creator),time=self.time,removals=indices,packages=[self.extra['package']] if add and not remove else []);proof=self.certify(candidate)
            for group in self.groups[:2]:decision=group.install(candidate,proof,time=self.time)
            self.carriers.append(package(self.author_group.db.execute('SELECT bytes FROM qo_outbox WHERE identity=?',(decision,)).fetchone()[0]))
            if not remove and not add:self.intermediate=self.sender.prepare('intermediate',encode_event(self.event(self.f.creator,'7')),key=self.f.creator['key'],envelope_sender='creator@example.invalid',recipients=['offline@example.invalid'],time=self.time)
        from quorum_historical_release import QuorumHistoricalRelease
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        d=self.target.device;c=next(c for d0,c in zip(self.f.devices,self.selected) if d0 is d)
        history=QuorumHistoricalRelease(self.sender,self.author_group)
        names=history.prepare('recoverhistory',self.start,target=dict(mailbox=c['mailbox'],principal=d['principal'],device=d['device']),key=d['key'],association_target=dict(mailbox=c['mailbox'],generation=c['generation'],principal=d['principal'],observation=c['digest']),envelope_sender='creator@example.invalid',time=self.time)
        self.carriers=[]
        with SenderWorker(self.sender) as sender_worker:
            for name in names:
                smtp=LocalSMTP();self.assertEqual(sender_worker.submit_quorum_history(name,group=self.author_group,port=smtp.port,time=self.time)['state'],'accepted');smtp.done();self.carriers.append(smtp.wire)
        bundle=copy.deepcopy(self.f.bundles[self.f.creator['principal']]);state=json.loads(base64.b64decode(bundle['states'][0]['payload']))
        state.update(record='9'*32,revision='2',previous=[self.f.heads[self.f.creator['principal']]],revoked=[self.removed['device']],bindings=[b for b in state['bindings'] if b['device']!=self.removed['device']])
        raw=encode_event(state);bundle['states'].insert(0,dict(payload=base64.b64encode(raw).decode(),signature=sign(self.provider,self.f.creator,'email-next/identity-state/v0',raw)))
        self.assertEqual(self.target.identity.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(raw).hexdigest(),time=self.time)['status'],'accepted-unverified')
        self.recovery=QuorumRecovery(self.target)
    def test_atomic_sibling_revocation_recovery_rollback_and_current_exchange(self):
        self.setup_chain();before=self.target.live()
        with self.assertRaises(ValueError):receive(self.target,self.carriers[0],time=self.time)
        self.assertEqual(self.target.live(),before)
        options=dict(expected_predecessor=self.start,allowed=set(),time=self.time,policy=POLICY)
        with self.assertRaises(RuntimeError):self.recovery.receive(self.carriers,**options,crash=lambda _:(_ for _ in ()).throw(RuntimeError('crash')))
        self.assertEqual(self.target.live(),before);self.assertEqual(self.target.db.execute('SELECT count(*) FROM qo_recovery_step').fetchone()[0],0)
        result=self.recovery.receive(self.carriers,**options);self.assertEqual(result['status'],'accepted-quorum-recovery');self.assertEqual(result,self.recovery.receive(self.carriers,**options))
        self.assertEqual(self.target.live()[1]['snapshot']['epoch'],'3');self.assertEqual(self.target.db.execute('SELECT count(*) FROM mls_remediation_epoch_hold').fetchone()[0],1)
        self.assertEqual(self.target.db.execute('SELECT count(*) FROM qo_history').fetchone()[0],0)
        import membership_episodes
        self.assertFalse(membership_episodes.permits(self.target.db,self.target.live()[1]['snapshot']['group'],self.f.creator['identity'],self.f.creator['key'],'2'))
        from mls_mime import unpack
        from smtp_loopback import roundtrip
        late=self.target.receiver.receive(unpack(self.intermediate),time=self.time,trust_policy='allow-unverified')
        self.assertNotEqual(late.get('applicationState'),'accepted')
        sender=self.senders[self.target.device['device']]
        wire=sender.prepare('recoveredreply',encode_event(self.event(self.target.device,'8')),key=self.target.device['key'],envelope_sender='recovered@example.invalid',recipients=['creator@example.invalid'],time=self.time)
        self.assertEqual(self.sender.receiver.receive(unpack(roundtrip(wire)),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        predecessor=self.target.live()[1]['snapshot']['predecessor']
        candidate=self.author_group.stage(ProviderKey(self.provider,self.f.creator),time=self.time);proof=self.certify(candidate)
        for group in self.groups[:2]:decision=group.install(candidate,proof,time=self.time)
        following=roundtrip(package(self.author_group.db.execute('SELECT bytes FROM qo_outbox WHERE identity=?',(decision,)).fetchone()[0]))
        self.assertEqual(self.recovery.receive([following],expected_predecessor=predecessor,allowed=set(),time=self.time,policy=POLICY)['epoch'],'4')

    def test_new_final_member_needs_current_exact_support(self):
        self.setup_chain(add=True);before=self.target.live();allowed={(self.extra['identity'],self.extra['key'])}
        options=dict(expected_predecessor=self.start,allowed=allowed,time=self.time,policy=POLICY)
        with self.assertRaisesRegex(ValueError,'Final application agreement'):self.recovery.receive(self.carriers,**options)
        self.assertEqual(self.target.live(),before)
        with self.assertRaises(ValueError):self.recovery.receive(self.carriers,**dict(options,allowed=set()),final_support=[self.extra_proof])
        result=self.recovery.receive(self.carriers,**options,final_support=[self.extra_proof]);self.assertEqual(result['status'],'accepted-quorum-recovery')
        self.assertEqual(self.target.live()[1]['snapshot']['epoch'],'3')
    def test_recovery_witness_ancestry_binding_and_revocation_holds(self):
        self.setup_chain();w=next(w for w in self.f.context['ordering']['witnesses'] if w['principal']==self.f.creator['principal']);db=self.target.db
        db.execute('BEGIN IMMEDIATE')
        try:
            check_witness(self.target.identity,w,self.time)
            for field in ('state','binding','signingKey'):
                wrong=dict(w);wrong[field]='f'*64
                with self.subTest(field=field),self.assertRaises(ValueError):check_witness(self.target.identity,wrong,self.time)
            revoked=dict(w,device=self.removed['device'],signingKey=self.removed['key'])
            with self.assertRaisesRegex(ValueError,'Current unchanged'):check_witness(self.target.identity,revoked,self.time)
            db.execute('UPDATE identity_heads SET conflicted=1 WHERE principal=?',(w['principal'],))
            with self.assertRaises(ValueError):check_witness(self.target.identity,w,self.time)
        finally:db.execute('ROLLBACK')
        with self.assertRaises(ValueError):self.recovery.receive(self.carriers[::-1],expected_predecessor=self.start,allowed=set(),time=self.time,policy=POLICY)
        self.assertEqual(self.target.live()[1]['snapshot']['epoch'],'1')
        head=self.target.identity.current_state(w['principal'])['head'];bundle=json.loads(db.execute('SELECT bundle FROM identity_transitions WHERE principal=? AND digest=?',(w['principal'],head)).fetchone()[0]);state=json.loads(base64.b64decode(bundle['states'][0]['payload']))
        binding=next(json.loads(base64.b64decode(b['payload'])) for b in bundle['bindings'] if json.loads(base64.b64decode(b['payload']))['device']==w['device'])
        binding.update(record='a'*32,authority=dict(kind='state',digest=head));binding_raw=encode_event(binding);binding_digest=hashlib.sha256(binding_raw).hexdigest()
        bundle['bindings'].insert(0,dict(payload=base64.b64encode(binding_raw).decode(),authorization=sign(self.provider,self.f.creator,'email-next/device-binding/v0',binding_raw),possession=sign(self.provider,self.f.creator,'email-next/device-possession/v0',binding_raw)))
        state.update(record='b'*32,revision='3',previous=[head],bindings=[dict(b,digest=binding_digest) if b['device']==w['device'] else b for b in state['bindings']]);raw=encode_event(state);bundle['states'].insert(0,dict(payload=base64.b64encode(raw).decode(),signature=sign(self.provider,self.f.creator,'email-next/identity-state/v0',raw)))
        self.assertEqual(self.target.identity.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(raw).hexdigest(),time=self.time)['status'],'accepted-unverified')
        with self.assertRaisesRegex(ValueError,'unchanged witness binding'):self.recovery.receive(self.carriers,expected_predecessor=self.start,allowed=set(),time=self.time,policy=POLICY)


if __name__=='__main__':unittest.main()
