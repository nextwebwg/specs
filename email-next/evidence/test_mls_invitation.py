import base64
import copy
import json
import unittest
from email import policy
from email.parser import BytesParser
import test_provider_mls as integration
from provider_mls import call,sign,advertisement
from mls_invitation import InvitationAdmission,parse
from invitation_mime import package,select
from event_encoding import encode_event


class InvitationTests(integration.ProviderMlsTests):
    # Reuse setup and real retained keys; only own tests are selected below.
    def invitation(self,embedded=True,creator=None):
        creator=creator or self.a
        invited=call(self.binary,op='invite',checkpoint=self.a['checkpoint'],key=self.a['key'],identity=self.a['identity'],package=self.b['package'],embedded=embedded)
        value=dict(version='0',purpose='mls-new-conversation-invitation',invitation='a'*32,profile='mls-1-0001',conversation='2'*32,
            creator={k:creator[k] for k in ['principal','device','state','binding']},
            target=dict({k:self.b[k] for k in ['principal','device','state','binding']},mailbox='Bob@example.com'),
            group=base64.b64encode(bytes.fromhex(invited['group'])).decode(),epoch='1',
            keyPackageRef=base64.b64encode(bytes.fromhex(self.b['reference'])).decode(),
            notBefore=str(self.now[0]),notAfter=str(self.now[0]+100),context=base64.b64encode(self.context).decode(),
            welcome=base64.b64encode(bytes.fromhex(invited['welcome'])).decode())
        return self.wrap(value,creator),value
    def wrap(self,value,creator=None):
        creator=creator or self.a;raw=encode_event(value)
        return encode_event({'payload':base64.b64encode(raw).decode(),'signature':sign(self.binary,creator,'email-next/mls-new-conversation-invitation/v0',raw),
                             'identity':advertisement(self.binary,creator,'Alice@example.com')['identity']})
    def accept_signed(self,raw,**kwargs):
        admission=InvitationAdmission(self.identity,self.binary)
        return admission.accept_message(raw,target=self.b,mailbox='Bob@example.com',allow_creator=self.a['principal'],time=kwargs.get('time',self.time))
    def test_embedded_carrier_admission_and_replay_signature_boundary(self):
        raw,_=self.invitation();self.assertEqual(select(package(raw)),raw)
        bad=json.loads(raw);bad['signature']='0'*128
        with self.assertRaises(ValueError):self.accept_signed(encode_event(bad))
        self.assertIsNone(self.identity.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])
        result=self.accept_signed(select(package(raw)));self.assertEqual(result['status'],'admitted-unverified')
        wrapper=json.loads(raw);reserialized=json.dumps(wrapper,indent=2).encode()
        self.assertEqual(self.accept_signed(reserialized,time={'earliest':str(self.now[0]+1000),'latest':str(self.now[0]+1000)}),result)
        wrapper['signature']='0'*128
        with self.assertRaises(ValueError):self.accept_signed(encode_event(wrapper))
        self.assertEqual(self.accept_signed(raw),result)
    def test_missing_tree_and_signed_target_context_tampering_do_not_consume(self):
        raw,_=self.invitation(False)
        with self.assertRaises(ValueError):self.accept_signed(raw)
        raw,value=self.invitation(True)
        for field in ['group','welcome','context']:
            changed=copy.deepcopy(value);changed[field]=base64.b64encode(b'wrong').decode()
            with self.assertRaises(ValueError):self.accept_signed(self.wrap(changed))
        changed=copy.deepcopy(value);changed['target']['device']='end0:'+'9'*64
        with self.assertRaises(ValueError):self.accept_signed(self.wrap(changed))
        self.assertIsNone(self.identity.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])
        self.accept_signed(raw)
    def test_validated_groupinfo_signer_differs_from_signed_creator(self):
        # A third accepted signer wraps Alice's cryptographically valid Welcome.
        from provider_mls import make_device
        other=make_device(self.binary,5,6)
        self.identity.observe(other['record'],first_contact_policy='allow-unverified')
        raw,value=self.invitation(True,other)
        context=json.loads(base64.b64decode(value['context']));context['administrators']=[other['principal']]
        value['context']=base64.b64encode(encode_event(context)).decode();raw=self.wrap(value,other)
        admission=InvitationAdmission(self.identity,self.binary)
        with self.assertRaisesRegex(ValueError,'Wrong Welcome signer'):
            admission.accept_message(raw,target=self.b,mailbox='Bob@example.com',allow_creator=other['principal'],time=self.time)
        self.assertIsNone(self.identity.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])
    def test_strict_schema_and_direct_mime_scope(self):
        raw,value=self.invitation()
        changed=dict(value,ratchetTree='AAAA')
        with self.assertRaises(ValueError):parse(self.wrap(changed))
        wrapper=json.loads(raw);wrapper['payload']+='\n'
        with self.assertRaises(ValueError):parse(encode_event(wrapper))
        wire=package(raw);message=BytesParser(policy=policy.default).parsebytes(wire)
        message.attach(copy.deepcopy(list(message.iter_parts())[1]))
        with self.assertRaises(ValueError):select(message.as_bytes())
        from email.message import EmailMessage
        forwarded=EmailMessage();forwarded.set_content('Forward');forwarded.add_attachment(BytesParser(policy=policy.default).parsebytes(wire))
        with self.assertRaises(ValueError):select(forwarded.as_bytes())
        message=BytesParser(policy=policy.default).parsebytes(wire);part=list(message.iter_parts())[1];part._headers.append(('Content-Type','text/plain'))
        with self.assertRaises(ValueError):select(message.as_bytes())

class InvitationMimeTests(unittest.TestCase):
    def wire(self,root='',notice_headers='Content-Transfer-Encoding: 7bit\r\n',body=b'Invitation notice'):
        return (b'MIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary="b"'+root.encode()+
                b'\r\n\r\n--b\r\nContent-Type: text/plain; charset=utf-8\r\n'+notice_headers.encode()+
                b'\r\n'+body+b'\r\n--b\r\nContent-Type: application/vnd.email-next.mls-invitation+json\r\n'
                b'Content-Disposition: attachment\r\nContent-Transfer-Encoding: base64\r\n\r\ne30=\r\n--b--\r\n')
    def test_header_defects_and_ambiguous_singletons(self):
        cases=[self.wire(root='; boundary="other"'),self.wire(root='; broken'),
               self.wire(root='\r\nContent-Transfer-Encoding: 7bit\r\nContent-Transfer-Encoding: 8bit'),
               self.wire(notice_headers='Content-Transfer-Encoding: 7bit\r\nContent-Transfer-Encoding: base64\r\n'),
               self.wire(notice_headers='Content-Disposition: inline\r\nContent-Disposition: attachment\r\n'),
               self.wire(notice_headers='Content-Disposition: inline; filename=a; filename=b\r\n'),
               self.wire().replace(b'charset=utf-8',b'charset=utf-8; charset=ascii')]
        for wire in cases:
            with self.subTest(wire=wire),self.assertRaises(ValueError):select(wire)
    def test_notice_transfer_decoding_is_strict_and_not_authority(self):
        cases=[('7bit',b'\xff'),('8bit',b'\xff'),('base64',b'/w=='),('base64',b'a==='),
               ('quoted-printable',b'bad=QZ'),('quoted-printable',b'bad=\ncontinuation'),('unknown',b'text')]
        for encoding,body in cases:
            with self.subTest(encoding=encoding,body=body),self.assertRaises(ValueError):
                select(self.wire(notice_headers='Content-Transfer-Encoding: '+encoding+'\r\n',body=body))
        for encoding,body in [('7bit',b'plain'),('8bit','café'.encode()),('base64',b'Y2Fmw6k='),('quoted-printable',b'caf=C3=A9')]:
            self.assertEqual(select(self.wire(notice_headers='Content-Transfer-Encoding: '+encoding+'\r\n',body=body)),b'{}')

# Avoid rerunning the inherited integration suite; it remains a separate check.
for name in list(vars(integration.ProviderMlsTests)):
    if name.startswith('test_'):setattr(InvitationTests,name,None)

if __name__=='__main__':unittest.main()
