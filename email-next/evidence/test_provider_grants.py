"""Actual Ed25519/identity proofs; trusted links/grants are fixture inputs."""
import base64
import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from event_encoding import encode_event
from identity_store import IdentityStore
from provider_control import DEFAULT_LIMITS, OPERATIONS
from provider_grants import (PROFILE, ActiveLink, approve_pair, credential_proof, framing,
                             parse, role_config, role_request, signed, wire_hash)
from test_history_transfer import identity_material, proof


def wire(value):
    return json.dumps(value, separators=(',', ':')).encode()


class PublicProviderGrantTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.material = identity_material()
        self.store = IdentityStore(Path(self.temp.name) / 'identity.sqlite'); self.addCleanup(self.store.close)
        self.assertEqual(self.store.observe(self.material['record'], first_contact_policy='allow-unverified')['status'], 'pinned-unverified')
        self.assertEqual(self.store.accept_successor(encode_event(self.material['bundle']), candidate_digest=self.material['head'], time=dict(earliest='20', latest='21'))['status'], 'accepted-unverified')
        self.initiator, self.target = self.material['refs']
        self.config = dict(profile='en-provider-control-0', grant='1' * 64, account='2' * 64,
                           service='https://mail.example', prefix='https://mail.example/control/',
                           initiator={k:self.initiator[k] for k in ['principal','device']},
                           target={k:self.target[k] for k in ['principal','device']},
                           initiatorState=self.initiator['state'], initiatorBinding=self.initiator['binding'],
                           targetState=self.target['state'], targetBinding=self.target['binding'],
                           role='target', operations=OPERATIONS['target'][:], notBefore=10, notAfter=90,
                           limits=DEFAULT_LIMITS.copy())
        self.link = ActiveLink(account=self.config['account'], link='3' * 32, family='4' * 64,
                               mailbox='bob@example.org', delegation='5' * 64, service=self.config['service'],
                               prefix=self.config['prefix'], target=self.target, not_before=10, not_after=95)
        self.prepared = dict(profile=PROFILE, purpose='provider-pair-approval', preparation='6' * 32,
                             request='7' * 32, nonce='8' * 64, delegationDigest=self.link.delegation,
                             link=self.link.link, family=self.link.family, mailbox=self.link.mailbox,
                             configuration=self.config, initiatorKey=self.initiator['key'], targetKey=self.target['key'],
                             notBefore=10, notAfter=50)
        self.raw = wire(self.prepared)
        self.approval = signed('pair-approval', self.raw, self.material['target'])
        self.pair = self.approve()
        self.request_value = dict(profile=PROFILE, purpose='provider-role-request', request='9' * 32,
                                  approvalDigest=wire_hash(self.raw), grant=self.config['grant'],
                                  service=self.config['service'], prefix=self.config['prefix'],
                                  role='initiator', device=self.initiator, notBefore=20, notAfter=75)
        self.request = signed('role-request', wire(self.request_value), self.material['source'])
        self.challenge = dict(self.request_value, purpose='provider-role-credential', credential='a' * 64,
                              nonce='b' * 64, account=self.link.account, notAfter=60)
        self.credential = signed('role-credential', wire(self.challenge), self.material['source'])

    def approve(self, proof_value=None, **kwargs):
        return approve_pair(proof_value or self.approval, kwargs.pop('link', self.link), self.store,
                            prepared_payload=kwargs.pop('prepared_payload', self.raw), time=kwargs.pop('time', (20,21)),
                            trust_policy=kwargs.pop('trust_policy', 'allow-unverified'), **kwargs)

    def issue(self, value=None, request=None, **kwargs):
        return credential_proof(value or self.credential, request or self.request, self.pair,
                                kwargs.pop('link', self.link), self.store, retained_challenge=kwargs.pop('retained_challenge', wire(self.challenge)),
                                time=kwargs.pop('time', (20,21)), trust_policy=kwargs.pop('trust_policy', 'allow-unverified'),
                                grant_active=kwargs.pop('grant_active', True), **kwargs)

    def test_actual_pair_and_possession_proofs_select_only_initiator_operations(self):
        c = self.issue()
        self.assertEqual(c['role'], 'initiator')
        self.assertEqual(c['operations'], OPERATIONS['initiator'])
        self.assertNotIn('response-write', c['operations'])
        self.assertNotIn('accessToken', c)

    def test_target_gets_distinct_role_after_its_own_two_signatures(self):
        request_value = dict(self.request_value, role='target', device=self.target)
        req = signed('role-request', wire(request_value), self.material['target'])
        challenge = dict(self.challenge, role='target', device=self.target)
        c = self.issue(signed('role-credential', wire(challenge), self.material['target']), request=req, retained_challenge=wire(challenge))
        self.assertEqual(c['operations'], OPERATIONS['target'])
        self.assertNotIn('request-write', c['operations'])

    def test_forwarded_public_approval_is_not_target_key_possession(self):
        request_value = dict(self.request_value, role='target', device=self.target)
        req = signed('role-request', wire(request_value), self.material['source'])
        with self.assertRaises(ValueError):
            role_request(req, self.pair, self.link, self.store, time=(20,21), trust_policy='allow-unverified', grant_active=True)

    def test_approval_cannot_change_retained_preparation_even_with_valid_target_signature(self):
        value = dict(self.prepared, mailbox='elsewhere@example.org')
        w = signed('pair-approval', wire(value), self.material['target'])
        with self.assertRaises(ValueError): self.approve(w)
        # A changed preparation supplied by the trusted caller still cannot cross the link.
        with self.assertRaises(ValueError): self.approve(w, prepared_payload=wire(value))

    def test_link_account_family_origin_and_delegation_are_separate_bindings(self):
        for change in [dict(account='c'*64),dict(family='c'*64),dict(link='c'*32),dict(service='https://other.example'),
                       dict(prefix='https://mail.example/elsewhere/'),dict(delegation='c'*64),dict(mailbox='other@example.org')]:
            with self.subTest(change=change), self.assertRaises(ValueError): self.approve(link=replace(self.link, **change))

    def test_role_key_and_challenge_id_cannot_be_replaced(self):
        for change in [dict(role='target'),dict(grant='c'*64),dict(approvalDigest='c'*64),dict(request='c'*32),
                       dict(account='c'*64),dict(prefix='https://mail.example/other/')]:
            value = dict(self.challenge, **change)
            w = signed('role-credential', wire(value), self.material['source'])
            with self.subTest(change=change), self.assertRaises(ValueError): self.issue(w, retained_challenge=wire(value))
        with self.assertRaises(ValueError): self.issue(retained_challenge=wire(dict(self.challenge, nonce='c'*64)))

    def test_revoked_link_or_grant_blocks_both_roles_without_erasing_identity(self):
        self.assertEqual(self.store.current_state(self.target['principal'])['head'], self.material['head'])
        with self.assertRaises(ValueError): self.issue(grant_active=False)
        with self.assertRaises(ValueError): self.issue(link=replace(self.link, active=False))
        self.assertEqual(self.store.current_state(self.target['principal'])['head'], self.material['head'])

    def test_real_target_revocation_blocks_credential_after_valid_preparation(self):
        self.assertEqual(self.store.accept_successor(encode_event(self.material['removal']), candidate_digest=self.material['removed'], time=dict(earliest='20',latest='21'))['status'], 'accepted-unverified')
        with self.assertRaises(ValueError): self.issue()

    def test_unrelated_accepted_head_change_preserves_original_frozen_grant(self):
        bundle=copy.deepcopy(self.material['bundle'])
        value=json.loads(base64.b64decode(bundle['states'][-1]['payload']))
        value.update(record='c'*32,revision='2',previous=[self.material['head']],issuedAt='12')
        raw=encode_event(value)
        bundle['states'].append(dict(payload=base64.b64encode(raw).decode(),signature=proof(self.material['source'],'email-next/identity-state/v0',raw)))
        self.assertEqual(self.store.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(raw).hexdigest(),time=dict(earliest='20',latest='21'))['status'],'accepted-unverified')
        self.assertEqual(self.issue()['grant'], self.config['grant'])
        self.assertEqual(self.link.target['state'], self.material['head'])
        self.assertEqual(self.pair.payload, self.raw)
        with self.assertRaises(ValueError): self.issue(time=(80,81))

    def test_anchor_cannot_borrow_a_binding_added_after_it(self):
        from history_transfer import authorize, authority_snapshot
        ref = dict(self.target, state=self.material['genesis'])
        with authority_snapshot(self.store), self.assertRaisesRegex(ValueError, 'binding changed'):
            authorize(self.store, ref, 'receive', dict(earliest='20',latest='21'), 'allow-unverified')

    def test_authorized_fork_still_holds_retained_grant(self):
        bundle=copy.deepcopy(self.material['bundle'])
        value=json.loads(base64.b64decode(bundle['states'][-1]['payload']))
        value.update(record='d'*32,issuedAt='12')
        raw=encode_event(value)
        bundle['states'][-1]=dict(payload=base64.b64encode(raw).decode(),signature=proof(self.material['source'],'email-next/identity-state/v0',raw))
        result=self.store.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(raw).hexdigest(),time=dict(earliest='20',latest='21'))
        self.assertEqual(result['status'],'conflicted')
        with self.assertRaises(ValueError): self.issue()

    def test_unavailable_accepted_ancestor_holds_without_repinning(self):
        from history_transfer import authorize, authority_snapshot
        ref = dict(self.initiator, state='e'*64)
        before = self.store.current_state(self.target['principal'])
        with authority_snapshot(self.store), self.assertRaisesRegex(ValueError, 'available accepted ancestor'):
            authorize(self.store, ref, 'receive', dict(earliest='20',latest='21'), 'allow-unverified')
        self.assertEqual(self.store.current_state(self.target['principal']), before)

    def test_missing_identity_cannot_be_bootstrapped_by_grant_record(self):
        empty=IdentityStore(Path(self.temp.name)/'empty.sqlite'); self.addCleanup(empty.close)
        with self.assertRaises(ValueError): approve_pair(self.approval,self.link,empty,prepared_payload=self.raw,time=(20,21),trust_policy='allow-unverified')
        self.assertIsNone(empty.current_state(self.target['principal'])['head'])

    def test_approval_expiry_does_not_end_an_already_activated_grant(self):
        # The trusted activation is fixture input. Current grant/link/request,
        # not the old one-time approval window, governs later issuance.
        self.assertEqual(self.issue(time=(55,56))['grant'],self.config['grant'])
        with self.assertRaises(ValueError): self.approve(time=(55,56))

    def test_interval_clock_and_binding_lifetime_bounds(self):
        for time in [(19,21),(59,61),(21,20),(20,30),(True,21)]:
            with self.subTest(time=time), self.assertRaises(ValueError): self.issue(time=time)
        with self.assertRaises(ValueError): self.issue(link=replace(self.link,not_after=80))
        value=copy.deepcopy(self.prepared);value['configuration']['notAfter']=101;value['notAfter']=50
        w=signed('pair-approval',wire(value),self.material['target'])
        with self.assertRaises(ValueError): self.approve(w,prepared_payload=wire(value),link=replace(self.link,not_after=110))

    def test_strict_verification_policy_holds_instead_of_claiming_verified_peer(self):
        with self.assertRaises(ValueError): self.approve(trust_policy='require-verification')
        with self.assertRaises(ValueError): self.issue(trust_policy='require-verification')

    def test_signature_domains_and_altered_signatures_are_not_interchangeable(self):
        wrong=dict(self.credential,signature=self.material['source'].sign(framing('role-request',wire(self.challenge))).hex())
        with self.assertRaises(ValueError): self.issue(wrong)
        wrong=dict(self.approval,signature='0'*128)
        with self.assertRaises(ValueError): self.approve(wrong)

    def test_duplicate_json_canonical_base64_and_payload_limits(self):
        raw=self.raw[:-1]+b',"profile":"email2-provider-grants-v0"}'
        w=dict(payload=base64.b64encode(raw).decode(),signature=self.material['target'].sign(framing('pair-approval',raw)).hex())
        with self.assertRaises(ValueError): self.approve(w)
        for change in [dict(payload=self.approval['payload']+'\n'),dict(signature='A'*128),dict(extra='x'),dict(payload='a'*349529)]:
            with self.subTest(change=list(change)), self.assertRaises(ValueError): self.approve(dict(self.approval,**change))
        value=dict(self.request_value,role=[])
        w=dict(payload=base64.b64encode(wire(value)).decode(),signature='0'*128)
        with self.assertRaises(ValueError): parse(w,'role-request')


if __name__=='__main__': unittest.main()
