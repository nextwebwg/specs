import copy
from itertools import combinations
import unittest
from suite_modules import CORE,MODULES,application,offers,modules_for,validate_offers,select


def subsets():
    names=sorted(MODULES)
    return [frozenset(c) for n in range(4) for c in combinations(names,n)]


class ModuleAgreementTests(unittest.TestCase):
    def test_all_eight_combinations_have_core_and_exact_roundtrip(self):
        self.assertEqual(len(subsets()),8)
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

    def test_prior_selected_tuple_does_not_mutate_when_new_offer_arrives(self):
        old=select([offers(),offers(['answers'])]);saved=copy.deepcopy(old)
        new=select([offers(['answers']),offers(['answers'])])
        self.assertEqual(old,saved)
        self.assertNotEqual(old,new)
        # Context migration/admission remains the owning protocol's work.


if __name__=='__main__':unittest.main()
