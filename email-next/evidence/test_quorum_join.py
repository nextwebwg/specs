import base64,json,unittest
from provider_mls import make_device,advertisement,sign
from event_encoding import encode_event
from passive_discovery import decode_passive_discovery
from admitted_quorum import AdmittedQuorum
from quorum_join import import_anchor
from quorum_join_support import confirm
from quorum_invitation import QuorumInvitation
from established_invitation import EstablishedAdmission,parse
from established_invitation_mime import select
from invitation_mime import select as initial_select
from initial_roster import parse as parse_initial
from ordering_mls import ProviderKey
from smtp_loopback import roundtrip
from mls_mime import unpack
import test_admitted_quorum as initial

class QuorumJoinTests(unittest.TestCase):
    setUp=initial.AdmittedQuorumTests.setUp;tearDown=initial.AdmittedQuorumTests.tearDown
    endpoint=initial.AdmittedQuorumTests.endpoint;prepare=initial.AdmittedQuorumTests.prepare;join=initial.AdmittedQuorumTests.join;certify=initial.AdmittedQuorumTests.certify;event=initial.AdmittedQuorumTests.event
    def prepare_join(self,remove=False):
        self.join();self.new=make_device(self.provider,7,8)
        self.new_identity,self.new_sender,_=self.endpoint('newquorumtarget')
        for identity in self.stores:identity.observe(self.new['record'],first_contact_policy='allow-unverified')
        wrapper=advertisement(self.provider,self.new,'newjoiner@example.invalid');v=json.loads(base64.b64decode(wrapper['payload']));v.update(version=getattr(self,'exchange_assertion_version','6'),applications=[dict(self.f.context['application'],ordering='endpoint-quorum-v0')]);v.update(orderingExchanges=[dict(format='quorum-exchange-experiment',version='1')]) if v['version']=='7' else None;raw=encode_event(v);wrapper.update(payload=base64.b64encode(raw).decode(),signature=sign(self.provider,self.new,'email-next/passive-discovery/v'+v['version'],raw));self.new_proof=encode_event(wrapper)
        for group in self.groups:confirm(group,self.new_proof,time=self.time)
        removals=[int(m['index']) for m in self.author_group.live()[1]['snapshot']['members'] if m['identity']==self.removed['identity']] if remove else []
        candidate=self.author_group.stage(ProviderKey(self.provider,self.f.creator),time=self.time,packages=[self.new['package']],removals=removals);proof=self.certify(candidate)
        for group in self.groups:decision=group.install(candidate,proof,time=self.time)
        self.exporter=QuorumInvitation(self.author_group,self.sender)
        self.wire=self.exporter.prepare('f'*32,decision,target={k:self.new[k] for k in ('principal','device')},not_before=self.time['earliest'],not_after=str(int(self.time['latest'])+20),time=self.time)
        self.raw=select(roundtrip(self.wire));self.parsed=parse(self.raw);self.admission=EstablishedAdmission(self.new_identity,self.provider);self.admission.publish_local(self.new)
        self.genesis=initial_select(self.identity.db.execute('SELECT wire FROM initial_roster_prepared LIMIT 1').fetchone()[0]);p=parse_initial(self.genesis)
        self.anchor_args=dict(expected_anchor=p['anchor'],allow_creator=self.f.creator['principal'],expected_context=encode_event(self.f.context),intended_members=[{k:m[k] for k in ('principal','device','signingKey')} for m in p['roster']['members']],time=self.time)
        self.args=dict(target=self.new,mailbox='newjoiner@example.invalid',allow_creator=self.f.creator['principal'],expected_context=encode_event(self.f.context),time=self.time)
    def test_certified_join_and_actual_protected_exchange(self):
        self.prepare_join()
        with self.assertRaisesRegex(ValueError,'genesis'):self.admission.accept_message(self.raw,**self.args)
        import_anchor(self.new_identity,self.genesis,**self.anchor_args)
        self.assertIsNone(self.new_identity.db.execute('SELECT 1 FROM mls_checkpoint').fetchone())
        self.assertIsNone(self.new_identity.db.execute('SELECT invitation FROM provider_mls_admission WHERE reference=?',(self.new['reference'],)).fetchone()[0])
        with self.assertRaises(RuntimeError):self.admission.accept_message(self.raw,**self.args,crash=lambda _:(_ for _ in ()).throw(RuntimeError('crash')))
        self.assertIsNone(self.new_identity.db.execute('SELECT 1 FROM mls_checkpoint').fetchone())
        result=self.admission.accept_message(self.raw,**self.args);self.assertEqual(result,self.admission.accept_message(self.raw,**self.args))
        self.assertEqual(result['status'],'accepted-unverified');self.assertIsNone(self.new_identity.db.execute('SELECT 1 FROM mls_configured_context').fetchone())
        self.principals=sorted(self.principals+[self.new['principal']])
        event=self.event(self.new,'e');wire=self.new_sender.prepare('joinedreply',encode_event(event),key=self.new['key'],envelope_sender='newjoiner@example.invalid',recipients=['creator@example.invalid'],time=self.time)
        self.assertEqual(self.sender.receiver.receive(unpack(roundtrip(wire)),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        back=self.event(self.f.creator,'d');wire=self.sender.prepare('backtojoiner',encode_event(back),key=self.f.creator['key'],envelope_sender='creator@example.invalid',recipients=['newjoiner@example.invalid'],time=self.time)
        self.assertEqual(self.new_sender.receiver.receive(unpack(roundtrip(wire)),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        joined=AdmittedQuorum(self.new_sender.receiver,self.worker,self.new);self.assertEqual(joined.live()[1]['snapshot']['epoch'],'2')
    def test_substituted_path_and_wrong_anchor_do_not_consume_package(self):
        self.prepare_join();wrong=dict(self.anchor_args,expected_anchor='f'*64)
        with self.assertRaises(ValueError):import_anchor(self.new_identity,self.genesis,**wrong)
        import_anchor(self.new_identity,self.genesis,**self.anchor_args)
        for mode in ('result','missing','duplicate','target','old-support'):
            wrapper=json.loads(self.raw);v=json.loads(base64.b64decode(wrapper['payload']))
            if mode=='result':v['orderingPath'][0]['candidate']['plan']['result']['epoch']='99'
            elif mode=='missing':v['orderingPath']=[]
            elif mode=='duplicate':v['orderingPath']*=2
            elif mode=='target':v['target']['device']=self.f.creator['device']
            else:
                item=wrapper['applicationAssertions'][-1];a=json.loads(base64.b64decode(item['payload']));a['version']='5';item['payload']=base64.b64encode(encode_event(a)).decode()
            raw=encode_event(v);wrapper.update(payload=base64.b64encode(raw).decode(),signature=sign(self.provider,self.f.creator,'email-next/mls-established-membership-invitation/v6',raw))
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.admission.accept_message(encode_event(wrapper),**self.args)
            self.assertIsNone(self.new_identity.db.execute('SELECT invitation FROM provider_mls_admission WHERE reference=?',(self.new['reference'],)).fetchone()[0])
            self.assertIsNone(self.new_identity.db.execute('SELECT 1 FROM mls_checkpoint').fetchone())

    def test_private_copy_rejects_new_principal_before_staging(self):
        keep=self.principals[:2];self.f.bundles={p:b for p,b in self.f.bundles.items() if p in keep}
        pairs=[(d,p) for d,p in zip(self.f.devices,self.f.proofs) if d['principal'] in keep];self.f.devices=[d for d,p in pairs];self.f.proofs=[p for d,p in pairs]
        self.principals=keep;self.devices=[{k:d[k] for k in ('principal','device')} for d in self.f.devices];self.witnesses=[d for d in self.witnesses if d['principal'] in keep]
        self.f.context['delivery']=dict(kind='private-copy-v0',originator=self.f.creator['principal'],recipient=next(p for p in keep if p!=self.f.creator['principal']))
        self.f.context['ordering']['witnesses']=[w for w in self.f.context['ordering']['witnesses'] if w['principal'] in keep]
        self.identity,self.sender,self.selected=self.endpoint('privatequorum');from initial_roster_lifecycle import InitialRosterRelease
        self.release=InitialRosterRelease(self.sender);self.join();new=make_device(self.provider,7,8)
        for identity in self.stores:identity.observe(new['record'],first_contact_policy='allow-unverified')
        with self.assertRaisesRegex(ValueError,'Private copy'):self.author_group.stage(ProviderKey(self.provider,self.f.creator),time=self.time,packages=[new['package']])
        self.assertEqual(self.author_group.live()[1]['snapshot']['epoch'],'1')


if __name__=='__main__':unittest.main()
