"""Configured service control; accepted mail is not service authorization.

Registrations and credential resolution are trusted local inputs. No public
credential acquisition or universal registration discovery is implemented here.
"""
import hashlib,json,uuid
from event_encoding import decode_event,encode_event
from provider_mls import call
import group_instances as instances

class ServiceFlow:
    def __init__(self,sender,journal,*,key,registration,credential,transport):
        self.sender=sender;self.db=sender.db;self.journal=journal;self.key=key
        self.registration=registration;self.credential=credential;self.transport=transport
        self.db.execute('CREATE TABLE IF NOT EXISTS service_client_actions(id TEXT PRIMARY KEY,selection TEXT NOT NULL,raw BLOB NOT NULL,service TEXT NOT NULL)')

    def _source(self,reference,carrier,time):
        rows=[r for r in self.sender.receiver.journal.snapshot(reference['conversation']) if r['reference']==reference]
        if len(rows)!=1 or rows[0]['state']!='recorded':raise ValueError('Accepted question required')
        raw=rows[0]['octets'][0];event=decode_event(raw)['value']
        row=self.db.execute('SELECT application,evidence FROM mls_receives WHERE digest=?',(carrier,)).fetchone()
        accepted=self.db.execute('SELECT state FROM mls_application_acceptance WHERE digest=?',(hashlib.sha256(raw).hexdigest(),)).fetchone()
        if not row or row[0]!=raw or accepted!=('accepted',):raise ValueError('Accepted carrier required')
        evidence=json.loads(row[1]);group=evidence['processed']['group'];current=instances.optional_current(self.db,group)
        origin=instances.receive_origin(self.db,carrier,group)
        if not current or current['status']!='active' or current['instance']!=origin:raise ValueError('Question membership instance')
        checkpoint=self.db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
        if not checkpoint or checkpoint[0]!=group:raise ValueError('Question group')
        metadata=call(self.sender.binary,op='inspect-send',checkpoint=json.loads(checkpoint[1]),group=group,key=self.key)['metadata']
        policy=json.loads(self.db.execute('SELECT policy FROM sender_policy WHERE id=1').fetchone()[0])
        self.sender._authority(metadata,time,policy['trustPolicy'])
        context=decode_event(bytes.fromhex(metadata['context']))['value']
        if context['version']!='6' or context['conversation']!=reference['conversation'] or 'service-question' not in context['application']['operations']:raise ValueError('Service application agreement')
        principal='enp0:'+bytes.fromhex(metadata['senderIdentity'])[21:53].hex()
        if event['version']!='3' or event['operation']['kind']!='service-question' or principal not in event['audience']:raise ValueError('Service question')
        descriptor=event['operation']['serviceAction'];registration=self.registration()
        if not registration or not registration.get('enabled') or registration['principal']!=principal or registration['service']!=descriptor['service'] or registration['action']!=descriptor['action'] or registration['submit']!=descriptor['submit'] or registration['statusPrefix']!=descriptor['statusPrefix']:raise ValueError('Service registration unavailable')
        token=hashlib.sha256(encode_event(dict(event=hashlib.sha256(raw).hexdigest(),carrier=carrier,instance=origin,registration=registration['generation'],principal=principal))).hexdigest()
        return event,descriptor,registration,token

    def view(self,reference,carrier,*,time):
        event,descriptor,registration,token=self._source(reference,carrier,time)
        return dict(text=event['operation']['text'],options=event['operation']['options'],service=descriptor['service'],sourceToken=token)

    def activate(self,action_id,reference,carrier,option,source_token,*,time,status=False):
        if not isinstance(action_id,str) or not action_id.isalnum() or len(action_id)>128:raise ValueError('Local action identity')
        selection=encode_event(dict(reference=reference,carrier=carrier,option=option)).decode()
        self.db.execute('BEGIN IMMEDIATE')
        try:
            event,descriptor,registration,token=self._source(reference,carrier,time)
            if token!=source_token:raise ValueError('Changed service snapshot')
            if option not in [o['id'] for o in event['operation']['options']]:raise ValueError('Service option')
            old=self.db.execute('SELECT selection,raw,service FROM service_client_actions WHERE id=?',(action_id,)).fetchone()
            if old:
                if old[0]!=selection:raise ValueError('Local action conflict')
                raw,service=old[1:]
            else:
                if status:raise ValueError('No retained service request')
                raw=encode_event(dict(version='0',purpose='service-answer-submit',submission=uuid.uuid4().hex,action=descriptor['action'],question=reference,principal=registration['principal'],option=option,replaces=[]));service=descriptor['service']
                self.db.execute('INSERT INTO service_client_actions VALUES(?,?,?,?)',(action_id,selection,raw,service))
            self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
        # Local source transaction ends before transport. Retaining again repairs
        # a crash between the two journals without changing submission identity.
        submission=self.journal.retain(raw,service)
        _,descriptor,registration,token=self._source(reference,carrier,time)
        if token!=source_token:raise ValueError('Changed service snapshot')
        secret=self.credential(registration['credentialHandle'])
        if not secret:raise ValueError('Service credential unavailable')
        client=self.transport(descriptor)
        return dict(submission=submission,**client.request(submission,secret,status=status))
