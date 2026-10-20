"""Explicit configured readable-copy plan and fixed local submission adapter."""
import base64
import hashlib
import json
import uuid
from email.message import EmailMessage
from email import policy
from event_encoding import decode_event
from passive_discovery import mailbox_syntax
from sender_release import canonical

KIND='configured-plaintext-submit-v1'

class PlaintextRelease:
    def __init__(self,sender):
        self.sender=sender;self.db=sender.db
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS plaintext_target_representations(target TEXT NOT NULL,recipient TEXT NOT NULL,message_id TEXT NOT NULL,wire BLOB NOT NULL,digest TEXT NOT NULL,provenance TEXT NOT NULL,PRIMARY KEY(target,recipient,digest));
          CREATE TABLE IF NOT EXISTS plaintext_rich_resources(digest TEXT PRIMARY KEY,resources TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS plaintext_exposure(digest TEXT PRIMARY KEY,review TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS plaintext_plans(digest TEXT PRIMARY KEY,application BLOB NOT NULL,recipients TEXT NOT NULL,policy_revision INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS plaintext_prepared(id TEXT PRIMARY KEY,wire BLOB NOT NULL,metadata TEXT NOT NULL,dependencies TEXT NOT NULL,policy_revision INTEGER NOT NULL,envelope TEXT NOT NULL,associations TEXT NOT NULL,protected_delivery TEXT NOT NULL,digest TEXT NOT NULL);
        ''')
    def import_target_representation(self,target,recipient,wire,*,provenance,max_wire_bytes=1048576):
        """Trusted local import, never called with a browser's asserted mapping.

        The importer attests that these exact bytes represent this target for this
        recipient. MIME alone cannot authenticate that association. Provenance
        identifies the local evidence source; imports do not grant event authority.
        """
        from email.parser import BytesParser
        from reaction_mime import _message_id, _reference
        if not _reference(target):raise ValueError('Exact target reference required')
        mailbox_syntax(recipient)
        if type(max_wire_bytes) is not int or max_wire_bytes<1 or not isinstance(wire,bytes) or not wire or len(wire)>max_wire_bytes:raise ValueError('Target representation bound')
        if not isinstance(provenance,dict) or set(provenance)!={'kind','source'} or provenance['kind']!='trusted-local-import' or not isinstance(provenance['source'],str) or not provenance['source'].strip():raise ValueError('Trusted import provenance required')
        parsed=BytesParser(policy=policy.default).parsebytes(wire)
        ids=parsed.get_all('Message-ID',[])
        if parsed.defects or len(ids)!=1 or getattr(ids[0],'defects',()):raise ValueError('One valid target Message-ID required')
        identifier=_message_id(str(ids[0]));digest=hashlib.sha256(wire).hexdigest()
        self.db.execute('BEGIN IMMEDIATE')
        try:
            prior=self.db.execute('SELECT wire,message_id,provenance FROM plaintext_target_representations WHERE target=? AND recipient=? AND digest=?',(canonical(target),recipient,digest)).fetchone()
            if prior and prior!=(wire,identifier,canonical(provenance)):raise ValueError('Immutable target import conflict')
            if not prior:self.db.execute('INSERT INTO plaintext_target_representations VALUES(?,?,?,?,?,?)',(canonical(target),recipient,identifier,wire,digest,canonical(provenance)))
            self.db.execute('COMMIT');return digest
        except BaseException:
            self.db.execute('ROLLBACK');raise

    def _mapping_evidence(self,target,recipients,mapping):
        result=[]
        for recipient in recipients:
            rows=self.db.execute('SELECT message_id,digest,provenance FROM plaintext_target_representations WHERE target=? AND recipient=? ORDER BY digest',(canonical(target),recipient)).fetchall()
            if len(rows)!=1 or rows[0][0]!=mapping[recipient]:raise ValueError('Missing or ambiguous target representation evidence')
            result.append(dict(recipient=recipient,representations=[dict(messageId=r[0],digest=r[1],provenance=json.loads(r[2])) for r in rows]))
        return result

    def preview(self,application,recipients,*,target_mapping=None,resources=None):
        """Trusted local disclosure review, not a browser authorization object.

        Covers complete text/HTML and disclosed transport reference. No structured
        event alternative or private recipient list is transmitted in the body.
        """
        from plaintext_projection import project
        from reaction_mime import _message_id
        event=decode_event(application)['value'];kind=event['operation']['kind']
        if kind not in ('message','question','answer','reaction','reaction-withdraw','rich-message','edit'):raise ValueError('Unsupported ordinary copy')
        if not isinstance(recipients,list) or not recipients or len(set(recipients))!=len(recipients):raise ValueError('Explicit fallback recipients')
        for address in recipients:mailbox_syntax(address)
        mapping=None;mapping_evidence=[]
        if target_mapping is not None:
            if kind!='reaction' or not isinstance(target_mapping,dict) or set(target_mapping)!=set(recipients):raise ValueError('Recipient-specific target mapping required')
            values=[_message_id(target_mapping[r]) for r in recipients]
            mapping_evidence=self._mapping_evidence(event['operation']['target'],recipients,target_mapping)
            mapping=values[0] if len(set(values))==1 else None
        if kind=='rich-message':
            from plaintext_rich import preview as rich_preview
            if resources is None:
                retained=self.db.execute('SELECT resources FROM plaintext_rich_resources WHERE digest=?',(hashlib.sha256(application).hexdigest(),)).fetchone()
                if not retained:raise ValueError('Complete rich resource disclosure required')
                resources={k:base64.b64decode(v,validate=True) for k,v in json.loads(retained[0]).items()}
            return dict(version='readable-copy-v1',recipients=recipients,subject=event['presentation']['subject'] if event['version']=='3' else 'Message',text=event['operation']['text'],html=event['operation']['html'],dependencies=[],targetMessageId=None,targetMapping=None,mappingEvidence=[],headerPolicy='local-author-undisclosed-recipients-fresh-message-id',**rich_preview(application,resources))
        projected=project(self.sender,application)
        return dict(version='readable-copy-v1',format='plain-html',recipients=recipients,
            subject=event['presentation']['subject'] if event['version']=='3' else {'answer':'Answer','reaction':'Reaction','reaction-withdraw':'Reaction withdrawal','question':'Question','message':'Message','edit':'Correction'}[kind],
            text=projected['projection']['text'],html=projected['projection']['html'],
            dependencies=projected['dependencies'],targetMessageId=mapping,
            targetMapping=target_mapping,mappingEvidence=mapping_evidence,headerPolicy='local-author-undisclosed-recipients-fresh-message-id')

    def authorize(self,application,recipients,*,exposure=None,resources=None):
        """Trusted local sender decision, not inferred from a received descriptor."""
        from hosted_disclosure import validate_local_shape
        event=validate_local_shape(application)
        if event.get('version') not in ('1','2','3') or {'kind':'plaintext-email'} not in event.get('disclosures',[]):raise ValueError('Plaintext disclosure required')
        kind=event.get('operation',{}).get('kind')
        if kind not in ('message','question','answer','reaction','reaction-withdraw','rich-message','edit'):raise ValueError('Unsupported ordinary copy')
        if not isinstance(recipients,list) or not recipients or len(set(recipients))!=len(recipients):raise ValueError('Explicit fallback recipients')
        for address in recipients:mailbox_syntax(address)
        digest=hashlib.sha256(application).hexdigest();encoded=canonical(recipients)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            review=self.preview(application,recipients,target_mapping=exposure.get('targetMapping') if isinstance(exposure,dict) else None,resources=resources)
            if exposure is not None and exposure!=review:raise ValueError('Changed disclosure exposure')
            if kind in ('answer','reaction','reaction-withdraw','rich-message','edit') and exposure is None:raise ValueError('Exact copied context/reference authorization required')
            revision=self.db.execute('SELECT revision FROM sender_policy WHERE id=1').fetchone()
            if not revision:raise ValueError('Configure policy first')
            old=self.db.execute('SELECT application,recipients,policy_revision FROM plaintext_plans WHERE digest=?',(digest,)).fetchone()
            if old and old!=(application,encoded,revision[0]):raise ValueError('Immutable plaintext plan conflict')
            if not old:self.db.execute('INSERT INTO plaintext_plans VALUES(?,?,?,?)',(digest,application,encoded,revision[0]))
            prior=self.db.execute('SELECT review FROM plaintext_exposure WHERE digest=?',(digest,)).fetchone()
            if prior and prior[0]!=canonical(review):raise ValueError('Immutable exposure conflict')
            if not prior:self.db.execute('INSERT INTO plaintext_exposure VALUES(?,?)',(digest,canonical(review)))
            if kind=='rich-message':
                if resources is None:raise ValueError('Exact resource bytes required')
                encoded_resources=canonical({k:base64.b64encode(v).decode() for k,v in resources.items()})
                old_resources=self.db.execute('SELECT resources FROM plaintext_rich_resources WHERE digest=?',(digest,)).fetchone()
                if old_resources and old_resources[0]!=encoded_resources:raise ValueError('Immutable rich resource conflict')
                if not old_resources:self.db.execute('INSERT INTO plaintext_rich_resources VALUES(?,?)',(digest,encoded_resources))
            self.db.execute('COMMIT');return digest
        except BaseException:
            self.db.execute('ROLLBACK');raise
    def prepare(self,delivery,protected_delivery,*,recipients=None):
        if not isinstance(delivery,str) or not delivery or not delivery.isascii() or not delivery.isalnum():raise ValueError('Delivery ID')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            from proposal_observation import check_send
            protected_metadata=self.db.execute('SELECT metadata FROM sender_prepared WHERE id=?',(protected_delivery,)).fetchone()
            if protected_metadata:
                from provider_mls import call
                checkpoint=self.db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
                if checkpoint:
                    current=call(self.sender.binary,op='inspect-send',checkpoint=json.loads(checkpoint[1]),group=checkpoint[0],key=json.loads(protected_metadata[0])['senderKey'])['metadata']
                    check_send(self.db,current)
            prior=self.db.execute('SELECT protected_delivery,wire,envelope FROM plaintext_prepared WHERE id=?',(delivery,)).fetchone()
            if prior:
                if prior[0]!=protected_delivery or (recipients is not None and json.loads(prior[2])['recipients']!=recipients):raise ValueError('Delivery ID conflict')
                self.db.execute('COMMIT');return prior[1]
            row=self.db.execute('SELECT application,metadata,dependencies,policy_revision,envelope FROM sender_prepared WHERE id=?',(protected_delivery,)).fetchone()
            if not row:raise ValueError('Protected contribution not prepared')
            digest=hashlib.sha256(row[0]).hexdigest()
            plan=self.db.execute('SELECT application,recipients,policy_revision FROM plaintext_plans WHERE digest=?',(digest,)).fetchone()
            if not plan or plan[0]!=row[0] or plan[2]!=row[3]:raise ValueError('Plaintext plan mismatch')
            stored=self.db.execute('SELECT review FROM plaintext_exposure WHERE digest=?',(digest,)).fetchone()
            if not stored:raise ValueError('Retained disclosure exposure required')
            review=json.loads(stored[0])
            if self.preview(row[0],json.loads(plan[1]),target_mapping=review['targetMapping'])!=review:raise ValueError('Changed disclosure dependencies')
            selected=json.loads(plan[1]) if recipients is None else recipients
            if not isinstance(selected,list) or not selected or len(set(selected))!=len(selected) or not all(r in json.loads(plan[1]) for r in selected):raise ValueError('Unapproved route recipients')
            target=review['targetMessageId']
            if review['targetMapping'] is not None:
                targets={review['targetMapping'][r] for r in selected}
                target=next(iter(targets)) if len(targets)==1 else None
            message=EmailMessage(policy=policy.SMTP);message['From']=json.loads(row[4])['sender']
            message['To']='undisclosed-recipients:;';message['Subject']=review['subject']
            message['Message-ID']='<'+uuid.uuid4().hex+'@plaintext.example.invalid>'
            if target is not None:
                message.make_mixed();message['In-Reply-To']=target
                reaction=EmailMessage(policy=policy.SMTP)
                emoji=decode_event(row[0])['value']['operation']['emoji']
                reaction.set_content((emoji+'\r\n').encode(),maintype='text',subtype='plain',cte='base64')
                reaction.set_param('charset','utf-8');reaction['Content-Disposition']='reaction';message.attach(reaction)
                alternatives=EmailMessage(policy=policy.SMTP)
            else:alternatives=message
            if review['format']=='rich-copy-v1':
                from email.parser import BytesParser
                entity=BytesParser(policy=policy.SMTP).parsebytes(base64.b64decode(review['entityBase64'],validate=True))
                for name,value in message.raw_items():entity[name]=value
                message=entity;alternatives=message
            else:alternatives.set_content(review['text'],charset='utf-8');alternatives.add_alternative(review['html'],subtype='html',charset='utf-8')
            if alternatives is not message:message.attach(alternatives)
            wire=message.as_bytes();envelope=canonical(dict(sender=json.loads(row[4])['sender'],recipients=selected))
            self.db.execute('INSERT INTO plaintext_prepared VALUES(?,?,?,?,?,?,?,?,?)',(delivery,wire,row[1],row[2],row[3],envelope,canonical({'mode':'configured-roster'}),protected_delivery,digest))
            self.db.execute('COMMIT');return wire
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def validate_locked(self,delivery,time):
        if not self.db.in_transaction:raise ValueError('Transaction required')
        row=self.db.execute('SELECT protected_delivery,digest,policy_revision,envelope FROM plaintext_prepared WHERE id=?',(delivery,)).fetchone()
        if not row:raise ValueError('Not prepared')
        protected=self.db.execute('SELECT application FROM sender_prepared WHERE id=?',(row[0],)).fetchone()
        plan=self.db.execute('SELECT application,recipients,policy_revision FROM plaintext_plans WHERE digest=?',(row[1],)).fetchone()
        if not plan or not protected or protected[0]!=plan[0] or hashlib.sha256(plan[0]).hexdigest()!=row[1] or plan[2]!=row[2] or not json.loads(row[3])['recipients'] or not all(r in json.loads(plan[1]) for r in json.loads(row[3])['recipients']):raise ValueError('Changed plaintext plan')
        stored=self.db.execute('SELECT review FROM plaintext_exposure WHERE digest=?',(row[1],)).fetchone()
        if not stored:raise ValueError('Retained disclosure exposure required')
        review=json.loads(stored[0])
        if self.preview(plan[0],json.loads(plan[1]),target_mapping=review['targetMapping'])!=review:raise ValueError('Changed disclosure dependencies')
        return {'contract':KIND,'digest':row[1],'protectedDelivery':row[0]}
