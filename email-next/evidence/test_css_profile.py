import unittest
from css_profile import filter_style, KEYWORDS


class StyleTests(unittest.TestCase):
    def test_every_declared_value(self):
        for name, values in KEYWORDS.items():
            for value in values.split():
                with self.subTest(name=name, value=value):
                    self.assertEqual(filter_style(f'{name}:{value}'), f'{name}:{value}')

    def test_escaped_numeric_identifiers(self):
        self.assertEqual(filter_style(r'font-weight:\34 00;line-height:\31;padding-top:\30'), '')

    def test_invalid_duplicate_preserves_valid_value(self):
        for name, values in KEYWORDS.items():
            first = values.split()[0]
            with self.subTest(name=name):
                self.assertEqual(filter_style(f'{name}:{first};{name}:var(--x)'), f'{name}:{first}')

    def test_allowlist(self):
        self.assertEqual(filter_style('COLOR:#aBc; font-size:1rem; padding-left:0.5rem'), 'color:#abc;font-size:1rem;padding-left:0.5rem')

    def test_active_and_layout_values(self):
        self.assertEqual(filter_style('background-color:url(https://example.org); position:fixed; display:none; color:var(--x); width:100%; @import "x"; color:#123'), 'color:#123')

    def test_escaped_names(self):
        self.assertEqual(filter_style(r'c\6flor:#123; font\2d size:1rem; color:#456'), 'color:#456')

    def test_last_valid_and_important(self):
        self.assertEqual(filter_style('color:#123;color:red;color:#456!important;color:#789;color:inherit'), 'color:#789')

    def test_literal_numbers(self):
        self.assertEqual(filter_style(r'font-size:1.0rem;line-height:+1;border-width:01px;padding-top:1r\65m;font-weight:4e2'), '')
        self.assertEqual(filter_style('font-weight:400;line-height:1.25;border-width:1px'), 'font-weight:400;line-height:1.25;border-width:1px')

    def test_comments_and_recovery(self):
        self.assertEqual(filter_style('bad;\r\n color:/**/#abc; font-size:1/**/rem; padding-top:0;'), 'color:#abc;padding-top:0')

    def test_multiple_values_and_colors(self):
        self.assertEqual(filter_style('color:transparent;background-color:transparent;border-color:#12345678;text-decoration-line:underline line-through;margin:0'), 'background-color:transparent')

    def test_surrogates_do_not_change_following_declaration_coordinates(self):
        for surrogate in ('\ud800', '\udfff'):
            self.assertEqual(filter_style('color:#a'+surrogate+'bc;\r\nfont-size:1rem;color:#123'), 'font-size:1rem;color:#123')
    def test_hash_escapes_match_decoded_hex_only(self):
        self.assertEqual(filter_style(r'color:#a\62 c;border-color:#12\33 456'), 'color:#abc;border-color:#123456')
        self.assertEqual(filter_style(r'color:#a\67 c;color:#12345678'), '')

    def test_rebuilt_values(self):
        result = filter_style(r'font-style:it\61lic;color:#aBc;white-space:PRE-WRAP')
        self.assertEqual(result, 'font-style:italic;color:#abc;white-space:pre-wrap')
        self.assertEqual(filter_style(result), result)


if __name__ == '__main__':
    unittest.main()
