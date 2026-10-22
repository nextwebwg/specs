"""Actual authorized fork snapshots and Ed25519 repair candidate proofs.

No repaired IdentityStore state, v1 network admission or final release is supplied.
"""
import base64
import hashlib
import json
import unittest

from identity_repair_candidate import (Parent,derive,verify_candidate,canonical,STATE_DOMAIN,APPROVAL_DOMAIN)
import test_admin_concurrency as concurrency
TIME=concurrency.TIME
from test_history_transfer import proof


class RepairCandidateTests(unittest.TestCase):
    setUp=concurrency.AdminConcurrencyTests.setUp
    store=concurrency.AdminConcurrencyTests.store
    branch=concurrency.AdminConcurrencyTests.branch
    check_independently=concurrency.AdminConcurrencyTests.check_independently

    def parents(self,left=None,right=None,*,kind='renew'):
        left=left or self.branch(self.a,kind=kind);right=right or self.branch(self.b,kind=kind)
        self.check_independently(left,right)
        parents=[]
        for bundle,_,_ in (left,right):
            raw=base64.b64decode(bundle['states'][-1]['payload'])
            bindings={hashlib.sha256(base64.b64decode(b['payload'])).hexdigest():base64.b64decode(b['payload']) for b in bundle['bindings']}
            parents.append(Parent(raw,bindings))
        return parents

    def key(self,device):return self.m['source'] if device==self.a['device'] else self.m['target']

    def certificate(self,plan):
        raw=plan['payload'];signers=plan['authorizers']
        wrapper=dict(payload=base64.b64encode(raw).decode(),signature=proof(self.key(signers[0]),STATE_DOMAIN,raw),approvals=[dict(device=d,signature=proof(self.key(d),APPROVAL_DOMAIN,raw)) for d in signers[1:]])
        replacements={d:dict(authorization=proof(self.key(signers[0]),'email-next/device-binding/v0',body),possession=proof(self.key(d),'email-next/device-possession/v0',body)) for d,body in plan['replacements'].items()}
        return wrapper,replacements

    def test_actual_renewal_fork_has_one_candidate_without_expiry_amplification(self):
        parents=self.parents();plan=derive(parents,time=TIME)
        self.assertEqual(set(plan['replacements']),{self.a['device'],self.b['device']})
        for binding in plan['bindings'].values():
            self.assertEqual(binding['notBefore'],'20');self.assertEqual(binding['notAfter'],'100')
        wrapper,replacements=self.certificate(plan)
        checked=verify_candidate(wrapper,parents,replacements,time=TIME)
        self.assertEqual(checked['status'],'repair-candidate-only')
        self.assertEqual(checked['payload'],plan['payload'])

    def test_independent_parent_order_produces_exactly_equal_signed_payload(self):
        parents=self.parents();forward=derive(parents,time=TIME);backward=derive(list(reversed(parents)),time=TIME)
        self.assertEqual(forward['payload'],backward['payload']);self.assertEqual(forward['replacements'],backward['replacements'])
        wrapper,replacements=self.certificate(forward)
        self.assertEqual(verify_candidate(wrapper,list(reversed(parents)),replacements,time=TIME)['payload'],forward['payload'])

    def test_replacement_authority_commits_one_parent_without_dropping_other_approvals(self):
        parents=self.parents();plan=derive(parents,time=TIME)
        wrapper,replacements=self.certificate(plan)
        first,other=sorted(parent.digest for parent in parents)
        device=self.b['device'];raw=plan['replacements'][device]
        binding=json.loads(raw)
        self.assertEqual(binding['authority'],dict(kind='state',digest=first))
        self.assertEqual(len(plan['authorizers']),2)
        self.assertEqual(verify_candidate(wrapper,parents,replacements,time=TIME)['status'],'repair-candidate-only')
        # Both signatures are real and use the correct keys/domains, but refer
        # to different binding bytes from the deterministic repair certificate.
        changed=canonical(dict(binding,authority=dict(kind='state',digest=other)))
        replacements[device]=dict(
            authorization=proof(self.key(plan['authorizers'][0]),'email-next/device-binding/v0',changed),
            possession=proof(self.key(device),'email-next/device-possession/v0',changed))
        with self.assertRaisesRegex(ValueError,'proof signature'):
            verify_candidate(wrapper,parents,replacements,time=TIME)

    def test_concurrent_enrollments_need_all_shared_administrators_to_reapprove_union(self):
        parents=self.parents(kind='enroll');plan=derive(parents,time=TIME)
        self.assertEqual(len(plan['bindings']),4);self.assertEqual(plan['replacements'],{})
        wrapper,replacements=self.certificate(plan)
        self.assertEqual(verify_candidate(wrapper,parents,replacements,time=TIME)['status'],'repair-candidate-only')
        wrapper['approvals']=[]
        with self.assertRaisesRegex(ValueError,'Every surviving administrator'):verify_candidate(wrapper,parents,replacements,time=TIME)

    def test_valid_signatures_cannot_erase_a_branch_revocation(self):
        parents=self.parents(self.branch(self.a,kind='enroll'),self.branch(self.b,kind='revoke-peer'))
        plan=derive(parents,time=TIME);self.assertEqual(plan['value']['revoked'],[self.a['device']])
        self.assertEqual(plan['authorizers'],[self.b['device']])
        wrapper,replacements=self.certificate(plan)
        self.assertEqual(verify_candidate(wrapper,parents,replacements,time=TIME)['status'],'repair-candidate-only')
        changed=dict(plan['value'],revoked=[]);raw=canonical(changed)
        wrapper.update(payload=base64.b64encode(raw).decode(),signature=proof(self.m['target'],STATE_DOMAIN,raw))
        with self.assertRaisesRegex(ValueError,'deterministic candidate'):verify_candidate(wrapper,parents,replacements,time=TIME)

    def test_mutual_revocation_has_no_implicit_ancestor_override(self):
        parents=self.parents(self.branch(self.a,kind='revoke-peer'),self.branch(self.b,kind='revoke-peer'))
        with self.assertRaisesRegex(ValueError,'No shared surviving'):derive(parents,time=TIME)

    def test_renewal_cannot_borrow_current_rights_from_just_one_branch(self):
        parents=self.parents()
        for time in (dict(earliest='101',latest='102'),dict(earliest='99',latest='101')):
            with self.assertRaisesRegex(ValueError,'not current on every branch'):derive(parents,time=time)

    def test_repair_and_approval_domains_are_distinct(self):
        parents=self.parents();plan=derive(parents,time=TIME);wrapper,replacements=self.certificate(plan)
        wrapper['approvals'][0]['signature']=proof(self.m['target'],STATE_DOMAIN,plan['payload'])
        with self.assertRaisesRegex(ValueError,'proof signature'):verify_candidate(wrapper,parents,replacements,time=TIME)

    def test_replacement_possession_is_not_supplied_by_another_administrator(self):
        parents=self.parents();plan=derive(parents,time=TIME);wrapper,replacements=self.certificate(plan)
        replacements[self.b['device']]['possession']=proof(self.m['source'],'email-next/device-possession/v0',plan['replacements'][self.b['device']])
        with self.assertRaisesRegex(ValueError,'proof signature'):verify_candidate(wrapper,parents,replacements,time=TIME)
        del replacements[self.b['device']]
        with self.assertRaisesRegex(ValueError,'Exact replacement proof set'):verify_candidate(wrapper,parents,replacements,time=TIME)

    def test_signature_valid_noncanonical_bytes_do_not_create_another_repair(self):
        parents=self.parents();plan=derive(parents,time=TIME);wrapper,replacements=self.certificate(plan)
        pretty=json.dumps(plan['value'],indent=2).encode()
        wrapper.update(payload=base64.b64encode(pretty).decode(),signature=proof(self.m['source'],STATE_DOMAIN,pretty),approvals=[dict(device=self.b['device'],signature=proof(self.m['target'],APPROVAL_DOMAIN,pretty))])
        with self.assertRaisesRegex(ValueError,'deterministic candidate'):verify_candidate(wrapper,parents,replacements,time=TIME)

    def test_certificate_cannot_be_transplanted_to_another_frontier(self):
        parents=self.parents();plan=derive(parents,time=TIME);wrapper,replacements=self.certificate(plan)
        other=self.parents(kind='enroll')
        with self.assertRaisesRegex(ValueError,'deterministic candidate'):verify_candidate(wrapper,other,replacements,time=TIME)
        with self.assertRaisesRegex(ValueError,'Distinct parent'):derive([parents[0],parents[0]],time=TIME)


if __name__=='__main__':unittest.main()
