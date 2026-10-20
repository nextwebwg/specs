"""Signed common roster admission followed by actual rich protected SMTP."""
import hashlib,io,unittest
from PIL import Image
import test_initial_roster_lifecycle as fixture
from initial_roster import parse
from initial_roster_lifecycle import InitialRosterAdmission
from invitation_mime import select
from event_encoding import encode_event
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from mls_mime import unpack
from received_rich import render
class SignedRich(unittest.TestCase):
    application=dict(envelopeVersion='1',payload='mime-rich-v0',operations=['rich-message'])
    setUp=fixture.RosterLifecycleTests.setUp;tearDown=fixture.RosterLifecycleTests.tearDown
    endpoint=fixture.RosterLifecycleTests.endpoint;prepare=fixture.RosterLifecycleTests.prepare
    def test_signed_roster_smtp_then_rich_resource(self):
        ident,invitation=next(iter(self.prepare().items()));smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:worker.submit_initial_roster(ident,port=smtp.port,time=self.time)
        smtp.done();self.assertEqual(smtp.wire,invitation);raw=select(smtp.wire);p=parse(raw)
        target=next(d for d in self.f.devices if d['device']==p['value']['target']['device'] and d['principal']==p['value']['target']['principal'])
        identity,sender,selected=self.endpoint('richreceiver');admission=InitialRosterAdmission(identity,self.f.binary);admission.publish_local(target)
        choices=[dict(principal=d['principal'],device=d['device'],mailbox=c['mailbox'],generation=c['generation']) for d,c in zip(self.f.devices,selected)]
        admission.accept_message(raw,target=target,mailbox=p['value']['target']['mailbox'],allow_creator=self.f.creator['principal'],intended_principals=self.principals,intended_devices=self.devices,expected_context=encode_event(self.f.context),selections=choices,time=self.time,trust_policy='allow-unverified')
        stream=io.BytesIO();Image.new('RGB',(1,1),'red').save(stream,format='PNG');data=stream.getvalue();resource='c'*32
        event=dict(version='1',purpose='contribution',event='d'*32,conversation=self.f.context['conversation'],principal=self.f.creator['principal'],audience=self.principals,disclosures=[],operation=dict(kind='rich-message',text='Red diagram',html='<!doctype html><html><head><meta charset="utf-8"></head><body><img alt="Red diagram" src="cid:'+resource+'.'+'d'*32+'@resources.email-next.invalid"></body></html>',presentation='html-css-v0',replyTo=[],manifest=[dict(id=resource,size=str(len(data)),sha256=hashlib.sha256(data).hexdigest())],embedded=[dict(resource=resource,mediaType='image/png')],attachments=[]))
        source=next(c['mailbox'] for d,c in zip(self.f.devices,self.selected) if d['device']==self.f.creator['device'] and d['principal']==self.f.creator['principal']);recipients=sorted({c['mailbox'] for c in self.selected}-{source})
        wire=self.sender.prepare('richbody',encode_event(event),key=self.f.creator['key'],envelope_sender=source,recipients=recipients,time=self.time,resources={resource:data})
        smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:worker.submit('richbody',port=smtp.port,time=self.time)
        smtp.done();self.assertEqual(smtp.wire,wire);self.assertEqual(sender.receiver.receive(unpack(wire),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        result=render(sender.receiver,{k:event[k] for k in ('principal','conversation','event')},carrier=hashlib.sha256(unpack(wire)).hexdigest());self.assertEqual(next(iter(result['images'].values()))['rgba'],[255,0,0,255])
        self.display_receiver=sender.receiver;self.display_reference={k:event[k] for k in ('principal','conversation','event')};self.display_carrier=hashlib.sha256(unpack(wire)).hexdigest();self.display_text=event['operation']['text']
