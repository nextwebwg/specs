import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from event_encoding import encode_event
from identity_store import IdentityStore
from provider_mls import make_device,advertisement,sign,call
from passive_discovery import decode_passive_discovery
from passive_discovery_verify import verify_passive_discovery
from signed_application_admission import SignedApplicationAdmission
from mls_receive import MlsReceive

def crash_admission(path,binary,reference,invitation,args):
    identity=IdentityStore(path);admission=SignedApplicationAdmission(identity,binary)
    admission.accept_signed(reference,invitation,**args,crash=lambda stage:os._exit(87) if stage=='before-commit' else None)

class SignedAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'identity.sqlite'
        self.binary=Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR'])/'provider-mls'
        self.devices=[make_device(self.binary,1,2),make_device(self.binary,3,4)]
        self.time=dict.fromkeys(['earliest','latest'],str(max(d['time'] for d in self.devices)))
        self.identity=IdentityStore(self.path)
        for d in self.devices:self.identity.observe(d['record'],first_contact_policy='allow-unverified')
        self.admission=SignedApplicationAdmission(self.identity,self.binary);self.admission.publish_local(self.devices[1])
        self.selected=[]
        for i,d in enumerate(self.devices):self.selected.append(self.observe(i,getattr(self,'advertised_operations',{}).get(i,getattr(self,'selected_operations',['answer','message','question']))))
        self.context=dict(version='2',purpose='conversation-context',conversation='2'*32,profile='mls-1-0001',administrators=[self.devices[0]['principal']],application=dict(envelopeVersion='1',operations=getattr(self,'selected_operations',['answer','message','question'])),ordering={'kind':'fixed-roster-v0'})
        self.create_group()
    def tearDown(self):self.identity.close();self.temp.cleanup()
    def observe(self,i,operations):
        d=self.devices[i];mailbox=f'person{i}@example.invalid';wrapper=advertisement(self.binary,d,mailbox)
        value=json.loads(base64.b64decode(wrapper['payload']));value.update(version='1',record=('a' if i==0 else 'b')*32,applications=[dict(envelopeVersion='1',operations=operations,ordering=['fixed-roster-v0'])])
        raw=encode_event(value);wrapper['payload']=base64.b64encode(raw).decode();wrapper['signature']=sign(self.binary,d,'email-next/passive-discovery/v1',raw)
        wire=encode_event(wrapper);self.assertEqual(verify_passive_discovery(wire,self.identity,time=self.time,trust_policy='allow-unverified')['status'],'snapshot-authorized-unverified')
        parsed=decode_passive_discovery(wire);digest=parsed['assertion']['digest']
        self.admission.associations.observe_validated_batch([dict(assertion=raw,signature=parsed['signature'],signingKey=bytes.fromhex(d['key']),outerFrom=[mailbox],sourceId='fixture',parserRevision='fixture0',observedAt=self.time['earliest'])])
        result=self.admission.associations.decide(decision_id=str(i+1)*32,mailbox=mailbox,expected_generation=None,kind='first-contact',principal=d['principal'],actor='configured-policy',policy_revision='1',trust_policy='allow-unverified',time=self.time)
        self.assertEqual(result['status'],'associated-unverified')
        return dict(wrapper=wire,mailbox=mailbox,generation=result['generation'],digest=digest)
    def create_group(self):
        a,b=self.devices;self.context_raw=encode_event(self.context)
        self.group=call(self.binary,op='invite-fixture-context',checkpoint=a['checkpoint'],key=a['key'],identity=a['identity'],package=b['package'],context=self.context_raw.hex())
        self.invitation=dict(reference=b['reference'],welcome=self.group['welcome'],tree=self.group['tree'])
    def accept(self,**overrides):
        args=dict(selected=self.selected,expected_group=self.group['group'],expected_context=self.context_raw,creator=self.devices[0]['identity'],time=self.time,trust_policy='allow-unverified');args.update(overrides)
        return self.admission.accept_signed(self.devices[1]['reference'],self.invitation,**args)
    def test_real_signed_admission_and_application_without_configured_flags(self):
        joined=self.accept();self.assertEqual(joined['group'],self.group['group'])
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM application_admission_devices').fetchone()[0],2)
        self.assertEqual(set(r[0] for r in self.identity.db.execute('SELECT kind FROM mls_application_agreement_provenance')),{'signed-admission'})
        event=dict(version='1',purpose='contribution',event='3'*32,conversation='2'*32,principal=self.devices[0]['principal'],audience=sorted(d['principal'] for d in self.devices),operation=dict(kind='message',text='Signed agreement works.',replyTo=[]),disclosures=[])
        sent=call(self.binary,op='send',checkpoint=self.group['checkpoint'],key=self.devices[0]['key'],group=self.group['group'],application=encode_event(event).hex())
        result=self.admission.receiver.receive(bytes.fromhex(sent['wire']),time=self.time,trust_policy='allow-unverified')
        self.assertEqual(result['status'],'projected-context-matched')
        with self.assertRaisesRegex(ValueError,'Signed agreement'):self.admission.receiver.application_agreement.configure_device(self.group['group'],self.devices[0]['identity'],self.devices[0]['key'],self.context['application'])
    def test_rollback_retry_and_expiry_do_not_retroactively_remove_agreement(self):
        def fail(stage):raise RuntimeError('before commit')
        with self.assertRaises(RuntimeError):self.accept(crash=fail)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0],0)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mls_application_agreement').fetchone()[0],0)
        self.assertIsNone(self.identity.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])
        joined=self.accept();later=dict.fromkeys(['earliest','latest'],str(int(self.time['latest'])+601))
        self.identity.close();self.identity=IdentityStore(self.path);self.admission=SignedApplicationAdmission(self.identity,self.binary)
        self.assertEqual(self.accept(time=later),joined)
        self.assertEqual(self.admission.receiver.application_agreement.resolve(joined['group'],joined['members']),self.context['application'])
        event=dict(version='1',purpose='contribution',event='4'*32,conversation='2'*32,principal=self.devices[0]['principal'],audience=sorted(d['principal'] for d in self.devices),operation=dict(kind='message',text='Agreement survives advertisement expiry.',replyTo=[]),disclosures=[])
        sent=call(self.binary,op='send',checkpoint=self.group['checkpoint'],key=self.devices[0]['key'],group=self.group['group'],application=encode_event(event).hex())
        self.assertEqual(self.admission.receiver.receive(bytes.fromhex(sent['wire']),time=later,trust_policy='allow-unverified')['status'],'projected-context-matched')
        changed=[dict(s) for s in self.selected];wrapper=json.loads(changed[0]['wrapper']);wrapper['signature']='00'*64;changed[0]['wrapper']=encode_event(wrapper)
        with self.assertRaisesRegex(ValueError,'retry conflict'):self.accept(selected=changed,time=later)
    def test_expired_new_admission_and_strict_trust_fail_before_consumption(self):
        later=dict.fromkeys(['earliest','latest'],str(int(self.time['latest'])+601))
        with self.assertRaisesRegex(ValueError,'Signed authority'):self.accept(time=later)
        with self.assertRaisesRegex(ValueError,'Signed authority'):self.accept(trust_policy='require-verification')
        self.assertIsNone(self.identity.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])
    def test_changed_mailbox_generation_holds_new_admission(self):
        selected=self.selected[0]
        self.admission.associations.decide(decision_id='9'*32,mailbox=selected['mailbox'],expected_generation=selected['generation'],kind='disable',principal=self.devices[0]['principal'],actor='local-user',policy_revision='2',trust_policy='allow-unverified',time=self.time)
        with self.assertRaisesRegex(ValueError,'Changed mailbox'):self.accept()
    def test_complementary_support_is_not_union(self):
        changed=[]
        for i,ops in enumerate([['message','question'],['answer','message']]):
            choice=dict(self.selected[i]);wrapper=json.loads(choice['wrapper']);value=json.loads(base64.b64decode(wrapper['payload']));value['applications'][0]['operations']=ops
            raw=encode_event(value);wrapper['payload']=base64.b64encode(raw).decode();wrapper['signature']=sign(self.binary,self.devices[i],'email-next/passive-discovery/v1',raw)
            choice.update(wrapper=encode_event(wrapper),digest=hashlib.sha256(raw).hexdigest());changed.append(choice)
        with self.assertRaisesRegex(ValueError,'intersection'):self.accept(selected=changed)
        # Retain fresh, independently signed observations, then select the actual
        # common subset in a newly constructed authenticated context.
        for i,choice in enumerate(changed):
            wrapper=json.loads(choice['wrapper']);value=json.loads(base64.b64decode(wrapper['payload']));value['record']=str(i+3)*32
            raw=encode_event(value);wrapper['payload']=base64.b64encode(raw).decode();wrapper['signature']=sign(self.binary,self.devices[i],'email-next/passive-discovery/v1',raw)
            choice.update(wrapper=encode_event(wrapper),digest=hashlib.sha256(raw).hexdigest())
            parsed=decode_passive_discovery(choice['wrapper'])
            self.assertEqual(verify_passive_discovery(choice['wrapper'],self.identity,time=self.time,trust_policy='allow-unverified')['status'],'snapshot-authorized-unverified')
            self.admission.associations.observe_validated_batch([dict(assertion=raw,signature=parsed['signature'],signingKey=bytes.fromhex(self.devices[i]['key']),outerFrom=[choice['mailbox']],sourceId='subset',parserRevision='fixture0',observedAt=self.time['earliest'])])
        self.selected=changed;self.context['application']['operations']=['message'];self.create_group()
        self.assertEqual(self.accept()['group'],self.group['group'])


    def test_real_identity_successor_makes_old_assertion_stale(self):
        d=self.devices[0];r=d['record'];state=json.loads(base64.b64decode(r['state']))
        state.update(record='e'*32,revision='1',previous=[d['state']]);raw=encode_event(state)
        bundle=dict(version='0',purpose='identity-bundle',principal=d['principal'],states=[dict(payload=base64.b64encode(raw).decode(),signature=sign(self.binary,d,'email-next/identity-state/v0',raw)),dict(payload=r['state'],signature=r['stateProof'])],bindings=[dict(payload=r['binding'],authorization=r['authorization'],possession=r['possession'])])
        self.assertEqual(self.identity.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(raw).hexdigest(),time=self.time)['status'],'accepted-unverified')
        with self.assertRaisesRegex(ValueError,'Signed authority: stale'):self.accept()
        self.assertIsNone(self.identity.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])

    def test_process_exit_rolls_back_package_agreement_and_checkpoint(self):
        import multiprocessing
        args=dict(selected=self.selected,expected_group=self.group['group'],expected_context=self.context_raw,creator=self.devices[0]['identity'],time=self.time,trust_policy='allow-unverified')
        child=multiprocessing.get_context('spawn').Process(target=crash_admission,args=(self.path,self.binary,self.devices[1]['reference'],self.invitation,args))
        child.start();child.join(15);self.assertEqual(child.exitcode,87)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0],0)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM application_admissions').fetchone()[0],0)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mls_application_agreement').fetchone()[0],0)
        self.assertIsNone(self.identity.db.execute('SELECT invitation FROM provider_mls_admission').fetchone()[0])
        self.assertEqual(self.accept()['group'],self.group['group'])
