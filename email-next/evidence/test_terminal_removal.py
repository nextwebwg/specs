import json
import multiprocessing
import os
import unittest
from unittest.mock import patch
import test_group_removal as fixtures
import test_historical_release as history_fixtures
from test_sender_release import LocalSMTP
from sender_release import SenderRelease
from sender_worker import SenderWorker
from commit_history import CommitHistory
from terminal_removal_release import TerminalRemovalRelease
from provider_mls import call
from identity_store import IdentityStore
from group_transitions import GroupTransitions
from transition_carrier import receive_mime

def crashed(path,binary,device,port,time):
    identity=IdentityStore(path);g=GroupTransitions(identity,binary,device);h=CommitHistory(g,max_count=8,max_bytes=4000000)
    sender=SenderRelease(identity,binary.with_name('provider-mls'))
    with SenderWorker(sender) as worker:worker.submit_terminal_removal('terminal',history=h,port=port,time=time,crash=lambda stage:os._exit(83) if stage=='after-final-response' else None)

class TerminalRemovalTests(unittest.TestCase):
    tearDown=fixtures.RemovalTests.tearDown
    store=fixtures.RemovalTests.store
    prepared=fixtures.RemovalTests.prepared
    add_phone=fixtures.RemovalTests.add_phone
    remove=fixtures.RemovalTests.remove
    revoke_phone=fixtures.RemovalTests.revoke_phone
    observe_selected=history_fixtures.HistoricalReleaseTests.observe_selected
    select_mapping=history_fixtures.HistoricalReleaseTests.select_mapping
    def setUp(self):
        fixtures.RemovalTests.setUp(self)
        self.history=CommitHistory(self.ga,max_count=8,max_bytes=4000000)
        addition=self.add_phone()
        joined=call(self.binary,op='join',checkpoint=self.phone['checkpoint'],key=self.phone['key'],welcome=addition['welcome'])
        self.gp=self.store('phone',self.phone,joined)
        self.sender=SenderRelease(self.ga.identity,self.provider);self.sender.configure(expected_revision=0)
        self.target=self.observe_selected(self.phone);self.select_mapping('first-contact',self.a['principal'],None)
        if getattr(self,'collision_before_removal',False):self.observe_selected(self.phone,'other@example.invalid')
        if getattr(self,'miss_prior_epoch',False):
            skipped=self.ga.prepare([]);self.ga.decide(skipped,allowed=set(),time=self.time)
        self.revoke_phone();self.removal=self.remove(self.phone)
        self.decision=self.ga.db.execute('SELECT digest FROM gt_decision WHERE predecessor=?',(self.removal['before']['predecessor'],)).fetchone()[0]
        self.adapter=TerminalRemovalRelease(self.sender,self.history)
        self.wire=self.adapter.prepare('terminal',self.decision,key=self.a['key'],target_identity=self.phone['identity'],target_key=self.phone['key'],association_target=self.target,envelope_sender='alice@example.invalid',time=self.time)
    def blocked(self,time=None):
        with SenderWorker(self.sender) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No blocked socket')):
            with self.assertRaises(ValueError):worker.submit_terminal_removal('terminal',history=self.history,port=1,time=time or self.time)
    def test_exact_terminal_ciphertext_despite_revoked_receive_role(self):
        with SenderWorker(self.sender) as worker:
            server=LocalSMTP();result=worker.submit_terminal_removal('terminal',history=self.history,port=server.port,time=self.time);server.done()
        self.assertEqual(result['state'],'accepted');self.assertEqual(server.wire,self.wire)
        with SenderWorker(self.sender) as worker:self.assertEqual(self.adapter.finish('terminal',worker=worker),'completed')
        self.assertEqual(self.ga.db.execute("SELECT count(*) FROM commit_history_pin WHERE owner='terminal:terminal'").fetchone()[0],0)
        self.assertEqual(receive_mime(self.gp,server.wire,allowed=set(),time=self.time),'accepted')
        with self.assertRaisesRegex(ValueError,'Inactive'):self.gp.live()
        evidence=json.loads(self.ga.db.execute('SELECT evidence FROM sender_attempts').fetchone()[0])
        self.assertEqual(evidence['associationMode'],'terminal-only-routing');self.assertEqual(evidence['associations'][0]['kind'],'terminal-routing-only')
    def test_disable_reenable_holds_original_generation(self):
        self.select_mapping('disable',self.a['principal'],'1');self.blocked()
        # Revoked device cannot be used as current eligible evidence to enable.
        self.assertNotEqual(self.select_mapping('enable',self.a['principal'],'2')['status'],'associated-unverified')
    def test_expired_observation_holds(self):
        late=str(self.phone['time']+601);self.blocked(dict(earliest=late,latest=late))
    def test_second_connection_disable_aborts_before_data(self):
        from mailbox_association_store import MailboxAssociationStore
        def disable(stage):
            if stage=='after-release':
                identity=IdentityStore(self.root/'a.sqlite')
                try:self.select_mapping('disable',self.a['principal'],'1',MailboxAssociationStore(identity))
                finally:identity.close()
        with SenderWorker(self.sender) as worker:
            server=LocalSMTP();result=worker.submit_terminal_removal('terminal',history=self.history,port=server.port,time=self.time,crash=disable);server.done()
        self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(server.wire)
    def test_uncertain_retry_retains_only_original_bytes(self):
        with SenderWorker(self.sender) as worker:
            first=LocalSMTP(drop=True);self.assertEqual(worker.submit_terminal_removal('terminal',history=self.history,port=first.port,time=self.time)['state'],'uncertain');first.done()
            with self.assertRaisesRegex(ValueError,'Uncertain'):worker.submit_terminal_removal('terminal',history=self.history,port=1,time=self.time)
            retry=LocalSMTP();self.assertEqual(worker.submit_terminal_removal('terminal',history=self.history,port=retry.port,time=self.time,retry_uncertain=True)['state'],'accepted');retry.done()
        self.assertEqual(first.wire,retry.wire);self.assertEqual(retry.wire,self.wire)
    def test_actual_process_death_after_acceptance_preserves_uncertainty(self):
        server=LocalSMTP();process=multiprocessing.get_context('spawn').Process(target=crashed,args=(self.root/'a.sqlite',self.binary,self.a,server.port,self.time));process.start();process.join(15)
        if process.is_alive():process.terminate();process.join();self.fail('Timeout')
        self.assertEqual(process.exitcode,83);server.done()
        with SenderWorker(self.sender) as worker:
            with self.assertRaisesRegex(ValueError,'Uncertain'):worker.submit_terminal_removal('terminal',history=self.history,port=1,time=self.time)
        self.assertEqual(self.ga.db.execute('SELECT state FROM sender_attempts').fetchone()[0],'uncertain')
    def test_altered_retained_mime_is_not_submitted(self):
        self.ga.db.execute("UPDATE terminal_removal_prepared SET wire=? WHERE id='terminal'",(b'not a transition',));self.blocked()
    def test_removed_target_cannot_use_history_adapter(self):
        with self.assertRaisesRegex(ValueError,'not current'):self.history.path(self.removal['before']['predecessor'],target_identity=self.phone['identity'],target_key=self.phone['key'],time=self.time,trust_policy='allow-unverified')

    def test_authenticated_preexisting_collision_prevents_preparation(self):
        self.tearDown();self.collision_before_removal=True
        with self.assertRaisesRegex(ValueError,'collided'):self.setUp()
    def test_different_selected_principal_holds(self):
        target=self.observe_selected(self.c)
        self.select_mapping('replace-with-continuity-break',target['principal'],'1');self.blocked()
    def test_wrong_device_evidence_cannot_be_substituted(self):
        target=self.observe_selected(self.c,'carol@example.invalid')
        with self.assertRaisesRegex(ValueError,'route|target'):
            self.adapter.prepare('wrong',self.decision,key=self.a['key'],target_identity=self.phone['identity'],target_key=self.phone['key'],association_target=target,envelope_sender='alice@example.invalid',time=self.time)
    def test_actual_successor_removes_committer_send_authority(self):
        import base64,hashlib
        from event_encoding import encode_event
        from provider_mls import sign
        head=self.ga.db.execute('SELECT digest FROM identity_heads WHERE principal=?',(self.a['principal'],)).fetchone()[0]
        bundle=json.loads(self.ga.db.execute('SELECT bundle FROM identity_transitions WHERE principal=? AND digest=?',(self.a['principal'],head)).fetchone()[0])
        binding=json.loads(base64.b64decode(self.a['record']['binding']));binding.update(record='a'*32,roles=['receive','enroll','revoke'],authority=dict(kind='state',digest=head))
        raw=encode_event(binding);binding_digest=hashlib.sha256(raw).hexdigest()
        state=next(json.loads(base64.b64decode(r['payload'])) for r in bundle['states'] if hashlib.sha256(base64.b64decode(r['payload'])).hexdigest()==head)
        state.update(record='b'*32,revision='3',previous=[head],bindings=[dict(device=r['device'],digest=binding_digest if r['device']==self.a['device'] else r['digest']) for r in state['bindings']])
        payload=encode_event(state)
        bundle['bindings'].insert(0,dict(payload=base64.b64encode(raw).decode(),authorization=sign(self.provider,self.a,'email-next/device-binding/v0',raw),possession=sign(self.provider,self.a,'email-next/device-possession/v0',raw)))
        bundle['states'].insert(0,dict(payload=base64.b64encode(payload).decode(),signature=sign(self.provider,self.a,'email-next/identity-state/v0',payload)))
        self.assertEqual(self.ga.identity.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(payload).hexdigest(),time=self.time)['status'],'accepted-unverified');self.blocked()
    def test_cancel_uncertain_archives_before_unpin(self):
        with SenderWorker(self.sender) as worker:
            server=LocalSMTP(drop=True);worker.submit_terminal_removal('terminal',history=self.history,port=server.port,time=self.time);server.done()
            self.assertEqual(self.adapter.finish('terminal',worker=worker,cancel=True),'cancelled-uncertain')
            with self.assertRaisesRegex(ValueError,'closed'):worker.submit_terminal_removal('terminal',history=self.history,port=1,time=self.time,retry_uncertain=True)
        archive=json.loads(self.ga.db.execute('SELECT archive FROM terminal_removal_closed').fetchone()[0])
        self.assertTrue(archive['possibleEarlierDelivery']);self.assertTrue(archive['records'])
        self.assertEqual(self.ga.db.execute("SELECT count(*) FROM commit_history_pin WHERE owner='terminal:terminal'").fetchone()[0],0)
    def test_tip_extension_keeps_terminal_bytes_and_predat_change_aborts(self):
        def extend(stage):
            if stage=='after-release':
                ident=self.ga.prepare([]);self.ga.decide(ident,allowed=set(),time=self.time)
        with SenderWorker(self.sender) as worker:
            server=LocalSMTP();result=worker.submit_terminal_removal('terminal',history=self.history,port=server.port,time=self.time,crash=extend);server.done()
            self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(server.wire)
            retry=LocalSMTP();self.assertEqual(worker.submit_terminal_removal('terminal',history=self.history,port=retry.port,time=self.time)['state'],'accepted');retry.done()
        self.assertEqual(retry.wire,self.wire)

    def test_offline_target_missing_predecessor_gets_no_secret_catchup(self):
        self.tearDown();self.miss_prior_epoch=True;self.setUp()
        with SenderWorker(self.sender) as worker:
            server=LocalSMTP();self.assertEqual(worker.submit_terminal_removal('terminal',history=self.history,port=server.port,time=self.time)['state'],'accepted');server.done()
        self.assertEqual(server.wire,self.wire)
        self.assertEqual(receive_mime(self.gp,server.wire,allowed=set(),time=self.time),'pending')
        self.assertEqual(self.gp.db.execute('SELECT count(*) FROM gt_pending').fetchone()[0],1)
        with self.assertRaisesRegex(ValueError,'not current'):self.history.path(self.gp.live()['snapshot']['predecessor'],target_identity=self.phone['identity'],target_key=self.phone['key'],time=self.time,trust_policy='allow-unverified')
