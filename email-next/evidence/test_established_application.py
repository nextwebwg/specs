import base64
import hashlib
import json
import unittest
import test_group_removal as fixture
from provider_mls import advertisement,sign,call
from group_transitions import GroupTransitions
from transition_carrier import receive_mime
import uuid
from event_encoding import encode_event
from transition_support import TransitionSupport
from commit_history import CommitHistory
from sender_release import SenderRelease
from control_release import ControlRelease
from established_invitation_release import EstablishedInvitationRelease
from established_invitation import EstablishedAdmission
from established_invitation_mime import select
from passive_discovery import decode_passive_discovery
from identity_store import IdentityStore
from test_sender_release import LocalSMTP
from sender_worker import SenderWorker

class EstablishedApplicationTests(unittest.TestCase):
    application_profile=dict(envelopeVersion='1',operations=['answer','message','question'])
    setUp=fixture.RemovalTests.setUp
    tearDown=fixture.RemovalTests.tearDown
    store=fixture.RemovalTests.store
    prepared=fixture.RemovalTests.prepared
    def assertion(self,device,*,expires=None):
        wrapper=advertisement(self.provider,device,'phone@example.invalid' if device is self.phone else device['device'][-8:]+'@example.invalid')
        value=json.loads(base64.b64decode(wrapper['payload']));value.update(version='1',record=uuid.uuid4().hex,applications=[dict(self.application_profile,ordering=['designated-member-v0'])])
        if device['principal']==self.a['principal']:
            value['state']=self.head;wrapper['identity']=self.bundle
            value['binding']=next(hashlib.sha256(base64.b64decode(b['payload'])).hexdigest() for b in self.bundle['bindings'] if json.loads(base64.b64decode(b['payload']))['device']==device['device'])
        if expires is not None:value['notAfter']=expires
        raw=encode_event(value);wrapper.update(payload=base64.b64encode(raw).decode(),signature=sign(self.provider,device,'email-next/passive-discovery/v1',raw))
        return encode_event(wrapper)
    def setup_delivery(self,*,historical_expired=False):
        self.history=CommitHistory(self.ga,max_count=8,max_bytes=4000000)
        self.proofs={d['identity']:self.assertion(d,expires=self.time['latest'] if historical_expired and d is not self.phone else None) for d in [self.a,self.b,self.c,self.phone]}
        for g in [self.ga,self.gb,self.gc]:
            support=TransitionSupport(g)
            for proof in self.proofs.values():support.confirm(proof,time=self.time)
        if historical_expired:self.time={k:str(int(v)+2) for k,v in self.time.items()}
        self.decision=self.prepared();self.assertEqual(self.ga.decide(self.decision,allowed=self.allowed,time=self.time),'accepted')
        self.sender=SenderRelease(self.ga.identity,self.provider);self.sender.configure(expected_revision=0)
        self.wrapper=self.proofs[self.phone['identity']];d=decode_passive_discovery(self.wrapper);a=d['assertion'];mailbox=a['value']['mailbox']
        self.sender.associations.observe_validated_batch([dict(assertion=a['octets'],signature=d['signature'],signingKey=bytes.fromhex(self.phone['key']),outerFrom=[mailbox],sourceId=a['digest'],parserRevision='test-real-proof',observedAt=self.time['earliest'])])
        self.sender.associations.decide(decision_id='11111111111111111111111111111111',mailbox=mailbox,expected_generation=None,kind='first-contact',principal=self.a['principal'],actor='configured-policy',policy_revision='1',trust_policy='allow-unverified',time=self.time)
        route=dict(mailbox=mailbox,generation='1',principal=self.a['principal'],observation=a['digest'])
        ControlRelease(self.sender).prepare('commit',self.decision,key=self.a['key'],envelope_sender='a@example.invalid',recipients=[dict(mailbox='b@example.invalid',principal=self.b['principal'],device=self.b['device']),dict(mailbox='c@example.invalid',principal=self.c['principal'],device=self.c['device'])],time=self.time)
        self.release=EstablishedInvitationRelease(self.sender,self.history)
        self.wire=self.release.prepare('welcome',self.decision,key=self.a['key'],creator_bundle=self.bundle,selected_wrapper=self.wrapper,association_target=route,predecessor_deliveries=['commit'],envelope_sender='a@example.invalid',not_before=self.time['earliest'],not_after=str(int(self.time['latest'])+20),time=self.time)
        return route
    def test_actual_smtp_v1_admission_installs_exact_instance_agreements(self):
        route=self.setup_delivery()
        with SenderWorker(self.sender) as worker:
            commit=LocalSMTP();self.assertEqual(worker.submit_control('commit',port=commit.port,time=self.time)['state'],'accepted');commit.done()
            mail=LocalSMTP();self.assertEqual(worker.submit_established_invitation('welcome',history=self.history,port=mail.port,time=self.time)['state'],'accepted');mail.done()
        identity=IdentityStore(self.root/'phone.sqlite');self.stores.append(identity)
        for peer in [self.a,self.b,self.c]:identity.observe(peer['record'],first_contact_policy='allow-unverified')
        identity.accept_successor(encode_event(self.bundle),candidate_digest=self.head,time=self.time)
        admission=EstablishedAdmission(identity,self.provider);admission.publish_local(self.phone)
        result=admission.accept_message(select(mail.wire),target=self.phone,mailbox=route['mailbox'],allow_creator=self.a['principal'],expected_context=self.ctx,time=self.time)
        self.assertEqual(result['status'],'accepted-unverified')
        self.assertEqual(identity.db.execute('SELECT count(*) FROM mls_instance_agreements WHERE instance=?',(result['instance'],)).fetchone()[0],4)
        self.assertEqual(identity.db.execute('SELECT count(*) FROM mls_established_support WHERE instance=?',(result['instance'],)).fetchone()[0],4)

    def test_smtp_same_key_rejoin_keeps_old_pending_in_ended_instance(self):
        route=self.setup_delivery()
        with SenderWorker(self.sender) as worker:
            commit=LocalSMTP();worker.submit_control('commit',port=commit.port,time=self.time);commit.done()
            for g in [self.gb,self.gc]:self.assertEqual(receive_mime(g,commit.wire,allowed=self.allowed,time=self.time),'accepted')
            mail=LocalSMTP();worker.submit_established_invitation('welcome',history=self.history,port=mail.port,time=self.time);mail.done()
        identity=IdentityStore(self.root/'rejoinphone.sqlite');self.stores.append(identity)
        for peer in [self.a,self.b,self.c]:identity.observe(peer['record'],first_contact_policy='allow-unverified')
        identity.accept_successor(encode_event(self.bundle),candidate_digest=self.head,time=self.time)
        admission=EstablishedAdmission(identity,self.provider);admission.publish_local(self.phone)
        first=admission.accept_message(select(mail.wire),target=self.phone,mailbox=route['mailbox'],allow_creator=self.a['principal'],expected_context=self.ctx,time=self.time)
        phone_group=GroupTransitions(identity,self.binary,self.phone)
        event=dict(version='1',purpose='contribution',event='6'*32,conversation='2'*32,principal=self.b['principal'],audience=sorted([self.a['principal'],self.b['principal'],self.c['principal']]),disclosures=[],operation=dict(kind='answer',question=dict(principal=self.b['principal'],conversation='2'*32,event='5'*32),option='7'*32,replaces=[]))
        state=self.gb.live();pending=call(self.provider,op='send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.b['key'],application=encode_event(event).hex())
        self.assertEqual(phone_group.receiver.receive(bytes.fromhex(pending['wire']),time=self.time,trust_policy='allow-unverified')['status'],'pending')
        removed=self.ga.prepare_removal([dict(identity=self.phone['identity'],key=self.phone['key'])],time=self.time);self.ga.decide(removed,allowed=set(),time=self.time)
        removal=json.loads(self.ga.db.execute('SELECT state FROM gt_decision WHERE digest=?',(removed,)).fetchone()[0])
        for g in [self.gb,self.gc,phone_group]:self.assertEqual(g.receive(bytes.fromhex(removal['wire']),allowed=set(),time=self.time),'accepted')
        old_package=self.phone['package'];fresh=call(self.provider,op='fresh-package',checkpoint=self.phone['checkpoint'],key=self.phone['key'],identity=self.phone['identity']);self.phone=dict(self.phone,**fresh)
        self.assertNotEqual(self.phone['package'],old_package)
        proof=self.assertion(self.phone)
        for g in [self.ga,self.gb,self.gc]:TransitionSupport(g).confirm(proof,time=self.time)
        decision=self.ga.prepare([self.phone['package']]);self.assertEqual(self.ga.decide(decision,allowed=self.allowed,time=self.time),'accepted')
        d=decode_passive_discovery(proof);a=d['assertion']
        self.sender.associations.observe_validated_batch([dict(assertion=a['octets'],signature=d['signature'],signingKey=bytes.fromhex(self.phone['key']),outerFrom=[route['mailbox']],sourceId=a['digest'],parserRevision='test-real-proof',observedAt=self.time['earliest'])])
        newroute=dict(route,observation=a['digest'])
        ControlRelease(self.sender).prepare('rejoincommit',decision,key=self.a['key'],envelope_sender='a@example.invalid',recipients=[dict(mailbox='b@example.invalid',principal=self.b['principal'],device=self.b['device']),dict(mailbox='c@example.invalid',principal=self.c['principal'],device=self.c['device'])],time=self.time)
        self.release.prepare('rejoinwelcome',decision,key=self.a['key'],creator_bundle=self.bundle,selected_wrapper=proof,association_target=newroute,predecessor_deliveries=['rejoincommit'],envelope_sender='a@example.invalid',not_before=self.time['earliest'],not_after=str(int(self.time['latest'])+20),time=self.time)
        with SenderWorker(self.sender) as worker:
            commit=LocalSMTP();self.assertEqual(worker.submit_control('rejoincommit',port=commit.port,time=self.time)['state'],'accepted');commit.done()
            for g in [self.gb,self.gc]:self.assertEqual(receive_mime(g,commit.wire,allowed=self.allowed,time=self.time),'accepted')
            mail=LocalSMTP();self.assertEqual(worker.submit_established_invitation('rejoinwelcome',history=self.history,port=mail.port,time=self.time)['state'],'accepted');mail.done()
        admission.publish_local(self.phone)
        joined=admission.accept_message(select(mail.wire),target=self.phone,mailbox=route['mailbox'],allow_creator=self.a['principal'],expected_context=self.ctx,time=self.time)
        self.assertNotEqual(joined['instance'],first['instance'])
        self.assertEqual(list(phone_group.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')['states'].values()),['held:membership-instance'])
        followup=dict(event,event='8'*32,principal=self.a['principal'],operation=dict(kind='message',text='New membership only',replyTo=[]))
        state=self.ga.live();sent=call(self.provider,op='send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.a['key'],application=encode_event(followup).hex())
        self.assertEqual(phone_group.receiver.receive(bytes.fromhex(sent['wire']),time=self.time,trust_policy='allow-unverified')['status'],'projected-context-matched')
        self.assertEqual(admission.accept_message(select(mail.wire),target=self.phone,mailbox=route['mailbox'],allow_creator=self.a['principal'],expected_context=self.ctx,time=self.time),joined)

    def test_expired_existing_confirmation_remains_historical_not_current_support(self):
        self.setup_delivery(historical_expired=True)
        wrapper=json.loads(select(self.wire));value=json.loads(base64.b64decode(wrapper['payload']))
        self.assertEqual(value['version'],'1')
        records=[json.loads(row[0]) for row in self.ga.db.execute('SELECT record FROM mls_support_records')]
        self.assertTrue(all(int(r['time']['latest'])<int(self.time['earliest']) for r in records))
        from established_invitation import parse
        parse(select(self.wire))
        self.assertEqual(len(value['applicationAssertions']),4)

    def test_changed_target_proof_cannot_replace_decided_selection(self):
        route=self.setup_delivery()
        changed=self.assertion(self.phone)
        d=decode_passive_discovery(changed);a=d['assertion']
        self.sender.associations.observe_validated_batch([dict(assertion=a['octets'],signature=d['signature'],signingKey=bytes.fromhex(self.phone['key']),outerFrom=[route['mailbox']],sourceId=a['digest'],parserRevision='test-real-proof',observedAt=self.time['earliest'])])
        with self.assertRaisesRegex(ValueError,'Target support changed'):
            self.release.prepare('changed',self.decision,key=self.a['key'],creator_bundle=self.bundle,selected_wrapper=changed,association_target=dict(route,observation=a['digest']),predecessor_deliveries=['commit'],envelope_sender='a@example.invalid',not_before=self.time['earliest'],not_after=str(int(self.time['latest'])+20),time=self.time)
        self.assertIsNone(self.ga.db.execute("SELECT 1 FROM established_invitation_prepared WHERE id='changed'").fetchone())

    def test_target_interval_and_ref_substitution_reject_before_package_consumption(self):
        route=self.setup_delivery()
        identity=IdentityStore(self.root/'rejectedphone.sqlite');self.stores.append(identity)
        for peer in [self.a,self.b,self.c]:identity.observe(peer['record'],first_contact_policy='allow-unverified')
        identity.accept_successor(encode_event(self.bundle),candidate_digest=self.head,time=self.time)
        admission=EstablishedAdmission(identity,self.provider);admission.publish_local(self.phone)
        wrapper=json.loads(select(self.wire));value=json.loads(base64.b64decode(wrapper['payload']))
        targetproof=next(json.loads(base64.b64decode(p['payload'])) for p in wrapper['applicationAssertions'] if json.loads(base64.b64decode(p['payload']))['device']==self.phone['device'])
        value['notAfter']=str(int(targetproof['notAfter'])+1)
        raw=encode_event(value);wrapper.update(payload=base64.b64encode(raw).decode(),signature=sign(self.provider,self.a,'email-next/mls-established-membership-invitation/v1',raw))
        with self.assertRaisesRegex(ValueError,'Fresh target support'):
            admission.accept_message(encode_event(wrapper),target=self.phone,mailbox=route['mailbox'],allow_creator=self.a['principal'],expected_context=self.ctx,time=self.time)
        self.assertIsNone(identity.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])
        self.assertEqual(identity.db.execute('SELECT count(*) FROM mls_group_instances').fetchone()[0],0)
        wrapper=json.loads(select(self.wire));wrapper['applicationAssertions'][0],wrapper['applicationAssertions'][1]=wrapper['applicationAssertions'][1],wrapper['applicationAssertions'][0]
        with self.assertRaisesRegex(ValueError,'proof binding'):
            admission.accept_message(encode_event(wrapper),target=self.phone,mailbox=route['mailbox'],allow_creator=self.a['principal'],expected_context=self.ctx,time=self.time)
