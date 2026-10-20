import unittest,json
import test_joined_reactions as reactions
from client_flow import ClientFlow

class EmojiIntentTests(unittest.TestCase):
 selected_operations=reactions.JoinedReactions.selected_operations
 setUp=reactions.JoinedReactions.setUp
 tearDown=reactions.JoinedReactions.tearDown
 event=reactions.JoinedReactions.event
 prepare=reactions.JoinedReactions.prepare
 receive=reactions.JoinedReactions.receive
 question=reactions.JoinedReactions.question
 ref=reactions.JoinedReactions.ref
 view=reactions.JoinedReactions.view
 def test_selected_emoji_withdrawal_retry_and_foreign_author(self):
  target=self.question();self.receive(1,self.prepare(0,target));ref=self.ref(target)
  client=ClientFlow(self.senders[1],key=self.devices[1]['key'],envelope_sender='bob@example.invalid',recipients=['alice@example.invalid'])
  def react(id,emoji):
   wire=client.react(id,ref,emoji,self.view(1,target)['sourceToken'],time=self.time);self.receive(0,wire);return wire
  react('thumb','👍');react('heart','❤️');react('thumbtwo','👍')
  foreign=self.event(0,'8',dict(kind='reaction',target=ref,emoji='👍'));self.receive(1,self.prepare(0,foreign))
  token=self.view(1,target)['sourceToken'];wire=client.withdraw_reactions('removeThumb',ref,token,emoji='👍',time=self.time);self.receive(0,wire)
  self.assertEqual(client.withdraw_reactions('removeThumb',ref,token,emoji='👍',time=self.time),wire)
  with self.assertRaisesRegex(ValueError,'conflict'):client.withdraw_reactions('removeThumb',ref,token,emoji='❤️',time=self.time)
  from client_reactions import active_events
  remaining=active_events(self.senders[0].receiver.journal,ref,self.view(0,target))
  self.assertCountEqual([(r['principal'],e) for r,e in remaining],[(self.principals[1],'❤️'),(self.principals[0],'👍')])
  allwire=client.withdraw_reactions('removeAll',ref,self.view(1,target)['sourceToken'],time=self.time);self.receive(0,allwire)
  self.assertEqual(self.view(0,target)['active'],[self.ref(foreign)])
  for invalid in ('❤','not emoji',['👍']):
   with self.assertRaises(ValueError):client.react('invalid',ref,invalid,self.view(1,target)['sourceToken'],time=self.time)

class DemoEmojiTests(unittest.TestCase):
 def test_group_counts_and_old_api(self):
  from client_flow_server import Demo
  demo=Demo()
  try:
   for action,emoji in [('one','👍'),('two','👍'),('three','❤️')]:
    demo.react(dict(action=action,token=demo.state()['reactionToken'],emoji=emoji))
   groups={r['emoji']:r for r in demo.state()['reactionGroups']}
   self.assertEqual(groups['👍'],dict(emoji='👍',count=1,mine=True));self.assertEqual(groups['❤️']['count'],1)
   f=demo.fixture;foreign=f.event(0,'8',dict(kind='reaction',target=demo.ref,emoji='👍'));f.prepare(0,foreign);demo.transport(0,foreign['event'],lambda wire:f.receive(1,wire))
   self.assertEqual(next(r for r in demo.state()['reactionGroups'] if r['emoji']=='👍'),dict(emoji='👍',count=2,mine=True))
   demo.react(dict(action='remove',token=demo.state()['reactionToken'],emoji='👍'),withdraw=True)
   groups={r['emoji']:r for r in demo.state()['reactionGroups']};self.assertEqual(groups['👍'],dict(emoji='👍',count=1,mine=False));self.assertEqual(groups['❤️'],dict(emoji='❤️',count=1,mine=True))
   demo.react(dict(action='oldreact',token=demo.state()['reactionToken']))
   demo.react(dict(action='oldwithdraw',token=demo.state()['reactionToken']),withdraw=True)
   self.assertEqual(demo.state()['reactionGroups'],[dict(emoji='👍',count=1,mine=False)])
   self.assertEqual(demo.state('maya')['reactionGroups'],[])
  finally:demo.close()
