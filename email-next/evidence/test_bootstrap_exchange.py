"""Known own-account stores, unknown peer, actual device/assertion signatures.

Fixture KeyPackages are deliberately not MLS objects: this suite cannot establish
admission or release human content. HTTP/TLS/account facts are configured inputs.
"""
import base64
from dataclasses import replace
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import struct
import tempfile
import time
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from bootstrap_exchange import (SourceAccount,SourceObservation,RecipientSlot,BootstrapExchange,
                                authorize_source,signed,parse,handle)
from event_encoding import encode_event
from identity_store import IdentityStore
from suite_modules import offers
from test_history_transfer import identity_material


def ad(material,actor,address,*,package=b'',modules=('answers',)):
    v=dict(version='8',purpose='passive-discovery',record='1'*32,
        **{k:actor[k] for k in ['principal','device','state','binding']},mailbox=address,
        notBefore='10',notAfter='100',features=['mls-1-0001'],keyPackage=[base64.b64encode(package).decode()] if package else [],
        applications=offers(modules),orderingExchanges=[dict(format='quorum-exchange-experiment',version='2')])
    raw=encode_event(v);key=material['target']
    wrapper=dict(payload=base64.b64encode(raw).decode(),signature=key.sign(b'email-next/passive-discovery/v8\0'+struct.pack('>I',len(raw))+raw).hex(),identity=material['bundle'])
    return base64.b64encode(encode_event(wrapper)).decode()


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.source_ids=IdentityStore(Path(self.temp.name)/'source.sqlite');self.addCleanup(self.source_ids.close)
        self.target_ids=IdentityStore(Path(self.temp.name)/'target.sqlite');self.addCleanup(self.target_ids.close)
        self.a=identity_material('enp0:'+'a'*64);self.b=identity_material('enp0:'+'b'*64)
        for store,material in [(self.source_ids,self.a),(self.target_ids,self.b)]:
            self.assertEqual(store.observe(material['record'],first_contact_policy='allow-unverified')['status'],'pinned-unverified')
            self.assertEqual(store.accept_successor(encode_event(material['bundle']),candidate_digest=material['head'],time=dict(earliest='20',latest='21'))['status'],'accepted-unverified')
        self.sender=self.a['refs'][1];self.recipient=self.b['refs'][1]
        self.account=SourceAccount('sender.example','https://source.example','1'*64,'alice@sender.example',self.sender,'2'*64)
        self.slot=RecipientSlot('target-account-incarnation-link-family','bob@recipient.example',self.recipient)
        self.server=BootstrapExchange(self.target_ids,'https://destination.example','recipient.example')
        self.source_value=dict(version='0',purpose='bootstrap-source',preparation='2'*32,request='3'*32,source='4'*64,
            issuer=self.account.issuer,delegation=self.account.delegation,accountSource=self.account.account_source,
            senderMailbox=self.account.mailbox,sender=self.sender,targetMailbox=self.slot.mailbox,targetService=self.server.issuer,
            conversation='5'*32,advertisement=ad(self.a,self.sender,self.account.mailbox),nonce='6'*64,notBefore='10',notAfter='90')
        self.source=self.source_proof(self.source_value);self.prepared=encode_event(self.source_value)
        self.fetch_calls=[];self.lookups=[]
        self.exchange=self.post()['exchange'];self.server.dispatch(self.exchange,fetch=self.fetch,lookup=self.lookup)
        self.response_value=dict(version='0',purpose='bootstrap-response',response='7'*32,issuer=self.server.issuer,
            exchange=self.exchange,sourceDigest=hashlib.sha256(self.prepared).hexdigest(),nonce=self.source_value['nonce'],
            mailbox=self.slot.mailbox,device=self.recipient,advertisement=ad(self.b,self.recipient,self.slot.mailbox,package=b'NOT-A-VALID-MLS-PACKAGE'),
            relayDomain='',notBefore='20',notAfter='70')
        self.response=self.response_proof(self.response_value)

    def source_proof(self,v,key=None):return signed('source',encode_event(v),key or self.a['target'])
    def response_proof(self,v,key=None):return signed('response',encode_event(v),key or self.b['target'])

    def fetch(self,domain,issuer,source,proof):
        self.fetch_calls.append((domain,issuer,source))
        if (domain,issuer,source)!=('sender.example',self.account.issuer,self.source_value['source']):raise ValueError('Configured source location mismatch')
        return authorize_source(proof,self.account,self.source_ids,retained_preparation=self.prepared,
                                target_domain='recipient.example',target_service=self.server.issuer)

    def lookup(self,address):
        self.lookups.append(address)
        return self.slot if self.slot is not None and self.slot.mailbox==address else None

    def post(self,source=None,**kwargs):return self.server.post(source or self.source,fetch=kwargs.pop('fetch',self.fetch),**kwargs)

    def possession(self,kind='inspect',**changes):
        v=dict(version='0',purpose='bootstrap-'+kind,issuer=self.server.issuer,exchange=self.exchange,
               sourceDigest=hashlib.sha256(self.prepared).hexdigest(),nonce='8'*64,notBefore='20',notAfter='70')
        v.update(changes);return signed(kind,encode_event(v),self.a['target'])

    def inspect(self,proof=None,**kwargs):
        return self.server.inspect(proof or self.possession(),fetch=kwargs.pop('fetch',self.fetch),lookup=self.lookup,**kwargs)

    def respond(self,proof=None,**kwargs):
        return self.server.respond(proof or self.response,slot=kwargs.pop('slot',self.slot),fetch=kwargs.pop('fetch',self.fetch),**kwargs)

    def test_unknown_peer_flow_returns_signed_candidate_without_pinning_or_content_release(self):
        self.assertIsNone(self.target_ids.db.execute('SELECT digest FROM pins WHERE principal=?',(self.sender['principal'],)).fetchone())
        self.assertEqual(self.inspect()['state'],'pending')
        self.assertEqual(self.respond(),'stored-response-candidate')
        result=self.inspect();self.assertEqual(result['state'],'ready');self.assertEqual(result['responses'],[self.response])
        self.assertIsNone(self.source_ids.db.execute('SELECT digest FROM pins WHERE principal=?',(self.recipient['principal'],)).fetchone())
        self.assertIsNone(self.target_ids.db.execute('SELECT digest FROM pins WHERE principal=?',(self.sender['principal'],)).fetchone())
        self.assertNotIn('contentReleased',result)

    def test_public_post_never_consults_recipient_existence(self):
        self.lookups.clear()
        self.assertEqual(self.post(),dict(exchange=self.exchange,state='pending'))
        self.assertEqual(self.lookups,[])
        # Eligibility stays private and never changes the public response shape.
        for slot in [None,replace(self.slot,enabled=False),replace(self.slot,device_enabled=False),replace(self.slot,active=False)]:
            self.slot=slot
            self.assertEqual(self.post(),dict(exchange=self.exchange,state='pending'))
            self.assertFalse(self.server.dispatch(self.exchange,fetch=self.fetch,lookup=self.lookup))
            self.assertEqual(self.inspect()['state'],'pending')

    def test_international_and_quoted_at_mailboxes_keep_correct_provider_scope(self):
        self.account=replace(self.account,mailbox='"sender@desk"@sender.example')
        self.slot=replace(self.slot,mailbox='"用 户@desk"@recipient.example')
        self.source_value=dict(self.source_value,source='d'*64,request='e'*32,senderMailbox=self.account.mailbox,
            targetMailbox=self.slot.mailbox,advertisement=ad(self.a,self.sender,self.account.mailbox))
        self.source=self.source_proof(self.source_value);self.prepared=encode_event(self.source_value)
        self.exchange=self.post()['exchange']
        self.assertTrue(self.server.dispatch(self.exchange,fetch=self.fetch,lookup=self.lookup))
        response=dict(self.response_value,exchange=self.exchange,sourceDigest=hashlib.sha256(self.prepared).hexdigest(),
            mailbox=self.slot.mailbox,advertisement=ad(self.b,self.recipient,self.slot.mailbox,package=b'UTF8-NOT-MLS'))
        proof=self.response_proof(response);self.respond(proof)
        self.assertEqual(self.inspect()['responses'],[proof])
        self.assertTrue(all(domain=='sender.example' for domain,_,_ in self.fetch_calls))

    def test_source_mailbox_membership_is_not_a_self_signature(self):
        v=dict(self.source_value,senderMailbox='victim@sender.example',advertisement=ad(self.a,self.sender,'victim@sender.example'))
        raw=encode_event(v);p=self.source_proof(v)
        with self.assertRaises(ValueError):authorize_source(p,self.account,self.source_ids,retained_preparation=raw,target_domain='recipient.example',target_service=self.server.issuer)

    def test_wrong_source_signature_and_forged_service_observation_fail(self):
        p=self.source_proof(self.source_value,Ed25519PrivateKey.generate())
        with self.assertRaises(ValueError):self.post(p)
        for patch in [dict(domain='attacker.example'),dict(issuer='https://attacker.example'),dict(delegation='f'*64),dict(active=False)]:
            fact=SourceObservation('sender.example',self.account.issuer,self.account.delegation,self.source)
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.post(fetch=lambda *args:replace(fact,**patch))

    def test_source_expiry_and_current_account_or_device_revocation_stop_use(self):
        self.account=replace(self.account,active=False)
        with self.assertRaises(ValueError):self.inspect()
        self.account=replace(self.account,active=True)
        self.source_ids.accept_successor(encode_event(self.a['removal']),candidate_digest=self.a['removed'],time=dict(earliest='20',latest='21'))
        with self.assertRaises(ValueError):self.inspect()

    def test_copied_source_permission_cannot_read_results_without_device_signature(self):
        self.respond()
        raw,_,_=parse(self.possession(),'inspect')
        p=signed('inspect',raw,Ed25519PrivateKey.generate())
        with self.assertRaises(ValueError):self.inspect(p)
        with self.assertRaises(ValueError):self.inspect(self.source)

    def test_wrong_target_mailbox_or_service_rejected_before_exchange(self):
        for patch in [dict(targetMailbox='bob@other.example'),dict(targetService='https://attacker.example')]:
            value=dict(self.source_value,**patch);p=self.source_proof(value)
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.post(p)

    def test_response_nonce_source_digest_and_mailbox_are_bound_even_with_valid_signatures(self):
        for patch in [dict(nonce='f'*64),dict(sourceDigest='f'*64),dict(mailbox='other@recipient.example'),dict(issuer='https://other.example'),dict(relayDomain='unconfigured.example')]:
            with self.subTest(patch=patch),self.assertRaises(ValueError):self.respond(self.response_proof(dict(self.response_value,**patch)))
        self.assertEqual(self.inspect()['state'],'pending')

    def test_foreign_account_and_wrong_recipient_key_cannot_respond(self):
        with self.assertRaises(ValueError):self.respond(slot=replace(self.slot,account='another-account'))
        with self.assertRaises(ValueError):self.respond(self.response_proof(self.response_value,self.a['target']))
        with self.assertRaises(ValueError):self.respond(slot=replace(self.slot,active=False))

    def test_invalid_proof_cannot_poison_exact_response_identity(self):
        with self.assertRaises(ValueError):self.respond(self.response_proof(self.response_value,Ed25519PrivateKey.generate()))
        self.assertEqual(self.respond(),'stored-response-candidate')
        self.assertEqual(self.respond(),'duplicate-response')
        with self.assertRaises(ValueError):self.respond(self.response_proof(dict(self.response_value,response='9'*32)))

    def test_known_recipient_revocation_or_optout_holds_new_disclosure(self):
        self.respond();self.slot=replace(self.slot,enabled=False)
        self.assertEqual(self.inspect()['state'],'pending')
        self.slot=replace(self.slot,enabled=True)
        self.target_ids.accept_successor(encode_event(self.b['removal']),candidate_digest=self.b['removed'],time=dict(earliest='20',latest='21'))
        self.assertEqual(self.inspect()['state'],'pending')

    def test_stale_response_time_never_becomes_ready_again(self):
        self.respond()
        self.assertEqual(self.inspect(self.possession(notBefore='71',notAfter='80'),time=(71,72))['state'],'pending')

    def test_terminal_cancel_does_not_reopen_on_post_retry(self):
        self.respond();self.server.cancel(self.possession('cancel'),fetch=self.fetch)
        self.assertEqual(self.inspect()['state'],'pending')
        self.assertEqual(self.post()['state'],'pending')
        with self.assertRaises(ValueError):self.respond()
        self.assertEqual(self.inspect()['responses'],[])

    def test_deadline_is_fixed_and_unknown_time_does_not_refresh(self):
        for after in ['611','18446744073709551616']:
            with self.assertRaises(ValueError):self.source_proof(dict(self.source_value,notAfter=after))
        with self.assertRaises(ValueError):self.inspect(time=(90,91))
        with self.assertRaises(ValueError):self.inspect(self.possession(notAfter='91'))

    def test_unknown_or_rolled_back_clock_does_not_release_candidates(self):
        self.respond()
        for time in [None,(21,20),(True,21),(-1,21)]:
            with self.subTest(time=time),self.assertRaises(ValueError):self.inspect(time=time)

    def test_changed_connected_relay_does_not_relabel_old_signed_response(self):
        self.respond();self.slot=replace(self.slot,relay_domain='new-relay.example')
        self.assertEqual(self.inspect()['state'],'pending')

    def test_new_exchange_cannot_reuse_disclosed_package(self):
        self.respond()
        self.source_value=dict(self.source_value,source='e'*64,request='a'*32,nonce='b'*64)
        self.source=self.source_proof(self.source_value);self.prepared=encode_event(self.source_value)
        exchange=self.post()['exchange'];self.server.dispatch(exchange,fetch=self.fetch,lookup=self.lookup)
        response=dict(self.response_value,exchange=exchange,sourceDigest=hashlib.sha256(self.prepared).hexdigest(),nonce=self.source_value['nonce'])
        with self.assertRaisesRegex(ValueError,'cannot be reallocated'):self.respond(self.response_proof(response))

    def test_response_and_package_reservation_rollback_together(self):
        def fail(stage):raise RuntimeError(stage)
        with self.assertRaises(RuntimeError):self.respond(crash=fail)
        self.assertEqual(self.inspect()['state'],'pending')
        self.assertEqual(self.target_ids.db.execute('SELECT count(*) FROM bootstrap_package').fetchone()[0],0)
        self.assertEqual(self.respond(),'stored-response-candidate')

    def test_own_account_block_hides_existing_result_and_suppresses_new_request(self):
        self.respond();self.server.block(self.slot,self.exchange)
        self.assertEqual(self.inspect()['state'],'pending')
        self.source_value=dict(self.source_value,source='e'*64,request='a'*32,nonce='b'*64)
        self.source=self.source_proof(self.source_value);self.prepared=encode_event(self.source_value)
        exchange=self.post()['exchange']
        self.assertFalse(self.server.dispatch(exchange,fetch=self.fetch,lookup=self.lookup))

    def test_other_account_cannot_block_source_of_this_private_exchange(self):
        with self.assertRaises(ValueError):self.server.block(replace(self.slot,account='other'),self.exchange)
        self.assertEqual(self.respond(),'stored-response-candidate')
        self.assertEqual(self.inspect()['state'],'ready')

    def test_no_extra_human_content_fields_or_digest_enter_request_schema(self):
        for extra in ['subject','body','attachments','contentDigest','replyText']:
            with self.subTest(extra=extra),self.assertRaises(ValueError):self.source_proof(dict(self.source_value,**{extra:'PRIVATE-HUMAN-CONTENT'}))
        raw,_,_=parse(self.source,'source')
        self.assertNotIn(b'PRIVATE-HUMAN-CONTENT',raw)

    def test_malformed_advertisement_cannot_be_called_setup(self):
        for value in ['e30=','not-base64']:
            with self.assertRaises(ValueError):
                response=self.response_proof(dict(self.response_value,advertisement=value));self.respond(response)

    def test_inspection_and_cancel_purpose_do_not_mix(self):
        with self.assertRaises(ValueError):self.inspect(self.possession('cancel'))
        with self.assertRaises(ValueError):self.server.cancel(self.possession(),fetch=self.fetch)

    def test_invalid_source_proof_never_creates_an_exchange_collision(self):
        v=dict(self.source_value,source='e'*64,request='f'*32)
        good=self.source_proof(v);bad=self.source_proof(v,Ed25519PrivateKey.generate())
        self.source_value=v;self.source=good;self.prepared=encode_event(v)
        with self.assertRaises(ValueError):self.post(bad)
        result=self.post(good)
        self.assertEqual(result,dict(exchange=handle(v),state='pending'))

    def test_response_retry_after_restart_preserves_original_bytes(self):
        self.respond();path=Path(self.temp.name)/'target.sqlite'
        self.target_ids.close();self.target_ids=IdentityStore(path)
        self.addCleanup(self.target_ids.close)
        self.server=BootstrapExchange(self.target_ids,self.server.issuer,self.server.domain)
        self.assertEqual(self.respond(),'duplicate-response');self.assertEqual(self.inspect()['responses'],[self.response])


    def publication(self,*,identifier='a'*32,package=b'OFFLINE-NOT-A-VALID-MLS-PACKAGE',**changes):
        value=dict(version='0',purpose='bootstrap-publication',publication=identifier,issuer=self.server.issuer,
                   mailbox=self.slot.mailbox,device=self.recipient,
                   advertisement=ad(self.b,self.recipient,self.slot.mailbox,package=package),relayDomain='',
                   scope='automatic-first-contact',notBefore='20',notAfter='70')
        value.update(changes)
        return signed('publication',encode_event(value),self.b['target'])

    def next_exchange(self):
        self.source_value=dict(self.source_value,source='e'*64,request='f'*32,nonce='c'*64)
        self.source=self.source_proof(self.source_value);self.prepared=encode_event(self.source_value)
        self.exchange=self.post()['exchange']
        self.assertTrue(self.server.dispatch(self.exchange,fetch=self.fetch,lookup=self.lookup))

    def test_offline_publication_is_not_fabricated_as_a_fresh_response(self):
        publication=self.publication();self.assertEqual(self.server.publish(publication,slot=self.slot),'stored-publication-candidate')
        result=self.inspect()
        self.assertEqual((result['state'],result['responses'],result['publications']),('ready',[],[publication]))
        self.assertEqual(self.target_ids.db.execute('SELECT count(*) FROM bootstrap_response').fetchone()[0],0)
        self.assertIsNone(self.source_ids.db.execute('SELECT digest FROM pins WHERE principal=?',(self.recipient['principal'],)).fetchone())
        self.assertNotIn('contentReleased',result)

    def test_public_post_and_wrong_possession_do_not_allocate_offline_material(self):
        self.server.publish(self.publication(),slot=self.slot);self.post()
        v=dict(version='0',purpose='bootstrap-inspect',issuer=self.server.issuer,exchange=self.exchange,
               sourceDigest=hashlib.sha256(self.prepared).hexdigest(),nonce='8'*64,notBefore='20',notAfter='70')
        bad=signed('inspect',encode_event(v),Ed25519PrivateKey.generate())
        with self.assertRaises(ValueError):self.inspect(bad)
        self.assertEqual(self.target_ids.db.execute('SELECT count(*) FROM bootstrap_allocation').fetchone()[0],0)
        self.assertEqual(self.inspect()['state'],'ready')

    def test_publication_signature_scope_and_validity_are_checked_before_storage(self):
        proof=self.publication();raw,v,_=parse(proof,'publication')
        for change in [dict(mailbox='other@recipient.example'),dict(issuer='https://other.example'),dict(relayDomain='other.example'),dict(notAfter='101')]:
            with self.subTest(change=change),self.assertRaises(ValueError):
                self.server.publish(self.publication(**change),slot=self.slot)
        with self.assertRaises(ValueError):self.server.publish(signed('publication',raw,Ed25519PrivateKey.generate()),slot=self.slot)
        for change in [dict(scope='mailbox-directory'),dict(notAfter='19')]:
            with self.subTest(change=change),self.assertRaises(ValueError):self.publication(**change)
        self.assertEqual(self.target_ids.db.execute('SELECT count(*) FROM bootstrap_publication').fetchone()[0],0)
        self.assertEqual(self.server.publish(proof,slot=self.slot),'stored-publication-candidate')

    def test_longer_publication_is_syntax_valid_but_cannot_extend_underlying_authority(self):
        proof=self.publication(notAfter='1209620')
        self.assertEqual(parse(proof,'publication')[1]['notAfter'],'1209620')
        with self.assertRaises(ValueError):self.server.publish(proof,slot=self.slot)
        self.assertEqual(self.target_ids.db.execute('SELECT count(*) FROM bootstrap_publication').fetchone()[0],0)

    def test_invalid_publication_cannot_poison_id_and_valid_conflict_cannot_replace_bytes(self):
        proof=self.publication();raw,_,_=parse(proof,'publication')
        with self.assertRaises(ValueError):self.server.publish(signed('publication',raw,Ed25519PrivateKey.generate()),slot=self.slot)
        self.server.publish(proof,slot=self.slot)
        self.assertEqual(self.server.publish(proof,slot=self.slot),'duplicate-publication')
        with self.assertRaisesRegex(ValueError,'conflict'):self.server.publish(self.publication(package=b'DIFFERENT'),slot=self.slot)
        self.assertEqual(self.inspect()['publications'],[proof])

    def test_exact_allocation_survives_retry_and_reopening(self):
        proof=self.publication(identifier='b'*32);self.server.publish(proof,slot=self.slot)
        result=self.inspect()
        # A newly uploaded earlier-sorting publication cannot replace this allocation.
        self.server.publish(self.publication(identifier='a'*32,package=b'ANOTHER'),slot=self.slot)
        other=IdentityStore(Path(self.temp.name)/'target.sqlite');self.addCleanup(other.close)
        reopened=BootstrapExchange(other,self.server.issuer,self.server.domain)
        self.assertEqual(reopened.inspect(self.possession(),fetch=self.fetch,lookup=self.lookup),result)
        self.assertEqual(self.inspect(),result)
        self.assertEqual(self.target_ids.db.execute('SELECT count(*) FROM bootstrap_allocation').fetchone()[0],1)

    def test_two_exchange_connections_cannot_reallocate_one_published_package(self):
        self.server.publish(self.publication(),slot=self.slot);self.assertEqual(self.inspect()['state'],'ready')
        self.next_exchange()
        # A second publication of identical package bytes does not make it unused.
        self.server.publish(self.publication(identifier='b'*32),slot=self.slot)
        other=IdentityStore(Path(self.temp.name)/'target.sqlite');self.addCleanup(other.close)
        reopened=BootstrapExchange(other,self.server.issuer,self.server.domain)
        self.assertEqual(reopened.inspect(self.possession(),fetch=self.fetch,lookup=self.lookup)['state'],'pending')
        fresh=self.publication(identifier='c'*32,package=b'NEW-PACKAGE')
        self.server.publish(fresh,slot=self.slot)
        self.assertEqual(reopened.inspect(self.possession(),fetch=self.fetch,lookup=self.lookup)['publications'],[fresh])

    def test_simultaneous_processes_allocate_one_package_to_only_one_exchange(self):
        self.server.publish(self.publication(),slot=self.slot)
        first=dict(source=self.source,proof=self.possession())
        self.next_exchange();second=dict(source=self.source,proof=self.possession())
        gate=Path(self.temp.name)/'start-allocation'
        script="""
import json,sys,time
from pathlib import Path
from identity_store import IdentityStore
from bootstrap_exchange import BootstrapExchange,RecipientSlot,SourceObservation
v=json.load(open(sys.argv[1]));store=IdentityStore(v['database'])
s=BootstrapExchange(store,v['issuer'],v['domain']);slot=RecipientSlot(v['account'],v['mailbox'],v['device'])
Path(v['ready']).touch()
deadline=time.monotonic()+5
while not Path(v['gate']).exists():
    if time.monotonic()>deadline:raise RuntimeError('Allocation test start gate timed out')
    time.sleep(.01)
result=s.inspect(v['proof'],fetch=lambda *args:SourceObservation('sender.example','https://source.example','1'*64,v['source']),lookup=lambda address:slot)
print(json.dumps(result));store.close()
"""
        processes=[]
        try:
            for index,intent in enumerate([first,second]):
                request=Path(self.temp.name)/('race-'+str(index)+'.json')
                request.write_text(json.dumps(dict(database=str(Path(self.temp.name)/'target.sqlite'),issuer=self.server.issuer,
                    domain=self.server.domain,account=self.slot.account,mailbox=self.slot.mailbox,
                    device=self.slot.device,gate=str(gate),ready=str(Path(self.temp.name)/('ready-'+str(index))),**intent)))
                processes.append(subprocess.Popen([sys.executable,'-c',script,str(request)],cwd=Path(__file__).parent,
                                                  stdout=subprocess.PIPE,stderr=subprocess.PIPE))
            deadline=time.monotonic()+5
            while not all((Path(self.temp.name)/('ready-'+str(i))).exists() for i in range(2)):
                if time.monotonic()>deadline:raise RuntimeError('Allocation processes did not reach start gate')
                time.sleep(.01)
            gate.touch();states=[]
            for process in processes:
                output,error=process.communicate(timeout=15)
                self.assertEqual(process.returncode,0,error.decode());states.append(json.loads(output)['state'])
            self.assertEqual(sorted(states),['pending','ready'])
            self.assertEqual(self.target_ids.db.execute('SELECT count(*) FROM bootstrap_allocation').fetchone()[0],1)
            self.assertEqual(self.target_ids.db.execute('SELECT count(*) FROM bootstrap_package').fetchone()[0],1)
        finally:
            for process in processes:
                if process.poll() is None:process.kill()
                process.communicate()

    def test_withdrawal_stops_disclosure_without_recycling_or_retry_reactivation(self):
        proof=self.publication();self.server.publish(proof,slot=self.slot);self.inspect()
        self.server.withdraw('a'*32,slot=self.slot)
        self.assertEqual(self.server.publish(proof,slot=self.slot),'duplicate-withdrawn-publication')
        self.server.publish(self.publication(identifier='b'*32,package=b'NEW-PACKAGE'),slot=self.slot)
        self.assertEqual(self.inspect()['state'],'pending')
        self.assertEqual(self.target_ids.db.execute('SELECT count(*) FROM bootstrap_package').fetchone()[0],1)
        self.next_exchange()
        self.assertEqual(parse(self.inspect()['publications'][0],'publication')[1]['publication'],'b'*32)

    def test_foreign_account_cannot_withdraw_another_accounts_publication(self):
        self.server.publish(self.publication(),slot=self.slot)
        self.server.withdraw('a'*32,slot=replace(self.slot,account='another-account'))
        self.assertEqual(self.inspect()['state'],'ready')

    def test_cancelled_exchange_keeps_disclosed_offline_package_reserved(self):
        self.server.publish(self.publication(),slot=self.slot);self.inspect()
        self.server.cancel(self.possession('cancel'),fetch=self.fetch)
        self.assertEqual(self.inspect()['state'],'pending')
        self.next_exchange();self.assertEqual(self.inspect()['state'],'pending')
        self.assertEqual(self.target_ids.db.execute('SELECT count(*) FROM bootstrap_package').fetchone()[0],1)

    def test_current_policy_identity_or_relay_change_suppresses_offline_disclosure(self):
        self.server.publish(self.publication(),slot=self.slot)
        original=self.slot
        for patch in [dict(enabled=False),dict(device_enabled=False),dict(active=False),dict(relay_domain='relay.example'),dict(account='new-incarnation')]:
            with self.subTest(patch=patch):
                self.slot=replace(original,**patch);self.assertEqual(self.inspect()['state'],'pending')
        self.slot=original
        self.assertEqual(self.inspect()['state'],'ready')
        self.assertEqual(self.target_ids.accept_successor(encode_event(self.b['removal']),candidate_digest=self.b['removed'],time=dict(earliest='20',latest='21'))['status'],'accepted-unverified')
        self.assertEqual(self.inspect()['state'],'pending')

    def test_expired_allocated_publication_does_not_switch_to_another_on_retry(self):
        proof=self.publication(notAfter='30');self.server.publish(proof,slot=self.slot);self.inspect()
        self.server.publish(self.publication(identifier='b'*32,package=b'NEW-PACKAGE'),slot=self.slot)
        self.assertEqual(self.inspect(time=(31,32))['state'],'pending')
        self.next_exchange()
        result=self.inspect(time=(31,32));self.assertEqual(result['state'],'ready')
        self.assertEqual(parse(result['publications'][0],'publication')[1]['publication'],'b'*32)

    def test_fresh_response_preferred_without_allocating_an_unused_publication(self):
        self.server.publish(self.publication(),slot=self.slot);self.respond()
        result=self.inspect();self.assertEqual(result['responses'],[self.response]);self.assertEqual(result['publications'],[])
        self.assertEqual(self.target_ids.db.execute('SELECT count(*) FROM bootstrap_allocation').fetchone()[0],0)

    def test_fresh_response_and_publication_share_package_single_allocation_ledger(self):
        self.server.publish(self.publication(package=b'NOT-A-VALID-MLS-PACKAGE'),slot=self.slot)
        self.inspect();self.next_exchange()
        response=dict(self.response_value,exchange=self.exchange,sourceDigest=hashlib.sha256(self.prepared).hexdigest(),nonce=self.source_value['nonce'])
        with self.assertRaisesRegex(ValueError,'cannot be reallocated'):self.respond(self.response_proof(response))

    def test_blocked_source_cannot_allocate_offline_material(self):
        self.server.publish(self.publication(),slot=self.slot);self.server.block(self.slot,self.exchange)
        self.assertEqual(self.inspect()['state'],'pending')
        self.assertEqual(self.target_ids.db.execute('SELECT count(*) FROM bootstrap_allocation').fetchone()[0],0)

    def test_allocation_and_package_reservation_roll_back_together(self):
        self.server.publish(self.publication(),slot=self.slot)
        def fail(stage):raise RuntimeError(stage)
        with self.assertRaisesRegex(RuntimeError,'before-allocation-commit'):self.inspect(crash=fail)
        for table in ['bootstrap_allocation','bootstrap_package']:
            self.assertEqual(self.target_ids.db.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
        self.assertEqual(self.inspect()['state'],'ready')

    def test_process_exit_before_allocation_commit_leaves_no_exposed_reservation(self):
        self.server.publish(self.publication(),slot=self.slot)
        request=Path(self.temp.name)/'allocation.json'
        request.write_text(json.dumps(dict(database=str(Path(self.temp.name)/'target.sqlite'),issuer=self.server.issuer,
            domain=self.server.domain,source=self.source,account=self.slot.account,mailbox=self.slot.mailbox,
            device=self.slot.device,proof=self.possession())))
        script="""
import json,os,sys
from identity_store import IdentityStore
from bootstrap_exchange import BootstrapExchange,RecipientSlot,SourceObservation
v=json.load(open(sys.argv[1]));store=IdentityStore(v['database'])
s=BootstrapExchange(store,v['issuer'],v['domain']);slot=RecipientSlot(v['account'],v['mailbox'],v['device'])
s.inspect(v['proof'],fetch=lambda *args:SourceObservation('sender.example','https://source.example','1'*64,v['source']),
    lookup=lambda address:slot,crash=lambda stage:os._exit(91))
"""
        result=subprocess.run([sys.executable,'-c',script,str(request)],cwd=Path(__file__).parent,
                              stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        self.assertEqual(result.returncode,91,result.stderr.decode())
        for table in ['bootstrap_allocation','bootstrap_package']:
            self.assertEqual(self.target_ids.db.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
        self.assertEqual(self.inspect()['state'],'ready')


if __name__=='__main__':unittest.main()
