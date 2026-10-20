import base64,json,unittest
from pathlib import Path
from event_encoding import encode_event
from provider_mls import sign
from initial_roster import parse
from initial_roster_lifecycle import InitialRosterRelease,InitialRosterAdmission
from invitation_mime import select
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
import test_initial_roster_lifecycle as roster_tests
import test_joined_ordering as ordering_tests
from ordering_mls import ProviderKey
from admitted_quorum import AdmittedQuorum
from mls_mime import unpack
from smtp_loopback import roundtrip
import ordering_carrier

class AdmittedQuorumTests(unittest.TestCase):
    endpoint=roster_tests.RosterLifecycleTests.endpoint;prepare=roster_tests.RosterLifecycleTests.prepare;tearDown=roster_tests.RosterLifecycleTests.tearDown
    certify=ordering_tests.JoinedTests.certify
    def setUp(self):
        roster_tests.RosterLifecycleTests.setUp(self)
        chosen=[self.f.creator]
        chosen += [next(d for d in self.f.devices if d['principal']==p) for p in self.principals if p!=self.f.creator['principal']]
        self.witnesses=sorted(chosen,key=lambda d:d['principal'])
        self.removed=next(d for d in self.f.devices if d['principal']==self.f.creator['principal'] and d is not self.f.creator)
        selected=sorted(chosen+[self.removed],key=lambda d:(d['principal'],d['device']))
        old=dict((d['device'],p) for d,p in zip(self.f.devices,self.f.proofs));self.f.devices=selected
        witnesses=[]
        for d in self.witnesses:
            v=json.loads(base64.b64decode(old[d['device']]['payload']));witnesses.append(dict(principal=d['principal'],device=d['device'],signingKey=d['key'],state=v['state'],binding=v['binding']))
        self.f.context.update(version='7',delivery={'kind':'ordinary-v0'},application=dict(envelopeVersion='3',payload='mime-rich-v0',operations=['message','rich-message']),ordering=dict(kind='endpoint-quorum-v0',generation='0',faultBound='0',witnesses=witnesses))
        self.f.proofs=[]
        for d in selected:
            p=old[d['device']];v=json.loads(base64.b64decode(p['payload']));v.update(version='6',applications=[dict(self.f.context['application'],ordering='endpoint-quorum-v0')]);raw=encode_event(v)
            self.f.proofs.append(dict(p,payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,d,'email-next/passive-discovery/v6',raw)))
        self.devices=[{k:d[k] for k in ('principal','device')} for d in selected]
        self.identity,self.sender,self.selected=self.endpoint('quorum-creator');self.release=InitialRosterRelease(self.sender)
        self.provider=self.f.binary;self.worker=self.provider.with_name('group-transitions');self.root=Path(self.temp.name)
    def join(self):
        wires=self.prepare();self.senders={self.f.creator['device']:self.sender}
        for ident,wire in wires.items():
            smtp=LocalSMTP()
            with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit_initial_roster(ident,port=smtp.port,time=self.time)['state'],'accepted')
            smtp.done();p=parse(select(smtp.wire));expected_new=json.loads(base64.b64decode(self.f.proofs[0]['payload']))['version']=='7';self.assertEqual(p['value']['version'],'7' if expected_new else '6');self.assertEqual(p['roster']['version'],'4' if expected_new else '3')
            target=next(d for d in self.f.devices if d['device']==p['value']['target']['device']);identity,sender,selected=self.endpoint('target'+target['device'][5:10]);admission=InitialRosterAdmission(identity,self.provider);admission.publish_local(target)
            choices=[dict(principal=d['principal'],device=d['device'],mailbox=c['mailbox'],generation=c['generation']) for d,c in zip(self.f.devices,selected)]
            admission.accept_message(select(smtp.wire),target=target,mailbox=p['value']['target']['mailbox'],allow_creator=self.f.creator['principal'],intended_principals=self.principals,intended_devices=self.devices,expected_context=encode_event(self.f.context),selections=choices,time=self.time,trust_policy='allow-unverified')
            self.senders[target['device']]=sender
        self.devices=self.witnesses
        self.groups=[AdmittedQuorum(self.senders[d['device']].receiver,self.worker,d) for d in self.witnesses]
        self.author_group=next(g for g in self.groups if g.device is self.f.creator)
    def event(self,d,ident,rich=False):
        operation=dict(kind='rich-message',text='Rich greeting',html='<p><strong>Rich greeting</strong></p>',presentation='html-css-v0',manifest=[],replyTo=[],embedded=[],attachments=[]) if rich else dict(kind='message',text='Reply after membership change',replyTo=[])
        return dict(version='3',purpose='contribution',event=ident*32,conversation=self.f.context['conversation'],principal=d['principal'],audience=self.principals,disclosures=[],presentation=dict(subject='Quorum conversation',authoredAt=self.time['earliest'],to=sorted(set(self.principals)-{d['principal']}),cc=[]),operation=operation)
    def send(self,d,ident,rich=False):
        sender=self.senders[d['device']];source=next(c['mailbox'] for x,c in zip(self.f.devices,self.selected) if x is d);destinations=sorted({c['mailbox'] for x,c in zip(self.f.devices,self.selected) if x is not d and x is not self.removed})
        wire=sender.prepare(ident,encode_event(self.event(d,ident,rich)),key=d['key'],envelope_sender=source,recipients=destinations,time=self.time,resources={} if rich else None)
        smtp=LocalSMTP()
        with SenderWorker(sender) as worker:self.assertEqual(worker.submit(ident,port=smtp.port,time=self.time)['state'],'accepted')
        smtp.done()
        for peer in self.witnesses:
            if peer is not d:self.assertEqual(self.senders[peer['device']].receiver.receive(unpack(smtp.wire),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        return wire
    def test_durable_candidates_continue_handshake_with_application_interleaving(self):
        self.join();author=self.author_group;before=author.live()[1]
        first=author.stage(ProviderKey(self.provider,self.f.creator),time=self.time)
        self.assertEqual(author.live()[1]['snapshot'],before['snapshot'])
        self.assertEqual(author.live()[1]['revision'],before['revision']+1)
        self.send(self.f.creator,'7')
        restarted=AdmittedQuorum(self.sender.receiver,self.worker,self.f.creator)
        before_failure=restarted.live()
        restarted.db.execute("CREATE TEMP TRIGGER fail_revision BEFORE INSERT ON qo_stage_revision BEGIN SELECT RAISE(ABORT,'revision retention failure'); END")
        import sqlite3
        with self.assertRaisesRegex(sqlite3.IntegrityError,'revision retention failure'):restarted.stage(ProviderKey(self.provider,self.f.creator),time=self.time)
        self.assertTrue(restarted.live()==before_failure,'stage revision failure must preserve atomic checkpoint')
        restarted.db.execute('DROP TRIGGER fail_revision')
        second=restarted.stage(ProviderKey(self.provider,self.f.creator),time=self.time)
        from provider_mls import call
        peer=next(g for g in self.groups if g is not author);state=peer.live()[1]
        one=call(self.worker,op='receive-quorum',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=peer.device['key'],wire=first['plan']['commit'])
        two=call(self.worker,op='receive-quorum',checkpoint=one['unmerged'],group=state['snapshot']['group'],key=peer.device['key'],wire=second['plan']['commit'])
        self.assertEqual(one['before'],two['before'])
        # Installing the earlier exact candidate merges into the latest ratchets.
        self.send(self.f.creator,'8');proof=self.certify(first)
        for g in self.groups:g.install(first,proof,time=self.time)
        self.send(self.f.creator,'9');self.send(peer.device,'b')
        for row in author.db.execute('SELECT state FROM qo_staged'):
            self.assertNotIn('continuedCheckpoint',json.loads(row[0]))

    def test_initial_rich_certified_removal_and_normal_reply(self):
        self.join();wire=self.send(self.f.creator,'a',True)
        from managed_presentation import describe
        import hashlib
        peer=next(d for d in self.witnesses if d is not self.f.creator)
        shown=describe(self.senders[peer['device']].receiver,dict(principal=self.f.creator['principal'],conversation=self.f.context['conversation'],event='a'*32),carrier=hashlib.sha256(unpack(wire)).hexdigest(),transport_wire=wire)
        self.assertEqual(shown['subject'],'Quorum conversation')
        snap=self.author_group.live()[1]['snapshot'];index=next(m['index'] for m in snap['members'] if m['identity']==self.removed['identity'])
        candidate=self.author_group.stage(ProviderKey(self.provider,self.f.creator),time=self.time,removals=[int(index)]);proof=self.certify(candidate)
        before=self.author_group.live()
        with self.assertRaises(RuntimeError):self.author_group.install(candidate,proof,time=self.time,crash=lambda _:(_ for _ in ()).throw(RuntimeError('crash')))
        self.assertEqual(before,self.author_group.live())
        decision=self.author_group.install(candidate,proof,time=self.time);wire=roundtrip(ordering_carrier.package(self.author_group.release(decision,time=self.time)))
        for g in self.groups:
            self.assertEqual(ordering_carrier.receive(g,wire,time=self.time)['decision'],decision)
            self.assertEqual(g.live()[1]['snapshot']['epoch'],'2')
            self.assertIsNone(g.db.execute('SELECT 1 FROM mls_configured_context').fetchone())
            self.assertIsNone(g.db.execute('SELECT 1 FROM qo_checkpoint').fetchone())
        peer=next(d for d in self.witnesses if d is not self.f.creator);self.send(peer,'b')
        restarted=AdmittedQuorum(self.sender.receiver,self.worker,self.f.creator);self.assertEqual(restarted.install(candidate,proof,time=self.time),decision)
    def test_exact_candidate_preserves_advanced_ratchets_and_wrong_proof_holds(self):
        self.join();candidate=self.author_group.stage(ProviderKey(self.provider,self.f.creator),time=self.time);proof=self.certify(candidate)
        self.send(self.f.creator,'c');self.send(self.f.creator,'2')
        peer=next(d for d in self.witnesses if d is not self.f.creator)
        old_wire=self.send(peer,'e');before=self.author_group.live()
        restarted=AdmittedQuorum(self.sender.receiver,self.worker,self.f.creator)
        from ordering_mls import candidate_id
        retained=self.sender.db.execute('SELECT state FROM qo_staged WHERE candidate=?',(candidate_id(candidate),)).fetchone()[0]
        changed_stage=json.loads(retained);changed_stage['localStageBinding']['library']='unknown-version'
        self.sender.db.execute('UPDATE qo_staged SET state=? WHERE candidate=?',(json.dumps(changed_stage).encode(),candidate_id(candidate)))
        with self.assertRaisesRegex(ValueError,'staged binding'):restarted.install(candidate,proof,time=self.time)
        self.assertEqual(restarted.live(),before)
        self.sender.db.execute('UPDATE qo_staged SET state=? WHERE candidate=?',(retained,candidate_id(candidate)))
        with self.assertRaises(RuntimeError):restarted.install(candidate,proof,time=self.time,crash=lambda point:(_ for _ in ()).throw(RuntimeError('crash')) if point=='before-commit' else None)
        self.assertEqual(self.author_group.live(),before)
        import subprocess,sys
        config=self.root/'staged-merge-child.json'
        config.write_text(json.dumps(dict(db=self.sender.db.execute('PRAGMA database_list').fetchone()[2],worker=str(self.worker.resolve()),receiver=str(self.sender.receiver.binary.resolve()),device=self.f.creator,candidate=candidate,proof=proof.hex(),time=self.time)))
        program="""
import json,os,sys
from pathlib import Path
from identity_store import IdentityStore
from mls_receive import MlsReceive
from admitted_quorum import AdmittedQuorum
c=json.loads(Path(sys.argv[1]).read_text());identity=IdentityStore(c['db'])
g=AdmittedQuorum(MlsReceive(identity,c['receiver']),c['worker'],c['device'])
def crash(point):
 if point==sys.argv[2]:os._exit(73)
g.install(c['candidate'],bytes.fromhex(c['proof']),time=c['time'],crash=crash)
identity.close()
"""
        for point in ('before-commit','after-commit'):
            child=subprocess.run([sys.executable,'-c',program,str(config),point],cwd=Path(__file__).resolve().parent,capture_output=True)
            self.assertEqual(child.returncode,73,child.stderr)
            if point=='before-commit':self.assertEqual(restarted.live(),before)
        decision=restarted.install(candidate,proof,time=self.time)
        for g in self.groups:
            if g is not self.author_group:g.install(candidate,proof,time=self.time)
        self.assertEqual(restarted.install(candidate,proof,time=self.time),decision)
        with self.assertRaises(ValueError):restarted.install(candidate,b'{}',time=self.time)
        from ordering_certificates import encode
        equivalent=json.loads(proof);equivalent['objects'].reverse();alternative=encode(equivalent)
        self.assertEqual(restarted.install(candidate,alternative,time=self.time),decision)
        from quorum_join_support import retain_path_locked
        import base64
        self.sender.db.execute('BEGIN IMMEDIATE')
        retain_path_locked(self.sender.db,[dict(candidate=candidate,proof=base64.b64encode(alternative).decode())])
        self.sender.db.execute('COMMIT')
        replay_before=restarted.live()
        received_before=self.sender.db.execute('SELECT count(*) FROM mls_receives').fetchone()
        self.sender.receiver.receive(unpack(old_wire),time=self.time,trust_policy='allow-unverified')
        self.assertEqual(restarted.live(),replay_before)
        self.assertEqual(self.sender.db.execute('SELECT count(*) FROM mls_receives').fetchone(),received_before)
        self.send(self.f.creator,'f');self.send(peer,'1')
        other=next(g for g in self.groups if g is not self.author_group);changed=json.loads(json.dumps(candidate));changed['plan']['commit']='00'
        with self.assertRaises(ValueError):other.install(changed,proof,time=self.time)
    def test_witness_and_old_tuple_fail_without_checkpoint(self):
        self.f.context['ordering']['witnesses'][0]['binding']='f'*64
        with self.assertRaisesRegex(ValueError,'witness'):self.prepare()
        self.assertIsNone(self.identity.db.execute('SELECT 1 FROM mls_checkpoint').fetchone())

    def test_old_tuple_service_question_and_missing_admission_hold(self):
        from application_tuples import validate_tuples
        value=[dict(self.f.context['application'],ordering='endpoint-quorum-v0')]
        with self.assertRaises(ValueError):validate_tuples(value,version='5')
        with self.assertRaises(ValueError):validate_tuples([dict(value[0],operations=['service-question'])],version='6')
        self.join();group=self.author_group.live()[1]['snapshot']['group']
        from group_transitions import GroupTransitions
        with self.assertRaisesRegex(ValueError,'Ordering not configured'):GroupTransitions(self.identity,self.worker,self.f.creator).live()
        self.identity.db.execute('DELETE FROM mls_quorum_admission')
        with self.assertRaisesRegex(ValueError,'Application contract|quorum admission'):self.send(self.f.creator,'d')
        self.assertIsNone(self.identity.db.execute("SELECT 1 FROM sender_prepared WHERE id='d'").fetchone())

if __name__=='__main__':unittest.main()
