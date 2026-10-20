"""Actual configured v2 designated-writer removal, not a consensus claim."""
import json
import unittest
from unittest.mock import patch
import test_group_removal as fixture
from provider_mls import call
from event_encoding import encode_event
from journal_reaction_view import derive_reaction_view

class ReactionRemovalTests(unittest.TestCase):
    application_profile=dict(envelopeVersion='1',operations=['message','reaction','reaction-withdraw'])
    setUp=fixture.RemovalTests.setUp
    tearDown=fixture.RemovalTests.tearDown
    store=fixture.RemovalTests.store
    prepared=fixture.RemovalTests.prepared
    remove=fixture.RemovalTests.remove
    def test_default_retention_rejects_delayed_target_and_holds_pending_reaction(self):
        audience=sorted([self.a['principal'],self.b['principal'],self.c['principal']])
        target=dict(version='1',purpose='contribution',event='5'*32,conversation='2'*32,principal=self.b['principal'],audience=audience,disclosures=[],operation=dict(kind='message',text='The original message.',replyTo=[]))
        ref={k:target[k] for k in ('principal','conversation','event')}
        reaction=dict(version='1',purpose='contribution',event='6'*32,conversation='2'*32,principal=self.c['principal'],audience=audience,disclosures=[],operation=dict(kind='reaction',target=ref,emoji='👍'))
        def send(g,d,event):
            state=g.live();return call(self.provider,op='send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=d['key'],application=encode_event(event).hex())
        sent=send(self.gc,self.c,reaction);target_wire=send(self.gb,self.b,target)
        self.assertEqual(self.ga.receiver.receive(bytes.fromhex(sent['wire']),time=self.time,trust_policy='allow-unverified')['status'],'pending')
        self.ga.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')
        self.remove(self.c)
        self.assertEqual(self.ga.identity.check_device(bytes.fromhex(self.c['identity']),bytes.fromhex(self.c['key']),role='send',time=self.time,trust_policy='allow-unverified')['status'],'authorized-unverified')
        rejected=self.ga.receiver.receive(bytes.fromhex(target_wire['wire']),time=self.time,trust_policy='allow-unverified')
        self.assertEqual(rejected['status'],'crypto-not-accepted')
        with patch('mls_receive.worker_call',side_effect=AssertionError('No re-decryption')):
            result=self.ga.receiver.reevaluate(time=self.time,trust_policy='allow-unverified')
        self.assertIn('held:membership-episode',result['states'].values())
        self.assertEqual(derive_reaction_view(self.ga.receiver.journal,ref)['active'],[])
        self.assertEqual(self.ga.db.execute('SELECT count(*) FROM contributions').fetchone()[0],0)
    def test_added_device_requires_explicit_exact_support(self):
        identifier=self.prepared()
        with self.assertRaisesRegex(ValueError,'support'):self.ga.decide(identifier,allowed=self.allowed,time=self.time)
        group=self.ga.live()['snapshot']['group'];agreement=self.ga.receiver.application_agreement
        agreement.configure_device(group,self.phone['identity'],self.phone['key'],dict(envelopeVersion='1',operations=['message']))
        with self.assertRaisesRegex(ValueError,'support'):self.ga.decide(identifier,allowed=self.allowed,time=self.time)
        agreement.configure_device(group,self.phone['identity'],self.phone['key'],self.application_profile)
        self.assertEqual(self.ga.decide(identifier,allowed=self.allowed,time=self.time),'accepted')
