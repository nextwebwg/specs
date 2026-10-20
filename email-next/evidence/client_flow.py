"""Local configured client actions. The browser never supplies trust or authorship."""
import json
import uuid
from event_encoding import decode_event
from journal_button_view import derive_button_view
from provider_mls import call

class ClientFlow:
    def __init__(self,sender,*,key,envelope_sender,recipients):
        self.sender=sender;self.db=sender.db;self.key=key;self.address=envelope_sender;self.recipients=list(recipients)
        self.db.execute('CREATE TABLE IF NOT EXISTS client_actions(id TEXT PRIMARY KEY,request TEXT NOT NULL,event BLOB NOT NULL,source_token TEXT NOT NULL)')

    def answer(self,action_id,question,option,source_token,*,time):
        """A stable action ID is the local idempotency key, not an event authority."""
        if not isinstance(action_id,str) or len(action_id)>128 or not action_id.isascii() or not action_id.isalnum():raise ValueError('Action ID')
        request=json.dumps(dict(question=question,option=option,sourceToken=source_token),sort_keys=True)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT request,event,source_token FROM client_actions WHERE id=?',(action_id,)).fetchone()
            if old:
                if old[0]!=request:raise ValueError('Action ID conflict')
                raw,token=old[1:]
            else:
                view=derive_button_view(self.sender.receiver.journal,question)
                if view['sourceToken']!=source_token:raise ValueError('Changed question snapshot')
                if view['state']!='evaluated':raise ValueError('Question unavailable')
                rows=[r for r in self.sender.receiver.journal.snapshot(question['conversation']) if r['reference']==question]
                if len(rows)!=1 or rows[0]['state']!='recorded':raise ValueError('Question unavailable')
                target=decode_event(rows[0]['octets'][0])['value']
                if target['operation']['kind']!='question' or option not in [o['id'] for o in target['operation']['options']]:raise ValueError('Question option')
                checkpoint=self.db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
                metadata=call(self.sender.binary,op='inspect-send',checkpoint=json.loads(checkpoint[1]),group=checkpoint[0],key=self.key)['metadata']
                policy=json.loads(self.db.execute('SELECT policy FROM sender_policy WHERE id=1').fetchone()[0])
                self.sender._authority(metadata,time,policy['trustPolicy'])
                principal='enp0:'+bytes.fromhex(metadata['senderIdentity'])[21:53].hex()
                context=decode_event(bytes.fromhex(metadata['context']))['value']
                if context['version'] not in ('2','3','4','5') or context['conversation']!=question['conversation'] or 'answer' not in context['application']['operations']:raise ValueError('Application context')
                from application_payload import selected_format
                selected_format(context,self.sender._application_agreement(metadata),configured_ordering=self.sender.receiver.configured_endpoint_ordering(metadata['group']))
                event=dict(version=context['application']['envelopeVersion'],purpose='contribution',event=uuid.uuid4().hex,conversation=question['conversation'],principal=principal,
                    audience=sorted(set('enp0:'+bytes.fromhex(m['identity'])[21:53].hex() for m in metadata['members'])),disclosures=[],
                    operation=dict(kind='answer',question=question,option=option,replaces=[r for r in view['heads'] if r['principal']==principal]))
                raw=json.dumps(event,separators=(',',':')).encode();token=source_token
                self.db.execute('INSERT INTO client_actions VALUES(?,?,?,?)',(action_id,request,raw,token))
            self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
        # The retained action survives a crash before preparation. Preparation checks
        # the snapshot again inside its own transaction; no network is used here.
        return self.sender.prepare(action_id,raw,key=self.key,envelope_sender=self.address,recipients=self.recipients,time=time,source_token=token)

    def react(self,action_id,target,emoji,source_token,*,time):
        from client_reactions import act
        return act(self,action_id,target,source_token,emoji=emoji,time=time)

    def withdraw_reactions(self,action_id,target,source_token,*,time,emoji=None):
        from client_reactions import act
        return act(self,action_id,target,source_token,withdraw=True,emoji=emoji,time=time)
