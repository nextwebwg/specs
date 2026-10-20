import sqlite3,unittest
from types import SimpleNamespace
from event_encoding import encode_event
from private_copy_plan import authorize,check

class CopyPlan(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:',isolation_level=None);self.db.execute('CREATE TABLE sender_policy(id INTEGER,revision INTEGER)');self.db.execute('INSERT INTO sender_policy VALUES(1,1)');self.sender=SimpleNamespace(db=self.db)
        a='enp0:'+'1'*64;b='enp0:'+'2'*64;c='enp0:'+'3'*64
        self.first=dict(version='2',purpose='contribution',event='1'*32,conversation='2'*32,principal=a,audience=[a,b],disclosures=[{'kind':'separate-protected-copy'}],operation=dict(kind='message',text='Selected content',replyTo=[]))
        self.second=dict(self.first,event='3'*32,conversation='4'*32,audience=[a,c])
    def tearDown(self):self.db.close()
    def test_exact_permission_retry_policy_and_peer_change(self):
        raw=encode_event(self.first);peer=encode_event(self.second)
        authorize(self.sender,raw,other_copies=[peer],expected_revision=1);check(self.db,raw,1)
        authorize(self.sender,raw,other_copies=[peer],expected_revision=1)
        with self.assertRaisesRegex(ValueError,'Immutable'):authorize(self.sender,raw,other_copies=[encode_event(dict(self.second,event='5'*32))],expected_revision=1)
        self.db.execute('UPDATE sender_policy SET revision=2')
        with self.assertRaisesRegex(ValueError,'plan required'):check(self.db,raw,2)
        authorize(self.sender,raw,other_copies=[peer],expected_revision=2);check(self.db,raw,2)
    def test_foreign_author_target_and_shared_identity_rejected(self):
        raw=encode_event(self.first)
        for peer in [dict(self.second,principal=self.second['audience'][1]),dict(self.second,conversation=self.first['conversation']),dict(self.second,event=self.first['event'])]:
            with self.assertRaisesRegex(ValueError,'Independent'):authorize(self.sender,raw,other_copies=[encode_event(peer)],expected_revision=1)
        foreign=dict(self.second,operation=dict(kind='reaction',target={k:self.first[k] for k in ('principal','conversation','event')},emoji='👍'))
        with self.assertRaises(ValueError):authorize(self.sender,raw,other_copies=[encode_event(foreign)],expected_revision=1)
