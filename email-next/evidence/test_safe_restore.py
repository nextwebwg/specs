import base64,hashlib,json,sqlite3,unittest
from contextlib import closing
from unittest.mock import patch
import test_remote_pairing as pairing_fixture
from safe_restore import RestoreWorkspace
from remote_pairing import Pairing,commitment,decode_offer
from own_devices import OwnDevices,PublicSpool
from event_encoding import encode_event
from provider_mls import advertisement,sign

class SafeRestore(unittest.TestCase):
    def setUp(self):
        self.f=pairing_fixture.RemotePairing();self.f.setUp();self.addCleanup(self.f.tearDown);self.addCleanup(self.f.doCleanups)
        self.f.test_actual_protected_delivery_after_remote_pairing()
        self.root=self.f.root;self.binary=self.f.binary;self.time=self.f.time
        self.source=self.root/'backup.sqlite'
        with closing(sqlite3.connect(self.source)) as db:self.f.stores[0].db.backup(db)
        self.workspace=RestoreWorkspace(self.root/'restored',create=True);self.addCleanup(self.workspace.close)
    def test_real_snapshot_is_history_only(self):
        with closing(sqlite3.connect(self.source)) as db:
            self.assertGreater(db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0],0)
            self.assertGreater(db.execute('SELECT count(*) FROM sender_prepared').fetchone()[0],0)
        from test_signed_ordering import Fixture
        from ordering_store import VoteStore
        f=Fixture();vote_path=self.source;voter=VoteStore(vote_path,scope=f.scope,keys=f.keys,f=1,signer='0',key=f.private['0'],create=True)
        voter.vote('prepare',f.proof(f.proposal()),authority=lambda:True)
        result=self.workspace.import_history(self.source);self.assertGreater(result['records'],0);self.assertEqual(self.workspace.import_history(self.source),result)
        self.assertTrue(all(not row['actions'] for row in self.workspace.view()))
        tables={r[0] for r in self.workspace.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertFalse(tables & {'mls_checkpoint','sender_prepared','votes','contributions','own_approval'})
        with patch('provider_mls.call',side_effect=AssertionError('No restored crypto')):
            with self.assertRaises(ValueError):self.workspace.sender(self.binary,time=self.time)
            with self.assertRaises(ValueError):self.workspace.voter(vote_path)
        with closing(sqlite3.connect(self.source)) as db:self.assertEqual(db.execute('SELECT count(*) FROM votes').fetchone()[0],1)
    def test_views_virtual_tables_budgets_and_rollback(self):
        for name,sql in [('view','CREATE VIEW contributions AS SELECT 1 AS octets'),('virtual','CREATE VIRTUAL TABLE contributions USING fts5(octets)')]:
            source=self.root/(name+'.sqlite')
            with closing(sqlite3.connect(source)) as db:db.execute(sql);db.commit()
            with self.assertRaisesRegex(ValueError,'views/virtual'):self.workspace.import_history(source)
        with self.assertRaises(RuntimeError):self.workspace.import_history(self.source,crash=lambda _:(_ for _ in ()).throw(RuntimeError('crash')))
        self.assertEqual(self.workspace.view(),[])
        self.workspace.limits=(1,1,1,10)
        with self.assertRaises(ValueError):self.workspace.import_history(self.source)
        self.assertEqual(self.workspace.view(),[])
    def test_activation_crash_and_reopen_keep_archive_separate(self):
        before=hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.workspace.import_history(self.source)
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(),before)
        fresh=self.workspace.start_fresh(self.binary)
        time=dict.fromkeys(('earliest','latest'),str(fresh['time']))
        with self.assertRaises(RuntimeError):
            self.workspace.activate_new_identity(time=time,crash=lambda _:(_ for _ in ()).throw(RuntimeError('crash')))
        self.assertEqual(self.workspace.status(),'needs-reconnect')
        self.assertIsNone(self.workspace.identity.current_state(fresh['principal'])['head'])
        with self.assertRaises(ValueError):self.workspace.sender(self.binary,time=time)
        self.workspace.activate_new_identity(time=time)
        reopened=RestoreWorkspace(self.workspace.path);self.addCleanup(reopened.close)
        self.assertEqual(reopened.status(),'new-identity-needs-contact-approval')
        self.assertEqual(reopened.view(),self.workspace.view())

    def paired(self):
        self.workspace.import_history(self.source);fresh=self.workspace.start_fresh(self.binary,principal=self.f.a['principal'])
        self.assertNotEqual(fresh['key'],self.f.a['key']);self.assertNotEqual(fresh['key'],self.f.b['key'])
        time=dict.fromkeys(('earliest','latest'),str(max(int(self.time['latest']),fresh['time'])));self.time=time
        head=self.f.stores[0].current_state(self.f.a['principal'])['head'];anchor=self.f.stores[0].db.execute('SELECT bundle FROM identity_transitions WHERE digest=?',(head,)).fetchone()[0]
        old=Pairing(self.f.stores[0],account='local-account');new=Pairing(self.workspace.identity,account='local-account');now=int(time['latest'])
        offer=old.offer(self.f.owner,anchor,roles=['receive','send'],session_before=str(now),session_after=str(now+60),grant_before=str(now),grant_after=str(now+600),time=time);session=decode_offer(offer)['session']
        new.confirm_offer(offer,anchor,comparison=commitment('offer',offer),channel='independent-qr',time=time)
        request=new.request(session,fresh,binary=self.binary,time=time)
        result=old.commit(session,request,owner=self.f.owner,device=self.f.a,binary=self.binary,comparison=commitment('request',request),channel='independent-qr',time=time)
        with self.assertRaises(ValueError):self.workspace.activate_pairing(new,session,time=time)
        new.accept(session,result,time=time);self.workspace.activate_pairing(new,session,time=time)
        return fresh,json.loads(base64.b64decode(json.loads(result)['bundle'])),json.loads(result)['head']
    def test_participating_restore_device_cannot_enroll_or_reactivate_history(self):
        # Actual enrolled send/receive credentials are not administrator credentials.
        fresh,bundle,head=self.paired()
        owner=OwnDevices(self.workspace.identity,account='local-account',
                         principal=fresh['principal'],local_device=fresh['device'],
                         mailboxes=[self.f.mailbox])
        pairing=Pairing(self.workspace.identity,account='local-account')
        before=self.workspace.identity.db.execute('SELECT count(*) FROM pairing_sessions').fetchone()[0]
        history=self.workspace.view()
        self.assertTrue(history)
        self.assertTrue(all(not row['actions'] for row in history))
        now=int(self.time['latest'])
        for roles in (['receive','send'],['enroll','receive','revoke','send']):
            with self.subTest(roles=roles), self.assertRaisesRegex(ValueError,'Current enrollment authority'):
                pairing.offer(owner,encode_event(bundle),roles=roles,
                              session_before=str(now),session_after=str(now+30),
                              grant_before=str(now),grant_after=str(now+120),time=self.time)
        self.assertEqual(self.workspace.identity.db.execute('SELECT count(*) FROM pairing_sessions').fetchone()[0],before)
        self.assertEqual(self.workspace.identity.current_state(fresh['principal'])['head'],head)
        self.assertEqual(self.workspace.view(),history)

    def deliver(self,devices,identities,bundle,head):
        from sender_release import SenderRelease
        from initial_roster_lifecycle import InitialRosterRelease,InitialRosterAdmission
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        from invitation_mime import select
        from mls_mime import unpack
        owners=[OwnDevices(i,account='local-account',principal=d['principal'],local_device=d['device'],mailboxes=[self.f.mailbox]) for d,i in zip(devices,identities)]
        spool=PublicSpool(self.root/'fresh-public.sqlite');self.addCleanup(spool.close)
        for owner,d in zip(owners,devices):
            w=advertisement(self.binary,d,self.f.mailbox);v=json.loads(base64.b64decode(w['payload']));b=next(b for b in bundle['bindings'] if json.loads(base64.b64decode(b['payload']))['device']==d['device'])
            v.update(version='2',state=head,binding=hashlib.sha256(base64.b64decode(b['payload'])).hexdigest(),applications=[dict(envelopeVersion='1',payload='mime-contribution-v0',operations=['message'],ordering='designated-member-v0')]);raw=encode_event(v);w.update(payload=base64.b64encode(raw).decode(),signature=sign(self.binary,d,'email-next/passive-discovery/v2',raw),identity=bundle)
            from test_discovery_mime import message
            msg=message(encode_event(w));msg['From']=self.f.mailbox
            revision=owner.db.execute('SELECT revision FROM own_account').fetchone()[0];owner.publication(expected_revision=revision,enabled=True);owner.publish_device(msg.as_bytes(),time=self.time);spool.put(owner.publications(time=self.time))
        for owner in owners:owner.sync_from('fresh-sync',spool,time=self.time)
        senders=[self.workspace.sender(self.binary,time=self.time),SenderRelease(identities[1],self.binary)]
        for sender in senders:
            if not sender.db.execute('SELECT 1 FROM sender_policy').fetchone():sender.configure(expected_revision=0)
        context=dict(self.f.context,ordering=dict(kind='designated-member-v0',principal=devices[0]['principal'],device=devices[0]['device']))
        roster=sorted([dict(principal=d['principal'],device=d['device']) for d in devices],key=lambda d:(d['principal'],d['device']))
        selected=owners[0].snapshot(time=self.time)['selected'];wires=InitialRosterRelease(senders[0]).prepare('c'*32,device=devices[0],selected=selected,intended_principals=[devices[0]['principal']],intended_devices=roster,context=context,not_before=self.time['earliest'],not_after=str(int(self.time['latest'])+30),time=self.time)
        smtp=LocalSMTP()
        with SenderWorker(senders[0]) as worker:worker.submit_initial_roster(next(iter(wires)),port=smtp.port,time=self.time)
        smtp.done();admission=InitialRosterAdmission(identities[1],self.binary);admission.publish_local(devices[1]);selection=owners[1].snapshot(time=self.time)['selected']
        from passive_discovery import decode_passive_discovery
        choices=[dict(principal=decode_passive_discovery(s['wrapper'])['assertion']['value']['principal'],device=decode_passive_discovery(s['wrapper'])['assertion']['value']['device'],mailbox=s['mailbox'],generation=s['generation']) for s in selection]
        admission.accept_message(select(smtp.wire),target=devices[1],mailbox=self.f.mailbox,allow_creator=devices[0]['principal'],intended_principals=[devices[0]['principal']],intended_devices=roster,expected_context=encode_event(context),selections=choices,time=self.time,trust_policy='allow-unverified')
        event=dict(version='1',purpose='contribution',event='f'*32,conversation=context['conversation'],principal=devices[0]['principal'],audience=[devices[0]['principal']],disclosures=[],operation=dict(kind='message',text='Fresh key after restore',replyTo=[]))
        senders[0].prepare('freshmessage',encode_event(event),key=devices[0]['key'],envelope_sender=self.f.mailbox,recipients=[self.f.mailbox],time=self.time);smtp=LocalSMTP()
        with SenderWorker(senders[0]) as worker:worker.submit('freshmessage',port=smtp.port,time=self.time)
        smtp.done();self.assertEqual(senders[1].receiver.receive(unpack(smtp.wire),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        with closing(sqlite3.connect(self.source)) as source:old=source.execute("SELECT wire FROM sender_prepared WHERE id='message'").fetchone()[0]
        self.assertNotEqual(senders[0].receiver.receive(unpack(old),time=self.time,trust_policy='allow-unverified').get('applicationState'),'accepted')
    def test_fresh_pairing_then_actual_smtp(self):
        fresh,bundle,head=self.paired()
        # A separate surviving-device store has no old group's checkpoint, so
        # accepting this new conversation does not replace an existing group.
        from identity_store import IdentityStore
        peer=IdentityStore(self.root/'survivor-new-conversation.sqlite');self.addCleanup(peer.close);peer.observe(self.f.a['record'],first_contact_policy='allow-unverified')
        from identity_bundle import decode_identity_bundle
        for state in sorted(decode_identity_bundle(encode_event(bundle))['states'],key=lambda s:int(s['value']['revision'])):
            if state['value']['revision']!='0':peer.accept_successor(encode_event(bundle),candidate_digest=state['digest'],time=self.time)
        self.deliver([fresh,self.f.a],[self.workspace.identity,peer],bundle,head)
    def test_explicit_new_identity_not_old_account_continuity(self):
        fresh=self.workspace.start_fresh(self.binary);self.assertNotEqual(fresh['principal'],self.f.a['principal'])
        self.workspace.activate_new_identity(time=dict.fromkeys(('earliest','latest'),str(fresh['time'])))
        self.assertEqual(self.workspace.status(),'new-identity-needs-contact-approval')
        self.assertIsNone(self.workspace.identity.current_state(self.f.a['principal'])['head'])
        self.assertIsNone(self.workspace.db.execute("SELECT 1 FROM sqlite_master WHERE name='mls_checkpoint'").fetchone())
    def test_new_identity_requires_contact_choice_then_actual_smtp(self):
        from provider_mls import make_device
        from identity_store import IdentityStore
        from client_onboarding import ClientOnboarding
        from sender_release import SenderRelease
        from application_invitation_release import ApplicationInvitationRelease
        from application_invitation import ApplicationInvitationAdmission
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        from invitation_mime import select
        from mls_mime import unpack
        from test_discovery_mime import message
        fresh=self.workspace.start_fresh(self.binary);peer=make_device(self.binary,9,10)
        self.time=dict.fromkeys(('earliest','latest'),str(max(fresh['time'],peer['time'])))
        self.workspace.activate_new_identity(time=self.time)
        peerstore=IdentityStore(self.root/'correspondent.sqlite');self.addCleanup(peerstore.close)
        clients=[ClientOnboarding(self.workspace.identity),ClientOnboarding(peerstore)]
        def wire(d,mailbox):
            w=advertisement(self.binary,d,mailbox);v=json.loads(base64.b64decode(w['payload']));v.update(version='1',applications=[dict(envelopeVersion='1',operations=['message'],ordering=['fixed-roster-v0'])]);raw=encode_event(v);w.update(payload=base64.b64encode(raw).decode(),signature=sign(self.binary,d,'email-next/passive-discovery/v1',raw));m=message(encode_event(w));m['From']=mailbox;return m.as_bytes()
        options=dict(mode='automatic-unverified-continuity',target_policy='all-authorized-devices',policy_revision='1',time=self.time)
        source='restored@example.invalid';target='correspondent@example.invalid'
        clients[1].ingest('old-pin',[wire(self.f.a,source)],**options)
        old=clients[1].associations._current(source)
        for i,c in enumerate(clients):c.ingest('new-material',[wire(fresh,source),wire(peer,target)],**options)
        held=clients[1].targets(source,target_policy='all-authorized-devices',time=self.time,mode=options['mode'])
        self.assertFalse(any(__import__('passive_discovery').decode_passive_discovery(e['wrapper'])['assertion']['value']['principal']==fresh['principal'] for e in held.get('selected',[])))
        self.assertEqual(clients[1].associations._current(source)['principal'],self.f.a['principal'])
        # Explicit correspondent choice installs the held signed claim; automatic
        # onboarding deliberately did not replace the old account association.
        from discovery_mime import extract_discovery
        from passive_discovery import decode_passive_discovery
        claim=decode_passive_discovery(extract_discovery(wire(fresh,source),max_wire_bytes=2097152,max_parts=64)['octets'])
        peerstore.db.execute('BEGIN IMMEDIATE')
        try:
            checked=clients[1]._install(claim,self.time)
            self.assertEqual(checked['status'],'snapshot-authorized-unverified')
            clients[1].associations._observe_validated_batch_locked([dict(assertion=claim['assertion']['octets'],signature=claim['signature'],signingKey=bytes.fromhex(fresh['key']),outerFrom=[source],sourceId='explicit-new-identity',parserRevision='python-email-passive-v0',observedAt=self.time['earliest'])])
            peerstore.db.execute('COMMIT')
        except BaseException:
            peerstore.db.execute('ROLLBACK');raise
        decision=clients[1].associations.decide(decision_id='e'*32,mailbox=source,expected_generation=old['generation'],kind='replace-with-continuity-break',principal=fresh['principal'],actor='local-user',policy_revision='1',trust_policy='allow-unverified',time=self.time)
        self.assertEqual(decision['status'],'associated-unverified',decision)
        self.assertEqual(clients[1].associations._current(source)['principal'],fresh['principal'])
        selected=[clients[0].targets(m,target_policy='all-authorized-devices',time=self.time,mode=options['mode'])['selected'][0] for m in [source,target]]
        senders=[self.workspace.sender(self.binary,time=self.time),SenderRelease(peerstore,self.binary)]
        for sender in senders:sender.configure(expected_revision=0)
        ApplicationInvitationRelease(senders[0]).prepare('newlife',device=fresh,selected=selected,application=dict(envelopeVersion='1',operations=['message']),conversation='a'*32,not_before=self.time['earliest'],not_after=str(int(self.time['latest'])+30),time=self.time)
        smtp=LocalSMTP()
        with SenderWorker(senders[0]) as worker:worker.submit_initial_invitation('newlife',port=smtp.port,time=self.time)
        smtp.done();admission=ApplicationInvitationAdmission(peerstore,self.binary);admission.publish_local(peer)
        peer_selected=[clients[1].targets(m,target_policy='all-authorized-devices',time=self.time,mode=options['mode'])['selected'][0] for m in [source,target]]
        choices=[dict(principal=d['principal'],device=d['device'],mailbox=e['mailbox'],generation=e['generation']) for d,e in zip([fresh,peer],peer_selected)]
        admission.accept_message(select(smtp.wire),target=peer,mailbox=target,allow_creator=fresh['principal'],selections=choices,time=self.time,trust_policy='allow-unverified')
        event=dict(version='1',purpose='contribution',event='b'*32,conversation='a'*32,principal=fresh['principal'],audience=sorted([fresh['principal'],peer['principal']]),disclosures=[],operation=dict(kind='message',text='New identity, explicitly accepted',replyTo=[]))
        senders[0].prepare('freshstart',encode_event(event),key=fresh['key'],envelope_sender=source,recipients=[target],time=self.time);smtp=LocalSMTP()
        with SenderWorker(senders[0]) as worker:worker.submit('freshstart',port=smtp.port,time=self.time)
        smtp.done();self.assertEqual(senders[1].receiver.receive(unpack(smtp.wire),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')

    def test_pairing_choice_cannot_self_authorize_new_genesis(self):
        fresh=self.workspace.start_fresh(self.binary,principal=self.f.a['principal'])
        with self.assertRaisesRegex(ValueError,'Explicit new identity'):self.workspace.activate_new_identity(time=self.time)

if __name__=='__main__':unittest.main()
