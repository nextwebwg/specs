"""Outbound handshake continuity at the durable candidate publication boundary."""
import unittest
from pathlib import Path
from unittest.mock import patch
import test_joined_ordering as joined_tests
from ordering_mls import JoinedOrdering,ProviderKey
from provider_mls import call

class SenderContinuityTests(unittest.TestCase):
    setUp=joined_tests.JoinedTests.setUp;tearDown=joined_tests.JoinedTests.tearDown
    def test_consecutive_candidates_continue_predecessor_after_reopen(self):
        author=self.groups[0];peer=self.groups[1];before=author.live()[1]
        first=author.stage(ProviderKey(self.provider,self.devices[0]),time=self.time)
        self.assertEqual(author.live()[1]['snapshot'],before['snapshot'])
        old_storage=dict(before['checkpoint']);continued=dict(author.live()[1]['checkpoint'])
        self.assertTrue(old_storage.keys()==continued.keys(),'continuation must not retain candidate-only storage keys')
        changed=[bytes.fromhex(k).split(b'{',1)[0] for k in old_storage if old_storage[k]!=continued[k]]
        self.assertEqual(changed,[b'MessageSecrets'])
        self.identities[0].close()
        from identity_store import IdentityStore
        self.identities[0]=IdentityStore(self.root/'0.sqlite')
        author=JoinedOrdering(self.identities[0],self.worker,self.devices[0]);self.groups[0]=author
        author.db.execute("CREATE TEMP TRIGGER fail_stage BEFORE INSERT ON qo_staged BEGIN SELECT RAISE(ABORT,'retention failure'); END")
        before_failure=author.live()
        import sqlite3
        with self.assertRaisesRegex(sqlite3.IntegrityError,'retention failure'):author.stage(ProviderKey(self.provider,self.devices[0]),time=self.time)
        self.assertTrue(author.live()==before_failure,'failed publication must roll back atomically')
        author.db.execute('DROP TRIGGER fail_stage')
        second=author.stage(ProviderKey(self.provider,self.devices[0]),time=self.time)
        state=peer.live()[1]
        one=call(self.worker,op='receive-quorum',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.devices[1]['key'],wire=first['plan']['commit'])
        two=call(self.worker,op='receive-quorum',checkpoint=one['unmerged'],group=state['snapshot']['group'],key=self.devices[1]['key'],wire=second['plan']['commit'])
        self.assertFalse(two.get('unsupported',False))
        self.assertEqual(one['before'],two['before'])
        with self.assertRaises(ValueError):call(self.worker,op='receive-quorum',checkpoint=two['unmerged'],group=state['snapshot']['group'],key=self.devices[1]['key'],wire=first['plan']['commit'])

    def test_stage_failure_and_transaction_ownership(self):
        author=self.groups[0];before=author.live()
        with patch.object(author,'validate',side_effect=ValueError('authority changed')):
            with self.assertRaisesRegex(ValueError,'authority changed'):author.stage(ProviderKey(self.provider,self.devices[0]),time=self.time)
        self.assertEqual(author.live(),before)
        self.assertEqual(author.db.execute('SELECT count(*) FROM qo_staged').fetchone()[0],0)
        author.db.execute('BEGIN IMMEDIATE')
        try:
            with self.assertRaisesRegex(ValueError,'transaction'):author.stage(ProviderKey(self.provider,self.devices[0]),time=self.time)
            self.assertTrue(author.db.in_transaction)
        finally:author.db.execute('ROLLBACK')

    def test_process_crash_before_and_after_candidate_commit(self):
        import json,subprocess,sys
        author=self.groups[0];before=author.live()
        config=self.root/'stage-child.json'
        config.write_text(json.dumps(dict(db=str(self.root/'0.sqlite'),worker=str(self.worker),provider=str(self.provider),device=self.devices[0],time=self.time)))
        program="""
import json,os,sys
from pathlib import Path
from identity_store import IdentityStore
from ordering_mls import JoinedOrdering,ProviderKey
c=json.loads(Path(sys.argv[1]).read_text());identity=IdentityStore(c['db'])
g=JoinedOrdering(identity,c['worker'],c['device'])
def crash(point):
 if point==sys.argv[2]:os._exit(74)
g.stage(ProviderKey(c['provider'],c['device']),time=c['time'],crash=crash)
raise RuntimeError('stage unexpectedly returned')
"""
        for point in ('before-commit','after-commit'):
            child=subprocess.run([sys.executable,'-c',program,str(config),point],cwd=Path(__file__).resolve().parent,capture_output=True)
            self.assertEqual(child.returncode,74,child.stderr)
            self.assertEqual(child.stdout,b'')
            self.assertEqual(author.db.execute('SELECT count(*) FROM qo_staged').fetchone()[0],int(point=='after-commit'))
            if point=='before-commit':self.assertTrue(author.live()==before)
        retained=json.loads(author.db.execute('SELECT state FROM qo_staged').fetchone()[0])
        self.assertNotIn('continuedCheckpoint',retained)
        next_candidate=author.stage(ProviderKey(self.provider,self.devices[0]),time=self.time)
        peer=self.groups[1];state=peer.live()[1]
        one=call(self.worker,op='receive-quorum',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.devices[1]['key'],wire=retained['wire'])
        call(self.worker,op='receive-quorum',checkpoint=one['unmerged'],group=state['snapshot']['group'],key=self.devices[1]['key'],wire=next_candidate['plan']['commit'])

    def test_legacy_same_predecessor_holds(self):
        import json
        author=self.groups[0]
        author.stage(ProviderKey(self.provider,self.devices[0]),time=self.time)
        row=author.db.execute('SELECT candidate,state FROM qo_staged').fetchone()
        legacy=json.loads(row[1]);del legacy['senderContinuity']
        author.db.execute('UPDATE qo_staged SET state=? WHERE candidate=?',(json.dumps(legacy).encode(),row[0]))
        before=author.live()
        with self.assertRaisesRegex(ValueError,'fresh admission'):author.stage(ProviderKey(self.provider,self.devices[0]),time=self.time)
        self.assertTrue(author.live()==before)

if __name__=='__main__':unittest.main()
