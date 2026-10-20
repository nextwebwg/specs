"""Explicitly configured predecision exchange; no automatic capability discovery."""
import hashlib,json
from email import policy
from email.parser import BytesParser
from ordering_certificates import Proof,encode
from ordering_scope import scope_digest
from ordering_mls import candidate_id
from ordering_carrier import package as mime_package,MAX_MESSAGE,MAX_CONTENT
from event_encoding import decode_event,EventLimitExceeded
from admitted_quorum import AdmittedQuorum
from initial_roster import credential
from sender_association import targets,check_locked
from sender_release import canonical
from provider_mls import call
KIND='quorum-exchange-submit-v0'
PURPOSE='quorum-exchange-experiment'

def parse(content):
    value=decode_event(content,max_octets=MAX_CONTENT)['value']
    if encode(value)!=content or not isinstance(value,dict) or set(value)!=({'version','purpose','scope','proof','candidates'}|({'witnessAssertions'} if value.get('version')=='1' else set())) or value['version'] not in ('0','1') or value['purpose']!=PURPOSE:raise ValueError('Exact exchange wrapper')
    scope=value['scope'];sd=scope_digest(scope)
    raw=value['proof']
    if not isinstance(raw,str) or len(raw)%2 or any(c not in '0123456789abcdef' for c in raw):raise ValueError('Exchange proof hex')
    keys={w['principal']+'|'+w['device']:w['signingKey'] for w in scope['ordering']['witnesses']}
    proof=Proof(bytes.fromhex(raw),scope=sd,keys=keys,f=int(scope['ordering']['faultBound']))
    if not isinstance(value['candidates'],list):raise ValueError('Candidate array')
    ids=[]
    for candidate in value['candidates']:
        if candidate['plan']['scope']!=scope:raise ValueError('Candidate scope')
        ids.append(candidate_id(candidate))
    required=sorted({o['body']['candidate'] for o in proof.nodes.values() if o['body']['kind']=='proposal'})
    if ids!=required:raise ValueError('Exact sorted candidate closure')
    if value['version']=='1':
        from quorum_exchange_support import shape
        shape(value['witnessAssertions'],result_context(value,proof))
    return value,proof

def result_context(value,proof,fallback=None):
    candidate=next((c for c in value['candidates'] if candidate_id(c)==proof.result['candidate']),None)
    return json.loads(bytes.fromhex(candidate['plan']['result']['context'])) if candidate else (fallback or {'ordering':value['scope']['ordering']})

def content(scope,proof,candidates,*,witness_assertions=None):
    raw=encode(dict(version='1' if witness_assertions is not None else '0',purpose=PURPOSE,scope=scope,proof=proof.hex(),candidates=sorted(candidates,key=candidate_id),**({'witnessAssertions':witness_assertions} if witness_assertions is not None else {})))
    parse(raw);return raw

def select(wire):
    if not isinstance(wire,bytes) or len(wire)>MAX_MESSAGE:raise EventLimitExceeded('unsupported-size')
    mail=BytesParser(policy=policy.default).parsebytes(wire);parts=list(mail.iter_parts())
    if mail.defects or mail.get_content_type()!='multipart/mixed' or len(parts)!=2 or parts[0].get_content_type()!='text/plain' or parts[1].get_content_type()!='application/json' or any(p.defects or p.is_multipart() for p in parts):raise ValueError('Exchange MIME')
    raw=parts[1].get_payload(decode=True);parse(raw);return raw

class QuorumExchange:
    def __init__(self,sender,group):
        if type(group) is not AdmittedQuorum or sender.db is not group.db:raise ValueError('Fixed admitted exchange')
        self.sender=sender;self.group=group;self.db=sender.db
        self.db.executescript('''CREATE TABLE IF NOT EXISTS qo_exchange_support(identity TEXT PRIMARY KEY,record BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS qo_exchange_received(root TEXT PRIMARY KEY,content BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS quorum_prepared(id TEXT PRIMARY KEY,kind TEXT NOT NULL,request TEXT NOT NULL,wire BLOB NOT NULL,metadata TEXT NOT NULL,dependencies TEXT NOT NULL,policy_revision INTEGER NOT NULL,envelope TEXT NOT NULL,associations TEXT NOT NULL,evidence TEXT NOT NULL);''')
    def configure(self,record,*,time):
        """Trusted local configuration only, never called from received MIME."""
        if set(record)!={'version','purpose','principal','device','signingKey','state','binding','format','formatVersion'} or record['version']!='0' or record['purpose']!='ordering-exchange-support' or record['format']!=PURPOSE or record['formatVersion']!='0':raise ValueError('Exchange support record')
        ident=credential(record);witness=next((w for w in self.group.scope()['ordering']['witnesses'] if credential(w)==ident),None)
        if witness is None or any(record[k]!=witness[k] for k in ('signingKey','state','binding')):raise ValueError('Exchange witness binding')
        self._current(record,time)
        self.db.execute('INSERT INTO qo_exchange_support VALUES(?,?) ON CONFLICT(identity) DO UPDATE SET record=excluded.record',(ident,encode(record)))
    def _current(self,record,time):
        status=self.group.current(dict(identity=credential(record),key=record['signingKey']),'receive',time)
        if (status['head'],status['binding'])!=(record['state'],record['binding']):raise ValueError('exchange-support-held')
    def _support(self,ident,time):
        row=self.db.execute('SELECT record FROM qo_exchange_support WHERE identity=?',(ident,)).fetchone()
        if not row:raise ValueError('exchange-support-required')
        record=json.loads(row[0]);self._current(record,time);return record
    def _signed(self,value,proof,time):
        from quorum_exchange_support import complete
        context=result_context(value,proof,json.loads(bytes.fromhex(self.group.live()[1]['snapshot']['context'])))
        digests=complete(self.group.identity,value['witnessAssertions'],context,time=time)
        return context,digests
    def _signed_target(self,ident,time):
        from quorum_exchange_support import check
        context=json.loads(bytes.fromhex(self.group.live()[1]['snapshot']['context']))
        witness=next((w for w in context['ordering']['witnesses'] if credential(w)==ident),None)
        if witness is None:raise ValueError('Current witness target')
        row=self.db.execute('SELECT wrapper,digest FROM qo_signed_exchange_support WHERE group_id=? AND identity=?',(self.group.scope()['group'],ident)).fetchone()
        if row is None:raise ValueError('Signed exchange support required')
        wrapper=json.loads(row[0]);digest=check(self.group.identity,wrapper,context,witness,time=time)
        if digest!=row[1]:raise ValueError('Signed support digest')
        return dict(kind='signed-assertion7',digest=digest)
    def receive(self,wire,*,time):
        raw=select(wire);value,proof=parse(raw)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            if value['scope']!=self.group.scope():raise ValueError('Current exchange scope')
            if value['version']=='1':
                context,digests=self._signed(value,proof,time);self._signed_target(self.group.device['identity'],time)
                from quorum_exchange_support import retain_locked
                retain_locked(self.db,value['scope']['group'],value['witnessAssertions'],digests)
            else:self._support(self.group.device['identity'],time)
            # Retention alone grants no vote, installation, membership or application effect.
            old=self.db.execute('SELECT content FROM qo_exchange_received WHERE root=?',(proof.root,)).fetchone()
            if not old:self.db.execute('INSERT INTO qo_exchange_received VALUES(?,?)',(proof.root,raw))
            self.db.execute('COMMIT');return dict(status='already-retained' if old else 'retained',root=proof.root,kind=proof.result['kind'])
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def vote(self,store,kind,root,*,time):
        """Explicit local action on retained evidence; receipt never calls this."""
        if kind not in ('prepare','commit'):raise ValueError('Explicit exchange vote kind')
        row=self.db.execute('SELECT content FROM qo_exchange_received WHERE root=?',(root,)).fetchone()
        if not row:raise ValueError('Retained exchange required')
        value,proof=parse(row[0])
        if value['version']=='1':self._signed(value,proof,time)
        else:self._support(self.group.device['identity'],time)
        candidate=next((c for c in value['candidates'] if candidate_id(c)==proof.result['candidate']),None)
        if candidate is None:raise ValueError('Selected candidate required')
        return self.group.vote(store,kind,bytes.fromhex(value['proof']),candidate,time=time,candidate_dependencies=value['candidates'],before_vote=lambda:(self._signed(value,proof,time),self._signed_target(self.group.device['identity'],time)) if value['version']=='1' else self._support(self.group.device['identity'],time))
    def prepare(self,delivery,raw,*,envelope_sender,recipient,association_targets,time):
        value,proof=parse(raw)
        if not isinstance(delivery,str) or not delivery.isascii() or not delivery.isalnum():raise ValueError('Delivery ID')
        if set(recipient)!={'mailbox','principal','device'}:raise ValueError('Exact target')
        selected=targets(association_targets,[recipient['mailbox']])
        if selected is None:raise ValueError('Explicit target route')
        request=canonical(dict(raw=raw.hex(),sender=envelope_sender,recipient=recipient,targets=selected))
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT request,wire FROM quorum_prepared WHERE id=?',(delivery,)).fetchone()
            if old:
                if old[0]!=request:raise ValueError('Immutable exchange conflict')
                self.db.execute('COMMIT');return old[1]
            if value['scope']!=self.group.scope():raise ValueError('Current exchange scope')
            if value['version']=='1':
                self._signed(value,proof,time);support=self._signed_target(credential(recipient),time);self._signed_target(self.group.device['identity'],time)
            else:support=self._support(credential(recipient),time);self._support(self.group.device['identity'],time)
            if credential(recipient) not in {credential(w) for w in value['scope']['ordering']['witnesses']}:raise ValueError('Witness recipient required')
            state=self.group.live()[1];setting=self.db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone();trust=json.loads(setting[1])['trustPolicy']
            metadata=call(self.sender.binary,op='inspect-send',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.group.device['key'])['metadata']
            deps=self.sender._authority(metadata,time,trust);checked=check_locked(self.sender.associations,selected,metadata,time,trust,verification=self.sender._verification_enabled())
            if not any((d['principal'],d['device'],d['mailbox'])==(recipient['principal'],recipient['device'],recipient['mailbox']) for d in checked):raise ValueError('Exact exchange route')
            wire=mime_package(raw);evidence=dict(root=proof.root,scope=scope_digest(value['scope']),target=credential(recipient),support=support,wireDigest=hashlib.sha256(wire).hexdigest())
            envelope=dict(sender=envelope_sender,recipients=[recipient['mailbox']]);associations=dict(mode='selected-association',targets=selected,dependencies=checked)
            self.db.execute('INSERT INTO quorum_prepared VALUES(?,?,?,?,?,?,?,?,?,?)',(delivery,KIND,request,wire,canonical(metadata),canonical(deps),setting[0],canonical(envelope),canonical(associations),canonical(evidence)))
            self.db.execute('COMMIT');return wire
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def validate_locked(self,delivery,time):
        row=self.db.execute('SELECT kind,wire,evidence FROM quorum_prepared WHERE id=?',(delivery,)).fetchone()
        if not row or row[0]!=KIND:raise ValueError('Fixed exchange contract')
        evidence=json.loads(row[2]);value,proof=parse(select(row[1]))
        if value['scope']!=self.group.scope() or proof.root!=evidence['root'] or hashlib.sha256(row[1]).hexdigest()!=evidence['wireDigest']:raise ValueError('Current immutable exchange')
        if value['version']=='1':
            self._signed(value,proof,time);self._signed_target(self.group.device['identity'],time);support=self._signed_target(evidence['target'],time)
        else:
            self._support(self.group.device['identity'],time);support=self._support(evidence['target'],time)
        if support!=evidence['support']:raise ValueError('exchange-support-held')
        return evidence
