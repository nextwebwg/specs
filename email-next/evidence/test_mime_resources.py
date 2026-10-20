import unittest
import base64
import hashlib
import json
from pathlib import Path
import subprocess
from mime_resources import parse_resources
CID='1'*32+'.'+'2'*32+'@resources.email-next.invalid'

def fixture(body='aGVsbG8=',headers=''):
    return ('MIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary=x\r\n\r\n'
            '--x\r\nContent-Type: application/octet-stream\r\n'
            'Content-ID: <'+CID+'>\r\nContent-Transfer-Encoding: base64\r\n'+headers+
            '\r\n'+body+'\r\n--x--\r\n').encode('ascii')

def parse(wire,**limits):
    return parse_resources(wire,**({'max_wire_bytes':4096,'max_parts':2,'max_decoded_bytes':100}|limits))

class MimeResourcesTests(unittest.TestCase):
    def test_actual_mime_bytes_decode(self):
        self.assertEqual(parse(fixture('aGVs\r\nbG8=')),[{'contentId':CID,'bytes':b'hello'}])
    def test_parsed_bytes_reach_manifest_binding(self):
        for body,expected in [('aGVsbG8=','complete'),('aGVsbGE=','digest-mismatch')]:
            parts=parse(fixture(body))
            data={'event':'2'*32,'id':'1'*32,
                  'manifest':[{'id':'1'*32,'size':'5','sha256':hashlib.sha256(b'hello').hexdigest()}],
                  'parts':[{'contentId':p['contentId'],'base64':base64.b64encode(p['bytes']).decode()} for p in parts],
                  'limits':{'maxBytes':100,'maxChunks':1,'maxInputBytes':100}}
            result=subprocess.run(['node',str(Path(__file__).with_name('check-mime-resource.mjs'))],
                                  input=json.dumps(data),text=True,capture_output=True,check=True)
            self.assertEqual(json.loads(result.stdout)['state'],expected)

    def test_duplicate_headers_fail(self):
        for header in ['Content-ID: <'+CID+'>\r\n','Content-Type: text/plain\r\n','Content-Transfer-Encoding: base64\r\n']:
            with self.assertRaises(ValueError):parse(fixture(headers=header))
    def test_invalid_encoding_and_noncanonical_padding_fail(self):
        for body in ['aGVsbG8=!','aGVsbG8','aGVsbG9=','aGVsbG8===']:
            with self.assertRaises(ValueError):parse(fixture(body))
    def test_limits_and_truncated_container_fail(self):
        for limits in [{'max_wire_bytes':2},{'max_parts':0},{'max_decoded_bytes':4}]:
            with self.assertRaises(ValueError):parse(fixture(),**limits)
        with self.assertRaises(ValueError):parse(fixture().replace(b'--x--\r\n',b''))
    def test_nested_multipart_is_not_searched(self):
        wire=fixture().replace(b'Content-Type: application/octet-stream',b'Content-Type: multipart/mixed; boundary=y')
        with self.assertRaises(ValueError):parse(wire)

if __name__=='__main__':unittest.main()
