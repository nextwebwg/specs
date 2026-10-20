import unittest
from pathlib import Path
from email import policy
from email.parser import BytesParser
from mime_package import inspect_contribution_package

class EditExampleTests(unittest.TestCase):
    def test_paired_examples_bind_exact_root_and_preserve_complete_replacement(self):
        folder=Path(__file__).resolve().parent.parent/'examples'
        messages=[];selected=[]
        for name in ['meeting-original','meeting-correction']:
            wire=(folder/(name+'.eml')).read_bytes()
            messages.append(BytesParser(policy=policy.default).parsebytes(wire))
            selected.append(inspect_contribution_package(wire,max_wire_bytes=16384,max_parts=4,max_decoded_bytes=8192))
        original,correction=[item['event']['value'] for item in selected]
        self.assertEqual(correction['operation']['root'],{key:original[key] for key in ['principal','conversation','event']})
        self.assertEqual(correction['operation']['predecessors'],[correction['operation']['root']])
        self.assertEqual(str(messages[1]['In-Reply-To']),str(messages[0]['Message-ID']))
        self.assertNotEqual(original['event'],correction['event'])
        self.assertIn(b"Let's meet at 4.",selected[1]['plain'])
        self.assertNotIn(b"Let's meet at 3.",selected[1]['plain'])
        self.assertIn(b'Correction to an earlier message',selected[1]['plain'])

    def test_attaching_correction_does_not_bundle_original_history(self):
        # Model preservation of the entire delivered message, not a claim about
        # any particular legacy client's Forward button.
        from email.message import EmailMessage
        folder=Path(__file__).resolve().parent.parent/'examples'
        original=inspect_contribution_package((folder/'meeting-original.eml').read_bytes(),
            max_wire_bytes=16384,max_parts=4,max_decoded_bytes=8192)
        secret=original['event']['value']['operation']['text'].encode('utf-8')
        correction=BytesParser(policy=policy.default).parsebytes((folder/'meeting-correction.eml').read_bytes())
        forward=EmailMessage(policy=policy.SMTP)
        forward.set_content('Forwarding the correction.')
        forward.add_attachment(correction)
        received=BytesParser(policy=policy.default).parsebytes(forward.as_bytes())
        self.assertTrue(any(part.get_content_type()=='message/rfc822' for part in received.walk()))
        leaves=[part.get_payload(decode=True) for part in received.walk() if not part.is_multipart()]
        self.assertTrue(any(b"Let's meet at 4." in body for body in leaves if body))
        for body in leaves:
            if body is not None:
                self.assertNotIn(secret,body)
