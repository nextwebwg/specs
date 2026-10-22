"""Signed mailbox-setup0/1 records with explicit assertion8/9 package validation.

Candidate-only: no MIME/DKIM/envelope verification, identity installation, disclosure
policy, attempt/key custody, durable response reservation, transport or MLS admission.
"""
import hashlib

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from email2_mailbox import validate as mailbox
from event_encoding import decode_event
from passive_discovery import canonical_base64, decode_passive_discovery, hexadecimal, uint64
from provider_control import exact
from suite_discovery8 import verify as verify_discovery

MAX = 4194304
FIELDS = set('version purpose request nonce source target assertion notBefore notAfter'.split())


def framing(kind, raw, *, version='0'):
    if version not in ('0', '1'):
        raise ValueError('Explicit supported setup version required')
    if kind not in ('request', 'response'):
        raise ValueError('Explicit setup kind required')
    return ('mail/setup-'+kind+'/v'+version).encode()+b'\0'+len(raw).to_bytes(4,'big')+raw


def decode(raw, kind):
    return decode_version(raw, kind, version='0')


def decode_version(raw, kind, *, version):
    framing(kind, b'', version=version)
    wrapper = decode_event(raw, max_octets=MAX)['value']
    exact(wrapper, {'payload', 'signature', 'advertisement'})
    if not hexadecimal(wrapper['signature'], 128):
        raise ValueError('Setup signature encoding')
    payload = canonical_base64(wrapper['payload'])
    if len(payload) > 262144:
        raise ValueError('Setup payload bound')
    value = decode_event(payload, max_octets=262144)['value']
    exact(value, FIELDS | ({'requestDigest'} if kind == 'response' else set())
          | ({'agreement'} if version == '1' else set()))
    if (value['version'], value['purpose']) != (version, 'mailbox-setup-'+kind):
        raise ValueError('Setup version/purpose')
    if version == '1' and value['agreement'] != 'mail-conversation-v1':
        raise ValueError('Exact requested reply-aware agreement required')
    if not hexadecimal(value['request'], 32) or value['request'] == '0'*32:
        raise ValueError('Setup request ObjectId')
    for name in ['nonce', 'assertion'] + (['requestDigest'] if kind == 'response' else []):
        if not hexadecimal(value[name], 64):
            raise ValueError('Setup digest/nonce')
    mailbox(value['source']); mailbox(value['target'])
    if value['source'] == value['target']:
        raise ValueError('Distinct source and target required')
    before, after = uint64(value['notBefore']), uint64(value['notAfter'])
    if before > after or (kind == 'request' and after-before > 600):
        raise ValueError('Setup interval')
    advertised = canonical_base64(wrapper['advertisement'])
    if len(advertised) > 1048576 or hashlib.sha256(advertised).hexdigest() != value['assertion']:
        raise ValueError('Original assertion wrapper commitment')
    decoded = decode_passive_discovery(advertised)
    assertion = decoded['assertion']['value']
    if assertion['version'] != ('9' if version == '1' else '8') or assertion['mailbox'] != value['source' if kind == 'request' else 'target']:
        raise ValueError('Current assertion actor mailbox')
    if not uint64(assertion['notBefore']) <= before <= after <= uint64(assertion['notAfter']):
        raise ValueError('Assertion interval')
    key = assertion['controlKey']
    if key is None:
        raise ValueError('Setup control key required')
    if kind == 'request':
        if assertion['keyPackage'] or assertion['keyPackageReceiveUntil'] is not None:
            raise ValueError('Initiating attempt has no MLS package')
        if key['notAfter'] != value['notAfter'] or key['receiveUntil'] != value['notAfter']:
            raise ValueError('Original attempt control-key deadline')
    elif not assertion['keyPackage']:
        raise ValueError('Responding package required')
    return wrapper, payload, value, advertised, decoded


def verify(raw, kind, identity, binary, *, time, trust_policy, request=None):
    return verify_version(raw, kind, identity, binary, time=time,
                          trust_policy=trust_policy, request=request, version='0')


def verify_version(raw, kind, identity, binary, *, time, trust_policy, version, request=None):
    wrapper, payload, value, advertised, decoded = decode_version(raw, kind, version=version)
    if kind == 'response':
        if not isinstance(request, bytes):
            raise ValueError('Original local request bytes required')
        original = verify_version(request, 'request', identity, binary, time=time,
                                  trust_policy=trust_policy, version=version)
        expected = original['record']
        for name in ['request', 'nonce', 'source', 'target'] + (['agreement'] if version == '1' else []):
            if value[name] != expected[name]:
                raise ValueError('Exact original request correlation')
        if value['requestDigest'] != original['payloadDigest']:
            raise ValueError('Original request payload digest')
        if not uint64(expected['notBefore']) <= uint64(value['notBefore']) <= uint64(value['notAfter']) <= uint64(expected['notAfter']):
            raise ValueError('Response exceeds original attempt')
    elif request is not None:
        raise ValueError('Initiation has no parent request')
    if not uint64(value['notBefore']) <= uint64(time['earliest']) <= uint64(time['latest']) <= uint64(value['notAfter']):
        raise ValueError('Current complete setup interval')
    assertion = decoded['assertion']['value']
    binding = next((b['value'] for b in decoded['identity']['bindings'] if b['digest'] == assertion['binding']), None)
    if binding is None or binding['device'] != assertion['device']:
        raise ValueError('Setup signing binding')
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(binding['signingKey'])).verify(bytes.fromhex(wrapper['signature']), framing(kind, payload, version=version))
    except (InvalidSignature, ValueError) as error:
        raise ValueError('Setup original signature') from error
    if version == '1':
        from suite_discovery9 import verify as selected_discovery
    else:
        selected_discovery = verify_discovery
    checked = selected_discovery(advertised, identity, binary, time=time, trust_policy=trust_policy)
    expected = 'suite-capabilities-validated-unverified' if kind == 'request' else 'suite-setup-validated-unverified'
    if checked.get('status') != expected:
        raise ValueError('Current setup assertion/package required')
    return dict(status='mailbox-setup-candidate-only', record=value,
                payloadDigest=hashlib.sha256(payload).hexdigest(), original_payload=payload,
                actor={k:assertion[k] for k in ('principal','device','state','binding')},
                original_advertisement=advertised, mailbox_verified=False)


def verify_response_candidate(candidate, request, identity, binary, *, time, trust_policy):
    """Bind a trusted open_candidate result to the exact original pending request.

    This still does not prove local pending-state/key custody, transport provenance,
    association selection, journal admission or permission to release human content.
    """
    if candidate.get('status') != 'sealed-control-candidate-only':
        raise ValueError('Validated sealed-control candidate required')
    response = verify(candidate['original_body'], 'response', identity, binary,
                      time=time, trust_policy=trust_policy, request=request)
    _, _, original, _, decoded = decode(request, 'request')
    source = decoded['assertion']['value']
    intent = candidate['intent']
    if (intent['kind'] != 'mailbox-setup-response' or intent['sender'] != response['actor'] or
            intent['recipient'] != {k:source[k] for k in ('principal','device')} or
            intent['key'] != source['controlKey']['id']):
        raise ValueError('Exact response actor/initiating recipient/key required')
    value = response['record']
    if not uint64(value['notBefore']) <= uint64(intent['notBefore']) <= uint64(intent['notAfter']) <= uint64(value['notAfter']) <= uint64(original['notAfter']):
        raise ValueError('Sealed response original interval')
    return response


def creator_receiving_candidate(request, ordinary, identity, binary, *, time, trust_policy):
    """Check a separate ordinary creator assertion, never roster/admission readiness.

    Current suite verification is real; local secret custody, its independent
    publication role, application intersection and final roster selection are not.
    """
    initiating = verify(request, 'request', identity, binary, time=time, trust_policy=trust_policy)
    _, _, _, _, original = decode(request, 'request')
    source = original['assertion']['value']
    decoded = decode_passive_discovery(ordinary)
    candidate = decoded['assertion']['value']
    checked = verify_discovery(ordinary, identity, binary, time=time, trust_policy=trust_policy)
    if checked.get('status') not in ('suite-capabilities-validated-unverified', 'suite-setup-validated-unverified'):
        raise ValueError('Current ordinary creator receiving assertion required')
    if any(candidate[name] != initiating['actor'][name] for name in ('principal', 'device')) or candidate['mailbox'] != source['mailbox']:
        raise ValueError('Same intended creator and mailbox required')
    key = candidate['controlKey']
    if key is None or key['id'] == source['controlKey']['id'] or key['publicKey'] == source['controlKey']['publicKey']:
        raise ValueError('Dedicated attempt key cannot become ordinary receiving key')
    return dict(status='ordinary-creator-assertion-candidate-only', original_assertion=ordinary,
                wrapperDigest=hashlib.sha256(ordinary).hexdigest(),
                assertionDigest=decoded['assertion']['digest'],
                actor={name:candidate[name] for name in ('principal','device','state','binding')})
