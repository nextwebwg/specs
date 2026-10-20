import base64,json,unittest
from event_encoding import encode_event
from provider_mls import sign
from initial_roster_lifecycle import InitialRosterRelease
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from mls_mime import unpack
from journal_edit_view import view
import test_managed_presentation_lifecycle as managed

class JoinedEdits(unittest.TestCase):
    endpoint=managed.ManagedPresentation.endpoint;prepare=managed.ManagedPresentation.prepare;join=managed.ManagedPresentation.join;event=managed.ManagedPresentation.event;tearDown=managed.ManagedPresentation.tearDown
    def setUp(self):
        managed.ManagedPresentation.setUp(self)
        self.f.context['application']['operations']=sorted(set(self.f.context['application']['operations'])|{'edit'})
        proofs=[]
        for device,p in zip(self.f.devices,self.f.proofs):
            value=json.loads(base64.b64decode(p['payload']));value['applications']=[dict(self.f.context['application'],ordering='designated-member-v0')];raw=encode_event(value)
            proofs.append(dict(p,payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,device,'email-next/passive-discovery/v5',raw)))
        self.f.proofs=proofs;self.identity,self.sender,self.selected=self.endpoint('edit-creator');self.release=InitialRosterRelease(self.sender);self.join()
    def send(self,event,receive=True):
        delivery=event['event'];wire=self.sender.prepare(delivery,encode_event(event),key=self.f.creator['key'],envelope_sender=self.source,recipients=[self.destination],time=self.time)
        smtp=LocalSMTP()
        with SenderWorker(self.sender) as worker:self.assertEqual(worker.submit(delivery,port=smtp.port,time=self.time)['state'],'accepted')
        smtp.done();self.assertEqual(smtp.wire,wire)
        if receive:return wire,self.peer_sender.receiver.receive(unpack(wire),time=self.time,trust_policy='allow-unverified')
        return wire,None
    @staticmethod
    def ref(e):return {k:e[k] for k in ('principal','conversation','event')}
    def edit(self,id,root,predecessors,text):
        e=self.event(id=id);e['operation']=dict(kind='edit',root=self.ref(root),predecessors=[self.ref(x) for x in predecessors],text=text);return e
    def test_signed_smtp_reordered_conflict_merge_and_exact_retry(self):
        root=self.event();rootwire,_=self.send(root,False)
        a=self.edit('b',root,[root],'Wednesday');b=self.edit('c',root,[root],'Thursday')
        awire,result=self.send(a);self.assertEqual(result['applicationState'],'pending')
        bwire,result=self.send(b);self.assertEqual(result['applicationState'],'pending')
        receiver=self.peer_sender.receiver;receiver.receive(unpack(rootwire),time=self.time,trust_policy='allow-unverified')
        shown=view(receiver,self.ref(root));self.assertEqual({x['event'] for x in shown['heads']},{a['event'],b['event']})
        merge=self.edit('d',root,[a,b],'Friday');mwire,result=self.send(merge);self.assertEqual(result['applicationState'],'accepted')
        self.assertEqual(view(receiver,self.ref(root))['heads'],[self.ref(merge)])
        receiver.receive(unpack(mwire),time=self.time,trust_policy='allow-unverified');self.assertEqual(len(receiver.journal.snapshot(root['conversation'])),4)
        self.assertEqual(next(r for r in receiver.journal.snapshot(root['conversation']) if r['reference']==self.ref(root))['octets'][0],encode_event(root))
    def test_wrong_author_wrong_root_and_self_reference_hold_before_send(self):
        root=self.event();self.send(root)
        for change in ('author','self','kind'):
            e=self.edit('e',root,[root],'changed')
            if change=='author':e['operation']['root']['principal']=self.peer['principal']
            if change=='self':e['operation']['predecessors']=[self.ref(e)]
            if change=='kind':e['operation']['root']=dict(self.ref(root),event='f'*32)
            with self.assertRaises(ValueError):self.send(e)
    def transition(self,*,remove=False,replace=False,record='8',predecessor=None):
        import hashlib
        d=self.f.creator;principal=d['principal'];bundle=json.loads(encode_event(self.f.bundles[principal]));head=predecessor or self.peer_identity.current_state(principal)['head']
        state=json.loads(base64.b64decode(next(s['payload'] for s in bundle['states'] if hashlib.sha256(base64.b64decode(s['payload'])).hexdigest()==head)))
        signer=next(x for x in self.f.devices if x['principal']==principal and x['device']!=d['device']) if remove else d
        state.update(record=__import__('uuid').uuid4().hex,revision=str(int(state['revision'])+1),previous=[head],signer=signer['device'])
        if remove:state.update(bindings=[b for b in state['bindings'] if b['device']!=d['device']],revoked=sorted(state['revoked']+[d['device']]))
        if replace:
            old=next(b for b in bundle['bindings'] if hashlib.sha256(base64.b64decode(b['payload'])).hexdigest()==next(b['digest'] for b in state['bindings'] if b['device']==d['device']))
            binding=json.loads(base64.b64decode(old['payload']));binding.update(record='7'*32,roles=['receive','enroll','revoke'],authority=dict(kind='state',digest=head));raw=encode_event(binding)
            state['bindings']=[dict(b,digest=hashlib.sha256(raw).hexdigest()) if b['device']==d['device'] else b for b in state['bindings']]
            bundle['bindings'].append(dict(payload=base64.b64encode(raw).decode(),authorization=sign(self.f.binary,d,'email-next/device-binding/v0',raw),possession=sign(self.f.binary,d,'email-next/device-possession/v0',raw)))
        raw=encode_event(state);bundle['states'].append(dict(payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,signer,'email-next/identity-state/v0',raw)))
        return self.peer_identity.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(raw).hexdigest(),time=self.time)
    def test_explicit_revocation_suspends_effect_without_erasing_versions(self):
        root=self.event();self.send(root);edit=self.edit('b',root,[root],'Wednesday');self.send(edit)
        self.assertEqual(self.transition(remove=True)['status'],'accepted-unverified')
        shown=view(self.peer_sender.receiver,self.ref(root));self.assertEqual(shown['heads'],[self.ref(root)])
        self.assertEqual(shown['eligibility'][0]['reason'],'device-revoked');self.assertEqual(len(self.peer_sender.receiver.journal.snapshot(root['conversation'])),2)
    def test_binding_replacement_is_not_retroactive_revocation(self):
        root=self.event();self.send(root);edit=self.edit('b',root,[root],'Wednesday');self.send(edit)
        self.assertEqual(self.transition(replace=True)['status'],'accepted-unverified')
        self.assertEqual(view(self.peer_sender.receiver,self.ref(root))['heads'],[self.ref(edit)])
    def test_authorized_identity_fork_suspends_effect(self):
        root=self.event();self.send(root);edit=self.edit('b',root,[root],'Wednesday');self.send(edit)
        head=self.peer_identity.current_state(root['principal'])['head']
        self.assertEqual(self.transition(record='8',predecessor=head)['status'],'accepted-unverified')
        self.assertEqual(self.transition(record='9',predecessor=head)['status'],'conflicted')
        shown=view(self.peer_sender.receiver,self.ref(root));self.assertEqual(shown['heads'],[self.ref(root)]);self.assertEqual(shown['eligibility'][0]['reason'],'identity-conflict')
    def test_unknown_authority_and_budget_preserve_stale_view(self):
        from unittest.mock import patch
        root=self.event();self.send(root);edit=self.edit('b',root,[root],'Wednesday');self.send(edit);receiver=self.peer_sender.receiver
        good=view(receiver,self.ref(root))
        with patch.object(receiver.identity,'current_state',return_value=dict(head=None,conflicted=False)):
            held=view(receiver,self.ref(root));self.assertEqual(held['state'],'incomplete');self.assertTrue(held['lastCommitted']['stale']);self.assertEqual(held['lastCommitted']['heads'],good['heads'])
        self.assertEqual(view(receiver,self.ref(root),max_records=1)['state'],'incomplete')
        self.assertEqual(view(receiver,self.ref(root))['heads'],[self.ref(edit)])
    def test_same_author_other_device_and_readable_correction(self):
        from initial_roster import parse
        from invitation_mime import select
        from initial_roster_lifecycle import InitialRosterAdmission
        from plaintext_release import PlaintextRelease
        from email.parser import BytesParser
        from email import policy
        root=self.event();root['operation']['text']='Original private wording';rootwire,_=self.send(root)
        target=next(d for d in self.f.devices if d['principal']==self.f.creator['principal'] and d['device']!=self.f.creator['device'])
        identifier,invitation=next((i,w) for i,w in self.prepare().items() if parse(select(w))['value']['target']['device']==target['device'])
        identity,sender,selected=self.endpoint('second-author');self.secondary=(identity,sender,target);admission=InitialRosterAdmission(identity,self.f.binary);admission.publish_local(target);p=parse(select(invitation))
        choices=[dict(principal=d['principal'],device=d['device'],mailbox=c['mailbox'],generation=c['generation']) for d,c in zip(self.f.devices,selected)]
        admission.accept_message(select(invitation),target=target,mailbox=p['value']['target']['mailbox'],allow_creator=self.f.creator['principal'],intended_principals=self.principals,intended_devices=self.devices,expected_context=encode_event(self.f.context),selections=choices,time=self.time,trust_policy='allow-unverified')
        sender.receiver.receive(unpack(rootwire),time=self.time,trust_policy='allow-unverified')
        edit=self.edit('b',root,[root],'Corrected wording');edit['disclosures']=[dict(kind='plaintext-email')];raw=encode_event(edit)
        fallback=PlaintextRelease(sender);exposure=fallback.preview(raw,['legacy@example.invalid'])
        self.assertNotIn(root['operation']['text'],exposure['text'])
        with self.assertRaises(ValueError):fallback.authorize(raw,['legacy@example.invalid'])
        fallback.authorize(raw,['legacy@example.invalid'],exposure=exposure)
        wire=sender.prepare('otherdeviceedit',raw,key=target['key'],envelope_sender=p['value']['target']['mailbox'],recipients=[self.destination],time=self.time)
        smtp=LocalSMTP()
        with SenderWorker(sender) as worker:worker.submit('otherdeviceedit',port=smtp.port,time=self.time)
        smtp.done();self.assertEqual(self.peer_sender.receiver.receive(unpack(smtp.wire),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        fallback.prepare('ordinaryedit','otherdeviceedit');smtp=LocalSMTP()
        with SenderWorker(sender) as worker:worker.submit_plaintext('ordinaryedit',port=smtp.port,time=self.time)
        smtp.done();parts=list(BytesParser(policy=policy.default).parsebytes(smtp.wire).iter_parts());self.assertEqual([p.get_content_type() for p in parts],['text/plain','text/html'])
        self.assertIn('Correction to an earlier message',parts[0].get_content());self.assertNotIn(root['operation']['text'],parts[0].get_content())
    def test_expired_discovery_and_binding_do_not_remove_accepted_effect(self):
        root=self.event();self.send(root);edit=self.edit('b',root,[root],'Wednesday');self.send(edit)
        late=dict(earliest=str(int(self.time['latest'])+100000),latest=str(int(self.time['latest'])+100000))
        self.peer_sender.receiver.reevaluate(time=late,trust_policy='allow-unverified')
        self.assertEqual(view(self.peer_sender.receiver,self.ref(root))['heads'],[self.ref(edit)])
    def test_client_compose_atomic_retry_and_crash_rollback(self):
        from client_edits import prepare
        root=self.event();self.send(root);token=view(self.sender.receiver,self.ref(root))['sourceToken']
        args=('composeedit',self.ref(root),[self.ref(root)],'Wednesday',token)
        kwargs=dict(key=self.f.creator['key'],address=self.source,recipients=[self.destination],time=self.time)
        with self.assertRaises(RuntimeError):prepare(self.sender,*args,**kwargs,crash=lambda stage:(_ for _ in ()).throw(RuntimeError('crash')) if stage=='before-prepare-commit' else None)
        self.assertEqual(self.sender.db.execute('SELECT count(*) FROM client_edit_actions').fetchone()[0],0)
        wire=prepare(self.sender,*args,**kwargs);self.assertEqual(prepare(self.sender,*args,**kwargs),wire)
        with self.assertRaises(ValueError):prepare(self.sender,'staleedit',self.ref(root),[self.ref(root)],'Thursday',token,**kwargs)
    def test_membership_removal_keeps_accepted_edit_but_holds_old_pending(self):
        self.test_same_author_other_device_and_readable_correction()
        from group_transitions import GroupTransitions
        from transition_carrier import release_mime,receive_mime
        from secret_retention import SecretRetention
        from test_secret_retention import POLICY
        from mls_receive import MlsReceive
        second_identity,second_sender,device=self.secondary
        for sender in (self.sender,self.peer_sender):SecretRetention(sender.receiver).configure(POLICY,time=self.time)
        delayed=self.event(id='c');delayedwire,_=self.send(delayed,False)
        second_sender.receiver.receive(unpack(delayedwire),time=self.time,trust_policy='allow-unverified')
        pending=self.edit('d',delayed,[delayed],'Delayed correction')
        wire=second_sender.prepare('pendingedit',encode_event(pending),key=device['key'],envelope_sender=self.source,recipients=[self.destination],time=self.time)
        self.assertEqual(self.peer_sender.receiver.receive(unpack(wire),time=self.time,trust_policy='allow-unverified')['applicationState'],'pending')
        creator=GroupTransitions(self.identity,self.f.binary.with_name('group-transitions'),self.f.creator)
        recipient=GroupTransitions(self.peer_identity,self.f.binary.with_name('group-transitions'),self.peer)
        decision=creator.prepare_removal([dict(identity=device['identity'],key=device['key'])],time=self.time);self.assertEqual(creator.decide(decision,allowed=set(),time=self.time),'accepted')
        control=release_mime(creator,decision,sender=self.source,recipient=self.destination,allowed=set(),time=self.time)
        smtp=LocalSMTP()
        import smtplib
        with smtplib.SMTP('127.0.0.1',smtp.port) as transport:transport.sendmail(self.source,[self.destination],control)
        smtp.done();self.assertEqual(receive_mime(recipient,smtp.wire,allowed=set(),time=self.time),'accepted')
        receiver=MlsReceive(self.peer_identity,self.f.binary.with_name('receive-staged'))
        self.assertEqual(receiver.receive(unpack(delayedwire),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        result=receiver.reevaluate(time=self.time,trust_policy='allow-unverified');self.assertIn('held:membership-episode',result['states'].values())
        self.assertEqual(view(receiver,self.ref(delayed))['heads'],[self.ref(delayed)])
        oldroot=self.event();self.assertEqual(view(receiver,self.ref(oldroot))['heads'],[self.ref(self.edit('b',oldroot,[oldroot],'Corrected wording'))])
    def test_merge_before_all_dependencies_and_equal_distinct_events(self):
        root=self.event();rw,_=self.send(root,False);a=self.edit('b',root,[root],'Same correction');b=self.edit('c',root,[root],'Same correction')
        aw,_=self.send(a,False);bw,_=self.send(b,False);merge=self.edit('d',root,[a,b],'Resolved');mw,_=self.send(merge,False);receiver=self.peer_sender.receiver
        for wire in (mw,bw,aw):self.assertEqual(receiver.receive(unpack(wire),time=self.time,trust_policy='allow-unverified')['applicationState'],'pending')
        self.assertEqual(receiver.journal.snapshot(root['conversation']),[])
        receiver.receive(unpack(rw),time=self.time,trust_policy='allow-unverified')
        self.assertEqual(view(receiver,self.ref(root))['heads'],[self.ref(merge)]);self.assertEqual(len(receiver.journal.snapshot(root['conversation'])),4)
    def test_signed_device_without_edit_prevents_new_profile_selection(self):
        i=1;p=self.f.proofs[i];d=self.f.devices[i];value=json.loads(base64.b64decode(p['payload']));value['applications'][0]['operations'].remove('edit');raw=encode_event(value)
        self.f.proofs[i]=dict(p,payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,d,'email-next/passive-discovery/v5',raw))
        identity,sender,selected=self.endpoint('missing-edit');release=InitialRosterRelease(sender)
        with self.assertRaises(ValueError):release.prepare('f'*32,device=self.f.creator,selected=selected,intended_principals=self.principals,intended_devices=self.devices,context=self.f.context,not_before=self.f.time,not_after=str(int(self.f.time)+30),time=self.time)
    def test_view_bounds_precede_materialization_and_ignore_unrelated_provenance(self):
        from unittest.mock import patch
        root=self.event();self.send(root);edit=self.edit('b',root,[root],'Wednesday');self.send(edit);receiver=self.peer_sender.receiver
        good=view(receiver,self.ref(root))
        # Unrelated malformed/large provenance must never be loaded or decoded.
        receiver.db.execute('INSERT INTO local_author_evidence VALUES(?,?,?)',('0'*64,'unrelated','not-json'*10000))
        self.assertEqual(view(receiver,self.ref(root))['heads'],good['heads'])
        with patch.object(receiver.journal,'snapshot',side_effect=AssertionError('Must hold before materialization')):
            for limits in (dict(max_records=1),dict(max_bytes=1)):
                held=view(receiver,self.ref(root),**limits);self.assertEqual(held['state'],'incomplete');self.assertTrue(held['lastCommitted']['stale'])
        for value in (True,-1,float('inf'),float('nan'),1.5):
            for key in ('max_records','max_references','max_bytes'):
                with self.assertRaises(ValueError):view(receiver,self.ref(root),**{key:value})
