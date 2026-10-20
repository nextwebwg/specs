"""Client-owned reaction intents; browser inputs never supply author or membership."""
import json
import uuid
from pathlib import Path

# Same pinned exact vocabulary used by reaction-operations.mjs; no normalization.
EMOJI=frozenset(json.loads((Path(__file__).parent/'unicode-17/fully-qualified.json').read_text()))

def active_events(journal,target,view):
    active={json.dumps(r,sort_keys=True) for r in view.get('active',[])}
    result=[]
    for row in journal.snapshot(target['conversation']):
        if row['state']!='recorded' or json.dumps(row['reference'],sort_keys=True) not in active:continue
        event=decode_event(row['octets'][0])['value']
        if event['operation']['kind']!='reaction' or event['operation']['target']!=target:raise ValueError('Reaction snapshot mismatch')
        result.append((row['reference'],event['operation']['emoji']))
    if len(result)!=len(active):raise ValueError('Reaction snapshot incomplete')
    return result

from event_encoding import decode_event
from journal_reaction_view import derive_reaction_view
from provider_mls import call


def act(client,action_id,target,source_token,*,emoji=None,withdraw=False,time):
    if not isinstance(action_id,str) or len(action_id)>128 or not action_id.isascii() or not action_id.isalnum():raise ValueError('Action ID')
    if type(withdraw)!=bool or (emoji is not None and (not isinstance(emoji,str) or emoji not in EMOJI)) or (not withdraw and emoji is None):raise ValueError('Reaction action')
    request=json.dumps(dict(kind='reaction-withdraw' if withdraw else 'reaction',target=target,emoji=emoji,sourceToken=source_token),sort_keys=True)
    db=client.db;db.execute('BEGIN IMMEDIATE')
    try:
        old=db.execute('SELECT request,event,source_token FROM client_actions WHERE id=?',(action_id,)).fetchone()
        if old:
            if old[0]!=request:raise ValueError('Action ID conflict')
            raw,token=old[1:]
        else:
            view=derive_reaction_view(client.sender.receiver.journal,target)
            if view['sourceToken']!=source_token:raise ValueError('Changed reaction snapshot')
            if view['state']!='evaluated':raise ValueError('Target unavailable')
            selected=[r for r in view['results'] if r['ref']==target]
            if len(selected)!=1 or selected[0]['state']!='valid':raise ValueError('Target unavailable')
            checkpoint=db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
            if not checkpoint:raise ValueError('No accepted group')
            metadata=call(client.sender.binary,op='inspect-send',checkpoint=json.loads(checkpoint[1]),group=checkpoint[0],key=client.key)['metadata']
            policy=json.loads(db.execute('SELECT policy FROM sender_policy WHERE id=1').fetchone()[0])
            client.sender._authority(metadata,time,policy['trustPolicy'])
            principal='enp0:'+bytes.fromhex(metadata['senderIdentity'])[21:53].hex()
            context=decode_event(bytes.fromhex(metadata['context']))['value']
            kind='reaction-withdraw' if withdraw else 'reaction'
            if context['version'] not in ('2','3','4','5') or context['conversation']!=target['conversation'] or kind not in context['application']['operations']:raise ValueError('Application context')
            from application_payload import selected_format
            selected_format(context,client.sender._application_agreement(metadata),configured_ordering=client.sender.receiver.configured_endpoint_ordering(metadata['group']))
            operation=dict(kind=kind,target=target)
            if withdraw:
                operation['reactions']=[r for r,e in active_events(client.sender.receiver.journal,target,view) if r['principal']==principal and (emoji is None or e==emoji)]
                if not operation['reactions']:raise ValueError('No own active reactions')
            else:operation['emoji']=emoji
            event=dict(version=context['application']['envelopeVersion'],purpose='contribution',event=uuid.uuid4().hex,conversation=target['conversation'],principal=principal,
                audience=sorted(set('enp0:'+bytes.fromhex(m['identity'])[21:53].hex() for m in metadata['members'])),disclosures=[],operation=operation)
            raw=json.dumps(event,separators=(',',':')).encode();token=source_token
            db.execute('INSERT INTO client_actions VALUES(?,?,?,?)',(action_id,request,raw,token))
        db.execute('COMMIT')
    except BaseException:
        if db.in_transaction:db.execute('ROLLBACK')
        raise
    return client.sender.prepare(action_id,raw,key=client.key,envelope_sender=client.address,recipients=client.recipients,time=time,source_token=token)
