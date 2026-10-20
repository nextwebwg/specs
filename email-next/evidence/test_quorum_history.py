import unittest
import test_admitted_quorum as fixtures
from ordering_mls import ProviderKey
from quorum_history import QuorumHistory
from quorum_historical_release import QuorumHistoricalRelease,KIND,TERMINAL
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from admitted_quorum import AdmittedQuorum
import ordering_carrier

class QuorumHistoryTests(unittest.TestCase):
    setUp=fixtures.AdmittedQuorumTests.setUp;tearDown=fixtures.AdmittedQuorumTests.tearDown
    endpoint=fixtures.AdmittedQuorumTests.endpoint;prepare=fixtures.AdmittedQuorumTests.prepare;join=fixtures.AdmittedQuorumTests.join;certify=fixtures.AdmittedQuorumTests.certify
    def step(self,remove=False):
        indices=[int(m['index']) for m in self.author_group.live()[1]['snapshot']['members'] if m['identity']==self.removed['identity']] if remove else []
        candidate=self.author_group.stage(ProviderKey(self.provider,self.f.creator),time=self.time,removals=indices);proof=self.certify(candidate)
        for group in self.groups:decision=group.install(candidate,proof,time=self.time)
        return decision
    def run_history(self,terminal):
        self.join();start=self.author_group.live()[1]['snapshot']['predecessor'];first=self.step();self.step(remove=terminal)
        if terminal:self.step()
        d=self.removed;c=next(c for d0,c in zip(self.f.devices,self.selected) if d0 is d)
        target=dict(mailbox=c['mailbox'],principal=d['principal'],device=d['device']);route=dict(mailbox=c['mailbox'],generation=c['generation'],principal=d['principal'],observation=c['digest'])
        adapter=QuorumHistoricalRelease(self.sender,self.author_group,TERMINAL if terminal else KIND)
        names=adapter.prepare('catchup',start,target=target,key=d['key'],association_target=route,envelope_sender='creator@example.invalid',time=self.time)
        self.assertEqual(len(names),2)
        receiver=AdmittedQuorum(self.senders[d['device']].receiver,self.worker,d)
        wires=[self.sender.db.execute('SELECT wire FROM quorum_prepared WHERE id=?',(n,)).fetchone()[0] for n in names]
        with self.assertRaises(ValueError):ordering_carrier.receive(receiver,wires[1],time=self.time)
        with SenderWorker(self.sender) as worker:
            submit=worker.submit_quorum_terminal_history if terminal else worker.submit_quorum_history
            with self.assertRaisesRegex(ValueError,'unresolved'):submit(names[1],group=self.author_group,port=1,time=self.time)
            for i,name in enumerate(names):
                smtp=LocalSMTP();self.assertEqual(submit(name,group=self.author_group,port=smtp.port,time=self.time)['state'],'accepted');smtp.done()
                self.assertEqual(smtp.wire,wires[i]);self.assertEqual(ordering_carrier.receive(receiver,smtp.wire,time=self.time)['status'],'accepted')
            with self.assertRaisesRegex(ValueError,'Already handed off'):submit(names[0],group=self.author_group,port=1,time=self.time)
        self.assertEqual(receiver.db.execute('SELECT status FROM mls_group_instances').fetchone()[0],'inactive' if terminal else 'active')
        self.assertEqual(adapter.prepare('catchup',start,target=target,key=d['key'],association_target=route,envelope_sender='creator@example.invalid',time=self.time),names)
        self.sender.db.execute('BEGIN IMMEDIATE')
        try:
            with self.assertRaisesRegex(ValueError,'unsupported-size'):QuorumHistory(self.author_group,max_bytes=1).path_locked(start,target_identity=d['identity'],target_key=d['key'],time=self.time)
            self.sender.db.execute('DELETE FROM qo_history WHERE decision=?',(first,))
            with self.assertRaisesRegex(ValueError,'gap'):adapter.validate_locked(names[0],self.time)
        finally:self.sender.db.execute('ROLLBACK')
    def test_retained_offline_endpoint_ordered_catchup(self):self.run_history(False)
    def test_removed_offline_endpoint_stops_at_terminal_edge(self):self.run_history(True)

if __name__=='__main__':unittest.main()
