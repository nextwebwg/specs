"""Version-bound tuple negotiation only; no signed assertion9/admission claim."""
import copy
from itertools import combinations
import unittest
import suite_modules as old
import reply_suite as new


def subsets():
    names = sorted(old.MODULES)
    return [frozenset(items) for size in range(len(names)+1)
            for items in combinations(names, size)]


class ReplySuiteTests(unittest.TestCase):
    def test_every_module_set_keeps_required_reply_aware_core(self):
        for modules in subsets():
            with self.subTest(modules=modules):
                app = new.select([new.offers(modules), new.offers()])
                self.assertEqual(app, new.application())
                self.assertEqual(app['envelopeVersion'], '5')
                self.assertEqual(app['payload'], 'mime-suite-v1')
                self.assertEqual(new.validate_all_offers(new.offers(modules))[old.STREAM], modules)

    def test_all_pairwise_intersections_preserve_successor_tuple(self):
        for a in subsets():
            for b in subsets():
                self.assertEqual(new.select([new.offers(a), new.offers(b)]), new.application(a & b))

    def test_ordinary_and_managed_support_have_independent_control_requirements(self):
        offers = new.offers(['answers'], managed_modules=['reactions'])
        other = new.offers(['answers'], managed_modules=['corrections'])
        self.assertEqual(new.select([offers, other]), new.application(['answers']))
        self.assertEqual(new.select([offers, other], ordering=old.QUORUM), new.application())
        self.assertEqual(new.exchanges(offers), [dict(format='quorum-exchange-experiment', version='3'),
                                               dict(format='sender-stream-control', version='1')])
        with self.assertRaises(ValueError):
            new.select([offers, new.offers()], ordering=old.QUORUM)

    def test_old_support_mixed_versions_and_unadvertised_tuple_never_supply_successor(self):
        for device in [old.offers(), new.offers()+old.offers(),
                       [dict(new.offers()[0], envelopeVersion='4')],
                       [dict(new.offers()[0], payload='mime-suite-v0')],
                       [dict(new.offers()[0], replyIntent='0')]]:
            with self.subTest(device=device), self.assertRaises(ValueError):
                new.select([new.offers(), device])
        with self.assertRaises(ValueError):
            old.select([new.offers()])

    def test_maximal_closures_are_complete_and_strictly_bounded(self):
        full = new.offers(old.MODULES, managed_modules=old.MODULES)
        self.assertEqual(len(full), 64)
        for bad in [full[1:], full[:-1], full+full, list(reversed(full)), [], None]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                new.validate_all_offers(bad)

    def test_every_device_including_sender_is_required_and_inputs_are_not_rewritten(self):
        left = new.offers(['answers', 'reactions'])
        right = new.offers(['answers'])
        saved = copy.deepcopy([left, right])
        self.assertEqual(new.select([left, right]), new.application(['answers']))
        self.assertEqual([left, right], saved)
        self.assertEqual(new.select([left, right]), new.select([right, left]))
        for devices in [[], None, [left, None]]:
            with self.subTest(devices=devices), self.assertRaises(ValueError):
                new.select(devices)


if __name__ == '__main__':
    unittest.main()
