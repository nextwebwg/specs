import unittest
from smtp_loopback import roundtrip
from mls_mime import package,unpack

class SmtpLoopbackTests(unittest.TestCase):
    def test_data_dot_stuffing_is_removed_exactly_once(self):
        wire=b'From: alice@example.invalid\r\nTo: bob@example.invalid\r\n\r\n.\r\n..line\r\n...line\r\n'
        self.assertEqual(roundtrip(wire),wire)
    def test_binary_attachment_survives_smtp_and_mime(self):
        payload=bytes(range(256))*5
        self.assertEqual(unpack(roundtrip(package(payload))),payload)
    def test_invalid_input_fails_before_opening_listener(self):
        for wire in [b'x\n',b'x',b'x'*2097153]:
            with self.assertRaises(ValueError):roundtrip(wire)
