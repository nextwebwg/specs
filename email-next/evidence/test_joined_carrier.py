"""Configured context3 actual MLS body carrier. No signed invitation claim."""
import json
import hashlib
import unittest
from pathlib import Path
import test_joined_questions as questions
from event_encoding import decode_event
from mls_mime import unpack,package
from provider_mls import call
from identity_store import IdentityStore
from sender_release import SenderRelease
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from protected_carrier import inspect_carrier,package_carrier
from application_payload import DEFAULT_LIMITS

class JoinedCarrier(unittest.TestCase):
    context_version='3'
    selected_payload='mime-contribution-v0'
    selected_operations=['answer','message','question','reaction','reaction-withdraw']
    setUp=questions.JoinedQuestions.setUp
    tearDown=questions.JoinedQuestions.tearDown
    event=questions.JoinedQuestions.event
    prepare=questions.JoinedQuestions.prepare
    receive=questions.JoinedQuestions.receive
    question=questions.JoinedQuestions.question
    def ref(self,e):return {k:e[k] for k in ('principal','conversation','event')}
    def inject(self,who,payload):
        db=self.identities[who].db
        checkpoint=json.loads(db.execute('SELECT snapshot FROM mls_checkpoint').fetchone()[0])
        sent=call(self.binary,op='send',checkpoint=checkpoint,key=self.devices[who]['key'],group=self.group,application=payload.hex())
        db.execute('UPDATE mls_checkpoint SET revision=revision+1,snapshot=?',(json.dumps(sent['checkpoint']).encode(),))
        return package(bytes.fromhex(sent['wire']))
    def test_actual_smtp_question_answer_reaction_and_exact_retained_event(self):
        q=self.question();wire=self.prepare(0,q)
        payload=self.identities[0].db.execute('SELECT event,payload FROM sender_payloads WHERE delivery=?',(q['event'],)).fetchone()
        self.assertEqual(payload[0],json.dumps(q).encode());self.assertNotEqual(payload[0],payload[1]);self.assertNotIn(b'Which time works?',wire)
        self.assertEqual(inspect_carrier(payload[1],**DEFAULT_LIMITS)['event']['octets'],payload[0])
        smtp=LocalSMTP()
        with SenderWorker(self.senders[0]) as worker:worker.submit(q['event'],port=smtp.port,time=self.time)
        smtp.done();self.assertIn('accepted',self.receive(1,smtp.wire)[1]['states'].values())
        answer=self.event(1,'b',dict(kind='answer',question=self.ref(q),option='c'*32,replaces=[]))
        self.assertIn('accepted',self.receive(0,self.prepare(1,answer))[1]['states'].values())
        reaction=self.event(1,'c',dict(kind='reaction',target=self.ref(q),emoji='👍'))
        self.assertIn('accepted',self.receive(0,self.prepare(1,reaction))[1]['states'].values())
        withdrawal=self.event(1,'d',dict(kind='reaction-withdraw',target=self.ref(q),reactions=[self.ref(reaction)]))
        self.assertIn('accepted',self.receive(0,self.prepare(1,withdrawal))[1]['states'].values())
        self.assertEqual(self.identities[1].db.execute('SELECT application FROM mls_receives WHERE digest=?',(hashlib.sha256(unpack(wire)).hexdigest(),)).fetchone()[0],payload[0])
    def test_malformed_carrier_commits_receive_state_without_raw_fallback(self):
        q=self.question();raw=json.dumps(q).encode()
        invalid=self.inject(0,raw)
        self.assertEqual(self.receive(1,invalid)[0]['status'],'invalid-application-encoding')
        self.assertEqual(self.identities[1].db.execute('SELECT count(*) FROM contributions').fetchone()[0],0)
        self.assertEqual(self.identities[1].db.execute('SELECT payload FROM mls_received_payloads').fetchone()[0],raw)
        self.assertIn('accepted',self.receive(1,self.prepare(0,q))[1]['states'].values())
    def test_distinct_mime_same_event_restart_and_pairing_diagnostic(self):
        q=self.question();self.receive(1,self.prepare(0,q))
        reaction=self.event(0,'c',dict(kind='reaction',target=self.ref(q),emoji='👍'));raw=json.dumps(reaction).encode()
        for n in range(2):
            payload=package_carrier(raw,'Reaction','<p>Reaction</p>',target_message_id='<known@target.example>',**DEFAULT_LIMITS)
            result=self.receive(1,self.inject(0,payload))
            self.assertIn('accepted',result[1]['states'].values());self.assertEqual(result[0]['projection'],'mismatch')
        self.assertEqual(self.identities[1].db.execute('SELECT count(*) FROM contributions').fetchone()[0],2)
        before=self.prepare(0,self.event(0,'d',dict(kind='message',text='Next',replyTo=[])))
        self.identities[1].close();self.identities[1]=IdentityStore(Path(self.temp.name)/'1.sqlite');self.senders[1]=SenderRelease(self.identities[1],self.binary)
        self.assertIn('accepted',self.receive(1,before)[1]['states'].values())
        self.assertEqual(self.prepare(0,self.event(0,'d',dict(kind='message',text='Next',replyTo=[]))),before)

    def test_receive_transaction_fault_rolls_back_payload_and_checkpoint(self):
        q=self.question();wire=self.prepare(0,q);db=self.identities[1].db
        before=db.execute('SELECT revision,snapshot FROM mls_checkpoint').fetchone()
        with self.assertRaisesRegex(RuntimeError,'Injected'):
            self.senders[1].receiver.receive(unpack(wire),time=self.time,trust_policy='allow-unverified',fail_at='receive')
        self.assertEqual(db.execute('SELECT revision,snapshot FROM mls_checkpoint').fetchone(),before)
        self.assertEqual(db.execute('SELECT count(*) FROM mls_received_payloads').fetchone()[0],0)
        self.assertIn('accepted',self.receive(1,wire)[1]['states'].values())

    def test_pending_answer_projection_refreshes_each_distinct_wire(self):
        q=self.question();question_wire=self.prepare(0,q)
        answer=self.event(0,'b',dict(kind='answer',question=self.ref(q),option='c'*32,replaces=[]))
        # Author already has the target; third device receives answers first.
        normal=self.prepare(0,answer);raw=json.dumps(answer).encode()
        bad=self.inject(0,package_carrier(raw,'Conflicting answer','<p>Changed claim</p>',**DEFAULT_LIMITS))
        self.receive(2,normal);self.receive(2,bad)
        db=self.identities[2].db
        self.assertEqual(db.execute('SELECT count(*) FROM contributions').fetchone()[0],0)
        self.receive(2,question_wire)
        diagnostics=[]
        for wire in (normal,bad):
            digest=hashlib.sha256(unpack(wire)).hexdigest()
            diagnostics.append(json.loads(db.execute('SELECT representation FROM mls_received_payloads WHERE digest=?',(digest,)).fetchone()[0])['projection'])
            receipt=json.loads(db.execute('SELECT result FROM mls_receives WHERE digest=?',(digest,)).fetchone()[0])
            self.assertEqual(receipt['projection'],diagnostics[-1])
        self.assertEqual(diagnostics,['matched','mismatch'])
        self.assertEqual(db.execute('SELECT count(*) FROM contributions').fetchone()[0],2)

class JoinedRawCarrier(JoinedCarrier):
    selected_payload='raw-event-v0'
    def test_raw_context_rejects_mime_without_guessing(self):
        q=self.question();raw=json.dumps(q).encode();mime=package_carrier(raw,'Question','<p>Question</p>',**DEFAULT_LIMITS)
        self.assertEqual(self.receive(1,self.inject(0,mime))[0]['status'],'invalid-application-encoding')
        self.assertIn('accepted',self.receive(1,self.prepare(0,q))[1]['states'].values())
    # Only the format-specific test uses this subclass; do not inherit MIME cases.
    test_actual_smtp_question_answer_reaction_and_exact_retained_event=None
    test_malformed_carrier_commits_receive_state_without_raw_fallback=None
    test_distinct_mime_same_event_restart_and_pairing_diagnostic=None
    test_receive_transaction_fault_rolls_back_payload_and_checkpoint=None
    test_pending_answer_projection_refreshes_each_distinct_wire=None
