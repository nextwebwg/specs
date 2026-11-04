"""Actual record/assertion signatures and native packages; configured identities only."""
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
from mail_setup import decode, verify, verify_response_candidate, creator_receiving_candidate
from provider_mls import advertisement, make_device, sign
from sealed_control import native, frame, seal, open_candidate
from suite_modules import offers, exchanges


def wire(value):
    return json.dumps(value,separators=(',',':')).encode()


class MailSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binary=Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR'])/'provider-mls'
        cls.a=make_device(cls.binary,51,52);cls.b=make_device(cls.binary,53,54)
        cls.now=max(cls.a['time'],cls.b['time']);cls.clock=dict(earliest=str(cls.now),latest=str(cls.now))
        cls.source_secret=native(cls.binary.with_name('sealed-control'),op='generate')
        cls.target_secret=native(cls.binary.with_name('sealed-control'),op='generate')

    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.store=IdentityStore(Path(tmp.name)/'identity.sqlite');self.addCleanup(self.store.close)
        for device in (self.a,self.b):self.store.observe(device['record'],first_contact_policy='allow-unverified')
        self.ads={}
        for kind,device,address,secret in [('request',self.a,'alice@example.org',self.source_secret),('response',self.b,'bob@example.org',self.target_secret)]:
            base=advertisement(self.binary,device,address);value=json.loads(base64.b64decode(base['payload']))
            expiry=self.now+120 if kind=='request' else self.now+600
            value.update(version='8',notBefore=str(self.now),notAfter=str(self.now+120),applications=offers(),orderingExchanges=exchanges(offers()),keyPackageReceiveUntil=None if kind=='request' else str(self.now+660),controlKey=dict(id=secret['id'],publicKey=secret['publicKey'],notBefore=str(self.now),notAfter=str(expiry),receiveUntil=str(expiry if kind=='request' else self.now+660)))
            if kind=='request':value['keyPackage']=[]
            payload=encode_event(value,nullable_members=('controlKey','keyPackageReceiveUntil'))
            self.ads[kind]=wire(dict(base,payload=base64.b64encode(payload).decode(),signature=sign(self.binary,device,'email-next/passive-discovery/v8',payload)))
        self.request=self.record('request')

    def record(self,kind,changes=None,*,advertised=None,domain=None):
        ad=advertised or self.ads[kind]
        value=dict(version='0',purpose='mailbox-setup-'+kind,request='1'*32,nonce='2'*64,source='alice@example.org',target='bob@example.org',assertion=hashlib.sha256(ad).hexdigest(),notBefore=str(self.now),notAfter=str(self.now+120))
        if kind=='response':value['requestDigest']=hashlib.sha256(base64.b64decode(json.loads(self.request)['payload'])).hexdigest()
        value.update(changes or {});payload=wire(value)
        signature=sign(self.binary,self.a if kind=='request' else self.b,domain or 'mail/setup-'+kind+'/v0',payload)
        return wire(dict(payload=base64.b64encode(payload).decode(),signature=signature,advertisement=base64.b64encode(ad).decode()))

    def check(self,raw,kind='request',**kwargs):
        return verify(raw,kind,self.store,self.binary,time=kwargs.pop('time',self.clock),trust_policy='allow-unverified',request=self.request if kind=='response' else None,**kwargs)

    def test_actual_request_response_and_no_identity_or_mailbox_promotion(self):
        before=self.store.db.total_changes
        self.assertEqual(self.check(self.request)['status'],'mailbox-setup-candidate-only')
        checked=self.check(self.record('response'),'response')
        self.assertEqual(checked['actor']['device'],self.b['device']);self.assertFalse(checked['mailbox_verified'])
        self.assertEqual(before,self.store.db.total_changes)

    def test_wrong_signature_domain_or_original_bytes(self):
        for kind in ('request','response'):
            with self.assertRaises(ValueError):self.check(self.record(kind,domain='mail/setup-'+('response' if kind=='request' else 'request')+'/v0'),kind)
        value=json.loads(self.request);raw=base64.b64decode(value['payload']);value['payload']=base64.b64encode(b' '+raw).decode()
        with self.assertRaises(ValueError):self.check(wire(value))

    def test_exact_nonce_target_request_and_payload_correlation(self):
        for changes in [dict(request='3'*32),dict(nonce='4'*64),dict(source='other@example.org'),dict(target='other@example.org'),dict(requestDigest='5'*64)]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):self.check(self.record('response',changes),'response')

    def test_attempt_expiry_bounds_and_no_timer_extension(self):
        with self.assertRaises(ValueError):self.check(self.request,time=dict(earliest=str(self.now+121),latest=str(self.now+121)))
        for changes in [dict(notAfter=str(self.now+601)),dict(notBefore=str(self.now+1)),dict(notAfter=str(self.now-1))]:
            with self.assertRaises(ValueError):self.check(self.record('request',changes))
        with self.assertRaises(ValueError):self.check(self.record('response',dict(notAfter=str(self.now+121))),'response')

    def test_assertion_commitment_actor_schema_and_duplicate_fields(self):
        for changes in [dict(assertion='6'*64),dict(source='bob@example.org'),dict(extra='x'),dict(version='1'),dict(purpose='provider-account-link')]:
            with self.assertRaises(ValueError):self.check(self.record('request',changes))
        with self.assertRaises(ValueError):decode(self.request[:-1]+b',"signature":"'+b'0'*128+b'"}', 'request')
        with self.assertRaises(ValueError):decode(self.request,'automatic')
        with self.assertRaises(ValueError):self.check(self.record('request',advertised=self.ads['response']))

    def test_creator_selects_separate_ordinary_assertion_not_attempt_key_or_other_device(self):
        key=native(self.binary.with_name('sealed-control'),op='generate')
        base=json.loads(self.ads['request']);value=json.loads(base64.b64decode(base['payload']))
        ordinary_key=dict(id=key['id'],publicKey=key['publicKey'],notBefore=str(self.now),notAfter=str(self.now+600),receiveUntil=str(self.now+660))
        def ordinary(control):
            raw=encode_event(dict(value,controlKey=control),nullable_members=('controlKey','keyPackageReceiveUntil'))
            return wire(dict(base,payload=base64.b64encode(raw).decode(),signature=sign(self.binary,self.a,'email-next/passive-discovery/v8',raw)))
        def select(raw):
            return creator_receiving_candidate(self.request,raw,self.store,self.binary,time=self.clock,trust_policy='allow-unverified')
        raw=ordinary(ordinary_key);selected=select(raw)
        self.assertEqual(selected['original_assertion'],raw)
        self.assertEqual(selected['actor']['device'],self.a['device'])
        self.assertEqual(selected['status'],'ordinary-creator-assertion-candidate-only')
        for rejected in [self.ads['request'],self.ads['response'],ordinary(dict(ordinary_key,id=value['controlKey']['id'])),ordinary(dict(ordinary_key,publicKey=value['controlKey']['publicKey']))]:
            with self.assertRaises(ValueError):select(rejected)

    def test_response_seals_to_exact_initiating_device_and_cannot_be_request(self):
        response=self.record('response');checked=self.check(response,'response')
        descriptor=json.loads(base64.b64decode(json.loads(self.ads['request'])['payload']))['controlKey']
        intent=dict(version='0',purpose='sealed-control-intent',record='7'*32,sender=checked['actor'],recipient={k:self.a[k] for k in ('principal','device')},key=descriptor['id'],kind='mailbox-setup-response',body=base64.b64encode(response).decode(),notBefore=str(self.now),notAfter=str(self.now+120))
        raw=wire(intent);sig=bytes.fromhex(sign(self.binary,self.b,'email2/sealed-control-intent/v0',raw))
        identity=wire(json.loads(self.ads['response'])['identity'])
        ciphertext=seal(self.binary.with_name('sealed-control'),descriptor,frame(raw,sig,identity),time=self.clock,recipient=intent['recipient'])
        self.assertNotIn(b'bob@example.org',ciphertext)
        args=dict(private_key=self.source_secret['privateKey'],descriptor=descriptor,recipient=intent['recipient'],identity=self.store,time=self.clock,expected_kind='mailbox-setup-response')
        candidate=open_candidate(self.binary.with_name('sealed-control'),ciphertext,**args)
        self.assertEqual(candidate['original_body'],response)
        bound=verify_response_candidate(candidate,self.request,self.store,self.binary,time=self.clock,trust_policy='allow-unverified')
        self.assertEqual(bound['actor'],checked['actor'])
        for change in [dict(sender={k:self.a[k] for k in ('principal','device','state','binding')}),dict(key='9'*32),dict(recipient={k:self.b[k] for k in ('principal','device')}),dict(notAfter=str(self.now+121))]:
            altered=dict(candidate,intent=dict(candidate['intent'],**change))
            with self.assertRaises(ValueError):verify_response_candidate(altered,self.request,self.store,self.binary,time=self.clock,trust_policy='allow-unverified')
        with self.assertRaises(ValueError):open_candidate(self.binary.with_name('sealed-control'),ciphertext,**dict(args,expected_kind='initial-invitation'))
        with self.assertRaises(ValueError):decode(candidate['original_body'],'request')


if __name__=='__main__':unittest.main()
