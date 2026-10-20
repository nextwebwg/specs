import unittest
from event_encoding import encode_event
from passive_discovery import decode_assertion,RICH_DOMAIN
from application_tuples import validate_tuples,covers,intersect
from test_passive_discovery import assertion
class RichDiscovery(unittest.TestCase):
    def test_new_exact_version_and_old_rejection(self):
        tuple=dict(envelopeVersion='1',payload='mime-rich-v0',ordering='fixed-roster-v0',operations=['rich-message'])
        value=assertion();value.update(version='3',applications=[tuple]);raw=encode_event(value)
        self.assertEqual(decode_assertion(raw)['signature_input'],RICH_DOMAIN+len(raw).to_bytes(4,'big')+raw)
        self.assertTrue(covers([tuple],{k:v for k,v in tuple.items() if k!='ordering'},tuple['ordering'],version='3'))
        self.assertEqual(intersect([[tuple],[tuple]],version='3'),[tuple])
        with self.assertRaises(ValueError):validate_tuples([tuple])
        value['version']='2'
        with self.assertRaises(ValueError):decode_assertion(encode_event(value))
    def test_old_payload_does_not_gain_rich_operations(self):
        for payload in ('raw-event-v0','mime-contribution-v0'):
            with self.assertRaises(ValueError):validate_tuples([dict(envelopeVersion='1',payload=payload,ordering='fixed-roster-v0',operations=['rich-message'])],version='3')
