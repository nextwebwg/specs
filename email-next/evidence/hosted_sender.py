"""Encrypted sender preparation; sending notification remains an explicit operation."""
from contextlib import contextmanager
import sqlite3
from pathlib import Path
from hosted_vault import HostedVault
from hosted_access import parse

class HostedSender:
    def __init__(self,path,*,key,service,owner,writer_owner=None):
        if writer_owner is not None: writer_owner.check_application(path)
        self.path=str(Path(path).resolve());self.vault=HostedVault(key,'sender-0','sender-request',service,owner,writer_owner=writer_owner)
        with self.db() as db:
            HostedVault.schema(db)
            db.execute('CREATE TABLE IF NOT EXISTS outgoing(operation TEXT PRIMARY KEY,grant_id TEXT,purpose TEXT,state TEXT)')
    @contextmanager
    def db(self):
        db=sqlite3.connect(self.path)
        try:
            db.execute('PRAGMA synchronous=FULL')
            with db:yield db
        finally:db.close()
    def retain(self,raw,*,purpose='hosted-grant-create',crash=None):
        if purpose not in ('hosted-grant-create','hosted-grant-revoke'):raise ValueError('management purpose')
        req=parse(raw,purpose)
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            self.vault.put(db,req['operation'],req['purpose'],req['grant'],raw)
            db.execute('INSERT OR IGNORE INTO outgoing VALUES(?,?,?,?)',(req['operation'],req['grant'],req['purpose'],'prepared'))
            if crash:crash('before-commit')
            db.commit()
            if crash:crash('after-commit')
        return req['operation']
    def load(self,operation):
        with self.db() as db:
            row=db.execute('SELECT grant_id,purpose FROM outgoing WHERE operation=?',(operation,)).fetchone()
            if not row:raise ValueError('unknown operation')
            return self.vault.get(db,operation,row[1],row[0])
