"""Fixed ordered delivery of retained quorum controls to an offline endpoint."""
import hashlib,json
from email import policy
from email.parser import BytesParser
from quorum_history import QuorumHistory
from quorum_release import QuorumRelease,CONTROL
from ordering_carrier import package
from sender_release import canonical
from sender_association import targets,check_locked
from terminal_routing import check_terminal_route_locked
from initial_roster import credential
from provider_mls import call
from passive_discovery import mailbox_syntax
KIND='quorum-history-submit-v0'
TERMINAL='quorum-history-terminal-submit-v0'

class QuorumHistoricalRelease:
    def __init__(self,sender,group,kind=KIND):
        QuorumRelease(sender,group,CONTROL)
        if kind not in (KIND,TERMINAL):raise ValueError('Fixed history kind')
        self.sender=sender;self.group=group;self.db=sender.db;self.kind=kind;self.history=QuorumHistory(group)
        self.db.execute("CREATE TABLE IF NOT EXISTS qo_history_plans(id TEXT PRIMARY KEY,request TEXT NOT NULL,deliveries TEXT NOT NULL)")
    def _path(self,evidence,time):
        path=self.history.path_locked(evidence['start'],target_identity=credential(evidence['target']),target_key=evidence['key'],time=time)
        if (self.kind==TERMINAL)!=path[-1]['terminal']:raise ValueError('Changed recipient terminal scope')
        return path
    def prepare(self,plan,start,*,target,key,association_target,envelope_sender,time):
        if not isinstance(plan,str) or not plan.isascii() or not plan.isalnum():raise ValueError('Plan ID')
        if set(target)!={'mailbox','principal','device'}:raise ValueError('Exact target')
        mailbox_syntax(envelope_sender);selected=targets([association_target],[target['mailbox']])
        if selected is None:raise ValueError('Selected history route required')
        base=dict(start=start,target=target,key=key)
        request=canonical(dict(kind=self.kind,**base,selected=selected,sender=envelope_sender))
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old_plan=self.db.execute('SELECT request,deliveries FROM qo_history_plans WHERE id=?',(plan,)).fetchone()
            if old_plan:
                if old_plan[0]!=request:raise ValueError('Immutable history plan conflict')
                self.db.execute('COMMIT');return json.loads(old_plan[1])
            path=self._path(base,time);state=self.group.live()[1]
            setting=self.db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone();trust=json.loads(setting[1])['trustPolicy']
            metadata=call(self.sender.binary,op='inspect-send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.group.device['key'])['metadata'];deps=self.sender._authority(metadata,time,trust)
            route=[check_terminal_route_locked(self.sender.associations,selected[0],credential(target),key,time,trust)] if self.kind==TERMINAL else check_locked(self.sender.associations,selected,metadata,time,trust,verification=self.sender._verification_enabled())
            if len(route)!=1 or (route[0]['principal'],route[0]['device'])!=(target['principal'],target['device']):raise ValueError('Exact history route')
            names=[]
            for i,edge in enumerate(path):
                name=plan+'step'+str(i);item_request=canonical(dict(request=request,decision=edge['decision'],previous=names[:]))
                old=self.db.execute('SELECT request FROM quorum_prepared WHERE id=?',(name,)).fetchone()
                if old:
                    if old[0]!=item_request:raise ValueError('Immutable history plan conflict')
                    names.append(name);continue
                message=BytesParser(policy=policy.SMTP).parsebytes(package(edge['carrier']))
                for header,value in [('From',envelope_sender),('To',target['mailbox'])]:
                    if header in message:message.replace_header(header,value)
                    else:message[header]=value
                wire=message.as_bytes();evidence=dict(base,decision=edge['decision'],step=i,previous=names[:],wireDigest=hashlib.sha256(wire).hexdigest())
                self.db.execute('INSERT INTO quorum_prepared VALUES(?,?,?,?,?,?,?,?,?,?)',(name,self.kind,item_request,wire,canonical(metadata),canonical(deps),setting[0],canonical(dict(sender=envelope_sender,recipients=[target['mailbox']])),canonical(dict(mode='terminal-only-routing' if self.kind==TERMINAL else 'selected-association',targets=selected,dependencies=route)),canonical(evidence)))
                names.append(name)
            self.db.execute('INSERT INTO qo_history_plans VALUES(?,?,?)',(plan,request,canonical(names)))
            self.db.execute('COMMIT');return names
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def validate_locked(self,delivery,time):
        row=self.db.execute('SELECT kind,wire,evidence,associations FROM quorum_prepared WHERE id=?',(delivery,)).fetchone()
        if not row or row[0]!=self.kind:raise ValueError('Fixed history contract')
        evidence=json.loads(row[2]);path=self._path(evidence,time);i=evidence['step']
        if type(i) is not int or i<0 or i>=len(path) or path[i]['decision']!=evidence['decision'] or len(evidence['previous'])!=i:raise ValueError('Exact history position')
        from ordering_carrier import select_object
        if select_object(row[1])!=json.loads(path[i]['carrier']) or hashlib.sha256(row[1]).hexdigest()!=evidence['wireDigest']:raise ValueError('Immutable history carrier')
        carrier=select_object(row[1])
        if carrier['version']=='2':
            from quorum_exchange_support import complete
            complete(self.group.identity,carrier['witnessAssertions'],json.loads(bytes.fromhex(carrier['candidate']['plan']['result']['context'])),time=time)
        for index,prior in enumerate(evidence['previous']):
            old=self.db.execute('SELECT kind,evidence FROM quorum_prepared WHERE id=?',(prior,)).fetchone()
            if not old or old[0]!=self.kind:raise ValueError('Fixed prior history step')
            p=json.loads(old[1])
            if any(p[k]!=evidence[k] for k in ('start','target','key')) or p['decision']!=path[index]['decision'] or p['step']!=index:raise ValueError('History dependency scope')
            attempts=self.db.execute("SELECT result FROM sender_attempts WHERE delivery=? AND kind=? AND state='accepted'",(prior,self.kind)).fetchall()
            if not any(evidence['target']['mailbox'] in json.loads(r[0]).get('acceptedRecipients',[]) for r in attempts):raise ValueError('Prior history handoff unresolved')
        if self.kind==TERMINAL:
            association=json.loads(row[3]);trust=json.loads(self.db.execute('SELECT policy FROM sender_policy WHERE id=1').fetchone()[0])['trustPolicy']
            routing=check_terminal_route_locked(self.sender.associations,association['targets'][0],credential(evidence['target']),evidence['key'],time,trust)
            if association['dependencies']!=[routing]:raise ValueError('Changed terminal history route')
            evidence=dict(evidence,routing=routing)
        return evidence
