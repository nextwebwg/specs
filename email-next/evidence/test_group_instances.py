import json
import unittest
import test_group_removal as fixture
from group_instances import GroupInstances,current
from provider_mls import call
from event_encoding import encode_event

class InstanceMigrationTests(unittest.TestCase):
    setUp=fixture.RemovalTests.setUp
    tearDown=fixture.RemovalTests.tearDown
    store=fixture.RemovalTests.store
    prepared=fixture.RemovalTests.prepared
    remove=fixture.RemovalTests.remove
    def retained(self):
        event=dict(version='0',purpose='contribution',event='6'*32,conversation='2'*32,principal=self.c['principal'],audience=sorted([self.a['principal'],self.b['principal'],self.c['principal']]),operation=dict(kind='answer',question=dict(principal=self.c['principal'],conversation='2'*32,event='5'*32),option='7'*32,replaces=[]))
        state=self.gc.live();sent=call(self.provider,op='send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.c['key'],application=encode_event(event).hex())
        self.assertEqual(self.ga.receiver.receive(bytes.fromhex(sent['wire']),time=self.time,trust_policy='allow-unverified')['status'],'pending')
    def test_actual_pending_evidence_qualified_and_exact_migration_retry(self):
        self.retained();self.remove(self.c);migration=GroupInstances(self.ga.db)
        result=migration.migrate_configured(self.ga);self.assertEqual(migration.migrate_configured(self.ga),result)
        self.assertEqual(current(self.ga.db,result['group']),result)
        self.assertEqual(self.ga.db.execute('SELECT instance FROM mls_receive_instance').fetchone()[0],result['instance'])
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM mls_episode_instance').fetchone()[0],3)
        self.assertEqual(list(self.ga.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')['states'].values()),['held:membership-episode'])
    def test_inactive_terminal_migrates_without_fabricated_final_context(self):
        removal=self.remove(self.c);self.gc.receive(bytes.fromhex(removal['wire']),allowed=set(),time=self.time)
        result=GroupInstances(self.gc.db).migrate_configured(self.gc)
        self.assertEqual(result['status'],'inactive')
        self.assertEqual(self.gc.db.execute('SELECT count(*) FROM gt_decision').fetchone()[0],0)
    def test_fault_after_instance_write_rolls_back_all_qualification(self):
        self.retained();migration=GroupInstances(self.ga.db)
        def fail(stage):
            if stage=='after-instance':raise RuntimeError('crash')
        with self.assertRaises(RuntimeError):migration.migrate_configured(self.ga,crash=fail)
        for table in ['mls_group_instances','mls_checkpoint_instance','mls_episode_instance','mls_receive_instance','mls_instance_schema']:
            self.assertEqual(self.ga.db.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
        self.assertEqual(migration.migrate_configured(self.ga)['status'],'active')
    def test_ambiguous_receive_epoch_fails_atomically(self):
        self.retained();raw=self.ga.db.execute('SELECT evidence FROM mls_receives').fetchone()[0];value=json.loads(raw)
        value['snapshot']['epoch']='999';value['processed']['epoch']='999'
        self.ga.db.execute('UPDATE mls_receives SET evidence=?',(json.dumps(value),))
        migration=GroupInstances(self.ga.db)
        with self.assertRaisesRegex(ValueError,'Ambiguous retained'):migration.migrate_configured(self.ga)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM mls_group_instances').fetchone()[0],0)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM mls_episode_instance').fetchone()[0],0)
    def test_missing_initial_evidence_is_not_inferred_from_current_roster(self):
        self.ga.db.execute("UPDATE mls_membership_episode SET admission=?",('configured-install:'+'f'*64,))
        migration=GroupInstances(self.ga.db)
        with self.assertRaisesRegex(ValueError,'installation snapshot'):migration.migrate_configured(self.ga)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM mls_group_instances').fetchone()[0],0)

    def test_terminal_is_qualified_after_migration(self):
        migration=GroupInstances(self.gc.db);result=migration.migrate_configured(self.gc)
        removal=self.remove(self.c);self.gc.receive(bytes.fromhex(removal['wire']),allowed=set(),time=self.time)
        self.assertEqual(current(self.gc.db,result['group'])['status'],'inactive')
        self.assertEqual(self.gc.db.execute('SELECT terminal_decision FROM mls_group_instances').fetchone()[0],self.gc.db.execute('SELECT decision FROM mls_group_inactive').fetchone()[0])
    def test_new_receive_mapping_is_in_same_transaction(self):
        result=GroupInstances(self.ga.db).migrate_configured(self.ga);self.retained()
        self.assertEqual(self.ga.db.execute('SELECT instance FROM mls_receive_instance').fetchone()[0],result['instance'])
