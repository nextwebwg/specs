"""Actual state1 signatures over exact pairing deltas; no accepted-history store."""
import base64
import hashlib
import unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from identity_repair_candidate import canonical,framed,STATE_DOMAIN
from pairing_successor import check_successor


class PairingSuccessorTests(unittest.TestCase):
    def setUp(self):
        self.keys={n:Ed25519PrivateKey.generate() for n in ('1','2')}
        self.parent=dict(version='1',purpose='identity-state',kind='update',principal='enp0:'+'a'*64,
                         record='a'*32,revision='1',previous=['0'*64],issuedAt='10',
                         bindings=[dict(device='end0:'+n*64,digest=n*64) for n in ('1','2')],revoked=[],signer='end0:'+'1'*64)
        self.parent_raw=canonical(self.parent)
        self.binding=dict(version='0',purpose='device-binding',record='b'*32,principal=self.parent['principal'],
                          device='end0:'+'3'*64,signingKey='3'*64,roles=['receive','send'],notBefore='10',notAfter='100',
                          authority=dict(kind='state',digest=hashlib.sha256(self.parent_raw).hexdigest()))
        self.binding_raw=canonical(self.binding)

    def child(self,authorizer='1'):
        return dict(self.parent,record='c'*32,revision='2',previous=[hashlib.sha256(self.parent_raw).hexdigest()],issuedAt='20',
                    signer='end0:'+authorizer*64,bindings=self.parent['bindings']+[dict(device=self.binding['device'],digest=hashlib.sha256(self.binding_raw).hexdigest())])

    def entry(self,value,authorizer='1',domain=STATE_DOMAIN,raw=None):
        raw=canonical(value) if raw is None else raw
        return dict(payload=base64.b64encode(raw).decode(),signature=self.keys[authorizer].sign(framed(domain,raw)).hex(),approvals=[])

    def check(self,entry,authorizer='1',binding=None):
        key=self.keys[authorizer].public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex()
        return check_successor(self.parent_raw,binding or self.binding_raw,entry,authorizer='end0:'+authorizer*64,
                               authorizer_key=key,not_before='15',not_after='30')

    def test_either_administrator_can_authorize_exact_update_without_primary(self):
        for admin in ('1','2'):
            self.assertEqual(self.check(self.entry(self.child(admin),admin),admin)['status'],'pairing-successor-candidate-only')

    def test_two_valid_siblings_do_not_choose_or_install_a_winner(self):
        results=[self.check(self.entry(self.child(a),a),a) for a in ('1','2')]
        self.assertNotEqual(results[0]['head'],results[1]['head'])
        self.assertEqual(self.parent_raw,canonical(self.parent))
        self.assertEqual(self.check(self.entry(self.child()))['head'],results[0]['head'])

    def test_signed_extra_changes_cannot_hide_in_pairing(self):
        for changes in [dict(revoked=['end0:'+'4'*64]),dict(principal='enp0:'+'f'*64),dict(revision='3'),
                        dict(previous=['f'*64]),dict(kind='repair'),dict(extra='value'),dict(bindings=[])]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):self.check(self.entry(self.child()|changes))

    def test_changed_approved_binding_cannot_reuse_result(self):
        changed=canonical(self.binding|dict(roles=['enroll','receive','revoke','send']))
        with self.assertRaises(ValueError):self.check(self.entry(self.child()),binding=changed)

    def test_old_or_wrong_signature_domain_and_key_are_rejected(self):
        for entry in [self.entry(self.child(),domain='email-next/identity-state/v0'),self.entry(self.child(),'2')]:
            with self.assertRaises(ValueError):self.check(entry)

    def test_session_and_predecessor_times_bound_successor(self):
        for value in ('14','31','0'):
            with self.subTest(value=value),self.assertRaises(ValueError):self.check(self.entry(self.child()|dict(issuedAt=value)))

    def test_state0_child_and_noncanonical_state1_cannot_downgrade(self):
        value=self.child();value.pop('kind');value['version']='0'
        with self.assertRaises(ValueError):self.check(self.entry(value))
        with self.assertRaises(ValueError):self.check(self.entry(self.child(),raw=canonical(self.child())+b' '))

    def test_ordinary_enrollment_cannot_import_repair_approvals(self):
        entry=self.entry(self.child());entry['approvals']=[dict(device='end0:'+'2'*64,signature='0'*128)]
        with self.assertRaises(ValueError):self.check(entry)


if __name__=='__main__':unittest.main()
