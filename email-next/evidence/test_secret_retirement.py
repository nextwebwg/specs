import json
import hashlib
import multiprocessing
import os
import unittest
from unittest.mock import patch
import test_application_invitation_release as fixture
from secret_retention import SecretRetention
from test_secret_retention import POLICY
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP

class AdmissionRetirementTests(unittest.TestCase):
    setUp=fixture.InitialReleaseTests.setUp
    tearDown=fixture.InitialReleaseTests.tearDown
    prepare=fixture.InitialReleaseTests.prepare
    accept=fixture.InitialReleaseTests.accept
    def test_consumed_package_and_joined_maps_retire_without_changing_receipt(self):
        wire=self.prepare();accepted=self.accept(wire)
        receiver=self.receiver_fixture.admission.receiver
        self.assertEqual(SecretRetention(receiver).configure(POLICY,time=self.f.time),'maintained')
        device,joined,invitation=receiver.db.execute('SELECT device,joined,invitation FROM provider_mls_admission').fetchone()
        for raw in (device,joined):
            self.assertNotIn('checkpoint',json.loads(raw));self.assertEqual(json.loads(raw)['privateState'],'retired')
        self.assertIsNotNone(invitation)
        result=json.loads(receiver.db.execute('SELECT result FROM application_admissions').fetchone()[0]);self.assertNotIn('checkpoint',result)
        self.assertEqual(self.accept(wire),accepted)
    def test_uncertain_exact_ciphertext_retry_survives_logical_retirement(self):
        wire=self.prepare();smtp=LocalSMTP()
        child=multiprocessing.get_context('spawn').Process(target=fixture.submit_child,args=(self.path,self.f.binary,smtp.port,self.f.time,'after-final-response'))
        child.start();child.join(20);self.assertEqual(child.exitcode,88);smtp.done()
        SecretRetention(self.sender.receiver).configure(POLICY,time=self.f.time)
        with SenderWorker(self.sender) as worker:
            with patch('sender_worker.smtplib.SMTP',side_effect=AssertionError('No implicit retry')):
                with self.assertRaisesRegex(ValueError,'Uncertain'):worker.submit_initial_invitation('invitation1',port=1,time=self.f.time)
            again=LocalSMTP();result=worker.submit_initial_invitation('invitation1',port=again.port,time=self.f.time,retry_uncertain=True);again.done()
        self.assertEqual(result['state'],'accepted');self.assertEqual(again.wire,wire)


def crash_retire(path,binary,time,point):
    from identity_store import IdentityStore
    from mls_receive import MlsReceive
    store=IdentityStore(path);receiver=MlsReceive(store,binary)
    SecretRetention(receiver).configure(dict(POLICY,maxCheckpointBytes=1),time=time,expected_revision=1,crash=lambda stage:os._exit(91) if stage==point else None)
    os._exit(92)

class RetirementCrashTests(unittest.TestCase):
    import test_secret_retention as fixtures
    application_profile=fixtures.SecretRetentionTests.application_profile
    setUp=fixtures.SecretRetentionTests.setUp
    tearDown=fixtures.SecretRetentionTests.tearDown
    store=fixtures.SecretRetentionTests.store
    enable=fixtures.SecretRetentionTests.enable
    def test_real_process_exit_before_and_after_logical_retirement_commit(self):
        self.enable();before=hashlib.sha256(self.ga.db.execute('SELECT snapshot FROM mls_checkpoint').fetchone()[0]).digest()
        for point,retired in [('before-retention-commit',False),('after-retention-commit',True)]:
            child=multiprocessing.get_context('spawn').Process(target=crash_retire,args=(self.root/'a.sqlite',self.provider.with_name('receive-staged'),self.time,point))
            child.start();child.join(15);self.assertEqual(child.exitcode,91)
            if not retired:self.assertEqual(hashlib.sha256(self.ga.db.execute('SELECT snapshot FROM mls_checkpoint').fetchone()[0]).digest(),before)
            else:self.assertNotEqual(hashlib.sha256(self.ga.db.execute('SELECT snapshot FROM mls_checkpoint').fetchone()[0]).digest(),before)
        self.assertTrue(self.ga.db.execute('SELECT 1 FROM mls_retention_retired').fetchone())
