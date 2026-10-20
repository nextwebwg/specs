import json
import tempfile
from pathlib import Path
import unittest
import test_initial_roster as roster_fixture
from identity_store import IdentityStore
from sender_release import SenderRelease
from initial_roster_lifecycle import InitialRosterRelease,InitialRosterAdmission
from passive_discovery import decode_passive_discovery
from passive_discovery_verify import verify_passive_discovery
from event_encoding import encode_event
from invitation_mime import select

class RosterLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.f=roster_fixture.InitialRosterTests();
        if hasattr(self,'application'):self.f.application=self.application
        self.f.setUp();self.temp=tempfile.TemporaryDirectory();self.stores=[];self.time=dict(earliest=self.f.time,latest=self.f.time)
        self.identity,self.sender,self.selected=self.endpoint('creator');self.release=InitialRosterRelease(self.sender)
        self.principals=sorted({d['principal'] for d in self.f.devices});self.devices=[{k:d[k] for k in ('principal','device')} for d in self.f.devices]
    def tearDown(self):
        for store in self.stores:store.close()
        self.temp.cleanup()
    def endpoint(self,name):
        identity=IdentityStore(Path(self.temp.name)/(name+'.sqlite'));self.stores.append(identity)
        for principal in self.f.bundles:
            first=next(d for d in self.f.devices if d['principal']==principal)
            identity.observe(first['record'],first_contact_policy='allow-unverified')
            self.assertEqual(identity.accept_successor(encode_event(self.f.bundles[principal]),candidate_digest=self.f.heads[principal],time=self.time)['status'],'accepted-unverified')
        sender=SenderRelease(identity,self.f.binary);sender.configure(expected_revision=0);selected=[]
        for i,(device,proof) in enumerate(zip(self.f.devices,self.f.proofs)):
            raw=encode_event(proof);d=decode_passive_discovery(raw);mailbox=d['assertion']['value']['mailbox']
            self.assertEqual(verify_passive_discovery(raw,identity,time=self.time,trust_policy='allow-unverified')['status'],'snapshot-authorized-unverified')
            sender.associations.observe_validated_batch([dict(assertion=d['assertion']['octets'],signature=d['signature'],signingKey=bytes.fromhex(device['key']),outerFrom=[mailbox],sourceId='roster-test',parserRevision='0',observedAt=self.f.time)])
            sender.associations.decide(decision_id=f'{i+1:032x}',mailbox=mailbox,expected_generation=None,kind='first-contact',principal=device['principal'],actor='configured-policy',policy_revision='1',trust_policy='allow-unverified',time=self.time)
            selected.append(dict(wrapper=raw,mailbox=mailbox,generation='1',digest=d['assertion']['digest']))
        return identity,sender,selected
    def prepare(self,**overrides):
        args=dict(device=self.f.creator,selected=self.selected,intended_principals=self.principals,intended_devices=self.devices,context=self.f.context,not_before=self.f.time,not_after=str(int(self.f.time)+30),time=self.time);args.update(overrides)
        return self.release.prepare('3'*32,**args)
    def test_atomic_creation_and_five_independent_admissions_share_anchor(self):
        wires=self.prepare();self.assertEqual(len(wires),5);self.assertEqual(self.prepare(),wires)
        creator_instance=self.identity.db.execute('SELECT instance FROM mls_checkpoint_instance').fetchone()[0]
        for index,(ident,wire) in enumerate(wires.items()):
            raw=select(wire);from initial_roster import parse
            p=parse(raw);target=next(d for d in self.f.devices if d['device']==p['value']['target']['device'] and d['principal']==p['value']['target']['principal'])
            identity,sender,selected=self.endpoint('receiver'+str(index));admission=InitialRosterAdmission(identity,self.f.binary);admission.publish_local(target)
            choices=[dict(principal=d['principal'],device=d['device'],mailbox=c['mailbox'],generation=c['generation']) for d,c in zip(self.f.devices,selected)]
            args=dict(target=target,mailbox=p['value']['target']['mailbox'],allow_creator=self.f.creator['principal'],intended_principals=self.principals,intended_devices=self.devices,expected_context=encode_event(self.f.context),selections=choices,time=self.time,trust_policy='allow-unverified')
            if index==0:
                with self.assertRaises(RuntimeError):admission.accept_message(raw,**args,crash=lambda _:(_ for _ in ()).throw(RuntimeError('crash')))
                self.assertIsNone(identity.db.execute('SELECT invitation FROM provider_mls_admission WHERE reference=?',(target['reference'],)).fetchone()[0])
                self.assertEqual(identity.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0],0)
            result=admission.accept_message(raw,**args);self.assertEqual(result['instance'],creator_instance);self.assertEqual(admission.accept_message(raw,**args),result)
    def test_creator_crash_rolls_back_all_targets_and_checkpoint(self):
        with self.assertRaises(RuntimeError):self.prepare(crash=lambda _:(_ for _ in ()).throw(RuntimeError('crash')))
        for table in ['mls_checkpoint','initial_rosters','initial_roster_prepared','initial_roster_packages','mls_group_instances']:
            self.assertEqual(self.identity.db.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
        self.assertEqual(len(self.prepare()),5)
    def test_independent_device_inventory_cannot_be_silently_truncated(self):
        with self.assertRaisesRegex(ValueError,'coverage'):self.prepare(intended_devices=self.devices[:-1])
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0],0)

    def test_smtp_target_delivery_is_independent_and_exact(self):
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        wires=self.prepare();ids=list(wires)
        with SenderWorker(self.sender) as worker:
            for ident in ids[:2]:
                smtp=LocalSMTP();result=worker.submit_initial_roster(ident,port=smtp.port,time=self.time);smtp.done()
                self.assertEqual(result['state'],'accepted');self.assertEqual(smtp.wire,wires[ident])
        self.assertEqual(self.identity.db.execute("SELECT count(*) FROM sender_attempts WHERE state='accepted'").fetchone()[0],2)
        self.assertEqual(len(self.prepare()),5)

    def test_uncertain_target_does_not_block_other_target_or_implicitly_retry(self):
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        from unittest.mock import patch
        wires=self.prepare();first,second=list(wires)[:2]
        with SenderWorker(self.sender) as worker:
            smtp=LocalSMTP(drop=True);result=worker.submit_initial_roster(first,port=smtp.port,time=self.time);smtp.done();self.assertEqual(result['state'],'uncertain')
            smtp=LocalSMTP();self.assertEqual(worker.submit_initial_roster(second,port=smtp.port,time=self.time)['state'],'accepted');smtp.done()
            with patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No implicit uncertain retry')):
                with self.assertRaisesRegex(ValueError,'Uncertain'):worker.submit_initial_roster(first,port=1,time=self.time)
            smtp=LocalSMTP();self.assertEqual(worker.submit_initial_roster(first,port=smtp.port,time=self.time,retry_uncertain=True)['state'],'accepted');smtp.done();self.assertEqual(smtp.wire,wires[first])
    def test_policy_change_after_release_aborts_before_data(self):
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        ident=next(iter(self.prepare()));smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:result=worker.submit_initial_roster(ident,port=smtp.port,time=self.time,crash=lambda stage:self.sender.configure(expected_revision=1) if stage=='after-release' else None)
        smtp.done();self.assertEqual(result['state'],'aborted-before-data');self.assertIsNone(smtp.wire)

class RichRosterLifecycleTests(RosterLifecycleTests):
    application=dict(envelopeVersion='1',payload='mime-rich-v0',operations=['rich-message'])
