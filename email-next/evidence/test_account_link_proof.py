"""Real shared link signatures; account/module/descriptor facts are configured."""
import base64
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from account_link_proof import PreparedLink, account_link_proof, decode_account_status
from event_encoding import encode_event
from identity_store import IdentityStore
from provider_grants import PROFILE, framing
from test_history_transfer import identity_material


def wire(value):
    return json.dumps(value, separators=(',', ':')).encode()


class SharedAccountLinkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.material = identity_material(target_roles=['receive'])
        self.store = IdentityStore(Path(self.temp.name) / 'identity.sqlite'); self.addCleanup(self.store.close)
        self.store.observe(self.material['record'], first_contact_policy='allow-unverified')
        self.store.accept_successor(encode_event(self.material['bundle']), candidate_digest=self.material['head'], time=dict(earliest='20', latest='21'))
        self.device = self.material['refs'][1]

    def attempt(self, module='provider', mailbox='bob@example.org'):
        purpose={'provider':'provider-service-discovery','relay':'relay-service-discovery','bootstrap':'bootstrap-service-discovery'}[module]
        descriptor=dict(version='0',purpose=purpose,domain='example.org',publication='1'*32,generation='1',service='https://mail.example',managementPrefix='https://mail.example/manage/',notBefore='10',notAfter='100')
        if module=='provider':descriptor.update(controlPrefix='https://mail.example/control/')
        elif module=='relay':descriptor.update(permissionPrefix='https://mail.example/permissions/',roles=['accountability'])
        else:descriptor.update(sourcePrefix='https://mail.example/source/',exchangePrefix='https://mail.example/exchanges/',roles=['request-source'])
        raw_descriptor=wire(descriptor)
        value=dict(profile=PROFILE,purpose='provider-account-link',challenge='2'*32,request='3'*32,nonce='4'*64,delegationDigest=hashlib.sha256(raw_descriptor).hexdigest(),service=descriptor['service'],account='5'*64,family='6'*64,mailbox=mailbox,device=self.device,notBefore=10,notAfter=80)
        scopes={'provider':('mail.provider.link','mail.provider.manage'),'relay':('mail.relay.link',),'bootstrap':('mail.setup.link',)}[module]
        prepared=PreparedLink(module,module,raw_descriptor,wire(value),value['account'],value['family'],scopes,10,90)
        return prepared,value

    def sign(self, raw, key=None, kind='account-link'):
        return dict(payload=base64.b64encode(raw).decode(),signature=(key or self.material['target']).sign(framing(kind,raw)).hex())

    def check(self, prepared, proof=None, **kwargs):
        return account_link_proof(proof or self.sign(prepared.payload),prepared,self.store,time=kwargs.pop('time',(20,21)),trust_policy='allow-unverified',**kwargs)

    def test_all_modules_share_exact_framing_without_granting_send_authority(self):
        for module in ['provider','relay','bootstrap']:
            prepared,_=self.attempt(module)
            result=self.check(prepared)
            self.assertEqual(result['module'],module)
            self.assertEqual(result['principal'],self.device['principal'])
            self.assertNotIn('link',result)
            self.assertNotIn('accessToken',result)

    def test_other_module_scope_or_token_context_cannot_complete_link(self):
        p,_=self.attempt('relay')
        for changed in [replace(p,token_module='provider'),replace(p,scopes=('mail.provider.link',)),replace(p,scopes=('mail.relay.manage',))]:
            with self.assertRaises(ValueError):self.check(changed)

    def test_same_origin_does_not_make_another_descriptor_valid(self):
        p,_=self.attempt('relay');other,_=self.attempt('bootstrap')
        with self.assertRaises(ValueError):self.check(replace(p,descriptor=other.descriptor))
        with self.assertRaises(ValueError):self.check(replace(p,module='bootstrap',token_module='bootstrap',scopes=('mail.setup.link',)))

    def test_relay_contact_is_not_a_foreign_mailbox_domain_delegation(self):
        p,_=self.attempt('relay',mailbox='bob@personal.example')
        self.assertEqual(self.check(p)['module'],'relay')
        for module in ['provider','bootstrap']:
            p,_=self.attempt(module,mailbox='bob@personal.example')
            with self.assertRaisesRegex(ValueError,'mailbox-domain'):self.check(p)

    def test_wrong_key_and_signature_domain_are_rejected(self):
        p,_=self.attempt()
        for proof in [self.sign(p.payload,self.material['source']),self.sign(p.payload,kind='pair-approval')]:
            with self.assertRaises(ValueError):self.check(p,proof)

    def test_retained_original_bytes_not_equal_reserialized_claims(self):
        p,value=self.attempt();other=json.dumps(value,indent=2).encode()
        with self.assertRaisesRegex(ValueError,'retained'):self.check(p,self.sign(other))
        self.assertEqual(self.check(replace(p,payload=other),self.sign(other))['requestDigest'],hashlib.sha256(other).hexdigest())

    def test_inactive_changed_account_family_or_expired_authority_holds(self):
        p,_=self.attempt()
        for changed in [replace(p,active=False),replace(p,account='7'*64),replace(p,family='8'*64),replace(p,not_after=15)]:
            with self.assertRaises(ValueError):self.check(changed)
        with self.assertRaises(ValueError):self.check(p,time=(79,81))

    def test_revoked_receiving_key_cannot_link_under_active_bearer_context(self):
        p,_=self.attempt();m=self.material
        self.store.accept_successor(encode_event(m['removal']),candidate_digest=m['removed'],time=dict(earliest='20',latest='21'))
        with self.assertRaises(ValueError):self.check(p)

    def test_schema_and_encoding_fail_before_any_link_effect(self):
        p,value=self.attempt();before=self.store.current_state(self.device['principal'])
        for changed in [dict(value,extra=True),dict(value,notBefore=True),dict(value,notBefore='10')]:
            raw=wire(changed)
            with self.assertRaises(ValueError):self.check(replace(p,payload=raw),self.sign(raw))
        proof=self.sign(p.payload);proof['payload']+='\n'
        with self.assertRaises(ValueError):self.check(p,proof)
        self.assertEqual(self.store.current_state(self.device['principal']),before)


class AccountInspectionTests(unittest.TestCase):
    def account(self):
        return dict(profile=PROFILE,purpose='provider-account-state',account='1'*64,family='2'*64,principal='')

    def reset(self):
        return dict(profile=PROFILE,purpose='provider-account-reset-state',account='3'*64,preparation='4'*32,outcome='completed')

    def test_current_account_and_each_retained_outcome(self):
        for principal in ['', 'enp0:'+'5'*64]:
            value=self.account();value['principal']=principal
            self.assertEqual(decode_account_status(wire(value),kind='account'),value)
        for outcome in ['pending','completed','expired']:
            value=self.reset();value['outcome']=outcome
            self.assertEqual(decode_account_status(wire(value),kind='reset',preparation='4'*32),value)

    def test_exact_schema_no_grammar_or_route_fallback(self):
        value=self.account()
        bad=[dict(value,extra='x'),dict(value,principal=None),dict(value,principal='enp0:'+'0'*64),dict(value,family='A'*64),dict(value,account=1),dict(value,purpose='provider-account-reset-state')]
        for changed in bad:
            with self.assertRaises(ValueError):decode_account_status(wire(changed),kind='account')
        with self.assertRaises(ValueError):decode_account_status(wire(value)[:-1]+b',"family":"'+b'2'*64+b'"}',kind='account')
        with self.assertRaises(ValueError):decode_account_status(wire(value),kind='automatic')
        with self.assertRaises(ValueError):decode_account_status(wire(value),kind='account',preparation='4'*32)

    def test_original_preparation_and_closed_outcome_set(self):
        value=self.reset()
        for preparation in [None,'0'*32,'5'*32]:
            with self.assertRaises(ValueError):decode_account_status(wire(value),kind='reset',preparation=preparation)
        for outcome in ['unknown','failed',None,True]:
            with self.assertRaises(ValueError):decode_account_status(wire(dict(value,outcome=outcome)),kind='reset',preparation='4'*32)


if __name__=='__main__':unittest.main()
