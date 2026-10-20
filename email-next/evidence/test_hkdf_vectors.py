"""Separate cryptography-library known answers; no OpenMLS implementation claim."""
import unittest
from hkdf_vectors import check_sha256_boundaries, check_vector, extract_source, load_vectors


class HKDFVectorsTest(unittest.TestCase):
    def test_all_seven_published_known_answers(self):
        for vector in load_vectors():
            with self.subTest(case=vector['case']):
                check_vector(vector)

    def test_empty_and_omitted_salt_remain_distinct_fixture_inputs(self):
        cases = {v['case']: v for v in load_vectors()}
        self.assertEqual(cases[3]['salt'], '')
        self.assertEqual(cases[6]['salt'], '')
        self.assertIsNone(cases[7]['salt'])

    def test_selected_sha256_output_bound(self):
        check_sha256_boundaries()

    def test_wrong_expected_output_and_source_are_rejected(self):
        vector = dict(load_vectors()[0])
        vector['OKM'] = '00' * vector['length']
        with self.assertRaisesRegex(AssertionError, 'OKM mismatch'):
            check_vector(vector)
        with self.assertRaisesRegex(ValueError, 'snapshot differs'):
            extract_source(b'untrusted substitute source')


if __name__ == '__main__':
    unittest.main()
