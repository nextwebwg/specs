"""Strict bytes -> decoded value -> JS schema integration, without cryptography."""
import json
from pathlib import Path
import subprocess
import unittest
from event_encoding import decode_event, encode_event

HERE = Path(__file__).resolve().parent

def pipeline(octets):
    decoded = decode_event(octets)
    result = subprocess.run(
        ['node', str(HERE / 'check-decoded-envelope.mjs')],
        input=json.dumps(decoded['value'], ensure_ascii=False),
        text=True, capture_output=True, check=True)
    return decoded, json.loads(result.stdout)['shapeValid']

def event(operation):
    return {'version': '0', 'purpose': 'contribution',
            'event': '1' * 32, 'conversation': '2' * 32,
            'principal': 'enp0:'+'a'*64,
            'audience': ['enp0:'+'a'*64, 'enp0:'+'b'*64], 'operation': operation}

class WireTests(unittest.TestCase):
    def test_message_and_form_bytes_reach_schema(self):
        for operation in [
            {'kind':'message', 'text':'Hello / こんにちは', 'replyTo':[]},
            {'kind':'form', 'form':'3'*32, 'title':'Question', 'fields':[], 'supersedes':[]},
        ]:
            with self.subTest(kind=operation['kind']):
                original=encode_event(event(operation))
                decoded, valid=pipeline(original)
                self.assertTrue(valid)
                self.assertEqual(decoded['octets'],original)
                self.assertEqual(decoded['value']['operation'],operation)

    def test_attachment_bytes_validate_and_reject_duplicate_manifest_fields(self):
        operation={'kind':'attachment-message','text':'A file','replyTo':[],
                   'manifest':[{'id':'3'*32,'size':'0','sha256':'a'*64}],
                   'attachments':[{'resource':'3'*32,'name':'example.txt',
                                   'description':'Example','mediaType':'text/plain'}]}
        original=encode_event(event(operation))
        decoded,valid=pipeline(original)
        self.assertTrue(valid)
        self.assertEqual(decoded['octets'],original)
        with self.assertRaises(ValueError):
            pipeline(original.replace(b'"size":"0"',b'"size":"0","size":"1"'))
        _,valid=pipeline(original.replace(b'"size":"0"',b'"size":"00"'))
        self.assertFalse(valid)

    def test_edit_bytes_preserve_target_and_literal_replacement(self):
        reference={'principal':'enp0:'+'a'*64,'conversation':'2'*32,'event':'3'*32}
        operation={'kind':'edit','root':reference,'predecessors':[reference],
                   'text':'Meet at 4 / 明日 <b>literal</b>'}
        original=encode_event(event(operation))
        decoded,valid=pipeline(original)
        self.assertTrue(valid)
        self.assertEqual(decoded['octets'],original)
        self.assertEqual(decoded['value']['operation'],operation)

    def test_duplicate_edit_target_members_fail_before_schema(self):
        reference={'principal':'enp0:'+'a'*64,'conversation':'2'*32,'event':'3'*32}
        original=encode_event(event({'kind':'edit','root':reference,
                                    'predecessors':[reference],'text':'Correction'}))
        replacements=[
            (b'"text":"Correction"',b'"text":"Correction","\\u0074ext":"Different"'),
            (b'"event":"'+b'3'*32+b'"',b'"event":"'+b'3'*32+b'","\\u0065vent":"'+b'4'*32+b'"'),
        ]
        for before,after in replacements:
            with self.subTest(after=after),self.assertRaises(ValueError):
                pipeline(original.replace(before,after,1))

    def test_edit_schema_rejects_ambiguous_predecessors_after_decoding(self):
        reference={'principal':'enp0:'+'a'*64,'conversation':'2'*32,'event':'3'*32}
        base={'kind':'edit','root':reference,'predecessors':[reference],'text':'Correction'}
        for patch in [{'predecessors':[]},{'predecessors':[reference,reference]},
                      {'root':{**reference,'event':'0'*32}}, {'replyTo':[]}]:
            with self.subTest(patch=patch):
                _,valid=pipeline(encode_event(event({**base,**patch})))
                self.assertFalse(valid)

    def test_duplicate_envelope_and_operation_names_fail_before_schema(self):
        original=encode_event(event({'kind':'message','text':'Hello','replyTo':[]}))
        for wire in [original.replace(b'"version":"0"',b'"version":"0","version":"0"'),
                     original.replace(b'"text":"Hello"',b'"text":"Hello","\\u0074ext":"Changed"')]:
            with self.assertRaises(ValueError):
                pipeline(wire)

    def test_valid_json_can_still_be_invalid_event(self):
        base=event({'kind':'message','text':'Hello','replyTo':[]})
        for patch in [{'version':'unknown'}, {'principal':'fixture:unknown'},
                      {'audience':['enp0:'+'b'*64]}, {'extra':True},
                      {'operation':{'kind':'message','text':'Hello','replyTo':[], 'execute':True}}]:
            with self.subTest(patch=patch):
                _,valid=pipeline(encode_event({**base,**patch}))
                self.assertFalse(valid)

    def test_equal_decoded_records_keep_distinct_wire_identity(self):
        base=event({'kind':'message','text':'Hello','replyTo':[]})
        compact=encode_event(base)
        spaced=json.dumps(base,indent=2).encode('utf-8')
        a,av=pipeline(compact);b,bv=pipeline(spaced)
        self.assertTrue(av and bv)
        self.assertEqual(a['value'],b['value'])
        self.assertNotEqual(a['octets'],b['octets'])

if __name__ == '__main__':
    unittest.main()
