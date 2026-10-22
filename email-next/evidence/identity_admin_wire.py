"""State1 shape and outer bundle1/share1 carrier syntax. NO authorization.

No parent DAG validation, repair derivation, signature/current-role check, local
approval, operational state installation or send permission follows from parsing.
Original bytes remain separate from their decoded values.
"""
import base64
import hashlib
import json
import re
from event_encoding import decode_event
from identity_repair_candidate import canonical
from admission_windows import uint

PAYLOAD_MAX=1048576
CONTAINER_MAX=4194304
HEX=re.compile('[0-9a-f]{64}\\Z')
SIG=re.compile('[0-9a-f]{128}\\Z')
DEVICE=re.compile('end0:[0-9a-f]{64}\\Z')
PRINCIPAL=re.compile('enp0:[0-9a-f]{64}\\Z')
OID=re.compile('[0-9a-f]{32}\\Z')


def exact(value,keys):
    if not isinstance(value,dict) or set(value)!=set(keys.split()):raise ValueError('Exact schema required')


def identifier(value,pattern):
    if not isinstance(value,str) or not pattern.fullmatch(value) or value.split(':')[-1]=='0'*len(value.split(':')[-1]):raise ValueError('Identifier encoding')


def signature(value,*,partial=False):
    if partial and value=='':return
    if not isinstance(value,str) or not SIG.fullmatch(value):raise ValueError('Signature encoding')


def payload(value):
    if not isinstance(value,str) or len(value)>1398104:raise ValueError('Payload base64 bound')
    try:raw=base64.b64decode(value,validate=True)
    except (ValueError,TypeError) as error:raise ValueError('Payload base64') from error
    if len(raw)>PAYLOAD_MAX or base64.b64encode(raw).decode()!=value:raise ValueError('Canonical bounded payload')
    return raw


def state(raw):
    value=decode_event(raw)['value']
    exact(value,'version purpose kind principal record revision previous issuedAt bindings revoked signer')
    if value['version']!='1' or value['purpose']!='identity-state' or value['kind'] not in ('genesis','update','prune','repair','retire'):raise ValueError('State1 version/kind')
    if raw!=canonical(value):raise ValueError('State1 original canonical bytes required')
    identifier(value['principal'],PRINCIPAL);identifier(value['signer'],DEVICE);identifier(value['record'],OID)
    uint(value['revision']);uint(value['issuedAt'])
    parents=value['previous']
    if not isinstance(parents,list):raise ValueError('Parents array')
    for parent in parents:
        if not isinstance(parent,str) or not HEX.fullmatch(parent):raise ValueError('Parent digest')
    if parents!=sorted(set(parents)):raise ValueError('Distinct sorted parents')
    if value['kind']=='genesis':
        if parents or value['revision']!='0' or value['revoked']:raise ValueError('Genesis shape')
    elif value['revision']=='0' or (len(parents)<2 if value['kind']=='repair' else len(parents)!=1):raise ValueError('Kind predecessor shape')
    bindings=value['bindings'];revoked=value['revoked']
    if not isinstance(bindings,list) or not isinstance(revoked,list):raise ValueError('Roster arrays')
    for entry in bindings:
        exact(entry,'device digest');identifier(entry['device'],DEVICE)
        if not isinstance(entry['digest'],str) or not HEX.fullmatch(entry['digest']):raise ValueError('Binding digest')
    devices=[e['device'] for e in bindings]
    if devices!=sorted(set(devices)):raise ValueError('Distinct sorted bindings')
    for device in revoked:identifier(device,DEVICE)
    if revoked!=sorted(set(revoked)) or set(devices)&set(revoked):raise ValueError('Revocation roster')
    if (not bindings)!=(value['kind']=='retire'):raise ValueError('Empty roster only for retirement')
    if value['kind']=='genesis' and (len(devices)!=1 or devices[0]!=value['signer']):raise ValueError('Genesis signer')
    return dict(status='state1-syntax-only',octets=raw,digest=hashlib.sha256(raw).hexdigest(),value=value)


def bundle(raw):
    value=decode_event(raw,max_octets=CONTAINER_MAX)['value'];exact(value,'version purpose principal states bindings')
    if value['version']!='1' or value['purpose']!='identity-bundle':raise ValueError('Bundle1 version')
    identifier(value['principal'],PRINCIPAL)
    if not isinstance(value['states'],list) or not isinstance(value['bindings'],list) or not(value['states'] or value['bindings']):raise ValueError('Nonempty collections')
    for collection in ('states','bindings'):
        seen=set()
        for entry in value[collection]:
            if not isinstance(entry,dict) or 'payload' not in entry:raise ValueError('Proof entry')
            body=payload(entry['payload']);record=decode_event(body)['value'];digest=hashlib.sha256(body).hexdigest()
            if digest in seen or record.get('principal')!=value['principal']:raise ValueError('Duplicate or foreign record')
            seen.add(digest)
            if collection=='bindings':
                exact(entry,'payload authorization possession');signature(entry['authorization']);signature(entry['possession'])
                if record.get('purpose')!='device-binding' or record.get('version')!='0':raise ValueError('Binding0 scope')
                # Full binding schema/proof validation is an owning prerequisite.
            elif record.get('version')=='0':
                exact(entry,'payload signature');signature(entry['signature'])
                if record.get('purpose')!='identity-state':raise ValueError('State0 scope')
            elif record.get('version')=='1':
                exact(entry,'payload signature approvals');checked=state(body);signature(entry['signature'])
                if not isinstance(entry['approvals'],list):raise ValueError('Approvals array')
                devices=[]
                for approval in entry['approvals']:
                    exact(approval,'device signature');identifier(approval['device'],DEVICE);signature(approval['signature']);devices.append(approval['device'])
                if devices!=sorted(set(devices)) or checked['value']['signer'] in devices or (checked['value']['kind']!='repair' and devices):raise ValueError('Approval shape')
            else:raise ValueError('Unsupported state version')
    return dict(status='bundle1-carrier-only',octets=raw,value=value)


def share(raw):
    value=decode_event(raw,max_octets=CONTAINER_MAX)['value'];exact(value,'version purpose principal parents candidate by proof bindings')
    if value['version']!='1' or value['purpose']!='identity-repair-share':raise ValueError('Share1 version')
    identifier(value['principal'],PRINCIPAL);identifier(value['by'],DEVICE);signature(value['proof'],partial=True)
    candidate=state(payload(value['candidate']))
    if candidate['value']['kind']!='repair' or candidate['value']['principal']!=value['principal']:raise ValueError('Repair candidate scope')
    # The parent wrapper can be reserialized: original enclosed payloads remain
    # base64 strings and all authoritative comparisons use their original bytes.
    parent=bundle(json.dumps(value['parents'],separators=(',',':')).encode())
    if parent['value']['principal']!=value['principal']:raise ValueError('Parent scope')
    if not isinstance(value['bindings'],list):raise ValueError('Bindings array')
    digests=[]
    for entry in value['bindings']:
        exact(entry,'payload authorization possession');body=payload(entry['payload']);record=decode_event(body)['value']
        if record.get('version')!='0' or record.get('purpose')!='device-binding' or record.get('principal')!=value['principal']:raise ValueError('Replacement scope')
        signature(entry['authorization'],partial=True);signature(entry['possession'],partial=True)
        if not(entry['authorization'] or entry['possession']):raise ValueError('Empty proof entry')
        digests.append(hashlib.sha256(body).hexdigest())
    if digests!=sorted(set(digests)):raise ValueError('Distinct sorted replacement proofs')
    return dict(status='repair-share1-carrier-only',octets=raw,value=value,candidate=candidate)
