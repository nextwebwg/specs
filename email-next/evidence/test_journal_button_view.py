from pathlib import Path
import tempfile
import unittest
import test_button_mime as fixtures
from contribution_journal import ContributionJournal
from journal_button_view import derive_button_view
from event_encoding import encode_event

class JournalButtonViewTests(unittest.TestCase):
    def test_late_question_restart_duplicate_and_conflict_recompute_the_view(self):
        question,answer=fixtures.ButtonMimeTests().fixtures()
        ref=lambda e:{k:e[k] for k in ('principal','conversation','event')}
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'journal.db';store=ContributionJournal(path)
            store.append_validated(encode_event(answer),ref(answer))
            self.assertEqual(derive_button_view(store,ref(question))['heads'],[])
            store.append_validated(encode_event(question),ref(question))
            self.assertEqual(derive_button_view(store,ref(question))['heads'],[ref(answer)])
            store.close();store=ContributionJournal(path)
            store.append_validated(encode_event(answer),ref(answer))
            self.assertEqual(derive_button_view(store,ref(question))['heads'],[ref(answer)])
            store.append_validated(b' '+encode_event(question),ref(question))
            self.assertEqual(derive_button_view(store,ref(question))['heads'],[])
            self.assertEqual(len(store.snapshot(question['conversation'])),2)
            store.close()

    def test_recorded_malformed_envelope_is_not_application_authority(self):
        question,answer=fixtures.ButtonMimeTests().fixtures()
        ref=lambda e:{k:e[k] for k in ('principal','conversation','event')}
        del answer['audience']
        with tempfile.TemporaryDirectory() as folder:
            store=ContributionJournal(Path(folder)/'journal.db')
            for event in [question,answer]:store.append_validated(encode_event(event),ref(event))
            self.assertEqual(derive_button_view(store,ref(question))['heads'],[])
            store.close()

    def test_snapshot_token_detects_an_intervening_connection_write(self):
        question,answer=fixtures.ButtonMimeTests().fixtures()
        ref=lambda e:{k:e[k] for k in ('principal','conversation','event')}
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'journal.db'
            reader=ContributionJournal(path);writer=ContributionJournal(path)
            writer.append_validated(encode_event(question),ref(question))
            old=derive_button_view(reader,ref(question))
            writer.append_validated(encode_event(question),ref(question))
            self.assertEqual(old['sourceToken'],reader.snapshot_with_token(question['conversation'])['token'])
            writer.append_validated(encode_event(answer),ref(answer))
            self.assertNotEqual(old['sourceToken'],reader.snapshot_with_token(question['conversation'])['token'])
            new=derive_button_view(reader,ref(question))
            self.assertEqual(new['heads'],[ref(answer)])
            reader.close();reader=ContributionJournal(path)
            self.assertEqual(new['sourceToken'],reader.snapshot_with_token(question['conversation'])['token'])
            reader.close();writer.close()

    def test_durable_view_rejects_stale_install_and_hides_invalidated_cache(self):
        question,answer=fixtures.ButtonMimeTests().fixtures()
        ref=lambda e:{k:e[k] for k in ('principal','conversation','event')}
        conversation=question['conversation']
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'journal.db'
            reader=ContributionJournal(path);writer=ContributionJournal(path)
            self.assertEqual(reader.read_view(conversation,'answers'),{'state':'missing'})
            writer.append_validated(encode_event(question),ref(question))
            old=derive_button_view(reader,ref(question))
            writer.append_validated(encode_event(answer),ref(answer))
            self.assertEqual(reader.install_view(conversation,'answers',old['sourceToken'],old),
                             {'state':'stale'})
            self.assertEqual(reader.read_view(conversation,'answers'),{'state':'missing'})
            new=derive_button_view(reader,ref(question))
            self.assertEqual(reader.install_view(conversation,'answers',new['sourceToken'],new),
                             {'state':'installed'})
            reader.close();reader=ContributionJournal(path)
            self.assertEqual(reader.read_view(conversation,'answers')['payload']['heads'],[ref(answer)])
            writer.append_validated(encode_event(answer),ref(answer))
            self.assertEqual(reader.read_view(conversation,'answers')['state'],'current')
            writer.append_validated(b' '+encode_event(question),ref(question))
            self.assertEqual(reader.read_view(conversation,'answers'),{'state':'stale'})
            reader.close();writer.close()
