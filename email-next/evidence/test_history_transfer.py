"""Real identity proofs and recipient-bound offline historical import."""
import base64
import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from archive_set import account_index, signed_catalog
from correspondence_archive import write_plain
from event_encoding import encode_event
from history_transfer import (admit_grant, approve_grant, check_cancel, check_receipt, check_release,
                              import_history, receipt_for_import, sign_record, unpack,
                              verify_record, delivery_descriptors, select_delivery_entries, validate)
from identity_store import IdentityStore

TIME = dict(earliest='20', latest='21')
POLICY = 'allow-unverified'


def public(key):
    return key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()


def proof(key, domain, raw):
    return key.sign(domain.encode() + b'\0' + struct.pack('>I', len(raw)) + raw).hex()


def identity_material(principal=None, target_roles=None):
    source, target = Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()
    principal = principal or 'enp0:' + 'a' * 64
    device = lambda n: 'end0:' + n * 64
    old = encode_event(dict(version='0', purpose='device-binding', record='1' * 32,
                            principal=principal, device=device('1'), signingKey=public(source),
                            roles=['send', 'receive', 'enroll', 'revoke'], notBefore='10', notAfter='100',
                            authority=dict(kind='first-contact')))
    genesis = encode_event(dict(version='0', purpose='identity-state', principal=principal, record='2' * 32,
                                revision='0', previous=[], issuedAt='10',
                                bindings=[dict(device=device('1'), digest=hashlib.sha256(old).hexdigest())],
                                revoked=[], signer=device('1')))
    head0 = hashlib.sha256(genesis).hexdigest()
    added = encode_event(dict(version='0', purpose='device-binding', record='3' * 32,
                              principal=principal, device=device('2'), signingKey=public(target),
                              roles=target_roles or ['send', 'receive'], notBefore='10', notAfter='100',
                              authority=dict(kind='state', digest=head0)))
    next_value = json.loads(genesis)
    next_value = dict(next_value, record='4' * 32, revision='1', previous=[head0], issuedAt='11',
                      bindings=next_value['bindings'] + [dict(device=device('2'), digest=hashlib.sha256(added).hexdigest())])
    successor = encode_event(next_value)
    head1 = hashlib.sha256(successor).hexdigest()
    def state(raw):
        return dict(payload=base64.b64encode(raw).decode(), signature=proof(source, 'email-next/identity-state/v0', raw))
    def binding(raw, key):
        return dict(payload=base64.b64encode(raw).decode(), authorization=proof(source, 'email-next/device-binding/v0', raw),
                    possession=proof(key, 'email-next/device-possession/v0', raw))
    bundle = dict(version='0', purpose='identity-bundle', principal=principal,
                  states=[state(genesis), state(successor)], bindings=[binding(old, source), binding(added, target)])
    removed_value = dict(next_value, record='5' * 32, revision='2', previous=[head1], issuedAt='12',
                         bindings=[next_value['bindings'][0]], revoked=[device('2')])
    removed = encode_event(removed_value)
    removal_bundle = dict(version='0', purpose='identity-bundle', principal=principal,
                          states=[state(successor), state(removed)], bindings=bundle['bindings'])
    record = dict(state=base64.b64encode(genesis).decode(), binding=base64.b64encode(old).decode(),
                  stateProof=proof(source, 'email-next/identity-state/v0', genesis),
                  authorization=proof(source, 'email-next/device-binding/v0', old),
                  possession=proof(source, 'email-next/device-possession/v0', old), time=TIME)
    refs = [dict(principal=principal, device=device(n), state=head1, binding=hashlib.sha256(raw).hexdigest(), key=public(key))
            for n, raw, key in [('1', old, source), ('2', added, target)]]
    return dict(source=source, target=target, record=record, bundle=bundle, head=head1,
                genesis=head0, removal=removal_bundle, removed=hashlib.sha256(removed).hexdigest(), refs=refs)


@unittest.skipUnless(shutil.which('age') and shutil.which('age-keygen'), 'Installed age tools required')
class HistoryTransferTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.material = identity_material()
        self.store = IdentityStore(self.root / 'identity.sqlite')
        self.addCleanup(self.store.close)
        result = self.store.observe(self.material['record'], first_contact_policy=POLICY)
        self.assertEqual(result['status'], 'pinned-unverified')
        result = self.store.accept_successor(encode_event(self.material['bundle']), candidate_digest=self.material['head'], time=TIME)
        self.assertEqual(result['status'], 'accepted-unverified')
        self.key = self.root / 'transfer-identity'
        subprocess.run(['age-keygen', '-o', str(self.key)], capture_output=True, check=True)
        self.recipient = subprocess.run(['age-keygen', '-y', str(self.key)], capture_output=True, check=True).stdout.strip().decode()
        self.source, self.target = self.material['refs']
        self.request = dict(version='0', purpose='history-transfer-request', transfer='b' * 32,
                            source=self.source, target=self.target, recipient=self.recipient,
                            accounts=[], deliveries=[], receipt='import-result', notBefore='10', notAfter='90')
        self.request_wrapper = sign_record('request', encode_event(self.request), self.material['target'])
        self.grant = dict(version='0', purpose='history-transfer-grant', transfer='b' * 32,
                          request=unpack(self.request_wrapper, 'request')[3], source=self.source, target=self.target,
                          scope=[dict(id='c' * 32, principal='', selection='d' * 32, mode='all-retained',
                                      cutoff='1', entries='0', digest=account_index([]))],
                          archive='e' * 32, set='f' * 32, verificationKey='1' * 64,
                          catalog=dict(sha256='2' * 64, size='100'), complete=True, notBefore='10', notAfter='80')

    def approve(self, value=None, request=None, approval=None):
        raw = encode_event(value or self.grant)
        return approve_grant(request or self.request_wrapper, raw, self.material['source'], self.store,
                             time=TIME, trust_policy=POLICY,
                             approved_payload_digest=approval or hashlib.sha256(raw).hexdigest())

    def admitted(self, wrapper):
        return admit_grant(self.request_wrapper, wrapper, self.store, time=TIME, trust_policy=POLICY,
                           expected_grant_reference=unpack(wrapper, 'grant')[3])

    def test_signed_delivery_selectors_are_bound_and_unintegrated_export_holds(self):
        request = dict(self.request, deliveries=[dict(sha256='1' * 64, size='80')])
        wrapper = sign_record('request', encode_event(request), self.material['target'])
        accepted = verify_record(wrapper, 'request', self.store, time=TIME, trust_policy=POLICY)
        self.assertEqual(accepted['value']['deliveries'], request['deliveries'])
        changed = dict(request, deliveries=[dict(sha256='2' * 64, size='80')])
        tampered = dict(wrapper, payload=base64.b64encode(encode_event(changed)).decode())
        with self.assertRaises(ValueError):
            verify_record(tampered, 'request', self.store, time=TIME, trust_policy=POLICY)
        grant = dict(self.grant, request=accepted['reference'])
        with self.assertRaisesRegex(ValueError, 'not integrated'):
            self.approve(grant, request=wrapper)

    def test_valid_real_authority_and_explicit_source_approval(self):
        grant = self.approve()
        self.assertEqual(check_release(self.request_wrapper, grant, self.store, time=TIME, trust_policy=POLICY,
                                       prepared_reference=unpack(grant, 'grant')[3]),
                         unpack(grant, 'grant')[3])
        self.assertEqual(self.admitted(grant).grant, unpack(grant, 'grant')[0])

    def test_missing_source_approval(self):
        with self.assertRaises(ValueError):
            self.approve(approval='0' * 64)

    def test_withdrawn_local_disclosure_permission_holds_release(self):
        grant = self.approve()
        with self.assertRaises(ValueError):
            check_release(self.request_wrapper, grant, self.store, time=TIME, trust_policy=POLICY, prepared_reference='0' * 64)

    def test_tampered_signed_request(self):
        wrapper = copy.deepcopy(self.request_wrapper)
        changed = dict(self.request, recipient=self.recipient[:-1] + ('q' if self.recipient[-1] != 'q' else 'p'))
        wrapper['payload'] = base64.b64encode(encode_event(changed)).decode()
        with self.assertRaises(ValueError):
            self.approve(request=wrapper)

    def test_wrong_request_and_expanded_interval(self):
        for value in [dict(self.grant, request='0' * 64), dict(self.grant, notAfter='95')]:
            with self.assertRaises(ValueError):
                self.approve(value)

    def test_request_interval_cannot_outlive_device_binding(self):
        value = dict(self.request, notAfter='101')
        wrapper = sign_record('request', encode_event(value), self.material['target'])
        with self.assertRaises(ValueError):
            verify_record(wrapper, 'request', self.store, time=TIME, trust_policy=POLICY)

    def test_requested_account_scope_is_enforced(self):
        value = dict(self.request, accounts=['1' * 32])
        request = sign_record('request', encode_event(value), self.material['target'])
        grant = dict(self.grant, request=unpack(request, 'request')[3])
        with self.assertRaises(ValueError):
            self.approve(grant, request=request)

    def test_expired_and_uncertain_time_hold_release(self):
        grant = self.approve()
        for time in [dict(earliest='81', latest='82'), dict(earliest='79', latest='81')]:
            with self.assertRaises(ValueError):
                check_release(self.request_wrapper, grant, self.store, time=time, trust_policy=POLICY,
                              prepared_reference=unpack(grant, 'grant')[3])

    def test_required_verification_is_not_silently_weakened(self):
        with self.assertRaises(ValueError):
            verify_record(self.request_wrapper, 'request', self.store, time=TIME, trust_policy='require-verification')

    def test_revocation_after_preparation_stops_release(self):
        grant = self.approve()
        self.store.accept_successor(encode_event(self.material['removal']), candidate_digest=self.material['removed'], time=TIME)
        with self.assertRaises(ValueError):
            check_release(self.request_wrapper, grant, self.store, time=TIME, trust_policy=POLICY,
                                       prepared_reference=unpack(grant, 'grant')[3])

    def test_source_cancellation_after_target_revocation_stops_only_future_release(self):
        grant = self.approve()
        self.store.accept_successor(encode_event(self.material['removal']), candidate_digest=self.material['removed'], time=TIME)
        value = dict(version='0', purpose='history-transfer-cancel', transfer=self.request['transfer'],
                     request=unpack(self.request_wrapper, 'request')[3], grant=unpack(grant, 'grant')[3],
                     source=self.source, target=self.target, by='source', notBefore='10', notAfter='80')
        cancel = sign_record('cancel', encode_event(value), self.material['source'])
        self.assertEqual(check_cancel(self.request_wrapper, grant, cancel, self.store, time=TIME, trust_policy=POLICY),
                         unpack(cancel, 'cancel')[3])

    def test_cancellation_cannot_target_an_unrelated_grant(self):
        grant = self.approve()
        value = dict(version='0', purpose='history-transfer-cancel', transfer=self.request['transfer'],
                     request=unpack(self.request_wrapper, 'request')[3], grant='0' * 64,
                     source=self.source, target=self.target, by='target', notBefore='10', notAfter='80')
        cancel = sign_record('cancel', encode_event(value), self.material['target'])
        with self.assertRaises(ValueError):
            check_cancel(self.request_wrapper, grant, cancel, self.store, time=TIME, trust_policy=POLICY)

    def test_valid_ancestor_reference_is_not_a_claim_of_current_head(self):
        source = dict(self.source, state=self.material['genesis'])
        value = dict(self.request, source=source)
        wrapper = sign_record('request', encode_event(value), self.material['target'])
        self.assertEqual(verify_record(wrapper, 'request', self.store, time=TIME, trust_policy=POLICY)['sourceHead'],
                         self.material['head'])

    def test_same_key_binding_renewal_does_not_renew_an_old_history_grant(self):
        grant=self.approve()
        bundle=copy.deepcopy(self.material['bundle'])
        original=next(item for item in bundle['bindings']
                      if hashlib.sha256(base64.b64decode(item['payload'])).hexdigest()==self.target['binding'])
        binding=json.loads(base64.b64decode(original['payload']))
        binding.update(record='6'*32,notAfter='110',
                       authority=dict(kind='state',digest=self.material['head']))
        raw=encode_event(binding);digest=hashlib.sha256(raw).hexdigest()
        bundle['bindings'].append(dict(payload=base64.b64encode(raw).decode(),
            authorization=proof(self.material['source'],'email-next/device-binding/v0',raw),
            possession=proof(self.material['target'],'email-next/device-possession/v0',raw)))
        parent=next(json.loads(base64.b64decode(item['payload'])) for item in bundle['states']
                    if hashlib.sha256(base64.b64decode(item['payload'])).hexdigest()==self.material['head'])
        parent.update(record='7'*32,revision='2',previous=[self.material['head']],issuedAt='20')
        parent['bindings']=[dict(device=ref['device'],digest=digest) if ref['device']==self.target['device'] else ref
                            for ref in parent['bindings']]
        state=encode_event(parent);head=hashlib.sha256(state).hexdigest()
        bundle['states'].append(dict(payload=base64.b64encode(state).decode(),
            signature=proof(self.material['source'],'email-next/identity-state/v0',state)))
        self.assertEqual(self.store.accept_successor(encode_event(bundle),candidate_digest=head,time=TIME)['status'],
                         'accepted-unverified')
        with self.assertRaisesRegex(ValueError,'not currently authorized'):
            check_release(self.request_wrapper,grant,self.store,time=TIME,trust_policy=POLICY,
                          prepared_reference=unpack(grant,'grant')[3])

    def test_unknown_state_and_key_substitution_rejected(self):
        for source in [dict(self.source, state='0' * 64), dict(self.source, key='1' * 64)]:
            wrapper = sign_record('request', encode_event(dict(self.request, source=source)), self.material['target'])
            with self.assertRaises(ValueError):
                verify_record(wrapper, 'request', self.store, time=TIME, trust_policy=POLICY)

    def test_duplicate_members_and_unknown_control_fields(self):
        wire = json.dumps(self.request_wrapper, separators=(',', ':')).encode()
        wire = wire.replace(b'{', b'{"payload":"untrusted",', 1)
        with self.assertRaises(ValueError):
            verify_record(wire, 'request', self.store, time=TIME, trust_policy=POLICY)
        raw = encode_event(dict(self.request, callback='https://example.invalid/'))
        with self.assertRaises(ValueError):
            sign_record('request', raw, self.material['target'])
        raw = encode_event(self.request).replace(b'"version":"0"', b'"version":"0","version":"0"')
        with self.assertRaises(ValueError):
            sign_record('request', raw, self.material['target'])

    def make_files(self):
        signer = Ed25519PrivateKey.generate()
        resource = b'exact historical mail bytes'
        h = hashlib.sha256(resource).hexdigest()
        entry = dict(id='3' * 32, account='c' * 32, kind='original-mail', object=h, contribution='')
        manifest = dict(version='0', purpose='correspondence-archive', archive=self.grant['archive'],
                        snapshot='4' * 32, sequence='0', previous='', createdAt='0',
                        accounts=[dict(id='c' * 32, principal='')], coverage=dict(complete=True, omissions=[]),
                        entries=[entry], objects=[dict(sha256=h, size=str(len(resource)))])
        raw = io.BytesIO()
        write_plain(manifest, {h: resource}, signer, raw)
        encrypted = subprocess.run(['age', '-r', self.recipient], input=raw.getvalue(), capture_output=True, check=True).stdout
        part_hash = hashlib.sha256(encrypted).hexdigest()
        part = self.root / part_hash
        part.write_bytes(encrypted)
        scope = dict(self.grant['scope'][0], entries='1', digest=account_index([entry]))
        catalog = dict(version='0', purpose='correspondence-archive-set', archive=self.grant['archive'], set=self.grant['set'],
                       generation='0', previous='', firstSequence='0', previousPart='', accounts=[scope],
                       parts=[dict(snapshot=manifest['snapshot'], sequence='0', ciphertext=part_hash, size=str(len(encrypted)))],
                       complete=True, omissions=[])
        encrypted = subprocess.run(['age', '-r', self.recipient], input=signed_catalog(catalog, signer), capture_output=True, check=True).stdout
        catalog_file = self.root / 'catalog.age'
        catalog_file.write_bytes(encrypted)
        self.grant.update(scope=[scope], verificationKey=public(signer),
                          catalog=dict(sha256=hashlib.sha256(encrypted).hexdigest(), size=str(len(encrypted))))
        return catalog_file, {part_hash: part}, h, resource

    def test_recipient_bound_import_and_terminal_receipt(self):
        catalog, parts, h, data = self.make_files()
        wrapper = self.approve()
        admission = self.admitted(wrapper)
        before = self.store.current_state(self.source['principal'])
        destination = self.root / 'history'
        completed = import_history(admission, catalog, self.key, parts, destination)
        self.assertEqual((destination / ('4' * 32) / h).read_bytes(), data)
        self.assertEqual(self.store.current_state(self.source['principal']), before)
        receipt = receipt_for_import(admission, completed, self.material['target'], self.store, time=TIME, trust_policy=POLICY)
        self.assertEqual(check_receipt(self.request_wrapper, wrapper, receipt, self.store, time=TIME, trust_policy=POLICY),
                         unpack(receipt, 'receipt')[3])
        self.assertEqual(import_history(admission, catalog, self.key, parts, destination), completed)
        with self.assertRaises(ValueError):
            receipt_for_import(admission, json.loads(completed.receipt), self.material['target'], self.store,
                               time=TIME, trust_policy=POLICY)

    def test_explicit_cross_principal_disclosure_uses_accepted_peer(self):
        peer = identity_material('enp0:' + 'b' * 64)
        self.store.observe(peer['record'], first_contact_policy=POLICY)
        result = self.store.accept_successor(encode_event(peer['bundle']), candidate_digest=peer['head'], time=TIME)
        self.assertEqual(result['status'], 'accepted-unverified')
        self.target = peer['refs'][0]
        self.request['target'] = self.target
        self.request_wrapper = sign_record('request', encode_event(self.request), peer['source'])
        self.grant.update(target=self.target, request=unpack(self.request_wrapper, 'request')[3])
        catalog, parts, _, _ = self.make_files()
        wrapper = self.approve()
        self.assertNotEqual(self.grant['source']['principal'], self.grant['target']['principal'])
        admission = self.admitted(wrapper)
        before = [self.store.current_state(ref['principal']) for ref in (self.source, self.target)]
        import_history(admission, catalog, self.key, parts, self.root / 'shared-history')
        self.assertEqual(before, [self.store.current_state(ref['principal']) for ref in (self.source, self.target)])

    def test_other_requester_cannot_hijack_the_transfer_id(self):
        grant = self.approve()
        peer = identity_material('enp0:' + 'b' * 64)
        self.store.observe(peer['record'], first_contact_policy=POLICY)
        self.store.accept_successor(encode_event(peer['bundle']), candidate_digest=peer['head'], time=TIME)
        other = dict(self.request, target=peer['refs'][0])
        request = sign_record('request', encode_event(other), peer['source'])
        with self.assertRaises(ValueError):
            check_release(request, grant, self.store, time=TIME, trust_policy=POLICY,
                          prepared_reference=unpack(grant, 'grant')[3])
        self.assertEqual(check_release(self.request_wrapper, grant, self.store, time=TIME, trust_policy=POLICY,
                                       prepared_reference=unpack(grant, 'grant')[3]), unpack(grant, 'grant')[3])

    def test_terminal_result_does_not_require_revoked_source_permission(self):
        peer = identity_material('enp0:' + 'b' * 64, target_roles=['send', 'receive', 'enroll', 'revoke'])
        self.store.observe(peer['record'], first_contact_policy=POLICY)
        self.store.accept_successor(encode_event(peer['bundle']), candidate_digest=peer['head'], time=TIME)
        self.material = peer
        self.source, self.target = peer['refs']
        self.request.update(source=self.source, target=self.target)
        self.request_wrapper = sign_record('request', encode_event(self.request), peer['target'])
        self.grant.update(source=self.source, target=self.target, request=unpack(self.request_wrapper, 'request')[3])
        catalog, parts, _, _ = self.make_files()
        grant = self.approve()
        admission = self.admitted(grant)
        completed = import_history(admission, catalog, self.key, parts, self.root / 'history')
        previous = peer['bundle']['states'][1]
        state = json.loads(base64.b64decode(previous['payload']))
        state.update(record='7' * 32, revision='2', previous=[peer['head']], issuedAt='12',
                     bindings=[state['bindings'][1]], revoked=[self.source['device']])
        raw = encode_event(state)
        bundle = dict(version='0', purpose='identity-bundle', principal=self.source['principal'],
                      states=[previous, dict(payload=base64.b64encode(raw).decode(),
                                             signature=proof(peer['source'], 'email-next/identity-state/v0', raw))],
                      bindings=peer['bundle']['bindings'])
        accepted = self.store.accept_successor(encode_event(bundle), candidate_digest=hashlib.sha256(raw).hexdigest(), time=TIME)
        self.assertEqual(accepted['status'], 'accepted-unverified')
        receipt = receipt_for_import(admission, completed, peer['target'], self.store, time=TIME, trust_policy=POLICY)
        self.assertEqual(check_receipt(self.request_wrapper, grant, receipt, self.store, time=TIME, trust_policy=POLICY),
                         unpack(receipt, 'receipt')[3])
        with self.assertRaises(ValueError):
            check_release(self.request_wrapper, grant, self.store, time=TIME, trust_policy=POLICY,
                          prepared_reference=unpack(grant, 'grant')[3])

    def test_catalog_scope_mismatch_never_publishes(self):
        catalog, parts, _, _ = self.make_files()
        self.grant['scope'][0]['entries'] = '0'
        admission = self.admitted(self.approve())
        destination = self.root / 'history'
        with self.assertRaises(ValueError):
            import_history(admission, catalog, self.key, parts, destination)
        self.assertFalse(destination.exists())

    def test_wrong_target_private_key(self):
        catalog, parts, _, _ = self.make_files()
        admission = self.admitted(self.approve())
        wrong = self.root / 'wrong-key'
        subprocess.run(['age-keygen', '-o', str(wrong)], capture_output=True, check=True)
        destination = self.root / 'history'
        with self.assertRaises(ValueError):
            import_history(admission, catalog, wrong, parts, destination)
        self.assertFalse(destination.exists())

    def test_unapproved_or_unretained_grant_cannot_self_admit(self):
        wrapper = self.approve()
        with self.assertRaises(ValueError):
            admit_grant(self.request_wrapper, wrapper, self.store, time=TIME, trust_policy=POLICY,
                        expected_grant_reference='0' * 64)
        with self.assertRaises(ValueError):
            import_history(wrapper, self.root / 'unused', self.key, {}, self.root / 'history')


class DeliverySelectionTests(unittest.TestCase):
    def setUp(self):
        refs = identity_material()['refs']
        self.request = dict(version='0', purpose='history-transfer-request', transfer='b' * 32,
                            source=refs[0], target=refs[1], recipient='age1' + 'q' * 58,
                            accounts=[], deliveries=[dict(sha256='1' * 64, size='80')],
                            receipt='import-result', notBefore='10', notAfter='90')
        self.row = dict(principal=refs[1]['principal'], account='c' * 32, entry='d' * 32)
        self.index = {('1' * 64, 80): [self.row]}

    def test_exact_mapping_proposes_only_matched_entries(self):
        index = dict(self.index, unrelated=[dict(self.row, entry='e' * 32)])
        index[('2' * 64, 80)] = [dict(self.row, entry='e' * 32)]
        self.assertEqual(select_delivery_entries(self.request, index), (('c' * 32, 'd' * 32),))

    def test_copied_ciphertext_does_not_authorize_another_principal(self):
        request = copy.deepcopy(self.request)
        request['target']['principal'] = 'enp0:' + 'f' * 64
        with self.assertRaisesRegex(ValueError, 'principal mismatch'):
            select_delivery_entries(request, self.index)

    def test_missing_or_wrong_size_mapping_holds(self):
        for index in ({}, {('1' * 64, 81): [self.row]}, {('1' * 64, 80): []}):
            with self.subTest(index=index), self.assertRaises(ValueError):
                select_delivery_entries(self.request, index)

    def test_one_missing_selector_prevents_partial_proposal(self):
        request = dict(self.request, deliveries=self.request['deliveries'] + [dict(sha256='2' * 64, size='80')])
        with self.assertRaises(ValueError):
            select_delivery_entries(request, self.index)

    def test_account_constraint_cannot_be_widened(self):
        request = dict(self.request, accounts=['e' * 32])
        with self.assertRaisesRegex(ValueError, 'requested accounts'):
            select_delivery_entries(request, self.index)

    def test_union_is_stable_without_duplicating_shared_content(self):
        request = dict(self.request, deliveries=self.request['deliveries'] + [dict(sha256='2' * 64, size='80')])
        index = dict(self.index)
        index[('2' * 64, 80)] = [dict(self.row, entry='e' * 32), self.row]
        self.assertEqual(select_delivery_entries(request, index), (('c' * 32, 'd' * 32), ('c' * 32, 'e' * 32)))

    def test_descriptor_schema_rejects_ambiguity_and_noncanonical_sizes(self):
        descriptor = self.request['deliveries'][0]
        invalid = [None, [descriptor, descriptor], [dict(descriptor, size='0')],
                   [dict(descriptor, size='080')], [dict(descriptor, size=80)],
                   [dict(descriptor, size='18446744073709551616')],
                   [dict(descriptor, callback='https://untrusted.example/')],
                   [dict(descriptor, sha256='A' * 64)],
                   [dict(sha256='2' * 64, size='80'), descriptor]]
        for values in invalid:
            with self.subTest(values=values), self.assertRaises(ValueError):
                delivery_descriptors(values)
        old = dict(self.request)
        del old['deliveries']
        with self.assertRaises(ValueError):
            validate(old, 'request')


if __name__ == '__main__':
    unittest.main()
