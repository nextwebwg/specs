"""Configured MLS feasibility probe; no selected Email/2 stream wire binding.

Only synthetic fixtures contain copied compromise state. No live user state is
read, exported or logged. Public admission and durable stream ownership are not
implemented by this probe.
"""
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from event_encoding import encode_event
from identity_store import IdentityStore
from mls_mime import package, unpack
from mls_receive import LockedIdentity, worker_call
from provider_mls import call, make_device, sign
from smtp_loopback import roundtrip
from test_group_transitions import enroll

CONVERSATION = '2' * 32


class SenderStreamFeasibilityTests(unittest.TestCase):
    def setUp(self):
        self.provider = Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR']) / 'provider-mls'
        self.transitions = self.provider.with_name('group-transitions')
        self.receive_binary = self.provider.with_name('receive-staged')
        self.alice = make_device(self.provider, 1, 2)
        self.bob = make_device(self.provider, 3, 4)
        self.phone = make_device(self.provider, 1, 7)
        self.time = dict(earliest=str(max(self.alice['time'], self.bob['time'], self.phone['time'])), latest=str(max(self.alice['time'], self.bob['time'], self.phone['time'])))
        self.temp = tempfile.TemporaryDirectory()
        self.identity = IdentityStore(Path(self.temp.name) / 'accepted-identity.sqlite')
        for device in (self.alice, self.bob):
            self.identity.observe(device['record'], first_contact_policy='allow-unverified')
        enrollment, head = enroll(self.provider, self.alice, self.phone)
        self.assertEqual(self.identity.accept_successor(encode_event(enrollment), candidate_digest=head, time=self.time)['status'], 'accepted-unverified')

    def tearDown(self):
        self.identity.close()
        self.temp.cleanup()

    def fresh(self, device):
        # This method is called before taking the recipient offline, except in
        # the explicit post-remediation package experiment below.
        return dict(device, **call(self.provider, op='fresh-package', checkpoint=device['checkpoint'], key=device['key'], identity=device['identity']))

    def current(self, stream):
        for device, role in ((stream['owner'], 'send'), (stream['recipient'], 'receive')):
            checked = LockedIdentity(self.identity).check_device(bytes.fromhex(device['identity']), bytes.fromhex(device['key']), role=role, time=self.time, trust_policy='allow-unverified')
            if checked['status'] != 'authorized-unverified':
                raise ValueError('Current stream authority held')

    def create(self, owner, recipient):
        for device, role in ((owner, 'send'), (recipient, 'receive')):
            checked = LockedIdentity(self.identity).check_device(bytes.fromhex(device['identity']), bytes.fromhex(device['key']), role=role, time=self.time, trust_policy='allow-unverified')
            self.assertEqual(checked['status'], 'authorized-unverified')
        # Existing comparison context grammar only. It is not a new public mode.
        context = encode_event(dict(version='1', purpose='conversation-context', conversation=CONVERSATION, profile='mls-1-0001', administrators=[owner['principal']], ordering=dict(kind='designated-member-v0', principal=owner['principal'], device=owner['device'])))
        start = call(self.transitions, op='create', checkpoint=owner['checkpoint'], key=owner['key'], identity=owner['identity'], context=context.hex())
        staged = call(self.transitions, op='candidate', checkpoint=start['checkpoint'], key=owner['key'], group=start['snapshot']['group'], packages=[recipient['package']])
        return dict(owner=owner, recipient=recipient, context=context.hex(), group=staged['after']['group'], checkpoint=staged['checkpoint'], welcome=staged['welcome'])

    def join(self, stream, recipient=None):
        recipient = stream['recipient'] if recipient is None else recipient
        joined = call(self.transitions, op='join', checkpoint=recipient['checkpoint'], key=recipient['key'], welcome=stream['welcome'])
        self.assertEqual(joined['snapshot']['group'], stream['group'])
        self.assertEqual(joined['snapshot']['context'], stream['context'])
        return joined['checkpoint']

    def send(self, stream, event_id, text, reply_to=None, *, checkpoint=None, device=None):
        self.current(stream)
        device = stream['owner'] if device is None else device
        body = dict(conversation=CONVERSATION, principal=device['principal'], event=event_id, text=text, replyTo=[] if reply_to is None else [reply_to])
        sent = call(self.provider, op='send', checkpoint=stream['checkpoint'] if checkpoint is None else checkpoint, key=device['key'], group=stream['group'], application=encode_event(body).hex())
        if checkpoint is None:
            stream['checkpoint'] = sent['checkpoint']
        return sent['wire']

    def read(self, stream, checkpoint, wire):
        received = call(self.receive_binary, format='openmls-0.9.1-map-0', checkpoint=checkpoint, group=stream['group'], wire=wire)
        body = json.loads(bytes.fromhex(received['application']))
        # MLS authenticates any member. The application must enforce stream
        # authorship separately; a decrypting member is not this stream's owner.
        if received['processed']['credential'] != stream['owner']['identity']:
            raise ValueError('Non-owner stream author')
        if body['principal'] != stream['owner']['principal'] or body['conversation'] != CONVERSATION:
            raise ValueError('Application binding')
        self.current(stream)
        return received['checkpoint'], body

    def test_new_authorized_device_can_prepare_and_submit_before_contact_joins(self):
        published_bob = self.fresh(self.bob)
        stream = self.create(self.phone, published_bob)
        wire = self.send(stream, 'a' * 32, 'Hello from the newly enrolled phone')
        delivered = unpack(roundtrip(package(bytes.fromhex(wire)))).hex()
        # Bob does no processing until after the first encrypted SMTP handoff.
        bob_checkpoint = self.join(stream)
        _, body = self.read(stream, bob_checkpoint, delivered)
        self.assertEqual(body['principal'], self.alice['principal'])
        self.assertEqual(body['text'], 'Hello from the newly enrolled phone')

    def test_simultaneous_sends_and_reply_reference_across_independent_groups(self):
        left = self.create(self.alice, self.fresh(self.bob))
        right = self.create(self.bob, self.fresh(self.alice))
        self.assertNotEqual(left['group'], right['group'])
        a_wire = self.send(left, 'a' * 32, 'Alice first')
        b_wire = self.send(right, 'b' * 32, 'Bob independently')
        bob_checkpoint, first = self.read(left, self.join(left), a_wire)
        alice_checkpoint, second = self.read(right, self.join(right), b_wire)
        reference = {k: first[k] for k in ('principal', 'conversation', 'event')}
        reply_wire = self.send(right, 'c' * 32, 'Bob replies to Alice', reference)
        _, reply = self.read(right, alice_checkpoint, reply_wire)
        self.assertEqual(reply['replyTo'], [reference])
        self.assertEqual(second['text'], 'Bob independently')
        self.assertTrue(bool(bob_checkpoint))

    def test_member_encryption_is_not_owner_authentication(self):
        stream = self.create(self.alice, self.fresh(self.bob))
        bob_checkpoint = self.join(stream)
        forged = self.send(stream, 'd' * 32, 'Member-authenticated but not owner-authored', checkpoint=bob_checkpoint, device=self.bob)
        with self.assertRaisesRegex(ValueError, 'Non-owner stream author'):
            self.read(stream, stream['checkpoint'], forged)

    def test_owner_self_update_does_not_heal_recipient_group_state_compromise(self):
        stream = self.create(self.alice, self.fresh(self.bob))
        bob_checkpoint = self.join(stream)
        attacker_checkpoint = copy.deepcopy(bob_checkpoint)
        changed = call(self.transitions, op='candidate', checkpoint=stream['checkpoint'], key=self.alice['key'], group=stream['group'], packages=[])
        stream['checkpoint'] = changed['checkpoint']
        # A passive copy of the compromised recipient's state can follow the
        # owner's update. This counterexample prohibits a global PCS claim.
        for checkpoint in (bob_checkpoint, attacker_checkpoint):
            accepted = call(self.transitions, op='receive', checkpoint=checkpoint, key=self.bob['key'], group=stream['group'], wire=changed['wire'])
            if checkpoint is bob_checkpoint:
                honest_next = accepted['checkpoint']
            else:
                attacker_next = accepted['checkpoint']
        wire = self.send(stream, 'e' * 32, 'Still exposed to the old recipient state')
        _, honest = self.read(stream, honest_next, wire)
        _, exposed = self.read(stream, attacker_next, wire)
        self.assertEqual(exposed['event'], honest['event'])

    def test_fresh_recipient_admission_is_not_recoverable_from_old_group_state(self):
        old = self.create(self.alice, self.fresh(self.bob))
        compromised = self.join(old)
        # Recipient remediation precedes generating this independent package.
        replacement = self.create(self.alice, self.fresh(self.bob))
        self.assertNotEqual(old['group'], replacement['group'])
        with self.assertRaises((ValueError, RuntimeError)):
            self.join(replacement, dict(self.bob, checkpoint=compromised))
        wire = self.send(replacement, 'f' * 32, 'Protected by new recipient admission material')
        _, body = self.read(replacement, self.join(replacement), wire)
        self.assertEqual(body['event'], 'f' * 32)

    def test_recipient_update_can_heal_its_stream_without_recipient_ordering_vote(self):
        stream = self.create(self.alice, self.fresh(self.bob))
        bob_checkpoint = self.join(stream)
        compromised = copy.deepcopy(bob_checkpoint)
        binary = self.provider.with_name('sender-streams-probe')
        update = call(binary, op='propose-update', checkpoint=bob_checkpoint, key=self.bob['key'], group=stream['group'])
        committed = call(binary, op='commit-update', checkpoint=stream['checkpoint'], key=self.alice['key'], group=stream['group'], wire=update['wire'])
        self.assertEqual(committed['proposalSender'], self.bob['identity'])
        # Supply the copied state with the exact public Update and reference.
        # A missing proposal dependency must not masquerade as PCS recovery.
        exposed = call(binary, op='cache-public', checkpoint=compromised, key=self.bob['key'], group=stream['group'], publicProposal=committed['publicProposal'])
        self.assertTrue(exposed['pending'])
        attacker_result = worker_call(binary, dict(op='receive-update', checkpoint=exposed['checkpoint'], key=self.bob['key'], group=stream['group'], wire=committed['wire']))
        self.assertEqual(attacker_result.get('status'), 'worker-rejected')
        self.assertEqual(attacker_result.get('reason'), 'commit-crypto-rejected')
        honest = call(binary, op='receive-update', checkpoint=update['checkpoint'], key=self.bob['key'], group=stream['group'], wire=committed['wire'])
        self.assertEqual(honest['epoch'], committed['epoch'])
        stream['checkpoint'] = committed['checkpoint']
        wire = self.send(stream, '9' * 32, 'Readable after the recipient refresh')
        _, body = self.read(stream, honest['checkpoint'], wire)
        self.assertEqual(body['text'], 'Readable after the recipient refresh')

    def test_known_owner_revocation_blocks_prepared_receive_effect_and_future_send(self):
        stream = self.create(self.phone, self.fresh(self.bob))
        bob_checkpoint = self.join(stream)
        wire = self.send(stream, '8' * 32, 'Prepared before local revocation was known')
        bundle, head = enroll(self.provider, self.alice, self.phone)
        state = json.loads(base64.b64decode(bundle['states'][0]['payload']))
        state.update(record='9' * 32, revision='2', previous=[head], revoked=[self.phone['device']], bindings=[item for item in state['bindings'] if item['device'] != self.phone['device']])
        payload = encode_event(state)
        bundle['states'].insert(0, dict(payload=base64.b64encode(payload).decode(), signature=sign(self.provider, self.alice, 'email-next/identity-state/v0', payload)))
        self.assertEqual(self.identity.accept_successor(encode_event(bundle), candidate_digest=hashlib.sha256(payload).hexdigest(), time=self.time)['status'], 'accepted-unverified')
        with self.assertRaisesRegex(ValueError, 'Current stream authority held'):
            self.read(stream, bob_checkpoint, wire)
        with self.assertRaisesRegex(ValueError, 'Current stream authority held'):
            self.send(stream, '7' * 32, 'Must not send after revocation')


if __name__ == '__main__':
    unittest.main()
