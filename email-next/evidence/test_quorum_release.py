import json,unittest
from passive_discovery import decode_passive_discovery
from quorum_release import QuorumRelease,CONTROL,INVITATION,INVITATION7
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from established_invitation_mime import select
from quorum_join import import_anchor
from admitted_quorum import AdmittedQuorum
import ordering_carrier
import test_quorum_join as join_tests

class QuorumReleaseTests(unittest.TestCase):
    setUp=join_tests.QuorumJoinTests.setUp;tearDown=join_tests.QuorumJoinTests.tearDown
    endpoint=join_tests.QuorumJoinTests.endpoint;prepare=join_tests.QuorumJoinTests.prepare;join=join_tests.QuorumJoinTests.join;certify=join_tests.QuorumJoinTests.certify;event=join_tests.QuorumJoinTests.event;prepare_join=join_tests.QuorumJoinTests.prepare_join
    def prepare_release(self):
        self.prepare_join();self.decision=self.author_group.live()[0];self.control=QuorumRelease(self.sender,self.author_group,CONTROL);self.invite=QuorumRelease(self.sender,self.author_group,INVITATION7 if getattr(self,'exchange_assertion_version','6')=='7' else INVITATION);self.controls=[]
        self.source=next(c['mailbox'] for d,c in zip(self.f.devices,self.selected) if d is self.f.creator)
        for i,(d,c) in enumerate(zip(self.f.devices,self.selected)):
            if d is self.f.creator:continue
            name='quorumcontrol'+str(i);self.controls.append(name)
            self.control.prepare(name,self.decision,envelope_sender=self.source,recipients=[dict(mailbox=c['mailbox'],principal=d['principal'],device=d['device'])],association_targets=[dict(mailbox=c['mailbox'],generation=c['generation'],principal=d['principal'],observation=c['digest'])],time=self.time)
        d=decode_passive_discovery(self.new_proof);mailbox=d['assertion']['value']['mailbox'];self.sender.associations.observe_validated_batch([dict(assertion=d['assertion']['octets'],signature=d['signature'],signingKey=bytes.fromhex(self.new['key']),outerFrom=[mailbox],sourceId='quorum-release-test',parserRevision='0',observedAt=self.time['earliest'])]);self.sender.associations.decide(decision_id='e'*32,mailbox=mailbox,expected_generation=None,kind='first-contact',principal=self.new['principal'],actor='configured-policy',policy_revision='1',trust_policy='allow-unverified',time=self.time)
        self.invitation_wire=self.invite.prepare('quorumwelcome',self.decision,invitation='f'*32,controls=self.controls,envelope_sender=self.source,recipients=[dict(mailbox=mailbox,principal=self.new['principal'],device=self.new['device'])],association_targets=[dict(mailbox=mailbox,generation='1',principal=self.new['principal'],observation=d['assertion']['digest'])],time=self.time)
    def test_durable_ordered_controls_uncertain_retry_then_invitation(self):
        self.prepare_release()
        with SenderWorker(self.sender) as worker:
            with self.assertRaisesRegex(ValueError,'handoff unresolved'):worker.submit_quorum_invitation('quorumwelcome',group=self.author_group,port=1,time=self.time)
            first=self.controls[0];smtp=LocalSMTP(drop=True);self.assertEqual(worker.submit_quorum_control(first,group=self.author_group,port=smtp.port,time=self.time)['state'],'uncertain');smtp.done();original=smtp.wire
            with self.assertRaisesRegex(ValueError,'Uncertain'):worker.submit_quorum_control(first,group=self.author_group,port=1,time=self.time)
            smtp=LocalSMTP();self.assertEqual(worker.submit_quorum_control(first,group=self.author_group,port=smtp.port,time=self.time,retry_uncertain=True)['state'],'accepted');smtp.done();self.assertEqual(smtp.wire,original)
            with self.assertRaisesRegex(ValueError,'Already handed off'):worker.submit_quorum_control(first,group=self.author_group,port=1,time=self.time)
            for name in self.controls[1:]:
                smtp=LocalSMTP();self.assertEqual(worker.submit_quorum_control(name,group=self.author_group,port=smtp.port,time=self.time)['state'],'accepted');smtp.done()
            # The initial non-voting endpoint has not installed this Add yet.
            target=AdmittedQuorum(self.senders[self.removed['device']].receiver,self.worker,self.removed)
            self.assertIsNone(target.db.execute('SELECT 1 FROM qo_join_support').fetchone())
            row=self.sender.db.execute('SELECT wire FROM quorum_prepared WHERE evidence LIKE ?',(f'%{self.removed["device"]}%',)).fetchone();self.assertEqual(ordering_carrier.receive(target,row[0],time=self.time)['status'],'accepted')
            smtp=LocalSMTP();self.assertEqual(worker.submit_quorum_invitation('quorumwelcome',group=self.author_group,port=smtp.port,time=self.time)['state'],'accepted');smtp.done();self.assertEqual(smtp.wire,self.invitation_wire)
        import_anchor(self.new_identity,self.genesis,**self.anchor_args)
        self.assertEqual(self.admission.accept_message(select(smtp.wire),**self.args)['status'],'accepted-unverified')
        self.assertEqual(self.sender.db.execute('SELECT count(*) FROM sender_attempts WHERE delivery=?',(first,)).fetchone()[0],2)
        from event_encoding import encode_event
        from mls_mime import unpack
        self.principals=sorted(self.principals+[self.new['principal']])
        for sender,device,source,destination,receiver,ident in [(self.new_sender,self.new,'newjoiner@example.invalid',self.source,self.sender.receiver,'a'),(self.sender,self.f.creator,self.source,'newjoiner@example.invalid',self.new_sender.receiver,'b')]:
            sender.prepare('joined'+ident,encode_event(self.event(device,ident)),key=device['key'],envelope_sender=source,recipients=[destination],time=self.time)
            smtp=LocalSMTP()
            with SenderWorker(sender) as worker:self.assertEqual(worker.submit('joined'+ident,port=smtp.port,time=self.time)['state'],'accepted')
            smtp.done();self.assertEqual(receiver.receive(unpack(smtp.wire),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
    def test_policy_change_aborts_before_control_data(self):
        self.prepare_release();smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:
            result=worker.submit_quorum_control(self.controls[0],group=self.author_group,port=smtp.port,time=self.time,crash=lambda point:self.sender.configure(expected_revision=1) if point=='after-release' else None)
        smtp.done();self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(smtp.wire)

if __name__=='__main__':unittest.main()
