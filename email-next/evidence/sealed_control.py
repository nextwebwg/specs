"""Dedicated HPKE control-container component; never owning-protocol admission.

Trusted local keys/binary/identity store are not supplied by received mail.
Opening a signed capsule returns candidate original bytes only: complete native
MLS, association, route, freshness, replay and atomic lifecycle gates remain.
"""
import base64
import json
from pathlib import Path
import subprocess
import struct

from event_encoding import decode_event,encode_event
from identity_bundle import decode_identity_bundle
from history_transfer import authority_snapshot,authorize,unpack as unpack_history,frame as history_frame
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
from passive_discovery import hexadecimal,uint64,canonical_base64
from provider_control import exact,participant,verify_signature

MAGIC=b'EML2CTL0'
INNER=b'EML2CIN0'
DOMAIN=b'email2/sealed-control-intent/v0\0'
MAX=8*1024*1024
BODY_MAX=4*1024*1024
IDENTITY_MAX=1024*1024
KINDS={'initial-invitation':'send','established-invitation':'send','stream-control':'send','stream-recipient-update':'receive','quorum-exchange':'receive','quorum-control':'receive',
       'history-request':'receive','history-grant':'send','history-receipt':'receive',
       'history-source-cancel':'send','history-target-cancel':'receive','mailbox-setup-response':'receive'}


def key_descriptor(value, *, maximum_lifetime=None):
    exact(value,{'id','publicKey','notBefore','notAfter','receiveUntil'})
    if not hexadecimal(value['id'],32) or value['id']=='0'*32 or not hexadecimal(value['publicKey'],64):raise ValueError('Control key encoding')
    public=bytes.fromhex(value['publicKey'])
    if int.from_bytes(public,'little')>=2**255-19 or int.from_bytes(public,'little') in (0,1):raise ValueError('Canonical nontrivial X25519 public key required')
    lo,hi,receive=(uint64(value[k]) for k in ('notBefore','notAfter','receiveUntil'))
    if not lo<=hi<=receive:raise ValueError('Control key windows')
    if maximum_lifetime is not None and (uint64(maximum_lifetime)==0 or hi-lo>uint64(maximum_lifetime)):raise ValueError('Control key lifetime policy')
    return value


def native(binary,**request):
    result=subprocess.run([str(Path(binary).resolve())],input=json.dumps(request).encode(),capture_output=True,timeout=15,check=True)
    if len(result.stdout)>2*(MAX+76)+1024:raise ValueError('Native output bound')
    value=json.loads(result.stdout)
    if value.get('status')=='rejected':raise ValueError('HPKE control rejected: '+value['reason'])
    return value


def history_binding(intent, body):
    """Bind a signed history actor/peer before seal; no journal or disclosure approval."""
    kind=intent['kind']
    if not kind.startswith('history-'):return
    cancel=kind in ('history-source-cancel','history-target-cancel')
    record_kind='cancel' if cancel else kind.removeprefix('history-')
    raw,signature,value,_=unpack_history(body,record_kind)
    actor_side=('source' if kind=='history-source-cancel' else 'target') if cancel else ('source' if record_kind=='grant' else 'target')
    if cancel and value['by']!=actor_side:raise ValueError('History cancellation kind/actor')
    actor=value[actor_side];peer=value['target' if actor_side=='source' else 'source']
    if intent['sender']!={k:actor[k] for k in ('principal','device','state','binding')} or intent['recipient']!={k:peer[k] for k in ('principal','device')}:
        raise ValueError('History actor/recipient binding')
    if not uint64(value['notBefore'])<=uint64(intent['notBefore'])<=uint64(intent['notAfter'])<=uint64(value['notAfter']):raise ValueError('History control interval')
    try:Ed25519PublicKey.from_public_bytes(bytes.fromhex(actor['key'])).verify(signature,history_frame(record_kind,raw))
    except (InvalidSignature,ValueError) as error:raise ValueError('History original signature') from error
    return actor['key']


def parse_intent(raw):
    value=decode_event(raw,max_octets=MAX)['value']
    exact(value,set('version purpose record sender recipient key kind body notBefore notAfter'.split()))
    if (value['version'],value['purpose'])!=('0','sealed-control-intent') or not isinstance(value['kind'],str) or value['kind'] not in KINDS:raise ValueError('Exact sealed control purpose/kind')
    for key in ('record','key'):
        if not hexadecimal(value[key],32) or value[key]=='0'*32:raise ValueError('Control ObjectId')
    participant(value['recipient']);exact(value['sender'],{'principal','device','state','binding'})
    participant({k:value['sender'][k] for k in ('principal','device')})
    if any(not hexadecimal(value['sender'][k],64) for k in ('state','binding')):raise ValueError('Sender evidence references')
    if uint64(value['notBefore'])>uint64(value['notAfter']):raise ValueError('Intent interval')
    body=canonical_base64(value['body'])
    if not body or len(body)>BODY_MAX:raise ValueError('Original control body bound')
    history_binding(value,body)
    return value,body


def frame(raw,signature,identity):
    parse_intent(raw)
    if not isinstance(signature,bytes) or len(signature)!=64:raise ValueError('Signature bytes')
    if not isinstance(identity,bytes) or len(identity)>IDENTITY_MAX:raise ValueError('Identity bundle bound')
    bundle=decode_identity_bundle(identity)
    intent,body=parse_intent(raw);history_key=history_binding(intent,body)
    if history_key is not None:
        actor=intent['sender']
        binding=next((b for b in bundle['bindings'] if b['digest']==actor['binding']),None)
        if bundle['principal']!=actor['principal'] or binding is None or binding['value']['device']!=actor['device'] or binding['value']['signingKey']!=history_key:
            raise ValueError('History original/outer signing key')
    result=INNER+struct.pack('>I',len(raw))+raw+signature+struct.pack('>I',len(identity))+identity
    if len(result)>MAX:raise ValueError('Control plaintext bound')
    return result


def unframe(plain):
    if not isinstance(plain,bytes) or len(plain)>MAX or len(plain)<80 or plain[:8]!=INNER:raise ValueError('Control plaintext frame')
    n=struct.unpack('>I',plain[8:12])[0]
    if n>MAX or 12+n+68>len(plain):raise ValueError('Control payload length')
    raw=plain[12:12+n];signature=plain[12+n:76+n];length=struct.unpack('>I',plain[76+n:80+n])[0]
    if length>IDENTITY_MAX or len(plain)!=80+n+length:raise ValueError('Control identity/trailing bytes')
    return raw,signature,plain[80+n:]


def seal(binary,descriptor,plain,*,time,recipient):
    key_descriptor(descriptor);participant(recipient);raw,_,_=unframe(plain);intent,_=parse_intent(raw)
    if intent['recipient']!=recipient:raise ValueError('Independent recipient selection mismatch')
    lo,hi=uint64(time['earliest']),uint64(time['latest'])
    if not uint64(descriptor['notBefore'])<=uint64(intent['notBefore'])<=lo<=hi<=uint64(intent['notAfter'])<=uint64(descriptor['notAfter']) or intent['key']!=descriptor['id']:raise ValueError('Creation/recipient key binding')
    return bytes.fromhex(native(binary,op='seal',id=descriptor['id'],publicKey=descriptor['publicKey'],plaintext=plain.hex())['ciphertext'])


def open_candidate(binary,wire,*,descriptor,private_key,recipient,identity,time,expected_kind):
    key_descriptor(descriptor);participant(recipient)
    lo,hi=uint64(time['earliest']),uint64(time['latest'])
    if not lo<=hi<=uint64(descriptor['receiveUntil']):raise ValueError('Receiving window')
    if not isinstance(wire,bytes) or len(wire)>MAX+76:raise ValueError('Ciphertext bound')
    plain=bytes.fromhex(native(binary,op='open',id=descriptor['id'],publicKey=descriptor['publicKey'],privateKey=private_key,ciphertext=wire.hex())['plaintext'])
    raw,sig,bundle_bytes=unframe(plain);value,body=parse_intent(raw)
    if value['recipient']!=recipient or value['key']!=descriptor['id'] or value['kind']!=expected_kind:raise ValueError('Exact recipient/kind selection')
    if not uint64(descriptor['notBefore'])<=uint64(value['notBefore'])<=uint64(value['notAfter'])<=uint64(descriptor['notAfter']) or lo<uint64(value['notBefore']):raise ValueError('Original creation interval')
    bundle=decode_identity_bundle(bundle_bytes);actor=value['sender']
    binding=next((b for b in bundle['bindings'] if b['digest']==actor['binding']),None)
    if bundle['principal']!=actor['principal'] or binding is None or binding['value']['device']!=actor['device']:raise ValueError('Sender bundle')
    key=binding['value']['signingKey'];verify_signature(raw,sig.hex(),key,DOMAIN)
    history_key=history_binding(value,body)
    if history_key is not None and history_key!=key:raise ValueError('History original/outer signing key')
    with authority_snapshot(identity):
        try:checked=authorize(identity,dict(actor,key=key),KINDS[value['kind']],time,'allow-unverified',allow_binding_renewal=True)
        except ValueError as error:raise ValueError('Current accepted sender required') from error
    if not uint64(binding['value']['notBefore'])<=uint64(value['notBefore'])<=uint64(value['notAfter'])<=uint64(binding['value']['notAfter']):raise ValueError('Original sender authority interval')
    return dict(status='sealed-control-candidate-only',intent=value,original_body=body,original_intent=raw,signature=sig,authority=checked)
