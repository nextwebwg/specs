import base64
import json
import unittest
from event_encoding import encode_event, EventLimitExceeded, MAX_EVENT_OCTETS
from passive_discovery import decode_assertion, decode_passive_discovery, assertion_time_status, mailbox_syntax, canonical_base64, DOMAIN


def assertion():
    return dict(version='0', purpose='passive-discovery', record='1'*32,
                principal='enp0:'+'a'*64, device='end0:'+'b'*64, state='c'*64,
                binding='d'*64, mailbox='Alice+tag@example.com', notBefore='10',
                notAfter='100', features=['mls-1-0001'], keyPackage=[])


def wrapper(raw=None):
    # Deliberately incomplete identity record demonstrates syntax-only boundary.
    record=encode_event(dict(version='0',purpose='identity-state',principal='enp0:'+'a'*64))
    return dict(payload=base64.b64encode(raw if raw is not None else encode_event(assertion())).decode(),signature='0'*128,
                identity=dict(version='0',purpose='identity-bundle',principal='enp0:'+'a'*64,
                              states=[dict(payload=base64.b64encode(record).decode(),signature='0'*128)],bindings=[]))


class PassiveDiscoveryTests(unittest.TestCase):
    def test_exact_bytes_and_signature_domain_survive_wrapper_changes(self):
        raw=json.dumps(assertion(),indent=2).encode()
        a=decode_passive_discovery(encode_event(wrapper(raw)))
        b=decode_passive_discovery(json.dumps(wrapper(raw),indent=3).encode())
        self.assertEqual(a['assertion'],b['assertion'])
        self.assertEqual(a['assertion']['signature_input'],DOMAIN+len(raw).to_bytes(4,'big')+raw)
        self.assertEqual(a['assertion']['octets'],raw)
        self.assertNotEqual(a['assertion']['digest'],decode_assertion(encode_event(assertion()))['digest'])
        self.assertEqual(a['status'],'syntax-only-unverified')

    def test_schema_purpose_identifier_and_time_substitution(self):
        for field,bad in [('purpose','contribution'),('version','1'),('record','0'*32),('principal','end0:'+'a'*64),('device','end0:'+'0'*64),('state','G'*64),('notBefore','01'),('notAfter',str(2**64)),('notAfter','9'),('extra','x')]:
            with self.subTest(field=field,bad=bad):
                value=assertion();value[field]=bad
                with self.assertRaises(ValueError):decode_assertion(encode_event(value))
        value=assertion();del value['binding']
        with self.assertRaises(ValueError):decode_assertion(encode_event(value))

    def test_longer_signed_advertisement_retains_its_own_expiry(self):
        value=assertion();value['notAfter']='1209610'
        parsed=decode_assertion(encode_event(value))
        self.assertEqual(assertion_time_status(parsed,earliest='1209610',latest='1209610'),'within-asserted-interval')
        self.assertEqual(assertion_time_status(parsed,earliest='1209611',latest='1209611'),'expired')
        # Syntax support does not bypass package, identity or binding validation.
        self.assertEqual(parsed['status'],'syntax-only-unverified')

    def test_wrapper_substitution_and_identity_scope(self):
        for mutate in [lambda v:v.update(extra='x'),lambda v:v.update(signature='A'*128),lambda v:v.update(payload='Zh=='),lambda v:v['identity'].update(principal='enp0:'+'c'*64),lambda v:v.update(identity=[])]:
            value=wrapper();mutate(value)
            with self.assertRaises(ValueError):decode_passive_discovery(encode_event(value))

    def test_duplicates_utf8_and_json_rules(self):
        raw=encode_event(assertion())
        for bad in [raw.replace(b'"version":"0"',b'"version":"0","\\u0076ersion":"0"'),b'\xef\xbb\xbf'+raw,raw+b'{}',b'{"x":null}',b'{"x":1}',b'{"x":"\xff"}',b'{"x":"\\ud800"}']:
            with self.assertRaises(ValueError):decode_assertion(bad)
        raw=encode_event(wrapper()).replace(b'"signature":',b'"payload":"e30=","signature":',1)
        with self.assertRaises(ValueError):decode_passive_discovery(raw)

    def test_bounds_before_schema_and_nested_record_decode(self):
        with self.assertRaises(EventLimitExceeded):decode_passive_discovery(b' '*(MAX_EVENT_OCTETS+1))
        with self.assertRaises(EventLimitExceeded):decode_assertion(b' '*(MAX_EVENT_OCTETS+1))
        with self.assertRaises(EventLimitExceeded):decode_assertion(b'{"x":'+b'['*32+b'false'+b']'*32+b'}')
        raw=encode_event(assertion());padded=raw+b' '*(MAX_EVENT_OCTETS-len(raw))
        self.assertEqual(len(decode_assertion(padded)['octets']),MAX_EVENT_OCTETS)
        value=wrapper();inner=b'{"x":'+b'['*32+b'false'+b']'*32+b'}'
        value['identity']['states'][0]['payload']=base64.b64encode(inner).decode()
        with self.assertRaises(EventLimitExceeded):decode_passive_discovery(encode_event(value))

    def test_base64_and_features_do_not_validate_mls(self):
        for invalid in ['Zh==','Zg','Zg===','Zg==\n','-_==']:
            with self.assertRaises(ValueError):canonical_base64(invalid)
        for features,packages in [(['unknown'],[]),(['mls-1-0001']*2,[]),([],['Zg==']),(['mls-1-0001'],['Zg==']*2),('mls-1-0001',[])]:
            value=assertion();value.update(features=features,keyPackage=packages)
            with self.assertRaises(ValueError):decode_assertion(encode_event(value))
        value=assertion();value['keyPackage']=['Zg==']
        self.assertEqual(decode_assertion(encode_event(value))['key_package_octets'],b'f')

    def test_mailbox_grammar_limits_and_alabel_dependency(self):
        for address in ['a..b@example.com','.a@example.com','a.@example.com','"a"@example.com','a@EXAMPLE.com','a@-example.com','a@example-.com','a@example.com.','a@[127.0.0.1]','a b@example.com','é@example.com','a@'+('x'*64)+'.com','a'*65+'@example.com','<a@example.com>','a@ex_ample.com']:
            with self.subTest(address=address):
                with self.assertRaises(ValueError):mailbox_syntax(address)
        self.assertEqual(mailbox_syntax('Alice+tag@example.com'),'syntax-valid')
        self.assertEqual(mailbox_syntax('a@xn--bcher-kva.example'),'a-label-validation-required')
        # Even an LDH-shaped but invalid A-label cannot acquire validated status.
        self.assertEqual(mailbox_syntax('a@xn--a.example'),'a-label-validation-required')
        maximal='a'*64+'@'+'b'*63+'.'+'c'*63+'.'+'d'*61
        self.assertEqual(len(maximal),254)
        self.assertEqual(mailbox_syntax(maximal),'syntax-valid')
        with self.assertRaises(ValueError):mailbox_syntax(maximal+'d')

    def test_uncertain_time_does_not_authorize(self):
        parsed=decode_assertion(encode_event(assertion()))
        for low,high,expected in [('10','100','within-asserted-interval'),('9','10','pending'),('100','101','pending'),('0','9','not-yet-valid'),('101','102','expired'),('20','10','pending'),(None,None,'pending')]:
            self.assertEqual(assertion_time_status(parsed,earliest=low,latest=high),expected)
