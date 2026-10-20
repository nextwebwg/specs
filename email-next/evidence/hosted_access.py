"""One-owner configured hosted experiment; grants confer holder authority only."""
import base64
from contextlib import contextmanager
import hashlib
import hmac
import json
import os
import sqlite3
import time
from pathlib import Path
from event_encoding import decode_event, encode_event, serialize_json, MAX_EVENT_OCTETS
from service_answer import identifier, reference
from hosted_vault import HostedVault

CREATE = {'version','purpose','operation','grant','credential','contribution','content','recipient','replyDestination','expiry'}
REVOKE = {'version','purpose','operation','grant'}
REPLY = {'version','purpose','operation','text'}

def credential():
    return base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode()

def valid_credential(value):
    if not isinstance(value,str) or len(value)!=43 or not value.isascii(): return False
    try:
        raw=base64.b64decode(value+'=',altchars=b'-_',validate=True)
        return len(raw)==32 and base64.urlsafe_b64encode(raw).rstrip(b'=').decode()==value
    except ValueError:return False

def exact(value,keys):return isinstance(value,dict) and set(value)==keys

def text(value):return isinstance(value,str) and bool(value.strip()) and not any(0xD800<=ord(c)<=0xDFFF for c in value)

def epoch(value):
    return isinstance(value,str) and value.isascii() and value.isdigit() and str(int(value))==value and int(value)<2**64

def parse(raw,purpose):
    value=decode_event(raw)['value']
    keys={'hosted-grant-create':CREATE,'hosted-grant-revoke':REVOKE,'hosted-holder-reply':REPLY}[purpose]
    version=value.get('version')
    if purpose=='hosted-grant-create' and version=='1':keys=keys|{'replyTextLimit'}
    if not exact(value,keys) or version not in (('0','1') if purpose=='hosted-grant-create' else ('0',)) or value['purpose']!=purpose or not identifier(value['operation']):raise ValueError('invalid hosted request')
    if purpose=='hosted-holder-reply':
        if not text(value['text']):raise ValueError('invalid reply')
        return value
    if not identifier(value['grant']):raise ValueError('invalid grant')
    if purpose=='hosted-grant-create':
        if version=='1' and (not epoch(value['replyTextLimit']) or not 3<=int(value['replyTextLimit'])<=MAX_EVENT_OCTETS):raise ValueError('invalid reply limit')
        expiry=value['expiry']
        valid_expiry=expiry=={'kind':'none'} or (exact(expiry,{'kind','epoch'}) and expiry['kind']=='at' and epoch(expiry['epoch']))
        if not valid_credential(value['credential']) or not reference(value['contribution']) or not exact(value['content'],{'kind','text'}) or value['content']['kind']!='text' or not text(value['content']['text']) or not identifier(value['recipient']) or not identifier(value['replyDestination']) or not valid_expiry:
            raise ValueError('invalid create')
    return value

class HostedStore:
    def __init__(self,path,*,service,owner,management_token,management_grant,host_key,reply_key,configuration,clock=time.time,writer_owner=None):
        if writer_owner is not None: writer_owner.check_application(path)
        self.path=str(path);self.service=service;self.owner=owner;self.clock=clock;self.configuration=configuration
        self.management_grant=management_grant
        self.management_digest=hashlib.sha256(management_token.encode()).digest()
        self.vault=HostedVault(host_key,'host-0','host-request',service,owner,writer_owner=writer_owner)
        self.reply_vault=HostedVault(reply_key,'reply-0','host-reply',service,owner,writer_owner=writer_owner)
        if not Path(path).is_file():raise RuntimeError('missing hosted database')
        with self.db() as db:
            if db.execute('SELECT version FROM initialized').fetchone()!=(0,):raise RuntimeError('uninitialized')
    @staticmethod
    def provision(path):
        with open(path,'xb'):pass
        db=sqlite3.connect(path)
        try:
            with db:
                db.executescript('''CREATE TABLE initialized(version INTEGER);INSERT INTO initialized VALUES(0);
                CREATE TABLE grants(id TEXT PRIMARY KEY,operation TEXT UNIQUE,digest BLOB,revoked INTEGER);
                CREATE TABLE decisions(operation TEXT PRIMARY KEY,grant_id TEXT,purpose TEXT,receipt BLOB);
                CREATE TABLE replies(operation TEXT,grant_id TEXT,destination TEXT,receipt BLOB,PRIMARY KEY(grant_id,operation));
                CREATE TABLE notification_outbox(grant_id TEXT PRIMARY KEY,state TEXT);
                CREATE TABLE disclosure(grant_id TEXT PRIMARY KEY,model TEXT,state TEXT);''')
                HostedVault.schema(db)
        finally:db.close()
    @contextmanager
    def db(self):
        db=sqlite3.connect('file:'+self.path+'?mode=rw',uri=True,timeout=5)
        try:
            db.execute('PRAGMA synchronous=FULL')
            with db:yield db
        finally:db.close()
    def management(self,token,scope):
        grant=self.management_grant
        if not isinstance(token,str) or not hmac.compare_digest(hashlib.sha256(token.encode()).digest(),self.management_digest):return 401
        if grant['issuer']!='fixture' or grant['service']!=self.service or grant['owner']!=self.owner or not grant['notBefore']<=int(self.clock())<=grant['expires']:return 401
        return 200 if scope in grant['scopes'] else 403
    def receipt(self,req,raw,reason):
        return encode_event(dict(version='0',purpose='hosted-management-result',service=self.service,owner=self.owner,operation=req['operation'],grant=req['grant'],requestDigest=hashlib.sha256(raw).hexdigest(),outcome='confirmed',reason=reason))
    def manage(self,raw,token,purpose,*,crash=None):
        auth=self.management(token,'create' if purpose=='hosted-grant-create' else 'revoke')
        if auth!=200:return auth,b''
        try:req=parse(raw,purpose)
        except (ValueError,TypeError):return 400,b''
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            auth=self.management(token,'create' if purpose=='hosted-grant-create' else 'revoke')
            if auth!=200:return auth,b''
            old=db.execute('SELECT grant_id,purpose,receipt FROM decisions WHERE operation=?',(req['operation'],)).fetchone()
            if old:
                if old[:2]!=(req['grant'],purpose):return 409,b''
                return (200,old[2]) if self.vault.get(db,req['operation'],purpose,req['grant'])==raw else (409,b'')
            if db.execute('SELECT 1 FROM vault WHERE operation=?',(req['operation'],)).fetchone():return 409,b''
            grant=db.execute('SELECT operation FROM grants WHERE id=?',(req['grant'],)).fetchone()
            if purpose=='hosted-grant-create':
                if grant:return 409,b''
                expected={k:req[k] for k in ('contribution','content','recipient','replyDestination')}
                if req['version']=='1':expected['replyTextLimit']=req['replyTextLimit']
                if expected!=self.configuration:return 403,b''
                if req['expiry']['kind']=='at' and int(self.clock())>int(req['expiry']['epoch']):return 403,b''
                db.execute('INSERT INTO grants VALUES(?,?,?,0)',(req['grant'],req['operation'],hashlib.sha256(req['credential'].encode()).digest()))
                db.execute('INSERT INTO notification_outbox VALUES(?,?)',(req['grant'],'ready'))
                db.execute('INSERT INTO disclosure VALUES(?,?,?)',(req['grant'],'bearer','hosted-created'))
                reason='created'
            else:
                if not grant:return 404,b''
                db.execute('UPDATE grants SET revoked=1 WHERE id=?',(req['grant'],));reason='revoked'
            self.vault.put(db,req['operation'],purpose,req['grant'],raw)
            receipt=self.receipt(req,raw,reason)
            db.execute('INSERT INTO decisions VALUES(?,?,?,?)',(req['operation'],req['grant'],purpose,receipt))
            if crash:crash('before-commit')
            db.commit()
            if crash:crash('after-commit')
            return 200,receipt
    def lookup(self,operation,token):
        auth=self.management(token,'inspect')
        if auth!=200:return auth,b''
        with self.db() as db:row=db.execute('SELECT receipt FROM decisions WHERE operation=?',(operation,)).fetchone()
        return (200,row[0]) if row else (404,b'')
    def authorize_grant(self,db,grant,token):
        if not valid_credential(token):return None
        row=db.execute('SELECT operation,digest,revoked FROM grants WHERE id=?',(grant,)).fetchone()
        if not row or row[2] or not hmac.compare_digest(row[1],hashlib.sha256(token.encode()).digest()):return None
        value=parse(self.vault.get(db,row[0],'hosted-grant-create',grant),'hosted-grant-create')
        if value['expiry']['kind']=='at' and int(self.clock())>int(value['expiry']['epoch']):return None
        return value
    def denial(self,db,grant,token):
        row=db.execute('SELECT digest FROM grants WHERE id=?',(grant,)).fetchone()
        if not valid_credential(token) or not row or not hmac.compare_digest(row[0],hashlib.sha256(token.encode()).digest()):return 401,b''
        return 403,b''
    def retrieve(self,grant,token):
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            value=self.authorize_grant(db,grant,token)
            if value is None:return self.denial(db,grant,token)
            return 200,encode_event(dict(version='0',purpose='hosted-content',grant=grant,contribution=value['contribution'],content=value['content'],attribution='provider-hosted'))
    def reply(self,grant,raw,token):
        try:req=parse(raw,'hosted-holder-reply')
        except (ValueError,TypeError):return 400,b''
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE');value=self.authorize_grant(db,grant,token)
            if value is None:return self.denial(db,grant,token)
            old=db.execute('SELECT grant_id,receipt FROM replies WHERE operation=? AND grant_id=?',(req['operation'],grant)).fetchone()
            if old:
                if old[0]!=grant:return 409,b''
                return (200,old[1]) if self.reply_vault.get(db,grant+':'+req['operation'],'hosted-holder-reply',grant)==raw else (409,b'')
            if value['version']=='1' and len(serialize_json(req['text']))>int(value['replyTextLimit']):return 413,b''
            self.reply_vault.put(db,grant+':'+req['operation'],'hosted-holder-reply',grant,raw)
            receipt=encode_event(dict(version='0',purpose='hosted-holder-result',service=self.service,grant=grant,operation=req['operation'],requestDigest=hashlib.sha256(raw).hexdigest(),outcome='confirmed',reason='stored',attribution='grant-holder'))
            db.execute('INSERT INTO replies VALUES(?,?,?,?)',(req['operation'],grant,value['replyDestination'],receipt))
            return 200,receipt
    def reply_status(self,grant,operation,token):
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            if self.authorize_grant(db,grant,token) is None:return self.denial(db,grant,token)
            row=db.execute('SELECT receipt FROM replies WHERE operation=? AND grant_id=?',(operation,grant)).fetchone()
            return (200,row[0]) if row else (404,b'')

    def management_reply(self,grant,operation,token):
        auth=self.management(token,'read-management')
        if auth!=200:return auth,b''
        with self.db() as db:
            row=db.execute('SELECT receipt FROM replies WHERE grant_id=? AND operation=?',(grant,operation)).fetchone()
            return (200,row[0]) if row else (404,b'')

    def export_reply(self,grant,operation,token):
        if self.management(token,'read-management')!=200:return self.management(token,'read-management'),b''
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            auth=self.management(token,'read-management')
            if auth!=200:return auth,b''
            row=db.execute('SELECT destination,receipt FROM replies WHERE grant_id=? AND operation=?',(grant,operation)).fetchone()
            if not row:return 404,b''
            raw=self.reply_vault.get(db,grant+':'+operation,'hosted-holder-reply',grant)
            value=dict(version='0',purpose='hosted-reply-export',service=self.service,grant=grant,operation=operation,request=base64.urlsafe_b64encode(raw).rstrip(b'=').decode(),receipt=decode_event(row[1])['value'],replyDestination=row[0])
            body=serialize_json(value)
            decode_event(body,max_octets=2097152)
            return 200,body
