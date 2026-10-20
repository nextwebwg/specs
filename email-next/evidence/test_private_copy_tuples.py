import unittest
from application_tuples import validate_tuples,intersect,covers
from application_agreement import profile
from application_support import supports

class PrivateCopyTuples(unittest.TestCase):
    def setUp(self):
        self.t=dict(envelopeVersion='2',payload='mime-rich-v0',ordering='fixed-roster-v0',operations=['message','question'])
    def test_exact_new_tuple_and_no_old_upgrade(self):
        validate_tuples([self.t],version='4')
        for version in ('2','3'):
            with self.assertRaises(ValueError):validate_tuples([self.t],version=version)
        for payload in ('raw-event-v0','mime-contribution-v0'):
            with self.assertRaises(ValueError):validate_tuples([dict(self.t,payload=payload)],version='4')
        selected={k:v for k,v in self.t.items() if k!='ordering'}
        profile(selected)
        self.assertTrue(supports(dict(version='4',applications=[self.t]),selected,'fixed-roster-v0'))
        self.assertFalse(supports(dict(version='3',applications=[self.t]),selected,'fixed-roster-v0'))
    def test_complementary_support_is_not_union(self):
        a=dict(self.t,operations=['message']);b=dict(self.t,operations=['question'])
        self.assertEqual(intersect([[a],[b]],version='4'),[])
        b=dict(self.t,ordering='designated-member-v0')
        self.assertEqual(intersect([[self.t],[b]],version='4'),[])
