"""Actual signed established Welcome and same-key, fresh-package rejoin."""
import hashlib
import json
import unittest
import test_group_removal as fixture
from event_encoding import encode_event
from provider_mls import call,sign
from group_instances import GroupInstances,current
from established_invitation import EstablishedAdmission,b64,sha
from group_transitions import ids

class EstablishedInvitationTests(unittest.TestCase):
    setUp=fixture.RemovalTests.setUp
    tearDown=fixture.RemovalTests.tearDown
    store=fixture.RemovalTests.store
    prepared=fixture.RemovalTests.prepared
    remove=fixture.RemovalTests.remove
    def setup_rejoin(self,pending=False):
        # Retain an actual old-instance application before eviction.
        GroupInstances(self.gc.db).migrate_configured(self.gc)
        if pending:
            event=dict(version='0',purpose='contribution',event='6'*32,conversation='2'*32,principal=self.b['principal'],audience=sorted([self.a['principal'],self.b['principal'],self.c['principal']]),operation=dict(kind='answer',question=dict(principal=self.b['principal'],conversation='2'*32,event='5'*32),option='7'*32,replaces=[]))
            state=self.gb.live();sent=call(self.provider,op='send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.b['key'],application=encode_event(event).hex())
            self.assertEqual(self.gc.receiver.receive(bytes.fromhex(sent['wire']),time=self.time,trust_policy='allow-unverified')['status'],'pending')
        # Phone is a continuous survivor across C's removal and rejoin.
        added=self.prepared();self.ga.decide(added,allowed=self.allowed,time=self.time)
        record=json.loads(self.ga.db.execute('SELECT state FROM gt_decision WHERE digest=?',(added,)).fetchone()[0])
        self.assertEqual(self.gc.receive(bytes.fromhex(record['wire']),allowed=self.allowed,time=self.time),'accepted')
        removed=self.remove(self.c);self.assertEqual(self.gc.receive(bytes.fromhex(removed['wire']),allowed=set(),time=self.time),'accepted')
        self.old=current(self.gc.db,removed['after']['group'])['instance']
        fresh=call(self.provider,op='fresh-package',checkpoint=self.c['checkpoint'],key=self.c['key'],identity=self.c['identity'])
        self.target=dict(self.c,**fresh)
        ident=self.ga.prepare([self.target['package']]);self.ga.decide(ident,allowed={(self.c['identity'],self.c['key'])},time=self.time)
        result=json.loads(self.ga.db.execute('SELECT state FROM gt_decision WHERE digest=?',(ident,)).fetchone()[0])
        self.admission=EstablishedAdmission(self.gc.identity,self.provider);self.admission.publish_local(self.target)
        members=[]
        for m in result['after']['members']:
            p,d=ids(m['identity']);check=self.ga.identity.check_device(bytes.fromhex(m['identity']),bytes.fromhex(m['key']),role='receive',time=self.time,trust_policy='allow-unverified')
            members.append(dict(principal=p,device=d,signingKey=m['key'],state=check['head'],binding=check['binding']))
        members.sort(key=lambda m:(m['principal'],m['device']))
        def named(device):
            m=next(m for m in members if (m['principal'],m['device'])==(device['principal'],device['device']))
            return {k:m[k] for k in ('principal','device','state','binding')}
        value=dict(version='0',purpose='mls-established-membership-invitation',invitation='a'*32,profile='mls-1-0001',conversation='2'*32,creator=named(self.a),target=dict(named(self.c),mailbox='carol@example.invalid'),group=b64(bytes.fromhex(result['after']['group'])),previousEpoch=result['before']['epoch'],epoch=result['after']['epoch'],previousGroupContextDigest=sha(bytes.fromhex(result['before']['predecessor'])),resultGroupContextDigest=sha(bytes.fromhex(result['after']['predecessor'])),decision=ident,keyPackageRef=b64(bytes.fromhex(self.target['reference'])),keyPackageDigest=sha(bytes.fromhex(self.target['package'])),notBefore=str(int(self.time['earliest'])-1),notAfter=str(int(self.time['latest'])+30),context=b64(self.ctx),applicationContextDigest=sha(self.ctx),members=members,welcome=b64(bytes.fromhex(result['welcome'])))
        self.value=value;return self.wrap(value)
    def wrap(self,value):
        raw=encode_event(value)
        return encode_event(dict(payload=b64(raw),signature=sign(self.provider,self.a,'email-next/mls-established-membership-invitation/v0',raw),identity=self.bundle))
    def accept(self,raw,**extra):
        return self.admission.accept_message(raw,target=self.target,mailbox='carol@example.invalid',allow_creator=self.a['principal'],expected_context=self.ctx,time=self.time,**extra)
    def test_real_same_key_rejoin_then_remove_continuous_survivor(self):
        raw=self.setup_rejoin(pending=True);accepted=self.accept(raw)
        self.assertNotEqual(accepted['instance'],self.old);self.assertEqual(self.target['key'],self.c['key']);self.assertNotEqual(self.target['package'],self.c['package'])
        self.assertEqual(self.accept(raw),accepted)
        self.assertEqual(list(self.gc.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')['states'].values()),['held:membership-instance'])
        removed=self.remove(self.phone)
        self.assertEqual(self.gc.receive(bytes.fromhex(removed['wire']),allowed=set(),time=self.time),'accepted')
        rows=self.gc.db.execute('SELECT i.instance,e.end_epoch FROM mls_membership_episode e JOIN mls_episode_instance i USING(group_id,identity,key,admission) WHERE e.identity=?',(self.phone['identity'],)).fetchall()
        self.assertEqual(dict(rows),{self.old:None,accepted['instance']:removed['after']['epoch']})
        event=dict(version='0',purpose='contribution',event='b'*32,conversation='2'*32,principal=self.a['principal'],audience=sorted([self.a['principal'],self.b['principal'],self.c['principal']]),operation=dict(kind='message',text='New membership instance',replyTo=[]))
        state=self.ga.live();sent=call(self.provider,op='send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.a['key'],application=encode_event(event).hex())
        self.assertEqual(self.gc.receiver.receive(bytes.fromhex(sent['wire']),time=self.time,trust_policy='allow-unverified')['status'],'projected-context-matched')
        self.assertEqual(self.gc.db.execute('SELECT instance FROM mls_receive_instance WHERE digest=?',(sha(bytes.fromhex(sent['wire'])),)).fetchone()[0],accepted['instance'])
    def test_crash_rolls_back_package_checkpoint_instance_and_retry(self):
        raw=self.setup_rejoin();before=self.gc.db.execute('SELECT snapshot FROM mls_checkpoint').fetchone()[0]
        def fail(stage):raise RuntimeError('crash')
        with self.assertRaises(RuntimeError):self.accept(raw,crash=fail)
        self.assertEqual(self.gc.db.execute('SELECT snapshot FROM mls_checkpoint').fetchone()[0],before)
        self.assertEqual(self.gc.db.execute('SELECT count(*) FROM mls_group_instances').fetchone()[0],1)
        self.assertIsNone(self.gc.db.execute('SELECT invitation FROM provider_mls_admission WHERE reference=?',(self.target['reference'],)).fetchone()[0])
        self.assertEqual(self.accept(raw)['status'],'accepted-unverified')
    def test_wrong_finalized_context_does_not_install(self):
        self.setup_rejoin();value=dict(self.value,resultGroupContextDigest='f'*64)
        with self.assertRaisesRegex(ValueError,'Welcome mismatch'):self.accept(self.wrap(value))
        self.assertEqual(self.gc.db.execute('SELECT status FROM mls_group_instances').fetchone()[0],'inactive')

    def test_signature_target_policy_and_consumed_package_conflicts(self):
        raw=self.setup_rejoin();wrapper=json.loads(raw);wrapper['signature']='0'*128
        with self.assertRaises(ValueError):self.accept(encode_event(wrapper))
        with self.assertRaises(ValueError):self.accept(raw,trust_policy='require-verification')
        self.assertEqual(self.gc.db.execute('SELECT count(*) FROM membership_invitation_acceptance').fetchone()[0],0)
        self.accept(raw)
        with self.assertRaisesRegex(ValueError,'replay conflict'):self.accept(self.wrap(dict(self.value,notAfter=str(int(self.value['notAfter'])+1))))
        with self.assertRaisesRegex(ValueError,'unavailable package'):self.accept(self.wrap(dict(self.value,invitation='b'*32)))

    def test_signed_overlong_interval_does_not_consume_package(self):
        self.setup_rejoin()
        value=dict(self.value,notAfter=str(int(self.time['latest'])+100000))
        with self.assertRaisesRegex(ValueError,'authority|Package validity'):self.accept(self.wrap(value))
        self.assertIsNone(self.gc.db.execute('SELECT invitation FROM provider_mls_admission WHERE reference=?',(self.target['reference'],)).fetchone()[0])
        self.assertEqual(self.gc.db.execute('SELECT count(*) FROM membership_invitation_acceptance').fetchone()[0],0)
