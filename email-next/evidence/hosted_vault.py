"""Configured encrypted request storage. No keystore or rollback protection."""
import json
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROLES = {'sender-request', 'host-request', 'host-reply'}

class HostedVault:
    def __init__(self, key, key_id, role, service, owner, *, writer_owner=None):
        if len(key) != 32 or role not in ROLES or not key_id:
            raise ValueError('invalid vault configuration')
        self.cipher = AESGCM(key)
        self.key, self.writer_owner = key, writer_owner
        self.key_id, self.role, self.service, self.owner = key_id, role, service, owner

    def aad(self, operation, purpose, grant):
        return json.dumps(['hosted-vault-0', self.role, self.service, self.owner,
                           operation, purpose, grant, self.key_id], separators=(',', ':')).encode()

    @staticmethod
    def schema(db):
        db.execute('CREATE TABLE IF NOT EXISTS vault(operation TEXT PRIMARY KEY,purpose TEXT,grant_id TEXT,key_id TEXT,nonce BLOB,ciphertext BLOB,UNIQUE(key_id,nonce))')

    def put(self, db, operation, purpose, grant, raw):
        if db.execute('SELECT 1 FROM vault WHERE operation=?', (operation,)).fetchone():
            if self.get(db, operation, purpose, grant) != raw:
                raise ValueError('operation conflict')
            return
        if self.writer_owner is None: raise ValueError('writer-key-owner-required')
        self.writer_owner.check_application(db.execute('PRAGMA database_list').fetchone()[2])
        nonce = self.writer_owner.reserve(self.key)
        ciphertext = self.cipher.encrypt(nonce, raw, self.aad(operation, purpose, grant))
        db.execute('INSERT INTO vault VALUES(?,?,?,?,?,?)', (operation,purpose,grant,self.key_id,nonce,ciphertext))

    def get(self, db, operation, purpose, grant):
        row = db.execute('SELECT purpose,grant_id,key_id,nonce,ciphertext FROM vault WHERE operation=?', (operation,)).fetchone()
        if not row or row[:3] != (purpose, grant, self.key_id):
            raise ValueError('vault binding mismatch')
        return self.cipher.decrypt(row[3], row[4], self.aad(operation,purpose,grant))

    def migrate(self, db, *, key, key_id, writer_owner):
        """Caller owns application transaction; return replacement after commit.

        Old object remains usable if transaction rolls back. New reservations
        are never refunded. Restrict to this vault's existing friendly key ID.
        """
        if not db.in_transaction:
            raise ValueError('Vault migration requires an application transaction')
        writer_owner.check_application(db.execute('PRAGMA database_list').fetchone()[2])
        target = HostedVault(key,key_id,self.role,self.service,self.owner,writer_owner=writer_owner)
        for operation,purpose,grant in db.execute('SELECT operation,purpose,grant_id FROM vault WHERE key_id=?',(self.key_id,)).fetchall():
            raw=self.get(db,operation,purpose,grant)
            nonce=writer_owner.reserve(key)
            ciphertext=target.cipher.encrypt(nonce,raw,target.aad(operation,purpose,grant))
            db.execute('UPDATE vault SET key_id=?,nonce=?,ciphertext=? WHERE operation=?',(key_id,nonce,ciphertext,operation))
        return target
