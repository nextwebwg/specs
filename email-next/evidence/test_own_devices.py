import base64,hashlib,json,os,tempfile,unittest
from pathlib import Path
from email import policy
from unittest.mock import patch
from identity_store import IdentityStore
from own_devices import OwnDevices,PublicSpool
from provider_mls import make_device,advertisement,sign
from event_encoding import encode_event
from test_group_transitions import enroll
from test_discovery_mime import message

class OwnDeviceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.binary=Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR'])/'provider-mls'
        self.a=make_device(self.binary,1,2);self.b=make_device(self.binary,1,7);self.time=dict.fromkeys(('earliest','latest'),str(max(self.a['time'],self.b['time'])))
        self.bundle,self.head=enroll(self.binary,self.a,self.b);self.raw=encode_event(self.bundle)
        self.binding=next(base64.b64decode(b['payload']) for b in self.bundle['bindings'] if json.loads(base64.b64decode(b['payload']))['device']==self.b['device'])
        self.wires={};self.mailbox='own@example.invalid';self.stores=[IdentityStore(self.root/(str(i)+'.sqlite')) for i in range(2)]
        # Explicit trusted anchor handoff: both local stores begin from the same
        # existing account anchor, never the new device's self-issued genesis.
        for store in self.stores:store.observe(self.a['record'],first_contact_policy='allow-unverified')
        self.owners=[OwnDevices(store,account='local-account',principal=self.a['principal'],local_device=device['device'],mailboxes=[self.mailbox]) for store,device in zip(self.stores,[self.a,self.b])]
        self.application=dict(envelopeVersion='1',payload='mime-contribution-v0',operations=['message'])
        self.context=dict(version='3',purpose='conversation-context',conversation='2'*32,profile='mls-1-0001',administrators=[self.a['principal']],application=self.application,ordering=dict(kind='designated-member-v0',principal=self.a['principal'],device=self.a['device']))
    def tearDown(self):
        for store in self.stores:store.close()
        self.temp.cleanup()
    def approve(self):self.owners[0].approve('approved',self.binding,expected_head=self.a['state'])
    def commit(self,**kw):return self.owners[0].commit_enrollment('approved',self.raw,candidate_digest=self.head,time=self.time,**kw)
    def wire(self,device,*,mailbox=None):
        cache=(device['device'],mailbox or self.mailbox)
        if cache in self.wires:return self.wires[cache]
        wrapper=advertisement(self.binary,device,mailbox or self.mailbox);v=json.loads(base64.b64decode(wrapper['payload']));binding=next(b for b in self.bundle['bindings'] if json.loads(base64.b64decode(b['payload']))['device']==device['device'])
        v.update(version='2',state=self.head,binding=hashlib.sha256(base64.b64decode(binding['payload'])).hexdigest(),applications=[dict(self.application,ordering='designated-member-v0')]);raw=encode_event(v)
        wrapper.update(payload=base64.b64encode(raw).decode(),signature=sign(self.binary,device,'email-next/passive-discovery/v2',raw),identity=self.bundle)
        root=message(encode_event(wrapper));root['From']=mailbox or self.mailbox;self.wires[cache]=root.as_bytes(policy=policy.SMTP);return self.wires[cache]
    def sync(self):
        self.approve();self.commit();spool=PublicSpool(self.root/'public-spool.sqlite');self.addCleanup(spool.close)
        self.owners[0].publication(expected_revision=0,enabled=True)
        spool.put(self.owners[0].publications(time=self.time));self.owners[1].sync_from('approved-channel',spool,time=self.time)
        wires=[self.wire(d) for d in [self.a,self.b]]
        self.owners[1].publication(expected_revision=0,enabled=True)
        for own,wire in zip(self.owners,wires):own.publish_device(wire,time=self.time);spool.put(own.publications(time=self.time))
        for own in self.owners:own.sync_from('approved-channel',spool,time=self.time)
        return wires
    def test_exact_approval_atomic_publication_and_setting(self):
        with self.assertRaisesRegex(ValueError,'approval'):self.commit()
        self.approve()
        with self.assertRaises(RuntimeError):self.commit(crash=lambda _:(_ for _ in ()).throw(RuntimeError('crash')))
        self.assertEqual(self.stores[0].current_state(self.a['principal'])['head'],self.a['state']);self.assertEqual(self.stores[0].db.execute('SELECT count(*) FROM own_outbox').fetchone()[0],0)
        result=self.commit();self.assertEqual(self.commit(),result)
        self.assertEqual(self.owners[0].publications(time=self.time),[])
        self.owners[0].publication(expected_revision=0,enabled=True)
        published=self.owners[0].publications(time=self.time);self.assertEqual(len(published),1);self.assertEqual(published[0]['bytes'],self.raw)
        self.assertNotIn(b'checkpoint',published[0]['bytes']);self.assertFalse(result['historyTransferred'])
        self.owners[1].ingest('configured',[(1,'identity',published[0]['bytes'])],time=self.time)
        self.assertEqual(self.owners[1].publications(time=self.time),[])
        self.assertEqual(self.stores[1].current_state(self.a['principal'])['head'],self.head)
    def test_unknown_anchor_alias_and_foreign_account_do_not_authorize(self):
        fresh=IdentityStore(self.root/'empty.sqlite')
        try:
            with self.assertRaisesRegex(ValueError,'anchor'):OwnDevices(fresh,account='login',principal=self.a['principal'],local_device=self.b['device'],mailboxes=[self.mailbox])
        finally:fresh.close()
        self.approve();self.commit()
        with self.assertRaisesRegex(ValueError,'mailbox'):self.owners[0].publish_device(self.wire(self.a,mailbox='alias@example.invalid'),time=self.time)
        with self.assertRaisesRegex(ValueError,'device'):self.owners[0].publish_device(self.wire(self.b),time=self.time)
        with self.assertRaisesRegex(ValueError,'configuration'):OwnDevices(self.stores[0],account='other',principal=self.a['principal'],local_device=self.a['device'],mailboxes=[self.mailbox])
    def test_source_crash_rollback_inventory_partial_and_retry(self):
        self.approve();self.commit();owner=self.owners[1]
        with self.assertRaises(RuntimeError):owner.ingest('sync',[(1,'identity',self.raw)],time=self.time,crash=lambda _:(_ for _ in ()).throw(RuntimeError('crash')))
        self.assertEqual(self.stores[1].current_state(self.a['principal'])['head'],self.a['state']);self.assertEqual(self.stores[1].db.execute('SELECT count(*) FROM own_cursor').fetchone()[0],0)
        owner.ingest('sync',[(1,'identity',self.raw),(2,'discovery',self.wire(self.a))],time=self.time)
        snapshot=owner.snapshot(time=self.time);self.assertEqual(snapshot['missing'],[self.b['device']]);self.assertFalse(snapshot['completeRelativeToHead'])
        owner.ingest('sync',[(3,'discovery',self.wire(self.b))],time=self.time);full=owner.snapshot(time=self.time);self.assertTrue(full['completeRelativeToHead']);self.assertFalse(full['mailboxOwnershipVerified']);self.assertFalse(full['sendAuthorized'])
        owner.ingest('sync',[(3,'discovery',self.wire(self.b))],time=self.time)
        self.assertEqual(owner.snapshot(time=self.time)['snapshot'],full['snapshot'])
    def test_approval_head_race_and_swapped_binding(self):
        self.approve();changed=json.loads(self.binding);changed['signingKey']='f'*64
        with self.assertRaisesRegex(ValueError,'conflict'):self.owners[0].approve('approved',encode_event(changed),expected_head=self.a['state'])
        self.stores[0].accept_successor(self.raw,candidate_digest=self.head,time=self.time)
        with self.assertRaisesRegex(ValueError,'head changed'):self.commit()
        self.assertEqual(self.stores[0].db.execute('SELECT count(*) FROM own_outbox').fetchone()[0],0)
    def test_signed_revocation_and_conflict_do_not_reopen_targets(self):
        self.sync();state=json.loads(base64.b64decode(self.bundle['states'][0]['payload']))
        state.update(record='9'*32,revision='2',previous=[self.head],revoked=[self.b['device']],bindings=[b for b in state['bindings'] if b['device']!=self.b['device']])
        raw=encode_event(state);bundle=json.loads(json.dumps(self.bundle));bundle['states'].insert(0,dict(payload=base64.b64encode(raw).decode(),signature=sign(self.binary,self.a,'email-next/identity-state/v0',raw)))
        revoked=encode_event(bundle)
        self.owners[0].ingest('revocation',[(1,'identity',revoked)],time=self.time)
        snapshot=self.owners[0].snapshot(time=self.time);self.assertIn(self.b['device'],snapshot['revoked']);self.assertNotIn(self.b['device'],snapshot['required']);self.assertFalse(snapshot['completeRelativeToHead'])
        # Replayed old valid discovery cannot roll back the accepted revocation.
        self.owners[0].ingest('old-advertisement',[(1,'discovery',self.wire(self.b))],time=self.time)
        self.assertEqual(self.stores[0].current_state(self.a['principal'])['head'],hashlib.sha256(raw).hexdigest())
        alternate=json.loads(json.dumps(bundle));other=dict(state,record='a'*32,bindings=json.loads(base64.b64decode(self.bundle['states'][0]['payload']))['bindings'],revoked=[])
        other_raw=encode_event(other);alternate['states'][0]=dict(payload=base64.b64encode(other_raw).decode(),signature=sign(self.binary,self.a,'email-next/identity-state/v0',other_raw))
        self.owners[0].ingest('branch',[(1,'identity',encode_event(alternate))],time=self.time)
        self.assertTrue(self.stores[0].current_state(self.a['principal'])['conflicted'])
        with self.assertRaisesRegex(ValueError,'conflict'):self.owners[0].snapshot(time=self.time)
    def test_receive_only_device_cannot_enroll(self):
        # Enroll the second device with receive authority only, using real proofs.
        binding=json.loads(self.binding);binding['roles']=['receive'];self.binding=encode_event(binding)
        bundle=json.loads(json.dumps(self.bundle));entry=next(b for b in bundle['bindings'] if json.loads(base64.b64decode(b['payload']))['device']==self.b['device']);entry.update(payload=base64.b64encode(self.binding).decode(),authorization=sign(self.binary,self.a,'email-next/device-binding/v0',self.binding),possession=sign(self.binary,self.b,'email-next/device-possession/v0',self.binding))
        state=json.loads(base64.b64decode(bundle['states'][0]['payload']));next(r for r in state['bindings'] if r['device']==self.b['device'])['digest']=hashlib.sha256(self.binding).hexdigest();raw=encode_event(state);bundle['states'][0]=dict(payload=base64.b64encode(raw).decode(),signature=sign(self.binary,self.a,'email-next/identity-state/v0',raw));self.raw=encode_event(bundle);self.head=hashlib.sha256(raw).hexdigest()
        self.approve();self.commit();self.owners[1].ingest('enrollment',[(1,'identity',self.raw)],time=self.time)
        third=make_device(self.binary,1,9);b=json.loads(base64.b64decode(third['record']['binding']));b.update(authority=dict(kind='state',digest=self.head),roles=['receive']);payload=encode_event(b)
        next_state=dict(state,record='a'*32,revision='2',previous=[self.head],signer=self.b['device'],bindings=sorted(state['bindings']+[dict(device=third['device'],digest=hashlib.sha256(payload).hexdigest())],key=lambda x:x['device']));next_raw=encode_event(next_state)
        bundle['bindings'].append(dict(payload=base64.b64encode(payload).decode(),authorization=sign(self.binary,self.b,'email-next/device-binding/v0',payload),possession=sign(self.binary,third,'email-next/device-possession/v0',payload)));bundle['states'].insert(0,dict(payload=base64.b64encode(next_raw).decode(),signature=sign(self.binary,self.b,'email-next/identity-state/v0',next_raw)))
        self.owners[1].approve('noauthority',payload,expected_head=self.head)
        with self.assertRaisesRegex(ValueError,'not accepted'):self.owners[1].commit_enrollment('noauthority',encode_event(bundle),candidate_digest=hashlib.sha256(next_raw).hexdigest(),time=self.time)
        self.assertEqual(self.stores[1].current_state(self.a['principal'])['head'],self.head)
    def test_enrollment_does_not_copy_old_conversation_secrets(self):
        from provider_mls import call
        from mls_receive import worker_call,FORMAT
        peer=make_device(self.binary,3,4)
        old=call(self.binary,op='create-initial-roster',checkpoint=self.a['checkpoint'],key=self.a['key'],identity=self.a['identity'],context=encode_event(self.context).hex(),packages=[peer['package']])
        sent=call(self.binary,op='send',checkpoint=old['checkpoint'],group=old['group'],key=self.a['key'],application=b'old protected content'.hex())
        self.sync()
        result=worker_call(self.binary.with_name('receive-staged'),dict(format=FORMAT,checkpoint=self.b['checkpoint'],group=old['group'],wire=sent['wire']))
        self.assertNotEqual(result['status'],'authenticated-application')
        for store in self.stores:
            for raw, in store.db.execute('SELECT bytes FROM own_outbox'):
                self.assertNotIn(b'checkpoint',raw);self.assertNotIn(b'old protected content',raw)
    def test_publication_preserves_only_signed_evidence_and_exact_retry(self):
        self.approve();self.commit()
        from email.parser import BytesParser
        root=BytesParser(policy=policy.SMTP).parsebytes(self.wire(self.a));root.add_attachment(b'PRIVATE CHECKPOINT OR OLD HISTORY',maintype='application',subtype='octet-stream')
        ident=self.owners[0].publish_device(root.as_bytes(),time=self.time)
        self.assertEqual(self.owners[0].publish_device(root.as_bytes(),time=self.time),ident)
        self.owners[0].publication(expected_revision=0,enabled=True)
        published=next(r for r in self.owners[0].publications(time=self.time) if r['kind']=='discovery')
        self.assertNotIn(b'PRIVATE CHECKPOINT',published['bytes'])
        from discovery_mime import extract_discovery
        options=dict(max_wire_bytes=1000000,max_parts=64)
        self.assertEqual(extract_discovery(published['bytes'],**options),extract_discovery(self.wire(self.a),**options))
        self.assertEqual(len(list(BytesParser(policy=policy.SMTP).parsebytes(published['bytes']).iter_parts())),2)
    def test_retention_failure_keeps_cursor_and_observations_atomic(self):
        self.approve();self.commit()
        owner=OwnDevices(self.stores[1],account='local-account',principal=self.a['principal'],local_device=self.b['device'],mailboxes=[self.mailbox],max_records=2)
        owner.ingest('limited',[(1,'identity',self.raw),(2,'identity',self.raw)],time=self.time)
        with self.assertRaisesRegex(ValueError,'retention budget'):owner.ingest('limited',[(3,'discovery',self.wire(self.b))],time=self.time)
        self.assertEqual(self.stores[1].db.execute('SELECT position FROM own_cursor WHERE source="limited"').fetchone()[0],2)
        self.assertEqual(self.stores[1].db.execute('SELECT count(*) FROM mailbox_observations').fetchone()[0],0)
        self.assertEqual(self.stores[1].db.execute('SELECT count(*) FROM mailbox_associations').fetchone()[0],0)
    def test_actual_two_stores_initial_roster_and_protected_delivery(self):
        self.sync()
        from sender_release import SenderRelease
        from initial_roster_lifecycle import InitialRosterRelease,InitialRosterAdmission
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        from invitation_mime import select
        from mls_mime import unpack
        senders=[SenderRelease(store,self.binary) for store in self.stores]
        for sender in senders:sender.configure(expected_revision=0)
        selected=self.owners[0].snapshot(time=self.time)['selected'];devices=sorted([self.a,self.b],key=lambda d:(d['principal'],d['device']))
        inventory=[{k:d[k] for k in ('principal','device')} for d in devices]
        wires=InitialRosterRelease(senders[0]).prepare('3'*32,device=self.a,selected=selected,intended_principals=[self.a['principal']],intended_devices=inventory,context=self.context,not_before=self.time['earliest'],not_after=str(int(self.time['latest'])+30),time=self.time)
        smtp=LocalSMTP()
        with SenderWorker(senders[0]) as worker:self.assertEqual(worker.submit_initial_roster(next(iter(wires)),port=smtp.port,time=self.time)['state'],'accepted')
        smtp.done();admission=InitialRosterAdmission(self.stores[1],self.binary);admission.publish_local(self.b)
        choices=[dict(principal=d['principal'],device=d['device'],mailbox=e['mailbox'],generation=e['generation']) for d,e in zip(devices,self.owners[1].snapshot(time=self.time)['selected'])]
        admission.accept_message(select(smtp.wire),target=self.b,mailbox=self.mailbox,allow_creator=self.a['principal'],intended_principals=[self.a['principal']],intended_devices=inventory,expected_context=encode_event(self.context),selections=choices,time=self.time,trust_policy='allow-unverified')
        event=dict(version='1',purpose='contribution',event='7'*32,conversation='2'*32,principal=self.a['principal'],audience=[self.a['principal']],disclosures=[],operation=dict(kind='message',text='Both my devices',replyTo=[]))
        senders[0].prepare('message',encode_event(event),key=self.a['key'],envelope_sender=self.mailbox,recipients=[self.mailbox],time=self.time)
        smtp=LocalSMTP()
        with SenderWorker(senders[0]) as worker:self.assertEqual(worker.submit('message',port=smtp.port,time=self.time)['state'],'accepted')
        smtp.done();self.assertEqual(senders[1].receiver.receive(unpack(smtp.wire),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        self.assertEqual(self.stores[0].db.execute('SELECT count(*) FROM own_outbox WHERE bytes LIKE ?',(b'%checkpoint%',)).fetchone()[0],0)
        # Current signed revocation after preparation aborts the actual SMTP
        # transaction before DATA, despite the mailbox itself still working.
        event['event']='8'*32
        senders[0].prepare('raced',encode_event(event),key=self.a['key'],envelope_sender=self.mailbox,recipients=[self.mailbox],time=self.time)
        state=json.loads(base64.b64decode(self.bundle['states'][0]['payload']));state.update(record='b'*32,revision='2',previous=[self.head],revoked=[self.b['device']],bindings=[r for r in state['bindings'] if r['device']!=self.b['device']]);raw=encode_event(state);bundle=json.loads(json.dumps(self.bundle));bundle['states'].insert(0,dict(payload=base64.b64encode(raw).decode(),signature=sign(self.binary,self.a,'email-next/identity-state/v0',raw)))
        def revoke(stage):
            if stage=='after-release':self.owners[0].ingest('racing-revocation',[(1,'identity',encode_event(bundle))],time=self.time)
        smtp=LocalSMTP()
        with SenderWorker(senders[0]) as worker:self.assertEqual(worker.submit('raced',port=smtp.port,time=self.time,crash=revoke)['state'],'aborted-before-data')
        smtp.done();self.assertIsNone(smtp.wire)


if __name__=='__main__':unittest.main()
