"""Actual current-suite signatures/packages and local staging, not full conformance."""
import base64
import copy
import json
import hashlib
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from event_encoding import encode_event
from identity_store import IdentityStore
from passive_discovery import decode_passive_discovery
from provider_mls import advertisement, make_device, sign, call
from suite_modules import offers,exchanges,application,QUORUM,select
from suite_discovery8 import LocalIssuance, verify
from sealed_control import native


class SuiteDiscovery8Tests(unittest.TestCase):
    def setUp(self):
        self.binary = Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR']) / 'provider-mls'
        self.device = make_device(self.binary, 1, 2)
        self.time = dict(earliest=str(self.device['time']), latest=str(self.device['time']))
        self.temp = tempfile.TemporaryDirectory()
        self.identity = IdentityStore(Path(self.temp.name) / 'issuer.sqlite')
        self.identity.observe(self.device['record'], first_contact_policy='allow-unverified')
        self.control=native(self.binary.with_name('sealed-control'),op='generate')
        self.device['controlSecret']=self.control
        self.base = advertisement(self.binary, self.device, 'Alice@example.org')
        self.value = json.loads(base64.b64decode(self.base['payload']))
        self.value.update(version='8', notAfter=str(self.device['time']+60), applications=offers(['answers','reactions']), orderingExchanges=exchanges(offers(['answers','reactions'])), keyPackageReceiveUntil=str(self.device['time']+660),controlKey=dict(id=self.control['id'],publicKey=self.control['publicKey'],notBefore=str(self.device['time']-60),notAfter=str(self.device['time']+600),receiveUntil=str(self.device['time']+660)))
        self.issuer = LocalIssuance(self.identity, self.binary)

    def tearDown(self):
        self.identity.close()
        self.temp.cleanup()

    def signed(self, patch_value=None, *, domain='email-next/passive-discovery/v8'):
        value = copy.deepcopy(self.value)
        if patch_value:
            value.update(patch_value)
        raw = encode_event(value, nullable_members=('keyPackageReceiveUntil','controlKey'))
        return encode_event(dict(self.base, payload=base64.b64encode(raw).decode(), signature=sign(self.binary,self.device,domain,raw)))

    def verify(self, raw):
        return verify(raw,self.identity,self.binary,time=self.time,trust_policy='allow-unverified')

    def stage(self, raw, **overrides):
        args=dict(time=self.time,trust_policy='allow-unverified',receive_delay=60)
        args.update(overrides)
        return self.issuer.stage(raw,self.device,**args)

    def test_unchanged_accepted_successor_preserves_original_advertisement_and_issuance(self):
        raw=self.signed();self.stage(raw)
        bundle=copy.deepcopy(self.base['identity'])
        state=json.loads(base64.b64decode(bundle['states'][-1]['payload']))
        state.update(record='f'*32,revision='1',previous=[self.value['state']],issuedAt=self.time['earliest'])
        payload=encode_event(state);head=hashlib.sha256(payload).hexdigest()
        bundle['states'].append(dict(payload=base64.b64encode(payload).decode(),signature=sign(self.binary,self.device,'email-next/identity-state/v0',payload)))
        self.assertEqual(self.identity.accept_successor(encode_event(bundle),candidate_digest=head,time=self.time)['status'],'accepted-unverified')
        checked=self.verify(raw)
        self.assertEqual(checked['status'],'suite-setup-validated-unverified');self.assertEqual(checked['head'],head)
        self.assertEqual(self.stage(raw)['status'],'staged-only')
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM email2_issued_assertions').fetchone()[0],1)
        self.assertEqual(self.identity.db.execute('SELECT wrapper FROM email2_issued_assertions').fetchone()[0],raw)

    def test_actual_signature_current_identity_package_and_receiving_deadline(self):
        result=self.verify(self.signed())
        self.assertEqual(result['status'],'suite-setup-validated-unverified')
        self.assertTrue(result['mls_validated'])
        self.assertFalse(result['mailbox_verified'])
        self.assertEqual(result['package']['reference'],self.device['reference'])
        self.assertEqual(result['package']['notAfter'],str(self.device['time']+600))
        self.assertEqual(result['package']['receiveUntil'],self.value['keyPackageReceiveUntil'])

    def test_signed_mode_support_cannot_be_downgraded_or_cross_combined(self):
        support=offers(['answers'],managed_modules=['reactions'])
        raw=self.signed(dict(applications=support,orderingExchanges=exchanges(support)))
        self.assertEqual(self.verify(raw)['status'],'suite-setup-validated-unverified')
        for changed in (dict(applications=support,orderingExchanges=exchanges(offers())),dict(applications=[dict(application(),ordering=QUORUM)],orderingExchanges=[dict(format='quorum-exchange-experiment',version='2')])):
            with self.subTest(changed=changed),self.assertRaises(ValueError):decode_passive_discovery(self.signed(changed))

    def test_actual_signed_endpoint_support_is_per_mode_and_cannot_be_replaced_unsigned(self):
        for module in ['service-actions','hosted-replies']:
            with self.subTest(module=module):
                support=offers([module],managed_modules=['answers'])
                raw=self.signed(dict(applications=support,orderingExchanges=exchanges(support)))
                self.assertEqual(self.verify(raw)['status'],'suite-setup-validated-unverified')
                self.assertEqual(select([support,offers([module])]),application([module]))
                self.assertEqual(select([support,offers(['answers'])]),application())
                with self.assertRaises(ValueError):select([support,offers([module])],ordering=QUORUM)
                outer=json.loads(raw);payload=json.loads(base64.b64decode(outer['payload']))
                payload['applications']=offers(['answers'],managed_modules=['answers'])
                outer['payload']=base64.b64encode(encode_event(payload,nullable_members=('keyPackageReceiveUntil','controlKey'))).decode()
                # Well-shaped replacement retains the package and ordering;
                # the original signature must still reject changed capabilities.
                self.assertEqual(self.verify(encode_event(outer)),{'status':'invalid','reason':'assertion-proof'})

    def test_signed_full_five_module_closure_contains_sixty_four_mode_tuples(self):
        names=['answers','reactions','corrections','service-actions','hosted-replies']
        support=offers(names,managed_modules=names)
        self.assertEqual(len(support),64)
        raw=self.signed(dict(applications=support,orderingExchanges=exchanges(support)))
        self.assertEqual(self.verify(raw)['status'],'suite-setup-validated-unverified')
        self.assertEqual(select([support]),application(names))
        self.assertEqual(select([support],ordering=QUORUM),application(names))

    def test_same_key_binding_replacement_invalidates_cached_setup_after_accepted_change(self):
        original=self.signed();self.assertEqual(self.verify(original)['status'],'suite-setup-validated-unverified')
        bundle=copy.deepcopy(self.base['identity'])
        binding=json.loads(base64.b64decode(bundle['bindings'][0]['payload']))
        binding.update(record='9'*32,authority=dict(kind='state',digest=self.value['state']))
        raw=encode_event(binding);digest=hashlib.sha256(raw).hexdigest()
        bundle['bindings'].append(dict(payload=base64.b64encode(raw).decode(),authorization=sign(self.binary,self.device,'email-next/device-binding/v0',raw),possession=sign(self.binary,self.device,'email-next/device-possession/v0',raw)))
        state=json.loads(base64.b64decode(bundle['states'][-1]['payload']))
        state.update(record='a'*32,revision='1',previous=[self.value['state']],issuedAt=self.time['earliest'],bindings=[dict(device=self.device['device'],digest=digest)])
        raw=encode_event(state);head=hashlib.sha256(raw).hexdigest()
        bundle['states'].append(dict(payload=base64.b64encode(raw).decode(),signature=sign(self.binary,self.device,'email-next/identity-state/v0',raw)))
        self.assertEqual(self.identity.accept_successor(encode_event(bundle),candidate_digest=head,time=self.time)['status'],'accepted-unverified')
        result=self.verify(original)
        self.assertEqual(result['status'],'stale');self.assertEqual(result['reason'],'asserted-state-or-binding')
        self.assertEqual(result['head'],head)
        with self.assertRaisesRegex(ValueError,'Current local assertion'):self.stage(original)

    def test_control_key_requires_local_private_material_and_immutable_promise(self):
        raw=self.signed();self.stage(raw)
        missing=dict(self.device);missing.pop('controlSecret')
        with self.assertRaisesRegex(ValueError,'own control-key'):self.issuer.stage(self.signed(dict(record='6'*32)),missing,time=self.time,trust_policy='allow-unverified',receive_delay=60)
        changed=dict(self.value['controlKey'],receiveUntil=str(self.device['time']+661))
        with self.assertRaisesRegex(ValueError,'Immutable control-key'):self.stage(self.signed(dict(record='6'*32,controlKey=changed)))
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM email2_issued_control_keys').fetchone()[0],1)
        self.assertEqual(verify(raw,self.identity,self.binary,time=self.time,trust_policy='allow-unverified',maximum_control_lifetime='60')['reason'],'control-key-lifetime-policy')

    def test_loose_timestamp_does_not_cover_the_actual_package(self):
        raw=self.signed(dict(keyPackageReceiveUntil=str(self.device['time']+599)))
        decode_passive_discovery(raw)  # Syntax alone is insufficient.
        self.assertEqual(self.verify(raw)['reason'],'receiving-deadline-before-package-expiry')
        with self.assertRaisesRegex(ValueError,'immutable local custody'):
            self.stage(raw)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM email2_issued_packages').fetchone()[0],0)

    def test_wrong_purpose_and_signed_byte_tamper_do_not_verify(self):
        self.assertEqual(self.verify(self.signed(domain='email-next/passive-discovery/v7'))['reason'],'assertion-proof')
        value=json.loads(self.signed());payload=base64.b64decode(value['payload'])
        value['payload']=base64.b64encode(payload.replace(b'Alice',b'Carol')).decode()
        self.assertEqual(self.verify(encode_event(value))['reason'],'assertion-proof')

    def test_substituted_package_has_no_identity_or_receiving_right(self):
        other=make_device(self.binary,1,3)
        raw=self.signed(dict(keyPackage=[base64.b64encode(bytes.fromhex(other['package'])).decode()]))
        self.assertEqual(self.verify(raw)['reason'],'package-validation')
        with self.assertRaises((ValueError,RuntimeError)):
            self.stage(raw)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM email2_issued_assertions').fetchone()[0],0)

    def test_complete_module_closure_required_and_old_version_not_reinterpreted(self):
        for changes in (dict(applications=self.value['applications'][1:]),dict(orderingExchanges=[dict(format='quorum-exchange-experiment',version='1')]),dict(keyPackageReceiveUntil='01'),dict(version='7')):
            with self.subTest(changes=changes),self.assertRaises(ValueError):decode_passive_discovery(self.signed(changes))
        outer=json.loads(self.signed());value=json.loads(base64.b64decode(outer['payload']));del value['keyPackageReceiveUntil'];outer['payload']=base64.b64encode(encode_event(value)).decode()
        with self.assertRaises(ValueError):decode_passive_discovery(encode_event(outer))

    def test_canonical_internationalized_and_quoted_mailbox_signed_octets(self):
        raw=self.signed(dict(mailbox='"用户 desk"@example.org'))
        self.assertEqual(self.verify(raw)['status'],'suite-setup-validated-unverified')
        with self.assertRaises(ValueError):decode_passive_discovery(self.signed(dict(mailbox='"Alice"@example.org')))
        with self.assertRaises(ValueError):decode_passive_discovery(self.signed(dict(mailbox='Alice@EXAMPLE.ORG')))
        with patch.dict(os.environ):
            os.environ.pop('EMAIL_NEXT_IDNA17_CONFIG', None)
            result=self.verify(self.signed(dict(mailbox='Alice@xn--bcher-kva.example')))
            self.assertEqual(result,dict(status='pending',reason='a-label-validation'))

    def test_no_package_is_capability_only_and_still_needs_local_key_possession(self):
        raw=self.signed(dict(keyPackage=[],keyPackageReceiveUntil=None))
        self.assertEqual(self.verify(raw)['status'],'suite-capabilities-validated-unverified')
        self.assertIsNone(self.stage(raw)['reference'])
        public_only=dict(self.device,checkpoint=[])
        with self.assertRaises((ValueError,RuntimeError)):
            self.issuer.stage(self.signed(dict(keyPackage=[],keyPackageReceiveUntil=None,record='4'*32)),public_only,time=self.time,trust_policy='allow-unverified')
        with self.assertRaises(ValueError):decode_passive_discovery(self.signed(dict(keyPackage=[],keyPackageReceiveUntil='1')))

    def test_original_deadline_survives_republication_and_new_local_policy(self):
        raw=self.signed();first=self.stage(raw)
        self.assertEqual(first['status'],'staged-only')
        self.assertEqual(self.stage(raw,receive_delay=0),first)
        refreshed=self.signed(dict(record='4'*32))
        self.assertEqual(self.stage(refreshed,receive_delay=0)['window'],first['window'])
        with self.assertRaisesRegex(ValueError,'immutable local custody'):
            self.stage(self.signed(dict(record='5'*32,keyPackageReceiveUntil=str(self.device['time']+661))),receive_delay=61)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM email2_issued_packages').fetchone()[0],1)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM email2_issued_assertions').fetchone()[0],2)

    def test_real_fresh_package_can_use_another_realm_without_reassigning_old_material(self):
        original=self.stage(self.signed())
        self.identity.db.execute('BEGIN IMMEDIATE')
        first=self.issuer.bind_allocation_realm_locked(original['reference'],'configured-provider-A/account/device')
        self.identity.db.commit()
        self.assertEqual(first['status'],'allocation-realm-bound-only')
        self.identity.db.execute('BEGIN IMMEDIATE')
        try:
            with self.assertRaisesRegex(ValueError,'authority is immutable'):self.issuer.bind_allocation_realm_locked(original['reference'],'configured-provider-B/account/device')
        finally:self.identity.db.rollback()
        fresh=call(self.binary,op='fresh-package',checkpoint=self.device['checkpoint'],key=self.device['key'],identity=self.device['identity'])
        device=dict(self.device,**{k:fresh[k] for k in ('checkpoint','package','reference')})
        raw=self.signed(dict(record='8'*32,notBefore=str(fresh['time']-60),keyPackage=[base64.b64encode(bytes.fromhex(fresh['package'])).decode()],keyPackageReceiveUntil=str(fresh['time']+660)))
        staged=self.issuer.stage(raw,device,time=self.time,trust_policy='allow-unverified',receive_delay=60)
        self.assertNotEqual(original['reference'],staged['reference'])
        self.assertEqual(self.issuer.db.execute('SELECT count(*) FROM email2_issued_packages').fetchone()[0],2)
        self.identity.db.execute('BEGIN IMMEDIATE')
        self.issuer.bind_allocation_realm_locked(staged['reference'],'configured-provider-B/account/device')
        self.identity.db.commit()
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM email2_package_allocation_realm').fetchone()[0],2)
        self.assertEqual(self.verify(raw)['status'],'suite-setup-validated-unverified')

    def test_realm_freeze_rolls_back_and_committed_owner_survives_another_connection(self):
        original=self.stage(self.signed());ref=original['reference']
        with self.assertRaisesRegex(ValueError,'transaction'):self.issuer.bind_allocation_realm_locked(ref,'realm-A')
        self.identity.db.execute('BEGIN IMMEDIATE');self.issuer.bind_allocation_realm_locked(ref,'realm-A');self.identity.db.rollback()
        other=IdentityStore(Path(self.temp.name)/'issuer.sqlite')
        try:
            issuer=LocalIssuance(other,self.binary);other.db.execute('BEGIN IMMEDIATE')
            issuer.bind_allocation_realm_locked(ref,'realm-B');other.db.commit()
            self.identity.db.execute('BEGIN IMMEDIATE')
            with self.assertRaisesRegex(ValueError,'authority is immutable'):self.issuer.bind_allocation_realm_locked(ref,'realm-A')
            self.identity.db.rollback()
            self.identity.db.execute('BEGIN IMMEDIATE');self.issuer.terminal_locked(ref,'withdrawn',time=self.time);self.identity.db.commit()
            other.db.execute('BEGIN IMMEDIATE')
            with self.assertRaisesRegex(ValueError,'Terminal package'):issuer.bind_allocation_realm_locked(ref,'realm-B')
            other.db.rollback()
        finally:
            if self.identity.db.in_transaction:self.identity.db.rollback()
            other.close()

    def test_staging_failure_rolls_back_both_public_records(self):
        self.identity.db.execute("CREATE TEMP TRIGGER fail_assertion BEFORE INSERT ON email2_issued_assertions BEGIN SELECT RAISE(ABORT,'staging failure'); END")
        with self.assertRaisesRegex(sqlite3.IntegrityError,'staging failure'):self.stage(self.signed())
        for table in ('email2_issued_packages','email2_issued_assertions','email2_issued_control_keys'):
            self.assertEqual(self.identity.db.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
        self.identity.db.execute('DROP TRIGGER fail_assertion')
        self.stage(self.signed())

    def test_known_consumption_prevents_stale_private_snapshot_reissue(self):
        raw=self.signed();reference=self.stage(raw)['reference']
        self.identity.db.execute('BEGIN IMMEDIATE')
        self.issuer.terminal_locked(reference,'consumed',time=self.time)
        self.identity.db.execute('COMMIT')
        with self.assertRaisesRegex(ValueError,'Package terminal'):self.stage(raw)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM email2_issued_assertions').fetchone()[0],1)

    def test_clock_uncertainty_and_work_elapsed_before_commit_hold_staging(self):
        raw=self.signed()
        with patch('suite_discovery8.elapsed_time.monotonic',side_effect=[0,61]):
            with self.assertRaisesRegex(ValueError,'before commit'):self.stage(raw)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM email2_issued_packages').fetchone()[0],0)
        self.assertEqual(self.verify(raw)['status'],'suite-setup-validated-unverified')
        self.assertNotEqual(verify(raw,self.identity,self.binary,time=dict(earliest=self.time['earliest'],latest=str(self.device['time']+61)),trust_policy='allow-unverified')['status'],'suite-setup-validated-unverified')

    def test_unknown_peer_identity_and_strict_policy_do_not_get_installed(self):
        path=Path(self.temp.name)/'unknown.sqlite';other=IdentityStore(path)
        try:
            self.assertEqual(verify(self.signed(),other,self.binary,time=self.time,trust_policy='allow-unverified')['status'],'pending')
            self.assertIsNone(other.current_state(self.device['principal'])['head'])
        finally:other.close()
        self.assertEqual(verify(self.signed(),self.identity,self.binary,time=self.time,trust_policy='require-verification')['status'],'verification-required')


if __name__ == '__main__':unittest.main()
