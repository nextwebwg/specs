import json
import unittest
from event_encoding import encode_event
from pairing_rendezvous import descriptor,transport_digest,check_return


class RendezvousQR(unittest.TestCase):
    def setUp(self):
        self.offer=dict(version='0',purpose='pairing-rendezvous-offer',service='https://relay.example',prefix='https://relay.example/pair/',session='1'*64,token='A'*43,offerDigest='2'*64,anchorBundleDigest='3'*64,notAfter='1800000000')
        self.raw=json.dumps(self.offer,indent=2).encode()
        self.reply=dict(version='0',purpose='pairing-rendezvous-request',service=self.offer['service'],prefix=self.offer['prefix'],session=self.offer['session'],transportDigest=transport_digest(self.raw),offerDigest=self.offer['offerDigest'],requestDigest='4'*64,notAfter=self.offer['notAfter'])

    def test_exact_original_bytes_bind_the_return_without_becoming_approval(self):
        raw=encode_event(self.reply);result=check_return(raw,original_offer_qr=self.raw)
        self.assertEqual(result['status'],'rendezvous-wire-only');self.assertIs(result['original'],raw)
        with self.assertRaises(ValueError):check_return(raw,original_offer_qr=encode_event(self.offer))

    def test_changed_origin_prefix_session_offer_or_lease_cannot_retarget(self):
        for change in (dict(service='https://other.example',prefix='https://other.example/pair/'),dict(prefix='https://relay.example/other/'),dict(session='5'*64),dict(offerDigest='6'*64),dict(notAfter='1800000001')):
            with self.subTest(change=change),self.assertRaises(ValueError):check_return(encode_event(self.reply|change),original_offer_qr=self.raw)

    def test_unknown_fields_short_commitments_tokens_and_unsafe_routes_rejected(self):
        for change in (dict(token='short'),dict(session='0'*64),dict(offerDigest='short'),dict(prefix='https://other.example/pair/'),dict(prefix='https://relay.example/pair/?token=x'),dict(approve=True),dict(notAfter='01')):
            with self.subTest(change=change),self.assertRaises(ValueError):descriptor(encode_event(self.offer|change))

    def test_duplicate_names_and_payload_budget_precede_acceptance(self):
        for raw in (b'{"version":"0",'+encode_event(self.offer)[1:],b' '*2049):
            with self.assertRaises(ValueError):descriptor(raw)


if __name__=='__main__':unittest.main()
