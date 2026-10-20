"""Configured transition handoff through the existing loopback sender worker."""
import json
import multiprocessing
import os
import unittest
from unittest.mock import patch
import test_group_transitions as groups
import test_sender_association as associations
from test_sender_release import LocalSMTP
from sender_release import SenderRelease
from sender_worker import SenderWorker
from control_release import ControlRelease,CONTRACT
from identity_store import IdentityStore
from transition_carrier import receive_mime
from event_encoding import encode_event

def child_control(path,binary,port,time,stage):
    identity=IdentityStore(path);sender=SenderRelease(identity,binary)
    with SenderWorker(sender) as worker:
        worker.submit_control('control1',port=port,time=time,crash=lambda where:os._exit(81) if where==stage else None,retry_uncertain=True)
    os._exit(82)

class ControlReleaseTests(groups.GroupTransitionTests):
    def setUp(self):
        super().setUp();self.sender=SenderRelease(self.ga.identity,self.provider);self.sender.configure(expected_revision=0)
        self.control=ControlRelease(self.sender);self.target=dict(mailbox='bob@example.invalid',principal=self.b['principal'],device=self.b['device'])
        self.ident=self.prepared()
    def decide(self):self.ga.decide(self.ident,allowed=self.allowed,time=self.time)
    def prepare_control(self,**kwargs):
        return self.control.prepare('control1',self.ident,key=self.a['key'],envelope_sender='alice@example.invalid',recipients=kwargs.pop('recipients',[self.target]),time=self.time,**kwargs)
    def test_no_decision_or_wrong_recipient_opens_no_socket(self):
        with patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No unapproved socket')):
            with self.assertRaisesRegex(ValueError,'No decided'):self.prepare_control()
            with SenderWorker(self.sender) as worker:
                with self.assertRaisesRegex(ValueError,'Not prepared'):worker.submit_control('control1',port=1,time=self.time)
        self.decide()
        with self.assertRaisesRegex(ValueError,'outside predecessor'):self.prepare_control(recipients=[dict(self.target,principal=self.phone['principal'],device=self.phone['device'])])
    def test_real_control_receive_and_application_id_are_separate(self):
        self.decide();wire=self.prepare_control();self.assertEqual(self.prepare_control(),wire)
        server=LocalSMTP()
        with SenderWorker(self.sender) as worker:outcome=worker.submit_control('control1',port=server.port,time=self.time)
        server.done();self.assertEqual(outcome['state'],'accepted');self.assertEqual(server.wire,wire)
        self.assertEqual(receive_mime(self.gb,wire,allowed=self.allowed,time=self.time),'accepted')
        # The same local label cannot cause cross-kind attempt suppression.
        event=dict(version='0',purpose='contribution',event='e'*32,conversation='2'*32,principal=self.a['principal'],audience=sorted([self.a['principal'],self.b['principal'],self.c['principal']]),operation=dict(kind='message',text='hello',replyTo=[]))
        self.sender.prepare('control1',encode_event(event),key=self.a['key'],envelope_sender='alice@example.invalid',recipients=['bob@example.invalid'],time=self.time)
        app=LocalSMTP()
        with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit('control1',port=app.port,time=self.time)['state'],'accepted')
        app.done();self.assertEqual({r[0] for r in self.ga.db.execute('SELECT kind FROM sender_attempts')},{CONTRACT,'application-v0'})
    def test_lost_committer_send_authority_blocks_before_socket(self):
        self.decide();self.prepare_control();self.strip_committer_send(self.ga.identity)
        with SenderWorker(self.sender) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No revoked socket')):
            with self.assertRaises(ValueError):worker.submit_control('control1',port=1,time=self.time)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM sender_attempts').fetchone()[0],0)
    def test_policy_change_after_release_aborts_before_data(self):
        self.decide();self.prepare_control();server=LocalSMTP()
        def change(stage):
            if stage=='after-release':self.sender.configure(expected_revision=1,trust_policy='require-verification')
        with SenderWorker(self.sender) as worker:result=worker.submit_control('control1',port=server.port,time=self.time,crash=change)
        server.done();self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(server.wire)
    def test_association_change_after_release_aborts_before_data(self):
        self.decide();self.binary=self.provider;self.identity=self.ga.identity;self.sequence=0;self.mailbox='bob@example.invalid'
        target=associations.SenderAssociationTests.observe(self,self.b,self.mailbox)
        associations.SenderAssociationTests.decision(self,'first-contact',self.b['principal'],None)
        self.prepare_control(association_targets=[target]);server=LocalSMTP()
        def change(stage):
            if stage=='after-release':associations.SenderAssociationTests.decision(self,'disable',self.b['principal'],'1')
        with SenderWorker(self.sender) as worker:result=worker.submit_control('control1',port=server.port,time=self.time,crash=change)
        server.done();self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(server.wire)
    def test_process_exit_and_uncertain_retry_retain_exact_control(self):
        self.decide();wire=self.prepare_control();ctx=multiprocessing.get_context('spawn')
        child=ctx.Process(target=child_control,args=(self.root/'a.sqlite',self.provider,1,self.time,'after-release'));child.start();child.join(20)
        self.assertEqual(child.exitcode,81)
        with SenderWorker(self.sender) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No implicit retry')):
            with self.assertRaisesRegex(ValueError,'Uncertain'):worker.submit_control('control1',port=1,time=self.time)
        server=LocalSMTP();child=ctx.Process(target=child_control,args=(self.root/'a.sqlite',self.provider,server.port,self.time,'after-final-response'));child.start();child.join(20)
        self.assertEqual(child.exitcode,81);server.done();self.assertEqual(server.wire,wire)
        with SenderWorker(self.sender) as worker:
            with self.assertRaisesRegex(ValueError,'Uncertain'):worker.submit_control('control1',port=1,time=self.time)
            retry=LocalSMTP();result=worker.submit_control('control1',port=retry.port,time=self.time,retry_uncertain=True);retry.done()
        self.assertEqual(result['state'],'accepted');self.assertEqual(retry.wire,wire)
        self.assertEqual(receive_mime(self.gb,wire,allowed=self.allowed,time=self.time),'accepted')
        self.assertEqual(receive_mime(self.gb,wire,allowed=set(),time=self.time),'accepted')
    def test_new_epoch_holds_historical_control_and_partial_retry_scope(self):
        self.decide();recipients=[self.target,dict(mailbox='carol@example.invalid',principal=self.c['principal'],device=self.c['device'])]
        wire=self.prepare_control(recipients=recipients);first=LocalSMTP(rcpt=[b'250 first\r\n',b'450 later\r\n'])
        with SenderWorker(self.sender) as worker:
            result=worker.submit_control('control1',port=first.port,time=self.time);first.done()
            second=LocalSMTP();result=worker.submit_control('control1',port=second.port,time=self.time);second.done()
            self.assertEqual(result['result']['acceptedRecipients'],['carol@example.invalid']);self.assertEqual(second.wire,wire)
        # A separately prepared historical item remains held under this intermediate restriction.
        self.control.prepare('historical',self.ident,key=self.a['key'],envelope_sender='alice@example.invalid',recipients=[self.target],time=self.time)
        newer=self.ga.prepare([]);self.ga.decide(newer,allowed=set(),time=self.time)
        with SenderWorker(self.sender) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No stale socket')):
            with self.assertRaisesRegex(ValueError,'Changed group metadata'):worker.submit_control('historical',port=1,time=self.time)

for name in vars(groups.GroupTransitionTests):
    if name.startswith('test_'):setattr(ControlReleaseTests,name,None)
if __name__=='__main__':unittest.main()
