from vault_fixture import fresh_key
import json
from contextlib import contextmanager
from unittest.mock import patch
import os
from pathlib import Path
import tempfile
import unittest
from cryptography.exceptions import InvalidTag
from event_encoding import encode_event
from hosted_access import HostedStore,credential
from vault_fixture import HostedStore
from vault_fixture import HostedSender

class HostedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.now=100;self.secret=credential();self.keys=[fresh_key(self.root/'vault.db') for _ in range(3)]
        self.configuration=dict(contribution=dict(principal='enp0:'+'1'*64,conversation='2'*32,event='3'*32),content=dict(kind='text',text='CONFIDENTIAL_CONTENT_MARKER'),recipient='4'*32,replyDestination='5'*32)
        self.req=dict(version='0',purpose='hosted-grant-create',operation='6'*32,grant='7'*32,credential=self.secret,expiry=dict(kind='at',epoch='100'),**self.configuration);self.raw=encode_event(self.req)
        self.path=self.root/'host.db';HostedStore.provision(self.path)
        self.store=HostedStore(self.path,service='https://host.example',owner='enp0:'+'a'*64,management_token='management',management_grant=dict(issuer='fixture',service='https://host.example',owner='enp0:'+'a'*64,notBefore=0,expires=1000,scopes=['create','inspect','revoke','read-management']),host_key=self.keys[0],reply_key=self.keys[1],configuration=self.configuration,clock=lambda:self.now)
    def create(self):return self.store.manage(self.raw,'management','hosted-grant-create')
    def test_create_exact_retry_and_separate_authority(self):
        first=self.create();self.assertEqual(first[0],200);self.assertEqual(self.create(),first)
        self.assertEqual(self.store.manage(json.dumps(self.req).encode(),'management','hosted-grant-create')[0],409)
        self.assertEqual(self.store.manage(self.raw,self.secret,'hosted-grant-create')[0],401)
        self.assertEqual(self.store.retrieve('7'*32,self.secret)[0],200)
    def test_expiry_revoke_and_historical_evidence(self):
        first=self.create();self.now=101;self.assertEqual(self.store.retrieve('7'*32,self.secret)[0],403)
        self.now=100;revoke=encode_event(dict(version='0',purpose='hosted-grant-revoke',operation='8'*32,grant='7'*32))
        self.assertEqual(self.store.manage(revoke,'management','hosted-grant-revoke')[0],200)
        self.assertEqual(self.store.retrieve('7'*32,self.secret)[0],403)
        self.assertEqual(self.store.lookup('6'*32,'management'),first)
    def test_holder_reply_exact_bytes_and_denial_after_expiry(self):
        self.create();raw=encode_event(dict(version='0',purpose='hosted-holder-reply',operation='9'*32,text='PRIVATE_REPLY_MARKER'))
        first=self.store.reply('7'*32,raw,self.secret);self.assertEqual(json.loads(first[1])['attribution'],'grant-holder')
        self.assertEqual(first,self.store.reply('7'*32,raw,self.secret))
        self.now=101;self.assertEqual(self.store.reply_status('7'*32,'9'*32,self.secret)[0],403)
        for p in self.root.iterdir():
            data=p.read_bytes();self.assertNotIn(self.secret.encode(),data);self.assertNotIn(b'PRIVATE_REPLY_MARKER',data);self.assertNotIn(b'CONFIDENTIAL_CONTENT_MARKER',data)
    def test_forwarded_bearer_has_same_access_without_holder_identity(self):
        self.create()
        # Independent holder requests carry the copied bearer, not a mailbox
        # identity. Different operation IDs are two deliberate submissions.
        copied_credential=self.secret.encode().decode()
        self.assertEqual(self.store.retrieve('7'*32,self.secret),
                         self.store.retrieve('7'*32,copied_credential))
        for ident,credential in [('a'*32,self.secret),('b'*32,copied_credential)]:
            raw=encode_event(dict(version='0',purpose='hosted-holder-reply',
                                  operation=ident,text='A holder reply'))
            status,receipt=self.store.reply('7'*32,raw,credential)
            self.assertEqual(status,200)
            self.assertEqual(json.loads(receipt)['attribution'],'grant-holder')
            self.assertEqual(self.store.manage(self.raw,credential,'hosted-grant-create')[0],401)
        retained=self.store.retrieve('7'*32,copied_credential)
        revoke=encode_event(dict(version='0',purpose='hosted-grant-revoke',
                                operation='c'*32,grant='7'*32))
        self.assertEqual(self.store.manage(revoke,'management','hosted-grant-revoke')[0],200)
        for credential in [self.secret,copied_credential]:
            self.assertEqual(self.store.retrieve('7'*32,credential)[0],403)
        # Revocation did not erase the response already returned to a holder.
        self.assertEqual(retained[0],200)

    def test_sender_restart_and_encrypted_storage(self):
        sender=HostedSender(self.root/'sender.db',key=self.keys[2],service='https://host.example',owner='enp0:'+'a'*64)
        sender.retain(self.raw);self.assertEqual(sender.load('6'*32),self.raw)
        reopened=HostedSender(self.root/'sender.db',key=self.keys[2],service='https://host.example',owner='enp0:'+'a'*64)
        self.assertEqual(reopened.load('6'*32),self.raw)
        self.assertNotIn(self.secret.encode(),(self.root/'sender.db').read_bytes())
    def test_ciphertext_nonce_key_and_identity_tampering(self):
        self.create()
        with self.store.db() as db:original=db.execute('SELECT nonce,ciphertext FROM vault').fetchone()
        for column,index in [('nonce',0),('ciphertext',1)]:
            changed=bytes([original[index][0]^1])+original[index][1:]
            with self.store.db() as db:db.execute('UPDATE vault SET '+column+'=?',(changed,))
            with self.assertRaises(InvalidTag):self.store.retrieve('7'*32,self.secret)
            with self.store.db() as db:db.execute('UPDATE vault SET nonce=?,ciphertext=?',original)
        self.store.vault.owner='enp0:'+'b'*64
        with self.assertRaises(InvalidTag):self.store.retrieve('7'*32,self.secret)
    def test_wrong_content_config_and_database_loss(self):
        raw=encode_event(dict(self.req,recipient='f'*32))
        self.assertEqual(self.store.manage(raw,'management','hosted-grant-create')[0],403)
        self.path.unlink()
        with self.assertRaises(Exception):self.create()
        self.assertFalse(self.path.exists())
    def test_management_scope_expiry_and_reply_row_binding(self):
        self.store.management_grant['scopes']=['inspect'];self.assertEqual(self.create()[0],403)
        self.store.management_grant['scopes']=['create'];self.store.management_grant['expires']=99;self.assertEqual(self.create()[0],401)
    def test_actual_crashes_around_host_and_sender_commit(self):
        import subprocess
        import sys
        config=dict(service=self.store.service,owner=self.store.owner,management_token='management',management_grant=self.store.management_grant,configuration=self.configuration)
        script="""import json,sys,os
from hosted_access import HostedStore
from vault_fixture import HostedStore
from vault_fixture import HostedSender
config=json.loads(sys.argv[2]);raw=bytes.fromhex(sys.argv[3]);keys=[bytes.fromhex(k) for k in sys.argv[4:7]]
hook=lambda point:os._exit(71) if point==sys.argv[8] else None
if sys.argv[7]=='host':
 s=HostedStore(sys.argv[1],host_key=keys[0],reply_key=keys[1],clock=lambda:100,**config);s.manage(raw,'management','hosted-grant-create',crash=hook)
else:
 s=HostedSender(sys.argv[1],key=keys[2],service=config['service'],owner=config['owner']);s.retain(raw,crash=hook)
"""
        for role in ('host','sender'):
            path=self.path if role=='host' else self.root/'sender-crash.db'
            for point in ('before-commit','after-commit'):
                result=subprocess.run([sys.executable,'-c',script,str(path),json.dumps(config),self.raw.hex(),*[k.hex() for k in self.keys],role,point],cwd=Path(__file__).parent)
                self.assertEqual(result.returncode,71)
                if role=='host':self.assertEqual(self.store.lookup('6'*32,'management')[0],404 if point=='before-commit' else 200)
                else:
                    sender=HostedSender(path,key=self.keys[2],service=self.store.service,owner=self.store.owner)
                    if point=='before-commit':
                        with self.assertRaises(ValueError):sender.load('6'*32)
                    else:self.assertEqual(sender.load('6'*32),self.raw)
    def test_minimal_notification_loopback_and_no_ambiguous_retry(self):
        from hosted_notification import prepare,submit
        from smtp_loopback import roundtrip
        sender=HostedSender(self.root/'sender-notify.db',key=self.keys[2],service=self.store.service,owner=self.store.owner)
        sender.retain(self.raw);receipt=json.loads(self.create()[1])
        wire=prepare(sender,'6'*32,from_address='alice@example.invalid',recipient_address='bob@example.invalid')
        self.assertNotIn(b'CONFIDENTIAL_CONTENT_MARKER',wire)
        self.assertEqual(submit(sender,'6'*32,confirmed_creation=receipt,transport=roundtrip),wire)
        with self.assertRaises(ValueError):submit(sender,'6'*32,confirmed_creation=receipt,transport=roundtrip)

    def test_management_reads_recheck_expiry_after_database_entry(self):
        original_create=self.create()
        raw=encode_event(dict(version='0',purpose='hosted-holder-reply',operation='9'*32,text='Reply'))
        original_reply=self.store.reply('7'*32,raw,self.secret)
        for read in (lambda:self.store.lookup('6'*32,'management'),
                     lambda:self.store.management_reply('7'*32,'9'*32,'management')):
            self.now=100
            real_db=self.store.db
            @contextmanager
            def expired_on_entry():
                with real_db() as db:
                    self.now=1001
                    yield db
            with self.subTest(read=read):
                try:
                    with patch.object(self.store,'db',expired_on_entry):
                        self.assertEqual(read(),(401,b''))
                finally:self.now=100
        self.assertEqual(self.store.lookup('6'*32,'management'),original_create)
        self.assertEqual(self.store.management_reply('7'*32,'9'*32,'management'),original_reply)

    def test_management_reads_recheck_owner_and_scope_after_database_entry(self):
        self.create()
        raw=encode_event(dict(version='0',purpose='hosted-holder-reply',operation='9'*32,text='Reply'))
        self.store.reply('7'*32,raw,self.secret)
        for method in ('lookup','reply'):
            for change,expected in [('owner',401),('scope',403)]:
                with self.subTest(method=method,change=change):
                    real_db=self.store.db
                    original=dict(self.store.management_grant)
                    @contextmanager
                    def changed_on_entry():
                        with real_db() as db:
                            if change=='owner':self.store.management_grant['owner']='enp0:'+'b'*64
                            else:self.store.management_grant['scopes']=[]
                            yield db
                    try:
                        with patch.object(self.store,'db',changed_on_entry):
                            result=(self.store.lookup('6'*32,'management') if method=='lookup'
                                    else self.store.management_reply('7'*32,'9'*32,'management'))
                            self.assertEqual(result,(expected,b''))
                    finally:self.store.management_grant=original

    def test_management_reads_expire_while_waiting_for_actual_database_lock(self):
        import sqlite3
        import threading
        self.create()
        raw=encode_event(dict(version='0',purpose='hosted-holder-reply',operation='9'*32,text='Reply'))
        self.store.reply('7'*32,raw,self.secret)
        for method in ('lookup','reply'):
            with self.subTest(method=method):
                self.now=100
                blocker=sqlite3.connect(self.path)
                blocker.execute('BEGIN IMMEDIATE')
                began=threading.Event();finished=threading.Event();result=[]
                real_db=self.store.db
                @contextmanager
                def traced_db():
                    with real_db() as db:
                        db.set_trace_callback(lambda sql:began.set() if sql=='BEGIN IMMEDIATE' else None)
                        yield db
                def read():
                    try:
                        result.append(self.store.lookup('6'*32,'management') if method=='lookup'
                                      else self.store.management_reply('7'*32,'9'*32,'management'))
                    except Exception as error:result.append(error)
                    finally:finished.set()
                worker=threading.Thread(target=read)
                try:
                    with patch.object(self.store,'db',traced_db):
                        worker.start()
                        self.assertTrue(began.wait(2),'read did not request its serialized snapshot')
                        self.assertFalse(finished.wait(0.05),'read bypassed the held write lock')
                        self.now=1001
                        blocker.commit()
                        worker.join(2)
                        self.assertFalse(worker.is_alive())
                        self.assertEqual(result,[(401,b'')])
                finally:
                    blocker.rollback();blocker.close()
                    worker.join(2)
                    self.now=100

    def test_management_reply_history_after_revocation(self):
        self.create();raw=encode_event(dict(version='0',purpose='hosted-holder-reply',operation='9'*32,text='Reply'))
        original=self.store.reply('7'*32,raw,self.secret)
        revoke=encode_event(dict(version='0',purpose='hosted-grant-revoke',operation='8'*32,grant='7'*32))
        self.store.manage(revoke,'management','hosted-grant-revoke')
        self.assertEqual(self.store.reply_status('7'*32,'9'*32,self.secret)[0],403)
        self.assertEqual(self.store.management_reply('7'*32,'9'*32,'management'),original)
        self.assertEqual(self.store.management_reply('7'*32,'9'*32,self.secret)[0],401)
        self.store.management_grant['owner']='enp0:'+'b'*64
        self.assertEqual(self.store.management_reply('7'*32,'9'*32,'management'),(401,b''))
