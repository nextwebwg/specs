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

class SignedRemediation(unittest.TestCase):
    application=rich.RichGroupLifecycle.application
    setUp=rich.RichGroupLifecycle.setUp;tearDown=rich.RichGroupLifecycle.tearDown
    endpoint=rich.RichGroupLifecycle.endpoint;prepare=rich.RichGroupLifecycle.prepare;proof=rich.RichGroupLifecycle.proof
    def setup_chain(self):
        wires=self.prepare();wire=next(iter(wires.values()));p=parse(select(wire));target=next(d for d in self.f.devices if d['device']==p['value']['target']['device'] and d['principal']==p['value']['target']['principal'])
        identity,sender,selected=self.endpoint('recovering');admission=InitialRosterAdmission(identity,self.f.binary);admission.publish_local(target)
        choices=[dict(principal=d['principal'],device=d['device'],mailbox=c['mailbox'],generation=c['generation']) for d,c in zip(self.f.devices,selected)]
        admission.accept_message(select(wire),target=target,mailbox=p['value']['target']['mailbox'],allow_creator=self.f.creator['principal'],intended_principals=self.principals,intended_devices=self.devices,expected_context=encode_event(self.f.context),selections=choices,time=self.time,trust_policy='allow-unverified')
        ga=GroupTransitions(self.identity,self.f.binary.with_name('group-transitions'),self.f.creator);gb=GroupTransitions(identity,self.f.binary.with_name('group-transitions'),target)
        start=gb.live()['snapshot']['predecessor']
        temporary=next(d for d in self.f.devices if d is not target and d is not self.f.creator and d['device']!=json.loads(base64.b64decode(self.f.bundles[d['principal']]['states'][0]['payload']))['signer'])
        final=make_device(self.f.binary,9,10);proof=self.proof(final)
        for store in (self.identity,identity):self.assertEqual(store.observe(final['record'],first_contact_policy='allow-unverified')['status'],'pinned-unverified')
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
    def test_signed_final_proof_installed_atomically_and_retry_retains_selection(self):
        ga,gb,start,carriers,allowed,final,proof=self.setup_chain();recovery=RemediationChain(gb);old=gb.live()
        args=dict(allowed=allowed,time=self.time,expected_predecessor=start,policy=POLICY)
        with self.assertRaisesRegex(ValueError,'Actual final'):recovery.receive(carriers,**args)
        self.assertEqual(gb.live(),old)
        from unittest.mock import patch
        with patch('remediation_support.install',side_effect=RuntimeError('support install failure')):
            with self.assertRaisesRegex(RuntimeError,'support install failure'):recovery.receive(carriers,final_support=[proof],**args)
        self.assertEqual(gb.live(),old)
        for table in ('gt_receive','mls_remediation_step','mls_remediation_receipt'):self.assertEqual(gb.db.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
        self.assertEqual(gb.db.execute('SELECT count(*) FROM mls_membership_episode WHERE identity=?',(final['identity'],)).fetchone()[0],0)
        result=recovery.receive(carriers,final_support=[proof],**args)
        self.assertEqual(gb.live()['snapshot'],ga.live()['snapshot'])
        import group_instances
        origin=group_instances.current(gb.db,ga.live()['snapshot']['group'])['instance']
        self.assertEqual(gb.receiver.application_agreement.resolve(ga.live()['snapshot']['group'],[dict(identity=final['identity'],key=final['key'])],instance=origin),self.application)
        row=gb.db.execute('SELECT record FROM mls_support_records').fetchone();accepted=json.loads(row[0]);self.assertEqual(accepted['epoch'],result['epoch']);self.assertEqual(accepted['confirmation'],'atomic-remediation-final')
        event=dict(version='1',purpose='contribution',event='a'*32,conversation=self.f.context['conversation'],principal=self.f.creator['principal'],audience=sorted(self.principals+[final['principal']]),disclosures=[],operation=dict(kind='rich-message',text='Recovered conversation',html='<!doctype html><html><head></head><body><p>Recovered conversation</p></body></html>',presentation='html-css-v0',replyTo=[],manifest=[],embedded=[],attachments=[]))
        source=self.selected[self.f.devices.index(self.f.creator)]['mailbox']
        destination=self.selected[self.f.devices.index(gb.device)]['mailbox']
        wire=self.sender.prepare('recoveredrich',encode_event(event),key=self.f.creator['key'],envelope_sender=source,recipients=[destination],time=self.time)
        from mls_mime import unpack
        self.assertEqual(gb.receiver.receive(unpack(wire),time=self.time,trust_policy='allow-unverified')['applicationState'],'accepted')
        from unittest.mock import patch
        with patch('remediation_support.verify_passive_discovery',side_effect=AssertionError('No reselection')):self.assertEqual(recovery.receive(carriers,final_support=[proof],**args),result)
    def test_forged_or_wrong_profile_final_proof_rolls_back(self):
        ga,gb,start,carriers,allowed,final,proof=self.setup_chain();recovery=RemediationChain(gb);old=gb.live();wrapper=json.loads(proof);wrapper['signature']='0'*128
        with self.assertRaises(ValueError):recovery.receive(carriers,allowed=allowed,time=self.time,expected_predecessor=start,policy=POLICY,final_support=[encode_event(wrapper)])
        self.assertEqual(gb.live(),old);self.assertEqual(gb.db.execute('SELECT count(*) FROM mls_remediation_receipt').fetchone()[0],0)
        wrapper=json.loads(proof);value=json.loads(base64.b64decode(wrapper['payload']));value['applications'][0]['operations']=['message'];raw=encode_event(value);wrapper.update(payload=base64.b64encode(raw).decode(),signature=sign(self.f.binary,final,'email-next/passive-discovery/v3',raw))
        with self.assertRaises(ValueError):recovery.receive(carriers,allowed=allowed,time=self.time,expected_predecessor=start,policy=POLICY,final_support=[encode_event(wrapper)])
        self.assertEqual(gb.live(),old)

if __name__=='__main__':unittest.main()
