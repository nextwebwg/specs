"""Internal MLS/genesis integration fixture; no network identity discovery."""
import base64
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
from event_encoding import decode_event, encode_event
from identity_store import IdentityStore


def prepare(credential, key, now):
    if not re.fullmatch('[0-9a-f]{170}', credential) or not re.fullmatch('[0-9a-f]{64}', key):
        raise ValueError('Fixture encoding')
    raw = bytes.fromhex(credential)
    if raw[:21] != b'email-next/device/v0\0':
        raise ValueError('Credential prefix')
    principal, device = 'enp0:'+raw[21:53].hex(), 'end0:'+raw[53:].hex()
    binding = encode_event(dict(version='0', purpose='device-binding', record='5'*32,
        principal=principal, device=device, signingKey=key,
        roles=['send','receive','enroll','revoke'], notBefore=str(now-60), notAfter=str(now+3600),
        authority={'kind':'first-contact'}))
    state = encode_event(dict(version='0', purpose='identity-state', principal=principal,
        record='6'*32, revision='0', previous=[], issuedAt=str(now),
        bindings=[dict(device=device,digest=hashlib.sha256(binding).hexdigest())], revoked=[], signer=device))
    return binding, state


def check(binding, state, authorization, possession, state_proof, credential, leaf_key, now):
    record = dict(binding=base64.b64encode(binding).decode(), state=base64.b64encode(state).decode(),
        authorization=authorization, possession=possession, stateProof=state_proof,
        time={'earliest':str(now),'latest':str(now)})
    # A fresh store is deliberate fixture policy, not a replacement for retained account history.
    with tempfile.TemporaryDirectory() as directory:
        store=IdentityStore(Path(directory)/'identity.sqlite')
        try:
            accepted=store.observe(record,first_contact_policy='allow-unverified')
            if accepted['status']!='pinned-unverified':return accepted['status']
            current=store.check_device(credential,leaf_key,role='send',
                time=record['time'],trust_policy='allow-unverified')
            if current['status']=='authorized-unverified':return 'authorized-first-contact-unverified'
            if current.get('reason')=='signing-key':return 'signing-key-mismatch'
            if current.get('reason') in ('device-not-current','accepted-identity'):return 'credential-mismatch'
            return current['status']
        finally:
            store.close()

if __name__=='__main__':
    if sys.argv[1]=='prepare':
        for value in prepare(sys.argv[2],sys.argv[3],int(sys.argv[4])):print(value.hex())
    elif sys.argv[1]=='check':
        print(check(bytes.fromhex(sys.argv[2]),bytes.fromhex(sys.argv[3]),*sys.argv[4:7],
            bytes.fromhex(sys.argv[7]),bytes.fromhex(sys.argv[8]),int(sys.argv[9])),end='')
    else:raise ValueError('Unknown fixture operation')
