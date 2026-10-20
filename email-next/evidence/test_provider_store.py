import copy
import tempfile
import unittest
from pathlib import Path
from provider_control import OPERATIONS
from provider_store import ProviderStore, ExchangeConflict, QuotaExceeded
import test_provider_control as fixtures


class ProviderStoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.ProviderControlTests.setUpClass()
    def setUp(self):
        self.fixture=fixtures.ProviderControlTests();self.fixture.setUp()
        self.c=self.fixture.c
        # Grant outlives request so exact retained retries remain accessible.
        self.c['notAfter']=1000
        self.target=copy.deepcopy(self.c)
        self.target.update(role='target',operations=OPERATIONS['target'][:])
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'queue.sqlite'
        self.store=ProviderStore(self.path)
        self.ident='5'*64
        self.response=self.fixture.sign(self.fixture.response,'target')
    def tearDown(self):
        self.store.close();self.temp.cleanup()
    def request(self,time=(20,21),octets=None,config=None):
        return self.store.put_request(config or self.c,self.fixture.f['initiatorKey'],self.ident,
            octets or self.fixture.request,time=time)
    def respond(self,time=(20,21),octets=None,config=None):
        return self.store.put_response(config or self.target,self.fixture.f['initiatorKey'],
            self.fixture.f['targetKey'],self.ident,octets or self.response,time=time,target_mailbox='Alice@example.com')
    def test_restart_and_exact_retries_after_expiry(self):
        self.assertEqual(self.request()['status'],'pending')
        self.assertEqual(self.respond()['status'],'responded')
        self.store.close();self.store=ProviderStore(self.path)
        self.assertEqual(self.request((110,111))['response'],self.response)
        result=self.respond((110,111))
        self.assertEqual(result['status'],'responded');self.assertFalse(result['effects_applied'])
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM exchanges').fetchone()[0],1)
    def test_concurrent_request_creation_has_one_created_outcome(self):
        import concurrent.futures
        import threading
        barrier=threading.Barrier(2)
        def submit():
            store=ProviderStore(self.path)
            try:
                barrier.wait(timeout=5)
                return store.put_request(self.c,self.fixture.f['initiatorKey'],self.ident,self.fixture.request,time=(20,21))['created']
            finally:store.close()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(submit) for _ in range(2)]
            self.assertEqual(sorted(f.result(timeout=15) for f in futures),[False,True])
        self.assertTrue(self.respond()['created'])
        self.assertFalse(self.respond()['created'])

    def test_expired_pending_not_reopened(self):
        self.request()
        self.assertEqual(self.request((95,96))['status'],'expired')
        with self.assertRaises(ValueError):self.respond((95,96))
        self.assertIsNone(self.store.get(self.target,self.ident,time=(95,96))['response'])
        with self.assertRaises(ValueError):self.respond((20,21))
        self.assertEqual(self.store.get(self.target,self.ident,time=(20,21))['status'],'expired')
    def test_expired_new_request_has_no_effect(self):
        with self.assertRaises(ValueError):self.request((95,96))
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM exchanges').fetchone()[0],0)
    def test_authenticated_collisions_preserve_original(self):
        self.request();self.respond()
        other=self.fixture.sign(dict(self.fixture.r,nonce='7'*64))
        with self.assertRaises(ExchangeConflict):self.request(octets=other)
        other=self.fixture.sign(dict(self.fixture.response,notAfter=79),'target')
        with self.assertRaises(ExchangeConflict):self.respond(octets=other)
        self.assertEqual(self.store.get(self.c,self.ident,time=(20,21))['response'],self.response)
        # Semantically equal reserialization is not a byte-identical retry.
        import json
        altered=json.dumps(json.loads(self.fixture.request),indent=2).encode()
        with self.assertRaises(ExchangeConflict):self.request(octets=altered)
    def test_role_grant_account_and_configuration_scope(self):
        with self.assertRaises(PermissionError):self.request(config=self.target)
        self.request()
        with self.assertRaises(PermissionError):self.respond(config=self.c)
        for key in ('account','grant'):
            c=copy.deepcopy(self.target);c[key]='8'*64
            with self.assertRaises(KeyError):self.store.get(c,self.ident,time=(20,21))
        c=copy.deepcopy(self.target);c['limits']['pendingPageSize']=31
        with self.assertRaises(ExchangeConflict):self.store.get(c,self.ident,time=(20,21))
        with self.assertRaises(ValueError):self.store.get(self.c,self.ident,time=(1001,1002))
    def test_invalid_response_does_not_occupy_slot(self):
        self.request()
        bad=self.fixture.sign(self.fixture.response,'initiator')
        with self.assertRaises(ValueError):self.respond(octets=bad)
        self.assertIsNone(self.store.get(self.c,self.ident,time=(20,21))['response'])
        self.assertEqual(self.respond()['status'],'responded')
    def test_two_connections_see_one_immutable_commit(self):
        self.request()
        second=ProviderStore(self.path)
        try:
            self.respond()
            self.assertEqual(second.put_response(self.target,self.fixture.f['initiatorKey'],self.fixture.f['targetKey'],
                self.ident,self.response,time=(20,21),target_mailbox='Alice@example.com')['status'],'responded')
        finally:second.close()

    def configure_limits(self, **limits):
        self.c['limits'].update(limits);self.target['limits'].update(limits)

    def admit(self,number,time=(20,21),config=None):
        c=config or self.c
        record=dict(self.fixture.r,id=format(number,'064x'),grant=c['grant'],account=c['account'])
        body=self.fixture.sign(record)
        return self.store.put_request(c,self.fixture.f['initiatorKey'],record['id'],body,time=time)

    def test_grant_pending_and_exact_retry_not_new_admission(self):
        self.configure_limits(maxPendingPerGrant=1,newRequestsPerMinute=1)
        self.request();self.request()
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM admissions').fetchone()[0],1)
        with self.assertRaises(QuotaExceeded):self.admit(2)
        self.respond()
        with self.assertRaises(QuotaExceeded):self.admit(2)
        self.admit(2,time=(80,81))
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM exchanges').fetchone()[0],2)

    def test_account_and_service_admission_budgets(self):
        self.configure_limits(newRequestsPerAccountPerMinute=1,newRequestsPerServicePerMinute=2)
        self.admit(1)
        c=copy.deepcopy(self.c);c['grant']='8'*64
        with self.assertRaises(QuotaExceeded):self.admit(2,config=c)
        c['account']='9'*64;self.admit(2,config=c)
        c['account']='a'*64
        with self.assertRaises(QuotaExceeded):self.admit(3,config=c)

    def test_account_service_pending_and_configuration_disagreement(self):
        self.configure_limits(maxPendingPerAccount=1,maxPendingPerService=2)
        self.admit(1)
        c=copy.deepcopy(self.c);c['grant']='8'*64
        with self.assertRaises(QuotaExceeded):self.admit(2,config=c)
        c['account']='9'*64;self.admit(2,config=c)
        c['account']='a'*64
        with self.assertRaises(QuotaExceeded):self.admit(3,config=c)
        c['limits']['maxPendingPerService']=3
        with self.assertRaises(ExchangeConflict):self.admit(3,config=c)

    def test_snapshot_pages_retry_restart_new_arrivals_and_scope(self):
        self.configure_limits(pendingPageSize=1)
        self.admit(1);self.admit(2);self.admit(3)
        first=self.store.pending(self.target,time=(20,21))
        self.assertEqual(first['ids'],[format(1,'064x')]);token=first['next']
        with self.assertRaises(QuotaExceeded):self.store.pending(self.target,time=(21,22))
        self.admit(4,time=(21,22))
        second=self.store.pending(self.target,time=(21,22),after=token)
        self.assertEqual(second['ids'],[format(2,'064x')])
        self.store.close();self.store=ProviderStore(self.path)
        self.assertEqual(second,self.store.pending(self.target,time=(21,22),after=token))
        final=self.store.pending(self.target,time=(21,22),after=second['next'])
        self.assertEqual(final['ids'],[format(3,'064x')]);self.assertIsNone(final['next'])
        c=copy.deepcopy(self.target);c['grant']='8'*64
        with self.assertRaises(ValueError):self.store.pending(c,time=(21,22),after=token)
        with self.assertRaises(PermissionError):self.store.pending(self.c,time=(21,22))
        fresh=self.store.pending(self.target,time=(25,26))
        seen=fresh['ids'][:]
        while fresh['next']:
            fresh=self.store.pending(self.target,time=(25,26),after=fresh['next']);seen+=fresh['ids']
        self.assertIn(format(4,'064x'),seen)

    def test_terminal_records_are_skipped_on_cursor_retry(self):
        self.configure_limits(pendingPageSize=1)
        self.admit(1);self.request()
        first=self.store.pending(self.target,time=(20,21))
        page=self.store.pending(self.target,time=(20,21),after=first['next'])
        self.assertEqual(page['ids'],[self.ident])
        self.respond()
        retried=self.store.pending(self.target,time=(20,21),after=first['next'])
        self.assertEqual(retried['ids'],[]);self.assertIsNone(retried['next'])

    def test_cursor_expiry_bound_and_clock_rollback(self):
        self.configure_limits(pendingPageSize=1,cursorLifetimeSeconds=6,maxActiveCursorsPerGrant=1)
        self.admit(1);self.admit(2)
        first=self.store.pending(self.target,time=(20,21))
        with self.assertRaises(QuotaExceeded):self.store.pending(self.target,time=(25,26))
        with self.assertRaises(ValueError):self.store.pending(self.target,time=(27,28),after=first['next'])
        self.store.pending(self.target,time=(27,28))
        with self.assertRaises(ValueError):self.store.pending(self.target,time=(20,21))

if __name__=='__main__':unittest.main()
