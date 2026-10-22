"""Versioned original-byte carrier tests; not v1 graph/install conformance."""
import base64
import copy
import json
import unittest

import test_identity_repair_candidate as fixtures
from identity_repair_candidate import derive,canonical
from identity_admin_wire import state,bundle,share,payload

TIME=fixtures.TIME


class IdentityAdminWireTests(unittest.TestCase):
    setUp=fixtures.RepairCandidateTests.setUp
    store=fixtures.RepairCandidateTests.store
    branch=fixtures.RepairCandidateTests.branch
    check_independently=fixtures.RepairCandidateTests.check_independently
    parents=fixtures.RepairCandidateTests.parents
    key=fixtures.RepairCandidateTests.key
    certificate=fixtures.RepairCandidateTests.certificate

    def data(self):
        parents=self.parents();plan=derive(parents,time=TIME);wrapper,replacements=self.certificate(plan)
        parent_bundle=dict(version='1',purpose='identity-bundle',principal=self.a['principal'],states=[dict(payload=base64.b64encode(p.raw).decode(),signature=fixtures.proof(self.key(json.loads(p.raw)['signer']),'email-next/identity-state/v0',p.raw)) for p in parents],bindings=[])
        # Parent records carry their actual synthetic signatures. The partial
        # bundle still needs independently retained predecessors/owning checks.
        final_bundle=dict(parent_bundle,states=parent_bundle['states']+[wrapper])
        value=dict(version='1',purpose='identity-repair-share',principal=self.a['principal'],parents=parent_bundle,candidate=wrapper['payload'],by=self.a['device'],proof='',bindings=[])
        return plan,wrapper,replacements,final_bundle,value

    def encoded(self,value):return json.dumps(value,separators=(',',':')).encode()

    def test_actual_derived_repair_original_bytes_and_carrier_roundtrip(self):
        plan,wrapper,_,value,request=self.data()
        self.assertEqual(state(plan['payload'])['status'],'state1-syntax-only')
        result=bundle(self.encoded(value));self.assertEqual(result['status'],'bundle1-carrier-only')
        self.assertEqual(result['value']['states'][-1],wrapper)
        result=share(self.encoded(request));self.assertEqual(result['status'],'repair-share1-carrier-only')
        self.assertEqual(result['candidate']['octets'],plan['payload'])
        self.assertNotIn('authorized',result)

    def test_noncanonical_duplicate_and_unknown_state_members_fail(self):
        plan,*_=self.data()
        for raw in (json.dumps(plan['value'],indent=2).encode(),plan['payload'].replace(b'"version":"1"',b'"version":"1","version":"1"'),canonical(dict(plan['value'],extra='ignored'))):
            with self.assertRaises(ValueError):state(raw)

    def test_retirement_is_the_only_empty_roster_kind(self):
        plan,*_=self.data();value=dict(plan['value'],kind='retire',previous=[plan['value']['previous'][0]],bindings=[],revoked=sorted(plan['bindings']))
        self.assertEqual(state(canonical(value))['value']['kind'],'retire')
        with self.assertRaises(ValueError):state(canonical(dict(value,kind='update')))
        with self.assertRaises(ValueError):state(canonical(dict(value,bindings=plan['value']['bindings'],revoked=[])))

    def test_kind_predecessors_and_canonical_counters_do_not_mix(self):
        plan,*_=self.data()
        for patch in (dict(kind='update'),dict(previous=plan['value']['previous'][:1]),dict(previous=list(reversed(plan['value']['previous']))),dict(revision='01'),dict(revision=str(2**64)),dict(version='0')):
            with self.subTest(patch=patch),self.assertRaises(ValueError):state(canonical(dict(plan['value'],**patch)))

    def test_wrapper_shape_is_chosen_by_original_payload_version(self):
        _,wrapper,_,value,_=self.data()
        changed=copy.deepcopy(value);changed['states'][-1].pop('approvals')
        with self.assertRaises(ValueError):bundle(self.encoded(changed))
        changed=copy.deepcopy(value);changed['states'][0]['approvals']=[]
        with self.assertRaises(ValueError):bundle(self.encoded(changed))
        changed=copy.deepcopy(value);changed['states'].append(wrapper)
        with self.assertRaises(ValueError):bundle(self.encoded(changed))

    def test_partial_possession_proof_is_not_a_complete_binding_or_approval(self):
        plan,_,replacements,_,value=self.data();device=sorted(plan['replacements'])[0]
        entry=dict(payload=base64.b64encode(plan['replacements'][device]).decode(),authorization=replacements[device]['authorization'],possession='')
        value['bindings']=[entry]
        self.assertEqual(share(self.encoded(value))['value']['proof'],'')
        value['bindings'][0]['authorization']=''
        with self.assertRaises(ValueError):share(self.encoded(value))

    def test_duplicate_or_unsorted_proof_inventory_and_foreign_scope_fail(self):
        plan,_,replacements,_,value=self.data()
        entries=[dict(payload=base64.b64encode(raw).decode(),**replacements[device]) for device,raw in plan['replacements'].items()]
        import hashlib
        entries.sort(key=lambda e:hashlib.sha256(base64.b64decode(e['payload'])).hexdigest())
        value['bindings']=entries
        self.assertEqual(share(self.encoded(value))['status'],'repair-share1-carrier-only')
        for bad in (entries+[entries[0]],list(reversed(entries))):
            with self.assertRaises(ValueError):share(self.encoded(dict(value,bindings=bad)))
        with self.assertRaises(ValueError):share(self.encoded(dict(value,principal='enp0:'+'f'*64)))

    def test_oversized_base64_is_bounded_before_decode(self):
        with self.assertRaisesRegex(ValueError,'base64 bound'):payload('A'*1398105)
        with self.assertRaises(ValueError):bundle(b' '*4194305)
        _,_,_,_,value=self.data();value['proof']=False
        with self.assertRaises(ValueError):share(self.encoded(value))


if __name__=='__main__':unittest.main()
