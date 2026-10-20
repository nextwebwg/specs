import hashlib
import json
import ssl
import threading
from pathlib import Path
import test_service_execution as fixtures
import test_service_tls as certificates
from service_execution import ClientJournal
from service_https import make_server, ServiceHTTPSClient
from event_encoding import encode_event

class HTTPSTests(fixtures.ExecutionTests):
    @classmethod
    def setUpClass(cls): certificates.ServiceTLSTest.setUpClass()
    @classmethod
    def tearDownClass(cls): certificates.ServiceTLSTest.tearDownClass()
    def start(self, **faults):
        cert,key=certificates.ServiceTLSTest('test_valid_san').leaf('service.example')
        context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.minimum_version=ssl.TLSVersion.TLSv1_3
        context.set_alpn_protocols(['http/1.1']);context.load_cert_chain(cert,key)
        server=make_server(self.store,context,**faults)
        origin='https://service.example:'+str(server.server_port);self.action['service']=origin
        with self.store.connect() as db:db.execute('UPDATE action SET data=?',(json.dumps(self.action),))
        for grant in self.tokens.values():grant['audience']=origin
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(server.server_close);self.addCleanup(thread.join,2);self.addCleanup(server.shutdown)
        journal=ClientJournal(Path(self.tmp.name)/'client.db');self.addCleanup(journal.close)
        identity=journal.retain(self.raw,origin)
        client=ServiceHTTPSClient(journal,host='service.example',port=server.server_port,ca_file=str(certificates.ServiceTLSTest.ca_file),submit_path='/submit',status_prefix='/status/',address=server.server_address,not_before=100,retry_until=200,credible_time=lambda:(self.now,self.now))
        return client,journal,identity
    def test_real_https_confirm_and_renew(self):
        client,journal,identity=self.start();self.assertEqual(client.request(identity,'test-token')['state'],'confirmed')
        self.tokens[hashlib.sha256(b'renewed').hexdigest()]=dict(next(iter(self.tokens.values())))
        self.assertEqual(client.request(identity,'renewed')['state'],'confirmed');self.assertEqual(self.count(),1)
    def test_lost_response_recovers_with_get(self):
        client,journal,identity=self.start(drop_after_commit=True)
        with self.assertRaises(Exception):client.request(identity,'test-token')
        self.assertEqual(self.count(),1);self.assertEqual(client.request(identity,'test-token',status=True)['state'],'confirmed')
    def test_authenticated_reordering_and_conflict(self):
        phase=[0]
        def transform(code,raw):
            value=json.loads(raw)
            if phase[0]==1:value.update(outcome='pending',reason='reconciling');code=202
            if phase[0]==2:value.update(outcome='rejected',reason='not-applied')
            return code,encode_event(value)
        client,journal,identity=self.start(response_transform=transform)
        self.assertEqual(client.request(identity,'test-token')['state'],'confirmed')
        phase[0]=1;self.assertEqual(client.request(identity,'test-token',status=True)['state'],'confirmed')
        phase[0]=2;self.assertEqual(client.request(identity,'test-token',status=True)['state'],'conflict');self.assertEqual(self.count(),1)
    def test_auth_failure_and_status_not_found(self):
        client,journal,identity=self.start();self.assertEqual(client.request(identity,'wrong')['http'],401)
        self.assertEqual(client.request(identity,'test-token',status=True)['http'],404);self.assertEqual(self.count(),0)
    def test_concurrent_local_calls(self):
        import concurrent.futures
        client,journal,identity=self.start()
        with concurrent.futures.ThreadPoolExecutor(3) as pool:results=list(pool.map(lambda _:client.request(identity,'test-token'),range(3)))
        self.assertEqual([r['state'] for r in results],['confirmed']*3);self.assertEqual(self.count(),1)
    def test_wrong_digest_and_redirect_not_accepted(self):
        phase=[0]
        def transform(code,raw):
            if phase[0]:return 307,b''
            value=json.loads(raw);value['requestDigest']='0'*64
            return code,encode_event(value)
        client,journal,identity=self.start(response_transform=transform)
        with self.assertRaises(ValueError):client.request(identity,'test-token')
        phase[0]=1;self.assertEqual(client.request(identity,'test-token',status=True)['http'],307)
        self.assertEqual(journal.db.execute('SELECT count(*) FROM receipts').fetchone()[0],0)
    def test_terminal_survives_http_errors(self):
        phase=[200]
        def transform(code,raw):return (code,raw) if phase[0]==200 else (phase[0],b'')
        client,journal,identity=self.start(response_transform=transform)
        self.assertEqual(client.request(identity,'test-token')['state'],'confirmed')
        for code in (404,403,409):
            phase[0]=code
            result=client.request(identity,'test-token',status=True)
            self.assertEqual(result['http'],code);self.assertEqual(result['state'],'confirmed')
    def test_credible_interval_preflight(self):
        client,journal,identity=self.start()
        for interval in [(99,100),(200,201),(151,150),(True,150),(150,False)]:
            client.credible_time=lambda interval=interval:interval
            self.assertEqual(client.request(identity,'test-token')['attempt'],'time-held')
        self.assertEqual(self.count(),0)
        client.credible_time=lambda:(100,200)
        self.assertEqual(client.request(identity,'test-token')['state'],'confirmed')
        client.credible_time=lambda:(201,201)
        self.assertEqual(client.request(identity,'test-token')['state'],'confirmed')
        self.assertEqual(client.request(identity,'test-token',status=True)['state'],'confirmed')
    def test_honest_pending_over_https(self):
        self.store.deferred=True;client,journal,identity=self.start()
        self.assertEqual(client.request(identity,'test-token')['state'],'pending')
        self.assertEqual(client.request(identity,'test-token',status=True)['state'],'pending');self.assertEqual(self.count(),0)
        self.store.reconcile_one('test-token')
        self.assertEqual(client.request(identity,'test-token',status=True)['state'],'confirmed')
    def test_rejected_and_conflict_survive_http_errors(self):
        phase=['reject']
        def transform(code,raw):
            if isinstance(phase[0],int):return phase[0],b''
            value=json.loads(raw)
            if phase[0]=='reject':value.update(outcome='rejected',reason='not-applied')
            return 200,encode_event(value)
        client,journal,identity=self.start(response_transform=transform)
        self.assertEqual(client.request(identity,'test-token')['state'],'rejected')
        for code in (404,403,409):
            phase[0]=code;self.assertEqual(client.request(identity,'test-token',status=True)['state'],'rejected')
        phase[0]='confirm';self.assertEqual(client.request(identity,'test-token',status=True)['state'],'conflict')
        for code in (404,403,409):
            phase[0]=code;self.assertEqual(client.request(identity,'test-token',status=True)['state'],'conflict')

    def test_configured_time_bounds_reject_boolean_and_overflow(self):
        for low, high in [(True,200),(100,False),(-1,200),(100,2**64),(201,200)]:
            with self.assertRaises(ValueError):
                ServiceHTTPSClient(None,host='service.example',port=443,ca_file='',submit_path='/submit',status_prefix='/status/',address=('127.0.0.1',443),not_before=low,retry_until=high,credible_time=lambda:(100,100))
