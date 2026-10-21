"""Bounded discovery syntax experiment. No signatures, identity acceptance or MLS validation.

Input is an already transfer-decoded MIME part. Identity bundle decoding checks
carrier structure/scope, not complete state/binding schemas or their proofs.
A-labels require an explicitly configured coherent Unicode17 acceptance provider.
"""
import base64
import binascii
import hashlib
import re
from event_encoding import decode_event, encode_event
from identity_bundle import decode_identity_bundle

FIELDS = set('version purpose record principal device state binding mailbox notBefore notAfter features keyPackage'.split())
DOMAIN = b'email-next/passive-discovery/v0\0'
APPLICATION_DOMAIN = b'email-next/passive-discovery/v1\0'
TUPLE_DOMAIN = b'email-next/passive-discovery/v2\0'
PRESENTATION_DOMAIN = b'email-next/passive-discovery/v5\0'
PRIVATE_COPY_DOMAIN = b'email-next/passive-discovery/v4\0'
RICH_DOMAIN = b'email-next/passive-discovery/v3\0'
ATEXT = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&'*+-/=?^_`{|}~")


def hexadecimal(value, length):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{'+str(length)+'}', value) is not None


def uint64(value):
    if not isinstance(value, str) or not re.fullmatch(r'0|[1-9][0-9]{0,19}', value):
        raise ValueError('Expected canonical uint64 string')
    result = int(value)
    if result > 2**64-1:
        raise ValueError('Unsigned overflow')
    return result


def canonical_base64(value):
    if not isinstance(value, str):
        raise ValueError('Expected base64 string')
    try:
        result = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error) as error:
        raise ValueError('Invalid base64') from error
    if base64.b64encode(result).decode('ascii') != value:
        raise ValueError('Noncanonical base64')
    return result


def mailbox_syntax(value):
    """Narrow ASCII dot-string/LDH syntax only; no identity or deliverability proof."""
    if not isinstance(value, str) or not value.isascii() or value.count('@') != 1:
        raise ValueError('Unsupported mailbox spelling')
    local, domain = value.split('@')
    if not local or len(local) > 64 or len(value) + 2 > 256:
        raise ValueError('SMTP mailbox/path limit')
    if any(not atom or any(c not in ATEXT for c in atom) for atom in local.split('.')):
        raise ValueError('Expected unquoted Dot-string')
    if not domain or domain != domain.lower() or len(domain) > 253:
        raise ValueError('Expected lowercase DNS domain')
    labels = domain.split('.')
    for label in labels:
        if not 1 <= len(label) <= 63 or not label[0].isalnum() or not label[-1].isalnum():
            raise ValueError('Invalid DNS label bounds')
        if any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in label):
            raise ValueError('Expected LDH domain')
    if sum(1+len(label) for label in labels)+1 > 255:
        raise ValueError('DNS wire name limit')
    if any(label.startswith('xn--') for label in labels):
        from idna17_acceptance import validate_domain
        if not validate_domain(domain):return 'a-label-validation-required'
    return 'syntax-valid'


def decode_assertion(octets):
    value = decode_event(octets)['value']
    application_version = value.get('version') in ('1','2','3','4','5','6','7')
    fields = FIELDS | {'applications'} if application_version else FIELDS
    if value.get('version')=='7':fields=fields|{'orderingExchanges'}
    if set(value) != fields or value['version'] not in ('0', '1', '2', '3', '4', '5', '6', '7') or value['purpose'] != 'passive-discovery':
        raise ValueError('Invalid assertion schema/purpose')
    if value['version']=='7' and value['orderingExchanges']!=[{'format':'quorum-exchange-experiment','version':'1'}]:raise ValueError('Exact ordering exchange capability')
    if not hexadecimal(value['record'], 32) or value['record'] == '0'*32:
        raise ValueError('Invalid ObjectId')
    for name, prefix in [('principal', 'enp0:'), ('device', 'end0:')]:
        identifier = value[name]
        if not isinstance(identifier, str) or not identifier.startswith(prefix) or not hexadecimal(identifier[len(prefix):], 64) or identifier[len(prefix):] == '0'*64:
            raise ValueError('Invalid identifier')
    if not all(hexadecimal(value[name], 64) for name in ['state', 'binding']):
        raise ValueError('Invalid reference digest')
    before, after = uint64(value['notBefore']), uint64(value['notAfter'])
    if after < before:
        raise ValueError('Invalid advertisement interval')
    features = value['features']
    if not isinstance(features, list) or features not in [[], ['mls-1-0001']]:
        raise ValueError('Unsupported, duplicate or unordered features')
    if value['version'] in ('2','3','4','5','6','7'):
        from application_tuples import validate_tuples
        validate_tuples(value['applications'],version=value['version'])
        if value['applications'] and not features:raise ValueError('Application tuple capability')
    elif application_version:
        applications = value['applications']
        if not isinstance(applications, list) or len(applications) > 1 or (applications and not features):
            raise ValueError('Application descriptor cardinality/capability')
        for application in applications:
            if not isinstance(application, dict) or set(application) != {'envelopeVersion', 'operations', 'ordering'} or application['envelopeVersion'] != '1':
                raise ValueError('Application descriptor')
            for field, supported in [('operations', {'answer', 'message', 'question', 'reaction', 'reaction-withdraw'}), ('ordering', {'fixed-roster-v0', 'designated-member-v0'})]:
                items = application[field]
                if not isinstance(items, list) or not items or any(not isinstance(item, str) or item not in supported for item in items) or items != sorted(set(items)):
                    raise ValueError('Unsupported, duplicate or unordered application capability')
    packages = value['keyPackage']
    if not isinstance(packages, list) or len(packages) > 1 or (packages and not features):
        raise ValueError('Invalid package cardinality/capability')
    package = canonical_base64(packages[0]) if packages else None
    mailbox = mailbox_syntax(value['mailbox'])
    return {'octets': octets, 'value': value, 'digest': hashlib.sha256(octets).hexdigest(),
            'signature_input': (b'email-next/passive-discovery/v7\0' if value['version']=='7' else b'email-next/passive-discovery/v6\0' if value['version']=='6' else PRESENTATION_DOMAIN if value['version']=='5' else PRIVATE_COPY_DOMAIN if value['version']=='4' else RICH_DOMAIN if value['version']=='3' else TUPLE_DOMAIN if value['version']=='2' else APPLICATION_DOMAIN if application_version else DOMAIN)+len(octets).to_bytes(4, 'big')+octets,
            'mailbox_syntax': mailbox, 'key_package_octets': package,
            'status': 'syntax-only-unverified'}


def decode_passive_discovery(octets):
    value = decode_event(octets)['value']
    if set(value) != {'payload', 'signature', 'identity'} or not hexadecimal(value['signature'], 128):
        raise ValueError('Invalid discovery wrapper')
    assertion = decode_assertion(canonical_base64(value['payload']))
    # Wrapper bytes are not signed; enclosed record bytes survive reserialization.
    identity = decode_identity_bundle(encode_event(value['identity']))
    if identity['principal'] != assertion['value']['principal']:
        raise ValueError('Identity/assertion scope mismatch')
    return {'octets': octets, 'assertion': assertion, 'signature': bytes.fromhex(value['signature']),
            'identity': identity, 'status': 'syntax-only-unverified'}


def assertion_time_status(assertion, *, earliest=None, latest=None):
    """Time result alone never authorizes use; inputs are canonical uint64 strings."""
    if earliest is None or latest is None:
        return 'pending'
    low, high = uint64(earliest), uint64(latest)
    if high < low:
        return 'pending'
    value = assertion['value']
    before, after = uint64(value['notBefore']), uint64(value['notAfter'])
    if high < before:
        return 'not-yet-valid'
    if low > after:
        return 'expired'
    return 'within-asserted-interval' if before <= low <= high <= after else 'pending'
