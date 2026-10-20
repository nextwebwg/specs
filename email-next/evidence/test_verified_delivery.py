import hashlib,json,tempfile,unittest
from pathlib import Path
from email import policy
from unittest.mock import patch
import test_initial_roster as fixture
from test_discovery_mime import message
from identity_store import IdentityStore
from client_onboarding import ClientOnboarding
from human_verification import HumanVerification
from sender_release import SenderRelease
from initial_roster_lifecycle import InitialRosterRelease,InitialRosterAdmission
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from event_encoding import encode_event
from invitation_mime import select
from initial_roster import parse
from mls_mime import unpack
from mls_receive import MlsReceive

class VerifiedDelivery(unittest.TestCase):
    def setUp(self):
        self.f=fixture.InitialRosterTests();self.f.setUp();self.temp=tempfile.TemporaryDirectory();self.stores=[]
        self.time=dict(earliest=self.f.time,latest=self.f.time);self.creator=self.f.creator;self.target=next(d for d in self.f.devices if d['principal']!=self.creator['principal'])
        self.a=self.endpoint('a',self.creator);self.b=self.endpoint('b',self.target)
    def tearDown(self):
        for s in self.stores:s.close()
        self.temp.cleanup()
    def endpoint(self,name,device):
        identity=IdentityStore(Path(self.temp.name)/(name+'.sqlite'));self.stores.append(identity);client=ClientOnboarding(identity);verifier=HumanVerification(identity,account=name,local_principal=device['principal'],own_mailboxes=[json.loads(__import__('base64').b64decode(p['payload']))['mailbox'] for d,p in zip(self.f.devices,self.f.proofs) if d['principal']==device['principal']]);evidence={}
        for i,(peer,proof) in enumerate(zip(self.f.devices,self.f.proofs)):
            root=message(encode_event(proof));v=json.loads(__import__('base64').b64decode(proof['payload']));root['From']=v['mailbox'];wire=root.as_bytes(policy=policy.SMTP)
            mode='automatic-unverified-continuity' if peer['principal']==device['principal'] else 'verification-required'
            result=client.ingest('mail'+str(i),[wire],mode=mode,target_policy='all-authorized-devices',policy_revision='1',time=self.time)
            if mode=='verification-required':
                session=verifier.begin(hashlib.sha256(wire).hexdigest(),time=self.time,session_expires=str(int(self.f.time)+100))
                result=verifier.confirm('compare'+str(i),session['session'],session['comparison'],channel='in-person',time=self.time,not_before=self.f.time,not_after=str(int(self.f.time)+600),continuity='ordinary-authorized-descendants');evidence[v['mailbox']]=result['evidence']
        selected=[]
        for proof in self.f.proofs:
            v=json.loads(__import__('base64').b64decode(proof['payload']));plan=client.targets(v['mailbox'],target_policy='evidenced-devices',time=self.time,mode='verification-required')
            self.assertEqual(plan['status'],'ready-verified');selected.append(plan['selected'][0])
        sender=SenderRelease(identity,self.f.binary);sender.configure(expected_revision=0,trust_policy='require-verification',verification_mechanism='human-comparison-v0')
        sender.receiver=MlsReceive(identity,self.f.binary.with_name('receive-staged'),verification_mechanism='human-comparison-v0')
        return dict(identity=identity,client=client,verifier=verifier,evidence=evidence,selected=selected,sender=sender)
    def prepare(self):
        selected=self.a['selected'];release=InitialRosterRelease(self.a['sender'])
        wires=release.prepare('3'*32,device=self.creator,selected=selected,intended_principals=sorted({d['principal'] for d in self.f.devices}),intended_devices=[{k:d[k] for k in ('principal','device')} for d in self.f.devices],context=self.f.context,not_before=self.f.time,not_after=str(int(self.f.time)+30),time=self.time)
        return next((key,wire) for key,wire in wires.items() if parse(select(wire))['value']['target']['device']==self.target['device'] and parse(select(wire))['value']['target']['principal']==self.target['principal'])
    def test_strict_roster_smtp_admission_and_protected_reply(self):
        delivery,wire=self.prepare();smtp=LocalSMTP()
        with SenderWorker(self.a['sender']) as worker:self.assertEqual(worker.submit_initial_roster(delivery,port=smtp.port,time=self.time)['state'],'accepted')
        smtp.done();self.assertEqual(smtp.wire,wire);admission=InitialRosterAdmission(self.b['identity'],self.f.binary,verification_mechanism='human-comparison-v0');admission.publish_local(self.target)
        choices=[dict(principal=d['principal'],device=d['device'],mailbox=s['mailbox'],generation=s['generation']) for d,s in zip(self.f.devices,self.b['selected'])]
        target_route=self.b['selected'][self.f.devices.index(self.target)]
        admission.accept_message(select(wire),target=self.target,mailbox=target_route['mailbox'],allow_creator=self.creator['principal'],intended_principals=sorted({d['principal'] for d in self.f.devices}),intended_devices=[{k:d[k] for k in ('principal','device')} for d in self.f.devices],expected_context=encode_event(self.f.context),selections=choices,time=self.time,trust_policy='require-verification')
        for local,peer,device,destination in [(self.a,self.b,self.creator,self.target),(self.b,self.a,self.target,self.creator)]:
            route=local['selected'][self.f.devices.index(destination)];source=local['selected'][self.f.devices.index(device)]['mailbox']
            event=dict(version='1',purpose='contribution',event=('a' if local is self.a else 'b')*32,conversation='2'*32,principal=device['principal'],audience=sorted({d['principal'] for d in self.f.devices}),disclosures=[],operation=dict(kind='message',text='Verified protected reply',replyTo=[]))
            local['sender'].prepare('reply',encode_event(event),key=device['key'],envelope_sender=source,recipients=[route['mailbox']],association_targets=[dict(mailbox=route['mailbox'],generation=route['generation'],principal=destination['principal'],observation=route['digest'])],time=self.time)
            smtp=LocalSMTP()
            with SenderWorker(local['sender']) as worker:self.assertEqual(worker.submit('reply',port=smtp.port,time=self.time)['state'],'accepted')
            smtp.done();self.assertEqual(peer['sender'].receiver.receive(unpack(smtp.wire),time=self.time,trust_policy='require-verification')['applicationState'],'accepted')
    def test_expired_evidence_holds_before_socket(self):
        delivery,wire=self.prepare();later={k:str(int(v)+601) for k,v in self.time.items()}
        with SenderWorker(self.a['sender']) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No socket after evidence expiry')):
            with self.assertRaises(ValueError):worker.submit_initial_roster(delivery,port=1,time=later)

    def test_withdrawal_blocks_before_socket_and_after_release_before_data(self):
        delivery,wire=self.prepare();mailbox=parse(select(wire))['value']['target']['mailbox'];evidence=self.a['evidence'][mailbox]
        with SenderWorker(self.a['sender']) as worker:
            smtp=LocalSMTP();result=worker.submit_initial_roster(delivery,port=smtp.port,time=self.time,crash=lambda point:self.a['verifier'].withdraw(evidence,expected_revision=1) if point=='after-release' else None);smtp.done()
            self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(smtp.wire)
            with patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No socket after withdrawal')):
                with self.assertRaises(ValueError):worker.submit_initial_roster(delivery,port=1,time=self.time)

if __name__=='__main__':unittest.main()
