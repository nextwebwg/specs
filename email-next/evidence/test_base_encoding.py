"""RFC4648 octet vectors and the stricter discovery-field decoding contract."""
import unittest
from passive_discovery import canonical_base64


class BaseEncodingTests(unittest.TestCase):
    def test_rfc4648_ascii_octet_vectors(self):
        # RFC4648 section10, interpreting inputs as ASCII octets (erratum5855).
        for raw, encoded in [
            (b'', ''), (b'f', 'Zg=='), (b'fo', 'Zm8='), (b'foo', 'Zm9v'),
            (b'foob', 'Zm9vYg=='), (b'fooba', 'Zm9vYmE='),
            (b'foobar', 'Zm9vYmFy'),
            (bytes.fromhex('14fb9c03d97e'), 'FPucA9l+'),
            (bytes.fromhex('14fb9c03d9'), 'FPucA9k='),
            (bytes.fromhex('14fb9c03'), 'FPucAw=='),
        ]:
            with self.subTest(encoded=encoded):
                self.assertEqual(canonical_base64(encoded), raw)

    def test_all_nonzero_unused_bits_are_rejected(self):
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        # One octet has four unused bits; two octets have two unused bits.
        # These alternatives decode to the same bytes in permissive decoders.
        for encoded in ['Z' + alphabet[32 + n] + '==' for n in range(1, 16)] + [
            'Zm' + alphabet[60 + n] + '=' for n in range(1, 4)
        ]:
            with self.subTest(encoded=encoded), self.assertRaises(ValueError):
                canonical_base64(encoded)

    def test_field_encoding_is_not_mime_folding_or_base64url(self):
        for value in [
            'Zg', 'Zg=', 'Zg===', '=Zg==', 'Z=g=', 'A', 'AAAA=',
            'Zg==\r\n', ' Zg==', 'Zg==\t', 'Zg==\x00', 'Zg==é',
            '_w==', '-w==', None, b'Zg==',
        ]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                canonical_base64(value)


if __name__ == '__main__':
    unittest.main()
