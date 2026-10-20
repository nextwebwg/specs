"""Actual protected reaction admission; configured profile, no public discovery claim."""
import json
import unittest
import test_joined_questions as questions
from journal_reaction_view import derive_reaction_view

class JoinedReactions(unittest.TestCase):
    selected_operations=['answer','message','question','reaction','reaction-withdraw']
    setUp=questions.JoinedQuestions.setUp
    tearDown=questions.JoinedQuestions.tearDown
    event=questions.JoinedQuestions.event
    prepare=questions.JoinedQuestions.prepare
    receive=questions.JoinedQuestions.receive
    question=questions.JoinedQuestions.question
    def ref(self,event):return {k:event[k] for k in ('principal','conversation','event')}
    def view(self,who,target):return derive_reaction_view(self.senders[who].receiver.journal,self.ref(target))
    def test_actual_reaction_withdrawal_and_distinct_equal_events(self):
        target=self.question();self.receive(1,self.prepare(0,target))
        one=self.event(1,'1',dict(kind='reaction',target=self.ref(target),emoji='👍'))
        two=self.event(1,'2',dict(kind='reaction',target=self.ref(target),emoji='👍'))
        wire=self.prepare(1,one);self.receive(0,wire);self.receive(0,wire)
        self.assertEqual(self.view(0,target)['active'],[self.ref(one)])
        self.receive(0,self.prepare(1,two));self.assertEqual(len(self.view(0,target)['active']),2)
        withdrawal=self.event(1,'3',dict(kind='reaction-withdraw',target=self.ref(target),reactions=[self.ref(one)]))
        self.receive(0,self.prepare(1,withdrawal));self.assertEqual(self.view(0,target)['active'],[self.ref(two)])
    def test_reordered_target_and_withdrawal_promote_only_when_complete(self):
        target=self.question();target_wire=self.prepare(0,target);self.receive(1,target_wire)
        reaction=self.event(1,'1',dict(kind='reaction',target=self.ref(target),emoji='👍'))
        reaction_wire=self.prepare(1,reaction)
        withdrawal=self.event(1,'2',dict(kind='reaction-withdraw',target=self.ref(target),reactions=[self.ref(reaction)]))
        withdrawal_wire=self.prepare(1,withdrawal)
        # Third member has neither target nor reaction. Authenticating the
        # withdrawal first cannot create a target or suppress arbitrary history.
        self.receive(2,withdrawal_wire);self.assertEqual(self.view(2,target)['active'],[])
        self.receive(2,reaction_wire);self.assertEqual(self.view(2,target)['active'],[])
        self.receive(2,target_wire);self.assertEqual(self.view(2,target)['active'],[])
        kinds=[json.loads(r[0])['operation']['kind'] for r in self.identities[2].db.execute('SELECT octets FROM contributions')]
        self.assertCountEqual(kinds,['question','reaction','reaction-withdraw'])
    def test_pending_answer_is_not_an_authorized_reaction_target(self):
        question=self.question();self.receive(1,self.prepare(0,question))
        answer=self.event(1,'1',dict(kind='answer',question=self.ref(question),option='c'*32,replaces=[]))
        answer_wire=self.prepare(1,answer)
        reaction=self.event(1,'2',dict(kind='reaction',target=self.ref(answer),emoji='👍'))
        reaction_wire=self.prepare(1,reaction)
        self.receive(2,answer_wire);self.receive(2,reaction_wire)
        self.assertEqual(self.identities[2].db.execute('SELECT count(*) FROM contributions').fetchone()[0],0)
        self.assertEqual(self.view(2,answer)['active'],[])

    def test_durable_client_intent_restart_and_deliberate_second_reaction(self):
        from client_flow import ClientFlow
        from identity_store import IdentityStore
        from sender_release import SenderRelease
        from pathlib import Path
        target=self.question();self.receive(1,self.prepare(0,target));ref=self.ref(target)
        def client():return ClientFlow(self.senders[1],key=self.devices[1]['key'],envelope_sender='bob@example.invalid',recipients=['alice@example.invalid'])
        token=self.view(1,target)['sourceToken'];wire=client().react('click1',ref,'👍',token,time=self.time)
        self.identities[1].close();self.identities[1]=IdentityStore(Path(self.temp.name)/'1.sqlite');self.senders[1]=SenderRelease(self.identities[1],self.binary)
        self.assertEqual(client().react('click1',ref,'👍',token,time=self.time),wire)
        with self.assertRaisesRegex(ValueError,'conflict'):client().react('click1',ref,'👎',token,time=self.time)
        self.receive(0,wire)
        second=client().react('click2',ref,'👍',self.view(1,target)['sourceToken'],time=self.time);self.receive(0,second)
        self.assertEqual(len(self.view(0,target)['active']),2)
        withdrawal=client().withdraw_reactions('withdraw1',ref,self.view(1,target)['sourceToken'],time=self.time)
        self.receive(0,withdrawal);self.assertEqual(self.view(0,target)['active'],[])

    def test_real_signed_send_revocation_holds_reaction_and_prepared_submission(self):
        import base64,hashlib
        from unittest.mock import patch
        from provider_mls import sign
        from event_encoding import encode_event
        from client_flow import ClientFlow
        from journal_reaction_view import derive_reaction_view
        from sender_worker import SenderWorker
        question=self.question();self.receive(1,self.prepare(0,question));ref={k:question[k] for k in ('principal','conversation','event')}
        client=ClientFlow(self.senders[1],key=self.devices[1]['key'],envelope_sender='bob@example.invalid',recipients=['alice@example.invalid'])
        token=derive_reaction_view(self.senders[1].receiver.journal,ref)['sourceToken']
        client.react('readyanswer',ref,'👍',token,time=self.time)
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
        token=derive_reaction_view(self.senders[1].receiver.journal,ref)['sourceToken']
        with self.assertRaisesRegex(ValueError,'authority'):client.react('afterrevoke',ref,'👍',token,time=self.time)


    def test_ordinary_rfc9078_message_cannot_create_protected_badge(self):
        from email.message import EmailMessage
        from email import policy
        from mls_mime import unpack
        from smtp_loopback import roundtrip
        target=self.question();self.receive(1,self.prepare(0,target))
        before=self.view(1,target)
        ordinary=EmailMessage(policy=policy.SMTP);ordinary['From']='bob@example.invalid';ordinary['To']='alice@example.invalid'
        ordinary['Subject']='Reaction';ordinary['In-Reply-To']='<ordinary-target@example.invalid>'
        ordinary.set_content('👍',charset='utf-8');ordinary['Content-Disposition']='reaction'
        raw=roundtrip(ordinary.as_bytes())
        with self.assertRaises(ValueError):unpack(raw)
        self.assertEqual(self.view(1,target),before)
