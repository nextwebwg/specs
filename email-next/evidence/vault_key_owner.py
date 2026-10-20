"""Independent local writer accounting. Ledger continuity is trusted, not detected.

Never restore/clone this ledger to authorize the same key independently. On
uncertain continuity retain old keys only for decryption and provision fresh keys.
Fingerprints are secret local metadata; do not log or send them.
"""
import hashlib
import os
from pathlib import Path
import secrets
import sqlite3
from contextlib import closing

MAX_INVOCATIONS = 2**32  # SP800-38D section 8.3, across instances of a key.


def fingerprint(key):
    if not isinstance(key, bytes) or len(key) != 32:
        raise ValueError('Vault key must be 32 bytes')
    return hashlib.sha256(b'email-next/local-vault-key/v0\0' + key).digest()


class VaultKeyOwner:
    def __init__(self, path):
        self.path = str(Path(path).resolve())
        with closing(sqlite3.connect(self.path)) as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS writer_key
              (fingerprint BLOB PRIMARY KEY,state TEXT NOT NULL,attempted INTEGER NOT NULL,ceiling INTEGER NOT NULL);
              CREATE TABLE IF NOT EXISTS writer_nonce
              (fingerprint BLOB NOT NULL,nonce BLOB NOT NULL,PRIMARY KEY(fingerprint,nonce));''')

    def check_application(self, path):
        other = Path(path).resolve()
        if str(other) == self.path or (other.exists() and os.path.samefile(self.path, other)):
            raise ValueError('Writer ledger must be separate from application database')

    def provision(self, *, ceiling=MAX_INVOCATIONS):
        if type(ceiling) is not int or not 0 <= ceiling <= MAX_INVOCATIONS:
            raise ValueError('Invalid writer invocation ceiling')
        key = secrets.token_bytes(32)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('PRAGMA synchronous=FULL')
            db.execute('INSERT INTO writer_key VALUES(?,?,?,?)', (fingerprint(key),'active',0,ceiling))
        return key

    def retire(self, key):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('UPDATE writer_key SET state=? WHERE fingerprint=?', ('decrypt-only',fingerprint(key)))

    def reserve(self, key):
        fp = fingerprint(key)
        with closing(sqlite3.connect(self.path, isolation_level=None)) as db:
            db.execute('PRAGMA synchronous=FULL')
            db.execute('BEGIN IMMEDIATE')
            try:
                row = db.execute('SELECT state,attempted,ceiling FROM writer_key WHERE fingerprint=?',(fp,)).fetchone()
                if not row or row[0] != 'active': raise ValueError('Writer key unavailable; fresh provisioning required')
                if row[1] >= row[2]: raise ValueError('Writer key exhausted; fresh provisioning required')
                nonce = secrets.token_bytes(12)
                if not isinstance(nonce,bytes) or len(nonce)!=12: raise ValueError('Random source failed')
                if db.execute('SELECT 1 FROM writer_nonce WHERE fingerprint=? AND nonce=?',(fp,nonce)).fetchone():
                    raise ValueError('Random nonce repeated')
                db.execute('INSERT INTO writer_nonce VALUES(?,?)',(fp,nonce))
                db.execute('UPDATE writer_key SET attempted=attempted+1 WHERE fingerprint=?',(fp,))
                db.execute('COMMIT')
                return nonce
            except BaseException:
                if db.in_transaction: db.execute('ROLLBACK')
                raise
