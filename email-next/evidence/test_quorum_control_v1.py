import base64,json,unittest
from event_encoding import encode_event
from provider_mls import make_device,advertisement,sign,call
from quorum_join_support import confirm
from admitted_quorum import AdmittedQuorum
from ordering_mls import ProviderKey
from ordering_certificates import encode
import ordering_carrier
import test_admitted_quorum as initial

class CarrierOneTests(unittest.TestCase):
    setUp=initial.AdmittedQuorumTests.setUp;tearDown=initial.AdmittedQuorumTests.tearDown
    endpoint=initial.AdmittedQuorumTests.endpoint;prepare=initial.AdmittedQuorumTests.prepare;join=initial.AdmittedQuorumTests.join;certify=initial.AdmittedQuorumTests.certify
    def assertion(self,d):
        w=advertisement(self.provider,d,'new'+d['principal'][5:7]+'@example.invalid');v=json.loads(base64.b64decode(w['payload']));v.update(version='6',applications=[dict(self.f.context['application'],ordering='endpoint-quorum-v0')]);raw=encode_event(v);w.update(payload=base64.b64encode(raw).decode(),signature=sign(self.provider,d,'email-next/passive-discovery/v6',raw));return w
    def test_multi_add_exact_package_atomicity_and_replay(self):
        self.join();devices=[make_device(self.provider,7,8),make_device(self.provider,9,10)];wrappers=[self.assertion(d) for d in devices]
        for store in self.stores:
            for d in devices:store.observe(d['record'],first_contact_policy='allow-unverified')
        for group in self.groups:
            for w in wrappers:confirm(group,encode_event(w),time=self.time)
        candidate=self.author_group.stage(ProviderKey(self.provider,self.f.creator),time=self.time,packages=[d['package'] for d in devices]);proof=self.certify(candidate)
        for group in self.groups:decision=group.install(candidate,proof,time=self.time)
        carrier=self.author_group.release(decision,time=self.time);value=json.loads(carrier);self.assertEqual(value['version'],'1');self.assertEqual(len(value['applicationAssertions']),2)
        target=AdmittedQuorum(self.senders[self.removed['device']].receiver,self.worker,self.removed);before=target.live()
        fresh=dict(devices[0],**call(self.provider,op='fresh-package',checkpoint=devices[0]['checkpoint'],key=devices[0]['key'],identity=devices[0]['identity']));self.assertNotEqual(fresh['reference'],devices[0]['reference'])
        for mode in ('missing','duplicate','extra','older','different-package'):
            changed=json.loads(carrier)
            if mode=='missing':changed['applicationAssertions'].pop()
            elif mode=='duplicate':changed['applicationAssertions'].append(changed['applicationAssertions'][0])
            elif mode=='extra':changed['applicationAssertions'].insert(0,self.f.proofs[0])
            elif mode=='older':
                w=changed['applicationAssertions'][0];v=json.loads(base64.b64decode(w['payload']));v['version']='5';w['payload']=base64.b64encode(encode_event(v)).decode()
            else:changed['applicationAssertions'][0]=self.assertion(fresh)
            with self.subTest(mode=mode),self.assertRaises(ValueError):ordering_carrier.receive(target,ordering_carrier.package(encode(changed)),time=self.time)
            self.assertEqual(target.live(),before);self.assertEqual(target.db.execute('SELECT count(*) FROM qo_join_support').fetchone()[0],0)
        with self.assertRaises(RuntimeError):target.install(candidate,proof,time=self.time,application_assertions=value['applicationAssertions'],crash=lambda _:(_ for _ in ()).throw(RuntimeError('crash')))
        self.assertEqual(target.live(),before);self.assertEqual(target.db.execute('SELECT count(*) FROM qo_join_support').fetchone()[0],0)
        raw=ordering_carrier.package(carrier);self.assertEqual(ordering_carrier.receive(target,raw,time=self.time)['decision'],decision);self.assertEqual(ordering_carrier.receive(target,raw,time=self.time)['decision'],decision)
        malformed=json.loads(carrier);malformed['extra']='ignored?'
        with self.assertRaises(ValueError):ordering_carrier.receive(target,ordering_carrier.package(encode(malformed)),time=self.time)
        self.assertEqual(target.db.execute('SELECT count(*) FROM qo_join_support').fetchone()[0],2)
        # No-Add transition must carry exactly an empty assertion array.
        candidate=self.author_group.stage(ProviderKey(self.provider,self.f.creator),time=self.time);proof=self.certify(candidate);decision=self.author_group.install(candidate,proof,time=self.time);carrier=self.author_group.release(decision,time=self.time);value=json.loads(carrier);self.assertEqual(value['applicationAssertions'],[])
        changed=dict(value,applicationAssertions=wrappers)
        with self.assertRaises(ValueError):ordering_carrier.receive(target,ordering_carrier.package(encode(changed)),time=self.time)
        self.assertEqual(ordering_carrier.receive(target,ordering_carrier.package(carrier),time=self.time)['decision'],decision)

if __name__=='__main__':unittest.main()
