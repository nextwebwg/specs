import json
from pathlib import Path
import subprocess
import unittest
from event_encoding import encode_event
from identity_bundle import verify_successor_bundle
HERE=Path(__file__).resolve().parent

def fixture(*args):
    return json.loads(subprocess.run(['node',str(HERE/'make-successor-fixture.mjs'),*args],capture_output=True,text=True,check=True).stdout)
def run(f):
    return verify_successor_bundle(encode_event(f['bundle']),accepted_digest=f['acceptedDigest'],candidate_digest=f['candidateDigest'],time={'earliest':'20','latest':'21'})

class SuccessorTests(unittest.TestCase):
    def test_unordered_bundle_validates_real_transition_proofs(self):
        f=fixture();self.assertEqual(run(f)['status'],'transition-valid-uncommitted')
        f['bundle']['states'].reverse();f['bundle']['bindings'].reverse()
        self.assertEqual(run(f)['status'],'transition-valid-uncommitted')
    def test_valid_signatures_do_not_permit_excessive_roles(self):
        self.assertEqual(run(fixture('--excess-role'))['reason'],'delegation')
    def test_missing_dependency_is_pending(self):
        f=fixture();f['bundle']['bindings'].pop()
        self.assertEqual(run(f),{'status':'pending','reason':'binding'})
    def test_wrong_proof_purpose_and_forged_state_fail(self):
        f=fixture();f['bundle']['bindings'][0]['authorization']=f['bundle']['bindings'][0]['possession']
        self.assertEqual(run(f)['reason'],'binding-proof')
        f=fixture();f['bundle']['states'][0]['signature']='0'*128
        self.assertEqual(run(f)['reason'],'state-proof')
    def test_bundle_cannot_select_its_own_accepted_anchor(self):
        f=fixture();f['acceptedDigest']='f'*64
        self.assertEqual(run(f),{'status':'pending','reason':'state'})
        f=fixture();f['acceptedDigest']=f['candidateDigest']
        self.assertEqual(run(f)['reason'],'predecessor')
