"""Wire vectors only; no token/link/cursor authentication or host effects."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from event_encoding import encode_event
from hosted_public_wire import create_request, feed_page


class PublicHostedWireTests(unittest.TestCase):
    def setUp(self):
        self.examples = json.loads(Path(__file__).with_name('hosted-public-examples.json').read_text())
        self.req = self.examples['create']
        self.owner = self.req['ownerBinding']
        self.principal = self.req['contribution']['principal']
        self.service = self.examples['replyPages'][0]['service']

    def create(self, value=None, **expected):
        return create_request(encode_event(self.req if value is None else value),
                              **(dict(owner=self.owner, principal=self.principal) | expected))

    def page(self, value, **expected):
        return feed_page(encode_event(value), **(dict(service=self.service, collection='replies',
                         owner=self.owner, grant=self.req['grant']) | expected))

    def test_original_create_bytes_preserved_not_reserialized_as_v1(self):
        raw = json.dumps(self.req, indent=2).encode()
        result = create_request(raw, owner=self.owner, principal=self.principal)
        self.assertEqual(result['status'], 'wire-only')
        self.assertIs(result['original'], raw)
        self.assertEqual(result['value']['version'], '2')

    def test_example_receipts_bind_actual_original_holder_requests(self):
        for page, raw in zip(self.examples["replyPages"], self.examples["holderRequests"]):
            receipt = page["items"][0]
            self.assertEqual(receipt["requestDigest"], hashlib.sha256(raw.encode()).hexdigest())
            self.assertEqual(receipt["operation"], json.loads(raw)["operation"])

    def test_owner_and_principal_are_independently_expected(self):
        for expected in (dict(owner='f'*64), dict(principal='enp0:'+'e'*64)):
            with self.subTest(expected=expected), self.assertRaises(ValueError):
                self.create(**expected)

    def test_create_rejects_legacy_or_malformed_link_and_bounds(self):
        for update in (dict(version='1'), dict(generation='0'), dict(generation='01'),
                       dict(generation=str(2**64)), dict(link='0'*32),
                       dict(replyTextLimit='2'), dict(ownerBinding='0'*64),
                       dict(content={'kind':'html','text':'<b>Hello</b>'}),
                       dict(recipient='https://callback.example/'), dict(extra='ignored')):
            with self.subTest(update=update), self.assertRaises(ValueError):
                self.create(self.req | update)

    def test_two_pages_have_no_completed_checkpoint_until_final(self):
        first, last = [self.page(p)['value'] for p in self.examples['replyPages']]
        self.assertEqual(first['checkpoint'], '')
        self.assertEqual(last['next'], '')
        self.assertTrue(last['checkpoint'])
        self.assertNotEqual(first['items'][0]['operation'], last['items'][0]['operation'])

    def test_page_correlation_cannot_move_records_to_another_account_or_grant(self):
        page = self.examples['replyPages'][0]
        for update in (dict(service='https://other.example'), dict(ownerBinding='f'*64), dict(grant='e'*32)):
            with self.subTest(update=update), self.assertRaises(ValueError):
                self.page(page | update)
        changed = copy.deepcopy(page); changed['items'][0]['grant'] = 'e'*32
        with self.assertRaises(ValueError): self.page(changed)

    def test_holder_reply_never_becomes_authenticated_person(self):
        page = copy.deepcopy(self.examples['replyPages'][0])
        page['items'][0]['attribution'] = 'verified-recipient'
        with self.assertRaises(ValueError): self.page(page)

    def test_feed_rejects_ambiguous_completion_and_bad_tokens(self):
        page = self.examples['replyPages'][0]
        for update in (dict(checkpoint='premature'),dict(next='',checkpoint=''),
                       dict(next='has space'),dict(next='\n'),dict(next='é'),
                       dict(next='x'*2049),dict(items={}),dict(credential='secret')):
            with self.subTest(update=update), self.assertRaises(ValueError): self.page(page | update)

    def test_empty_finished_feed_is_valid_not_absence_assurance(self):
        page = self.examples['replyPages'][1] | dict(items=[])
        self.assertEqual(self.page(page)['status'], 'wire-only')

    def test_owner_and_grant_collections_are_distinct_shapes(self):
        base = dict(version='1', service=self.service, next='', checkpoint='complete')
        owners = base | dict(purpose='hosted-owner-index',items=[dict(ownerBinding=self.owner,principal=self.principal)])
        self.assertEqual(feed_page(encode_event(owners),service=self.service,collection='owners')['status'],'wire-only')
        grants = base | dict(purpose='hosted-grant-index',ownerBinding=self.owner,items=[{key:self.req[key] for key in ('grant','contribution','expiry')} | dict(state='revoked')])
        self.assertEqual(feed_page(encode_event(grants),service=self.service,collection='grants',owner=self.owner)['status'],'wire-only')
        with self.assertRaises(ValueError): self.page(grants)

    def test_duplicate_fields_and_transport_bounds_apply_before_shape(self):
        raw = encode_event(self.req)
        for changed in (b'{"version":"2",'+raw[1:], b' '*1048577):
            with self.assertRaises(ValueError): create_request(changed,owner=self.owner,principal=self.principal)


if __name__ == '__main__': unittest.main()
