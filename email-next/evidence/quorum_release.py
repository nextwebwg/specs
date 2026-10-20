"""Fixed current-tip quorum control/invitation release through the durable worker."""
import json,hashlib
from email import policy
from email.parser import BytesParser
from admitted_quorum import AdmittedQuorum
from ordering_mls import candidate_id
from ordering_carrier import package as control_package,select as control_select
from established_invitation_mime import select as invitation_select
from established_invitation import parse
from provider_mls import call
from sender_release import canonical
from sender_association import targets,check_locked
from passive_discovery import mailbox_syntax,uint64
from initial_roster import credential
CONTROL='quorum-control-submit-v0'
INVITATION='quorum-established-submit-v6'
INVITATION7='quorum-established-submit-v7'
TERMINAL='quorum-terminal-submit-v0'

class QuorumRelease:
    def __init__(self,sender,group,kind):
        if type(group) is not AdmittedQuorum or group.db is not sender.db or kind not in (CONTROL,INVITATION,INVITATION7,TERMINAL):raise ValueError('Fixed admitted quorum adapter')
        self.sender=sender;self.group=group;self.db=sender.db;self.kind=kind
        self.db.execute('CREATE TABLE IF NOT EXISTS quorum_prepared(id TEXT PRIMARY KEY,kind TEXT NOT NULL,request TEXT NOT NULL,wire BLOB NOT NULL,metadata TEXT NOT NULL,dependencies TEXT NOT NULL,policy_revision INTEGER NOT NULL,envelope TEXT NOT NULL,associations TEXT NOT NULL,evidence TEXT NOT NULL)')
    def _decision(self,decision):
        tip,state=self.group.live()
        if tip!=decision:raise ValueError('Current certified tip required')
        row=self.db.execute('SELECT bytes FROM qo_outbox WHERE identity=?',(decision,)).fetchone()
        if not row:raise ValueError('Retained certified outbox required')
        carrier=json.loads(row[0]);staged=self.db.execute('SELECT state FROM qo_staged WHERE candidate=?',(candidate_id(carrier['candidate']),)).fetchone()
        if not staged:raise ValueError('Local certified author required')
        result=json.loads(staged[0])
        if result['after']['predecessor']!=state['snapshot']['predecessor'] or result['sender']!=self.group.device['identity']:raise ValueError('Exact local decision author')
        return row[0],result
    def _dependencies(self,decision,controls,record,*,accepted):
        if not isinstance(controls,list) or len(controls)!=len(set(controls)):raise ValueError('Control dependencies')
        needed={m['identity'] for m in record['before']['members'] if m['identity']!=record['sender']};covered=set()
        for delivery in controls:
            row=self.db.execute('SELECT kind,evidence,envelope,associations FROM quorum_prepared WHERE id=?',(delivery,)).fetchone()
            if not row or row[0] not in (CONTROL,TERMINAL):raise ValueError('Fixed predecessor control required')
            evidence=json.loads(row[1]);envelope=json.loads(row[2]);association=json.loads(row[3])
            if evidence['decision']!=decision or len(evidence['recipients'])!=1:raise ValueError('Exact per-device control dependency')
            target=evidence['recipients'][0];ident=credential(target)
            if ident not in needed or ident in covered:raise ValueError('Predecessor coverage')
            if not any((d['principal'],d['device'],d['mailbox'])==(target['principal'],target['device'],target['mailbox']) for d in association['dependencies']):raise ValueError('Device-bound control route')
            if accepted:
                attempts=self.db.execute('SELECT evidence,result FROM sender_attempts WHERE delivery=? AND kind=? AND state=?',(delivery,row[0],'accepted')).fetchall() if self.db.execute("SELECT 1 FROM sqlite_master WHERE name='sender_attempts'").fetchone() else []
                if not any(target['mailbox'] in set(json.loads(a)['envelope']['recipients'])&set(json.loads(r).get('acceptedRecipients',[])) for a,r in attempts):raise ValueError('Predecessor handoff unresolved')
            covered.add(ident)
        if covered!=needed:raise ValueError('Complete predecessor handoff coverage')
        return sorted(covered)
    def prepare(self,delivery,decision,*,envelope_sender,recipients,association_targets,time,invitation=None,controls=None):
        if not isinstance(delivery,str) or not delivery.isascii() or not delivery.isalnum():raise ValueError('Delivery ID')
        mailbox_syntax(envelope_sender)
        if not isinstance(recipients,list) or not recipients or any(not isinstance(r,dict) or set(r)!={'mailbox','principal','device'} for r in recipients):raise ValueError('Exact recipient selection')
        addresses=[r['mailbox'] for r in recipients];selected=targets(association_targets,addresses)
        if selected is None:raise ValueError('Explicit selected mailbox evidence required')
        request=canonical(dict(kind=self.kind,decision=decision,sender=envelope_sender,recipients=recipients,targets=selected,invitation=invitation,controls=controls))
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT request,wire FROM quorum_prepared WHERE id=?',(delivery,)).fetchone()
            if old:
                if old[0]!=request:raise ValueError('Immutable quorum delivery conflict')
                self.db.execute('COMMIT');return old[1]
            carrier,record=self._decision(decision);tip,state=self.group.live()
            setting=self.db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone();trust=json.loads(setting[1])['trustPolicy']
            metadata=call(self.sender.binary,op='inspect-send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.group.device['key'])['metadata'];deps=self.sender._authority(metadata,time,trust)
            if self.kind==TERMINAL:
                if len(recipients)!=1 or len(selected)!=1:raise ValueError('One terminal recipient')
                from terminal_routing import check_terminal_route_locked
                own=credential(recipients[0]);old=next((m for m in record['before']['members'] if m['identity']==own),None)
                if old is None or own in {m['identity'] for m in record['after']['members']}:raise ValueError('Removed predecessor recipient')
                checked=[check_terminal_route_locked(self.sender.associations,selected[0],own,old['key'],time,trust)]
            else:checked=check_locked(self.sender.associations,selected,metadata,time,trust,verification=self.sender._verification_enabled())
            for target in recipients:
                if not any((d['principal'],d['device'],d['mailbox'])==(target['principal'],target['device'],target['mailbox']) for d in checked):raise ValueError('Exact selected device route')
            if self.kind in (CONTROL,TERMINAL):
                if invitation is not None or controls is not None:raise ValueError('Control-only fields')
                allowed={m['identity'] for m in record['before']['members']} & {m['identity'] for m in record['after']['members']}
                if self.kind==CONTROL and any(credential(r) not in allowed or credential(r)==record['sender'] for r in recipients):raise ValueError('Retained predecessor recipients')
                wire=control_package(carrier)
            else:
                row=self.db.execute('SELECT wire FROM qo_invitations WHERE id=?',(invitation,)).fetchone()
                if not row:raise ValueError('Retained invitation required')
                wire=row[0];_,_,value,_,_=parse(invitation_select(wire));target=value['target']
                if value['version']!=('7' if self.kind==INVITATION7 else '6') or value['decision']!=decision or recipients!=[{k:target[k] for k in ('mailbox','principal','device')}]:raise ValueError('Exact invitation target/decision')
                self._dependencies(decision,controls,record,accepted=False)
            message=BytesParser(policy=policy.SMTP).parsebytes(wire)
            for name,value in [('From',envelope_sender),('To',', '.join(addresses))]:
                if name in message:message.replace_header(name,value)
                else:message[name]=value
            wire=message.as_bytes();evidence=dict(kind=self.kind,decision=decision,recipients=recipients,controls=controls,invitation=invitation,wireDigest=hashlib.sha256(wire).hexdigest())
            self.db.execute('INSERT INTO quorum_prepared VALUES(?,?,?,?,?,?,?,?,?,?)',(delivery,self.kind,request,wire,canonical(metadata),canonical(deps),setting[0],canonical(dict(sender=envelope_sender,recipients=addresses)),canonical(dict(mode='terminal-only-routing' if self.kind==TERMINAL else 'selected-association',targets=selected,dependencies=checked)),canonical(evidence)))
            self.db.execute('COMMIT');return wire
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def validate_locked(self,delivery,time):
        row=self.db.execute('SELECT kind,wire,evidence,associations FROM quorum_prepared WHERE id=?',(delivery,)).fetchone()
        if not row or row[0]!=self.kind:raise ValueError('Fixed quorum contract mismatch')
        evidence=json.loads(row[2]);carrier,record=self._decision(evidence['decision'])
        if hashlib.sha256(row[1]).hexdigest()!=evidence['wireDigest']:raise ValueError('Immutable quorum wire')
        value=json.loads(carrier)
        if value['version']=='2':
            from quorum_exchange_support import complete,current
            context=json.loads(bytes.fromhex(value['candidate']['plan']['result']['context']))
            complete(self.group.identity,value['witnessAssertions'],context,time=time)
            if current(self.group,time=time,context=context)!=value['witnessAssertions']:raise ValueError('Changed witness support dependency')
        if self.kind in (CONTROL,TERMINAL):
            candidate,proof=control_select(row[1]);value=json.loads(carrier)
            if candidate!=value['candidate'] or proof.hex()!=value['proof']:raise ValueError('Certified control binding')
        else:
            _,_,value,_,_=parse(invitation_select(row[1]))
            if value['decision']!=evidence['decision'] or not uint64(value['notBefore'])<=uint64(time['earliest'])<=uint64(time['latest'])<=uint64(value['notAfter']):raise ValueError('Current invitation scope/time')
            self._dependencies(evidence['decision'],evidence['controls'],record,accepted=True)
        if self.kind==TERMINAL:
            from terminal_routing import check_terminal_route_locked
            selected=json.loads(row[3]);target=evidence['recipients'][0];ident=credential(target)
            member=next((m for m in record['before']['members'] if m['identity']==ident),None)
            if member is None or ident in {m['identity'] for m in record['after']['members']}:raise ValueError('Terminal predecessor scope')
            trust=json.loads(self.db.execute('SELECT policy FROM sender_policy WHERE id=1').fetchone()[0])['trustPolicy']
            routing=check_terminal_route_locked(self.sender.associations,selected['targets'][0],ident,member['key'],time,trust)
            if selected['dependencies']!=[routing]:raise ValueError('Changed terminal evidence')
            evidence=dict(evidence,routing=routing)
        return evidence
