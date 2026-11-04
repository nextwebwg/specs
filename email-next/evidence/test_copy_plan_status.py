"""Scoped projection invariants, not release/identity/disclosure authorization."""
from dataclasses import replace
from itertools import permutations
import unittest
from copy_plan_status import CopySnapshot as Copy, RecipientEvidence as Recipient, summarize


class CopyProjectionTests(unittest.TestCase):
    def test_independent_ready_copy_does_not_make_held_peer_ready(self):
        copies=[Copy('visible','ready',(Recipient('bob'),)),Copy('private','waiting',(Recipient('dana'),))]
        result=summarize(('visible','private'),copies,progression='independent')
        self.assertEqual(result['candidate_units'],(('visible','bob'),))
        self.assertFalse(result['all_handoffs_confirmed']);self.assertEqual(result['counts']['pending'],2)

    def test_collective_initial_barrier_requires_every_original_selected_copy(self):
        first=Copy('visible','ready',(Recipient('bob'),));second=Copy('private','retiring',(Recipient('dana'),))
        self.assertEqual(summarize(('visible','private'),[first,second],progression='together')['candidate_units'],())
        ready=summarize(('visible','private'),[first,replace(second,readiness='ready')],progression='together')
        self.assertEqual(ready['candidate_units'],(('private','dana'),('visible','bob')))

    def test_committed_collective_barrier_does_not_erase_partial_handoff_or_repeat_it(self):
        copies=[Copy('visible','held',(Recipient('bob',accepted=True),)),Copy('private','ready',(Recipient('dana'),))]
        result=summarize(('visible','private'),copies,progression='together',collective_activated=True)
        self.assertTrue(result['complete']);self.assertEqual(result['counts']['accepted'],1)
        self.assertEqual(result['candidate_units'],(('private','dana'),))

    def test_partial_transport_uses_pending_recipient_without_shrinking_native_copy(self):
        copy=Copy('shared','ready',(Recipient('bob',accepted=True),Recipient('carol')))
        result=summarize(('shared',),[copy],progression='independent')
        self.assertEqual(result['candidate_units'],(('shared','carol'),));self.assertFalse(result['all_handoffs_confirmed'])
        held=summarize(('shared',),[replace(copy,readiness='waiting')],progression='independent')
        self.assertEqual(held['candidate_units'],());self.assertEqual(held['counts'],result['counts'])
        self.assertEqual(len(copy.recipients),2)

    def test_uncertain_and_accepted_observations_coexist_without_automatic_retry(self):
        copy=Copy('shared','ready',(Recipient('bob',accepted=True,uncertain=True),Recipient('carol',accepted=True)))
        result=summarize(('shared',),[copy],progression='independent')
        self.assertEqual(result['counts']['accepted'],2);self.assertEqual(result['counts']['uncertain'],1)
        self.assertFalse(result['all_handoffs_confirmed']);self.assertEqual(result['candidate_units'],())

    def test_later_failure_keeps_prior_handoff_and_other_copy_success(self):
        copies=[Copy('one','ready',(Recipient('bob',accepted=True,failed=True),)),Copy('two','held',(Recipient('carol',accepted=True),))]
        result=summarize(('one','two'),copies,progression='independent')
        self.assertEqual(result['counts']['accepted'],2);self.assertEqual(result['counts']['failed'],1)
        self.assertFalse(result['all_handoffs_confirmed']);self.assertEqual(result['candidate_units'],())
        clean=replace(copies[0],recipients=(Recipient('bob',accepted=True),))
        self.assertTrue(summarize(('one','two'),[clean,copies[1]],progression='independent')['all_handoffs_confirmed'])

    def test_missing_copy_or_incomplete_processing_never_qualifies_the_surviving_subset(self):
        copy=Copy('visible','ready',(Recipient('bob',accepted=True),))
        result=summarize(('visible','private'),[copy],progression='together')
        self.assertFalse(result['complete']);self.assertFalse(result['all_handoffs_confirmed']);self.assertEqual(result['candidate_units'],())
        result=summarize(('visible',),[copy],progression='independent',complete=False)
        self.assertFalse(result['all_handoffs_confirmed'])

    def test_host_exposure_survives_failed_notification_and_missing_collective_record(self):
        copy=Copy('hosted','ready',(Recipient('carol',failed=True),),content_exposed=True)
        result=summarize(('hosted',),[copy],progression='independent')
        self.assertTrue(result['content_exposure_observed']);self.assertEqual(result['counts']['accepted'],0)
        unreconciled=summarize(('hosted',),[copy],progression='together')
        self.assertFalse(unreconciled['complete']);self.assertEqual(unreconciled['reason'],'collective-state-unreconciled')
        self.assertTrue(unreconciled['content_exposure_observed']);self.assertEqual(unreconciled['candidate_units'],())

    def test_uncertain_upload_is_possible_exposure_even_without_receipt_or_successful_notification(self):
        copy=Copy('hosted','held',(Recipient('carol',uncertain=True),),content_release_uncertain=True)
        result=summarize(('hosted',),[copy],progression='independent')
        self.assertTrue(result['content_may_be_exposed']);self.assertTrue(result['content_release_uncertain'])
        self.assertFalse(result['content_exposure_observed']);self.assertFalse(result['all_handoffs_confirmed'])
        failed=replace(copy,recipients=(Recipient('carol',failed=True),))
        self.assertTrue(summarize(('hosted',),[failed],progression='independent')['content_may_be_exposed'])
        notified=replace(copy,recipients=(Recipient('carol',accepted=True),))
        self.assertFalse(summarize(('hosted',),[notified],progression='independent')['all_handoffs_confirmed'])
        known=replace(notified,content_exposed=True,content_release_uncertain=False)
        resolved=summarize(('hosted',),[known],progression='independent')
        self.assertTrue(resolved['content_may_be_exposed']);self.assertTrue(resolved['content_exposure_observed'])
        self.assertFalse(resolved['content_release_uncertain']);self.assertTrue(resolved['all_handoffs_confirmed'])

    def test_uncertain_upload_cannot_reconstruct_an_uncommitted_collective_barrier(self):
        copy=Copy('hosted','ready',(Recipient('carol'),),content_release_uncertain=True)
        result=summarize(('hosted',),[copy],progression='together')
        self.assertFalse(result['complete']);self.assertEqual(result['reason'],'collective-state-unreconciled')
        self.assertEqual(result['candidate_units'],());self.assertTrue(result['content_may_be_exposed'])
        with self.assertRaises(ValueError):summarize(('hosted',),[replace(copy,content_release_uncertain=1)],progression='independent')

    def test_snapshot_order_does_not_change_projection_or_mutate_inputs(self):
        copies=(Copy('a','ready',(Recipient('bob',accepted=True),Recipient('carol'))),Copy('b','held',(Recipient('dana',uncertain=True),)),Copy('c','ready',(Recipient('eli'),)))
        expected=summarize(('a','b','c'),copies,progression='independent')
        for order in permutations(copies):
            for recipients in permutations(order[0].recipients):
                candidate=(replace(order[0],recipients=recipients),*order[1:])
                self.assertEqual(summarize(('a','b','c'),candidate,progression='independent'),expected)
        self.assertEqual(copies[0].recipients[0],Recipient('bob',accepted=True))

    def test_malformed_ambiguous_or_empty_snapshots_cannot_be_vacuous_success(self):
        copy=Copy('a','ready',(Recipient('bob'),))
        for planned,copies,kwargs in [((),[],{}),(('a','a'),[copy],{}),(('a',),[copy,copy],{}),(('a',),[replace(copy,copy='foreign')],{}),(('a',),[replace(copy,recipients=())],{}),(('a',),[replace(copy,recipients=(Recipient('bob'),Recipient('bob')))],{}),(('a',),[replace(copy,recipients=(Recipient('bob',accepted=1),))],{}),(('a',),[copy],dict(collective_activated=True)),(('a',),[copy],dict(complete=0))]:
            with self.assertRaises(ValueError):summarize(planned,copies,progression='independent',**kwargs)
        with self.assertRaises(ValueError):summarize(('a',),[copy],progression='guess')


if __name__=='__main__':unittest.main()
