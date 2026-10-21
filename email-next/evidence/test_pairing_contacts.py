"""Actual contact-store export -> encrypted pairing setup -> live trust lookup."""
import copy
import hashlib
import json
import base64
import unittest
from unittest.mock import patch

import test_pairing_setup as fixture
from pairing_contacts import PairedContacts
from pairing_setup import b64,sha,unpack
from provider_mls import make_device,advertisement,sign
from event_encoding import encode_event
from test_discovery_mime import message
from human_verification import resolve_locked


class PairedContactTests(unittest.TestCase):
    tearDown=fixture.PairingSetupTests.tearDown
    request=fixture.PairingSetupTests.request
    commit=fixture.PairingSetupTests.commit
    pair=fixture.PairingSetupTests.pair
    row=fixture.PairingSetupTests.row
    release=fixture.PairingSetupTests.release
    resign=fixture.PairingSetupTests.resign
    def setUp(self):
        fixture.PairingSetupTests.setUp(self)
        self.old_contacts=PairedContacts(self.source);self.new_contacts=PairedContacts(self.target)
        self.friend=make_device(self.binary,4,5);self.address='friend@example.invalid'
        wrapper=advertisement(self.binary,self.friend,self.address)
        root=message(encode_event(wrapper));root['From']=self.address;self.mail=root.as_bytes()
        client=self.old_contacts.verifier.onboarding
        client.ingest('old-introduction',[self.mail],mode='verification-required',target_policy='all-authorized-devices',policy_revision='selected',time=self.time)
        session=self.old_contacts.verifier.begin(hashlib.sha256(self.mail).hexdigest(),time=self.time,session_expires=str(int(self.time['latest'])+60))
        self.confirmed=self.old_contacts.verifier.confirm('old-device-only-comparison',session['session'],session['comparison'],channel='in-person',time=self.time,not_before=self.time['earliest'],not_after=str(int(self.time['latest'])+600),continuity='ordinary-authorized-descendants')
        self.settings=dict(self.preferences,trust='require-verification')
        self.old_contacts.set_local_policy('',self.settings)
        self.selected=self.old_contacts.snapshot([self.address])

    def staged(self):
        response=self.release();self.target.stage(response,self.key,time=self.time);return response
    def resolve(self):
        self.stores[1].db.execute('BEGIN')
        try:return resolve_locked(self.stores[1],self.address,self.friend['principal'],self.time)
        finally:self.stores[1].db.execute('ROLLBACK')
    def install(self,**kwargs):return self.new_contacts.install_contact(self.transfer,self.address,time=self.time,**kwargs)

    def test_actual_export_import_inherits_verification_without_another_comparison(self):
        self.assertEqual(self.selected['contacts'][0]['verification'][0]['originDevice'],self.a['device'])
        self.staged();self.key.unlink();self.assertEqual(self.install()['status'],'installed')
        self.assertEqual(self.resolve()['status'],'verified-for-use')
        self.assertEqual(self.stores[1].db.execute('SELECT count(*) FROM human_verification_sessions').fetchone()[0],0)
        self.assertEqual(self.stores[1].db.execute('SELECT count(*) FROM onboarding_sources').fetchone()[0],0)
        client=self.new_contacts.verifier.onboarding
        client.ingest('new-fresh-evidence',[self.mail],mode='automatic-unverified-continuity',target_policy='all-authorized-devices',policy_revision='inherited',time=self.time)
        plan=client.targets(self.address,target_policy='all-authorized-devices',time=self.time,mode='verification-required')
        self.assertEqual(plan['status'],'ready-verified');self.assertEqual(plan['devices'],[self.friend['device']])
        self.assertEqual(self.install()['status'],'installed')
        receipt=self.new_contacts.finish(self.transfer,time=self.time)
        self.assertEqual(unpack(receipt,'receipt')[1]['result'],'installed')
        self.assertEqual(self.new_contacts.finish(self.transfer,time=self.time),receipt)

    def test_onward_export_preserves_original_comparison_identity(self):
        self.staged();self.install();self.new_contacts.finish(self.transfer,time=self.time)
        exported=self.new_contacts.snapshot([self.address]);original=self.selected['contacts'][0]['verification'][0]
        self.assertEqual(exported['contacts'][0]['verification'],[original])
        self.assertEqual(original['id'],self.confirmed['evidence'])
        self.assertEqual(original['originDevice'],self.a['device'])

    def test_withdrawn_verification_does_not_become_current(self):
        self.old_contacts.verifier.withdraw(self.confirmed['evidence'],expected_revision=1)
        self.selected=self.old_contacts.snapshot([self.address]);self.staged();self.install();self.new_contacts.finish(self.transfer,time=self.time)
        self.assertEqual(self.resolve()['status'],'verification-required')
        self.assertEqual(self.selected['contacts'][0]['verification'][0]['status'],'withdrawn')
        self.assertEqual(self.new_contacts.snapshot([self.address])['contacts'][0]['verification'][0]['revision'],'2')

    def test_original_verification_expiry_is_preserved(self):
        self.staged();self.install()
        later=dict.fromkeys(('earliest','latest'),str(int(self.time['latest'])+601))
        self.stores[1].db.execute('BEGIN')
        try:self.assertEqual(resolve_locked(self.stores[1],self.address,self.friend['principal'],later)['status'],'verification-required')
        finally:self.stores[1].db.execute('ROLLBACK')

    def test_later_local_withdrawal_survives_another_source_transfer(self):
        self.staged();self.install();self.new_contacts.finish(self.transfer,time=self.time)
        inherited=self.resolve()['evidence'];self.new_contacts.verifier.withdraw(inherited,expected_revision=1)
        import subprocess
        key=self.root/'another-setup-key';subprocess.run(['/opt/homebrew/bin/age-keygen','-o',str(key)],capture_output=True,check=True)
        recipient=subprocess.run(['/opt/homebrew/bin/age-keygen','-y',str(key)],capture_output=True,check=True).stdout.strip().decode()
        transfer='c'*32;request=self.target.request(transfer,self.session,recipient,not_before=self.time['latest'],not_after=str(int(self.time['latest'])+30),time=self.time)
        response=self.source.release(request,self.selected,time=self.time);self.target.stage(response,key,time=self.time)
        self.assertEqual(self.new_contacts.install_contact(transfer,self.address,time=self.time)['status'],'installed')
        self.assertEqual(self.resolve()['status'],'verification-required')
        self.assertEqual(self.stores[1].db.execute('SELECT revision,status FROM human_verification_evidence WHERE id=?',(inherited,)).fetchone(),(2,'withdrawn'))

    def test_time_spent_validating_history_cannot_extend_installation_deadline(self):
        self.staged()
        with patch('pairing_setup.monotonic_ns',side_effect=[0,31000000000]):
            self.assertEqual(self.install()['status'],'held')
        self.assertIsNone(self.stores[1].current_state(self.friend['principal'])['head'])
        self.assertIsNone(self.new_contacts.associations._current(self.address))

    def fresh_stage(self,selected):
        import subprocess,uuid
        transfer=uuid.uuid4().hex;key=self.root/('setup-'+transfer)
        subprocess.run(['/opt/homebrew/bin/age-keygen','-o',str(key)],capture_output=True,check=True)
        recipient=subprocess.run(['/opt/homebrew/bin/age-keygen','-y',str(key)],capture_output=True,check=True).stdout.strip().decode()
        request=self.target.request(transfer,self.session,recipient,not_before=self.time['latest'],not_after=str(int(self.time['latest'])+30),time=self.time)
        response=self.source.release(request,selected,time=self.time);self.target.stage(response,key,time=self.time)
        return transfer

    def test_comparison_cannot_be_extended_to_another_address(self):
        self.staged();self.install()
        changed=copy.deepcopy(self.selected);changed['contacts'][0]['mailbox']='alias@example.invalid'
        transfer=self.fresh_stage(changed)
        result=self.new_contacts.install_contact(transfer,'alias@example.invalid',time=self.time)
        self.assertEqual(result['status'],'held');self.assertIsNone(self.new_contacts.associations._current('alias@example.invalid'))
        self.assertEqual(self.resolve()['status'],'verified-for-use')
        # A single selection with this contradictory provenance is invalid before release.
        changed=copy.deepcopy(self.selected);alias=copy.deepcopy(changed['contacts'][0]);alias['mailbox']='alias@example.invalid'
        changed['contacts']=sorted(changed['contacts']+[alias],key=lambda c:c['mailbox'])
        from pairing_setup import configuration
        with self.assertRaises(ValueError):configuration(changed)

    def test_comparison_dates_cannot_be_renewed_under_the_same_origin_identifier(self):
        self.staged();self.install();ident=self.resolve()['evidence']
        before=self.stores[1].db.execute('SELECT not_after,record FROM human_verification_evidence WHERE id=?',(ident,)).fetchone()
        changed=copy.deepcopy(self.selected);proof=changed['contacts'][0]['verification'][0]
        proof.update(revision='2',notAfter=str(int(proof['notAfter'])+600))
        transfer=self.fresh_stage(changed)
        self.assertEqual(self.new_contacts.install_contact(transfer,self.address,time=self.time)['status'],'held')
        self.assertEqual(self.stores[1].db.execute('SELECT not_after,record FROM human_verification_evidence WHERE id=?',(ident,)).fetchone(),before)

    def test_uint64_revision_survives_native_sqlite_without_precision_loss(self):
        self.selected['contacts'][0]['verification'][0].update(status='withdrawn',revision=str(2**64-2))
        self.staged();self.assertEqual(self.install()['status'],'installed');self.new_contacts.finish(self.transfer,time=self.time)
        proof=self.new_contacts.snapshot([self.address])['contacts'][0]['verification'][0]
        self.assertEqual(proof['revision'],str(2**64-2));self.assertEqual(self.resolve()['status'],'verification-required')

    def test_large_revision_withdrawal_remains_exact_and_exhaustion_cannot_prevent_it(self):
        self.selected['contacts'][0]['verification'][0]['revision']=str(2**64-1)
        self.staged();self.install();self.new_contacts.finish(self.transfer,time=self.time)
        result=self.resolve();self.assertEqual(result['revision'],str(2**64-1))
        self.new_contacts.verifier.withdraw(result['evidence'],expected_revision=2**64-1)
        self.assertEqual(self.resolve()['status'],'verification-required')
        proof=self.new_contacts.snapshot([self.address])['contacts'][0]['verification'][0]
        self.assertEqual((proof['status'],proof['revision']),('withdrawn',str(2**64-1)))

    def test_earlier_withdrawal_is_terminal_despite_a_larger_accepted_bookkeeping_revision(self):
        self.selected['contacts'][0]['verification'][0]['revision']='5'
        self.staged();self.install()
        changed=copy.deepcopy(self.selected);changed['contacts'][0]['verification'][0].update(status='withdrawn',revision='2')
        transfer=self.fresh_stage(changed)
        self.assertEqual(self.new_contacts.install_contact(transfer,self.address,time=self.time)['status'],'installed')
        self.assertEqual(self.resolve()['status'],'verification-required')

    def test_explicit_local_defaults_are_not_weakened_for_a_new_contact(self):
        stronger=dict(self.settings,freshness='live-confirmation',maximumAge='20')
        self.new_contacts.set_local_policy('',stronger);self.staged()
        self.assertEqual(self.install()['status'],'held')
        self.assertIsNone(self.stores[1].current_state(self.friend['principal'])['head'])
        self.assertEqual(json.loads(self.stores[1].db.execute("SELECT policy FROM pairing_contact_policies WHERE mailbox='' ").fetchone()[0]),stronger)

    def test_contact_installation_and_receipt_survive_database_reopen(self):
        self.staged();self.install();receipt=self.new_contacts.finish(self.transfer,time=self.time)
        from identity_store import IdentityStore
        from remote_pairing import Pairing
        from pairing_setup import SetupTransfer
        self.stores[1].close();self.stores[1]=IdentityStore(self.root/'unpaired.sqlite')
        self.target=SetupTransfer(Pairing(self.stores[1],account='local-account'),self.b,self.binary,age='/opt/homebrew/bin/age',staging_parent=self.root)
        self.new_contacts=PairedContacts(self.target)
        self.assertEqual(self.resolve()['status'],'verified-for-use')
        self.assertEqual(self.new_contacts.finish(self.transfer,time=self.time),receipt)
        self.assertEqual(self.install()['status'],'installed')

    def test_local_association_generation_is_not_copied_from_the_source(self):
        source=self.old_contacts.associations
        for decision,kind,generation in [('d'*32,'disable','1'),('e'*32,'enable','2')]:
            source.decide(decision_id=decision,mailbox=self.address,expected_generation=generation,kind=kind,principal=self.friend['principal'],actor='local-user',policy_revision='local-settings',trust_policy='allow-unverified',time=self.time)
        self.selected=self.old_contacts.snapshot([self.address]);self.assertEqual(self.selected['contacts'][0]['generation'],'3')
        self.staged();self.install()
        self.assertEqual(self.new_contacts.associations._current(self.address)['generation'],'1')
        self.assertEqual(self.stores[1].db.execute('SELECT source_generation FROM pairing_contact_origins').fetchone()[0],'3')

    def test_one_held_contact_does_not_install_it_or_prevent_another_contact(self):
        other=make_device(self.binary,8,9);r=other['record']
        bundle=dict(version='0',purpose='identity-bundle',principal=other['principal'],states=[dict(payload=r['state'],signature='0'*128)],bindings=[dict(payload=r['binding'],authorization=r['authorization'],possession=r['possession'])])
        self.selected['contacts'].append(dict(mailbox='later@example.invalid',principal=other['principal'],anchor=other['state'],head=other['state'],bundle=b64(encode_event(bundle)),generation='1',enabled=True,verification=[],policy=self.settings))
        self.staged();self.assertEqual(self.install()['status'],'installed')
        self.assertEqual(self.new_contacts.install_contact(self.transfer,'later@example.invalid',time=self.time)['status'],'held')
        self.assertEqual(self.resolve()['status'],'verified-for-use')
        self.assertIsNone(self.stores[1].current_state(other['principal'])['head'])
        with self.assertRaises(ValueError):self.new_contacts.finish(self.transfer,time=self.time)

    def test_existing_different_peer_pin_holds_without_overwriting_it(self):
        other=make_device(self.binary,4,9)
        self.stores[1].observe(other['record'],first_contact_policy='allow-unverified')
        self.staged();self.assertEqual(self.install()['status'],'held')
        self.assertEqual(self.stores[1].current_state(self.friend['principal'])['head'],other['state'])
        self.assertIsNone(self.new_contacts.associations._current(self.address))
        with self.assertRaises(ValueError):self.new_contacts.finish(self.transfer,time=self.time)

    def test_local_policy_cannot_be_weakened_by_the_transfer(self):
        strong=dict(self.settings,freshness='live-confirmation',maximumAge='20')
        self.new_contacts.set_local_policy(self.address,strong)
        self.staged();self.assertEqual(self.install()['status'],'held')
        value=self.stores[1].db.execute('SELECT policy FROM pairing_contact_policies WHERE mailbox=?',(self.address,)).fetchone()[0]
        self.assertEqual(json.loads(value),strong)
        self.assertIsNone(self.stores[1].current_state(self.friend['principal'])['head'])

    def test_invalid_peer_proof_does_not_install_even_inside_a_valid_own_device_response(self):
        bundle=json.loads(base64.b64decode(self.selected['contacts'][0]['bundle']))
        bundle['states'][0]['signature']='0'*128
        self.selected['contacts'][0]['bundle']=b64(encode_event(bundle))
        self.staged();self.assertEqual(self.install()['status'],'held')
        self.assertIsNone(self.stores[1].current_state(self.friend['principal'])['head'])
        self.assertIsNone(self.new_contacts.associations._current(self.address))
        self.assertEqual(self.resolve()['status'],'verification-conflicted')

    def test_contact_commit_crash_does_not_leave_a_partial_pin_or_verification(self):
        self.staged()
        def fail(_):raise RuntimeError('crash')
        with self.assertRaises(RuntimeError):self.install(crash=fail)
        self.assertIsNone(self.stores[1].current_state(self.friend['principal'])['head'])
        self.assertIsNone(self.new_contacts.associations._current(self.address))
        self.assertEqual(self.stores[1].db.execute('SELECT count(*) FROM human_verification_evidence').fetchone()[0],0)
        self.assertEqual(self.install()['status'],'installed')

    def test_valid_existing_peer_fork_is_not_repaired_by_an_older_transfer(self):
        from test_group_transitions import enroll
        phone=make_device(self.binary,4,8);bundle,head=enroll(self.binary,self.friend,phone)
        self.stores[1].observe(self.friend['record'],first_contact_policy='allow-unverified')
        self.assertEqual(self.stores[1].accept_successor(encode_event(bundle),candidate_digest=head,time=self.time)['status'],'accepted-unverified')
        state=json.loads(base64.b64decode(bundle['states'][0]['payload']));state['record']='f'*32;raw=encode_event(state)
        bundle['states'][0]=dict(payload=b64(raw),signature=sign(self.binary,self.friend,'email-next/identity-state/v0',raw))
        self.assertEqual(self.stores[1].accept_successor(encode_event(bundle),candidate_digest=sha(raw),time=self.time)['status'],'conflicted')
        self.staged();self.assertEqual(self.install()['status'],'held')
        self.assertTrue(self.stores[1].current_state(self.friend['principal'])['conflicted'])
        self.assertIsNone(self.new_contacts.associations._current(self.address))

    def test_installed_receipt_and_defaults_commit_together(self):
        self.staged();self.install()
        def fail(_):raise RuntimeError('crash')
        with self.assertRaises(RuntimeError):self.new_contacts.finish(self.transfer,time=self.time,crash=fail)
        self.assertIsNone(self.stores[1].db.execute("SELECT policy FROM pairing_contact_policies WHERE mailbox='' ").fetchone())
        self.assertEqual(self.stores[1].db.execute('SELECT count(*) FROM pairing_installed_receipts').fetchone()[0],0)
        self.assertEqual(unpack(self.new_contacts.finish(self.transfer,time=self.time),'receipt')[1]['result'],'installed')

    def test_newer_local_removal_is_preserved_over_an_older_source_snapshot(self):
        from test_group_transitions import enroll
        phone=make_device(self.binary,4,8);bundle,head=enroll(self.binary,self.friend,phone)
        self.stores[1].observe(self.friend['record'],first_contact_policy='allow-unverified')
        self.assertEqual(self.stores[1].accept_successor(encode_event(bundle),candidate_digest=head,time=self.time)['status'],'accepted-unverified')
        state=json.loads(base64.b64decode(bundle['states'][0]['payload']));state.update(record='d'*32,revision='2',previous=[head],revoked=[phone['device']],bindings=[r for r in state['bindings'] if r['device']!=phone['device']])
        raw=encode_event(state);bundle['states'].insert(0,dict(payload=b64(raw),signature=sign(self.binary,self.friend,'email-next/identity-state/v0',raw)))
        latest=sha(raw);self.assertEqual(self.stores[1].accept_successor(encode_event(bundle),candidate_digest=latest,time=self.time)['status'],'accepted-unverified')
        self.staged();self.assertEqual(self.install()['status'],'installed')
        self.assertEqual(self.stores[1].current_state(self.friend['principal'])['head'],latest)
        from pairing_contacts import public_chain
        current=json.loads(public_chain(self.stores[1],self.friend['principal'])[2]);tip=next(json.loads(base64.b64decode(s['payload'])) for s in current['states'] if sha(base64.b64decode(s['payload']))==latest)
        self.assertIn(phone['device'],tip['revoked'])

    def test_unauthenticated_staging_or_out_of_scope_contact_cannot_activate(self):
        with self.assertRaises(ValueError):self.install()
        self.staged()
        with self.assertRaises(ValueError):self.new_contacts.install_contact(self.transfer,'other@example.invalid',time=self.time)
        self.assertIsNone(self.new_contacts.associations._current(self.address))

    def test_authenticated_transfer_conflict_holds_both_association_and_inherited_verification(self):
        response=self.staged();self.install();self.assertEqual(self.resolve()['status'],'verified-for-use')
        _,value,_,_=unpack(response,'response');value['ciphertext']=b64(base64.b64decode(value['ciphertext'])+b'\0')
        with self.assertRaises(ValueError):self.target.stage(self.resign(value),self.key,time=self.time)
        self.assertEqual(self.resolve()['status'],'verification-required')
        self.assertEqual(self.new_contacts.associations._current(self.address)['held'],'pairing-transfer-conflict')
        self.assertFalse(self.new_contacts.associations._current(self.address)['enabled'])
        with self.assertRaises(ValueError):self.new_contacts.finish(self.transfer,time=self.time)

if __name__=='__main__':unittest.main()
