"""Configured local service experiment; no public acquisition or full PKIX claim."""
from contextlib import contextmanager, closing
import hashlib
import json
import sqlite3
import time
from pathlib import Path
from event_encoding import encode_event
from service_answer import decode_request, bind_result

class ServiceStore:
    def __init__(self, path, tokens, clock=time.time, *, deferred=False):
        self.path = str(path)
        self.deferred = deferred
        self.tokens = tokens  # digest -> independently provisioned authorization
        self.clock = clock
        if not Path(path).is_file():
            raise RuntimeError('missing provisioned database')
        with self.connect() as db:
            if db.execute('SELECT version FROM provisioned').fetchone() != (0,):
                raise RuntimeError('unprovisioned database')

    @contextmanager
    def connect(self):
        db = sqlite3.connect('file:' + self.path + '?mode=rw', uri=True, timeout=5)
        try:
            db.execute('PRAGMA synchronous=FULL')
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def provision(path, action):
        # Exclusive creation: loss/restart must not recreate an existing action.
        with open(path, 'xb'): pass
        with closing(sqlite3.connect(path)) as db, db:
            db.executescript('''CREATE TABLE provisioned(version INTEGER);
            INSERT INTO provisioned VALUES(0);
            CREATE TABLE action(data TEXT NOT NULL);
            CREATE TABLE submissions(principal TEXT, action TEXT, submission TEXT,
              raw BLOB NOT NULL, result BLOB NOT NULL,
              PRIMARY KEY(principal,action,submission));
            CREATE TABLE current(principal TEXT PRIMARY KEY, submission TEXT, option TEXT);
            CREATE TABLE effects(submission TEXT, principal TEXT, option TEXT, PRIMARY KEY(principal,submission));''')
            db.execute('INSERT INTO action VALUES(?)', (json.dumps(action),))

    def authorized(self, token, action, scope):
        try: digest = hashlib.sha256(token.encode('ascii')).hexdigest()
        except (UnicodeError, AttributeError): return None, 401
        grant = self.tokens.get(digest)
        now = int(self.clock())
        if not grant or grant['issuer'] != 'fixture' or grant['audience'] != action['service'] or not grant['start'] <= now <= grant['end']:
            return None, 401
        if scope not in grant['scopes']:
            return None, 403
        if grant['principal'] not in action['principals']:
            return None, 403
        return grant['principal'], 200

    def action(self):
        with self.connect() as db:
            return json.loads(db.execute('SELECT data FROM action').fetchone()[0])

    def submit(self, raw, token, *, crash=None):
        action = self.action()
        principal, status = self.authorized(token, action, 'submit')
        if status != 200: return status, b''
        try: request = decode_request(raw)['value']
        except (ValueError, TypeError): return 400, b''
        if request['principal'] != principal or request['action'] != action['action'] or request['question'] != action['question']:
            return 403, b''
        key = (principal, action['action'], request['submission'])
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            # Recheck authorization and time after waiting for the transaction.
            principal, status = self.authorized(token, action, 'submit')
            if status != 200: return status, b''
            existing = db.execute('SELECT raw,result FROM submissions WHERE principal=? AND action=? AND submission=?', key).fetchone()
            if existing:
                return (self.receipt_status(existing[1]), existing[1]) if existing[0] == raw else (409, b'')
            now = int(self.clock())
            if now < action['notBefore']: return 403, b''
            pending = any(json.loads(row[0])['outcome'] == 'pending' for row in db.execute(
                'SELECT result FROM submissions WHERE principal=? AND action=? ORDER BY rowid', (principal, action['action'])))
            receipt = self.decide(db, action, request, raw, wait=self.deferred or pending)
            db.execute('INSERT INTO submissions VALUES(?,?,?,?,?)', (*key, raw, receipt))
            if crash: crash('before-commit')
            db.commit()
            if crash: crash('after-commit')
            return self.receipt_status(receipt), receipt

    @staticmethod
    def receipt_status(raw):
        return 202 if json.loads(raw)['outcome'] == 'pending' else 200

    def decide(self, db, action, request, raw, *, wait=False):
        principal = request['principal']
        current = db.execute('SELECT submission FROM current WHERE principal=?', (principal,)).fetchone()
        outcome, reason = 'confirmed', 'applied'
        if int(self.clock()) > action['retryUntil']:
            outcome, reason = 'rejected', 'action-expired'
        elif request['option'] not in action['options']:
            outcome, reason = 'rejected', 'option-not-allowed'
        elif request['replaces'] and request['replaces'] != ([current[0]] if current else []):
            # Unknown/pending predecessors never become executable dependencies.
            outcome, reason = 'rejected', 'replacement-not-current'
        elif not request['replaces'] and current:
            outcome, reason = 'rejected', 'replacement-not-current'
        elif wait:
            outcome, reason = 'pending', 'processing'
        elif request['replaces'] != ([current[0]] if current else []):
            outcome, reason = 'rejected', 'replacement-not-current'
        result = dict(request, purpose='service-answer-result', service=action['service'],
                      requestDigest=hashlib.sha256(raw).hexdigest(), outcome=outcome, reason=reason)
        if outcome == 'confirmed':
            db.execute('INSERT INTO effects VALUES(?,?,?)', (request['submission'], principal, request['option']))
            db.execute('INSERT OR REPLACE INTO current VALUES(?,?,?)', (principal, request['submission'], request['option']))
        return encode_event(result)

    def reconcile_one(self, token):
        """Explicit worker, never called by GET. Fresh configured authorization required."""
        action = self.action()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            principal, status = self.authorized(token, action, 'submit')
            if status != 200: return status, b''
            if int(self.clock()) < action['notBefore']: return 403, b''
            rows = db.execute('SELECT submission,raw,result FROM submissions WHERE principal=? AND action=? ORDER BY rowid',
                              (principal, action['action'])).fetchall()
            for submission, raw, old in rows:
                if json.loads(old)['outcome'] != 'pending': continue
                receipt = self.decide(db, action, decode_request(raw)['value'], raw)
                db.execute('UPDATE submissions SET result=? WHERE principal=? AND action=? AND submission=?',
                           (receipt, principal, action['action'], submission))
                return self.receipt_status(receipt), receipt
            return 204, b''

    def status(self, submission, token):
        action = self.action()
        principal, status = self.authorized(token, action, 'status')
        if status != 200: return status, b''
        with self.connect() as db:
            row = db.execute('SELECT result FROM submissions WHERE principal=? AND action=? AND submission=?', (principal, action['action'], submission)).fetchone()
        return (self.receipt_status(row[0]), row[0]) if row else (404, b'')

class ClientJournal:
    """Durable exact requests and observed receipts; transport calls private reducer."""
    def __init__(self, path):
        self.db = sqlite3.connect(path, check_same_thread=False)
        try:
            self.db.executescript('''CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY, raw BLOB, service TEXT);
        CREATE TABLE IF NOT EXISTS receipts(id TEXT, raw BLOB);
        CREATE TABLE IF NOT EXISTS states(id TEXT PRIMARY KEY, state TEXT, terminal TEXT);''')
        except BaseException:
            self.db.close()
            raise

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def retain(self, raw, service):
        identity = decode_request(raw)['value']['submission']
        old = self.db.execute('SELECT raw,service FROM requests WHERE id=?', (identity,)).fetchone()
        if old and old != (raw, service): raise ValueError('immutable request')
        with self.db: self.db.execute('INSERT OR IGNORE INTO requests VALUES(?,?,?)', (identity, raw, service))
        return identity

    def state(self, identity):
        row = self.db.execute('SELECT state FROM states WHERE id=?', (identity,)).fetchone()
        return row[0] if row else 'uncertain'

    def _observe_direct_response(self, identity, receipt):
        raw, service = self.db.execute('SELECT raw,service FROM requests WHERE id=?', (identity,)).fetchone()
        value = bind_result(receipt, raw, expected_service=service)['value']
        canonical = json.dumps(value, sort_keys=True)
        previous = self.db.execute('SELECT state,terminal FROM states WHERE id=?', (identity,)).fetchone()
        state, terminal = previous or ('uncertain', None)
        if value['outcome'] != 'pending':
            if terminal is not None and terminal != canonical: state = 'conflict'
            elif state != 'conflict': state, terminal = value['outcome'], canonical
        elif terminal is None and state != 'conflict': state = 'pending'
        with self.db:
            self.db.execute('INSERT INTO receipts VALUES(?,?)', (identity, receipt))
            self.db.execute('INSERT OR REPLACE INTO states VALUES(?,?,?)', (identity, state, terminal))
        return state
