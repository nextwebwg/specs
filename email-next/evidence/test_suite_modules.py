import copy
from itertools import combinations
import unittest
from suite_modules import CORE,MODULES,application,offers,modules_for,validate_offers,select,STREAM,QUORUM,exchanges


def subsets():
    names=sorted(MODULES)
    return [frozenset(c) for n in range(len(names)+1) for c in combinations(names,n)]


class ModuleAgreementTests(unittest.TestCase):
    def test_all_thirty_two_combinations_have_core_and_exact_roundtrip(self):
        self.assertEqual(len(subsets()),32)
        for names in subsets():
            with self.subTest(names=names):
                self.assertEqual(modules_for(application(names)),names)
                self.assertEqual(validate_offers(offers(names)),names)
                self.assertEqual(select([offers(names)]),application(names))
                self.assertTrue(CORE<=set(application(names)['operations']))

    def test_every_pair_negotiates_actual_common_modules(self):
        for a in subsets():
            for b in subsets():
                self.assertEqual(select([offers(a),offers(b)]),application(a&b))

    def test_every_managed_pair_uses_its_own_intersection_not_stream_support(self):
        for a in subsets():
            for b in subsets():
                with self.subTest(managed_a=a,managed_b=b):
                    left=offers(['answers'],managed_modules=a)
                    right=offers(['corrections'],managed_modules=b)
                    self.assertEqual(select([left,right],ordering=QUORUM),application(a&b))
                    self.assertEqual(select([left,right],ordering=STREAM),application())

    def test_group_intersection_uses_every_device_including_senders(self):
        all_modules=offers(MODULES)
        self.assertEqual(select([all_modules,offers(['answers','reactions']),offers(['answers','corrections'])]),application(['answers']))
        self.assertEqual(select([all_modules,all_modules,offers()]),application())

    def test_device_order_does_not_change_agreement(self):
        a,b=offers(['answers']),offers(['reactions'])
        self.assertEqual(select([a,b]),select([b,a]))

    def test_one_sided_answer_or_reaction_is_not_a_module(self):
        for name in ['answer','question','reaction','reaction-withdraw']:
            v=application();v['operations']=sorted(v['operations']+[name])
            with self.assertRaises(ValueError):modules_for(v)

    def test_missing_core_unknown_operations_duplicates_and_order_fail(self):
        for ops in [sorted(CORE-{'reply-message'}),sorted(CORE|{'execute'}),sorted(CORE)+['message'],list(reversed(sorted(CORE)))]:
            with self.assertRaises(ValueError):modules_for(dict(application(),operations=ops))

    def test_unknown_fields_old_versions_and_other_payloads_do_not_mix(self):
        for patch in [dict(envelopeVersion='3'),dict(payload='mime-rich-v0'),dict(extra='yes')]:
            with self.assertRaises(ValueError):modules_for(dict(application(),**patch))
        with self.assertRaises(ValueError):modules_for(dict(application(),ordering='endpoint-quorum-v0'))
        with self.assertRaises(ValueError):modules_for(dict(application(),ordering='designated-member-v0'),offer=True)

    def test_omitted_core_tuple_duplicate_or_unsorted_offers_fail(self):
        v=offers(MODULES)
        for bad in [v[:-1],v[1:],list(reversed(v)),v+[v[0]],[],v*2]:
            with self.assertRaises(ValueError):validate_offers(bad)

    def test_individually_valid_unclosed_offers_cannot_claim_support(self):
        v=[dict(application(['answers','reactions']),ordering='endpoint-quorum-v0')]
        with self.assertRaises(ValueError):validate_offers(v)
        with self.assertRaises(ValueError):select([offers(),v])

    def test_unknown_modules_and_missing_device_evidence_fail(self):
        with self.assertRaises(ValueError):offers(['fake-security-level2'])
        with self.assertRaises(ValueError):select([])
        with self.assertRaises(ValueError):select([None])

    def test_managed_support_is_optional_and_cannot_supply_stream_operations(self):
        mixed=offers(['answers'],managed_modules=['reactions'])
        self.assertEqual(validate_offers(mixed),frozenset(['answers']))
        self.assertEqual(validate_offers(mixed,ordering=QUORUM),frozenset(['reactions']))
        self.assertEqual(select([mixed,offers(['answers'])]),application(['answers']))
        with self.assertRaises(ValueError):select([mixed,offers(['answers'])],ordering=QUORUM)
        with self.assertRaises(ValueError):validate_offers([v for v in mixed if v['ordering']==QUORUM])
        self.assertEqual(exchanges(mixed),[dict(format='quorum-exchange-experiment',version='2'),dict(format='sender-stream-control',version='0')])
        self.assertEqual(exchanges(offers()),[dict(format='sender-stream-control',version='0')])

    def test_both_orderings_have_independent_complete_subset_closures(self):
        for a in subsets():
            for b in subsets():
                value=offers(a,managed_modules=b)
                self.assertEqual(validate_offers(value),a)
                self.assertEqual(validate_offers(value,ordering=QUORUM),b)
                self.assertEqual(validate_offers([v for v in value if v['ordering']==STREAM]),a)
                for wrong in [[v for v in value if v['ordering']==QUORUM],list(reversed(value)),value+[value[0]]]:
                    with self.assertRaises(ValueError):validate_offers(wrong)

    def test_service_actions_are_independent_and_absence_never_reinterprets_question(self):
        service=application(['service-actions'])
        self.assertIn('service-question',service['operations'])
        self.assertNotIn('question',service['operations'])
        self.assertEqual(modules_for(service),frozenset(['service-actions']))
        self.assertEqual(select([offers(['service-actions']),offers(['answers'])]),application())
        old=select([offers(),offers()]);saved=copy.deepcopy(old)
        self.assertEqual(select([offers(['service-actions']),offers(['service-actions'])]),service)
        self.assertEqual(old,saved)
        self.assertEqual(len(offers(MODULES,managed_modules=MODULES)),64)
        with self.assertRaises(ValueError):validate_offers(offers(MODULES,managed_modules=MODULES)*2)

    def test_hosted_receiving_support_is_independent_of_service_and_answers(self):
        hosted=application(['hosted-replies'])
        self.assertIn('hosted-holder-observation',hosted['operations'])
        self.assertNotIn('question',hosted['operations'])
        self.assertNotIn('service-question',hosted['operations'])
        self.assertEqual(select([offers(['hosted-replies']),offers(['answers','service-actions'])]),application())
        self.assertEqual(select([offers(['hosted-replies','answers']),offers(['hosted-replies'])]),hosted)
        prior=application(['answers','reactions','corrections','service-actions'])
        self.assertEqual(modules_for(prior),frozenset(['answers','reactions','corrections','service-actions']))
        with self.assertRaises(ValueError):validate_offers(offers(MODULES)[:-1])

    def test_prior_selected_tuple_does_not_mutate_when_new_offer_arrives(self):
        old=select([offers(),offers(['answers'])]);saved=copy.deepcopy(old)
        new=select([offers(['answers']),offers(['answers'])])
        self.assertEqual(old,saved)
        self.assertNotEqual(old,new)
        # Context migration/admission remains the owning protocol's work.


if __name__=='__main__':unittest.main()
