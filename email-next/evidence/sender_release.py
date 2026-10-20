"""Configured-roster sender preparation and local release experiment.

Caller configures exact mailbox targets. This does not resolve mailbox associations
or establish verified ownership. sender_worker provides a separately locked loopback-only submission path.
"""
import uuid
import json
import subprocess
from pathlib import Path
from email import policy as email_policy
from email.parser import BytesParser
from event_encoding import decode_event
from mls_receive import MlsReceive, LockedIdentity
from mls_mime import package
from provider_mls import call
from mailbox_association_store import MailboxAssociationStore
from sender_association import targets,check_locked


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))


class SenderRelease:
    def __init__(self,identity,binary):
        self.identity=identity;self.db=identity.db;self.binary=Path(binary)
        if self.db.in_transaction:raise ValueError('Initialize outside transaction')
        self.associations=MailboxAssociationStore(identity)
        # Same checkpoint table as receive; no second source of group truth.
        self.receiver=MlsReceive(identity,self.binary.with_name('receive-staged'))
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS sender_payloads(delivery TEXT PRIMARY KEY,event BLOB NOT NULL,payload BLOB NOT NULL,representation TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS local_author_evidence(digest TEXT PRIMARY KEY,delivery TEXT NOT NULL,metadata TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS sender_policy(id INTEGER PRIMARY KEY CHECK(id=1),revision INTEGER NOT NULL,policy TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS sender_prepared(id TEXT PRIMARY KEY,request TEXT NOT NULL,application BLOB NOT NULL,wire BLOB NOT NULL,metadata TEXT NOT NULL,dependencies TEXT NOT NULL,policy_revision INTEGER NOT NULL,envelope TEXT NOT NULL);
        ''')
        if 'associations' not in [r[1] for r in self.db.execute('PRAGMA table_info(sender_prepared)')]:
            self.db.execute('ALTER TABLE sender_prepared ADD COLUMN associations TEXT NOT NULL DEFAULT \'{"mode":"configured-roster"}\'')

    def configure(self,*,expected_revision,trust_policy='allow-unverified',verification_mechanism=None):
        if type(expected_revision)!=int or not 0<=expected_revision<2**63-1:raise ValueError('Policy revision')
        if trust_policy not in ('allow-unverified','require-verification'):raise ValueError('Trust policy')
        if verification_mechanism not in (None,'human-comparison-v0'):raise ValueError('Unsupported verification mechanism')
        settings={'trustPolicy':trust_policy,'protection':'mls-required','freshness':'local-current'}
        if verification_mechanism:settings['verificationMechanism']=verification_mechanism
        value=canonical(settings)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row=self.db.execute('SELECT revision FROM sender_policy WHERE id=1').fetchone()
            revision=row[0] if row else 0
            if expected_revision!=revision:raise ValueError('Stale policy')
            self.db.execute('INSERT OR REPLACE INTO sender_policy VALUES(1,?,?)',(revision+1,value))
            self.db.execute('COMMIT');return revision+1
        except BaseException:
            self.db.execute('ROLLBACK');raise

    def _application_agreement(self,metadata):
        import group_instances
        current=group_instances.optional_current(self.db,metadata['group'])
        return self.receiver.application_agreement.resolve(metadata['group'],metadata['members'],instance=current['instance'] if current else None)

    def _verification_enabled(self):
        row=self.db.execute('SELECT policy FROM sender_policy WHERE id=1').fetchone()
        return bool(row and json.loads(row[0]).get('verificationMechanism')=='human-comparison-v0')

    def _authority(self,metadata,time,trust_policy):
        context=decode_event(bytes.fromhex(metadata['context']))['value']
        if context.get('version') in ('2','3','4','5','6','7'):
            agreement=self._application_agreement(metadata)
            if agreement is None or agreement!=context.get('application'):raise ValueError('Current application agreement')
        if context.get('version')=='7' and not self.receiver.configured_quorum_ordering(metadata['group'],metadata['context']):raise ValueError('Current quorum admission')
        dependencies=[];identity=LockedIdentity(self.identity)
        if self._verification_enabled():
            from human_verification import HumanVerifiedIdentity
            identity=HumanVerifiedIdentity(self.identity)
        for member in metadata['members']:
            role='send' if member['identity']==metadata['senderIdentity'] else 'receive'
            checked=identity.check_device(bytes.fromhex(member['identity']),bytes.fromhex(member['key']),role=role,time=time,trust_policy=trust_policy)
            if checked['status']!='authorized-unverified':raise ValueError('Current authority: '+checked['status'])
            dependencies.append(dict(identity=member['identity'],key=member['key'],**checked))
        if not any(d['identity']==metadata['senderIdentity'] for d in dependencies):raise ValueError('Sender absent')
        return dependencies

    def retention_preflight(self,time):
        import secret_retention as retention
        if self.db.execute('SELECT 1 FROM mls_retention_policy').fetchone():
            result=retention.SecretRetention(self.receiver).maintain(time=time)
            if result and result['status']=='retired':raise ValueError('Retention retired group')

    def prepare(self,delivery_id,application,**options):
        self.retention_preflight(options['time'])
        return self._prepare(delivery_id,application,owned_transaction=True,**options)

    def _prepare(self,delivery_id,application,*,key,envelope_sender,recipients,time,association_targets=None,source_token=None,resources=None,crash=lambda stage:None,owned_transaction):
        MlsReceive._policy(time,'allow-unverified')
        if not isinstance(delivery_id,str) or not delivery_id or not delivery_id.isascii() or not delivery_id.isalnum():raise ValueError('Local delivery ID')
        if not isinstance(application,bytes):raise ValueError('Application bytes')
        decoded=decode_event(application)['value']
        if decoded.get('purpose')!='contribution' or decoded.get('operation',{}).get('kind') not in ('message','question','answer','hosted-holder-observation','reaction','reaction-withdraw','attachment-message','rich-message','service-question','edit'):raise ValueError('Unsupported contribution')
        # External disclosure requires the separate durable fallback adapter.

        from passive_discovery import mailbox_syntax
        if not isinstance(recipients,list) or not recipients or len(set(recipients))!=len(recipients):raise ValueError('Recipients')
        for address in [envelope_sender,*recipients]:mailbox_syntax(address)
        selected=targets(association_targets,recipients)
        request_value=dict(application=application.hex(),key=key,sender=envelope_sender,recipients=recipients)
        if resources is not None:
            if not isinstance(resources,dict) or any(not isinstance(k,str) or not isinstance(v,bytes) for k,v in resources.items()) or sum(len(v) for v in resources.values())>1048576:raise ValueError('Resource input bound')
            request_value['resources']={k:v.hex() for k,v in sorted(resources.items())}
        if selected is not None:request_value['associationTargets']=selected
        if source_token is not None:request_value['sourceToken']=source_token
        request=canonical(request_value)
        if owned_transaction:self.db.execute('BEGIN IMMEDIATE')
        elif not self.db.in_transaction:raise ValueError('Preparation transaction required')
        try:
            import secret_retention as retention
            setting=self.db.execute('SELECT watermark FROM mls_retention_policy').fetchone()
            if not owned_transaction and setting and int(time['latest'])>setting[0]:raise ValueError('Retention maintenance required before caller transaction')
            if decoded['operation']['kind']=='hosted-holder-observation':
                if not self.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='hosted_observers'").fetchone():raise ValueError('Hosted provenance required')
                binding=self.db.execute('SELECT application FROM hosted_observers WHERE delivery=?',(delivery_id,)).fetchone()
                if not binding or binding[0]!=application:raise ValueError('Hosted provenance required')
            old=self.db.execute('SELECT request,wire FROM sender_prepared WHERE id=?',(delivery_id,)).fetchone()
            if old:
                if old[0]!=request:raise ValueError('Delivery ID conflict')

                if owned_transaction:self.db.execute('COMMIT')
                return old[1]
            if source_token is not None and self.receiver.journal.snapshot_with_token(decoded['conversation'])['token']!=source_token:raise ValueError('Changed question snapshot')
            policy=self.db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone()
            if not policy:raise ValueError('Configure policy first')
            settings=json.loads(policy[1])
            from hosted_disclosure import check_plans
            check_plans(self.db,application,policy[0])

            row=self.db.execute('SELECT revision,group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
            if not row:raise ValueError('No accepted group')
            args=dict(checkpoint=json.loads(row[2]),key=key,group=row[1])
            metadata=call(self.binary,op='inspect-send',**args)['metadata']
            context=decode_event(bytes.fromhex(metadata['context']))['value']
            principal='enp0:'+bytes.fromhex(metadata['senderIdentity'])[21:53].hex()
            if decoded.get('principal')!=principal or decoded.get('conversation')!=context['conversation']:raise ValueError('Application context')
            audience=sorted(set('enp0:'+bytes.fromhex(m['identity'])[21:53].hex() for m in metadata['members']))
            if decoded.get('audience')!=audience:raise ValueError('Application audience')
            records=[]
            for record in self.receiver.journal.snapshot(decoded['conversation']):
                item={'reference':record['reference'],'state':'conflict' if record['state']=='conflict' else 'valid'}
                if record['state']=='recorded':item['event']=decode_event(record['octets'][0])['value']
                records.append(item)
            if decoded['operation']['kind']=='edit':
                from journal_edit_view import records_locked
                records=records_locked(self.receiver,decoded['conversation'])
            projection=subprocess.run(['node',str(Path(__file__).with_name('check-mls-contribution.mjs'))],input=json.dumps({'event':decoded,'credential':metadata['senderIdentity'],'context':context,'members':[m['identity'] for m in metadata['members']],'configuredEndpointOrdering':self.receiver.configured_endpoint_ordering(metadata['group']),'configuredQuorumOrdering':self.receiver.configured_quorum_ordering(metadata['group'],metadata['context']),'configuredApplication':self._application_agreement(metadata),'records':records}),text=True,capture_output=True,check=True,timeout=10)
            if projection.stdout!='projected-context-matched':raise ValueError('Application contract')
            if settings['trustPolicy']=='require-verification' and selected is None:raise ValueError('verification-required: exact selected mailbox routes required')
            dependencies=self._authority(metadata,time,settings['trustPolicy'])
            associations={'mode':'configured-roster'} if selected is None else {'mode':'selected-association','targets':selected,'dependencies':check_locked(self.associations,selected,metadata,time,settings['trustPolicy'],verification=self._verification_enabled())}
            from application_payload import encode as encode_payload
            payload,representation=encode_payload(self,application,context,self._application_agreement(metadata),configured_ordering=self.receiver.configured_endpoint_ordering(metadata['group']),configured_quorum_ordering=self.receiver.configured_quorum_ordering(metadata['group'],metadata['context']),resources=resources)
            staged=call(self.binary,op='send',application=payload.hex(),**args)
            if staged['metadata']!=metadata:raise ValueError('Changed crypto metadata')
            maintained=retention.maintain_locked(self.db,self.binary,time,checkpoint=staged['checkpoint'])
            if maintained:
                staged['checkpoint']=maintained['checkpoint']
                if maintained['status']=='retired':
                    if owned_transaction:
                        self.db.execute('COMMIT');raise ValueError('Retention retired group')
                    raise ValueError('Staged retention budget exceeded; caller rollback required')
            mime=BytesParser(policy=email_policy.SMTP).parsebytes(package(bytes.fromhex(staged['wire'])))
            mime.replace_header('From',envelope_sender);mime.replace_header('To',', '.join(recipients))
            mime['Message-ID']='<'+uuid.uuid4().hex+'@sender.example.invalid>'
            wire=mime.as_bytes();crash('after-encryption')
            self.db.execute('UPDATE mls_checkpoint SET revision=revision+1,snapshot=? WHERE id=1',(json.dumps(staged['checkpoint']).encode(),))
            self.db.execute('INSERT INTO sender_prepared VALUES(?,?,?,?,?,?,?,?,?)',(delivery_id,request,application,wire,canonical(metadata),canonical(dependencies),policy[0],canonical({'sender':envelope_sender,'recipients':recipients}),canonical(associations)))
            self.db.execute('INSERT INTO sender_payloads VALUES(?,?,?,?)',(delivery_id,application,payload,canonical(representation)))
            import hashlib
            recorded=self.receiver.journal.append_validated_in_transaction(application,{k:decoded[k] for k in ('conversation','principal','event')})
            if recorded['state']=='conflict':raise ValueError('Local event collision')
            self.db.execute('INSERT OR IGNORE INTO local_author_evidence VALUES(?,?,?)',(hashlib.sha256(application).hexdigest(),delivery_id,canonical(metadata)))
            crash('before-prepare-commit')
            if owned_transaction:self.db.execute('COMMIT')
            return wire
        except BaseException:
            if owned_transaction and self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
