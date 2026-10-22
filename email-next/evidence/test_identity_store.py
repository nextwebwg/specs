from concurrent.futures import ThreadPoolExecutor
import tempfile
import base64
import sqlite3
from contextlib import closing
import subprocess
import json
import sys
from pathlib import Path
import unittest
from identity_store import IdentityStore
from event_encoding import encode_event
from test_successor_pipeline import fixture
TIME={'earliest':'20','latest':'21'}

def seed(store,f):
    state=f['bundle']['states'][1];binding=f['bundle']['bindings'][1]
    return store.observe({'state':state['payload'],'binding':binding['payload'],'stateProof':state['signature'],
                          'authorization':binding['authorization'],'possession':binding['possession'],'time':TIME},
                         first_contact_policy='allow-unverified')

class IdentityStoreTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'identity.sqlite'
    def tearDown(self):self.temp.cleanup()
    def test_commit_reopen_retry_preserves_head(self):
        f=fixture();store=IdentityStore(self.path);seed(store,f)
        result=store.accept_successor(encode_event(f['bundle']),candidate_digest=f['candidateDigest'],time=TIME)
        self.assertEqual(result['status'],'accepted-unverified');store.close()
        store=IdentityStore(self.path)
        self.assertEqual(store.accept_successor(encode_event(f['bundle']),candidate_digest=f['candidateDigest'],time=TIME),{'status':'already-recorded','head':f['candidateDigest']})
        self.assertEqual(store.current_state(f['bundle']['principal']),{'head':f['candidateDigest'],'conflicted':False});store.close()
    def test_untrusted_predecessor_cannot_initialize_identity(self):
        f=fixture();store=IdentityStore(self.path)
        self.assertEqual(store.accept_successor(encode_event(f['bundle']),candidate_digest=f['candidateDigest'],time=TIME)['reason'],'accepted-genesis');store.close()
    def test_forged_candidate_cannot_advance_or_create_conflict(self):
        f=fixture();store=IdentityStore(self.path);seed(store,f)
        f['bundle']['states'][0]['signature']='0'*128
        self.assertEqual(store.accept_successor(encode_event(f['bundle']),candidate_digest=f['candidateDigest'],time=TIME)['reason'],'state-proof')
        self.assertEqual(store.current_state(f['bundle']['principal']),{'head':f['acceptedDigest'],'conflicted':False});store.close()
    def test_authorized_concurrent_branches_are_retained_and_hold_future_operations(self):
        f=fixture();store=IdentityStore(self.path);seed(store,f);store.close()
        def accept(args):
            bundle,digest=args;store=IdentityStore(self.path)
            try:return store.accept_successor(encode_event(bundle),candidate_digest=digest,time=TIME)
            finally:store.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(accept,[(f['bundle'],f['candidateDigest']),(f['alternateBundle'],f['alternateDigest'])]))
        self.assertEqual(sorted(x['status'] for x in results),['accepted-unverified','conflicted'])
        store=IdentityStore(self.path);snapshot=store.current_state(f['bundle']['principal'])
        self.assertTrue(snapshot['conflicted']);self.assertIn(snapshot['head'],[f['candidateDigest'],f['alternateDigest']])
        self.assertEqual(store.db.execute('SELECT COUNT(*) FROM identity_transitions').fetchone()[0],2)
        self.assertEqual(store.accept_successor(encode_event(f['bundle']),candidate_digest=f['candidateDigest'],time=TIME)['status'],'conflicted');store.close()

    def test_old_transition_replay_cannot_restore_revoked_device(self):
        f=fixture();store=IdentityStore(self.path);seed(store,f)
        store.accept_successor(encode_event(f['bundle']),candidate_digest=f['candidateDigest'],time=TIME)
        removed=store.accept_successor(encode_event(f['removalBundle']),candidate_digest=f['removalDigest'],time=TIME)
        self.assertEqual(removed['status'],'accepted-unverified');store.close()
        store=IdentityStore(self.path)
        retry=store.accept_successor(encode_event(f['bundle']),candidate_digest=f['candidateDigest'],time=TIME)
        self.assertEqual(retry,{'status':'already-recorded','head':f['removalDigest']})
        self.assertEqual(store.current_state(f['bundle']['principal']),{'head':f['removalDigest'],'conflicted':False})
        store.close()

    def test_restoring_whole_authority_store_demonstrates_missing_rollback_detection(self):
        # A limitation test: transaction/replay safety is not an external
        # monotonic anchor. No production restore path is authorized here.
        f = fixture()
        store = IdentityStore(self.path)
        self.addCleanup(store.close)
        seed(store, f)
        store.accept_successor(encode_event(f['bundle']), candidate_digest=f['candidateDigest'], time=TIME)
        binding = json.loads(base64.b64decode(f['bundle']['bindings'][0]['payload']))
        self.assertEqual(binding['device'], 'end0:' + '2'*64)
        credential = b'email-next/device/v0\0' + bytes.fromhex(binding['principal'][5:] + binding['device'][5:])
        key = bytes.fromhex(binding['signingKey'])
        snapshot = Path(self.temp.name)/'earlier-authority.sqlite'
        with closing(sqlite3.connect(snapshot)) as backup:
            store.db.backup(backup)
        store.accept_successor(encode_event(f['removalBundle']), candidate_digest=f['removalDigest'], time=TIME)
        current = store.check_device(credential, key, role='send', time=TIME, trust_policy='allow-unverified')
        self.assertEqual((current['status'], current['reason']), ('unauthorized', 'revoked'))
        restored_path = Path(self.temp.name)/'isolated-restored-authority.sqlite'
        with closing(sqlite3.connect(snapshot)) as source, closing(sqlite3.connect(restored_path)) as target:
            source.backup(target)
        restored = IdentityStore(restored_path)
        self.addCleanup(restored.close)
        old = restored.check_device(credential, key, role='send', time=TIME, trust_policy='allow-unverified')
        self.assertEqual(old['status'], 'authorized-unverified')
        self.assertEqual(old['head'], f['candidateDigest'])
        # Supplying separately retained authentic revocation resolves this
        # configured stale view; it is not proof no other state was withheld.
        restored.accept_successor(encode_event(f['removalBundle']), candidate_digest=f['removalDigest'], time=TIME)
        learned = restored.check_device(credential, key, role='send', time=TIME, trust_policy='allow-unverified')
        self.assertEqual((learned['status'], learned['reason']), ('unauthorized', 'revoked'))
        self.assertEqual(store.current_state(binding['principal'])['head'], f['removalDigest'])

    def test_authorized_record_id_reuse_cannot_advance_head(self):
        f=fixture('--record-collision');store=IdentityStore(self.path);seed(store,f)
        store.accept_successor(encode_event(f['bundle']),candidate_digest=f['candidateDigest'],time=TIME)
        result=store.accept_successor(encode_event(f['removalBundle']),candidate_digest=f['removalDigest'],time=TIME)
        self.assertEqual(result,{'status':'conflicted','head':f['candidateDigest']});store.close()

    def test_exit_after_writes_before_commit_rolls_back_then_retry_succeeds(self):
        f=fixture();store=IdentityStore(self.path);seed(store,f);store.close()
        script="""
import json,os,sys
from identity_store import IdentityStore
from event_encoding import encode_event
record=json.load(sys.stdin)
store=IdentityStore(sys.argv[1])
original=store._accept_locked
def crash(*args):
    result=original(*args)
    if result['status']!='accepted-unverified':raise AssertionError(result)
    os._exit(73)
store._accept_locked=crash
store.accept_successor(encode_event(record['bundle']),candidate_digest=record['candidateDigest'],time={'earliest':'20','latest':'21'})
"""
        child=subprocess.run([sys.executable,'-c',script,str(self.path)],input=json.dumps(f),text=True,capture_output=True,cwd=Path(__file__).resolve().parent)
        self.assertEqual(child.returncode,73,child.stderr)
        store=IdentityStore(self.path)
        self.assertEqual(store.current_state(f['bundle']['principal']),{'head':f['acceptedDigest'],'conflicted':False})
        self.assertEqual(store.db.execute('SELECT COUNT(*) FROM identity_transitions').fetchone()[0],0)
        self.assertEqual(store.accept_successor(encode_event(f['bundle']),candidate_digest=f['candidateDigest'],time=TIME)['status'],'accepted-unverified')
        store.close()
