"""Single cooperating POSIX worker, configured loopback SMTP only.

Keep the canonical database and adjacent lock file in place. No lease takeover,
network filesystem, database restore, inherited socket or background transmitter.
"""
import fcntl
import json
import os
from pathlib import Path
import smtplib
import uuid
from sender_release import canonical
from mls_receive import MlsReceive
from provider_mls import call
from sender_association import check_locked

class SenderWorker:
    def __init__(self,sender):
        self.sender=sender;self.db=sender.db;self.pid=os.getpid();self.fd=None
        if self.db.in_transaction:raise ValueError('Initialize outside transaction')
        filename=self.db.execute('PRAGMA database_list').fetchone()[2]
        if not filename:raise ValueError('File database required')
        self.path=Path(filename).resolve(strict=True)
        if self.path.stat().st_nlink!=1:raise ValueError('Hard-linked database unsupported')
        self.inode=(self.path.stat().st_dev,self.path.stat().st_ino)
        self.owner=uuid.uuid4().hex
        self.db.execute('''CREATE TABLE IF NOT EXISTS sender_attempts(id TEXT PRIMARY KEY,delivery TEXT NOT NULL,owner TEXT NOT NULL,state TEXT NOT NULL,evidence TEXT NOT NULL,result TEXT)''')
        if 'kind' not in [r[1] for r in self.db.execute('PRAGMA table_info(sender_attempts)')]:
            self.db.execute("ALTER TABLE sender_attempts ADD COLUMN kind TEXT NOT NULL DEFAULT 'application-v0'")
    def __enter__(self):
        if self.fd is not None:raise ValueError('Already locked')
        fd=os.open(str(self.path)+'.sender-lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
        try:
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            if os.fstat(fd).st_nlink!=1:raise ValueError('Invalid lock file')
            self.fd=fd;self._owned()
            # Lock acquisition proves the previous cooperating worker stopped;
            # it does not prove that queued TCP bytes were never delivered.
            self.db.execute("UPDATE sender_attempts SET state='uncertain' WHERE state='released'")
            return self
        except BaseException:
            self.fd=None;os.close(fd);raise
    def __exit__(self,*args):
        if self.fd is not None:os.close(self.fd);self.fd=None
    def _owned(self):
        if self.fd is None or os.getpid()!=self.pid:raise ValueError('Worker ownership')
        st=self.path.stat();lock=Path(str(self.path)+'.sender-lock').stat()
        if (st.st_dev,st.st_ino)!=self.inode or (lock.st_dev,lock.st_ino)!=(os.fstat(self.fd).st_dev,os.fstat(self.fd).st_ino):raise ValueError('Replaced database or lock')
    def _finish(self,attempt,state,result):
        self._owned()
        changed=self.db.execute('UPDATE sender_attempts SET state=?,result=? WHERE id=? AND owner=? AND state=?',(state,canonical(result),attempt,self.owner,'released')).rowcount
        if changed!=1:raise ValueError('Lost attempt ownership')
        return dict(attempt=attempt,state=state,result=result)
    def submit(self,delivery,**options):
        return self._submit(delivery,kind='application-v0',**options)
    def submit_control(self,delivery,**options):
        from control_release import ControlRelease
        return self._submit(delivery,kind='configured-transition-submit-v0',control=ControlRelease(self.sender),**options)
    def submit_historical(self,delivery,*,history,**options):
        from historical_release import HistoricalRelease,KIND
        return self._submit(delivery,kind=KIND,control=HistoricalRelease(self.sender,history),**options)
    def submit_terminal_removal(self,delivery,*,history,**options):
        from terminal_removal_release import TerminalRemovalRelease,KIND
        return self._submit(delivery,kind=KIND,control=TerminalRemovalRelease(self.sender,history),**options)
    def submit_established_invitation(self,delivery,*,history,**options):
        from established_invitation_release import EstablishedInvitationRelease,KIND
        return self._submit(delivery,kind=KIND,control=EstablishedInvitationRelease(self.sender,history),**options)
    def submit_observer(self,delivery,hosted,**options):
        from hosted_observer_release import HostedObserverRelease,KIND
        return self._submit(delivery,kind=KIND,control=HostedObserverRelease(self.sender,hosted),**options)
    def submit_plaintext(self,delivery,**options):
        from plaintext_release import PlaintextRelease,KIND
        return self._submit(delivery,kind=KIND,control=PlaintextRelease(self.sender),**options)
    def submit_initial_invitation(self,delivery,**options):
        from application_invitation_release import ApplicationInvitationRelease,KIND
        return self._submit(delivery,kind=KIND,control=ApplicationInvitationRelease(self.sender),**options)
    def submit_quorum_exchange(self,delivery,*,group,**options):
        from quorum_exchange import QuorumExchange,KIND
        return self._submit(delivery,kind=KIND,control=QuorumExchange(self.sender,group),**options)
    def submit_quorum_control(self,delivery,*,group,**options):
        from quorum_release import QuorumRelease,CONTROL
        return self._submit(delivery,kind=CONTROL,control=QuorumRelease(self.sender,group,CONTROL),**options)
    def submit_quorum_history(self,delivery,*,group,**options):
        from quorum_historical_release import QuorumHistoricalRelease,KIND
        return self._submit(delivery,kind=KIND,control=QuorumHistoricalRelease(self.sender,group,KIND),**options)
    def submit_quorum_terminal_history(self,delivery,*,group,**options):
        from quorum_historical_release import QuorumHistoricalRelease,TERMINAL
        return self._submit(delivery,kind=TERMINAL,control=QuorumHistoricalRelease(self.sender,group,TERMINAL),**options)
    def submit_quorum_terminal(self,delivery,*,group,**options):
        from quorum_release import QuorumRelease,TERMINAL
        return self._submit(delivery,kind=TERMINAL,control=QuorumRelease(self.sender,group,TERMINAL),**options)
    def submit_quorum_invitation7(self,delivery,*,group,**options):
        from quorum_release import QuorumRelease,INVITATION7
        return self._submit(delivery,kind=INVITATION7,control=QuorumRelease(self.sender,group,INVITATION7),**options)
    def submit_quorum_invitation(self,delivery,*,group,**options):
        from quorum_release import QuorumRelease,INVITATION
        return self._submit(delivery,kind=INVITATION,control=QuorumRelease(self.sender,group,INVITATION),**options)
    def submit_initial_roster(self,delivery,**options):
        from initial_roster_lifecycle import InitialRosterRelease
        return self._submit(delivery,kind='initial-roster-invitation-v3',control=InitialRosterRelease(self.sender),**options)
    def submit_initial_roster_late(self,delivery,history,*,catchup_plan,**options):
        from initial_roster_lifecycle import InitialRosterRelease
        return self._submit(delivery,kind='initial-roster-invitation-v3',control=InitialRosterRelease(self.sender,history,catchup_plan),**options)
    def _submit(self,delivery,*,kind,control=None,port,time,retry_uncertain=False,timeout=5,crash=lambda stage:None):
        self._owned();MlsReceive._policy(time,'allow-unverified')
        import secret_retention as retention
        if self.db.execute('SELECT 1 FROM mls_retention_policy').fetchone():
            maintained=retention.SecretRetention(self.sender.receiver).maintain(time=time)
            if maintained and maintained['status']=='retired':raise ValueError('Retention retired group')
        if type(port)!=int or not 1<=port<=65535 or type(timeout) not in (int,float) or not 0<timeout< float('inf'):raise ValueError('Local transport configuration')
        if type(retry_uncertain)!=bool:raise ValueError('Explicit retry choice')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            self._owned()
            terminal=kind in ('configured-terminal-removal-v0','quorum-terminal-submit-v0','quorum-history-terminal-submit-v0')
            historical=kind in ('configured-historical-transition-submit-v0','configured-established-invitation-v0','quorum-history-submit-v0') or terminal or (kind=='initial-roster-invitation-v3' and control.history is not None)
            table='quorum_prepared' if kind in ('quorum-exchange-submit-v0','quorum-control-submit-v0','quorum-established-submit-v6','quorum-established-submit-v7','quorum-terminal-submit-v0','quorum-history-submit-v0','quorum-history-terminal-submit-v0') else 'initial_roster_prepared' if kind=='initial-roster-invitation-v3' else 'established_invitation_prepared' if kind=='configured-established-invitation-v0' else 'initial_invitation_prepared' if kind=='initial-application-invitation-v1' else 'terminal_removal_prepared' if terminal else 'sender_prepared' if kind=='hosted-observer-submit-v1' else 'plaintext_prepared' if kind=='configured-plaintext-submit-v1' else 'historical_prepared' if historical else 'control_prepared' if control is not None else 'sender_prepared'
            row=self.db.execute('SELECT wire,metadata,dependencies,policy_revision,envelope,associations FROM '+table+' WHERE id=?',(delivery,)).fetchone()
            if not row:raise ValueError('Not prepared')
            if kind=='application-v0' and self.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='hosted_observers'").fetchone() and self.db.execute('SELECT 1 FROM hosted_observers WHERE delivery=?',(delivery,)).fetchone():raise ValueError('Use fixed observer submission')
            envelope=json.loads(row[4]);recipient_state={r:'new' for r in envelope['recipients']}
            history=self.db.execute('SELECT state,evidence,result FROM sender_attempts WHERE delivery=? AND kind=? ORDER BY rowid',(delivery,kind)).fetchall()
            for state,stored_evidence,stored_result in history:
                if state=='released':raise ValueError('Attempt still active')
                scope=json.loads(stored_evidence)['envelope']['recipients'];outcome=json.loads(stored_result) if stored_result else {}
                replies={r['recipient']:r['code'] for r in outcome.get('rcpt',[])}
                for recipient in scope:
                    if recipient_state[recipient] in ('accepted','permanent'):continue
                    code=replies.get(recipient)
                    if code is not None and code not in (250,251):
                        status='temporary' if 400<=code<500 else 'permanent' if 500<=code<600 else 'uncertain'
                    elif state=='accepted' and recipient in outcome.get('acceptedRecipients',[]):status='accepted'
                    elif state=='rejected':status='temporary' if outcome.get('retryable') else 'permanent'
                    elif state=='aborted-before-data':status='temporary'
                    else:status='uncertain'
                    recipient_state[recipient]=status
            eligible=[r for r in envelope['recipients'] if recipient_state[r] in ('new','temporary') or (recipient_state[r]=='uncertain' and retry_uncertain)]
            if not eligible:
                if 'uncertain' in recipient_state.values():raise ValueError('Uncertain prior attempt')
                if 'accepted' in recipient_state.values():raise ValueError('Already handed off; remaining recipients held')
                raise ValueError('Permanent rejection')
            envelope=dict(envelope,recipients=eligible)
            policy=self.db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone()
            if not policy or policy[0]!=row[3]:raise ValueError('Changed policy')
            previous=json.loads(row[1]);checkpoint=self.db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
            if not checkpoint or checkpoint[0]!=previous['group']:raise ValueError('Changed group')
            current=call(self.sender.binary,op='inspect-send',checkpoint=json.loads(checkpoint[1]),group=checkpoint[0],key=previous['senderKey'])['metadata']
            if table in ('sender_prepared','plaintext_prepared'):
                from proposal_observation import check_send
                check_send(self.db,current)
            if not historical and current!=previous:raise ValueError('Changed group metadata')
            deps=self.sender._authority(current,time,json.loads(policy[1])['trustPolicy'])
            if not historical and canonical(deps)!=row[2]:raise ValueError('Changed identity dependency')
            associations=json.loads(row[5]);association_checked=[]
            if associations['mode'] not in (('terminal-only-routing',) if terminal else ('configured-roster','selected-association')):raise ValueError('Unknown association mode')
            if associations['mode']=='selected-association':
                selected=[t for t in associations['targets'] if t['mailbox'] in eligible]
                association_checked=check_locked(self.sender.associations,selected,current,time,json.loads(policy[1])['trustPolicy'],verification=self.sender._verification_enabled())
                if association_checked!=[d for d in associations['dependencies'] if d['mailbox'] in eligible]:raise ValueError('Changed mailbox evidence')
            if table=='sender_prepared':
                from hosted_disclosure import check_plans
                original_application=self.db.execute('SELECT application FROM sender_prepared WHERE id=?',(delivery,)).fetchone()[0]
                check_plans(self.db,original_application,policy[0])
            control_evidence=control.validate_locked(delivery,time) if control is not None else None
            if terminal:association_checked=[control_evidence['routing']]
            attempt=uuid.uuid4().hex
            evidence={'dependencies':deps,'policyRevision':policy[0],'time':time,'metadata':current,'envelope':envelope,'associationMode':associations['mode'],'associations':association_checked,'kind':kind,'control':control_evidence}
            self.db.execute('INSERT INTO sender_attempts(id,delivery,owner,state,evidence,result,kind) VALUES(?,?,?,?,?,NULL,?)',(attempt,delivery,self.owner,'released',canonical(evidence),kind))
            self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
        crash('after-release')
        result={'phase':'connect','rcpt':[],'acceptedRecipients':[]};client=None
        try:
            self._owned();client=smtplib.SMTP('127.0.0.1',port,timeout=timeout)
            client.ehlo_or_helo_if_needed();envelope=evidence['envelope']
            code,reply=client.mail(envelope['sender']);result.update(phase='mail',code=code,reply=reply.decode('ascii','replace'))
            if code!=250:return self._finish(attempt,'rejected',dict(result,retryable=400<=code<500))
            for recipient in envelope['recipients']:
                code,reply=client.rcpt(recipient);result['rcpt'].append({'recipient':recipient,'code':code,'reply':reply.decode('ascii','replace')})
                if code in (250,251):result['acceptedRecipients'].append(recipient)
            if not result['acceptedRecipients']:
                return self._finish(attempt,'rejected',dict(result,retryable=any(400<=r['code']<500 for r in result['rcpt'])))
            # A change learned after release can still abort undisclosed content.
            # Serialize this observation, but never hold the write lock during I/O.
            self.db.execute('BEGIN IMMEDIATE')
            try:
                latest=self.db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone()
                checkpoint=self.db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
                if latest[0]!=evidence['policyRevision']:raise ValueError('Changed policy')
                if checkpoint[0]!=current['group']:raise ValueError('Changed group')
                observed=call(self.sender.binary,op='inspect-send',checkpoint=json.loads(checkpoint[1]),group=checkpoint[0],key=current['senderKey'])['metadata']
                if table in ('sender_prepared','plaintext_prepared'):check_send(self.db,observed)
                if observed!=current:raise ValueError('Changed group metadata')
                if self.sender._authority(observed,time,json.loads(latest[1])['trustPolicy'])!=deps:raise ValueError('Changed identity')
                if associations['mode']=='selected-association' and check_locked(self.sender.associations,selected,observed,time,json.loads(latest[1])['trustPolicy'],verification=self.sender._verification_enabled())!=association_checked:raise ValueError('Changed mailbox evidence')
                if table=='sender_prepared':check_plans(self.db,original_application,latest[0])
                if control is not None and control.validate_locked(delivery,time)!=control_evidence:raise ValueError('Changed control evidence')
                self.db.execute('COMMIT')
            except ValueError as error:
                self.db.execute('ROLLBACK')
                return self._finish(attempt,'aborted-before-data',dict(result,reason=str(error)))
            except BaseException:
                if self.db.in_transaction:self.db.execute('ROLLBACK')
                raise
            # Conservative durable phase before any DATA body can be transmitted.
            result['phase']='data-may-have-been-sent'
            self.db.execute('UPDATE sender_attempts SET result=? WHERE id=? AND owner=?',(canonical(result),attempt,self.owner))
            self._owned();code,reply=client.data(row[0]);result.update(phase='final-data',code=code,reply=reply.decode('ascii','replace'))
            crash('after-final-response')
            if 200<=code<300:return self._finish(attempt,'accepted',result)
            if 400<=code<600:return self._finish(attempt,'rejected',dict(result,retryable=400<=code<500))
            return self._finish(attempt,'uncertain',result)
        except smtplib.SMTPDataError as error:
            result.update(phase='data-command-rejected',code=error.smtp_code,reply=error.smtp_error.decode('ascii','replace'))
            return self._finish(attempt,'rejected',dict(result,retryable=400<=error.smtp_code<500))
        except (OSError,smtplib.SMTPException):
            return self._finish(attempt,'uncertain',result)
        finally:
            if client is not None:client.close()
