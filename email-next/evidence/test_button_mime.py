"""Button projections through MIME; no authentication or provider delivery claim."""
import json
from pathlib import Path
import subprocess
import unittest
from event_encoding import encode_event, decode_event
from mime_package import contribution_alternatives, inspect_contribution_package

HERE = Path(__file__).resolve().parent

class ButtonMimeTests(unittest.TestCase):
    def fixtures(self):
        alice, bob = 'enp0:' + 'a' * 64, 'enp0:' + 'b' * 64
        base = dict(version='0', purpose='contribution', conversation='1'*32, audience=[alice,bob])
        question = dict(base, principal=alice, event='2'*32, operation={
            'kind':'question', 'text':'Which day? / 何曜日',
            'options':[{'id':'3'*32,'label':'Tuesday'}, {'id':'4'*32,'label':'Thursday <afternoon>'}]})
        answer = dict(base, principal=bob, event='5'*32, operation={
            'kind':'answer', 'question':{k:question[k] for k in ['principal','event','conversation']},
            'option':'4'*32, 'replaces':[]})
        return question, answer

    def project(self, event, question):
        script = """import {projectReadable} from './readable-projection.mjs';
import {isPrincipalId} from './principal-identifiers.mjs';
let input='';for await(const chunk of process.stdin)input+=chunk;
const {event,question}=JSON.parse(input);
process.stdout.write(JSON.stringify(projectReadable(event,()=>({state:'valid',event:question}),isPrincipalId)));
"""
        return json.loads(subprocess.run(['node','--input-type=module','-e',script], cwd=HERE,
            input=json.dumps(dict(event=event,question=question)), text=True,
            capture_output=True, check=True).stdout)

    def test_question_and_answer_survive_mime_with_exact_event_bytes(self):
        question, answer = self.fixtures()
        for event in [question,answer]:
            with self.subTest(kind=event['operation']['kind']):
                projection=self.project(event,question)
                self.assertEqual(projection['state'],'projected')
                original=encode_event(event)
                wire=contribution_alternatives(original,projection['text'],projection['html']).as_bytes()
                selected=inspect_contribution_package(wire,max_wire_bytes=32768,max_parts=4,max_decoded_bytes=16384)
                self.assertEqual(selected['event']['octets'],original)
                self.assertEqual(decode_event(selected['event']['octets'])['value'],event)
                self.assertIn('何曜日',selected['plain'].decode('utf-8'))
                self.assertIn('&lt;afternoon&gt;',selected['html'].decode('utf-8'))
                self.assertNotIn('<button',selected['html'].decode('utf-8'))
                if event is answer:
                    self.assertNotIn('Tuesday',selected['plain'].decode('utf-8'))

    def test_missing_question_does_not_generate_guessed_fallback(self):
        _,answer=self.fixtures()
        self.assertEqual(self.project(answer,None)['state'],'invalid')

    def test_expanded_audience_is_refused_before_packaging(self):
        question,answer=self.fixtures()
        answer['audience']=[*answer['audience'],'enp0:'+'c'*64]
        self.assertEqual(self.project(answer,question),{'state':'audience-mismatch'})

    def test_downloadable_examples_match_projected_events_and_reply_headers(self):
        from email import policy
        from email.parser import BytesParser
        question, answer = self.fixtures()
        messages = []
        for kind, event in [('question', question), ('answer', answer)]:
            wire = (HERE.parent/'examples'/('button-'+kind+'.eml')).read_bytes()
            message = BytesParser(policy=policy.default).parsebytes(wire)
            messages.append(message)
            selected = inspect_contribution_package(wire, max_wire_bytes=32768,
                max_parts=4, max_decoded_bytes=16384)
            self.assertEqual(selected['event']['octets'], encode_event(event))
            projection = self.project(event, question)
            for part, source in [('plain', 'text'), ('html', 'html')]:
                self.assertEqual(selected[part].decode('utf-8').replace('\r\n', '\n').rstrip('\n'),
                    projection[source].rstrip('\n'))
            self.assertFalse(any(p.get_content_type() == 'message/rfc822' for p in message.walk()))
        self.assertEqual(str(messages[1]['In-Reply-To']), str(messages[0]['Message-ID']))
        self.assertEqual(str(messages[1]['References']), str(messages[0]['Message-ID']))
        self.assertNotEqual(str(messages[1]['Message-ID']), str(messages[0]['Message-ID']))
