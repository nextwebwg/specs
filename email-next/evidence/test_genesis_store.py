from concurrent.futures import ThreadPoolExecutor
import tempfile
from pathlib import Path
import unittest
from genesis_store import GenesisStore
from test_genesis_pipeline import fixture

class GenesisStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'claims.sqlite'
    def tearDown(self):self.temp.cleanup()
    def test_retry_and_reopen_preserve_pin_and_original_evidence(self):
        record=fixture();store=GenesisStore(self.path)
        result=store.observe(record,first_contact_policy='allow-unverified');store.close()
        store=GenesisStore(self.path)
        self.assertEqual(store.observe(record,first_contact_policy='allow-unverified'),result)
        self.assertEqual(store.snapshot(result['principal']),{'pin':result['pin'],'claims':1,'firstContactAmbiguous':False,'unlinkedClaims':0})
        store.close()
    def test_strict_policy_records_claim_without_pin(self):
        store=GenesisStore(self.path);result=store.observe(fixture(),first_contact_policy='require-verification')
        self.assertEqual(result['status'],'verification-required');self.assertIsNone(result['pin']);store.close()
    def test_competing_valid_claim_cannot_replace_pin(self):
        store=GenesisStore(self.path);first=fixture();result=store.observe(first,first_contact_policy='allow-unverified')
        second=store.observe(fixture(),first_contact_policy='allow-unverified')
        self.assertEqual(second['status'],'unlinked-claim');self.assertEqual(second['pin'],result['pin'])
        self.assertEqual(store.observe(first,first_contact_policy='allow-unverified')['status'],'pinned-unverified');store.close()
    def test_invalid_proof_does_not_poison_established_claim(self):
        store=GenesisStore(self.path);record=fixture();result=store.observe(record,first_contact_policy='allow-unverified')
        bad=fixture();bad['stateProof']='0'*128
        self.assertEqual(store.observe(bad,first_contact_policy='allow-unverified')['status'],'invalid')
        self.assertFalse(store.snapshot(result['principal'])['firstContactAmbiguous']);store.close()
    def test_concurrent_claims_retain_both_and_at_most_one_pin(self):
        GenesisStore(self.path).close()
        records=[fixture(),fixture()]
        def observe(record):
            store=GenesisStore(self.path)
            try:return store.observe(record,first_contact_policy='allow-unverified')
            finally:store.close()
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(observe,records))
        self.assertEqual(sorted(r['status'] for r in results),['pinned-unverified','unlinked-claim'])
        store=GenesisStore(self.path);snapshot=store.snapshot(results[0]['principal']);store.close()
        self.assertEqual(snapshot['claims'],2);self.assertFalse(snapshot['firstContactAmbiguous']);self.assertEqual(snapshot['unlinkedClaims'],1)
        self.assertIn(snapshot['pin'],[r['candidate'] for r in results])

    def test_ambiguous_unpinned_claims_cannot_be_resolved_by_policy_toggle(self):
        store=GenesisStore(self.path);first=fixture()
        store.observe(first,first_contact_policy='require-verification')
        result=store.observe(fixture(),first_contact_policy='require-verification')
        self.assertEqual(result['status'],'first-contact-ambiguous')
        retry=store.observe(first,first_contact_policy='allow-unverified')
        self.assertEqual(retry['status'],'first-contact-ambiguous');self.assertIsNone(retry['pin'])
        store.close()

    def test_unlinked_claim_after_restart_cannot_suspend_original_pin(self):
        first=fixture();store=GenesisStore(self.path)
        original=store.observe(first,first_contact_policy='allow-unverified')
        store.observe(fixture(),first_contact_policy='allow-unverified');store.close()
        store=GenesisStore(self.path)
        self.assertEqual(store.observe(first,first_contact_policy='allow-unverified'),original)
        snapshot=store.snapshot(original['principal'])
        self.assertEqual(snapshot['unlinkedClaims'],1);self.assertFalse(snapshot['firstContactAmbiguous'])
        store.close()

    def test_expired_replay_preserves_pin_but_cannot_establish_new_one(self):
        record=fixture();store=GenesisStore(self.path)
        original=store.observe(record,first_contact_policy='allow-unverified')
        record['time']={'earliest':'101','latest':'102'}
        self.assertEqual(store.observe(record,first_contact_policy='allow-unverified'),{'status':'not-current','reason':'expired'})
        self.assertEqual(store.snapshot(original['principal'])['pin'],original['pin']);store.close()
        empty=GenesisStore(Path(self.temp.name)/'empty.sqlite')
        self.assertEqual(empty.observe(record,first_contact_policy='allow-unverified')['status'],'not-current')
        self.assertEqual(empty.snapshot(original['principal'])['claims'],0);empty.close()
