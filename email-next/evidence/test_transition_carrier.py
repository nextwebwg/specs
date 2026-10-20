"""Joined ordinary MIME/SMTP comparison; established-group joining remains test-only."""
import copy
import json
import subprocess
import unittest
from unittest.mock import patch
from email import policy
from email.parser import BytesParser
import test_group_transitions as fixtures
from transition_carrier import encode_transition,parse,receive_mime,release_mime
from transition_mime import package,select
from smtp_loopback import roundtrip
from sender_release import SenderRelease
from sender_worker import SenderWorker
from mls_mime import unpack
from event_encoding import encode_event

class TransitionCarrierTests(fixtures.GroupTransitionTests):
    def record(self,ident):return json.loads(self.ga.db.execute('SELECT state FROM gt_candidate WHERE digest=?',(ident,)).fetchone()[0])
    def mime(self,ident):return release_mime(self.ga,ident,sender='alice@example.invalid',recipient='bob@example.invalid',allowed=self.allowed,time=self.time)
    def application(self,event,text):
        return encode_event(dict(version='0',purpose='contribution',event=event*32,conversation='2'*32,principal=self.a['principal'],audience=sorted([self.a['principal'],self.b['principal'],self.c['principal']]),operation=dict(kind='message',text=text,replyTo=[])))
    def prepare_application(self,sender,identifier,event):
        return sender.prepare(identifier,self.application(event,'hello'),key=self.a['key'],envelope_sender='alice@example.invalid',recipients=['bob@example.invalid','carol@example.invalid'],time=self.time)
    def test_actual_mail_before_and_after_transition_and_stale_release_hold(self):
        sender=SenderRelease(self.ga.identity,self.provider);sender.configure(expected_revision=0)
        first=self.prepare_application(sender,'first','1')
        self.assertEqual(self.gb.receiver.receive(unpack(roundtrip(first)),time=self.time,trust_policy='allow-unverified')['status'],'projected-context-matched')
        ident=self.prepared();self.ga.decide(ident,allowed=self.allowed,time=self.time)
        transported=roundtrip(self.mime(ident))
        self.assertEqual(receive_mime(self.gb,transported,allowed=self.allowed,time=self.time),'accepted')
        self.assertEqual(receive_mime(self.gb,transported,allowed=set(),time=self.time),'accepted')
        with SenderWorker(sender) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No stale socket')):
            with self.assertRaisesRegex(ValueError,'Changed group metadata'):worker.submit('first',port=1,time=self.time)
        after=self.prepare_application(sender,'after','3')
        self.assertEqual(self.gb.receiver.receive(unpack(roundtrip(after)),time=self.time,trust_policy='allow-unverified')['status'],'projected-context-matched')
        self.assertEqual(self.gb.db.execute('SELECT count(*) FROM contributions').fetchone()[0],2)
        self.assertFalse(self.gb.db.execute("SELECT 1 FROM sqlite_master WHERE name='gt_live'").fetchone())
    def test_same_epoch_application_change_retire_and_fresh_authorization(self):
        ident=self.prepared();sender=SenderRelease(self.ga.identity,self.provider);sender.configure(expected_revision=0)
        application=self.prepare_application(sender,'between','1')
        # Receiving an application also changes Bob's shared ratchet state before commit arrival.
        self.gb.receiver.receive(unpack(application),time=self.time,trust_policy='allow-unverified')
        retained=self.ga.live()
        with self.assertRaisesRegex(ValueError,'Predecessor changed'):self.ga.decide(ident,allowed=self.allowed,time=self.time)
        with self.assertRaisesRegex(ValueError,'Unauthorized addition'):self.ga.retire(ident,allowed=set(),time=self.time)
        self.ga.retire(ident,allowed=self.allowed,time=self.time)
        replacement=self.prepared();self.assertNotEqual(ident,replacement)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM gt_abandoned').fetchone()[0],1)
        self.assertEqual(self.ga.live(),retained)
        self.ga.decide(replacement,allowed=self.allowed,time=self.time)
        with self.assertRaisesRegex(ValueError,'Already decided'):self.ga.retire(replacement,allowed=self.allowed,time=self.time)
        self.assertEqual(receive_mime(self.gb,self.mime(replacement),allowed=self.allowed,time=self.time),'accepted')
    def test_strict_carrier_tampering_and_direct_scope_are_inert(self):
        ident=self.prepared()
        with self.assertRaisesRegex(ValueError,'withheld'):self.mime(ident)
        self.ga.decide(ident,allowed=self.allowed,time=self.time)
        wire=self.mime(ident);initial=self.gb.live()
        v,commit=parse(select(wire))
        for field,value in [('previousContext','0'*64),('previousEpoch','9'),('ordering','unknown'),('proposals',['AAAA'])]:
            changed=dict(v);changed[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):receive_mime(self.gb,package(encode_event(changed),sender='alice@example.invalid',recipient='bob@example.invalid'),allowed=self.allowed,time=self.time)
        root=BytesParser(policy=policy.default).parsebytes(wire);root.attach(copy.deepcopy(list(root.iter_parts())[1]))
        with self.assertRaises(ValueError):receive_mime(self.gb,root.as_bytes(),allowed=self.allowed,time=self.time)
        from email.message import EmailMessage
        forward=EmailMessage();forward.set_content('Forward');forward.add_attachment(BytesParser(policy=policy.default).parsebytes(wire))
        with self.assertRaises(ValueError):receive_mime(self.gb,forward.as_bytes(),allowed=self.allowed,time=self.time)
        self.assertEqual(self.gb.live(),initial)
    def test_rejected_control_then_application_and_receive_race(self):
        bad=self.gb.prepare([self.phone['package']])
        wrong=json.loads(self.gb.db.execute('SELECT state FROM gt_candidate WHERE digest=?',(bad,)).fetchone()[0])
        self.assertEqual(self.gc.receive(bytes.fromhex(wrong['wire']),allowed=self.allowed,time=self.time),'rejected-policy')
        alice_sender=SenderRelease(self.ga.identity,self.provider);alice_sender.configure(expected_revision=0)
        wire=self.prepare_application(alice_sender,'afterrejection','1')
        self.assertEqual(self.gc.receiver.receive(unpack(roundtrip(wire)),time=self.time,trust_policy='allow-unverified')['status'],'projected-context-matched')
        candidate=self.prepared()
        bob_sender=SenderRelease(self.gb.identity,self.provider);bob_sender.configure(expected_revision=0)
        reply=json.loads(self.application('4','reply'));reply['principal']=self.b['principal']
        mail=bob_sender.prepare('reply',encode_event(reply),key=self.b['key'],envelope_sender='bob@example.invalid',recipients=['alice@example.invalid','carol@example.invalid'],time=self.time)
        self.assertEqual(self.ga.receiver.receive(unpack(roundtrip(mail)),time=self.time,trust_policy='allow-unverified')['status'],'projected-context-matched')
        retained=self.ga.live()
        with self.assertRaisesRegex(ValueError,'Predecessor changed'):self.ga.decide(candidate,allowed=self.allowed,time=self.time)
        self.assertEqual(self.ga.live(),retained)
    def test_malformed_mime_headers_and_notice_do_not_activate(self):
        ident=self.prepared();self.ga.decide(ident,allowed=self.allowed,time=self.time);wire=self.mime(ident)
        for location,header,value in [('root','Content-Type','multipart/mixed'),('notice','Content-Transfer-Encoding','base64'),('notice','Content-Disposition','inline'),('part','Content-Type','text/plain')]:
            message=BytesParser(policy=policy.default).parsebytes(wire);notice,part=list(message.iter_parts());target={'root':message,'notice':notice,'part':part}[location]
            if header=='Content-Disposition':target._headers.append((header,'attachment'))
            target._headers.append((header,value))
            with self.subTest(location=location,header=header),self.assertRaises(ValueError):select(message.as_bytes())
        message=BytesParser(policy=policy.default).parsebytes(wire);notice=list(message.iter_parts())[0]
        notice.replace_header('Content-Transfer-Encoding','base64');notice.set_payload('/w==')
        with self.assertRaises(ValueError):select(message.as_bytes())
        self.assertEqual(self.gb.db.execute('SELECT count(*) FROM gt_receive').fetchone()[0],0)
    def test_future_carrier_retains_exact_binding_and_bare_retry_cannot_strip_it(self):
        from group_transitions import digest
        first=self.prepared();self.ga.decide(first,allowed=self.allowed,time=self.time);first_mail=self.mime(first)
        second=self.ga.prepare([]);self.ga.decide(second,allowed=set(),time=self.time)
        good_raw=encode_transition(self.record(second));value,commit=parse(good_raw)
        value['previousContext']='0'*64
        bad_raw=json.dumps(value,indent=2).encode()
        bad_mail=package(bad_raw,sender='alice@example.invalid',recipient='bob@example.invalid')
        self.assertEqual(receive_mime(self.gb,bad_mail,allowed=set(),time=self.time),'pending')
        identifier=digest(commit)
        self.assertEqual(self.gb.db.execute('SELECT carrier FROM gt_pending WHERE digest=?',(identifier,)).fetchone()[0],bad_raw)
        self.assertEqual(receive_mime(self.gb,first_mail,allowed=self.allowed,time=self.time),'accepted')
        before=self.gb.live()
        with self.assertRaisesRegex(ValueError,'predecessor mismatch'):self.gb.reprocess_pending(identifier,allowed=set(),time=self.time)
        with self.assertRaisesRegex(ValueError,'predecessor mismatch'):self.gb.receive(commit,allowed=set(),time=self.time)
        self.assertEqual(self.gb.live(),before)
        # Unauthenticated bad metadata cannot permanently poison a valid commit.
        correct=package(good_raw,sender='alice@example.invalid',recipient='bob@example.invalid')
        self.assertEqual(receive_mime(self.gb,correct,allowed=set(),time=self.time),'accepted')
    def test_digest_index_never_substitutes_for_exact_commit_bytes(self):
        from group_transitions import digest
        ident=self.prepared();self.ga.decide(ident,allowed=self.allowed,time=self.time)
        value,wire=parse(select(self.mime(ident)))
        self.assertEqual(receive_mime(self.gb,self.mime(ident),allowed=self.allowed,time=self.time),'accepted')
        self.assertEqual(self.gb.db.execute('SELECT wire FROM gt_receive WHERE digest=?',(digest(wire),)).fetchone()[0],wire)
        self.assertEqual(self.gb.receive(wire,allowed=set(),time=self.time),'accepted')
        changed=wire[:-1]+bytes([wire[-1]^1])
        with patch('group_transitions.digest',return_value=digest(wire)):
            with self.assertRaisesRegex(ValueError,'digest collision'):self.gb.receive(changed,allowed=set(),time=self.time)
    def test_context_opt_in_is_explicit_and_unknown_shapes_rejected(self):
        event=json.loads(self.application('1','hello'));context=json.loads(self.ctx)
        request=dict(event=event,credential=self.a['identity'],context=context,members=[m['identity'] for m in self.initial['snapshot']['members']])
        from pathlib import Path
        bridge=Path(__file__).with_name('check-mls-contribution.mjs')
        def check(value):return subprocess.run(['node',str(bridge)],input=json.dumps(value),text=True,capture_output=True,check=True,timeout=10).stdout
        self.assertEqual(check(request),'invalid-shape')
        self.assertEqual(check(dict(request,configuredEndpointOrdering=True)),'projected-context-matched')
        for mutate in [dict(context,version='2'),dict(context,extra=True),dict(context,ordering=dict(context['ordering'],device=self.c['device']))]:
            self.assertNotEqual(check(dict(request,context=mutate,configuredEndpointOrdering=True)),'projected-context-matched')

for name in vars(fixtures.GroupTransitionTests):
    if name.startswith('test_'):setattr(TransitionCarrierTests,name,None)
if __name__=='__main__':unittest.main()
