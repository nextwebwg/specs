import base64
import json
import unittest
import uuid
from unittest.mock import patch
import test_application_invitation_release as fixtures
from provider_mls import sign,make_device,advertisement
from event_encoding import encode_event
from passive_discovery import decode_passive_discovery
from invitation_mime import select
from application_invitation import parse
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from group_transitions import GroupTransitions
from transition_support import TransitionSupport
from control_release import ControlRelease
from transition_carrier import receive_mime
from commit_history import CommitHistory
from established_invitation_release import EstablishedInvitationRelease
from established_invitation import EstablishedAdmission
from established_invitation_mime import select as select_established
from identity_store import IdentityStore

class DesignatedInitialTests(unittest.TestCase):
    tearDown=fixtures.InitialReleaseTests.tearDown
    prepare=fixtures.InitialReleaseTests.prepare
    def setUp(self):
        fixtures.InitialReleaseTests.setUp(self)
        self.context=dict(self.f.context,ordering=dict(kind='designated-member-v0',principal=self.f.devices[0]['principal'],device=self.f.devices[0]['device']))
        if hasattr(self,'selected_payload'):self.context=dict(self.context,version='3',application=dict(self.context['application'],payload=self.selected_payload))
        if hasattr(self,'selected_operations'):self.context['application']=dict(self.context['application'],operations=self.selected_operations)
        self.f.context=self.context
        for i,(device,choice) in enumerate(zip(self.f.devices,self.f.selected)):
            wrapper=json.loads(choice['wrapper']);value=json.loads(base64.b64decode(wrapper['payload']));value['record']=uuid.uuid4().hex;value['applications'][0]['ordering']=['designated-member-v0']
            if hasattr(self,'selected_payload'):value.update(version='2',applications=[dict(self.context['application'],ordering='designated-member-v0')])
            payload=encode_event(value);wrapper.update(payload=base64.b64encode(payload).decode(),signature=sign(self.f.binary,device,'email-next/passive-discovery/v'+value['version'],payload));raw=encode_event(wrapper);decoded=decode_passive_discovery(raw)
            for store in [self.sender.associations,self.receiver_fixture.admission.associations]:
                store.observe_validated_batch([dict(assertion=payload,signature=decoded['signature'],signingKey=bytes.fromhex(device['key']),outerFrom=[choice['mailbox']],sourceId='designated',parserRevision='test',observedAt=self.f.time['earliest'])])
            self.f.selected[i]=dict(choice,wrapper=raw,digest=decoded['assertion']['digest'])
    def create(self):
        wire=self.prepare(designated=True)
        smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit_initial_invitation('invitation1',port=smtp.port,time=self.f.time)['state'],'accepted')
        smtp.done();self.assertEqual(wire,smtp.wire)
        evidence=json.loads(self.identity.db.execute("SELECT evidence FROM sender_attempts WHERE delivery='invitation1'").fetchone()[0])
        self.assertEqual(evidence['control']['contract'],'initial-application-invitation-v2')
        accepted=self.receiver_fixture.accept(select(wire),expected_context=encode_event(self.context))
        self.assertEqual(accepted['status'],'admitted-unverified');return wire
    def test_actual_smtp_initial2_then_add_uses_original_signed_proofs(self):
        self.create();a,b=self.f.devices
        if hasattr(self,'selected_payload'):
            from mls_mime import unpack
            event=dict(version='1',purpose='contribution',event='b'*32,conversation='2'*32,principal=a['principal'],audience=sorted(d['principal'] for d in [a,b]),disclosures=[],operation=dict(kind='message',text='Signed MIME agreement',replyTo=[]))
            wire=self.sender.prepare('body',encode_event(event),key=a['key'],envelope_sender=self.f.selected[0]['mailbox'],recipients=[self.f.selected[1]['mailbox']],time=self.f.time)
            smtp=LocalSMTP()
            with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit('body',port=smtp.port,time=self.f.time)['state'],'accepted')
            smtp.done();self.assertEqual(self.receiver_fixture.admission.receiver.receive(unpack(smtp.wire),time=self.f.time,trust_policy='allow-unverified')['status'],'projected-context-matched')
            event_bytes,payload_bytes=self.identity.db.execute("SELECT event,payload FROM sender_payloads WHERE delivery='body'").fetchone()
            self.assertEqual(event_bytes,encode_event(event));self.assertNotEqual(event_bytes,payload_bytes)

        ga=GroupTransitions(self.identity,self.f.binary.with_name('group-transitions'),a);gb=GroupTransitions(self.f.identity,self.f.binary.with_name('group-transitions'),b)
        history=CommitHistory(ga,max_count=8,max_bytes=4000000)
        new=make_device(self.f.binary,5,6)
        for identity in [self.identity,self.f.identity]:identity.observe(new['record'],first_contact_policy='allow-unverified')
        wrapper=advertisement(self.f.binary,new,'third@example.invalid');value=json.loads(base64.b64decode(wrapper['payload']));value.update(version='2' if hasattr(self,'selected_payload') else '1',applications=[dict(self.context['application'],ordering='designated-member-v0' if hasattr(self,'selected_payload') else ['designated-member-v0'])]);payload=encode_event(value);wrapper.update(payload=base64.b64encode(payload).decode(),signature=sign(self.f.binary,new,'email-next/passive-discovery/v'+value['version'],payload))
        for g in [ga,gb]:TransitionSupport(g).confirm(encode_event(wrapper),time=self.f.time)
        with patch.object(TransitionSupport,'confirm',side_effect=AssertionError('No original-member reconfirmation')):
            decision=ga.prepare([new['package']]);self.assertEqual(ga.decide(decision,allowed={(new['identity'],new['key'])},time=self.f.time),'accepted')
            ControlRelease(self.sender).prepare('add',decision,key=a['key'],envelope_sender=self.f.selected[0]['mailbox'],recipients=[dict(mailbox=self.f.selected[1]['mailbox'],principal=b['principal'],device=b['device'])],time=self.f.time)
            smtp=LocalSMTP()
            with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit_control('add',port=smtp.port,time=self.f.time)['state'],'accepted')
            smtp.done();self.assertEqual(receive_mime(gb,smtp.wire,allowed={(new['identity'],new['key'])},time=self.f.time),'accepted')
        for g in [ga,gb]:self.assertEqual(sum(json.loads(r[0])['kind']=='signed-initial-admission' for r in g.db.execute('SELECT record FROM mls_support_records')),2)
        raw=encode_event(wrapper);decoded=decode_passive_discovery(raw);mailbox='third@example.invalid'
        self.sender.associations.observe_validated_batch([dict(assertion=payload,signature=decoded['signature'],signingKey=bytes.fromhex(new['key']),outerFrom=[mailbox],sourceId='third',parserRevision='test',observedAt=self.f.time['earliest'])])
        self.sender.associations.decide(decision_id=uuid.uuid4().hex,mailbox=mailbox,expected_generation=None,kind='first-contact',principal=new['principal'],actor='configured-policy',policy_revision='1',trust_policy='allow-unverified',time=self.f.time)
        release=EstablishedInvitationRelease(self.sender,history)
        release.prepare('thirdwelcome',decision,key=a['key'],creator_bundle=json.loads(self.f.selected[0]['wrapper'])['identity'],selected_wrapper=raw,association_target=dict(mailbox=mailbox,generation='1',principal=new['principal'],observation=decoded['assertion']['digest']),predecessor_deliveries=['add'],envelope_sender=self.f.selected[0]['mailbox'],not_before=self.f.time['earliest'],not_after=str(int(self.f.time['latest'])+30),time=self.f.time)
        smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit_established_invitation('thirdwelcome',history=history,port=smtp.port,time=self.f.time)['state'],'accepted')
        smtp.done()
        evidence=json.loads(self.identity.db.execute("SELECT evidence FROM sender_attempts WHERE delivery='thirdwelcome'").fetchone()[0])
        self.assertEqual(evidence['control']['contract'],'established-membership-invitation-v'+('2' if hasattr(self,'selected_payload') else '1'))
        identity=IdentityStore(self.path.with_name('third.sqlite'))
        try:
            for device in [a,b,new]:identity.observe(device['record'],first_contact_policy='allow-unverified')
            admission=EstablishedAdmission(identity,self.f.binary);admission.publish_local(new)
            accepted=admission.accept_message(select_established(smtp.wire),target=new,mailbox=mailbox,allow_creator=a['principal'],expected_context=encode_event(self.context),time=self.f.time)
            self.assertEqual(accepted['status'],'accepted-unverified')
        finally:identity.close()

    def test_explicit_selection_and_wrong_versions_are_rejected(self):
        wire=self.prepare(designated=True)
        with self.assertRaisesRegex(ValueError,'selected initial context'):self.receiver_fixture.accept(select(wire))
        wrapper=json.loads(select(wire));value=json.loads(base64.b64decode(wrapper['payload']));value['version']='1';wrapper['payload']=base64.b64encode(encode_event(value)).decode()
        with self.assertRaisesRegex(ValueError,'Application context'):parse(encode_event(wrapper))
        value['version']='2';context=dict(self.context,version='4');value['context']=base64.b64encode(encode_event(context)).decode();wrapper['payload']=base64.b64encode(encode_event(value)).decode()
        with self.assertRaisesRegex(ValueError,'Application context'):parse(encode_event(wrapper))

    def test_wrong_domain_rolls_back_then_exact_retry_preserves_admission(self):
        wire=self.prepare(designated=True);wrapper=json.loads(select(wire));raw=base64.b64decode(wrapper['payload'])
        wrapper['signature']=sign(self.f.binary,self.f.devices[0],'email-next/mls-new-conversation-invitation/v1',raw)
        with self.assertRaises(ValueError):self.receiver_fixture.accept(encode_event(wrapper),expected_context=encode_event(self.context))
        self.assertEqual(self.f.identity.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0],0)
        accepted=self.receiver_fixture.accept(select(wire),expected_context=encode_event(self.context))
        self.assertEqual(self.receiver_fixture.accept(select(wire),expected_context=encode_event(self.context)),accepted)
