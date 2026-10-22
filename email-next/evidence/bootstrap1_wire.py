"""Bootstrap1 wire/signature/correlation candidates, not a service or authority.

Expected actors and descriptor fetch trust come from the caller. This component
never authorizes an account, accepts an identity, validates native MLS packages,
allocates a slot, contacts a URL or releases content.
"""
import hashlib
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from bootstrap_exchange import FIELDS as OLD_FIELDS, b64, interval
from event_encoding import decode_event
from history_transfer import endpoint
from passive_discovery import hexadecimal, uint64, decode_passive_discovery
from email2_mailbox import validate as mailbox, selected_domain
from provider_discovery import urls, domain_name

AGREEMENT = 'mail-conversation-v1'
FIELDS = {kind: set(fields.split()) | {'agreement'} for kind, fields in OLD_FIELDS.items()}
FIELDS['source'].add('targetDelegation')
FIELDS['route-request'] = set('version purpose agreement request issuer exchange sourceDigest nonce recipient relayDomain sourceDomain sourceService sourcePermission permissionDigest notBefore notAfter'.split())
FIELDS['route-response'] = set('version purpose agreement response issuer exchange sourceDigest requestDigest nonce device relayDomain invitation notBefore notAfter'.split())
DESCRIPTOR = set('version purpose agreement domain publication generation service managementPrefix sourcePrefix exchangePrefix roles notBefore notAfter'.split())


def hex_field(value, size=64, *, nonzero=False):
    if not hexadecimal(value, size) or (nonzero and int(value, 16) == 0):
        raise ValueError('Exact hexadecimal field required')


def frame(kind, raw):
    if kind not in FIELDS or not isinstance(raw, bytes) or len(raw) > 262144:
        raise ValueError('Explicit supported kind and bounded original bytes required')
    return ('mail/bootstrap/'+kind+'/v1').encode()+b'\0'+len(raw).to_bytes(4, 'big')+raw


def parse(octets, kind):
    frame(kind, b'')
    wrapper = decode_event(octets, max_octets=4194304)['value']
    if set(wrapper) != {'payload', 'signature'}:
        raise ValueError('Exact proof wrapper required')
    raw = b64(wrapper['payload']); frame(kind, raw)
    hex_field(wrapper['signature'], 128)
    value = decode_event(raw, max_octets=262144)['value']
    if (set(value) != FIELDS[kind] or value['version'] != '1'
            or value['purpose'] != 'bootstrap-'+kind or value['agreement'] != AGREEMENT):
        raise ValueError('Exact bootstrap1 kind/version/agreement/members required')
    urls(value['issuer'])
    before, after = uint64(value['notBefore']), uint64(value['notAfter'])
    if before > after or (kind == 'source' and after-before > 600):
        raise ValueError('Original bounded interval required')
    for key in ['preparation', 'request', 'conversation', 'response', 'publication']:
        if key in value:
            hex_field(value[key], 32, nonzero=True)
    for key in ['source', 'delegation', 'targetDelegation', 'accountSource', 'nonce',
                'exchange', 'sourceDigest', 'requestDigest', 'sourcePermission', 'permissionDigest']:
        if key in value:
            hex_field(value[key])
    for key in ['sender', 'device', 'recipient']:
        if key in value:
            endpoint(value[key])
    for key in ['senderMailbox', 'targetMailbox', 'mailbox']:
        if key in value:
            mailbox(value[key])
    for key in ['targetService', 'sourceService']:
        if key in value:
            urls(value[key])
    for key in ['sourceDomain', 'relayDomain']:
        if key in value and value[key] != '':
            domain_name(value[key])
    for key in ['advertisement', 'invitation']:
        if key in value:
            b64(value[key])
    if kind == 'publication' and value['scope'] != 'automatic-first-contact':
        raise ValueError('Exact publication scope required')
    return raw, value, bytes.fromhex(wrapper['signature'])


def verify_candidate(octets, kind, actor, *, time):
    endpoint(actor)
    raw, value, signature = parse(octets, kind)
    if kind == 'source' and value['sender'] != actor:
        raise ValueError('Exact independently selected source actor required')
    if kind in ('response', 'publication', 'route-response') and value['device'] != actor:
        raise ValueError('Exact independently selected target actor required')
    interval(value, time)
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(actor['key'])).verify(signature, frame(kind, raw))
    except InvalidSignature as error:
        raise ValueError('Original bootstrap1 signature required') from error
    if 'advertisement' in value:
        decoded = decode_passive_discovery(b64(value['advertisement']))
        ad = decoded['assertion']['value']
        address = value['senderMailbox'] if kind == 'source' else value['mailbox']
        if (ad['version'] != '9' or ad['mailbox'] != address
                or any(ad[key] != actor[key] for key in ('principal', 'device', 'state', 'binding'))):
            raise ValueError('Original assertion9 actor/mailbox required')
        interval(ad, time)
        evidence = decoded['identity']
        if (evidence['principal'] != actor['principal']
                or not any(item['digest'] == actor['state'] for item in evidence['states'])
                or not any(item['digest'] == actor['binding'] for item in evidence['bindings'])):
            raise ValueError('Complete original assertion identity references required')
        try:
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(actor['key'])).verify(
                decoded['signature'], decoded['assertion']['signature_input'])
        except InvalidSignature as error:
            raise ValueError('Original assertion9 signature required') from error
        if kind in ('response', 'publication') and len(ad['keyPackage']) != 1:
            raise ValueError('Responding admission material required')
    return dict(state='candidate-bootstrap1-proof', original_payload=raw, record=value,
                payload_digest=hashlib.sha256(raw).hexdigest(), package_validated=False)


def descriptor_candidate(octets, *, domain, time):
    value = decode_event(octets, max_octets=1048576)['value']
    if (set(value) != DESCRIPTOR or value['version'] != '1'
            or value['purpose'] != 'bootstrap-service-discovery'
            or value['agreement'] != AGREEMENT or value['domain'] != domain):
        raise ValueError('Exact bootstrap descriptor1 required')
    domain_name(domain); hex_field(value['publication'], 32, nonzero=True)
    if uint64(value['generation']) == 0:
        raise ValueError('Positive descriptor generation required')
    interval(value, time)
    prefixes = [value[key] for key in ['managementPrefix', 'sourcePrefix', 'exchangePrefix']]
    urls(value['service'], prefixes=prefixes)
    for index, prefix in enumerate(prefixes):
        for other in prefixes[index+1:]:
            if prefix.startswith(other) or other.startswith(prefix):
                raise ValueError('Nonoverlapping descriptor prefixes required')
    roles = value['roles']
    if (not isinstance(roles, list) or not roles
            or any(role not in ('request-source', 'respond-target') for role in roles)
            or roles != sorted(set(roles))):
        raise ValueError('Exact canonical roles required')
    return value


def handle(source):
    issuer = source['issuer'].encode()
    return hashlib.sha256(b'mail/bootstrap/exchange/v1\0'+len(issuer).to_bytes(4, 'big')
                          +issuer+bytes.fromhex(source['source'])).hexdigest()


def correlate_response(source, response, source_actor, target_actor, target_descriptor, *, time):
    src = verify_candidate(source, 'source', source_actor, time=time)
    result = verify_candidate(response, 'response', target_actor, time=time)
    s, r = src['record'], result['record']
    d = descriptor_candidate(target_descriptor, domain=selected_domain(s['targetMailbox']), time=time)
    if (hashlib.sha256(target_descriptor).hexdigest() != s['targetDelegation']
            or d['service'] != s['targetService'] or 'respond-target' not in d['roles']):
        raise ValueError('Exact original target delegation required')
    if (r['issuer'] != s['targetService'] or r['exchange'] != handle(s)
            or r['sourceDigest'] != src['payload_digest'] or r['nonce'] != s['nonce']
            or r['mailbox'] != s['targetMailbox']
            or not uint64(s['notBefore']) <= uint64(r['notBefore']) <= uint64(r['notAfter']) <= uint64(s['notAfter'])):
        raise ValueError('Exact original source/target/nonce/deadline correlation required')
    return result
