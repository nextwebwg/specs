"""Actual signed rich initial roster and final support, no configured agreement injection."""
import base64,hashlib,json,unittest
import test_rich_group_lifecycle as rich
from provider_mls import make_device,sign
from event_encoding import encode_event
from initial_roster_lifecycle import InitialRosterAdmission
from initial_roster import parse
from invitation_mime import select
from group_transitions import GroupTransitions
from transition_support import TransitionSupport
from transition_carrier import encode_transition
from remediation_chain import RemediationChain,POLICY

import test_private_copy_lifecycle as private_fixture
import test_managed_presentation_lifecycle as managed_fixture
from recovery_retrieval import RecoveryRetrieval,MailSpool
from transition_mime import package
from test_sender_release import LocalSMTP
from unittest.mock import patch
import smtplib

class DeliveryRecovery(unittest.TestCase):
    endpoint=private_fixture.PrivateCopyLifecycle.endpoint;prepare=private_fixture.PrivateCopyLifecycle.prepare;tearDown=private_fixture.PrivateCopyLifecycle.tearDown
    def configure(self,version):
        (managed_fixture.ManagedPresentation if version=='6' else private_fixture.PrivateCopyLifecycle).setUp(self)
    def setup_chain(self):
        final=next(d for d in self.f.devices if d['principal']==self.f.creator['principal'] and d is not self.f.creator)
        index=self.f.devices.index(final);proof=encode_event(self.f.proofs[index])
        self.f.devices.pop(index);self.f.proofs.pop(index);self.selected.pop(index);self.devices=[{k:d[k] for k in ('principal','device')} for d in self.f.devices]
        wires=self.prepare();wire=next(w for w in wires.values() if parse(select(w))['value']['target']['device']==next(d['device'] for d in self.f.devices if d['principal']!=self.f.creator['principal'] and d['device']==json.loads(base64.b64decode(self.f.bundles[d['principal']]['states'][0]['payload']))['signer']));p=parse(select(wire));target=next(d for d in self.f.devices if d['device']==p['value']['target']['device'] and d['principal']==p['value']['target']['principal'])
        identity,sender,selected=self.endpoint('recovering');admission=InitialRosterAdmission(identity,self.f.binary);admission.publish_local(target)
        choices=[dict(principal=d['principal'],device=d['device'],mailbox=c['mailbox'],generation=c['generation']) for d,c in zip(self.f.devices,selected)]
        admission.accept_message(select(wire),target=target,mailbox=p['value']['target']['mailbox'],allow_creator=self.f.creator['principal'],intended_principals=self.principals,intended_devices=self.devices,expected_context=encode_event(self.f.context),selections=choices,time=self.time,trust_policy='allow-unverified')
        ga=GroupTransitions(self.identity,self.f.binary.with_name('group-transitions'),self.f.creator);gb=GroupTransitions(identity,self.f.binary.with_name('group-transitions'),target)
        from commit_history import CommitHistory
        self.history=CommitHistory(ga,max_count=16,max_bytes=8000000)
        start=gb.live()['snapshot']['predecessor']
        temporary=next(d for d in self.f.devices if d is not target and d is not self.f.creator and d['device']!=json.loads(base64.b64decode(self.f.bundles[d['principal']]['states'][0]['payload']))['signer'])
        # A real authenticated pending answer exists before its device is revoked.
        twire=next(w for w in wires.values() if parse(select(w))['value']['target']['device']==temporary['device'])
        ti,ts,tselected=self.endpoint('temporary-author');ta=InitialRosterAdmission(ti,self.f.binary);ta.publish_local(temporary)
        tp=parse(select(twire));tchoices=[dict(principal=d['principal'],device=d['device'],mailbox=c['mailbox'],generation=c['generation']) for d,c in zip(self.f.devices,tselected)]
        ta.accept_message(select(twire),target=temporary,mailbox=tp['value']['target']['mailbox'],allow_creator=self.f.creator['principal'],intended_principals=self.principals,intended_devices=self.devices,expected_context=encode_event(self.f.context),selections=tchoices,time=self.time,trust_policy='allow-unverified')
        event=dict(version=self.f.context['application']['envelopeVersion'],purpose='contribution',event='6'*32,conversation=self.f.context['conversation'],principal=temporary['principal'],audience=self.principals,disclosures=[],operation=dict(kind='answer',question=dict(principal=temporary['principal'],conversation=self.f.context['conversation'],event='5'*32),option='7'*32,replaces=[]))
        if event['version']=='3':event['presentation']=dict(subject='Pending answer',authoredAt='',to=[self.f.creator['principal']],cc=[])
        destination=self.selected[self.f.devices.index(target)]['mailbox'];source=tselected[self.f.devices.index(temporary)]['mailbox']
        from provider_mls import call
        from protected_carrier import package_carrier
        # Construct valid authenticated incoming bytes independently of the
        # composing client, which correctly refuses an unresolved answer target.
        tg=GroupTransitions(ti,self.f.binary.with_name('group-transitions'),temporary);state=tg.live()
        payload=package_carrier(encode_event(event),'Pending answer','<p>Pending answer</p>',max_wire_bytes=1048576,max_parts=64,max_decoded_bytes=1048576)
        pending=call(self.f.binary,op='send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=temporary['key'],application=payload.hex())
        self.assertEqual(gb.receiver.receive(bytes.fromhex(pending['wire']),time=self.time,trust_policy='allow-unverified')['status'],'pending')
        self.pending_raw=encode_event(event)
        accepted=dict(event,principal=self.f.creator['principal'],event='8'*32,operation=dict(kind='message',text='Previously accepted history',replyTo=[]))
        if accepted['version']=='3':accepted['presentation']=dict(subject='Earlier message',authoredAt='',to=[target['principal']],cc=[])
        accepted_raw=encode_event(accepted);source=self.selected[self.f.devices.index(self.f.creator)]['mailbox']
        accepted_wire=self.sender.prepare('acceptedhistory',accepted_raw,key=self.f.creator['key'],envelope_sender=source,recipients=[destination],time=self.time)
        from mls_mime import unpack
        self.assertEqual(gb.receiver.receive(unpack(accepted_wire),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        self.accepted_raw=accepted_raw
        TransitionSupport(ga).confirm(proof,time=self.time)
        allowed={(final['identity'],final['key'])}
        added=ga.prepare([final['package']]);ga.decide(added,allowed=allowed,time=self.time)
        first=json.loads(ga.db.execute('SELECT state FROM gt_decision WHERE digest=?',(added,)).fetchone()[0])
        bundle=json.loads(json.dumps(self.f.bundles[temporary['principal']]))
        state=json.loads(base64.b64decode(bundle['states'][0]['payload']))
        signer=next(d for d in self.f.devices if d['principal']==temporary['principal'] and d['device']==state['signer'])
        state.update(record='9'*32,revision='2',previous=[self.f.heads[temporary['principal']]],revoked=[temporary['device']],bindings=[b for b in state['bindings'] if b['device']!=temporary['device']])
        raw=encode_event(state);bundle['states'].insert(0,dict(payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,signer,'email-next/identity-state/v0',raw)))
        for store in (self.identity,identity):self.assertEqual(store.accept_successor(encode_event(bundle),candidate_digest=hashlib.sha256(raw).hexdigest(),time=self.time)['status'],'accepted-unverified')
        removed=ga.prepare_removal([dict(identity=temporary['identity'],key=temporary['key'])]);ga.decide(removed,allowed=set(),time=self.time)
        last=json.loads(ga.db.execute('SELECT state FROM gt_decision WHERE digest=?',(removed,)).fetchone()[0])
        return ga,gb,start,[encode_transition(first),encode_transition(last)],allowed,final,proof

    def exercise(self,version):
        self.configure(version)
        ga,gb,start,carriers,allowed,final,proof=self.setup_chain();old=gb.live()
        spool=MailSpool(__import__('pathlib').Path(self.temp.name)/'delivery-recovery.sqlite');self.addCleanup(spool.close)
        from historical_release import HistoricalRelease
        from sender_worker import SenderWorker
        source=self.selected[self.f.devices.index(self.f.creator)]['mailbox'];destination=self.selected[self.f.devices.index(gb.device)]['mailbox']
        items=HistoricalRelease(self.sender,self.history).prepare('recoverymail',start,key=self.f.creator['key'],target_identity=gb.device['identity'],target_key=gb.device['key'],mailbox=destination,envelope_sender=source,time=self.time)
        with SenderWorker(self.sender) as worker:
            for item in items:
                smtp=LocalSMTP();self.assertEqual(worker.submit_historical(item,history=self.history,port=smtp.port,time=self.time)['state'],'accepted');smtp.done();spool.append(smtp.wire)
        recovery=RecoveryRetrieval(gb,{'mail':spool});recovery.schedule('delivery',allowed=allowed,policy=POLICY);recovery.collect()
        # A genuinely signed narrower tuple is not support for this profile.
        wrong=json.loads(proof);v=json.loads(base64.b64decode(wrong['payload']));v['applications'][0]['operations']=['message'];raw=encode_event(v)
        wrong.update(payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,final,'email-next/passive-discovery/v'+v['version'],raw))
        recovery.add_support(encode_event(wrong))
        self.assertEqual(recovery.run('delivery',time=self.time)['status'],'waiting-for-support');self.assertEqual(gb.live(),old)
        expired=json.loads(proof);v=json.loads(base64.b64decode(expired['payload']));v.update(notBefore='0',notAfter='1');raw=encode_event(v)
        expired.update(payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,final,'email-next/passive-discovery/v'+v['version'],raw))
        recovery.add_support(encode_event(expired))
        self.assertEqual(recovery.run('delivery',time=self.time)['status'],'waiting-for-support');self.assertEqual(gb.live(),old)
        recovery.add_support(proof)
        # Structural checks reject role or presentation changes before install.
        staged=gb.invoke('receive',old,wire=__import__('transition_carrier').parse(carriers[0])[1].hex())
        for change in ('role','presentation'):
            altered=json.loads(json.dumps(staged));ctx=json.loads(bytes.fromhex(altered['before']['context']))
            if change=='role':ctx['delivery']['recipient']='enp0:'+'f'*64
            else:ctx['application']['envelopeVersion']='1'
            altered['after']['context']=encode_event(ctx).hex()
            if change=='role':altered['before']['context']=altered['after']['context']
            with self.assertRaises(ValueError):recovery.recovery._structure(altered,allowed,self.time)
        self.assertEqual(gb.live(),old)
        # Final proof comes from the original signed assertion, never retroactive authority.
        with patch('remediation_support.install',side_effect=RuntimeError('final install crash')):
            with self.assertRaisesRegex(RuntimeError,'final install crash'):recovery.run('delivery',time=self.time)
        self.assertEqual(gb.live(),old)
        for table in ('mls_remediation_receipt','mls_remediation_step','gt_receive'):self.assertEqual(gb.db.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
        result=recovery.run('delivery',time=self.time)
        self.assertEqual(result['status'],'accepted-remediation');self.assertEqual(gb.live()['snapshot'],ga.live()['snapshot'])
        self.assertEqual(json.loads(bytes.fromhex(gb.live()['snapshot']['context']))['delivery'],self.f.context['delivery'])
        self.assertEqual(recovery.run('delivery',time=self.time),result)
        with patch('mls_receive.worker_call',side_effect=AssertionError('No decryption during reevaluation')):
            states=gb.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')['states']
        self.assertTrue(states[hashlib.sha256(self.pending_raw).hexdigest()].startswith('held:'))
        self.assertEqual(states[hashlib.sha256(self.accepted_raw).hexdigest()],'accepted')
        self.assertEqual(gb.db.execute('SELECT count(*) FROM contributions').fetchone()[0],1)
        self.assertEqual(gb.db.execute('SELECT application FROM mls_receives WHERE application=?',(self.accepted_raw,)).fetchone()[0],self.accepted_raw)
        self.assertEqual(gb.db.execute('SELECT application FROM mls_receives WHERE application=?',(self.pending_raw,)).fetchone()[0],self.pending_raw)
    def test_private5_smtp_spool_recovery(self):self.exercise('5')
    def test_managed6_smtp_spool_recovery(self):self.exercise('6')

if __name__=='__main__':unittest.main()
