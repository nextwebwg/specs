"""Render only an accepted exact event and one retained protected carrier."""
import hashlib,json
from event_encoding import decode_event
from rich_presentation import project

def render(receiver,reference,*,carrier):
    records=[r for r in receiver.journal.snapshot(reference['conversation']) if r['reference']==reference]
    if len(records)!=1 or records[0]['state']!='recorded':raise ValueError('Rich event unavailable')
    raw=records[0]['octets'][0];event=decode_event(raw)['value']
    if event['operation']['kind']!='rich-message':raise ValueError('Rich operation required')
    row=receiver.db.execute('SELECT application FROM mls_receives WHERE digest=?',(carrier,)).fetchone()
    accepted=receiver.db.execute('SELECT state FROM mls_application_acceptance WHERE digest=?',(hashlib.sha256(raw).hexdigest(),)).fetchone()
    if not row or row[0]!=raw or accepted!=('accepted',):raise ValueError('Accepted carrier required')
    declared={x['resource']+'.'+event['event']+'@resources.email-next.invalid':x['mediaType'] for x in event['operation']['embedded']}
    parts=[];diagnostics=[]
    for cid,data,role,hint in receiver.db.execute('SELECT r.cid,r.bytes,p.role,p.media_type FROM mls_received_resources r JOIN mls_received_resource_roles p ON p.digest=r.digest AND p.position=r.position WHERE r.digest=? ORDER BY r.position',(carrier,)):
        if role!='embedded':continue
        if cid in declared:
            if hint!=declared[cid]:diagnostics.append('embedded-media-projection-mismatch')
            parts.append(dict(contentId=cid,bytes=data,mediaType=declared[cid]))
    result=project(event['operation'],event['event'],parts=parts)
    result['diagnostics']+=diagnostics
    return result
