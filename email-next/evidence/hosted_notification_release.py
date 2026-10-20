"""Fixed encrypted hosted-notification release, loopback SMTP only.

No MLS authority is inferred: this uses separately configured local hosted policy.
A historical create receipt is not proof of currently active remote grant state.
"""
from contextlib import closing, contextmanager
import fcntl
import hashlib
import json
import os
import uuid
from pathlib import Path
import smtplib
from event_encoding import decode_event
from hosted_access import parse
from service_answer import identifier
from hosted_notification import prepare as prepare_wire
from passive_discovery import mailbox_syntax

CONTRACT='hosted-notification-v0'

class HostedNotificationRelease:
    def __init__(self,sender):
        self.sender=sender;self.pid=os.getpid();self.owner=uuid.uuid4().hex;self.fd=None
        self.path=Path(sender.path).resolve(strict=True)
        st=self.path.stat()
        if st.st_nlink!=1:raise ValueError('Hard-linked database unsupported')
        self.inode=(st.st_dev,st.st_ino)
        with sender.db() as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS hosted_policy(id INTEGER PRIMARY KEY CHECK(id=1),revision INTEGER,configuration TEXT);
            CREATE TABLE IF NOT EXISTS hosted_prepared(operation TEXT PRIMARY KEY,evidence TEXT,policy_revision INTEGER,request_digest TEXT,wire_digest TEXT,kind TEXT);
            CREATE TABLE IF NOT EXISTS hosted_attempts(id TEXT PRIMARY KEY,operation TEXT,owner TEXT,state TEXT,kind TEXT,result TEXT);''')
            if 'id' not in [r[1] for r in db.execute('PRAGMA table_info(hosted_attempts)')]:
                db.execute('ALTER TABLE hosted_attempts RENAME TO hosted_attempts_legacy')
                db.execute('CREATE TABLE hosted_attempts(id TEXT PRIMARY KEY,operation TEXT,owner TEXT,state TEXT,kind TEXT,result TEXT)')
                db.execute("INSERT INTO hosted_attempts SELECT operation,operation,'legacy',state,kind,result FROM hosted_attempts_legacy")
    def _owned(self):
        if os.getpid()!=self.pid or self.fd is None:raise ValueError('Worker ownership')
        st=self.path.stat();lock=Path(str(self.path)+'.notification-lock').stat();opened=os.fstat(self.fd)
        if st.st_nlink!=1 or (st.st_dev,st.st_ino)!=self.inode or (lock.st_dev,lock.st_ino)!=(opened.st_dev,opened.st_ino):raise ValueError('Replaced database or lock')
    @contextmanager
    def _locked(self):
        if os.getpid()!=self.pid or self.fd is not None:raise ValueError('Worker ownership')
        fd=os.open(str(self.path)+'.notification-lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
        try:
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            if os.fstat(fd).st_nlink!=1:raise ValueError('Invalid lock file')
            self.fd=fd;self._owned()
            with self.sender.db() as db:db.execute("UPDATE hosted_attempts SET state='uncertain' WHERE state='released'")
            yield
        finally:
            self.fd=None;os.close(fd)
    def reconcile(self,operation):
        # Lock acquisition proves no cooperating transmitter remains; no delivery inference.
        with self._locked():
            with self.sender.db() as db:
                return [dict(attempt=r[0],state=r[1],result=json.loads(r[2]) if r[2] else None) for r in db.execute('SELECT id,state,result FROM hosted_attempts WHERE operation=? AND kind=? ORDER BY rowid',(operation,CONTRACT))]
    def configure(self,*,expected_revision,configuration):
        required={'service','owner','recipient','replyDestination','fromAddress','recipientAddress','enabled'}
        if not isinstance(configuration,dict) or set(configuration)!=required or type(configuration['enabled']) is not bool:raise ValueError('hosted configuration')
        if configuration['service']!=self.sender.vault.service or configuration['owner']!=self.sender.vault.owner:raise ValueError('configuration authority')
        for field in ('fromAddress','recipientAddress'):mailbox_syntax(configuration[field])
        if not all(identifier(configuration[field]) for field in ('recipient','replyDestination')):raise ValueError('configuration identifier')
        if type(expected_revision) is not int or expected_revision<0:raise ValueError('revision')
        with self.sender.db() as db:
            db.execute('BEGIN IMMEDIATE');row=db.execute('SELECT revision FROM hosted_policy WHERE id=1').fetchone()
            current=row[0] if row else 0
            if current!=expected_revision:raise ValueError('stale policy')
            db.execute('INSERT OR REPLACE INTO hosted_policy VALUES(1,?,?)',(current+1,json.dumps(configuration,sort_keys=True)))
            return current+1
    def _check(self,db,operation,evidence,credible_time,revision=None):
        if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='hosted_disclosure_grants'").fetchone() and db.execute('SELECT 1 FROM hosted_disclosure_grants WHERE create_operation=?',(operation,)).fetchone():raise ValueError('Use source-bound notification')
        return self._check_common(db,operation,evidence,credible_time,revision)

    def _check_common(self,db,operation,evidence,credible_time,revision=None):
        if not isinstance(credible_time,tuple) or len(credible_time)!=2 or any(type(v) is not int for v in credible_time) or not 0<=credible_time[0]<=credible_time[1]<2**64:raise ValueError('credible time')
        row=db.execute('SELECT grant_id,purpose FROM outgoing WHERE operation=?',(operation,)).fetchone()
        if not row or row[1]!='hosted-grant-create':raise ValueError('not a create')
        raw=self.sender.vault.get(db,operation,row[1],row[0]);req=parse(raw,row[1])
        observed=db.execute('SELECT operation,grant_id,purpose,request_digest,receipt,state FROM management_evidence WHERE id=?',(evidence,)).fetchone()
        if not observed or observed[:4]!=(operation,req['grant'],req['purpose'],hashlib.sha256(raw).hexdigest()) or observed[5]!='observed':raise ValueError('management evidence required')
        receipt=decode_event(observed[4])['value']
        if receipt.get('service')!=self.sender.vault.service or receipt.get('owner')!=self.sender.vault.owner or receipt.get('reason')!='created':raise ValueError('creation authority')
        if db.execute("SELECT 1 FROM management_evidence WHERE grant_id=? AND (purpose='hosted-grant-revoke' OR state='conflict')",(req['grant'],)).fetchone():raise ValueError('known revocation or conflict')
        policy=db.execute('SELECT revision,configuration FROM hosted_policy WHERE id=1').fetchone()
        if not policy or revision is not None and policy[0]!=revision:raise ValueError('changed policy')
        config=json.loads(policy[1])
        if not config['enabled'] or config['service']!=self.sender.vault.service or config['owner']!=self.sender.vault.owner or config['recipient']!=req['recipient'] or config['replyDestination']!=req['replyDestination']:raise ValueError('current hosted authority')
        if req['expiry']['kind']=='at' and credible_time[1]>int(req['expiry']['epoch']):raise ValueError('grant expiry')
        return req,policy[0],config,raw
    def prepare(self,operation,*,evidence,credible_time):
        with self.sender.db() as db:
            db.execute('BEGIN IMMEDIATE')
            req,revision,config,raw=self._check(db,operation,evidence,credible_time)
        wire=prepare_wire(self.sender,operation,from_address=config['fromAddress'],recipient_address=config['recipientAddress'])
        binding=(evidence,revision,hashlib.sha256(raw).hexdigest(),hashlib.sha256(wire).hexdigest(),CONTRACT)
        with self.sender.db() as db:
            db.execute('BEGIN IMMEDIATE');self._check(db,operation,evidence,credible_time,revision)
            old=db.execute('SELECT evidence,policy_revision,request_digest,wire_digest,kind FROM hosted_prepared WHERE operation=?',(operation,)).fetchone()
            if old and old!=binding:raise ValueError('immutable preparation')
            db.execute('INSERT OR IGNORE INTO hosted_prepared VALUES(?,?,?,?,?,?)',(operation,*binding))
        return operation
    def submit(self,operation,*,port,credible_time,retry_uncertain=False,hook=lambda stage:None):
        if type(port) is not int or not 1<=port<=65535:raise ValueError('loopback port')
        if type(retry_uncertain) is not bool:raise ValueError('Explicit uncertain retry choice')
        with self._locked():return self._submit(operation,port,credible_time,retry_uncertain,hook)
    @staticmethod
    def _classification(code):
        return 'temporary' if 400<=code<500 else 'permanent' if 500<=code<600 else 'uncertain'
    def _submit(self,operation,port,time_source,retry_uncertain,hook):
        with self.sender.db() as db:
            db.execute('BEGIN IMMEDIATE');self._owned()
            prepared=db.execute('SELECT evidence,policy_revision,request_digest,wire_digest,kind FROM hosted_prepared WHERE operation=?',(operation,)).fetchone()
            if not prepared or prepared[4]!=CONTRACT:raise ValueError('not prepared')
            history=db.execute('SELECT state,result FROM hosted_attempts WHERE operation=? AND kind=? ORDER BY rowid',(operation,CONTRACT)).fetchall()
            status='new'
            for state,result in history:
                if status in ('smtp-submitted','permanent'):continue
                if state=='rejected':
                    old=json.loads(result) if result else {};code=old.get('smtpCode')
                    status=self._classification(code) if type(code) is int else 'uncertain'
                else:status='temporary' if state=='aborted-before-data' else state
            if status in ('smtp-submitted','permanent'):raise ValueError('Accepted or permanent prior attempt')
            if status not in ('new','temporary') and not retry_uncertain:raise ValueError('Explicit uncertain retry required')
            req,revision,config,raw=self._check(db,operation,prepared[0],time_source(),prepared[1])
            if hashlib.sha256(raw).hexdigest()!=prepared[2]:raise ValueError('request changed')
            wire=self.sender.vault.get(db,'notification:'+operation,'hosted-notification',req['grant'])
            if hashlib.sha256(wire).hexdigest()!=prepared[3]:raise ValueError('wire changed')
            attempt=uuid.uuid4().hex
            db.execute('INSERT INTO hosted_attempts VALUES(?,?,?,?,?,?)',(attempt,operation,self.owner,'released',CONTRACT,json.dumps({'retryUncertain':retry_uncertain})))
        hook('after-release')
        try:
            with closing(smtplib.SMTP('127.0.0.1',port,timeout=5)) as client:
                client.ehlo_or_helo_if_needed()
                code,_=client.mail(config['fromAddress'])
                if code!=250:return self._finish(attempt,self._classification(code),code)
                code,_=client.rcpt(config['recipientAddress'])
                if code not in (250,251):return self._finish(attempt,self._classification(code),code)
                hook('before-data-check')
                try:
                    with self.sender.db() as db:
                        db.execute('BEGIN IMMEDIATE');self._owned();self._check(db,operation,prepared[0],time_source(),revision)
                except ValueError:return self._finish(attempt,'aborted-before-data',None)
                hook('before-data');self._owned()
                code,_=client.data(wire)
                return self._finish(attempt,'smtp-submitted' if code==250 else self._classification(code),code)
        except smtplib.SMTPDataError as error:
            return self._finish(attempt,self._classification(error.smtp_code),error.smtp_code)
        except Exception:
            self._finish(attempt,'uncertain',None)
            raise
    def _finish(self,attempt,state,code):
        self._owned();result={'attempt':attempt,'state':state,'smtpCode':code,'kind':CONTRACT}
        with self.sender.db() as db:
            old=db.execute('SELECT result FROM hosted_attempts WHERE id=? AND owner=?',(attempt,self.owner)).fetchone()
            result['retryUncertain']=json.loads(old[0]).get('retryUncertain',False) if old and old[0] else False
            changed=db.execute("UPDATE hosted_attempts SET state=?,result=? WHERE id=? AND owner=? AND state='released'",(state,json.dumps(result),attempt,self.owner)).rowcount
            if changed!=1:raise ValueError('Lost attempt ownership')
        return result
