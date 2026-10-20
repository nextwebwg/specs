import json,unittest
from pathlib import Path
import test_admitted_quorum as admitted
from quorum_exchange import QuorumExchange,content,parse
from ordering_certificates import unsigned,sign,digest,bundle,encode,decode_event
from ordering_scope import scope_digest
from ordering_mls import ProviderKey,candidate_id
from ordering_store import VoteStore
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP

class ExchangeTests(unittest.TestCase):
    setUp=admitted.AdmittedQuorumTests.setUp;tearDown=admitted.AdmittedQuorumTests.tearDown
    endpoint=admitted.AdmittedQuorumTests.endpoint;prepare=admitted.AdmittedQuorumTests.prepare;join=admitted.AdmittedQuorumTests.join
    def test_explicit_support_exact_retry_receive_and_durable_prepare(self):
        self.join();author=self.author_group;adapter=QuorumExchange(self.sender,author)
        candidate=author.stage(ProviderKey(self.provider,self.f.creator),time=self.time)
        scope=candidate['plan']['scope'];d=self.witnesses[0];sid=d['principal']+'|'+d['device']
        obj=sign(unsigned('proposal',scope_digest(scope),0,sid,candidate=candidate_id(candidate),newView=''),ProviderKey(self.provider,d));proof=bundle(digest(obj),[obj]);raw=content(scope,proof,[candidate])
        peer=next(g for g in self.groups if g is not author);device=peer.device;sender=self.senders[device['device']];receiver=QuorumExchange(sender,peer)
        association=next(c for x,c in zip(self.f.devices,self.selected) if x is device);source=next(c['mailbox'] for x,c in zip(self.f.devices,self.selected) if x is self.f.creator)
        options=dict(envelope_sender=source,recipient=dict(mailbox=association['mailbox'],principal=device['principal'],device=device['device']),association_targets=[dict(mailbox=association['mailbox'],generation=association['generation'],principal=device['principal'],observation=association['digest'])],time=self.time)
        with self.assertRaisesRegex(ValueError,'support-required'):adapter.prepare('exchange1',raw,**options)
        for a in (adapter,receiver):
            for w in scope['ordering']['witnesses']:a.configure(dict(version='0',purpose='ordering-exchange-support',**w,format='quorum-exchange-experiment',formatVersion='0'),time=self.time)
        wire=adapter.prepare('exchange1',raw,**options)
        with SenderWorker(self.sender) as worker:
            smtp=LocalSMTP(drop=True);self.assertEqual(worker.submit_quorum_exchange('exchange1',group=author,port=smtp.port,time=self.time)['state'],'uncertain');smtp.done();self.assertEqual(smtp.wire,wire)
            with self.assertRaisesRegex(ValueError,'Uncertain'):worker.submit_quorum_exchange('exchange1',group=author,port=1,time=self.time)
            smtp=LocalSMTP();self.assertEqual(worker.submit_quorum_exchange('exchange1',group=author,port=smtp.port,time=self.time,retry_uncertain=True)['state'],'accepted');smtp.done();self.assertEqual(smtp.wire,wire)
            with self.assertRaisesRegex(ValueError,'Already handed off'):worker.submit_quorum_exchange('exchange1',group=author,port=1,time=self.time)
        before=peer.live();self.assertEqual(receiver.receive(wire,time=self.time)['status'],'retained');self.assertEqual(receiver.receive(wire,time=self.time)['status'],'already-retained');self.assertEqual(peer.live(),before)
        store=VoteStore(self.root/'exchange-votes',scope=scope_digest(scope),keys=peer.keys(),f=0,signer=device['principal']+'|'+device['device'],key=ProviderKey(self.provider,device),create=True)
        receiver.vote(store,'prepare',digest(obj),time=self.time)
        reopened=VoteStore(self.root/'exchange-votes',scope=store.scope,keys=store.keys,f=0,signer=store.signer,key=store.key)
        self.assertEqual(reopened.retained_candidates(proof),[encode(candidate)])
        malformed=json.loads(raw);malformed['candidates']=[]
        with self.assertRaisesRegex(ValueError,'closure'):parse(encode(malformed))
        adapter.prepare('exchange2',raw,**options);adapter.db.execute('DELETE FROM qo_exchange_support WHERE identity=?',(device['identity'],))
        with SenderWorker(self.sender) as worker:
            with self.assertRaisesRegex(ValueError,'support-required'):worker.submit_quorum_exchange('exchange2',group=author,port=1,time=self.time)

        # Complete the same prepared value through real mail handoffs.
        target_w=next(w for w in scope['ordering']['witnesses'] if w['device']==device['device'])
        adapter.configure(dict(version='0',purpose='ordering-exchange-support',**target_w,format='quorum-exchange-experiment',formatVersion='0'),time=self.time)
        objects=[obj];pv=decode_event(receiver.vote(store,'prepare',digest(obj),time=self.time))['value'];objects.append(pv)
        own_store=VoteStore(self.root/'own-exchange-votes',scope=scope_digest(scope),keys=author.keys(),f=0,signer=author.device['principal']+'|'+author.device['device'],key=ProviderKey(self.provider,author.device),create=True)
        own=decode_event(author.vote(own_store,'prepare',proof,candidate,time=self.time))['value'];objects.append(own)
        prepared=sign(unsigned('prepared',scope_digest(scope),0,own_store.signer,proposal=digest(obj),prepares=sorted([digest(pv),digest(own)])),own_store.key);objects.append(prepared)
        prepared_raw=content(scope,bundle(digest(prepared),objects),[candidate]);adapter.prepare('preparedmail',prepared_raw,**options)
        smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:worker.submit_quorum_exchange('preparedmail',group=author,port=smtp.port,time=self.time)
        smtp.done();self.assertEqual(receiver.receive(smtp.wire,time=self.time)['kind'],'prepared')
        commits=[]
        for group,votes in ((peer,store),(author,own_store)):
            vote=decode_event(group.vote(votes,'commit',bundle(digest(prepared),objects),candidate,time=self.time))['value'];objects.append(vote);commits.append(digest(vote))
        decision_obj=sign(unsigned('decision',scope_digest(scope),0,own_store.signer,prepared=digest(prepared),commits=sorted(commits)),own_store.key);objects.append(decision_obj)
        decision_proof=bundle(digest(decision_obj),objects)
        decision_raw=content(scope,decision_proof,[candidate]);adapter.prepare('decisionmail',decision_raw,**options)
        smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:worker.submit_quorum_exchange('decisionmail',group=author,port=smtp.port,time=self.time)
        smtp.done();self.assertEqual(receiver.receive(smtp.wire,time=self.time)['kind'],'decision');self.assertEqual(peer.live(),before)
        # A justified higher view travels by mail; a delayed lower-view decision
        # still certifies the same exact candidate after the local minimum advances.
        reports=[]
        for votes in (store,own_store):
            report=decode_event(votes.vote('report',target=1,authority=lambda:True))['value'];objects.append(report);reports.append(digest(report))
        coordinator=self.witnesses[1];coordinator_key=ProviderKey(self.provider,coordinator);coordinator_id=coordinator['principal']+'|'+coordinator['device']
        newview=sign(unsigned('new-view',scope_digest(scope),1,coordinator_id,reports=sorted(reports)),coordinator_key);objects.append(newview)
        nextproposal=sign(unsigned('proposal',scope_digest(scope),1,coordinator_id,candidate=candidate_id(candidate),newView=digest(newview)),coordinator_key);objects.append(nextproposal)
        next_raw=content(scope,bundle(digest(nextproposal),objects),[candidate]);adapter.prepare('nextview',next_raw,**options)
        smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:worker.submit_quorum_exchange('nextview',group=author,port=smtp.port,time=self.time)
        smtp.done();self.assertEqual(receiver.receive(smtp.wire,time=self.time)['root'],digest(nextproposal))
        nextvote=decode_event(receiver.vote(store,'prepare',digest(nextproposal),time=self.time))['value']
        self.assertEqual(nextvote['body']['view'],'1');self.assertEqual(nextvote['body']['proposal'],digest(nextproposal))
        # The exchange receipt cannot install membership; final carrier checks still run.
        import ordering_carrier
        final=encode(dict(version='1',purpose='quorum-control-experiment',candidate=candidate,proof=decision_proof.hex(),applicationAssertions=[]))
        final_wire=ordering_carrier.package(final)
        for group in self.groups:ordering_carrier.receive(group,final_wire,time=self.time)
        self.assertEqual(author.live()[1]['snapshot']['predecessor'],peer.live()[1]['snapshot']['predecessor'])
        retained=json.loads(author.db.execute('SELECT state FROM qo_staged WHERE candidate=?',(candidate_id(candidate),)).fetchone()[0])
        self.assertNotIn('localStaged',retained);self.assertNotIn('checkpoint',retained)
        self.assertEqual(own_store.retained_candidates(decision_proof),[encode(candidate)])
