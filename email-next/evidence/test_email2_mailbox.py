"""Spelling/equality cases, not mailbox ownership, headers or SMTP delivery."""
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from email2_mailbox import construct,validate,selected_domain,requires_smtputf8,IDNAUnavailable


class MailboxTests(unittest.TestCase):
    def test_international_local_parts_preserve_exact_unicode_and_case(self):
        for value in ['δοκιμή@example.org','用户@example.org','é@example.org','e\u0301@example.org','🙂@example.org','A+标签@example.org']:
            with self.subTest(value=value):
                self.assertEqual(validate(value),value);self.assertTrue(requires_smtputf8(value))
        self.assertNotEqual(construct('é@example.org'),construct('e\u0301@example.org'))
        self.assertNotEqual(construct('User@example.org'),construct('user@example.org'))

    def test_quoted_forms_use_one_minimal_wire_spelling(self):
        for source,expected in [('"alice"@EXAMPLE.ORG','alice@example.org'),('"a\\b"@example.org','ab@example.org'),
            ('"a b"@example.org','"a b"@example.org'),('"a@b"@example.org','"a@b"@example.org'),
            ('"a..b"@example.org','"a..b"@example.org'),('""@example.org','""@example.org'),
            ('"用户"@example.org','用户@example.org'),('"a\\"b"@example.org','"a\\"b"@example.org'),
            ('"a\\\\b"@example.org','"a\\\\b"@example.org')]:
            with self.subTest(source=source):
                self.assertEqual(construct(source),expected);self.assertEqual(validate(expected),expected)

    def test_signed_wire_rejects_repairable_noncanonical_spellings(self):
        for value in ['alice@EXAMPLE.ORG','"alice"@example.org','"a\\b"@example.org','用户@EXAMPLE.ORG']:
            with self.subTest(value=value),self.assertRaises(ValueError):validate(value)

    def test_quoted_at_is_not_the_domain_separator(self):
        value='"user@desk"@example.org'
        self.assertEqual(selected_domain(value),'example.org');self.assertFalse(requires_smtputf8(value))

    def test_invalid_bare_forms_never_become_an_address(self):
        for value in ['a..b@example.org','.a@example.org','a.@example.org','a b@example.org','a@example.org.',
            'Name <a@example.org>','a(comment)@example.org','a@[127.0.0.1]','mailto:a@example.org',
            'a@-bad.example','a@bad-.example','a@ab--cd.example','a@a..example','a@a_b.example',
            '"a"b@example.org','"a\\é"@example.org','"a\tb"@example.org','a\r\n@example.org','a\x7f@example.org',
            'a\ud800@example.org','a@\udfff.example']:
            with self.subTest(value=repr(value)),self.assertRaises(ValueError):construct(value)

    def test_local_octet_limits_count_utf8_and_required_quoting(self):
        self.assertEqual(validate('é'*32+'@example.org'),'é'*32+'@example.org')
        with self.assertRaises(ValueError):construct('é'*33+'@example.org')
        self.assertEqual(validate('"'+' '*62+'"@example.org'),'"'+' '*62+'"@example.org')
        with self.assertRaises(ValueError):construct('"'+' '*63+'"@example.org')
        self.assertEqual(validate('a'*64+'@example.org'),'a'*64+'@example.org')
        with self.assertRaises(ValueError):construct('a'*65+'@example.org')

    def test_path_limit_is_independent_of_dns_domain_limit(self):
        host='a'*63+'.'+'b'*63+'.'+'c'*61
        self.assertEqual(len(('x'*64+'@'+host).encode())+2,256)
        self.assertEqual(validate('x'*64+'@'+host),'x'*64+'@'+host)
        with self.assertRaises(ValueError):validate('x'*64+'@'+host+'d')

    def test_nonascii_controls_and_formatting_are_not_silently_rewritten(self):
        # RFC6531's UTF8-non-ascii grammar includes these; display safety is a
        # separate mandatory boundary, not permission to alter mailbox identity.
        for scalar in ['\u0085','\u200d','\u202e','\U000f0000']:
            value='a'+scalar+'@example.org';self.assertEqual(validate(value),value)
        self.assertNotEqual(construct('a\u200d@example.org'),construct('a@example.org'))

    def test_missing_idna_provider_is_unavailable_not_accepted(self):
        with patch.dict(os.environ,{},clear=True):
            for value in ['a@xn--bcher-kva.example','a@bücher.example']:
                with self.subTest(value=value),self.assertRaises(IDNAUnavailable):construct(value)
        self.assertEqual(validate('a@example.org'),'a@example.org')

    def test_smtputf8_depends_on_outer_local_part_not_a_label(self):
        self.assertFalse(requires_smtputf8('Alice+tag@example.org'))
        self.assertFalse(requires_smtputf8('"a b"@example.org'))
        self.assertTrue(requires_smtputf8('"用户 desk"@example.org'))


class ConfiguredIDNATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config=os.environ.get('EMAIL_NEXT_IDNA17_CONFIG')
        if not config:raise unittest.SkipTest('Explicit coherent Unicode17 provider not configured')
        if not Path(config).is_file():raise AssertionError('Configured provider file missing')

    def test_u_label_input_and_a_label_wire_are_same_domain(self):
        self.assertEqual(construct('用户@bücher.example'),'用户@xn--bcher-kva.example')
        self.assertEqual(validate('用户@xn--bcher-kva.example'),'用户@xn--bcher-kva.example')
        with self.assertRaises(ValueError):validate('用户@bücher.example')
        self.assertFalse(requires_smtputf8('user@xn--bcher-kva.example'))

    def test_idna_disallowed_fake_alabel_and_non_nfc_are_rejected(self):
        for host in ['xn--a.example','xn--.example','xn--bcher-kva-.example','bu\u0308cher.example','foo。example','☃.example']:
            with self.subTest(host=host),self.assertRaises(ValueError):construct('a@'+host)

    def test_whole_domain_bidi_rule_is_applied(self):
        self.assertEqual(selected_domain(construct('a@مثال.example')),'xn--mgbh0fb.example')
        with self.assertRaises(ValueError):construct('a@مثال.1abc')


if __name__=='__main__':unittest.main()
