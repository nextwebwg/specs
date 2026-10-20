"""Sample topics keep real source messages and exact reply relationships."""
import unittest
from email import policy
from email.parser import BytesParser
from client_flow_server import Demo
from conversation_demo_samples import populate


class ConversationSamples(unittest.TestCase):
    def test_topics_have_distinct_roots_and_late_reply_keeps_original_parent(self):
        demo=Demo()
        try:
            populate(demo)
            state=demo.state('sam')
            self.assertEqual(len(state['timeline']),9)
            targets=state['replyTargets']
            self.assertEqual(sum(t['parent'] is None for t in targets),3)
            self.assertEqual(targets[-1]['parent'],targets[0]['id'])
            for row,target in zip(state['timeline'],targets):
                with self.subTest(text=row['text']):
                    message=BytesParser(policy=policy.default).parsebytes(demo.reply_originals[row['id']])
                    self.assertEqual(message.get_content(),row['text'])
                    parent=demo.reply_targets.get(target['parent'])
                    self.assertEqual(str(message.get('In-Reply-To','')),parent['messageId'] if parent else '')
                    self.assertFalse(row['protected'])
            self.assertEqual(state['threads'][0]['id'],'sam')
        finally:
            demo.close()
