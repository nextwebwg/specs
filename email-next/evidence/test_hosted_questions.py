import json
import unittest
from unittest.mock import patch
from event_encoding import encode_event,serialize_json,decode_event,MAX_EVENT_OCTETS
from hosted_projection import hosted_source_text
from hosted_reply_export import HostedReplyExporter
from journal_button_view import derive_button_view
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
import test_hosted_disclosure

class HostedQuestionTests(unittest.TestCase):
    setUpClass=classmethod(test_hosted_disclosure.DisclosureTests.setUpClass.__func__)
    tearDownClass=classmethod(test_hosted_disclosure.DisclosureTests.tearDownClass.__func__)
    setUp=test_hosted_disclosure.DisclosureTests.setUp
    stop=test_hosted_disclosure.DisclosureTests.stop
    prepare_original=test_hosted_disclosure.DisclosureTests.prepare_original
    def plan(self,**kw):return test_hosted_disclosure.DisclosureTests.plan(self,question=True,**kw)
    def test_joined_question_full_projection_and_no_answer_inference(self):
        self.plan();self.bound.create('a'*32,'manager',time=self.f.time)
        code,body=self.client._exchange('GET','/v0/grants/'+'b'*32+'/content',None,self.secret)
        self.assertEqual(code,200);text=json.loads(body)['content']['text'];self.assertEqual(text,hosted_source_text(self.application))
        for expected in ['Which time? 日本語','1. <img src=x onerror=alert(1)> 朝','2. Evening & late','Opening this message submits nothing.','Author-declared external sharing:']:self.assertIn(expected,text)
        smtp=LocalSMTP()
        with SenderWorker(self.f.senders[0]) as worker:worker.submit('hostedoriginal',port=smtp.port,time=self.f.time)
        smtp.done();self.f.receive(2,smtp.wire)
        ref={k:self.original[k] for k in ('principal','conversation','event')}
        self.assertEqual(derive_button_view(self.f.senders[2].receiver.journal,ref)['heads'],[])
        for index,answer in enumerate(['1',self.original['operation']['options'][0]['label']]):
            op=str(index+1)*32;raw=encode_event(dict(version='0',purpose='hosted-holder-reply',operation=op,text=answer))
            self.assertEqual(self.client._exchange('POST','/v0/grants/'+'b'*32+'/replies',raw,self.secret)[0],200)
            evidence=HostedReplyExporter(self.client).fetch('a'*32,op,'manager')['evidence']
            observation=self.adapter.prepare(evidence,key=self.f.devices[0]['key'],envelope_sender='author@example.invalid',recipients=['reader@example.invalid'],time=self.f.time)
            smtp=LocalSMTP()
            with SenderWorker(self.f.senders[0]) as worker:worker.submit_observer(observation['delivery'],self.hosted,port=smtp.port,time=self.f.time)
            smtp.done();self.assertIn('accepted',self.f.receive(2,smtp.wire)[1]['states'].values())
        events=[decode_event(r['octets'][0])['value'] for r in self.f.senders[2].receiver.journal.snapshot('2'*32) if r['state']=='recorded']
        self.assertEqual(sum(e['operation']['kind']=='answer' for e in events),0)
        self.assertEqual(sum(e['operation']['kind']=='hosted-holder-observation' for e in events),2)
        self.assertEqual(derive_button_view(self.f.senders[2].receiver.journal,ref)['heads'],[])
    def test_changed_option_or_formatter_cannot_keep_heading_only_binding(self):
        self.plan(prepare=False)
        changed=json.loads(self.application);changed['operation']['options'][0]['label']='Different label'
        with self.assertRaisesRegex(ValueError,'content binding'):self.plans.authorize(encode_event(changed),{'a'*32:self.route})
        changed=json.loads(self.application);changed['operation']['options'].reverse()
        with self.assertRaisesRegex(ValueError,'content binding'):self.plans.authorize(encode_event(changed),{'a'*32:self.route})
        self.prepare_original()
        with patch('hosted_disclosure.hosted_source_text',return_value=self.configuration['content']['text']+'Changed instruction'):
            with self.assertRaisesRegex(ValueError,'formatter'):self.bound.create('a'*32,'manager',time=self.f.time)
        self.assertEqual(self.store.lookup('a'*32,'manager')[0],404)
    def test_projection_overflow_holds_without_truncating_choices(self):
        self.plan(prepare=False);question=json.loads(self.application);question['event']='e'*32;question['operation']['text']=''
        baseline=len(encode_event(question));question['operation']['text']='x'*(MAX_EVENT_OCTETS-baseline)
        exact=encode_event(question);self.assertEqual(len(exact),MAX_EVENT_OCTETS)
        text=hosted_source_text(exact);self.assertIn('2. Evening & late',text)
        request=dict(self.request,operation='c'*32,grant='d'*32,contribution={k:question[k] for k in ('principal','conversation','event')},content={'kind':'text','text':text})
        self.assertGreater(len(serialize_json(request)),MAX_EVENT_OCTETS)
        with self.assertRaises(ValueError):self.hosted.retain(encode_event(request))
        self.assertEqual(self.store.lookup('c'*32,'manager')[0],404)

if __name__=='__main__':unittest.main()
