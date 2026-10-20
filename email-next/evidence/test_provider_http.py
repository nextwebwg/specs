import copy
import json
import socket
import tempfile
import unittest
from pathlib import Path
import test_service_tls as tls_fixtures
import test_provider_control as signed_fixtures
from provider_control import OPERATIONS
from provider_http import ProviderHTTP
from service_tls import wrap_service_socket


class ProviderHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tls_fixtures.ServiceTLSTest.setUpClass();signed_fixtures.ProviderControlTests.setUpClass()
        cls.tls=tls_fixtures.ServiceTLSTest()
        cls.cert,cls.key=cls.tls.leaf('example.com')
    @classmethod
    def tearDownClass(cls):tls_fixtures.ServiceTLSTest.tearDownClass()
    def setUp(self):
        self.f=signed_fixtures.ProviderControlTests();self.f.setUp()
        self.f.c['notAfter']=1000
        self.target=copy.deepcopy(self.f.c);self.target.update(role='target',operations=OPERATIONS['target'][:])
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'provider.sqlite'
        self.now=(20,21)
        common={'notBefore':10,'notAfter':1000,'initiatorKey':self.f.f['initiatorKey'],
                'targetKey':self.f.f['targetKey'],'targetMailbox':'Alice@example.com'}
        self.creds={'init-token':dict(common,configuration=self.f.c),'target-token':dict(common,configuration=self.target)}
        self.server=ProviderHTTP(self.path,self.creds,self.cert,self.key,lambda:self.now).start()
    def tearDown(self):self.server.close();self.temp.cleanup()
    def send(self,method,path,token='init-token',body=b'',extra=None,raw=None):
        # Explicit test-only network mapping; trust reference remains configured example.com.
        with socket.create_connection(('127.0.0.1',self.server.port),timeout=3) as sock:
            with wrap_service_socket(sock,reference_host='example.com',trusted_ca_file=str(self.tls.ca_file)) as conn:
                conn.settimeout(3)
                headers={'Host':'example.com','Authorization':'Bearer '+token,'Content-Length':str(len(body)),
                         'Content-Type':'application/json','Cache-Control':'no-store'}
                headers.update(extra or {})
                request=raw or (f'{method} /control/{path} HTTP/1.1\r\n'+''.join(f'{k}: {v}\r\n' for k,v in headers.items())+'\r\n').encode()+body
                conn.sendall(request);data=b''
                while True:
                    chunk=conn.recv(65536)
                    if not chunk:break
                    data+=chunk
        head,payload=data.split(b'\r\n\r\n',1);lines=head.decode().split('\r\n')
        status=int(lines[0].split()[1]);h=dict(line.split(': ',1) for line in lines[1:])
        self.assertEqual(h['Cache-Control'],'no-store');self.assertNotIn('Location',h)
        self.assertEqual(int(h['Content-Length']),len(payload))
        return status,json.loads(payload),h
    def request_path(self):return 'exchanges/'+'5'*64+'/request'
    def response_path(self):return 'exchanges/'+'5'*64+'/response'
    def test_two_credentials_actual_https_exchange_and_expired_retry(self):
        self.assertEqual(self.send('GET','configuration')[1]['role'],'initiator')
        self.assertEqual(self.send('PUT',self.request_path(),body=self.f.request)[0],201)
        pending=self.send('GET','pending','target-token')
        self.assertEqual(pending[1]['ids'],['5'*64])
        response=self.f.sign(self.f.response,'target')
        self.assertEqual(self.send('PUT',self.response_path(),'target-token',response)[0],201)
        self.now=(110,111)
        self.assertEqual(self.send('PUT',self.request_path(),body=self.f.request)[0],200)
        self.assertEqual(self.send('PUT',self.response_path(),'target-token',response)[0],200)
        result=self.send('GET','exchanges/'+'5'*64)[1]
        self.assertEqual(result['status'],'responded');self.assertEqual(result['response'],json.loads(response))
    def test_wrong_token_role_context_and_media(self):
        self.assertEqual(self.send('GET','configuration','wrong')[0],401)
        self.assertEqual(self.send('GET','pending')[0],403)
        self.assertEqual(self.send('PUT',self.request_path(),'target-token',self.f.request)[0],403)
        self.assertEqual(self.send('PUT',self.request_path(),body=self.f.request,extra={'Content-Type':'text/plain'})[0],415)
        bad=self.f.sign(dict(self.f.r,grant='8'*64))
        self.assertEqual(self.send('PUT',self.request_path(),body=bad)[0],400)
        self.assertEqual(self.send('GET','exchanges/'+'5'*64)[0],404)
        self.assertEqual(self.send('POST','configuration')[0],405)
        self.assertEqual(self.send('GET','configuration?redirect=1')[0],404)
    def test_framing_and_body_bounds(self):
        self.assertEqual(self.send('GET','configuration',body=b'x')[0],400)
        self.assertEqual(self.send('PUT',self.request_path(),body=b'{}',extra={'Content-Encoding':'gzip'})[0],415)
        self.assertEqual(self.send('GET','configuration',extra={'Host':'evil.example'})[0],400)
        raw=b'GET /control/configuration HTTP/1.1\r\nHost: example.com\r\nHost: example.com\r\n\r\n'
        self.assertEqual(self.send('GET','',raw=raw)[0],400)
        raw=b'PUT /control/configuration HTTP/1.1\r\nHost: example.com\r\nContent-Length: 999999\r\n\r\n'
        self.assertEqual(self.send('PUT','',raw=raw)[0],413)
    def test_http_budgets_are_durable_and_distinct(self):
        self.f.c['limits']['requestsPerMinute']=2
        self.target['limits']['requestsPerMinute']=2
        self.assertEqual(self.send('GET','configuration')[0],200)
        self.assertEqual(self.send('GET','configuration')[0],200)
        self.assertEqual(self.send('GET','configuration')[0],429)
        self.assertEqual(self.send('GET','configuration','target-token')[0],200)
        self.server.close()
        self.server=ProviderHTTP(self.path,self.creds,self.cert,self.key,lambda:self.now).start()
        self.assertEqual(self.send('GET','configuration')[0],429)
        self.now=(80,81);self.assertEqual(self.send('GET','configuration')[0],200)
    def test_https_pagination_cursor_retries(self):
        self.f.c['limits']['pendingPageSize']=1;self.target['limits']['pendingPageSize']=1
        for number in [1,2,3]:
            identifier=format(number,'064x')
            body=self.f.sign(dict(self.f.r,id=identifier))
            self.assertEqual(self.send('PUT','exchanges/'+identifier+'/request',body=body)[0],201)
        page=self.send('GET','pending','target-token')[1]
        self.assertEqual(page['ids'],[format(1,'064x')])
        path='pending?after='+page['next']
        second=self.send('GET',path,'target-token')[1]
        self.assertEqual(second,self.send('GET',path,'target-token')[1])
        self.assertEqual(second['ids'],[format(2,'064x')])
        final=self.send('GET','pending?after='+second['next'],'target-token')[1]
        self.assertEqual(final['ids'],[format(3,'064x')]);self.assertIsNone(final['next'])

    def test_expired_unanswered_response_is_conflict(self):
        self.assertEqual(self.send('PUT',self.request_path(),body=self.f.request)[0],201)
        self.now=(95,96)
        self.assertEqual(self.send('PUT',self.response_path(),'target-token',self.f.sign(self.f.response,'target'))[0],409)
        self.assertEqual(self.send('GET','exchanges/'+'5'*64)[1]['status'],'expired')

    def test_incomplete_request_times_out_without_exchange(self):
        self.server.timeout=.15
        with socket.create_connection(('127.0.0.1',self.server.port),timeout=3) as sock:
            with wrap_service_socket(sock,reference_host='example.com',trusted_ca_file=str(self.tls.ca_file)) as conn:
                conn.settimeout(2)
                conn.sendall(b'GET /control/configuration HTTP/1.1\r\nHost: example.com\r\n')
                self.assertEqual(conn.recv(1),b'')
        self.assertEqual(self.send('GET','exchanges/'+'5'*64)[0],404)

    def test_bearer_challenges_distinguish_missing_malformed_and_invalid(self):
        for auth in ['', 'Basic dXNlcjpwYXNz']:
            status,body,headers=self.send('GET','configuration',extra={'Authorization':auth})
            self.assertEqual(status,401);self.assertEqual(headers['WWW-Authenticate'],'Bearer')
        for auth in ['Bearer', 'Bearer bad!token', 'Bearer\tinit-token', 'Bearer init-token extra']:
            status,body,headers=self.send('GET','configuration',extra={'Authorization':auth})
            self.assertEqual(status,400);self.assertEqual(headers['WWW-Authenticate'],'Bearer error="invalid_request"')
        status,body,headers=self.send('GET','configuration','unknown-token')
        self.assertEqual(status,401);self.assertEqual(headers['WWW-Authenticate'],'Bearer error="invalid_token"')
        self.creds['init-token']['notAfter']=19
        status,body,headers=self.send('GET','configuration')
        self.assertEqual(status,401);self.assertEqual(headers['WWW-Authenticate'],'Bearer error="invalid_token"')
        for scheme in ['bearer','bEaReR']:
            self.assertEqual(self.send('GET','configuration','target-token',extra={'Authorization':scheme+' target-token'})[0],200)
        self.assertEqual(self.send('GET','configuration','TARGET-TOKEN')[0],401)

    def test_failed_auth_source_budget(self):
        self.server.fail_limit=2
        self.assertEqual(self.send('GET','configuration','bad')[0],401)
        self.assertEqual(self.send('GET','configuration','bad')[0],401)
        self.assertEqual(self.send('GET','configuration','bad')[0],429)

if __name__=='__main__':unittest.main()
