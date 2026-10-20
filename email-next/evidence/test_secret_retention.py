"""Real OpenMLS maintenance in disposable fixtures only."""
import json
import hashlib
import unittest
import test_reaction_removal as fixtures
from secret_retention import SecretRetention,maintain_locked,historical_snapshot
from provider_mls import call
from event_encoding import encode_event
from journal_reaction_view import derive_reaction_view

POLICY=dict(maxPastEpochs=2,maxAgeSeconds=3600,maxCheckpointBytes=4*1024*1024,outOfOrderTolerance=8,maximumForwardDistance=32)
class SecretRetentionTests(unittest.TestCase):
    application_profile=fixtures.ReactionRemovalTests.application_profile
    setUp=fixtures.ReactionRemovalTests.setUp
    tearDown=fixtures.ReactionRemovalTests.tearDown
    store=fixtures.ReactionRemovalTests.store
    prepared=fixtures.ReactionRemovalTests.prepared
    def enable(self):
        for g in (self.ga,self.gb,self.gc):self.assertEqual(SecretRetention(g.receiver).configure(POLICY,time=self.time),'maintained')
    def remove(self):
        ident=self.ga.prepare_removal([dict(identity=self.c['identity'],key=self.c['key'])],time=self.time)
        self.ga.decide(ident,allowed=set(),time=self.time)
        return json.loads(self.ga.db.execute('SELECT state FROM gt_decision WHERE digest=?',(ident,)).fetchone()[0])
    def messages(self):
        audience=sorted([self.a['principal'],self.b['principal'],self.c['principal']])
        target=dict(version='1',purpose='contribution',event='5'*32,conversation='2'*32,principal=self.b['principal'],audience=audience,disclosures=[],operation=dict(kind='message',text='Delayed original.',replyTo=[]))
        ref={k:target[k] for k in ('principal','conversation','event')}
        reaction=dict(version='1',purpose='contribution',event='6'*32,conversation='2'*32,principal=self.c['principal'],audience=audience,disclosures=[],operation=dict(kind='reaction',target=ref,emoji='👍'))
        def send(g,d,event):
            state=g.live();return call(self.provider,op='send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=d['key'],application=encode_event(event).hex())
        return ref,send(self.gb,self.b,target),send(self.gc,self.c,reaction)
    def test_delayed_original_target_after_real_removal_and_restart(self):
        self.enable();ref,target,reaction=self.messages()
        self.ga.receiver.receive(bytes.fromhex(reaction['wire']),time=self.time,trust_policy='allow-unverified')
        decision=self.remove()
        self.assertNotIn('checkpoint',decision)
        from mls_receive import MlsReceive
        self.ga.receiver=MlsReceive(self.ga.identity,self.provider.with_name('receive-staged'))
        received=self.ga.receiver.receive(bytes.fromhex(target['wire']),time=self.time,trust_policy='allow-unverified')
        self.assertEqual(received['status'],'projected-context-matched')
        result=self.ga.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')
        self.assertIn('held:membership-episode',result['states'].values())
        self.assertEqual(derive_reaction_view(self.ga.receiver.journal,ref)['active'],[])
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM contributions').fetchone()[0],1)
    def test_age_prunes_actual_secrets_and_clock_rollback_holds(self):
        self.enable();ref,target,reaction=self.messages();self.remove()
        later=dict.fromkeys(('earliest','latest'),str(int(self.time['latest'])+4000))
        SecretRetention(self.ga.receiver).maintain(time=later)
        with self.assertRaisesRegex(ValueError,'clock rollback'):SecretRetention(self.ga.receiver).maintain(time=self.time)
        result=self.ga.receiver.receive(bytes.fromhex(target['wire']),time=later,trust_policy='allow-unverified')
        self.assertEqual(result['status'],'crypto-not-accepted')
    def test_storage_budget_retires_group_and_prunes_candidate_copy(self):
        self.enable();identifier=self.ga.prepare_removal([dict(identity=self.c['identity'],key=self.c['key'])],time=self.time)
        policy=dict(POLICY,maxCheckpointBytes=1)
        self.assertEqual(SecretRetention(self.ga.receiver).configure(policy,time=self.time,expected_revision=1),'retired')
        self.assertIsNone(self.ga.db.execute('SELECT 1 FROM gt_candidate WHERE digest=?',(identifier,)).fetchone())
        self.assertTrue(self.ga.db.execute('SELECT 1 FROM gt_abandoned WHERE digest=?',(identifier,)).fetchone())
        self.assertTrue(self.ga.db.execute('SELECT 1 FROM mls_retention_retired').fetchone())
    def test_transaction_failure_preserves_previous_checkpoint_and_policy(self):
        self.enable();before=hashlib.sha256(self.ga.db.execute('SELECT snapshot FROM mls_checkpoint').fetchone()[0]).digest();policy=list(self.ga.db.execute('SELECT * FROM mls_retention_policy'))
        with self.assertRaises(RuntimeError):SecretRetention(self.ga.receiver).configure(dict(POLICY,maxCheckpointBytes=1),time=self.time,expected_revision=1,crash=lambda point:(_ for _ in ()).throw(RuntimeError('crash')))
        self.assertEqual(hashlib.sha256(self.ga.db.execute('SELECT snapshot FROM mls_checkpoint').fetchone()[0]).digest(),before)
        self.assertEqual(list(self.ga.db.execute('SELECT * FROM mls_retention_policy')),policy)

    def test_count_and_generation_limits_use_actual_library_checks(self):
        self.enable();ref,target,reaction=self.messages();self.remove()
        self.assertEqual(SecretRetention(self.ga.receiver).configure(dict(POLICY,maxPastEpochs=0),time=self.time,expected_revision=1),'maintained')
        self.assertEqual(self.ga.receiver.receive(bytes.fromhex(target['wire']),time=self.time,trust_policy='allow-unverified')['status'],'crypto-not-accepted')
        self.assertEqual(self.ga.db.execute('SELECT wire FROM mls_retention_held').fetchone()[0],bytes.fromhex(target['wire']))

    def test_generation_jump_rejected_without_consuming_available_message(self):
        self.enable();SecretRetention(self.ga.receiver).configure(dict(POLICY,maximumForwardDistance=1),time=self.time,expected_revision=1)
        state=self.gb.live();cp=state['checkpoint'];messages=[]
        for number in range(3):
            event=dict(version='1',purpose='contribution',event=str(number+1)*32,conversation='2'*32,principal=self.b['principal'],audience=sorted([self.a['principal'],self.b['principal'],self.c['principal']]),disclosures=[],operation=dict(kind='message',text='Generation '+str(number),replyTo=[]))
            sent=call(self.provider,op='send',checkpoint=cp,group=state['snapshot']['group'],key=self.b['key'],application=encode_event(event).hex());cp=sent['checkpoint'];messages.append(sent)
        self.assertEqual(self.ga.receiver.receive(bytes.fromhex(messages[2]['wire']),time=self.time,trust_policy='allow-unverified')['status'],'crypto-not-accepted')
        self.assertEqual(self.ga.receiver.receive(bytes.fromhex(messages[0]['wire']),time=self.time,trust_policy='allow-unverified')['status'],'projected-context-matched')

    def test_missing_or_conflicting_historical_snapshot_cannot_supply_authority(self):
        from secret_retention import retain_snapshot
        self.enable();ref,target,reaction=self.messages();self.remove()
        group=self.ga.live()['snapshot']['group'];before=historical_snapshot(self.ga.db,group,'1')
        self.ga.db.execute('BEGIN IMMEDIATE')
        try:
            bad=dict(before,predecessor='00')
            with self.assertRaisesRegex(ValueError,'Conflicting'):retain_snapshot(self.ga.db,bad)
        finally:self.ga.db.execute('ROLLBACK')
        # Deliberately unavailable local public evidence is an indexed-boundary
        # fixture, not invented MLS authority or a secret rollback.
        self.ga.db.execute("DELETE FROM mls_retained_epoch WHERE epoch='1'")
        result=self.ga.receiver.receive(bytes.fromhex(target['wire']),time=self.time,trust_policy='allow-unverified')
        self.assertEqual(result['reason'],'historical-context-unavailable')
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM contributions').fetchone()[0],0)

    def test_retired_restart_is_terminal_without_loading_deleted_group(self):
        from mls_receive import MlsReceive
        from unittest.mock import patch
        self.enable();SecretRetention(self.ga.receiver).configure(dict(POLICY,maxCheckpointBytes=1),time=self.time,expected_revision=1)
        restarted=MlsReceive(self.ga.identity,self.provider.with_name('receive-staged'))
        with patch('provider_mls.call',side_effect=AssertionError('Deleted group must not load')):
            self.assertEqual(SecretRetention(restarted).maintain(time=self.time)['status'],'retired')
            self.assertEqual(restarted.receive(b'opaque retained ciphertext',time=self.time,trust_policy='allow-unverified')['status'],'retention-retired')

    def test_exact_library_age_boundary_and_legacy_untimestamped_deletion(self):
        # Test-only timestamp fixtures: real secret bytes and MLS ciphertext stay
        # unchanged. No production path rewrites historical creation timestamps.
        import copy
        self.enable();ref,target,reaction=self.messages();self.remove();state=self.ga.live();stamp=int(self.time['latest'])
        def dated(legacy=False):
            cp=copy.deepcopy(state['checkpoint']);found=0
            for row in cp:
                try:value=json.loads(bytes.fromhex(row[1]))
                except (ValueError,UnicodeError):continue
                if not isinstance(value,dict) or set(value)!={'max_epochs','past_epoch_trees','message_secrets'}:continue
                found+=1;self.assertTrue(value['past_epoch_trees'])
                value['message_secrets']['added_at']={'secs_since_epoch':stamp+100,'nanos_since_epoch':0}
                for old in value['past_epoch_trees']:
                    if legacy:old['message_secrets'].pop('added_at',None)
                    else:old['message_secrets']['added_at']={'secs_since_epoch':stamp,'nanos_since_epoch':0}
                row[1]=json.dumps(value,separators=(',',':')).encode().hex()
            self.assertEqual(found,1);return cp
        def accepted(cp,cutoff):
            maintained=call(self.provider.with_name('retention-staged'),checkpoint=cp,group=state['snapshot']['group'],policy=POLICY,cutoff=cutoff)
            from mls_receive import worker_call,FORMAT
            result=worker_call(self.provider.with_name('receive-staged'),dict(format=FORMAT,checkpoint=maintained['checkpoint'],group=state['snapshot']['group'],wire=target['wire'],allowHistorical=True))
            return result['status']=='authenticated-application'
        self.assertTrue(accepted(dated(),stamp))
        self.assertFalse(accepted(dated(),stamp+1))
        self.assertFalse(accepted(dated(legacy=True),stamp))

    def test_unknown_clock_rejects_without_mutation(self):
        self.enable();before=hashlib.sha256('\n'.join(self.ga.db.iterdump()).encode()).digest()
        for time in ({},None,{'earliest':'unknown','latest':'unknown'}):
            with self.assertRaises(ValueError):SecretRetention(self.ga.receiver).maintain(time=time)
        self.assertEqual(hashlib.sha256('\n'.join(self.ga.db.iterdump()).encode()).digest(),before)

    def test_send_only_and_inactive_endpoint_perform_age_maintenance(self):
        from sender_release import SenderRelease
        from mls_receive import worker_call,FORMAT
        self.enable();ref,target,reaction=self.messages();decision=self.remove()
        self.gc.receive(bytes.fromhex(decision['wire']),allowed=set(),time=self.time)
        for g in (self.ga,self.gc):SecretRetention(g.receiver).configure(dict(POLICY,maxAgeSeconds=0),time=self.time,expected_revision=1)
        later=dict.fromkeys(('earliest','latest'),str(int(self.time['latest'])+2))
        sender=SenderRelease(self.ga.identity,self.provider);sender.configure(expected_revision=0)
        event=dict(version='1',purpose='contribution',event='9'*32,conversation='2'*32,principal=self.a['principal'],audience=sorted([self.a['principal'],self.b['principal']]),disclosures=[],operation=dict(kind='message',text='Send-only activity.',replyTo=[]))
        sender.prepare('sendonly',encode_event(event),key=self.a['key'],envelope_sender='a@example.invalid',recipients=['b@example.invalid'],time=later)
        cp=json.loads(self.ga.db.execute('SELECT snapshot FROM mls_checkpoint').fetchone()[0]);group=decision['after']['group']
        result=worker_call(self.provider.with_name('receive-staged'),dict(format=FORMAT,group=group,checkpoint=cp,wire=target['wire'],allowHistorical=True))
        self.assertNotEqual(result['status'],'authenticated-application')
        self.assertEqual(SecretRetention(self.gc.receiver).maintain(time=later)['status'],'maintained')
        self.assertEqual(self.gc.receiver.receive(b'new ciphertext',time=later,trust_policy='allow-unverified')['status'],'inactive-group')

    def test_control_only_activity_prunes_before_new_candidate(self):
        from mls_receive import worker_call,FORMAT
        self.enable();ref,target,reaction=self.messages();self.remove()
        SecretRetention(self.ga.receiver).configure(dict(POLICY,maxAgeSeconds=0),time=self.time,expected_revision=1)
        later=dict.fromkeys(('earliest','latest'),str(int(self.time['latest'])+2))
        candidate=self.ga.prepare([],time=later);self.ga.decide(candidate,allowed=set(),time=later)
        state=self.ga.live();result=worker_call(self.provider.with_name('receive-staged'),dict(format=FORMAT,group=state['snapshot']['group'],checkpoint=state['checkpoint'],wire=target['wire'],allowHistorical=True))
        self.assertNotEqual(result['status'],'authenticated-application')

    def test_unconsumed_legacy_package_group_map_requires_explicit_migration(self):
        from provider_mls import Admission
        legacy=dict(self.a,checkpoint=self.ga.live()['checkpoint'])
        Admission(self.ga.identity,self.provider).publish_local(legacy)
        before=hashlib.sha256(self.ga.db.execute('SELECT snapshot FROM mls_checkpoint').fetchone()[0]).digest()
        with self.assertRaisesRegex(ValueError,'Unconsumed package carries group secrets'):
            SecretRetention(self.ga.receiver).configure(POLICY,time=self.time)
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM mls_retention_policy').fetchone()[0],0)
        self.assertEqual(hashlib.sha256(self.ga.db.execute('SELECT snapshot FROM mls_checkpoint').fetchone()[0]).digest(),before)
