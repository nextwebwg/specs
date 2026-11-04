"""Two-principal availability boundaries using admitted MLS and durable votes."""
import json
import unittest
from unittest.mock import patch

import test_admitted_quorum as admitted
from admitted_quorum import AdmittedQuorum
from event_encoding import encode_event
from initial_roster_lifecycle import InitialRosterRelease
from mls_mime import unpack
from ordering_certificates import Proof, bundle, digest, sign, unsigned
from ordering_mls import ProviderKey, candidate_id
from ordering_scope import scope_digest
from ordering_store import VoteStore
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP


class SmallGroupAvailabilityTests(unittest.TestCase):
    tearDown = admitted.AdmittedQuorumTests.tearDown
    endpoint = admitted.AdmittedQuorumTests.endpoint
    prepare = admitted.AdmittedQuorumTests.prepare
    join = admitted.AdmittedQuorumTests.join
    event = admitted.AdmittedQuorumTests.event
    send = admitted.AdmittedQuorumTests.send
    certify = admitted.AdmittedQuorumTests.certify

    def setUp(self):
        admitted.AdmittedQuorumTests.setUp(self)
        peer = next(d for d in self.witnesses if d['principal'] != self.f.creator['principal'])
        retained = {self.f.creator['principal'], peer['principal']}
        pairs = [(d, p) for d, p in zip(self.f.devices, self.f.proofs) if d['principal'] in retained]
        self.f.devices = [d for d, _ in pairs]
        self.f.proofs = [p for _, p in pairs]
        self.f.bundles = {p: b for p, b in self.f.bundles.items() if p in retained}
        self.principals = sorted(retained)
        self.witnesses = [d for d in self.witnesses if d['principal'] in retained]
        self.f.context['ordering']['witnesses'] = [w for w in self.f.context['ordering']['witnesses'] if w['principal'] in retained]
        self.devices = [{k: d[k] for k in ('principal', 'device')} for d in self.f.devices]
        self.identity, self.sender, self.selected = self.endpoint('two-principal-creator')
        self.release = InitialRosterRelease(self.sender)
        self.join()

    def prepare_message(self, delivery, event_id):
        source = next(c['mailbox'] for d, c in zip(self.f.devices, self.selected) if d is self.f.creator)
        targets = sorted({c['mailbox'] for d, c in zip(self.f.devices, self.selected) if d['principal'] != self.f.creator['principal']})
        return self.sender.prepare(delivery, encode_event(self.event(self.f.creator, event_id)), key=self.f.creator['key'], envelope_sender=source, recipients=targets, time=self.time)

    def test_offline_peer_does_not_block_ordinary_encrypted_delivery(self):
        peer = next(g for g in self.groups if g is not self.author_group)
        before = peer.live()
        retained = []
        # No peer receive, vote or MLS processing occurs during either SMTP send.
        with SenderWorker(self.sender) as worker:
            for delivery, event_id in [('offlineone', 'a'), ('offlinetwo', 'b')]:
                self.prepare_message(delivery, event_id)
                smtp = LocalSMTP()
                self.assertEqual(worker.submit(delivery, port=smtp.port, time=self.time)['state'], 'accepted')
                smtp.done()
                retained.append(smtp.wire)
        self.assertEqual(peer.live(), before)
        for wire in retained:
            self.assertEqual(peer.receiver.receive(unpack(wire), time=self.time, trust_policy='allow-unverified')['applicationState'], 'accepted')

    def test_one_witness_cannot_complete_change_and_restart_does_not_clear_hold(self):
        author = self.author_group
        before = author.live()[1]['snapshot']
        index = next(m['index'] for m in before['members'] if m['identity'] == self.removed['identity'])
        candidate = author.stage(ProviderKey(self.provider, self.f.creator), time=self.time, removals=[int(index)])
        scope = candidate['plan']['scope']
        self.assertEqual(len(scope['ordering']['witnesses']), 2)
        self.assertEqual(scope['ordering']['faultBound'], '0')
        coordinator = self.witnesses[0]
        proposal = sign(unsigned('proposal', scope_digest(scope), 0, coordinator['principal'] + '|' + coordinator['device'], candidate=candidate_id(candidate), newView=''), ProviderKey(self.provider, coordinator))
        # The coordinator alone can prepare; duplicating its vote is not q=2.
        group = self.groups[0]
        store = VoteStore(self.root / 'one-witness.sqlite', scope=scope_digest(scope), keys=group.keys(), f=0, signer=coordinator['principal'] + '|' + coordinator['device'], key=ProviderKey(self.provider, coordinator), create=True)
        vote_raw = group.vote(store, 'prepare', bundle(digest(proposal), [proposal]), candidate, time=self.time)
        vote = json.loads(vote_raw)
        objects = [proposal, vote]
        prepared = sign(unsigned('prepared', scope_digest(scope), 0, coordinator['principal'] + '|' + coordinator['device'], proposal=digest(proposal), prepares=[digest(vote), digest(vote)]), ProviderKey(self.provider, coordinator))
        with self.assertRaisesRegex(ValueError, 'quorum list'):
            Proof(bundle(digest(prepared), objects + [prepared]), scope=scope_digest(scope), keys=group.keys(), f=0)
        with self.assertRaisesRegex(ValueError, 'Observed proposals'):
            self.prepare_message('heldbefore', 'c')
        # Reconstruct the real checkpoint adapter; no observation rows are erased.
        reopened = AdmittedQuorum(self.sender.receiver, self.worker, self.f.creator)
        self.assertEqual(reopened.live()[1]['snapshot']['predecessor'], before['predecessor'])
        with patch('sender_worker.smtplib.SMTP') as smtp:
            with self.assertRaisesRegex(ValueError, 'Observed proposals'):
                self.prepare_message('heldrestart', 'd')
            smtp.assert_not_called()
        # Once the second endpoint participates, a full certificate advances MLS.
        proof = self.certify(candidate)
        for current in self.groups:
            current.install(candidate, proof, time=self.time)
        self.assertNotEqual(author.live()[1]['snapshot']['predecessor'], before['predecessor'])
        self.send(self.f.creator, 'e')

    def test_addition_can_hold_sender_before_any_peer_processes_candidate(self):
        import base64
        from provider_mls import advertisement, make_device, sign as sign_advertisement
        from quorum_join_support import confirm

        author = self.author_group
        peer = next(g for g in self.groups if g is not author)
        before_peer = peer.live()
        newcomer = make_device(self.provider, 7, 8)
        self.identity.observe(newcomer['record'], first_contact_policy='allow-unverified')
        wrapper = advertisement(self.provider, newcomer, 'newjoiner@example.invalid')
        value = json.loads(base64.b64decode(wrapper['payload']))
        value.update(version='6', applications=[dict(self.f.context['application'], ordering='endpoint-quorum-v0')])
        raw = encode_event(value)
        wrapper.update(payload=base64.b64encode(raw).decode(), signature=sign_advertisement(self.provider, newcomer, 'email-next/passive-discovery/v6', raw))
        confirm(author, encode_event(wrapper), time=self.time)
        self.prepare_message('beforeaddition', 'a')
        candidate = author.stage(ProviderKey(self.provider, self.f.creator), time=self.time, packages=[newcomer['package']])
        self.assertEqual(author.db.execute('SELECT proposal_count FROM qo_proposal_observation').fetchone()[0], 1)
        self.assertEqual(peer.live(), before_peer)
        self.assertEqual(peer.db.execute('SELECT count(*) FROM qo_proposal_observation').fetchone()[0], 0)
        with self.assertRaisesRegex(ValueError, 'Observed proposals'):
            self.prepare_message('additionheld', 'f')
        self.assertEqual(candidate['plan']['scope']['predecessor'], author.live()[1]['snapshot']['predecessor'])


if __name__ == '__main__':
    unittest.main()
