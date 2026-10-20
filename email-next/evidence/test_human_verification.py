import hashlib,json,unittest
import test_client_onboarding as fixture
from human_verification import HumanVerification,resolve_locked
class HumanComparison(unittest.TestCase):
    setUp=fixture.Onboarding.setUp;tearDown=fixture.Onboarding.tearDown;wire=fixture.Onboarding.wire;ingest=fixture.Onboarding.ingest
    def session(self):
        self.ingest(mode='verification-required')
        self.verifier=HumanVerification(self.identity,account='local-test-profile',local_principal=self.f.devices[1]['principal'])
        return self.verifier.begin(hashlib.sha256(self.wire()).hexdigest(),time=self.f.time,session_expires=str(int(self.f.time['latest'])+60))
    def confirm(self,session,**overrides):
        options=dict(channel='in-person',time=self.f.time,not_before=self.f.time['earliest'],not_after=str(int(self.f.time['latest'])+600),continuity='ordinary-authorized-descendants');options.update(overrides)
        return self.verifier.confirm('comparison1',session['session'],session['comparison'],**options)
    def test_exact_comparison_pins_and_associates_atomically(self):
        session=self.session();self.assertEqual(self.identity.db.execute('SELECT count(*) FROM pins').fetchone()[0],0)
        result=self.confirm(session);self.assertEqual(result['status'],'verified-for-use');self.assertEqual(result['mechanism'],'human-comparison-v0');self.assertFalse(result['sendAuthorized'])
        self.assertEqual(self.confirm(session),result)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM human_verification_evidence').fetchone()[0],1)
        plan=self.client.targets(session['comparison']['mailbox'],target_policy='evidenced-devices',time=self.f.time,mode='verification-required')
        self.assertEqual(plan['status'],'ready-verified');self.assertEqual(plan['verification']['evidence'],result['evidence'])
        self.verifier.withdraw(result['evidence'],expected_revision=1)
        self.assertEqual(self.client.targets(session['comparison']['mailbox'],target_policy='evidenced-devices',time=self.f.time,mode='verification-required')['status'],'verification-required')
    def test_comparison_mismatch_and_same_channel_cannot_pin(self):
        session=self.session();bad=dict(session,comparison=dict(session['comparison'],stateDigest='0'*64))
        with self.assertRaisesRegex(ValueError,'mismatch'):self.confirm(bad)
        with self.assertRaisesRegex(ValueError,'Independent'):self.confirm(session,channel='same-email')
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM pins').fetchone()[0],0)
    def test_expired_session_and_crash_roll_back(self):
        session=self.session();later={k:str(int(v)+61) for k,v in self.f.time.items()}
        with self.assertRaisesRegex(ValueError,'expired'):self.confirm(session,time=later)
        with self.assertRaises(RuntimeError):self.confirm(session,crash=lambda _:(_ for _ in ()).throw(RuntimeError('crash')))
        for table in ('pins','mailbox_associations','human_verification_evidence'):self.assertEqual(self.identity.db.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
        self.assertEqual(self.confirm(session)['status'],'verified-for-use')
    def test_account_scope_and_evidence_expiry(self):
        session=self.session();self.confirm(session)
        with self.assertRaisesRegex(ValueError,'Different local'):HumanVerification(self.identity,account='other',local_principal=self.f.devices[1]['principal'])
        self.identity.db.execute('BEGIN')
        try:
            later={k:str(int(v)+601) for k,v in self.f.time.items()}
            self.assertEqual(resolve_locked(self.identity,session['comparison']['mailbox'],session['comparison']['principal'],later)['status'],'verification-required')
            self.assertEqual(resolve_locked(self.identity,'alias@example.invalid',session['comparison']['principal'],self.f.time)['status'],'verification-required')
        finally:self.identity.db.execute('ROLLBACK')

    def test_changed_identity_snapshot_prevents_confirmation(self):
        session=self.session();self.ingest('other-decision')
        with self.assertRaisesRegex(ValueError,'snapshot changed'):self.confirm(session)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM human_verification_evidence').fetchone()[0],0)

    def test_ordinary_successor_scope_and_fork_hold(self):
        import base64,hashlib
        from test_group_transitions import enroll
        from provider_mls import make_device,sign
        from event_encoding import encode_event
        session=self.session();self.confirm(session)
        device=self.f.devices[0];phone=make_device(self.f.binary,1,7);bundle,head=enroll(self.f.binary,device,phone)
        self.assertEqual(self.identity.accept_successor(encode_event(bundle),candidate_digest=head,time=self.f.time)['status'],'accepted-unverified')
        self.identity.db.execute('BEGIN')
        try:self.assertEqual(resolve_locked(self.identity,session['comparison']['mailbox'],device['principal'],self.f.time)['status'],'verified-for-use')
        finally:self.identity.db.execute('ROLLBACK')
        state=json.loads(base64.b64decode(bundle['states'][0]['payload']));state['record']='c'*32;raw=encode_event(state);bundle['states'][0]=dict(payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,device,'email-next/identity-state/v0',raw))
        self.identity.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(raw).hexdigest(),time=self.f.time)
        self.identity.db.execute('BEGIN')
        try:self.assertEqual(resolve_locked(self.identity,session['comparison']['mailbox'],device['principal'],self.f.time)['status'],'verification-conflicted')
        finally:self.identity.db.execute('ROLLBACK')
    def test_anchor_only_and_own_mailbox_scope(self):
        from test_group_transitions import enroll
        from provider_mls import make_device
        from event_encoding import encode_event
        session=self.session();self.confirm(session,continuity='anchor-only');device=self.f.devices[0]
        bundle,head=enroll(self.f.binary,device,make_device(self.f.binary,1,7));self.identity.accept_successor(encode_event(bundle),candidate_digest=head,time=self.f.time)
        self.identity.observe(self.f.devices[1]['record'],first_contact_policy='allow-unverified')
        self.identity.db.execute('BEGIN')
        try:
            self.assertEqual(resolve_locked(self.identity,session['comparison']['mailbox'],device['principal'],self.f.time)['status'],'verification-required')
            self.assertEqual(resolve_locked(self.identity,'arbitrary@example.invalid',self.f.devices[1]['principal'],self.f.time)['status'],'verification-required')
        finally:self.identity.db.execute('ROLLBACK')

if __name__=='__main__':unittest.main()
