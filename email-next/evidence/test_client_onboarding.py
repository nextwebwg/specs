import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from email import policy
from identity_store import IdentityStore
from client_onboarding import ClientOnboarding
from test_discovery_mime import message
import test_signed_application_admission as fixture
class Onboarding(unittest.TestCase):
    def setUp(self):
        self.f=fixture.SignedAdmissionTests();self.f.setUp();self.temp=tempfile.TemporaryDirectory();self.identity=IdentityStore(Path(self.temp.name)/'new.sqlite');self.client=ClientOnboarding(self.identity);self.wires={}
    def tearDown(self):self.identity.close();self.temp.cleanup();self.f.tearDown()
    def wire(self,index=0):
        if index in self.wires:return self.wires[index]
        selected=self.f.selected[index];root=message(selected['wrapper']);root['From']=selected['mailbox'];self.wires[index]=root.as_bytes(policy=policy.SMTP);return self.wires[index]
    def ingest(self,id='one',**overrides):
        options=dict(mode='automatic-unverified-continuity',target_policy='evidenced-devices',policy_revision='1',time=self.f.time);options.update(overrides)
        return self.client.ingest(id,[self.wire()],**options)
    def test_no_seed_ordinary_mail_and_exact_retry_no_network(self):
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM pins').fetchone()[0],0)
        with patch('socket.socket',side_effect=AssertionError('No ingestion network')):result=self.ingest();self.assertEqual(result,self.ingest())
        self.assertFalse(result['identityVerified']);self.assertEqual(self.identity.db.execute('SELECT count(*) FROM pins').fetchone()[0],1)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mailbox_associations').fetchone()[0],1)
    def test_strict_and_crash_never_partially_pin(self):
        self.assertEqual(self.ingest(mode='verification-required')['outcomes'][0]['status'],'verification-required')
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM pins').fetchone()[0],0)
        with self.assertRaises(RuntimeError):self.ingest('two',crash=lambda _:(_ for _ in ()).throw(RuntimeError('crash')))
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM pins').fetchone()[0],0)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mailbox_associations').fetchone()[0],0)
        self.assertEqual(len(self.ingest('two')['outcomes']),1)
    def test_ordinary_smtp_without_seeded_peer_then_protected_exchange(self):
        from smtp_loopback import roundtrip
        from sender_release import SenderRelease
        from application_invitation_release import ApplicationInvitationRelease
        from application_invitation import ApplicationInvitationAdmission
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        from invitation_mime import select
        from mls_mime import unpack
        from event_encoding import encode_event
        other=IdentityStore(Path(self.temp.name)/'other.sqlite')
        try:
            clients=[self.client,ClientOnboarding(other)];stores=[self.identity,other]
            options=dict(mode='automatic-unverified-continuity',target_policy='all-authorized-devices',policy_revision='1',time=self.f.time)
            # Only the local account's own material is installed before receipt.
            for i in range(2):clients[i].ingest('own',[self.wire(i)],**options)
            self.assertIsNone(stores[0].current_state(self.f.devices[1]['principal'])['head'])
            self.assertIsNone(stores[1].current_state(self.f.devices[0]['principal'])['head'])
            clients[1].ingest('alice-human',[roundtrip(self.wire(0))],**options)
            clients[0].ingest('bob-human',[roundtrip(self.wire(1))],**options)
            selected=[clients[0].targets(s['mailbox'],target_policy='all-authorized-devices',time=self.f.time,mode=options['mode'])['selected'][0] for s in self.f.selected]
            senders=[SenderRelease(store,self.f.binary) for store in stores]
            for sender in senders:sender.configure(expected_revision=0)
            release=ApplicationInvitationRelease(senders[0]);release.prepare('first',device=self.f.devices[0],selected=selected,application=self.f.context['application'],conversation='2'*32,not_before=self.f.time['earliest'],not_after=str(int(self.f.time['latest'])+30),time=self.f.time)
            smtp=LocalSMTP()
            with SenderWorker(senders[0]) as worker:worker.submit_initial_invitation('first',port=smtp.port,time=self.f.time)
            smtp.done();admission=ApplicationInvitationAdmission(other,self.f.binary);admission.publish_local(self.f.devices[1])
            choices=[dict(principal=d['principal'],device=d['device'],mailbox=s['mailbox'],generation=s['generation']) for d,s in zip(self.f.devices,selected)]
            self.assertEqual(admission.accept_message(select(smtp.wire),target=self.f.devices[1],mailbox=selected[1]['mailbox'],allow_creator=self.f.devices[0]['principal'],selections=choices,time=self.f.time,trust_policy='allow-unverified')['status'],'admitted-unverified')
            for index in range(2):
                event=dict(version='1',purpose='contribution',event=str(index+7)*32,conversation='2'*32,principal=self.f.devices[index]['principal'],audience=sorted(d['principal'] for d in self.f.devices),disclosures=[],operation=dict(kind='message',text='Protected reply' if index else 'Protected first contribution',replyTo=[]))
                delivery='message'+str(index);senders[index].prepare(delivery,encode_event(event),key=self.f.devices[index]['key'],envelope_sender=selected[index]['mailbox'],recipients=[selected[1-index]['mailbox']],time=self.f.time)
                smtp=LocalSMTP()
                with SenderWorker(senders[index]) as worker:worker.submit(delivery,port=smtp.port,time=self.f.time)
                smtp.done();self.assertEqual(senders[1-index].receiver.receive(unpack(smtp.wire),time=self.f.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        finally:other.close()
    def test_competing_first_contact_and_later_unlinked_identity(self):
        import base64
        from provider_mls import sign
        from event_encoding import encode_event
        wrapper=json.loads(self.f.selected[1]['wrapper']);payload=json.loads(base64.b64decode(wrapper['payload']));payload['mailbox']=self.f.selected[0]['mailbox'];raw=encode_event(payload);wrapper['payload']=base64.b64encode(raw).decode();wrapper['signature']=sign(self.f.binary,self.f.devices[1],'email-next/passive-discovery/v1',raw)
        root=message(encode_event(wrapper));root['From']=payload['mailbox'];rival=root.as_bytes(policy=policy.SMTP)
        options=dict(mode='automatic-unverified-continuity',target_policy='evidenced-devices',policy_revision='1',time=self.f.time)
        result=self.client.ingest('competing',[self.wire(),rival],**options)
        self.assertEqual(result['outcomes'][0]['status'],'ambiguous');self.assertEqual(self.identity.db.execute('SELECT count(*) FROM pins').fetchone()[0],0)
        self.ingest('chosen');result=self.client.ingest('later',[rival],**options);self.assertEqual(result['outcomes'][0]['status'],'unlinked-claim')
        self.assertEqual(self.client.associations.snapshot(payload['mailbox'])['association']['principal'],self.f.devices[0]['principal'])
    def test_missing_required_second_device_is_explicit(self):
        import test_initial_roster as roster_fixture
        from event_encoding import encode_event
        f=roster_fixture.InitialRosterTests();f.setUp()
        proof=f.proofs[0];import base64
        value=json.loads(base64.b64decode(proof['payload']));root=message(encode_event(proof));root['From']=value['mailbox'];time=dict(earliest=f.time,latest=f.time)
        self.client.ingest('multidevice',[root.as_bytes(policy=policy.SMTP)],mode='automatic-unverified-continuity',target_policy='evidenced-devices',policy_revision='1',time=time)
        partial=self.client.targets(value['mailbox'],target_policy='evidenced-devices',time=time,mode='automatic-unverified-continuity')
        self.assertEqual(partial['status'],'ready-unverified');self.assertFalse(partial['allAuthorizedDevicesIncluded']);self.assertTrue(partial['missingDevices'])
        all_devices=self.client.targets(value['mailbox'],target_policy='all-authorized-devices',time=time,mode='automatic-unverified-continuity');self.assertEqual(all_devices['status'],'pending')
    def test_restart_and_stripped_evidence_do_not_reset_pin(self):
        self.ingest();mailbox=self.f.selected[0]['mailbox'];before=self.client.associations.snapshot(mailbox)['association']
        path=Path(self.temp.name)/'new.sqlite';self.identity.close();self.identity=IdentityStore(path);self.client=ClientOnboarding(self.identity)
        ordinary=message();ordinary.set_payload([ordinary.get_payload()[0]])
        result=self.client.ingest('stripped',[ordinary.as_bytes(policy=policy.SMTP)],mode='automatic-unverified-continuity',target_policy='evidenced-devices',policy_revision='1',time=self.f.time)
        self.assertEqual(result['diagnostics'][0]['state'],'absent');self.assertEqual(self.client.associations.snapshot(mailbox)['association'],before)
        self.assertEqual(self.ingest()['outcomes'][0]['status'],'associated-unverified')
    def test_expired_or_mismatched_from_cannot_pin(self):
        import base64
        value=json.loads(base64.b64decode(json.loads(self.f.selected[0]['wrapper'])['payload']));late=str(int(value['notAfter'])+1)
        result=self.ingest(time=dict(earliest=late,latest=late));self.assertFalse(result['outcomes']);self.assertEqual(self.identity.db.execute('SELECT count(*) FROM pins').fetchone()[0],0)
        root=message(self.f.selected[0]['wrapper']);root['From']='someoneelse@example.invalid'
        result=self.client.ingest('wrongfrom',[root.as_bytes(policy=policy.SMTP)],mode='automatic-unverified-continuity',target_policy='evidenced-devices',policy_revision='1',time=self.f.time)
        self.assertFalse(result['outcomes']);self.assertEqual(self.identity.db.execute('SELECT count(*) FROM pins').fetchone()[0],0)
    def test_authorized_successor_conflict_survives_unusable_advertisement(self):
        import base64,hashlib
        from test_successor_pipeline import fixture as successor
        from test_identity_store import seed,TIME
        from test_passive_discovery import assertion
        from event_encoding import encode_event
        f=successor();seed(self.identity,f)
        self.identity.accept_successor(encode_event(f['bundle']),candidate_digest=f['candidateDigest'],time=TIME)
        bundle=f['alternateBundle'];state=json.loads(base64.b64decode(bundle['states'][0]['payload']));binding=state['bindings'][0]
        value=assertion();value.update(principal=bundle['principal'],device=binding['device'],state=f['alternateDigest'],binding=binding['digest'],mailbox='alice@example.invalid')
        # Broken capability signature must not erase independently valid identity proofs.
        wrapper=dict(payload=base64.b64encode(encode_event(value)).decode(),signature='0'*128,identity=bundle);root=message(encode_event(wrapper));root['From']=value['mailbox']
        result=self.client.ingest('conflict',[root.as_bytes(policy=policy.SMTP)],mode='automatic-unverified-continuity',target_policy='evidenced-devices',policy_revision='1',time=TIME)
        self.assertFalse(result['outcomes']);self.assertTrue(self.identity.current_state(bundle['principal'])['conflicted'])
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM identity_transitions WHERE principal=?',(bundle['principal'],)).fetchone()[0],2)
    def test_old_head_candidate_cannot_roll_back_authorized_fork_in_either_order(self):
        import base64
        from test_successor_pipeline import fixture as successor
        from test_identity_store import seed,TIME
        from event_encoding import encode_event
        for reverse in (False,True):
            with self.subTest(reverse=reverse):
                identity=IdentityStore(Path(self.temp.name)/('batch'+str(reverse)+'.sqlite'))
                try:
                    client=ClientOnboarding(identity);f=successor('--discovery');seed(identity,f);identity.accept_successor(encode_event(f['bundle']),candidate_digest=f['candidateDigest'],time=TIME)
                    valid=dict(f['discovery'],identity=f['bundle']);fork=dict(f['discovery'],identity=f['alternateBundle']);fork['signature']='0'*128
                    def carrier(wrapper):
                        root=message(encode_event(wrapper));root['From']='alice@example.invalid';return root.as_bytes(policy=policy.SMTP)
                    messages=[carrier(valid),carrier(fork)]
                    if reverse:messages.reverse()
                    args=dict(mode='automatic-unverified-continuity',target_policy='evidenced-devices',policy_revision='1',time=TIME)
                    result=client.ingest('batch',messages,**args)
                    self.assertTrue(identity.current_state(f['bundle']['principal'])['conflicted'])
                    self.assertEqual(result['outcomes'][0]['status'],'held')
                    self.assertEqual(identity.db.execute('SELECT count(*) FROM mailbox_associations').fetchone()[0],0)
                    self.assertEqual(client.ingest('batch',messages,**args),result)
                    self.assertEqual(identity.db.execute('SELECT count(*) FROM identity_transitions').fetchone()[0],2)
                finally:identity.close()
