import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from identity_store import IdentityStore
from provider_mls import make_device,call
from mls_receive import MlsReceive
from sender_release import SenderRelease

class SenderPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'identity.sqlite'
        self.binary=Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR'])/'provider-mls'
        self.a=make_device(self.binary,1,2);self.b=make_device(self.binary,3,4)
        self.time={'earliest':str(max(self.a['time'],self.b['time'])),'latest':str(max(self.a['time'],self.b['time']))}
        self.identity=IdentityStore(self.path)
        for device in [self.a,self.b]:self.identity.observe(device['record'],first_contact_policy='allow-unverified')
        self.group=call(self.binary,op='invite',checkpoint=self.a['checkpoint'],key=self.a['key'],identity=self.a['identity'],package=self.b['package'])
        MlsReceive(self.identity,self.binary.with_name('receive-staged')).install_fixture(self.group['group'],self.group['checkpoint'])
        self.sender=SenderRelease(self.identity,self.binary);self.sender.configure(expected_revision=0)
        self.application=(Path(__file__).parent/'mls-smoke/fixtures/message.json').read_bytes()
    def tearDown(self):self.identity.close();self.temp.cleanup()
    def prepare(self,**kwargs):return self.sender.prepare('delivery1',self.application,key=self.a['key'],envelope_sender='alice@example.invalid',recipients=['bob@example.invalid'],time=self.time,**kwargs)
    def test_prepare_restart_exact_retry_advances_crypto_once_without_socket(self):
        before=self.identity.db.execute('SELECT snapshot FROM mls_checkpoint').fetchone()[0]
        with patch('socket.socket',side_effect=AssertionError('No transport before release')):wire=self.prepare()
        row=self.identity.db.execute('SELECT revision,snapshot FROM mls_checkpoint').fetchone()
        self.assertEqual(row[0],1);self.assertNotEqual(row[1],before)
        self.identity.close();self.identity=IdentityStore(self.path);self.sender=SenderRelease(self.identity,self.binary)
        with patch('sender_release.call',side_effect=AssertionError('Do not encrypt retry')):self.assertEqual(self.prepare(),wire)
        self.assertEqual(self.identity.db.execute('SELECT revision,snapshot FROM mls_checkpoint').fetchone(),row)
        self.assertIn(b'Message-ID:',wire)
    def test_precommit_failure_discards_staged_checkpoint_and_prepared_record(self):
        before=self.identity.db.execute('SELECT revision,snapshot FROM mls_checkpoint').fetchone()
        def fail(stage):
            if stage=='before-prepare-commit':raise RuntimeError('injected')
        with self.assertRaises(RuntimeError):self.prepare(crash=fail)
        self.assertEqual(self.identity.db.execute('SELECT revision,snapshot FROM mls_checkpoint').fetchone(),before)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM sender_prepared').fetchone()[0],0)
        self.prepare();self.assertEqual(self.identity.db.execute('SELECT revision FROM mls_checkpoint').fetchone()[0],1)
    def test_strict_policy_cannot_prepare(self):
        self.sender.configure(expected_revision=1,trust_policy='require-verification')
        with self.assertRaisesRegex(ValueError,'verification-required'):self.prepare()
        self.assertEqual(self.identity.db.execute('SELECT revision FROM mls_checkpoint').fetchone()[0],0)


def child_submit(path,binary,port,time,stage):
    from sender_worker import SenderWorker
    identity=IdentityStore(path);sender=SenderRelease(identity,binary)
    with SenderWorker(sender) as worker:
        worker.submit('delivery1',port=port,time=time,crash=lambda where:os._exit(81) if where==stage else None)


def child_hold(path,binary,ready,finish):
    from sender_worker import SenderWorker
    identity=IdentityStore(path)
    with SenderWorker(SenderRelease(identity,binary)):
        ready.set();finish.wait(15)
    identity.close()


class LocalSMTP:
    def __init__(self,final=b'250 accepted\r\n',drop=False,rcpt=None):
        import socket,threading
        self.listener=socket.socket();self.listener.bind(('127.0.0.1',0));self.listener.listen(1);self.listener.settimeout(10)
        self.port=self.listener.getsockname()[1];self.wire=None;self.error=None;self.connected=False
        def serve():
            try:
                connection,_=self.listener.accept();self.connected=True
                with connection:
                    connection.settimeout(10)
                    with connection.makefile('rwb') as stream:
                        def reply(b):stream.write(b);stream.flush()
                        reply(b'220 fixture\r\n');index=0
                        while True:
                            line=stream.readline(10000)
                            if not line:return
                            cmd=line.upper()
                            if cmd.startswith(b'EHLO'):reply(b'250 fixture\r\n')
                            elif cmd.startswith(b'MAIL'):reply(b'250 sender\r\n')
                            elif cmd.startswith(b'RCPT'):
                                reply(rcpt[index] if rcpt else b'250 recipient\r\n');index+=1
                            elif cmd==b'DATA\r\n':
                                reply(b'354 data\r\n');parts=[]
                                while True:
                                    line=stream.readline(10000)
                                    if line==b'.\r\n':break
                                    if not line:raise ValueError('Incomplete DATA')
                                    parts.append(line[1:] if line.startswith(b'..') else line)
                                self.wire=b''.join(parts)
                                if not drop:reply(final)
                                return
                            else:reply(b'503 sequence\r\n')
            except BaseException as error:self.error=error
            finally:self.listener.close()
        self.thread=threading.Thread(target=serve);self.thread.start()
    def done(self):
        self.thread.join(12)
        if self.thread.is_alive():raise AssertionError('Server did not stop')
        if self.error:raise self.error


class SenderTransportTests(SenderPreparationTests):
    # Preparation tests remain inherited as integration setup regressions.
    def test_release_handoff_and_no_automatic_repeat(self):
        from sender_worker import SenderWorker
        wire=self.prepare();server=LocalSMTP()
        with SenderWorker(self.sender) as worker:
            outcome=worker.submit('delivery1',port=server.port,time=self.time)
            self.assertEqual(outcome['state'],'accepted')
            with patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No second socket')):
                with self.assertRaisesRegex(ValueError,'Already handed off'):worker.submit('delivery1',port=server.port,time=self.time)
        server.done();self.assertEqual(server.wire,wire)
    def test_live_process_lock_cannot_be_taken_over(self):
        import multiprocessing
        from sender_worker import SenderWorker
        ctx=multiprocessing.get_context('spawn');ready=ctx.Event();finish=ctx.Event()
        child=ctx.Process(target=child_hold,args=(self.path,self.binary,ready,finish));child.start()
        try:
            self.assertTrue(ready.wait(10))
            with self.assertRaises(BlockingIOError):
                with SenderWorker(self.sender):pass
        finally:finish.set();child.join(15)
        self.assertEqual(child.exitcode,0)
        with SenderWorker(self.sender):pass
    def test_server_acceptance_then_process_death_retains_uncertainty(self):
        import multiprocessing
        from sender_worker import SenderWorker
        wire=self.prepare();server=LocalSMTP()
        child=multiprocessing.get_context('spawn').Process(target=child_submit,args=(self.path,self.binary,server.port,self.time,'after-final-response'))
        child.start();child.join(15)
        if child.is_alive():child.terminate();child.join();self.fail('Worker timeout')
        self.assertEqual(child.exitcode,81);server.done();self.assertEqual(server.wire,wire)
        with SenderWorker(self.sender) as worker:
            self.assertEqual(self.identity.db.execute('SELECT state FROM sender_attempts').fetchone()[0],'uncertain')
            with patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No silent retry')):
                with self.assertRaisesRegex(ValueError,'Uncertain'):worker.submit('delivery1',port=server.port,time=self.time)
            retry=LocalSMTP();self.assertEqual(worker.submit('delivery1',port=retry.port,time=self.time,retry_uncertain=True)['state'],'accepted');retry.done()
            self.assertEqual(retry.wire,wire)
    def test_real_accepted_identity_successor_blocks_release_before_socket(self):
        import base64,hashlib
        from event_encoding import encode_event
        from provider_mls import sign
        from sender_worker import SenderWorker
        self.prepare();device=self.b;record=device['record'];previous=json.loads(base64.b64decode(record['state']))
        successor=dict(previous,record='7'*32,revision='1',previous=[device['state']])
        raw=encode_event(successor);digest=hashlib.sha256(raw).hexdigest()
        bundle=dict(version='0',purpose='identity-bundle',principal=device['principal'],states=[{'payload':base64.b64encode(raw).decode(),'signature':sign(self.binary,device,'email-next/identity-state/v0',raw)},{'payload':record['state'],'signature':record['stateProof']}],bindings=[{'payload':record['binding'],'authorization':record['authorization'],'possession':record['possession']}])
        result=self.identity.accept_successor(encode_event(bundle),candidate_digest=digest,time=self.time)
        self.assertEqual(result['status'],'accepted-unverified')
        with SenderWorker(self.sender) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No stale release socket')):
            with self.assertRaisesRegex(ValueError,'Changed identity'):worker.submit('delivery1',port=1,time=self.time)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM sender_attempts').fetchone()[0],0)
    def test_changed_policy_blocks_before_socket(self):
        from sender_worker import SenderWorker
        self.prepare();self.sender.configure(expected_revision=1,trust_policy='require-verification')
        with SenderWorker(self.sender) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No stale socket')):
            with self.assertRaisesRegex(ValueError,'Changed policy'):worker.submit('delivery1',port=1,time=self.time)
    def test_lost_final_reply_and_explicit_temporary_rejection_differ(self):
        from sender_worker import SenderWorker
        self.prepare();server=LocalSMTP(drop=True)
        with SenderWorker(self.sender) as worker:
            self.assertEqual(worker.submit('delivery1',port=server.port,time=self.time)['state'],'uncertain');server.done()
            server=LocalSMTP(final=b'451 temporary\r\n')
            rejected=worker.submit('delivery1',port=server.port,time=self.time,retry_uncertain=True);server.done()
            self.assertEqual(rejected['state'],'rejected');self.assertTrue(rejected['result']['retryable'])
    def test_partial_recipient_result_preserves_final_data_scope(self):
        from sender_worker import SenderWorker
        self.sender.prepare('delivery1',self.application,key=self.a['key'],envelope_sender='alice@example.invalid',recipients=['bob@example.invalid','second@example.invalid'],time=self.time)
        server=LocalSMTP(rcpt=[b'250 first\r\n',b'550 second refused\r\n'])
        with SenderWorker(self.sender) as worker:result=worker.submit('delivery1',port=server.port,time=self.time)
        server.done();self.assertEqual(result['state'],'accepted')
        self.assertEqual(result['result']['acceptedRecipients'],['bob@example.invalid'])
        self.assertEqual([r['code'] for r in result['result']['rcpt']],[250,550])
    def test_observed_policy_change_after_release_aborts_before_data(self):
        from sender_worker import SenderWorker
        self.prepare();server=LocalSMTP()
        def change(stage):
            if stage=='after-release':self.sender.configure(expected_revision=1,trust_policy='require-verification')
        with SenderWorker(self.sender) as worker:result=worker.submit('delivery1',port=server.port,time=self.time,crash=change)
        server.done();self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(server.wire)
    def test_multiple_attempts_retry_only_temporary_recipient_scope(self):
        from sender_worker import SenderWorker
        targets=['bob@example.invalid','later@example.invalid','never@example.invalid']
        wire=self.sender.prepare('delivery1',self.application,key=self.a['key'],envelope_sender='alice@example.invalid',recipients=targets,time=self.time)
        first=LocalSMTP(rcpt=[b'250 accepted\r\n',b'450 later\r\n',b'550 never\r\n'])
        with SenderWorker(self.sender) as worker:
            result=worker.submit('delivery1',port=first.port,time=self.time);first.done()
            self.assertEqual(result['state'],'accepted')
            second=LocalSMTP();result=worker.submit('delivery1',port=second.port,time=self.time);second.done()
            self.assertEqual([r['recipient'] for r in result['result']['rcpt']],['later@example.invalid'])
            self.assertEqual(second.wire,wire)
            with self.assertRaisesRegex(ValueError,'Already handed off'):worker.submit('delivery1',port=1,time=self.time)
        scopes=[json.loads(row[0])['envelope']['recipients'] for row in self.identity.db.execute('SELECT evidence FROM sender_attempts ORDER BY rowid')]
        self.assertEqual(scopes,[targets,['later@example.invalid']])
    def test_mixed_rejected_recipients_preserve_temporary_retry(self):
        from sender_worker import SenderWorker
        targets=['later@example.invalid','never@example.invalid']
        self.sender.prepare('delivery1',self.application,key=self.a['key'],envelope_sender='alice@example.invalid',recipients=targets,time=self.time)
        first=LocalSMTP(rcpt=[b'450 later\r\n',b'550 never\r\n'])
        with SenderWorker(self.sender) as worker:
            result=worker.submit('delivery1',port=first.port,time=self.time);first.done();self.assertEqual(result['state'],'rejected');self.assertIsNone(first.wire)
            second=LocalSMTP();result=worker.submit('delivery1',port=second.port,time=self.time);second.done()
            self.assertEqual(result['result']['acceptedRecipients'],['later@example.invalid'])
    def test_uncertain_scope_survives_other_recipient_success(self):
        from sender_worker import SenderWorker
        targets=['uncertain@example.invalid','later@example.invalid','never@example.invalid']
        self.sender.prepare('delivery1',self.application,key=self.a['key'],envelope_sender='alice@example.invalid',recipients=targets,time=self.time)
        first=LocalSMTP(drop=True,rcpt=[b'250 accepted\r\n',b'450 later\r\n',b'550 never\r\n'])
        with SenderWorker(self.sender) as worker:
            self.assertEqual(worker.submit('delivery1',port=first.port,time=self.time)['state'],'uncertain');first.done()
            second=LocalSMTP();result=worker.submit('delivery1',port=second.port,time=self.time);second.done()
            self.assertEqual(result['result']['acceptedRecipients'],['later@example.invalid'])
            with self.assertRaisesRegex(ValueError,'Uncertain'):worker.submit('delivery1',port=1,time=self.time)
            third=LocalSMTP();result=worker.submit('delivery1',port=third.port,time=self.time,retry_uncertain=True);third.done()
            self.assertEqual(result['result']['acceptedRecipients'],['uncertain@example.invalid'])
    def test_real_receiver_revocation_blocks_prepared_release(self):
        import base64,hashlib
        from event_encoding import encode_event
        from provider_mls import sign
        from sender_worker import SenderWorker
        self.prepare();b=self.b;c=make_device(self.binary,3,5)
        old=json.loads(base64.b64decode(b['record']['state']))
        binding=json.loads(base64.b64decode(c['record']['binding']));binding.update(record='8'*32,authority={'kind':'state','digest':b['state']})
        binding_raw=encode_event(binding);binding_digest=hashlib.sha256(binding_raw).hexdigest()
        delegated={'payload':base64.b64encode(binding_raw).decode(),'authorization':sign(self.binary,b,'email-next/device-binding/v0',binding_raw),'possession':sign(self.binary,c,'email-next/device-possession/v0',binding_raw)}
        original={'payload':b['record']['binding'],'authorization':b['record']['authorization'],'possession':b['record']['possession']}
        def wrap(value,device):
            raw=encode_event(value)
            return {'payload':base64.b64encode(raw).decode(),'signature':sign(self.binary,device,'email-next/identity-state/v0',raw)},hashlib.sha256(raw).hexdigest()
        added=dict(old,record='9'*32,revision='1',previous=[b['state']],bindings=old['bindings']+[{'device':c['device'],'digest':binding_digest}])
        added_entry,added_digest=wrap(added,b)
        bundle=dict(version='0',purpose='identity-bundle',principal=b['principal'],states=[added_entry,{'payload':b['record']['state'],'signature':b['record']['stateProof']}],bindings=[original,delegated])
        self.assertEqual(self.identity.accept_successor(encode_event(bundle),candidate_digest=added_digest,time=self.time)['status'],'accepted-unverified')
        removed=dict(added,record='a'*32,revision='2',previous=[added_digest],bindings=[{'device':c['device'],'digest':binding_digest}],revoked=[b['device']],signer=c['device'])
        removed_entry,removed_digest=wrap(removed,c);bundle['states']=[removed_entry,added_entry]
        self.assertEqual(self.identity.accept_successor(encode_event(bundle),candidate_digest=removed_digest,time=self.time)['status'],'accepted-unverified')
        authority=self.identity.check_device(bytes.fromhex(b['identity']),bytes.fromhex(b['key']),role='receive',time=self.time,trust_policy='allow-unverified')
        self.assertEqual(authority['reason'],'revoked')
        with SenderWorker(self.sender) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('Revoked recipient must not receive')):
            with self.assertRaisesRegex(ValueError,'Current authority: unauthorized'):worker.submit('delivery1',port=1,time=self.time)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM sender_attempts').fetchone()[0],0)
    def test_same_epoch_receive_advancement_keeps_prepared_delivery_eligible(self):
        from event_encoding import encode_event
        from sender_worker import SenderWorker
        wire=self.prepare();before=self.identity.db.execute('SELECT revision,snapshot FROM mls_checkpoint').fetchone()
        joined=call(self.binary,op='join',checkpoint=self.b['checkpoint'],key=self.b['key'],welcome=self.group['welcome'],tree=self.group['tree'])
        incoming=json.loads(self.application);incoming['principal']=self.b['principal'];incoming['event']='c'*32;incoming['operation']['text']='A simultaneous message'
        sent=call(self.binary,op='send',checkpoint=joined['checkpoint'],key=self.b['key'],group=joined['group'],application=encode_event(incoming).hex())
        result=MlsReceive(self.identity,self.binary.with_name('receive-staged')).receive(bytes.fromhex(sent['wire']),time=self.time,trust_policy='allow-unverified')
        self.assertEqual(result['status'],'projected-context-matched')
        after=self.identity.db.execute('SELECT revision,snapshot FROM mls_checkpoint').fetchone();self.assertEqual(after[0],before[0]+1);self.assertNotEqual(after[1],before[1])
        server=LocalSMTP()
        with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit('delivery1',port=server.port,time=self.time)['state'],'accepted')
        server.done();self.assertEqual(server.wire,wire)
