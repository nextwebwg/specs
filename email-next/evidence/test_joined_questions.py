"""Actual configured v2 question/answer preparation and protected MIME receive."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from identity_store import IdentityStore
from provider_mls import make_device,call
from sender_release import SenderRelease
from mls_receive import MlsReceive
from mls_mime import unpack


class JoinedQuestions(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.binary=Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR'])/'provider-mls'
        self.devices=[make_device(self.binary,1,2),make_device(self.binary,3,4),make_device(self.binary,5,6)]
        self.time=dict.fromkeys(['earliest','latest'],str(max(d['time'] for d in self.devices)))
        a,b,c=self.devices
        self.principals=['enp0:'+bytes.fromhex(d['identity'])[21:53].hex() for d in self.devices]
        self.application={'envelopeVersion':'1','operations':getattr(self,'selected_operations',['answer','message','question'])}
        if getattr(self,'selected_payload',None) is not None:self.application['payload']=self.selected_payload
        self.context={'version':getattr(self,'context_version','2'),'purpose':'conversation-context','conversation':'2'*32,'profile':'mls-1-0001','administrators':[self.principals[0]],'application':self.application,'ordering':{'kind':'fixed-roster-v0'}}
        group_worker=self.binary.with_name('group-transitions')
        initial=call(group_worker,op='create',checkpoint=a['checkpoint'],key=a['key'],identity=a['identity'],context=json.dumps(self.context).encode().hex())
        candidate=call(group_worker,op='candidate',checkpoint=initial['checkpoint'],key=a['key'],group=initial['snapshot']['group'],packages=[b['package'],c['package']])
        group=dict(checkpoint=candidate['checkpoint'],group=candidate['after']['group'])
        joined=call(group_worker,op='join',checkpoint=b['checkpoint'],key=b['key'],welcome=candidate['welcome'])
        observer=call(group_worker,op='join',checkpoint=c['checkpoint'],key=c['key'],welcome=candidate['welcome'])
        self.group=group['group'];self.identities=[];self.senders=[]
        for i,state in enumerate([group,joined,observer]):
            identity=IdentityStore(Path(self.temp.name)/f'{i}.sqlite');self.identities.append(identity)
            for d in self.devices:identity.observe(d['record'],first_contact_policy='allow-unverified')
            receiver=MlsReceive(identity,self.binary.with_name('receive-staged'));receiver.install_fixture(self.group,state['checkpoint'])
            sender=SenderRelease(identity,self.binary);sender.configure(expected_revision=0);self.senders.append(sender)
            metadata=call(self.binary,op='inspect-send',checkpoint=state['checkpoint'],group=self.group,key=self.devices[i]['key'])['metadata']
            for m in metadata['members']:receiver.application_agreement.configure_device(self.group,m['identity'],m['key'],self.application)
    def tearDown(self):
        for i in self.identities:i.close()
        self.temp.cleanup()
    def event(self,who,event,operation):
        return dict(version='1',purpose='contribution',event=event*32,conversation='2'*32,principal=self.principals[who],audience=sorted(self.principals),operation=operation,disclosures=[])
    def prepare(self,who,event):
        return self.senders[who].prepare(event['event'],json.dumps(event).encode(),key=self.devices[who]['key'],envelope_sender=f'person{who}@example.invalid',recipients=[f'person{1-who}@example.invalid'],time=self.time)
    def receive(self,who,wire):
        receiver=self.senders[who].receiver
        result=receiver.receive(unpack(wire),time=self.time,trust_policy='allow-unverified')
        evaluated=receiver.reevaluate(time=self.time,trust_policy='allow-unverified')
        return result,evaluated
    def question(self):return self.event(0,'a',dict(kind='question',text='Which time works?',options=[dict(id='c'*32,label='Morning'),dict(id='d'*32,label='Afternoon')]))
    def test_real_question_answer_and_plain_reply_with_restart_and_duplicate(self):
        question=self.question();wire=self.prepare(0,question)
        self.assertNotIn(b'Which time works?',wire)
        self.receive(1,wire)
        answer=self.event(1,'b',dict(kind='answer',question={k:question[k] for k in ('principal','conversation','event')},option='c'*32,replaces=[]))
        response=self.prepare(1,answer)
        self.identities[0].close();self.identities[0]=IdentityStore(Path(self.temp.name)/'0.sqlite');self.senders[0]=SenderRelease(self.identities[0],self.binary)
        result,evaluated=self.receive(0,response)
        self.assertIn('accepted',evaluated['states'].values())
        self.assertEqual(self.receive(0,response)[0],result)
        self.assertEqual(self.identities[0].db.execute('SELECT count(*) FROM contributions').fetchone()[0],2)
        reply=self.event(0,'e',dict(kind='message',text='Morning it is. Thank you!',replyTo=[]))
        self.assertIn('accepted',self.receive(1,self.prepare(0,reply))[1]['states'].values())
    def test_one_click_action_is_stable_after_restart_and_does_not_reencrypt(self):
        from client_flow import ClientFlow
        from journal_button_view import derive_button_view
        question=self.question();self.receive(1,self.prepare(0,question))
        ref={k:question[k] for k in ('principal','conversation','event')}
        token=derive_button_view(self.senders[1].receiver.journal,ref)['sourceToken']
        def client():return ClientFlow(self.senders[1],key=self.devices[1]['key'],envelope_sender='bob@example.invalid',recipients=['alice@example.invalid'])
        wire=client().answer('click1',ref,'c'*32,token,time=self.time)
        revision=self.identities[1].db.execute('SELECT revision FROM mls_checkpoint').fetchone()[0]
        self.identities[1].close();self.identities[1]=IdentityStore(Path(self.temp.name)/'1.sqlite');self.senders[1]=SenderRelease(self.identities[1],self.binary)
        self.assertEqual(client().answer('click1',ref,'c'*32,token,time=self.time),wire)
        self.assertEqual(self.identities[1].db.execute('SELECT revision FROM mls_checkpoint').fetchone()[0],revision)
        with self.assertRaisesRegex(ValueError,'conflict'):client().answer('click1',ref,'d'*32,token,time=self.time)
        with self.assertRaisesRegex(ValueError,'snapshot'):client().answer('click2',ref,'d'*32,token,time=self.time)
        self.assertIn('accepted',self.receive(0,wire)[1]['states'].values())

    def test_actual_loopback_submission_in_both_directions(self):
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        question=self.question();self.prepare(0,question)
        smtp=LocalSMTP()
        with SenderWorker(self.senders[0]) as worker:worker.submit(question['event'],port=smtp.port,time=self.time)
        smtp.done();self.receive(1,smtp.wire)
        answer=self.event(1,'b',dict(kind='answer',question={k:question[k] for k in ('principal','conversation','event')},option='c'*32,replaces=[]))
        self.prepare(1,answer);smtp=LocalSMTP()
        with SenderWorker(self.senders[1]) as worker:worker.submit(answer['event'],port=smtp.port,time=self.time)
        smtp.done();self.assertIn('accepted',self.receive(0,smtp.wire)[1]['states'].values())

    def test_explicit_plaintext_plan_and_separate_actual_submission(self):
        from plaintext_release import PlaintextRelease
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        from email.parser import BytesParser
        question=self.question();question['disclosures']=[{'kind':'plaintext-email'}]
        raw=json.dumps(question).encode();fallback=PlaintextRelease(self.senders[0])
        fallback.authorize(raw,['legacy@example.invalid'])
        protected=self.prepare(0,question)
        self.assertNotIn(b'Which time works?',protected)
        plain=fallback.prepare('legacycopy',question['event'])
        self.assertEqual(fallback.prepare('legacycopy',question['event']),plain)
        self.assertNotIn(b'legacy@example.invalid',plain)
        parsed=BytesParser().parsebytes(plain)
        self.assertEqual(parsed.get_content_type(),'multipart/alternative')
        self.assertIn(b'Which time works?',plain)
        smtp=LocalSMTP()
        with SenderWorker(self.senders[0]) as worker:worker.submit_plaintext('legacycopy',port=smtp.port,time=self.time)
        smtp.done();self.assertEqual(smtp.wire,plain)
        self.assertIn('accepted',self.receive(1,protected)[1]['states'].values())

    def test_real_signed_send_revocation_holds_click_and_prepared_submission(self):
        import base64,hashlib
        from unittest.mock import patch
        from provider_mls import sign
        from event_encoding import encode_event
        from client_flow import ClientFlow
        from journal_button_view import derive_button_view
        from sender_worker import SenderWorker
        question=self.question();self.receive(1,self.prepare(0,question));ref={k:question[k] for k in ('principal','conversation','event')}
        client=ClientFlow(self.senders[1],key=self.devices[1]['key'],envelope_sender='bob@example.invalid',recipients=['alice@example.invalid'])
        token=derive_button_view(self.senders[1].receiver.journal,ref)['sourceToken']
        client.answer('readyanswer',ref,'c'*32,token,time=self.time)
        d=self.devices[1];r=d['record'];binding=json.loads(base64.b64decode(r['binding']))
        binding.update(record='f'*32,roles=['receive','enroll','revoke'],authority={'kind':'state','digest':d['state']})
        raw=encode_event(binding);state=json.loads(base64.b64decode(r['state']))
        state.update(record='9'*32,revision='1',previous=[d['state']],bindings=[dict(device=d['device'],digest=hashlib.sha256(raw).hexdigest())])
        payload=encode_event(state)
        bundle=dict(version='0',purpose='identity-bundle',principal=d['principal'],
          states=[dict(payload=base64.b64encode(payload).decode(),signature=sign(self.binary,d,'email-next/identity-state/v0',payload)),dict(payload=r['state'],signature=r['stateProof'])],
          bindings=[dict(payload=base64.b64encode(raw).decode(),authorization=sign(self.binary,d,'email-next/device-binding/v0',raw),possession=sign(self.binary,d,'email-next/device-possession/v0',raw)),dict(payload=r['binding'],authorization=r['authorization'],possession=r['possession'])])
        self.assertEqual(self.identities[1].accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(payload).hexdigest(),time=self.time)['status'],'accepted-unverified')
        self.assertEqual(self.identities[1].check_device(bytes.fromhex(d['identity']),bytes.fromhex(d['key']),role='receive',time=self.time,trust_policy='allow-unverified')['status'],'authorized-unverified')
        with patch('socket.socket',side_effect=AssertionError('No socket for revoked sender')):
            with SenderWorker(self.senders[1]) as worker:
                with self.assertRaisesRegex(ValueError,'authority'):worker.submit('readyanswer',port=1,time=self.time)
        token=derive_button_view(self.senders[1].receiver.journal,ref)['sourceToken']
        with self.assertRaisesRegex(ValueError,'authority'):client.answer('afterrevoke',ref,'d'*32,token,time=self.time)

    def test_actual_observer_delayed_question_resolves_after_restart(self):
        question=self.question();wire=self.prepare(0,question);self.receive(1,wire)
        answer=self.event(1,'b',dict(kind='answer',question={k:question[k] for k in ('principal','conversation','event')},option='c'*32,replaces=[]))
        response=self.prepare(1,answer)
        result,evaluated=self.receive(2,response)
        self.assertIn('pending',evaluated['states'].values())
        self.identities[2].close();self.identities[2]=IdentityStore(Path(self.temp.name)/'2.sqlite');self.senders[2]=SenderRelease(self.identities[2],self.binary)
        self.receive(2,wire)
        evaluated=self.senders[2].receiver.reevaluate(time=self.time,trust_policy='allow-unverified')
        self.assertEqual(set(evaluated['states'].values()),{'accepted'})
        self.assertEqual(self.identities[2].db.execute('SELECT count(*) FROM contributions').fetchone()[0],2)

    def test_plaintext_policy_change_holds_without_socket(self):
        from unittest.mock import patch
        from plaintext_release import PlaintextRelease
        from sender_worker import SenderWorker
        question=self.question();question['disclosures']=[{'kind':'plaintext-email'}]
        fallback=PlaintextRelease(self.senders[0]);fallback.authorize(json.dumps(question).encode(),['legacy@example.invalid'])
        self.prepare(0,question);fallback.prepare('legacycopy',question['event'])
        self.senders[0].configure(expected_revision=1)
        with patch('socket.socket',side_effect=AssertionError('No socket after policy change')):
            with SenderWorker(self.senders[0]) as worker:
                with self.assertRaisesRegex(ValueError,'Changed policy'):worker.submit_plaintext('legacycopy',port=1,time=self.time)

    def test_retained_action_recovers_before_preparation_without_new_event(self):
        from unittest.mock import patch
        from client_flow import ClientFlow
        from journal_button_view import derive_button_view
        question=self.question();self.receive(1,self.prepare(0,question));ref={k:question[k] for k in ('principal','conversation','event')}
        token=derive_button_view(self.senders[1].receiver.journal,ref)['sourceToken']
        client=ClientFlow(self.senders[1],key=self.devices[1]['key'],envelope_sender='bob@example.invalid',recipients=['alice@example.invalid'])
        with patch.object(self.senders[1],'prepare',side_effect=RuntimeError('interrupted before prepare')):
            with self.assertRaises(RuntimeError):client.answer('interrupted',ref,'c'*32,token,time=self.time)
        original=self.identities[1].db.execute('SELECT event FROM client_actions WHERE id=?',('interrupted',)).fetchone()[0]
        wire=client.answer('interrupted',ref,'c'*32,token,time=self.time)
        self.assertEqual(self.identities[1].db.execute('SELECT application FROM sender_prepared WHERE id=?',('interrupted',)).fetchone()[0],original)
        self.assertIn('accepted',self.receive(0,wire)[1]['states'].values())

    def test_missing_device_agreement_holds_before_preparation(self):
        self.identities[0].db.execute('DELETE FROM mls_application_agreement WHERE credential=?',(self.devices[1]['identity'],))
        with self.assertRaisesRegex(ValueError,'Application contract'):self.prepare(0,self.question())
        self.assertEqual(self.identities[0].db.execute('SELECT revision FROM mls_checkpoint').fetchone()[0],0)
    def test_disclosure_requires_durable_plan_not_just_schema(self):
        event=self.question();event['disclosures']=[{'kind':'plaintext-email'}]
        with self.assertRaisesRegex(ValueError,'disclosure plan'):self.prepare(0,event)
