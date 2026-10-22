import unittest
from event_encoding import decode_event, encode_event, EventLimitExceeded, MAX_EVENT_OCTETS, MAX_CONTAINER_DEPTH

class EncodingTests(unittest.TestCase):
    def test_exact_byte_limit_includes_whitespace(self):
        data = b'{}' + b' ' * (MAX_EVENT_OCTETS - 2)
        self.assertEqual(decode_event(data)['octets'], data)
        with self.assertRaises(EventLimitExceeded):
            decode_event(data + b' ')

    def test_container_depth_bound_before_tree_allocation(self):
        def nested(depth):
            return b'{"x":' * depth + b'true' + b'}' * depth
        decode_event(nested(MAX_CONTAINER_DEPTH))
        with self.assertRaises(EventLimitExceeded):
            decode_event(nested(MAX_CONTAINER_DEPTH + 1))
        with self.assertRaises(EventLimitExceeded):
            decode_event(b'{"x":' + b'[' * MAX_CONTAINER_DEPTH + b'true' + b']' * MAX_CONTAINER_DEPTH + b'}')

    def test_structural_looking_text_does_not_count_as_nesting(self):
        value = {'text': ('[{' * 100) + '"' + '\\' + ('}]' * 100)}
        self.assertEqual(decode_event(encode_event(value))['value'], value)
        with self.assertRaises(ValueError):
            decode_event(b'{"x":[true}')

    def test_generator_escapes_solidus_and_rejects_unsupported_values(self):
        data = encode_event({'text': 'a/b', 'required': True})
        self.assertIn(b'a\\/b', data)
        self.assertEqual(decode_event(data)['value']['text'], 'a/b')
        for value in [{'number': 1}, {'none': None}, []]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                encode_event(value)

    def test_null_exception_is_explicit_and_root_field_only(self):
        raw = b'{"keyPackageReceiveUntil":null}'
        with self.assertRaises(ValueError):decode_event(raw)
        self.assertIsNone(decode_event(raw, nullable_members=('keyPackageReceiveUntil',))['value']['keyPackageReceiveUntil'])
        self.assertEqual(encode_event({'keyPackageReceiveUntil':None}, nullable_members=('keyPackageReceiveUntil',)), raw)
        for other in (b'{"other":null}', b'{"nested":{"keyPackageReceiveUntil":null}}', b'{"keyPackageReceiveUntil":[null]}'):
            with self.subTest(other=other), self.assertRaises(ValueError):decode_event(other, nullable_members=('keyPackageReceiveUntil',))

    def test_bytes_preserved_and_unicode_decoded(self):
        original = b' {"text":"\\ud83d\\ude00", "required":true} \r\n'
        result = decode_event(original)
        self.assertEqual(result['octets'], original)
        self.assertEqual(result['value']['text'], '\U0001f600')

    def test_duplicate_decoded_names_at_every_depth(self):
        for value in [b'{"event":"a","\\u0065vent":"b"}',
                      b'{"nested":[{"x":true,"x":false}]}']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                decode_event(value)

    def test_disallowed_values_and_syntax(self):
        for value in [b'{"x":null}', b'{"x":1}', b'{"x":1e400}',
                      b'{"x":NaN}', b'[]', b'{}{}', b'{"x":true,}',
                      b'\xef\xbb\xbf{}', b'{"x":"\xff"}',
                      b'{"x":"\\ud800"}', b'{"\\udfff":true}']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                decode_event(value)

    def test_literal_and_escaped_solidus_have_equal_values_not_bytes(self):
        literal = decode_event(b'{"path":"a/b"}')
        escaped = decode_event(b'{"path":"a\\/b"}')
        self.assertEqual(literal['value'], escaped['value'])
        self.assertNotEqual(literal['octets'], escaped['octets'])

    def test_equal_objects_do_not_erase_distinct_wire_bytes(self):
        left=decode_event(b'{"a":true,"b":false}')
        right=decode_event(b'{ "b":false, "a":true }')
        self.assertEqual(left['value'],right['value'])
        self.assertNotEqual(left['octets'],right['octets'])

    def test_utf8_boundary_failures_are_not_repaired(self):
        invalid = [b'\xc0\x80', b'\xe0\x80\xaf', b'\xed\xa0\x80',
                   b'\xf0\x80\x80\xaf', b'\xf4\x90\x80\x80',
                   b'\x80', b'\xe2\x82', b'\xe2(\xa1',
                   b'\xf8\x88\x80\x80\x80', b'\xed\xa0\xbd\xed\xb8\x80']
        for raw in invalid:
            with self.subTest(octets=raw.hex()), self.assertRaises(ValueError):
                decode_event(b'{"text":"' + raw + b'"}')

    def test_valid_scalars_do_not_require_assigned_glyphs(self):
        # Replacement character as authored text, noncharacters, an unassigned
        # scalar, internal BOM and encoding boundaries are all valid UTF-8.
        text = ''.join(chr(n) for n in (0x7f, 0x80, 0x7ff, 0x800, 0xd7ff,
                    0xe000, 0xfdd0, 0xfffd, 0xfeff, 0x378, 0x10000, 0x10ffff))
        raw = ('{"text":"' + text + '"}').encode('utf-8')
        result = decode_event(raw)
        self.assertEqual(result['value']['text'], text)
        self.assertEqual(result['octets'], raw)

if __name__ == '__main__':
    unittest.main()
