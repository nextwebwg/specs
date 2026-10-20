import unittest
from email import policy
from email.parser import BytesParser
from client_flow_server import Demo

class MessageReactionTests(unittest.TestCase):
 def test_protected_answer_and_ordinary_rfc9078_are_separate(self):
  demo=Demo()
  try:
   state=demo.state();demo.answer(dict(action='replyAnswer',option=state['question']['options'][0]['id'],token=state['token']))
   state=demo.state();target=state['timeline'][-1]['reactionTarget'];control=next(c for c in state['reactionTargets'] if c['target']==target)
   self.assertEqual(control['mode'],'protected');demo.react(dict(action='answerReaction',target=target,token=control['token'],emoji='🎉'))
   state=demo.state();self.assertEqual(next(c for c in state['reactionTargets'] if c['target']==target)['groups'],[dict(emoji='🎉',count=1,mine=True)]);self.assertEqual(state['reactionGroups'],[])
   ordinary=demo.state('maya');target=ordinary['timeline'][0]['reactionTarget'];control=ordinary['reactionTargets'][0]
   request=dict(action='ordinaryReaction',target=target,token=control['token'],emoji='❤️',account='work');demo.react(request,thread_id='maya');demo.react(request,thread_id='maya')
   source=demo.ordinary_reaction_actions['ordinaryReaction']['source'];raw=demo.reply_originals[source];mail=BytesParser(policy=policy.default).parsebytes(raw)
   self.assertEqual(mail.get_content_disposition(),'reaction');self.assertEqual(mail['From'],'carol@work.example.invalid');self.assertEqual(mail['In-Reply-To'],ordinary['legacyQuestion']['id']);self.assertEqual(mail.get_content().strip(),'❤️')
   updated=demo.state('maya')['reactionTargets'][0];self.assertFalse(updated['canWithdraw']);self.assertEqual(updated['groups'],[dict(emoji='❤️',count=1,mine=True)])
   with self.assertRaises(ValueError):demo.react(request,thread_id='sam')
   with self.assertRaises(ValueError):demo.react(dict(request,action='withdraw'),withdraw=True,thread_id='maya')
   with self.assertRaises(ValueError):demo.react(dict(request,emoji='👍'),thread_id='maya')
  finally:demo.close()
 def test_rich_does_not_downgrade_and_attachment_is_protected(self):
  demo=Demo(mime=True,rich=True)
  try:
   state=demo.state();controls={c['target']:c for c in state['reactionTargets']}
   for card in state['richMessages']:self.assertEqual(controls[card['reactionTarget']]['mode'],'unavailable')
   target=state['attachments'][0]['reactionTarget'];control=controls[target];self.assertEqual(control['mode'],'protected')
   demo.react(dict(action='attachmentReaction',target=target,token=control['token'],emoji='👀'))
   self.assertEqual(next(c for c in demo.state()['reactionTargets'] if c['target']==target)['groups'][0]['emoji'],'👀')
  finally:demo.close()
