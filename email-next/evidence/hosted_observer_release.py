"""Fixed observer preparation from authenticated retained exports, one SQLite database.

The observer authors the event. Holder possession never supplies mailbox identity.
"""
import base64
import hashlib
import json
from pathlib import Path
import uuid
from event_encoding import decode_event
from hosted_access import parse
from hosted_reply_admission import fill_template
from hosted_reply_export import EXPORT_MAX
from provider_mls import call
from hosted_projection import hosted_source_text
from sender_release import canonical

KIND='hosted-observer-submit-v1'

class HostedObserverRelease:
    def __init__(self,sender,hosted):
        self.sender=sender;self.hosted=hosted;self.db=sender.db
        if self.db.in_transaction:raise ValueError('Initialize outside transaction')
        path=self.db.execute('PRAGMA database_list').fetchone()[2]
        if not path or Path(path).resolve()!=Path(hosted.path).resolve():raise ValueError('Shared canonical database required')
        self.db.execute('''CREATE TABLE IF NOT EXISTS hosted_observers(service TEXT,grant_id TEXT,reply_operation TEXT,delivery TEXT UNIQUE,evidence TEXT,application BLOB,target BLOB,PRIMARY KEY(service,grant_id,reply_operation))''')
    def _source(self,evidence):
        row=self.db.execute('SELECT create_operation,grant_id,reply_operation,digest,state FROM hosted_exports WHERE id=?',(evidence,)).fetchone()
        if not row or row[4]!='observed':raise ValueError('Authenticated export required')
        create,grant,reply,digest,_=row
        if self.db.execute("SELECT 1 FROM hosted_exports WHERE grant_id=? AND reply_operation=? AND state!='observed'",(grant,reply)).fetchone():raise ValueError('Conflicting export')
        exported=decode_event(self.hosted.vault.get(self.db,'export:'+evidence,'hosted-reply-export',grant),max_octets=EXPORT_MAX)['value']
        raw=base64.urlsafe_b64decode(exported['request']+'='*((-len(exported['request']))%4));value=parse(raw,'hosted-holder-reply')
        creation=parse(self.hosted.vault.get(self.db,create,'hosted-grant-create',grant),'hosted-grant-create')
        template=self.hosted.vault.get(self.db,'observer-template:'+create,'hosted-observer-template',grant)
        if creation['version']!='1' or exported['service']!=self.hosted.vault.service or exported['grant']!=grant or exported['operation']!=reply or value['operation']!=reply or exported['replyDestination']!=creation['replyDestination'] or digest!=hashlib.sha256(raw).hexdigest():raise ValueError('Export binding')
        expected=dict(version='0',purpose='hosted-holder-result',service=self.hosted.vault.service,grant=grant,operation=reply,requestDigest=digest,outcome='confirmed',reason='stored',attribution='grant-holder')
        if exported['receipt']!=expected:raise ValueError('Export receipt')
        return creation,template,value,digest
    def _target(self,reference):
        rows=self.db.execute('SELECT octets FROM contributions WHERE conversation=? AND principal=? AND event=?',tuple(reference[k] for k in ('conversation','principal','event'))).fetchall()
        if len(rows)!=1:raise ValueError('Missing or conflicting target')
        raw=rows[0][0];digest=hashlib.sha256(raw).hexdigest()
        local=self.db.execute('SELECT p.application FROM local_author_evidence a JOIN sender_prepared p ON p.id=a.delivery WHERE a.digest=?',(digest,)).fetchone()
        received=self.db.execute("SELECT r.application FROM mls_receives r JOIN mls_application_acceptance a ON a.digest=? WHERE a.state='accepted' AND r.application=?",(digest,raw)).fetchone()
        if not (local and local[0]==raw or received and received[0]==raw):raise ValueError('Authenticated target required')
        return raw
    def prepare(self,evidence,*,key,envelope_sender,recipients,time,association_targets=None,crash=lambda stage:None):
        self.sender.retention_preflight(time)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            creation,template,reply,digest=self._source(evidence)
            target=self._target(creation['contribution'])
            if hosted_source_text(target)!=creation['content']['text']:raise ValueError('Hosted content target mismatch')
            existing=self.db.execute('SELECT delivery,evidence,application,target FROM hosted_observers WHERE service=? AND grant_id=? AND reply_operation=?',(self.hosted.vault.service,creation['grant'],reply['operation'])).fetchone()
            if existing:
                delivery,original,application,old_target=existing
                original_source=self._source(original)
                if original_source[2]!=reply or old_target!=target:raise ValueError('Immutable observation conflict')
                # Current source/target checks still run; exact application is never regenerated.
            else:
                delivery=uuid.uuid4().hex
                application=fill_template(template,reply['text'],uuid.uuid4().hex)
                self.db.execute('INSERT INTO hosted_observers VALUES(?,?,?,?,?,?,?)',(self.hosted.vault.service,creation['grant'],reply['operation'],delivery,evidence,application,target))
            wire=self.sender._prepare(delivery,application,key=key,envelope_sender=envelope_sender,recipients=recipients,time=time,association_targets=association_targets,crash=crash,owned_transaction=False)
            self.validate_locked(delivery,time)
            crash('before-observer-commit');self.db.execute('COMMIT');crash('after-observer-commit')
            return {'delivery':delivery,'wire':wire}
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def validate_locked(self,delivery,time):
        if not self.db.in_transaction:raise ValueError('Transaction required')
        row=self.db.execute('SELECT service,grant_id,reply_operation,evidence,application,target FROM hosted_observers WHERE delivery=?',(delivery,)).fetchone()
        if not row:raise ValueError('Observer mapping required')
        creation,template,reply,digest=self._source(row[3]);application=decode_event(row[4])['value']
        if row[0]!=self.hosted.vault.service or row[1]!=creation['grant'] or row[2]!=reply['operation'] or fill_template(template,reply['text'],application['event'])!=row[4] or self._target(creation['contribution'])!=row[5]:raise ValueError('Changed observer evidence')
        if hosted_source_text(row[5])!=creation['content']['text']:raise ValueError('Changed hosted target formatter')
        prepared=self.db.execute('SELECT application FROM sender_prepared WHERE id=?',(delivery,)).fetchone()
        if not prepared or prepared[0]!=row[4]:raise ValueError('Changed prepared observation')
        policy=self.db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone()
        saved=self.db.execute('SELECT request,metadata,dependencies,policy_revision FROM sender_prepared WHERE id=?',(delivery,)).fetchone()
        checkpoint=self.db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
        if not policy or not checkpoint or policy[0]!=saved[3]:raise ValueError('Changed observer policy')
        metadata=call(self.sender.binary,op='inspect-send',checkpoint=json.loads(checkpoint[1]),group=checkpoint[0],key=json.loads(saved[0])['key'])['metadata']
        if canonical(metadata)!=saved[1] or canonical(self.sender._authority(metadata,time,json.loads(policy[1])['trustPolicy']))!=saved[2]:raise ValueError('Changed observer authority or context')
        return {'contract':KIND,'service':row[0],'grant':row[1],'replyOperation':row[2],'requestDigest':digest,'applicationDigest':hashlib.sha256(row[4]).hexdigest()}
