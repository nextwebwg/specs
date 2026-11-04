"""Deterministic repair/proof experiment, NOT identity-state installation.

Parents are trusted local snapshots already independently validated to one pinned
identity. This component does not validate that history, a complete DAG frontier,
network authority, storage rollback, release or current-suite interoperability.
Only the first repair of historical v0 parents is exercised. No wire deployment
or general-purpose JCS implementation is supplied.
"""
import base64
from dataclasses import dataclass
import hashlib
import json
import struct

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from event_encoding import decode_event
from admission_windows import clock,uint,MAX

STATE_DOMAIN='email2/identity-state/v1'
APPROVAL_DOMAIN='email2/identity-repair-approval/v1'


def canonical(value):
    # All candidate schema members/values are restricted ASCII strings, arrays
    # and objects, with no numeric JSON values. For this subset sorted compact
    # JSON agrees with RFC8785; do not use this as a general JCS serializer.
    def check(v):
        if isinstance(v,str):
            if not v.isascii() or any(ord(c)<32 for c in v):raise ValueError('ASCII schema only')
        elif isinstance(v,list):
            for child in v:check(child)
        elif isinstance(v,dict):
            for k,child in v.items():check(k);check(child)
        else:raise ValueError('String/array/object schema only')
    check(value)
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('ascii')


def framed(domain,raw):return domain.encode('ascii')+b'\0'+struct.pack('>I',len(raw))+raw


def object_id(domain,scope):
    value=hashlib.sha256(domain.encode('ascii')+b'\0'+scope).digest()[:16].hex()
    return value if value!='0'*32 else '0'*31+'1'


@dataclass(frozen=True)
class Parent:
    raw:bytes
    bindings:dict  # digest -> previously validated original binding payload bytes

    @property
    def digest(self):return hashlib.sha256(self.raw).hexdigest()


def derive(parents,*,time):
    """Trusted-parent derivation only. Signature verification remains separate."""
    lo,hi=clock(time)
    if len(parents)<2 or len({p.digest for p in parents})!=len(parents):raise ValueError('Distinct parent frontier required')
    ordered=sorted(parents,key=lambda p:p.digest);heads=[p.digest for p in ordered]
    scope=struct.pack('>I',len(heads))+b''.join(bytes.fromhex(h) for h in heads)
    states=[decode_event(p.raw)['value'] for p in ordered]
    if any(s.get('version')!='0' or s.get('purpose')!='identity-state' for s in states):raise ValueError('Validated historical v0 parents only')
    principal=states[0]['principal']
    if any(s['principal']!=principal for s in states):raise ValueError('One pinned principal required')
    if max(uint(s['revision']) for s in states)==MAX:raise ValueError('Revision overflow')
    rosters=[]
    for parent,state in zip(ordered,states):
        roster={}
        for ref in state['bindings']:
            raw=parent.bindings.get(ref['digest'])
            if raw is None or hashlib.sha256(raw).hexdigest()!=ref['digest']:raise ValueError('Exact retained binding bytes required')
            binding=decode_event(raw)['value']
            if binding['principal']!=principal or binding['device']!=ref['device']:raise ValueError('Binding actor mismatch')
            roster[ref['device']]=(ref['digest'],binding)
        if len(roster)!=len(state['bindings']):raise ValueError('Unique devices required')
        rosters.append(roster)
    revoked=set().union(*(set(s['revoked']) for s in states))
    shared=set.intersection(*(set(r) for r in rosters))-revoked
    admins=[];keys={}
    for device in sorted(shared):
        values=[r[device][1] for r in rosters]
        if len({v['signingKey'] for v in values})==1 and all({'enroll','revoke'}<=set(v['roles']) for v in values):
            admins.append(device);keys[device]=values[0]['signingKey']
            if any(not uint(v['notBefore'])<=lo<=hi<=uint(v['notAfter']) for v in values):raise ValueError('Shared administrator not current on every branch')
    if not admins:raise ValueError('No shared surviving administration')
    primary=admins[0];result=[];fresh={};result_values={}
    devices=sorted(set().union(*(set(r) for r in rosters))-revoked)
    for device in devices:
        members=[r[device] for r in rosters if device in r]
        digests=sorted({digest for digest,_ in members});values=[v for _,v in members]
        if len(digests)==1:
            digest=digests[0];binding=values[0]
        else:
            roles=set.intersection(*(set(v['roles']) for v in values))
            before=max(uint(v['notBefore']) for v in values);after=min(uint(v['notAfter']) for v in values)
            if len({v['signingKey'] for v in values})!=1 or not roles or before>after:
                revoked.add(device);continue
            binding=dict(version='0',purpose='device-binding',record=object_id('email2/identity-repair-binding/v1',scope+device.encode('ascii')),principal=principal,device=device,signingKey=values[0]['signingKey'],roles=sorted(roles),notBefore=str(before),notAfter=str(after),authority=dict(kind='state',digest=heads[0]))
            raw=canonical(binding);digest=hashlib.sha256(raw).hexdigest();fresh[device]=raw
            if not before<=lo<=hi<=after:raise ValueError('Derived replacement binding not current')
        # A branch-only retained binding is a newly approved grant on the other
        # branch. Every repair authorizer must independently be able to grant it.
        for roster in rosters:
            prior=set(roster[device][1]['roles']) if device in roster else set()
            added=set(binding['roles'])-prior
            if any(not added<=set(roster[admin][1]['roles']) for admin in admins):raise ValueError('Repair cannot amplify administrative grant roles')
        result.append(dict(device=device,digest=digest));result_values[device]=binding
    if any(admin in revoked or admin not in result_values for admin in admins):raise ValueError('Repair cannot remove its shared authorizers')
    value=dict(version='1',purpose='identity-state',kind='repair',principal=principal,record=object_id('email2/identity-repair-record/v1',scope),revision=str(max(uint(s['revision']) for s in states)+1),previous=heads,issuedAt=str(max(uint(s['issuedAt']) for s in states)),bindings=result,revoked=sorted(revoked),signer=primary)
    payload=canonical(value)
    if len(payload)>1048576 or any(len(raw)>1048576 for raw in fresh.values()):raise ValueError('Candidate payload bound')
    return dict(status='repair-derivation-only',payload=payload,value=value,authorizers=admins,keys=keys,replacements=fresh,bindings=result_values)


def _verify(key,signature,domain,raw):
    if not isinstance(signature,str) or len(signature)!=128 or any(c not in '0123456789abcdef' for c in signature):raise ValueError('Exact signature encoding')
    try:Ed25519PublicKey.from_public_bytes(bytes.fromhex(key)).verify(bytes.fromhex(signature),framed(domain,raw))
    except (InvalidSignature,ValueError) as error:raise ValueError('Repair proof signature') from error


def verify_candidate(wrapper,parents,replacements,*,time):
    """Check deterministic bytes and all proofs; return no installation rights."""
    plan=derive(parents,time=time)
    if not isinstance(wrapper,dict) or set(wrapper)!={'payload','signature','approvals'}:raise ValueError('Exact proof wrapper required')
    if not isinstance(wrapper['payload'],str) or len(wrapper['payload'])>1398104:raise ValueError('Payload base64 bound')
    try:raw=base64.b64decode(wrapper['payload'],validate=True)
    except (ValueError,TypeError) as error:raise ValueError('Payload base64') from error
    if base64.b64encode(raw).decode()!=wrapper['payload'] or raw!=plan['payload']:raise ValueError('Exact deterministic candidate required')
    expected=plan['authorizers'][1:]
    proofs=wrapper['approvals']
    if not isinstance(proofs,list) or len(proofs)!=len(expected):raise ValueError('Every surviving administrator approval required')
    _verify(plan['keys'][plan['authorizers'][0]],wrapper['signature'],STATE_DOMAIN,raw)
    for device,entry in zip(expected,proofs):
        if not isinstance(entry,dict) or set(entry)!={'device','signature'} or entry['device']!=device:raise ValueError('Exact ordered approval set required')
        _verify(plan['keys'][device],entry['signature'],APPROVAL_DOMAIN,raw)
    if not isinstance(replacements,dict) or set(replacements)!=set(plan['replacements']):raise ValueError('Exact replacement proof set required')
    for device,payload in plan['replacements'].items():
        entry=replacements[device]
        if not isinstance(entry,dict) or set(entry)!={'authorization','possession'}:raise ValueError('Exact replacement proofs required')
        _verify(plan['keys'][plan['authorizers'][0]],entry['authorization'],'email-next/device-binding/v0',payload)
        _verify(plan['bindings'][device]['signingKey'],entry['possession'],'email-next/device-possession/v0',payload)
    return dict(status='repair-candidate-only',digest=hashlib.sha256(raw).hexdigest(),payload=raw)
