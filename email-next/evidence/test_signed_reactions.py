"""Signed per-device selection and versioned public initial carrier for reactions."""
import unittest
import test_application_invitation as fixture
from event_encoding import encode_event
from provider_mls import call
from journal_reaction_view import derive_reaction_view
from invitation_mime import package,select
from smtp_loopback import roundtrip

class SignedReactionTests(unittest.TestCase):
    selected_operations=['message','reaction','reaction-withdraw']
    setUp=fixture.ApplicationInvitationTests.setUp
    tearDown=fixture.ApplicationInvitationTests.tearDown
    wrap=fixture.ApplicationInvitationTests.wrap
    accept=fixture.ApplicationInvitationTests.accept
    def test_signed_initial_carrier_and_actual_protected_reaction(self):
        self.accept(select(roundtrip(package(self.raw))));f=self.f;a=f.devices[0]
        base=dict(version='1',purpose='contribution',conversation='2'*32,principal=a['principal'],audience=sorted(d['principal'] for d in f.devices),disclosures=[])
        message=dict(base,event='3'*32,operation=dict(kind='message',text='A signed agreement.',replyTo=[]));ref={k:message[k] for k in ('principal','conversation','event')}
        reaction=dict(base,event='4'*32,operation=dict(kind='reaction',target=ref,emoji='👍'))
        cp=self.group['checkpoint']
        for event in [message,reaction]:
            sent=call(f.binary,op='send',checkpoint=cp,key=a['key'],group=self.group['group'],application=encode_event(event).hex());cp=sent['checkpoint']
            self.admission.receiver.receive(bytes.fromhex(sent['wire']),time=f.time,trust_policy='allow-unverified')
            self.admission.receiver.reevaluate(time=f.time,trust_policy='allow-unverified')
        self.assertEqual(len(derive_reaction_view(self.admission.receiver.journal,ref)['active']),1)
    def test_complementary_support_cannot_form_reaction_agreement(self):
        import test_signed_application_admission as signed
        other=signed.SignedAdmissionTests();other.selected_operations=self.selected_operations
        other.advertised_operations={0:['message','reaction'],1:['message','reaction-withdraw']};other.setUp()
        try:
            with self.assertRaisesRegex(ValueError,'intersection'):other.accept()
            self.assertEqual(other.identity.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0],0)
        finally:other.tearDown()
