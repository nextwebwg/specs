import unittest
from admission_windows import issue, validate, check_create_window, check_receive_window, MAX


class AdmissionWindowTests(unittest.TestCase):
    def setUp(self):
        self.local = issue('a' * 64, '100', '200', receive_delay=50)
        self.invitation = dict(keyPackageRef='a' * 64, notBefore='120', notAfter='180', receiveUntil='240')

    def test_receiving_never_reopens_creation(self):
        time = dict(earliest='210', latest='211')
        self.assertEqual(check_create_window(self.local, time), 'creation-held')
        self.assertEqual(check_receive_window(self.local, self.invitation, time), 'within-delayed-receive-window')
        self.assertEqual(check_create_window(self.local, dict(earliest='200', latest='200')), 'within-create-window')

    def test_entire_clock_interval_must_fit_original_deadline(self):
        self.assertEqual(check_receive_window(self.local, self.invitation, dict(earliest='240', latest='240')), 'within-delayed-receive-window')
        self.assertEqual(check_receive_window(self.local, self.invitation, dict(earliest='240', latest='241')), 'receiving-held')
        self.assertEqual(check_receive_window(self.local, self.invitation, dict(earliest='119', latest='120')), 'receiving-held')

    def test_peer_cannot_extend_or_substitute_custody(self):
        for changed in (dict(receiveUntil='251'), dict(keyPackageRef='b' * 64), dict(notAfter='201'), dict(notBefore='99')):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                check_receive_window(self.local, dict(self.invitation, **changed), dict(earliest='210', latest='210'))

    def test_strict_policy_can_choose_zero_delay(self):
        local = issue('a' * 64, '100', '200', receive_delay=0)
        invitation = dict(self.invitation, notAfter='200', receiveUntil='200')
        self.assertEqual(check_receive_window(local, invitation, dict(earliest='201', latest='201')), 'receiving-held')

    def test_overflow_and_noncanonical_times_never_wrap(self):
        with self.assertRaisesRegex(ValueError, 'overflow'):
            issue('a' * 64, '100', str(MAX), receive_delay=1)
        record = issue('a' * 64, str(MAX - 1), str(MAX), receive_delay=0)
        self.assertEqual(validate(record), (MAX - 1, MAX, MAX))
        for bad in ('01', '-1', '1.0', str(MAX + 1), 200, True):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                issue('a' * 64, '100', bad)

    def test_a_shorter_invitation_does_not_reset_issuer_retention(self):
        invitation = dict(self.invitation, notAfter='150', receiveUntil='220')
        self.assertEqual(check_receive_window(self.local, invitation, dict(earliest='221', latest='221')), 'receiving-held')
        self.assertEqual(self.local['receiveUntil'], '250')


if __name__ == '__main__':
    unittest.main()
