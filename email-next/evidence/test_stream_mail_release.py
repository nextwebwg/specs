"""Actual loopback SMTP, signed admission and owner-bound source traffic."""
import json
import sqlite3
import unittest
from unittest.mock import patch

from event_encoding import encode_event,decode_event
from initial_roster import parse
from initial_roster_lifecycle import InitialRosterAdmission
from invitation_mime import select
from mls_mime import unpack
from provider_mls import call
from sender_stream_admission import SenderStreamAdmission
from sender_stream_source import SenderStreamSource
from sender_worker import SenderWorker
from stream_mail_release import StreamMailRelease
from test_sender_release import LocalSMTP
import test_initial_roster_lifecycle as fixtures


class StreamMailTests(unittest.TestCase):
    application=dict(envelopeVersion='1',payload='raw-event-v0',operations=['message'])
    endpoint=fixtures.RosterLifecycleTests.endpoint
    prepare=fixtures.RosterLifecycleTests.prepare
    tearDown=fixtures.RosterLifecycleTests.tearDown

    def setUp(self):
        fixtures.RosterLifecycleTests.setUp(self)
        if self._testMethodName=='test_enrolled_phone_sends_before_recipient_joins':
            self.f.creator=next(d for d in self.f.devices if d['principal']==self.f.creator['principal'] and d is not self.f.creator)
            self.f.context['ordering']['device']=self.f.creator['device']
        self.wires=self.prepare()
        self.raw=select(next(iter(self.wires.values())))
        self.source=SenderStreamSource(self.identity,self.f.binary,configured=True)
        self.stream=self.source.adopt_created(self.raw,device=self.f.creator,time=self.time)
        self.release=StreamMailRelease(self.sender,self.source)
        self.peer=next(d for d in self.f.devices if d['principal']!=self.f.creator['principal'])
        self.initial_id=next(ident for ident,wire in self.wires.items() if parse(select(wire))['value']['target']['device']==self.peer['device'])

    def event(self,ident):
        return encode_event(dict(version='1',purpose='contribution',event=ident,conversation=self.f.context['conversation'],principal=self.f.creator['principal'],audience=self.principals,disclosures=[],operation=dict(kind='message',text='Over actual SMTP',replyTo=[])))

    def submit(self,delivery,**options):
        server=LocalSMTP()
        with SenderWorker(self.sender) as worker:
            result=worker.submit_stream(delivery,release=self.release,port=server.port,time=self.time,**options)
        server.done()
        return result,server.wire

    def prepare_root(self,ident='a'*32):
        body=self.event(ident)
        self.source.prepare(self.stream,ident,time=self.time,application=body)
        return body,self.release.prepare('b'*32,self.stream,ident,time=self.time)

    def test_invitation_root_update_and_followup_cross_mail_path(self):
        expected=self.release.prepare('1'*32,self.stream,self.initial_id,time=self.time,form='initial')
        result,received=self.submit('1'*32)
        self.assertEqual(result['state'],'accepted');self.assertEqual(received,expected)
        identity,receiver_sender,selected=self.endpoint('stream-mail-recipient')
        admission=InitialRosterAdmission(identity,self.f.binary);admission.publish_local(self.peer)
        owner=dict(principal=self.f.creator['principal'],device=self.f.creator['device'],signingKey=self.f.creator['key'])
        parsed=parse(select(received))
        SenderStreamAdmission(admission,configured=True).accept(select(received),stream=self.stream,owner=owner,target=self.peer,mailbox=parsed['value']['target']['mailbox'],allow_creator=owner['principal'],intended_principals=self.principals,intended_devices=self.devices,expected_context=encode_event(self.f.context),selections=[dict(principal=d['principal'],device=d['device'],mailbox=c['mailbox'],generation=c['generation']) for d,c in zip(self.f.devices,selected)],time=self.time,trust_policy='allow-unverified')
        body,wire=self.prepare_root()
        result,received=self.submit('b'*32)
        self.assertEqual(result['state'],'accepted');self.assertEqual(received,wire)
        accepted=receiver_sender.receiver.receive(unpack(received),time=self.time,trust_policy='allow-unverified')
        self.assertEqual(accepted['applicationState'],'accepted')
        self.assertEqual(json.loads(body)['operation']['text'],'Over actual SMTP')
        self.source.prepare(self.stream,'c'*32,time=self.time)
        self.release.prepare('d'*32,self.stream,'c'*32,time=self.time)
        result,control_wire=self.submit('d'*32);self.assertEqual(result['state'],'accepted')
        packet=decode_event(unpack(control_wire))['value']
        row=identity.db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
        # Controlled test installation; complete control-receiver API remains absent.
        transitioned=call(self.f.binary.with_name('group-transitions'),op='receive',checkpoint=json.loads(row[1]),group=row[0],key=self.peer['key'],wire=packet['commit'])
        self.assertEqual(transitioned['sender'],self.f.creator['identity'])
        self.assertEqual(transitioned['before']['predecessor'],packet['predecessor']);self.assertEqual(transitioned['after']['predecessor'],packet['result'])
        identity.db.execute('UPDATE mls_checkpoint SET revision=revision+1,snapshot=? WHERE id=1',(json.dumps(transitioned['checkpoint']).encode(),))
        body=self.event('e'*32);self.source.prepare(self.stream,'e'*32,time=self.time,application=body)
        self.release.prepare('f'*32,self.stream,'e'*32,time=self.time)
        result,received=self.submit('f'*32);self.assertEqual(result['state'],'accepted')
        self.assertEqual(receiver_sender.receiver.receive(unpack(received),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')

    def test_enrolled_phone_sends_before_recipient_joins(self):
        self.assertIsNot(self.f.creator,self.f.devices[0])
        body,wire=self.prepare_root()
        result,waiting=self.submit('b'*32)
        self.assertEqual(result['state'],'accepted');self.assertEqual(waiting,wire)
        # No recipient endpoint has joined or supplied an ordering vote yet.
        self.release.prepare('1'*32,self.stream,self.initial_id,time=self.time,form='initial')
        result,invitation=self.submit('1'*32);self.assertEqual(result['state'],'accepted')
        identity,receiver_sender,selected=self.endpoint('offline-peer')
        admission=InitialRosterAdmission(identity,self.f.binary);admission.publish_local(self.peer)
        parsed=parse(select(invitation));owner=dict(principal=self.f.creator['principal'],device=self.f.creator['device'],signingKey=self.f.creator['key'])
        SenderStreamAdmission(admission,configured=True).accept(select(invitation),stream=self.stream,owner=owner,target=self.peer,mailbox=parsed['value']['target']['mailbox'],allow_creator=owner['principal'],intended_principals=self.principals,intended_devices=self.devices,expected_context=encode_event(self.f.context),selections=[dict(principal=d['principal'],device=d['device'],mailbox=c['mailbox'],generation=c['generation']) for d,c in zip(self.f.devices,selected)],time=self.time,trust_policy='allow-unverified')
        self.assertEqual(receiver_sender.receiver.receive(unpack(waiting),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        self.assertEqual(json.loads(body)['principal'],self.f.creator['principal'])

    def test_handoff_is_not_automatically_repeated_or_rewrapped(self):
        _,wire=self.prepare_root()
        result,received=self.submit('b'*32);self.assertEqual(result['state'],'accepted');self.assertEqual(wire,received)
        with SenderWorker(self.sender) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No repeated socket')):
            with self.assertRaisesRegex(ValueError,'Already handed off'):worker.submit_stream('b'*32,release=self.release,port=12345,time=self.time)
        with self.assertRaises(sqlite3.IntegrityError):self.release.prepare('c'*32,self.stream,'a'*32,time=self.time)
        self.assertEqual(self.release.prepare('b'*32,self.stream,'a'*32,time=self.time),wire)

    def test_policy_change_after_release_aborts_before_data(self):
        self.prepare_root()
        def change(stage):
            if stage=='after-release':self.sender.configure(expected_revision=1,trust_policy='require-verification')
        result,wire=self.submit('b'*32,crash=change)
        self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(wire)

    def test_sender_address_disabled_after_release_aborts_before_data(self):
        self.prepare_root()
        source_index=self.f.devices.index(self.f.creator);mailbox=self.selected[source_index]['mailbox']
        def disable(stage):
            if stage=='after-release':self.sender.associations.decide(decision_id='e'*32,mailbox=mailbox,expected_generation='1',kind='disable',principal=self.f.creator['principal'],actor='local-user',policy_revision='1',trust_policy='allow-unverified',time=self.time)
        result,wire=self.submit('b'*32,crash=disable)
        self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(wire)

    def test_lost_data_response_requires_explicit_retry_of_original_mail(self):
        _,wire=self.prepare_root();before=self.source._live(self.stream)[1]
        first=LocalSMTP(drop=True)
        with SenderWorker(self.sender) as worker:
            outcome=worker.submit_stream('b'*32,release=self.release,port=first.port,time=self.time)
            first.done();self.assertEqual(outcome['state'],'uncertain');self.assertEqual(first.wire,wire)
            with patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No implicit uncertainty retry')):
                with self.assertRaisesRegex(ValueError,'Uncertain prior attempt'):worker.submit_stream('b'*32,release=self.release,port=12345,time=self.time)
            second=LocalSMTP()
            retried=worker.submit_stream('b'*32,release=self.release,port=second.port,time=self.time,retry_uncertain=True)
            second.done();self.assertEqual(retried['state'],'accepted');self.assertEqual(second.wire,wire)
        self.assertEqual(self.source._live(self.stream)[1],before)

    def test_partial_rcpt_retry_uses_only_remaining_envelope_recipient(self):
        _,wire=self.prepare_root()
        targets=json.loads(self.identity.db.execute('SELECT envelope FROM stream_mail_prepared').fetchone()[0])['recipients']
        first=LocalSMTP(rcpt=[b'450 temporary\r\n']+[b'250 recipient\r\n']*(len(targets)-1))
        with SenderWorker(self.sender) as worker:
            initial=worker.submit_stream('b'*32,release=self.release,port=first.port,time=self.time)
            first.done();self.assertEqual(initial['state'],'accepted')
            second=LocalSMTP();retried=worker.submit_stream('b'*32,release=self.release,port=second.port,time=self.time)
            second.done();self.assertEqual(retried['state'],'accepted');self.assertEqual(second.wire,wire)
            self.assertEqual(retried['result']['acceptedRecipients'],targets[:1])

    def test_change_while_waiting_for_354_blocks_first_body_byte(self):
        self.prepare_root()
        path=self.identity.db.execute('PRAGMA database_list').fetchone()[2]
        def change():
            from identity_store import IdentityStore
            from sender_release import SenderRelease
            other=IdentityStore(path)
            try:SenderRelease(other,self.f.binary).configure(expected_revision=1,trust_policy='require-verification')
            finally:other.close()
        server=LocalSMTP(before_data=change,allow_empty_abort=True)
        with SenderWorker(self.sender) as worker:
            result=worker.submit_stream('b'*32,release=self.release,port=server.port,time=self.time)
        server.done();self.assertEqual(result['state'],'aborted-before-data')
        self.assertEqual(result['result']['phase'],'body-not-released');self.assertIsNone(server.wire)

    def test_invitation_expiring_during_proof_work_opens_no_socket(self):
        self.release.prepare('1'*32,self.stream,self.initial_id,time=self.time,form='initial')
        original=self.release._material;elapsed=[0]
        def spending(*args):
            material=original(*args);elapsed[0]=31*1000000000;return material
        with patch('stream_mail_release.elapsed_time.monotonic_ns',side_effect=lambda:elapsed[0]),patch.object(self.release,'_material',side_effect=spending),patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No expired release socket')):
            with SenderWorker(self.sender) as worker:
                with self.assertRaisesRegex(ValueError,'invitation validity'):worker.submit_stream('1'*32,release=self.release,port=12345,time=self.time)

    def test_original_invitation_expiry_not_extended_by_stream_clock(self):
        self.release.prepare('1'*32,self.stream,self.initial_id,time=self.time,form='initial')
        future=dict(earliest=str(int(self.f.time)+31),latest=str(int(self.f.time)+31))
        with SenderWorker(self.sender) as worker,patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No expired socket')):
            with self.assertRaisesRegex(ValueError,'invitation validity'):worker.submit_stream('1'*32,release=self.release,port=12345,time=future)


if __name__=='__main__':unittest.main()
