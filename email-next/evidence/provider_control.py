"""Bounded configured-provider wire experiment. No HTTP, authority or MLS effects.

Keys/configuration are supplied by the caller. Signature validity does not verify
mailbox ownership, current device authority, binding expiry or package validity.
"""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
from passive_discovery import canonical_base64, hexadecimal, decode_passive_discovery, uint64

PROFILE = 'en-provider-control-0'
DOMAIN = b'email-next/provider-control/v0\0'
OPERATIONS = {'initiator': ['configuration-read', 'request-write', 'exchange-read'],
              'target': ['configuration-read', 'pending-read', 'exchange-read', 'response-write']}
DEFAULT_LIMITS = dict(maxWrapperBytes=262144, maxResponseBytes=1048576, maxJsonDepth=32,
 pendingPageSize=32, maxPendingPerGrant=8, maxRequestLifetimeSeconds=120,
 maxClockUncertaintySeconds=5, newRequestsPerMinute=10, requestsPerMinute=60,
 minPollIntervalSeconds=5, cursorLifetimeSeconds=120, retentionSeconds=86400,
 maxActiveCursorsPerGrant=8, maxPendingPerAccount=64, newRequestsPerAccountPerMinute=100,
 maxPendingPerService=1024, newRequestsPerServicePerMinute=1000,
 failedAuthenticationPerSourcePerMinute=30)
CONFIG_FIELDS = set('profile grant account service prefix initiator target initiatorState initiatorBinding targetState targetBinding role operations notBefore notAfter limits'.split())
COMMON = set('profile kind id service prefix grant account initiator target nonce notBefore notAfter'.split())
REQUEST_FIELDS = COMMON | set('initiatorState initiatorBinding targetState targetBinding purpose'.split())
RESPONSE_FIELDS = COMMON | {'requestHash', 'advertisement'}


def exact(value, fields):
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError('Exact object schema required')


def integer(value, positive=False):
    if type(value) is not int or not (int(positive) <= value <= 9007199254740991):
        raise ValueError('Expected safe integer')
    return value


def decode(octets, *, max_bytes, max_depth):
    if not isinstance(octets, bytes) or len(octets) > max_bytes:
        raise ValueError('Byte limit')
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError('Duplicate JSON name')
            out[k] = v
        return out
    try:
        text = octets.decode('utf-8')
        value = json.loads(text, object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError('JSON constant')))
    except (UnicodeError, RecursionError, json.JSONDecodeError) as e:
        raise ValueError('Invalid JSON') from e
    def walk(v, depth):
        if isinstance(v, (dict, list)):
            if depth > max_depth:
                raise ValueError('Depth limit')
            for x in (list(v.keys()) + list(v.values()) if isinstance(v, dict) else v):
                walk(x, depth + 1 if isinstance(x, (dict, list)) else depth)
        elif isinstance(v, str):
            try: v.encode('utf-8')
            except UnicodeError as e: raise ValueError('Invalid scalar') from e
        elif v is not None:
            integer(v)
    walk(value, 1)
    return value


def node(script, value):
    result = subprocess.run(['node', '--input-type=module', '-e', script],
        input=json.dumps(value), text=True, capture_output=True, check=True, timeout=10)
    return json.loads(result.stdout)


def participant(value):
    exact(value, {'principal', 'device'})
    for field, prefix in [('principal', 'enp0:'), ('device', 'end0:')]:
        v = value[field]
        if not isinstance(v, str) or not v.startswith(prefix) or not hexadecimal(v[5:], 64) or v[5:] == '0'*64:
            raise ValueError('Participant identifier')


def interval(value):
    before, after = integer(value['notBefore']), integer(value['notAfter'])
    if before > after: raise ValueError('Reversed interval')
    return before, after


def current(value, time, limits):
    if not isinstance(time, tuple) or len(time) != 2: raise ValueError('Clock interval required')
    low, high = map(integer, time)
    if high < low or high-low > limits['maxClockUncertaintySeconds']: raise ValueError('Clock uncertainty')
    before, after = interval(value)
    if not before <= low <= high <= after: raise ValueError('Not current')


def timing(config, records, time):
    """Separate use-time outcome; never prevents inspection of retained retries."""
    if time is None:
        return 'unavailable'
    try:
        for record in [config] + records:
            current(record,time,config['limits'])
    except ValueError:
        return 'not-usable'
    return 'within-intervals'


def validate_configuration(octets, *, max_bytes=1048576, max_depth=32):
    """Local budgets cap untrusted configuration; never authority by itself."""
    c = decode(octets, max_bytes=max_bytes, max_depth=max_depth)
    exact(c, CONFIG_FIELDS)
    if c['profile'] != PROFILE or not isinstance(c['role'], str) or c['role'] not in OPERATIONS or c['operations'] != OPERATIONS[c['role']]:
        raise ValueError('Profile or role operations')
    for name in ['grant', 'account', 'initiatorState', 'initiatorBinding', 'targetState', 'targetBinding']:
        if not hexadecimal(c[name], 64): raise ValueError('Digest or identifier')
    participant(c['initiator']); participant(c['target']); interval(c)
    exact(c['limits'], set(DEFAULT_LIMITS))
    for value in c['limits'].values(): integer(value, positive=True)
    if c['limits']['maxResponseBytes'] < 2*c['limits']['maxWrapperBytes']+4096:
        raise ValueError('Response cannot contain maximum wrappers')
    url = Path(__file__).with_name('service-question.mjs').as_uri()
    script = f"import {{isServiceOrigin,isServiceEndpoint}} from {json.dumps(url)}; let s=''; for await(const c of process.stdin)s+=c; const v=JSON.parse(s); console.log(JSON.stringify(isServiceOrigin(v.service)&&isServiceEndpoint(v.prefix,v.service,{{prefix:true}})));"
    if not node(script, c): raise ValueError('Unsupported service origin/prefix')
    return c


def verify_signature(payload, signature, public_key, domain=DOMAIN):
    if not hexadecimal(signature, 128) or not hexadecimal(public_key, 64): raise ValueError('Signature/key spelling')
    signed = domain + len(payload).to_bytes(4, 'big') + payload
    script = """import {createPublicKey,verify} from 'node:crypto';let s='';for await(const c of process.stdin)s+=c;
const v=JSON.parse(s);const key=createPublicKey({key:Buffer.concat([Buffer.from('302a300506032b6570032100','hex'),Buffer.from(v.key,'hex')]),format:'der',type:'spki'});
console.log(JSON.stringify(verify(null,Buffer.from(v.bytes,'base64'),key,Buffer.from(v.signature,'hex'))));"""
    if not node(script, {'key':public_key,'signature':signature,'bytes':base64.b64encode(signed).decode()}):
        raise ValueError('Signature invalid')


def wrapper(octets, config):
    limits = config['limits']
    w = decode(octets, max_bytes=limits['maxWrapperBytes'], max_depth=limits['maxJsonDepth'])
    exact(w, {'payload', 'signature'})
    raw = canonical_base64(w['payload'])
    v = decode(raw, max_bytes=limits['maxWrapperBytes'], max_depth=limits['maxJsonDepth'])
    return w, raw, v


def common(v, config, route_id, time):
    for field in ['profile','service','prefix','grant','account','initiator','target']:
        if v[field] != config[field]: raise ValueError('Configuration binding')
    if not hexadecimal(route_id,64) or v['id'] != route_id or not hexadecimal(v['nonce'],64):
        raise ValueError('Route/nonce binding')
    interval(v)
    if not config['notBefore'] <= v['notBefore'] <= v['notAfter'] <= config['notAfter']:
        raise ValueError('Grant interval')


def validate_request(octets, config, public_key, *, route_id, time):
    w, raw, v = wrapper(octets,config)
    exact(v, REQUEST_FIELDS); common(v,config,route_id,time)
    if v['kind'] != 'challenge' or v['purpose'] != 'fresh-device-discovery': raise ValueError('Purpose')
    for field in ['initiatorState','initiatorBinding','targetState','targetBinding']:
        if v[field] != config[field]: raise ValueError('State/binding mismatch')
    if v['notAfter']-v['notBefore'] > config['limits']['maxRequestLifetimeSeconds']: raise ValueError('Lifetime')
    verify_signature(raw,w['signature'],public_key)
    return {'status':'signature-valid-only','value':v,'payload':raw,'wrapper':octets,
            'digest':hashlib.sha256(raw).hexdigest(),'new_admission_time':timing(config, [v], time),
            'identity_authorized':False,'mls_validated':False}


def validate_response(octets, request_octets, config, initiator_key, target_key, *, route_id, time, target_mailbox):
    request = validate_request(request_octets,config,initiator_key,route_id=route_id,time=time)
    w, raw, v = wrapper(octets,config)
    exact(v,RESPONSE_FIELDS); common(v,config,route_id,time)
    r=request['value']
    if v['kind'] != 'device-evidence' or v['requestHash'] != request['digest'] or v['nonce'] != r['nonce']:
        raise ValueError('Request binding')
    if not r['notBefore'] <= v['notBefore'] <= v['notAfter'] <= r['notAfter']: raise ValueError('Response interval')
    verify_signature(raw,w['signature'],target_key)
    encoded=json.dumps(v['advertisement'],separators=(',',':'),ensure_ascii=False).encode()
    ad=decode_passive_discovery(encoded); assertion=ad['assertion']; a=assertion['value']
    for field in ['principal','device']:
        if a[field] != config['target'][field]: raise ValueError('Advertisement participant')
    if a['state'] != config['targetState'] or a['binding'] != config['targetBinding'] or a['mailbox'] != target_mailbox:
        raise ValueError('Advertisement binding')
    if assertion['mailbox_syntax'] != 'syntax-valid': raise ValueError('Mailbox dependency unresolved')
    before,after=uint64(a['notBefore']),uint64(a['notAfter'])
    if v['notAfter'] > after: raise ValueError('Advertisement interval')
    verify_signature(assertion['octets'],ad['signature'].hex(),target_key,b'email-next/passive-discovery/v0\0')
    return {'status':'signature-valid-only','value':v,'payload':raw,'wrapper':octets,
            'new_admission_time':timing(config,[r,v,{'notBefore':before,'notAfter':after}],time),
            'identity_authorized':False,'mls_validated':False}
