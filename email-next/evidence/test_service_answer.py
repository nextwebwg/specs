import copy
import hashlib
import json
import unittest
from event_encoding import encode_event
from service_answer import decode_request, bind_result

class ServiceAnswerTests(unittest.TestCase):
    def setUp(self):
        self.service='https://schedule.example'
        self.request=dict(version='0', purpose='service-answer-submit', submission='1'*32,
                          action='2'*32, question=dict(principal='enp0:'+'3'*64,
                          conversation='4'*32,event='5'*32), principal='enp0:'+'6'*64,
                          option='7'*32,replaces=[])
        self.raw=encode_event(self.request)
        self.result=dict(self.request,purpose='service-answer-result',service=self.service,
                         requestDigest=hashlib.sha256(self.raw).hexdigest(),outcome='confirmed',reason='applied')
    def check(self, value):
        return bind_result(encode_event(value),self.raw,expected_service=self.service)
    def test_valid_binding_does_not_claim_authentication(self):
        self.assertEqual(self.check(self.result)['status'],'bound-unverified')
        reformatted=json.dumps(self.result,indent=2).encode()
        self.assertEqual(bind_result(reformatted,self.raw,expected_service=self.service)['value'],self.result)
    def test_every_request_binding_is_checked(self):
        changes={'service':'https://other.example','submission':'8'*32,'action':'8'*32,
                 'principal':'enp0:'+'8'*64,'option':'8'*32,'replaces':['8'*32],
                 'question':dict(self.request['question'],event='8'*32),'requestDigest':'0'*64}
        for key,value in changes.items():
            with self.subTest(key=key),self.assertRaises(ValueError):self.check(dict(self.result,**{key:value}))
    def test_equal_parsed_requests_have_distinct_byte_bindings(self):
        alternate=json.dumps(self.request,indent=2).encode()
        self.assertEqual(decode_request(alternate)['value'],self.request)
        with self.assertRaises(ValueError):bind_result(encode_event(self.result),alternate,expected_service=self.service)
    def test_invalid_receipts_and_strict_bytes(self):
        for changes in [{'outcome':'confirmed','reason':'processing'}, {'outcome':'unknown'},
                        {'reason':[]}, {'extra':'ignored?'}, {'version':'1'}, {'purpose':'service-answer-submit'}]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):self.check(dict(self.result,**changes))
        raw=encode_event(self.result)
        duplicate=b'{"outcome":"pending",'+raw[1:]
        with self.assertRaises(ValueError):bind_result(duplicate,self.raw,expected_service=self.service)
        for key in self.result:
            changed=copy.deepcopy(self.result);del changed[key]
            with self.subTest(missing=key),self.assertRaises(ValueError):self.check(changed)
    def test_request_ids_replacement_and_unknown_fields(self):
        for changes in [{'submission':'0'*32},{'principal':'person@example.com'},
                        {'replaces':['1'*32]}, {'replaces':['8'*32,'9'*32]}, {'extra':'no'}, {'option':True}]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):decode_request(encode_event(dict(self.request,**changes)))
