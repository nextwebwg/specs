import tempfile
from pathlib import Path
import unittest
from contribution_journal import ContributionJournal
from event_encoding import encode_event
from journal_reaction_view import derive_reaction_view,install_reaction_view

class JournalReactionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'journal.sqlite';self.journal=ContributionJournal(self.path)
        self.a='enp0:'+'01'*32;self.b='enp0:'+'03'*32;self.conversation='2'*32
        self.target=self.event('1',self.a,dict(kind='message',text='Meet at three.',replyTo=[]));self.ref={k:self.target[k] for k in ('principal','conversation','event')}
    def tearDown(self):self.journal.close();self.temp.cleanup()
    def event(self,n,author,op):return dict(version='1',purpose='contribution',event=n*32,conversation=self.conversation,principal=author,audience=[self.a,self.b],operation=op,disclosures=[])
    def append(self,event):return self.journal.append_validated(encode_event(event),{k:event[k] for k in ('principal','conversation','event')})
    def reaction(self,n):return self.event(n,self.b,dict(kind='reaction',target=self.ref,emoji='👍'))
    def withdrawal(self,n,refs,author=None):return self.event(n,author or self.b,dict(kind='reaction-withdraw',target=self.ref,reactions=refs))
    def reference(self,event):return {k:event[k] for k in ('principal','conversation','event')}
    def test_exact_retry_distinct_equal_events_and_restart(self):
        self.append(self.target);r1,r2=self.reaction('3'),self.reaction('4');self.append(r1);self.append(r1);self.append(r2)
        view=derive_reaction_view(self.journal,self.ref);self.assertEqual(len(view['active']),2)
        self.assertEqual(install_reaction_view(self.journal,self.ref,view),{'state':'installed'})
        self.journal.close();self.journal=ContributionJournal(self.path)
        self.assertEqual(derive_reaction_view(self.journal,self.ref),view)
        self.append(self.withdrawal('5',[self.reference(r1)]));self.assertEqual(derive_reaction_view(self.journal,self.ref)['active'],[self.reference(r2)])
    def test_withdrawal_before_reaction_is_all_or_nothing(self):
        self.append(self.target);r1,r2=self.reaction('3'),self.reaction('4');self.append(r1)
        self.append(self.withdrawal('5',[self.reference(r1),self.reference(r2)]))
        self.assertEqual(derive_reaction_view(self.journal,self.ref)['active'],[self.reference(r1)])
        self.append(r2);self.assertEqual(derive_reaction_view(self.journal,self.ref)['active'],[])
    def test_missing_target_cross_author_conflict_and_stale_install(self):
        r=self.reaction('3');self.append(r);self.assertEqual(derive_reaction_view(self.journal,self.ref)['active'],[])
        self.append(self.target);view=derive_reaction_view(self.journal,self.ref)
        self.append(self.withdrawal('5',[self.reference(r)],author=self.a))
        self.assertEqual(install_reaction_view(self.journal,self.ref,view),{'state':'stale'})
        self.assertEqual(derive_reaction_view(self.journal,self.ref)['active'],[self.reference(r)])
        changed=dict(r,operation=dict(r['operation'],emoji='👎'));self.append(changed)
        self.assertEqual(derive_reaction_view(self.journal,self.ref)['active'],[])
    def test_budget_exhaustion_cannot_install_partial_view(self):
        self.append(self.target);self.append(self.reaction('3'))
        view=derive_reaction_view(self.journal,self.ref,max_records=1)
        self.assertEqual(view['state'],'incomplete');self.assertEqual(install_reaction_view(self.journal,self.ref,view),{'state':'incomplete'})
        self.assertEqual(self.journal.db.execute('SELECT count(*) FROM derived_views').fetchone()[0],0)
