"""Real setup/assertion9 signatures and MLS package checks; configured identity0.

No complete publication, sealed1 response, mailbox, durable handoff or UI proof.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from event_encoding import encode_event
from identity_store import IdentityStore
from provider_mls import advertisement, make_device, sign
from reply_suite import offers, exchanges
from sealed_control import native
from mail_setup1 import decode, verify, live_candidate
from mail_setup import verify as old_verify
from suite_discovery8 import verify as old_discovery
from suite_discovery9 import verify as new_discovery


def wire(value):
    return json.dumps(value, separators=(',', ':')).encode()


class MailSetup1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binary = Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR'])/'provider-mls'
        cls.a = make_device(cls.binary, 71, 72)
        cls.b = make_device(cls.binary, 73, 74)
        cls.now = max(cls.a['time'], cls.b['time'])
        cls.clock = dict(earliest=str(cls.now), latest=str(cls.now))
        cls.source_key = native(cls.binary.with_name('sealed-control'), op='generate')
        cls.target_key = native(cls.binary.with_name('sealed-control'), op='generate')

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.store = IdentityStore(Path(tmp.name)/'identity.sqlite'); self.addCleanup(self.store.close)
        for device in [self.a, self.b]:
            self.store.observe(device['record'], first_contact_policy='allow-unverified')
        self.ads = {}
        for kind, device, address, key in [('request', self.a, 'alice@example.org', self.source_key),
                                          ('response', self.b, 'bob@example.org', self.target_key)]:
            wrapper = advertisement(self.binary, device, address)
            value = json.loads(base64.b64decode(wrapper['payload']))
            expiry = self.now+120 if kind == 'request' else self.now+600
            value.update(version='9', notBefore=str(self.now), notAfter=str(self.now+120),
                         applications=offers(['answers']), orderingExchanges=exchanges(offers(['answers'])),
                         keyPackageReceiveUntil=None if kind == 'request' else str(self.now+660),
                         controlKey=dict(id=key['id'], publicKey=key['publicKey'], notBefore=str(self.now),
                                         notAfter=str(expiry), receiveUntil=str(expiry if kind == 'request' else self.now+660)))
            if kind == 'request':
                value['keyPackage'] = []
            payload = encode_event(value, nullable_members=('controlKey', 'keyPackageReceiveUntil'))
            self.ads[kind] = wire(dict(wrapper, payload=base64.b64encode(payload).decode(),
                                      signature=sign(self.binary, device, 'mail/passive-discovery/v9', payload)))
        self.request = self.record('request')

    def record(self, kind, changes=None, *, ad=None, domain=None):
        ad = self.ads[kind] if ad is None else ad
        value = dict(version='1', purpose='mailbox-setup-'+kind, agreement='mail-conversation-v1',
                     request='1'*32, nonce='2'*64, source='alice@example.org', target='bob@example.org',
                     assertion=hashlib.sha256(ad).hexdigest(), notBefore=str(self.now), notAfter=str(self.now+120))
        if kind == 'response':
            value['requestDigest'] = hashlib.sha256(base64.b64decode(json.loads(self.request)['payload'])).hexdigest()
        value.update(changes or {})
        raw = wire(value)
        signature = sign(self.binary, self.a if kind == 'request' else self.b,
                         domain or 'mail/setup-'+kind+'/v1', raw)
        return wire(dict(payload=base64.b64encode(raw).decode(), signature=signature,
                         advertisement=base64.b64encode(ad).decode()))

    def check(self, raw, kind='request', time=None):
        return verify(raw, kind, self.store, self.binary, time=self.clock if time is None else time,
                      trust_policy='allow-unverified', request=self.request if kind == 'response' else None)

    def test_actual_new_signatures_and_native_package_leave_identity_store_unchanged(self):
        before = self.store.db.total_changes
        self.assertEqual(self.check(self.request)['status'], 'mailbox-setup-candidate-only')
        result = self.check(self.record('response'), 'response')
        self.assertEqual(result['record']['agreement'], 'mail-conversation-v1')
        self.assertEqual(result['actor']['device'], self.b['device'])
        self.assertFalse(result['mailbox_verified'])
        self.assertEqual(self.store.db.total_changes, before)

    def association_observation(self, raw):
        # Synthetic trusted sole-From parser input after actual assertion/package
        # verification. This is not evidence of real mailbox ownership or mail.
        new_discovery(raw, self.store, self.binary, time=self.clock, trust_policy='allow-unverified')
        wrapper = json.loads(raw)
        payload = base64.b64decode(wrapper['payload'])
        value = json.loads(payload)
        return dict(assertion=payload, signature=bytes.fromhex(wrapper['signature']),
                    signingKey=bytes.fromhex(self.b['key']), outerFrom=[value['mailbox']],
                    sourceId='configured-ordinary-observation', parserRevision='fixture-sole-from-0',
                    observedAt=self.clock['earliest'])

    def test_reply_aware_association_preserves_unverified_and_strict_outcomes(self):
        from mailbox_association_store import MailboxAssociationStore
        associations = MailboxAssociationStore(self.store)
        raw = self.ads['response']
        item = self.association_observation(raw)
        associations.observe_validated_batch([item])
        options = dict(mailbox='bob@example.org', expected_generation=None, kind='first-contact',
                       principal=self.b['principal'], actor='configured-policy', policy_revision='configured-0',
                       trust_policy='require-verification', time=self.clock)
        result = associations.decide(decision_id='3'*32, **options)
        self.assertEqual(result['status'], 'verification-required')
        self.assertIsNone(associations.snapshot('bob@example.org')['association'])
        result = associations.decide(decision_id='4'*32, **dict(options, trust_policy='allow-unverified'))
        self.assertEqual(result['status'], 'associated-unverified')
        self.assertFalse(result['sendAuthorized'])
        self.assertEqual(result['generation'], '1')

    def test_protocol_version_does_not_reset_authenticated_record_collision(self):
        from mailbox_association_store import MailboxAssociationStore
        from suite_modules import offers as old_offers, exchanges as old_exchanges
        associations = MailboxAssociationStore(self.store)
        raw = self.ads['response']
        item = self.association_observation(raw)
        associations.observe_validated_batch([item])
        options = dict(mailbox='bob@example.org', expected_generation=None, kind='first-contact',
                       principal=self.b['principal'], actor='configured-policy', policy_revision='configured-0',
                       trust_policy='allow-unverified', time=self.clock)
        associations.decide(decision_id='5'*32, **options)
        wrapper = json.loads(raw)
        value = json.loads(base64.b64decode(wrapper['payload']))
        value.update(version='8', applications=old_offers(), orderingExchanges=old_exchanges(old_offers()))
        payload = encode_event(value, nullable_members=('controlKey', 'keyPackageReceiveUntil'))
        old = wire(dict(wrapper, payload=base64.b64encode(payload).decode(),
                        signature=sign(self.binary, self.b, 'email-next/passive-discovery/v8', payload)))
        old_discovery(old, self.store, self.binary, time=self.clock, trust_policy='allow-unverified')
        older = dict(item, assertion=payload, signature=bytes.fromhex(json.loads(old)['signature']),
                     sourceId='configured-older-observation')
        associations.observe_validated_batch([older])
        self.store.db.execute('BEGIN IMMEDIATE')
        try:
            for data in (item['assertion'], payload):
                self.assertIsNone(associations.eligible_observation_locked(
                    'bob@example.org', hashlib.sha256(data).hexdigest(), self.clock))
        finally:
            self.store.db.execute('ROLLBACK')
        selected = associations.snapshot('bob@example.org')['association']
        self.assertEqual((selected['principal'], selected['generation']), (self.b['principal'], '1'))
        self.assertEqual(self.store.check_device(bytes.fromhex(self.b['identity']),
                         bytes.fromhex(self.b['key']), role='receive', time=self.clock,
                         trust_policy='allow-unverified')['status'], 'authorized-unverified')

    def test_old_setup_and_old_discovery_do_not_accept_successor(self):
        with self.assertRaises(ValueError):
            old_verify(self.request, 'request', self.store, self.binary, time=self.clock, trust_policy='allow-unverified')
        with self.assertRaises(ValueError):
            old_discovery(self.ads['response'], self.store, self.binary, time=self.clock, trust_policy='allow-unverified')
        for changes in [dict(version='0'), dict(agreement='email2-conversation-v0'), dict(agreement='future')]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.check(self.record('request', changes))

    def test_domain_and_original_payload_changes_are_rejected(self):
        for kind in ['request', 'response']:
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.check(self.record(kind, domain='mail/setup-'+kind+'/v0'), kind)
        wrapper = json.loads(self.request)
        wrapper['payload'] = base64.b64encode(b' '+base64.b64decode(wrapper['payload'])).decode()
        with self.assertRaises(ValueError):
            self.check(wire(wrapper))

    def test_exact_response_correlation_cannot_select_another_agreement_or_attempt(self):
        for changes in [dict(agreement='email2-conversation-v0'), dict(nonce='4'*64),
                        dict(request='3'*32), dict(requestDigest='5'*64), dict(target='other@example.org')]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.check(self.record('response', changes), 'response')

    def test_attempt_deadline_cannot_be_extended_by_new_version_or_response(self):
        with self.assertRaises(ValueError):
            self.check(self.request, time=dict(earliest=str(self.now+121), latest=str(self.now+121)))
        with self.assertRaises(ValueError):
            self.check(self.record('response', dict(notAfter=str(self.now+121))), 'response')

    def test_assertion9_has_distinct_original_signature_and_exact_offer_branch(self):
        wrapper = json.loads(self.ads['response'])
        payload = base64.b64decode(wrapper['payload'])
        wrapper['signature'] = sign(self.binary, self.b, 'email-next/passive-discovery/v8', payload)
        with self.assertRaises(ValueError):
            self.check(self.record('response', ad=wire(wrapper)), 'response')
        value = json.loads(payload); value['applications'][0]['envelopeVersion'] = '4'
        raw = encode_event(value, nullable_members=('controlKey', 'keyPackageReceiveUntil'))
        wrapper.update(payload=base64.b64encode(raw).decode(),
                       signature=sign(self.binary, self.b, 'mail/passive-discovery/v9', raw))
        with self.assertRaises(ValueError):
            self.check(self.record('response', ad=wire(wrapper)), 'response')

    def test_advertisement_commitment_empty_request_and_response_package_are_independent(self):
        for kind, ad in [('request', self.ads['response']), ('response', self.ads['request'])]:
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.check(self.record(kind, ad=ad), kind)
        with self.assertRaises(ValueError):
            self.check(self.record('request', dict(assertion='6'*64)))
        candidate = new_discovery(self.ads['response'], self.store, self.binary,
                                  time=self.clock, trust_policy='allow-unverified')
        self.assertTrue(candidate['mls_validated'])

    def test_unknown_identity_and_strict_verification_still_hold_assertion9(self):
        before = self.store.db.total_changes
        result = new_discovery(self.ads['response'], self.store, self.binary,
                               time=self.clock, trust_policy='require-verification')
        self.assertEqual(result['status'], 'verification-required')
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        unknown = IdentityStore(Path(tmp.name)/'unknown.sqlite'); self.addCleanup(unknown.close)
        result = new_discovery(self.ads['response'], unknown, self.binary,
                               time=self.clock, trust_policy='allow-unverified')
        self.assertEqual(result['status'], 'pending')
        self.assertEqual(self.store.db.total_changes, before)

    def live(self, raw=None, **changes):
        options=dict(time=self.clock, started=self.clock, maximum_age=5,
                     expected_source={k:self.a[k] for k in ('principal','device')},
                     expected_target={k:self.b[k] for k in ('principal','device')})
        options.update(changes)
        return live_candidate(self.record('response') if raw is None else raw,
                              self.request,self.store,self.binary,**options)

    def test_mailbox_live_candidate_uses_original_age_and_exact_selected_devices(self):
        before=self.store.db.total_changes
        result=self.live()
        self.assertEqual(result['status'],'mailbox-live-response-candidate-only')
        self.assertFalse(result['mailbox_verified'])
        boundary=dict(earliest=str(self.now+5),latest=str(self.now+5))
        self.assertEqual(self.live(time=boundary)['responseDigest'],result['responseDigest'])
        with self.assertRaisesRegex(ValueError,'age window'):
            self.live(time=dict(earliest=str(self.now+6),latest=str(self.now+6)))
        with self.assertRaisesRegex(ValueError,'source/target'):
            self.live(expected_target={k:self.a[k] for k in ('principal','device')})
        with self.assertRaises(ValueError):
            self.live(self.record('response',dict(nonce='f'*64)))
        self.assertEqual(self.store.db.total_changes,before)

    def test_cached_setup_can_survive_head_advance_but_old_live_response_cannot(self):
        response=self.record('response')
        old=self.b['record']
        state=json.loads(base64.b64decode(old['state']))
        changed=dict(state,record='e'*32,revision='1',previous=[self.b['state']])
        raw=encode_event(changed)
        bundle=dict(version='0',purpose='identity-bundle',principal=self.b['principal'],
                    states=[dict(payload=base64.b64encode(raw).decode(),
                                 signature=sign(self.binary,self.b,'email-next/identity-state/v0',raw)),
                            dict(payload=old['state'],signature=old['stateProof'])],
                    bindings=[dict(payload=old['binding'],authorization=old['authorization'],
                                   possession=old['possession'])])
        head=hashlib.sha256(raw).hexdigest()
        self.assertEqual(self.store.accept_successor(encode_event(bundle),candidate_digest=head,
                         time=self.clock)['status'],'accepted-unverified')
        self.assertEqual(self.check(response,'response')['status'],'mailbox-setup-candidate-only')
        with self.assertRaisesRegex(ValueError,'exact current target head'):
            self.live(response)

    def test_mailbox_live_candidate_rejects_unreliable_or_implicit_age_inputs(self):
        for value in [None,0,-1,True,1.5,2**64]:
            with self.subTest(value=value),self.assertRaises(ValueError):
                self.live(maximum_age=value)
        for started in [None,{},dict(self.clock,extra='0'),
                        dict(earliest=str(self.now),latest=str(self.now+1)),
                        dict(earliest=str(self.now+1),latest=str(self.now))]:
            with self.subTest(started=started),self.assertRaises(ValueError):
                self.live(started=started)

    def test_exact_members_duplicate_fields_and_original_bytes(self):
        for changes in [dict(extra='x'), dict(purpose='provider-account-link')]:
            with self.assertRaises(ValueError):
                self.check(self.record('request', changes))
        with self.assertRaises(ValueError):
            decode(self.request[:-1]+b',"signature":"'+b'0'*128+b'"}', 'request')
        _, raw, _, original, _ = decode(self.request, 'request')
        self.assertEqual(original, self.ads['request'])
        self.assertEqual(raw, base64.b64decode(json.loads(self.request)['payload']))


if __name__ == '__main__':
    unittest.main()
