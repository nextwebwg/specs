import unittest
import test_designated_initial as fixtures
class TupleInvitationTests(unittest.TestCase):
    selected_payload='mime-contribution-v0'
    setUp=fixtures.DesignatedInitialTests.setUp
    tearDown=fixtures.DesignatedInitialTests.tearDown
    prepare=fixtures.DesignatedInitialTests.prepare
    create=fixtures.DesignatedInitialTests.create
    test_signed_smtp_initial_body_add_and_established_welcome=fixtures.DesignatedInitialTests.test_actual_smtp_initial2_then_add_uses_original_signed_proofs
    test_wrong_domain_and_atomic_replay=fixtures.DesignatedInitialTests.test_wrong_domain_rolls_back_then_exact_retry_preserves_admission
    def replace_tuples(self,tuples):
        import base64,json,uuid
        from provider_mls import sign
        from event_encoding import encode_event
        from passive_discovery import decode_passive_discovery
        for i,(device,choice) in enumerate(zip(self.f.devices,self.f.selected)):
            wrapper=json.loads(choice['wrapper']);value=json.loads(base64.b64decode(wrapper['payload']));value.update(record=uuid.uuid4().hex,applications=tuples)
            payload=encode_event(value);wrapper.update(payload=base64.b64encode(payload).decode(),signature=sign(self.f.binary,device,'email-next/passive-discovery/v2',payload));raw=encode_event(wrapper);d=decode_passive_discovery(raw)
            for store in [self.sender.associations,self.receiver_fixture.admission.associations]:store.observe_validated_batch([dict(assertion=payload,signature=d['signature'],signingKey=bytes.fromhex(device['key']),outerFrom=[choice['mailbox']],sourceId='tuple',parserRevision='test',observedAt=self.f.time['earliest'])])
            self.f.selected[i]=dict(choice,wrapper=raw,digest=d['assertion']['digest'])
    def test_fixed_context3_has_explicit_tuple_and_no_designated_opt_in(self):
        from invitation_mime import select
        from event_encoding import encode_event
        self.context=dict(self.context,ordering={'kind':'fixed-roster-v0'});self.f.context=self.context
        self.replace_tuples([dict(self.context['application'],ordering='fixed-roster-v0')])
        wire=self.prepare(designated=False)
        self.assertEqual(self.receiver_fixture.accept(select(wire),expected_context=encode_event(self.context))['status'],'admitted-unverified')
        self.assertEqual(self.f.identity.db.execute('SELECT count(*) FROM mls_configured_context').fetchone()[0],0)
    def test_other_payload_tuple_cannot_authorize_selected_mime(self):
        self.replace_tuples([dict(self.context['application'],payload='raw-event-v0',ordering='designated-member-v0')])
        with self.assertRaisesRegex(ValueError,'intersection'):self.prepare(designated=True)
        self.assertEqual(self.identity.db.execute('SELECT count(*) FROM mls_checkpoint').fetchone()[0],0)
