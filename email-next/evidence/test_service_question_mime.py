"""Service invitation MIME composition; no HTTP or authenticated delivery."""
import unittest
import test_button_mime as buttons
from event_encoding import encode_event
from mime_package import contribution_alternatives, inspect_contribution_package

class ServiceQuestionMimeTests(unittest.TestCase):
    def fixture(self):
        question,_=buttons.ButtonMimeTests().fixtures()
        question['operation']['kind']='service-question'
        question['operation']['serviceAction']=dict(version='0',purpose='service-answer-action',
            action='8'*32,question={k:question[k] for k in ['principal','conversation','event']},
            service='https://schedule.example',submit='https://schedule.example/submit',
            statusPrefix='https://schedule.example/status/',notBefore='1',retryUntil='100')
        return question
    def test_exact_event_and_inert_readable_service_destination(self):
        event=self.fixture()
        projection=buttons.ButtonMimeTests().project(event,event)
        self.assertEqual(projection['state'],'projected')
        original=encode_event(event)
        wire=contribution_alternatives(original,projection['text'],projection['html']).as_bytes()
        selected=inspect_contribution_package(wire,max_wire_bytes=32768,max_parts=4,max_decoded_bytes=16384)
        self.assertEqual(selected['event']['octets'],original)
        for name in ['plain','html']:
            text=selected[name].decode()
            self.assertIn('https://schedule.example',text)
            self.assertIn('Tuesday',text)
            self.assertIn('Thursday',text)
            self.assertNotIn('/submit',text)
            self.assertNotIn('/status/',text)
            self.assertNotIn('<button',text)
            self.assertNotIn('href=',text)
    def test_wrong_question_reference_cannot_generate_service_fallback(self):
        event=self.fixture()
        event['operation']['serviceAction']['question']['event']='9'*32
        self.assertEqual(buttons.ButtonMimeTests().project(event,event),{'state':'invalid'})
