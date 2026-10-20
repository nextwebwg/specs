import json
import unittest
import test_group_transitions as fixtures
from commit_history import CommitHistory
from transition_carrier import encode_transition,receive_mime
from transition_mime import package

class CommitHistoryTests(unittest.TestCase):
    setUp=fixtures.GroupTransitionTests.setUp
    tearDown=fixtures.GroupTransitionTests.tearDown
    store=fixtures.GroupTransitionTests.store
    prepared=fixtures.GroupTransitionTests.prepared
    def history(self,count=8,size=4000000):return CommitHistory(self.ga,max_count=count,max_bytes=size)
    def chain(self):
        start=self.ga.live()['snapshot']['predecessor'];first=self.prepared();self.ga.decide(first,allowed=self.allowed,time=self.time)
        second=self.ga.prepare([]);self.ga.decide(second,allowed=set(),time=self.time)
        return start,[first,second]
    def path(self,h,start,device=None):
        device=device or self.b
        return h.path(start,target_identity=device['identity'],target_key=device['key'],time=self.time,trust_policy='allow-unverified')
    def test_actual_two_epoch_catchup_uses_public_records_not_old_snapshots(self):
        h=self.history();start,decisions=self.chain()
        # Simulate retirement of old rich experiment rows; retain only current
        # crypto checkpoint and the minimized accepted public decision ledger.
        for table in ['gt_candidate','gt_outbox','gt_decision']:self.ga.db.execute('DELETE FROM '+table)
        plan=self.path(h,start);self.assertEqual([s['decision'] for s in plan['steps']],decisions)
        for step in plan['steps']:
            self.assertEqual(set(step['record']),{'before','after','sender','wire','authorization'})
            raw=package(encode_transition(step['record']),sender='alice@example.invalid',recipient='bob@example.invalid')
            self.assertEqual(receive_mime(self.gb,raw,allowed=self.allowed,time=self.time),'accepted')
            self.assertEqual(receive_mime(self.gb,raw,allowed=set(),time=self.time),'accepted')
        self.assertEqual(self.gb.live()['snapshot']['predecessor'],plan['tip'])
        self.assertFalse(plan['sendAuthorized'])
        from event_encoding import encode_event
        from provider_mls import call
        application={'version':'0','purpose':'contribution','event':'d'*32,'conversation':'2'*32,'principal':self.a['principal'],'audience':sorted([self.a['principal'],self.b['principal'],self.c['principal']]),'operation':{'kind':'message','text':'After catch-up','replyTo':[]}}
        current=self.ga.live();sent=call(self.provider,op='send',checkpoint=current['checkpoint'],group=current['snapshot']['group'],key=self.a['key'],application=encode_event(application).hex())
        self.assertEqual(self.gb.receiver.receive(bytes.fromhex(sent['wire']),time=self.time,trust_policy='allow-unverified')['status'],'projected-context-matched')
    def test_future_control_keeps_original_binding_until_missing_link_arrives(self):
        h=self.history();start,_=self.chain();steps=self.path(h,start)['steps'];wires=[package(encode_transition(s['record']),sender='alice@example.invalid',recipient='bob@example.invalid') for s in steps]
        self.assertEqual(receive_mime(self.gb,wires[1],allowed=set(),time=self.time),'pending')
        self.assertEqual(receive_mime(self.gb,wires[0],allowed=self.allowed,time=self.time),'accepted')
        self.assertEqual(receive_mime(self.gb,wires[1],allowed=set(),time=self.time),'accepted')
    def test_new_joiner_cannot_use_current_membership_for_predecessor_history(self):
        h=self.history();start,_=self.chain()
        with self.assertRaisesRegex(ValueError,'continuously'):self.path(h,start,self.phone)
    def test_missing_path_and_strict_policy_hold(self):
        h=self.history();start,decisions=self.chain();h.prune(decisions[0])
        with self.assertRaisesRegex(ValueError,'unavailable'):self.path(h,start)
        with self.assertRaisesRegex(ValueError,'Verification'):h.path(start,target_identity=self.b['identity'],target_key=self.b['key'],time=self.time,trust_policy='require-verification')
    def test_budget_pressure_never_discards_pinned_uncertain_history(self):
        h=self.history(count=1);start=self.ga.live()['snapshot']['predecessor'];first=self.prepared();self.ga.decide(first,allowed=self.allowed,time=self.time)
        self.ga.db.execute('BEGIN IMMEDIATE');h.pin_locked('plan1',[first],state='uncertain');self.ga.db.execute('COMMIT')
        before=self.ga.live();second=self.ga.prepare([])
        with self.assertRaisesRegex(ValueError,'retention budget'):self.ga.decide(second,allowed=set(),time=self.time)
        self.assertEqual(self.ga.live(),before)
        with self.assertRaisesRegex(ValueError,'uncertain'):h.prune(first)
        self.assertEqual(len(self.path(h,start)['steps']),1)
    def test_unaccepted_candidate_is_not_history(self):
        h=self.history();start=self.ga.live()['snapshot']['predecessor'];self.prepared()
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM commit_history').fetchone()[0],0)
        self.assertEqual(self.path(h,start)['steps'],[])
    def test_exact_decision_retry_keeps_one_minimized_record(self):
        h=self.history();first=self.prepared();self.ga.decide(first,allowed=self.allowed,time=self.time);self.ga.decide(first,allowed=self.allowed,time=self.time)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM commit_history').fetchone()[0],1)

    def test_current_committer_role_loss_holds_retained_history(self):
        h=self.history();start,_=self.chain()
        fixtures.GroupTransitionTests.strip_committer_send(self,self.ga.identity)
        with self.assertRaisesRegex(ValueError,'committer send'):self.path(h,start)
    def test_current_roster_revocation_holds_history_for_other_target(self):
        import base64,hashlib
        from event_encoding import encode_event
        from provider_mls import sign
        h=self.history();start,_=self.chain();bundle=json.loads(json.dumps(self.bundle))
        state=json.loads(base64.b64decode(bundle['states'][0]['payload']))
        state.update(record='9'*32,revision='2',previous=[self.head],revoked=[self.phone['device']],bindings=[r for r in state['bindings'] if r['device']!=self.phone['device']])
        raw=encode_event(state);bundle['states'].insert(0,{'payload':base64.b64encode(raw).decode(),'signature':sign(self.provider,self.a,'email-next/identity-state/v0',raw)})
        self.assertEqual(self.ga.identity.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(raw).hexdigest(),time=self.time)['status'],'accepted-unverified')
        with self.assertRaisesRegex(ValueError,'Current identity'):self.path(h,start)
    def test_restart_reconstructs_exact_public_path(self):
        from identity_store import IdentityStore
        from group_transitions import GroupTransitions
        h=self.history();start,decisions=self.chain();identity=IdentityStore(self.root/'a.sqlite')
        try:
            resumed=CommitHistory(GroupTransitions(identity,self.binary,self.a),max_count=8,max_bytes=4000000)
            self.assertEqual([s['decision'] for s in self.path(resumed,start)['steps']],decisions)
        finally:identity.close()
    def test_byte_budget_rejects_atomically_without_installing_decision(self):
        self.history(size=1);before=self.ga.live();first=self.prepared()
        with self.assertRaisesRegex(ValueError,'retention budget'):self.ga.decide(first,allowed=self.allowed,time=self.time)
        self.assertEqual(self.ga.live(),before)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM gt_decision').fetchone()[0],0)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM gt_outbox').fetchone()[0],0)
