import base64,copy,json,unittest
import test_quorum_signed_exchange as signed
import test_quorum_recovery as recovery
from event_encoding import encode_event
from passive_discovery import decode_passive_discovery
from provider_mls import sign
from ordering_carrier import select_object,package
from quorum_recovery import POLICY

class SignedRecoveryTests(unittest.TestCase):
    setUp=signed.SignedExchangeTests.setUp;tearDown=signed.SignedExchangeTests.tearDown
    endpoint=signed.SignedExchangeTests.endpoint;prepare=signed.SignedExchangeTests.prepare;join=signed.SignedExchangeTests.join;certify=signed.SignedExchangeTests.certify;event=signed.SignedExchangeTests.event
    setup_chain=recovery.QuorumRecoveryTests.setup_chain
    def test_signed_recovery_revoked_intermediate_and_exact_supplements(self):
        self.setup_chain();before=self.target.live();final=[]
        for witness in self.f.context['ordering']['witnesses']:
            device=next(d for d in self.f.devices if d['device']==witness['device'])
            wrapper=copy.deepcopy(next(w for w in self.f.proofs if decode_passive_discovery(encode_event(w))['assertion']['value']['device']==device['device']))
            value=json.loads(base64.b64decode(wrapper['payload']));head=self.target.identity.current_state(device['principal'])['head']
            if head!=value['state']:
                wrapper['identity']=json.loads(self.target.db.execute('SELECT bundle FROM identity_transitions WHERE principal=? AND digest=?',(device['principal'],head)).fetchone()[0]);value['state']=head
                raw=encode_event(value);wrapper.update(payload=base64.b64encode(raw).decode(),signature=sign(self.provider,device,'email-next/passive-discovery/v7',raw))
            final.append(encode_event(wrapper))
        options=dict(expected_predecessor=self.start,allowed=set(),time=self.time,policy=POLICY,final_support=final)
        for mode in ('missing','altered'):
            bad=select_object(self.carriers[0])
            if mode=='missing':bad['witnessAssertions'].pop()
            else:bad['witnessAssertions'][0]['signature']='0'*128
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.recovery.receive([package(encode_event(bad)),self.carriers[1]],**options)
            self.assertEqual(self.target.live(),before)
        with self.assertRaises(ValueError):self.recovery.receive(self.carriers,**dict(options,final_support=[]))
        with self.assertRaises(RuntimeError):self.recovery.receive(self.carriers,**options,crash=lambda _:(_ for _ in ()).throw(RuntimeError('crash')))
        self.assertEqual(self.target.live(),before)
        self.assertEqual(self.target.db.execute('SELECT count(*) FROM qo_recovery_step').fetchone()[0],0)
        result=self.recovery.receive(self.carriers,**options)
        self.assertEqual(result['status'],'accepted-quorum-recovery');self.assertEqual(result,self.recovery.receive(self.carriers,**options))
        self.assertEqual(self.target.db.execute('SELECT count(*) FROM mls_remediation_epoch_hold').fetchone()[0],1)
        retained=[json.loads(r[0])['carrier'] for r in self.target.db.execute('SELECT record FROM qo_recovery_step')]
        self.assertTrue(all(c['version']=='2' and len(c['witnessAssertions'])==len(final) for c in retained))
        from mls_mime import unpack
        self.assertNotEqual(self.target.receiver.receive(unpack(self.intermediate),time=self.time,trust_policy='allow-unverified').get('applicationState'),'accepted')
        from smtp_loopback import roundtrip
        sender=self.senders[self.target.device['device']]
        wire=sender.prepare('signedrecoveredreply',encode_event(self.event(self.target.device,'8')),key=self.target.device['key'],envelope_sender='recovered@example.invalid',recipients=['creator@example.invalid'],time=self.time)
        self.assertEqual(self.sender.receiver.receive(unpack(roundtrip(wire)),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')

if __name__=='__main__':unittest.main()
