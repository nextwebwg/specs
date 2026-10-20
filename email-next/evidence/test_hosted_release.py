import json
import ssl
import threading
import unittest
from event_encoding import encode_event
from vault_fixture import HostedSender
from hosted_management import HostedManagementClient
from hosted_notification_release import HostedNotificationRelease
from hosted_https import make_hosted_server
import test_hosted_access
import test_service_tls
from test_sender_release import LocalSMTP

class HostedReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):test_service_tls.ServiceTLSTest.setUpClass()
    @classmethod
    def tearDownClass(cls):test_service_tls.ServiceTLSTest.tearDownClass()
    def setUp(self):
        f=test_hosted_access.HostedTests();f.setUp();self.f=f;self.addCleanup(f.doCleanups)
        cert,key=test_service_tls.ServiceTLSTest('test_valid_san').leaf('host.example')
        context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.minimum_version=ssl.TLSVersion.TLSv1_3;context.load_cert_chain(cert,key)
        self.server=make_hosted_server(f.store,context)
        origin='https://host.example:'+str(self.server.server_port)
        f.store.service=origin;f.store.management_grant['service']=origin;f.store.vault.service=origin;f.store.reply_vault.service=origin
        self.thread=threading.Thread(target=self.server.serve_forever);self.thread.start();self.addCleanup(self.stop)
        self.sender=HostedSender(f.root/'release.db',key=f.keys[2],service=origin,owner=f.store.owner);self.sender.retain(f.raw)
        self.client=HostedManagementClient(self.sender,ca_file=str(test_service_tls.ServiceTLSTest.ca_file),address=('127.0.0.1',self.server.server_port))
        self.release=HostedNotificationRelease(self.sender)
        self.config=dict(service=origin,owner=f.store.owner,recipient=f.req['recipient'],replyDestination=f.req['replyDestination'],fromAddress='alice@example.invalid',recipientAddress='bob@example.invalid',enabled=True)
        self.release.configure(expected_revision=0,configuration=self.config)
    def stop(self):self.server.shutdown();self.server.server_close();self.thread.join()
    def prepare(self):
        result=self.client.request('6'*32,'management');self.assertEqual(result['http'],200)
        self.release.prepare('6'*32,evidence=result['evidence'],credible_time=(100,100));return result['evidence']
    def test_real_https_provenance_and_encrypted_exact_smtp(self):
        self.prepare();server=LocalSMTP()
        result=self.release.submit('6'*32,port=server.port,credible_time=lambda:(100,100));server.done()
        self.assertEqual(result['state'],'smtp-submitted');self.assertIn(self.f.secret.encode(),__import__('quopri').decodestring(server.wire))
        self.assertNotIn(b'CONFIDENTIAL_CONTENT_MARKER',server.wire)
        self.assertNotIn(self.f.secret.encode(),(self.f.root/'release.db').read_bytes())
        with self.assertRaises(ValueError):self.release.submit('6'*32,port=server.port,credible_time=lambda:(100,100))
    def test_forged_record_id_and_bad_management_credential(self):
        self.assertEqual(self.client.request('6'*32,self.f.secret)['http'],401)
        with self.assertRaises(ValueError):self.release.prepare('6'*32,evidence='forged',credible_time=(100,100))
    def test_historical_lookup_after_creation_and_revoke_holds(self):
        self.f.create();evidence=self.client.request('6'*32,'management',lookup=True)['evidence']
        self.release.prepare('6'*32,evidence=evidence,credible_time=(100,100))
        raw=encode_event(dict(version='0',purpose='hosted-grant-revoke',operation='8'*32,grant='7'*32))
        self.sender.retain(raw,purpose='hosted-grant-revoke');self.client.request('8'*32,'management')
        with self.assertRaisesRegex(ValueError,'revocation'):self.release.submit('6'*32,port=1,credible_time=lambda:(100,100))
    def test_policy_change_before_data_aborts(self):
        self.prepare();server=LocalSMTP()
        def hook(stage):
            if stage=='before-data-check':self.release.configure(expected_revision=1,configuration=dict(self.config,enabled=False))
        result=self.release.submit('6'*32,port=server.port,credible_time=lambda:(100,100),hook=hook);server.done()
        self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(server.wire)
    def test_expiry_rechecked_before_data(self):
        self.prepare();server=LocalSMTP();times=iter([(100,100),(100,101)])
        result=self.release.submit('6'*32,port=server.port,credible_time=lambda:next(times));server.done()
        self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(server.wire)
    def test_invalid_time_and_restart_no_repeat_after_lost_response(self):
        evidence=self.prepare()
        with self.assertRaises(ValueError):self.release.prepare('6'*32,evidence=evidence,credible_time=(True,100))
        server=LocalSMTP(drop=True)
        with self.assertRaises(Exception):self.release.submit('6'*32,port=server.port,credible_time=lambda:(100,100))
        server.done();reopened=HostedNotificationRelease(self.sender)
        with self.assertRaises(ValueError):reopened.submit('6'*32,port=server.port,credible_time=lambda:(100,100))
        with self.sender.db() as db:self.assertEqual(db.execute('SELECT state FROM hosted_attempts').fetchone()[0],'uncertain')

    def test_explicit_uncertain_retry_reuses_exact_wire_and_preserves_attempts(self):
        self.prepare();first=LocalSMTP(drop=True)
        with self.assertRaises(Exception):self.release.submit('6'*32,port=first.port,credible_time=lambda:(100,100))
        first.done()
        with self.assertRaisesRegex(ValueError,'uncertain'):self.release.submit('6'*32,port=1,credible_time=lambda:(100,100))
        second=LocalSMTP();self.release.submit('6'*32,port=second.port,credible_time=lambda:(100,100),retry_uncertain=True);second.done()
        self.assertEqual(first.wire,second.wire)
        self.assertEqual([r['state'] for r in self.release.reconcile('6'*32)],['uncertain','smtp-submitted'])
        with self.assertRaises(ValueError):self.release.submit('6'*32,port=1,credible_time=lambda:(100,100),retry_uncertain=True)
    def test_temporary_retry_and_permanent_hold(self):
        self.prepare();first=LocalSMTP(final=b'450 later\r\n')
        self.assertEqual(self.release.submit('6'*32,port=first.port,credible_time=lambda:(100,100))['state'],'temporary');first.done()
        second=LocalSMTP(final=b'550 denied\r\n')
        self.assertEqual(self.release.submit('6'*32,port=second.port,credible_time=lambda:(100,100))['state'],'permanent');second.done()
        self.assertEqual(first.wire,second.wire)
        with self.assertRaises(ValueError):self.release.submit('6'*32,port=1,credible_time=lambda:(100,100),retry_uncertain=True)
    def test_authenticated_bound_contradiction_holds_but_unrelated_is_rejected(self):
        self.prepare();original=self.f.store.manage
        def changed(raw,token,purpose,**kwargs):
            status,body=original(raw,token,purpose,**kwargs);receipt=json.loads(body);receipt['reason']='revoked'
            return status,encode_event(receipt)
        self.f.store.manage=changed
        result=self.client.request('6'*32,'management');self.assertEqual(result['state'],'conflict')
        with self.assertRaises(ValueError):self.release.submit('6'*32,port=1,credible_time=lambda:(100,100))
        with self.sender.db() as db:self.assertEqual(db.execute("SELECT count(*) FROM management_evidence WHERE state='conflict'").fetchone()[0],2)
        def unrelated(raw,token,purpose,**kwargs):
            status,body=original(raw,token,purpose,**kwargs);receipt=json.loads(body);receipt['operation']='f'*32
            return status,encode_event(receipt)
        self.f.store.manage=unrelated
        with self.assertRaises(ValueError):self.client.request('6'*32,'management')
        with self.sender.db() as db:self.assertEqual(db.execute('SELECT count(*) FROM management_evidence').fetchone()[0],2)
    def test_canonical_alias_lock_and_inherited_worker_denial(self):
        import os
        self.prepare();alias=self.f.root/'alias.db';alias.symlink_to(self.sender.path)
        sender=HostedSender(alias,key=self.f.keys[2],service=self.f.store.service,owner=self.f.store.owner)
        other=HostedNotificationRelease(sender);self.assertEqual(sender.path,self.sender.path)
        with self.release._locked():
            with self.assertRaises(BlockingIOError):other.reconcile('6'*32)
        import subprocess,sys
        script="""import os,sys
from vault_fixture import HostedSender
from hosted_notification_release import HostedNotificationRelease
s=HostedSender(sys.argv[1],key=bytes.fromhex(sys.argv[2]),service=sys.argv[3],owner=sys.argv[4]);r=HostedNotificationRelease(s)
with r._locked():
 child=os.fork()
 if child==0:
  try:r.reconcile('6'*32)
  except ValueError:os._exit(0)
  os._exit(1)
 _,status=os.waitpid(child,0)
 os._exit(os.waitstatus_to_exitcode(status))
"""
        result=subprocess.run([sys.executable,'-c',script,self.sender.path,self.f.keys[2].hex(),self.f.store.service,self.f.store.owner],cwd=__import__('pathlib').Path(__file__).parent)
        self.assertEqual(result.returncode,0)
    def test_subprocess_crash_reconciles_released_attempt_as_uncertain(self):
        import subprocess,sys
        self.prepare()
        script="""import os,sys
from vault_fixture import HostedSender
from hosted_notification_release import HostedNotificationRelease
s=HostedSender(sys.argv[1],key=bytes.fromhex(sys.argv[2]),service=sys.argv[3],owner=sys.argv[4])
r=HostedNotificationRelease(s)
r.submit('6'*32,port=1,credible_time=lambda:(100,100),hook=lambda stage:os._exit(73) if stage=='after-release' else None)
"""
        result=subprocess.run([sys.executable,'-c',script,self.sender.path,self.f.keys[2].hex(),self.f.store.service,self.f.store.owner],cwd=__import__('pathlib').Path(__file__).parent)
        self.assertEqual(result.returncode,73)
        self.assertEqual(self.release.reconcile('6'*32)[0]['state'],'uncertain')
        with self.assertRaises(ValueError):self.release.submit('6'*32,port=1,credible_time=lambda:(100,100))

if __name__=='__main__':unittest.main()
