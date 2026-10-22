import json
import smtplib
import unittest
from unittest.mock import patch
from event_encoding import encode_event,serialize_json,decode_event
from hosted_disclosure import HostedDisclosure
from hosted_disclosure_delivery import HostedDisclosureManagement,HostedDisclosureNotification
from hosted_reply_admission import retain_template,template_limit
from hosted_reply_export import HostedReplyExporter
from hosted_notification_release import HostedNotificationRelease
from plaintext_release import PlaintextRelease
from copy_plan_status import CopySnapshot, RecipientEvidence, summarize
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
import test_hosted_observer

class DisclosureTests(unittest.TestCase):
    setUpClass=classmethod(test_hosted_observer.ObserverTests.setUpClass.__func__)
    tearDownClass=classmethod(test_hosted_observer.ObserverTests.tearDownClass.__func__)
    setUp=test_hosted_observer.ObserverTests.setUp
    stop=test_hosted_observer.ObserverTests.stop
    def plan(self,*,mixed=False,prepare=True,two=False,question=False):
        self.original=self.f.event(0,'d',dict(kind='message',text='Original explicitly hosted message',replyTo=[]))
        if question:self.original['operation']=dict(kind='question',text='Which time? 日本語',options=[dict(id='1'*32,label='<img src=x onerror=alert(1)> 朝'),dict(id='2'*32,label='Evening & late')])
        self.original['disclosures']=([{'kind':'plaintext-email'}] if mixed else [])+[{'kind':'provider-hosted','service':self.store.service,'model':'bearer'}]
        self.application=encode_event(self.original);ref={k:self.original[k] for k in ('principal','conversation','event')}
        template=self.f.event(0,'f',dict(kind='hosted-holder-observation',text='',target=ref,service=self.store.service,attribution='grant-holder'));template=serialize_json(template)
        from hosted_projection import hosted_source_text
        self.configuration=dict(contribution=ref,content=dict(kind='text',text=hosted_source_text(self.application)),recipient='4'*32,replyDestination='5'*32,replyTextLimit=str(template_limit(template)))
        self.store.configuration=self.configuration
        self.request=dict(version='1',purpose='hosted-grant-create',operation='a'*32,grant='b'*32,credential=self.secret,expiry={'kind':'none'},**self.configuration)
        self.hosted.retain(encode_event(self.request));retain_template(self.hosted,'a'*32,template)
        self.route={'fromAddress':'author@example.invalid','recipientAddress':'legacy@example.invalid'};routes={'a'*32:self.route}
        if two:
            from hosted_access import credential
            req=dict(self.request,operation='c'*32,grant='d'*32,credential=credential())
            self.hosted.retain(encode_event(req));retain_template(self.hosted,'c'*32,template);routes['c'*32]=dict(self.route,recipientAddress='other-legacy@example.invalid')
        self.plans=HostedDisclosure(self.f.senders[0],self.hosted);self.digest=self.plans.authorize(self.application,routes)
        self.bound=HostedDisclosureManagement(self.f.senders[0],self.client)
        if mixed:PlaintextRelease(self.f.senders[0]).authorize(self.application,['plain@example.invalid'])
        if prepare:self.prepare_original()
    def prepare_original(self):return self.f.senders[0].prepare('hostedoriginal',self.application,key=self.f.devices[0]['key'],envelope_sender='author@example.invalid',recipients=['reader@example.invalid'],time=self.f.time)
    def notify(self,evidence):
        notification=HostedDisclosureNotification(self.f.senders[0],self.hosted)
        notification.configure(expected_revision=0,configuration=dict(service=self.store.service,owner=self.f.principals[0],recipient='4'*32,replyDestination='5'*32,enabled=True,**self.route))
        now=int(self.f.time['latest']);notification.prepare('a'*32,evidence=evidence,credible_time=(now,now));return notification,now
    def test_joined_original_disclosure_notification_holder_and_observer(self):
        self.plan();result=self.bound.create('a'*32,'manager',time=self.f.time)
        with self.assertRaises(ValueError):self.client.request('a'*32,'manager')
        notification,now=self.notify(result['evidence'])
        with self.assertRaises(ValueError):HostedNotificationRelease(self.hosted).prepare('a'*32,evidence=result['evidence'],credible_time=(now,now))
        smtp=LocalSMTP();notification.submit('a'*32,port=smtp.port,credible_time=lambda:(now,now));smtp.done()
        self.assertNotIn(b'Original explicitly hosted message',smtp.wire)
        smtp=LocalSMTP()
        with SenderWorker(self.f.senders[0]) as worker:worker.submit('hostedoriginal',port=smtp.port,time=self.f.time)
        smtp.done();self.assertNotIn(self.secret.encode(),smtp.wire);self.assertNotIn(b'legacy@example.invalid',smtp.wire)
        self.f.receive(2,smtp.wire)
        records=self.f.senders[2].receiver.journal.snapshot('2'*32)
        event=next(decode_event(r['octets'][0])['value'] for r in records if r['reference']['event']=='d'*32)
        self.assertEqual(event['disclosures'],self.original['disclosures']);self.assertEqual(event['audience'],sorted(self.f.principals))
        raw=encode_event(dict(version='0',purpose='hosted-holder-reply',operation='c'*32,text='Joined holder answer'))
        self.assertEqual(self.client._exchange('POST','/v0/grants/'+'b'*32+'/replies',raw,self.secret)[0],200)
        evidence=HostedReplyExporter(self.client).fetch('a'*32,'c'*32,'manager')['evidence']
        observation=self.adapter.prepare(evidence,key=self.f.devices[0]['key'],envelope_sender='author@example.invalid',recipients=['reader@example.invalid'],time=self.f.time)
        smtp=LocalSMTP()
        with SenderWorker(self.f.senders[0]) as worker:worker.submit_observer(observation['delivery'],self.hosted,port=smtp.port,time=self.f.time)
        smtp.done();self.assertIn('accepted',self.f.receive(2,smtp.wire)[1]['states'].values())
    def test_planning_or_preparation_does_not_authorize_after_policy_change(self):
        self.plan(prepare=False)
        with self.assertRaisesRegex(ValueError,'Prepared local author'):self.bound.create('a'*32,'manager',time=self.f.time)
        self.prepare_original();self.f.senders[0].configure(expected_revision=1)
        with self.assertRaises(ValueError):self.bound.create('a'*32,'manager',time=self.f.time)
        with SenderWorker(self.f.senders[0]) as worker:
            with self.assertRaises(ValueError):worker.submit('hostedoriginal',port=1,time=self.f.time)
        self.assertEqual(self.store.lookup('a'*32,'manager')[0],404)
    def test_lost_creation_response_exact_reconciliation_after_withdrawal(self):
        self.plan();original=self.client._exchange
        def lose(*args,**kwargs):original(*args,**kwargs);raise ConnectionError('lost fixture response')
        with patch.object(self.client,'_exchange',side_effect=lose):
            with self.assertRaises(ConnectionError):self.bound.create('a'*32,'manager',time=self.f.time)
        self.assertEqual(self.store.lookup('a'*32,'manager')[0],200)
        local=self.f.identities[0].db.execute('SELECT state FROM hosted_creation_state WHERE operation=?',('a'*32,)).fetchone()[0]
        self.assertEqual(local,'uncertain')
        snapshot=CopySnapshot('hosted','held',(RecipientEvidence(self.route['recipientAddress']),),content_release_uncertain=local in ('released','uncertain'))
        projected=summarize(('hosted',),[snapshot],progression='independent')
        self.assertTrue(projected['content_may_be_exposed']);self.assertFalse(projected['content_exposure_observed'])
        self.assertFalse(projected['all_handoffs_confirmed']);self.assertEqual(projected['candidate_units'],())
        with self.assertRaisesRegex(ValueError,'uncertain'):self.bound.create('a'*32,'manager',time=self.f.time)
        self.plans.withdraw(self.digest)
        result=self.bound.reconcile('a'*32,'manager');self.assertEqual(result['state'],'observed')
        self.assertEqual(self.f.identities[0].db.execute("SELECT state FROM hosted_creation_state WHERE operation=?",('a'*32,)).fetchone()[0],'confirmed')
        known=CopySnapshot('hosted','held',snapshot.recipients,content_exposed=True)
        observed=summarize(('hosted',),[known],progression='independent')
        self.assertTrue(observed['content_exposure_observed']);self.assertTrue(observed['content_may_be_exposed'])
        self.assertFalse(observed['all_handoffs_confirmed'])
        with self.assertRaises(ValueError):self.notify(result['evidence'])
    def test_notification_and_protected_original_recheck_plan_after_rcpt(self):
        self.plan();result=self.bound.create('a'*32,'manager',time=self.f.time);notification,now=self.notify(result['evidence']);smtp=LocalSMTP()
        original=smtplib.SMTP.rcpt
        def withdraw(client,*args,**kwargs):
            outcome=original(client,*args,**kwargs);self.plans.withdraw(self.digest);return outcome
        with patch('smtplib.SMTP.rcpt',new=withdraw):outcome=notification.submit('a'*32,port=smtp.port,credible_time=lambda:(now,now))
        smtp.done();self.assertEqual(outcome['state'],'aborted-before-data');self.assertIsNone(smtp.wire)
        with SenderWorker(self.f.senders[0]) as worker:
            with self.assertRaises(ValueError):worker.submit('hostedoriginal',port=1,time=self.f.time)
    def test_multiple_grants_one_descriptor_and_mixed_plans(self):
        self.plan(mixed=True,two=True,prepare=False)
        db=self.f.identities[0].db;db.execute('DELETE FROM plaintext_plans')
        with self.assertRaisesRegex(ValueError,'Plaintext'):self.prepare_original()
        PlaintextRelease(self.f.senders[0]).authorize(self.application,['plain@example.invalid']);self.prepare_original()
        self.assertEqual(len([d for d in self.original['disclosures'] if d['kind']=='provider-hosted']),1)
        for op in ['a'*32,'c'*32]:self.assertEqual(self.bound.create(op,'manager',time=self.f.time)['http'],200)
        self.assertEqual(db.execute('SELECT count(*) FROM hosted_disclosure_grants').fetchone()[0],2)
        with self.assertRaises(ValueError):self.plans.authorize(self.application,{'a'*32:self.route})

    def test_subprocess_death_after_create_release_retains_uncertainty(self):
        import subprocess,sys
        from pathlib import Path
        self.plan()
        script="""import os,sys,json
from identity_store import IdentityStore
from sender_release import SenderRelease
from vault_fixture import HostedSender
from hosted_management import HostedManagementClient
from hosted_disclosure_delivery import HostedDisclosureManagement
identity=IdentityStore(sys.argv[1]);sender=SenderRelease(identity,sys.argv[2]);hosted=HostedSender(sys.argv[1],key=bytes.fromhex(sys.argv[3]),service=sys.argv[4],owner=sys.argv[5])
client=HostedManagementClient(hosted,ca_file=sys.argv[6],address=('127.0.0.1',int(sys.argv[7])))
HostedDisclosureManagement(sender,client).create('a'*32,'manager',time=json.loads(sys.argv[8]),crash=lambda stage:os._exit(79) if stage=='after-release' else None)
"""
        result=subprocess.run([sys.executable,'-c',script,self.hosted.path,str(self.f.binary),self.keys[2].hex(),self.store.service,self.f.principals[0],self.client.ca,str(self.server.server_port),json.dumps(self.f.time)],cwd=Path(__file__).parent)
        self.assertEqual(result.returncode,79);self.assertEqual(self.store.lookup('a'*32,'manager')[0],404)
        with self.assertRaisesRegex(ValueError,'uncertain'):self.bound.create('a'*32,'manager',time=self.f.time)
        self.assertEqual(self.bound.create('a'*32,'manager',time=self.f.time,retry_uncertain=True)['state'],'observed')
        states=[r[0] for r in self.f.identities[0].db.execute('SELECT state FROM hosted_creation_attempts ORDER BY rowid')]
        self.assertEqual(states,['uncertain','confirmed'])
    def test_original_plan_withdrawal_after_rcpt_and_descriptor_completeness(self):
        self.plan();smtp=LocalSMTP();original=smtplib.SMTP.rcpt
        def withdraw(client,*args,**kwargs):
            result=original(client,*args,**kwargs);self.plans.withdraw(self.digest);return result
        with patch('smtplib.SMTP.rcpt',new=withdraw):
            with SenderWorker(self.f.senders[0]) as worker:result=worker.submit('hostedoriginal',port=smtp.port,time=self.f.time)
        smtp.done();self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(smtp.wire)
        other=dict(self.original,event='f'*32,disclosures=[{'kind':'provider-hosted','service':'https://other.example','model':'bearer'}])
        with self.assertRaises(ValueError):self.f.senders[0].prepare('unplanned',encode_event(other),key=self.f.devices[0]['key'],envelope_sender='a@example.invalid',recipients=['b@example.invalid'],time=self.f.time)

if __name__=='__main__':unittest.main()
