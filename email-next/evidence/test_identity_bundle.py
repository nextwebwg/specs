import base64
import copy
import json
import unittest
from event_encoding import encode_event,EventLimitExceeded
from identity_bundle import decode_identity_bundle,verify_genesis_bundle
from test_genesis_pipeline import fixture

def bundle():
    f=fixture()
    return {'version':'0','purpose':'identity-bundle','principal':'enp0:'+'a'*64,
            'states':[{'payload':f['state'],'signature':f['stateProof']}],
            'bindings':[{'payload':f['binding'],'authorization':f['authorization'],'possession':f['possession']}]}

class IdentityBundleTests(unittest.TestCase):
    def test_selected_carrier_reaches_real_proof_checks(self):
        value=bundle();octets=encode_event(value);decoded=decode_identity_bundle(octets)
        self.assertEqual(decoded['states'][0]['octets'],base64.b64decode(value['states'][0]['payload']))
        result=verify_genesis_bundle(octets,time={'earliest':'10','latest':'100'})
        self.assertEqual(result['status'],'claim-valid-unverified')
    def test_wrapper_reserialization_preserves_record_proofs(self):
        value=bundle()
        a=verify_genesis_bundle(encode_event(value),time={'earliest':'20','latest':'20'})
        b=verify_genesis_bundle(json.dumps(value,indent=2).encode(),time={'earliest':'20','latest':'20'})
        self.assertEqual(a,b)
    def test_duplicate_payloads_and_scope_mismatch_rejected(self):
        value=bundle();value['states'].append(copy.deepcopy(value['states'][0]))
        with self.assertRaises(ValueError):decode_identity_bundle(encode_event(value))
        value=bundle();value['principal']='enp0:'+'b'*64
        with self.assertRaises(ValueError):decode_identity_bundle(encode_event(value))
    def test_noncanonical_base64_and_proof_encoding_rejected(self):
        for mutate in [lambda e:e.update(payload=e['payload']+'\n'),lambda e:e.update(payload='Zh=='),lambda e:e.update(signature=e['signature'].upper()),lambda e:e.update(extra='ignored')]:
            value=bundle();mutate(value['states'][0])
            with self.assertRaises(ValueError):decode_identity_bundle(encode_event(value))
    def test_duplicate_names_inside_payload_rejected_before_proofs(self):
        value=bundle();raw=base64.b64decode(value['states'][0]['payload'])
        raw=raw.replace(b'"version":"0"',b'"version":"0","version":"0"')
        value['states'][0]['payload']=base64.b64encode(raw).decode()
        with self.assertRaises(ValueError):decode_identity_bundle(encode_event(value))
    def test_partial_bundle_decodes_but_cannot_be_used_as_genesis(self):
        value=bundle();value['states']=[]
        self.assertEqual(len(decode_identity_bundle(encode_event(value))['bindings']),1)
        with self.assertRaises(ValueError):verify_genesis_bundle(encode_event(value),time=None)
        value['bindings']=[]
        with self.assertRaises(ValueError):decode_identity_bundle(encode_event(value))
    def test_whole_bundle_limit_precedes_nested_decoding(self):
        with self.assertRaises(EventLimitExceeded):decode_identity_bundle(b' '*(1048576+1))
