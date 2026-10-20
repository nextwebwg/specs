import base64
import json
import tempfile
from pathlib import Path
import unittest
from identity_store import IdentityStore
from event_encoding import encode_event
from test_identity_store import seed,TIME
from test_successor_pipeline import fixture

class CurrentDeviceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'identity.sqlite'
        self.store=IdentityStore(self.path);self.f=fixture();seed(self.store,self.f)
        self.bindings=[json.loads(base64.b64decode(e['payload'])) for e in self.f['bundle']['bindings']]
    def tearDown(self):self.store.close();self.temp.cleanup()
    def check(self,binding,**kw):
        credential=b'email-next/device/v0\0'+bytes.fromhex(binding['principal'][5:])+bytes.fromhex(binding['device'][5:])
        args=dict(role='send',time=TIME,trust_policy='allow-unverified');args.update(kw)
        return self.store.check_device(credential,bytes.fromhex(binding['signingKey']),**args)
    def add(self):
        return self.store.accept_successor(encode_event(self.f['bundle']),candidate_digest=self.f['candidateDigest'],time=TIME)
    def test_current_genesis_key_and_explicit_trust(self):
        root=next(b for b in self.bindings if b['authority']['kind']=='first-contact')
        self.assertEqual(self.check(root)['status'],'authorized-unverified')
        self.assertEqual(self.check(root,trust_policy='require-verification')['status'],'verification-required')
        altered=dict(root,signingKey='00'*32)
        self.assertEqual(self.check(altered)['reason'],'signing-key')
    def test_enrollment_then_revocation_and_replay_with_reopen(self):
        device=next(b for b in self.bindings if b['authority']['kind']=='state')
        self.assertEqual(self.check(device)['reason'],'device-not-current')
        self.add();self.assertEqual(self.check(device)['status'],'authorized-unverified')
        self.assertEqual(self.check(device)['head'],self.f['candidateDigest'])
        self.store.accept_successor(encode_event(self.f['removalBundle']),candidate_digest=self.f['removalDigest'],time=TIME)
        self.store.close();self.store=IdentityStore(self.path)
        self.assertEqual(self.check(device)['reason'],'revoked')
        self.add();self.assertEqual(self.check(device)['reason'],'revoked')
    def test_conflicting_authorized_branch_holds_existing_key(self):
        root=next(b for b in self.bindings if b['authority']['kind']=='first-contact')
        self.add()
        self.store.accept_successor(encode_event(self.f['alternateBundle']),candidate_digest=self.f['alternateDigest'],time=TIME)
        self.assertEqual(self.check(root)['status'],'conflicted')
    def test_expiry_and_uncertain_time_are_checked_again_at_use(self):
        root=next(b for b in self.bindings if b['authority']['kind']=='first-contact')
        after=int(root['notAfter'])
        self.assertEqual(self.check(root,time={'earliest':str(after+1),'latest':str(after+1)})['status'],'not-current')
        self.assertEqual(self.check(root,time={'earliest':str(after),'latest':str(after+1)})['status'],'pending')
        self.assertEqual(self.check(root,time={'earliest':str(after),'latest':str(after)})['status'],'authorized-unverified')
        self.assertEqual(self.check(root,time={})['reason'],'time')
