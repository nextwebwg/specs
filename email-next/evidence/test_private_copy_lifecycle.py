import base64
import json
import unittest
from event_encoding import encode_event
from provider_mls import sign
from initial_roster import parse
from initial_roster_lifecycle import InitialRosterRelease,InitialRosterAdmission
from invitation_mime import select
import test_initial_roster_lifecycle as fixture

class PrivateCopyLifecycle(unittest.TestCase):
    endpoint=fixture.RosterLifecycleTests.endpoint
    prepare=fixture.RosterLifecycleTests.prepare
    tearDown=fixture.RosterLifecycleTests.tearDown
    def setUp(self):
        fixture.RosterLifecycleTests.setUp(self)
        creator=self.f.creator['principal'];recipient=next(d['principal'] for d in self.f.devices if d['principal']!=creator)
        chosen=[(d,p) for d,p in zip(self.f.devices,self.f.proofs) if d['principal'] in (creator,recipient)]
        self.f.devices=[d for d,p in chosen];self.f.proofs=[];self.f.bundles={k:v for k,v in self.f.bundles.items() if k in (creator,recipient)}
        self.f.context.update(version='5',delivery=dict(kind='private-copy-v0',originator=creator,recipient=recipient),application=dict(envelopeVersion='2',payload='mime-rich-v0',operations=['answer','attachment-message','message','question','reaction','reaction-withdraw','rich-message']))
        for d,p in chosen:
            v=json.loads(base64.b64decode(p['payload']));v.update(version='4',applications=[dict(self.f.context['application'],ordering='designated-member-v0')]);raw=encode_event(v)
            self.f.proofs.append(dict(p,payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,d,'email-next/passive-discovery/v4',raw)))
        self.identity,self.sender,self.selected=self.endpoint('private-creator');self.release=InitialRosterRelease(self.sender)
        self.principals=sorted({d['principal'] for d in self.f.devices});self.devices=[{k:d[k] for k in ('principal','device')} for d in self.f.devices]
    def test_signed_four_device_private_roster_admission_and_exact_retry(self):
        wires=self.prepare();self.assertEqual(len(wires),3);self.assertEqual(self.prepare(),wires)
        for i,wire in enumerate(wires.values()):
            p=parse(select(wire));self.assertEqual(p['value']['version'],'4');self.assertEqual(p['roster']['version'],'1');self.assertEqual(p['context']['delivery'],self.f.context['delivery'])
            target=next(d for d in self.f.devices if d['device']==p['value']['target']['device'])
            identity,sender,selected=self.endpoint('private-target'+str(i));admission=InitialRosterAdmission(identity,self.f.binary);admission.publish_local(target)
            choices=[dict(principal=d['principal'],device=d['device'],mailbox=c['mailbox'],generation=c['generation']) for d,c in zip(self.f.devices,selected)]
            args=dict(target=target,mailbox=p['value']['target']['mailbox'],allow_creator=self.f.creator['principal'],intended_principals=self.principals,intended_devices=self.devices,expected_context=encode_event(self.f.context),selections=choices,time=self.time,trust_policy='allow-unverified')
            first=admission.accept_message(select(wire),**args);self.assertEqual(admission.accept_message(select(wire),**args),first)
            if target['principal']!=self.f.creator['principal']:self.receiver_sender=sender
    def test_wrong_private_principal_holds_creation(self):
        self.f.context['delivery']['recipient']='enp0:'+'f'*64
        with self.assertRaisesRegex(ValueError,'Private copy principal roster'):self.prepare()
        self.assertIsNone(self.identity.db.execute('SELECT 1 FROM mls_checkpoint').fetchone())

    def test_actual_protected_smtp_message_after_signed_private_admission(self):
        self.test_signed_four_device_private_roster_admission_and_exact_retry()
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        from mls_mime import unpack
        event=dict(version='2',purpose='contribution',event='d'*32,conversation=self.f.context['conversation'],principal=self.f.creator['principal'],audience=self.principals,disclosures=[],operation=dict(kind='message',text='Private conversation',replyTo=[]))
        source=next(c['mailbox'] for d,c in zip(self.f.devices,self.selected) if d['device']==self.f.creator['device'])
        recipients=sorted({c['mailbox'] for c in self.selected}-{source})
        wire=self.sender.prepare('privatemessage',encode_event(event),key=self.f.creator['key'],envelope_sender=source,recipients=recipients,time=self.time)
        smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:worker.submit('privatemessage',port=smtp.port,time=self.time)
        smtp.done();self.assertEqual(smtp.wire,wire)
        self.assertEqual(self.receiver_sender.receiver.receive(unpack(wire),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
    def test_actual_third_principal_commit_is_rejected(self):
        self.prepare()
        from group_transitions import GroupTransitions
        from transition_support import TransitionSupport
        from provider_mls import make_device,advertisement
        new=make_device(self.f.binary,7,8);self.identity.observe(new['record'],first_contact_policy='allow-unverified')
        wrapper=advertisement(self.f.binary,new,'unrelated@example.invalid');value=json.loads(base64.b64decode(wrapper['payload']))
        value.update(version='4',applications=[dict(self.f.context['application'],ordering='designated-member-v0')]);raw=encode_event(value)
        wrapper.update(payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,new,'email-next/passive-discovery/v4',raw))
        group=GroupTransitions(self.identity,self.f.binary.with_name('group-transitions'),self.f.creator)
        TransitionSupport(group).confirm(encode_event(wrapper),time=self.time)
        decision=group.prepare([new['package']])
        with self.assertRaisesRegex(ValueError,'Private copy principal roster'):group.decide(decision,allowed={(new['identity'],new['key'])},time=self.time)
        self.assertEqual(group.live()['snapshot']['epoch'],'1')
    def test_same_principal_device_add_and_established4_actual_smtp(self):
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
        self.assertEqual(parse_established(select_established(wire))[2]['version'],'4')
        self.f.devices=full_devices;self.f.proofs=full_proofs
        identity,sender,_=self.endpoint('privatephone');admission=EstablishedAdmission(identity,self.f.binary);admission.publish_local(phone)
        result=admission.accept_message(select_established(wire),target=phone,mailbox=route['mailbox'],allow_creator=self.f.creator['principal'],expected_context=encode_event(self.f.context),time=self.time)
        self.assertEqual(result['status'],'accepted-unverified')
    def test_private_context_plaintext_fallback_is_explicit_and_actual_smtp(self):
        self.prepare()
        from plaintext_release import PlaintextRelease
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        fallback=PlaintextRelease(self.sender)
        event=dict(version='2',purpose='contribution',event='c'*32,conversation=self.f.context['conversation'],principal=self.f.creator['principal'],audience=self.principals,disclosures=[{'kind':'plaintext-email'}],operation=dict(kind='message',text='Explicitly shared selected text',replyTo=[]));raw=encode_event(event)
        source=next(c['mailbox'] for d,c in zip(self.f.devices,self.selected) if d is self.f.creator);recipients=sorted({c['mailbox'] for c in self.selected}-{source})
        with self.assertRaisesRegex(ValueError,'Plaintext disclosure plan'):self.sender.prepare('fallbacksource',raw,key=self.f.creator['key'],envelope_sender=source,recipients=recipients,time=self.time)
        fallback.authorize(raw,['legacy@example.invalid']);self.sender.prepare('fallbacksource',raw,key=self.f.creator['key'],envelope_sender=source,recipients=recipients,time=self.time)
        wire=fallback.prepare('fallbackcopy','fallbacksource');smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:worker.submit_plaintext('fallbackcopy',port=smtp.port,time=self.time)
        smtp.done();self.assertEqual(smtp.wire,wire);self.assertIn(b'Explicitly shared selected text',wire)
        for principal in self.principals:self.assertNotIn(principal.encode(),wire)
    def test_private_rich_resource_exact_bytes(self):
        self.test_signed_four_device_private_roster_admission_and_exact_retry()
        import hashlib
        from mls_mime import unpack
        from received_attachments import read
        data=b'opaque private attachment';resource='e'*32
        event=dict(version='2',purpose='contribution',event='f'*32,conversation=self.f.context['conversation'],principal=self.f.creator['principal'],audience=self.principals,disclosures=[],operation=dict(kind='attachment-message',text='Selected attachment',replyTo=[],manifest=[dict(id=resource,size=str(len(data)),sha256=hashlib.sha256(data).hexdigest())],attachments=[dict(resource=resource,name='private.txt',mediaType='text/plain',description='Selected file')]))
        source=next(c['mailbox'] for d,c in zip(self.f.devices,self.selected) if d is self.f.creator)
        wire=self.sender.prepare('privateresource',encode_event(event),key=self.f.creator['key'],envelope_sender=source,recipients=sorted({c['mailbox'] for c in self.selected}-{source}),time=self.time,resources={resource:data})
        self.assertNotIn(data,wire);receiver=self.receiver_sender.receiver
        self.assertEqual(receiver.receive(unpack(wire),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        self.assertEqual(read(receiver,{k:event[k] for k in ('principal','conversation','event')},resource,carrier=hashlib.sha256(unpack(wire)).hexdigest()),data)
