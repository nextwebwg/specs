"""Fixed initial-invitation preparation and release over configured SMTP worker."""
import base64
import hashlib
import json
import uuid
from email import policy
from email.parser import BytesParser
from event_encoding import encode_event
from passive_discovery import decode_passive_discovery,uint64
from passive_discovery_verify import verify_passive_discovery
from passive_discovery_package import validate_package
from mls_receive import LockedIdentity,FORMAT
from provider_mls import call,sign
from sender_release import canonical
from application_agreement import profile
from application_support import supports
from application_invitation import parse
from invitation_mime import package,select
from membership_episodes import install
from sender_association import check_locked

KIND='initial-application-invitation-v1'

class ApplicationInvitationRelease:
    def __init__(self,sender):
        self.sender=sender;self.db=sender.db
        if self.db.in_transaction:raise ValueError('Initialize outside transaction')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS initial_application_packages(reference TEXT PRIMARY KEY,delivery TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS initial_invitation_prepared(id TEXT PRIMARY KEY,request TEXT NOT NULL,wire BLOB NOT NULL,metadata TEXT NOT NULL,dependencies TEXT NOT NULL,policy_revision INTEGER NOT NULL,envelope TEXT NOT NULL,associations TEXT NOT NULL,proofs BLOB NOT NULL);
        ''')
        from signed_initial_instances import initialize
        initialize(self.db)
    def _proofs(self,selected,application,time,trust_policy,creator,since,until,ordering='fixed-roster-v0'):
        if not isinstance(selected,list) or len(selected)!=2:raise ValueError('Two selected devices required')
        result=[];seen=set()
        for choice in selected:
            if set(choice)!={'wrapper','mailbox','generation','digest'}:raise ValueError('Selection fields')
            decoded=decode_passive_discovery(choice['wrapper']);a=decoded['assertion'];v=a['value']
            if v['version']!=('2' if 'payload' in application else '1') or a['digest']!=choice['digest'] or v['mailbox']!=choice['mailbox']:raise ValueError('Selected assertion')
            verified=verify_passive_discovery(choice['wrapper'],LockedIdentity(self.sender.identity),time=time,trust_policy=trust_policy)
            if verified.get('status')!='snapshot-authorized-unverified':raise ValueError('Current assertion authority')
            association=self.sender.associations._current(choice['mailbox'])
            if not association or not association['enabled'] or association['generation']!=choice['generation'] or association['principal']!=v['principal']:raise ValueError('Changed association')
            eligible=self.sender.associations.eligible_observation_locked(choice['mailbox'],choice['digest'],time)
            retained=self.db.execute('SELECT assertion,signature FROM mailbox_observations WHERE mailbox=? AND digest=?',(choice['mailbox'],choice['digest'])).fetchone()
            if not eligible or retained!=(a['octets'],decoded['signature']):raise ValueError('Retained assertion proof')
            if not supports(v,application,ordering):raise ValueError('Application intersection')
            binding=next(x for x in decoded['identity']['bindings'] if x['digest']==v['binding'])['value']
            if uint64(since)<max(uint64(v['notBefore']),uint64(binding['notBefore'])) or uint64(until)>min(uint64(v['notAfter']),uint64(binding['notAfter'])):raise ValueError('Admission proof expiry')
            credential=(b'email-next/device/v0\0'+bytes.fromhex(v['principal'][5:])+bytes.fromhex(v['device'][5:])).hex()
            if credential in seen:raise ValueError('Duplicate device')
            seen.add(credential)
            if credential==creator:
                checked=LockedIdentity(self.sender.identity).check_device(bytes.fromhex(credential),bytes.fromhex(eligible['key']),role='send',time=time,trust_policy=trust_policy)
                if checked.get('status')!='authorized-unverified':raise ValueError('Creator send authority')
            result.append(dict(choice=choice,decoded=decoded,value=v,credential=credential,key=eligible['key'],association=association))
        if creator not in seen or len({r['value']['principal'] for r in result})!=2:raise ValueError('Initial creator/target scope')
        return sorted(result,key=lambda r:(r['value']['principal'],r['value']['device']))

    def prepare(self,delivery,*,device,selected,application,conversation,not_before,not_after,time,crash=None,designated=False):
        if not isinstance(delivery,str) or not delivery or not delivery.isascii() or not delivery.isalnum():raise ValueError('Delivery ID')
        if type(designated) is not bool:raise ValueError('Explicit ordering choice')
        version='2' if designated or 'payload' in application else '1';mode='designated-member-v0' if designated else 'fixed-roster-v0'
        encoded=profile(application)
        if any(op not in ({'answer','message','question','reaction','reaction-withdraw'}|({'attachment-message'} if application.get('payload')=='mime-contribution-v0' else set())) for op in application['operations']):raise ValueError('Unadvertised operation')
        if not uint64(not_before)<=uint64(time['earliest'])<=uint64(time['latest'])<=uint64(not_after) or uint64(not_after)-uint64(not_before)>604800:raise ValueError('Invitation interval')
        request=canonical(dict(device=device['identity'],key=device['key'],selected=[dict(c,wrapper=c['wrapper'].hex()) for c in selected],application=application,conversation=conversation,notBefore=not_before,notAfter=not_after,**({'invitationVersion':'2'} if version=='2' else {})))
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT request,wire FROM initial_invitation_prepared WHERE id=?',(delivery,)).fetchone()
            if old:
                if old[0]!=request:raise ValueError('Invitation delivery collision')
                self.db.execute('COMMIT');return old[1]
            if self.db.execute('SELECT 1 FROM mls_checkpoint').fetchone():raise ValueError('Existing conversation')
            setting=self.db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone()
            if not setting:raise ValueError('Configure policy')
            trust=json.loads(setting[1])['trustPolicy'];proofs=self._proofs(selected,application,time,trust,device['identity'],not_before,not_after,mode)
            creator=next(p for p in proofs if p['credential']==device['identity']);target=next(p for p in proofs if p['credential']!=device['identity'])
            if creator['key']!=device['key']:raise ValueError('Local creator key')
            package_bytes=target['decoded']['assertion']['key_package_octets']
            if package_bytes is None:raise ValueError('Target package missing')
            if validate_package(package_bytes,principal=target['value']['principal'],device=target['value']['device'],accepted_signing_key=bytes.fromhex(target['key']),earliest=not_before,latest=not_after,executable=self.sender.binary.with_name('validate-discovery-package'))!={'status':'package-valid'}:raise ValueError('Actual package validity')
            context=dict(version='3' if 'payload' in application else '2',purpose='conversation-context',conversation=conversation,profile='mls-1-0001',administrators=[creator['value']['principal']],application=application,ordering=(dict(kind=mode,principal=creator['value']['principal'],device=creator['value']['device']) if designated else dict(kind=mode)))
            context_raw=encode_event(context)
            group=call(self.sender.binary,op='create-initial-application',checkpoint=device['checkpoint'],key=device['key'],identity=device['identity'],package=package_bytes.hex(),context=context_raw.hex(),embedded=True)
            if self.db.execute('SELECT 1 FROM initial_application_packages WHERE reference=?',(group['reference'],)).fetchone():raise ValueError('Previously used package')
            metadata=call(self.sender.binary,op='inspect-send',checkpoint=group['checkpoint'],key=device['key'],group=group['group'])['metadata']
            expected=sorted((p['credential'],p['key']) for p in proofs)
            if sorted((m['identity'],m['key']) for m in metadata['members'])!=expected or metadata['epoch']!='1' or metadata['context']!=context_raw.hex() or metadata['senderIdentity']!=device['identity']:raise ValueError('Created group binding')
            value=dict(version=version,purpose='mls-new-conversation-invitation',invitation=uuid.uuid4().hex,profile='mls-1-0001',conversation=conversation,
                creator={k:creator['value'][k] for k in ('principal','device','state','binding')},target={k:target['value'][k] for k in ('principal','device','state','binding','mailbox')},
                group=base64.b64encode(bytes.fromhex(group['group'])).decode(),epoch='1',keyPackageRef=base64.b64encode(bytes.fromhex(group['reference'])).decode(),notBefore=not_before,notAfter=not_after,context=base64.b64encode(context_raw).decode(),welcome=base64.b64encode(bytes.fromhex(group['welcome'])).decode(),
                applicationAssertions=[dict(principal=p['value']['principal'],device=p['value']['device'],digest=p['decoded']['assertion']['digest'],signature=p['decoded']['signature'].hex()) for p in proofs])
            raw=encode_event(value);wrapper=dict(payload=base64.b64encode(raw).decode(),signature=sign(self.sender.binary,device,'email-next/mls-new-conversation-invitation/v'+version,raw),identity=json.loads(creator['choice']['wrapper'])['identity'],applicationAssertions=[json.loads(p['choice']['wrapper']) for p in proofs])
            encoded_wrapper=encode_event(wrapper);parse(encoded_wrapper)
            # Creator-side immutable signed selection accompanies accepted initial state.
            self.db.execute('INSERT INTO mls_checkpoint VALUES(1,0,?,?,?)',(FORMAT,group['group'],json.dumps(group['checkpoint']).encode()))
            for p in proofs:
                self.db.execute('INSERT INTO mls_application_agreement VALUES(?,?,?,?)',(group['group'],p['credential'],p['key'],encoded))
                self.db.execute("INSERT INTO mls_application_agreement_provenance VALUES(?,?,'signed-initial-creation',?)",(group['group'],p['credential'],delivery))
            install(self.db,metadata,'signed-initial-creation:'+hashlib.sha256(raw).hexdigest())
            if designated:self.db.execute("INSERT INTO mls_configured_context VALUES(?,'configured-endpoint-v0')",(group['group'],))
            dependencies=self.sender._authority(metadata,time,trust)
            route=dict(mailbox=target['value']['mailbox'],generation=target['choice']['generation'],principal=target['value']['principal'],observation=target['choice']['digest'])
            associations=dict(mode='selected-association',targets=[route],dependencies=check_locked(self.sender.associations,[route],metadata,time,trust))
            mime=BytesParser(policy=policy.SMTP).parsebytes(package(encoded_wrapper));mime.replace_header('From',creator['value']['mailbox']);mime.replace_header('To',target['value']['mailbox']);mime['Message-ID']='<'+uuid.uuid4().hex+'@invitation.example.invalid>'
            wire=mime.as_bytes();proof_record=encode_event(dict(selected=[dict(c,wrapper=c['wrapper'].hex()) for c in selected],creator=device['identity'],application=application,notAfter=not_after,notBefore=not_before))
            self.db.execute('INSERT INTO initial_application_packages VALUES(?,?)',(group['reference'],delivery))
            self.db.execute('INSERT INTO initial_invitation_prepared VALUES(?,?,?,?,?,?,?,?,?)',(delivery,request,wire,canonical(metadata),canonical(dependencies),setting[0],canonical(dict(sender=creator['value']['mailbox'],recipients=[target['value']['mailbox']])),canonical(associations),proof_record))
            from signed_initial_instances import qualify_signed_initial_locked
            qualify_signed_initial_locked(self.db,self.sender.binary,local_key=device['key'])
            if crash:crash('before-commit')
            self.db.execute('COMMIT');return wire
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise

    def validate_locked(self,delivery,time):
        if not self.db.in_transaction:raise ValueError('Caller transaction required')
        row=self.db.execute('SELECT wire,proofs FROM initial_invitation_prepared WHERE id=?',(delivery,)).fetchone()
        if not row:raise ValueError('Invitation not prepared')
        proof=json.loads(row[1]);_,raw,value,_,_,_=parse(select(row[0]))
        if not uint64(proof['notBefore'])<=uint64(time['earliest'])<=uint64(time['latest'])<=uint64(proof['notAfter']):raise ValueError('Invitation expired')
        selected=[dict(c,wrapper=bytes.fromhex(c['wrapper'])) for c in proof['selected']]
        setting=json.loads(self.db.execute('SELECT policy FROM sender_policy WHERE id=1').fetchone()[0])
        self._proofs(selected,proof['application'],time,setting['trustPolicy'],proof['creator'],proof['notBefore'],proof['notAfter'],json.loads(base64.b64decode(value['context']))['ordering']['kind'])
        return dict(contract='initial-application-invitation-v'+value['version'],invitation=value['invitation'],payload=hashlib.sha256(raw).hexdigest())
