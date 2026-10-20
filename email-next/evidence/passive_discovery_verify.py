"""Real assertion proof plus read-only identity snapshot. Never a release permission.

Does not install incoming identity records, verify mailbox ownership, validate MLS
packages, or reserve the store against changes after check_device returns.
"""
import base64
import json
from pathlib import Path
import subprocess
from passive_discovery import decode_passive_discovery, assertion_time_status, hexadecimal


def verify_passive_discovery(octets, store, *, time, trust_policy):
    return _verify(octets,store,time=time,trust_policy=trust_policy,locked=False)

def verify_passive_discovery_locked(octets,store,*,time,trust_policy):
    if not store.db.in_transaction:raise ValueError('Transaction required')
    return _verify(octets,store,time=time,trust_policy=trust_policy,locked=True)

def _verify(octets, store, *, time, trust_policy,locked):
    decoded = decode_passive_discovery(octets)
    assertion = decoded['assertion']
    value = assertion['value']
    binding = next((b for b in decoded['identity']['bindings'] if b['digest'] == value['binding']), None)
    if binding is None:
        return {'status':'pending', 'reason':'asserted-binding'}
    candidate = binding['value']
    if candidate.get('device') != value['device'] or not hexadecimal(candidate.get('signingKey'),64):
        return {'status':'invalid', 'reason':'asserted-binding'}
    # Incoming evidence supplies only a candidate key. Store comparison below
    # independently requires the exact binding already accepted locally.
    request = {'version':value['version'],'payload':base64.b64encode(assertion['octets']).decode('ascii'),
               'signature':decoded['signature'].hex(), 'key':candidate['signingKey']}
    check = subprocess.run(['node',str(Path(__file__).with_name('check-passive-discovery.mjs'))],
                           input=json.dumps(request),capture_output=True,text=True,check=True)
    if json.loads(check.stdout)['status'] != 'signature-valid':
        return {'status':'invalid', 'reason':'assertion-proof'}
    if assertion['mailbox_syntax'] != 'syntax-valid':
        return {'status':'pending', 'reason':'a-label-validation'}
    interval = time if isinstance(time,dict) else {}
    timing = assertion_time_status(assertion,earliest=interval.get('earliest'),latest=interval.get('latest'))
    if timing != 'within-asserted-interval':
        return {'status':'pending' if timing=='pending' else 'not-current','reason':'assertion-validity'}
    credential = b'email-next/device/v0\0'+bytes.fromhex(value['principal'][5:])+bytes.fromhex(value['device'][5:])
    decision = (store._check_device_locked(value['principal'],value['device'],bytes.fromhex(candidate['signingKey']),'receive',time,trust_policy) if locked else store.check_device(credential,bytes.fromhex(candidate['signingKey']),role='receive',time=time,trust_policy=trust_policy))
    if decision['status'] != 'authorized-unverified':
        return decision
    if decision['head'] != value['state'] or decision['binding'] != value['binding']:
        return {'status':'stale','reason':'asserted-state-or-binding','head':decision['head']}
    return {'status':'snapshot-authorized-unverified','head':decision['head'],'binding':decision['binding'],
            'assertion':assertion['digest'],'principal':value['principal'],'device':value['device'],
            'mailbox_verified':False,'mls_validated':False}
