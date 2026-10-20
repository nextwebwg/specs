"""Fixed configured-writer catch-up adapter. One exact device/mailbox per plan.

No removal/rejoin/failover, remote cursor proof or receiver-acceptance inference.
"""
import json
import uuid
from email import policy
from email.parser import BytesParser
from commit_history import CommitHistory
from sender_release import canonical
from sender_association import targets,check_locked
from passive_discovery import mailbox_syntax
from provider_mls import call
from transition_carrier import encode_transition,parse,check_binding
from transition_mime import package,select
from mls_receive import MlsReceive
from group_transitions import ids
KIND='configured-historical-transition-submit-v0'

class HistoricalRelease:
    def __init__(self,sender,history):
        if type(history) is not CommitHistory or history.db is not sender.db:raise ValueError('Shared configured history required')
        self.sender=sender;self.history=history;self.db=sender.db
        if self.db.in_transaction:raise ValueError('Initialize outside transaction')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS historical_plans(id TEXT PRIMARY KEY,request TEXT NOT NULL,state TEXT NOT NULL,items TEXT NOT NULL,archive TEXT);
          CREATE TABLE IF NOT EXISTS historical_prepared(id TEXT PRIMARY KEY,wire BLOB NOT NULL,metadata TEXT NOT NULL,dependencies TEXT NOT NULL,policy_revision INTEGER NOT NULL,envelope TEXT NOT NULL,associations TEXT NOT NULL,evidence TEXT NOT NULL);
        ''')
    def prepare(self,plan,start,*,key,target_identity,target_key,mailbox,envelope_sender,time,association_targets=None):
        MlsReceive._policy(time,'allow-unverified');mailbox_syntax(mailbox);mailbox_syntax(envelope_sender)
        if not isinstance(plan,str) or not plan or not plan.isascii() or not plan.isalnum():raise ValueError('Local plan ID')
        selected=targets(association_targets,[mailbox]);request=canonical(dict(start=start,key=key,targetIdentity=target_identity,targetKey=target_key,mailbox=mailbox,sender=envelope_sender,associationTargets=selected))
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT request,items FROM historical_plans WHERE id=?',(plan,)).fetchone()
            if old:
                if old[0]!=request:raise ValueError('Plan ID conflict')
                self.db.execute('COMMIT');return json.loads(old[1])
            setting=self.db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone()
            if not setting:raise ValueError('Configure policy')
            trust=json.loads(setting[1])['trustPolicy']
            path=self.history.path_locked(start,target_identity=target_identity,target_key=target_key,time=time,trust_policy=trust)
            cp=self.db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
            metadata=call(self.sender.binary,op='inspect-send',checkpoint=json.loads(cp[1]),group=cp[0],key=key)['metadata']
            deps=self.sender._authority(metadata,time,trust)
            associations={'mode':'configured-roster'} if selected is None else {'mode':'selected-association','targets':selected,'dependencies':check_locked(self.sender.associations,selected,metadata,time,trust)}
            if selected is not None:
                principal,device=ids(target_identity)
                if any(d['principal']!=principal or d['device']!=device for d in associations['dependencies']):raise ValueError('Target association mismatch')
            items=[]
            for position,step in enumerate(path['steps']):
                if step['record']['sender']!=metadata['senderIdentity']:raise ValueError('Only configured committer may submit')
                item=uuid.uuid4().hex;items.append(item)
                mime=BytesParser(policy=policy.SMTP).parsebytes(package(encode_transition(step['record']),sender=envelope_sender,recipient=mailbox));mime['Message-ID']='<'+uuid.uuid4().hex+'@historical.example.invalid>'
                evidence=dict(plan=plan,position=position,start=start,targetIdentity=target_identity,targetKey=target_key,decision=step['decision'],record=step['record'])
                self.db.execute('INSERT INTO historical_prepared VALUES(?,?,?,?,?,?,?,?)',(item,mime.as_bytes(),canonical(metadata),canonical(deps),setting[0],canonical({'sender':envelope_sender,'recipients':[mailbox]}),canonical(associations),canonical(evidence)))
            self.history.pin_locked('history-plan:'+plan,[s['decision'] for s in path['steps']],state='active')
            self.db.execute('INSERT INTO historical_plans VALUES(?,?,?,?,NULL)',(plan,request,'active' if items else 'completed',canonical(items)))
            self.db.execute('COMMIT');return items
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def _accepted(self,item):
        for state,result in self.db.execute('SELECT state,result FROM sender_attempts WHERE delivery=? AND kind=?',(item,KIND)):
            if state=='accepted' and json.loads(result).get('acceptedRecipients'):return True
        return False
    def validate_locked(self,item,time):
        if not self.db.in_transaction:raise ValueError('Caller transaction required')
        row=self.db.execute('SELECT wire,evidence,dependencies,policy_revision FROM historical_prepared WHERE id=?',(item,)).fetchone()
        if not row:raise ValueError('Unknown historical delivery')
        e=json.loads(row[1]);plan=self.db.execute('SELECT state,items FROM historical_plans WHERE id=?',(e['plan'],)).fetchone()
        if not plan or plan[0]!='active':raise ValueError('Plan not active')
        items=json.loads(plan[1])
        if items[e['position']]!=item or any(not self._accepted(prior) for prior in items[:e['position']]):raise ValueError('Earlier recipient handoff incomplete')
        setting=self.db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone()
        if setting[0]!=row[3]:raise ValueError('Changed policy')
        path=self.history.path_locked(e['start'],target_identity=e['targetIdentity'],target_key=e['targetKey'],time=time,trust_policy=json.loads(setting[1])['trustPolicy'])
        step=next((s for s in path['steps'] if s['decision']==e['decision']),None)
        if not step or step['record']!=e['record']:raise ValueError('Changed historical decision')
        value,wire=parse(select(row[0]));check_binding(value,step['record']['before'])
        if wire!=bytes.fromhex(step['record']['wire']):raise ValueError('Changed historical bytes')
        # New descendants may add members, but cannot silently refresh the
        # accepted head/binding dependencies of a prepared existing member.
        for dependency in json.loads(row[2]):
            principal,device=ids(dependency['identity'])
            checked=self.sender.identity._check_device_locked(principal,device,bytes.fromhex(dependency['key']),dependency['role'],time,json.loads(setting[1])['trustPolicy'])
            if any(checked.get(k)!=dependency[k] for k in ('status','head','binding','role')):raise ValueError('Changed historical identity')
        self.history.pin_locked('history-plan:'+e['plan'],[s['decision'] for s in path['steps']],state='active')
        return {'decision':e['decision'],'tip':path['tip'],'path':[s['decision'] for s in path['steps']],'target':path['target'],'plan':e['plan']}
    def finish_plan(self,plan,*,worker,cancel=False):
        """Explicit lifecycle under the transmitter fence. Cancellation never
        claims non-delivery. Archive exact public paths/attempts before unpinning.
        """
        if worker.sender is not self.sender:raise ValueError('Matching worker required')
        worker._owned();self.db.execute('BEGIN IMMEDIATE')
        try:
            row=self.db.execute('SELECT state,items FROM historical_plans WHERE id=?',(plan,)).fetchone()
            if not row:raise ValueError('Unknown plan')
            if row[0]!='active':self.db.execute('COMMIT');return row[0]
            items=json.loads(row[1]);attempts=[]
            for item in items:attempts.extend(self.db.execute('SELECT id,state,evidence,result FROM sender_attempts WHERE delivery=? AND kind=?',(item,KIND)).fetchall())
            initial_attempts=[];initial_messages=[]
            if self.db.execute("SELECT 1 FROM sqlite_master WHERE name='initial_roster_catchup'").fetchone():
                for (delivery,) in self.db.execute('SELECT delivery FROM initial_roster_catchup WHERE plan=?',(plan,)):
                    linked=self.db.execute("SELECT id,state,evidence,result FROM sender_attempts WHERE delivery=? AND kind='initial-roster-invitation-v3'",(delivery,)).fetchall()
                    initial_attempts.extend(linked)
                    wire=self.db.execute('SELECT wire FROM initial_roster_prepared WHERE id=?',(delivery,)).fetchone()
                    initial_messages.append(dict(delivery=delivery,wire=wire[0].hex()))
                    if not cancel and not any(a[1]=='accepted' for a in linked):raise ValueError('Initial roster handoff incomplete')
            attempts.extend(initial_attempts)
            if any(a[1]=='released' for a in attempts):raise ValueError('Live attempt must finish or recover first')
            if not cancel and not all(self._accepted(i) for i in items):raise ValueError('Plan not fully handed off')
            records=[json.loads(r[0]) for r in self.db.execute('SELECT h.record FROM commit_history h JOIN commit_history_pin p ON p.digest=h.digest WHERE p.owner=?',('history-plan:'+plan,))]
            state='cancelled-uncertain' if cancel and any(a[1]=='uncertain' for a in attempts) else 'cancelled' if cancel else 'completed'
            archive=canonical({'records':records,'attempts':attempts,'initialMessages':initial_messages,'possibleEarlierDelivery':any(a[1] in ('uncertain','accepted') for a in attempts)})
            self.db.execute('UPDATE historical_plans SET state=?,archive=? WHERE id=?',(state,archive,plan))
            self.db.execute('DELETE FROM commit_history_pin WHERE owner=?',('history-plan:'+plan,));self.db.execute('COMMIT');return state
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
