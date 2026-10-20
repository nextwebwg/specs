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
