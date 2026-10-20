import json,unittest
import test_quorum_release as release_tests
from quorum_release import QuorumRelease,CONTROL,TERMINAL,INVITATION
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from admitted_quorum import AdmittedQuorum
import ordering_carrier

class QuorumTerminalTests(unittest.TestCase):
    setUp=release_tests.QuorumReleaseTests.setUp;tearDown=release_tests.QuorumReleaseTests.tearDown
    endpoint=release_tests.QuorumReleaseTests.endpoint;prepare=release_tests.QuorumReleaseTests.prepare;join=release_tests.QuorumReleaseTests.join;certify=release_tests.QuorumReleaseTests.certify;event=release_tests.QuorumReleaseTests.event
    prepare_join=release_tests.QuorumReleaseTests.prepare_join
    def test_combined_add_remove_terminal_handoff_and_replay(self):
        self.prepare_join(remove=True);decision=self.author_group.live()[0];controls=[];terminal_wire=None
        source=next(c['mailbox'] for d,c in zip(self.f.devices,self.selected) if d is self.f.creator)
        with SenderWorker(self.sender) as worker:
            for i,(d,c) in enumerate(zip(self.f.devices,self.selected)):
                if d is self.f.creator:continue
                terminal=d['identity']==self.removed['identity'];kind=TERMINAL if terminal else CONTROL;name='terminalcontrol'+str(i);controls.append(name)
                adapter=QuorumRelease(self.sender,self.author_group,kind)
                wire=adapter.prepare(name,decision,envelope_sender=source,recipients=[dict(mailbox=c['mailbox'],principal=d['principal'],device=d['device'])],association_targets=[dict(mailbox=c['mailbox'],generation=c['generation'],principal=d['principal'],observation=c['digest'])],time=self.time)
                smtp=LocalSMTP();method=worker.submit_quorum_terminal if terminal else worker.submit_quorum_control
                self.assertEqual(method(name,group=self.author_group,port=smtp.port,time=self.time)['state'],'accepted');smtp.done()
                if terminal:terminal_wire=wire
        adapter=QuorumRelease(self.sender,self.author_group,INVITATION)
        self.sender.db.execute('BEGIN IMMEDIATE')
        try:
            _,record=adapter._decision(decision);adapter._dependencies(decision,controls,record,accepted=True)
        finally:self.sender.db.execute('ROLLBACK')
        target=AdmittedQuorum(self.senders[self.removed['device']].receiver,self.worker,self.removed)
        self.assertIsNotNone(terminal_wire)
        from provider_mls import call
        carrier=ordering_carrier.select_object(terminal_wire)
        candidate=carrier['candidate'];before=target.live()[1]
        wrong=call(self.worker,op='receive-quorum',checkpoint=before['checkpoint'],group=before['snapshot']['group'],key=self.removed['key'],wire=candidate['plan']['commit'],expectedContext=before['snapshot']['predecessor'])
        self.assertTrue(wrong['selfRemoved']);self.assertFalse(wrong['terminalPublicFieldsMatch'])
        import copy
        malformed=copy.deepcopy(carrier);malformed['candidate']['plan']['commit']=('01' if malformed['candidate']['plan']['commit'][:2]!='01' else '02')+malformed['candidate']['plan']['commit'][2:]
        from ordering_certificates import encode
        with self.assertRaises(ValueError):ordering_carrier.receive(target,ordering_carrier.package(encode(malformed)),time=self.time)
        for mode in ('predecessor','certificate'):
            altered=copy.deepcopy(carrier)
            if mode=='predecessor':altered['candidate']['plan']['scope']['previousDecision']='f'*64
            else:altered['proof']=altered['proof'][:-2]+'00'
            with self.subTest(mode=mode),self.assertRaises(ValueError):ordering_carrier.receive(target,ordering_carrier.package(encode(altered)),time=self.time)
        self.assertEqual(target.live()[1]['snapshot']['epoch'],'1')
        received=ordering_carrier.receive(target,terminal_wire,time=self.time);self.assertEqual(received['status'],'accepted')
        self.assertEqual(ordering_carrier.receive(target,terminal_wire,time=self.time),dict(received,status='already-installed'))
        self.assertEqual(target.db.execute('SELECT status FROM mls_group_instances').fetchone()[0],'inactive')
        with self.assertRaises(ValueError):target.live()
        self.assertIsNotNone(target.db.execute('SELECT 1 FROM mls_group_inactive').fetchone())
        from event_encoding import encode_event
        with self.assertRaises(ValueError):self.senders[self.removed['device']].prepare('afterterminal',encode_event(self.event(self.removed,'9')),key=self.removed['key'],envelope_sender='removed@example.invalid',recipients=[source],time=self.time)
    def test_remove_only_route_withdrawal_before_data(self):
        self.join()
        from ordering_mls import ProviderKey
        indices=[int(m['index']) for m in self.author_group.live()[1]['snapshot']['members'] if m['identity']==self.removed['identity']]
        candidate=self.author_group.stage(ProviderKey(self.provider,self.f.creator),time=self.time,removals=indices);proof=self.certify(candidate)
        for group in self.groups:decision=group.install(candidate,proof,time=self.time)
        d=self.removed;c=next(c for d0,c in zip(self.f.devices,self.selected) if d0 is d)
        route=dict(mailbox=c['mailbox'],generation=c['generation'],principal=d['principal'],observation=c['digest'])
        adapter=QuorumRelease(self.sender,self.author_group,TERMINAL)
        wire=adapter.prepare('removeonly',decision,envelope_sender='creator@example.invalid',recipients=[dict(mailbox=c['mailbox'],principal=d['principal'],device=d['device'])],association_targets=[route],time=self.time)
        def withdraw(stage):
            if stage=='after-release':self.sender.associations.decide(decision_id='c'*32,mailbox=c['mailbox'],expected_generation=c['generation'],kind='disable',principal=d['principal'],actor='local-user',policy_revision='1',trust_policy='allow-unverified',time=self.time)
        smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:result=worker.submit_quorum_terminal('removeonly',group=self.author_group,port=smtp.port,time=self.time,crash=withdraw)
        smtp.done();self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(smtp.wire)
        target=AdmittedQuorum(self.senders[d['device']].receiver,self.worker,d)
        self.assertEqual(ordering_carrier.receive(target,wire,time=self.time)['status'],'accepted')
        self.assertEqual(target.db.execute('SELECT status FROM mls_group_instances').fetchone()[0],'inactive')

if __name__=='__main__':unittest.main()
