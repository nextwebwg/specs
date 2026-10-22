"""Real new record/assertion signatures with caller-selected actors only.

Package bytes and route invitations are deliberately inert fixture markers;
no identity acceptance, account truth, MLS, service state or URL access is proved.
"""
import base64
import copy
import hashlib
import unittest
from bootstrap1_wire import (AGREEMENT, frame, parse, verify_candidate,
                             descriptor_candidate, handle, correlate_response)
from bootstrap_exchange import parse as old_parse, handle as old_handle
from event_encoding import encode_event
from reply_suite import offers, exchanges
from test_history_transfer import identity_material


def b64(raw):
    return base64.b64encode(raw).decode()


def ad(material, actor, mailbox, *, package=False, domain=b'mail/passive-discovery/v9\0'):
    value = dict(version='9', purpose='passive-discovery', record='1'*32,
                 **{k: actor[k] for k in ['principal', 'device', 'state', 'binding']},
                 mailbox=mailbox, notBefore='10', notAfter='100', features=['mls-1-0001'],
                 applications=offers(), orderingExchanges=exchanges(offers()),
                 keyPackage=[b64(b'inert package marker')] if package else [],
                 keyPackageReceiveUntil='110' if package else None,
                 controlKey=dict(id='2'*32, publicKey='3'*64, notBefore='10',
                                 notAfter='100', receiveUntil='110'))
    raw = encode_event(value, nullable_members=('controlKey', 'keyPackageReceiveUntil'))
    return b64(encode_event(dict(payload=b64(raw), signature=material['target'].sign(
        domain+len(raw).to_bytes(4, 'big')+raw).hex(), identity=material['bundle'])))


class Bootstrap1WireTests(unittest.TestCase):
    def setUp(self):
        self.a = identity_material('enp0:'+'a'*64); self.b = identity_material('enp0:'+'b'*64)
        self.source_actor = self.a['refs'][1]; self.target_actor = self.b['refs'][1]
        self.descriptor = dict(version='1', purpose='bootstrap-service-discovery', agreement=AGREEMENT,
                               domain='recipient.example', publication='1'*32, generation='1',
                               service='https://destination.example', managementPrefix='https://destination.example/manage1/',
                               sourcePrefix='https://destination.example/source1/', exchangePrefix='https://destination.example/exchange1/',
                               roles=['respond-target'], notBefore='10', notAfter='100')
        self.descriptor_bytes = encode_event(self.descriptor)
        common = dict(version='1', agreement=AGREEMENT, issuer='https://source.example',
                      notBefore='10', notAfter='90')
        self.source = dict(common, purpose='bootstrap-source', preparation='2'*32, request='3'*32,
                           source='4'*64, delegation='5'*64, accountSource='6'*64,
                           senderMailbox='alice@sender.example', sender=self.source_actor,
                           targetMailbox='bob@recipient.example', targetService='https://destination.example',
                           targetDelegation=hashlib.sha256(self.descriptor_bytes).hexdigest(),
                           conversation='7'*32, advertisement=ad(self.a, self.source_actor, 'alice@sender.example'),
                           nonce='8'*64)
        self.source_proof = self.sign('source', self.source)
        digest = hashlib.sha256(parse(self.source_proof, 'source')[0]).hexdigest()
        shared = dict(common, issuer=self.source['targetService'], exchange=handle(self.source), sourceDigest=digest,
                      nonce=self.source['nonce'])
        self.response = dict(shared, purpose='bootstrap-response', response='9'*32,
                             mailbox=self.source['targetMailbox'], device=self.target_actor,
                             advertisement=ad(self.b, self.target_actor, self.source['targetMailbox'], package=True),
                             relayDomain='')
        self.values = dict(source=self.source, response=self.response,
                           inspect=dict(shared, purpose='bootstrap-inspect'),
                           cancel=dict(shared, purpose='bootstrap-cancel'),
                           publication=dict(common, issuer=self.source['targetService'], purpose='bootstrap-publication',
                                            publication='9'*32, mailbox=self.source['targetMailbox'], device=self.target_actor,
                                            advertisement=self.response['advertisement'], relayDomain='', scope='automatic-first-contact'),
                           **{'route-request':dict(shared, purpose='bootstrap-route-request', request='a'*32,
                                                  recipient=self.target_actor, relayDomain='', sourceDomain='sender.example',
                                                  sourceService='https://source.example', sourcePermission='b'*64, permissionDigest='c'*64),
                              'route-response':dict(shared, purpose='bootstrap-route-response', response='d'*32,
                                                   requestDigest='e'*64, device=self.target_actor, relayDomain='',
                                                   invitation=b64(b'inert route marker'))})

    def actor(self, kind):
        return self.target_actor if kind in ['response', 'publication', 'route-response'] else self.source_actor

    def sign(self, kind, value, *, domain=None, raw=None):
        raw = encode_event(value) if raw is None else raw
        key = self.b['target'] if kind in ['response', 'publication', 'route-response'] else self.a['target']
        message = frame(kind, raw) if domain is None else domain+b'\0'+len(raw).to_bytes(4, 'big')+raw
        return encode_event(dict(payload=b64(raw), signature=key.sign(message).hex()))

    def check(self, kind, value=None, **kwargs):
        return verify_candidate(self.sign(kind, self.values[kind] if value is None else value), kind,
                                self.actor(kind), time=kwargs.get('time', (20, 21)))

    def correlate(self, response=None, descriptor=None):
        return correlate_response(self.source_proof, self.sign('response', self.response if response is None else response),
                                  self.source_actor, self.target_actor,
                                  self.descriptor_bytes if descriptor is None else descriptor, time=(20, 21))

    def test_all_seven_signed_kinds_keep_original_bytes_without_package_or_service_authority(self):
        for kind in self.values:
            with self.subTest(kind=kind):
                result = self.check(kind)
                self.assertEqual(result['state'], 'candidate-bootstrap1-proof')
                self.assertFalse(result['package_validated'])
                self.assertEqual(result['original_payload'], encode_event(self.values[kind]))

    def test_response_binds_original_source_and_target_descriptor(self):
        self.assertEqual(self.correlate()['record']['device'], self.target_actor)
        self.assertNotEqual(handle(self.source), old_handle(self.source))

    def test_changed_valid_target_descriptor_cannot_replace_original_permission_scope(self):
        changed = dict(self.descriptor, generation='2')
        descriptor_candidate(encode_event(changed), domain='recipient.example', time=(20, 21))
        with self.assertRaises(ValueError):
            self.correlate(descriptor=encode_event(changed))

    def test_valid_resigned_wrong_attempt_or_destination_never_correlates(self):
        for changes in [dict(nonce='a'*64), dict(sourceDigest='b'*64), dict(exchange='c'*64),
                        dict(issuer='https://other.example'), dict(mailbox='other@recipient.example'),
                        dict(notAfter='91')]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.correlate(dict(self.response, **changes))

    def test_old_profile_wrong_agreement_extra_and_missing_fields_fail(self):
        for changes in [dict(version='0'), dict(agreement='email2-conversation-v0'),
                        dict(agreement='future'), dict(extra='x')]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.check('source', dict(self.source, **changes))
        absent = dict(self.source); del absent['targetDelegation']
        with self.assertRaises(ValueError):self.check('source', absent)
        proof = self.sign('source', self.source)
        with self.assertRaises(ValueError):old_parse(__import__('json').loads(proof), 'source')

    def test_old_or_opposite_domain_is_not_a_successor_signature(self):
        for domain in [b'email2/bootstrap/source/v0', b'mail/bootstrap/response/v1']:
            with self.assertRaises(ValueError):
                verify_candidate(self.sign('source', self.source, domain=domain), 'source', self.source_actor, time=(20, 21))

    def test_actor_substitution_and_assertion9_wrong_signature_do_not_supply_identity(self):
        with self.assertRaises(ValueError):
            verify_candidate(self.source_proof, 'source', self.target_actor, time=(20, 21))
        bad = dict(self.response, advertisement=ad(self.b, self.target_actor, self.source['targetMailbox'],
                                                  package=True, domain=b'email-next/passive-discovery/v8\0'))
        with self.assertRaises(ValueError):self.check('response', bad)
        import json
        wrapper = json.loads(base64.b64decode(self.response['advertisement']))
        wrapper['identity']['bindings'] = []
        missing = dict(self.response, advertisement=b64(encode_event(wrapper)))
        with self.assertRaises(ValueError):self.check('response', missing)

    def test_exact_payload_signature_and_duplicate_decoded_fields(self):
        import json
        proof = json.loads(self.source_proof)
        proof['payload'] = b64(b' '+parse(self.source_proof, 'source')[0])
        with self.assertRaises(ValueError):verify_candidate(encode_event(proof), 'source', self.source_actor, time=(20, 21))
        raw = encode_event(self.source).replace(b'"version":"1"', b'"version":"1","\\u0076ersion":"1"')
        with self.assertRaises(ValueError):parse(self.sign('source', self.source, raw=raw), 'source')

    def test_original_deadlines_survive_retrieval_and_current_time_uncertainty(self):
        for time in [(91, 91), (89, 91), (21, 20)]:
            with self.subTest(time=time), self.assertRaises(ValueError):self.check('source', time=time)
        with self.assertRaises(ValueError):self.check('source', dict(self.source, notAfter='611'))

    def test_descriptor_exact_branch_prefixes_roles_and_domain(self):
        self.assertEqual(descriptor_candidate(self.descriptor_bytes, domain='recipient.example', time=(20, 21)), self.descriptor)
        for changes in [dict(version='0'), dict(agreement='other'), dict(sourcePrefix='https://destination.example/manage1/sub/'),
                        dict(roles=['respond-target', 'respond-target']), dict(domain='other.example'), dict(extra='x')]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                descriptor_candidate(encode_event(dict(self.descriptor, **changes)), domain='recipient.example', time=(20, 21))


if __name__ == '__main__':
    unittest.main()
