import base64,hashlib,json,unittest
from unittest.mock import patch
import test_own_devices as existing
from remote_pairing import Pairing,commitment,decode_offer
from pairing_relay import Relay,Channel
from own_devices import OwnDevices
from identity_store import IdentityStore
from event_encoding import encode_event
class RemotePairing(unittest.TestCase):
    tearDown=existing.OwnDeviceTests.tearDown
    wire=existing.OwnDeviceTests.wire
    def setUp(self):
        existing.OwnDeviceTests.setUp(self)
        self.stores[1].close();path=self.root/'unpaired.sqlite';self.stores[1]=IdentityStore(path)
        self.old=Pairing(self.stores[0],account='account');self.new=Pairing(self.stores[1],account='account')
        self.owner=OwnDevices(self.stores[0],account='local-account',principal=self.a['principal'],local_device=self.a['device'],mailboxes=[self.mailbox])
        # Existing own-account config is immutable; pairing uses the same local ID.
        self.old=Pairing(self.stores[0],account='local-account');self.new=Pairing(self.stores[1],account='local-account')
        self.anchor=encode_event(dict(version='0',purpose='identity-bundle',principal=self.a['principal'],states=[dict(payload=self.a['record']['state'],signature=self.a['record']['stateProof'])],bindings=[dict(payload=self.a['record']['binding'],authorization=self.a['record']['authorization'],possession=self.a['record']['possession'])]))
        now=int(self.time['latest']);self.offer=self.old.offer(self.owner,self.anchor,roles=['receive','send'],session_before=str(now-1),session_after=str(now+60),grant_before=str(now-1),grant_after=str(now+1800),time=self.time);self.session=decode_offer(self.offer)['session']
        self.relay=Relay(self.root/'relay.sqlite');self.addCleanup(self.relay.close);self.channel=Channel(self.relay.origin)
        self.channel.transfer(self.session,'offer',self.offer);self.channel.transfer(self.session,'anchor',self.anchor)
    def request(self):
        self.new.confirm_offer(self.channel.transfer(self.session,'offer'),self.channel.transfer(self.session,'anchor'),comparison=commitment('offer',self.offer),channel='independent-qr',time=self.time)
        request=self.new.request(self.session,self.b,binary=self.binary,time=self.time);self.channel.transfer(self.session,'request',request);return request
    def commit(self,request,**kw):return self.old.commit(self.session,request,owner=self.owner,device=self.a,binary=self.binary,comparison=commitment('request',request),channel='independent-qr',time=self.time,**kw)
    def pair(self):
        request=self.request();result=self.commit(self.channel.transfer(self.session,'request'));self.channel.transfer(self.session,'result',result)
        self.assertEqual(self.new.accept(self.session,self.channel.transfer(self.session,'result'),time=self.time)['status'],'received')
        self.bundle=json.loads(base64.b64decode(json.loads(result)['bundle']));self.raw=encode_event(self.bundle);self.head=json.loads(result)['head']
        self.owners=[self.owner,OwnDevices(self.stores[1],account='local-account',principal=self.a['principal'],local_device=self.b['device'],mailboxes=[self.mailbox])]
        return request,result
    def test_http_pairing_separate_grant_and_exact_retry(self):
        self.assertIsNone(self.stores[1].current_state(self.a['principal'])['head']);request,result=self.pair()
        self.assertEqual(self.commit(request),result);self.assertEqual(self.old.result(self.session),result)
        self.assertEqual(self.new.accept(self.session,result,time=self.time)['status'],'already-received')
        binding=json.loads(base64.b64decode(json.loads(request)['binding']));self.assertGreater(int(binding['notAfter']),int(decode_offer(self.offer)['notAfter']))
        for raw in [self.offer,self.anchor,request,result]:self.assertNotIn(b'checkpoint',raw);self.assertNotIn(b'privateKey',raw)
        self.assertEqual(self.owners[1].publications(time=self.time),[])
    def test_independent_comparison_and_request_swap(self):
        with self.assertRaises(ValueError):self.new.confirm_offer(self.offer,self.anchor,comparison='0'*64,channel='independent-qr',time=self.time)
        self.assertIsNone(self.stores[1].current_state(self.a['principal'])['head'])
        request=self.request();changed=json.loads(request);changed['session']='0'*64
        with self.assertRaises(ValueError):self.commit(encode_event(changed))
        with self.assertRaises(ValueError):self.old.commit(self.session,request,owner=self.owner,device=self.a,binary=self.binary,comparison='0'*64,channel='independent-qr',time=self.time)
        self.assertEqual(self.stores[0].current_state(self.a['principal'])['head'],self.a['state'])
    def test_commit_and_receive_crash_atomicity(self):
        request=self.request()
        with self.assertRaises(RuntimeError):self.commit(request,crash=lambda _:(_ for _ in ()).throw(RuntimeError('crash')))
        self.assertEqual(self.stores[0].current_state(self.a['principal'])['head'],self.a['state']);self.assertIsNone(self.old.result(self.session))
        self.assertEqual(self.stores[0].db.execute('SELECT count(*) FROM own_approval').fetchone()[0],0)
        result=self.commit(request)
        with self.assertRaises(RuntimeError):self.new.accept(self.session,result,time=self.time,crash=lambda _:(_ for _ in ()).throw(RuntimeError('crash')))
        self.assertEqual(self.stores[1].current_state(self.a['principal'])['head'],self.a['state']);self.assertIsNone(self.new.result(self.session))
        self.assertEqual(self.new.accept(self.session,result,time=self.time)['status'],'received')
    def test_withdraw_expiry_and_head_race(self):
        request=self.request();self.assertEqual(self.old.withdraw(self.session),'withdrawn')
        with self.assertRaises(ValueError):self.commit(request)
        later=dict.fromkeys(('earliest','latest'),str(int(self.time['latest'])+61))
        with self.assertRaises(ValueError):self.new.confirm_offer(self.offer,self.anchor,comparison=commitment('offer',self.offer),channel='independent-qr',time=later)
    def test_wrong_possession_and_relay_collision(self):
        request=self.request();bad=json.loads(request);bad['possession']='0'*128
        with self.assertRaises(ValueError):self.commit(encode_event(bad))
        from urllib.error import HTTPError
        with self.assertRaises(HTTPError) as error:self.channel.transfer(self.session,'request',encode_event(bad))
        error.exception.close()
    def test_accepted_head_change_blocks_enrollment(self):
        request=self.request();self.stores[0].accept_successor(self.raw,candidate_digest=self.head,time=self.time)
        with self.assertRaisesRegex(ValueError,'head'):self.commit(request)
    def test_restart_lost_result_and_delayed_receipt(self):
        request=self.request();result=self.commit(request)
        self.stores[0].close();self.stores[0]=IdentityStore(self.root/'0.sqlite');self.old=Pairing(self.stores[0],account='local-account')
        self.assertEqual(self.old.result(self.session),result)
        later=dict.fromkeys(('earliest','latest'),str(int(self.time['latest'])+61))
        self.assertEqual(self.new.accept(self.session,result,time=later)['status'],'received')
        self.assertEqual(self.old.withdraw(self.session),'already-terminal')
    def test_session_expiry_does_not_commit(self):
        request=self.request();later=dict.fromkeys(('earliest','latest'),str(int(self.time['latest'])+61))
        with self.assertRaisesRegex(ValueError,'validity'):self.old.commit(self.session,request,owner=self.owner,device=self.a,binary=self.binary,comparison=commitment('request',request),channel='independent-full-comparison',time=later)
        self.assertEqual(self.stores[0].current_state(self.a['principal'])['head'],self.a['state'])
    def test_wrong_anchor_and_new_device_cancellation(self):
        wrong=json.loads(self.anchor);wrong['principal']='enp0:'+'f'*64
        with self.assertRaises(ValueError):self.new.confirm_offer(self.offer,encode_event(wrong),comparison=commitment('offer',self.offer),channel='independent-qr',time=self.time)
        request=self.request();self.assertEqual(self.new.withdraw(self.session),'withdrawn');result=self.commit(request)
        with self.assertRaises(ValueError):self.new.accept(self.session,result,time=self.time)
        self.assertEqual(self.stores[1].current_state(self.a['principal'])['head'],self.a['state'])
    def test_grant_cannot_exceed_authorizer(self):
        with self.assertRaisesRegex(ValueError,'validity'):self.old.offer(self.owner,self.anchor,roles=['receive'],session_before=self.time['earliest'],session_after=str(int(self.time['latest'])+60),grant_before=self.time['earliest'],grant_after=str(int(self.time['latest'])+100000),time=self.time)

    def test_existing_different_anchor_is_not_replaced(self):
        self.stores[1].observe(self.b['record'],first_contact_policy='allow-unverified')
        with self.assertRaisesRegex(ValueError,'anchor conflict'):self.new.confirm_offer(self.offer,self.anchor,comparison=commitment('offer',self.offer),channel='independent-qr',time=self.time)
        self.assertEqual(self.stores[1].current_state(self.a['principal'])['head'],self.b['state'])
        self.assertIsNone(self.stores[1].db.execute('SELECT 1 FROM pairing_sessions').fetchone())

    def test_actual_protected_delivery_after_remote_pairing(self):
        self.pair()
        # Reuse the existing joined own-device delivery test, replacing only its
        # pairing setup with the completed remote flow and current public sync.
        def synced():
            from own_devices import PublicSpool
            spool=PublicSpool(self.root/'paired-public.sqlite');self.addCleanup(spool.close)
            for owner,device in zip(self.owners,[self.a,self.b]):
                owner.publication(expected_revision=0,enabled=True);owner.publish_device(self.wire(device),time=self.time);spool.put(owner.publications(time=self.time))
            for owner in self.owners:owner.sync_from('paired-public',spool,time=self.time)
            return [self.wire(d) for d in [self.a,self.b]]
        self.sync=synced
        existing.OwnDeviceTests.test_actual_two_stores_initial_roster_and_protected_delivery(self)

if __name__=='__main__':unittest.main()
