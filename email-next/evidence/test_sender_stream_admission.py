"""Owner admission joined to real signed roster/Welcome and receive effects."""
import base64
import hashlib
import json
import sqlite3
import unittest

from event_encoding import encode_event
from initial_roster import parse
from initial_roster_lifecycle import InitialRosterAdmission
from invitation_mime import select
from mls_receive import MlsReceive
from provider_mls import call, sign
from sender_stream_admission import SenderStreamAdmission, MODE
import test_initial_roster_lifecycle as fixtures


class SenderStreamAdmissionTests(unittest.TestCase):
    application = dict(envelopeVersion='1', payload='raw-event-v0', operations=['message'])
    endpoint = fixtures.RosterLifecycleTests.endpoint
    prepare = fixtures.RosterLifecycleTests.prepare
    tearDown = fixtures.RosterLifecycleTests.tearDown

    def setUp(self):
        fixtures.RosterLifecycleTests.setUp(self)
        if getattr(self, 'enrolled_creator', False):
            self.f.creator = next(d for d in self.f.devices if d['principal'] == self.f.creator['principal'] and d is not self.f.creator)
            self.f.context['ordering']['device'] = self.f.creator['device']
        self.wires = self.prepare()
        self.owner = {k: self.f.creator[k] for k in ('principal', 'device')}
        self.owner['signingKey'] = self.f.creator['key']
        self.peer = next(d for d in self.f.devices if d['principal'] != self.f.creator['principal'])
        self.identity2, self.sender2, self.selected2 = self.endpoint('stream-recipient')
        self.admission = InitialRosterAdmission(self.identity2, self.f.binary)
        self.admission.publish_local(self.peer)
        self.streams = SenderStreamAdmission(self.admission, configured=True)
        self.raw, self.args = self.selection(self.peer, self.selected2)

    def selection(self, target, selected):
        raw = next(select(w) for w in self.wires.values() if parse(select(w))['value']['target']['device'] == target['device'])
        parsed = parse(raw)
        choices = [dict(principal=d['principal'], device=d['device'], mailbox=c['mailbox'], generation=c['generation']) for d, c in zip(self.f.devices, selected)]
        args = dict(target=target, mailbox=parsed['value']['target']['mailbox'], allow_creator=self.f.creator['principal'], intended_principals=self.principals, intended_devices=self.devices, expected_context=encode_event(self.f.context), selections=choices, time=self.time, trust_policy='allow-unverified')
        return raw, args

    def accept(self, **overrides):
        args = dict(stream='3' * 32, owner=self.owner, **self.args)
        args.update(overrides)
        return self.streams.accept(self.raw, **args)

    def event(self, device, event_id):
        return dict(version='1', purpose='contribution', event=event_id, conversation=self.f.context['conversation'], principal=device['principal'], audience=self.principals, disclosures=[], operation=dict(kind='message', text='Owner-bound contribution', replyTo=[]))

    def encrypt(self, identity, device, event_id):
        row = identity.db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
        result = call(self.f.binary, op='send', checkpoint=json.loads(row[1]), group=row[0], key=device['key'], application=encode_event(self.event(device, event_id)).hex())
        identity.db.execute('UPDATE mls_checkpoint SET revision=revision+1,snapshot=? WHERE id=1', (json.dumps(result['checkpoint']).encode(),))
        return bytes.fromhex(result['wire'])

    def test_signed_owner_binding_and_actual_admission_are_retained_together(self):
        result = self.accept()
        self.assertEqual(result['mode'], MODE)
        binding = self.streams.retained('3' * 32)
        parsed = parse(self.raw)
        self.assertEqual(binding['anchor'], parsed['anchor'])
        self.assertEqual(binding['owner']['signingKey'], self.f.creator['key'])
        self.assertEqual(binding['group'], result['admission']['group'])
        self.assertEqual(binding['contextDigest'], hashlib.sha256(parsed['context_raw']).hexdigest())
        self.assertEqual(self.accept(), result)
        self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM sender_stream_admissions').fetchone()[0], 1)

    def test_wrong_owner_and_unsigned_stream_name_cannot_consume_package(self):
        wrong = dict(principal=self.peer['principal'], device=self.peer['device'], signingKey=self.peer['key'])
        with self.assertRaisesRegex(ValueError, 'selected stream owner'):
            self.accept(owner=wrong)
        with self.assertRaisesRegex(ValueError, 'signed stream identifier'):
            self.accept(stream='4' * 32)
        self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0], 0)
        self.assertIsNone(self.identity2.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])
        self.accept()

    def test_binding_retention_failure_rolls_back_mls_and_package_consumption(self):
        self.identity2.db.execute("CREATE TEMP TRIGGER fail_stream BEFORE INSERT ON sender_stream_admissions BEGIN SELECT RAISE(ABORT,'binding retention failure'); END")
        with self.assertRaisesRegex(sqlite3.IntegrityError, 'binding retention failure'):
            self.accept()
        for table in ('mls_checkpoint', 'mls_group_instances', 'initial_rosters', 'initial_roster_received', 'sender_stream_admissions'):
            self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM ' + table).fetchone()[0], 0)
        self.assertIsNone(self.identity2.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])
        self.identity2.db.execute('DROP TRIGGER fail_stream')
        self.accept()

    def test_before_commit_crash_exposes_neither_admission_nor_binding(self):
        def crash(point):
            self.assertEqual(point, 'before-commit')
            raise RuntimeError('simulated caller crash')
        with self.assertRaisesRegex(RuntimeError, 'simulated caller crash'):
            self.accept(crash=crash)
        self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0], 0)
        self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM sender_stream_admissions').fetchone()[0], 0)
        self.accept()

    def test_non_owner_never_promotes_and_valid_owner_message_still_arrives(self):
        self.accept()
        attacker = next(d for d in self.f.devices if d['principal'] not in (self.f.creator['principal'], self.peer['principal']))
        attacker_identity, _, selected = self.endpoint('attacker-member')
        admission = InitialRosterAdmission(attacker_identity, self.f.binary)
        admission.publish_local(attacker)
        raw, args = self.selection(attacker, selected)
        admission.accept_message(raw, **args)
        malicious = self.encrypt(attacker_identity, attacker, 'a' * 32)
        received = self.sender2.receiver.receive(malicious, time=self.time, trust_policy='allow-unverified')
        self.assertEqual(received['status'], 'stream-owner-mismatch')
        self.assertEqual(received['applicationState'], 'held:stream-owner-mismatch')
        self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM contributions').fetchone()[0], 0)
        restarted = MlsReceive(self.identity2, self.f.binary.with_name('receive-staged'))
        restarted.reevaluate(time=self.time, trust_policy='allow-unverified')
        self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM contributions').fetchone()[0], 0)
        good = self.encrypt(self.identity, self.f.creator, 'b' * 32)
        accepted = restarted.receive(good, time=self.time, trust_policy='allow-unverified')
        self.assertEqual(accepted['applicationState'], 'accepted')
        self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM contributions').fetchone()[0], 1)

    def test_configured_mode_cannot_be_selected_by_mail_or_nested_transaction(self):
        with self.assertRaisesRegex(ValueError, 'Explicit configured'):
            SenderStreamAdmission(self.admission)
        self.identity2.db.execute('BEGIN IMMEDIATE')
        try:
            with self.assertRaisesRegex(ValueError, 'transaction ownership'):
                self.accept()
            self.assertTrue(self.identity2.db.in_transaction)
        finally:
            self.identity2.db.execute('ROLLBACK')
        with self.assertRaisesRegex(ValueError, 'transaction required'):
            self.admission._accept_message_locked(self.raw, **self.args)

    def test_missing_binding_holds_instead_of_reverting_to_member_authorship(self):
        self.accept()
        self.identity2.db.execute('DELETE FROM sender_stream_admissions')
        wire = self.encrypt(self.identity, self.f.creator, 'c' * 32)
        received = self.sender2.receiver.receive(wire, time=self.time, trust_policy='allow-unverified')
        self.assertEqual(received['status'], 'stream-binding-held')
        self.assertEqual(received['applicationState'], 'held:stream-binding-held')
        self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM contributions').fetchone()[0], 0)
        self.accept()
        self.sender2.receiver.reevaluate(time=self.time, trust_policy='allow-unverified')
        self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM contributions').fetchone()[0], 1)

    def test_existing_member_conversation_cannot_be_relabelled_owner_bound(self):
        self.admission.accept_message(self.raw, **self.args)
        with self.assertRaisesRegex(ValueError, 'cannot change stream mode'):
            self.accept()
        self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM sender_stream_admissions').fetchone()[0], 0)

    def test_authenticated_competing_binding_holds_new_effects_and_preserves_history(self):
        self.accept()
        first = self.encrypt(self.identity, self.f.creator, 'd' * 32)
        self.assertEqual(self.sender2.receiver.receive(first, time=self.time, trust_policy='allow-unverified')['applicationState'], 'accepted')
        outer = json.loads(self.raw)
        roster = json.loads(base64.b64decode(outer['roster']['payload']))
        value = json.loads(base64.b64decode(outer['payload']))
        roster['notAfter'] = str(int(roster['notAfter']) - 1)
        value['notAfter'] = roster['notAfter']
        roster_raw = encode_event(roster)
        signature = sign(self.f.binary, self.f.creator, 'email-next/mls-initial-roster/v0', roster_raw)
        outer['roster'] = dict(payload=base64.b64encode(roster_raw).decode(), signature=signature)
        value.update(rosterDigest=hashlib.sha256(roster_raw).hexdigest(), rosterSignature=signature)
        value_raw = encode_event(value)
        outer.update(payload=base64.b64encode(value_raw).decode(), signature=sign(self.f.binary, self.f.creator, 'email-next/mls-new-conversation-invitation/v3', value_raw))
        competing = encode_event(outer)
        parse(competing)  # Original creator actually signed both complete rosters.
        with self.assertRaisesRegex(ValueError, 'Authenticated stream binding conflict'):
            self.streams.accept(competing, stream='3' * 32, owner=self.owner, **self.args)
        self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM sender_stream_conflicts').fetchone()[0], 1)
        self.accept()  # Replaying the original receipt cannot clear the hold.
        self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM sender_stream_conflicts').fetchone()[0], 1)
        self.sender2.receiver.reevaluate(time=self.time, trust_policy='allow-unverified')
        self.assertEqual(self.identity2.db.execute('SELECT state FROM mls_application_acceptance').fetchone()[0], 'accepted')
        second = self.encrypt(self.identity, self.f.creator, 'e' * 32)
        outcome = self.sender2.receiver.receive(second, time=self.time, trust_policy='allow-unverified')
        self.assertEqual(outcome['status'], 'stream-binding-conflict')
        self.assertEqual(outcome['applicationState'], 'held:stream-binding-conflict')
        self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM contributions').fetchone()[0], 1)

    def test_unsigned_binding_tamper_cannot_hold_a_valid_stream(self):
        self.accept()
        outer = json.loads(self.raw)
        signature = outer['roster']['signature']
        outer['roster']['signature'] = ('00' if signature[:2] != '00' else '01') + signature[2:]
        with self.assertRaises(ValueError):
            self.streams.accept(encode_event(outer), stream='3' * 32, owner=self.owner, **self.args)
        self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM sender_stream_conflicts').fetchone()[0], 0)
        wire = self.encrypt(self.identity, self.f.creator, 'f' * 32)
        self.assertEqual(self.sender2.receiver.receive(wire, time=self.time, trust_policy='allow-unverified')['applicationState'], 'accepted')

    def process_crash(self, point):
        import os
        import subprocess
        import sys
        from pathlib import Path
        config = Path(self.temp.name) / ('stream-crash-' + point + '.json')
        args = dict(self.args, target={k: self.peer[k] for k in ('principal', 'device', 'identity', 'key')}, expected_context=self.args['expected_context'].hex())
        config.write_text(json.dumps(dict(db=str(Path(self.temp.name) / 'stream-recipient.sqlite'), binary=str(self.f.binary), raw=self.raw.hex(), stream='3' * 32, owner=self.owner, selection=args, point=point)))
        program = """
import json,os,sys
from pathlib import Path
from identity_store import IdentityStore
from initial_roster_lifecycle import InitialRosterAdmission
from sender_stream_admission import SenderStreamAdmission
c=json.loads(Path(sys.argv[1]).read_text())
c['selection']['expected_context']=bytes.fromhex(c['selection']['expected_context'])
identity=IdentityStore(c['db'])
stream=SenderStreamAdmission(InitialRosterAdmission(identity,Path(c['binary'])),configured=True)
def crash(point):
 if point==c['point']:os._exit(73)
stream.accept(bytes.fromhex(c['raw']),stream=c['stream'],owner=c['owner'],crash=crash,**c['selection'])
"""
        env = dict(os.environ)
        env['PYTHONPATH'] = str(Path(__file__).parent.resolve())
        result = subprocess.run([sys.executable, '-c', program, str(config)], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=40)
        self.assertEqual(result.returncode, 73)

    def test_process_death_before_commit_releases_no_partial_admission(self):
        self.process_crash('before-commit')
        for table in ('mls_checkpoint', 'initial_roster_received', 'sender_stream_admissions'):
            self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM ' + table).fetchone()[0], 0)
        self.assertIsNone(self.identity2.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])
        self.accept()

    def test_process_death_after_commit_retries_exact_retained_result(self):
        self.process_crash('after-commit')
        self.assertEqual(self.identity2.db.execute('SELECT count(*) FROM sender_stream_admissions').fetchone()[0], 1)
        before = self.identity2.db.execute('SELECT revision FROM mls_checkpoint').fetchone()[0]
        result = self.accept()
        self.assertEqual(result['binding'], self.identity2.db.execute('SELECT reference FROM sender_stream_admissions').fetchone()[0])
        self.assertEqual(self.identity2.db.execute('SELECT revision FROM mls_checkpoint').fetchone()[0], before)


class EnrolledOwnerAdmissionTests(unittest.TestCase):
    """One signed-admission case with the enrolled sibling as actual creator."""
    enrolled_creator = True
    application = SenderStreamAdmissionTests.application
    setUp = SenderStreamAdmissionTests.setUp
    tearDown = SenderStreamAdmissionTests.tearDown
    endpoint = SenderStreamAdmissionTests.endpoint
    prepare = SenderStreamAdmissionTests.prepare
    selection = SenderStreamAdmissionTests.selection
    accept = SenderStreamAdmissionTests.accept
    test_enrolled_device_is_actual_authenticated_stream_creator = SenderStreamAdmissionTests.test_signed_owner_binding_and_actual_admission_are_retained_together


if __name__ == '__main__':
    unittest.main()
