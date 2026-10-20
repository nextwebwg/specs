import json
import os
import multiprocessing
import unittest
from unittest.mock import patch
import test_group_transitions as fixtures
from commit_history import CommitHistory
from historical_release import HistoricalRelease
from sender_release import SenderRelease
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from transition_carrier import receive_mime
from identity_store import IdentityStore
from group_transitions import GroupTransitions

def crash_submit(path,binary,device,item,port,time):
    identity=IdentityStore(path);g=GroupTransitions(identity,binary,device);h=CommitHistory(g,max_count=8,max_bytes=4000000)
    sender=SenderRelease(identity,binary.with_name('provider-mls'))
    with SenderWorker(sender) as worker:
        worker.submit_historical(item,history=h,port=port,time=time,crash=lambda stage:os._exit(82) if stage=='after-final-response' else None)

class HistoricalReleaseTests(unittest.TestCase):
    tearDown=fixtures.GroupTransitionTests.tearDown
    store=fixtures.GroupTransitionTests.store
    prepared=fixtures.GroupTransitionTests.prepared
    def setUp(self):
        fixtures.GroupTransitionTests.setUp(self)
        self.history=CommitHistory(self.ga,max_count=8,max_bytes=4000000)
        self.start=self.ga.live()['snapshot']['predecessor']
        first=self.prepared();self.ga.decide(first,allowed=self.allowed,time=self.time)
        second=self.ga.prepare([]);self.ga.decide(second,allowed=set(),time=self.time)
        self.sender=SenderRelease(self.ga.identity,self.provider);self.sender.configure(expected_revision=0)
        self.release=HistoricalRelease(self.sender,self.history)
        self.items=self.release.prepare('plan1',self.start,key=self.a['key'],target_identity=self.b['identity'],target_key=self.b['key'],mailbox='bob@example.invalid',envelope_sender='alice@example.invalid',time=self.time)
    def test_ordered_exact_mime_dispatch_and_completed_lifecycle(self):
        with SenderWorker(self.sender) as worker:
            with patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No out-of-order socket')):
                with self.assertRaisesRegex(ValueError,'Earlier'):worker.submit_historical(self.items[1],history=self.history,port=1,time=self.time)
            for item in self.items:
                server=LocalSMTP();result=worker.submit_historical(item,history=self.history,port=server.port,time=self.time);server.done()
                self.assertEqual(result['state'],'accepted');self.assertEqual(receive_mime(self.gb,server.wire,allowed=self.allowed,time=self.time),'accepted')
                self.assertEqual(server.wire,self.ga.db.execute('SELECT wire FROM historical_prepared WHERE id=?',(item,)).fetchone()[0])
            self.assertEqual(self.release.finish_plan('plan1',worker=worker),'completed')
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM commit_history_pin').fetchone()[0],0)
        self.assertEqual(self.gb.live()['snapshot']['predecessor'],self.ga.live()['snapshot']['predecessor'])
    def test_current_tip_extension_before_release_is_proved_not_equal_to_old_result(self):
        third=self.ga.prepare([]);self.ga.decide(third,allowed=set(),time=self.time)
        with SenderWorker(self.sender) as worker:
            server=LocalSMTP();self.assertEqual(worker.submit_historical(self.items[0],history=self.history,port=server.port,time=self.time)['state'],'accepted');server.done()
        e=json.loads(self.ga.db.execute('SELECT evidence FROM sender_attempts').fetchone()[0]);self.assertEqual(len(e['control']['path']),3)
    def test_tip_extension_after_release_aborts_data_then_new_attempt_rechecks(self):
        def extend(stage):
            if stage=='after-release':
                third=self.ga.prepare([]);self.ga.decide(third,allowed=set(),time=self.time)
        with SenderWorker(self.sender) as worker:
            server=LocalSMTP();result=worker.submit_historical(self.items[0],history=self.history,port=server.port,time=self.time,crash=extend);server.done()
            self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(server.wire)
            retry=LocalSMTP();self.assertEqual(worker.submit_historical(self.items[0],history=self.history,port=retry.port,time=self.time)['state'],'accepted');retry.done()
    def test_crash_after_acceptance_blocks_next_and_cancel_archives_uncertainty(self):
        server=LocalSMTP();child=multiprocessing.get_context('spawn').Process(target=crash_submit,args=(self.root/'a.sqlite',self.binary,self.a,self.items[0],server.port,self.time));child.start();child.join(15)
        if child.is_alive():child.terminate();child.join();self.fail('Worker timeout')
        self.assertEqual(child.exitcode,82);server.done()
        with SenderWorker(self.sender) as worker:
            with self.assertRaisesRegex(ValueError,'Earlier'):worker.submit_historical(self.items[1],history=self.history,port=1,time=self.time)
            self.assertEqual(self.release.finish_plan('plan1',worker=worker,cancel=True),'cancelled-uncertain')
            with self.assertRaisesRegex(ValueError,'Plan not active'):worker.submit_historical(self.items[0],history=self.history,port=1,time=self.time,retry_uncertain=True)
        state,archive=self.ga.db.execute('SELECT state,archive FROM historical_plans').fetchone();archive=json.loads(archive)
        self.assertTrue(archive['possibleEarlierDelivery']);self.assertEqual(len(archive['records']),2)
        self.assertEqual(archive['attempts'][0][1],'uncertain');self.assertEqual(self.ga.db.execute('SELECT count(*) FROM commit_history_pin').fetchone()[0],0)
        self.assertIsNotNone(self.ga.db.execute('SELECT wire FROM historical_prepared WHERE id=?',(self.items[0],)).fetchone())
    def test_uncertain_retry_preserves_wire_and_unblocks_only_after_handoff(self):
        with SenderWorker(self.sender) as worker:
            server=LocalSMTP(drop=True);self.assertEqual(worker.submit_historical(self.items[0],history=self.history,port=server.port,time=self.time)['state'],'uncertain');server.done()
            with self.assertRaisesRegex(ValueError,'Earlier'):worker.submit_historical(self.items[1],history=self.history,port=1,time=self.time)
            retry=LocalSMTP();self.assertEqual(worker.submit_historical(self.items[0],history=self.history,port=retry.port,time=self.time,retry_uncertain=True)['state'],'accepted');retry.done();self.assertEqual(server.wire,retry.wire)
            last=LocalSMTP();self.assertEqual(worker.submit_historical(self.items[1],history=self.history,port=last.port,time=self.time)['state'],'accepted');last.done()
    def test_symlink_lock_and_forked_worker_cannot_release(self):
        target=self.root/'elsewhere';target.touch();lock=self.root/'a.sqlite.sender-lock';lock.symlink_to(target)
        with self.assertRaises(OSError):
            with SenderWorker(self.sender):pass
        lock.unlink()
        with SenderWorker(self.sender) as worker:
            pid=os.fork()
            if pid==0:
                try:worker.submit_historical(self.items[0],history=self.history,port=1,time=self.time)
                except ValueError as error:os._exit(0 if str(error)=='Worker ownership' else 2)
                except BaseException:os._exit(3)
                os._exit(4)
            _,status=os.waitpid(pid,0);self.assertEqual(os.waitstatus_to_exitcode(status),0)

    def test_permanent_failure_blocks_only_its_recipient_plan(self):
        other=self.release.prepare('plan2',self.start,key=self.a['key'],target_identity=self.c['identity'],target_key=self.c['key'],mailbox='carol@example.invalid',envelope_sender='alice@example.invalid',time=self.time)
        with SenderWorker(self.sender) as worker:
            server=LocalSMTP(rcpt=[b'550 unavailable\r\n']);self.assertEqual(worker.submit_historical(self.items[0],history=self.history,port=server.port,time=self.time)['state'],'rejected');server.done()
            with self.assertRaisesRegex(ValueError,'Earlier'):worker.submit_historical(self.items[1],history=self.history,port=1,time=self.time)
            for item in other:
                server=LocalSMTP();self.assertEqual(worker.submit_historical(item,history=self.history,port=server.port,time=self.time)['state'],'accepted');server.done()
            self.assertEqual(self.release.finish_plan('plan2',worker=worker),'completed')
            self.assertEqual(self.release.finish_plan('plan1',worker=worker,cancel=True),'cancelled')
    def test_real_committer_role_loss_prevents_historical_socket(self):
        fixtures.GroupTransitionTests.strip_committer_send(self,self.ga.identity)
        with SenderWorker(self.sender) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No revoked send')):
            with self.assertRaises(ValueError):worker.submit_historical(self.items[0],history=self.history,port=1,time=self.time)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM sender_attempts').fetchone()[0],0)

    def observe_selected(self,device,mailbox='bob@example.invalid'):
        from provider_mls import advertisement
        from event_encoding import encode_event
        from passive_discovery import decode_passive_discovery
        from passive_discovery_verify import verify_passive_discovery
        ad=advertisement(self.provider,device,mailbox)
        if device is self.phone:
            import base64,hashlib
            from provider_mls import sign
            value=json.loads(base64.b64decode(ad['payload']))
            value.update(state=self.head,binding=hashlib.sha256(base64.b64decode(self.bundle['bindings'][0]['payload'])).hexdigest())
            payload=encode_event(value)
            ad.update(payload=base64.b64encode(payload).decode(),signature=sign(self.provider,device,'email-next/passive-discovery/v0',payload),identity=self.bundle)
        raw=encode_event(ad)
        self.assertEqual(verify_passive_discovery(raw,self.ga.identity,time=self.time,trust_policy='allow-unverified')['status'],'snapshot-authorized-unverified')
        decoded=decode_passive_discovery(raw)
        self.sender.associations.observe_validated_batch([dict(assertion=decoded['assertion']['octets'],signature=decoded['signature'],signingKey=bytes.fromhex(device['key']),outerFrom=[mailbox],sourceId=decoded['assertion']['digest'],parserRevision='test-trusted-parser-1',observedAt=self.time['earliest'])])
        return dict(mailbox=mailbox,generation='1',principal=device['principal'],observation=decoded['assertion']['digest'])
    def select_mapping(self,kind,principal,generation,store=None):
        import uuid
        return (store or self.sender.associations).decide(decision_id=uuid.uuid4().hex,mailbox='bob@example.invalid',expected_generation=generation,kind=kind,principal=principal,actor='configured-policy' if kind=='first-contact' else 'local-user',policy_revision='1',trust_policy='allow-unverified',time=self.time)
    def selected_plan(self):
        target=self.observe_selected(self.b)
        self.select_mapping('first-contact',self.b['principal'],None)
        items=self.release.prepare('selected',self.start,key=self.a['key'],target_identity=self.b['identity'],target_key=self.b['key'],mailbox='bob@example.invalid',envelope_sender='alice@example.invalid',time=self.time,association_targets=[target])
        return items,target
    def assert_selected_blocked(self,item):
        with SenderWorker(self.sender) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No association-blocked socket')):
            with self.assertRaises(ValueError):worker.submit_historical(item,history=self.history,port=1,time=self.time)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM sender_attempts').fetchone()[0],0)
    def test_selected_exact_mapping_dispatches_retained_wire(self):
        items,target=self.selected_plan()
        with SenderWorker(self.sender) as worker:
            server=LocalSMTP();result=worker.submit_historical(items[0],history=self.history,port=server.port,time=self.time);server.done()
        self.assertEqual(result['state'],'accepted')
        self.assertEqual(server.wire,self.ga.db.execute('SELECT wire FROM historical_prepared WHERE id=?',(items[0],)).fetchone()[0])
        evidence=json.loads(self.ga.db.execute('SELECT evidence FROM sender_attempts').fetchone()[0])
        self.assertEqual(evidence['associationMode'],'selected-association');self.assertEqual(evidence['associations'][0]['observation'],target['observation'])
        self.assertEqual(receive_mime(self.gb,server.wire,allowed=self.allowed,time=self.time),'accepted')
    def test_selected_disable_and_reenable_holds_old_generation(self):
        items,_=self.selected_plan()
        self.select_mapping('disable',self.b['principal'],'1');self.assert_selected_blocked(items[0])
        self.select_mapping('enable',self.b['principal'],'2');self.assert_selected_blocked(items[0])
    def test_selected_replacement_holds_before_socket(self):
        items,_=self.selected_plan();other=self.observe_selected(self.c)
        self.select_mapping('replace-with-continuity-break',other['principal'],'1');self.assert_selected_blocked(items[0])
    def test_selected_second_connection_disable_after_release_aborts_data(self):
        from mailbox_association_store import MailboxAssociationStore
        items,_=self.selected_plan()
        def disable(stage):
            if stage=='after-release':
                other=IdentityStore(self.root/'a.sqlite')
                try:self.select_mapping('disable',self.b['principal'],'1',MailboxAssociationStore(other))
                finally:other.close()
        with SenderWorker(self.sender) as worker:
            server=LocalSMTP();result=worker.submit_historical(items[0],history=self.history,port=server.port,time=self.time,crash=disable);server.done()
        self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(server.wire)
    def test_selected_same_principal_other_device_is_not_target_substitute(self):
        target=self.observe_selected(self.phone)
        self.select_mapping('first-contact',self.a['principal'],None)
        with self.assertRaisesRegex(ValueError,'Target association mismatch'):
            self.release.prepare('wrongdevice',self.start,key=self.a['key'],target_identity=self.a['identity'],target_key=self.a['key'],mailbox='bob@example.invalid',envelope_sender='alice@example.invalid',time=self.time,association_targets=[target])
        self.assertEqual(self.ga.db.execute("SELECT count(*) FROM historical_plans WHERE id='wrongdevice'").fetchone()[0],0)
