import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
import test_provider_http as http_tests
from provider_http import ProviderHTTP
from provider_control import DEFAULT_LIMITS,OPERATIONS,PROFILE,validate_response,validate_request
from provider_mls import make_device,advertisement,sign,call,Admission
from identity_store import IdentityStore
from passive_discovery_verify import verify_passive_discovery
from passive_discovery import decode_passive_discovery
from passive_discovery_package import validate_package
from event_encoding import encode_event
from mls_mime import package,unpack
from smtp_loopback import roundtrip
from mls_receive import MlsReceive


def carrier(value):return json.loads(unpack(roundtrip(package(encode_event(value)))))


def crash_admission(path,binary,reference,invitation,peers,group,context,time,stage):
    identity=IdentityStore(path)
    admission=Admission(identity,binary)
    def crash(where):
        if where==stage:os._exit(91)
    admission.accept(reference,invitation,peers=peers,expected_group=group,expected_context=context,time=time,crash=crash)
    os._exit(92)


class ProviderMlsTests(unittest.TestCase):
    send=http_tests.ProviderHTTPTests.send
    @classmethod
    def setUpClass(cls):
        http_tests.ProviderHTTPTests.setUpClass()
        cls.tls=http_tests.ProviderHTTPTests.tls;cls.cert=http_tests.ProviderHTTPTests.cert;cls.key=http_tests.ProviderHTTPTests.key
        cls.binary=Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR'])/'provider-mls'
    @classmethod
    def tearDownClass(cls):http_tests.ProviderHTTPTests.tearDownClass()
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.a=make_device(self.binary,1,2);self.b=make_device(self.binary,3,4)
        self.now=(max(self.a['time'],self.b['time']),)*2
        self.time={'earliest':str(self.now[0]),'latest':str(self.now[1])}
        self.identity=IdentityStore(self.root/'target.sqlite')
        self.initiator=IdentityStore(self.root/'initiator.sqlite')
        for store in [self.identity,self.initiator]:
            for device in [self.a,self.b]:self.assertEqual(store.observe(device['record'],first_contact_policy='allow-unverified')['status'],'pinned-unverified')
        self.admission=Admission(self.identity,self.binary);self.admission.publish_local(self.b)
        self.c=dict(profile=PROFILE,grant='1'*64,account='2'*64,service='https://example.com',prefix='https://example.com/control/',
          initiator={k:self.a[k] for k in ['principal','device']},target={k:self.b[k] for k in ['principal','device']},
          initiatorState=self.a['state'],initiatorBinding=self.a['binding'],targetState=self.b['state'],targetBinding=self.b['binding'],
          role='initiator',operations=OPERATIONS['initiator'][:],notBefore=self.now[0]-30,notAfter=self.now[0]+300,limits=DEFAULT_LIMITS.copy())
        target=dict(self.c,role='target',operations=OPERATIONS['target'][:])
        creds={}
        for token,c in [('init-token',self.c),('target-token',target)]:creds[token]=dict(configuration=c,notBefore=self.c['notBefore'],notAfter=self.c['notAfter'],initiatorKey=self.a['key'],targetKey=self.b['key'],targetMailbox='Bob@example.com')
        self.server=ProviderHTTP(self.root/'http.sqlite',creds,self.cert,self.key,lambda:self.now).start()
        self.context=(Path(__file__).parent/'mls-smoke/fixtures/context.json').read_bytes()
    def tearDown(self):self.server.close();self.identity.close();self.initiator.close();self.temp.cleanup()
    def wrapped(self,device,value):
        raw=encode_event(value) if all(not isinstance(v,int) for v in value.values()) else json.dumps(value,separators=(',',':')).encode()
        return json.dumps({'payload':base64.b64encode(raw).decode(),'signature':sign(self.binary,device,'email-next/provider-control/v0',raw)},separators=(',',':')).encode()
    def discover(self):
        request={k:self.c[k] for k in ['profile','service','prefix','grant','account','initiator','target','initiatorState','initiatorBinding','targetState','targetBinding']}
        request.update(kind='challenge',id='5'*64,nonce='6'*64,notBefore=self.now[0],notAfter=self.now[0]+100,purpose='fresh-device-discovery')
        raw=self.wrapped(self.a,request)
        self.assertEqual(self.send('PUT','exchanges/'+'5'*64+'/request',body=raw)[0],201)
        retrieved=json.dumps(self.send('GET','exchanges/'+'5'*64,'target-token')[1]['request'],separators=(',',':')).encode()
        validate_request(retrieved,self.c,self.a['key'],route_id='5'*64,time=self.now)
        authority=self.identity.check_device(bytes.fromhex(self.a['identity']),bytes.fromhex(self.a['key']),role='receive',time=self.time,trust_policy='allow-unverified')
        self.assertEqual(authority['status'],'authorized-unverified');self.assertEqual(authority['head'],self.a['state'])
        response={k:request[k] for k in ['profile','service','prefix','grant','account','initiator','target','id','nonce','notBefore','notAfter']}
        response.update(kind='device-evidence',requestHash=hashlib.sha256(base64.b64decode(json.loads(raw)['payload'])).hexdigest(),advertisement=advertisement(self.binary,self.b,'Bob@example.com'))
        signed=self.wrapped(self.b,response)
        self.assertEqual(self.send('PUT','exchanges/'+'5'*64+'/response','target-token',signed)[0],201)
        received=json.dumps(self.send('GET','exchanges/'+'5'*64)[1]['response'],separators=(',',':')).encode()
        checked=validate_response(received,raw,self.c,self.a['key'],self.b['key'],route_id='5'*64,time=self.now,target_mailbox='Bob@example.com')
        ad=encode_event(checked['value']['advertisement'])
        decision=verify_passive_discovery(ad,self.initiator,time=self.time,trust_policy='allow-unverified')
        self.assertEqual(decision['status'],'snapshot-authorized-unverified')
        stored=self.initiator.db.execute('SELECT record FROM claims WHERE principal=? AND digest=?',(self.b['principal'],decision['head'])).fetchone()[0]
        accepted=json.loads(base64.b64decode(json.loads(stored)['binding']))
        parsed=decode_passive_discovery(ad)['assertion'];package_bytes=parsed['key_package_octets']
        self.assertEqual(validate_package(package_bytes,principal=self.b['principal'],device=self.b['device'],accepted_signing_key=bytes.fromhex(accepted['signingKey']),earliest=self.time['earliest'],latest=self.time['latest'],executable=self.binary.with_name('validate-discovery-package')),{'status':'package-valid'})
        return package_bytes
    def invite(self,package_bytes):
        result=call(self.binary,op='invite',checkpoint=self.a['checkpoint'],key=self.a['key'],identity=self.a['identity'],package=package_bytes.hex())
        invitation=carrier({k:result[k] for k in ['welcome','tree','reference']})
        return result,invitation
    def accept(self,result,invitation,**kwargs):
        return self.admission.accept(self.b['reference'],invitation,peers=[self.a,self.b],expected_group=result['group'],expected_context=self.context,time=self.time,**kwargs)
    def test_https_package_admission_and_encrypted_mail_reply(self):
        discovered=self.discover();self.assertEqual(discovered,bytes.fromhex(self.b['package']))
        invited,invitation=self.invite(discovered);joined=self.accept(invited,invitation)
        self.assertEqual(joined['authenticator'],invited['authenticator'])
        application=(Path(__file__).parent/'mls-smoke/fixtures/message.json').read_bytes()
        sent=call(self.binary,op='send',checkpoint=invited['checkpoint'],key=self.a['key'],group=invited['group'],application=application.hex())
        wire=unpack(roundtrip(package(bytes.fromhex(sent['wire']))))
        result=self.admission.receiver.receive(wire,time=self.time,trust_policy='allow-unverified')
        self.assertEqual(result['status'],'projected-context-matched')
        retained=self.identity.db.execute('SELECT application FROM mls_receives').fetchone()[0]
        self.assertEqual(retained,application)
        reply=json.loads(application);reply['principal']=self.b['principal'];reply['event']='9'*32;reply['operation']['text']='Received over the admitted conversation.'
        # Use the committed post-receive checkpoint, not the pre-admission fixture.
        checkpoint=json.loads(self.identity.db.execute('SELECT snapshot FROM mls_checkpoint').fetchone()[0])
        response=call(self.binary,op='send',checkpoint=checkpoint,key=self.b['key'],group=joined['group'],application=encode_event(reply).hex())
        receiver=MlsReceive(self.initiator,self.binary.with_name('receive-staged'))
        receiver.install_fixture(invited['group'],sent['checkpoint']) # local creator state; no remote admission
        result=receiver.receive(unpack(roundtrip(package(bytes.fromhex(response['wire'])))),time=self.time,trust_policy='allow-unverified')
        self.assertEqual(result['status'],'projected-context-matched')
        self.assertEqual(self.initiator.db.execute('SELECT application FROM mls_receives').fetchone()[0],encode_event(reply))
    def test_invalid_welcome_does_not_consume_then_exact_retry(self):
        invited,invitation=self.invite(self.discover())
        bad=dict(invitation,welcome='00')
        with self.assertRaises(ValueError):self.accept(invited,bad)
        self.assertIsNone(self.identity.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])
        joined=self.accept(invited,invitation);self.assertEqual(self.accept(invited,invitation)['group'],joined['group'])
    def test_wrong_expected_roster_or_context_cannot_consume(self):
        invited,invitation=self.invite(self.discover())
        with self.assertRaises(ValueError):
            self.admission.accept(self.b['reference'],invitation,peers=[self.b],expected_group=invited['group'],expected_context=self.context,time=self.time)
        with self.assertRaises(ValueError):
            self.admission.accept(self.b['reference'],invitation,peers=[self.a,self.b],expected_group=invited['group'],expected_context=b'{}',time=self.time)
        changed=copy.deepcopy(self.a);changed['state']='8'*64
        with self.assertRaisesRegex(ValueError,'Current authority'):
            self.admission.accept(self.b['reference'],invitation,peers=[changed,self.b],expected_group=invited['group'],expected_context=self.context,time=self.time)
        self.assertIsNone(self.identity.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])
        self.accept(invited,invitation)

    def test_two_valid_invitations_only_one_consumes(self):
        import concurrent.futures
        import threading
        package_bytes=self.discover();one,i1=self.invite(package_bytes);two,i2=self.invite(package_bytes)
        barrier=threading.Barrier(2)
        def attempt(result,invitation):
            identity=IdentityStore(self.root/'target.sqlite')
            try:
                admission=Admission(identity,self.binary);barrier.wait(timeout=5)
                try:
                    admission.accept(self.b['reference'],invitation,peers=[self.a,self.b],expected_group=result['group'],expected_context=self.context,time=self.time)
                    return 'accepted'
                except ValueError as error:
                    if str(error)=='Package consumed':return 'consumed'
                    raise
            finally:identity.close()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(attempt,one,i1),pool.submit(attempt,two,i2)]
            self.assertEqual(sorted(f.result(timeout=20) for f in futures),['accepted','consumed'])
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0],1)

    def test_process_exit_before_and_after_commit(self):
        import multiprocessing
        invited,invitation=self.invite(self.discover())
        for stage in ['before-commit','after-commit']:
            process=multiprocessing.get_context('spawn').Process(target=crash_admission,args=(self.root/'target.sqlite',self.binary,self.b['reference'],invitation,[self.a,self.b],invited['group'],self.context,self.time,stage))
            process.start();process.join(20)
            if process.is_alive():process.terminate();process.join();self.fail('Admission process timeout')
            self.assertEqual(process.exitcode,91)
            count=self.identity.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0]
            self.assertEqual(count,0 if stage=='before-commit' else 1)
            consumed=self.identity.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0]
            self.assertEqual(consumed is not None,stage=='after-commit')
        self.identity.close();self.identity=IdentityStore(self.root/'target.sqlite');self.admission=Admission(self.identity,self.binary)
        self.assertEqual(self.accept(invited,invitation)['group'],invited['group'])


if __name__=='__main__':unittest.main()
