import json,unittest
from unittest.mock import patch
from recovery_retrieval import RecoveryRetrieval,MailSpool
from remediation_chain import POLICY
from transition_mime import package
from transition_carrier import encode_transition
import test_remediation_chain as base
import test_signed_remediation as signed

class Retrieval(unittest.TestCase):
    setUp=base.RemediationTests.setUp;tearDown=base.RemediationTests.tearDown
    store=base.RemediationTests.store;prepared=base.RemediationTests.prepared;remove=base.RemediationTests.remove;chain=base.RemediationTests.chain
    def setup_retrieval(self,carriers,**options):
        self.spool=MailSpool(self.root/'mail.sqlite');self.addCleanup(self.spool.close)
        for raw in reversed(carriers):self.spool.append(package(raw,sender='a@example.test',recipient='b@example.test'))
        r=RecoveryRetrieval(self.gb,{'mail':self.spool},**options);r.schedule('job',allowed=self.allowed,policy=POLICY);r.collect();return r
    def test_reverse_order_gap_duplicate_and_invalid_ciphertext(self):
        start,carriers=self.chain();old=self.gb.live();r=self.setup_retrieval(carriers[1:])
        self.assertEqual(r.run('job',time=self.time)['status'],'waiting-for-gap');self.assertEqual(self.gb.live(),old)
        import base64
        bad=json.loads(carriers[0]);raw=bytearray(base64.b64decode(bad['commit']));raw[-1]^=1;bad['commit']=base64.b64encode(raw).decode()
        mislabeled=json.loads(carriers[0]);mislabeled['previousContext']='f'*64
        for c in [json.dumps(bad).encode(),carriers[0],carriers[0],json.dumps(mislabeled).encode()]:self.spool.append(package(c,sender='a@example.test',recipient='b@example.test'))
        r.collect();result=r.run('job',time=self.time)
        self.assertEqual(result['status'],'accepted-remediation');self.assertEqual(self.gb.live()['snapshot'],self.ga.live()['snapshot'])
        self.assertEqual(r.run('job',time=self.time),result)
    def test_policy_permission_and_source_failover(self):
        start,carriers=self.chain();r=self.setup_retrieval(carriers)
        r.schedule('nopolicy',allowed=self.allowed)
        self.assertEqual(r.run('nopolicy',time=self.time)['status'],'waiting-for-policy')
        r.schedule('nopermission',allowed=set(),policy=POLICY)
        self.assertEqual(r.run('nopermission',time=self.time)['status'],'held')
        class Broken:
            def scan(self,*a,**kw):raise OSError('offline')
        r.sources={'offline':Broken(),'mail':self.spool}
        self.assertEqual(r.collect()['offline']['status'],'unavailable')
        self.assertEqual(r.run('job',time=self.time)['status'],'accepted-remediation')
    def test_source_cursor_and_ready_crash_atomicity(self):
        start,carriers=self.chain();r=self.setup_retrieval([]);old=self.gb.live()
        for c in carriers:self.spool.append(package(c,sender='a@example.test',recipient='b@example.test'))
        def crash(stage):raise RuntimeError(stage)
        with self.assertRaisesRegex(RuntimeError,'before-source'):r.collect(crash=crash)
        self.assertEqual(self.gb.db.execute('SELECT cursor FROM recovery_source').fetchone()[0],0)
        r.collect()
        with self.assertRaisesRegex(RuntimeError,'after-ready'):r.run('job',time=self.time,crash=crash)
        chosen=self.gb.db.execute('SELECT chosen FROM recovery_job WHERE id="job"').fetchone()[0];self.assertIsNotNone(chosen);self.assertEqual(self.gb.live(),old)
        def before(stage):
            if stage=='before-commit':raise RuntimeError(stage)
        with self.assertRaisesRegex(RuntimeError,'before-commit'):r.run('job',time=self.time,crash=before)
        self.assertEqual(self.gb.live(),old);self.assertEqual(self.gb.db.execute('SELECT count(*) FROM mls_remediation_receipt').fetchone()[0],0)
        self.assertEqual(r.run('job',time=self.time)['status'],'accepted-remediation')
        self.assertEqual(self.gb.db.execute('SELECT chosen FROM recovery_job WHERE id="job"').fetchone()[0],chosen)
    def test_real_authenticated_writer_fork_holds(self):
        before=self.ga.live()
        # Generate two genuine independent writer candidates from the same MLS
        # state without installing either. Both signatures validate at receiver.
        one=self.ga.invoke('candidate',before,packages=[])
        two=self.ga.invoke('candidate',before,packages=[])
        self.assertNotEqual(one['wire'],two['wire'])
        r=self.setup_retrieval([encode_transition(one),encode_transition(two)]);old=self.gb.live()
        self.assertEqual(r.run('job',time=self.time),{'status':'conflict','reason':'authenticated-successors'})
        self.assertEqual(self.gb.live(),old)

    def test_process_crash_retry_and_budget(self):
        import multiprocessing,os
        from identity_store import IdentityStore
        from group_transitions import GroupTransitions
        start,carriers=self.chain();r=self.setup_retrieval(carriers);old=self.gb.live()
        def child(point):
            for store in self.stores:store.close()
            identity=IdentityStore(self.root/'b.sqlite');group=GroupTransitions(identity,self.binary,self.b)
            source=MailSpool(self.root/'mail.sqlite');retrieval=RecoveryRetrieval(group,{'mail':source})
            retrieval.run('job',time=self.time,crash=lambda stage:os._exit(91) if stage==point else None)
        for point in ('before-commit','after-commit'):
            child_process=multiprocessing.get_context('fork').Process(target=child,args=(point,));child_process.start();child_process.join(30)
            if child_process.is_alive():child_process.terminate();child_process.join();self.fail('Child timeout')
            self.assertEqual(child_process.exitcode,91)
            if point=='before-commit':self.assertEqual(self.gb.live(),old)
        self.assertEqual(r.run('job',time=self.time)['status'],'accepted-remediation')
        self.assertEqual(self.gb.live()['revision'],old['revision']+1)
    def test_retained_budget_never_skips_cursor(self):
        start,carriers=self.chain();r=self.setup_retrieval([],max_messages=1)
        for c in carriers:self.spool.append(package(c,sender='a@example.test',recipient='b@example.test'))
        r.collect()
        with self.assertRaisesRegex(ValueError,'Retained mailbox budget'):r.collect()
        self.assertEqual(self.gb.db.execute('SELECT cursor FROM recovery_source').fetchone()[0],1)
        self.assertEqual(self.gb.db.execute('SELECT count(*) FROM recovery_mail').fetchone()[0],1)
    def test_support_budget_rolls_back_mail_and_scan_cursor(self):
        from email.message import EmailMessage
        from email import policy
        from discovery_mime import MEDIA_TYPE
        r=self.setup_retrieval([],max_messages=2);r.add_support(b'first cached bytes');r.add_support(b'other cached bytes')
        mail=EmailMessage(policy=policy.SMTP);mail.set_content('Support candidate')
        mail.add_attachment(b'second cached bytes',maintype='application',subtype=MEDIA_TYPE.split('/')[1],cte='base64')
        self.spool.append(mail.as_bytes())
        with self.assertRaisesRegex(ValueError,'Support budget'):r.collect()
        self.assertEqual(self.gb.db.execute('SELECT cursor FROM recovery_source').fetchone()[0],0)
        self.assertEqual(self.gb.db.execute('SELECT count(*) FROM recovery_mail').fetchone()[0],0)
        self.assertEqual(self.gb.db.execute('SELECT count(*) FROM recovery_origin').fetchone()[0],0)
        self.assertEqual(self.gb.db.execute('SELECT count(*) FROM recovery_support').fetchone()[0],2)
    def test_ready_retry_cannot_ignore_new_authenticated_fork(self):
        before=self.ga.live();one=self.ga.invoke('candidate',before,packages=[]);two=self.ga.invoke('candidate',before,packages=[])
        r=self.setup_retrieval([encode_transition(one)])
        def stop(stage):
            if stage=='after-ready':raise RuntimeError(stage)
        with self.assertRaisesRegex(RuntimeError,'after-ready'):r.run('job',time=self.time,crash=stop)
        selected=self.gb.db.execute('SELECT chosen FROM recovery_job').fetchone()[0]
        self.spool.append(package(encode_transition(two),sender='a@example.test',recipient='b@example.test'));r.collect()
        self.assertEqual(r.run('job',time=self.time)['status'],'conflict')
        self.assertEqual(self.gb.db.execute('SELECT chosen FROM recovery_job').fetchone()[0],selected)

    def test_changed_checkpoint_and_cancelled_request_do_not_apply(self):
        original=self.ga.live();candidate=self.ga.invoke('candidate',original,packages=[])
        r=self.setup_retrieval([encode_transition(candidate)])
        def advance(stage):
            if stage=='after-ready':self.assertEqual(self.gb.receive(bytes.fromhex(candidate['wire']),allowed=set(),time=self.time),'accepted')
        self.assertEqual(r.run('job',time=self.time,crash=advance)['status'],'obsolete')
        r.schedule('cancelled',allowed=set(),policy=POLICY);r.cancel('cancelled')
        old=self.gb.live();self.assertEqual(r.run('cancelled',time=self.time)['status'],'cancelled');self.assertEqual(self.gb.live(),old)

class SignedRetrieval(unittest.TestCase):
    application=signed.SignedRemediation.application
    setUp=signed.SignedRemediation.setUp;tearDown=signed.SignedRemediation.tearDown
    endpoint=signed.SignedRemediation.endpoint;prepare=signed.SignedRemediation.prepare;proof=signed.SignedRemediation.proof;setup_chain=signed.SignedRemediation.setup_chain
    def test_actual_smtp_signed_rich_mailbox_retrieval(self):
        # Install accepted-history retention before generating writer decisions.
        from commit_history import CommitHistory
        from group_transitions import GroupTransitions
        writer=GroupTransitions(self.identity,self.f.binary.with_name('group-transitions'),self.f.creator)
        history=CommitHistory(writer,max_count=16,max_bytes=8000000)
        ga,gb,start,carriers,allowed,final,proof=self.setup_chain()
        from historical_release import HistoricalRelease
        from sender_worker import SenderWorker
        from test_sender_release import LocalSMTP
        release=HistoricalRelease(self.sender,history)
        source=self.selected[self.f.devices.index(self.f.creator)]['mailbox'];destination=self.selected[self.f.devices.index(gb.device)]['mailbox']
        items=release.prepare('retrieval',start,key=self.f.creator['key'],target_identity=gb.device['identity'],target_key=gb.device['key'],mailbox=destination,envelope_sender=source,time=self.time)
        spool=MailSpool(__import__('pathlib').Path(self.temp.name)/'retrieved.sqlite');self.addCleanup(spool.close)
        with SenderWorker(self.sender) as worker:
            for item in items:
                server=LocalSMTP();result=worker.submit_historical(item,history=history,port=server.port,time=self.time);server.done()
                self.assertEqual(result['state'],'accepted');spool.append(server.wire)
        retrieval=RecoveryRetrieval(gb,{'configured-mail':spool});retrieval.schedule('signed',allowed=allowed,policy=POLICY)
        self.assertEqual(retrieval.refresh('signed',time=self.time)['recovery']['status'],'waiting-for-support')
        from email.message import EmailMessage
        from email import policy as mail_policy
        from discovery_mime import MEDIA_TYPE
        announcement=EmailMessage(policy=mail_policy.SMTP);announcement['From']=source;announcement['To']=destination;announcement.set_content('Current application support')
        announcement.add_attachment(proof,maintype='application',subtype=MEDIA_TYPE.split('/')[1],cte='base64')
        spool.append(announcement.as_bytes());retrieval.collect();before=gb.live()
        with patch('remediation_support.install',side_effect=RuntimeError('installation failed')):
            with self.assertRaisesRegex(RuntimeError,'installation failed'):retrieval.run('signed',time=self.time)
        self.assertEqual(gb.live(),before)
        self.assertEqual(gb.db.execute('SELECT count(*) FROM mls_remediation_receipt').fetchone()[0],0)
        self.assertEqual(gb.db.execute('SELECT state FROM recovery_job').fetchone()[0],'ready')
        result=retrieval.run('signed',time=self.time)
        self.assertEqual(result['status'],'accepted-remediation');self.assertEqual(gb.live()['snapshot'],ga.live()['snapshot'])
        self.assertEqual(result['pastEpochSecrets'],'deleted');self.assertEqual(result['acceptedHistory'],'preserved')
        with patch('remediation_support.verify_passive_discovery',side_effect=AssertionError('No reselection')):self.assertEqual(retrieval.run('signed',time=self.time),result)

class PendingRetrieval(unittest.TestCase):
    setUp=base.PendingRecoveryTests.setUp;tearDown=base.PendingRecoveryTests.tearDown
    store=base.PendingRecoveryTests.store;prepared=base.PendingRecoveryTests.prepared;remove=base.PendingRecoveryTests.remove
    def test_already_decrypted_pending_remains_held_after_automatic_recovery(self):
        outer=self
        class ThroughMailbox:
            def __init__(self,group):self.group=group
            def receive(self,carriers,*,allowed,time,expected_predecessor,policy):
                spool=MailSpool(outer.root/'pending-mail.sqlite');outer.addCleanup(spool.close)
                for c in reversed(carriers):spool.append(package(c,sender='a@example.test',recipient='b@example.test'))
                retrieval=RecoveryRetrieval(self.group,{'mail':spool});retrieval.schedule('pending',allowed=allowed,policy=policy);retrieval.collect()
                result=retrieval.run('pending',time=time);outer.assertEqual(result['status'],'accepted-remediation');return result
        with patch.object(base,'RemediationChain',ThroughMailbox):
            base.PendingRecoveryTests.test_authenticated_pending_removed_sender_never_promotes(self)

if __name__=='__main__':unittest.main()
