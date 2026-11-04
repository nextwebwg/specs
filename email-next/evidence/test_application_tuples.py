"""Exact tuple grammar/intersection and actual domain-separated Ed25519 checks."""
import copy
import json
import subprocess
from pathlib import Path
import base64
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from event_encoding import encode_event
from passive_discovery import decode_assertion,TUPLE_DOMAIN,APPLICATION_DOMAIN,DOMAIN
from application_tuples import validate_tuples,covers,intersect
from test_passive_discovery import assertion

HERE=Path(__file__).parent

def item(payload='mime-contribution-v0',ordering='fixed-roster-v0',operations=None):
    return dict(envelopeVersion='1',payload=payload,ordering=ordering,operations=operations or ['message'])

class ApplicationTuples(unittest.TestCase):
    def value(self):
        v=assertion();v.update(version='2',applications=[item()]);return v
    def test_actual_signature_dispatch_and_old_domain_rejection(self):
        raw=encode_event(self.value());key=Ed25519PrivateKey.generate();public=key.public_key().public_bytes_raw().hex()
        self.assertEqual(decode_assertion(raw)['signature_input'],TUPLE_DOMAIN+len(raw).to_bytes(4,'big')+raw)
        for domain,expected in [(TUPLE_DOMAIN,'signature-valid'),(APPLICATION_DOMAIN,'invalid-proof'),(DOMAIN,'invalid-proof')]:
            proof=key.sign(domain+len(raw).to_bytes(4,'big')+raw).hex()
            request=dict(version='2',payload=base64.b64encode(raw).decode(),signature=proof,key=public)
            result=subprocess.run(['node',str(HERE/'check-passive-discovery.mjs')],input=json.dumps(request),text=True,capture_output=True,check=True)
            self.assertEqual(json.loads(result.stdout)['status'],expected)
    def test_exact_keys_types_and_order(self):
        bad=[dict(item(),extra='x'),dict(item(),ordering=['fixed-roster-v0']),dict(item(),payload='mime'),dict(item(),operations=['message','answer']),dict(item(),operations=['message','message']),dict(item(),operations=[]),dict(item('raw-event-v0'),operations=['attachment-message'])]
        for descriptor in bad:
            v=self.value();v['applications']=[descriptor]
            with self.subTest(descriptor=descriptor),self.assertRaises(ValueError):decode_assertion(encode_event(v))
        for tuples in ([item(),item()],[item('raw-event-v0'),item()]):
            with self.assertRaises(ValueError):validate_tuples(tuples)
    def test_no_payload_ordering_or_device_cross_product(self):
        a=[item(operations=['attachment-message','message']),item('raw-event-v0',operations=['message','question'])]
        b=[item(operations=['message','question']),item('raw-event-v0',operations=['message'])]
        self.assertEqual(intersect([a,b]),[item(),item('raw-event-v0')])
        self.assertFalse(covers(a,dict(envelopeVersion='1',payload='mime-contribution-v0',operations=['question']),'fixed-roster-v0'))
        self.assertEqual(intersect([[item(ordering='designated-member-v0')],[item()]]),[])
        self.assertEqual(intersect([[item(operations=['question'])],[item(operations=['message'])]]),[])
    def test_old_schema_not_broadened_and_empty_is_no_support(self):
        for version in ('0','1'):
            v=self.value();v['version']=version
            with self.assertRaises(ValueError):decode_assertion(encode_event(v))
        v=self.value();v['applications']=[];v['features']=[]
        self.assertEqual(decode_assertion(encode_event(v))['value']['applications'],[])
        self.assertEqual(intersect([[],[item()]]),[])
        with self.assertRaises(ValueError):intersect([])
    def test_indexed_reply_does_not_extend_historical_tuple_versions(self):
        for version in ('2','3','4','5','6','7'):
            descriptor = dict(envelopeVersion='3' if version in ('5','6','7') else '2' if version=='4' else '1',
                              payload='mime-rich-v0' if version!='2' else 'mime-contribution-v0',
                              ordering='endpoint-quorum-v0' if version in ('6','7') else 'fixed-roster-v0',
                              operations=['message'])
            with self.subTest(version=version):
                self.assertEqual(validate_tuples([descriptor],version=version),[descriptor])
                original=copy.deepcopy(descriptor)
                expanded=dict(descriptor,operations=['message','reply-message'])
                with self.assertRaises(ValueError):validate_tuples([expanded],version=version)
                self.assertEqual(descriptor,original)

    def test_context3_exact_payload_agreement_old_context_unchanged(self):
        context=dict(version='3',purpose='conversation-context',conversation='1'*32,profile='mls-1-0001',administrators=['enp0:'+'a'*64],application=dict(envelopeVersion='1',payload='mime-contribution-v0',operations=['attachment-message','message']),ordering={'kind':'fixed-roster-v0'})
        script="import {validateConversationContext as v} from './conversation-context.mjs';let s='';for await(const c of process.stdin)s+=c;const a=JSON.parse(s);process.stdout.write(JSON.stringify(v(a.context,{configuredApplication:a.agreement})));"
        def check(c,a):
            r=subprocess.run(['node','--input-type=module','-e',script],cwd=HERE,input=json.dumps(dict(context=c,agreement=a)),text=True,capture_output=True,check=True);return json.loads(r.stdout)
        self.assertTrue(check(context,context['application']))
        self.assertFalse(check(context,dict(context['application'],payload='raw-event-v0')))
        self.assertFalse(check(dict(context,version='2'),context['application']))
        old=copy.deepcopy(context);old['version']='2';old['application']={'envelopeVersion':'1','operations':['hosted-holder-observation','message']}
        self.assertTrue(check(old,old['application']))
