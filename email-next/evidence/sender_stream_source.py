"""Durable configured stream source, not a current-suite publisher/receiver.

Move an existing, locally created signed initial3 group into exclusive source
ownership. Secret state is local only. Returned bytes are prepared public output,
not a transport release permission. No remote checkpoint installation is exposed.
"""
import hashlib
import json
import time as elapsed_time
from pathlib import Path

from admission_windows import clock
from event_encoding import decode_event, encode_event
from initial_roster import credential, parse, identifier
from initial_roster_lifecycle import canonical
from mls_receive import LockedIdentity
from provider_control import node
from provider_mls import call
from sender_stream_admission import derive, reference

CONTROL = 'configured-sender-stream-control-v0'


def later(interval, started):
    lo, hi = clock(interval)
    elapsed = elapsed_time.monotonic_ns() - started
    if elapsed < 0:raise ValueError('Monotonic clock rollback')
    result = dict(earliest=str(lo + elapsed // 1000000000), latest=str(hi + (elapsed + 999999999) // 1000000000))
    clock(result)
    return result


class SenderStreamSource:
    def __init__(self, identity, binary, *, configured=False):
        if configured is not True or identity.db.in_transaction:
            raise ValueError('Explicit configured source outside transaction required')
        self.identity = identity
        self.db = identity.db
        self.binary = Path(binary)
        self.transitions = self.binary.with_name('group-transitions')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS stream_source(stream TEXT PRIMARY KEY,group_id TEXT UNIQUE NOT NULL,binding BLOB NOT NULL,reference TEXT NOT NULL,checkpoint BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS stream_source_outbox(stream TEXT NOT NULL,id TEXT NOT NULL,request BLOB NOT NULL,wire BLOB NOT NULL,kind TEXT NOT NULL,PRIMARY KEY(stream,id));
        CREATE TABLE IF NOT EXISTS stream_source_events(principal TEXT NOT NULL,conversation TEXT NOT NULL,event TEXT NOT NULL,bytes BLOB NOT NULL,PRIMARY KEY(principal,conversation,event));''')

    def _transaction(self, work, crash):
        if self.db.in_transaction:
            raise ValueError('Source transaction ownership required')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            result = work()
            if crash:crash('before-commit')
            self.db.execute('COMMIT')
            if crash:crash('after-commit')
            return result
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise

    def _current(self, snapshot, owner, time):
        settings = self.db.execute('SELECT policy FROM sender_policy WHERE id=1').fetchone()
        policy = json.loads(settings[0]) if settings else {}
        if policy.get('trustPolicy') != 'allow-unverified' or policy.get('verificationMechanism'):
            raise ValueError('Configured source does not implement this verification policy')
        identity = LockedIdentity(self.identity)
        dependencies = []
        for member in snapshot['members']:
            checked = identity.check_device(bytes.fromhex(member['identity']), bytes.fromhex(member['key']), role='send' if member['identity'] == credential(owner) else 'receive', time=time, trust_policy='allow-unverified')
            if checked.get('status') != 'authorized-unverified':
                raise ValueError('Current source or recipient authority held')
            dependencies.append(dict(identity=member['identity'],key=member['key'],**checked))
        return dependencies

    def _inspect(self, binding, checkpoint):
        owner = binding['owner']
        actual = call(self.binary, op='inspect-send', checkpoint=checkpoint, key=owner['signingKey'], group=binding['group'])['metadata']
        if actual['senderIdentity'] != credential(owner) or actual['senderKey'] != owner['signingKey'] or hashlib.sha256(bytes.fromhex(actual['context'])).hexdigest() != binding['contextDigest'] or sorted({ 'enp0:' + bytes.fromhex(m['identity'])[21:53].hex() for m in actual['members'] }) != binding['audience']:
            raise ValueError('Actual source owner/context/audience mismatch')
        return actual

    def adopt_created(self, octets, *, device, time, crash=None):
        """Move only this database's locally created initial checkpoint.

        The owning initial creation already checked mailbox/policy/package support.
        Only ordinary historical context3 is supported by this experiment. This
        API cannot accept an incoming secret snapshot or relabel a receiver.
        """
        selected_time = dict(time)
        clock(selected_time)
        started = elapsed_time.monotonic_ns()
        parsed = parse(octets)
        owner = dict(principal=device['principal'], device=device['device'], signingKey=device['key'])
        binding = derive(parsed, owner)
        if parsed['context']['version'] != '3':raise ValueError('Configured ordinary context3 required')
        raw = canonical(binding)
        def work():
            old = self.db.execute('SELECT binding FROM stream_source WHERE stream=?', (binding['stream'],)).fetchone()
            if old:
                if old[0] != raw:raise ValueError('Source binding conflict')
                return binding['stream']
            creation = self.db.execute('SELECT anchor,role FROM initial_rosters WHERE creation=?', (binding['stream'],)).fetchone()
            instance = self.db.execute('SELECT instance FROM mls_checkpoint_instance WHERE id=1').fetchone()
            row = self.db.execute('SELECT group_id,snapshot,revision FROM mls_checkpoint WHERE id=1').fetchone()
            if creation != (binding['anchor'], 'creator') or instance != (binding['anchor'],) or row is None or row[0] != binding['group']:
                raise ValueError('Exclusive locally created checkpoint required')
            if row[2] != 0:
                raise ValueError('Only an unused initial source can select this configured mode')
            for table in ('sender_prepared','control_prepared','plaintext_prepared','mls_receives','gt_candidate','gt_decision','gt_outbox','qo_checkpoint','qo_staged'):
                if self.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone() and self.db.execute('SELECT 1 FROM '+table+' LIMIT 1').fetchone():
                    raise ValueError('Existing prepared or received traffic cannot change source mode')
            checkpoint = json.loads(row[1])
            actual = self._inspect(binding, checkpoint)
            observed = call(self.transitions, op='inspect', checkpoint=checkpoint, key=device['key'], group=binding['group'])['snapshot']
            expected_members = sorted((credential(m), m['signingKey']) for m in parsed['roster']['members'])
            if observed['epoch'] != '1' or hashlib.sha256(bytes.fromhex(observed['predecessor'])).hexdigest() != parsed['roster']['resultGroupContextDigest'] or sorted((m['identity'],m['key']) for m in observed['members']) != expected_members:
                raise ValueError('Exact original source state required')
            self._current(actual, binding['owner'], later(selected_time, started))
            self.db.execute('INSERT INTO stream_source VALUES(?,?,?,?,?)', (binding['stream'], binding['group'], raw, reference(binding), row[1]))
            self.db.execute('DELETE FROM mls_checkpoint WHERE id=1')
            self.db.execute('DELETE FROM mls_checkpoint_instance WHERE id=1')
            self.db.execute("UPDATE mls_group_instances SET provenance='configured-exclusive-stream-source-v0' WHERE instance=?", (binding['anchor'],))
            return binding['stream']
        return self._transaction(work, crash)

    def _live(self, stream):
        row = self.db.execute('SELECT binding,reference,checkpoint FROM stream_source WHERE stream=?', (stream,)).fetchone()
        if row is None:raise ValueError('Unknown source stream')
        binding = json.loads(row[0])
        if reference(binding) != row[1]:raise ValueError('Source binding integrity')
        marker = self.db.execute('SELECT provenance,status FROM mls_group_instances WHERE instance=? AND group_id=?',(binding['anchor'],binding['group'])).fetchone()
        if marker != ('configured-exclusive-stream-source-v0','active'):raise ValueError('Inactive or unbound source instance')
        return binding, json.loads(row[2])

    def prepare(self, stream, ident, *, time, application=None, crash=None):
        """Atomically prepare a root message or owner self-update and its outbox.

        application=None selects an empty self-update. Membership/recipient Update
        controls are deliberately unsupported, rather than treated as empty.
        """
        selected_time = dict(time)
        clock(selected_time)
        started = elapsed_time.monotonic_ns()
        identifier(ident)
        if application is not None and not isinstance(application,bytes):raise TypeError('Exact application bytes required')
        kind = 'owner-self-update' if application is None else 'root-message'
        request = canonical(dict(kind=kind,application='' if application is None else application.hex()))
        def work():
            binding, checkpoint = self._live(stream)
            old = self.db.execute('SELECT request,wire FROM stream_source_outbox WHERE stream=? AND id=?', (stream,ident)).fetchone()
            if old:
                if old[0] != request:raise ValueError('Immutable source operation conflict')
                return old[1] # Historical bytes only, not current release permission.
            current = self._inspect(binding, checkpoint)
            self._current(current, binding['owner'], selected_time)
            key = binding['owner']['signingKey']
            if application is None:
                result = call(self.transitions, op='candidate', checkpoint=checkpoint, group=binding['group'], key=key, packages=[])
                if result['sender'] != credential(binding['owner']) or result['proposalCount'] != 0 or result['welcome'] is not None or result['before']['context'] != result['after']['context'] or result['before']['members'] != result['after']['members']:
                    raise ValueError('Exact owner empty self-update required')
                wire = encode_event(dict(version='0',purpose=CONTROL,stream=stream,binding=reference(binding),group=binding['group'],predecessor=result['before']['predecessor'],result=result['after']['predecessor'],commit=result['wire']))
                advanced = result['checkpoint'] # Already merged successor, never a competing staged predecessor.
            else:
                event = decode_event(application)['value']
                module = Path(__file__).resolve().parent
                script = "import {validateEnvelopeShape} from '"+(module/'event-envelope.mjs').as_uri()+"';import {isPrincipalId} from '"+(module/'principal-identifiers.mjs').as_uri()+"';let t='';for await(const c of process.stdin)t+=c;process.stdout.write(JSON.stringify(validateEnvelopeShape(JSON.parse(t),isPrincipalId)));"
                if not node(script,event) or event['version'] != '1' or event['principal'] != binding['owner']['principal'] or event['conversation'] != binding['conversation'] or event['audience'] != binding['audience'] or event['disclosures'] != [] or event['operation']['kind'] != 'message' or event['operation']['replyTo'] != [] or 'message' not in binding['application']['operations'] or binding['application']['payload'] != 'raw-event-v0':
                    raise ValueError('Configured exact root-message agreement required')
                old_event = self.db.execute('SELECT bytes FROM stream_source_events WHERE principal=? AND conversation=? AND event=?',(event['principal'],event['conversation'],event['event'])).fetchone()
                if old_event and old_event[0] != application:raise ValueError('Immutable event conflict')
                if old_event:raise ValueError('Existing event requires exact retained delivery')
                result = call(self.binary, op='send', checkpoint=checkpoint, group=binding['group'], key=key, application=application.hex())
                advanced = result['checkpoint'];wire = bytes.fromhex(result['wire'])
                self.db.execute('INSERT INTO stream_source_events VALUES(?,?,?,?)',(event['principal'],event['conversation'],event['event'],application))
            advanced_metadata = self._inspect(binding, advanced)
            self._current(advanced_metadata, binding['owner'], later(selected_time, started))
            self.db.execute('UPDATE stream_source SET checkpoint=? WHERE stream=?',(canonical(advanced),stream))
            self.db.execute('INSERT INTO stream_source_outbox VALUES(?,?,?,?,?)',(stream,ident,request,wire,kind))
            return wire
        return self._transaction(work, crash)
