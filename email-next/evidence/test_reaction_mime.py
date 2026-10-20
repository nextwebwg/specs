import base64
from email import policy
from email.parser import BytesParser
from email.message import EmailMessage
import json
from pathlib import Path
import subprocess
import unittest
from event_encoding import encode_event
from reaction_mime import package_reaction, inspect_reaction_package

HERE=Path(__file__).parent
LIMITS=dict(max_wire_bytes=65536,max_parts=8,max_decoded_bytes=32768)
class ReactionMimeTests(unittest.TestCase):
    def setUp(self):
        p='enp0:'+'a'*64
        self.ref=lambda i:dict(principal=p,conversation='1'*32,event=str(i)*32)
        self.wrap=lambda i,op:dict(version='0',purpose='contribution',**self.ref(i),audience=[p],operation=op)
        self.root=self.wrap(2,dict(kind='message',text='PRIVATE TARGET TEXT',replyTo=[]))
        self.reaction=self.wrap(3,dict(kind='reaction',target=self.ref(2),emoji='👍🏽'))
        self.withdraw=self.wrap(4,dict(kind='reaction-withdraw',target=self.ref(2),reactions=[self.ref(3)]))
    def wire(self,event=None,target='<target@example.invalid>'):
        event=event or self.reaction
        script="""import {projectReadable} from './readable-projection.mjs';
import {isPrincipalId} from './principal-identifiers.mjs';
let input='';for await(const c of process.stdin)input+=c;
const {event,records}=JSON.parse(input);
const key=r=>JSON.stringify([r.principal,r.conversation,r.event]);
const index=new Map(records.map(e=>[key(e),e]));
process.stdout.write(JSON.stringify(projectReadable(event,r=>({state:'valid',event:index.get(key(r))}),isPrincipalId)));"""
        out=json.loads(subprocess.run(['node','--input-type=module','-e',script],cwd=HERE,
            input=json.dumps(dict(event=event,records=[self.root,self.reaction])),text=True,capture_output=True,check=True).stdout)
        self.assertEqual(out['state'],'projected')
        return package_reaction(encode_event(event),out['text'],out['html'],target_message_id=target)
    def inspect(self,wire):return inspect_reaction_package(wire,**LIMITS)
    def mutate(self,wire,fn):
        root=BytesParser(policy=policy.SMTP).parsebytes(wire);fn(root);return root.as_bytes()
    def test_real_projection_pair_exact_bytes_and_folded_transfer_encoding(self):
        wire=self.wire();result=self.inspect(wire)
        self.assertEqual(result['pairing'],'matched');self.assertEqual(result['reactionPart'],'👍🏽\r\n'.encode())
        self.assertEqual(result['event']['octets'],encode_event(self.reaction))
        self.assertNotIn(b'PRIVATE TARGET TEXT',result['plain'])
        encoded=base64.b64encode('👍🏽\r\n'.encode())
        self.assertEqual(self.inspect(wire.replace(encoded,encoded[:4]+b' \r\n '+encoded[4:]))['pairing'],'matched')
    def test_missing_mapping_and_withdrawal_use_ordinary_alternatives(self):
        for event,target in [(self.reaction,None),(self.withdraw,None),(self.withdraw,'<target@example.invalid>')]:
            wire=self.wire(event,target);out=self.inspect(wire)
            self.assertEqual(out['layout'],'ordinary-alternatives');self.assertNotIn(b'Content-Disposition: reaction',wire)
            self.assertEqual(out['event']['octets'],encode_event(event))
    def test_mismatch_retains_untrusted_event_without_claiming_pair(self):
        wire=self.wire();encoded=base64.b64encode('👍🏽\r\n'.encode())
        for bad in [b'bad\r\n','👍🏽\n'.encode()]:
            out=self.inspect(wire.replace(encoded,base64.b64encode(bad)))
            self.assertEqual(out['pairing'],'mismatch');self.assertEqual(out['event']['octets'],encode_event(self.reaction))
    def test_wrong_order_duplicates_and_nested_scope_rejected(self):
        wire=self.wire()
        mutations=[lambda r:r.set_payload(list(reversed(r.get_payload()))),
            lambda r:r.attach(r.get_payload()[0]),
            lambda r:r.get_payload()[1].attach(r.get_payload()[1].get_payload()[2]),
            lambda r:r.replace_header('In-Reply-To','<a@x> <b@x>')]
        for mutation in mutations:
            with self.assertRaises(ValueError):self.inspect(self.mutate(wire,mutation))
        outer=EmailMessage(policy=policy.SMTP);outer.set_content('forward');outer.add_attachment(BytesParser(policy=policy.SMTP).parsebytes(wire))
        with self.assertRaises(ValueError):self.inspect(outer.as_bytes())
    def test_invalid_headers_encoding_and_limits_rejected(self):
        wire=self.wire()
        for bad in [wire.replace(b'Content-Disposition: reaction',b'Content-Disposition: reaction\r\nContent-Disposition: reaction'),
                    wire.replace(b'In-Reply-To: <target@example.invalid>',b'In-Reply-To: <target@example.invalid>\r\nIn-Reply-To: <other@example.invalid>'),
                    wire.replace(base64.b64encode('👍🏽\r\n'.encode()),b'%%%')]:
            with self.assertRaises(ValueError):self.inspect(bad)
        for field in LIMITS:
            limits=dict(LIMITS);limits[field]=1
            with self.assertRaises(ValueError):inspect_reaction_package(wire,**limits)
    def test_mapping_not_inferred_or_header_injected_and_generation_does_not_claim_authentication(self):
        for target in ['target@example.invalid','<one@x> <two@x>','<x@x>\r\nBcc: secret@x']:
            with self.assertRaises(ValueError):self.wire(target=target)
        # Packaging accepts arbitrary supplied prose; this boundary is intentional.
        out=self.inspect(package_reaction(encode_event(self.reaction),'unrelated','<p>unrelated</p>',target_message_id='<target@example.invalid>'))
        self.assertEqual(out['pairing'],'matched');self.assertIn(b'unrelated',out['plain'])
        self.assertNotIn('authenticated',out)
