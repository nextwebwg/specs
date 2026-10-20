import base64
from concurrent.futures import ThreadPoolExecutor
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from event_encoding import encode_event
from identity_store import IdentityStore
from mailbox_association_store import MailboxAssociationStore
from passive_discovery_verify import verify_passive_discovery

TIME={'earliest':'20','latest':'21'}
HERE=Path(__file__).parent

def fixture(second=False):
    source=(HERE/'make-passive-discovery-fixture.mjs').read_text()
    source=source.replace('JSON.stringify({good,wrongPurpose', "JSON.stringify({collision:wrap({...assertion,mailbox:'Other@example.com'}),independent:wrap({...assertion,record:'4'.repeat(32)}),good,wrongPurpose")
    if second:source=source.replace("'a'.repeat(64)","'c'.repeat(64)").replace("'b'.repeat(64)","'d'.repeat(64)")
    return json.loads(subprocess.run(['node','--input-type=module','-e',source],cwd=HERE,capture_output=True,text=True,check=True).stdout)

class MailboxAssociationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'identity.sqlite'
        self.identity=IdentityStore(self.path);self.store=MailboxAssociationStore(self.identity)
        self.f=fixture();self.item=self.seed(self.f);self.principal=self.f['good']['identity']['principal']
    def tearDown(self):self.identity.close();self.temp.cleanup()
    def seed(self,f):
        self.identity.observe(f['genesis'],first_contact_policy='allow-unverified')
        verified=verify_passive_discovery(encode_event(f['good']),self.identity,time=TIME,trust_policy='allow-unverified')
        self.assertEqual(verified['status'],'snapshot-authorized-unverified')
        binding=json.loads(base64.b64decode(f['genesis']['binding']))
        return {'assertion':base64.b64decode(f['good']['payload']),'signature':bytes.fromhex(f['good']['signature']),
                'signingKey':bytes.fromhex(binding['signingKey']),'outerFrom':['Alice@example.com'],
                'sourceId':'message-one','parserRevision':'fixture-parser-0','observedAt':'20'}
    def decide(self,n=1,**kw):
        args=dict(decision_id=f'{n:032x}',mailbox='Alice@example.com',expected_generation=None,kind='first-contact',principal=self.principal,actor='configured-policy',policy_revision='local-0',trust_policy='allow-unverified',time=TIME)
        args.update(kw);return self.store.decide(**args)
    def test_reopen_retries_and_exact_decision_identity(self):
        self.store.observe_validated_batch([self.item,self.item]);result=self.decide()
        self.assertEqual(result['status'],'associated-unverified');self.assertFalse(result['sendAuthorized'])
        self.identity.close();self.identity=IdentityStore(self.path);self.store=MailboxAssociationStore(self.identity)
        self.assertEqual(self.decide(),result);self.assertEqual(len(self.store.snapshot('Alice@example.com')['observations']),1)
        with self.assertRaises(ValueError):self.decide(policy_revision='changed')
    def test_strict_policy_and_stale_identity_cannot_select(self):
        self.store.observe_validated_batch([self.item]);self.assertEqual(self.decide(trust_policy='require-verification')['status'],'verification-required')
        self.assertIsNone(self.store.snapshot('Alice@example.com')['association'])
        head=self.identity.current_state(self.principal)['head']
        # Model an accepted conflict as an identity-store dependency, not a forged observation.
        self.identity.db.execute('INSERT INTO identity_heads VALUES(?,?,1)',(self.principal,head))
        self.assertEqual(self.decide(2)['status'],'pending')
    def test_competing_initial_claims_require_explicit_resolution(self):
        second=self.seed(fixture(True));self.store.observe_validated_batch([self.item,second])
        self.assertEqual(self.decide()['status'],'ambiguous')
        self.assertEqual(self.decide(3,trust_policy='require-verification')['status'],'ambiguous')
        result=self.decide(2,kind='resolve-first-contact',actor='local-user')
        self.assertEqual(result['status'],'associated-unverified');self.assertEqual(len(result['reviewedCandidates']),2)
    def test_unlinked_claim_replacement_and_disable(self):
        self.store.observe_validated_batch([self.item]);self.decide()
        f=fixture(True);second=self.seed(f);new=f['good']['identity']['principal']
        self.assertEqual(self.store.observe_validated_batch([second])[0]['status'],'unlinked-claim')
        self.assertEqual(self.store.snapshot('Alice@example.com')['association']['principal'],self.principal)
        result=self.decide(2,expected_generation='1',kind='replace-with-continuity-break',principal=new,actor='local-user')
        self.assertEqual(result['generation'],'2');self.assertTrue(result['continuityBreak'])
        self.assertEqual(self.decide(3,expected_generation='1')['status'],'stale')
        disabled=self.decide(4,expected_generation='2',kind='disable',principal=new,actor='local-user',trust_policy='require-verification')
        self.assertEqual(disabled['status'],'disabled');self.assertEqual(disabled['generation'],'3')
        self.assertEqual(len(self.store.snapshot('Alice@example.com')['observations']),2)
    def test_enable_requires_current_evidence_policy_and_explicit_same_principal(self):
        self.store.observe_validated_batch([self.item]);self.decide()
        self.assertEqual(self.decide(2,expected_generation='1',kind='enable',actor='local-user')['status'],'no-change')
        disabled=self.decide(3,expected_generation='1',kind='disable',actor='local-user')
        self.assertEqual(disabled['generation'],'2')
        self.assertEqual(self.decide(4,expected_generation='2',kind='disable',actor='local-user')['status'],'no-change')
        self.assertEqual(self.decide(5,expected_generation='2',kind='enable',actor='local-user',trust_policy='require-verification')['status'],'verification-required')
        self.assertEqual(self.decide(6,expected_generation='2',kind='enable',actor='local-user',principal='enp0:'+'c'*64)['status'],'invalid')
        self.assertEqual(self.decide(7,expected_generation='2',kind='enable',actor='local-user',time={'earliest':'999999','latest':'999999'})['status'],'pending')
        result=self.decide(8,expected_generation='2',kind='enable',actor='local-user')
        self.assertEqual(result['generation'],'3');self.assertFalse(result['sendAuthorized'])
        self.assertEqual(self.decide(8,expected_generation='2',kind='enable',actor='local-user'),result)
        self.assertEqual(self.decide(9,expected_generation='2',kind='disable',actor='local-user')['status'],'stale')
    def test_initialization_does_not_commit_caller_transaction(self):
        self.identity.db.execute('BEGIN IMMEDIATE')
        self.identity.db.execute("INSERT INTO mailbox_decisions VALUES('temporary','{}','{}')")
        with self.assertRaises(ValueError):MailboxAssociationStore(self.identity)
        self.assertTrue(self.identity.db.in_transaction)
        self.identity.db.execute('ROLLBACK')
        self.assertIsNone(self.identity.db.execute("SELECT 1 FROM mailbox_decisions WHERE decision_id='temporary'").fetchone())
    def related(self,name):
        f=copy.deepcopy(self.f);f['good']=f[name]
        # Verify the real cryptographic signature and current authority first.
        self.assertEqual(verify_passive_discovery(encode_event(f['good']),self.identity,time=TIME,trust_policy='allow-unverified')['status'],'snapshot-authorized-unverified')
        item=copy.deepcopy(self.item);item['assertion']=base64.b64decode(f['good']['payload'])
        item['signature']=bytes.fromhex(f['good']['signature'])
        item['outerFrom']=[json.loads(item['assertion'])['mailbox']]
        return item
    def test_authenticated_collision_cross_mailbox_holds_only_disputed_record(self):
        self.store.observe_validated_batch([self.item,self.related('collision')])
        self.assertEqual(self.decide()['status'],'pending')
        self.assertEqual(self.decide(2,mailbox='Other@example.com')['status'],'pending')
        self.assertEqual(self.decide(3,trust_policy='require-verification')['status'],'pending')
        self.store.observe_validated_batch([self.related('independent')])
        self.assertEqual(self.decide(4)['status'],'associated-unverified')
    def test_collision_preserves_existing_association_and_forged_key_cannot_poison(self):
        self.store.observe_validated_batch([self.item]);self.decide()
        before=self.store.snapshot('Alice@example.com')['association']
        forged=self.related('collision');forged['signingKey']=b'x'*32
        # Violates trusted proof-input precondition; independent authority check
        # nevertheless prevents this foreign key from indexing a collision.
        self.store.observe_validated_batch([forged])
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mailbox_authenticated_records').fetchone()[0],1)
        self.assertEqual(self.store.snapshot('Alice@example.com')['association'],before)
    def test_authorized_collision_after_pin_preserves_association(self):
        self.store.observe_validated_batch([self.item]);self.decide()
        before=self.store.snapshot('Alice@example.com')['association']
        self.store.observe_validated_batch([self.related('collision')])
        self.assertEqual(self.store.snapshot('Alice@example.com')['association'],before)
    def test_unauthorized_same_payload_cannot_block_legitimate_proof(self):
        foreign=copy.deepcopy(self.item)
        # Sign the exact bytes with a real foreign key: valid proof, no authority.
        script="""const {generateKeyPairSync}=await import('node:crypto');
        const {signPassiveDiscovery}=await import('./binding-signature.mjs');
        const {privateKey,publicKey}=generateKeyPairSync('ed25519');
        const p=Buffer.from(process.argv[1],'base64');
        console.log(JSON.stringify({signature:signPassiveDiscovery(p,privateKey),
          key:publicKey.export({format:'der',type:'spki'}).subarray(-32).toString('hex')}));"""
        proof=json.loads(subprocess.run(['node','--input-type=module','-e',script,base64.b64encode(foreign['assertion']).decode()],cwd=HERE,capture_output=True,text=True,check=True).stdout)
        foreign['signature']=bytes.fromhex(proof['signature']);foreign['signingKey']=bytes.fromhex(proof['key'])
        self.store.observe_validated_batch([foreign])
        self.assertEqual(self.decide()['status'],'pending')
        self.store.observe_validated_batch([self.item])
        self.assertEqual(self.decide(2)['status'],'associated-unverified')
        retained=self.identity.db.execute('SELECT signature,signing_key FROM mailbox_observations').fetchone()
        self.store.observe_validated_batch([foreign])
        self.assertEqual(self.identity.db.execute('SELECT signature,signing_key FROM mailbox_observations').fetchone(),retained)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mailbox_observation_variants').fetchone()[0],2)
    def test_strict_policy_without_candidate_is_pending(self):
        self.assertEqual(self.decide(trust_policy='require-verification')['status'],'pending')
    def test_batch_rollback_from_malformed_from_and_no_address_merging(self):
        bad=copy.deepcopy(self.item);bad['outerFrom']=['alice@example.com']
        with self.assertRaises(ValueError):self.store.observe_validated_batch([self.item,bad])
        self.assertEqual(self.store.snapshot('Alice@example.com')['observations'],[])
        self.store.observe_validated_batch([self.item]);self.assertEqual(self.decide(mailbox='alice@example.com')['status'],'pending')
        self.assertEqual(self.decide(2,mailbox='Alice+tag@example.com')['status'],'pending')
    def test_stale_expired_and_wrong_key_observations_not_selected(self):
        for n,change in enumerate(['state','expiry','key'],1):
            item=copy.deepcopy(self.item);v=json.loads(item['assertion'])
            if change=='state':v['state']='f'*64
            elif change=='expiry':v['notBefore']='1';v['notAfter']='2'
            else:item['signingKey']=b'0'*32
            # Deliberately violate caller validation assumptions: local identity/time
            # rechecks still block these; the store does not verify the changed proof.
            item['assertion']=encode_event(v);item['sourceId']=change
            if change=='key':v['record']='9'*32;item['assertion']=encode_event(v)
            self.store.observe_validated_batch([item]);self.assertEqual(self.decide(n)['status'],'pending')
    def test_concurrent_connections_compare_generation(self):
        self.store.observe_validated_batch([self.item]);barrier=threading.Barrier(2)
        def select(n):
            identity=IdentityStore(self.path);store=MailboxAssociationStore(identity)
            try:
                barrier.wait()
                return store.decide(decision_id=f'{n:032x}',mailbox='Alice@example.com',expected_generation=None,kind='first-contact',principal=self.principal,actor='configured-policy',policy_revision='local-0',trust_policy='allow-unverified',time=TIME)['status']
            finally:identity.close()
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(select,[1,2]))
        self.assertEqual(sorted(results),['associated-unverified','stale'])
    def test_transaction_failure_rolls_back_decision_and_current_row(self):
        self.store.observe_validated_batch([self.item])
        self.identity.db.execute("CREATE TRIGGER reject_decision BEFORE INSERT ON mailbox_decisions BEGIN SELECT RAISE(ABORT,'injected'); END")
        with self.assertRaises(Exception):self.decide()
        self.assertIsNone(self.store.snapshot('Alice@example.com')['association'])
        self.identity.db.execute('DROP TRIGGER reject_decision')
        self.assertEqual(self.decide()['status'],'associated-unverified')

if __name__=='__main__':unittest.main()
