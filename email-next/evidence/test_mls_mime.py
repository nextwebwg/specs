import unittest
from mls_mime import package,unpack,MAX_PAYLOAD

class MlsMimeTests(unittest.TestCase):
    def test_all_octets_survive_without_text_normalization(self):
        payload=bytes(range(256))*4+b'\r\n.\r\n\x00'
        wire=package(payload)
        self.assertEqual(unpack(wire),payload)
        self.assertNotIn(b'\n',wire.replace(b'\r\n',b''))
    def test_transfer_corruption_and_duplicate_encoding_rejected(self):
        wire=package(b'opaque bytes')
        for changed in [wire.replace(b'b3BhcXVlIGJ5dGVz',b'b3BhcXVlIGJ5dGV!'),wire.replace(b'Content-Transfer-Encoding: base64',b'Content-Transfer-Encoding: base64\r\nContent-Transfer-Encoding: base64')]:
            with self.assertRaises(ValueError):unpack(changed)
    def test_bounds_apply_before_generation_or_parsing(self):
        with self.assertRaises(ValueError):package(b'x'*(MAX_PAYLOAD+1))
        with self.assertRaises(ValueError):unpack(b'x'*2097153)
