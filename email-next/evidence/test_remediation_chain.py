import base64
import hashlib
import json
import unittest
import test_group_removal as removal_fixture
from provider_mls import sign
from event_encoding import encode_event
from transition_carrier import encode_transition
from remediation_chain import RemediationChain,POLICY
from commit_history import CommitHistory

class RemediationTests(unittest.TestCase):
    setUp=removal_fixture.RemovalTests.setUp
    tearDown=removal_fixture.RemovalTests.tearDown
    store=removal_fixture.RemovalTests.store
    prepared=removal_fixture.RemovalTests.prepared
    remove=removal_fixture.RemovalTests.remove
    def chain(self):
        start=self.gb.live()['snapshot']['predecessor']
        if hasattr(self,'application_profile'):
            self.ga.receiver.application_agreement.configure_device(self.ga.live()['snapshot']['group'],self.phone['identity'],self.phone['key'],self.application_profile)
        ident=self.prepared();self.ga.decide(ident,allowed=self.allowed,time=self.time)
        self.intermediate=self.ga.live()
        added=json.loads(self.ga.db.execute('SELECT state FROM gt_decision WHERE digest=?',(ident,)).fetchone()[0])
        bundle=json.loads(json.dumps(self.bundle));state=json.loads(base64.b64decode(bundle['states'][0]['payload']))
        state.update(record='9'*32,revision='2',previous=[self.head],revoked=[self.phone['device']],bindings=[r for r in state['bindings'] if r['device']!=self.phone['device']])
        raw=encode_event(state);bundle['states'].insert(0,dict(payload=base64.b64encode(raw).decode(),signature=sign(self.provider,self.a,'email-next/identity-state/v0',raw)))
        for g in (self.ga,self.gb):self.assertEqual(g.identity.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(raw).hexdigest(),time=self.time)['status'],'accepted-unverified')
        removed=self.remove(self.phone)
        self.recovery=RemediationChain(self.gb)
        return start,[encode_transition(added),encode_transition(removed)]
    def run_chain(self,start,carriers,**kwargs):
        return self.recovery.receive(carriers,allowed=self.allowed,time=self.time,expected_predecessor=start,**kwargs)
    def test_atomic_recovery_and_public_only_receipts(self):
        start,carriers=self.chain();old=self.gb.live()
        result=self.run_chain(start,carriers,policy=POLICY)
        self.assertEqual(result['status'],'accepted-remediation')
        self.assertEqual(self.gb.live()['snapshot'],self.ga.live()['snapshot'])
        self.assertEqual(self.gb.live()['revision'],old['revision']+1)
        import membership_episodes
        self.assertFalse(membership_episodes.permits(self.gb.db,old['snapshot']['group'],self.a['identity'],self.a['key'],str(int(old['snapshot']['epoch'])+1)))
        self.assertTrue(membership_episodes.permits(self.gb.db,old['snapshot']['group'],self.a['identity'],self.a['key'],result['epoch']))
        self.assertEqual(self.run_chain(start,carriers,policy=POLICY),result)
        self.assertEqual(self.gb.db.execute('SELECT count(*) FROM gt_decision').fetchone()[0],0)
        for raw, in self.gb.db.execute('SELECT record FROM mls_remediation_step'):
            record=json.loads(raw);self.assertNotIn('checkpoint',record);self.assertNotIn('authorization',record)
        self.assertEqual(self.gb.db.execute('SELECT end_epoch FROM mls_membership_episode WHERE identity=?',(self.phone['identity'],)).fetchone()[0],result['epoch'])
        history=CommitHistory(self.gb,max_count=8,max_bytes=4000000)
        with self.assertRaisesRegex(ValueError,'History unavailable'):history.path(start,target_identity=self.b['identity'],target_key=self.b['key'],time=self.time,trust_policy='allow-unverified')
    def test_retired_intermediate_ciphertext_and_live_final_crypto(self):
        start,carriers=self.chain()
        from provider_mls import call
        from mls_receive import worker_call,FORMAT
        def send(state):
            return call(self.provider,op='send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.a['key'],application=b'opaque probe'.hex())['wire']
        intermediate=send(self.intermediate)
        self.run_chain(start,carriers,policy=POLICY)
        final=self.gb.live()
        def receive(wire):return worker_call(self.provider.with_name('receive-staged'),dict(format=FORMAT,group=final['snapshot']['group'],checkpoint=final['checkpoint'],wire=wire))
        self.assertNotEqual(receive(intermediate)['status'],'authenticated-application')
        self.assertEqual(receive(send(self.ga.live()))['status'],'authenticated-application')

    def test_explicit_policy_required(self):
        start,carriers=self.chain();old=self.gb.live()
        self.assertEqual(self.run_chain(start,carriers)['status'],'held');self.assertEqual(self.gb.live(),old)
    def test_incomplete_and_malformed_leave_checkpoint_unchanged(self):
        start,carriers=self.chain();old=self.gb.live()
        with self.assertRaisesRegex(ValueError,'final roster'):self.run_chain(start,carriers[:1],policy=POLICY)
        with self.assertRaises(ValueError):self.run_chain(start,list(reversed(carriers)),policy=POLICY)
        self.assertEqual(self.gb.live(),old)
        self.assertEqual(self.run_chain(start,carriers,policy=POLICY)['status'],'accepted-remediation')
    def test_process_crash_reopens_only_old_or_final_state(self):
        import multiprocessing,os
        from identity_store import IdentityStore
        from group_transitions import GroupTransitions
        start,carriers=self.chain();old=self.gb.live()
        def child(point):
            for store in self.stores:store.close()
            store=IdentityStore(self.root/'b.sqlite')
            recovery=RemediationChain(GroupTransitions(store,self.binary,self.b))
            recovery.receive(carriers,allowed=self.allowed,time=self.time,expected_predecessor=start,policy=POLICY,crash=lambda where:os._exit(91) if where==point else None)
        for point in ('before-commit','after-commit'):
            process=multiprocessing.get_context('fork').Process(target=child,args=(point,));process.start();process.join(20)
            if process.is_alive():process.terminate();process.join();self.fail('Child timeout')
            self.assertEqual(process.exitcode,91)
            if point=='before-commit':self.assertEqual(self.gb.live(),old)
            else:self.assertEqual(self.gb.live()['snapshot'],self.ga.live()['snapshot'])
        self.assertEqual(self.run_chain(start,carriers,policy=POLICY)['status'],'accepted-remediation')

    def test_concurrent_connections_install_once(self):
        import multiprocessing
        from identity_store import IdentityStore
        from group_transitions import GroupTransitions
        start,carriers=self.chain();revision=self.gb.live()['revision'];ctx=multiprocessing.get_context('fork');queue=ctx.Queue()
        def child():
            for store in self.stores:store.close()
            store=IdentityStore(self.root/'b.sqlite')
            try:
                recovery=RemediationChain(GroupTransitions(store,self.binary,self.b))
                queue.put(recovery.receive(carriers,allowed=self.allowed,time=self.time,expected_predecessor=start,policy=POLICY)['status'])
            finally:store.close()
        children=[ctx.Process(target=child) for _ in range(2)]
        for process in children:process.start()
        for process in children:
            process.join(20)
            if process.is_alive():process.terminate();process.join();self.fail('Child timeout')
            self.assertEqual(process.exitcode,0)
        self.assertEqual([queue.get(timeout=1) for _ in children],['accepted-remediation']*2)
        queue.close();queue.join_thread()
        self.assertEqual(self.gb.live()['revision'],revision+1)
        self.assertEqual(self.gb.db.execute('SELECT count(*) FROM mls_remediation_receipt').fetchone()[0],1)

    def test_unpermitted_addition_and_corrupt_final_commit_do_not_poison_retry(self):
        start,carriers=self.chain();old=self.gb.live()
        with self.assertRaisesRegex(ValueError,'Unauthorized addition'):self.recovery.receive(carriers,allowed=set(),time=self.time,expected_predecessor=start,policy=POLICY)
        last=json.loads(carriers[-1]);wire=bytearray(base64.b64decode(last['commit']));wire[-1]^=1;last['commit']=base64.b64encode(wire).decode()
        with self.assertRaises(ValueError):self.run_chain(start,[carriers[0],encode_event(last)],policy=POLICY)
        self.assertEqual(self.gb.live(),old)
        self.assertEqual(self.run_chain(start,carriers,policy=POLICY)['status'],'accepted-remediation')

    def test_crash_transaction_and_retry(self):
        start,carriers=self.chain();old=self.gb.live()
        def crash(point):raise RuntimeError(point)
        with self.assertRaisesRegex(RuntimeError,'before-commit'):self.run_chain(start,carriers,policy=POLICY,crash=crash)
        self.assertEqual(self.gb.live(),old)
        self.assertEqual(self.gb.db.execute('SELECT count(*) FROM mls_remediation_step').fetchone()[0],0)
        self.assertEqual(self.run_chain(start,carriers,policy=POLICY)['status'],'accepted-remediation')
    def test_pending_hold_does_not_consume_crypto_then_chain_completes(self):
        start,carriers=self.chain();old=self.gb.live()
        from transition_carrier import receive_mime
        from transition_mime import package
        self.assertEqual(receive_mime(self.gb,package(carriers[0],sender='a@example.test',recipient='b@example.test'),allowed=self.allowed,time=self.time),'pending-remediation')
        self.assertEqual(self.gb.live(),old)
        self.assertEqual(self.run_chain(start,carriers,policy=POLICY)['status'],'accepted-remediation')
        self.assertEqual(self.gb.db.execute('SELECT count(*) FROM gt_pending').fetchone()[0],0)

    def test_legacy_rejected_commit_is_not_reinterpreted(self):
        start,carriers=self.chain()
        from transition_carrier import parse
        # Reproduce the previous receive behavior to construct a legacy row.
        from unittest.mock import patch
        with patch('remediation_chain.should_hold',return_value=False):
            self.assertEqual(self.gb.receive(parse(carriers[0])[1],allowed=self.allowed,time=self.time),'rejected-policy')
        old=self.gb.live()
        with self.assertRaisesRegex(ValueError,'Legacy rejected'):self.run_chain(start,carriers,policy=POLICY)
        self.assertEqual(self.gb.live(),old)

class ApplicationRemediationTests(RemediationTests):
    application_profile={'envelopeVersion':'1','operations':['answer','message','question']}

class TupleRemediationTests(ApplicationRemediationTests):
    application_profile={'envelopeVersion':'1','payload':'mime-contribution-v0','operations':['message']}
    context_version='3'
    def setUp(self):
        from unittest.mock import patch
        import test_group_transitions as fixture
        original=fixture.encode_event
        def encode(value):
            if value.get('purpose')=='conversation-context':value=dict(value,version=self.context_version)
            return original(value)
        with patch.object(fixture,'encode_event',side_effect=encode):super().setUp()

class RichRemediationTests(TupleRemediationTests):
    application_profile={'envelopeVersion':'1','payload':'mime-rich-v0','operations':['rich-message']}
    context_version='4'

if __name__=='__main__':unittest.main()

class PendingRecoveryTests(unittest.TestCase):
    setUp=removal_fixture.RemovalTests.setUp;tearDown=removal_fixture.RemovalTests.tearDown
    store=removal_fixture.RemovalTests.store;prepared=removal_fixture.RemovalTests.prepared
    remove=removal_fixture.RemovalTests.remove
    def test_authenticated_pending_removed_sender_never_promotes(self):
        from provider_mls import call
        added=self.prepared();self.ga.decide(added,allowed=self.allowed,time=self.time)
        result=json.loads(self.ga.db.execute('SELECT state FROM gt_decision WHERE digest=?',(added,)).fetchone()[0])
        self.gb.receive(bytes.fromhex(result['wire']),allowed=self.allowed,time=self.time)
        phone=call(self.binary,op='join',checkpoint=self.phone['checkpoint'],key=self.phone['key'],welcome=result['welcome'])
        event=dict(version='0',purpose='contribution',event='6'*32,conversation='2'*32,principal=self.phone['principal'],audience=sorted([self.a['principal'],self.b['principal'],self.c['principal']]),operation=dict(kind='answer',question=dict(principal=self.phone['principal'],conversation='2'*32,event='5'*32),option='7'*32,replaces=[]))
        message=call(self.provider,op='send',checkpoint=phone['checkpoint'],group=phone['snapshot']['group'],key=self.phone['key'],application=encode_event(event).hex())
        self.assertEqual(self.gb.receiver.receive(bytes.fromhex(message['wire']),time=self.time,trust_policy='allow-unverified')['status'],'pending')
        start=self.gb.live()['snapshot']['predecessor'];update=self.ga.prepare([]);self.ga.decide(update,allowed=set(),time=self.time)
        first=json.loads(self.ga.db.execute('SELECT state FROM gt_decision WHERE digest=?',(update,)).fetchone()[0])
        bundle=json.loads(json.dumps(self.bundle));state=json.loads(base64.b64decode(bundle['states'][0]['payload']));state.update(record='9'*32,revision='2',previous=[self.head],revoked=[self.phone['device']],bindings=[r for r in state['bindings'] if r['device']!=self.phone['device']]);raw=encode_event(state);bundle['states'].insert(0,dict(payload=base64.b64encode(raw).decode(),signature=sign(self.provider,self.a,'email-next/identity-state/v0',raw)))
        for g in (self.ga,self.gb):self.assertEqual(g.identity.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(raw).hexdigest(),time=self.time)['status'],'accepted-unverified')
        last=self.remove(self.phone);recovery=RemediationChain(self.gb)
        recovery.receive([encode_transition(first),encode_transition(last)],allowed=set(),time=self.time,expected_predecessor=start,policy=POLICY)
        from unittest.mock import patch
        with patch('mls_receive.worker_call',side_effect=AssertionError('No re-decryption')):
            values=self.gb.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')['states'].values()
        self.assertTrue(all(v.startswith('held:') for v in values));self.assertEqual(self.gb.db.execute('SELECT count(*) FROM contributions').fetchone()[0],0)
        import membership_episodes
        self.assertFalse(membership_episodes.permits(self.gb.db,phone['snapshot']['group'],self.phone['identity'],self.phone['key'],phone['snapshot']['epoch']))
        # Fresh cryptographic package alone cannot restore revoked account authority.
        fresh=dict(self.phone,**call(self.provider,op='fresh-package',checkpoint=self.phone['checkpoint'],key=self.phone['key'],identity=self.phone['identity']))
        candidate=self.ga.prepare([fresh['package']])
        with self.assertRaisesRegex(ValueError,'Current identity'):self.ga.decide(candidate,allowed=self.allowed,time=self.time)
        self.assertFalse(membership_episodes.permits(self.gb.db,phone['snapshot']['group'],self.phone['identity'],self.phone['key'],phone['snapshot']['epoch']))
