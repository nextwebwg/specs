import base64,hashlib,json,ssl,threading,unittest
from pathlib import Path
from event_encoding import encode_event
from provider_mls import sign
from initial_roster_lifecycle import InitialRosterRelease
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from mls_mime import unpack
from service_execution import ServiceStore,ClientJournal
from service_https import make_server,ServiceHTTPSClient
from client_service import ServiceFlow
import test_managed_presentation_lifecycle as managed
import test_service_tls as certificates

class JoinedService(unittest.TestCase):
    endpoint=managed.ManagedPresentation.endpoint;prepare=managed.ManagedPresentation.prepare;join=managed.ManagedPresentation.join;event=managed.ManagedPresentation.event;tearDown=managed.ManagedPresentation.tearDown
    @classmethod
    def setUpClass(cls):certificates.ServiceTLSTest.setUpClass()
    @classmethod
    def tearDownClass(cls):certificates.ServiceTLSTest.tearDownClass()
    def setUp(self):
        managed.ManagedPresentation.setUp(self)
        self.f.context['application']['operations']=sorted(set(self.f.context['application']['operations'])|{'service-question'})
        proofs=[]
        for device,p in zip(self.f.devices,self.f.proofs):
            value=json.loads(base64.b64decode(p['payload']));value['applications']=[dict(self.f.context['application'],ordering='designated-member-v0')];raw=encode_event(value)
            proofs.append(dict(p,payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,device,'email-next/passive-discovery/v5',raw)))
        self.f.proofs=proofs
        self.identity,self.sender,self.selected=self.endpoint("service-creator");self.release=InitialRosterRelease(self.sender)
    def setup_flow(self,**faults):
        self.join();event=self.event();ref={k:event[k] for k in ('principal','conversation','event')};option='b'*32
        cert,key=certificates.ServiceTLSTest('test_valid_san').leaf('service.example')
        tls=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);tls.minimum_version=ssl.TLSVersion.TLSv1_3;tls.load_cert_chain(cert,key)
        action=dict(service='https://service.example',action='c'*32,question=ref,options=[option],principals=[self.peer['principal']],notBefore=int(self.time['earliest']),retryUntil=int(self.time['latest'])+100,submitPath='/submit',statusPrefix='/status/')
        # Fixture databases live beside the independently created recipient DB.
        root=Path(self.peer_identity.path).parent if hasattr(self.peer_identity,'path') else Path(self.peer_sender.db.execute('PRAGMA database_list').fetchone()[2]).parent
        path=root/'service-effect.sqlite';ServiceStore.provision(path,action)
        tokens={hashlib.sha256(b'test-token').hexdigest():dict(issuer='fixture',audience=action['service'],principal=self.peer['principal'],start=0,end=2**63,scopes=['submit','status'])}
        store=ServiceStore(path,tokens,clock=lambda:int(self.time['earliest']));server=make_server(store,tls,**faults)
        origin='https://service.example:'+str(server.server_port);action['service']=origin;next(iter(tokens.values()))['audience']=origin
        with store.connect() as db:db.execute('UPDATE action SET data=?',(json.dumps(action),))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();self.addCleanup(server.server_close);self.addCleanup(thread.join,2);self.addCleanup(server.shutdown)
        descriptor=dict(version='0',purpose='service-answer-action',action=action['action'],question=ref,service=origin,submit=origin+'/submit',statusPrefix=origin+'/status/',notBefore=str(action['notBefore']),retryUntil=str(action['retryUntil']))
        event['operation']=dict(kind='service-question',text='Reserve a seat?',options=[dict(id=option,label='Reserve')],serviceAction=descriptor)
        wire=self.sender.prepare('servicequestion',encode_event(event),key=self.f.creator['key'],envelope_sender=self.source,recipients=[self.destination],time=self.time)
        smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit('servicequestion',port=smtp.port,time=self.time)['state'],'accepted')
        smtp.done();payload=unpack(smtp.wire);self.assertEqual(self.peer_sender.receiver.receive(payload,time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        carrier=hashlib.sha256(payload).hexdigest();journal=ClientJournal(root/'service-client.sqlite');self.addCleanup(journal.close)
        registration=dict(enabled=True,generation='1',service=origin,action=action['action'],submit=descriptor['submit'],statusPrefix=descriptor['statusPrefix'],principal=self.peer['principal'],credentialHandle='local-service')
        credential=['test-token']
        def transport(d):return ServiceHTTPSClient(journal,host='service.example',port=server.server_port,ca_file=str(certificates.ServiceTLSTest.ca_file),submit_path='/submit',status_prefix='/status/',address=server.server_address,not_before=int(d['notBefore']),retry_until=int(d['retryUntil']),credible_time=lambda:(int(self.time['earliest']),int(self.time['latest'])))
        flow=ServiceFlow(self.peer_sender,journal,key=self.peer['key'],registration=lambda:registration,credential=lambda handle:credential[0],transport=transport)
        self.flow,self.store,self.journal,self.registration,self.credential,self.tokens=flow,store,journal,registration,credential,tokens
        self.args=('click1',ref,carrier,option,flow.view(ref,carrier,time=self.time)['sourceToken'])
    def count(self):
        with self.store.connect() as db:return db.execute('SELECT count(*) FROM effects').fetchone()[0]
    def test_signed_smtp_https_effect_exact_retry_and_renewal(self):
        self.setup_flow();first=self.flow.activate(*self.args,time=self.time);self.assertEqual(first['state'],'confirmed')
        self.tokens[hashlib.sha256(b'renewed').hexdigest()]=dict(next(iter(self.tokens.values())));self.credential[0]='renewed'
        self.assertEqual(self.flow.activate(*self.args,time=self.time),first);self.assertEqual(self.count(),1)
        raw=self.journal.db.execute('SELECT raw FROM requests').fetchone()[0];self.assertNotIn(b'Reserve a seat',raw);self.assertEqual(set(json.loads(raw)),{'version','purpose','submission','action','question','principal','option','replaces'})
    def test_registration_snapshot_and_missing_credentials_hold(self):
        self.setup_flow();self.registration['generation']='2'
        with self.assertRaisesRegex(ValueError,'snapshot'):self.flow.activate(*self.args,time=self.time)
        self.registration['generation']='1';self.credential[0]=None
        with self.assertRaisesRegex(ValueError,'credential'):self.flow.activate(*self.args,time=self.time)
        self.assertEqual(self.count(),0)
    def test_lost_response_status_reconciliation_and_withdrawal(self):
        self.setup_flow(drop_after_commit=True)
        with self.assertRaises(Exception):self.flow.activate(*self.args,time=self.time)
        self.assertEqual(self.count(),1);self.registration['enabled']=False
        with self.assertRaisesRegex(ValueError,'registration'):self.flow.activate(*self.args,time=self.time,status=True)
        self.assertEqual(self.journal.state(json.loads(self.journal.db.execute('SELECT raw FROM requests').fetchone()[0])['submission']),'uncertain')
        self.registration.update(enabled=True,generation='2')
        args=list(self.args);args[4]=self.flow.view(args[1],args[2],time=self.time)['sourceToken']
        self.assertEqual(self.flow.activate(*args,time=self.time,status=True)['state'],'confirmed');self.assertEqual(self.count(),1)
    def test_current_device_send_revocation_holds_existing_control(self):
        self.setup_flow();d=self.peer;bundle=json.loads(encode_event(self.f.bundles[d['principal']]))
        state_entry=next(e for e in bundle['states'] if hashlib.sha256(base64.b64decode(e['payload'])).hexdigest()==self.f.heads[d['principal']]);state=json.loads(base64.b64decode(state_entry['payload']))
        old=next(b for b in bundle['bindings'] if hashlib.sha256(base64.b64decode(b['payload'])).hexdigest()==next(b['digest'] for b in state['bindings'] if b['device']==d['device']))
        binding=json.loads(base64.b64decode(old['payload']));binding.update(record='f'*32,roles=['receive','enroll','revoke'],authority=dict(kind='state',digest=self.f.heads[d['principal']]))
        raw=encode_event(binding);state.update(record='9'*32,revision=str(int(state['revision'])+1),previous=[self.f.heads[d['principal']]],bindings=[dict(b,digest=hashlib.sha256(raw).hexdigest()) if b['device']==d['device'] else b for b in state['bindings']]);payload=encode_event(state)
        bundle['states'].append(dict(payload=base64.b64encode(payload).decode(),signature=sign(self.f.binary,d,'email-next/identity-state/v0',payload)))
        bundle['bindings'].append(dict(payload=base64.b64encode(raw).decode(),authorization=sign(self.f.binary,d,'email-next/device-binding/v0',raw),possession=sign(self.f.binary,d,'email-next/device-possession/v0',raw)))
        self.assertEqual(self.peer_identity.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(payload).hexdigest(),time=self.time)['status'],'accepted-unverified')
        with self.assertRaisesRegex(ValueError,'authority'):self.flow.activate(*self.args,time=self.time)
        self.assertEqual(self.count(),0)
    def test_wrong_registration_and_unaccepted_carrier(self):
        self.setup_flow()
        for key,value in [('service','https://wrong.example'),('action','f'*32),('principal',self.f.creator['principal'])]:
            old=self.registration[key];self.registration[key]=value
            with self.assertRaisesRegex(ValueError,'registration'):self.flow.activate(*self.args,time=self.time)
            self.registration[key]=old
        args=list(self.args);args[2]='0'*64
        with self.assertRaisesRegex(ValueError,'carrier'):self.flow.activate(*args,time=self.time)
        args=list(self.args);args[3]='f'*32
        with self.assertRaisesRegex(ValueError,'option'):self.flow.activate(*args,time=self.time)
        self.assertEqual(self.count(),0)
    def test_explicit_tuple_not_old_profile_or_partial_intersection(self):
        from application_tuples import validate_tuples,intersect
        selected=dict(self.f.context['application'],ordering='designated-member-v0')
        self.assertEqual(validate_tuples([selected],version='5'),[selected])
        older=dict(selected,envelopeVersion='2')
        with self.assertRaises(ValueError):validate_tuples([older],version='4')
        peer=dict(selected,operations=[x for x in selected['operations'] if x!='service-question'])
        self.assertNotIn('service-question',intersect([[selected],[peer]],version='5')[0]['operations'])
