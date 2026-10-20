import json
import multiprocessing
import os
import unittest
from pathlib import Path
from unittest.mock import patch
import test_application_invitation as fixtures
from identity_store import IdentityStore
from sender_release import SenderRelease
from sender_worker import SenderWorker
from application_invitation_release import ApplicationInvitationRelease
from passive_discovery import decode_passive_discovery
from passive_discovery_verify import verify_passive_discovery
from invitation_mime import select
from test_sender_release import LocalSMTP
from event_encoding import encode_event
from mls_mime import unpack

def submit_child(path,binary,port,time,point):
    identity=IdentityStore(path);sender=SenderRelease(identity,binary)
    with SenderWorker(sender) as worker:worker.submit_initial_invitation('invitation1',port=port,time=time,crash=lambda stage:os._exit(88) if stage==point else None)

class InitialReleaseTests(unittest.TestCase):
    def setUp(self):
        self.receiver_fixture=fixtures.ApplicationInvitationTests();self.receiver_fixture.setUp();self.f=self.receiver_fixture.f
        self.path=Path(self.f.temp.name)/'creator.sqlite';self.identity=IdentityStore(self.path)
        for device in self.f.devices:self.identity.observe(device['record'],first_contact_policy='allow-unverified')
        self.sender=SenderRelease(self.identity,self.f.binary);self.sender.configure(expected_revision=0)
        self.release=ApplicationInvitationRelease(self.sender)
        for i,(device,choice) in enumerate(zip(self.f.devices,self.f.selected)):
            self.assertEqual(verify_passive_discovery(choice['wrapper'],self.identity,time=self.f.time,trust_policy='allow-unverified')['status'],'snapshot-authorized-unverified')
            d=decode_passive_discovery(choice['wrapper'])
            self.sender.associations.observe_validated_batch([dict(assertion=d['assertion']['octets'],signature=d['signature'],signingKey=bytes.fromhex(device['key']),outerFrom=[choice['mailbox']],sourceId='creator-fixture',parserRevision='0',observedAt=self.f.time['earliest'])])
            self.sender.associations.decide(decision_id=str(i+1)*32,mailbox=choice['mailbox'],expected_generation=None,kind='first-contact',principal=device['principal'],actor='configured-policy',policy_revision='1',trust_policy='allow-unverified',time=self.f.time)
    def tearDown(self):self.identity.close();self.receiver_fixture.tearDown()
    def prepare(self,**overrides):
        args=dict(device=self.f.devices[0],selected=self.f.selected,application=self.f.context['application'],conversation='2'*32,not_before=self.f.time['earliest'],not_after=str(int(self.f.time['latest'])+300),time=self.f.time);args.update(overrides)
        return self.release.prepare('invitation1',**args)
    def accept(self,wire):return self.receiver_fixture.accept(select(wire))
    def test_actual_preparation_smtp_admission_and_protected_followup(self):
        wire=self.prepare();self.assertEqual(self.prepare(),wire)
        smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit_initial_invitation('invitation1',port=smtp.port,time=self.f.time)['state'],'accepted')
        smtp.done();self.assertEqual(smtp.wire,wire);self.assertEqual(self.accept(wire)['status'],'admitted-unverified')
        event=dict(version='1',purpose='contribution',event='8'*32,conversation='2'*32,principal=self.f.devices[0]['principal'],audience=sorted(d['principal'] for d in self.f.devices),disclosures=[],operation=dict(kind='message',text='Hello through the admitted group.',replyTo=[]))
        message=self.sender.prepare('followup',encode_event(event),key=self.f.devices[0]['key'],envelope_sender=self.f.selected[0]['mailbox'],recipients=[self.f.selected[1]['mailbox']],time=self.f.time)
        self.assertEqual(self.receiver_fixture.admission.receiver.receive(unpack(message),time=self.f.time,trust_policy='allow-unverified')['status'],'projected-context-matched')
    def test_unprepared_no_socket_and_policy_change_before_data(self):
        with SenderWorker(self.sender) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No unprepared socket')):
            with self.assertRaisesRegex(ValueError,'Not prepared'):worker.submit_initial_invitation('invitation1',port=1,time=self.f.time)
        self.prepare();smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:result=worker.submit_initial_invitation('invitation1',port=smtp.port,time=self.f.time,crash=lambda stage:self.sender.configure(expected_revision=1) if stage=='after-release' else None)
        smtp.done();self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(smtp.wire)
    def test_preparation_failure_rolls_back_initial_state_and_package_use(self):
        with self.assertRaises(RuntimeError):self.prepare(crash=lambda stage:(_ for _ in ()).throw(RuntimeError('crash')))
        for table in ['mls_checkpoint','initial_invitation_prepared','initial_application_packages','mls_application_agreement']:
            self.assertEqual(self.identity.db.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
        self.prepare()
    def test_process_exit_uncertainty_preserves_exact_invitation(self):
        wire=self.prepare();smtp=LocalSMTP()
        child=multiprocessing.get_context('spawn').Process(target=submit_child,args=(self.path,self.f.binary,smtp.port,self.f.time,'after-final-response'))
        child.start();child.join(20);self.assertEqual(child.exitcode,88);smtp.done();self.assertEqual(smtp.wire,wire)
        with SenderWorker(self.sender) as worker:
            with patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No implicit retry')):
                with self.assertRaisesRegex(ValueError,'Uncertain'):worker.submit_initial_invitation('invitation1',port=1,time=self.f.time)
            again=LocalSMTP();result=worker.submit_initial_invitation('invitation1',port=again.port,time=self.f.time,retry_uncertain=True);again.done()
        self.assertEqual(again.wire,wire);self.assertEqual(result['state'],'accepted')
        accepted=self.accept(wire);self.assertEqual(self.accept(again.wire),accepted)

    def test_invitation_lower_bound_is_checked_before_initial_state(self):
        import base64
        binding=json.loads(base64.b64decode(self.f.devices[0]['record']['binding']))
        with self.assertRaisesRegex(ValueError,'proof expiry'):
            self.prepare(not_before=str(int(binding['notBefore'])-1))
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM initial_application_packages').fetchone()[0],0)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM initial_invitation_prepared').fetchone()[0],0)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0],0)
