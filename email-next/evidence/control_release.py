"""Typed local transition preparation. Established-group Welcome is not submitted.

Only configured endpoint decisions are supported. Historical-epoch catch-up and
public ordering remain unimplemented; no atomic database/network claim is made.
"""
import json
import uuid
from email import policy
from email.parser import BytesParser
from sender_release import canonical
from sender_association import targets,check_locked
from passive_discovery import mailbox_syntax
from group_transitions import GroupTransitions,ids,digest
from transition_carrier import encode_transition,parse,check_binding
from transition_mime import package,select
from provider_mls import call
from mls_receive import MlsReceive

CONTRACT='configured-transition-submit-v0'

class ControlRelease:
    def __init__(self,sender):
        self.sender=sender;self.identity=sender.identity;self.db=sender.db
        if self.db.in_transaction:raise ValueError('Initialize outside transaction')
        self.db.execute('''CREATE TABLE IF NOT EXISTS control_prepared(id TEXT PRIMARY KEY,contract TEXT NOT NULL,request TEXT NOT NULL,wire BLOB NOT NULL,metadata TEXT NOT NULL,dependencies TEXT NOT NULL,policy_revision INTEGER NOT NULL,envelope TEXT NOT NULL,associations TEXT NOT NULL,evidence TEXT NOT NULL)''')
    def _decision(self,identifier):
        row=self.db.execute('SELECT state FROM gt_decision WHERE digest=?',(identifier,)).fetchone()
        if row is None:raise ValueError('No decided transition')
        result=json.loads(row[0])
        if digest(bytes.fromhex(result['wire']))!=identifier:raise ValueError('Decision byte binding')
        return result
    def _current_matches(self,result,key):
        row=self.db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
        if not row or not self.sender.receiver.configured_endpoint_ordering(row[0]):raise ValueError('Control mode not configured')
        current=call(self.sender.binary.with_name('group-transitions'),op='inspect',checkpoint=json.loads(row[1]),group=row[0],key=key)['snapshot']
        if current['predecessor']!=result['after']['predecessor']:raise ValueError('Changed decided state')
    def prepare(self,delivery,decision,*,key,envelope_sender,recipients,time,association_targets=None):
        MlsReceive._policy(time,'allow-unverified')
        if not isinstance(delivery,str) or not delivery or not delivery.isascii() or not delivery.isalnum():raise ValueError('Delivery ID')
        mailbox_syntax(envelope_sender)
        if not isinstance(recipients,list) or not recipients:raise ValueError('Explicit predecessor recipients')
        for target in recipients:
            if not isinstance(target,dict) or set(target)!={'mailbox','principal','device'}:raise ValueError('Recipient shape')
            mailbox_syntax(target['mailbox'])
        addresses=[t['mailbox'] for t in recipients]
        if len(set(addresses))!=len(addresses):raise ValueError('Duplicate recipient')
        selected=targets(association_targets,addresses)
        request=canonical(dict(decision=decision,key=key,sender=envelope_sender,recipients=recipients,associationTargets=selected))
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT request,wire FROM control_prepared WHERE id=?',(delivery,)).fetchone()
            if old:
                if old[0]!=request:raise ValueError('Control ID conflict')
                self.db.execute('COMMIT');return old[1]
            result=self._decision(decision);self._current_matches(result,key);before=result['before'];after=result['after']
            for target in recipients:
                if not any(ids(m['identity'])==(target['principal'],target['device']) for m in before['members']):raise ValueError('Recipient outside predecessor')
            setting=self.db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone()
            if not setting:raise ValueError('Configure policy first')
            settings=json.loads(setting[1]);checkpoint=self.db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
            metadata=call(self.sender.binary,op='inspect-send',checkpoint=json.loads(checkpoint[1]),group=checkpoint[0],key=key)['metadata']
            if metadata['senderIdentity']!=result['sender'] or metadata['group']!=after['group'] or metadata['epoch']!=after['epoch'] or metadata['context']!=after['context']:raise ValueError('Changed decided state')
            dependencies=self.sender._authority(metadata,time,settings['trustPolicy'])
            allowed={(m['identity'],m['key']) for m in after['members']} - {(m['identity'],m['key']) for m in before['members']}
            GroupTransitions._authorize(self,result,allowed,time)
            associations={'mode':'configured-roster'}
            if selected is not None:
                checked=check_locked(self.sender.associations,selected,dict(metadata,members=before['members']),time,settings['trustPolicy'])
                for target,proof in zip(sorted(recipients,key=lambda t:t['mailbox']),checked):
                    if (target['principal'],target['device'])!=(proof['principal'],proof['device']):raise ValueError('Recipient association mismatch')
                associations={'mode':'selected-association','targets':selected,'dependencies':checked}
            mime=BytesParser(policy=policy.SMTP).parsebytes(package(encode_transition(result),sender=envelope_sender,recipient=addresses[0]))
            mime.replace_header('To',', '.join(addresses));mime['Message-ID']='<'+uuid.uuid4().hex+'@control.example.invalid>'
            wire=mime.as_bytes();evidence=dict(contract=CONTRACT,decision=decision,recipients=recipients)
            envelope=dict(sender=envelope_sender,recipients=addresses)
            self.db.execute('INSERT INTO control_prepared VALUES(?,?,?,?,?,?,?,?,?,?)',(delivery,CONTRACT,request,wire,canonical(metadata),canonical(dependencies),setting[0],canonical(envelope),canonical(associations),canonical(evidence)))
            self.db.execute('COMMIT');return wire
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def validate_locked(self,delivery,time):
        if not self.db.in_transaction:raise ValueError('Transaction required')
        row=self.db.execute('SELECT contract,wire,evidence,metadata FROM control_prepared WHERE id=?',(delivery,)).fetchone()
        if row is None or row[0]!=CONTRACT:raise ValueError('Unsupported local control adapter')
        evidence=json.loads(row[2])
        if evidence.get('contract')!=CONTRACT:raise ValueError('Adapter contract')
        result=self._decision(evidence['decision']);self._current_matches(result,json.loads(row[3])['senderKey']);value,commit=parse(select(row[1]))
        if commit!=bytes.fromhex(result['wire']):raise ValueError('Changed control bytes')
        check_binding(value,result['before'])
        for target in evidence['recipients']:
            if not any(ids(m['identity'])==(target['principal'],target['device']) for m in result['before']['members']):raise ValueError('Recipient outside predecessor')
        allowed={(m['identity'],m['key']) for m in result['after']['members']} - {(m['identity'],m['key']) for m in result['before']['members']}
        GroupTransitions._authorize(self,result,allowed,time)
        return evidence
