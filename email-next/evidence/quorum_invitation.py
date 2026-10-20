"""Immutable established6 export from retained certified decisions; fixture transport."""
import base64,hashlib,json
from event_encoding import encode_event
from provider_mls import call,sign
from initial_roster import credential
from established_invitation import parse
from established_invitation_mime import package
from passive_discovery import decode_passive_discovery,uint64
from passive_discovery_verify import verify_passive_discovery
from mls_receive import LockedIdentity
from ordering_mls import candidate_id
from ordering_certificates import encode
import group_instances

def b64(raw):return base64.b64encode(raw).decode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
class QuorumInvitation:
    def __init__(self,group,sender):
        if group.db is not sender.db:raise ValueError('Shared admitted store')
        self.group=group;self.sender=sender;self.db=group.db
        self.db.execute('CREATE TABLE IF NOT EXISTS qo_invitations(id TEXT PRIMARY KEY,request BLOB NOT NULL,wire BLOB NOT NULL)')
    def prepare(self,invitation,decision,*,target,not_before,not_after,time):
        if not isinstance(invitation,str) or len(invitation)!=32 or any(c not in '0123456789abcdef' for c in invitation) or invitation=='0'*32:raise ValueError('Invitation ID')
        if not uint64(not_before)<=uint64(time['earliest'])<=uint64(time['latest'])<=uint64(not_after):raise ValueError('Invitation interval')
        request=encode(dict(decision=decision,target=target,notBefore=not_before,notAfter=not_after))
        self.db.execute('BEGIN IMMEDIATE')
        try:
            prior=self.db.execute('SELECT request,wire FROM qo_invitations WHERE id=?',(invitation,)).fetchone()
            if prior:
                if prior[0]!=request:raise ValueError('Immutable invitation conflict')
                self.db.execute('COMMIT');return prior[1]
            tip,state=self.group.live()
            if tip!=decision:raise ValueError('Exact current certified decision required')
            current=group_instances.current(self.db,state['snapshot']['group']);genesis=self.db.execute('SELECT anchor,roster FROM qo_genesis WHERE instance=?',(current['instance'],)).fetchone()
            path=[];seen=set();cursor=tip
            while cursor!='genesis':
                if cursor in seen:raise ValueError('History cycle')
                seen.add(cursor);row=self.db.execute('SELECT carrier FROM qo_history WHERE decision=?',(cursor,)).fetchone()
                if not row:raise ValueError('Complete certified history required')
                value=json.loads(row[0]);path.append(dict(candidate=value['candidate'],proof=b64(bytes.fromhex(value['proof'])),**({k:value[k] for k in ('applicationAssertions','witnessAssertions')} if value['version']=='2' else {})));cursor=value['candidate']['plan']['scope']['previousDecision']
            path.reverse();candidate=path[-1]['candidate'];plan=candidate['plan'];result=plan['result']
            if not self.db.execute('SELECT 1 FROM qo_staged WHERE candidate=?',(candidate_id(candidate),)).fetchone():raise ValueError('Local MLS Welcome author required')
            if len(plan['welcomes'])!=1 or plan['welcomes'][0]['recipients']!=[credential(target)]:raise ValueError('One exact joining recipient')
            interval=dict(earliest=not_before,latest=not_after);metadata=call(self.sender.binary,op='inspect-send',checkpoint=state['checkpoint'],key=self.group.device['key'],group=result['group'])['metadata'];self.sender._authority(metadata,interval,'allow-unverified')
            signed_exchange=self.db.execute('SELECT 1 FROM qo_signed_exchange_support WHERE group_id=?',(result['group'],)).fetchone() is not None
            members=[];proofs=[];refs=[]
            for m in sorted(result['members'],key=lambda m:m['identity']):
                row=self.db.execute('SELECT wrapper FROM qo_join_support WHERE identity=?',(m['identity'],)).fetchone()
                if row is None:row=self.db.execute('SELECT proof FROM initial_roster_members WHERE credential=? AND key=?',(m['identity'],m['key'])).fetchone()
                if row is None:
                    saved=self.db.execute('SELECT evidence FROM mls_established_support WHERE instance=? AND credential=?',(current['instance'],m['identity'])).fetchone()
                    if saved:row=(encode_event(json.loads(saved[0])['wrapper']),)
                if row is None:raise ValueError('Exact current signed member assertion required')
                d=decode_passive_discovery(row[0]);v=d['assertion']['value']
                if verify_passive_discovery(row[0],LockedIdentity(self.group.identity),time=interval,trust_policy='allow-unverified')['status']!='snapshot-authorized-unverified':raise ValueError('Current member assertion')
                from application_support import supports
                context=json.loads(bytes.fromhex(result['context']))
                if v['version']!=('7' if signed_exchange else '6'):raise ValueError('Exact lifecycle member assertion version')
                if not supports(v,context['application'],'endpoint-quorum-v0') or credential(v)!=m['identity']:raise ValueError('Member tuple binding')
                member=dict(principal=v['principal'],device=v['device'],signingKey=m['key'],state=v['state'],binding=v['binding']);members.append(member);proofs.append(json.loads(row[0]));refs.append(dict(principal=v['principal'],device=v['device'],digest=d['assertion']['digest'],signature=d['signature'].hex()))
                if m['identity']==credential(target):target_proof=d;target_member=member
                if m['identity']==self.group.device['identity']:creator_member=member;creator_bundle=json.loads(row[0])['identity']
            package_bytes=target_proof['assertion']['key_package_octets'];reference=call(self.sender.binary,op='package-reference',checkpoint=state['checkpoint'],key=self.group.device['key'],package=package_bytes.hex())['reference']
            value=dict(version='7' if signed_exchange else '6',purpose='mls-established-membership-invitation',invitation=invitation,profile='mls-1-0001',conversation=context['conversation'],creator={k:creator_member[k] for k in ('principal','device','state','binding')},target=dict(**{k:target_member[k] for k in ('principal','device','state','binding')},mailbox=target_proof['assertion']['value']['mailbox']),group=b64(bytes.fromhex(result['group'])),previousEpoch=str(int(result['epoch'])-1),epoch=result['epoch'],previousGroupContextDigest=sha(bytes.fromhex(plan['scope']['predecessor'])),resultGroupContextDigest=sha(bytes.fromhex(result['predecessor'])),decision=decision,keyPackageRef=b64(bytes.fromhex(reference)),keyPackageDigest=sha(package_bytes),notBefore=not_before,notAfter=not_after,context=b64(bytes.fromhex(result['context'])),applicationContextDigest=sha(bytes.fromhex(result['context'])),members=members,welcome=b64(bytes.fromhex(plan['welcomes'][0]['bytes'])),applicationAssertions=refs,genesis=genesis[0],orderingPath=path)
            raw=encode_event(value);wrapper=encode_event(dict(payload=b64(raw),signature=sign(self.sender.binary,self.group.device,'email-next/mls-established-membership-invitation/v'+value['version'],raw),identity=creator_bundle,applicationAssertions=proofs));parse(wrapper);wire=package(wrapper)
            self.db.execute('INSERT INTO qo_invitations VALUES(?,?,?)',(invitation,request,wire));self.db.execute('COMMIT');return wire
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
