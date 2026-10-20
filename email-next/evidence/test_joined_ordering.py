import json,os,tempfile,unittest
from pathlib import Path
from email.message import EmailMessage
from email import policy
from email.parser import BytesParser
from provider_mls import make_device,call
from identity_store import IdentityStore
from smtp_loopback import roundtrip
import ordering_carrier
from ordering_certificates import sign,unsigned,digest,bundle,decode_event,encode
from ordering_scope import scope_digest
from ordering_store import VoteStore
from ordering_mls import JoinedOrdering,ProviderKey,candidate_id

class JoinedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.provider=Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR'])/'provider-mls';self.worker=self.provider.with_name('group-transitions')
        self.devices=[make_device(self.provider,a,d) for a,d in ((1,2),(3,4),(5,6))]
        self.time=dict(earliest=str(self.devices[0]['time']),latest=str(self.devices[0]['time']))
        witnesses=[dict(principal=d['principal'],device=d['device'],signingKey=d['key'],state=d['state'],binding=d['binding']) for d in self.devices]
        self.context=dict(version='7',purpose='conversation-context',conversation='2'*32,profile='mls-1-0001',administrators=[self.devices[0]['principal']],application=dict(envelopeVersion='3',payload='mime-rich-v0',operations=['message']),delivery={'kind':'ordinary-v0'},ordering=dict(kind='endpoint-quorum-v0',generation='0',faultBound='0',witnesses=witnesses))
        a=self.devices[0];created=call(self.worker,op='create',checkpoint=a['checkpoint'],key=a['key'],identity=a['identity'],context=json.dumps(self.context,separators=(',',':')).encode().hex())
        initial=call(self.worker,op='candidate',checkpoint=created['checkpoint'],key=a['key'],group=created['snapshot']['group'],packages=[d['package'] for d in self.devices[1:]])
        states=[{'snapshot':initial['after'],'checkpoint':initial['checkpoint']}]+[call(self.worker,op='join',checkpoint=d['checkpoint'],key=d['key'],welcome=initial['welcome']) for d in self.devices[1:]]
        self.identities=[];self.groups=[]
        for i,(d,state) in enumerate(zip(self.devices,states)):
            identity=IdentityStore(self.root/f'{i}.sqlite');self.identities.append(identity)
            for peer in self.devices:identity.observe(peer['record'],first_contact_policy='allow-unverified')
            group=JoinedOrdering(identity,self.worker,d);group.install_fixture(state);self.groups.append(group)
    def tearDown(self):
        for identity in self.identities:identity.close()
        self.tmp.cleanup()
    def certify(self,candidate):
        scope=scope_digest(candidate['plan']['scope']);objects=[]
        def add(kind,signer,**fields):
            d=self.devices[signer];sid=d['principal']+'|'+d['device'];o=sign(unsigned(kind,scope,0,sid,**fields),ProviderKey(self.provider,d));objects.append(o);return digest(o)
        p=add('proposal',0,candidate=candidate_id(candidate),newView='')
        stores=[];prepares=[]
        for i in (0,1):
            self.groups[i].inspect_candidate(candidate,time=self.time)
            d=self.devices[i];store=VoteStore(self.root/f'vote-{i}-{scope}',scope=scope,keys=self.groups[i].keys(),f=0,signer=d['principal']+'|'+d['device'],key=ProviderKey(self.provider,d),create=True);stores.append(store)
            obj=decode_event(self.groups[i].vote(store,'prepare',bundle(p,objects),candidate,time=self.time))['value'];objects.append(obj);prepares.append(digest(obj))
        pc=add('prepared',1,proposal=p,prepares=sorted(prepares));commits=[]
        for i,store in enumerate(stores):
            obj=decode_event(self.groups[i].vote(store,'commit',bundle(pc,objects),candidate,time=self.time))['value'];objects.append(obj);commits.append(digest(obj))
        decision=add('decision',1,prepared=pc,commits=sorted(commits))
        for store in stores:self.assertEqual(store.retained_candidates(bundle(decision,objects)),[encode(candidate)])
        return bundle(decision,objects)
    def test_actual_mls_certificate_smtp_and_exact_replay(self):
        candidate=self.groups[0].stage(ProviderKey(self.provider,self.devices[0]),time=self.time)
        proof=self.certify(candidate);decision=self.groups[0].install(candidate,proof,time=self.time)
        carrier=self.groups[0].release(decision,time=self.time)
        raw=roundtrip(ordering_carrier.package(carrier))
        self.assertEqual(ordering_carrier.receive(self.groups[1],raw,time=self.time),{'status':'accepted','decision':decision})
        self.assertEqual(ordering_carrier.receive(self.groups[1],raw,time=self.time),{'status':'accepted','decision':decision})
        self.assertEqual(ordering_carrier.receive(self.groups[1],b'x'*2097153,time=self.time),{'status':'unsupported-size','accepted':False})
        self.assertEqual(self.groups[0].live()[1]['snapshot']['predecessor'],self.groups[1].live()[1]['snapshot']['predecessor'])
        self.assertEqual(self.groups[1].db.execute('SELECT count(*) FROM qo_outbox').fetchone()[0],1)
    def test_handoff_certified_only_by_old_policy(self):
        new=json.loads(json.dumps(self.context));new['ordering']['generation']='1';new['ordering']['witnesses']=new['ordering']['witnesses'][1:]
        candidate=self.groups[0].stage(ProviderKey(self.provider,self.devices[0]),time=self.time,new_context=new)
        proof=self.certify(candidate)
        for g in self.groups[:2]:g.install(candidate,proof,time=self.time)
        self.assertEqual(self.groups[1].scope()['ordering'],new['ordering'])
        self.assertEqual(len(self.groups[1].keys()),2)
    def test_atomic_install_failure_and_tampered_commit(self):
        candidate=self.groups[0].stage(ProviderKey(self.provider,self.devices[0]),time=self.time);proof=self.certify(candidate);before=self.groups[1].live()
        def crash(point):raise RuntimeError(point)
        with self.assertRaises(RuntimeError):self.groups[1].install(candidate,proof,time=self.time,crash=crash)
        self.assertEqual(before,self.groups[1].live());self.assertEqual(self.groups[1].db.execute('SELECT count(*) FROM qo_decision').fetchone()[0],0)
        tampered=json.loads(json.dumps(candidate));tampered['plan']['commit']=tampered['plan']['commit'][:-2]+'00'
        with self.assertRaises(ValueError):self.groups[1].install(tampered,proof,time=self.time)
        self.groups[1].install(candidate,proof,time=self.time)

    def test_process_crash_before_and_after_atomic_install(self):
        import subprocess,sys
        candidate=self.groups[0].stage(ProviderKey(self.provider,self.devices[0]),time=self.time);proof=self.certify(candidate)
        program="""
import json,os,sys
from pathlib import Path
from identity_store import IdentityStore
from ordering_mls import JoinedOrdering
c=json.loads(Path(sys.argv[1]).read_text());identity=IdentityStore(c['db'])
g=JoinedOrdering(identity,c['worker'],c['device'])
def crash(point):
 if point==c['point']:os._exit(71)
g.install(c['candidate'],bytes.fromhex(c['proof']),time=c['time'],crash=crash)
identity.close()
"""
        for point in ('before-commit','after-commit'):
            cfg=self.root/'child.json';cfg.write_text(json.dumps(dict(db=str(self.root/'1.sqlite'),worker=str(self.worker),device=self.devices[1],candidate=candidate,proof=proof.hex(),time=self.time,point=point)))
            child=subprocess.run([sys.executable,'-c',program,str(cfg)],cwd=Path(__file__).resolve().parent,capture_output=True)
            self.assertEqual(child.returncode,71,child.stderr)
            self.assertEqual(self.groups[1].db.execute('SELECT count(*) FROM qo_decision').fetchone()[0],int(point=='after-commit'))
        decision=self.groups[1].install(candidate,proof,time=self.time)
        self.assertEqual(self.groups[1].db.execute('SELECT count(*) FROM qo_outbox WHERE identity=?',(decision,)).fetchone()[0],1)

    def test_joiner_matches_decided_welcome_and_admin_is_predecessor(self):
        newcomer=make_device(self.provider,9,10)
        for store in self.identities:store.observe(newcomer['record'],first_contact_policy='allow-unverified')
        for group in self.groups:group.configure_support(newcomer['identity'],newcomer['key'],self.context['application'])
        with self.assertRaisesRegex(ValueError,'administrator'):
            self.groups[0].stage(ProviderKey(self.provider,self.devices[1]),time=self.time)
        candidate=self.groups[0].stage(ProviderKey(self.provider,self.devices[0]),time=self.time,packages=[newcomer['package']])
        proof=self.certify(candidate)
        for group in self.groups[:2]:group.install(candidate,proof,time=self.time)
        joined=call(self.worker,op='join',checkpoint=newcomer['checkpoint'],key=newcomer['key'],welcome=candidate['plan']['welcomes'][0]['bytes'])
        self.assertEqual(joined['snapshot']['predecessor'],candidate['plan']['result']['predecessor'])
        self.assertEqual(candidate['plan']['welcomes'][0]['recipients'],[newcomer['identity']])

    def test_signed_identity_successor_holds_prepared_decision(self):
        import base64,hashlib
        from event_encoding import encode_event
        from provider_mls import sign as sign_provider
        candidate=self.groups[0].stage(ProviderKey(self.provider,self.devices[0]),time=self.time);proof=self.certify(candidate)
        a=self.devices[0];record=a['record'];binding=json.loads(base64.b64decode(record['binding']))
        binding.update(record='a'*32,roles=['receive','enroll','revoke'],authority={'kind':'state','digest':a['state']})
        bound=encode_event(binding);state=json.loads(base64.b64decode(record['state']))
        state.update(record='b'*32,revision='1',previous=[a['state']],bindings=[{'device':a['device'],'digest':hashlib.sha256(bound).hexdigest()}])
        raw=encode_event(state)
        successor={'version':'0','purpose':'identity-bundle','principal':a['principal'],
          'states':[{'payload':base64.b64encode(raw).decode(),'signature':sign_provider(self.provider,a,'email-next/identity-state/v0',raw)},{'payload':record['state'],'signature':record['stateProof']}],
          'bindings':[{'payload':base64.b64encode(bound).decode(),'authorization':sign_provider(self.provider,a,'email-next/device-binding/v0',bound),'possession':sign_provider(self.provider,a,'email-next/device-possession/v0',bound)},{'payload':record['binding'],'authorization':record['authorization'],'possession':record['possession']}]}
        result=self.identities[1].accept_successor(encode_event(successor),candidate_digest=hashlib.sha256(raw).hexdigest(),time=self.time)
        self.assertEqual(result['status'],'accepted-unverified')
        before=self.groups[1].live()
        with self.assertRaisesRegex(ValueError,'current account authority'):self.groups[1].install(candidate,proof,time=self.time)
        self.assertEqual(before,self.groups[1].live())

if __name__=='__main__':unittest.main()
