"""Validated inline proposals hold old-epoch application preparation and release."""
import json,unittest
from unittest.mock import patch
import test_admitted_quorum as admitted
from ordering_mls import ProviderKey
from event_encoding import encode_event
from sender_worker import SenderWorker

class ProposalObservationTests(unittest.TestCase):
    setUp=admitted.AdmittedQuorumTests.setUp;tearDown=admitted.AdmittedQuorumTests.tearDown
    endpoint=admitted.AdmittedQuorumTests.endpoint;prepare=admitted.AdmittedQuorumTests.prepare
    join=admitted.AdmittedQuorumTests.join;event=admitted.AdmittedQuorumTests.event
    send=admitted.AdmittedQuorumTests.send;certify=admitted.AdmittedQuorumTests.certify
    def prepare_application(self,d,ident,application=None):
        source=next(c['mailbox'] for x,c in zip(self.f.devices,self.selected) if x is d)
        destinations=sorted({c['mailbox'] for x,c in zip(self.f.devices,self.selected) if x is not d and x is not self.removed})
        return self.senders[d['device']].prepare(ident,application if application is not None else encode_event(self.event(d,'a')),key=d['key'],envelope_sender=source,recipients=destinations,time=self.time)
    def test_validated_removal_holds_local_peer_and_prepared_dispatch(self):
        self.join();author=self.author_group;peer=next(g for g in self.groups if g is not author)
        self.prepare_application(self.f.creator,'beforeproposal')
        from plaintext_release import PlaintextRelease
        readable=PlaintextRelease(self.sender)
        copied=self.event(self.f.creator,'b');copied['disclosures']=[{'kind':'plaintext-email'}];application=encode_event(copied)
        readable.authorize(application,['copy@example.invalid'])
        self.prepare_application(self.f.creator,'boundcopy',application)
        readable.prepare('ordinarycopy','boundcopy')
        index=next(m['index'] for m in author.live()[1]['snapshot']['members'] if m['identity']==self.removed['identity'])
        import sqlite3
        author.db.execute("CREATE TEMP TRIGGER fail_observation BEFORE INSERT ON qo_proposal_observation BEGIN SELECT RAISE(ABORT,'observation retention failure'); END")
        with self.assertRaisesRegex(sqlite3.IntegrityError,'observation retention failure'):author.stage(ProviderKey(self.provider,self.f.creator),time=self.time,removals=[int(index)])
        self.assertEqual(author.db.execute('SELECT count(*) FROM qo_proposal_observation').fetchone()[0],0)
        author.db.execute('DROP TRIGGER fail_observation')
        self.prepare_application(self.f.creator,'beforeproposal')
        observed=[]
        def observe_after_release(point):
            if point=='after-release':observed.append(author.stage(ProviderKey(self.provider,self.f.creator),time=self.time,removals=[int(index)]))
        with patch('sender_worker.smtplib.SMTP') as smtp:
            smtp.return_value.mail.return_value=(250,b'ok');smtp.return_value.rcpt.return_value=(250,b'ok')
            with SenderWorker(self.sender) as worker:
                outcome=worker.submit('beforeproposal',port=9,time=self.time,crash=observe_after_release)
            self.assertEqual(outcome['state'],'aborted-before-data')
            smtp.return_value.data.assert_not_called()
        candidate=observed[0]
        with self.assertRaisesRegex(ValueError,'Observed proposals'):self.prepare_application(self.f.creator,'heldlocal')
        with self.assertRaisesRegex(ValueError,'Observed proposals'):readable.prepare('anothercopy','boundcopy')
        with patch('sender_worker.smtplib.SMTP') as smtp:
            with SenderWorker(self.sender) as worker:
                with self.assertRaisesRegex(ValueError,'Observed proposals'):worker.submit_plaintext('ordinarycopy',port=9,time=self.time)
            smtp.assert_not_called()
        with patch('sender_worker.smtplib.SMTP') as smtp:
            with SenderWorker(self.sender) as worker:
                with self.assertRaisesRegex(ValueError,'Observed proposals'):worker.submit('beforeproposal',port=9,time=self.time)
            smtp.assert_not_called()
        # A signed ordering wrapper can be retained without MLS/application
        # candidate inspection. Receipt alone must not create a send barrier.
        from quorum_exchange import QuorumExchange,content,mime_package
        from ordering_certificates import unsigned,sign,digest,bundle
        from ordering_scope import scope_digest
        from ordering_mls import candidate_id
        coordinator=self.witnesses[0];scope=candidate['plan']['scope']
        proposal=sign(unsigned('proposal',scope_digest(scope),0,coordinator['principal']+'|'+coordinator['device'],candidate=candidate_id(candidate),newView=''),ProviderKey(self.provider,coordinator))
        exchange=QuorumExchange(self.senders[peer.device['device']],peer)
        wrappers=None
        if getattr(self,'exchange_assertion_version','6')=='7':
            from quorum_exchange_support import current
            wrappers=current(author,time=self.time)
        else:
            witness=next(w for w in scope['ordering']['witnesses'] if w['device']==peer.device['device'])
            exchange.configure(dict(witness,version='0',purpose='ordering-exchange-support',format='quorum-exchange-experiment',formatVersion='0'),time=self.time)
        raw=content(scope,bundle(digest(proposal),[proposal]),[candidate],witness_assertions=wrappers)
        self.assertEqual(exchange.receive(mime_package(raw),time=self.time)['status'],'retained')
        self.prepare_application(peer.device,'rawdoesnothold')
        bad=json.loads(json.dumps(candidate));bad['approval']['signature']='00'*64
        with self.assertRaises(ValueError):peer.inspect_candidate(bad,time=self.time)
        self.prepare_application(peer.device,'invaliddoesnothold')
        peer.db.execute("CREATE TEMP TRIGGER fail_observation BEFORE INSERT ON qo_proposal_observation BEGIN SELECT RAISE(ABORT,'observation retention failure'); END")
        with self.assertRaisesRegex(sqlite3.IntegrityError,'observation retention failure'):peer.inspect_candidate(candidate,time=self.time)
        peer.db.execute('DROP TRIGGER fail_observation')
        self.prepare_application(peer.device,'invaliddoesnothold')
        peer.inspect_candidate(candidate,time=self.time)
        with self.assertRaisesRegex(ValueError,'Observed proposals'):self.prepare_application(peer.device,'heldpeer')
        from admitted_quorum import AdmittedQuorum
        reopened=AdmittedQuorum(self.sender.receiver,self.worker,self.f.creator)
        with self.assertRaisesRegex(ValueError,'Observed proposals'):self.prepare_application(self.f.creator,'heldrestart')
        proof=self.certify(candidate)
        decision=author.install(candidate,proof,time=self.time)
        import ordering_carrier
        from smtp_loopback import roundtrip
        wire=roundtrip(ordering_carrier.package(author.release(decision,time=self.time)))
        for g in self.groups:
            if g is not author:self.assertEqual(ordering_carrier.receive(g,wire,time=self.time)['decision'],decision)
        with patch('sender_worker.smtplib.SMTP') as smtp:
            with SenderWorker(self.sender) as worker:
                with self.assertRaisesRegex(ValueError,'Changed group metadata'):worker.submit('beforeproposal',port=9,time=self.time)
            smtp.assert_not_called()
        self.send(self.f.creator,'c');self.send(peer.device,'d')

    def test_addition_mixed_context_proposals_hold_and_legacy_fails_closed(self):
        self.join();author=self.author_group
        from provider_mls import make_device,advertisement,sign
        from quorum_join_support import confirm
        import base64
        new=make_device(self.provider,7,8)
        for identity in self.stores:identity.observe(new['record'],first_contact_policy='allow-unverified')
        wrapper=advertisement(self.provider,new,'newjoiner@example.invalid');value=json.loads(base64.b64decode(wrapper['payload']))
        value.update(version='6',applications=[dict(self.f.context['application'],ordering='endpoint-quorum-v0')]);raw=encode_event(value)
        wrapper.update(payload=base64.b64encode(raw).decode(),signature=sign(self.provider,new,'email-next/passive-discovery/v6',raw))
        for group in self.groups:confirm(group,encode_event(wrapper),time=self.time)
        candidate=author.stage(ProviderKey(self.provider,self.f.creator),time=self.time,packages=[new['package']])
        self.assertEqual(author.db.execute('SELECT proposal_count FROM qo_proposal_observation').fetchone()[0],1)
        peer=next(g for g in self.groups if g is not author)
        peer.inspect_candidate(candidate,time=self.time)
        with self.assertRaisesRegex(ValueError,'Observed proposals'):self.prepare_application(peer.device,'addheld')
        index=next(m['index'] for m in author.live()[1]['snapshot']['members'] if m['identity']==self.removed['identity'])
        author.stage(ProviderKey(self.provider,self.f.creator),time=self.time,packages=[new['package']],removals=[int(index)])
        self.assertEqual(sorted(r[0] for r in author.db.execute('SELECT proposal_count FROM qo_proposal_observation')),[1,2])
        changed=json.loads(json.dumps(self.f.context));changed['ordering']['generation']='1'
        peer.stage(ProviderKey(self.provider,self.f.creator),time=self.time,new_context=changed)
        self.assertEqual([r[0] for r in peer.db.execute('SELECT proposal_count FROM qo_proposal_observation')],[1,1])
        # Local private retention predating the observation provenance is unsafe
        # even if a legacy caller supplies a forged zero-count JSON hint.
        row=author.db.execute('SELECT candidate,state FROM qo_staged').fetchone();legacy=json.loads(row[1]);legacy.pop('proposalObservation');legacy['proposalCount']=0
        author.db.execute('UPDATE qo_staged SET state=? WHERE candidate=?',(json.dumps(legacy).encode(),row[0]))
        with self.assertRaisesRegex(ValueError,'fresh admission'):self.prepare_application(self.f.creator,'legacyheld')

import test_quorum_signed_exchange as signed_tests

class SignedProposalObservationTests(unittest.TestCase):
    exchange_assertion_version='7'
    setUp=signed_tests.SignedExchangeTests.setUp
    tearDown=ProposalObservationTests.tearDown;endpoint=ProposalObservationTests.endpoint;prepare=ProposalObservationTests.prepare
    join=ProposalObservationTests.join;event=ProposalObservationTests.event;send=ProposalObservationTests.send;certify=ProposalObservationTests.certify
    prepare_application=ProposalObservationTests.prepare_application
    test_signed_carrier_proposal_boundary=ProposalObservationTests.test_validated_removal_holds_local_peer_and_prepared_dispatch

if __name__=='__main__':unittest.main()
