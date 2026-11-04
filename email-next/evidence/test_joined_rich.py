import base64,hashlib,io,json,unittest
from email import policy
from unittest.mock import patch
from email.parser import BytesParser
from PIL import Image
import test_joined_carrier as fixture
from received_rich import render
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from mls_mime import unpack
class JoinedRich(unittest.TestCase):
    context_version='4';selected_payload='mime-rich-v0';selected_operations=['message','rich-message']
    tearDown=fixture.JoinedCarrier.tearDown
    def setUp(self):
        fixture.JoinedCarrier.setUp(self)
        # These historical carrier/resource fixtures use a declared fixed time.
        # Advancing release clocks are covered by sender-association tests.
        clock=patch('sender_worker.elapsed_time.monotonic_ns',return_value=0)
        clock.start();self.addCleanup(clock.stop)
    event=fixture.JoinedCarrier.event;receive=fixture.JoinedCarrier.receive;inject=fixture.JoinedCarrier.inject;ref=fixture.JoinedCarrier.ref
    def rich(self):
        self.resource='c'*32;stream=io.BytesIO();Image.new('RGB',(2,2),'blue').save(stream,format='PNG');self.data=stream.getvalue()
        return self.event(0,'a',dict(kind='rich-message',text='Update Blue diagram',html='<!doctype html><html><head><meta charset="utf-8"></head><body><h2>Update</h2><img alt="Blue diagram" src="cid:'+self.resource+'.'+'a'*32+'@resources.email-next.invalid"></body></html>',presentation='html-css-v0',replyTo=[],manifest=[dict(id=self.resource,size=str(len(self.data)),sha256=hashlib.sha256(self.data).hexdigest())],embedded=[dict(resource=self.resource,mediaType='image/png')],attachments=[]))
    def prepare(self,e):return self.senders[0].prepare(e['event'],json.dumps(e).encode(),key=self.devices[0]['key'],envelope_sender='alice@example.invalid',recipients=['bob@example.invalid'],time=self.time,resources={self.resource:self.data})
    def test_actual_smtp_accepted_body_and_scoped_pixels(self):
        event=self.rich();wire=self.prepare(event);smtp=LocalSMTP()
        with SenderWorker(self.senders[0]) as worker:worker.submit(event['event'],port=smtp.port,time=self.time)
        smtp.done();self.assertIn('accepted',self.receive(1,smtp.wire)[1]['states'].values())
        result=render(self.senders[1].receiver,self.ref(event),carrier=hashlib.sha256(unpack(wire)).hexdigest())
        self.assertEqual(result['state'],'rich');self.assertEqual(next(iter(result['images'].values()))['rgba'],[0,0,255,255]*4)
    def test_well_decoded_mime_mismatch_keeps_authenticated_html_authoritative(self):
        event=self.rich();self.prepare(event)
        payload=self.identities[0].db.execute('SELECT payload FROM sender_payloads').fetchone()[0]
        root=BytesParser(policy=policy.SMTP).parsebytes(payload)
        decoy=b'<!doctype html><html><head><meta charset="utf-8"></head><body><p>MIME DECOY</p></body></html>'
        root.get_payload()[1].get_payload()[0].set_payload(base64.b64encode(decoy).decode('ascii'))
        wire=self.inject(0,root.as_bytes());result=self.receive(1,wire)
        self.assertIn('accepted',result[1]['states'].values())
        self.assertEqual(result[0]['projection'],'mismatch')
        receiver=self.senders[1].receiver
        local=receiver.journal.snapshot(event['conversation'])
        self.assertEqual(json.loads(local[0]['octets'][0]),event)
        rich=render(receiver,self.ref(event),carrier=hashlib.sha256(unpack(wire)).hexdigest())
        self.assertEqual(rich['state'],'rich')
        self.assertIn('Update',json.dumps(rich))
        self.assertNotIn('MIME DECOY',json.dumps(rich))
        self.assertEqual(next(iter(rich['images'].values()))['rgba'],[0,0,255,255]*4)
        self.assertEqual(self.receive(1,wire)[0]['projection'],'mismatch')
        self.assertEqual(len(receiver.journal.snapshot(event['conversation'])),1)

    def test_invalid_utf8_projection_cannot_reserve_event_and_retry_uses_new_native_state(self):
        event=self.rich();self.prepare(event)
        payload=self.identities[0].db.execute('SELECT payload FROM sender_payloads').fetchone()[0]
        root=BytesParser(policy=policy.SMTP).parsebytes(payload)
        root.get_payload()[1].get_payload()[0].set_payload(base64.b64encode(b'\xff').decode('ascii'))
        invalid=self.inject(0,root.as_bytes());result=self.receive(1,invalid)
        self.assertEqual(result[0]['status'],'invalid-application-encoding')
        self.assertEqual(self.senders[1].receiver.journal.snapshot(event['conversation']),[])
        # A new native message carries the original valid payload. No raw fallback
        # or repeated decryption with the invalid carrier's consumed state.
        valid=self.inject(0,payload)
        self.assertIn('accepted',self.receive(1,valid)[1]['states'].values())
        self.assertEqual(len(self.senders[1].receiver.journal.snapshot(event['conversation'])),1)

    def test_corrupt_image_keeps_alt_and_cross_carrier_cannot_render(self):
        event=self.rich();self.prepare(event);payload=self.identities[0].db.execute('SELECT payload FROM sender_payloads').fetchone()[0]
        root=BytesParser(policy=policy.SMTP).parsebytes(payload);root.get_payload()[1].get_payload()[1].set_payload(base64.b64encode(b'x'*len(self.data)).decode())
        wire=self.inject(0,root.as_bytes());self.receive(1,wire)
        result=render(self.senders[1].receiver,self.ref(event),carrier=hashlib.sha256(unpack(wire)).hexdigest())
        self.assertEqual(next(iter(result['images'].values()))['state'],'alt')
        with self.assertRaises(ValueError):render(self.senders[1].receiver,self.ref(event),carrier='0'*64)
    def test_independent_attachment_remains_download_only(self):
        from received_attachments import view,read
        event=self.rich();resource='d'*32;data=b'<html>Never rendered</html>'
        event['operation']['manifest'].append(dict(id=resource,size=str(len(data)),sha256=hashlib.sha256(data).hexdigest()))
        event['operation']['attachments']=[dict(resource=resource,name='opaque.html',mediaType='text/html',description='Download-only source')]
        wire=self.senders[0].prepare(event['event'],json.dumps(event).encode(),key=self.devices[0]['key'],envelope_sender='alice@example.invalid',recipients=['bob@example.invalid'],time=self.time,resources={self.resource:self.data,resource:data})
        self.receive(1,wire);receiver=self.senders[1].receiver;carrier=hashlib.sha256(unpack(wire)).hexdigest()
        self.assertEqual(view(receiver,self.ref(event))['attachments'][0]['state'],'available')
        self.assertEqual(read(receiver,self.ref(event),resource,carrier=carrier),data)
        self.assertEqual(len(render(receiver,self.ref(event),carrier=carrier)['images']),1)
    def test_ordinary_rich_copy_requires_complete_exposure_and_sends_exact_resource(self):
        from plaintext_release import PlaintextRelease
        event=self.rich();event['disclosures']=[dict(kind='plaintext-email')];raw=json.dumps(event).encode();fallback=PlaintextRelease(self.senders[0]);resources={self.resource:self.data};recipients=['legacy@example.invalid']
        with self.assertRaises(ValueError):fallback.authorize(raw,recipients,resources=resources)
        review=fallback.preview(raw,recipients,resources=resources)
        self.assertFalse(review['structuredAlternative']);fallback.authorize(raw,recipients,resources=resources,exposure=review)
        self.prepare(event);wire=fallback.prepare('richordinary',event['event']);smtp=LocalSMTP()
        with SenderWorker(self.senders[0]) as worker:worker.submit_plaintext('richordinary',port=smtp.port,time=self.time)
        smtp.done();parsed=BytesParser(policy=policy.SMTP).parsebytes(smtp.wire)
        self.assertEqual([p.get_payload(decode=True) for p in parsed.walk() if p.get_content_type()=='image/png'],[self.data])
        self.assertFalse(any(p.get_content_type()=='application/vnd.threadlabs.email-next-event+json' for p in parsed.walk()))
        self.assertEqual(wire,fallback.prepare('richordinary',event['event']))

    def test_attachment_in_embedded_slot_is_unavailable_without_projection_crash(self):
        from received_attachments import view,read
        event=self.rich();resource='d'*32
        event['operation']['manifest'].append(dict(id=resource,size=str(len(self.data)),sha256=hashlib.sha256(self.data).hexdigest()))
        event['operation']['attachments']=[dict(resource=resource,name='download.png',mediaType='image/png',description='Download')]
        self.senders[0].prepare(event['event'],json.dumps(event).encode(),key=self.devices[0]['key'],envelope_sender='alice@example.invalid',recipients=['bob@example.invalid'],time=self.time,resources={self.resource:self.data,resource:self.data})
        payload=self.identities[0].db.execute('SELECT payload FROM sender_payloads').fetchone()[0]
        root=BytesParser(policy=policy.SMTP).parsebytes(payload)
        alternatives=root.get_payload()[0]
        if not alternatives.get('MIME-Version'):alternatives['MIME-Version']='1.0'
        embedded=alternatives.get_payload()[1].get_payload()[1]
        embedded.replace_header('Content-ID','<'+resource+'.'+event['event']+'@resources.email-next.invalid>')
        wire=self.inject(0,alternatives.as_bytes());self.receive(1,wire)
        receiver=self.senders[1].receiver;carrier=hashlib.sha256(unpack(wire)).hexdigest()
        item=view(receiver,self.ref(event))['attachments'][0]
        self.assertEqual(item['state'],'unavailable')
        self.assertEqual(item['diagnostics'][0]['resources'][0]['state'],'wrong-role')
        self.assertEqual(item['diagnostics'][0]['metadata'][0]['state'],'missing')
        with self.assertRaises(ValueError):read(receiver,self.ref(event),resource,carrier=carrier)

    def test_unexpected_attachment_does_not_shift_known_projection(self):
        from email.message import EmailMessage
        from received_attachments import view,read
        event=self.rich();resource='d'*32;data=b'expected file'
        event['operation']['manifest'].append(dict(id=resource,size=str(len(data)),sha256=hashlib.sha256(data).hexdigest()))
        event['operation']['attachments']=[dict(resource=resource,name='expected.txt',mediaType='text/plain',description='Expected')]
        self.senders[0].prepare(event['event'],json.dumps(event).encode(),key=self.devices[0]['key'],envelope_sender='alice@example.invalid',recipients=['bob@example.invalid'],time=self.time,resources={self.resource:self.data,resource:data})
        payload=self.identities[0].db.execute('SELECT payload FROM sender_payloads').fetchone()[0]
        root=BytesParser(policy=policy.SMTP).parsebytes(payload)
        extra=EmailMessage(policy=policy.SMTP)
        extra.set_content(b'unexpected',maintype='application',subtype='octet-stream',cte='base64')
        extra['Content-ID']='<'+('e'*32)+'.'+event['event']+'@resources.email-next.invalid>'
        extra.add_header('Content-Disposition','attachment',filename='unrelated.bin')
        children=list(root.iter_parts());root.set_payload([children[0],extra,*children[1:]])
        wire=self.inject(0,root.as_bytes());self.receive(1,wire)
        receiver=self.senders[1].receiver;carrier=hashlib.sha256(unpack(wire)).hexdigest()
        item=view(receiver,self.ref(event))['attachments'][0]
        self.assertEqual(item['state'],'available')
        self.assertEqual(item['diagnostics'][0]['metadata'][0]['state'],'matched')
        self.assertEqual(read(receiver,self.ref(event),resource,carrier=carrier),data)
