# SPDX-FileCopyrightText: 2026 Threadlabs Studio
# SPDX-License-Identifier: MIT
import unittest
from email import policy
from email.parser import BytesParser
from event_encoding import encode_event
from protected_carrier import package_carrier, inspect_carrier

LIMITS = dict(max_wire_bytes=65536, max_parts=8, max_decoded_bytes=32768)

class ProtectedCarrierTests(unittest.TestCase):
    def setUp(self):
        self.event = encode_event(dict(version='0', purpose='contribution',
            principal='enp0:'+'a'*64, conversation='1'*32, event='2'*32,
            audience=['enp0:'+'a'*64], operation=dict(kind='message', text='Hello', replyTo=[])))
        self.wire = package_carrier(self.event, 'Hello', '<p>Hello</p>', **LIMITS)

    def test_exact_event_and_entity_preserved_without_authentication_claim(self):
        result = inspect_carrier(self.wire, **LIMITS)
        self.assertEqual(result['event']['octets'], self.event)
        self.assertEqual(result['entity'], self.wire)
        self.assertNotIn('authenticated', result)

    def test_routing_headers_preamble_epilogue_and_charset_rejected(self):
        changes = [lambda r:r.__setitem__('From', 'spoof@example.invalid'),
                   lambda r:setattr(r, 'preamble', 'hidden history'),
                   lambda r:setattr(r, 'epilogue', 'hidden history'),
                   lambda r:r.get_payload()[0].set_param('charset', 'iso-8859-1'),
                   lambda r:r._headers.append(('MIME-Version', '1.0')),
                   lambda r:r.get_payload()[2].__setitem__('Subject', 'hidden')]
        for change in changes:
            root = BytesParser(policy=policy.SMTP).parsebytes(self.wire)
            change(root)
            with self.subTest(change=change), self.assertRaises(ValueError):
                inspect_carrier(root.as_bytes(), **LIMITS)

    def test_raw_event_and_noncanonical_lines_do_not_select_carrier(self):
        for wire in (self.event, self.wire.replace(b'\r\n', b'\n')):
            with self.assertRaises(ValueError):
                inspect_carrier(wire, **LIMITS)

    def test_independent_limits_are_enforced(self):
        for name in LIMITS:
            limits = dict(LIMITS); limits[name] = 1
            with self.subTest(name=name), self.assertRaises(ValueError):
                inspect_carrier(self.wire, **limits)

    def reaction(self):
        event=__import__('json').loads(self.event)
        event['operation']={'kind':'reaction','target':{'principal':event['principal'],'conversation':event['conversation'],'event':'3'*32},'emoji':'👍'}
        return encode_event(event)

    def test_reaction_pair_exact_scope_and_mismatch_diagnostic(self):
        raw=self.reaction();wire=package_carrier(raw,'Reaction','<p>Reaction</p>',target_message_id='<target@example.invalid>',**LIMITS)
        result=inspect_carrier(wire,**LIMITS)
        self.assertEqual(result['event']['octets'],raw);self.assertEqual(result['pairing'],'matched')
        self.assertEqual(result['reactionPart'],'👍\r\n'.encode())
        root=BytesParser(policy=policy.SMTP).parsebytes(wire)
        import base64
        root.get_payload()[0].set_payload(base64.b64encode('👎\r\n'.encode()).decode())
        result=inspect_carrier(root.as_bytes(),**LIMITS)
        self.assertEqual(result['pairing'],'mismatch');self.assertEqual(result['event']['octets'],raw)
        root.get_payload().reverse()
        with self.assertRaises(ValueError):inspect_carrier(root.as_bytes(),**LIMITS)

    def test_decoded_wire_part_and_depth_exact_boundaries(self):
        result=inspect_carrier(self.wire,**LIMITS)
        decoded=len(result['plain'])+len(result['html'])+len(self.event)
        exact=dict(max_wire_bytes=len(self.wire),max_parts=4,max_decoded_bytes=decoded,max_depth=2)
        inspect_carrier(self.wire,**exact)
        for key in exact:
            limits=dict(exact);limits[key]-=1
            with self.subTest(key=key),self.assertRaises(ValueError):inspect_carrier(self.wire,**limits)
        wire=package_carrier(self.reaction(),'Reaction','<p>Reaction</p>',target_message_id='<a@b>',**LIMITS)
        result=inspect_carrier(wire,**LIMITS)
        exact=dict(max_wire_bytes=len(wire),max_parts=6,max_depth=3,max_decoded_bytes=sum(len(result[k]) for k in ('plain','html','reactionPart'))+len(result['event']['octets']))
        inspect_carrier(wire,**exact)
        for key in exact:
            limits=dict(exact);limits[key]-=1
            with self.subTest(key=key),self.assertRaises(ValueError):inspect_carrier(wire,**limits)

    def test_invalid_utf8_in_each_readable_leaf(self):
        import base64
        for index in (0,1):
            root=BytesParser(policy=policy.SMTP).parsebytes(self.wire);root.get_payload()[index].set_payload(base64.b64encode(b'\xff').decode())
            with self.subTest(index=index),self.assertRaises(ValueError):inspect_carrier(root.as_bytes(),**LIMITS)
        wire=package_carrier(self.reaction(),'Reaction','<p>Reaction</p>',target_message_id='<a@b>',**LIMITS)
        root=BytesParser(policy=policy.SMTP).parsebytes(wire);root.get_payload()[0].set_payload(base64.b64encode(b'\xff\r\n').decode())
        with self.assertRaises(ValueError):inspect_carrier(root.as_bytes(),**LIMITS)

    def test_nested_forwarded_resources_and_duplicate_parameters_rejected(self):
        from email.message import EmailMessage
        for subtype in ('mixed','related','alternative'):
            root=BytesParser(policy=policy.SMTP).parsebytes(self.wire)
            wrapper=EmailMessage(policy=policy.SMTP);wrapper.set_type('multipart/'+subtype);wrapper.attach(root.get_payload()[0]);root.set_payload([wrapper]+root.get_payload()[1:])
            with self.subTest(subtype=subtype),self.assertRaises(ValueError):inspect_carrier(root.as_bytes(),**LIMITS)
        root=BytesParser(policy=policy.SMTP).parsebytes(self.wire)
        root.add_attachment(b'From: inner@example.invalid\r\n\r\nbody',maintype='application',subtype='octet-stream')
        with self.assertRaises(ValueError):inspect_carrier(root.as_bytes(),**LIMITS)
        duplicate=self.wire.replace(b'Content-Type: multipart/alternative;',b'Content-Type: multipart/alternative; boundary="second";',1)
        with self.assertRaises(ValueError):inspect_carrier(duplicate,**LIMITS)

    def test_invalid_limits_are_not_coerced(self):
        for value in (True,-1,1.5,None):
            with self.subTest(value=value),self.assertRaises(ValueError):inspect_carrier(self.wire,**dict(LIMITS,max_parts=value))
