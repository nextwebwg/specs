import base64
import copy
import json
from pathlib import Path
import subprocess
import unittest
from provider_control import (DEFAULT_LIMITS, OPERATIONS, PROFILE, DOMAIN,
 validate_configuration, validate_request, validate_response, decode, node)


def wire(value):
    return json.dumps(value,separators=(',',':'),ensure_ascii=False).encode()


class ProviderControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder=Path(__file__).parent
        script=(folder/'make-passive-discovery-fixture.mjs').read_text().split('process.stdout.write')[0]
        script+="""process.stdout.write(JSON.stringify({advertisement:good,targetKey:binding.signingKey,
 targetPrivate:privateKey.export({format:'der',type:'pkcs8'}).toString('base64'),
 initiatorKey:other.publicKey.export({format:'der',type:'spki'}).subarray(-32).toString('hex'),
 initiatorPrivate:other.privateKey.export({format:'der',type:'pkcs8'}).toString('base64'),state:hash(s),binding:hash(b)}));"""
        cls.f=json.loads(subprocess.run(['node','--input-type=module','-e',script],cwd=folder,
            capture_output=True,text=True,check=True).stdout)

    def setUp(self):
        self.c=dict(profile=PROFILE,grant='1'*64,account='2'*64,service='https://example.com',
          prefix='https://example.com/control/',initiator={'principal':'enp0:'+'c'*64,'device':'end0:'+'d'*64},
          target={'principal':'enp0:'+'a'*64,'device':'end0:'+'b'*64},initiatorState='3'*64,
          initiatorBinding='4'*64,targetState=self.f['state'],targetBinding=self.f['binding'],
          role='initiator',operations=OPERATIONS['initiator'][:],notBefore=10,notAfter=100,
          limits=DEFAULT_LIMITS.copy())
        self.r={k:self.c[k] for k in ['profile','service','prefix','grant','account','initiator','target',
            'initiatorState','initiatorBinding','targetState','targetBinding']}
        self.r.update(kind='challenge',id='5'*64,nonce='6'*64,notBefore=15,notAfter=90,purpose='fresh-device-discovery')
        self.request=self.sign(self.r)
        import hashlib
        self.response={k:self.r[k] for k in ['profile','id','service','prefix','grant','account','initiator','target','nonce']}
        self.response.update(kind='device-evidence',requestHash=hashlib.sha256(wire(self.r)).hexdigest(),
                             notBefore=20,notAfter=80,advertisement=copy.deepcopy(self.f['advertisement']))

    def sign(self,value,role='initiator',domain=DOMAIN):
        raw=wire(value); signed=domain+len(raw).to_bytes(4,'big')+raw
        script="""import {createPrivateKey,sign} from 'node:crypto';let s='';for await(const c of process.stdin)s+=c;
const v=JSON.parse(s);console.log(JSON.stringify(sign(null,Buffer.from(v.bytes,'base64'),createPrivateKey({key:Buffer.from(v.key,'base64'),format:'der',type:'pkcs8'})).toString('hex')));"""
        sig=node(script,{'bytes':base64.b64encode(signed).decode(),'key':self.f[role+'Private']})
        return wire({'payload':base64.b64encode(raw).decode(),'signature':sig})

    def check_request(self,request=None,time=(20,21)):
        return validate_request(request or self.request,self.c,self.f['initiatorKey'],route_id='5'*64,time=time)

    def check_response(self,response=None):
        return validate_response(response or self.sign(self.response,'target'),self.request,self.c,
            self.f['initiatorKey'],self.f['targetKey'],route_id='5'*64,time=(20,21),target_mailbox='Alice@example.com')

    def test_actual_signatures_and_role_configurations(self):
        self.assertEqual(validate_configuration(wire(self.c)),self.c)
        target=copy.deepcopy(self.c);target.update(role='target',operations=OPERATIONS['target'][:])
        self.assertEqual(validate_configuration(wire(target)),target)
        self.assertEqual(self.check_request()['status'],'signature-valid-only')
        self.assertEqual(self.check_request()['new_admission_time'],'within-intervals')
        self.assertEqual(self.check_request(time=(101,102))['status'],'signature-valid-only')
        self.assertEqual(self.check_request(time=None)['new_admission_time'],'unavailable')
        result=self.check_response()
        self.assertFalse(result['identity_authorized']);self.assertFalse(result['mls_validated'])

    def test_expired_response_remains_inspectable_without_admission(self):
        result=validate_response(self.sign(self.response,'target'),self.request,self.c,
            self.f['initiatorKey'],self.f['targetKey'],route_id='5'*64,time=(101,102),target_mailbox='Alice@example.com')
        self.assertEqual(result['status'],'signature-valid-only')
        self.assertEqual(result['new_admission_time'],'not-usable')

    def test_configuration_exact_types_limits_and_origin(self):
        variants=[dict(role='both'),dict(operations=['response-write']),dict(notBefore=True),
            dict(service='https://example.com:443'),dict(prefix='https://example.com/a/../'),
            dict(prefix='https://evil.example/control/'),dict(service='https://xn--a.example'),dict(extra='x')]
        for change in variants:
            with self.subTest(change=change),self.assertRaises(ValueError):
                validate_configuration(wire(dict(self.c,**change)))
        for field,value in [('maxPendingPerGrant',True),('maxResponseBytes',1),('maxJsonDepth',0)]:
            c=copy.deepcopy(self.c);c['limits'][field]=value
            with self.assertRaises(ValueError):validate_configuration(wire(c))

    def test_duplicate_json_and_bounded_parsing(self):
        for body in [b'{"a":1,"\\u0061":2}',b'{"a":NaN}',b'{"a":true}',b'{"a":"\\ud800"}',b'\xff']:
            with self.assertRaises(ValueError):decode(body,max_bytes=100,max_depth=2)
        with self.assertRaises(ValueError):decode(b'[[[]]]',max_bytes=100,max_depth=2)
        with self.assertRaises(ValueError):decode(b'{}',max_bytes=1,max_depth=2)
        w=json.loads(self.request);w['payload']+='\n'
        with self.assertRaises(ValueError):self.check_request(wire(w))
        w=json.loads(self.request);w['signature']='A'*128
        with self.assertRaises(ValueError):self.check_request(wire(w))

    def test_domain_key_tampering_and_request_context(self):
        for body in [self.sign(self.r,domain=b'wrong\0'),self.sign(self.r,'target')]:
            with self.assertRaises(ValueError):self.check_request(body)
        w=json.loads(self.request);w['payload']=base64.b64encode(wire(dict(self.r,nonce='7'*64))).decode()
        with self.assertRaises(ValueError):self.check_request(wire(w))
        for change in [dict(id='7'*64),dict(account='7'*64),dict(purpose='other'),dict(targetState='7'*64),dict(extra='x')]:
            with self.subTest(change=change),self.assertRaises(ValueError):self.check_request(self.sign(dict(self.r,**change)))

    def test_time_and_response_binding(self):
        for time in [(9,10),(20,30),(22,21),(91,92),(True,21)]:
            with self.subTest(time=time):self.assertEqual(self.check_request(time=time)['new_admission_time'],'not-usable')
        for change in [dict(nonce='7'*64),dict(requestHash='7'*64),dict(kind='challenge'),
                       dict(notAfter=91),dict(notBefore=14),dict(grant='7'*64)]:
            with self.subTest(change=change),self.assertRaises(ValueError):
                self.check_response(self.sign(dict(self.response,**change),'target'))

    def test_nested_passive_proof_and_exact_binding(self):
        for name,value in [('signature','0'*128),('payload',self.f['advertisement']['payload']+'\n')]:
            response=copy.deepcopy(self.response);response['advertisement'][name]=value
            with self.assertRaises(ValueError):self.check_response(self.sign(response,'target'))
        with self.assertRaises(ValueError):
            validate_response(self.sign(self.response,'target'),self.request,self.c,self.f['initiatorKey'],
                self.f['targetKey'],route_id='5'*64,time=(20,21),target_mailbox='Mallory@example.com')

if __name__=='__main__':unittest.main()
