"""Real endpoint/route signatures and SQLite acceptance, configured service facts."""
import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from event_encoding import encode_event
from identity_store import IdentityStore
from relay_routes import AccountLink,SourceObservation,RelayRoutes,parse,proof
from test_history_transfer import identity_material,public


class RelayRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'relay.sqlite'
        self.identity=IdentityStore(self.path)
        self.addCleanup(lambda:self.identity.close())
        self.a=identity_material('enp0:'+'a'*64);self.b=identity_material('enp0:'+'b'*64)
        for m in [self.a,self.b]:
            self.assertEqual(self.identity.observe(m['record'],first_contact_policy='allow-unverified')['status'],'pinned-unverified')
            self.assertEqual(self.identity.accept_successor(encode_event(m['bundle']),candidate_digest=m['head'],time=dict(earliest='20',latest='21'))['status'],'accepted-unverified')
        self.sender=self.a['refs'][1];self.recipient=self.b['refs'][1]
        self.route_key=Ed25519PrivateKey.generate()
        self.link=AccountLink(account='1'*64,incarnation='2'*64,link='3'*32,family='4'*64,recipient=self.recipient)
        self.service='https://destination.example';self.delegation='5'*64
        self.routes=RelayRoutes(self.identity,self.service,alias_domain='destination.example',delegation=self.delegation)
        self.source_value=dict(version='0',purpose='relay-source-permission',preparation='1'*32,request='2'*32,nonce='6'*64,
            permission='7'*64,domain='source.example',issuer='https://source.example',delegation='8'*64,source='9'*64,incarnation='a'*64,
            sender=self.sender,recipient=self.recipient['principal'],conversation='3'*32,routeKey=public(self.route_key),
            targetService=self.service,senderMode='shared-relay',outerFrom='relay@source.example',notBefore='10',notAfter='90',maxCarrierBytes='1000')
        self.source=self.source_observation(self.source_value)
        self.grant_value=dict(version='0',purpose='relay-route-approval',preparation='4'*32,request='5'*32,nonce='b'*64,
            issuer=self.service,delegation=self.delegation,route='c'*64,alias='r-'+'6'*32+'@destination.example',
            recipient=self.recipient,sender=self.sender,conversation='3'*32,sourceDomain=self.source_value['domain'],sourceService=self.source_value['issuer'],
            sourcePermission=self.source_value['permission'],sourceDigest=hashlib.sha256(encode_event(self.source_value)).hexdigest(),
            routeKey=public(self.route_key),notBefore='10',notAfter='80',maxCarrierBytes='900')
        self.calls=[]
        self.approval=self.sign_grant(self.grant_value)
        self.activate()
        self.carrier=b'configured opaque ciphertext fixture'
        self.delivery=self.sign_delivery()

    def source_observation(self,value,key=None):
        return SourceObservation(value['issuer'],proof('source-permission',encode_event(value),key or self.a['target']),
                                 'source.example','8'*64)

    def sign_grant(self,value,key=None):
        return proof('route-approval',encode_event(value),key or self.b['target'])

    def sign_delivery(self,**changes):
        delivery=changes.pop('delivery','7'*32)
        v=dict(version='0',purpose='relay-delivery',issuer=self.service,route=self.grant_value['route'],delivery=delivery,
            alias=self.grant_value['alias'],outerFrom='relay@source.example',mailFrom='b-'+delivery+'@source.example',
            messageId='<m-'+delivery+'@source.example>',carrierSha256=hashlib.sha256(self.carrier).hexdigest(),
            carrierBytes=str(len(self.carrier)),notBefore='20',notAfter='70')
        v.update(changes)
        return proof('delivery',encode_event(v),self.route_key)

    def fetch(self,domain,origin,permission):
        self.calls.append((domain,origin,permission))
        self.assertEqual((domain,origin,permission),(self.source_value['domain'],self.source_value['issuer'],self.source_value['permission']))
        return self.source

    def activate(self,approval=None,**kwargs):
        approval=approval or self.approval
        raw,_,_=parse(approval,'route-approval')
        return self.routes.activate(approval,retained_preparation=kwargs.pop('retained_preparation',raw),
                                   link=kwargs.pop('link',self.link),fetch=kwargs.pop('fetch',self.fetch),**kwargs)

    def admit(self,delivery=None,**kwargs):
        delivery=delivery or self.delivery
        _,d,_=parse(delivery,'delivery')
        observed={k:d[k] for k in ['alias','outerFrom','mailFrom','messageId']}
        return self.routes.admit(delivery,kwargs.pop('carrier',self.carrier),observed=kwargs.pop('observed',observed),
                                 link=kwargs.pop('link',self.link),fetch=kwargs.pop('fetch',self.fetch),**kwargs)

    def intents(self):return self.identity.db.execute('SELECT count(*) FROM relay_inbox_intent').fetchone()[0]

    def test_actual_device_and_route_signatures_accept_once_and_fetch_every_new_delivery(self):
        self.calls.clear()
        self.assertEqual(self.admit(),'accepted-local-inbox-intent')
        self.assertEqual(self.admit(),'duplicate-previously-accepted')
        self.assertEqual(len(self.calls),1)
        self.assertEqual(self.admit(self.sign_delivery(delivery='8'*32)),'accepted-local-inbox-intent')
        self.assertEqual(len(self.calls),2);self.assertEqual(self.intents(),2)

    def test_forwarded_alias_is_not_route_key_possession(self):
        raw,_,_=parse(self.delivery,'delivery')
        foreign=proof('delivery',raw,Ed25519PrivateKey.generate())
        with self.assertRaises(ValueError):self.admit(foreign)
        self.assertEqual(self.intents(),0)

    def test_wrong_recipient_signer_cannot_activate_route(self):
        with self.assertRaises(ValueError):self.activate(self.sign_grant(self.grant_value,self.a['target']))

    def test_changed_retained_preparation_cannot_authorize_activation(self):
        with self.assertRaises(ValueError):self.activate(retained_preparation=b'{}')

    def test_account_incarnation_family_and_link_are_not_message_choices(self):
        for patch in [dict(account='f'*64),dict(incarnation='f'*64),dict(family='f'*64),dict(link='f'*32),dict(active=False)]:
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.admit(link=replace(self.link,**patch))
        self.assertEqual(self.intents(),0)

    def test_source_live_account_withdrawal_and_dependency_failure_hold_new_delivery(self):
        self.source=replace(self.source,active=False)
        with self.assertRaises(ValueError):self.admit()
        def unavailable(*args):raise RuntimeError('Configured dependency unavailable')
        with self.assertRaises(RuntimeError):self.admit(fetch=unavailable)
        self.assertEqual(self.intents(),0)

    def test_source_tls_origin_and_descriptor_cannot_be_replaced_by_payload(self):
        for patch in [dict(origin='https://attacker.example'),dict(delegation='f'*64),dict(domain='attacker.example'),dict(roles=('accountability',))]:
            wrong=replace(self.source,**patch)
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.admit(fetch=lambda *args:wrong)

    def test_signed_source_scope_substitution_fails(self):
        for patch in [dict(recipient=self.sender['principal']),dict(conversation='f'*32),dict(targetService='https://other.example'),
                      dict(routeKey='f'*64),dict(permission='f'*64),dict(outerFrom='other@source.example')]:
            changed=self.source_observation(dict(self.source_value,**patch))
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.admit(fetch=lambda *args:changed)

    def test_two_valid_signatures_still_cannot_cross_peer_scope(self):
        for patch in [dict(recipient=self.sender['principal']),dict(conversation='f'*32),dict(targetService='https://other.example'),dict(routeKey='f'*64)]:
            value=dict(self.source_value,**patch);observation=self.source_observation(value)
            grant=dict(self.grant_value,route='d'*64,alias='r-'+'b'*32+'@destination.example',sourceDigest=hashlib.sha256(encode_event(value)).hexdigest())
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.activate(self.sign_grant(grant),fetch=lambda *args:observation)

    def test_invalid_source_signature_does_not_become_account_evidence(self):
        changed=self.source_observation(self.source_value,Ed25519PrivateKey.generate())
        with self.assertRaises(ValueError):self.admit(fetch=lambda *args:changed)

    def test_validly_signed_grant_cannot_use_other_domain_or_descriptor(self):
        for patch in [dict(alias='r-'+'9'*32+'@elsewhere.example'),dict(delegation='f'*64),dict(alias='personal@destination.example')]:
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.activate(self.sign_grant(dict(self.grant_value,**patch)))

    def test_outer_envelope_and_carrier_must_match_original_delivery(self):
        _,d,_=parse(self.delivery,'delivery')
        for key in ['alias','outerFrom','mailFrom','messageId']:
            observed={k:d[k] for k in ['alias','outerFrom','mailFrom','messageId']};observed[key]='forged'
            with self.subTest(key=key),self.assertRaises(ValueError):self.admit(observed=observed)
        with self.assertRaises(ValueError):self.admit(carrier=self.carrier+b'x')
        for patch in [dict(mailFrom='personal@source.example'),dict(messageId='<other@source.example>'),dict(outerFrom='other@source.example')]:
            with self.assertRaises(ValueError):self.admit(self.sign_delivery(**patch))

    def test_new_expired_or_overbroad_delivery_cannot_enqueue(self):
        for patch in [dict(notAfter='81'),dict(notBefore='22'),dict(notAfter='19')]:
            # Invalid inverted intervals can also fail at serialization helper.
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.admit(self.sign_delivery(**patch))
        with self.assertRaises(ValueError):self.admit(time=(80,81))
        self.assertEqual(self.intents(),0)

    def test_invalid_signature_cannot_poison_delivery_collision_index(self):
        raw,_,_=parse(self.delivery,'delivery');bad=proof('delivery',raw,Ed25519PrivateKey.generate())
        with self.assertRaises(ValueError):self.admit(bad)
        self.assertEqual(self.admit(),'accepted-local-inbox-intent')

    def test_authenticated_changed_bytes_under_delivery_id_conflict(self):
        self.admit()
        with self.assertRaises(ValueError):self.admit(self.sign_delivery(notAfter='69'))
        self.assertEqual(self.intents(),1)

    def test_revoke_blocks_new_delivery_but_exact_prior_ack_does_not_reenqueue(self):
        self.admit();self.routes.revoke(self.link.account,self.grant_value['route'])
        self.source=replace(self.source,active=False)
        self.assertEqual(self.admit(time=(90,91),link=replace(self.link,active=False)),'duplicate-previously-accepted')
        with self.assertRaises(ValueError):self.admit(self.sign_delivery(delivery='8'*32))
        self.assertEqual(self.intents(),1)

    def test_wrong_account_cannot_revoke_another_route(self):
        self.routes.revoke('f'*64,self.grant_value['route'])
        self.assertEqual(self.admit(),'accepted-local-inbox-intent')

    def test_alias_is_never_reassigned_even_after_revocation(self):
        self.routes.revoke(self.link.account,self.grant_value['route'])
        changed=dict(self.grant_value,route='d'*64,preparation='a'*32)
        with self.assertRaises(ValueError):self.activate(self.sign_grant(changed))
        with self.assertRaises(ValueError):self.activate()

    def test_account_scoped_block_applies_to_new_alias_and_source_incarnation(self):
        self.routes.block(self.link.account,self.source_value['issuer'],self.source_value['source'])
        self.source_value=dict(self.source_value,permission='d'*64,incarnation='e'*64)
        self.source=self.source_observation(self.source_value)
        changed=dict(self.grant_value,route='e'*64,alias='r-'+'a'*32+'@destination.example',sourcePermission='d'*64,
                     sourceDigest=hashlib.sha256(encode_event(self.source_value)).hexdigest())
        with self.assertRaises(ValueError):self.activate(self.sign_grant(changed))
        with self.assertRaises(ValueError):self.routes.block('f'*64,self.source_value['issuer'],self.source_value['source'])

    def test_blocked_peer_cannot_switch_relay_services_to_reuse_same_identity(self):
        self.routes.block(self.link.account,self.source_value['issuer'],self.source_value['source'])
        self.source_value=dict(self.source_value,domain='elsewhere.example',issuer='https://elsewhere.example',source='e'*64,outerFrom='relay@elsewhere.example')
        self.source=SourceObservation(self.source_value['issuer'],proof('source-permission',encode_event(self.source_value),self.a['target']),'elsewhere.example','8'*64)
        changed=dict(self.grant_value,route='e'*64,alias='r-'+'a'*32+'@destination.example',sourceDomain=self.source_value['domain'],sourceService=self.source_value['issuer'],
                     sourceDigest=hashlib.sha256(encode_event(self.source_value)).hexdigest())
        with self.assertRaisesRegex(ValueError,'account/peer blocked'):self.activate(self.sign_grant(changed))

    def test_unrelated_signed_successors_preserve_original_route_and_proofs(self):
        import base64
        from test_history_transfer import proof as state_proof
        for material in [self.a,self.b]:
            bundle=copy.deepcopy(material['bundle'])
            value=json.loads(base64.b64decode(bundle['states'][-1]['payload']))
            value.update(record='d'*32,revision='2',previous=[material['head']],issuedAt='12')
            raw=encode_event(value)
            bundle['states'].append(dict(payload=base64.b64encode(raw).decode(),signature=state_proof(material['source'],'email-next/identity-state/v0',raw)))
            self.assertEqual(self.identity.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(raw).hexdigest(),time=dict(earliest='20',latest='21'))['status'],'accepted-unverified')
        self.assertEqual(self.admit(),'accepted-local-inbox-intent')
        self.assertEqual(self.intents(),1)
        self.assertEqual(self.admit(),'duplicate-previously-accepted')
        self.assertEqual(self.intents(),1)
        self.assertEqual(self.sender['state'],self.a['head'])
        self.assertEqual(self.recipient['state'],self.b['head'])
        with self.assertRaises(ValueError): self.admit(self.sign_delivery(delivery='8'*32),time=(81,82))

    def test_actual_source_and_recipient_device_revocation_hold_route(self):
        for material in [self.a,self.b]:
            self.identity.accept_successor(encode_event(material['removal']),candidate_digest=material['removed'],time=dict(earliest='20',latest='21'))
            with self.assertRaises(ValueError):self.admit()
        self.assertEqual(self.intents(),0)

    def test_route_offer_must_fit_local_link_lifetime(self):
        for patch in [dict(not_before=11),dict(not_after=79)]:
            with self.assertRaises(ValueError):self.activate(link=replace(self.link,**patch))

    def test_strict_verification_policy_does_not_upgrade_unverified_identity(self):
        with self.assertRaises(ValueError):self.admit(policy='require-verification')

    def test_restart_and_rollback_keep_one_atomic_inbox_intent(self):
        def fail(stage):raise RuntimeError(stage)
        with self.assertRaises(RuntimeError):self.admit(crash=fail)
        self.assertEqual(self.intents(),0)
        self.identity.close();self.identity=IdentityStore(self.path)
        self.routes=RelayRoutes(self.identity,self.service,alias_domain='destination.example',delegation=self.delegation)
        self.assertEqual(self.admit(),'accepted-local-inbox-intent')
        self.assertEqual(self.admit(),'duplicate-previously-accepted')
        self.assertEqual(self.intents(),1)

    def test_process_exit_before_commit_leaves_no_acknowledged_inbox_intent(self):
        request=Path(self.temp.name)/'request.json'
        request.write_text(json.dumps(dict(delivery=self.delivery,carrier=self.carrier.hex(),source=self.source.permission,
            recipient=self.recipient,db=str(self.path))))
        self.identity.close()
        script='''import json,os,sys
from identity_store import IdentityStore
from relay_routes import AccountLink,SourceObservation,RelayRoutes,parse
v=json.load(open(sys.argv[1]));db=IdentityStore(v['db'])
r=RelayRoutes(db,'https://destination.example',alias_domain='destination.example',delegation='5'*64)
l=AccountLink('1'*64,'2'*64,'3'*32,'4'*64,v['recipient'])
_,d,_=parse(v['delivery'],'delivery');observed={k:d[k] for k in ['alias','outerFrom','mailFrom','messageId']}
r.admit(v['delivery'],bytes.fromhex(v['carrier']),observed=observed,link=l,fetch=lambda *a:SourceObservation('https://source.example',v['source'],'source.example','8'*64),crash=lambda stage:os._exit(91))
'''
        result=subprocess.run([sys.executable,'-c',script,str(request)],cwd=Path(__file__).parent,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        self.assertEqual(result.returncode,91,result.stderr.decode())
        self.identity=IdentityStore(self.path);self.routes=RelayRoutes(self.identity,self.service,alias_domain='destination.example',delegation=self.delegation)
        self.assertEqual(self.intents(),0);self.assertEqual(self.admit(),'accepted-local-inbox-intent')

    def test_record_strictness_and_signature_purpose(self):
        raw,_,_=parse(self.delivery,'delivery')
        for bad in [dict(self.delivery,extra='x'),dict(self.delivery,payload='Zg'),dict(self.delivery,signature='0'*128),
                    dict(payload=self.delivery['payload'],signature=Ed25519PrivateKey.generate().sign(b'other-purpose'+raw).hex())]:
            with self.assertRaises(ValueError):self.admit(bad)
        malformed=raw.replace(b'"version":"0"',b'"version":"0","\\u0076ersion":"0"')
        import base64
        with self.assertRaises(ValueError):parse(dict(self.delivery,payload=base64.b64encode(malformed).decode()),'delivery')


if __name__=='__main__':unittest.main()
