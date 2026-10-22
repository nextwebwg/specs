import hashlib
import unittest
from event_encoding import encode_event
from pairing_configuration_v1 import CHUNK,manifest,frame_chunk,assemble


class ConfigurationParts(unittest.TestCase):
    def setUp(self):
        # A UTF-8 scalar crosses the binary boundary; per-chunk decoding is wrong.
        self.data=b'x'*(CHUNK-1)+'€'.encode()+b' final configuration bytes'
        self.refs=['1'*64,'2'*64]
        self.value=dict(version='1',purpose='pairing-configuration-manifest',bytes=str(len(self.data)),sha256=hashlib.sha256(self.data).hexdigest(),parts=[dict(index=str(i),reference=r) for i,r in enumerate(self.refs)])
        self.raw=encode_event(self.value)
        self.parts=[(i,self.refs[i],frame_chunk(i,2,self.data[i*CHUNK:(i+1)*CHUNK])) for i in range(2)]

    def parse(self,raw=None,parts=None,**limits):
        return assemble(self.raw if raw is None else raw,self.parts if parts is None else parts,**(dict(max_bytes=2*CHUNK,max_parts=2)|limits))

    def test_reordered_complete_parts_preserve_exact_bytes_without_installation(self):
        result=self.parse(parts=list(reversed(self.parts)))
        self.assertEqual(result,dict(status='configuration-bytes-only',original=self.data))

    def test_missing_duplicate_foreign_or_tampered_parts_return_no_partial_result(self):
        for parts in (self.parts[:1],[self.parts[0],self.parts[0]],[(0,'3'*64,self.parts[0][2]),self.parts[1]],[(0,self.refs[0],self.parts[0][2]+b'x'),self.parts[1]],[(0,self.refs[0],frame_chunk(0,2,b'y'*CHUNK)),self.parts[1]]):
            with self.subTest(parts=len(parts)),self.assertRaises(ValueError):self.parse(parts=parts)

    def test_wrong_index_count_magic_and_length_rejected(self):
        original=self.parts[0][2]
        for changed in (b'BADMAGIC'+original[8:],original[:8]+(1).to_bytes(8,'big')+original[16:],original[:16]+(3).to_bytes(8,'big')+original[24:],original[:24]+(1).to_bytes(4,'big')+original[28:]):
            with self.assertRaises(ValueError):self.parse(parts=[(0,self.refs[0],changed),self.parts[1]])

    def test_manifest_and_local_bounds_are_independent(self):
        for limits in (dict(max_bytes=1),dict(max_parts=1),dict(max_bytes=0)):
            with self.subTest(limits=limits),self.assertRaises(ValueError):self.parse(**limits)
        for change in (dict(version='0'),dict(bytes='1'),dict(sha256='0'*64),dict(parts=[dict(index='1',reference=self.refs[0]),dict(index='0',reference=self.refs[1])]),dict(extra='ignored')):
            with self.subTest(change=change),self.assertRaises(ValueError):self.parse(raw=encode_event(self.value|change))

    def test_no_trailing_bytes_or_invalid_full_utf8_is_accepted(self):
        raw=b'\xff';v=dict(self.value,bytes='1',sha256=hashlib.sha256(raw).hexdigest(),parts=[dict(index='0',reference=self.refs[0])])
        with self.assertRaises(UnicodeError):self.parse(raw=encode_event(v),parts=[(0,self.refs[0],frame_chunk(0,1,raw))])
        with self.assertRaises(ValueError):manifest(b'{"version":"1",'+self.raw[1:],max_bytes=2*CHUNK,max_parts=2)


if __name__=='__main__':unittest.main()
