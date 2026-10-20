import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
from event_encoding import encode_event
from passive_discovery import decode_assertion, DOMAIN, APPLICATION_DOMAIN
from test_passive_discovery import assertion

class ApplicationDiscoveryTests(unittest.TestCase):
    def value(self):
        value=assertion();value.update(version='1',applications=[dict(envelopeVersion='1',operations=['answer','message','question'],ordering=['fixed-roster-v0'])]);return value
    def test_exact_signed_bytes_and_version_domain(self):
        raw=encode_event(self.value());decoded=decode_assertion(raw)
        self.assertEqual(decoded['signature_input'],APPLICATION_DOMAIN+len(raw).to_bytes(4,'big')+raw)
        key=Ed25519PrivateKey.generate();signature=key.sign(decoded['signature_input']);key.public_key().verify(signature,decoded['signature_input'])
        with self.assertRaises(InvalidSignature):key.public_key().verify(signature,DOMAIN+len(raw).to_bytes(4,'big')+raw)
        changed=self.value();changed['applications'][0]['operations']=['message']
        with self.assertRaises(InvalidSignature):key.public_key().verify(signature,decode_assertion(encode_event(changed))['signature_input'])
    def test_strict_version_and_capability_boundaries(self):
        cases=[]
        value=self.value();value['version']='0';cases.append(value)
        value=self.value();del value['applications'];cases.append(value)
        value=self.value();value['features']=[];cases.append(value)
        for field,bad in [('operations',['unknown']),('operations',[]),('operations',['message','answer']),('operations',['message','message']),('ordering',['unknown']),('ordering',[]),('envelopeVersion','0'),('extra','x')]:
            value=self.value();value['applications'][0][field]=bad;cases.append(value)
        value=self.value();value['applications']*=2;cases.append(value)
        for value in cases:
            with self.subTest(value=value),self.assertRaises(ValueError):decode_assertion(encode_event(value))
    def test_empty_applications_and_original_v0_remain_distinct(self):
        value=self.value();value['applications']=[];value['features']=[]
        self.assertEqual(decode_assertion(encode_event(value))['status'],'syntax-only-unverified')
        old=encode_event(assertion());self.assertEqual(decode_assertion(old)['signature_input'],DOMAIN+len(old).to_bytes(4,'big')+old)
