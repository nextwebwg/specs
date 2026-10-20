"""Historical provider evidence through the fixed management TLS client; no MLS release."""
import base64
import hashlib
import uuid
from event_encoding import decode_event
from hosted_access import parse
from service_answer import identifier

EXPORT_MAX=2097152
KEYS={'version','purpose','service','grant','operation','request','receipt','replyDestination'}

class HostedReplyExporter:
    def __init__(self,management):
        self.management=management;self.sender=management.sender
        with self.sender.db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS hosted_exports(id TEXT PRIMARY KEY,create_operation TEXT,grant_id TEXT,reply_operation TEXT,digest TEXT,state TEXT)')
    def fetch(self,create_operation,reply_operation,token,*,crash=lambda stage:None):
        if not identifier(reply_operation):raise ValueError('reply operation')
        creation=parse(self.sender.load(create_operation),'hosted-grant-create')
        grant=creation['grant'];path='/v0/grants/'+grant+'/reply-exports/'+reply_operation
        status,body=self.management._exchange('GET',path,None,token,max_octets=EXPORT_MAX)
        if status!=200:return {'http':status,'evidence':None}
        value=decode_event(body,max_octets=EXPORT_MAX)['value']
        if set(value)!=KEYS or value['version']!='0' or value['purpose']!='hosted-reply-export' or value['service']!=self.sender.vault.service or value['grant']!=grant or value['operation']!=reply_operation or value['replyDestination']!=creation['replyDestination'] or not isinstance(value['request'],str):raise ValueError('export binding')
        encoded=value['request']
        try:raw=base64.b64decode(encoded+'='*((-len(encoded))%4),altchars=b'-_',validate=True)
        except ValueError:raise ValueError('export encoding')
        if base64.urlsafe_b64encode(raw).rstrip(b'=').decode()!=encoded:raise ValueError('export canonical encoding')
        reply=parse(raw,'hosted-holder-reply');digest=hashlib.sha256(raw).hexdigest()
        if reply['operation']!=reply_operation:raise ValueError('reply identity')
        expected=dict(version='0',purpose='hosted-holder-result',service=self.sender.vault.service,grant=grant,operation=reply_operation,requestDigest=digest,outcome='confirmed',reason='stored',attribution='grant-holder')
        if value['receipt']!=expected:raise ValueError('export receipt')
        identity=uuid.uuid4().hex
        with self.sender.db() as db:
            db.execute('BEGIN IMMEDIATE')
            previous=db.execute('SELECT id,digest,state FROM hosted_exports WHERE grant_id=? AND reply_operation=?',(grant,reply_operation)).fetchall()
            conflict=False
            for old_id,old_digest,old_state in previous:
                retained=decode_event(self.sender.vault.get(db,'export:'+old_id,'hosted-reply-export',grant),max_octets=EXPORT_MAX)['value']
                old_raw=base64.urlsafe_b64decode(retained['request']+'='*((-len(retained['request']))%4))
                if old_raw!=raw or old_digest!=digest or old_state!='observed':conflict=True
            if conflict:db.execute("UPDATE hosted_exports SET state='conflict' WHERE grant_id=? AND reply_operation=?",(grant,reply_operation))
            self.sender.vault.put(db,'export:'+identity,'hosted-reply-export',grant,body)
            db.execute('INSERT INTO hosted_exports VALUES(?,?,?,?,?,?)',(identity,create_operation,grant,reply_operation,digest,'conflict' if conflict else 'observed'))
            crash('before-commit');db.commit();crash('after-commit')
        return {'http':200,'evidence':identity,'state':'conflict' if conflict else 'observed'}
