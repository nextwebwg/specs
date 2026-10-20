from vault_fixture import fresh_key
import json
import os
from pathlib import Path
import ssl
import threading
import unittest
from unittest.mock import patch
import test_joined_questions
import test_service_tls
from event_encoding import encode_event,serialize_json,decode_event
from hosted_access import HostedStore,credential
from vault_fixture import HostedStore
from vault_fixture import HostedSender
from hosted_https import make_hosted_server
from hosted_management import HostedManagementClient
from hosted_reply_export import HostedReplyExporter
from hosted_reply_admission import template_limit,retain_template
from hosted_observer_release import HostedObserverRelease
from sender_release import SenderRelease
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from identity_store import IdentityStore

class ObserverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):test_service_tls.ServiceTLSTest.setUpClass()
    @classmethod
    def tearDownClass(cls):test_service_tls.ServiceTLSTest.tearDownClass()
    def setUp(self):
        self.f=test_joined_questions.JoinedQuestions();original=test_joined_questions.call
        def call(binary,**args):
            if args.get('op')=='create':
                context=json.loads(bytes.fromhex(args['context']));context['application']['operations'].insert(1,'hosted-holder-observation');args['context']=encode_event(context).hex()
            return original(binary,**args)
        with patch('test_joined_questions.call',side_effect=call):self.f.setUp()
        self.addCleanup(self.f.tearDown);self.f.application['operations'].insert(1,'hosted-holder-observation')
        for sender in self.f.senders:
            for d in self.f.devices:sender.receiver.application_agreement.configure_device(self.f.group,d['identity'],d['key'],self.f.application)
        self.target=self.f.event(1,'e',dict(kind='message',text='Original hosted text',replyTo=[]))
        wire=self.f.prepare(1,self.target)
        self.f.receive(0,wire);self.f.receive(2,wire)
        self.root=Path(self.f.temp.name);self.keys=[fresh_key(self.root/'vault.db') for _ in range(3)];self.secret=credential()
        self.config=dict(contribution={k:self.target[k] for k in ('principal','conversation','event')},content=dict(kind='text',text=self.target['operation']['text']),recipient='4'*32,replyDestination='5'*32)
        path=self.root/'host.db';HostedStore.provision(path)
        self.store=HostedStore(path,service='https://host.example',owner=self.f.principals[0],management_token='manager',management_grant=dict(issuer='fixture',service='https://host.example',owner=self.f.principals[0],notBefore=0,expires=1000,scopes=['create','inspect','revoke','read-management']),host_key=self.keys[0],reply_key=self.keys[1],configuration=self.config,clock=lambda:100)
        cert,key=test_service_tls.ServiceTLSTest('test_valid_san').leaf('host.example');context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.minimum_version=ssl.TLSVersion.TLSv1_3;context.load_cert_chain(cert,key)
        self.server=make_hosted_server(self.store,context);self.thread=threading.Thread(target=self.server.serve_forever);self.thread.start();self.addCleanup(self.stop)
        origin='https://host.example:'+str(self.server.server_port);self.store.service=origin;self.store.management_grant['service']=origin;self.store.vault.service=origin;self.store.reply_vault.service=origin
        self.hosted=HostedSender(self.root/'0.sqlite',key=self.keys[2],service=origin,owner=self.f.principals[0])
        self.client=HostedManagementClient(self.hosted,ca_file=str(test_service_tls.ServiceTLSTest.ca_file),address=('127.0.0.1',self.server.server_port))
        template=self.f.event(0,'f',dict(kind='hosted-holder-observation',text='',target=self.config['contribution'],service=origin,attribution='grant-holder'));self.template=serialize_json(template)
        limit=str(template_limit(self.template));self.store.configuration=dict(self.config,replyTextLimit=limit)
        self.create=encode_event(dict(version='1',purpose='hosted-grant-create',operation='6'*32,grant='7'*32,credential=self.secret,expiry=dict(kind='at',epoch='100'),replyTextLimit=limit,**self.config))
        self.hosted.retain(self.create);retain_template(self.hosted,'6'*32,self.template);self.client.request('6'*32,'manager')
        raw=encode_event(dict(version='0',purpose='hosted-holder-reply',operation='8'*32,text='A holder answered'))
        self.assertEqual(self.client._exchange('POST','/v0/grants/'+'7'*32+'/replies',raw,self.secret)[0],200)
        self.evidence=HostedReplyExporter(self.client).fetch('6'*32,'8'*32,'manager')['evidence']
        self.adapter=HostedObserverRelease(self.f.senders[0],self.hosted)
    def stop(self):self.server.shutdown();self.server.server_close();self.thread.join()
    def prepare(self,**kw):
        args=dict(key=self.f.devices[0]['key'],envelope_sender='observer@example.invalid',recipients=['author@example.invalid','reader@example.invalid'],time=self.f.time);args.update(kw)
        return self.adapter.prepare(self.evidence,**args)
    def test_real_holder_export_observer_mls_smtp_and_attributed_projection(self):
        revoke=encode_event(dict(version='0',purpose='hosted-grant-revoke',operation='9'*32,grant='7'*32));self.store.manage(revoke,'manager','hosted-grant-revoke')
        self.evidence=HostedReplyExporter(self.client).fetch('6'*32,'8'*32,'manager')['evidence'];result=self.prepare()
        smtp=LocalSMTP()
        with SenderWorker(self.f.senders[0]) as worker:
            with self.assertRaisesRegex(ValueError,'fixed observer'):worker.submit(result['delivery'],port=1,time=self.f.time)
            worker.submit_observer(result['delivery'],self.hosted,port=smtp.port,time=self.f.time)
        smtp.done();self.assertNotIn(b'A holder answered',smtp.wire)
        received,states=self.f.receive(2,smtp.wire);self.assertIn('accepted',states['states'].values())
        rows=self.f.senders[2].receiver.journal.snapshot('2'*32);observations=[decode_event(r['octets'][0])['value'] for r in rows if r['state']=='recorded' and decode_event(r['octets'][0])['value']['operation']['kind']=='hosted-holder-observation']
        self.assertEqual(len(observations),1);self.assertEqual(observations[0]['principal'],self.f.principals[0]);self.assertEqual(observations[0]['operation']['attribution'],'grant-holder')
        import subprocess
        script="import{projectReadable}from'./readable-projection.mjs';import{isPrincipalId}from'./principal-identifiers.mjs';import{readFileSync}from'node:fs';let x=JSON.parse(readFileSync(0,'utf8'));console.log(JSON.stringify(projectReadable(x.event,()=>({state:'valid',event:x.target}),isPrincipalId)));"
        view=json.loads(subprocess.run(['node','--input-type=module','-e',script],input=json.dumps(dict(event=observations[0],target=self.target)),text=True,capture_output=True,check=True,cwd=Path(__file__).parent).stdout)
        self.assertIn('grant holder',json.dumps(view));self.assertIn('Observed by',json.dumps(view))
    def test_restart_duplicate_keeps_mapping_and_checkpoint(self):
        first=self.prepare();revision=self.f.identities[0].db.execute('SELECT revision FROM mls_checkpoint').fetchone()[0]
        self.f.identities[0].close();self.f.identities[0]=IdentityStore(self.root/'0.sqlite');self.f.senders[0]=SenderRelease(self.f.identities[0],self.f.binary);self.adapter=HostedObserverRelease(self.f.senders[0],self.hosted)
        self.assertEqual(self.prepare(),first);self.assertEqual(self.f.identities[0].db.execute('SELECT revision FROM mls_checkpoint').fetchone()[0],revision)
    def test_wrong_author_or_context_and_conflict_never_release(self):
        with self.assertRaises(ValueError):self.prepare(key=self.f.devices[1]['key'])
        result=self.prepare();db=self.f.identities[0].db
        db.execute("UPDATE hosted_exports SET state='conflict'")
        with SenderWorker(self.f.senders[0]) as worker:
            with self.assertRaises(ValueError):worker.submit_observer(result['delivery'],self.hosted,port=1,time=self.f.time)
        db.execute("UPDATE hosted_exports SET state='observed'")
        self.f.senders[0].receiver.application_agreement.configure_device(self.f.group,self.f.devices[1]['identity'],self.f.devices[1]['key'],{'envelopeVersion':'1','operations':['message']})
        with self.assertRaises(ValueError):self.prepare()
    def test_policy_change_before_data_holds(self):
        result=self.prepare();smtp=LocalSMTP()
        import smtplib
        original=smtplib.SMTP.rcpt;changed=False
        def change(client,*args,**kw):
            nonlocal changed
            result=original(client,*args,**kw)
            if not changed:self.f.senders[0].configure(expected_revision=1);changed=True
            return result
        with patch('smtplib.SMTP.rcpt',new=change):
            with SenderWorker(self.f.senders[0]) as worker:outcome=worker.submit_observer(result['delivery'],self.hosted,port=smtp.port,time=self.f.time)
        smtp.done();self.assertIsNone(smtp.wire);self.assertEqual(outcome['state'],'aborted-before-data')
    def test_untrusted_or_wrong_audience_target_and_raw_receipt_are_held(self):
        with self.assertRaises(ValueError):self.adapter.prepare('forged',key=self.f.devices[0]['key'],envelope_sender='a@example.invalid',recipients=['b@example.invalid'],time=self.f.time)
        db=self.f.identities[0].db;db.execute("DELETE FROM mls_application_acceptance")
        with self.assertRaisesRegex(ValueError,'Authenticated target'):self.prepare()

    def test_crash_atomic_mapping_and_mls_preparation(self):
        import subprocess,sys
        script="""import os,sys,json
from identity_store import IdentityStore
from sender_release import SenderRelease
from vault_fixture import HostedSender
from hosted_observer_release import HostedObserverRelease
identity=IdentityStore(sys.argv[1]);sender=SenderRelease(identity,sys.argv[2]);hosted=HostedSender(sys.argv[1],key=bytes.fromhex(sys.argv[3]),service=sys.argv[4],owner=sys.argv[5])
HostedObserverRelease(sender,hosted).prepare(sys.argv[6],key=json.loads(sys.argv[7]),envelope_sender='observer@example.invalid',recipients=['author@example.invalid','reader@example.invalid'],time=json.loads(sys.argv[8]),crash=lambda stage:os._exit(75) if stage==sys.argv[9] else None)
"""
        before=self.f.identities[0].db.execute('SELECT revision,snapshot FROM mls_checkpoint').fetchone()
        for stage,count in [('after-encryption',0),('before-observer-commit',0),('after-observer-commit',1)]:
            result=__import__('subprocess').run([sys.executable,'-c',script,str(self.root/'0.sqlite'),str(self.f.binary),self.keys[2].hex(),self.store.service,self.f.principals[0],self.evidence,json.dumps(self.f.devices[0]['key']),json.dumps(self.f.time),stage],cwd=Path(__file__).parent)
            self.assertEqual(result.returncode,75)
            db=self.f.identities[0].db;self.assertEqual(db.execute('SELECT count(*) FROM hosted_observers').fetchone()[0],count)
            self.assertEqual(db.execute('SELECT count(*) FROM sender_prepared').fetchone()[0],count)
            if count==0:self.assertEqual(db.execute('SELECT revision,snapshot FROM mls_checkpoint').fetchone(),before)
        first=self.prepare();self.assertEqual(self.prepare(),first)
    def test_template_audience_cannot_select_a_different_group(self):
        template=json.loads(self.template);template['audience']=[self.f.principals[0]];raw_template=serialize_json(template)
        request=json.loads(self.create);request.update(operation='a'*32,grant='b'*32,replyTextLimit=str(template_limit(raw_template)))
        self.store.configuration=dict(self.config,replyTextLimit=request['replyTextLimit'])
        self.hosted.retain(encode_event(request));retain_template(self.hosted,'a'*32,raw_template);self.client.request('a'*32,'manager')
        raw=encode_event(dict(version='0',purpose='hosted-holder-reply',operation='8'*32,text='Reply'))
        self.assertEqual(self.client._exchange('POST','/v0/grants/'+'b'*32+'/replies',raw,self.secret)[0],200)
        evidence=HostedReplyExporter(self.client).fetch('a'*32,'8'*32,'manager')['evidence']
        with self.assertRaisesRegex(ValueError,'audience'):self.adapter.prepare(evidence,key=self.f.devices[0]['key'],envelope_sender='a@example.invalid',recipients=['b@example.invalid'],time=self.f.time)
        self.assertEqual(self.f.identities[0].db.execute('SELECT count(*) FROM hosted_observers').fetchone()[0],0)

if __name__=='__main__':unittest.main()
