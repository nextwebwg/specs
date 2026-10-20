"""Exact-byte journal experiment. Callers authenticate and authorize before append.

Storage success does not authenticate content, validate an operation, or authorize
an external effect. Original protection/context evidence must be retained by the
caller; this bounded experiment stores only decoded contribution bytes.
"""
import hashlib
import json
import sqlite3
from event_encoding import decode_event

class ContributionJournal:
    def __init__(self, path=None, *, connection=None):
        if connection is not None and connection.in_transaction:
            raise ValueError("Initialize journal outside a caller transaction")
        self._owns_connection = connection is None
        self.db = connection if connection is not None else sqlite3.connect(path, isolation_level=None)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('''CREATE TABLE IF NOT EXISTS contributions (
            conversation TEXT NOT NULL, principal TEXT NOT NULL, event TEXT NOT NULL,
            octets BLOB NOT NULL,
            PRIMARY KEY(conversation, principal, event, octets))''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS derived_views (
            conversation TEXT NOT NULL, name TEXT NOT NULL,
            source_token TEXT NOT NULL, payload TEXT NOT NULL,
            PRIMARY KEY(conversation, name))''')

    def close(self):
        if self._owns_connection:self.db.close()

    def append_validated(self, octets, reference):
        """Caller supplies an independently validated exact identity, never a header hint."""
        self.db.execute('BEGIN IMMEDIATE')
        try:
            result=self.append_validated_in_transaction(octets,reference)
            self.db.execute('COMMIT')
            return result
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def append_validated_in_transaction(self, octets, reference):
        """Trusted coordinator only; caller owns commit/rollback and authorization."""
        if not self.db.in_transaction:raise ValueError('Caller transaction required')
        value = decode_event(octets)['value']
        fields = ('conversation', 'principal', 'event')
        if (not isinstance(reference, dict) or set(reference) != set(fields) or
            not isinstance(value, dict) or
            any(not isinstance(reference[k], str) or not reference[k] or
                value.get(k) != reference[k] for k in fields)):
            raise ValueError('Validated reference does not match stored bytes')
        identity = tuple(reference[k] for k in fields)
        found = self.db.execute('SELECT octets FROM contributions WHERE conversation=? AND principal=? AND event=?', identity).fetchall()
        duplicate = any(row[0] == octets for row in found)
        if not duplicate:
            self.db.execute('INSERT INTO contributions VALUES(?,?,?,?)', (*identity, octets))
        count = len(found) + int(not duplicate)
        return {'state': 'conflict' if count > 1 else 'duplicate' if duplicate else 'stored'}

    def snapshot_with_token(self, conversation):
        # One SELECT supplies a consistent snapshot; callers evaluate it without
        # further live reads, then serialize any later durable effects separately.
        rows = self.db.execute('SELECT principal,event,octets FROM contributions WHERE conversation=? ORDER BY principal,event,octets', (conversation,)).fetchall()
        digest = hashlib.sha256(b'email-next/local-journal-snapshot/v0\0')
        for value in [conversation.encode('utf-8')]:
            digest.update(len(value).to_bytes(8,'big')); digest.update(value)
        grouped = {}
        for principal, event, octets in rows:
            for value in (principal.encode('utf-8'), event.encode('utf-8'), octets):
                digest.update(len(value).to_bytes(8,'big')); digest.update(value)
            grouped.setdefault((principal,event), []).append(octets)
        records = [dict(reference=dict(conversation=conversation,principal=principal,event=event),
                     state='conflict' if len(variants)>1 else 'recorded', octets=variants)
                for (principal,event), variants in grouped.items()]

        return {'token':digest.hexdigest(), 'records':records}

    def snapshot(self, conversation):
        return self.snapshot_with_token(conversation)['records']

    def install_view(self, conversation, name, source_token, payload):
        """Save a local cache only if its source is still current.

        The write transaction excludes concurrent journal writers between the
        token comparison and installation. This does not validate the projection
        or serialize authorization records held in another database.
        """
        serialized = json.dumps(payload, allow_nan=False)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            current = self.snapshot_with_token(conversation)['token']
            if current != source_token:
                self.db.execute('ROLLBACK')
                return {'state': 'stale'}
            self.db.execute('''INSERT INTO derived_views VALUES(?,?,?,?)
                ON CONFLICT(conversation,name) DO UPDATE SET
                source_token=excluded.source_token,payload=excluded.payload''',
                (conversation, name, source_token, serialized))
            self.db.execute('COMMIT')
            return {'state': 'installed'}
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def read_view(self, conversation, name):
        """A cache is usable only while its exact journal snapshot still matches."""
        self.db.execute('BEGIN')
        try:
            row = self.db.execute(
                'SELECT source_token,payload FROM derived_views WHERE conversation=? AND name=?',
                (conversation, name)).fetchone()
            token = self.snapshot_with_token(conversation)['token']
            result = ({'state': 'missing'} if row is None else
                      {'state': 'stale'} if row[0] != token else
                      {'state': 'current', 'sourceToken': token, 'payload': json.loads(row[1])})
            self.db.execute('COMMIT')
            return result
        except BaseException:
            self.db.execute('ROLLBACK')
            raise
