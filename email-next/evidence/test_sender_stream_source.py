"""Actual source checkpoint/outbox continuity; no public stream negotiation claim."""
import json
import base64
import hashlib
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import unittest

from event_encoding import encode_event, decode_event
from identity_store import IdentityStore
from invitation_mime import select
from provider_mls import call, sign
from sender_stream_source import SenderStreamSource, CONTROL
import test_initial_roster_lifecycle as fixtures


class StreamSourceTests(unittest.TestCase):
    application = dict(envelopeVersion='1', payload='raw-event-v0', operations=['message'])
    endpoint = fixtures.RosterLifecycleTests.endpoint
    prepare = fixtures.RosterLifecycleTests.prepare
    tearDown = fixtures.RosterLifecycleTests.tearDown

    def setUp(self):
        fixtures.RosterLifecycleTests.setUp(self)
        self.wires = self.prepare()
        self.raw = select(next(iter(self.wires.values())))
        self.source = SenderStreamSource(self.identity, self.f.binary, configured=True)
        self.stream = '3'*32 if self._testMethodName=='test_used_ordinary_source_cannot_be_relabelled' else self.source.adopt_created(self.raw, device=self.f.creator, time=self.time)
        self.peer = next(d for d in self.f.devices if d is not self.f.creator)
        # Use only the exact original locally created Welcome, not peer state.
        from initial_roster import parse
        parsed = parse(self.raw)
        self.peer_state = call(self.f.binary, op='join-initial-roster', checkpoint=self.peer['checkpoint'], key=self.peer['key'], identity=self.peer['identity'], reference=self.peer['reference'], references=parsed['references'], welcome=parsed['welcome'].hex())['checkpoint']

    def event(self, ident, text='Root contribution'):
        return encode_event(dict(version='1', purpose='contribution', principal=self.f.creator['principal'], conversation=self.f.context['conversation'], audience=self.principals, disclosures=[], event=ident, operation=dict(kind='message',text=text,replyTo=[])))

    def send(self, ident, **options):
        return self.source.prepare(self.stream, ident, time=self.time, **options)

    def receive(self, wire):
        result = call(self.f.binary.with_name('receive-staged'), format='openmls-0.9.1-map-0', checkpoint=self.peer_state, group=self.source._live(self.stream)[0]['group'], wire=wire.hex())
        self.peer_state = result['checkpoint']
        return bytes.fromhex(result['application'])

    def test_used_ordinary_source_cannot_be_relabelled(self):
        source_index=self.f.devices.index(self.f.creator)
        self.sender.prepare('f'*32,self.event('e'*32),key=self.f.creator['key'],envelope_sender=self.selected[source_index]['mailbox'],recipients=[c['mailbox'] for i,c in enumerate(self.selected) if i!=source_index],time=self.time)
        with self.assertRaisesRegex(ValueError,'unused initial source'):
            self.source.adopt_created(self.raw,device=self.f.creator,time=self.time)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM stream_source').fetchone()[0],0)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0],1)

    def test_exclusive_adoption_and_exact_immutable_message_retry(self):
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0],0)
        body=self.event('a'*32);wire=self.send('1'*32,application=body)
        self.assertEqual(self.send('1'*32,application=body),wire)
        self.assertEqual(self.receive(wire),body)
        with self.assertRaisesRegex(ValueError,'Immutable source operation'):self.send('1'*32,application=self.event('b'*32))
        with self.assertRaisesRegex(ValueError,'Immutable event'):self.send('2'*32,application=self.event('a'*32,'Changed'))
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM stream_source_outbox').fetchone()[0],1)

    def test_consecutive_owner_controls_and_message_are_real_mls_chain(self):
        group=self.source._live(self.stream)[0]['group'];previous=None
        for ident in ('2'*32,'3'*32):
            raw=self.send(ident);packet=decode_event(raw)['value']
            self.assertEqual(packet['purpose'],CONTROL)
            if previous:self.assertEqual(packet['predecessor'],previous)
            applied=call(self.f.binary.with_name('group-transitions'),op='receive',checkpoint=self.peer_state,group=group,key=self.peer['key'],wire=packet['commit'])
            self.assertEqual(applied['sender'],self.f.creator['identity'])
            self.assertEqual(applied['before']['predecessor'],packet['predecessor'])
            self.assertEqual(applied['after']['predecessor'],packet['result'])
            self.peer_state=applied['checkpoint'];previous=packet['result']
            self.assertEqual(self.send(ident),raw)
        body=self.event('c'*32);self.assertEqual(self.receive(self.send('4'*32,application=body)),body)

    def test_precommit_failure_has_no_public_output_or_advanced_state(self):
        before=self.source._live(self.stream)[1]
        with self.assertRaisesRegex(RuntimeError,'caller crash'):
            self.send('5'*32,crash=lambda stage:(_ for _ in ()).throw(RuntimeError('caller crash')) if stage=='before-commit' else None)
        self.assertEqual(self.source._live(self.stream)[1],before)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM stream_source_outbox').fetchone()[0],0)
        packet=decode_event(self.send('5'*32))['value']
        self.assertEqual(packet['predecessor'],call(self.f.binary.with_name('group-transitions'),op='inspect',checkpoint=before,key=self.f.creator['key'],group=packet['group'])['snapshot']['predecessor'])

    def test_after_commit_failure_and_reopen_return_exact_original_bytes(self):
        with self.assertRaisesRegex(RuntimeError,'after commit'):
            self.send('6'*32,crash=lambda stage:(_ for _ in ()).throw(RuntimeError('after commit')) if stage=='after-commit' else None)
        expected=self.identity.db.execute('SELECT wire FROM stream_source_outbox').fetchone()[0]
        filename=self.identity.db.execute('PRAGMA database_list').fetchone()[2]
        reopened=IdentityStore(filename)
        try:
            source=SenderStreamSource(reopened,self.f.binary,configured=True)
            self.assertEqual(source.prepare(self.stream,'6'*32,time=self.time),expected)
            successor=decode_event(source.prepare(self.stream,'7'*32,time=self.time))['value']
            self.assertEqual(successor['predecessor'],decode_event(expected)['value']['result'])
        finally:reopened.close()

    def test_two_connections_cannot_reserve_competing_successors(self):
        filename=self.identity.db.execute('PRAGMA database_list').fetchone()[2]
        def prepare(ident):
            store=IdentityStore(filename)
            try:return SenderStreamSource(store,self.f.binary,configured=True).prepare(self.stream,ident,time=self.time)
            finally:store.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            packets=[decode_event(raw)['value'] for raw in pool.map(prepare,('a'*32,'b'*32))]
        self.assertNotEqual(packets[0]['predecessor'],packets[1]['predecessor'])
        self.assertTrue(packets[0]['result']==packets[1]['predecessor'] or packets[1]['result']==packets[0]['predecessor'])
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM stream_source_outbox').fetchone()[0],2)

    def test_real_process_exit_preserves_atomic_checkpoint_and_outbox(self):
        filename=self.identity.db.execute('PRAGMA database_list').fetchone()[2]
        script="""import json,os,sys
from identity_store import IdentityStore
from sender_stream_source import SenderStreamSource
s=IdentityStore(sys.argv[1]);source=SenderStreamSource(s,sys.argv[2],configured=True)
source.prepare(sys.argv[3],sys.argv[4],time=json.loads(sys.argv[5]),crash=lambda stage:os._exit(23) if stage==sys.argv[6] else None)
"""
        before=self.source._live(self.stream)[1]
        for point in ('before-commit','after-commit'):
            child=subprocess.run([sys.executable,'-c',script,filename,str(self.f.binary),self.stream,'e'*32,json.dumps(self.time),point],capture_output=True,timeout=20)
            self.assertEqual(child.returncode,23)
            self.assertEqual(child.stdout,b'')
            rows=self.identity.db.execute('SELECT wire FROM stream_source_outbox').fetchall()
            if point=='before-commit':
                self.assertEqual(rows,[]);self.assertEqual(self.source._live(self.stream)[1],before)
            else:
                self.assertEqual(len(rows),1);self.assertEqual(self.send('e'*32),rows[0][0])
                self.assertEqual(decode_event(self.send('f'*32))['value']['predecessor'],decode_event(rows[0][0])['value']['result'])

    def test_known_recipient_revocation_holds_new_source_output(self):
        recipient=self.peer
        bundle=json.loads(json.dumps(self.f.bundles[recipient['principal']]))
        state=json.loads(base64.b64decode(bundle['states'][0]['payload']))
        state.update(record='9'*32,revision='2',previous=[self.f.heads[recipient['principal']]],revoked=[recipient['device']],bindings=[b for b in state['bindings'] if b['device']!=recipient['device']])
        payload=encode_event(state)
        bundle['states'].insert(0,dict(payload=base64.b64encode(payload).decode(),signature=sign(self.f.binary,self.f.creator,'email-next/identity-state/v0',payload)))
        self.assertEqual(self.identity.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(payload).hexdigest(),time=self.time)['status'],'accepted-unverified')
        before=self.source._live(self.stream)[1]
        with self.assertRaisesRegex(ValueError,'authority held'):self.send('c'*32,application=self.event('c'*32))
        self.assertEqual(self.source._live(self.stream)[1],before)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM stream_source_outbox').fetchone()[0],0)

    def test_authority_expiring_during_work_rolls_back_preparation(self):
        before=self.source._live(self.stream)[1]
        with patch('sender_stream_source.elapsed_time.monotonic_ns',side_effect=[0,4000*1000000000]):
            with self.assertRaisesRegex(ValueError,'authority held'):self.send('d'*32,application=self.event('d'*32))
        self.assertEqual(self.source._live(self.stream)[1],before)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM stream_source_outbox').fetchone()[0],0)

    def test_stricter_verification_policy_cannot_be_bypassed_by_source(self):
        before=self.source._live(self.stream)[1]
        self.sender.configure(expected_revision=1,trust_policy='require-verification')
        with self.assertRaisesRegex(ValueError,'verification policy'):self.send('9'*32,application=self.event('9'*32))
        self.assertEqual(self.source._live(self.stream)[1],before)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM stream_source_outbox').fetchone()[0],0)

    def test_changed_audience_or_owner_and_bad_reply_do_not_consume_state(self):
        before=self.source._live(self.stream)[1]
        for changes in (dict(principal=next(d['principal'] for d in self.f.devices if d['principal'] != self.f.creator['principal'])),dict(audience=[self.f.creator['principal']]),dict(operation=dict(kind='message',text='Reply',replyTo=[dict(principal=self.peer['principal'],conversation=self.f.context['conversation'],event='8'*32)]))):
            event=json.loads(self.event('d'*32));event.update(changes)
            with self.assertRaises(ValueError):self.send('8'*32,application=encode_event(event))
            self.assertEqual(self.source._live(self.stream)[1],before)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM stream_source_outbox').fetchone()[0],0)


if __name__=='__main__':unittest.main()
