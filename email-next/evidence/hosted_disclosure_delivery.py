"""Fixed source-bound grant creation and encrypted notification delivery."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import uuid
from hosted_disclosure import HostedDisclosure,check_original
from hosted_access import parse
from hosted_notification_release import HostedNotificationRelease

class HostedDisclosureManagement:
    def __init__(self,sender,management):
        self.sender=sender;self.client=management;self.hosted=management.sender
        HostedDisclosure(sender,self.hosted)
        self.pid=os.getpid();self.path=Path(self.hosted.path);st=self.path.stat();self.inode=(st.st_dev,st.st_ino)
        if st.st_nlink!=1:raise ValueError('Hard-linked database')
        self.sender.db.executescript('''CREATE TABLE IF NOT EXISTS hosted_creation_state(operation TEXT PRIMARY KEY,state TEXT,evidence TEXT);
        CREATE TABLE IF NOT EXISTS hosted_creation_attempts(id TEXT PRIMARY KEY,operation TEXT,state TEXT,retry_uncertain INTEGER);''')
    def create(self,operation,token,*,time,retry_uncertain=False,crash=lambda stage:None):
        if type(retry_uncertain) is not bool or self.pid!=os.getpid():raise ValueError('Worker ownership/retry choice')
        fd=os.open(str(self.path)+'.host-create-lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
        try:
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            st=self.path.stat();lock=Path(str(self.path)+'.host-create-lock').stat();opened=os.fstat(fd)
            if st.st_nlink!=1 or opened.st_nlink!=1 or (st.st_dev,st.st_ino)!=self.inode or (lock.st_dev,lock.st_ino)!=(opened.st_dev,opened.st_ino):raise ValueError('Replaced database/lock')
            db=self.sender.db;db.execute('BEGIN IMMEDIATE')
            try:
                db.execute("UPDATE hosted_creation_attempts SET state='uncertain' WHERE state='released'")
                db.execute("UPDATE hosted_creation_state SET state='uncertain' WHERE state='released'")
                db.execute('COMMIT');db.execute('BEGIN IMMEDIATE')
                old=db.execute('SELECT state,evidence FROM hosted_creation_state WHERE operation=?',(operation,)).fetchone()
                if old and old[0]=='confirmed':db.execute('COMMIT');return {'http':200,'evidence':old[1],'state':'observed'}
                if old and old[0]=='conflict':raise ValueError('Conflicting creation')
                if old and not retry_uncertain:raise ValueError('Explicit uncertain retry required')
                source=check_original(self.sender,db,operation,time)
                raw=self.hosted.vault.get(db,operation,'hosted-grant-create',source['grant'])
                if hashlib.sha256(raw).hexdigest()!=source['requestDigest']:raise ValueError('Changed creation bytes')
                request=parse(raw,'hosted-grant-create')
                if request['expiry']['kind']=='at' and int(time['latest'])>int(request['expiry']['epoch']):raise ValueError('Expired creation')
                attempt=uuid.uuid4().hex
                db.execute('INSERT INTO hosted_creation_attempts VALUES(?,?,?,?)',(attempt,operation,'released',int(retry_uncertain)))
                db.execute('INSERT INTO hosted_creation_state VALUES(?,?,NULL) ON CONFLICT(operation) DO UPDATE SET state=excluded.state,evidence=NULL',(operation,'released'))
                db.execute('COMMIT')
            except BaseException:
                if db.in_transaction:db.execute('ROLLBACK')
                raise
            crash('after-release')
            try:result=self.client._request(operation,token)
            except Exception:
                db.execute("UPDATE hosted_creation_state SET state='uncertain' WHERE operation=?",(operation,));db.execute("UPDATE hosted_creation_attempts SET state='uncertain' WHERE id=?",(attempt,));raise
            st=self.path.stat();lock=Path(str(self.path)+'.host-create-lock').stat()
            if (st.st_dev,st.st_ino)!=self.inode or (lock.st_dev,lock.st_ino)!=(opened.st_dev,opened.st_ino):raise ValueError('Replaced database/lock after request')
            state='confirmed' if result.get('state')=='observed' else 'conflict' if result.get('state')=='conflict' or result['http']==409 else 'uncertain'
            db.execute('BEGIN IMMEDIATE')
            try:
                db.execute('UPDATE hosted_creation_attempts SET state=? WHERE id=?',(state,attempt))
                db.execute('UPDATE hosted_creation_state SET state=?,evidence=? WHERE operation=?',(state,result.get('evidence'),operation));db.execute('COMMIT')
            except BaseException:
                if db.in_transaction:db.execute('ROLLBACK')
                raise
            return result
        finally:os.close(fd)
    def reconcile(self,operation,token):
        # Read-only remote lookup preserves history after local authorization withdrawal.
        if self.pid!=os.getpid():raise ValueError('Worker ownership')
        fd=os.open(str(self.path)+'.host-create-lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
        try:
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            st=self.path.stat();lock=Path(str(self.path)+'.host-create-lock').stat();opened=os.fstat(fd)
            if st.st_nlink!=1 or opened.st_nlink!=1 or (st.st_dev,st.st_ino)!=self.inode or (lock.st_dev,lock.st_ino)!=(opened.st_dev,opened.st_ino):raise ValueError('Replaced database/lock')
            self.sender.db.execute("UPDATE hosted_creation_attempts SET state='uncertain' WHERE state='released'")
            self.sender.db.execute("UPDATE hosted_creation_state SET state='uncertain' WHERE state='released'")
            result=self.client.request(operation,token,lookup=True)
            if result.get('state') in ('observed','conflict'):
                self.sender.db.execute('UPDATE hosted_creation_state SET state=?,evidence=? WHERE operation=?',('confirmed' if result['state']=='observed' else 'conflict',result['evidence'],operation))
            return result
        finally:os.close(fd)

class HostedDisclosureNotification(HostedNotificationRelease):
    def __init__(self,source_sender,hosted):
        HostedDisclosure(source_sender,hosted);self.source_sender=source_sender
        super().__init__(hosted)
    def _check(self,db,operation,evidence,credible_time,revision=None):
        req,revision,configuration,raw=self._check_common(db,operation,evidence,credible_time,revision)
        source=check_original(self.source_sender,db,operation,dict(earliest=str(credible_time[0]),latest=str(credible_time[1])))
        if source['requestDigest']!=hashlib.sha256(raw).hexdigest() or source['route']!={k:configuration[k] for k in ('fromAddress','recipientAddress')}:raise ValueError('Bound notification route')
        return req,revision,configuration,raw
