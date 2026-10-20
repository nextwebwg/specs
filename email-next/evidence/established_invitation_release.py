"""Fixed configured-v1 Welcome submission; SMTP ordering is local policy only."""
import json
import uuid
from email import policy
from email.parser import BytesParser
from event_encoding import encode_event
from established_invitation import parse,b64,sha
from established_invitation_mime import package,select
from provider_mls import call,sign
from passive_discovery import decode_passive_discovery,uint64,mailbox_syntax
from passive_discovery_verify import verify_passive_discovery
from passive_discovery_package import validate_package
from mls_receive import MlsReceive,LockedIdentity
from group_transitions import ids
from sender_release import canonical
from sender_association import check_locked,targets
from commit_history import CommitHistory
from control_release import ControlRelease,CONTRACT
from transition_carrier import parse as parse_control
from transition_mime import select as select_control
import transition_support
KIND='configured-established-invitation-v0'

class EstablishedInvitationRelease:
    def __init__(self,sender,history):
        if type(history) is not CommitHistory or history.db is not sender.db:raise ValueError('Shared history required')
        self.sender=sender;self.history=history;self.db=sender.db
        if self.db.in_transaction:raise ValueError('Initialize outside transaction')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS established_invitation_prepared(id TEXT PRIMARY KEY,request TEXT NOT NULL,wire BLOB NOT NULL,metadata TEXT NOT NULL,dependencies TEXT NOT NULL,policy_revision INTEGER NOT NULL,envelope TEXT NOT NULL,associations TEXT NOT NULL,evidence TEXT NOT NULL,state TEXT NOT NULL,archive TEXT);
        ''')
    def _decision(self,decision):
        row=self.db.execute('SELECT state FROM gt_decision WHERE digest=?',(decision,)).fetchone()
        if not row:raise ValueError('Missing accepted decision')
        record=json.loads(row[0]);before={(m['identity'],m['key']) for m in record['before']['members']};after={(m['identity'],m['key']) for m in record['after']['members']}
        if sha(bytes.fromhex(record['wire']))!=decision or before-after or len(after-before)!=1 or not record.get('welcome'):raise ValueError('One target Add decision required')
        context=json.loads(bytes.fromhex(record['after']['context']))
        if context.get('version') not in ('1','2','3','4','5','6'):raise ValueError('Established context version')
        if context['version'] in ('2','3','4','5','6'):transition_support.wrappers(self.db,record)
        self.history.coordinator._authorize(record,after-before,{'earliest':'0','latest':'0'},historical=True)
        return record,next(iter(after-before))
    def _ordering(self,record,deliveries,*,require_accepted):
        if not isinstance(deliveries,list) or not deliveries or not all(isinstance(d,str) for d in deliveries) or len(deliveries)!=len(set(deliveries)):raise ValueError('Predecessor deliveries')
        needed={ids(m['identity']) for m in record['before']['members'] if m['identity']!=record['sender']};covered=set();mailboxes={}
        for delivery in deliveries:
            row=self.db.execute('SELECT wire,evidence,associations FROM control_prepared WHERE id=?',(delivery,)).fetchone()
            if not row:raise ValueError('Missing predecessor control')
            evidence=json.loads(row[1]);_,commit=parse_control(select_control(row[0]))
            if evidence.get('contract')!=CONTRACT or evidence.get('decision')!=sha(bytes.fromhex(record['wire'])) or commit!=bytes.fromhex(record['wire']):raise ValueError('Different predecessor Commit')
            accepted=set();accepted_proofs=[]
            if self.db.execute("SELECT 1 FROM sqlite_master WHERE name='sender_attempts'").fetchone():
                for state,attempt_raw,result_raw in self.db.execute('SELECT state,evidence,result FROM sender_attempts WHERE delivery=? AND kind=?',(delivery,CONTRACT)):
                    if state=='accepted':
                        attempt=json.loads(attempt_raw);result=json.loads(result_raw)
                        actual=set(result.get('acceptedRecipients',[]))&set(attempt['envelope']['recipients'])
                        accepted.update(actual)
                        if attempt.get('associationMode')=='selected-association':accepted_proofs.extend(p for p in attempt.get('associations',[]) if p['mailbox'] in actual)
            for recipient in evidence['recipients']:
                pair=(recipient['principal'],recipient['device']);mailbox=recipient['mailbox']
                if pair not in needed:raise ValueError('Predecessor device coverage')
                key=next(m['key'] for m in record['before']['members'] if ids(m['identity'])==pair)
                def matches(proof):return (proof.get('mailbox'),proof.get('principal'),proof.get('device'),proof.get('key'))==(mailbox,*pair,key)
                association=json.loads(row[2]);bound=association.get('mode')=='selected-association' and any(matches(p) for p in association.get('dependencies',[]))
                qualified=bound and (not require_accepted or any(matches(p) for p in accepted_proofs))
                mailboxes.setdefault(mailbox,[]).append((pair,delivery,qualified))
                if require_accepted and mailbox not in accepted:raise ValueError('Predecessor handoff unresolved')
                covered.add(pair)
        for submissions in mailboxes.values():
            if len({pair for pair,_,_ in submissions})>1 and (not all(ok for _,_,ok in submissions) or len({delivery for _,delivery,_ in submissions})!=len(submissions)):
                raise ValueError('Shared mailbox requires separate evidence-bound device submissions')
        if covered!=needed:raise ValueError('Incomplete predecessor device coverage')
        return sorted([list(pair) for pair in covered])
    def _scope(self,record,target,decision,time,trust):
        path=self.history.path_locked(record['after']['predecessor'],target_identity=target[0],target_key=target[1],time=time,trust_policy=trust)
        if self.history.coordinator.live()['snapshot']['context']!=record['after']['context']:raise ValueError('Changed application context')
        row=self.db.execute('SELECT end_epoch FROM mls_membership_episode WHERE group_id=? AND identity=? AND key=? AND admission=?',(record['after']['group'],*target,decision)).fetchall()
        if row!=[(None,)]:raise ValueError('Original admission episode ended')
        return path
    def prepare(self,delivery,decision,*,key,creator_bundle,selected_wrapper,association_target,predecessor_deliveries,envelope_sender,not_before,not_after,time,crash=None):
        MlsReceive._policy(time,'allow-unverified');mailbox_syntax(envelope_sender)
        if not isinstance(delivery,str) or not delivery or not delivery.isascii() or not delivery.isalnum():raise ValueError('Delivery ID')
        if not uint64(not_before)<=uint64(time['earliest'])<=uint64(time['latest'])<=uint64(not_after):raise ValueError('Invitation interval')
        request=canonical(dict(decision=decision,key=key,bundle=creator_bundle,wrapper=selected_wrapper.hex(),target=association_target,controls=predecessor_deliveries,sender=envelope_sender,notBefore=not_before,notAfter=not_after))
        self.db.execute('BEGIN IMMEDIATE')
        try:
            prior=self.db.execute('SELECT request,wire FROM established_invitation_prepared WHERE id=?',(delivery,)).fetchone()
            if prior:
                if prior[0]!=request:raise ValueError('Welcome delivery conflict')
                self.db.execute('COMMIT');return prior[1]
            setting=self.db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone()
            if not setting:raise ValueError('Configure sender policy')
            trust=json.loads(setting[1])['trustPolicy'];record,target=self._decision(decision)
            self._ordering(record,predecessor_deliveries,require_accepted=False)
            path=self._scope(record,target,decision,time,trust)
            cp=self.db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone();checkpoint=json.loads(cp[1])
            metadata=call(self.sender.binary,op='inspect-send',checkpoint=checkpoint,group=cp[0],key=key)['metadata']
            if metadata['senderIdentity']!=record['sender']:raise ValueError('Current configured writer')
            interval={'earliest':not_before,'latest':not_after};dependencies=self.sender._authority(metadata,interval,trust)
            decoded=decode_passive_discovery(selected_wrapper);assertion=decoded['assertion'];v=assertion['value']
            if verify_passive_discovery(selected_wrapper,LockedIdentity(self.sender.identity),time=interval,trust_policy=trust).get('status')!='snapshot-authorized-unverified':raise ValueError('Selected assertion interval/authority')
            selected=targets([association_target],[v['mailbox']])
            if selected[0]['observation']!=assertion['digest']:raise ValueError('Selected assertion digest')
            checked=check_locked(self.sender.associations,selected,metadata,interval,trust)
            if (checked[0]['principal'],checked[0]['device'],checked[0]['key'])!=(*ids(target[0]),target[1]):raise ValueError('Selected target device mismatch')
            retained=self.db.execute('SELECT assertion,signature FROM mailbox_observations WHERE mailbox=? AND digest=?',(v['mailbox'],assertion['digest'])).fetchone()
            if retained!=(assertion['octets'],decoded['signature']):raise ValueError('Retained assertion proof')
            package_bytes=assertion['key_package_octets'];candidate=self.db.execute('SELECT packages FROM gt_candidate WHERE digest=?',(decision,)).fetchone()
            if package_bytes is None or not candidate or json.loads(candidate[0])!=[package_bytes.hex()]:raise ValueError('Accepted candidate package mismatch')
            if validate_package(package_bytes,principal=v['principal'],device=v['device'],accepted_signing_key=bytes.fromhex(target[1]),earliest=not_before,latest=not_after,executable=self.sender.binary.with_name('validate-discovery-package'))!={'status':'package-valid'}:raise ValueError('Package interval')
            reference=call(self.sender.binary,op='package-reference',checkpoint=checkpoint,key=key,package=package_bytes.hex())['reference']
            members=[]
            for member in record['after']['members']:
                p,d=ids(member['identity']);authority=LockedIdentity(self.sender.identity).check_device(bytes.fromhex(member['identity']),bytes.fromhex(member['key']),role='receive',time=interval,trust_policy=trust)
                if authority.get('status')!='authorized-unverified':raise ValueError('Welcome roster interval authority')
                members.append(dict(principal=p,device=d,signingKey=member['key'],state=authority['head'],binding=authority['binding']))
            members.sort(key=lambda m:(m['principal'],m['device']))
            def named(identity):return {k:next(m for m in members if (m['principal'],m['device'])==ids(identity))[k] for k in ('principal','device','state','binding')}
            context=bytes.fromhex(record['after']['context']);value=dict(version='0',purpose='mls-established-membership-invitation',invitation=uuid.uuid4().hex,profile='mls-1-0001',conversation=json.loads(context)['conversation'],creator=named(record['sender']),target=dict(named(target[0]),mailbox=v['mailbox']),group=b64(bytes.fromhex(cp[0])),previousEpoch=record['before']['epoch'],epoch=record['after']['epoch'],previousGroupContextDigest=sha(bytes.fromhex(record['before']['predecessor'])),resultGroupContextDigest=sha(bytes.fromhex(record['after']['predecessor'])),decision=decision,keyPackageRef=b64(bytes.fromhex(reference)),keyPackageDigest=sha(package_bytes),notBefore=not_before,notAfter=not_after,context=b64(context),applicationContextDigest=sha(context),members=members,welcome=b64(bytes.fromhex(record['welcome'])))
            extra={}
            if json.loads(context)['version'] in ('2','3','4','5','6'):
                records=transition_support.wrappers(self.db,record);proofs=[];refs=[]
                for member in members:
                    source=next(r for r in records if ids(r['credential'])==(member['principal'],member['device']))
                    proof_raw=bytes.fromhex(source['wrapper']);proof=decode_passive_discovery(proof_raw)
                    if source['credential']==target[0] and proof_raw!=selected_wrapper:raise ValueError('Target support changed after decision')
                    refs.append(dict(principal=member['principal'],device=member['device'],digest=proof['assertion']['digest'],signature=proof['signature'].hex()));proofs.append(json.loads(proof_raw))
                value.update(version={'2':'1','3':'2','4':'3','5':'4','6':'5'}[json.loads(context)['version']],applicationAssertions=refs);extra['applicationAssertions']=proofs
            raw=encode_event(value);wrapper=encode_event(dict(payload=b64(raw),signature=sign(self.sender.binary,dict(checkpoint=checkpoint,key=key),'email-next/mls-established-membership-invitation/v'+value['version'],raw),identity=creator_bundle,**extra));parsed=parse(wrapper)
            creator_binding=next((b for b in parsed[4]['bindings'] if b['digest']==value['creator']['binding']),None)
            if not creator_binding or creator_binding['value']['signingKey']!=key:raise ValueError('Creator bundle binding')
            mime=BytesParser(policy=policy.SMTP).parsebytes(package(wrapper));mime.replace_header('From',envelope_sender);mime.replace_header('To',v['mailbox']);mime['Message-ID']='<'+uuid.uuid4().hex+'@welcome.example.invalid>';wire=mime.as_bytes()
            associations=dict(mode='selected-association',targets=selected,dependencies=checked)
            evidence=dict(decision=decision,target=list(target),controls=predecessor_deliveries,wrapper=selected_wrapper.hex(),interval=interval)
            self.db.execute('INSERT INTO established_invitation_prepared VALUES(?,?,?,?,?,?,?,?,?,?,NULL)',(delivery,request,wire,canonical(metadata),canonical(dependencies),setting[0],canonical(dict(sender=envelope_sender,recipients=[v['mailbox']])),canonical(associations),canonical(evidence),'active'))
            self.history.pin_locked('welcome:'+delivery,[decision]+[s['decision'] for s in path['steps']],state='active')
            if crash:crash('before-commit')
            self.db.execute('COMMIT');return wire
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def validate_locked(self,delivery,time):
        if not self.db.in_transaction:raise ValueError('Caller transaction required')
        row=self.db.execute('SELECT wire,evidence,state FROM established_invitation_prepared WHERE id=?',(delivery,)).fetchone()
        if not row or row[2]!='active':raise ValueError('Welcome not active')
        e=json.loads(row[1]);_,raw,value,_,_=parse(select(row[0]));record,target=self._decision(e['decision'])
        if tuple(e['target'])!=target or value['decision']!=e['decision'] or value['welcome']!=b64(bytes.fromhex(record['welcome'])):raise ValueError('Welcome decision binding')
        if not uint64(value['notBefore'])<=uint64(time['earliest'])<=uint64(time['latest'])<=uint64(value['notAfter']):raise ValueError('Welcome expired')
        trust=json.loads(self.db.execute('SELECT policy FROM sender_policy WHERE id=1').fetchone()[0])['trustPolicy']
        interval=e['interval'];authority=LockedIdentity(self.sender.identity)
        for member in value['members']:
            credential=(b'email-next/device/v0\0'+bytes.fromhex(member['principal'][5:])+bytes.fromhex(member['device'][5:]))
            check=authority.check_device(credential,bytes.fromhex(member['signingKey']),role='receive',time=interval,trust_policy=trust)
            if check.get('status')!='authorized-unverified' or check['head']!=member['state'] or check['binding']!=member['binding']:raise ValueError('Changed Welcome roster dependency')
        creator=value['creator'];credential=b'email-next/device/v0\0'+bytes.fromhex(creator['principal'][5:])+bytes.fromhex(creator['device'][5:])
        key=next(m['signingKey'] for m in value['members'] if (m['principal'],m['device'])==(creator['principal'],creator['device']))
        check=authority.check_device(credential,bytes.fromhex(key),role='send',time=interval,trust_policy=trust)
        if check.get('status')!='authorized-unverified' or check['head']!=creator['state'] or check['binding']!=creator['binding']:raise ValueError('Changed creator send dependency')
        self._ordering(record,e['controls'],require_accepted=True)
        path=self._scope(record,target,e['decision'],time,trust)
        self.history.pin_locked('welcome:'+delivery,[e['decision']]+[s['decision'] for s in path['steps']],state='active')
        return dict(contract='established-membership-invitation-v'+value['version'],decision=e['decision'],payload=sha(raw),tip=path['tip'],path=[s['decision'] for s in path['steps']])
    def finish(self,delivery,*,worker,cancel=False):
        """Archive public evidence before unpinning; uncertainty stays explicit."""
        if worker.sender is not self.sender:raise ValueError('Matching worker required')
        worker._owned();self.db.execute('BEGIN IMMEDIATE')
        try:
            row=self.db.execute('SELECT state,evidence FROM established_invitation_prepared WHERE id=?',(delivery,)).fetchone()
            if not row:raise ValueError('Unknown Welcome')
            if row[0]!='active':self.db.execute('COMMIT');return row[0]
            attempts=list(self.db.execute('SELECT id,state,evidence,result FROM sender_attempts WHERE delivery=? AND kind=?',(delivery,KIND)))
            if any(a[1]=='released' for a in attempts):raise ValueError('Active attempt')
            accepted=any(a[1]=='accepted' and json.loads(a[3]).get('acceptedRecipients') for a in attempts)
            uncertain=any(a[1]=='uncertain' for a in attempts)
            if not cancel and not accepted:raise ValueError('Handoff incomplete')
            state='completed' if accepted else 'cancelled-uncertain' if uncertain else 'cancelled'
            records=[]
            for digest, in self.db.execute('SELECT digest FROM commit_history_pin WHERE owner=?',('welcome:'+delivery,)):
                record=self.db.execute('SELECT record FROM commit_history WHERE digest=?',(digest,)).fetchone()
                if not record:raise ValueError('Missing pinned history')
                records.append(dict(decision=digest,record=json.loads(record[0])))
            self.db.execute('UPDATE established_invitation_prepared SET state=?,archive=? WHERE id=?',(state,canonical(dict(records=records,attempts=attempts)),delivery))
            self.db.execute('DELETE FROM commit_history_pin WHERE owner=?',('welcome:'+delivery,));self.db.execute('COMMIT');return state
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
