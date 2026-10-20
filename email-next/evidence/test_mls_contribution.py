"""Trusted-adapter unit cases; real MLS snapshot sourcing is tested in Rust."""
import base64
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from event_encoding import encode_event
from identity_store import IdentityStore
from mls_contribution import check
HERE=Path(__file__).parent
TIME={'earliest':'20','latest':'21'}

class ContributionBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=json.loads(subprocess.run(['node',str(HERE/'make-passive-discovery-fixture.mjs')],capture_output=True,text=True,check=True).stdout)
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.store=IdentityStore(Path(self.temp.name)/'identity.sqlite')
        f=self.fixture;self.store.observe(f['genesis'],first_contact_policy='allow-unverified')
        binding=json.loads(base64.b64decode(f['genesis']['binding']))
        self.principal=binding['principal'];self.key=binding['signingKey']
        self.credential=(b'email-next/device/v0\0'+bytes.fromhex(self.principal[5:])+bytes.fromhex(binding['device'][5:])).hex()
        event=json.loads((HERE/'mls-smoke/fixtures/message.json').read_text())
        event['principal']=self.principal;event['audience']=[self.principal]
        context={'version':'0','purpose':'conversation-context','conversation':event['conversation'],'profile':'mls-1-0001','administrators':[self.principal]}
        self.args=[encode_event(event),'aabb','1','0',self.credential,'','aabb','1',encode_event(context).hex(),['0:'+self.credential+':'+self.key]]
    def tearDown(self):self.store.close();self.temp.cleanup()
    def invoke(self):return check(*self.args,identity_store=self.store,time=TIME,trust_policy='allow-unverified')
    def test_current_accepted_key_and_identity(self):
        self.assertEqual(self.invoke(),'projected-context-matched')
        self.args[-1]=['0:'+self.credential+':'+'ff'*32]
        self.assertEqual(self.invoke(),'identity-unauthorized')
    def test_current_conflict_and_strict_policy_hold(self):
        self.assertEqual(check(*self.args,identity_store=self.store,time=TIME,trust_policy='require-verification'),'identity-verification-required')
        head=self.store.current_state(self.principal)['head']
        self.store.db.execute('INSERT INTO identity_heads VALUES(?,?,1)',(self.principal,head))
        self.assertEqual(self.invoke(),'identity-conflicted')
    def test_group_epoch_and_aad_mismatch(self):
        for position,value,expected in [(6,'ccdd','epoch-context-mismatch'),(7,'2','epoch-context-mismatch'),(5,'00','unsupported-aad')]:
            original=self.args[position];self.args[position]=value
            self.assertEqual(self.invoke(),expected);self.args[position]=original
    def test_sender_index_credential_and_duplicate_roster(self):
        self.args[3]='9';self.assertEqual(self.invoke(),'sender-not-member');self.args[3]='0'
        self.args[4]='00'*85;self.assertEqual(self.invoke(),'sender-credential-mismatch');self.args[4]=self.credential
        self.args[-1]*=2;self.assertEqual(self.invoke(),'invalid-roster')
    def test_exact_single_contribution_no_trailing_object(self):
        self.args[0]+=b'{}'
        with self.assertRaises(ValueError):self.invoke()
        self.args[0]=b'"not a contribution"'
        with self.assertRaises(ValueError):self.invoke()

if __name__=='__main__':unittest.main()
