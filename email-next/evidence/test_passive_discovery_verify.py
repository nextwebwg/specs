import base64
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from event_encoding import encode_event
from identity_store import IdentityStore
from passive_discovery_verify import verify_passive_discovery
TIME={'earliest':'20','latest':'21'}

class PassiveDiscoveryVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.store=IdentityStore(Path(self.temp.name)/'identity.sqlite')
        self.f=json.loads(subprocess.run(['node',str(Path(__file__).with_name('make-passive-discovery-fixture.mjs'))],capture_output=True,text=True,check=True).stdout)
    def tearDown(self):
        self.store.close();self.temp.cleanup()
    def seed(self):
        self.store.observe(self.f['genesis'],first_contact_policy='allow-unverified')
    def verify(self,name='good',policy='allow-unverified'):
        return verify_passive_discovery(encode_event(self.f[name]),self.store,time=TIME,trust_policy=policy)
    def test_real_signature_and_accepted_snapshot_without_mailbox_or_mls_claim(self):
        self.seed();before=self.store.db.total_changes
        result=self.verify()
        self.assertEqual(result['status'],'snapshot-authorized-unverified')
        self.assertFalse(result['mailbox_verified']);self.assertFalse(result['mls_validated'])
        self.assertEqual(before,self.store.db.total_changes)
    def test_no_identity_installation_from_bundle(self):
        self.assertEqual(self.verify(),{'status':'pending','reason':'accepted-identity'})
        self.assertIsNone(self.store.current_state('enp0:'+'a'*64)['head'])
    def test_tampering_and_wrong_signature_domain(self):
        self.seed()
        self.assertEqual(self.verify('wrongPurpose')['reason'],'assertion-proof')
        bad=copy.deepcopy(self.f['good']);raw=base64.b64decode(bad['payload'])
        bad['payload']=base64.b64encode(raw.replace(b'Alice',b'Carol')).decode()
        self.assertEqual(verify_passive_discovery(encode_event(bad),self.store,time=TIME,trust_policy='allow-unverified')['reason'],'assertion-proof')
    def test_stronger_policy_old_head_and_unaccepted_key(self):
        self.seed()
        self.assertEqual(self.verify(policy='require-verification')['status'],'verification-required')
        self.assertEqual(self.verify('oldHead')['status'],'stale')
        self.assertEqual(self.verify('wrongKey')['reason'],'signing-key')
    def test_alabel_holds_even_with_signature(self):
        self.seed();self.assertEqual(self.verify('alabel'),{'status':'pending','reason':'a-label-validation'})
    def test_real_signed_assertion_through_the_mime_carrier(self):
        from email import policy
        from discovery_mime import extract_discovery
        from test_discovery_mime import message
        self.seed()
        wire=message(encode_event(self.f['good']))
        part=list(wire.iter_parts())[1]
        encoded=''.join(part.get_payload().split())
        part.set_payload('\r\n'.join(encoded[i:i+20] for i in range(0,len(encoded),20)))
        extracted=extract_discovery(wire.as_bytes(policy=policy.SMTP),
                                   max_wire_bytes=2000000,max_parts=10)
        self.assertEqual(extracted['state'],'candidate')
        result=verify_passive_discovery(extracted['octets'],self.store,time=TIME,
                                       trust_policy='allow-unverified')
        self.assertEqual(result['status'],'snapshot-authorized-unverified')
        self.assertFalse(result['mailbox_verified'])
        # Re-encoding the outer wrapper leaves the signed inner bytes intact.
        decoded=json.loads(extracted['octets'])
        alternate=json.dumps(decoded,indent=2).encode()
        self.assertEqual(verify_passive_discovery(alternate,self.store,time=TIME,
                         trust_policy='allow-unverified'),result)
