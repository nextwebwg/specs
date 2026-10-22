import base64,hashlib,json,unittest
from unittest.mock import patch
from email import policy
from email.parser import BytesParser
from event_encoding import encode_event
from provider_mls import sign
from initial_roster_lifecycle import InitialRosterRelease,InitialRosterAdmission
from initial_roster import parse
from invitation_mime import select
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from mls_mime import unpack
from managed_presentation import describe,provisional
import test_private_copy_lifecycle as fixture

class ManagedPresentation(unittest.TestCase):
    endpoint=fixture.PrivateCopyLifecycle.endpoint;prepare=fixture.PrivateCopyLifecycle.prepare;tearDown=fixture.PrivateCopyLifecycle.tearDown
    def setUp(self):
        # These historical presentation/service fixtures supply a fixed credible
        # time. Keep their elapsed clock fixed too; advancing-clock release
        # behavior is tested separately by the sender-association cases.
        clock=patch('sender_worker.elapsed_time.monotonic_ns',return_value=0)
        clock.start();self.addCleanup(clock.stop)
        fixture.PrivateCopyLifecycle.setUp(self)
        self.f.context.update(version='6',application=dict(self.f.context['application'],envelopeVersion='3'))
        proofs=[]
        for device,p in zip(self.f.devices,self.f.proofs):
            value=json.loads(base64.b64decode(p['payload']));value.update(version='5',applications=[dict(self.f.context['application'],ordering='designated-member-v0')]);raw=encode_event(value)
            proofs.append(dict(p,payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,device,'email-next/passive-discovery/v5',raw)))
        self.f.proofs=proofs;self.identity,self.sender,self.selected=self.endpoint('managed-creator');self.release=InitialRosterRelease(self.sender)
    def join(self):
        wires=self.prepare();target=next(d for d in self.f.devices if d['principal']!=self.f.creator['principal'])
        item,wire=next((i,w) for i,w in wires.items() if parse(select(w))['value']['target']['device']==target['device'])
        smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit_initial_roster(item,port=smtp.port,time=self.time)['state'],'accepted')
        smtp.done();p=parse(select(smtp.wire));self.assertEqual(p['value']['version'],'5');self.assertEqual(p['roster']['version'],'2')
        identity,sender,selected=self.endpoint('managed-receiver');admission=InitialRosterAdmission(identity,self.f.binary);admission.publish_local(target)
        choices=[dict(principal=d['principal'],device=d['device'],mailbox=c['mailbox'],generation=c['generation']) for d,c in zip(self.f.devices,selected)]
        admission.accept_message(select(smtp.wire),target=target,mailbox=p['value']['target']['mailbox'],allow_creator=self.f.creator['principal'],intended_principals=self.principals,intended_devices=self.devices,expected_context=encode_event(self.f.context),selections=choices,time=self.time,trust_policy='allow-unverified')
        self.peer=target;self.peer_sender=sender;self.peer_identity=identity;self.peer_selected=selected
        self.source=next(c['mailbox'] for d,c in zip(self.f.devices,self.selected) if d['device']==self.f.creator['device']);self.destination=p['value']['target']['mailbox']
    def event(self,*,id='a',author=None):
        author=author or self.f.creator['principal'];other=next(p for p in self.principals if p!=author)
        return dict(version='3',purpose='contribution',event=id*32,conversation=self.f.context['conversation'],principal=author,audience=self.principals,disclosures=[],presentation=dict(subject='Confidential roadmap 📨',authoredAt='18446744073709551615',to=[other],cc=[]),operation=dict(kind='message',text='Protected body',replyTo=[]))
    def deliver(self):
        self.join();event=self.event();raw=encode_event(event)
        wire=self.sender.prepare('presentation',raw,key=self.f.creator['key'],envelope_sender=self.source,recipients=[self.destination],time=self.time)
        self.assertEqual(self.sender.prepare('presentation',raw,key=self.f.creator['key'],envelope_sender=self.source,recipients=[self.destination],time=self.time),wire)
        outer=BytesParser(policy=policy.SMTP).parsebytes(wire)
        self.assertNotIn('Confidential',str(outer));self.assertNotIn('roadmap',str(outer));self.assertNotIn('Confidential',str(outer['Subject']))
        smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit('presentation',port=smtp.port,time=self.time)['state'],'accepted')
        smtp.done();self.assertEqual(smtp.wire,wire)
        receiver=self.peer_sender.receiver;self.assertEqual(receiver.receive(unpack(wire),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        ref={k:event[k] for k in ('principal','conversation','event')};carrier=hashlib.sha256(unpack(wire)).hexdigest()
        return event,wire,ref,carrier
    def test_smtp_outer_mutations_cannot_change_protected_display_or_reply(self):
        event,wire,ref,carrier=self.deliver();receiver=self.peer_sender.receiver
        original=describe(receiver,ref,carrier=carrier,transport_wire=wire)
        for name,value in [('Subject','Forged title'),('From','attacker@example.invalid'),('Reply-To','attacker@example.invalid'),('References','<forged@example.invalid>')]:
            altered=BytesParser(policy=policy.SMTP).parsebytes(wire)
            if name in altered:altered.replace_header(name,value)
            else:altered[name]=value
            changed=altered.as_bytes();receiver.receive(unpack(changed),time=self.time,trust_policy='allow-unverified')
            shown=describe(receiver,ref,carrier=carrier,transport_wire=changed)
            self.assertEqual({k:v for k,v in shown.items() if k!='transport'},{k:v for k,v in original.items() if k!='transport'})
            self.assertEqual(shown['transport']['fields'][name],[value])
        self.assertEqual(original['subject'],event['presentation']['subject']);self.assertEqual(original['authoredAt']['display'],'Unavailable')
        reply=self.event(id='b',author=self.peer['principal']);reply['presentation']['subject']='Reply to protected roadmap'
        replywire=self.peer_sender.prepare('reply',encode_event(reply),key=self.peer['key'],envelope_sender=self.destination,recipients=[self.source],time=self.time)
        smtp=LocalSMTP()
        with SenderWorker(self.peer_sender) as worker:self.assertEqual(worker.submit('reply',port=smtp.port,time=self.time)['state'],'accepted')
        smtp.done();self.assertNotIn('attacker',str(BytesParser(policy=policy.SMTP).parsebytes(smtp.wire)['To']))
        self.assertEqual(self.sender.receiver.receive(unpack(replywire),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
    def test_private_roles_leak_and_old_envelope_are_rejected(self):
        self.join()
        for changed in [dict(self.event(),presentation=dict(self.event()['presentation'],cc=['enp0:'+'f'*64])),dict(self.event(),version='2')]:
            with self.assertRaises(ValueError):self.sender.prepare('invalid',encode_event(changed),key=self.f.creator['key'],envelope_sender=self.source,recipients=[self.destination],time=self.time)
    def test_subject_change_is_not_an_exact_retry(self):
        event,wire,ref,carrier=self.deliver();event['presentation']['subject']='Different subject'
        with self.assertRaisesRegex(ValueError,'conflict|different|changed|Immutable'):self.sender.prepare('presentation',encode_event(event),key=self.f.creator['key'],envelope_sender=self.source,recipients=[self.destination],time=self.time)
    def test_same_principal_device_add_and_established5_actual_smtp(self):
        from group_transitions import GroupTransitions
        from transition_support import TransitionSupport
        from commit_history import CommitHistory
        from control_release import ControlRelease
        from established_invitation_release import EstablishedInvitationRelease
        from established_invitation import EstablishedAdmission,parse as parse_established
        from established_invitation_mime import select as select_established
        from passive_discovery import decode_passive_discovery
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        phone=next(d for d in self.f.devices if d['principal']==self.f.creator['principal'] and d is not self.f.creator)
        index=self.f.devices.index(phone);proof=encode_event(self.f.proofs[index]);route=dict(self.selected[index],principal=phone['principal']);route.pop('wrapper');route['observation']=route.pop('digest')
        full_devices=list(self.f.devices);full_proofs=list(self.f.proofs)
        self.f.devices.pop(index);self.f.proofs.pop(index);self.selected.pop(index);self.devices=[{k:d[k] for k in ('principal','device')} for d in self.f.devices]
        self.prepare();group=GroupTransitions(self.identity,self.f.binary.with_name('group-transitions'),self.f.creator);history=CommitHistory(group,max_count=12,max_bytes=8000000)
        TransitionSupport(group).confirm(proof,time=self.time);decision=group.prepare([phone['package']]);self.assertEqual(group.decide(decision,allowed={(phone['identity'],phone['key'])},time=self.time),'accepted')
        source=next(c['mailbox'] for d,c in zip(self.f.devices,self.selected) if d is self.f.creator);controls=[]
        for i,(d,c) in enumerate(zip(self.f.devices,self.selected)):
            if d is self.f.creator:continue
            ident='privatecontrol'+str(i);controls.append(ident)
            ControlRelease(self.sender).prepare(ident,decision,key=self.f.creator['key'],envelope_sender=source,recipients=[dict(mailbox=c['mailbox'],principal=d['principal'],device=d['device'])],association_targets=[dict(mailbox=c['mailbox'],generation=c['generation'],principal=d['principal'],observation=c['digest'])],time=self.time)
        release=EstablishedInvitationRelease(self.sender,history);wire=release.prepare('privatewelcome',decision,key=self.f.creator['key'],creator_bundle=self.f.bundles[self.f.creator['principal']],selected_wrapper=proof,association_target=route,predecessor_deliveries=controls,envelope_sender=source,not_before=self.time['earliest'],not_after=str(int(self.time['latest'])+30),time=self.time)
        with SenderWorker(self.sender) as worker:
            for ident in controls:
                smtp=LocalSMTP();worker.submit_control(ident,port=smtp.port,time=self.time);smtp.done()
            smtp=LocalSMTP();worker.submit_established_invitation('privatewelcome',history=history,port=smtp.port,time=self.time);smtp.done();self.assertEqual(smtp.wire,wire)
        self.assertEqual(parse_established(select_established(wire))[2]['version'],'5')
        self.f.devices=full_devices;self.f.proofs=full_proofs
        identity,sender,_=self.endpoint('privatephone');admission=EstablishedAdmission(identity,self.f.binary);admission.publish_local(phone)
        result=admission.accept_message(select_established(wire),target=phone,mailbox=route['mailbox'],allow_creator=self.f.creator['principal'],expected_context=encode_event(self.f.context),time=self.time)
        self.assertEqual(result['status'],'accepted-unverified')

    def test_explicit_plaintext_copy_discloses_reviewed_subject(self):
        self.join()
        from plaintext_release import PlaintextRelease
        fallback=PlaintextRelease(self.sender);event=self.event(id='c');event['disclosures']=[{'kind':'plaintext-email'}];raw=encode_event(event)
        with self.assertRaisesRegex(ValueError,'Plaintext disclosure plan'):self.sender.prepare('fallbacksource',raw,key=self.f.creator['key'],envelope_sender=self.source,recipients=[self.destination],time=self.time)
        review=fallback.preview(raw,['legacy@example.invalid']);self.assertEqual(review['subject'],event['presentation']['subject'])
        fallback.authorize(raw,['legacy@example.invalid'],exposure=review)
        self.sender.prepare('fallbacksource',raw,key=self.f.creator['key'],envelope_sender=self.source,recipients=[self.destination],time=self.time)
        wire=fallback.prepare('fallbackcopy','fallbacksource');smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit_plaintext('fallbackcopy',port=smtp.port,time=self.time)['state'],'accepted')
        smtp.done();self.assertEqual(str(BytesParser(policy=policy.SMTP).parsebytes(wire)['Subject']),event['presentation']['subject'])

class LegacyPresentation(unittest.TestCase):
    setUp=fixture.PrivateCopyLifecycle.setUp;tearDown=fixture.PrivateCopyLifecycle.tearDown
    endpoint=fixture.PrivateCopyLifecycle.endpoint;prepare=fixture.PrivateCopyLifecycle.prepare
    test_signed_four_device_private_roster_admission_and_exact_retry=fixture.PrivateCopyLifecycle.test_signed_four_device_private_roster_admission_and_exact_retry
    def test_older_accepted_profile_does_not_authenticate_outer_subject(self):
        fixture.PrivateCopyLifecycle.test_actual_protected_smtp_message_after_signed_private_admission(self)
        wire=self.identity.db.execute("SELECT wire FROM sender_prepared WHERE id='privatemessage'").fetchone()[0]
        event=dict(principal=self.f.creator['principal'],conversation=self.f.context['conversation'],event='d'*32)
        shown=describe(self.receiver_sender.receiver,event,carrier=hashlib.sha256(unpack(wire)).hexdigest(),transport_wire=wire)
        self.assertEqual(shown['state'],'older-profile');self.assertNotIn('subject',shown);self.assertIn('not authenticated',shown['notice'])

if __name__=='__main__':unittest.main()
