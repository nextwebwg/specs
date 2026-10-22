"""Real SQLite process-exit, concurrent connection and immutable handoff cases."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from setup_handoff import HandoffJournal


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'handoff.sqlite'
        self.store=HandoffJournal(self.path);self.addCleanup(self.store.close)
        self.store.freeze('send-a',1,b'authored-v1')

    def stage(self):
        self.store.stage('send-a',1,0,b'checkpoint',b'event-identity-and-body',b'original-ciphertext-delivery-set')

    def child(self, code, expected):
        result=subprocess.run([sys.executable,'-c',code,str(self.path)],capture_output=True,text=True)
        self.assertEqual(result.returncode,expected,result.stderr)

    def test_stage_process_exit_before_commit_rolls_back_every_prepared_part(self):
        self.child("import os,sys;from setup_handoff import HandoffJournal;s=HandoffJournal(sys.argv[1]);s.stage('send-a',1,0,b'checkpoint',b'event',b'deliveries',_before_commit=lambda:os._exit(23))",23)
        self.assertIsNone(self.store.inspect('send-a',1));self.assertEqual(self.store.inspect_eligible(),[])
        self.stage();self.assertEqual(self.store.inspect('send-a',1)[1:4],(b'checkpoint',b'event-identity-and-body',b'original-ciphertext-delivery-set'))

    def test_stage_committed_before_process_exit_remains_held_without_recreation(self):
        self.child("import os,sys;from setup_handoff import HandoffJournal;s=HandoffJournal(sys.argv[1]);s.stage('send-a',1,0,b'checkpoint',b'event-identity-and-body',b'original-ciphertext-delivery-set');os._exit(24)",24)
        before=self.store.inspect('send-a',1);self.assertIsNone(before[4]);self.assertEqual(before[5],0)
        self.stage();self.assertEqual(self.store.inspect('send-a',1),before)
        with self.assertRaises(ValueError):self.store.activate('send-a',1)
        self.assertEqual(self.store.inspect_eligible(),[])

    def test_activation_process_exit_before_commit_keeps_retirement_and_no_active_outbox(self):
        self.stage();self.store.retirement_complete('send-a',1,b'trusted-engine-observation')
        self.child("import os,sys;from setup_handoff import HandoffJournal;s=HandoffJournal(sys.argv[1]);s.activate('send-a',1,_before_commit=lambda:os._exit(25))",25)
        row=self.store.inspect('send-a',1);self.assertEqual(row[4],b'trusted-engine-observation');self.assertEqual(row[5],0)
        self.store.activate('send-a',1);self.assertEqual(len(self.store.inspect_eligible()),1)

    def test_activation_committed_before_process_exit_recovers_one_exact_delivery(self):
        self.stage();self.store.retirement_complete('send-a',1,b'observation')
        self.child("import os,sys;from setup_handoff import HandoffJournal;s=HandoffJournal(sys.argv[1]);s.activate('send-a',1);os._exit(26)",26)
        self.store.activate('send-a',1);self.stage()
        self.assertEqual(self.store.inspect_eligible(),[('send-a',1,b'event-identity-and-body',b'original-ciphertext-delivery-set')])

    def test_concurrent_completion_returns_one_retained_outbox_set(self):
        self.stage();self.store.retirement_complete('send-a',1,b'observation')
        def complete(_):
            other=HandoffJournal(self.path)
            try:other.activate('send-a',1)
            finally:other.close()
        with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(complete,range(2)))
        self.assertEqual(len(self.store.inspect_eligible()),1)

    def test_edit_or_cancel_blocks_old_revision_even_after_retirement(self):
        self.stage();self.store.freeze('send-a',2,b'edited-v2')
        self.store.retirement_complete('send-a',1,b'observation-after-edit')
        with self.assertRaises(ValueError):self.store.activate('send-a',1)
        self.store.stage('send-a',2,0,b'new-checkpoint',b'new-event',b'new-delivery')
        self.store.cancel('send-a',2);self.store.retirement_complete('send-a',2,b'cleanup-after-cancel')
        with self.assertRaises(ValueError):self.store.activate('send-a',2)
        self.assertEqual(self.store.inspect_eligible(),[])

    def test_dependency_change_holds_release_but_does_not_skip_cleanup_or_erase_stage(self):
        self.stage();before=self.store.inspect('send-a',1)[1:4];self.store.advance_dependency()
        self.store.retirement_complete('send-a',1,b'observation')
        with self.assertRaises(ValueError):self.store.activate('send-a',1)
        self.assertEqual(self.store.inspect('send-a',1)[1:4],before)
        self.assertEqual(self.store.inspect_eligible(),[])

    def test_immutable_intent_preparation_and_retirement_receipt(self):
        self.stage();self.store.retirement_complete('send-a',1,b'observation')
        with self.assertRaises(ValueError):self.store.freeze('send-a',1,b'changed-authored-bytes')
        with self.assertRaises(ValueError):self.store.stage('send-a',1,0,b'checkpoint',b'different-event',b'different-ciphertext')
        with self.assertRaises(ValueError):self.store.retirement_complete('send-a',1,b'different-observation')
        with self.assertRaises(ValueError):self.store.stage('send-b',1,0,b'checkpoint',b'event',b'delivery')
        self.assertEqual(self.store.inspect('send-a',1)[1:4],(b'checkpoint',b'event-identity-and-body',b'original-ciphertext-delivery-set'))

    def test_cancellation_or_dependency_change_after_activation_holds_inspection(self):
        self.stage();self.store.retirement_complete('send-a',1,b'observation');self.store.activate('send-a',1)
        self.store.advance_dependency();self.assertEqual(self.store.inspect_eligible(),[])
        self.store.cancel('send-a',1);self.assertEqual(self.store.inspect('send-a',1)[5],1)
        with self.assertRaises(ValueError):self.store.activate('send-a',1)

    def test_separate_copy_unit_cannot_activate_or_cancel_its_peer(self):
        self.stage();self.store.retirement_complete('send-a',1,b'observation-a');self.store.activate('send-a',1)
        self.store.freeze('private-copy-unit',1,b'same-authored-snapshot')
        self.store.stage('private-copy-unit',1,0,b'private-checkpoint',b'independent-private-event',b'independent-private-delivery')
        self.assertEqual([r[0] for r in self.store.inspect_eligible()],['send-a'])
        self.store.retirement_complete('private-copy-unit',1,b'observation-private')
        self.store.activate('private-copy-unit',1)
        self.assertEqual(len(self.store.inspect_eligible()),2)
        self.store.cancel('private-copy-unit',1)
        self.assertEqual(self.store.inspect_eligible(),[('send-a',1,b'event-identity-and-body',b'original-ciphertext-delivery-set')])


if __name__=='__main__':unittest.main()
