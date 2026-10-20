"""Real MLS staging, persistence and rollback; no external effects."""
import base64
from concurrent.futures import ThreadPoolExecutor
import json
import os
import sys
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch
from identity_store import IdentityStore
from mls_receive import MlsReceive
HERE=Path(__file__).parent
BINARY=None
class DurableReceiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global BINARY
        directory=os.environ.get('EMAIL_NEXT_MLS_BIN_DIR')
        if not directory:raise RuntimeError('Set EMAIL_NEXT_MLS_BIN_DIR to the existing Cargo debug directory')
        BINARY=Path(directory)/'receive-staged'
        if not BINARY.exists():raise RuntimeError('Build receive-staged binary before these integration tests')
        cls.fixture=json.loads(subprocess.run([str(BINARY),'--fixture'],capture_output=True,check=True).stdout)
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'receiver.sqlite'
        self.identity=IdentityStore(self.path);self.receiver=MlsReceive(self.identity,BINARY)
        f=self.fixture;self.time={'earliest':f['time'],'latest':f['time']}
        record={'binding':base64.b64encode(bytes.fromhex(f['binding'])).decode(),'state':base64.b64encode(bytes.fromhex(f['state'])).decode(),'authorization':f['proofs'][0],'possession':f['proofs'][1],'stateProof':f['proofs'][2],'time':self.time}
        self.identity.observe(record,first_contact_policy='allow-unverified')
        self.receiver.install_fixture(f['group'],f['checkpoint']);self.wires=[bytes.fromhex(w)for w in f['wires']]
    def tearDown(self):self.identity.close();self.temp.cleanup()
    def receive(self,n=0,**kw):return self.receiver.receive(self.wires[n],time=self.time,trust_policy='allow-unverified',**kw)
    def revision(self):return self.identity.db.execute('SELECT revision FROM mls_checkpoint').fetchone()[0]
    def test_restart_exact_ciphertext_and_reencrypted_event(self):
        first=self.receive();self.assertEqual(first['journal'],'stored')
        self.identity.close();self.identity=IdentityStore(self.path);self.receiver=MlsReceive(self.identity,BINARY)
        self.assertEqual(self.receive(),first);self.assertEqual(self.revision(),1)
        self.assertEqual(self.receive(1)['journal'],'duplicate');self.assertEqual(self.revision(),2)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM contributions').fetchone()[0],1)
    def test_tampering_cannot_poison_real_copy(self):
        bad=bytearray(self.wires[0]);bad[-1]^=1
        result=self.receiver.receive(bytes(bad),time=self.time,trust_policy='allow-unverified')
        self.assertEqual(result['status'],'crypto-not-accepted');self.assertEqual(self.revision(),0)
        self.assertEqual(self.receive()['journal'],'stored')
    def test_valid_crypto_invalid_application_commits_and_replays_rejection(self):
        result=self.receive(2);self.assertEqual(result['status'],'invalid-application-encoding');self.assertEqual(self.revision(),1)
        self.assertEqual(self.receive(2),result);self.assertEqual(self.identity.db.execute('SELECT count(*) FROM contributions').fetchone()[0],0)
        self.assertEqual(self.receive()['journal'],'stored')
    def test_each_precommit_failure_is_atomic(self):
        for point in ('worker','journal','checkpoint','receive'):
            with self.assertRaises(RuntimeError):self.receive(fail_at=point)
            self.assertEqual(self.revision(),0)
            self.assertEqual(self.identity.db.execute('SELECT count(*) FROM contributions').fetchone()[0],0)
            self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mls_receives').fetchone()[0],0)
        self.assertEqual(self.receive()['journal'],'stored')
    def test_strict_policy_consumes_without_journal_effect(self):
        result=self.receiver.receive(self.wires[0],time=self.time,trust_policy='require-verification')
        self.assertEqual(result['status'],'identity-verification-required');self.assertEqual(self.revision(),1)
        self.assertEqual(self.receive(),result)
    def test_authenticated_event_collision_advances_checkpoint_preserves_both(self):
        self.assertEqual(self.receive()['journal'],'stored')
        result=self.receive(3)
        self.assertEqual(result['status'],'event-conflict')
        self.assertEqual(result['journal'],'conflict');self.assertEqual(self.revision(),2)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM contributions').fetchone()[0],2)
        self.assertEqual(self.receive(3),result);self.assertFalse(result['effectsApplied'])
    def test_invalid_local_time_never_consumes_ciphertext(self):
        for time in (None,{}, {'earliest':'020','latest':'21'}, {'earliest':'22','latest':'21'}, {'earliest':'20','latest':21}):
            with self.assertRaises(ValueError):self.receiver.receive(self.wires[0],time=time,trust_policy='allow-unverified')
            self.assertEqual(self.revision(),0)
        self.assertEqual(self.receive()['journal'],'stored')
    def test_current_identity_conflict_consumes_without_accepting_contribution(self):
        principal='enp0:'+'01'*32
        head=self.identity.current_state(principal)['head']
        # Existing identity tests establish branch validation; model its accepted
        # conflict outcome here to test the same-transaction integration boundary.
        self.identity.db.execute('INSERT INTO identity_heads VALUES(?,?,1)',(principal,head))
        self.assertEqual(self.receive()['status'],'identity-conflicted')
        self.assertEqual(self.revision(),1)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM contributions').fetchone()[0],0)
    def test_process_death_after_checkpoint_write_rolls_back_all(self):
        self.identity.db.execute("CREATE TRIGGER crash_receive BEFORE INSERT ON mls_receives BEGIN SELECT injected_exit(); END")
        code="""import os,sys,json
from identity_store import IdentityStore
from mls_receive import MlsReceive
i=IdentityStore(sys.argv[1]);r=MlsReceive(i,sys.argv[2])
i.db.create_function('injected_exit',0,lambda:os._exit(71))
r.receive(bytes.fromhex(sys.argv[3]),time=json.loads(sys.argv[4]),trust_policy='allow-unverified')
"""
        result=subprocess.run([sys.executable,'-c',code,str(self.path),str(BINARY),self.wires[0].hex(),json.dumps(self.time)],cwd=HERE,capture_output=True,timeout=15)
        self.assertEqual(result.returncode,71)
        self.identity.db.execute('DROP TRIGGER crash_receive')
        self.assertEqual(self.revision(),0)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM contributions').fetchone()[0],0)
        self.assertEqual(self.receive()['journal'],'stored')
    def test_answer_before_question_reopens_and_resolves_without_decryption(self):
        self.assertEqual(self.receive(4)['status'],'pending')
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM contributions').fetchone()[0],0)
        self.identity.close();self.identity=IdentityStore(self.path);self.receiver=MlsReceive(self.identity,BINARY)
        self.receive(5);revision=self.revision()
        with patch('mls_receive.worker_call',side_effect=AssertionError('Must not decrypt again')):
            result=self.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')
        self.assertEqual(self.revision(),revision);self.assertEqual(result['viewsChanged'],0)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM contributions').fetchone()[0],2)
        view=json.loads(self.identity.db.execute('SELECT payload FROM derived_views').fetchone()[0])
        self.assertEqual([h['event'] for h in view['heads']],['6'*32])
        before=self.identity.db.execute('SELECT source_token,payload FROM derived_views').fetchall()
        self.receive(6)
        self.assertEqual(self.identity.db.execute('SELECT source_token,payload FROM derived_views').fetchall(),before)
    def test_pending_answer_current_authority_loss_cannot_reactivate(self):
        self.receive(4)
        # Identity lifecycle tests validate actual successor proofs. This case
        # models its accepted revocation result at the transaction-aware boundary.
        original=self.identity._check_device_locked
        def revoked(principal,*args):
            if principal=='enp0:'+'01'*32:return {'status':'unauthorized','reason':'revoked'}
            return original(principal,*args)
        with patch.object(self.identity,'_check_device_locked',side_effect=revoked):
            self.receive(5)
            result=self.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')
        self.assertTrue(all(state=='held:identity-unauthorized' for state in result['states'].values()))
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM contributions').fetchone()[0],0)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM derived_views').fetchone()[0],0)
    def test_accepted_button_history_survives_later_authority_loss(self):
        self.receive(4);self.receive(5)
        snapshot=self.identity.db.execute('SELECT source_token,payload FROM derived_views').fetchall()
        with patch.object(self.identity,'_check_device_locked',return_value={'status':'unauthorized','reason':'revoked'}):
            result=self.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')
        self.assertEqual(result['viewsChanged'],0)
        self.assertEqual(self.identity.db.execute('SELECT source_token,payload FROM derived_views').fetchall(),snapshot)
        self.assertTrue(all(state=='accepted' for state in result['states'].values()))
    def test_answer_collision_removes_local_head_and_replay_changes_nothing(self):
        self.receive(4);self.receive(5);self.receive(7)
        view=json.loads(self.identity.db.execute('SELECT payload FROM derived_views').fetchone()[0])
        self.assertEqual(view['heads'],[])
        snapshot=self.identity.db.execute('SELECT source_token,payload FROM derived_views').fetchall()
        self.receive(7)
        result=self.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')
        self.assertEqual(result['viewsChanged'],0)
        self.assertEqual(self.identity.db.execute('SELECT source_token,payload FROM derived_views').fetchall(),snapshot)
    def test_concurrent_connections_one_commit(self):
        barrier=threading.Barrier(2)
        def run(_):
            identity=IdentityStore(self.path);receiver=MlsReceive(identity,BINARY)
            try:
                barrier.wait();return receiver.receive(self.wires[0],time=self.time,trust_policy='allow-unverified')
            finally:identity.close()
        with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(run,range(2)))
        self.assertEqual(results[0],results[1]);self.assertEqual(self.revision(),1)
if __name__=='__main__':unittest.main()
