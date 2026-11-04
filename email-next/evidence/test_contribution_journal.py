import sqlite3
import tempfile
from pathlib import Path
import unittest
from contribution_journal import ContributionJournal
import test_button_mime as button_fixtures
from event_encoding import encode_event

class ContributionJournalTests(unittest.TestCase):
    def test_reopen_duplicate_and_conflict_preserve_exact_bytes(self):
        question, _ = button_fixtures.ButtonMimeTests().fixtures()
        ref = {k:question[k] for k in ('conversation','principal','event')}
        original = encode_event(question)
        variant = b' '+original
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'journal.db'
            store=ContributionJournal(path)
            self.assertEqual(store.append_validated(original,ref),{'state':'stored'})
            store.close();store=ContributionJournal(path)
            self.assertEqual(store.append_validated(original,ref),{'state':'duplicate'})
            self.assertEqual(store.append_validated(variant,ref),{'state':'conflict'})
            self.assertEqual(store.append_validated(original,ref),{'state':'conflict'})
            store.close();store=ContributionJournal(path)
            snapshot=store.snapshot(ref['conversation'])
            self.assertEqual(len(snapshot),1)
            self.assertEqual(snapshot[0]['state'],'conflict')
            self.assertEqual(set(snapshot[0]['octets']),{original,variant})
            store.close()

    def test_cross_conversation_reuse_invalidates_both_views_without_returning_foreign_content(self):
        question,_=button_fixtures.ButtonMimeTests().fixtures()
        ref={k:question[k] for k in ('conversation','principal','event')}
        other=dict(question,conversation='9'*32)
        other_ref=dict(ref,conversation=other['conversation'])
        first,second=encode_event(question),encode_event(other)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'journal.db'
            a=ContributionJournal(path);b=ContributionJournal(path)
            self.assertEqual(a.append_validated(first,ref),{'state':'stored'})
            token=a.snapshot_with_token(ref['conversation'])['token']
            self.assertEqual(a.install_view(ref['conversation'],'answers',token,{'visible':True}),{'state':'installed'})
            self.assertEqual(b.append_validated(second,other_ref),{'state':'conflict'})
            self.assertEqual(a.read_view(ref['conversation'],'answers'),{'state':'stale'})
            self.assertEqual(a.install_view(ref['conversation'],'answers',token,{}),{'state':'stale'})
            for conv,wire in ((ref['conversation'],first),(other_ref['conversation'],second)):
                snapshot=a.snapshot(conv)
                self.assertEqual(snapshot,[dict(reference=dict(ref,conversation=conv),state='conflict',octets=[wire])])
            a.close();b.close();a=ContributionJournal(path)
            self.assertEqual(a.append_validated(first,ref),{'state':'conflict'})
            self.assertEqual(a.append_validated(second,other_ref),{'state':'conflict'})
            self.assertEqual(len(a.snapshot(ref['conversation'])[0]['octets']),1)
            a.close()

    def test_other_principal_same_event_and_failed_foreign_insert_do_not_poison_local_view(self):
        question,_=button_fixtures.ButtonMimeTests().fixtures()
        ref={k:question[k] for k in ('conversation','principal','event')}
        with tempfile.TemporaryDirectory() as folder:
            store=ContributionJournal(Path(folder)/'journal.db')
            store.append_validated(encode_event(question),ref)
            original=store.snapshot_with_token(ref['conversation'])
            other=dict(question,conversation='9'*32,principal='enp0:'+'9'*64)
            self.assertEqual(store.append_validated(encode_event(other),dict(ref,conversation=other['conversation'],principal=other['principal'])),{'state':'stored'})
            self.assertEqual(store.snapshot_with_token(ref['conversation']),original)
            store.db.execute("CREATE TRIGGER reject_other BEFORE INSERT ON contributions WHEN NEW.conversation='"+'8'*32+"' BEGIN SELECT RAISE(ABORT,'injected failure'); END")
            with self.assertRaises(sqlite3.IntegrityError):store.append_validated(encode_event(dict(question,conversation='8'*32)),dict(ref,conversation='8'*32))
            self.assertEqual(store.snapshot_with_token(ref['conversation']),original)
            store.close()

    def test_either_arrival_order_retains_conflict(self):
        question,_=button_fixtures.ButtonMimeTests().fixtures()
        events=[question,dict(question,conversation='9'*32)]
        for reverse in (False,True):
            with self.subTest(reverse=reverse),tempfile.TemporaryDirectory() as folder:
                store=ContributionJournal(Path(folder)/'journal.db')
                for i,event in enumerate(reversed(events) if reverse else events):
                    ref={k:event[k] for k in ('conversation','principal','event')}
                    self.assertEqual(store.append_validated(encode_event(event),ref),{'state':'stored' if i==0 else 'conflict'})
                for event in events:
                    self.assertEqual(store.snapshot(event['conversation'])[0]['state'],'conflict')
                store.close()

    def test_two_simultaneous_connections_serialize_global_namespace(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        question,_=button_fixtures.ButtonMimeTests().fixtures()
        events=[question,dict(question,conversation='9'*32)]
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'journal.db';ContributionJournal(path).close();barrier=Barrier(2)
            def write(event):
                store=ContributionJournal(path)
                try:
                    barrier.wait(timeout=5)
                    return store.append_validated(encode_event(event),{k:event[k] for k in ('conversation','principal','event')})['state']
                finally:store.close()
            with ThreadPoolExecutor(max_workers=2) as pool:
                results=[pool.submit(write,event) for event in events]
                self.assertEqual(sorted(f.result(timeout=10) for f in results),['conflict','stored'])
            store=ContributionJournal(path)
            for event in events:self.assertEqual(store.snapshot(event['conversation'])[0]['state'],'conflict')
            store.close()

    def test_retained_v0_cache_token_cannot_authorize_a_current_view(self):
        import hashlib
        question,_=button_fixtures.ButtonMimeTests().fixtures()
        ref={k:question[k] for k in ('conversation','principal','event')};raw=encode_event(question)
        # Reproduce the retained v0 token framing, not the new implementation.
        old=hashlib.sha256(b'email-next/local-journal-snapshot/v0\0')
        for value in (ref['conversation'].encode(),ref['principal'].encode(),ref['event'].encode(),raw):
            old.update(len(value).to_bytes(8,'big'));old.update(value)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'journal.db';store=ContributionJournal(path)
            store.append_validated(raw,ref)
            store.db.execute('INSERT INTO derived_views VALUES(?,?,?,?)',(ref['conversation'],'legacy',old.hexdigest(),'{}'))
            store.close();store=ContributionJournal(path)
            self.assertEqual(store.read_view(ref['conversation'],'legacy'),{'state':'stale'})
            token=store.snapshot_with_token(ref['conversation'])['token']
            self.assertEqual(store.install_view(ref['conversation'],'legacy',token,{}),{'state':'installed'})
            self.assertEqual(store.read_view(ref['conversation'],'legacy')['state'],'current')
            store.close()

    def test_invalid_identity_and_failed_transaction_leave_no_record(self):
        question, _ = button_fixtures.ButtonMimeTests().fixtures()
        ref = {k:question[k] for k in ('conversation','principal','event')}
        with tempfile.TemporaryDirectory() as folder:
            store=ContributionJournal(Path(folder)/'journal.db')
            with self.assertRaises(ValueError):
                store.append_validated(encode_event(question),dict(ref,event='wrong'))
            store.db.execute("CREATE TRIGGER reject_insert BEFORE INSERT ON contributions BEGIN SELECT RAISE(ABORT,'injected failure'); END")
            with self.assertRaises(sqlite3.IntegrityError): store.append_validated(encode_event(question),ref)
            self.assertFalse(store.db.in_transaction)
            self.assertEqual(store.snapshot(ref['conversation']),[])
            store.db.execute('DROP TRIGGER reject_insert')
            self.assertEqual(store.append_validated(encode_event(question),ref),{'state':'stored'})
            store.close()

    def test_process_exit_before_and_after_commit_has_unambiguous_retry(self):
        import json
        import subprocess
        import sys
        question, _ = button_fixtures.ButtonMimeTests().fixtures()
        ref = {k:question[k] for k in ('conversation','principal','event')}
        wire=encode_event(question)
        script = '''import json, os, sys
from contribution_journal import ContributionJournal
value=json.load(sys.stdin)
store=ContributionJournal(value['path'])
if value['phase']=='before':
    store.db.set_trace_callback(lambda sql: os._exit(91) if sql=='COMMIT' else None)
store.append_validated(bytes.fromhex(value['wire']),value['reference'])
os._exit(92)
'''
        for phase, exitcode, retry in [('before',91,'stored'),('after',92,'duplicate')]:
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as folder:
                path=Path(folder)/'journal.db'
                result=subprocess.run([sys.executable,'-c',script],cwd=Path(__file__).parent,
                    input=json.dumps(dict(path=str(path),phase=phase,wire=wire.hex(),reference=ref)),
                    text=True,capture_output=True,timeout=10)
                self.assertEqual(result.returncode,exitcode,result.stderr)
                store=ContributionJournal(path)
                self.assertEqual(store.append_validated(wire,ref),{'state':retry})
                snapshot=store.snapshot(ref['conversation'])
                self.assertEqual(len(snapshot),1)
                self.assertEqual(snapshot[0]['octets'],[wire])
                self.assertEqual(store.db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
                store.close()
