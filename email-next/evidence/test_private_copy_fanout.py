import base64,json,unittest
import test_initial_roster_lifecycle as fixture
from provider_mls import sign
from initial_roster import parse
from initial_roster_lifecycle import InitialRosterRelease,InitialRosterAdmission
from invitation_mime import select
from event_encoding import encode_event
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from mls_mime import unpack
from private_copy_plan import authorize

class PrivateFanout(unittest.TestCase):
    endpoint=fixture.RosterLifecycleTests.endpoint
    tearDown=fixture.RosterLifecycleTests.tearDown
    def setUp(self):
        fixture.RosterLifecycleTests.setUp(self)
        self.original_devices=list(self.f.devices);self.original_proofs=list(self.f.proofs);self.original_bundles=dict(self.f.bundles)
        from provider_mls import make_device,advertisement
        from test_group_transitions import enroll
        from initial_roster import sha
        extra=make_device(self.f.binary,7,8);phone=make_device(self.f.binary,7,18);bundle,head=enroll(self.f.binary,extra,phone)
        self.original_bundles[extra['principal']]=bundle;self.f.heads[extra['principal']]=head
        for d in (extra,phone):
            wrapper=advertisement(self.f.binary,d,'extra'+d['device'][5:9]+'@example.invalid');v=json.loads(base64.b64decode(wrapper['payload']))
            binding=next(b for b in bundle['bindings'] if json.loads(base64.b64decode(b['payload']))['device']==d['device'])
            v.update(state=head,binding=sha(base64.b64decode(binding['payload'])))
            wrapper.update(payload=base64.b64encode(encode_event(v)).decode(),identity=bundle)
            self.original_devices.append(d);self.original_proofs.append(wrapper)
        self.f.time=str(max(int(d['time']) for d in self.original_devices));self.time=dict(earliest=self.f.time,latest=self.f.time)
        self.groups=[];creator=self.f.creator
        others=sorted(set(self.original_bundles)-{creator['principal']})
        for index,recipient in enumerate(others):
            pairs=[(d,p) for d,p in zip(self.original_devices,self.original_proofs) if d is creator or d['principal']==recipient]
            self.f.devices=[d for d,p in pairs];self.f.bundles={k:v for k,v in self.original_bundles.items() if k in (creator['principal'],recipient)}
            context=dict(self.f.context,version='5',conversation=str(index+7)*32,application=dict(envelopeVersion='2',payload='mime-rich-v0',operations=['answer','message','question']),delivery={'kind':'ordinary-v0'} if index==0 else dict(kind='private-copy-v0',originator=creator['principal'],recipient=recipient))
            self.f.context=context;self.f.proofs=[]
            for d,p in pairs:
                v=json.loads(base64.b64decode(p['payload']));v.update(version='4',applications=[dict(context['application'],ordering='designated-member-v0')]);raw=encode_event(v)
                self.f.proofs.append(dict(p,payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,d,'email-next/passive-discovery/v4',raw)))
            identity,sender,selected=self.endpoint('author'+str(index));release=InitialRosterRelease(sender)
            principals=sorted({d['principal'] for d in self.f.devices});devices=[{k:d[k] for k in ('principal','device')} for d in self.f.devices]
            wires=release.prepare(str(index+1)*32,device=creator,selected=selected,intended_principals=principals,intended_devices=devices,context=context,not_before=self.f.time,not_after=str(int(self.f.time)+30),time=self.time)
            ident,wire=next(iter(wires.items()));smtp=LocalSMTP()
            with SenderWorker(sender) as worker:worker.submit_initial_roster(ident,port=smtp.port,time=self.time)
            smtp.done();self.assertEqual(smtp.wire,wire);p=parse(select(wire));target=next(d for d in self.f.devices if d['device']==p['value']['target']['device'])
            ri,rs,choices=self.endpoint('recipient'+str(index));admission=InitialRosterAdmission(ri,self.f.binary);admission.publish_local(target)
            admission.accept_message(select(wire),target=target,mailbox=p['value']['target']['mailbox'],allow_creator=creator['principal'],intended_principals=principals,intended_devices=devices,expected_context=encode_event(context),selections=[dict(principal=d['principal'],device=d['device'],mailbox=c['mailbox'],generation=c['generation']) for d,c in zip(self.f.devices,choices)],time=self.time,trust_policy='allow-unverified')
            source=next(c['mailbox'] for d,c in zip(self.f.devices,selected) if d is creator);recipients=sorted({c['mailbox'] for c in selected}-{source})
            self.groups.append(dict(sender=sender,receiver=rs,target=target,target_address=p['value']['target']['mailbox'],context=context,audience=principals,source=source,recipients=recipients))
    def test_independent_question_copies_real_smtp_and_private_answer(self):
        events=[]
        for i,g in enumerate(self.groups):events.append(dict(version='2',purpose='contribution',event=str(i+4)*32,conversation=g['context']['conversation'],principal=self.f.creator['principal'],audience=g['audience'],disclosures=[{'kind':'separate-protected-copy'}],operation=dict(kind='question',text='Which day?',options=[dict(id='a'*32,label='Friday')])) )
        self.events=events
        raws=[encode_event(e) for e in events]
        for i,g in enumerate(self.groups):
            with self.assertRaisesRegex(ValueError,'Private copy disclosure plan'):g['sender'].prepare('copy',raws[i],key=self.f.creator['key'],envelope_sender=g['source'],recipients=g['recipients'],time=self.time)
            authorize(g['sender'],raws[i],other_copies=[raw for j,raw in enumerate(raws) if j!=i],expected_revision=1)
            wire=g['sender'].prepare('copy',raws[i],key=self.f.creator['key'],envelope_sender=g['source'],recipients=g['recipients'],time=self.time)
            self.assertEqual(g['sender'].prepare('copy',raws[i],key=self.f.creator['key'],envelope_sender=g['source'],recipients=g['recipients'],time=self.time),wire)
            smtp=LocalSMTP()
            with SenderWorker(g['sender']) as worker:worker.submit('copy',port=smtp.port,time=self.time)
            smtp.done();self.assertEqual(smtp.wire,wire);g['wire']=wire
            result=g['receiver'].receiver.receive(unpack(wire),time=self.time,trust_policy='allow-unverified');self.assertEqual(result['applicationState'],'accepted')
            self.assertNotIn(b'Bcc:',wire)
            for j,other in enumerate(self.groups):
                if j!=i:
                    self.assertNotIn(events[j]['conversation'].encode(),raws[i]);self.assertNotIn(next(p for p in other['audience'] if p!=self.f.creator['principal']).encode(),raws[i])
        import hashlib
        from private_copy_view import describe
        blind=self.groups[1];private_ref={k:events[1][k] for k in ('principal','conversation','event')}
        shown=describe(blind['receiver'].receiver,private_ref,carrier=hashlib.sha256(unpack(blind['wire'])).hexdigest(),local_principal=blind['target']['principal'])
        self.presentation=shown
        self.assertEqual(shown['label'],'Private copy');self.assertEqual(shown['replyPrincipal'],self.f.creator['principal'])
        self.assertNotIn(self.groups[0]['context']['conversation'],json.dumps(shown))
        from client_flow import ClientFlow
        from journal_button_view import derive_button_view
        g=self.groups[1];ref={k:events[1][k] for k in ('principal','conversation','event')};view=derive_button_view(g['receiver'].receiver.journal,ref)
        target_address=g['target_address']
        client=ClientFlow(g['receiver'],key=g['target']['key'],envelope_sender=target_address,recipients=[g['source']])
        result=client.answer('answer',ref,'a'*32,view['sourceToken'],time=self.time)
        smtp=LocalSMTP()
        with SenderWorker(g['receiver']) as worker:worker.submit('answer',port=smtp.port,time=self.time)
        smtp.done();self.assertEqual(smtp.wire,result)
        self.assertEqual(g['sender'].receiver.receive(unpack(result),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        self.assertEqual(len(derive_button_view(g['sender'].receiver.journal,ref)['heads']),1)
        visible={k:events[0][k] for k in ('principal','conversation','event')}
        self.assertEqual(derive_button_view(self.groups[0]['sender'].receiver.journal,visible)['heads'],[])
        self.assertEqual(client.answer('answer',ref,'a'*32,view['sourceToken'],time=self.time),result)
