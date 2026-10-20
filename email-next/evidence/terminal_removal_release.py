"""Fixed removal-only notification; no current receiver authority or catch-up grant."""
import json
import uuid
from email import policy
from email.parser import BytesParser
from commit_history import CommitHistory
from sender_release import canonical
from sender_association import targets
from passive_discovery import mailbox_syntax
from mls_receive import MlsReceive
from provider_mls import call
from transition_carrier import encode_transition,parse,check_binding
from transition_mime import package,select
from terminal_routing import check_terminal_route_locked
KIND='configured-terminal-removal-v0'

class TerminalRemovalRelease:
    def __init__(self,sender,history):
        if type(history) is not CommitHistory or history.db is not sender.db:raise ValueError('Shared configured history required')
        self.sender=sender;self.history=history;self.db=sender.db
        if self.db.in_transaction:raise ValueError('Initialize outside transaction')
        self.db.execute('CREATE TABLE IF NOT EXISTS terminal_removal_closed(id TEXT PRIMARY KEY,state TEXT NOT NULL,archive TEXT NOT NULL)')
        self.db.execute('''CREATE TABLE IF NOT EXISTS terminal_removal_prepared(id TEXT PRIMARY KEY,request TEXT NOT NULL,wire BLOB NOT NULL,metadata TEXT NOT NULL,dependencies TEXT NOT NULL,policy_revision INTEGER NOT NULL,envelope TEXT NOT NULL,associations TEXT NOT NULL,evidence TEXT NOT NULL)''')
    def _record(self,decision):
        row=self.db.execute('SELECT record FROM commit_history WHERE digest=?',(decision,)).fetchone()
        if not row:raise ValueError('Missing accepted removal')
        record=json.loads(row[0]);old={(m['identity'],m['key']) for m in record['before']['members']};new={(m['identity'],m['key']) for m in record['after']['members']}
        if not new<old:raise ValueError('Not removal-only')
        return record,old-new
    def _proof(self,e,time,policy):
        record,removed=self._record(e['decision'])
        if record!=e['record'] or (e['identity'],e['key']) not in removed:raise ValueError('Changed removal target')
        episode=self.db.execute('SELECT admission FROM mls_membership_episode WHERE group_id=? AND identity=? AND key=? AND removal=?',(record['before']['group'],e['identity'],e['key'],e['decision'])).fetchall()
        if len(episode)!=1 or episode[0][0]!=e['episode']:raise ValueError('Changed removed episode')
        periods=self.db.execute('SELECT start_epoch,end_epoch FROM mls_membership_episode WHERE group_id=? AND identity=?',(record['before']['group'],e['identity'])).fetchall()
        if any(end is None or int(start)>=int(record['after']['epoch']) for start,end in periods):raise ValueError('Target rejoined; old notice held')
        path=self.history.path_locked(record['before']['predecessor'],target_identity=e['committer'],target_key=e['committerKey'],time=time,trust_policy=policy)
        if not path['steps'] or path['steps'][0]['decision']!=e['decision']:raise ValueError('Removal not on current lineage')
        route=check_terminal_route_locked(self.sender.associations,e['target'],e['identity'],e['key'],time,policy)
        return dict(decision=e['decision'],episode=e['episode'],tip=path['tip'],path=[s['decision'] for s in path['steps']],routing=route)
    def prepare(self,delivery,decision,*,key,target_identity,target_key,association_target,envelope_sender,time):
        MlsReceive._policy(time,'allow-unverified');mailbox_syntax(envelope_sender)
        if not isinstance(delivery,str) or not delivery.isascii() or not delivery.isalnum():raise ValueError('Local delivery ID')
        target=targets([association_target],[association_target['mailbox']])[0]
        request=canonical(dict(decision=decision,key=key,identity=target_identity,targetKey=target_key,target=target,sender=envelope_sender))
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT request,wire FROM terminal_removal_prepared WHERE id=?',(delivery,)).fetchone()
            if old:
                if old[0]!=request:raise ValueError('Terminal ID conflict')
                self.db.execute('COMMIT');return old[1]
            setting=self.db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone()
            if not setting:raise ValueError('Configure policy')
            trust=json.loads(setting[1])['trustPolicy'];record,removed=self._record(decision)
            if (target_identity,target_key) not in removed:raise ValueError('Not removed target')
            cp=self.db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
            metadata=call(self.sender.binary,op='inspect-send',checkpoint=json.loads(cp[1]),group=cp[0],key=key)['metadata']
            if metadata['senderIdentity']!=record['sender']:raise ValueError('Original committer required')
            deps=self.sender._authority(metadata,time,trust)
            row=self.db.execute('SELECT admission FROM mls_membership_episode WHERE group_id=? AND identity=? AND key=? AND removal=?',(cp[0],target_identity,target_key,decision)).fetchall()
            if len(row)!=1:raise ValueError('Missing removed episode')
            e=dict(decision=decision,record=record,identity=target_identity,key=target_key,target=target,committer=metadata['senderIdentity'],committerKey=key,episode=row[0][0])
            proof=self._proof(e,time,trust);e['routing']=proof['routing']
            mime=BytesParser(policy=policy.SMTP).parsebytes(package(encode_transition(record),sender=envelope_sender,recipient=target['mailbox']));mime['Message-ID']='<'+uuid.uuid4().hex+'@terminal.example.invalid>'
            wire=mime.as_bytes();envelope=dict(sender=envelope_sender,recipients=[target['mailbox']])
            self.db.execute('INSERT INTO terminal_removal_prepared VALUES(?,?,?,?,?,?,?,?,?)',(delivery,request,wire,canonical(metadata),canonical(deps),setting[0],canonical(envelope),canonical({'mode':'terminal-only-routing'}),canonical(e)))
            self.history.pin_locked('terminal:'+delivery,[s for s in proof['path']],state='active')
            self.db.execute('COMMIT');return wire
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def validate_locked(self,delivery,time):
        if not self.db.in_transaction:raise ValueError('Caller transaction required')
        if self.db.execute('SELECT 1 FROM terminal_removal_closed WHERE id=?',(delivery,)).fetchone():raise ValueError('Terminal delivery closed')
        row=self.db.execute('SELECT wire,evidence,policy_revision FROM terminal_removal_prepared WHERE id=?',(delivery,)).fetchone()
        if not row:raise ValueError('Unknown terminal delivery')
        setting=self.db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone()
        if not setting or setting[0]!=row[2]:raise ValueError('Changed terminal policy')
        e=json.loads(row[1]);proof=self._proof(e,time,json.loads(setting[1])['trustPolicy'])
        if proof['routing']!=e['routing']:raise ValueError('Changed retained terminal routing')
        value,wire=parse(select(row[0]));check_binding(value,e['record']['before'])
        if wire!=bytes.fromhex(e['record']['wire']):raise ValueError('Changed terminal bytes')
        self.history.pin_locked('terminal:'+delivery,proof['path'],state='active')
        return proof

    def finish(self,delivery,*,worker,cancel=False):
        if worker.sender is not self.sender:raise ValueError('Matching worker required')
        worker._owned();self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT state FROM terminal_removal_closed WHERE id=?',(delivery,)).fetchone()
            if old:self.db.execute('COMMIT');return old[0]
            if not self.db.execute('SELECT 1 FROM terminal_removal_prepared WHERE id=?',(delivery,)).fetchone():raise ValueError('Unknown delivery')
            attempts=self.db.execute('SELECT id,state,evidence,result FROM sender_attempts WHERE delivery=? AND kind=?',(delivery,KIND)).fetchall()
            if any(a[1]=='released' for a in attempts):raise ValueError('Live attempt must finish/recover')
            if not cancel and not any(a[1]=='accepted' for a in attempts):raise ValueError('Not handed off')
            records=[json.loads(r[0]) for r in self.db.execute('SELECT h.record FROM commit_history h JOIN commit_history_pin p ON h.digest=p.digest WHERE p.owner=?',('terminal:'+delivery,))]
            state='cancelled-uncertain' if cancel and any(a[1]=='uncertain' for a in attempts) else 'cancelled' if cancel else 'completed'
            archive=canonical(dict(records=records,attempts=attempts,possibleEarlierDelivery=any(a[1] in ('accepted','uncertain') for a in attempts)))
            self.db.execute('INSERT INTO terminal_removal_closed VALUES(?,?,?)',(delivery,state,archive))
            self.db.execute('DELETE FROM commit_history_pin WHERE owner=?',('terminal:'+delivery,));self.db.execute('COMMIT');return state
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
