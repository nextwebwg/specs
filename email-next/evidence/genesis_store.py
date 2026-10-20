"""Durable first-contact evidence experiment, not an MLS identity service."""
import copy
import json
import sqlite3
from genesis_pipeline import pipeline

class GenesisStore:
    def __init__(self,path):
        self.db=sqlite3.connect(path,timeout=10,isolation_level=None)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS claims (
            principal TEXT NOT NULL, digest TEXT NOT NULL, record TEXT NOT NULL,
            PRIMARY KEY(principal,digest));
          CREATE TABLE IF NOT EXISTS pins (
            principal TEXT PRIMARY KEY, digest TEXT NOT NULL);
        ''')

    def close(self):
        self.db.close()

    def observe(self,record,*,first_contact_policy):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            result=self._observe_locked(record,first_contact_policy=first_contact_policy)
            self.db.execute('COMMIT');return result
        except BaseException:
            self.db.execute('ROLLBACK');raise

    def _observe_locked(self,record,*,first_contact_policy):
        if not self.db.in_transaction:raise ValueError('Transaction required')
        if first_contact_policy not in ('allow-unverified','require-verification'):
            raise ValueError('Explicit first-contact policy required')
        # Freeze the caller's data before proofs and storage, avoiding mutation between them.
        record=copy.deepcopy(record)
        result=pipeline(record)
        if result['status']!='claim-valid-unverified':
            return result
        principal,digest=result['principal'],result['stateDigest']
        serialized=json.dumps(record,sort_keys=True,separators=(',',':'))
        self.db.execute('INSERT OR IGNORE INTO claims VALUES(?,?,?)',(principal,digest,serialized))
        claims=self.db.execute('SELECT digest FROM claims WHERE principal=?',(principal,)).fetchall()
        pin=self.db.execute('SELECT digest FROM pins WHERE principal=?',(principal,)).fetchone()
        # A new self-signed key can copy the public principal identifier.
        # Its claim cannot revoke or suspend a previously pinned identity.
        if pin:
            status='pinned-unverified' if pin[0]==digest else 'unlinked-claim'
        elif len(claims)>1:
            status='first-contact-ambiguous'
        elif first_contact_policy=='allow-unverified':
            self.db.execute('INSERT INTO pins VALUES(?,?)',(principal,digest))
            pin=(digest,)
            status='pinned-unverified'
        else:
            status='verification-required'
        return {'status':status,'principal':principal,'candidate':digest,'pin':pin[0] if pin else None}


    def snapshot(self,principal):
        # One transaction keeps the pin and claim count at the same database snapshot.
        self.db.execute('BEGIN')
        try:
            pin=self.db.execute('SELECT digest FROM pins WHERE principal=?',(principal,)).fetchone()
            count=self.db.execute('SELECT COUNT(*) FROM claims WHERE principal=?',(principal,)).fetchone()[0]
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise
        return {'pin':pin[0] if pin else None,'claims':count,
                'firstContactAmbiguous':pin is None and count>1,
                'unlinkedClaims':count-1 if pin else 0}
