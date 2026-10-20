import hashlib
import base64
import json
from pathlib import Path
import subprocess
import unittest
from email import policy
from email.parser import BytesParser
from email.message import EmailMessage
from event_encoding import encode_event
from pop_response import decode_multiline
from mime_package import package_attachment, inspect_attachment_package, EVENT_MEDIA_TYPE
from mime_resources import parse_resources

class PackageTests(unittest.TestCase):
    def setUp(self):
        self.data=b'\x00\xff\r\nattachment\x80'
        self.id='3'*32
        self.event={'version':'0','purpose':'contribution','event':'1'*32,'conversation':'2'*32,
                    'principal':'enp0:'+'a'*64,'audience':['enp0:'+'a'*64,'enp0:'+'b'*64],
                    'operation':{'kind':'attachment-message','text':'Hello 世界','replyTo':[],
                    'manifest':[{'id':self.id,'size':str(len(self.data)),'sha256':hashlib.sha256(self.data).hexdigest()}],
                    'attachments':[{'resource':self.id,'name':'résumé.bin','description':'Binary example','mediaType':'application/octet-stream'}]}}
        self.wire=encode_event(self.event)
        result=subprocess.run(['node',str(Path(__file__).with_name('project-event.mjs'))],
                              input=self.wire,capture_output=True,check=True)
        self.projection=json.loads(result.stdout)
        self.assertEqual(self.projection['state'],'projected')
    def package(self,resources=None):
        return package_attachment(self.wire,self.projection['text'],self.projection['html'],
                                  {self.id:self.data} if resources is None else resources)
    def test_layout_and_exact_event_and_resource_roundtrip(self):
        package=self.package()
        root=BytesParser(policy=policy.default).parsebytes(package)
        self.assertFalse(root.defects)
        self.assertEqual(root.get_content_type(),'multipart/mixed')
        alternatives,attachment=list(root.iter_parts())
        plain,html,structured=list(alternatives.iter_parts())
        self.assertEqual([p.get_content_type() for p in [plain,html,structured]],['text/plain','text/html',EVENT_MEDIA_TYPE])
        self.assertEqual(structured.get_payload(decode=True),self.wire)
        self.assertEqual(attachment.get_payload(decode=True),self.data)
        self.assertEqual(attachment.get_filename(),'résumé.bin')
        self.assertIn('Hello 世界',plain.get_content())
        # Feed only the selected sibling resource scope into the strict adapter.
        container=EmailMessage(policy=policy.SMTP);container.make_mixed();container.attach(attachment)
        parts=parse_resources(container.as_bytes(),max_wire_bytes=8192,max_parts=1,max_decoded_bytes=1024)
        self.assertEqual(parts[0]['bytes'],self.data)
    def inspect(self,wire):
        return inspect_attachment_package(wire,max_wire_bytes=16384,max_parts=10,max_decoded_bytes=8192)
    def test_incoming_selection_retains_exact_event_bytes(self):
        result=self.inspect(self.package())
        self.assertEqual(result['event']['octets'],self.wire)
        self.assertEqual(result['resources'][0]['bytes'],self.data)
    def test_incoming_duplicate_alternatives_and_nested_substitution_fail(self):
        root=BytesParser(policy=policy.default).parsebytes(self.package())
        alternative=list(root.iter_parts())[0]
        alternative.attach(list(alternative.iter_parts())[-1])
        with self.assertRaises(ValueError):self.inspect(root.as_bytes())
        root=BytesParser(policy=policy.default).parsebytes(self.package())
        resource=list(root.iter_parts())[1]
        resource.replace_header('Content-Type','multipart/mixed; boundary=inner')
        with self.assertRaises(ValueError):self.inspect(root.as_bytes())
    def receive(self,wire):
        selected=self.inspect(wire)
        fixture={'event':selected['event']['value'],
                 'parts':[{'contentId':p['contentId'],'base64':base64.b64encode(p['bytes']).decode()} for p in selected['resources']],
                 'limits':{'maxBytes':1024,'maxChunks':1,'maxInputBytes':1024}}
        result=subprocess.run(['node',str(Path(__file__).with_name('check-received-attachment.mjs'))],
                              input=json.dumps(fixture),text=True,capture_output=True,check=True)
        return json.loads(result.stdout)
    def test_incoming_pipeline_checks_schema_and_resource_integrity(self):
        result=self.receive(self.package())
        self.assertEqual(result['state'],'validated-unverified')
        self.assertEqual(result['resources'],[{'id':self.id,'state':'complete'}])
        root=BytesParser(policy=policy.default).parsebytes(self.package())
        resource=list(root.iter_parts())[1]
        changed=bytearray(self.data);changed[0]^=1
        resource.set_payload(base64.b64encode(changed).decode())
        result=self.receive(root.as_bytes())
        self.assertEqual(result['resources'][0]['state'],'digest-mismatch')
        root=BytesParser(policy=policy.default).parsebytes(self.package())
        structured=list(list(root.iter_parts())[0].iter_parts())[-1]
        malformed=self.wire.replace(b'"size":"'+str(len(self.data)).encode()+b'"',b'"size":"00"')
        structured.set_payload(base64.b64encode(malformed).decode())
        self.assertEqual(self.receive(root.as_bytes())['state'],'invalid-schema')
    def test_neighbor_html_does_not_supply_upgraded_display(self):
        root=BytesParser(policy=policy.default).parsebytes(self.package())
        html=list(list(root.iter_parts())[0].iter_parts())[1]
        html.set_payload(base64.b64encode(b'<script>attacker()</script>').decode())
        result=self.receive(root.as_bytes())
        self.assertNotIn('attacker()',result['projection']['html'])
        self.assertIn('Hello 世界',result['projection']['text'])

    def test_incoming_duplicate_content_type_fails(self):
        wire=self.package().replace(b'Content-Type: '+EVENT_MEDIA_TYPE.encode(),b'Content-Type: text/plain\r\nContent-Type: '+EVENT_MEDIA_TYPE.encode())
        with self.assertRaises(ValueError):self.inspect(wire)

    def test_generic_json_and_other_suffix_types_cannot_activate_event(self):
        for media_type in ['application/json','application/example+json','application/octet-stream']:
            wire=self.package().replace(EVENT_MEDIA_TYPE.encode(),media_type.encode())
            with self.assertRaises(ValueError):self.inspect(wire)

    def test_event_parameters_hold_processing_instead_of_changing_semantics(self):
        for parameters in ['; charset=utf-8','; charset=utf-16','; version=0','; future=yes',
                           '; version=0; version=1','; charset*=utf-8\'\'utf-8']:
            root=BytesParser(policy=policy.default).parsebytes(self.package())
            structured=list(list(root.iter_parts())[0].iter_parts())[-1]
            structured.replace_header('Content-Type',EVENT_MEDIA_TYPE+parameters)
            with self.assertRaises(ValueError):self.inspect(root.as_bytes())

    def test_media_type_case_does_not_change_authenticated_event_bytes(self):
        wire=self.package().replace(EVENT_MEDIA_TYPE.encode(),EVENT_MEDIA_TYPE.upper().encode())
        self.assertEqual(self.inspect(wire)['event']['octets'],self.wire)

    def test_control_characters_use_header_projection_without_changing_event(self):
        for name,projected in [('a\r\nb\x00c\x7f','a__b_c_'),('','attachment')]:
            self.event['operation']['attachments'][0]['name']=name
            self.wire=encode_event(self.event)
            root=BytesParser(policy=policy.default).parsebytes(self.package())
            self.assertEqual(list(root.iter_parts())[1].get_filename(),projected)
            self.assertEqual(self.inspect(root.as_bytes())['event']['value']['operation']['attachments'][0]['name'],name)

    def test_composite_attachment_types_remain_opaque_resources(self):
        self.data=(b'From: nested@example.test\r\nContent-Type: multipart/mixed; boundary=inner\r\n\r\n'
                   b'--inner\r\nContent-Type: text/plain\r\n\r\nNested message\r\n--inner--\r\n')
        item=self.event['operation']['manifest'][0]
        item['size']=str(len(self.data));item['sha256']=hashlib.sha256(self.data).hexdigest()
        for media_type in ['message/rfc822','message/global','multipart/mixed']:
            self.event['operation']['attachments'][0]['mediaType']=media_type
            self.wire=encode_event(self.event)
            wire=self.package()
            root=BytesParser(policy=policy.default).parsebytes(wire)
            resource=list(root.iter_parts())[1]
            self.assertEqual(resource.get_content_type(),'application/octet-stream')
            self.assertFalse(resource.is_multipart())
            selected=self.inspect(wire)
            self.assertEqual(selected['resources'][0]['bytes'],self.data)
            self.assertEqual(selected['event']['value']['operation']['attachments'][0]['mediaType'],media_type)
            self.assertEqual(self.receive(wire)['resources'][0]['state'],'complete')

    def test_unlisted_and_duplicate_parts_never_gain_attachment_authority(self):
        root=BytesParser(policy=policy.default).parsebytes(self.package())
        extra=EmailMessage(policy=policy.SMTP)
        extra.set_content(b'extra',maintype='application',subtype='octet-stream',cte='base64')
        extra['Content-ID']='<'+('4'*32)+'.'+('1'*32)+'@resources.email-next.invalid>'
        root.attach(extra)
        result=self.receive(root.as_bytes())
        self.assertEqual(result['inventory']['unbound'],[1])
        self.assertEqual(result['inventory']['state'],'incomplete-inventory')
        self.assertEqual(len(result['resources']),1)
        root=BytesParser(policy=policy.default).parsebytes(self.package())
        root.attach(list(root.iter_parts())[1])
        result=self.receive(root.as_bytes())
        self.assertEqual(result['inventory']['ambiguous'],[self.id])
        self.assertEqual(result['resources'][0]['state'],'ambiguous')

    def test_pop_retrieval_preserves_packaged_event_and_resources(self):
        message=self.package()
        self.assertTrue(message.endswith(b'\r\n'))
        stuffed=b'\r\n'.join(b'.'+line if line.startswith(b'.') else line for line in message.split(b'\r\n'))
        response=b'+OK message follows\r\n'+stuffed+b'.\r\n'
        decoded=decode_multiline(response,max_wire_bytes=32768,max_message_bytes=16384)
        self.assertEqual(decoded['message'],message)
        received=self.receive(decoded['message'])
        self.assertEqual(received['resources'][0]['state'],'complete')
        self.assertEqual(self.inspect(decoded['message'])['event']['octets'],self.wire)

    def test_missing_extra_and_altered_resources_fail_before_packaging(self):
        for resources in [{},{self.id:self.data,'4'*32:b''},{self.id:b'changed'}]:
            with self.assertRaises(ValueError):self.package(resources)

if __name__=='__main__':unittest.main()
