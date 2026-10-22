import base64
import json
import unittest
from unittest.mock import patch
from event_encoding import encode_event
from provider_mls import advertisement,sign
from passive_discovery import decode_passive_discovery
from passive_discovery_verify import verify_passive_discovery
from mailbox_association_store import MailboxAssociationStore
from identity_store import IdentityStore
from sender_worker import SenderWorker
from test_sender_release import SenderPreparationTests,LocalSMTP

class SenderAssociationTests(SenderPreparationTests):
    def setUp(self):
        super().setUp();self.sequence=0;self.mailbox='bob@example.invalid'
        self.target=self.observe(self.b,self.mailbox)
        self.decision('first-contact',self.b['principal'],None)
    def observe(self,device,mailbox,record=None):
        ad=advertisement(self.binary,device,mailbox)
        if record:
            value=json.loads(base64.b64decode(ad['payload']));value['record']=record
            raw=encode_event(value);ad['payload']=base64.b64encode(raw).decode();ad['signature']=sign(self.binary,device,'email-next/passive-discovery/v0',raw)
        raw=encode_event(ad)
        self.assertEqual(verify_passive_discovery(raw,self.identity,time=self.time,trust_policy='allow-unverified')['status'],'snapshot-authorized-unverified')
        decoded=decode_passive_discovery(raw)
        self.sender.associations.observe_validated_batch([dict(assertion=decoded['assertion']['octets'],signature=decoded['signature'],signingKey=bytes.fromhex(device['key']),outerFrom=[mailbox],sourceId=decoded['assertion']['digest'],parserRevision='test-trusted-parser-1',observedAt=self.time['earliest'])])
        return dict(mailbox=mailbox,generation='1',principal=device['principal'],observation=decoded['assertion']['digest'])
    def decision(self,kind,principal,generation,store=None):
        self.sequence+=1
        return (store or self.sender.associations).decide(decision_id=f'{self.sequence:032x}',mailbox=self.mailbox,expected_generation=generation,kind=kind,principal=principal,actor='configured-policy' if kind=='first-contact' else 'local-user',policy_revision='1',trust_policy='allow-unverified',time=self.time)
    def selected_prepare(self,delivery='selected1',targets=None,recipients=None):
        return self.sender.prepare(delivery,self.application,key=self.a['key'],envelope_sender='alice@example.invalid',recipients=recipients or [self.mailbox],time=self.time,association_targets=targets if targets is not None else [self.target])
    def assert_blocked(self,delivery='selected1'):
        with SenderWorker(self.sender) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No blocked socket')):
            with self.assertRaises(ValueError):worker.submit(delivery,port=1,time=self.time,retry_uncertain=True)
    def test_actual_selection_is_retained_at_prepare_and_release(self):
        wire=self.selected_prepare();server=LocalSMTP()
        with SenderWorker(self.sender) as worker:result=worker.submit('selected1',port=server.port,time=self.time)
        server.done();self.assertEqual(result['state'],'accepted');self.assertEqual(server.wire,wire)
        evidence=json.loads(self.identity.db.execute('SELECT evidence FROM sender_attempts').fetchone()[0])
        self.assertEqual(evidence['associationMode'],'selected-association')
        self.assertEqual(evidence['associations'][0]['observation'],self.target['observation'])
        self.assertEqual(evidence['associations'][0]['status'],'associated-unverified')
    def test_disable_reenable_never_revives_prepared_generation(self):
        self.selected_prepare();self.assertEqual(self.decision('disable',self.b['principal'],'1')['status'],'disabled');self.assert_blocked()
        self.assertEqual(self.decision('enable',self.b['principal'],'2')['generation'],'3');self.assert_blocked()
        self.assertEqual(self.selected_prepare(),self.identity.db.execute("SELECT wire FROM sender_prepared WHERE id='selected1'").fetchone()[0])
    def test_explicit_replacement_holds_old_recipient(self):
        self.selected_prepare();other=self.observe(self.a,self.mailbox)
        self.assertEqual(self.decision('replace-with-continuity-break',other['principal'],'1')['status'],'associated-unverified');self.assert_blocked()
    def test_second_connection_change_after_release_aborts_data(self):
        self.selected_prepare();server=LocalSMTP()
        def disable(stage):
            if stage=='after-release':
                other=IdentityStore(self.path)
                try:self.assertEqual(self.decision('disable',self.b['principal'],'1',MailboxAssociationStore(other))['status'],'disabled')
                finally:other.close()
        with SenderWorker(self.sender) as worker:result=worker.submit('selected1',port=server.port,time=self.time,crash=disable)
        server.done();self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(server.wire)
    def test_association_disabled_while_waiting_for_data_sends_no_body(self):
        self.selected_prepare()
        def disable():
            other=IdentityStore(self.path)
            try:self.decision('disable',self.b['principal'],'1',MailboxAssociationStore(other))
            finally:other.close()
        server=LocalSMTP(before_data=disable,allow_empty_abort=True)
        with SenderWorker(self.sender) as worker:
            result=worker.submit('selected1',port=server.port,time=self.time)
        server.done()
        self.assertEqual(result['state'],'aborted-before-data')
        self.assertEqual(result['result']['phase'],'body-not-released')
        self.assertIsNone(server.wire)

    def test_policy_changed_while_waiting_for_data_sends_no_body(self):
        self.selected_prepare()
        def change():
            from sender_release import SenderRelease
            other=IdentityStore(self.path)
            try:SenderRelease(other,self.binary).configure(expected_revision=1,trust_policy='require-verification')
            finally:other.close()
        server=LocalSMTP(before_data=change,allow_empty_abort=True)
        with SenderWorker(self.sender) as worker:
            result=worker.submit('selected1',port=server.port,time=self.time)
        server.done()
        self.assertEqual(result['state'],'aborted-before-data')
        self.assertIsNone(server.wire)

    def test_successful_body_release_retains_advanced_authorization_time(self):
        wire=self.selected_prepare();elapsed=[0]
        def advance():elapsed[0]=1000000000
        server=LocalSMTP(before_data=advance)
        with patch('time.monotonic_ns',side_effect=lambda:elapsed[0]):
            with SenderWorker(self.sender) as worker:
                result=worker.submit('selected1',port=server.port,time=self.time)
        server.done();self.assertEqual(result['state'],'accepted');self.assertEqual(server.wire,wire)
        retained=json.loads(self.identity.db.execute('SELECT result FROM sender_attempts').fetchone()[0])
        self.assertEqual(retained['bodyAuthorization']['time'],dict(earliest=str(int(self.time['earliest'])+1),latest=str(int(self.time['latest'])+1)))
        self.assertEqual(retained['bodyAuthorization']['recipients'],[self.mailbox])

    def test_assertion_expires_while_waiting_for_data_sends_no_body(self):
        self.selected_prepare();elapsed=[0]
        def expire():elapsed[0]=601*1000000000
        server=LocalSMTP(before_data=expire,allow_empty_abort=True)
        with patch('time.monotonic_ns',side_effect=lambda:elapsed[0]):
            with SenderWorker(self.sender) as worker:
                result=worker.submit('selected1',port=server.port,time=self.time)
        server.done()
        self.assertEqual(result['state'],'aborted-before-data')
        self.assertIsNone(server.wire)

    def test_second_connection_disable_before_release_blocks_socket(self):
        self.selected_prepare();other=IdentityStore(self.path)
        try:self.decision('disable',self.b['principal'],'1',MailboxAssociationStore(other))
        finally:other.close()
        self.assert_blocked();self.assertEqual(self.identity.db.execute('SELECT count(*) FROM sender_attempts').fetchone()[0],0)
    def test_cross_mailbox_authenticated_collision_holds_existing_evidence(self):
        self.selected_prepare();self.observe(self.b,'other@example.invalid')
        self.assert_blocked()
    def test_new_preparation_can_select_refresh_without_rewriting_old(self):
        self.selected_prepare();refreshed=self.observe(self.b,self.mailbox,record='d'*32)
        with self.assertRaisesRegex(ValueError,'Delivery ID conflict'):self.selected_prepare(targets=[refreshed])
        self.selected_prepare('refreshed',targets=[refreshed])
        retained=json.loads(self.identity.db.execute("SELECT associations FROM sender_prepared WHERE id='selected1'").fetchone()[0])
        self.assertEqual(retained['targets'],[self.target])
    def test_target_coverage_and_unknown_observation_fail_before_crypto_commit(self):
        for values in [[],[dict(self.target,mailbox='Bob@example.invalid')],[dict(self.target,observation='f'*64)],[dict(self.target,generation='2')]]:
            with self.subTest(values=values),self.assertRaises(ValueError):self.selected_prepare(targets=values)
        self.assertEqual(self.identity.db.execute('SELECT revision FROM mls_checkpoint').fetchone()[0],0)
    def test_uncertain_retry_obeys_changed_selection(self):
        self.selected_prepare();server=LocalSMTP(drop=True)
        with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit('selected1',port=server.port,time=self.time)['state'],'uncertain')
        server.done();self.decision('disable',self.b['principal'],'1');self.assert_blocked()
        self.assertEqual(self.identity.db.execute('SELECT state FROM sender_attempts').fetchone()[0],'uncertain')
    def test_retry_excludes_accepted_recipient_routing_change(self):
        second='later@example.invalid';target2=self.observe(self.b,second,record='e'*32)
        self.sequence+=1
        self.sender.associations.decide(decision_id=f'{self.sequence:032x}',mailbox=second,expected_generation=None,kind='first-contact',principal=self.b['principal'],actor='configured-policy',policy_revision='1',trust_policy='allow-unverified',time=self.time)
        self.selected_prepare(targets=[self.target,target2],recipients=[self.mailbox,second]);first=LocalSMTP(rcpt=[b'250 accepted\r\n',b'450 later\r\n'])
        with SenderWorker(self.sender) as worker:
            worker.submit('selected1',port=first.port,time=self.time);first.done();self.decision('disable',self.b['principal'],'1')
            retry=LocalSMTP();result=worker.submit('selected1',port=retry.port,time=self.time);retry.done()
        self.assertEqual(result['result']['acceptedRecipients'],[second])
    def test_expired_selected_assertion_holds_release(self):
        self.selected_prepare();late=str(self.b['time']+601)
        with SenderWorker(self.sender) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No expired evidence socket')):
            with self.assertRaisesRegex(ValueError,'Ineligible mailbox observation'):worker.submit('selected1',port=1,time={'earliest':late,'latest':late})
    def test_forged_advertisement_never_enters_validated_observation_boundary(self):
        self.selected_prepare();ad=advertisement(self.binary,self.b,'other@example.invalid');ad['signature']='0'*128
        result=verify_passive_discovery(encode_event(ad),self.identity,time=self.time,trust_policy='allow-unverified')
        self.assertEqual(result,{'status':'invalid','reason':'assertion-proof'})
        server=LocalSMTP()
        with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit('selected1',port=server.port,time=self.time)['state'],'accepted')
        server.done()
