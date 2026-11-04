"""Current pairing successor/proof candidate, never identity installation.

The caller supplies an independently accepted operational parent, independently
approved exact binding and authorizer key resolved from its validated parent
binding. This does not validate that history, current roles/time, approval,
configuration transfer, a whole bundle1 or any journal/transport transition.
"""
import base64
import hashlib
import re
from correspondence_archive import exact, oid, uint
from event_encoding import decode_event
from identity_repair_candidate import canonical, _verify, STATE_DOMAIN


def check_successor(parent_raw, approved_binding, entry, *, authorizer,
                    authorizer_key, not_before, not_after):
    parent=decode_event(parent_raw)['value']
    binding=decode_event(approved_binding)['value']
    exact(entry,'payload signature approvals')
    if type(entry['payload']) is not str or len(entry['payload'])>1398104:raise ValueError('Pairing payload encoding/bound')
    raw=base64.b64decode(entry['payload'],validate=True)
    if base64.b64encode(raw).decode()!=entry['payload']:raise ValueError('Canonical pairing payload encoding')
    child=decode_event(raw)['value']
    exact(child,'version purpose kind principal record revision previous issuedAt bindings revoked signer')
    if parent.get('version') not in ('0','1') or parent.get('purpose')!='identity-state' or parent.get('kind')=='retire':
        raise ValueError('Operational accepted pairing predecessor required')
    if parent['version']=='1' and canonical(parent)!=parent_raw:raise ValueError('Canonical parent bytes required')
    if canonical(child)!=raw:raise ValueError('Canonical state1 child required')
    oid(child['record'])
    if child['record']==parent['record']:raise ValueError('Fresh state record required')
    if uint(parent['revision'])==18446744073709551615:raise ValueError('Revision exhausted')
    before,after=uint(not_before),uint(not_after)
    if not before<=uint(child['issuedAt'])<=after or uint(child['issuedAt'])<uint(parent['issuedAt']):
        raise ValueError('Original session and predecessor time bounds')
    parent_digest=hashlib.sha256(parent_raw).hexdigest()
    if binding.get('version')!='0' or binding.get('purpose')!='device-binding' or binding.get('principal')!=parent['principal'] or binding.get('authority')!={'kind':'state','digest':parent_digest}:
        raise ValueError('Exact approved binding parent/principal required')
    device=binding.get('device')
    if type(device) is not str or not re.fullmatch(r'end0:[0-9a-f]{64}',device) or int(device[5:],16)==0:
        raise ValueError('New device spelling')
    if device in parent['revoked'] or any(b['device']==device for b in parent['bindings']):
        raise ValueError('New unrevoked device required')
    if not any(b['device']==authorizer for b in parent['bindings']):raise ValueError('Authorizer absent from parent')
    expected=dict(parent,version='1',kind='update',record=child['record'],
                  revision=str(uint(parent['revision'])+1),previous=[parent_digest],
                  issuedAt=child['issuedAt'],signer=authorizer,
                  bindings=sorted(parent['bindings']+[dict(device=device,digest=hashlib.sha256(approved_binding).hexdigest())],key=lambda b:b['device']))
    if child!=expected or entry['approvals']!=[]:raise ValueError('Only the exact approved one-device update is permitted')
    _verify(authorizer_key,entry['signature'],STATE_DOMAIN,raw)
    return dict(status='pairing-successor-candidate-only',head=hashlib.sha256(raw).hexdigest(),payload=raw)
