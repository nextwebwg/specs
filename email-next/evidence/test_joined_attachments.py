"""Configured context3 protected resources, accepted event identity and byte access."""
import hashlib
import json
import unittest
from email.parser import BytesParser
from email import policy
import base64
import test_joined_carrier as carrier
from received_attachments import view,read
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from mls_mime import unpack

class JoinedAttachments(unittest.TestCase):
    context_version='3';selected_payload='mime-contribution-v0';selected_operations=['attachment-message','message']
    setUp=carrier.JoinedCarrier.setUp;tearDown=carrier.JoinedCarrier.tearDown
    event=carrier.JoinedCarrier.event;receive=carrier.JoinedCarrier.receive;inject=carrier.JoinedCarrier.inject;ref=carrier.JoinedCarrier.ref
    def attachment(self):
        self.data=b'From: nested@example.invalid\r\nSubject: inert\r\n\r\nprivate attachment bytes'
        self.resource='c'*32
        return self.event(0,'a',dict(kind='attachment-message',text='One attached file',replyTo=[],manifest=[dict(id=self.resource,size=str(len(self.data)),sha256=hashlib.sha256(self.data).hexdigest())],attachments=[dict(resource=self.resource,name='note.eml',mediaType='message/rfc822',description='An opaque attached message')]))
    def prepare(self,event):
        return self.senders[0].prepare(event['event'],json.dumps(event).encode(),key=self.devices[0]['key'],envelope_sender='alice@example.invalid',recipients=['bob@example.invalid'],time=self.time,resources={self.resource:self.data})
    def test_actual_smtp_resource_and_explicit_opaque_read(self):
        event=self.attachment();wire=self.prepare(event);self.assertNotIn(self.data,wire)
        smtp=LocalSMTP()
        with SenderWorker(self.senders[0]) as worker:worker.submit(event['event'],port=smtp.port,time=self.time)
        smtp.done();self.assertIn('accepted',self.receive(1,smtp.wire)[1]['states'].values())
        receiver=self.senders[1].receiver;shown=view(receiver,self.ref(event))
        self.assertEqual(shown['attachments'][0]['state'],'available')
        self.assertEqual(shown['attachments'][0]['description']['mediaType'],'message/rfc822')
        digest=hashlib.sha256(unpack(wire)).hexdigest()
        self.assertEqual(read(receiver,self.ref(event),self.resource,carrier=digest),self.data)
        self.assertEqual(self.prepare(event),wire)
    def test_altered_resource_keeps_event_but_never_exposes_bytes(self):
        event=self.attachment();self.prepare(event)
        entity=self.identities[0].db.execute('SELECT payload FROM sender_payloads WHERE delivery=?',(event['event'],)).fetchone()[0]
        root=BytesParser(policy=policy.SMTP).parsebytes(entity);root.get_payload()[1].set_payload(base64.b64encode(b'x'*len(self.data)).decode())
        wire=self.inject(0,root.as_bytes());self.assertIn('accepted',self.receive(1,wire)[1]['states'].values())
        receiver=self.senders[1].receiver;shown=view(receiver,self.ref(event))
        self.assertEqual(shown['attachments'][0]['state'],'unavailable')
        self.assertEqual(shown['attachments'][0]['diagnostics'][0]['resources'][0]['state'],'digest-mismatch')
        with self.assertRaisesRegex(ValueError,'unavailable'):read(receiver,self.ref(event),self.resource,carrier=hashlib.sha256(unpack(wire)).hexdigest())

    def test_duplicate_scope_and_restart_keep_per_carrier_availability(self):
        from pathlib import Path
        from identity_store import IdentityStore
        from sender_release import SenderRelease
        event=self.attachment();good=self.prepare(event)
        entity=self.identities[0].db.execute('SELECT payload FROM sender_payloads').fetchone()[0]
        for change,expected in [('duplicate','ambiguous'),('scope','missing')]:
            root=BytesParser(policy=policy.SMTP).parsebytes(entity)
            if change=='duplicate':root.attach(root.get_payload()[1])
            else:root.get_payload()[1].replace_header('Content-ID','<'+self.resource+'.'+'f'*32+'@resources.email-next.invalid>')
            wire=self.inject(0,root.as_bytes());self.receive(1,wire)
            shown=view(self.senders[1].receiver,self.ref(event))
            self.assertEqual(shown['attachments'][0]['state'],'unavailable')
            self.assertIn(expected,[d['resources'][0]['state'] for d in shown['attachments'][0]['diagnostics']])
        self.receive(1,good)
        self.identities[1].close();self.identities[1]=IdentityStore(Path(self.temp.name)/'1.sqlite');self.senders[1]=SenderRelease(self.identities[1],self.binary)
        shown=view(self.senders[1].receiver,self.ref(event));self.assertEqual(shown['attachments'][0]['state'],'available')
        self.assertEqual(len(shown['attachments'][0]['carriers']),1)
        self.assertEqual(read(self.senders[1].receiver,self.ref(event),self.resource,carrier=hashlib.sha256(unpack(good)).hexdigest()),self.data)

    def test_resource_fault_and_changed_retry_preserve_transactions(self):
        event=self.attachment();wire=self.prepare(event);db=self.identities[1].db
        before=db.execute('SELECT revision,snapshot FROM mls_checkpoint').fetchone()
        with self.assertRaisesRegex(RuntimeError,'Injected'):self.senders[1].receiver.receive(unpack(wire),time=self.time,trust_policy='allow-unverified',fail_at='receive')
        self.assertEqual(db.execute('SELECT revision,snapshot FROM mls_checkpoint').fetchone(),before)
        self.assertEqual(db.execute('SELECT count(*) FROM mls_received_resources').fetchone()[0],0)
        self.data=b'changed'
        with self.assertRaisesRegex(ValueError,'conflict'):self.prepare(event)
        self.receive(1,wire)
        self.assertEqual(view(self.senders[1].receiver,self.ref(event))['attachments'][0]['state'],'available')
