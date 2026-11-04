"""Actual signed same-key renewals; delayed receipt is not a grant renewal."""
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from event_encoding import encode_event
from identity_store import IdentityStore
from history_transfer import authorize,authority_snapshot
from test_history_transfer import identity_material,proof


class ContinuousAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.ids=IdentityStore(Path(self.temp.name)/'identity.sqlite');self.addCleanup(self.ids.close)
        self.m=identity_material();self.ref=self.m['refs'][1]
        self.ids.observe(self.m['record'],first_contact_policy='allow-unverified')
        self.ids.accept_successor(encode_event(self.m['bundle']),candidate_digest=self.m['head'],time=dict(earliest='20',latest='21'))
        self.bundle=copy.deepcopy(self.m['bundle']);self.head=self.m['head'];self.revision=1

    def renew(self,*,before='90',roles=None,expected='accepted-unverified'):
        self.revision+=1
        binding=dict(version='0',purpose='device-binding',record=str(self.revision)*32,principal=self.ref['principal'],device=self.ref['device'],signingKey=self.ref['key'],roles=roles or ['send','receive'],notBefore=before,notAfter='200',authority=dict(kind='state',digest=self.head))
        raw=encode_event(binding);digest=hashlib.sha256(raw).hexdigest()
        self.bundle['bindings'].append(dict(payload=base64.b64encode(raw).decode(),authorization=proof(self.m['source'],'email-next/device-binding/v0',raw),possession=proof(self.m['target'],'email-next/device-possession/v0',raw)))
        state=json.loads(base64.b64decode(self.bundle['states'][-1]['payload']))
        state.update(record=hex(self.revision+8)[2:]*32,revision=str(self.revision),previous=[self.head],issuedAt='90')
        state['bindings']=[dict(entry,digest=digest) if entry['device']==self.ref['device'] else entry for entry in state['bindings']]
        raw=encode_event(state);self.head=hashlib.sha256(raw).hexdigest()
        self.bundle['states'].append(dict(payload=base64.b64encode(raw).decode(),signature=proof(self.m['source'],'email-next/identity-state/v0',raw)))
        self.assertEqual(self.ids.accept_successor(encode_event(self.bundle),candidate_digest=self.head,time=dict(earliest='90',latest='90'))['status'],expected)

    def check(self,*,renewal):
        with authority_snapshot(self.ids):
            return authorize(self.ids,self.ref,'receive',dict(earliest='110',latest='111'),'allow-unverified',allow_binding_renewal=renewal)

    def test_late_receipt_uses_continuous_same_key_without_extending_original_interval(self):
        self.renew()
        result=self.check(renewal=True)
        self.assertEqual(result,dict(head=self.head,before=10,after=100))
        with self.assertRaises(ValueError):self.check(renewal=False)

    def test_sealed_late_receipt_authenticates_original_signature_through_renewal(self):
        from sealed_control import native,frame,seal,open_candidate
        binary=Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR'])/'sealed-control'
        secret=native(binary,op='generate')
        descriptor=dict(id=secret['id'],publicKey=secret['publicKey'],notBefore='10',notAfter='100',receiveUntil='200')
        recipient=dict(principal=self.ref['principal'],device='end0:'+'9'*64)
        body=b'{"original":"retained control"}'
        value=dict(version='0',purpose='sealed-control-intent',record='a'*32,sender={k:self.ref[k] for k in ('principal','device','state','binding')},recipient=recipient,key=secret['id'],kind='stream-control',body=base64.b64encode(body).decode(),notBefore='90',notAfter='95')
        raw=encode_event(value);signature=bytes.fromhex(proof(self.m['target'],'email2/sealed-control-intent/v0',raw))
        wire=seal(binary,descriptor,frame(raw,signature,encode_event(self.m['bundle'])),time=dict(earliest='90',latest='90'),recipient=recipient)
        self.renew()
        result=open_candidate(binary,wire,descriptor=descriptor,private_key=secret['privateKey'],recipient=recipient,identity=self.ids,time=dict(earliest='110',latest='111'),expected_kind='stream-control')
        self.assertEqual(result['original_intent'],raw);self.assertEqual(result['original_body'],body)
        self.assertEqual(result['authority']['head'],self.head)

    def test_binding_interval_gap_is_not_continuity(self):
        self.renew(before='101',expected='invalid')
        with self.assertRaises(ValueError):self.check(renewal=True)

    def test_removed_role_cannot_reappear_as_uninterrupted_authority(self):
        self.renew(roles=['send']);self.renew()
        with self.assertRaisesRegex(ValueError,'binding changed'):self.check(renewal=True)

    def test_missing_accepted_parent_does_not_get_installed_from_the_bundle(self):
        self.renew()
        self.ids.db.execute('DELETE FROM identity_transitions WHERE digest=?',(self.ref['state'],));self.ids.db.commit()
        with self.assertRaisesRegex(ValueError,'accepted ancestor'):self.check(renewal=True)


if __name__=='__main__':unittest.main()
