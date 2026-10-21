"""Discovery is location authority, never a device pin or queue credential."""
from dataclasses import replace
import copy
import json
from pathlib import Path
import tempfile
import unittest

from provider_discovery import (CALLBACKS, SCOPES, DelegationStore, FetchFacts, descriptor,
                                metadata, registration_request, registration_response)


def wire(value):
    return json.dumps(value, separators=(',', ':')).encode()


class ProviderDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'delegations.sqlite'
        self.store = DelegationStore(self.path)
        self.addCleanup(self.store.close)
        self.value = dict(version='0', purpose='provider-service-discovery', domain='example.org',
                          publication='a' * 32, generation='1', service='https://mail.example',
                          controlPrefix='https://mail.example/control/', managementPrefix='https://mail.example/manage/',
                          notBefore='10', notAfter='100')
        self.facts = FetchFacts('https://example.org/.well-known/email2-provider')
        self.meta = dict(issuer='https://mail.example', authorization_endpoint='https://mail.example/authorize',
                         token_endpoint='https://mail.example/token', registration_endpoint='https://mail.example/register',
                         revocation_endpoint='https://mail.example/revoke', authorization_response_iss_parameter_supported=True,
                         response_types_supported=['code'], grant_types_supported=['authorization_code', 'refresh_token'],
                         token_endpoint_auth_methods_supported=['none'], code_challenge_methods_supported=['S256'],
                         scopes_supported=SCOPES[:])
        self.meta_facts = FetchFacts('https://mail.example/.well-known/oauth-authorization-server')

    def accept(self, value=None, **kwargs):
        return self.store.accept(wire(value or self.value), 'example.org', self.facts, time=(20, 21),
                                 expected_decision=kwargs.pop('expected_decision', None),
                                 setup_authorized=kwargs.pop('setup_authorized', True),
                                 confirmed_service=kwargs.pop('confirmed_service', 'https://mail.example'), **kwargs)

    def test_first_setup_durable_retry_restart_and_no_authority_effects(self):
        accepted = self.accept()
        self.assertEqual(accepted['decision'], 1)
        self.assertEqual(self.accept(expected_decision=1), accepted)
        peer = DelegationStore(self.path)
        self.addCleanup(peer.close)
        self.assertEqual(peer.snapshot('example.org'), accepted)
        tables = {x[0] for x in peer.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertEqual(tables, {'pd_current', 'pd_decisions'})
        self.assertNotIn(b'alice@', accepted['raw'])

    def test_recipient_setup_never_becomes_account_signin_authority(self):
        result = self.accept(purpose='recipient-bootstrap', confirmed_service=None)
        self.assertEqual(result['decision'], 1)
        self.assertIsNone(self.store.snapshot('example.org'))
        self.assertEqual(self.store.snapshot('example.org', 'recipient-bootstrap'), result)
        with self.assertRaises(ValueError):
            self.accept(confirmed_service=None)
        with self.assertRaises(ValueError):
            metadata(wire(self.meta), self.value, self.meta_facts, purpose='recipient-bootstrap')
        with self.assertRaises(ValueError):
            self.accept(purpose='from-incoming-email')

    def test_first_setup_requires_current_local_permission_and_origin_confirmation(self):
        for options in [dict(setup_authorized=False), dict(confirmed_service=None), dict(confirmed_service='https://other.example')]:
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.accept(**options)
        self.assertIsNone(self.store.snapshot('example.org'))

    def test_fetch_facts_cannot_redirect_change_origin_or_supply_ambient_credentials(self):
        changes = [dict(url='https://mail.example/.well-known/email2-provider'), dict(status=302),
                   dict(tls_authenticated=False), dict(redirected=True), dict(network_allowed=False),
                   dict(ambient_credentials=True), dict(no_store=False), dict(content_type='text/html'), dict(content_coding='gzip')]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                descriptor(wire(self.value), 'example.org', replace(self.facts, **change), time=(20, 21))
        with self.assertRaises(ValueError):
            descriptor(wire(self.value), 'example.org', self.facts.__dict__, time=(20, 21))

    def test_selected_domain_and_descriptor_agree_exactly(self):
        for domain in ['Example.org', 'example.org.', '127.0.0.1', 'example.org:443', 'example.org/route', 'elsewhere.example']:
            with self.subTest(domain=domain), self.assertRaises(ValueError):
                descriptor(wire(self.value), domain, self.facts, time=(20, 21))
        with self.assertRaises(ValueError):
            descriptor(wire(dict(self.value, domain='elsewhere.example')), 'example.org', self.facts, time=(20, 21))

    def test_descriptor_strict_schema_counters_and_intervals(self):
        variants = [dict(generation='0'), dict(generation='01'), dict(generation=1), dict(generation=str(2**64)),
                    dict(publication='0' * 32), dict(notAfter='19'), dict(notBefore='22'), dict(extra='x'), dict(service=None)]
        for change in variants:
            with self.subTest(change=change), self.assertRaises(ValueError):
                descriptor(wire(dict(self.value, **change)), 'example.org', self.facts, time=(20, 21))
        for time in [(20, 101), (21, 20), (True, 21), None]:
            with self.subTest(time=time), self.assertRaises(ValueError):
                descriptor(wire(self.value), 'example.org', self.facts, time=time)

    def test_canonical_same_origin_nonoverlapping_prefixes(self):
        for change in [dict(service='https://mail.example:443'), dict(controlPrefix='https://evil.example/control/'),
                       dict(controlPrefix='https://mail.example/a/../control/'), dict(controlPrefix='https://mail.example/manage/child/'),
                       dict(controlPrefix=self.value['managementPrefix']), dict(controlPrefix='https://mail.example/control/?q=x')]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                descriptor(wire(dict(self.value, **change)), 'example.org', self.facts, time=(20, 21))

    def test_conflict_and_rollback_preserve_accepted_bytes(self):
        old = self.accept()
        for value in [dict(self.value, notAfter='99'), dict(self.value, generation='0')]:
            with self.assertRaises(ValueError):
                self.accept(value, expected_decision=1)
            self.assertEqual(self.store.snapshot('example.org'), old)
        self.accept(dict(self.value, generation='3'), expected_decision=1)
        with self.assertRaises(ValueError):
            self.accept(expected_decision=2)
        self.assertEqual(json.loads(self.store.snapshot('example.org')['raw'])['generation'], '3')

    def test_new_origin_requires_confirmation_and_never_reuses_prior_configuration(self):
        self.accept()
        value = dict(self.value, generation='5', service='https://new.example',
                     controlPrefix='https://new.example/control/', managementPrefix='https://new.example/manage/')
        with self.assertRaises(ValueError):
            self.accept(value, expected_decision=1)
        accepted = self.accept(value, expected_decision=1, confirmed_service='https://new.example')
        self.assertEqual(json.loads(accepted['raw']), value)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM pd_decisions').fetchone()[0], 2)

    def test_publication_reset_is_explicit_and_keeps_old_decision(self):
        old = self.accept()
        new = dict(self.value, publication='b' * 32)
        with self.assertRaises(ValueError):
            self.accept(new, expected_decision=1)
        self.assertEqual(self.store.snapshot('example.org'), old)
        self.assertEqual(self.accept(new, expected_decision=1, reset=True)['decision'], 2)
        with self.assertRaises(ValueError):
            self.accept(new, expected_decision=2, reset=True)

    def test_two_connections_cannot_accept_stale_local_decision(self):
        self.accept()
        peer = DelegationStore(self.path)
        self.addCleanup(peer.close)
        retained = peer.snapshot('example.org')
        self.accept(dict(self.value, generation='2'), expected_decision=1)
        with self.assertRaises(ValueError):
            peer.accept(wire(dict(self.value, generation='3')), 'example.org', self.facts, time=(20, 21),
                        expected_decision=retained['decision'], setup_authorized=True)
        self.assertEqual(peer.snapshot('example.org')['decision'], 2)

    def test_duplicate_names_bytes_depth_and_invalid_unicode(self):
        for raw in [b'{"domain":"a","\\u0064omain":"b"}', b'{"x":NaN}', b'{"x":"\\ud800"}', b'\xff', b' ' * 65537,
                    wire({'x': [[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]})]:
            with self.subTest(raw=raw[:30]), self.assertRaises((ValueError, UnicodeError)):
                descriptor(raw, 'example.org', self.facts, time=(20, 21))

    def test_expired_fetch_never_erases_high_water_mark(self):
        self.accept()
        with self.assertRaises(ValueError):
            self.store.accept(wire(dict(self.value, generation='2')), 'example.org', self.facts, time=(101, 102),
                              expected_decision=1, setup_authorized=True)
        self.assertEqual(self.store.snapshot('example.org')['decision'], 1)

    def test_metadata_supports_selected_flow_without_adopting_unrelated_endpoints(self):
        value = dict(self.meta, response_types_supported=['code', 'code id_token'], jwks_uri='https://unrelated.example/keys', custom_extension={'ignored': True})
        self.assertEqual(metadata(wire(value), self.value, self.meta_facts), value)
        for key in ['response_types_supported', 'grant_types_supported', 'token_endpoint_auth_methods_supported', 'code_challenge_methods_supported', 'scopes_supported']:
            with self.subTest(key=key), self.assertRaises(ValueError):
                metadata(wire(dict(self.meta, **{key: []})), self.value, self.meta_facts)

    def test_metadata_exact_issuer_endpoints_pkce_and_issuer_response_defense(self):
        for change in [dict(issuer='https://other.example'), dict(token_endpoint='https://other.example/token'),
                       dict(code_challenge_methods_supported=['plain']), dict(authorization_response_iss_parameter_supported=1),
                       dict(registration_endpoint=self.meta['token_endpoint']), dict(scopes_supported=SCOPES + SCOPES),
                       dict(scopes_supported=' '.join(SCOPES))]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                metadata(wire(dict(self.meta, **change)), self.value, self.meta_facts)

    def test_registration_keeps_exact_native_hosts_paths_scopes_and_public_client(self):
        response = dict(registration_request(), client_id='native-public-123', client_id_issued_at=20)
        facts = FetchFacts(self.meta['registration_endpoint'], status=201)
        self.assertEqual(registration_response(wire(response), self.meta, facts), response)
        self.assertEqual(response['redirect_uris'], CALLBACKS)
        value = dict(response, scope=' '.join(SCOPES[::-1]), ignored_extension='https://elsewhere.example/')
        self.assertEqual(registration_response(wire(value), self.meta, facts), value)
        for change in [dict(client_id=''), dict(client_id_issued_at=True), dict(scope=SCOPES[0]),
                       dict(scope=' '.join(SCOPES + SCOPES)), dict(token_endpoint_auth_method='client_secret_basic'),
                       dict(redirect_uris=['http://localhost:1/email2/provider/callback'])]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                registration_response(wire(dict(response, **change)), self.meta, facts)
        for member in ['client_secret', 'client_secret_expires_at', 'registration_access_token', 'registration_client_uri']:
            with self.subTest(member=member), self.assertRaises(ValueError):
                registration_response(wire(dict(response, **{member: 'x'})), self.meta, facts)
        with self.assertRaises(ValueError):
            registration_response(wire(response), self.meta, replace(facts, status=200))


if __name__ == '__main__':
    unittest.main()
