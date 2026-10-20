import concurrent.futures
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from package_store import PackageStore

class PackageStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name) / 'allocation.sqlite')
        self.store = PackageStore(self.path)
    def tearDown(self):
        self.store.close()
        self.temp.cleanup()
    def allocate(self, request):
        store = PackageStore(self.path)
        try:
            return store.allocate('sender', 'device', 'profile', request)
        finally:
            store.close()
    def test_restart_preserves_allocation_and_depletion(self):
        self.store.publish('p1','device','profile')
        first = self.allocate('a')
        self.assertEqual(self.allocate('a'), first)
        self.assertEqual(self.allocate('b'), {'state':'depleted'})
        self.store.publish('p2','device','profile')
        self.assertEqual(self.allocate('b'), {'state':'depleted'})
        self.assertEqual(self.allocate('c')['packageReference'], 'p2')
    def test_concurrent_distinct_requests_allocate_once(self):
        self.store.publish('p1','device','profile')
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(self.allocate, [str(i) for i in range(16)]))
        self.assertEqual(sum(r['state']=='allocated' for r in results),1)
    def test_concurrent_same_request_has_one_durable_result(self):
        for i in range(4): self.store.publish('p'+str(i),'device','profile')
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(self.allocate, ['same']*16))
        self.assertTrue(all(result==results[0] for result in results))
        remaining = self.store.db.execute('SELECT count(*) FROM packages WHERE allocated=0').fetchone()[0]
        self.assertEqual(remaining,3)
    def test_wrong_scope_does_not_consume_other_device_package(self):
        self.store.publish('p1','different-device','profile')
        self.assertEqual(self.allocate('a'),{'state':'depleted'})
        self.assertEqual(self.store.allocate('sender','different-device','profile','a')['packageReference'],'p1')
    def test_allocated_reference_cannot_be_republished(self):
        self.store.publish('p1','device','profile');self.allocate('a')
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.publish('p1','device','profile')
        self.assertEqual(self.allocate('b'),{'state':'depleted'})
    def test_process_exit_after_commit_preserves_retry_result(self):
        self.store.publish('p1','device','profile')
        program = "from package_store import PackageStore; import os,sys; s=PackageStore(sys.argv[1]); s.allocate('sender','device','profile','a'); os._exit(17)"
        result = subprocess.run([sys.executable, '-c', program, self.path],
                                cwd=Path(__file__).parent, check=False)
        self.assertEqual(result.returncode,17)
        self.assertEqual(self.allocate('a')['packageReference'],'p1')
        self.assertEqual(self.allocate('b'),{'state':'depleted'})

    def test_transaction_failure_rolls_back_unexposed_allocation(self):
        self.store.publish('p1','device','profile')
        self.store.db.execute('''CREATE TRIGGER fail_request BEFORE INSERT ON requests
            BEGIN SELECT RAISE(ABORT,'injected failure'); END''')
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.allocate('sender','device','profile','a')
        self.store.db.execute('DROP TRIGGER fail_request')
        self.assertEqual(self.allocate('a')['packageReference'],'p1')

if __name__ == '__main__': unittest.main()
