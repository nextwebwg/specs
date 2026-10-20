import base64
import json
import unittest
from unittest.mock import patch
import test_initial_roster_lifecycle as fixtures
from provider_mls import make_device,advertisement,sign
from event_encoding import encode_event
from group_transitions import GroupTransitions
from transition_support import TransitionSupport
from commit_history import CommitHistory
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from initial_roster import parse
from initial_roster_lifecycle import InitialRosterAdmission
from invitation_mime import select
from historical_release import HistoricalRelease
from transition_carrier import receive_mime

class RosterCatchupTests(unittest.TestCase):
    setUp=fixtures.RosterLifecycleTests.setUp
    tearDown=fixtures.RosterLifecycleTests.tearDown
    endpoint=fixtures.RosterLifecycleTests.endpoint
    prepare=fixtures.RosterLifecycleTests.prepare
    def exercise(self,*,cancel_uncertain=False,extend_before_data=False):
        wires=self.prepare();ident,wire=next(iter(wires.items()));p=parse(select(wire));target=next(d for d in self.f.devices if d['identity']==self.identity.db.execute('SELECT target FROM initial_roster_prepared WHERE id=?',(ident,)).fetchone()[0])
        ga=GroupTransitions(self.identity,self.f.binary.with_name('group-transitions'),self.f.creator);history=CommitHistory(ga,max_count=8,max_bytes=4000000);initial=ga.live()['snapshot']['predecessor']
        new=make_device(self.f.binary,7,8);self.identity.observe(new['record'],first_contact_policy='allow-unverified')
        wrapper=advertisement(self.f.binary,new,'new@example.invalid');value=json.loads(base64.b64decode(wrapper['payload']));value.update(version='3' if self.f.context['version']=='4' else '2',applications=[dict(self.f.context['application'],ordering='designated-member-v0')]);raw=encode_event(value);wrapper.update(payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,new,'email-next/passive-discovery/v'+value['version'],raw))
        TransitionSupport(ga).confirm(encode_event(wrapper),time=self.time)
        with patch.object(TransitionSupport,'confirm',side_effect=AssertionError('No original-member reconfirmation')):
            decision=ga.prepare([new['package']]);self.assertEqual(ga.decide(decision,allowed={(new['identity'],new['key'])},time=self.time),'accepted')
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mls_support_records WHERE cast(record AS TEXT) LIKE ?',('%signed-initial-roster%',)).fetchone()[0],6)
        localroute=self.selected[self.f.devices.index(target)];route=dict(mailbox=localroute['mailbox'],generation=localroute['generation'],principal=target['principal'],observation=localroute['digest'])
        catchup=HistoricalRelease(self.sender,history);items=catchup.prepare('latecatchup',initial,key=self.f.creator['key'],target_identity=target['identity'],target_key=target['key'],mailbox=localroute['mailbox'],envelope_sender=self.selected[0]['mailbox'],time=self.time,association_targets=[route]);self.assertEqual(len(items),1)
        with SenderWorker(self.sender) as worker:
            with patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('Ordinary initial must hold advanced epoch')):
                with self.assertRaisesRegex(ValueError,'Changed group metadata'):worker.submit_initial_roster(ident,port=1,time=self.time)
            def hook(stage):
                if stage=='after-release' and extend_before_data:
                    update=ga.prepare([]);self.assertEqual(ga.decide(update,allowed=set(),time=self.time),'accepted')
            smtp=LocalSMTP(drop=cancel_uncertain);outcome=worker.submit_initial_roster_late(ident,history,catchup_plan='latecatchup',port=smtp.port,time=self.time,crash=hook);smtp.done()
            if extend_before_data:
                self.assertEqual(outcome['state'],'aborted-before-data');self.assertIsNone(smtp.wire);return
            self.assertEqual(smtp.wire,wire)
            if cancel_uncertain:
                self.assertEqual(outcome['state'],'uncertain')
                with self.assertRaisesRegex(ValueError,'Initial roster handoff incomplete'):catchup.finish_plan('latecatchup',worker=worker)
                self.assertEqual(catchup.finish_plan('latecatchup',worker=worker,cancel=True),'cancelled-uncertain')
                archived=json.loads(self.identity.db.execute("SELECT archive FROM historical_plans WHERE id='latecatchup'").fetchone()[0])
                self.assertEqual(archived['initialMessages'],[dict(delivery=ident,wire=wire.hex())]);self.assertTrue(archived['possibleEarlierDelivery']);self.assertEqual(len(archived['records']),1)
                self.assertEqual(self.identity.db.execute('SELECT count(*) FROM commit_history_pin').fetchone()[0],0)
                with patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('Cancelled catch-up cannot release')):
                    with self.assertRaisesRegex(ValueError,'Active retained catch-up'):worker.submit_initial_roster_late(ident,history,catchup_plan='latecatchup',port=1,time=self.time,retry_uncertain=True)
                return
            self.assertEqual(outcome['state'],'accepted')
        identity,sender,selected=self.endpoint('late');identity.observe(new['record'],first_contact_policy='allow-unverified');admission=InitialRosterAdmission(identity,self.f.binary);admission.publish_local(target)
        choices=[dict(principal=d['principal'],device=d['device'],mailbox=c['mailbox'],generation=c['generation']) for d,c in zip(self.f.devices,selected)]
        result=admission.accept_message(select(wire),target=target,mailbox=p['value']['target']['mailbox'],allow_creator=self.f.creator['principal'],intended_principals=self.principals,intended_devices=self.devices,expected_context=encode_event(self.f.context),selections=choices,time=self.time,trust_policy='allow-unverified');self.assertEqual(result['status'],'admitted-unverified')
        gb=GroupTransitions(identity,self.f.binary.with_name('group-transitions'),target);self.assertEqual(gb.live()['snapshot']['epoch'],'1');TransitionSupport(gb).confirm(encode_event(wrapper),time=self.time)
        with SenderWorker(self.sender) as worker:
            smtp=LocalSMTP();self.assertEqual(worker.submit_historical(items[0],history=history,port=smtp.port,time=self.time)['state'],'accepted');smtp.done();self.assertEqual(receive_mime(gb,smtp.wire,allowed={(new['identity'],new['key'])},time=self.time),'accepted')
            self.assertEqual(catchup.finish_plan('latecatchup',worker=worker),'completed')
        self.assertEqual(gb.live()['snapshot'],ga.live()['snapshot'])

    def test_original_roster_add_late_welcome_then_exact_commit(self):self.exercise()
    def test_uncertain_late_welcome_cancellation_archives_exact_public_path(self):self.exercise(cancel_uncertain=True)
    def test_tip_extension_before_data_holds_original_welcome(self):self.exercise(extend_before_data=True)
    def test_original_proof_reuse_rejects_changed_key_profile_and_ended_episode(self):
        from initial_roster_support import bootstrap_locked
        self.prepare();g=GroupTransitions(self.identity,self.f.binary.with_name('group-transitions'),self.f.creator);TransitionSupport(g)
        before=g.live()['snapshot'];member=next(m for m in before['members'] if m['identity']!=self.f.creator['identity'])
        altered=json.loads(bytes.fromhex(before['context']));altered['application']['operations']=['question']
        for snapshot,candidate in [(before,dict(member,key='ff'*32)),(dict(before,context=encode_event(altered).hex()),member)]:
            self.identity.db.execute('BEGIN IMMEDIATE')
            try:
                with self.assertRaises(ValueError):bootstrap_locked(self.identity.db,snapshot,candidate)
            finally:self.identity.db.execute('ROLLBACK')
        removal=g.prepare_removal([dict(identity=member['identity'],key=member['key'])]);self.assertEqual(g.decide(removal,allowed=set(),time=self.time),'accepted')
        self.identity.db.execute('BEGIN IMMEDIATE')
        try:
            with self.assertRaisesRegex(ValueError,'current support episode'):bootstrap_locked(self.identity.db,before,member)
        finally:self.identity.db.execute('ROLLBACK')
