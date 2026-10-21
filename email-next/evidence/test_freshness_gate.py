"""Actual accepted identity and assertion/bootstrap signatures, local journal only."""
from dataclasses import replace
import hashlib
from pathlib import Path
import tempfile
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from event_encoding import encode_event
from identity_store import IdentityStore
from freshness_gate import FreshnessGate,Policy
from bootstrap_exchange import signed,handle
from test_history_transfer import identity_material
from test_bootstrap_exchange import ad


class FreshnessTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'identities.sqlite';self.ids=IdentityStore(self.path);self.addCleanup(self.ids.close)
        self.a=identity_material('enp0:'+'a'*64);self.b=identity_material('enp0:'+'b'*64)
        for material in [self.a,self.b]:
            self.assertEqual(self.ids.observe(material['record'],first_contact_policy='allow-unverified')['status'],'pinned-unverified')
            self.assertEqual(self.ids.accept_successor(encode_event(material['bundle']),candidate_digest=material['head'],time=dict(earliest='20',latest='21'))['status'],'accepted-unverified')
        self.own=self.a['refs'][1];self.peer=self.b['refs'][1]
        self.gate=FreshnessGate(self.ids,account='own-account',own_principal=self.own['principal'],own_device=self.own['device'])
        self.cached=Policy('1'*32);self.recent=Policy('2'*32,'recent-checkpoint',10)
        self.live=Policy('3'*32,'live-confirmation',20,5)
        self.operation='4'*32;self.address='bob@recipient.example'
        self.ad=ad(self.b,self.peer,self.address,package=b'FRESHNESS-NOT-A-VALID-MLS-PACKAGE')
        self.s=dict(version='0',purpose='bootstrap-source',preparation='5'*32,request='6'*32,source='7'*64,
            issuer='https://source.example',delegation='8'*64,accountSource='9'*64,senderMailbox='alice@sender.example',sender=self.own,
            targetMailbox=self.address,targetService='https://target.example',conversation='a'*32,
            advertisement=ad(self.a,self.own,'alice@sender.example'),nonce='b'*64,notBefore='20',notAfter='80')
        self.source=signed('source',encode_event(self.s),self.a['target'])
        self.r=dict(version='0',purpose='bootstrap-response',response='c'*32,issuer='https://target.example',exchange=handle(self.s),
            sourceDigest=hashlib.sha256(encode_event(self.s)).hexdigest(),nonce=self.s['nonce'],mailbox=self.address,
            device=self.peer,advertisement=self.ad,relayDomain='',notBefore='21',notAfter='60')
        self.response=self.sign()

    def sign(self,value=None,key=None):return signed('response',encode_event(value or self.r),key or self.b['target'])
    def prepare(self,**kwargs):return self.gate.prepare_bootstrap(self.operation,self.live,self.source,clock=(20,21),**kwargs)
    def evaluate(self,policy=None,**kwargs):
        return self.gate.evaluate(policy or self.cached,self.peer,self.address,self.ad,clock=kwargs.pop('clock',(22,23)),**kwargs)
    def confirmed(self,**kwargs):return self.evaluate(self.live,operation=self.operation,response=kwargs.pop('response',self.response),**kwargs)

    def test_cached_mode_requires_current_signed_device_evidence_without_network(self):
        result=self.evaluate();self.assertEqual(result['mode'],'cached-continuity');self.assertEqual(result['evidence'],'')
        self.assertEqual(result['status'],'freshness-satisfied-only');self.assertNotIn('sendAuthorized',result)

    def test_cached_mode_holds_expired_binding_or_assertion(self):
        with self.assertRaises(ValueError):self.evaluate(clock=(101,102))
        with self.assertRaises(ValueError):self.gate.evaluate(self.cached,self.peer,self.address,'e30=',clock=(22,23))

    def test_recent_checkpoint_uses_current_accepted_state_issuance_not_arrival(self):
        self.assertEqual(self.evaluate(self.recent,clock=(20,21))['evidence'],self.peer['state'])
        with self.assertRaisesRegex(ValueError,'age window'):self.evaluate(self.recent,clock=(10,10))
        self.assertEqual(self.evaluate(replace(self.recent,maximum_age=2**64-1))['mode'],'recent-checkpoint')
        with self.assertRaisesRegex(ValueError,'age window'):self.evaluate(replace(self.recent,maximum_age=9),clock=(20,21))
        # Re-read/reopen does not alter the state timestamp or its bound.
        with self.assertRaises(ValueError):self.evaluate(self.recent,clock=(22,23))

    def test_new_accepted_head_or_known_revocation_invalidates_prior_evidence(self):
        self.prepare();self.confirmed()
        self.ids.accept_successor(encode_event(self.b['removal']),candidate_digest=self.b['removed'],time=dict(earliest='22',latest='23'))
        for policy in [self.cached,self.recent,self.live]:
            with self.subTest(mode=policy.mode),self.assertRaises(ValueError):
                self.evaluate(policy,operation=self.operation,response=self.response)

    def test_live_requires_original_locally_outstanding_attempt(self):
        with self.assertRaisesRegex(ValueError,'outstanding'):self.confirmed()
        self.assertEqual(self.prepare(),'stored-attempt')
        result=self.confirmed();self.assertEqual(result['mode'],'live-confirmation')
        self.assertEqual(result['evidence'],hashlib.sha256(encode_event(self.r)).hexdigest())

    def test_publication_or_provider_status_cannot_be_called_live_response(self):
        self.prepare()
        for value in [dict(state='ready'),dict(encryptionSupported='true'),self.source]:
            with self.subTest(value=value),self.assertRaises(ValueError):self.confirmed(response=value)
        publication=dict(version='0',purpose='bootstrap-publication',publication='d'*32,issuer=self.r['issuer'],mailbox=self.address,
                         device=self.peer,advertisement=self.ad,relayDomain='',scope='automatic-first-contact',notBefore='21',notAfter='60')
        with self.assertRaises(ValueError):self.confirmed(response=signed('publication',encode_event(publication),self.b['target']))

    def test_live_signature_and_exact_challenge_target_binding(self):
        self.prepare()
        for patch in [dict(nonce='e'*64),dict(sourceDigest='e'*64),dict(exchange='e'*64),dict(issuer='https://other.example'),
                      dict(mailbox='other@recipient.example'),dict(device=self.own)]:
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.confirmed(response=self.sign(dict(self.r,**patch)))
        with self.assertRaises(ValueError):self.confirmed(response=self.sign(key=Ed25519PrivateKey.generate()))
        self.assertEqual(self.confirmed()['status'],'freshness-satisfied-only')

    def test_new_record_or_operation_cannot_borrow_another_operations_response(self):
        self.prepare()
        other=dict(self.s,source='e'*64,request='f'*32,nonce='d'*64)
        self.gate.prepare_bootstrap('d'*32,self.live,signed('source',encode_event(other),self.a['target']),clock=(20,21))
        with self.assertRaises(ValueError):self.evaluate(self.live,operation='d'*32,response=self.response)

    def test_retry_and_reopen_do_not_refresh_original_age_anchor(self):
        self.prepare()
        self.gate.prepare_bootstrap(self.operation,self.live,self.source,clock=(30,31))
        other=IdentityStore(self.path);self.addCleanup(other.close)
        reopened=FreshnessGate(other,account='own-account',own_principal=self.own['principal'],own_device=self.own['device'])
        with self.assertRaisesRegex(ValueError,'age window'):
            reopened.evaluate(self.live,self.peer,self.address,self.ad,clock=(40,41),operation=self.operation,response=self.response)

    def test_clock_uncertainty_backwards_and_unknown_time_hold(self):
        self.prepare()
        for clock in [None,(23,22),(True,23),(-1,23),(22,2**64),(22,28),(19,21)]:
            with self.subTest(clock=clock),self.assertRaises(ValueError):self.confirmed(clock=clock)
        self.assertEqual(self.confirmed(clock=(39,40))['mode'],'live-confirmation')
        with self.assertRaises(ValueError):self.confirmed(clock=(39,41))

    def test_response_or_source_deadline_cannot_be_extended_by_retrieval(self):
        self.prepare()
        with self.assertRaises(ValueError):self.confirmed(response=self.sign(dict(self.r,notAfter='81')))
        # Maximum age is deliberately widened, so this failure is response expiry.
        policy=replace(self.live,maximum_age=100);op='d'*32
        self.gate.prepare_bootstrap(op,policy,self.source,clock=(20,21))
        with self.assertRaises(ValueError):self.evaluate(policy,clock=(61,62),operation=op,response=self.response)

    def test_cancellation_is_terminal_for_exact_prepare_retry(self):
        self.prepare();self.gate.cancel(self.operation);self.assertEqual(self.prepare(),'retained-attempt')
        with self.assertRaises(ValueError):self.confirmed()

    def test_policy_or_local_account_change_cannot_reuse_attempt(self):
        self.prepare()
        with self.assertRaises(ValueError):self.evaluate(replace(self.live,revision='f'*32),operation=self.operation,response=self.response)
        other=FreshnessGate(self.ids,account='other-account',own_principal=self.own['principal'],own_device=self.own['device'])
        with self.assertRaises(ValueError):other.evaluate(self.live,self.peer,self.address,self.ad,clock=(22,23),operation=self.operation,response=self.response)

    def test_source_self_scope_and_later_source_device_removal_are_checked(self):
        other=FreshnessGate(self.ids,account='own-account',own_principal=self.peer['principal'],own_device=self.peer['device'])
        with self.assertRaises(ValueError):other.prepare_bootstrap(self.operation,self.live,self.source,clock=(20,21))
        self.prepare();self.ids.accept_successor(encode_event(self.a['removal']),candidate_digest=self.a['removed'],time=dict(earliest='22',latest='23'))
        with self.assertRaises(ValueError):self.confirmed()

    def test_local_preparation_conflicts_do_not_replace_original_attempt(self):
        self.prepare();source=signed('source',encode_event(dict(self.s,nonce='e'*64)),self.a['target'])
        with self.assertRaisesRegex(ValueError,'conflict'):self.gate.prepare_bootstrap(self.operation,self.live,source,clock=(20,21))
        self.assertEqual(self.confirmed()['status'],'freshness-satisfied-only')

    def test_age_policy_is_explicit_and_never_inferred_from_receipt(self):
        for policy in [replace(self.cached,maximum_age=10),replace(self.recent,maximum_age=None),
                       replace(self.live,maximum_age=True),replace(self.live,maximum_age=0),replace(self.live,maximum_uncertainty=True)]:
            with self.subTest(policy=policy),self.assertRaises(ValueError):self.evaluate(policy)


if __name__=='__main__':unittest.main()
