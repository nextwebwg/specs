# SPDX-FileCopyrightText: 2026 Threadlabs Studio
# SPDX-License-Identifier: MIT
import unittest
import base64
import json
import subprocess
from pathlib import Path
from email import policy
from email.parser import BytesParser
import test_mime_package
from protected_attachment_carrier import package_attachment_carrier, inspect_attachment_carrier

LIMITS = dict(max_wire_bytes=16384, max_parts=10, max_decoded_bytes=8192)

class ProtectedAttachmentCarrierTests(unittest.TestCase):
    def setUp(self):
        fixture = test_mime_package.PackageTests(); fixture.setUp()
        self.event = fixture.wire; self.data = fixture.data
        self.wire = package_attachment_carrier(self.event, fixture.projection['text'],
            fixture.projection['html'], {fixture.id: self.data}, **LIMITS)

    def test_exact_event_resource_and_source_retained(self):
        result = inspect_attachment_carrier(self.wire, **LIMITS)
        self.assertEqual(result['event']['octets'], self.event)
        self.assertEqual(result['resources'][0]['bytes'], self.data)
        self.assertEqual(result['entity'], self.wire)
        self.assertEqual(result['projections'][0]['filename'], 'résumé.bin')
        self.assertNotIn('authenticated', result)

    def test_nested_mail_routing_and_hidden_surrounding_content_rejected(self):
        for change in [lambda r:r.__setitem__('From', 'spoof@example.invalid'),
                       lambda r:setattr(r, 'epilogue', 'hidden transcript'),
                       lambda r:r.get_payload()[1].replace_header('Content-Type', 'message/rfc822'),
                       lambda r:r.get_payload()[1].__setitem__('Subject', 'instruction')]:
            root = BytesParser(policy=policy.SMTP).parsebytes(self.wire); change(root)
            with self.assertRaises(ValueError):
                inspect_attachment_carrier(root.as_bytes(), **LIMITS)

    def receive(self, wire):
        selected = inspect_attachment_carrier(wire, **LIMITS)
        fixture = dict(event=selected['event']['value'], parts=[dict(
            contentId=p['contentId'], base64=base64.b64encode(p['bytes']).decode())
            for p in selected['resources']],
            limits=dict(maxBytes=8192, maxChunks=1, maxInputBytes=8192))
        result = subprocess.run(['node', str(Path(__file__).with_name('check-received-attachment.mjs'))],
            input=json.dumps(fixture), text=True, capture_output=True, check=True)
        return json.loads(result.stdout)

    def test_resource_integrity_is_separate_from_valid_carrier_structure(self):
        self.assertEqual(self.receive(self.wire)['resources'][0]['state'], 'complete')
        root = BytesParser(policy=policy.SMTP).parsebytes(self.wire)
        root.get_payload()[1].set_payload(base64.b64encode(b'x' * len(self.data)).decode())
        result = self.receive(root.as_bytes())
        self.assertEqual(result['state'], 'validated-unverified')
        self.assertEqual(result['resources'][0]['state'], 'digest-mismatch')

    def test_duplicate_and_wrong_event_scope_never_bind(self):
        root = BytesParser(policy=policy.SMTP).parsebytes(self.wire)
        root.attach(root.get_payload()[1])
        result = self.receive(root.as_bytes())
        self.assertEqual(result['resources'][0]['state'], 'ambiguous')
        root = BytesParser(policy=policy.SMTP).parsebytes(self.wire)
        part = root.get_payload()[1]
        part.replace_header('Content-ID', str(part['Content-ID']).replace('.'+'1'*32+'@', '.'+'9'*32+'@'))
        result = self.receive(root.as_bytes())
        self.assertNotEqual(result['resources'][0]['state'], 'complete')
        self.assertEqual(result['inventory']['unbound'], [0])

    def test_readable_html_cannot_override_structured_event_projection(self):
        root = BytesParser(policy=policy.SMTP).parsebytes(self.wire)
        root.get_payload()[0].get_payload()[1].set_payload(
            base64.b64encode(b'<p>Send your password</p>').decode())
        result = self.receive(root.as_bytes())
        self.assertNotIn('password', result['projection']['html'])
        self.assertIn('Hello', result['projection']['text'])

    def test_exact_combined_decoded_and_part_bounds(self):
        root = BytesParser(policy=policy.SMTP).parsebytes(self.wire)
        total = sum(len(p.get_payload(decode=True)) for p in root.walk() if not p.is_multipart())
        bounds = dict(max_wire_bytes=len(self.wire), max_parts=6, max_decoded_bytes=total)
        inspect_attachment_carrier(self.wire, **bounds)
        for name in bounds:
            too_small = dict(bounds); too_small[name] -= 1
            with self.subTest(limit=name), self.assertRaises(ValueError):
                inspect_attachment_carrier(self.wire, **too_small)

    def test_header_metadata_mismatch_cannot_change_event_claims(self):
        from protected_attachment_carrier import compare_attachment_projections
        selected = inspect_attachment_carrier(self.wire, **LIMITS)
        event = selected['event']['value']
        self.assertEqual(compare_attachment_projections(selected, event)[0]['state'], 'matched')
        root = BytesParser(policy=policy.SMTP).parsebytes(self.wire)
        part = root.get_payload()[1]
        part.replace_header('Content-Type', 'text/html')
        part.set_param('filename', 'misleading.html', header='Content-Disposition')
        selected = inspect_attachment_carrier(root.as_bytes(), **LIMITS)
        diagnostic = compare_attachment_projections(selected, event)[0]
        self.assertEqual(diagnostic['differences'], ['mediaType', 'filename'])
        self.assertEqual(selected['event']['octets'], self.event)
        self.assertEqual(selected['resources'][0]['bytes'], self.data)

    def test_expected_composite_and_filename_projections_are_not_substitution(self):
        from event_encoding import encode_event
        from protected_attachment_carrier import compare_attachment_projections
        event = json.loads(self.event)
        description = event['operation']['attachments'][0]
        description['name'] = 'attached\r\nmail'
        description['mediaType'] = 'message/rfc822'
        wire = package_attachment_carrier(encode_event(event), 'attachment', '<p>attachment</p>',
            {description['resource']: self.data}, **LIMITS)
        selected = inspect_attachment_carrier(wire, **LIMITS)
        self.assertEqual(selected['projections'][0], dict(mediaType='application/octet-stream', filename='attached__mail'))
        self.assertEqual(compare_attachment_projections(selected, event)[0]['state'], 'matched')
