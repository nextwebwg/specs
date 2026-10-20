import json
import multiprocessing
import os
import unittest
from unittest.mock import patch
import test_group_removal as fixture
import test_historical_release as mappings
from test_sender_release import LocalSMTP
from commit_history import CommitHistory
from sender_release import SenderRelease
from sender_worker import SenderWorker
from control_release import ControlRelease
from established_invitation_release import EstablishedInvitationRelease
from established_invitation_mime import select
from established_invitation import EstablishedAdmission,b64
from identity_store import IdentityStore
from event_encoding import encode_event

def crashed_welcome(path,binary,device,port,time):
    from group_transitions import GroupTransitions
    identity=IdentityStore(path);group=GroupTransitions(identity,binary.with_name('group-transitions'),device)
    history=CommitHistory(group,max_count=8,max_bytes=4000000);sender=SenderRelease(identity,binary)
    with SenderWorker(sender) as worker:
        worker.submit_established_invitation('welcome',history=history,port=port,time=time,crash=lambda stage:os._exit(83) if stage=='after-final-response' else None)

class EstablishedReleaseTests(unittest.TestCase):
    tearDown=fixture.RemovalTests.tearDown
    store=fixture.RemovalTests.store
    prepared=fixture.RemovalTests.prepared
    remove=fixture.RemovalTests.remove
    observe_selected=mappings.HistoricalReleaseTests.observe_selected
    select_mapping=mappings.HistoricalReleaseTests.select_mapping
    def setUp(self):
        fixture.RemovalTests.setUp(self)
        self.history=CommitHistory(self.ga,max_count=8,max_bytes=4000000)
        self.decision=self.prepared();self.ga.decide(self.decision,allowed=self.allowed,time=self.time)
        self.sender=SenderRelease(self.ga.identity,self.provider);self.sender.configure(expected_revision=0)
        self.route=self.observe_selected(self.phone);self.select_mapping('first-contact',self.a['principal'],None)
        assertion,signature=self.ga.db.execute('SELECT assertion,signature FROM mailbox_observations WHERE digest=?',(self.route['observation'],)).fetchone()
        self.wrapper=encode_event(dict(payload=b64(assertion),signature=signature.hex(),identity=self.bundle))
        self.control=ControlRelease(self.sender)
        self.control.prepare('commit',self.decision,key=self.a['key'],envelope_sender='alice@example.invalid',recipients=[dict(mailbox='b@example.invalid',principal=self.b['principal'],device=self.b['device']),dict(mailbox='c@example.invalid',principal=self.c['principal'],device=self.c['device'])],time=self.time)
        self.adapter=EstablishedInvitationRelease(self.sender,self.history);self.wire=self.prepare()
    def prepare(self,delivery='welcome',**extra):
        args=dict(key=self.a['key'],creator_bundle=self.bundle,selected_wrapper=self.wrapper,association_target=self.route,predecessor_deliveries=['commit'],envelope_sender='alice@example.invalid',not_before=str(int(self.time['earliest'])-1),not_after=str(int(self.time['latest'])+30),time=self.time)
        args.update(extra);return self.adapter.prepare(delivery,self.decision,**args)
    def handoff(self,drop=False):
        with SenderWorker(self.sender) as worker:
            server=LocalSMTP(drop=drop);result=worker.submit_control('commit',port=server.port,time=self.time,retry_uncertain=True);server.done();return result
    def submit(self,**extra):
        with SenderWorker(self.sender) as worker:
            server=LocalSMTP();result=worker.submit_established_invitation('welcome',history=self.history,port=server.port,time=self.time,**extra);server.done();return result,server
    def blocked(self):
        with SenderWorker(self.sender) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No blocked socket')):
            with self.assertRaises(ValueError):worker.submit_established_invitation('welcome',history=self.history,port=1,time=self.time,retry_uncertain=True)
    def test_unavailable_uncertain_then_accepted_predecessor_handoff(self):
        self.blocked();self.assertEqual(self.handoff(drop=True)['state'],'uncertain');self.blocked()
        self.assertEqual(self.handoff()['state'],'accepted');result,server=self.submit();self.assertEqual(result['state'],'accepted');self.assertEqual(server.wire,self.wire)
        # Remote existing members have deliberately NOT processed the Commit.
        self.assertNotEqual(self.gb.live()['snapshot']['epoch'],self.ga.live()['snapshot']['epoch'])
        identity=IdentityStore(self.root/'newphone.sqlite');self.stores.append(identity)
        for peer in [self.a,self.b,self.c]:identity.observe(peer['record'],first_contact_policy='allow-unverified')
        identity.accept_successor(encode_event(self.bundle),candidate_digest=self.head,time=self.time)
        admission=EstablishedAdmission(identity,self.provider);admission.publish_local(self.phone)
        self.assertEqual(admission.accept_message(select(server.wire),target=self.phone,mailbox=self.route['mailbox'],allow_creator=self.a['principal'],expected_context=self.ctx,time=self.time)['status'],'accepted-unverified')
        with SenderWorker(self.sender) as worker:self.assertEqual(self.adapter.finish('welcome',worker=worker),'completed')
        self.assertEqual(self.ga.db.execute("SELECT count(*) FROM commit_history_pin WHERE owner='welcome:welcome'").fetchone()[0],0)
    def test_route_change_before_socket_and_predata(self):
        self.handoff()
        def disable(stage):
            if stage=='after-release':self.select_mapping('disable',self.a['principal'],'1')
        result,server=self.submit(crash=disable);self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(server.wire);self.blocked()
    def test_later_continuous_tip_allowed_but_predata_extension_aborts(self):
        self.handoff();later=self.ga.prepare([]);self.ga.decide(later,allowed=set(),time=self.time)
        def advance(stage):
            if stage=='after-release':
                ident=self.ga.prepare([]);self.ga.decide(ident,allowed=set(),time=self.time)
        result,server=self.submit(crash=advance);self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(server.wire)
        result,server=self.submit();self.assertEqual(result['state'],'accepted');self.assertEqual(server.wire,self.wire)
    def test_removed_target_cannot_release_original_welcome(self):
        self.handoff();self.remove(self.phone);self.blocked()
    def test_uncertain_welcome_exact_retry_and_cancel(self):
        self.handoff()
        with SenderWorker(self.sender) as worker:
            server=LocalSMTP(drop=True);result=worker.submit_established_invitation('welcome',history=self.history,port=server.port,time=self.time);server.done();self.assertEqual(result['state'],'uncertain')
            with self.assertRaisesRegex(ValueError,'Uncertain'):worker.submit_established_invitation('welcome',history=self.history,port=1,time=self.time)
            retry=LocalSMTP();result=worker.submit_established_invitation('welcome',history=self.history,port=retry.port,time=self.time,retry_uncertain=True);retry.done()
            self.assertEqual(result['state'],'accepted');self.assertEqual(retry.wire,server.wire)
    def test_partial_predecessor_recipient_acceptance_holds_welcome(self):
        with SenderWorker(self.sender) as worker:
            server=LocalSMTP(rcpt=[b'250 accepted\r\n',b'450 later\r\n']);worker.submit_control('commit',port=server.port,time=self.time);server.done()
        self.blocked();self.handoff();self.assertEqual(self.submit()[0]['state'],'accepted')
    def test_changed_retry_request_and_cancel_before_submission(self):
        self.assertEqual(self.prepare(),self.wire)
        with self.assertRaisesRegex(ValueError,'conflict'):self.prepare(not_after=str(int(self.time['latest'])+20))
        with SenderWorker(self.sender) as worker:self.assertEqual(self.adapter.finish('welcome',worker=worker,cancel=True),'cancelled')
        self.blocked()

    def test_shared_mailbox_cannot_count_as_two_predecessor_devices(self):
        for name,device in [('b',self.b),('c',self.c)]:
            self.control.prepare(name,self.decision,key=self.a['key'],envelope_sender='alice@example.invalid',recipients=[dict(mailbox='shared@example.invalid',principal=device['principal'],device=device['device'])],time=self.time)
        with self.assertRaisesRegex(ValueError,'Shared mailbox'):self.prepare('shared',predecessor_deliveries=['b','c'])
        self.assertEqual(self.ga.db.execute("SELECT count(*) FROM established_invitation_prepared WHERE id='shared'").fetchone()[0],0)
    def test_preparation_failure_rolls_back_wire_and_pins(self):
        def fail(stage):raise RuntimeError('crash')
        with self.assertRaises(RuntimeError):self.prepare('fault',crash=fail)
        self.assertEqual(self.ga.db.execute("SELECT count(*) FROM established_invitation_prepared WHERE id='fault'").fetchone()[0],0)
        self.assertEqual(self.ga.db.execute("SELECT count(*) FROM commit_history_pin WHERE owner='welcome:fault'").fetchone()[0],0)
        self.assertTrue(self.prepare('fault'))
    def test_original_signed_interval_and_target_proof_cannot_be_refreshed(self):
        with self.assertRaises(ValueError):self.prepare('long',not_after=str(int(self.time['latest'])+100000))
        with self.assertRaises(ValueError):self.prepare('wrongroute',association_target=dict(self.route,observation='f'*64))
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM established_invitation_prepared').fetchone()[0],1)

    def test_actual_crash_after_smtp_acceptance_recovers_uncertain(self):
        self.handoff();server=LocalSMTP()
        process=multiprocessing.get_context('spawn').Process(target=crashed_welcome,args=(self.root/'a.sqlite',self.provider,self.a,server.port,self.time))
        process.start();process.join(15)
        if process.is_alive():process.terminate();process.join();self.fail('Child timeout')
        self.assertEqual(process.exitcode,83);server.done()
        with SenderWorker(self.sender) as worker:
            with self.assertRaisesRegex(ValueError,'Uncertain'):worker.submit_established_invitation('welcome',history=self.history,port=1,time=self.time)
            self.assertEqual(self.adapter.finish('welcome',worker=worker,cancel=True),'cancelled-uncertain')
        self.assertEqual(server.wire,self.wire)
        self.assertEqual(self.ga.db.execute("SELECT count(*) FROM commit_history_pin WHERE owner='welcome:welcome'").fetchone()[0],0)

    def test_distinct_mime_carrier_is_not_initial_invitation(self):
        from invitation_mime import select as initial_select,package as initial_package
        with self.assertRaises(ValueError):initial_select(self.wire)
        with self.assertRaises(ValueError):select(initial_package(select(self.wire)))
