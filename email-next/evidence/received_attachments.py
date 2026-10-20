"""Accepted event attachment presentation and deliberate byte retrieval.

No filesystem writes, automatic opening, nested MIME activation or network fetch.
"""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
from event_encoding import decode_event
from protected_attachment_carrier import compare_attachment_projections

def validate_resources(receiver,digest,raw,representation):
    rows=receiver.db.execute('SELECT r.cid,r.bytes,p.role FROM mls_received_resources r LEFT JOIN mls_received_resource_roles p ON p.digest=r.digest AND p.position=r.position WHERE r.digest=? ORDER BY r.position',(digest,)).fetchall()
    parts=[dict(contentId=cid,base64=base64.b64encode(data).decode()) for cid,data,role in rows]
    event=decode_event(raw)['value']
    request=dict(event=event,parts=parts,limits=dict(maxBytes=1048576,maxChunks=1,maxInputBytes=1048576))
    check=subprocess.run(['node',str(Path(__file__).with_name('check-received-attachment.mjs'))],input=json.dumps(request),text=True,capture_output=True,check=True,timeout=10)
    checked=json.loads(check.stdout)
    if checked['state']!='validated-unverified':raise ValueError('Attachment schema')
    # Projections follow physical independent-part order, including unexpected CIDs.
    # Filtering by claimed ID first would shift metadata onto another resource.
    attachments=[dict(contentId=cid,bytes=data) for cid,data,role in rows if role=='attachment']
    for resource in checked['resources']:
        cid=resource['id']+'.'+event['event']+'@resources.email-next.invalid'
        if resource['state']=='complete' and not any(p['contentId']==cid for p in attachments):
            resource['state']='wrong-role'
    selected=dict(resources=attachments,projections=representation['projections'])
    return dict(inventory=checked['inventory'],resources=checked['resources'],metadata=compare_attachment_projections(selected,event))

def view(receiver,reference):
    records=[r for r in receiver.journal.snapshot(reference['conversation']) if r['reference']==reference]
    if len(records)!=1 or records[0]['state']!='recorded':return dict(state='unavailable',attachments=[])
    raw=records[0]['octets'][0];event=decode_event(raw)['value']
    if event['operation']['kind'] not in ('attachment-message','rich-message'):return dict(state='unavailable',attachments=[])
    accepted=receiver.db.execute('SELECT state FROM mls_application_acceptance WHERE digest=?',(hashlib.sha256(raw).hexdigest(),)).fetchone()
    if accepted!=('accepted',):return dict(state='unavailable',attachments=[])
    carriers=receiver.db.execute('SELECT p.digest,p.representation FROM mls_received_payloads p JOIN mls_receives r ON r.digest=p.digest WHERE r.application=?',(raw,)).fetchall()
    result=[]
    for description in event['operation']['attachments']:
        found=[];diagnostics=[]
        for digest,encoded in carriers:
            evidence=json.loads(encoded).get('attachments',{})
            states=[r for r in evidence.get('resources',[]) if r['id']==description['resource']]
            diagnostics.append(dict(carrier=digest,resources=states,metadata=evidence.get('metadata',[])))
            if states and states[0]['state']=='complete':found.append(digest)
        result.append(dict(description=description,state='available' if found else 'unavailable',carriers=found,diagnostics=diagnostics))
    return dict(state='accepted',attachments=result)

def read(receiver,reference,resource,*,carrier):
    """Explicit local retrieval under one accepted representation's integrity result."""
    selected=[a for a in view(receiver,reference)['attachments'] if a['description']['resource']==resource and carrier in a['carriers']]
    if len(selected)!=1:raise ValueError('Attachment unavailable')
    cid=resource+'.'+reference['event']+'@resources.email-next.invalid'
    rows=receiver.db.execute('SELECT bytes FROM mls_received_resources WHERE digest=? AND cid=?',(carrier,cid)).fetchall()
    if len(rows)!=1:raise ValueError('Ambiguous attachment')
    return rows[0][0]
