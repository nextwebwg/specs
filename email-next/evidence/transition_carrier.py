"""Configured endpoint comparison carrier. MIME selection is not authorization."""
import base64
import hashlib
import json
from provider_control import decode,exact
from passive_discovery import canonical_base64,uint64
from transition_mime import package,select
FIELDS=set('version purpose profile ordering group previousEpoch previousContext commit proposals'.split())

def parse(raw):
    v=decode(raw,max_bytes=4*1024*1024,max_depth=32);exact(v,FIELDS)
    if (v['version'],v['purpose'],v['profile'],v['ordering'])!=('0','mls-group-transition','mls-1-0001','configured-endpoint-v0') or v['proposals']!=[]:raise ValueError('Unsupported carrier')
    import re
    if not isinstance(v['previousContext'],str) or not re.fullmatch('[0-9a-f]{64}',v['previousContext']):raise ValueError('Context digest')
    uint64(v['previousEpoch']);group=canonical_base64(v['group']);commit=canonical_base64(v['commit'])
    if not group or not commit or len(commit)>1024*1024:raise ValueError('Carrier limits')
    return v,commit

def encode_transition(result):
    before=result['before']
    raw=json.dumps(dict(version='0',purpose='mls-group-transition',profile='mls-1-0001',ordering='configured-endpoint-v0',group=base64.b64encode(bytes.fromhex(before['group'])).decode(),previousEpoch=before['epoch'],previousContext=hashlib.sha256(bytes.fromhex(before['predecessor'])).hexdigest(),commit=base64.b64encode(bytes.fromhex(result['wire'])).decode(),proposals=[]),separators=(',',':'),allow_nan=False).encode()
    parse(raw)
    return raw

def check_binding(value,before):
    if (canonical_base64(value['group']).hex()!=before['group'] or value['previousEpoch']!=before['epoch'] or value['previousContext']!=hashlib.sha256(bytes.fromhex(before['predecessor'])).hexdigest()):raise ValueError('Carrier predecessor mismatch')

def receive_mime(coordinator,wire,**policy):
    raw=select(wire);value,commit=parse(raw)
    return coordinator.receive(commit,carrier=value,carrier_octets=raw,**policy)


def release_mime(coordinator,identifier,*,sender,recipient,allowed,time):
    """Prepare selected bytes after local release checks; not an atomic SMTP handoff."""
    released=coordinator.release(identifier,allowed=allowed,time=time)
    return package(encode_transition(released),sender=sender,recipient=recipient)
