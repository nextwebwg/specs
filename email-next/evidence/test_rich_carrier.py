import hashlib,json,unittest
from email.parser import BytesParser
from email import policy
from event_encoding import encode_event
from rich_carrier import package_rich,inspect_rich
LIMITS=dict(max_wire_bytes=65536,max_parts=16,max_decoded_bytes=32768)
class RichCarrier(unittest.TestCase):
    def setUp(self):
        self.image='b'*32;self.file='c'*32;self.event='a'*32;self.resources={self.image:b'png-placeholder',self.file:b'From: opaque\r\n\r\nfile'}
        self.op=dict(kind='rich-message',text='A diagram and source',html='<p>A diagram</p><img alt="Diagram" src="cid:'+self.image+'.'+self.event+'@resources.email-next.invalid">',presentation='html-css-v0',replyTo=[],manifest=[dict(id=k,size=str(len(v)),sha256=hashlib.sha256(v).hexdigest()) for k,v in self.resources.items()],embedded=[dict(resource=self.image,mediaType='image/png')],attachments=[dict(resource=self.file,name='source.eml',mediaType='message/rfc822',description='Source')])
        self.raw=encode_event(dict(version='1',purpose='contribution',event=self.event,conversation='d'*32,principal='enp0:'+'e'*64,audience=['enp0:'+'e'*64],disclosures=[],operation=self.op))
        self.wire=package_rich(self.raw,self.resources,**LIMITS)
    def test_exact_event_and_separate_resource_roles(self):
        selected=inspect_rich(self.wire,**LIMITS)
        self.assertEqual(selected['event']['octets'],self.raw)
        self.assertEqual(selected['embedded'][0]['bytes'],self.resources[self.image]);self.assertEqual(selected['attachments'][0]['bytes'],self.resources[self.file])
        self.assertEqual(selected['attachmentProjections'][0]['mediaType'],'application/octet-stream')
    def test_no_routing_hidden_history_or_implicit_related_root(self):
        for change in [lambda r:r.__setitem__('From','evil@example.invalid'),lambda r:setattr(r,'epilogue','hidden history'),lambda r:r.get_payload()[0].get_payload()[1].set_param('start','<other>')]:
            root=BytesParser(policy=policy.SMTP).parsebytes(self.wire);change(root)
            with self.assertRaises(ValueError):inspect_rich(root.as_bytes(),**LIMITS)
    def test_wrong_role_projection_and_resource_integrity(self):
        root=BytesParser(policy=policy.SMTP).parsebytes(self.wire)
        root.get_payload()[0].get_payload()[1].get_payload()[1].replace_header('Content-Disposition','attachment')
        with self.assertRaises(ValueError):inspect_rich(root.as_bytes(),**LIMITS)
        with self.assertRaises(ValueError):package_rich(self.raw,dict(self.resources,**{self.image:b'wrong'}),**LIMITS)
    def test_exact_decoded_total_and_plain_body_without_resources(self):
        selected=inspect_rich(self.wire,**LIMITS);size=sum(len(selected[k]) for k in ('plain','html'))+len(self.raw)+sum(map(len,self.resources.values()))
        inspect_rich(self.wire,**dict(LIMITS,max_decoded_bytes=size))
        with self.assertRaises(ValueError):inspect_rich(self.wire,**dict(LIMITS,max_decoded_bytes=size-1))
        value=json.loads(self.raw);value['operation'].update(manifest=[],embedded=[],attachments=[],html='<p>Only text</p>')
        raw=encode_event(value);self.assertEqual(inspect_rich(package_rich(raw,{},**LIMITS),**LIMITS)['embedded'],[])
