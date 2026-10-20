import base64,json,unittest
import test_admitted_quorum as admitted
import test_quorum_join as joined
import test_quorum_release as releases
from event_encoding import encode_event
from provider_mls import sign
from initial_roster_lifecycle import InitialRosterRelease
from quorum_exchange_support import current
from passive_discovery import decode_passive_discovery

class SignedExchangeTests(unittest.TestCase):
    exchange_assertion_version="7"
    send=admitted.AdmittedQuorumTests.send
    test_sender_handshake_continuity=admitted.AdmittedQuorumTests.test_durable_candidates_continue_handshake_with_application_interleaving
    prepare_release=releases.QuorumReleaseTests.prepare_release
    prepare_join=joined.QuorumJoinTests.prepare_join;certify=admitted.AdmittedQuorumTests.certify;event=admitted.AdmittedQuorumTests.event
    test_established7_actual_protected_exchange=joined.QuorumJoinTests.test_certified_join_and_actual_protected_exchange
    endpoint=admitted.AdmittedQuorumTests.endpoint;prepare=admitted.AdmittedQuorumTests.prepare;join=admitted.AdmittedQuorumTests.join;tearDown=admitted.AdmittedQuorumTests.tearDown
    def setUp(self):
        admitted.AdmittedQuorumTests.setUp(self)
        for d,p in zip(self.f.devices,self.f.proofs):
            v=json.loads(base64.b64decode(p['payload']));v.update(version='7',orderingExchanges=[dict(format='quorum-exchange-experiment',version='1')]);raw=encode_event(v);p.update(payload=base64.b64encode(raw).decode(),signature=sign(self.provider,d,'email-next/passive-discovery/v7',raw))
        self.identity,self.sender,self.selected=self.endpoint('signed-exchange-creator');self.release=InitialRosterRelease(self.sender)
    def test_initial7_admits_signed_exchange_support_without_configuration(self):
        self.join()
        for group in self.groups:
            wrappers=current(group,time=self.time)
            self.assertEqual(len(wrappers),len(self.witnesses))
            self.assertEqual(group.db.execute("SELECT count(*) FROM qo_signed_exchange_support").fetchone()[0],len(self.f.devices))
            self.assertTrue(all(decode_passive_discovery(encode_event(w))['assertion']['value']['version']=='7' for w in wrappers))
    def test_signed_exchange1_and_carrier2_keep_old_versions_strict(self):
        self.join()
        from quorum_exchange import QuorumExchange,content,parse
        from ordering_mls import ProviderKey,candidate_id
        from ordering_certificates import unsigned,sign as certificate_sign,digest,bundle,encode
        from ordering_scope import scope_digest
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        import ordering_carrier
        author=self.author_group;candidate=author.stage(ProviderKey(self.provider,self.f.creator),time=self.time);scope=candidate['plan']['scope']
        coordinator=self.witnesses[0];obj=certificate_sign(unsigned('proposal',scope_digest(scope),0,coordinator['principal']+'|'+coordinator['device'],candidate=candidate_id(candidate),newView=''),ProviderKey(self.provider,coordinator));proof=bundle(digest(obj),[obj])
        wrappers=current(author,time=self.time);raw=content(scope,proof,[candidate],witness_assertions=wrappers)
        peer=next(g for g in self.groups if g is not author);target=peer.device;route=next(c for d,c in zip(self.f.devices,self.selected) if d is target);source=next(c['mailbox'] for d,c in zip(self.f.devices,self.selected) if d is self.f.creator)
        adapter=QuorumExchange(self.sender,author);receiver=QuorumExchange(self.senders[target['device']],peer)
        self.assertEqual(adapter.db.execute('SELECT count(*) FROM qo_exchange_support').fetchone()[0],0)
        wire=adapter.prepare('signedexchange',raw,envelope_sender=source,recipient=dict(mailbox=route['mailbox'],principal=target['principal'],device=target['device']),association_targets=[dict(mailbox=route['mailbox'],generation=route['generation'],principal=target['principal'],observation=route['digest'])],time=self.time)
        from quorum_exchange_support import complete,retain_locked
        renewed=json.loads(json.dumps(wrappers));position=next(i for i,w in enumerate(renewed) if decode_passive_discovery(encode_event(w))['assertion']['value']['device']==target['device'])
        renewed_value=json.loads(base64.b64decode(renewed[position]['payload']));renewed_value['record']='f'*32;renewed_raw=encode_event(renewed_value)
        renewed[position].update(payload=base64.b64encode(renewed_raw).decode(),signature=sign(self.provider,target,'email-next/passive-discovery/v7',renewed_raw))
        for selected in (renewed,wrappers):
            adapter.db.execute('BEGIN IMMEDIATE');digests=complete(self.identity,selected,self.f.context,time=self.time);retain_locked(adapter.db,scope['group'],selected,digests);adapter.db.execute('COMMIT')
            if selected is renewed:
                with SenderWorker(self.sender) as worker:
                    with self.assertRaisesRegex(ValueError,'support-held'):worker.submit_quorum_exchange('signedexchange',group=author,port=1,time=self.time)
        smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit_quorum_exchange('signedexchange',group=author,port=smtp.port,time=self.time)['state'],'accepted')
        smtp.done();self.assertEqual(receiver.receive(smtp.wire,time=self.time)['kind'],'proposal')
        bad=json.loads(raw);bad['witnessAssertions'].pop()
        with self.assertRaisesRegex(ValueError,'coverage'):parse(encode(bad))
        bad=json.loads(raw);bad['version']='0'
        with self.assertRaises(ValueError):parse(encode(bad))
        proof=admitted.AdmittedQuorumTests.certify(self,candidate);decision=author.install(candidate,proof,time=self.time);carrier=author.release(decision,time=self.time);value=json.loads(carrier);self.assertEqual(value['version'],'2');self.assertEqual(len(value['witnessAssertions']),len(self.witnesses))
        old=dict(value,version='1');old.pop('witnessAssertions')
        with self.assertRaisesRegex(ValueError,'carrier2'):ordering_carrier.receive(peer,ordering_carrier.package(encode(old)),time=self.time)
        changed=json.loads(carrier);changed['witnessAssertions'].reverse()
        with self.assertRaises(ValueError):ordering_carrier.receive(peer,ordering_carrier.package(encode(changed)),time=self.time)
        self.assertEqual(ordering_carrier.receive(peer,ordering_carrier.package(carrier),time=self.time)['decision'],decision)

    def test_established7_fixed_durable_release(self):
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        from quorum_join import import_anchor
        from established_invitation_mime import select
        self.prepare_release()
        self.assertEqual(self.parsed[2]['version'],'7')
        with SenderWorker(self.sender) as worker:
            with self.assertRaises(ValueError):worker.submit_quorum_invitation('quorumwelcome',group=self.author_group,port=1,time=self.time)
            for control in self.controls:
                smtp=LocalSMTP();self.assertEqual(worker.submit_quorum_control(control,group=self.author_group,port=smtp.port,time=self.time)['state'],'accepted');smtp.done()
            smtp=LocalSMTP();self.assertEqual(worker.submit_quorum_invitation7('quorumwelcome',group=self.author_group,port=smtp.port,time=self.time)['state'],'accepted');smtp.done()
        import_anchor(self.new_identity,self.genesis,**self.anchor_args)
        self.assertEqual(self.admission.accept_message(select(smtp.wire),**self.args)['status'],'accepted-unverified')

    def test_assertion7_schema_purpose_and_expiry(self):
        from passive_discovery_verify import verify_passive_discovery
        from mls_receive import LockedIdentity
        proof=json.loads(json.dumps(self.f.proofs[0]));value=json.loads(base64.b64decode(proof['payload']));device=self.f.devices[0]
        for mode in ('old-version','old-exchange'):
            changed=dict(value)
            if mode=='old-version':changed['version']='6'
            else:changed['orderingExchanges']=[dict(format='quorum-exchange-experiment',version='0')]
            raw=encode_event(changed);bad=dict(proof,payload=base64.b64encode(raw).decode())
            with self.assertRaises(ValueError):decode_passive_discovery(encode_event(bad))
        raw=base64.b64decode(proof['payload']);proof['signature']=sign(self.provider,device,'email-next/passive-discovery/v6',raw)
        self.assertEqual(verify_passive_discovery(encode_event(proof),LockedIdentity(self.identity),time=self.time,trust_policy='allow-unverified')['status'],'invalid')
        value['notAfter']=self.time['latest'];raw=encode_event(value);proof.update(payload=base64.b64encode(raw).decode(),signature=sign(self.provider,device,'email-next/passive-discovery/v7',raw))
        future={k:str(int(v)+1) for k,v in self.time.items()}
        self.assertEqual(verify_passive_discovery(encode_event(proof),LockedIdentity(self.identity),time=future,trust_policy='allow-unverified')['status'],'not-current')
