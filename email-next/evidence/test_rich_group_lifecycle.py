"""Signed roster3/context4 → accepted Add → established3 over actual local SMTP."""
import base64,hashlib,io,json,unittest,uuid
from unittest.mock import patch
from PIL import Image
import test_initial_roster_lifecycle as fixture
from identity_store import IdentityStore
from provider_mls import make_device,advertisement,sign,call
from event_encoding import encode_event
from group_transitions import GroupTransitions
from transition_support import TransitionSupport
from commit_history import CommitHistory
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from control_release import ControlRelease
from established_invitation_release import EstablishedInvitationRelease
from established_invitation import EstablishedAdmission,parse
from established_invitation_mime import select
from passive_discovery import decode_passive_discovery
from mls_mime import unpack
from received_rich import render

class RichGroupLifecycle(unittest.TestCase):
    application=dict(envelopeVersion='1',payload='mime-rich-v0',operations=['answer','question','rich-message'])
    setUp=fixture.RosterLifecycleTests.setUp;tearDown=fixture.RosterLifecycleTests.tearDown
    endpoint=fixture.RosterLifecycleTests.endpoint;prepare=fixture.RosterLifecycleTests.prepare
    def configure(self):
        self.prepare();self.g=GroupTransitions(self.identity,self.f.binary.with_name('group-transitions'),self.f.creator);self.history=CommitHistory(self.g,max_count=12,max_bytes=8000000)
        self.new=make_device(self.f.binary,7,8);self.identity.observe(self.new['record'],first_contact_policy='allow-unverified')
        self.source=self.selected[self.f.devices.index(self.f.creator)]['mailbox']
    def proof(self,device):
        w=advertisement(self.f.binary,device,'new@example.invalid');v=json.loads(base64.b64decode(w['payload']));v.update(version='3',record=uuid.uuid4().hex,applications=[dict(self.application,ordering='designated-member-v0')]);raw=encode_event(v);w.update(payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,device,'email-next/passive-discovery/v3',raw));return encode_event(w)
    def route(self,device,wrapper):
        d=decode_passive_discovery(wrapper);a=d['assertion'];mailbox=a['value']['mailbox'];store=self.sender.associations
        store.observe_validated_batch([dict(assertion=a['octets'],signature=d['signature'],signingKey=bytes.fromhex(device['key']),outerFrom=[mailbox],sourceId=a['digest'],parserRevision='rich-lifecycle',observedAt=self.time['earliest'])])
        if store._current(mailbox) is None:store.decide(decision_id=uuid.uuid4().hex,mailbox=mailbox,expected_generation=None,kind='first-contact',principal=device['principal'],actor='configured-policy',policy_revision='1',trust_policy='allow-unverified',time=self.time)
        return dict(mailbox=mailbox,generation=store._current(mailbox)['generation'],principal=device['principal'],observation=a['digest'])
    def add(self,device,*,name='add'):
        proof=self.proof(device);route=self.route(device,proof);TransitionSupport(self.g).confirm(proof,time=self.time)
        with patch.object(TransitionSupport,'confirm',side_effect=AssertionError('Original roster proofs must suffice')):
            decision=self.g.prepare([device['package']]);self.assertEqual(self.g.decide(decision,allowed={(device['identity'],device['key'])},time=self.time),'accepted')
        controls=[]
        for index,(d,c) in enumerate(zip(self.f.devices,self.selected)):
            if d is self.f.creator:continue
            delivery=name+str(index);controls.append(delivery)
            ControlRelease(self.sender).prepare(delivery,decision,key=self.f.creator['key'],envelope_sender=self.source,recipients=[dict(mailbox=c['mailbox'],principal=d['principal'],device=d['device'])],association_targets=[dict(mailbox=c['mailbox'],generation=c['generation'],principal=d['principal'],observation=c['digest'])],time=self.time)
        release=EstablishedInvitationRelease(self.sender,self.history);wire=release.prepare(name+'welcome',decision,key=self.f.creator['key'],creator_bundle=self.f.bundles[self.f.creator['principal']],selected_wrapper=proof,association_target=route,predecessor_deliveries=controls,envelope_sender=self.source,not_before=self.time['earliest'],not_after=str(int(self.time['latest'])+30),time=self.time)
        with SenderWorker(self.sender) as worker:
            for control in controls:
                smtp=LocalSMTP();self.assertEqual(worker.submit_control(control,port=smtp.port,time=self.time)['state'],'accepted');smtp.done()
            smtp=LocalSMTP();self.assertEqual(worker.submit_established_invitation(name+'welcome',history=self.history,port=smtp.port,time=self.time)['state'],'accepted');smtp.done();self.assertEqual(smtp.wire,wire)
        self.assertEqual(parse(select(wire))[2]['version'],'3');return wire,decision,route
    def admit(self,wire,device,*,name='new'):
        identity,sender,_=self.endpoint(name);identity.observe(device['record'],first_contact_policy='allow-unverified');admission=EstablishedAdmission(identity,self.f.binary);admission.publish_local(device)
        args=dict(target=device,mailbox='new@example.invalid',allow_creator=self.f.creator['principal'],expected_context=encode_event(self.f.context),time=self.time)
        result=admission.accept_message(select(wire),**args);self.assertEqual(admission.accept_message(select(wire),**args),result);return identity,sender,admission,result
    def rich(self,receiver,*,delivery='richbody',event_id='d'*32):
        image=io.BytesIO();Image.new('RGB',(1,1),'red').save(image,format='PNG');data=image.getvalue();rid='c'*32;attachment=b'actual attachment';aid='e'*32
        audience=sorted(self.principals+[self.new['principal']]);event=dict(version='1',purpose='contribution',event=event_id,conversation=self.f.context['conversation'],principal=self.f.creator['principal'],audience=audience,disclosures=[],operation=dict(kind='rich-message',text='Red diagram and file',html='<!doctype html><html><head><meta charset="utf-8"></head><body><img alt="Red diagram" src="cid:'+rid+'.'+event_id+'@resources.email-next.invalid"></body></html>',presentation='html-css-v0',replyTo=[],manifest=[dict(id=rid,size=str(len(data)),sha256=hashlib.sha256(data).hexdigest()),dict(id=aid,size=str(len(attachment)),sha256=hashlib.sha256(attachment).hexdigest())],embedded=[dict(resource=rid,mediaType='image/png')],attachments=[dict(resource=aid,mediaType='text/plain',name='notes.txt',description='Notes')]))
        wire=self.sender.prepare(delivery,encode_event(event),key=self.f.creator['key'],envelope_sender=self.source,recipients=['new@example.invalid'],time=self.time,resources={rid:data,aid:attachment});smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit(delivery,port=smtp.port,time=self.time)['state'],'accepted')
        smtp.done();self.assertEqual(receiver.receive(unpack(smtp.wire),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted');result=render(receiver,{k:event[k] for k in ('principal','conversation','event')},carrier=hashlib.sha256(unpack(wire)).hexdigest());self.assertEqual(next(iter(result['images'].values()))['rgba'],[255,0,0,255])
        from received_attachments import read
        self.assertEqual(read(receiver,{k:event[k] for k in ('principal','conversation','event')},aid,carrier=hashlib.sha256(unpack(wire)).hexdigest()),attachment);return event
    def test_signed_initial_rich_add_established3_smtp_and_resource(self):
        self.configure();wire,decision,route=self.add(self.new);identity,sender,admission,result=self.admit(wire,self.new)
        self.rich(sender.receiver);self.assertEqual(result['historyShared'],False)
    def test_old_established_version_cannot_claim_context4(self):
        self.configure();wire,_,_=self.add(self.new);wrapper=json.loads(select(wire));value=json.loads(base64.b64decode(wrapper['payload']));value['version']='2';wrapper['payload']=base64.b64encode(encode_event(value)).decode()
        with self.assertRaisesRegex(ValueError,'Context'):parse(encode_event(wrapper))

    def test_smtp_same_key_fresh_package_rejoin_keeps_old_pending_ended(self):
        from terminal_removal_release import TerminalRemovalRelease
        from transition_carrier import receive_mime
        self.configure();wire,_,route=self.add(self.new);identity,peer,admission,first=self.admit(wire,self.new)
        target_group=GroupTransitions(identity,self.f.binary.with_name('group-transitions'),self.new)
        event=dict(version='1',purpose='contribution',event='6'*32,conversation=self.f.context['conversation'],principal=self.f.creator['principal'],audience=sorted(self.principals+[self.new['principal']]),disclosures=[],operation=dict(kind='answer',question=dict(principal=self.f.creator['principal'],conversation=self.f.context['conversation'],event='5'*32),option='7'*32,replaces=[]))
        from protected_carrier import package_carrier
        from application_payload import DEFAULT_LIMITS
        state=self.g.live();payload=package_carrier(encode_event(event),'Pending answer','<p>Pending answer</p>',**DEFAULT_LIMITS)
        pending=call(self.f.binary,op='send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.f.creator['key'],application=payload.hex())
        self.assertEqual(peer.receiver.receive(bytes.fromhex(pending['wire']),time=self.time,trust_policy='allow-unverified')['status'],'pending')
        from_peer=dict(event,event='9'*32,principal=self.new['principal'],operation=dict(event['operation'],question=dict(event['operation']['question'],principal=self.new['principal'])))
        peer_state=target_group.live();peer_payload=package_carrier(encode_event(from_peer),'Pending answer','<p>Pending answer</p>',**DEFAULT_LIMITS)
        incoming=call(self.f.binary,op='send',checkpoint=peer_state['checkpoint'],group=peer_state['snapshot']['group'],key=self.new['key'],application=peer_payload.hex())
        self.assertEqual(self.sender.receiver.receive(bytes.fromhex(incoming['wire']),time=self.time,trust_policy='allow-unverified')['status'],'pending')
        removed=self.g.prepare_removal([dict(identity=self.new['identity'],key=self.new['key'])],time=self.time);self.assertEqual(self.g.decide(removed,allowed=set(),time=self.time),'accepted')
        self.assertEqual(list(self.sender.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')['states'].values()),['held:membership-episode'])
        terminal=TerminalRemovalRelease(self.sender,self.history);terminal.prepare('removed',removed,key=self.f.creator['key'],target_identity=self.new['identity'],target_key=self.new['key'],association_target=route,envelope_sender=self.source,time=self.time)
        with SenderWorker(self.sender) as worker:
            smtp=LocalSMTP();self.assertEqual(worker.submit_terminal_removal('removed',history=self.history,port=smtp.port,time=self.time)['state'],'accepted');smtp.done();self.assertEqual(receive_mime(target_group,smtp.wire,allowed=set(),time=self.time),'accepted');terminal.finish('removed',worker=worker)
        old_package=self.new['package'];self.new=dict(self.new,**call(self.f.binary,op='fresh-package',checkpoint=self.new['checkpoint'],key=self.new['key'],identity=self.new['identity']));self.assertNotEqual(self.new['package'],old_package)
        wire,_,_=self.add(self.new,name='rejoin');admission.publish_local(self.new);joined=admission.accept_message(select(wire),target=self.new,mailbox='new@example.invalid',allow_creator=self.f.creator['principal'],expected_context=encode_event(self.f.context),time=self.time)
        self.assertNotEqual(joined['instance'],first['instance']);self.assertEqual(list(peer.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')['states'].values()),['held:membership-instance'])
        self.assertEqual(list(self.sender.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')['states'].values()),['held:membership-episode'])
        self.rich(peer.receiver,delivery='afterrejoin');self.assertEqual(admission.accept_message(select(wire),target=self.new,mailbox='new@example.invalid',allow_creator=self.f.creator['principal'],expected_context=encode_event(self.f.context),time=self.time),joined)

    def test_wrong_established_domain_leaves_package_available_for_exact_retry(self):
        self.configure();wire,_,_=self.add(self.new);identity,peer,_=self.endpoint('wrongdomain');identity.observe(self.new['record'],first_contact_policy='allow-unverified');admission=EstablishedAdmission(identity,self.f.binary);admission.publish_local(self.new)
        wrapper=json.loads(select(wire));raw=base64.b64decode(wrapper['payload']);wrapper['signature']=sign(self.f.binary,self.f.creator,'email-next/mls-established-membership-invitation/v2',raw)
        args=dict(target=self.new,mailbox='new@example.invalid',allow_creator=self.f.creator['principal'],expected_context=encode_event(self.f.context),time=self.time)
        with self.assertRaises(ValueError):admission.accept_message(encode_event(wrapper),**args)
        self.assertIsNone(identity.db.execute('SELECT invitation FROM provider_mls_admission WHERE reference=?',(self.new['reference'],)).fetchone()[0]);self.assertEqual(identity.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0],0)
        original=json.loads(select(wire));value=json.loads(base64.b64decode(original['payload']));proof=next(json.loads(base64.b64decode(p['payload'])) for p in original['applicationAssertions'] if json.loads(base64.b64decode(p['payload']))['principal']==self.new['principal'])
        value['notAfter']=str(int(proof['notAfter'])+1);too_long=encode_event(value);original.update(payload=base64.b64encode(too_long).decode(),signature=sign(self.f.binary,self.f.creator,'email-next/mls-established-membership-invitation/v3',too_long))
        with self.assertRaisesRegex(ValueError,'Fresh target support'):admission.accept_message(encode_event(original),**args)
        self.assertIsNone(identity.db.execute('SELECT invitation FROM provider_mls_admission WHERE reference=?',(self.new['reference'],)).fetchone()[0])
        self.assertEqual(admission.accept_message(select(wire),**args)['status'],'accepted-unverified')

    def test_expired_original_roster_proofs_remain_historical_only(self):
        for i,(device,choice) in enumerate(zip(self.f.devices,self.selected)):
            wrapper=json.loads(choice['wrapper']);value=json.loads(base64.b64decode(wrapper['payload']));value.update(record=uuid.uuid4().hex,notAfter=str(int(self.time['latest'])+30));payload=encode_event(value);wrapper.update(payload=base64.b64encode(payload).decode(),signature=sign(self.f.binary,device,'email-next/passive-discovery/v3',payload));raw=encode_event(wrapper);route=self.route(device,raw);self.selected[i]=dict(choice,wrapper=raw,digest=route['observation'])
        self.configure();self.time={k:str(int(v)+31) for k,v in self.time.items()}
        # Current routing is separate from historical capability selection.
        for i,(device,choice) in enumerate(zip(self.f.devices,self.selected)):
            wrapper=json.loads(choice['wrapper']);value=json.loads(base64.b64decode(wrapper['payload']));value.update(record=uuid.uuid4().hex,notAfter=str(int(self.time['latest'])+60));payload=encode_event(value);wrapper.update(payload=base64.b64encode(payload).decode(),signature=sign(self.f.binary,device,'email-next/passive-discovery/v3',payload));raw=encode_event(wrapper);route=self.route(device,raw);self.selected[i]=dict(choice,wrapper=raw,digest=route['observation'])
        wire,_,_=self.add(self.new)
        _,_,admission,accepted=self.admit(wire,self.new);self.assertEqual(accepted['status'],'accepted-unverified')
        wrapper,_,value,_,_=parse(select(wire));originals=[json.loads(base64.b64decode(p['payload'])) for p in wrapper['applicationAssertions'] if json.loads(base64.b64decode(p['payload']))['principal']!=self.new['principal']]
        self.assertTrue(all(int(p['notAfter'])<int(self.time['earliest']) for p in originals))

    def test_established3_recipient_reuses_original_proofs_on_later_commit(self):
        from transition_carrier import receive_mime
        self.configure();wire,_,route=self.add(self.new);identity,peer,_,_=self.admit(wire,self.new)
        recipient=GroupTransitions(identity,self.f.binary.with_name('group-transitions'),self.new);next_device=make_device(self.f.binary,9,10);proof=self.proof(next_device)
        for store in [self.identity,identity]:store.observe(next_device['record'],first_contact_policy='allow-unverified')
        for group in [self.g,recipient]:TransitionSupport(group).confirm(proof,time=self.time)
        with patch.object(TransitionSupport,'confirm',side_effect=AssertionError('No historical member reconfirmation')):
            decision=self.g.prepare([next_device['package']]);self.assertEqual(self.g.decide(decision,allowed={(next_device['identity'],next_device['key'])},time=self.time),'accepted')
            control=ControlRelease(self.sender);control.prepare('nextcommit',decision,key=self.f.creator['key'],envelope_sender=self.source,recipients=[dict(mailbox=route['mailbox'],principal=self.new['principal'],device=self.new['device'])],association_targets=[route],time=self.time)
            with SenderWorker(self.sender) as worker:
                smtp=LocalSMTP();self.assertEqual(worker.submit_control('nextcommit',port=smtp.port,time=self.time)['state'],'accepted');smtp.done()
            self.assertEqual(receive_mime(recipient,smtp.wire,allowed={(next_device['identity'],next_device['key'])},time=self.time),'accepted')
        self.assertEqual(identity.db.execute('SELECT count(*) FROM mls_support_records WHERE cast(record AS TEXT) LIKE ?',('%signed-established-admission%',)).fetchone()[0],7)

class SharedMailboxRichGroup(RichGroupLifecycle):
    def endpoint(self,name):
        from sender_release import SenderRelease
        from passive_discovery_verify import verify_passive_discovery
        if not getattr(self,'shared_adjusted',False):
            for device,proof in zip(self.f.devices,self.f.proofs):
                value=json.loads(base64.b64decode(proof['payload']));value['mailbox']='account'+device['principal'][5:9]+'@example.invalid';raw=encode_event(value)
                proof.update(payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,device,'email-next/passive-discovery/v3',raw))
            self.shared_adjusted=True
        identity=IdentityStore(self.temp.name+'/'+name+'.sqlite');self.stores.append(identity)
        for principal,bundle in self.f.bundles.items():
            first=next(d for d in self.f.devices if d['principal']==principal);identity.observe(first['record'],first_contact_policy='allow-unverified');identity.accept_successor(encode_event(bundle),candidate_digest=self.f.heads[principal],time=self.time)
        sender=SenderRelease(identity,self.f.binary);sender.configure(expected_revision=0);selected=[]
        for device,proof in zip(self.f.devices,self.f.proofs):
            raw=encode_event(proof);d=decode_passive_discovery(raw);a=d['assertion'];mailbox=a['value']['mailbox'];self.assertEqual(verify_passive_discovery(raw,identity,time=self.time,trust_policy='allow-unverified')['status'],'snapshot-authorized-unverified')
            sender.associations.observe_validated_batch([dict(assertion=a['octets'],signature=d['signature'],signingKey=bytes.fromhex(device['key']),outerFrom=[mailbox],sourceId='shared-mailbox',parserRevision='test',observedAt=self.time['earliest'])])
            if sender.associations._current(mailbox) is None:sender.associations.decide(decision_id=uuid.uuid4().hex,mailbox=mailbox,expected_generation=None,kind='first-contact',principal=device['principal'],actor='configured-policy',policy_revision='1',trust_policy='allow-unverified',time=self.time)
            selected.append(dict(wrapper=raw,mailbox=mailbox,generation='1',digest=a['digest']))
        return identity,sender,selected

    def test_shared_mailbox_caller_labels_without_association_cannot_count(self):
        self.configure();_,decision,_=self.add(self.new);deliveries=[]
        for i,(d,c) in enumerate(zip(self.f.devices,self.selected)):
            if d is self.f.creator:continue
            delivery='unbound'+str(i);deliveries.append(delivery);ControlRelease(self.sender).prepare(delivery,decision,key=self.f.creator['key'],envelope_sender=self.source,recipients=[dict(mailbox=c['mailbox'],principal=d['principal'],device=d['device'])],time=self.time)
        release=EstablishedInvitationRelease(self.sender,self.history);record,_=release._decision(decision)
        with self.assertRaisesRegex(ValueError,'separate evidence-bound'):release._ordering(record,deliveries,require_accepted=False)


import test_initial_roster_catchup as catchup_fixture
class RichRosterCatchup(catchup_fixture.RosterCatchupTests):
    application=dict(envelopeVersion='1',payload='mime-rich-v0',operations=['rich-message'])
