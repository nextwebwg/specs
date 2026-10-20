from vault_fixture import fresh_key
import base64,hashlib,json,secrets,unittest
from pathlib import Path
from urllib.parse import parse_qsl,urlsplit,urlencode
from unittest.mock import patch
import test_joined_service as joined
from service_authorization import AuthorizationStore,digest
from vault_fixture import NativeAuthorization
from service_authorization_client import AuthorizationHTTPS,bind_loopback
from service_authorization_http import LinkedServiceStore,make_authorization_server
from event_encoding import encode_event
from provider_mls import sign

class ServiceAuthorization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):joined.JoinedService.setUpClass()
    @classmethod
    def tearDownClass(cls):joined.JoinedService.tearDownClass()
    def setUp(self):
        self.f=joined.JoinedService();self.f.setUp();self.addCleanup(self.f.tearDown);self.addCleanup(self.f.doCleanups)
        self.drop=[self._testMethodName=='test_lost_link_response_restart_exact_retry']
        def make(store,tls,**kwargs):return make_authorization_server(store,tls,drop_link_response=lambda:self.drop[0],simulated_account=getattr(self,'simulated_account',None))
        with patch.object(joined,'ServiceStore',LinkedServiceStore),patch.object(joined,'make_server',make):self.f.setup_flow()
        self.root=Path(self.f.temp.name);self.now=int(self.f.time['earliest']);origin=self.f.registration['service']
        self.reg=encode_event(dict(version='0',purpose='service-authorization-registration',registration='1'*32,generation='1',issuer=origin,service=origin,clientId='native-mail',authorization=origin+'/authorize',token=origin+'/token',linkChallenge=origin+'/link/challenge',linkComplete=origin+'/link/complete',redirectPath='/email-next/oauth/callback',scopes=['email-next.link','email-next.status','email-next.submit']))
        self.auth=AuthorizationStore(self.root/'oauth.sqlite',self.reg,clock=lambda:self.now);self.addCleanup(self.auth.close)
        self.f.store.authorization_config=(self.root/'oauth.sqlite',self.reg,lambda:self.now)
        self.key=fresh_key(self.root/'vault.sqlite');self.client=NativeAuthorization(self.root/'vault.sqlite',self.reg,key=self.key,clock=lambda:self.now);self.addCleanup(self.client.close)
        port=urlsplit(origin).port
        self.https=AuthorizationHTTPS(self.reg,ca_file=str(joined.certificates.ServiceTLSTest.ca_file),address=('127.0.0.1',port))
    def login(self,account='simulated-account-A'):
        listener,redirect=bind_loopback();self.addCleanup(listener.close)
        url,state=self.client.start(redirect);params=dict(parse_qsl(urlsplit(url).query));response=self.auth.approve_account(params,authenticated_account=account)
        # Simulate the trusted browser following the authorization redirect over
        # the actual selected IPv4/IPv6 loopback listener.
        import concurrent.futures,http.client
        from service_authorization_client import receive_loopback_callback
        with concurrent.futures.ThreadPoolExecutor(1) as pool:
            pending=pool.submit(receive_loopback_callback,listener,redirect)
            p=urlsplit(redirect);conn=http.client.HTTPConnection(p.hostname,p.port,timeout=5)
            try:conn.request('GET',p.path+'?'+urlencode(response));reply=conn.getresponse();self.assertEqual(reply.status,200);reply.read()
            finally:conn.close()
            callback=pending.result()
        token=self.client.callback(state,callback,self.https.exchange)
        return token
    def link(self,token):
        from service_authorization_client import link_account
        return link_account(self.client,self.https,device=self.f.peer,identity_bundle=self.f.f.bundles[self.f.peer['principal']],identity_store=self.f.peer_identity,binary=self.f.f.binary,token=token,time=self.f.time)
    def test_simulated_account_signin_device_link_smtp_question_click(self):
        # No token-to-principal mapping exists before account authentication/link.
        self.assertEqual(self.auth.db.execute('SELECT count(*) FROM sa_links').fetchone()[0],0)
        token=self.login();self.assertEqual(self.auth.authorize_service(token,self.f.store.action(),'submit'),(None,403))
        proof,receipt=self.link(token);self.assertEqual(receipt['principal'],self.f.peer['principal'])
        self.f.credential[0]=token;self.assertEqual(self.f.flow.activate(*self.f.args,time=self.f.time)['state'],'confirmed');self.assertEqual(self.f.count(),1)
        self.assertEqual(self.f.flow.activate(*self.f.args,time=self.f.time,status=True)['state'],'confirmed')
        renewed=self.client.refresh(self.https.exchange);self.f.credential[0]=renewed
        self.assertEqual(self.f.flow.activate(*self.f.args,time=self.f.time)['state'],'confirmed');self.assertEqual(self.f.count(),1)
        self.assertEqual(self.https.post(json.loads(self.reg)['linkComplete'],proof,token=renewed),receipt)
        self.assertNotIn(token.encode(),(self.root/'vault.sqlite').read_bytes())
    def test_callback_issuer_state_expiry_and_registration_no_exchange(self):
        listener,redirect=bind_loopback();self.addCleanup(listener.close);url,state=self.client.start(redirect);params=dict(parse_qsl(urlsplit(url).query));response=self.auth.approve_account(params,authenticated_account='account')
        def forbidden(*args):raise AssertionError('No token exchange')
        for values in [dict(response,iss='https://wrong.example'),dict(response,state='wrong'),dict(response,error='denied')]:
            with self.assertRaises(ValueError):self.client.callback(state,redirect+'?'+urlencode(values),forbidden)
        with self.assertRaises(ValueError):self.client.callback(state,redirect+'?'+urlencode(response)+'&code=duplicate',forbidden)
        self.now+=301
        with self.assertRaises(ValueError):self.client.callback(state,redirect+'?'+urlencode(response),forbidden)
    def test_proof_mismatch_other_account_and_exact_retry(self):
        token=self.login();proof,receipt=self.link(token);other=self.login('account-B')
        with self.assertRaises(ValueError):self.https.post(json.loads(self.reg)['linkComplete'],proof,token=other)
        changed=dict(proof,signature='0'*128)
        with self.assertRaises(ValueError):self.https.post(json.loads(self.reg)['linkComplete'],changed,token=token)
        malformed=dict(proof,identity=None)
        with self.assertRaises(ValueError):self.https.post(json.loads(self.reg)['linkComplete'],malformed,token=token)
        self.now+=121;self.assertEqual(self.https.post(json.loads(self.reg)['linkComplete'],proof,token=token),receipt)
        self.assertEqual(self.auth.db.execute('SELECT count(*) FROM sa_links').fetchone()[0],1)
    def test_refresh_replay_and_unlink_disable_service(self):
        token=self.login();self.link(token);refresh=self.client.get('tokens')['refresh_token'];renewed=self.client.refresh(self.https.exchange)
        with self.assertRaises(ValueError):self.https.exchange(json.loads(self.reg)['token'],dict(grant_type='refresh_token',client_id='native-mail',refresh_token=refresh))
        self.assertEqual(self.auth.authorize_service(renewed,self.f.store.action(),'submit'),(None,401))
        other=self.login();self.link(other);self.auth.unlink(other);self.assertEqual(self.auth.authorize_service(other,self.f.store.action(),'submit'),(None,401))

    def test_pkce_redirect_and_code_replay(self):
        listener,redirect=bind_loopback();self.addCleanup(listener.close);url,state=self.client.start(redirect);params=dict(parse_qsl(urlsplit(url).query));response=self.auth.approve_account(params,authenticated_account='account')
        saved=self.client.get(state);request=dict(grant_type='authorization_code',client_id='native-mail',code=response['code'],redirect_uri=redirect,code_verifier=saved['verifier'])
        for altered in [dict(request,code_verifier='a'*43),dict(request,redirect_uri=redirect+'?code=wrong')]:
            with self.assertRaises(ValueError):self.https.exchange(json.loads(self.reg)['token'],altered)
        self.assertEqual(self.auth.db.execute('SELECT count(*) FROM sa_families').fetchone()[0],0)
        self.https.exchange(json.loads(self.reg)['token'],request)
        with self.assertRaises(ValueError):self.https.exchange(json.loads(self.reg)['token'],request)
    def test_lost_link_response_restart_exact_retry(self):
        from service_authorization_client import retry_link
        token=self.login()
        with self.assertRaises(Exception):self.link(token)
        self.assertEqual(self.auth.db.execute('SELECT count(*) FROM sa_links').fetchone()[0],1)
        original=self.client.get('link-pending')['proof'];self.drop[0]=False
        self.client.close();self.client=NativeAuthorization(self.root/'vault.sqlite',self.reg,key=self.key,clock=lambda:self.now);self.addCleanup(self.client.close)
        proof,receipt=retry_link(self.client,self.https,token);self.assertEqual(proof,original);self.assertEqual(receipt['outcome'],'linked')
        self.assertEqual(self.auth.db.execute('SELECT count(*) FROM sa_links').fetchone()[0],1)
    def test_changed_registration_holds_before_token_exchange(self):
        listener,redirect=bind_loopback();self.addCleanup(listener.close);url,state=self.client.start(redirect);params=dict(parse_qsl(urlsplit(url).query));response=self.auth.approve_account(params,authenticated_account='account')
        revised=json.loads(self.reg);revised['generation']='2'
        changed=NativeAuthorization(self.root/'vault.sqlite',encode_event(revised),key=self.key,clock=lambda:self.now);self.addCleanup(changed.close)
        def forbidden(*args):raise AssertionError('No exchange after registration change')
        with self.assertRaisesRegex(ValueError,'binding'):changed.callback(state,redirect+'?'+urlencode(response),forbidden)
    def test_signed_known_device_revocation_blocks_resource(self):
        token=self.login();self.link(token);d=self.f.peer;bundle=json.loads(encode_event(self.f.f.bundles[d['principal']]));head=self.auth.identity.current_state(d['principal'])['head']
        state=json.loads(base64.b64decode(next(s['payload'] for s in bundle['states'] if digest(base64.b64decode(s['payload']))==head)))
        old=next(b for b in bundle['bindings'] if digest(base64.b64decode(b['payload']))==next(b['digest'] for b in state['bindings'] if b['device']==d['device']))
        binding=json.loads(base64.b64decode(old['payload']));binding.update(record='f'*32,roles=['receive','enroll','revoke'],authority=dict(kind='state',digest=head));raw=encode_event(binding)
        state.update(record='9'*32,revision=str(int(state['revision'])+1),previous=[head],bindings=[dict(b,digest=digest(raw)) if b['device']==d['device'] else b for b in state['bindings']]);payload=encode_event(state)
        bundle['states'].append(dict(payload=base64.b64encode(payload).decode(),signature=sign(self.f.f.binary,d,'email-next/identity-state/v0',payload)));bundle['bindings'].append(dict(payload=base64.b64encode(raw).decode(),authorization=sign(self.f.f.binary,d,'email-next/device-binding/v0',raw),possession=sign(self.f.f.binary,d,'email-next/device-possession/v0',raw)))
        self.assertEqual(self.auth.identity.accept_successor(encode_event(bundle),candidate_digest=digest(payload),time=self.f.time)['status'],'accepted-unverified')
        self.assertEqual(self.auth.authorize_service(token,self.f.store.action(),'submit'),(None,403))
        self.f.credential[0]=token;self.assertEqual(self.f.flow.activate(*self.f.args,time=self.f.time)['http'],403);self.assertEqual(self.f.count(),0)

class BearerParsing(unittest.TestCase):
    def test_scheme_case_and_error_boundaries(self):
        from email.message import Message
        from service_authorization_http import bearer
        from service_authorization import GrantError
        for value,result in [('bearer ABC','ABC'),('bEaReR AbC==','AbC==')]:
            h=Message();h['Authorization']=value;self.assertEqual(bearer(h),result)
        for value,status,error in [(None,401,None),('Basic abc',401,None),('Bearer',400,'invalid_request'),('Bearer x y',400,'invalid_request')]:
            h=Message()
            if value is not None:h['Authorization']=value
            with self.assertRaises(GrantError) as caught:bearer(h)
            self.assertEqual((caught.exception.status,caught.exception.error),(status,error))
