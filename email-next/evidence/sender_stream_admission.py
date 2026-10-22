"""Configured owner binding around real signed initial-roster admission.

The accepted historical wire formats are unchanged. A trusted caller explicitly
selects this experiment and its owner; received mail cannot select the mode.
This is not a context8 stream advertisement or complete multi-stream client.
"""
import hashlib
import json

from initial_roster import credential, parse
from initial_roster_lifecycle import InitialRosterAdmission, canonical
from provider_control import exact

MODE = 'configured-sender-stream-experiment'
DOMAIN = b'email2/sender-stream-binding-experiment/v0\0'


def derive(parsed, owner):
    exact(owner, {'principal', 'device', 'signingKey'})
    roster = parsed['roster']
    context = parsed['context']
    creator = next(m for m in roster['members'] if m['kind'] == 'creator')
    actual = {k: creator[k] for k in owner}
    expected_ordering = dict(kind='designated-member-v0', principal=owner['principal'], device=owner['device'])
    if actual != owner or context['ordering'] != expected_ordering or context['administrators'] != [owner['principal']]:
        raise ValueError('Exact independently selected stream owner required')
    # The binding contains only values covered by the original creator's signed
    # common roster. No new owner statement or invitation wrapper is invented.
    return dict(version='0', purpose=MODE, stream=roster['creation'], conversation=roster['conversation'], group=parsed['group'].hex(), anchor=parsed['anchor'], rosterDigest=hashlib.sha256(parsed['roster_raw']).hexdigest(), contextDigest=hashlib.sha256(parsed['context_raw']).hexdigest(), owner={k: creator[k] for k in ('principal', 'device', 'signingKey', 'state', 'binding')}, audience=roster['intendedPrincipals'], application=context['application'], delivery=context.get('delivery', {'kind': 'ordinary-v0'}))


def reference(binding):
    raw = canonical(binding)
    return hashlib.sha256(DOMAIN + len(raw).to_bytes(4, 'big') + raw).hexdigest()


class SenderStreamAdmission:
    def __init__(self, admission, *, configured=False):
        if type(admission) is not InitialRosterAdmission or configured is not True:
            raise ValueError('Explicit configured initial-admission experiment required')
        self.admission = admission
        self.db = admission.db
        if self.db.in_transaction:
            raise ValueError('Initialize outside transaction')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS sender_stream_admissions(stream TEXT PRIMARY KEY,group_id TEXT UNIQUE NOT NULL,anchor TEXT NOT NULL,binding BLOB NOT NULL,reference TEXT NOT NULL,result BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS sender_stream_conflicts(stream TEXT NOT NULL,owner TEXT NOT NULL,reference TEXT NOT NULL,wire BLOB NOT NULL,binding BLOB NOT NULL,PRIMARY KEY(stream,owner,reference));''')

    def accept(self, octets, *, stream, owner, crash=None, **selection):
        if self.db.in_transaction:
            raise ValueError('Stream admission requires transaction ownership')
        parsed = parse(octets)
        binding = derive(parsed, owner)
        if stream != binding['stream']:
            raise ValueError('Exact signed stream identifier required')
        if selection.get('allow_creator') != owner['principal']:
            raise ValueError('Independently selected creator required')
        raw = canonical(binding)
        digest = reference(binding)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old = self.db.execute('SELECT binding,reference,result FROM sender_stream_admissions WHERE stream=?', (stream,)).fetchone()
            if old and old[:2] != (raw, digest):
                original = json.loads(old[0])
                if all(original['owner'][k] == binding['owner'][k] for k in ('principal', 'device', 'signingKey')):
                    # Retain the owner's signed contradiction even though the
                    # proposed admission is refused. No package or live group
                    # state is installed by this conflict-only transaction.
                    self.db.execute('INSERT OR IGNORE INTO sender_stream_conflicts VALUES(?,?,?,?,?)', (stream, credential(owner), digest, octets, raw))
                    self.db.execute('COMMIT')
                    raise ValueError('Authenticated stream binding conflict')
                raise ValueError('Configured stream identifier collision')
            existing = self.db.execute('SELECT 1 FROM initial_roster_received WHERE creator=? AND id=?', (owner['principal'], parsed['value']['invitation'])).fetchone()
            marker = self.db.execute('SELECT provenance FROM mls_group_instances WHERE instance=? AND group_id=?', (binding['anchor'], binding['group'])).fetchone()
            if existing and not old and (not marker or marker[0] != MODE):
                raise ValueError('Existing admission cannot change stream mode')
            # Signature, current authority, exact independently selected audience,
            # target package, actual MLS signer/result and mailbox checks remain
            # inside the same transaction as this additional owner binding.
            admitted = self.admission._accept_message_locked(octets, **selection)
            result = dict(binding=digest, stream=stream, owner=credential(owner), admission=admitted, mode=MODE)
            if old:
                if old[2] != canonical(result):
                    raise ValueError('Retained stream admission result conflict')
            else:
                self.db.execute('INSERT INTO sender_stream_admissions VALUES(?,?,?,?,?,?)', (stream, binding['group'], binding['anchor'], raw, digest, canonical(result)))
            self.db.execute('UPDATE mls_group_instances SET provenance=? WHERE instance=? AND group_id=?', (MODE, binding['anchor'], binding['group']))
            if crash:
                crash('before-commit')
            self.db.execute('COMMIT')
            if crash:
                crash('after-commit')
            return result
        except BaseException:
            if self.db.in_transaction:
                self.db.execute('ROLLBACK')
            raise

    def retained(self, stream):
        """Return historical provenance, never a current send/receive permission."""
        row = self.db.execute('SELECT binding,reference FROM sender_stream_admissions WHERE stream=?', (stream,)).fetchone()
        if row is None:
            raise ValueError('Unknown stream')
        binding = json.loads(row[0])
        if reference(binding) != row[1]:
            raise ValueError('Retained binding integrity')
        return binding


def owner_guard(db, processed, snapshot, *, historical=False):
    """Guard configured owner-bound groups before receive and every promotion.

    Absent configuration preserves historical profiles. A stored binding grants
    no current role: ordinary cryptographic/identity/audience checks still run.
    """
    has_instances = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='mls_group_instances'").fetchone()
    marked = has_instances and db.execute('SELECT instance FROM mls_group_instances WHERE group_id=? AND provenance=?', (processed['group'], MODE)).fetchone()
    if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='sender_stream_admissions'").fetchone():
        return 'stream-binding-held' if marked else None
    row = db.execute('SELECT binding,reference,anchor FROM sender_stream_admissions WHERE group_id=?', (processed['group'],)).fetchone()
    if row is None:
        return 'stream-binding-held' if marked else None
    if not marked or marked[0] != row[2]:
        return 'stream-binding-held'
    try:
        binding = json.loads(row[0])
        if reference(binding) != row[1] or binding['anchor'] != row[2] or snapshot['group'] != binding['group'] or hashlib.sha256(bytes.fromhex(snapshot['context'])).hexdigest() != binding['contextDigest']:
            return 'stream-binding-held'
        if not historical and db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='sender_stream_conflicts'").fetchone() and db.execute('SELECT 1 FROM sender_stream_conflicts WHERE stream=? AND owner=?', (binding['stream'], credential(binding['owner']))).fetchone():
            return 'stream-binding-conflict'
        member = [item.split(':') for item in snapshot['members'] if item.split(':')[0] == processed['sender']]
        if len(member) != 1 or member[0][1:] != [credential(binding['owner']), binding['owner']['signingKey']] or processed['credential'] != credential(binding['owner']):
            return 'stream-owner-mismatch'
    except (ValueError, TypeError, KeyError, IndexError):
        return 'stream-binding-held'
    return None
