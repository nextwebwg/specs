"""Real signed tuple admission and ordinary SMTP protected attachment delivery."""
import hashlib
import unittest
import test_designated_initial as fixtures
from event_encoding import encode_event
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from mls_mime import unpack
from received_attachments import view,read

class SignedAttachments(unittest.TestCase):
    selected_payload='mime-contribution-v0';selected_operations=['attachment-message','message']
    setUp=fixtures.DesignatedInitialTests.setUp;tearDown=fixtures.DesignatedInitialTests.tearDown
    prepare=fixtures.DesignatedInitialTests.prepare;create=fixtures.DesignatedInitialTests.create
    def test_actual_signed_initial2_then_smtp_attachment(self):
        self.create();a,b=self.f.devices;resource='c'*32;data=b'opaque signed-admission attachment'
        event=dict(version='1',purpose='contribution',event='d'*32,conversation=self.context['conversation'],principal=a['principal'],audience=sorted([a['principal'],b['principal']]),disclosures=[],operation=dict(kind='attachment-message',text='Attached',replyTo=[],manifest=[dict(id=resource,size=str(len(data)),sha256=hashlib.sha256(data).hexdigest())],attachments=[dict(resource=resource,name='note.txt',mediaType='text/plain',description='An authenticated attachment description')]))
        wire=self.sender.prepare('attachment1',encode_event(event),key=a['key'],envelope_sender=self.f.selected[0]['mailbox'],recipients=[self.f.selected[1]['mailbox']],time=self.f.time,resources={resource:data})
        smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit('attachment1',port=smtp.port,time=self.f.time)['state'],'accepted')
        smtp.done();self.assertEqual(smtp.wire,wire)
        receiver=self.receiver_fixture.admission.receiver
        result=receiver.receive(unpack(wire),time=self.f.time,trust_policy='allow-unverified');self.assertEqual(result['applicationState'],'accepted')
        reference={k:event[k] for k in ('principal','conversation','event')}
        self.assertEqual(view(receiver,reference)['attachments'][0]['state'],'available')
        self.assertEqual(read(receiver,reference,resource,carrier=hashlib.sha256(unpack(wire)).hexdigest()),data)
