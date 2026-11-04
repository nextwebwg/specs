"""Real signed counterexamples for unresolved multi-admin coordination.

These tests preserve the current fail-closed behavior. They do not implement or
certify branch repair, a distributed lock, a preferred admin or a new identity
format. Software keys are isolated synthetic test material.
"""
import base64
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from event_encoding import encode_event
from identity_store import IdentityStore
from test_history_transfer import identity_material,proof,public

ROLES=['send','receive','enroll','revoke']
TIME=dict(earliest='22',latest='23')


class AdminConcurrencyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.m=identity_material(target_roles=ROLES)
        self.a,self.b=self.m['refs'];self.serial=0

    def store(self):
        self.serial+=1;store=IdentityStore(Path(self.temp.name)/f'identity-{self.serial}.sqlite');self.addCleanup(store.close)
        self.assertEqual(store.observe(self.m['record'],first_contact_policy='allow-unverified')['status'],'pinned-unverified')
        self.assertEqual(store.accept_successor(encode_event(self.m['bundle']),candidate_digest=self.m['head'],time=TIME)['status'],'accepted-unverified')
        return store

    def branch(self,actor,*,kind):
        bundle=copy.deepcopy(self.m['bundle']);state=json.loads(base64.b64decode(bundle['states'][-1]['payload']))
        index=1 if actor==self.a else 2;key=self.m['source'] if index==1 else self.m['target']
        state.update(record=str(index+5)*32,revision='2',previous=[self.m['head']],issuedAt='22',signer=actor['device'])
        if kind in ('enroll','renew'):
            new_key=Ed25519PrivateKey.generate() if kind=='enroll' else key
            device='end0:'+str(index+2)*64 if kind=='enroll' else actor['device']
            binding=dict(version='0',purpose='device-binding',record=str(index+7)*32,principal=actor['principal'],device=device,signingKey=public(new_key),roles=['send','receive'] if kind=='enroll' else ROLES,notBefore='20',notAfter='90' if kind=='enroll' else '200',authority=dict(kind='state',digest=self.m['head']))
            raw=encode_event(binding);digest=hashlib.sha256(raw).hexdigest()
            bundle['bindings'].append(dict(payload=base64.b64encode(raw).decode(),authorization=proof(key,'email-next/device-binding/v0',raw),possession=proof(new_key,'email-next/device-possession/v0',raw)))
            state['bindings']=[entry for entry in state['bindings'] if entry['device']!=device]+[dict(device=device,digest=digest)]
            state['bindings'].sort(key=lambda entry:entry['device'])
        else:
            self.assertEqual(kind,'revoke-peer')
            peer=self.b if index==1 else self.a
            state['bindings']=[entry for entry in state['bindings'] if entry['device']!=peer['device']]
            state['revoked']=[peer['device']]
        raw=encode_event(state);digest=hashlib.sha256(raw).hexdigest()
        bundle['states'].append(dict(payload=base64.b64encode(raw).decode(),signature=proof(key,'email-next/identity-state/v0',raw)))
        return bundle,digest,state

    def check_independently(self,left,right):
        stores=[]
        for bundle,digest,_ in (left,right):
            store=self.store();stores.append(store)
            self.assertEqual(store.accept_successor(encode_event(bundle),candidate_digest=digest,time=TIME)['status'],'accepted-unverified')
        return stores

    def conflict(self,store,other):
        bundle,digest,_=other
        self.assertEqual(store.accept_successor(encode_event(bundle),candidate_digest=digest,time=TIME)['status'],'conflicted')
        self.assertTrue(store.current_state(self.a['principal'])['conflicted'])
        for actor in (self.a,self.b):
            credential=b'email-next/device/v0\0'+bytes.fromhex(actor['principal'][5:])+bytes.fromhex(actor['device'][5:])
            self.assertEqual(store.check_device(credential,bytes.fromhex(actor['key']),role='send',time=TIME,trust_policy='allow-unverified')['status'],'conflicted')

    def test_concurrent_enrollments_are_valid_but_both_arrival_orders_hold(self):
        left,right=self.branch(self.a,kind='enroll'),self.branch(self.b,kind='enroll')
        stores=self.check_independently(left,right)
        self.conflict(stores[0],right);self.conflict(stores[1],left)
        common={(r['device'],r['digest']) for r in left[2]['bindings']} & {(r['device'],r['digest']) for r in right[2]['bindings']}
        self.assertEqual({device for device,_ in common},{self.a['device'],self.b['device']})

    def test_healthy_concurrent_renewals_have_no_common_exact_binding(self):
        left,right=self.branch(self.a,kind='renew'),self.branch(self.b,kind='renew')
        stores=self.check_independently(left,right);self.conflict(stores[0],right)
        common={(r['device'],r['digest']) for r in left[2]['bindings']} & {(r['device'],r['digest']) for r in right[2]['bindings']}
        self.assertEqual(common,set())
        for branch in (left,right):
            bindings={hashlib.sha256(base64.b64decode(r['payload'])).hexdigest():json.loads(base64.b64decode(r['payload'])) for r in branch[0]['bindings']}
            for actor in (self.a,self.b):
                ref=next(r for r in branch[2]['bindings'] if r['device']==actor['device'])
                self.assertEqual(bindings[ref['digest']]['signingKey'],actor['key'])
                self.assertEqual(set(bindings[ref['digest']]['roles']),set(ROLES))

    def test_mutual_revocation_cannot_be_repaired_by_restoring_one_admin(self):
        left,right=self.branch(self.a,kind='revoke-peer'),self.branch(self.b,kind='revoke-peer')
        stores=self.check_independently(left,right);self.conflict(stores[0],right)
        revoked=set(left[2]['revoked'])|set(right[2]['revoked'])
        self.assertEqual(revoked,{self.a['device'],self.b['device']})
        self.assertEqual({r['device'] for r in left[2]['bindings']} & {r['device'] for r in right[2]['bindings']},set())

    def test_a_later_valid_descendant_does_not_choose_a_branch_or_clear_conflict(self):
        left,right=self.branch(self.a,kind='enroll'),self.branch(self.b,kind='enroll')
        stores=self.check_independently(left,right)
        bundle=copy.deepcopy(left[0]);state=dict(left[2],record='c'*32,revision='3',previous=[left[1]],issuedAt='23')
        raw=encode_event(state);digest=hashlib.sha256(raw).hexdigest()
        bundle['states'].append(dict(payload=base64.b64encode(raw).decode(),signature=proof(self.m['source'],'email-next/identity-state/v0',raw)))
        self.assertEqual(stores[0].accept_successor(encode_event(bundle),candidate_digest=digest,time=TIME)['status'],'accepted-unverified')
        self.conflict(stores[0],right)
        self.assertEqual(stores[0].accept_successor(encode_event(bundle),candidate_digest=digest,time=TIME)['status'],'conflicted')


if __name__=='__main__':unittest.main()
