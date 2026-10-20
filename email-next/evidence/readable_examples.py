"""Validate the readable MIME fixtures; no delivery or cryptographic claim."""
from pathlib import Path
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
import unittest

EXAMPLES = Path(__file__).resolve().parent.parent / 'examples'

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.words = []
        self.elements = []
        self.attributes = []
    def handle_starttag(self, tag, attrs):
        self.elements.append(tag)
        self.attributes.extend(attrs)
    def handle_data(self, data):
        self.words.append(data)

class ReadableExamples(unittest.TestCase):
    def read(self, name):
        raw = (EXAMPLES / name).read_bytes()
        self.assertNotIn(b'\n', raw.replace(b'\r\n', b''))
        self.assertTrue(all(len(line) <= 998 for line in raw.split(b'\r\n')))
        message = BytesParser(policy=policy.default).parsebytes(raw)
        self.assertTrue(all(not part.defects for part in message.walk()))
        self.assertEqual(message.get_content_type(), 'multipart/alternative')
        parts = list(message.iter_parts())
        self.assertEqual([p.get_content_type() for p in parts], ['text/plain','text/html'])
        self.assertTrue(all(p.get_content_charset() == 'utf-8' for p in parts))
        plain, html = [p.get_content() for p in parts]
        parsed = Text(); parsed.feed(html)
        self.assertFalse(set(parsed.elements) & {'script','form','input','button','iframe','object'})
        self.assertFalse(any(k.startswith('on') or k in {'src','action'} for k,v in parsed.attributes))
        return message, plain, ' '.join(parsed.words)

    def test_question_has_equivalent_visible_choices_and_instructions(self):
        _, plain, html = self.read('question.eml')
        for phrase in ['Which day works for our meeting?', 'Tuesday', 'Thursday', 'Location preference (optional)', 'Reading this message sends nothing.']:
            self.assertIn(phrase,plain);self.assertIn(phrase,html)

    def test_answer_retains_unanswered_distinction_and_reply_target(self):
        question,_,_=self.read('question.eml')
        answer,plain,html=self.read('answer.eml')
        self.assertEqual(answer['In-Reply-To'],question['Message-ID'])
        self.assertEqual(answer['References'],question['Message-ID'])
        self.assertNotEqual(answer['Message-ID'],question['Message-ID'])
        for phrase in ['Thursday','unanswered','does not assert a cryptographically authenticated form submission']:
            self.assertIn(phrase.lower(),plain.lower());self.assertIn(phrase.lower(),html.lower())

if __name__ == '__main__':
    unittest.main()
