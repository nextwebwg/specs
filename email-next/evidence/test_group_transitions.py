"""Actual MLS transitions under configured endpoint ordering, not consensus."""
import base64
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import tempfile
import unittest
from provider_mls import make_device,call,sign
from identity_store import IdentityStore
from event_encoding import encode_event
from group_transitions import GroupTransitions


def crash_run(path,binary,device,action,value,allowed,time,point):
    identity=IdentityStore(path);g=GroupTransitions(identity,binary,device)
    def crash(where):
        if where==point:os._exit(91)
    getattr(g,action)(value,allowed=allowed,time=time,crash=crash)
    os._exit(92)


def enroll(binary,a,phone):
    previous=base64.b64decode(a['record']['state']);state=json.loads(previous)
    b=json.loads(base64.b64decode(phone['record']['binding']));b.update(record='7'*32,authority={'kind':'state','digest':a['state']});binding=encode_event(b)
    nxt=dict(state,record='8'*32,revision='1',previous=[a['state']],bindings=sorted(state['bindings']+[{'device':phone['device'],'digest':hashlib.sha256(binding).hexdigest()}],key=lambda x:x['device']))
    payload=encode_event(nxt)
    return {'version':'0','purpose':'identity-bundle','principal':a['principal'],
      'states':[{'payload':base64.b64encode(payload).decode(),'signature':sign(binary,a,'email-next/identity-state/v0',payload)},
                {'payload':a['record']['state'],'signature':a['record']['stateProof']}],
      'bindings':[{'payload':base64.b64encode(binding).decode(),'authorization':sign(binary,a,'email-next/device-binding/v0',binding),'possession':sign(binary,phone,'email-next/device-possession/v0',binding)},
                  {'payload':a['record']['binding'],'authorization':a['record']['authorization'],'possession':a['record']['possession']}]},hashlib.sha256(payload).hexdigest()


class GroupTransitionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.provider=Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR'])/'provider-mls';self.binary=self.provider.with_name('group-transitions')
        self.a=make_device(self.provider,1,2);self.b=make_device(self.provider,3,4);self.c=make_device(self.provider,5,6);self.phone=make_device(self.provider,1,7)
        self.time={'earliest':str(self.a['time']),'latest':str(self.a['time'])};self.bundle,self.head=enroll(self.provider,self.a,self.phone)
        self.ctx=encode_event(dict(version='1',purpose='conversation-context',conversation='2'*32,profile='mls-1-0001',administrators=sorted([self.a['principal'],self.b['principal']]),ordering=dict(kind='designated-member-v0',principal=self.a['principal'],device=self.a['device'])))
        if hasattr(self,'application_profile'):
            context=json.loads(self.ctx);context.update(version='2',application=self.application_profile);self.ctx=encode_event(context)
        created=call(self.binary,op='create',checkpoint=self.a['checkpoint'],key=self.a['key'],identity=self.a['identity'],context=self.ctx.hex())
        initial=call(self.binary,op='candidate',checkpoint=created['checkpoint'],key=self.a['key'],group=created['snapshot']['group'],packages=[self.b['package'],self.c['package']])
        # Configured initial group establishment is setup, not the tested admission protocol.
        self.initial={'checkpoint':initial['checkpoint'],'snapshot':initial['after']};self.stores=[]
        self.ga=self.store('a',self.a,self.initial)
        # Initial Welcome has two recipients; the generic fixture join accepts its embedded tree via this worker.
        joined=call(self.binary,op='join',checkpoint=self.b['checkpoint'],key=self.b['key'],welcome=initial['welcome'])
        self.gb=self.store('b',self.b,joined)
        self.gc=self.store('c',self.c,call(self.binary,op='join',checkpoint=self.c['checkpoint'],key=self.c['key'],welcome=initial['welcome']))
        self.allowed={(self.phone['identity'],self.phone['key'])}
    def store(self,name,device,state):
        identity=IdentityStore(self.root/(name+'.sqlite'));self.stores.append(identity)
        for peer in [self.a,self.b,self.c]:self.assertEqual(identity.observe(peer['record'],first_contact_policy='allow-unverified')['status'],'pinned-unverified')
        self.assertEqual(identity.accept_successor(encode_event(self.bundle),candidate_digest=self.head,time=self.time)['status'],'accepted-unverified')
        g=GroupTransitions(identity,self.binary,device);g.install_configured_fixture(state)
        if hasattr(self,'application_profile'):
            for member in state['snapshot']['members']:g.receiver.application_agreement.configure_device(state['snapshot']['group'],member['identity'],member['key'],self.application_profile)
        return g
    def tearDown(self):
        for store in self.stores:store.close()
        self.tmp.cleanup()
    def prepared(self):return self.ga.prepare([self.phone['package']])
    def test_decision_welcome_replay_and_four_leaf_result(self):
        ident=self.prepared()
        with self.assertRaisesRegex(ValueError,'withheld'):self.ga.release(ident,allowed=self.allowed,time=self.time)
        self.assertEqual(self.ga.decide(ident,allowed=self.allowed,time=self.time),'accepted')
        wire=self.ga.release(ident,allowed=self.allowed,time=self.time)
        self.assertEqual(self.gb.receive(bytes.fromhex(wire['wire']),allowed=self.allowed,time=self.time),'accepted')
        self.assertEqual(self.gb.receive(bytes.fromhex(wire['wire']),allowed=set(),time=self.time),'accepted')
        self.assertEqual(len(self.gb.live()['snapshot']['members']),4)
        joined=call(self.binary,op='join',checkpoint=self.phone['checkpoint'],key=self.phone['key'],welcome=wire['welcome'])
        self.assertEqual(joined['snapshot']['predecessor'],self.ga.live()['snapshot']['predecessor'])
    def test_policy_rejection_preserves_ratchet_for_later_real_commit(self):
        # Bob is an administrator, but not the writer. His valid commit is rejected.
        bad=self.gb.prepare([self.phone['package']]);raw=json.loads(self.gb.db.execute('SELECT state FROM gt_candidate WHERE digest=?',(bad,)).fetchone()[0])
        previous=self.gc.live()
        self.assertEqual(self.gc.receive(bytes.fromhex(raw['wire']),allowed=self.allowed,time=self.time),'rejected-policy')
        self.assertNotEqual(self.gc.live()['checkpoint'],previous['checkpoint'])
        with self.assertRaises(ValueError):self.gc.invoke('receive',self.gc.live(),wire=raw['wire'])
        # Reload the rejected receiver from its persisted unmerged checkpoint.
        ident=self.prepared();self.ga.decide(ident,allowed=self.allowed,time=self.time)
        wire=self.ga.release(ident,allowed=self.allowed,time=self.time)
        self.assertEqual(self.gc.receive(bytes.fromhex(wire['wire']),allowed=self.allowed,time=self.time),'accepted')
    def test_unauthorized_addition_and_candidate_reservation(self):
        ident=self.prepared()
        with self.assertRaisesRegex(ValueError,'Unauthorized addition'):self.ga.decide(ident,allowed=set(),time=self.time)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM gt_outbox').fetchone()[0],0)
        self.assertEqual(self.ga.prepare([self.phone['package']]),ident)
        with self.assertRaisesRegex(ValueError,'reserved'):self.ga.prepare([self.c['package']])
    def test_future_epoch_waits_and_invalid_crypto_does_not_install(self):
        first=self.prepared();self.ga.decide(first,allowed=self.allowed,time=self.time)
        w1=self.ga.release(first,allowed=self.allowed,time=self.time)['wire']
        second=self.ga.prepare([]);self.ga.decide(second,allowed=set(),time=self.time)
        w2=bytes.fromhex(self.ga.release(second,allowed=set(),time=self.time)['wire'])
        original=self.gb.live()
        self.assertEqual(self.gb.receive(w2,allowed=set(),time=self.time),'pending')
        self.assertEqual(self.gb.live(),original)
        invalid=bytearray.fromhex(w1);invalid[-1]^=1
        with self.assertRaises(ValueError):self.gb.receive(bytes(invalid),allowed=self.allowed,time=self.time)
        self.assertEqual(self.gb.live(),original)
        self.assertEqual(self.gb.receive(bytes.fromhex(w1),allowed=self.allowed,time=self.time),'accepted')
        self.assertEqual(self.gb.receive(w2,allowed=set(),time=self.time),'accepted')
        self.assertEqual(self.gb.db.execute('SELECT count(*) FROM gt_pending').fetchone()[0],0)
    def test_two_process_exact_decision_has_one_outbox(self):
        ident=self.prepared();ctx=multiprocessing.get_context('fork')
        processes=[ctx.Process(target=crash_run,args=(self.root/'a.sqlite',self.binary,self.a,'decide',ident,self.allowed,self.time,'never')) for _ in range(2)]
        for p in processes:p.start()
        for p in processes:p.join(20);self.assertEqual(p.exitcode,92)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM gt_decision').fetchone()[0],1)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM gt_outbox').fetchone()[0],1)
    def test_identity_revocation_invalidates_prepared_addition(self):
        ident=self.prepared();bundle=json.loads(json.dumps(self.bundle))
        state=json.loads(base64.b64decode(bundle['states'][0]['payload']))
        state.update(record='9'*32,revision='2',previous=[self.head],revoked=[self.phone['device']],bindings=[r for r in state['bindings'] if r['device']!=self.phone['device']])
        payload=encode_event(state);bundle['states'].insert(0,{'payload':base64.b64encode(payload).decode(),'signature':sign(self.provider,self.a,'email-next/identity-state/v0',payload)})
        accepted=self.ga.identity.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(payload).hexdigest(),time=self.time)
        self.assertEqual(accepted['status'],'accepted-unverified')
        with self.assertRaisesRegex(ValueError,'Current identity'):self.ga.decide(ident,allowed=self.allowed,time=self.time)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM gt_outbox').fetchone()[0],0)
    def test_same_epoch_receive_change_cannot_be_overwritten_by_candidate(self):
        ident=self.prepared();bad=self.gb.prepare([self.phone['package']])
        raw=json.loads(self.gb.db.execute('SELECT state FROM gt_candidate WHERE digest=?',(bad,)).fetchone()[0])
        self.assertEqual(self.ga.receive(bytes.fromhex(raw['wire']),allowed=self.allowed,time=self.time),'rejected-policy')
        retained=self.ga.live()
        with self.assertRaisesRegex(ValueError,'Predecessor changed'):self.ga.decide(ident,allowed=self.allowed,time=self.time)
        self.assertEqual(self.ga.live(),retained)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM gt_outbox').fetchone()[0],0)
    def strip_committer_send(self,identity):
        # A real successor replaces the retained binding; the predecessor key signs it.
        bundle=json.loads(json.dumps(self.bundle))
        binding=json.loads(base64.b64decode(self.a['record']['binding']))
        binding.update(record='a'*32,roles=['receive','enroll','revoke'],authority={'kind':'state','digest':self.head})
        raw=encode_event(binding);binding_digest=hashlib.sha256(raw).hexdigest()
        state=json.loads(base64.b64decode(bundle['states'][0]['payload']))
        state.update(record='b'*32,revision='2',previous=[self.head],bindings=[dict(device=row['device'],digest=binding_digest if row['device']==self.a['device'] else row['digest']) for row in state['bindings']])
        payload=encode_event(state)
        bundle['bindings'].insert(0,{'payload':base64.b64encode(raw).decode(),'authorization':sign(self.provider,self.a,'email-next/device-binding/v0',raw),'possession':sign(self.provider,self.a,'email-next/device-possession/v0',raw)})
        bundle['states'].insert(0,{'payload':base64.b64encode(payload).decode(),'signature':sign(self.provider,self.a,'email-next/identity-state/v0',payload)})
        result=identity.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(payload).hexdigest(),time=self.time)
        self.assertEqual(result['status'],'accepted-unverified')
        self.assertEqual(identity.check_device(bytes.fromhex(self.a['identity']),bytes.fromhex(self.a['key']),role='receive',time=self.time,trust_policy='allow-unverified')['status'],'authorized-unverified')
    def test_lost_send_role_blocks_decision_receive_and_release(self):
        ident=self.prepared()
        # Another independent local replica retains the same valid prepared state.
        replica=self.store('replica',self.a,self.initial)
        candidate=replica.prepare([self.phone['package']])
        self.strip_committer_send(replica.identity)
        with self.assertRaisesRegex(ValueError,'committer send'):replica.decide(candidate,allowed=self.allowed,time=self.time)
        self.assertEqual(replica.db.execute('SELECT count(*) FROM gt_outbox').fetchone()[0],0)
        self.ga.decide(ident,allowed=self.allowed,time=self.time)
        wire=self.ga.release(ident,allowed=self.allowed,time=self.time)['wire']
        self.strip_committer_send(self.gb.identity)
        self.assertEqual(self.gb.receive(bytes.fromhex(wire),allowed=self.allowed,time=self.time),'rejected-policy')
        self.assertEqual(len(self.gb.live()['snapshot']['members']),3)
        self.strip_committer_send(self.ga.identity)
        with self.assertRaisesRegex(ValueError,'committer send'):self.ga.release(ident,allowed=self.allowed,time=self.time)
    def test_process_exit_atomic_decision_and_receive(self):
        ident=self.prepared();ctx=multiprocessing.get_context('fork')
        for point,expected in [('before-commit',0),('after-commit',1)]:
            process=ctx.Process(target=crash_run,args=(self.root/'a.sqlite',self.binary,self.a,'decide',ident,self.allowed,self.time,point));process.start();process.join(20)
            self.assertEqual(process.exitcode,91);self.assertEqual(self.ga.db.execute('SELECT count(*) FROM gt_decision').fetchone()[0],expected)
            self.assertEqual(self.ga.db.execute('SELECT count(*) FROM gt_outbox').fetchone()[0],expected)
            self.assertEqual(len(self.ga.live()['snapshot']['members']),3+expected)
        wire=bytes.fromhex(self.ga.release(ident,allowed=self.allowed,time=self.time)['wire'])
        for point,expected in [('before-commit',0),('after-commit',1)]:
            process=ctx.Process(target=crash_run,args=(self.root/'b.sqlite',self.binary,self.b,'receive',wire,self.allowed,self.time,point));process.start();process.join(20)
            self.assertEqual(process.exitcode,91);self.assertEqual(self.gb.db.execute('SELECT count(*) FROM gt_receive').fetchone()[0],expected)
            self.assertEqual(len(self.gb.live()['snapshot']['members']),3+expected)

if __name__=='__main__':unittest.main()
