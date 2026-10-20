import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from event_encoding import encode_event
from service_execution import ServiceStore, ClientJournal

class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'service.db'
        self.principal='enp0:'+'6'*64
        self.question=dict(principal='enp0:'+'3'*64,conversation='4'*32,event='5'*32)
        self.action=dict(action='2'*32,question=self.question,options=['7'*32,'8'*32],principals=[self.principal],service='https://service.example',notBefore=100,retryUntil=200,submitPath='/submit',statusPrefix='/status/')
        self.tokens={hashlib.sha256(b'test-token').hexdigest():dict(issuer='fixture',audience=self.action['service'],principal=self.principal,start=0,end=300,scopes=['submit','status'])}
        ServiceStore.provision(self.path,self.action)
        self.now=150;self.store=ServiceStore(self.path,self.tokens,lambda:self.now)
        self.request=dict(version='0',purpose='service-answer-submit',submission='1'*32,action='2'*32,question=self.question,principal=self.principal,option='7'*32,replaces=[])
        self.raw=encode_event(self.request)
    def count(self):
        with self.store.connect() as db:return db.execute('SELECT count(*) FROM effects').fetchone()[0]
    def test_apply_duplicate_and_exact_bytes(self):
        first=self.store.submit(self.raw,'test-token');self.assertEqual(json.loads(first[1])['outcome'],'confirmed')
        self.assertEqual(first,self.store.submit(self.raw,'test-token'))
        self.assertEqual(self.store.submit(json.dumps(self.request,indent=2).encode(),'test-token'),(409,b''));self.assertEqual(self.count(),1)
    def test_concurrent_duplicates(self):
        with concurrent.futures.ThreadPoolExecutor(4) as pool:results=list(pool.map(lambda _:self.store.submit(self.raw,'test-token'),range(8)))
        self.assertTrue(all(r==results[0] for r in results));self.assertEqual(self.count(),1)
    def test_replacement_race(self):
        original=self.store.submit(self.raw,'test-token')
        raws=[encode_event(dict(self.request,submission=c*32,replaces=['1'*32],option='8'*32)) for c in ('a','b')]
        with concurrent.futures.ThreadPoolExecutor(2) as pool:results=list(pool.map(lambda raw:self.store.submit(raw,'test-token'),raws))
        self.assertEqual(sorted(json.loads(r[1])['outcome'] for r in results),['confirmed','rejected'])
        self.assertEqual(self.store.status('1'*32,'test-token'),original);self.assertEqual(self.count(),2)
    def test_authority_and_expiry(self):
        self.assertEqual(self.store.submit(self.raw,'wrong')[0],401)
        self.assertEqual(self.store.submit(encode_event(dict(self.request,principal='enp0:'+'a'*64)),'test-token')[0],403)
        self.now=99;self.assertEqual(self.store.submit(self.raw,'test-token'),(403,b''))
        self.now=201;self.assertEqual(json.loads(self.store.submit(self.raw,'test-token')[1])['reason'],'action-expired');self.assertEqual(self.count(),0)
    def test_inclusive_bounds_and_duplicate_after_expiry(self):
        self.now=100;receipt=self.store.submit(self.raw,'test-token')
        self.now=200;self.assertEqual(json.loads(self.store.submit(encode_event(dict(self.request,submission='a'*32,replaces=['1'*32])),'test-token')[1])['outcome'],'confirmed')
        self.now=201;self.assertEqual(self.store.submit(self.raw,'test-token'),receipt)
    def test_unallowed_option_durable_and_get_readonly(self):
        self.assertEqual(json.loads(self.store.submit(encode_event(dict(self.request,option='f'*32)),'test-token')[1])['reason'],'option-not-allowed')
        self.assertEqual(self.store.status('f'*32,'test-token'),(404,b''));self.assertEqual(self.count(),0)
    def test_process_crash_before_and_after_commit(self):
        script="import json,os,sys;from service_execution import ServiceStore;s=ServiceStore(sys.argv[1],json.loads(sys.argv[2]),lambda:150);s.submit(bytes.fromhex(sys.argv[3]),'test-token',crash=lambda point:os._exit(73) if point==sys.argv[4] else None)"
        for point in ('before-commit','after-commit'):
            result=subprocess.run([sys.executable,'-c',script,str(self.path),json.dumps(self.tokens),self.raw.hex(),point],cwd=Path(__file__).parent)
            self.assertEqual(result.returncode,73);self.assertEqual(self.count(),0 if point=='before-commit' else 1)
        self.assertEqual(self.store.submit(self.raw,'test-token')[0],200);self.assertEqual(self.count(),1)
    def test_database_loss_fails_closed(self):
        self.path.unlink()
        with self.assertRaises(Exception):self.store.submit(self.raw,'test-token')
        self.assertFalse(self.path.exists())
    def test_journal_retains_bytes(self):
        path=Path(self.tmp.name)/'client.db';journal=ClientJournal(path);identity=journal.retain(self.raw,self.action['service']);journal.close()
        journal=ClientJournal(path);self.addCleanup(journal.close)
        self.assertEqual(journal.db.execute('SELECT raw FROM requests WHERE id=?',(identity,)).fetchone()[0],self.raw)
        with self.assertRaises(ValueError):journal.retain(json.dumps(self.request,indent=2).encode(),self.action['service'])
    def test_grant_rechecked_after_lock_wait(self):
        import threading
        import time
        result=[]
        with self.store.connect() as blocker:
            blocker.execute('BEGIN IMMEDIATE')
            thread=threading.Thread(target=lambda:result.append(self.store.submit(self.raw,'test-token')))
            thread.start();time.sleep(0.05);self.now=301;blocker.rollback()
        thread.join(2)
        self.assertFalse(thread.is_alive());self.assertEqual(result,[(401,b'')]);self.assertEqual(self.count(),0)
    def test_authorization_scope_audience_issuer(self):
        grant=next(iter(self.tokens.values()))
        for field,bad,status in [('audience','https://other.example',401),('issuer','other',401),('scopes',[],403),('principal','enp0:'+'a'*64,403)]:
            old=grant[field];grant[field]=bad
            self.assertEqual(self.store.submit(self.raw,'test-token')[0],status)
            grant[field]=old
        self.assertEqual(self.count(),0)
    def test_deferred_restart_order_and_get_readonly(self):
        self.store.deferred=True
        self.assertEqual(self.store.submit(self.raw,'test-token')[0],202)
        second=encode_event(dict(self.request,submission='a'*32))
        self.assertEqual(self.store.submit(second,'test-token')[0],202)
        self.store=ServiceStore(self.path,self.tokens,lambda:self.now,deferred=True)
        self.assertEqual(self.store.status('1'*32,'test-token')[0],202);self.assertEqual(self.count(),0)
        self.assertEqual(json.loads(self.store.reconcile_one('test-token')[1])['outcome'],'confirmed')
        self.assertEqual(json.loads(self.store.reconcile_one('test-token')[1])['reason'],'replacement-not-current')
        self.assertEqual(self.count(),1)
    def test_pending_replacement_order_and_invalid_predecessor(self):
        self.store.submit(self.raw,'test-token');self.store.deferred=True
        for c in ('a','b'):
            self.assertEqual(self.store.submit(encode_event(dict(self.request,submission=c*32,replaces=['1'*32])),'test-token')[0],202)
        invalid=encode_event(dict(self.request,submission='c'*32,replaces=['a'*32]))
        self.assertEqual(json.loads(self.store.submit(invalid,'test-token')[1])['reason'],'replacement-not-current')
        self.assertEqual(json.loads(self.store.reconcile_one('test-token')[1])['outcome'],'confirmed')
        self.assertEqual(json.loads(self.store.reconcile_one('test-token')[1])['reason'],'replacement-not-current');self.assertEqual(self.count(),2)
    def test_pending_expiry_and_boundary(self):
        self.store.deferred=True;self.store.submit(self.raw,'test-token');self.now=201
        self.assertEqual(json.loads(self.store.reconcile_one('test-token')[1])['reason'],'action-expired');self.assertEqual(self.count(),0)
    def test_action_expiry_rechecked_after_lock(self):
        import threading
        import time
        result=[]
        with self.store.connect() as blocker:
            blocker.execute('BEGIN IMMEDIATE')
            thread=threading.Thread(target=lambda:result.append(self.store.submit(self.raw,'test-token')))
            thread.start();time.sleep(.05);self.now=201;blocker.rollback()
        thread.join(2)
        self.assertEqual(json.loads(result[0][1])['reason'],'action-expired');self.assertEqual(self.count(),0)
    def test_connection_context_closes_on_success_and_error(self):
        import sqlite3
        with self.store.connect() as db:
            db.execute('SELECT 1')
        with self.assertRaises(sqlite3.ProgrammingError):db.execute('SELECT 1')
        with self.assertRaises(RuntimeError):
            with self.store.connect() as failed:
                raise RuntimeError('fixture failure')
        with self.assertRaises(sqlite3.ProgrammingError):failed.execute('SELECT 1')
    def test_journal_context_closes(self):
        import sqlite3
        with ClientJournal(Path(self.tmp.name)/'closed.db') as journal:
            journal.retain(self.raw,self.action['service'])
        with self.assertRaises(sqlite3.ProgrammingError):journal.state('1'*32)
