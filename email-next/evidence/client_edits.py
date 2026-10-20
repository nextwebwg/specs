"""Trusted local edit composer; browser supplies choices, never author authority."""
import json,uuid
from event_encoding import decode_event,encode_event
from journal_edit_view import view
from provider_mls import call

def prepare(sender,action_id,root,predecessors,text,source_token,*,key,address,recipients,time,crash=lambda stage:None):
    sender.retention_preflight(time);db=sender.db
    if db.in_transaction:raise ValueError('Own edit transaction required')
    db.execute('CREATE TABLE IF NOT EXISTS client_edit_actions(id TEXT PRIMARY KEY,request TEXT NOT NULL,application BLOB NOT NULL)')
    request=json.dumps(dict(root=root,predecessors=predecessors,text=text,sourceToken=source_token),sort_keys=True)
    db.execute('BEGIN IMMEDIATE')
    try:
        old=db.execute('SELECT request,application FROM client_edit_actions WHERE id=?',(action_id,)).fetchone()
        if old:
            if old[0]!=request:raise ValueError('Edit action conflict')
            raw=old[1]
        else:
            current=view(sender.receiver,root)
            if current['state']!='evaluated' or current['sourceToken']!=source_token:raise ValueError('Changed edit snapshot')
            original=next((r for r in current['results'] if r['ref']==root and r['state']=='valid'),None)
            if original is None:raise ValueError('Root unavailable')
            checkpoint=db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
            metadata=call(sender.binary,op='inspect-send',checkpoint=json.loads(checkpoint[1]),group=checkpoint[0],key=key)['metadata']
            context=decode_event(bytes.fromhex(metadata['context']))['value'];principal='enp0:'+bytes.fromhex(metadata['senderIdentity'])[21:53].hex()
            if principal!=root['principal'] or context['version']!='6' or 'edit' not in context['application']['operations']:raise ValueError('Edit authority/profile')
            from application_payload import selected_format
            selected_format(context,sender._application_agreement(metadata),configured_ordering=sender.receiver.configured_endpoint_ordering(metadata['group']))
            event=dict(original['event'],event=uuid.uuid4().hex,version='3',audience=sorted(set('enp0:'+bytes.fromhex(m['identity'])[21:53].hex() for m in metadata['members'])),disclosures=[],operation=dict(kind='edit',root=root,predecessors=predecessors,text=text))
            # Presentation is a local compose choice, not reinterpretation of root text.
            event['presentation']=dict(event['presentation'],subject='Correction: '+event['presentation']['subject'],to=[p for p in event['audience'] if p!=principal],cc=[])
            raw=encode_event(event);db.execute('INSERT INTO client_edit_actions VALUES(?,?,?)',(action_id,request,raw))
        wire=sender._prepare(action_id,raw,key=key,envelope_sender=address,recipients=recipients,time=time,owned_transaction=False,crash=crash)
        db.execute('COMMIT');return wire
    except BaseException:
        if db.in_transaction:db.execute('ROLLBACK')
        raise
