import base64
import hashlib
import json
import unittest
import test_group_transitions as fixture
from event_encoding import encode_event
from provider_mls import call,sign
from commit_history import CommitHistory
from sender_release import SenderRelease

class RemovalTests(unittest.TestCase):
    setUp=fixture.GroupTransitionTests.setUp
    tearDown=fixture.GroupTransitionTests.tearDown
    store=fixture.GroupTransitionTests.store
    prepared=fixture.GroupTransitionTests.prepared
    def remove(self,device):
        ident=self.ga.prepare_removal([{'identity':device['identity'],'key':device['key']}]);self.ga.decide(ident,allowed=set(),time=self.time)
        return json.loads(self.ga.db.execute('SELECT state FROM gt_decision WHERE digest=?',(ident,)).fetchone()[0])
    def add_phone(self):
        ident=self.prepared();self.ga.decide(ident,allowed=self.allowed,time=self.time)
        result=json.loads(self.ga.db.execute('SELECT state FROM gt_decision WHERE digest=?',(ident,)).fetchone()[0])
        self.assertEqual(self.gb.receive(bytes.fromhex(result['wire']),allowed=self.allowed,time=self.time),'accepted')
        return result
    def revoke_phone(self):
        bundle=json.loads(json.dumps(self.bundle));state=json.loads(base64.b64decode(bundle['states'][0]['payload']))
        state.update(record='9'*32,revision='2',previous=[self.head],revoked=[self.phone['device']],bindings=[r for r in state['bindings'] if r['device']!=self.phone['device']])
        raw=encode_event(state);bundle['states'].insert(0,{'payload':base64.b64encode(raw).decode(),'signature':sign(self.provider,self.a,'email-next/identity-state/v0',raw)})
        self.assertEqual(self.ga.identity.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(raw).hexdigest(),time=self.time)['status'],'accepted-unverified')
    def test_signed_revocation_holds_app_but_allows_removal(self):
        self.add_phone();self.revoke_phone();sender=SenderRelease(self.ga.identity,self.provider)
        current=self.ga.live();metadata=call(self.provider,op='inspect-send',checkpoint=current['checkpoint'],group=current['snapshot']['group'],key=self.a['key'])['metadata']
        self.ga.db.execute('BEGIN IMMEDIATE')
        try:
            with self.assertRaises(ValueError):sender._authority(metadata,self.time,'allow-unverified')
        finally:self.ga.db.execute('ROLLBACK')
        result=self.remove(self.phone)
        self.assertNotIn(self.phone['identity'],[m['identity'] for m in result['after']['members']])
        self.assertEqual(self.gb.receive(bytes.fromhex(result['wire']),allowed=set(),time=self.time),'accepted')
    def test_removed_endpoint_inactive_and_new_ciphertext_unavailable(self):
        result=self.remove(self.c)
        staged=self.gc.invoke('receive',self.gc.live(),wire=result['wire'])
        self.assertTrue(staged['selfRemoved'])
        self.assertEqual({k for k in result['after'] if result['after'][k]!=staged['after'][k]},{'predecessor'})
        self.assertEqual(self.gc.receive(bytes.fromhex(result['wire']),allowed=set(),time=self.time),'accepted')
        terminal=json.loads(self.gc.db.execute('SELECT snapshot FROM mls_group_inactive').fetchone()[0])
        self.assertEqual({k:terminal[k] for k in ('group','epoch','context','members')},{k:result['after'][k] for k in ('group','epoch','context','members')})
        self.assertNotIn('predecessor',terminal)
        self.assertEqual(self.gc.db.execute('SELECT count(*) FROM gt_decision').fetchone()[0],0)
        with self.assertRaisesRegex(ValueError,'Inactive'):self.gc.live()
        self.assertEqual(self.gc.receive(bytes.fromhex(result['wire']),allowed=set(),time=self.time),'accepted')
        self.assertEqual(self.gc.receiver.receive(b'anything',time=self.time,trust_policy='allow-unverified')['status'],'inactive-group')
        state=self.ga.live();app=dict(version='0',purpose='contribution',event='e'*32,conversation='2'*32,principal=self.a['principal'],audience=sorted([self.a['principal'],self.b['principal']]),operation=dict(kind='message',text='After removal',replyTo=[]))
        sent=call(self.provider,op='send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.a['key'],application=encode_event(app).hex())
        from mls_receive import worker_call,FORMAT
        cp=self.gc.db.execute('SELECT group_id,snapshot FROM mls_checkpoint').fetchone()
        self.assertNotEqual(worker_call(self.provider.with_name('receive-staged'),dict(format=FORMAT,group=cp[0],checkpoint=json.loads(cp[1]),wire=sent['wire']))['status'],'authenticated-application')
    def test_exact_targets_and_writer_cannot_be_removed(self):
        for target in [dict(identity=self.a['identity'],key=self.a['key']),dict(identity=self.b['identity'],key=self.c['key'])]:
            with self.assertRaises(ValueError):self.ga.prepare_removal([target])
    def test_survivor_history_crosses_revoked_member_removal(self):
        h=CommitHistory(self.ga,max_count=8,max_bytes=4000000);start=self.ga.live()['snapshot']['predecessor']
        self.add_phone();self.revoke_phone();self.remove(self.phone)
        path=h.path(start,target_identity=self.b['identity'],target_key=self.b['key'],time=self.time,trust_policy='allow-unverified')
        self.assertEqual(len(path['steps']),2)
        self.assertTrue(all('authorization' in step['record'] for step in path['steps']))
        with self.assertRaisesRegex(ValueError,'not current'):h.path(start,target_identity=self.phone['identity'],target_key=self.phone['key'],time=self.time,trust_policy='allow-unverified')

    def test_pending_membership_only_removal_cannot_promote(self):
        audience=sorted([self.a['principal'],self.b['principal'],self.c['principal']])
        base=dict(version='0',purpose='contribution',event='6'*32,conversation='2'*32,principal=self.c['principal'],audience=audience)
        answer=dict(base,operation=dict(kind='answer',question=dict(principal=self.c['principal'],conversation='2'*32,event='5'*32),option='7'*32,replaces=[]))
        state=self.gc.live();sent=call(self.provider,op='send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.c['key'],application=encode_event(answer).hex())
        self.assertEqual(self.ga.receiver.receive(bytes.fromhex(sent['wire']),time=self.time,trust_policy='allow-unverified')['status'],'pending')
        result=self.remove(self.c)
        # Account authority is still valid: membership removal alone is decisive.
        self.assertEqual(self.ga.identity.check_device(bytes.fromhex(self.c['identity']),bytes.fromhex(self.c['key']),role='send',time=self.time,trust_policy='allow-unverified')['status'],'authorized-unverified')
        from unittest.mock import patch
        with patch('mls_receive.worker_call',side_effect=AssertionError('No re-decryption')):
            reevaluated=self.ga.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')
        self.assertEqual(list(reevaluated['states'].values()),['held:membership-episode'])
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM contributions').fetchone()[0],0)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM derived_views').fetchone()[0],0)

    def test_removal_crash_rolls_back_episodes_and_exact_retry(self):
        ident=self.ga.prepare_removal([dict(identity=self.c['identity'],key=self.c['key'])]);before=self.ga.live()
        def fail(point):
            if point=='before-commit':raise RuntimeError('crash')
        with self.assertRaises(RuntimeError):self.ga.decide(ident,allowed=set(),time=self.time,crash=fail)
        self.assertEqual(self.ga.live(),before)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM mls_membership_episode WHERE end_epoch IS NOT NULL').fetchone()[0],0)
        self.ga.decide(ident,allowed=set(),time=self.time);self.ga.decide(ident,allowed=set(),time=self.time)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM mls_membership_episode WHERE end_epoch IS NOT NULL').fetchone()[0],1)
    def test_previously_accepted_message_remains_history_after_removal(self):
        app=dict(version='0',purpose='contribution',event='a'*32,conversation='2'*32,principal=self.c['principal'],audience=sorted([self.a['principal'],self.b['principal'],self.c['principal']]),operation=dict(kind='message',text='Already accepted',replyTo=[]))
        state=self.gc.live();sent=call(self.provider,op='send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.c['key'],application=encode_event(app).hex())
        self.assertEqual(self.ga.receiver.receive(bytes.fromhex(sent['wire']),time=self.time,trust_policy='allow-unverified')['status'],'projected-context-matched')
        self.remove(self.c);self.ga.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')
        self.assertEqual(self.ga.db.execute('SELECT state FROM mls_application_acceptance').fetchone()[0],'accepted')
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM contributions').fetchone()[0],1)

    def test_survivor_actual_historical_dispatch_across_removal(self):
        from historical_release import HistoricalRelease
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        from transition_carrier import receive_mime
        h=CommitHistory(self.ga,max_count=8,max_bytes=4000000);start=self.ga.live()['snapshot']['predecessor']
        self.remove(self.c)
        later=self.ga.prepare([]);self.ga.decide(later,allowed=set(),time=self.time)
        sender=SenderRelease(self.ga.identity,self.provider);sender.configure(expected_revision=0)
        adapter=HistoricalRelease(sender,h)
        items=adapter.prepare('removalcatchup',start,key=self.a['key'],target_identity=self.b['identity'],target_key=self.b['key'],mailbox='bob@example.invalid',envelope_sender='alice@example.invalid',time=self.time)
        with SenderWorker(sender) as worker:
            for item in items:
                server=LocalSMTP();self.assertEqual(worker.submit_historical(item,history=h,port=server.port,time=self.time)['state'],'accepted');server.done()
                self.assertEqual(receive_mime(self.gb,server.wire,allowed=set(),time=self.time),'accepted')
        self.assertEqual(self.gb.live()['snapshot']['predecessor'],self.ga.live()['snapshot']['predecessor'])

    def test_missing_configured_episode_requires_migration(self):
        import membership_episodes as episodes
        group=self.ga.live()['snapshot']['group']
        self.ga.db.execute('DELETE FROM mls_membership_episode')
        self.assertFalse(episodes.permits(self.ga.db,group,self.a['identity'],self.a['key'],'1'))
        with self.assertRaisesRegex(ValueError,'migration'):self.ga.live()
