import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import language_tags as tags

class LanguageTagTests(unittest.TestCase):
    def test_registered_and_deprecated(self):
        for value in ('en', 'EN-us', 'sr-Latn-RS', 'es-419', 'sl-rozaj-biske-1994', 'de-CH-1901', 'iw', 'en-BU', 'i-klingon', 'en-GB-oed', 'sgn-BE-FR'):
            self.assertTrue(tags.validate_language_tag(value).valid, value)

    def test_all_grandfathered(self):
        values = tags._registry()[2]
        self.assertEqual(len(values), 26)
        for value in values:
            self.assertTrue(tags.validate_language_tag(value.upper()).valid, value)

    def test_private_use_and_ranges(self):
        for value in ('x-whatever', 'x-a', 'en-x-US', 'en-x-a-a', 'qaa-Qaaa-QM', 'qtz-Qabx-ZZ', 'de-AA', 'de-QZ', 'de-XA', 'de-XZ', 'en-XX'):
            self.assertTrue(tags.validate_language_tag(value).valid, value)
        for value in ('x', 'en-x', 'qzz', 'en-Qaby', 'en-QQQ'):
            self.assertFalse(tags.validate_language_tag(value).valid, value)

    def test_extlangs(self):
        for value in ('zh-cmn', 'zh-yue-Hant-HK', 'sgn-ase', 'cmn-Hans-CN'):
            self.assertTrue(tags.validate_language_tag(value).valid, value)
        for value in ('en-cmn', 'zh-cmn-yue', 'zh-cmn-yue-gan', 'zh-qqq'):
            self.assertFalse(tags.validate_language_tag(value).valid, value)

    def test_extensions(self):
        for value in ('en-u-ca-gregory', 'en-t-en-us', 'en-t-en-u-ca-gregory', 'en-u-zzzzzzzz', 'en-u-ca-x-u-ca'):
            result = tags.validate_language_tag(value)
            self.assertTrue(result.valid, value)
            self.assertFalse(result.extension_contents_checked)
            self.assertFalse(result.canonicalization_performed)
        for value in ('en-a-hello', 'en-u', 'en-u-t-en', 'en-u-ca-U-nu', 'en-0-hello'):
            self.assertFalse(tags.validate_language_tag(value).valid, value)

    def test_variants_and_plausibility(self):
        for value in ('de-1901-1901', 'sl-ROZAJ-rozaj'):
            self.assertFalse(tags.validate_language_tag(value).valid, value)
        # Variant Prefix is guidance, not a universal validity prohibition.
        self.assertTrue(tags.validate_language_tag('en-rozaj').valid)
        self.assertTrue(tags.validate_language_tag('ar-Cyrl-CO').valid)

    def test_malformed_and_unknown(self):
        for value in (' en', 'en ', 'en\n', 'en_US', 'en--US', 'en-', '-en', 'e', 'en-abcdefghi', 'é', 'en-İN', 'en–US', 'notalang', 'en-UK', 'de-419-DE', 'en-US-Latn', 'en-unknown', 'en-u-foo-', None, 123):
            self.assertFalse(tags.validate_language_tag(value).valid, repr(value))

    def test_empty_attribute(self):
        self.assertFalse(tags.validate_language_tag('').valid)
        self.assertTrue(tags.validate_lang_attribute('').valid)
        self.assertFalse(tags.validate_lang_attribute(' ').valid)

    def test_no_arbitrary_limit_or_canonicalization(self):
        value = 'EN-x-' + '-'.join(['private'] * 80)
        self.assertGreater(len(value), 35)
        self.assertTrue(tags.validate_language_tag(value).valid)
        self.assertTrue(value.startswith('EN-x-'))
        self.assertTrue(tags.validate_language_tag('en-u-nu-latn-t-en').valid)

    def test_manifest_and_corruption(self):
        manifest = tags.registry_versions()
        self.assertEqual([d['file_date'] for d in manifest['datasets']], ['2026-09-17', '2014-04-02'])
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)
            (path / 'manifest.json').write_text(json.dumps(manifest))
            for entry in manifest['datasets']:
                (path / entry['file']).write_bytes((tags.DATA / entry['file']).read_bytes() + b'\n')
            tags._registry.cache_clear()
            try:
                with patch.object(tags, 'DATA', path):
                    with self.assertRaisesRegex(ValueError, 'digest mismatch'):
                        tags.validate_language_tag('en')
            finally:
                tags._registry.cache_clear()

    def test_registry_reader(self):
        records = list(tags._records('Type: variant\r\nDescription: one\r\n continued\r\nDescription: two\r\n%%\r\n'))
        self.assertEqual(records[0]['Description'], ['one continued', 'two'])

if __name__ == '__main__':
    unittest.main()
