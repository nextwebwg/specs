"""Exact private scope/candidate commitments; no implicit trusted caller hash."""
import hashlib,re
from ordering_certificates import encode
H=re.compile(r'[0-9a-f]{64}\Z')

def octets(value,*,empty=False):
    if not isinstance(value,str) or len(value)%2 or (not empty and not value) or not re.fullmatch('[0-9a-f]*',value):raise ValueError('canonical hex octets')
    return bytes.fromhex(value)
def uint(value):
    if not isinstance(value,str) or not re.fullmatch(r'0|[1-9][0-9]{0,19}',value) or int(value)>=2**64:raise ValueError('uint64')
    return int(value)
def commitment(domain,value):
    raw=encode(value);return hashlib.sha256(domain+b'\0'+len(raw).to_bytes(4,'big')+raw).hexdigest()
def scope_object(*,conversation,group,predecessor,previous_decision,ordering,slot):
    if not isinstance(conversation,str) or not re.fullmatch('[0-9a-f]{32}',conversation):raise ValueError('conversation')
    octets(group);octets(predecessor);uint(slot)
    if previous_decision!='genesis' and (not isinstance(previous_decision,str) or not H.fullmatch(previous_decision)):raise ValueError('previous decision')
    if set(ordering)!={'kind','generation','faultBound','witnesses'} or ordering['kind']!='endpoint-quorum-v0':raise ValueError('ordering')
    uint(ordering['generation']);f=uint(ordering['faultBound']);ws=ordering['witnesses']
    if not isinstance(ws,list) or len(ws)<3*f+1:raise ValueError('fault bound')
    seen=[]
    for w in ws:
        if not isinstance(w,dict) or set(w)!={'principal','device','signingKey','state','binding'}:raise ValueError('witness')
        if not re.fullmatch('enp0:[0-9a-f]{64}',w['principal']) or not re.fullmatch('end0:[0-9a-f]{64}',w['device']):raise ValueError('identity')
        if any(not H.fullmatch(w[k]) for k in ('signingKey','state','binding')):raise ValueError('witness commitment')
        seen.append(w['principal'])
    if seen!=sorted(set(seen)):raise ValueError('unique ordered principal')
    return dict(version='0',purpose='ordering-scope',conversation=conversation,group=group,predecessor=predecessor,previousDecision=previous_decision,ordering=ordering,slot=slot)
def scope_digest(value):
    if not isinstance(value,dict) or set(value)!={'version','purpose','conversation','group','predecessor','previousDecision','ordering','slot'} or value['version']!='0' or value['purpose']!='ordering-scope':raise ValueError('scope shape')
    rebuilt=scope_object(conversation=value['conversation'],group=value['group'],predecessor=value['predecessor'],previous_decision=value['previousDecision'],ordering=value['ordering'],slot=value['slot'])
    return commitment(b'email-next/ordering-scope/v0',rebuilt)
def decision_identity(scope,candidate):
    if not H.fullmatch(candidate):raise ValueError('candidate digest')
    return commitment(b'email-next/ordering-decision/v0',{'scope':scope_digest(scope),'candidate':candidate})
