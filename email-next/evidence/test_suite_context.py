import copy
import unittest
from suite_context import validate,check_private_stream_role,check_roster
from suite_modules import application,STREAM,QUORUM

OWNER=dict(principal='enp0:'+'1'*64,device='end0:'+'2'*64,signingKey='3'*64,state='4'*64,binding='5'*64)

def context():return dict(version='8',purpose='conversation-context',conversation='6'*32,profile='mls-1-0001',administrators=[OWNER['principal']],application=application(),ordering=dict(kind=STREAM,stream='7'*32,owner=copy.deepcopy(OWNER)),delivery=dict(kind='ordinary-v0'))

class SuiteContextTests(unittest.TestCase):
    def test_exact_source_birth_context(self):self.assertEqual(validate(context()),context())
    def test_owner_is_exact_device_and_birth_key_not_just_administrator_name(self):
        for update in [dict(owner=dict(OWNER,extra='x')),dict(owner=dict(OWNER,device='end0:'+'0'*64)),dict(stream='0'*32),dict(kind='designated-member-v0')]:
            v=context();v['ordering'].update(update)
            with self.subTest(update=update),self.assertRaises(ValueError):validate(v)
        v=context();v['administrators']=['enp0:'+'8'*64]
        with self.assertRaises(ValueError):validate(v)
    def test_private_copy_originator_and_no_old_context_relabeling(self):
        v=context();v['delivery']=dict(kind='private-copy-v0',originator=OWNER['principal'],recipient='enp0:'+'8'*64);validate(v)
        v['delivery']['originator']='enp0:'+'9'*64
        with self.assertRaises(ValueError):validate(v)
        v=context();v['version']='7'
        with self.assertRaises(ValueError):validate(v)
    def test_private_recipient_can_own_return_stream_without_role_swap(self):
        v=context();pair=dict(kind='private-copy-v0',originator=OWNER['principal'],recipient='enp0:'+'8'*64)
        v['delivery']=pair;check_private_stream_role(v,expected_delivery=pair,established=False)
        v['ordering']['owner']['principal']=pair['recipient'];v['administrators']=[pair['recipient']]
        self.assertEqual(check_private_stream_role(v,expected_delivery=pair,established=True)['status'],'private-role-selection-only')
        self.assertEqual(check_roster(v,[pair['originator'],pair['recipient']])['status'],'context-roster-only')
        with self.assertRaises(ValueError):check_private_stream_role(v,expected_delivery=pair,established=False)
        swapped=dict(pair,originator=pair['recipient'],recipient=pair['originator'])
        with self.assertRaises(ValueError):check_private_stream_role(v,expected_delivery=swapped,established=True)
        for roster in ([pair['originator']], [pair['recipient']], [pair['originator'],pair['recipient'],'enp0:'+'9'*64]):
            with self.subTest(roster=roster),self.assertRaises(ValueError):check_roster(v,roster)

    def test_managed_context_retains_witness_shape_and_fault_bound(self):
        v=context();v['ordering']=dict(kind=QUORUM,generation='0',faultBound='0',witnesses=[OWNER]);validate(v)
        v['ordering']['faultBound']='1'
        with self.assertRaises(ValueError):validate(v)
    def test_unknown_fields_and_partial_modules_are_not_context8(self):
        v=context();v['application']['operations']=['message']
        with self.assertRaises(ValueError):validate(v)
        v=context();v['audience']=[]
        with self.assertRaises(ValueError):validate(v)

if __name__=='__main__':unittest.main()
