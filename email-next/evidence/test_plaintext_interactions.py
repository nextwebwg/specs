"""Real protected admission plus durable readable interaction copies."""
import json
from email.parser import BytesParser
from email import policy
import unittest
import test_joined_reactions as reactions
from plaintext_release import PlaintextRelease
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from identity_store import IdentityStore
from sender_release import SenderRelease
from pathlib import Path

def crash_submit(path,binary,delivery,port,time):
    import os
    store=IdentityStore(path)
    with SenderWorker(SenderRelease(store,binary)) as worker:
        worker.submit_plaintext(delivery,port=port,time=time,crash=lambda stage:os._exit(87) if stage=='after-final-response' else None)

class PlaintextInteractions(unittest.TestCase):
    selected_operations=reactions.JoinedReactions.selected_operations
    setUp=reactions.JoinedReactions.setUp
    tearDown=reactions.JoinedReactions.tearDown
    event=reactions.JoinedReactions.event
    prepare=reactions.JoinedReactions.prepare
    receive=reactions.JoinedReactions.receive
    question=reactions.JoinedReactions.question
    ref=reactions.JoinedReactions.ref
    def target(self):
        q=self.question();q['operation']['text']='Private question, deliberately copied only when authorized'
        self.receive(1,self.prepare(0,q));return q
    def import_mapping(self,fallback,target,mapping):
        from email.message import EmailMessage
        for recipient,identifier in mapping.items():
            message=EmailMessage(policy=policy.SMTP);message['Message-ID']=identifier
            message.set_content('Retained target representation')
            fallback.import_target_representation(target,recipient,message.as_bytes(),provenance={'kind':'trusted-local-import','source':'fixture-mailbox:'+recipient})

    def planned(self,event,*,mapping=None):
        event['disclosures']=[{'kind':'plaintext-email'}];raw=json.dumps(event).encode()
        fallback=PlaintextRelease(self.senders[1]);recipients=['legacy@example.invalid']
        if mapping is not None:self.import_mapping(fallback,event['operation']['target'],mapping)
        review=fallback.preview(raw,recipients,target_mapping=mapping)
        with self.assertRaisesRegex(ValueError,'authorization'):fallback.authorize(raw,recipients)
        fallback.authorize(raw,recipients,exposure=review)
        protected=self.prepare(1,event)
        wire=fallback.prepare('plain'+event['event'],event['event'])
        return fallback,review,protected,wire
    def submit(self,event):
        smtp=LocalSMTP()
        with SenderWorker(self.senders[1]) as worker:worker.submit_plaintext('plain'+event['event'],port=smtp.port,time=self.time)
        smtp.done();return smtp.wire
    def test_answer_exact_context_authorization_restart_and_actual_smtp(self):
        q=self.target();answer=self.event(1,'b',dict(kind='answer',question=self.ref(q),option='c'*32,replaces=[]))
        fallback,review,protected,wire=self.planned(answer)
        self.assertIn(q['operation']['text'],review['text']);self.assertIn('Morning',review['text'])
        self.assertNotIn(b'Private question',protected)
        self.identities[1].close();self.identities[1]=IdentityStore(Path(self.temp.name)/'1.sqlite');self.senders[1]=SenderRelease(self.identities[1],self.binary)
        self.assertEqual(PlaintextRelease(self.senders[1]).prepare('plain'+answer['event'],answer['event']),wire)
        self.assertEqual(self.submit(answer),wire)
        parsed=BytesParser(policy=policy.default).parsebytes(wire)
        self.assertEqual([p.get_content_type() for p in parsed.iter_parts()],['text/plain','text/html'])
        self.assertNotIn(b'legacy@example.invalid',wire)
        self.assertIn('accepted',self.receive(0,protected)[1]['states'].values())
    def test_reaction_pair_and_withdrawal_no_history_or_structured_alternative(self):
        q=self.target();reaction=self.event(1,'1',dict(kind='reaction',target=self.ref(q),emoji='👍'))
        _,review,protected,wire=self.planned(reaction,mapping={'legacy@example.invalid':'<known@legacy.example>'})
        parsed=BytesParser(policy=policy.default).parsebytes(self.submit(reaction));parts=list(parsed.iter_parts())
        self.assertEqual(parsed['In-Reply-To'],'<known@legacy.example>');self.assertEqual(parts[0].get_payload(decode=True),'👍\r\n'.encode())
        self.assertEqual(parts[0]['Content-Disposition'],'reaction');self.assertNotIn(q['operation']['text'],review['text'])
        self.receive(0,protected)
        withdrawal=self.event(1,'2',dict(kind='reaction-withdraw',target=self.ref(q),reactions=[self.ref(reaction)]))
        _,review,protected,wire=self.planned(withdrawal)
        parsed=BytesParser(policy=policy.default).parsebytes(self.submit(withdrawal))
        self.assertEqual(parsed.get_content_type(),'multipart/alternative')
        self.assertFalse(any(p.get_content_disposition()=='reaction' for p in parsed.walk()))
        self.assertNotIn(q['operation']['text'],review['text']);self.assertIn('accepted',self.receive(0,protected)[1]['states'].values())
    def test_missing_mapping_is_explanatory_and_changed_review_rejected(self):
        q=self.target();event=self.event(1,'1',dict(kind='reaction',target=self.ref(q),emoji='👍'));event['disclosures']=[{'kind':'plaintext-email'}]
        raw=json.dumps(event).encode();fallback=PlaintextRelease(self.senders[1]);recipients=['legacy@example.invalid']
        review=fallback.preview(raw,recipients);changed=dict(review,text='Hidden context')
        with self.assertRaisesRegex(ValueError,'exposure'):fallback.authorize(raw,recipients,exposure=changed)
        with self.assertRaisesRegex(ValueError,'Recipient-specific'):fallback.preview(raw,recipients,target_mapping={'other@example.invalid':'<a@b>'})
        fallback.authorize(raw,recipients,exposure=review);self.prepare(1,event)
        parsed=BytesParser().parsebytes(fallback.prepare('plain'+event['event'],event['event']))
        self.assertEqual(parsed.get_content_type(),'multipart/alternative');self.assertIsNone(parsed['In-Reply-To'])
    def test_recipient_specific_mapping_separate_routes_and_exact_retry(self):
        q=self.target();event=self.event(1,'1',dict(kind='reaction',target=self.ref(q),emoji='👍'));event['disclosures']=[{'kind':'plaintext-email'}]
        raw=json.dumps(event).encode();fallback=PlaintextRelease(self.senders[1]);recipients=['one@example.invalid','two@example.invalid']
        mapping=dict(zip(recipients,['<one@legacy.example>','<two@legacy.example>']))
        self.import_mapping(fallback,self.ref(q),mapping)
        review=fallback.preview(raw,recipients,target_mapping=mapping)
        fallback.authorize(raw,recipients,exposure=review);self.prepare(1,event)
        wires=[]
        for n,address in enumerate(recipients):
            delivery='route'+str(n);wire=fallback.prepare(delivery,event['event'],recipients=[address]);wires.append(wire)
            self.assertEqual(fallback.prepare(delivery,event['event'],recipients=[address]),wire)
            self.assertEqual(BytesParser().parsebytes(wire)['In-Reply-To'],review['targetMapping'][address])
            smtp=LocalSMTP()
            with SenderWorker(self.senders[1]) as worker:worker.submit_plaintext(delivery,port=smtp.port,time=self.time)
            smtp.done();self.assertEqual(smtp.wire,wire)
        self.assertNotEqual(wires[0],wires[1])
        with self.assertRaisesRegex(ValueError,'conflict'):fallback.prepare('route0',event['event'],recipients=[recipients[1]])
        with self.assertRaisesRegex(ValueError,'Unapproved'):fallback.prepare('other',event['event'],recipients=['other@example.invalid'])

    def test_actual_process_crash_after_data_preserves_uncertainty_and_exact_retry(self):
        import multiprocessing
        q=self.target();event=self.event(1,'1',dict(kind='reaction',target=self.ref(q),emoji='👍'))
        _,_,_,wire=self.planned(event);smtp=LocalSMTP();ctx=multiprocessing.get_context('spawn')
        process=ctx.Process(target=crash_submit,args=(Path(self.temp.name)/'1.sqlite',self.binary,'plain'+event['event'],smtp.port,self.time))
        process.start();process.join(15);smtp.done()
        self.assertEqual(process.exitcode,87);self.assertEqual(smtp.wire,wire)
        from unittest.mock import patch
        with SenderWorker(self.senders[1]) as worker:
            with patch('socket.create_connection',side_effect=AssertionError('No implicit retry')):
                with self.assertRaises(ValueError):worker.submit_plaintext('plain'+event['event'],port=1,time=self.time)
        smtp=LocalSMTP()
        with SenderWorker(self.senders[1]) as worker:worker.submit_plaintext('plain'+event['event'],port=smtp.port,time=self.time,retry_uncertain=True)
        smtp.done();self.assertEqual(smtp.wire,wire)

    def test_policy_change_after_release_aborts_before_data(self):
        q=self.target();event=self.event(1,'1',dict(kind='reaction',target=self.ref(q),emoji='👍'))
        self.planned(event);smtp=LocalSMTP()
        with SenderWorker(self.senders[1]) as worker:
            result=worker.submit_plaintext('plain'+event['event'],port=smtp.port,time=self.time,
                crash=lambda stage:self.senders[1].configure(expected_revision=1) if stage=='after-release' else None)
        smtp.done();self.assertIsNone(smtp.wire)
        self.assertEqual(result['state'],'aborted-before-data')

    def test_actual_signed_revocation_holds_ordinary_reaction_without_socket(self):
        import base64,hashlib
        from unittest.mock import patch
        from provider_mls import sign
        from event_encoding import encode_event
        q=self.target();event=self.event(1,'1',dict(kind='reaction',target=self.ref(q),emoji='👍'));self.planned(event)
        d=self.devices[1];r=d['record'];binding=json.loads(base64.b64decode(r['binding']))
        binding.update(record='f'*32,roles=['receive','enroll','revoke'],authority={'kind':'state','digest':d['state']})
        raw=encode_event(binding);state=json.loads(base64.b64decode(r['state']))
        state.update(record='9'*32,revision='1',previous=[d['state']],bindings=[dict(device=d['device'],digest=hashlib.sha256(raw).hexdigest())])
        payload=encode_event(state)
        bundle=dict(version='0',purpose='identity-bundle',principal=d['principal'],
          states=[dict(payload=base64.b64encode(payload).decode(),signature=sign(self.binary,d,'email-next/identity-state/v0',payload)),dict(payload=r['state'],signature=r['stateProof'])],
          bindings=[dict(payload=base64.b64encode(raw).decode(),authorization=sign(self.binary,d,'email-next/device-binding/v0',raw),possession=sign(self.binary,d,'email-next/device-possession/v0',raw)),dict(payload=r['binding'],authorization=r['authorization'],possession=r['possession'])])
        self.assertEqual(self.identities[1].accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(payload).hexdigest(),time=self.time)['status'],'accepted-unverified')
        with patch('socket.socket',side_effect=AssertionError('No socket')):
            with SenderWorker(self.senders[1]) as worker:
                with self.assertRaisesRegex(ValueError,'authority'):worker.submit_plaintext('plain'+event['event'],port=1,time=self.time)

    def test_mapping_requires_exact_target_recipient_and_unique_retained_evidence(self):
        q=self.target();event=self.event(1,'1',dict(kind='reaction',target=self.ref(q),emoji='👍'));event['disclosures']=[{'kind':'plaintext-email'}]
        raw=json.dumps(event).encode();fallback=PlaintextRelease(self.senders[1]);recipient='legacy@example.invalid';mapping={recipient:'<target@legacy.example>'}
        with self.assertRaisesRegex(ValueError,'evidence'):fallback.preview(raw,[recipient],target_mapping=mapping)
        other=dict(self.ref(q),event='f'*32)
        self.import_mapping(fallback,other,mapping)
        with self.assertRaisesRegex(ValueError,'evidence'):fallback.preview(raw,[recipient],target_mapping=mapping)
        self.import_mapping(fallback,self.ref(q),{'different@example.invalid':mapping[recipient]})
        with self.assertRaisesRegex(ValueError,'evidence'):fallback.preview(raw,[recipient],target_mapping=mapping)
        self.import_mapping(fallback,self.ref(q),mapping)
        review=fallback.preview(raw,[recipient],target_mapping=mapping)
        self.assertEqual(review['mappingEvidence'][0]['recipient'],recipient)
        fallback.authorize(raw,[recipient],exposure=review);self.prepare(1,event)
        self.import_mapping(fallback,self.ref(q),{recipient:'<conflict@legacy.example>'})
        with self.assertRaisesRegex(ValueError,'ambiguous'):fallback.prepare('ambiguous',event['event'])

    def test_unaccepted_question_cannot_authorize_copy(self):
        q=self.question();answer=self.event(1,'b',dict(kind='answer',question=self.ref(q),option='c'*32,replaces=[]));answer['disclosures']=[{'kind':'plaintext-email'}]
        with self.assertRaisesRegex(ValueError,'dependencies'):PlaintextRelease(self.senders[1]).preview(json.dumps(answer).encode(),['legacy@example.invalid'])

if __name__=='__main__':unittest.main()
