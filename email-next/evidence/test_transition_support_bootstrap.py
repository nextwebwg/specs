import json
import unittest
from unittest.mock import patch
import test_established_application as fixtures
from test_sender_release import LocalSMTP
from sender_worker import SenderWorker
from identity_store import IdentityStore
from established_invitation import EstablishedAdmission
from established_invitation_mime import select
from event_encoding import encode_event
from group_transitions import GroupTransitions
from provider_mls import call
from transition_support import TransitionSupport,bootstrap_established_locked
from transition_carrier import receive_mime

class EstablishedBootstrapTests(unittest.TestCase):
    application_profile=fixtures.EstablishedApplicationTests.application_profile
    setUp=fixtures.EstablishedApplicationTests.setUp
    tearDown=fixtures.EstablishedApplicationTests.tearDown
    store=fixtures.EstablishedApplicationTests.store
    prepared=fixtures.EstablishedApplicationTests.prepared
    def assertion(self,device,*,expires=None):
        return fixtures.EstablishedApplicationTests.assertion(self,device,expires=expires or str(int(self.time['latest'])+30))
    setup_delivery=fixtures.EstablishedApplicationTests.setup_delivery
    def admitted(self):
        route=self.setup_delivery()
        with SenderWorker(self.sender) as worker:
            commit=LocalSMTP();worker.submit_control('commit',port=commit.port,time=self.time);commit.done()
            for g in [self.gb,self.gc]:receive_mime(g,commit.wire,allowed=self.allowed,time=self.time)
            mail=LocalSMTP();worker.submit_established_invitation('welcome',history=self.history,port=mail.port,time=self.time);mail.done()
        identity=IdentityStore(self.root/'bootstrap.sqlite');self.stores.append(identity)
        for peer in [self.a,self.b,self.c]:identity.observe(peer['record'],first_contact_policy='allow-unverified')
        identity.accept_successor(encode_event(self.bundle),candidate_digest=self.head,time=self.time)
        admission=EstablishedAdmission(identity,self.provider);admission.publish_local(self.phone)
        result=admission.accept_message(select(mail.wire),target=self.phone,mailbox=route['mailbox'],allow_creator=self.a['principal'],expected_context=self.ctx,time=self.time)
        group=GroupTransitions(identity,self.binary,self.phone);TransitionSupport(group)
        return group,result
    def test_actual_admission_then_add_reuses_proofs_without_member_confirmation(self):
        g,result=self.admitted()
        self.time={k:str(int(v)+31) for k,v in self.time.items()}
        old_period=g.db.execute('SELECT admission FROM mls_membership_episode WHERE identity=? AND end_epoch IS NULL',(self.c['identity'],)).fetchone()[0]
        pending=dict(version='1',purpose='contribution',event='d'*32,conversation='2'*32,principal=self.c['principal'],audience=sorted([self.a['principal'],self.b['principal'],self.c['principal']]),disclosures=[],operation=dict(kind='answer',question=dict(principal=self.c['principal'],conversation='2'*32,event='e'*32),option='f'*32,replaces=[]))
        state=self.gc.live();sent=call(self.provider,op='send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.c['key'],application=encode_event(pending).hex())
        self.assertEqual(g.receiver.receive(bytes.fromhex(sent['wire']),time=self.time,trust_policy='allow-unverified')['status'],'pending')
        removal=self.ga.prepare_removal([dict(identity=self.c['identity'],key=self.c['key'])],time=self.time);self.ga.decide(removal,allowed=set(),time=self.time)
        record=json.loads(self.ga.db.execute('SELECT state FROM gt_decision WHERE digest=?',(removal,)).fetchone()[0])
        self.assertEqual(g.receive(bytes.fromhex(record['wire']),allowed=set(),time=self.time),'accepted')
        fresh=dict(self.c,**call(self.provider,op='fresh-package',checkpoint=self.c['checkpoint'],key=self.c['key'],identity=self.c['identity']))
        proof=self.assertion(fresh)
        TransitionSupport(self.ga).confirm(proof,time=self.time);TransitionSupport(g).confirm(proof,time=self.time)
        decision=self.ga.prepare([fresh['package']]);self.ga.decide(decision,allowed={(fresh['identity'],fresh['key'])},time=self.time)
        record=json.loads(self.ga.db.execute('SELECT state FROM gt_decision WHERE digest=?',(decision,)).fetchone()[0])
        with patch.object(TransitionSupport,'confirm',side_effect=AssertionError('No manual member confirmation')):
            self.assertEqual(g.receive(bytes.fromhex(record['wire']),allowed={(fresh['identity'],fresh['key'])},time=self.time),'accepted')
        records=[json.loads(r[0]) for r in g.db.execute('SELECT record FROM mls_support_records')]
        historical=[r for r in records if r['kind']=='signed-established-admission']
        self.assertEqual(len(historical),3)
        new_period=g.db.execute('SELECT admission FROM mls_membership_episode WHERE identity=? AND end_epoch IS NULL',(self.c['identity'],)).fetchone()[0]
        self.assertNotEqual(new_period,old_period)
        self.assertEqual(new_period,decision)
        self.assertIn('held:membership-episode',g.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')['states'].values())
        self.assertTrue(all(r['instance']==result['instance'] and 'time' not in r for r in historical))
    def test_changed_key_profile_and_fixed_roster_context_rejected(self):
        g,_=self.admitted();before=g.live()['snapshot'];member=before['members'][0]
        g.db.execute('BEGIN IMMEDIATE')
        try:
            with self.assertRaises(ValueError):bootstrap_established_locked(g.db,before,dict(member,key='f'*64))
            context=json.loads(bytes.fromhex(before['context']));context['application']=dict(envelopeVersion='1',operations=['message'])
            with self.assertRaisesRegex(ValueError,'context'):bootstrap_established_locked(g.db,dict(before,context=encode_event(context).hex()),member)
            context['ordering']={'kind':'fixed-roster-v0'}
            with self.assertRaisesRegex(ValueError,'designated'):bootstrap_established_locked(g.db,dict(before,context=encode_event(context).hex()),member)
        finally:g.db.execute('ROLLBACK')
    def test_removed_member_evidence_cannot_bootstrap_again(self):
        g,_=self.admitted();before=g.live()['snapshot'];member=next(m for m in before['members'] if m['identity']==self.c['identity'])
        removal=self.ga.prepare_removal([dict(identity=self.c['identity'],key=self.c['key'])],time=self.time);self.ga.decide(removal,allowed=set(),time=self.time)
        record=json.loads(self.ga.db.execute('SELECT state FROM gt_decision WHERE digest=?',(removal,)).fetchone()[0]);g.receive(bytes.fromhex(record['wire']),allowed=set(),time=self.time)
        g.db.execute('BEGIN IMMEDIATE')
        try:
            with self.assertRaisesRegex(ValueError,'episode'):bootstrap_established_locked(g.db,g.live()['snapshot'],member)
        finally:g.db.execute('ROLLBACK')
    def test_inactive_local_instance_cannot_supply_surviving_member_proof(self):
        g,_=self.admitted()
        removal=self.ga.prepare_removal([dict(identity=self.phone['identity'],key=self.phone['key'])],time=self.time);self.ga.decide(removal,allowed=set(),time=self.time)
        record=json.loads(self.ga.db.execute('SELECT state FROM gt_decision WHERE digest=?',(removal,)).fetchone()[0]);g.receive(bytes.fromhex(record['wire']),allowed=set(),time=self.time)
        g.db.execute('BEGIN IMMEDIATE')
        try:
            with self.assertRaisesRegex(ValueError,'instance ended'):bootstrap_established_locked(g.db,record['before'],next(m for m in record['before']['members'] if m['identity']==self.a['identity']))
        finally:g.db.execute('ROLLBACK')
