import base64
import hashlib
import json
import unittest
from application_invitation import ApplicationInvitationAdmission,parse
import test_signed_application_admission as fixtures
from provider_mls import call,sign
from event_encoding import encode_event
from passive_discovery import decode_passive_discovery
from invitation_mime import package,select
from smtp_loopback import roundtrip

def crash_received(path,binary,raw,args):
    import os
    from identity_store import IdentityStore
    identity=IdentityStore(path);admission=ApplicationInvitationAdmission(identity,binary)
    admission.accept_message(raw,**args,crash=lambda stage:os._exit(89) if stage=='before-commit' else None)

class ApplicationInvitationTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.SignedAdmissionTests();self.f.selected_operations=getattr(self,'selected_operations',['answer','message','question']);self.f.setUp();f=self.f;a,b=f.devices
        self.admission=ApplicationInvitationAdmission(f.identity,f.binary)
        self.group=call(f.binary,op='invite-fixture-context',checkpoint=a['checkpoint'],key=a['key'],identity=a['identity'],package=b['package'],context=f.context_raw.hex(),embedded=True)
        proofs=[json.loads(s['wrapper']) for s in f.selected];refs=[]
        for p in proofs:
            d=decode_passive_discovery(encode_event(p));v=d['assertion']['value'];refs.append(dict(principal=v['principal'],device=v['device'],digest=d['assertion']['digest'],signature=d['signature'].hex()))
        self.payload=dict(version='1',purpose='mls-new-conversation-invitation',invitation='6'*32,profile='mls-1-0001',conversation='2'*32,
          creator={k:a[k] for k in ('principal','device','state','binding')},target=dict({k:b[k] for k in ('principal','device','state','binding')},mailbox=f.selected[1]['mailbox']),
          group=base64.b64encode(bytes.fromhex(self.group['group'])).decode(),epoch='1',keyPackageRef=base64.b64encode(bytes.fromhex(b['reference'])).decode(),
          notBefore=f.time['earliest'],notAfter=str(int(f.time['latest'])+300),context=base64.b64encode(f.context_raw).decode(),welcome=base64.b64encode(bytes.fromhex(self.group['welcome'])).decode(),applicationAssertions=refs)
        self.proofs=proofs;self.raw=self.wrap()
        self.selections=[dict(principal=d['principal'],device=d['device'],mailbox=s['mailbox'],generation=s['generation']) for d,s in zip(f.devices,f.selected)]
    def tearDown(self):self.f.tearDown()
    def wrap(self):
        raw=encode_event(self.payload);a=self.f.devices[0]
        return encode_event(dict(payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,a,'email-next/mls-new-conversation-invitation/v1',raw),identity=self.proofs[0]['identity'],applicationAssertions=self.proofs))
    def accept(self,raw=None,**overrides):
        f=self.f;args=dict(target=f.devices[1],mailbox=f.selected[1]['mailbox'],allow_creator=f.devices[0]['principal'],selections=self.selections,time=f.time,trust_policy='allow-unverified');args.update(overrides)
        return self.admission.accept_message(self.raw if raw is None else raw,**args)
    def test_actual_smtp_embedded_admission_and_protected_contribution(self):
        received=select(roundtrip(package(self.raw)));result=self.accept(received)
        self.assertEqual(result['status'],'admitted-unverified')
        f=self.f;event=dict(version='1',purpose='contribution',event='7'*32,conversation='2'*32,principal=f.devices[0]['principal'],audience=sorted(d['principal'] for d in f.devices),disclosures=[],operation=dict(kind='message',text='Hello after a public carrier.',replyTo=[]))
        sent=call(f.binary,op='send',checkpoint=self.group['checkpoint'],key=f.devices[0]['key'],group=self.group['group'],application=encode_event(event).hex())
        self.assertEqual(self.admission.receiver.receive(bytes.fromhex(sent['wire']),time=f.time,trust_policy='allow-unverified')['status'],'projected-context-matched')
    def test_proof_substitution_cannot_poison_accepted_replay(self):
        accepted=self.accept();changed=json.loads(self.raw);changed['applicationAssertions'][0]['signature']='00'*64
        with self.assertRaises(ValueError):self.accept(encode_event(changed))
        later=dict.fromkeys(['earliest','latest'],str(int(self.f.time['latest'])+1000))
        self.assertEqual(self.accept(time=later),accepted)
        changed=json.loads(self.raw);changed['applicationAssertions'][0]['identity']=dict(reversed(list(changed['applicationAssertions'][0]['identity'].items())))
        self.assertEqual(self.accept(encode_event(changed),time=later),accepted)
    def test_no_configured_flag_can_replace_missing_association(self):
        with self.assertRaisesRegex(ValueError,'selection'):self.accept(selections=[])
        self.assertIsNone(self.f.identity.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])
    def test_transaction_failure_and_missing_embedded_tree_do_not_consume(self):
        with self.assertRaises(RuntimeError):self.accept(crash=lambda stage:(_ for _ in ()).throw(RuntimeError('crash')))
        self.assertEqual(self.f.identity.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0],0)
        self.assertEqual(self.f.identity.db.execute('SELECT count(*) FROM application_admissions').fetchone()[0],0)
        self.payload['welcome']=base64.b64encode(bytes.fromhex(self.f.group['welcome'])).decode()
        with self.assertRaises(ValueError):self.accept(self.wrap())
        self.assertIsNone(self.f.identity.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])
        self.accept()
    def test_version_domain_proof_coverage_and_context_are_exact(self):
        from mls_invitation import parse as parse_v0
        with self.assertRaises(ValueError):parse_v0(self.raw)
        wrong=json.loads(self.raw);payload=base64.b64decode(wrong['payload']);wrong['signature']=sign(self.f.binary,self.f.devices[0],'email-next/mls-new-conversation-invitation/v0',payload)
        with self.assertRaises(ValueError):self.accept(encode_event(wrong))
        wrong=json.loads(self.raw);wrong['applicationAssertions'].reverse()
        with self.assertRaises(ValueError):parse(encode_event(wrong))
        self.payload['applicationAssertions'][0]['signature']='00'*64
        with self.assertRaises(ValueError):parse(self.wrap())

    def test_process_exit_before_public_admission_commit(self):
        import multiprocessing
        f=self.f;args=dict(target=f.devices[1],mailbox=f.selected[1]['mailbox'],allow_creator=f.devices[0]['principal'],selections=self.selections,time=f.time,trust_policy='allow-unverified')
        child=multiprocessing.get_context('spawn').Process(target=crash_received,args=(f.path,f.binary,self.raw,args))
        child.start();child.join(15);self.assertEqual(child.exitcode,89)
        for table in ['mls_checkpoint','application_admissions','application_invitation_acceptance','mls_application_agreement']:
            self.assertEqual(f.identity.db.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
        self.assertIsNone(f.identity.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])
        self.assertEqual(self.accept()['status'],'admitted-unverified')

    def test_signed_interval_before_binding_does_not_consume_package(self):
        f=self.f
        binding=json.loads(base64.b64decode(f.devices[0]['record']['binding']))
        self.payload['notBefore']=str(int(binding['notBefore'])-1)
        # Broaden assertion intervals with real device signatures, so the
        # independently signed device binding is the decisive lower boundary.
        for index,(proof,device) in enumerate(zip(self.proofs,f.devices)):
            value=json.loads(base64.b64decode(proof['payload']));value['notBefore']=self.payload['notBefore']
            raw=encode_event(value);signature=sign(f.binary,device,'email-next/passive-discovery/v1',raw)
            proof['payload']=base64.b64encode(raw).decode();proof['signature']=signature
            ref=next(r for r in self.payload['applicationAssertions'] if r['device']==device['device'])
            ref.update(digest=hashlib.sha256(raw).hexdigest(),signature=signature)
        with self.assertRaisesRegex(ValueError,'Binding lifetime'):self.accept(self.wrap())
        self.assertIsNone(f.identity.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])
        self.assertEqual(f.identity.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0],0)
