"""Strict original bytes -> references -> three actual proofs, without identity acceptance."""
import base64
import copy
import json
from pathlib import Path
import subprocess
import unittest
from event_encoding import decode_event
HERE=Path(__file__).resolve().parent

def fixture():
    return json.loads(subprocess.run(['node',str(HERE/'make-genesis-fixture.mjs')],capture_output=True,text=True,check=True).stdout)

from genesis_pipeline import pipeline

class GenesisPipelineTests(unittest.TestCase):
    def test_complete_claim_preserves_unverified_status(self):
        result=pipeline(fixture())
        self.assertEqual(result['status'],'claim-valid-unverified')
        self.assertEqual(len(result['stateDigest']),64)

    def test_wrong_proof_purpose_never_passes(self):
        original=fixture()
        for field,replacement in [('possession','authorization'),('authorization','stateProof'),('stateProof','possession')]:
            record=copy.deepcopy(original);record[field]=record[replacement]
            self.assertEqual(pipeline(record)['status'],'invalid')

    def test_reserialization_breaks_binding_reference_or_state_proof(self):
        for field,reason in [('binding','binding-digest'),('state','state-proof')]:
            record=fixture();raw=base64.b64decode(record[field]);value=json.loads(raw)
            record[field]=base64.b64encode(json.dumps(value,indent=2).encode()).decode()
            self.assertEqual(pipeline(record)['reason'],reason)

    def test_duplicates_and_malformed_utf8_fail_before_proofs(self):
        for raw in [b'{"version":"0","version":"0"}',b'{"version":"\xff"}']:
            record=fixture();record['state']=base64.b64encode(raw).decode()
            with self.assertRaises(ValueError):pipeline(record)

    def test_clock_uncertainty_must_fit_entire_binding_interval(self):
        record=fixture()
        for interval in [{'earliest':'9','latest':'10'},{'earliest':'100','latest':'101'}, {'earliest':'11','latest':'10'},None]:
            record['time']=interval
            self.assertEqual(pipeline(record)['status'],'pending')

    def test_known_expiry_and_future_validity_are_distinct_from_uncertainty(self):
        record=fixture()
        for interval,reason in [({'earliest':'101','latest':'102'},'expired'),({'earliest':'0','latest':'9'},'not-yet-valid')]:
            record['time']=interval
            self.assertEqual(pipeline(record),{'status':'not-current','reason':reason})
        for instant in ['10','100']:
            record['time']={'earliest':instant,'latest':instant}
            self.assertEqual(pipeline(record)['status'],'claim-valid-unverified')
