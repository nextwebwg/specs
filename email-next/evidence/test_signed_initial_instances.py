import base64
import hashlib
import json
import multiprocessing
import os
import unittest
from unittest.mock import patch
from identity_store import IdentityStore
from event_encoding import encode_event
from provider_mls import sign,call
from mls_mime import unpack
from signed_initial_instances import migrate_signed_initial,initialize
import test_application_invitation_release as fixtures

def migrate_child(path,binary,key,point):
    identity=IdentityStore(path)
    migrate_signed_initial(identity,binary,local_key=key,crash=lambda stage:os._exit(86) if stage==point else None)

class SignedInitialInstanceTests(unittest.TestCase):
    setUp=fixtures.InitialReleaseTests.setUp
    tearDown=fixtures.InitialReleaseTests.tearDown
    prepare=fixtures.InitialReleaseTests.prepare
    accept=fixtures.InitialReleaseTests.accept
    def legacy(self):
        # Actual old-format admissions: suppress only the newly added qualification hook.
        with patch('signed_initial_instances.qualify_signed_initial_locked',return_value=None):
            self.wire=self.prepare();self.receipt=self.accept(self.wire)
        self.receiver=self.receiver_fixture.admission.receiver;self.db=self.f.identity.db
    def migrate(self):return migrate_signed_initial(self.f.identity,self.f.binary,local_key=self.f.devices[1]['key'])
    def message(self,pending=False):
        principal=self.f.devices[0]['principal']
        op=dict(kind='answer',question=dict(principal=principal,conversation='2'*32,event='4'*32),option='5'*32,replaces=[]) if pending else dict(kind='message',text='Before migration',replyTo=[])
        event=dict(version='1',purpose='contribution',event=('8' if pending else '9')*32,conversation='2'*32,principal=principal,audience=sorted(d['principal'] for d in self.f.devices),disclosures=[],operation=op)
        if pending:
            group,checkpoint=self.identity.db.execute('SELECT group_id,snapshot FROM mls_checkpoint').fetchone()
            sent=call(self.f.binary,op='send',checkpoint=json.loads(checkpoint),group=group,key=self.f.devices[0]['key'],application=encode_event(event).hex())
            return self.receiver.receive(bytes.fromhex(sent['wire']),time=self.f.time,trust_policy='allow-unverified')
        wire=self.sender.prepare('pending' if pending else 'message',encode_event(event),key=self.f.devices[0]['key'],envelope_sender=self.f.selected[0]['mailbox'],recipients=[self.f.selected[1]['mailbox']],time=self.f.time)
        return self.receiver.receive(unpack(wire),time=self.f.time,trust_policy='allow-unverified')
    def test_new_install_hooks_same_instance_and_exact_receipts(self):
        wire=self.prepare();receipt=self.accept(wire)
        creator=self.identity.db.execute('SELECT instance,provenance FROM mls_group_instances').fetchone()
        target=self.f.identity.db.execute('SELECT instance,provenance FROM mls_group_instances').fetchone()
        self.assertEqual(creator[0],target[0]);self.assertEqual((creator[1],target[1]),('signed-initial-creation','signed-initial-admission'))
        self.assertEqual(self.accept(wire),receipt)
        self.assertEqual(self.f.identity.db.execute('SELECT count(*) FROM mls_instance_agreements').fetchone()[0],2)
    def test_creator_selection_reverse_principal_order(self):
        from passive_discovery import decode_passive_discovery
        selected=sorted(self.f.selected,key=lambda c:decode_passive_discovery(c['wrapper'])['assertion']['value']['principal'],reverse=True)
        self.assertGreater(decode_passive_discovery(selected[0]['wrapper'])['assertion']['value']['principal'],decode_passive_discovery(selected[1]['wrapper'])['assertion']['value']['principal'])
        wire=self.prepare(selected=selected)
        self.assertEqual(self.accept(wire)['status'],'admitted-unverified')
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mls_instance_agreements').fetchone()[0],2)

    def test_original_receive_instance_and_history_without_redecryption(self):
        self.legacy();self.assertEqual(self.message()['status'],'projected-context-matched');self.assertEqual(self.message(True)['status'],'pending')
        before=self.db.execute('SELECT revision,snapshot FROM mls_checkpoint').fetchone();views=list(self.db.execute('SELECT * FROM derived_views'));accepted=list(self.db.execute('SELECT * FROM mls_application_acceptance'))
        with patch('mls_receive.worker_call',side_effect=AssertionError('No decrypt during migration')):result=self.migrate()
        self.assertEqual(self.db.execute('SELECT revision,snapshot FROM mls_checkpoint').fetchone(),before)
        self.assertEqual(list(self.db.execute('SELECT * FROM derived_views')),views);self.assertEqual(list(self.db.execute('SELECT * FROM mls_application_acceptance')),accepted)
        self.assertEqual(self.db.execute('SELECT count(*) FROM mls_receive_instance WHERE instance=?',(result['instance'],)).fetchone()[0],2)
        self.assertEqual(self.migrate(),result)
    def test_after_secret_retirement_and_expiry_preserves_source_digest(self):
        self.legacy();first=self.migrate()
        import secret_retention as retention
        retention.initialize(self.db);self.db.execute('BEGIN IMMEDIATE');retention.retire_copies(self.db,first['group'],'test');self.db.execute('COMMIT')
        self.assertNotIn('checkpoint',json.loads(self.db.execute('SELECT joined FROM provider_mls_admission').fetchone()[0]))
        self.assertEqual(self.migrate(),first)
        later=dict.fromkeys(['earliest','latest'],str(int(self.f.time['latest'])+1000))
        self.assertEqual(self.receiver_fixture.accept(__import__('invitation_mime').select(self.wire),time=later),self.receipt)
    def test_fault_and_conflicting_original_receive_leave_no_qualification(self):
        self.legacy();self.message()
        def fail(stage):
            if stage=='after-instance':raise RuntimeError('crash')
        with self.assertRaises(RuntimeError):migrate_signed_initial(self.f.identity,self.f.binary,local_key=self.f.devices[1]['key'],crash=fail)
        self.assertEqual(self.db.execute('SELECT count(*) FROM mls_group_instances').fetchone()[0],0)
        raw=self.db.execute('SELECT evidence FROM mls_receives').fetchone()[0];e=json.loads(raw);e['snapshot']['epoch']='2';self.db.execute('UPDATE mls_receives SET evidence=?',(json.dumps(e),))
        with self.assertRaisesRegex(ValueError,'Ambiguous'):self.migrate()
        self.assertEqual(self.db.execute('SELECT count(*) FROM mls_instance_agreements').fetchone()[0],0)
    def test_changed_historical_agreement_is_not_replaced_from_latest(self):
        self.legacy();self.db.execute("UPDATE mls_application_agreement SET application=?",('{"envelopeVersion":"1","operations":["message"]}',))
        with self.assertRaisesRegex(ValueError,'agreement source'):self.migrate()
        self.assertEqual(self.db.execute('SELECT count(*) FROM mls_group_instances').fetchone()[0],0)
    def test_actual_process_exits_atomic_migration(self):
        self.legacy();before=self.db.execute('SELECT revision,snapshot FROM mls_checkpoint').fetchone()
        for point in ('before-commit','after-commit'):
            process=multiprocessing.get_context('spawn').Process(target=migrate_child,args=(self.f.path,self.f.binary,self.f.devices[1]['key'],point));process.start();process.join(15)
            if process.is_alive():process.terminate();process.join();self.fail('Child timeout')
            self.assertEqual(process.exitcode,86)
            self.assertEqual(self.db.execute('SELECT count(*) FROM mls_group_instances').fetchone()[0],int(point=='after-commit'))
        self.assertEqual(self.db.execute('SELECT revision,snapshot FROM mls_checkpoint').fetchone(),before)
        self.assertEqual(self.migrate()['provenance'],'signed-initial-admission')
    def test_current_signed_send_revocation_does_not_rewrite_history(self):
        self.legacy();self.message(True);d=self.f.devices[0];r=d['record']
        binding=json.loads(base64.b64decode(r['binding']));binding.update(record='f'*32,roles=['receive','enroll','revoke'],authority={'kind':'state','digest':d['state']});raw=encode_event(binding)
        state=json.loads(base64.b64decode(r['state']));state.update(record='9'*32,revision='1',previous=[d['state']],bindings=[dict(device=d['device'],digest=hashlib.sha256(raw).hexdigest())]);payload=encode_event(state)
        bundle=dict(version='0',purpose='identity-bundle',principal=d['principal'],states=[dict(payload=base64.b64encode(payload).decode(),signature=sign(self.f.binary,d,'email-next/identity-state/v0',payload)),dict(payload=r['state'],signature=r['stateProof'])],bindings=[dict(payload=base64.b64encode(raw).decode(),authorization=sign(self.f.binary,d,'email-next/device-binding/v0',raw),possession=sign(self.f.binary,d,'email-next/device-possession/v0',raw)),dict(payload=r['binding'],authorization=r['authorization'],possession=r['possession'])])
        self.assertEqual(self.f.identity.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(payload).hexdigest(),time=self.f.time)['status'],'accepted-unverified')
        self.migrate();result=self.receiver.reevaluate(time=self.f.time,trust_policy='allow-unverified')
        self.assertTrue(all(s.startswith('held:') for s in result['states'].values()));self.assertEqual(self.db.execute('SELECT count(*) FROM contributions').fetchone()[0],0)

    def seed_retained(self,wrong=False):
        import secret_retention as retention
        retention.initialize(self.db)
        group,raw=self.db.execute('SELECT group_id,snapshot FROM mls_checkpoint').fetchone()
        snapshot=call(self.f.binary.with_name('group-transitions'),op='inspect',checkpoint=json.loads(raw),group=group,key=self.f.devices[1]['key'])['snapshot']
        snapshot['members']=[str(m['index'])+':'+m['identity']+':'+m['key'] for m in snapshot['members']]
        if wrong:snapshot['epoch']='2'
        encoded=json.dumps(snapshot).encode()
        self.db.execute('INSERT INTO mls_retained_epoch VALUES(?,?,?,?)',('configured:'+group,group,snapshot['epoch'],encoded))
        return encoded
    def test_retained_epoch_storage_key_requalified_without_provenance_invention(self):
        self.legacy();raw=self.seed_retained();result=self.migrate()
        self.assertEqual(self.db.execute('SELECT instance,snapshot FROM mls_retained_epoch').fetchone(),(result['instance'],raw))
        self.assertEqual(result['provenance'],'signed-initial-admission');self.assertEqual(self.migrate(),result)
    def test_unexplained_retained_epoch_fails_atomically(self):
        self.legacy();self.seed_retained(wrong=True)
        with self.assertRaisesRegex(ValueError,'retained epoch'):self.migrate()
        self.assertEqual(self.db.execute('SELECT count(*) FROM mls_group_instances').fetchone()[0],0)
    def test_missing_public_receipt_cannot_be_invented_from_cached_join(self):
        self.legacy();self.db.execute('DELETE FROM application_invitation_acceptance')
        with self.assertRaisesRegex(ValueError,'Unique signed'):self.migrate()
        self.assertEqual(self.db.execute('SELECT count(*) FROM mls_group_instances').fetchone()[0],0)
    def test_changed_qualified_agreement_fails_exact_migration_retry(self):
        self.legacy();self.migrate();self.db.execute("UPDATE mls_instance_agreements SET application='{}'")
        with self.assertRaisesRegex(ValueError,'Conflicting instance agreements'):self.migrate()
