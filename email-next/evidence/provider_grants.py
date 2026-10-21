"""Public pair/role proof validation experiment, not account login or token minting.

ActiveLink and retained payloads are trusted service-journal inputs. No received
record creates a link, installs identity anchors, activates a grant or issues a
credential. Standalone checks are snapshots; real mutation must join the same
transaction as authoritative OAuth/link/grant revocation and queue operations.
"""
import base64
from dataclasses import dataclass
import hashlib
import re
import struct

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from history_transfer import authorize, authority_snapshot, endpoint
from provider_control import OPERATIONS, current, decode, exact, integer, validate_configuration

PROFILE = 'email2-provider-grants-v0'
FIELDS = {
    'pair-approval': set('profile purpose preparation request nonce delegationDigest link family mailbox configuration initiatorKey targetKey notBefore notAfter'.split()),
    'role-request': set('profile purpose request approvalDigest grant service prefix role device notBefore notAfter'.split()),
    'role-credential': set('profile purpose credential request nonce approvalDigest grant account service prefix role device notBefore notAfter'.split()),
}


def wire_hash(raw):
    return hashlib.sha256(raw).hexdigest()


def hex_value(value, size=64, *, nonzero=False):
    if type(value) is not str or not re.fullmatch(r'[0-9a-f]{%d}' % size, value) or (nonzero and int(value, 16) == 0):
        raise ValueError('Provider identifier/digest encoding')


def framing(kind, raw):
    return ('email2/provider-' + kind + '/v0').encode() + b'\0' + struct.pack('>I', len(raw)) + raw


def parse(proof, kind):
    if type(proof) is bytes:
        proof = decode(proof, max_bytes=393216, max_depth=32)
    exact(proof, {'payload', 'signature'})
    if type(proof['payload']) is not str or len(proof['payload']) > 349528:
        raise ValueError('Proof payload budget')
    try:
        raw = base64.b64decode(proof['payload'], validate=True)
    except (ValueError, TypeError) as error:
        raise ValueError('Provider proof base64') from error
    if base64.b64encode(raw).decode() != proof['payload']:
        raise ValueError('Canonical provider base64')
    hex_value(proof['signature'], 128)
    value = decode(raw, max_bytes=262144, max_depth=32)
    exact(value, FIELDS[kind])
    if value['profile'] != PROFILE or value['purpose'] != 'provider-' + kind:
        raise ValueError('Provider proof purpose/profile')
    integer(value['notBefore']);integer(value['notAfter'])
    if value['notBefore'] > value['notAfter']:
        raise ValueError('Provider proof interval')
    hex_value(value['request'], 32, nonzero=True)
    if kind == 'pair-approval':
        for key in ('preparation', 'link'):
            hex_value(value[key], 32, nonzero=True)
        for key in ('nonce', 'delegationDigest', 'family', 'initiatorKey', 'targetKey'):
            hex_value(value[key])
    else:
        for key in ('approvalDigest', 'grant'):
            hex_value(value[key])
        if kind == 'role-credential':
            for key in ('credential', 'nonce', 'account'):
                hex_value(value[key])
        if type(value['role']) is not str or value['role'] not in OPERATIONS:
            raise ValueError('Exact credential role')
        endpoint(value['device'])
    return raw, value, bytes.fromhex(proof['signature'])


def signed(kind, raw, key):
    proof = dict(payload=base64.b64encode(raw).decode(), signature=key.sign(framing(kind, raw)).hex())
    parse(proof, kind)
    return proof


def verify(kind, raw, signature, key):
    hex_value(key)
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(key)).verify(signature, framing(kind, raw))
    except InvalidSignature as error:
        raise ValueError('Provider proof signature') from error


@dataclass(frozen=True)
class ActiveLink:
    account: str
    link: str
    family: str
    mailbox: str
    delegation: str
    service: str
    prefix: str
    target: dict
    not_before: int
    not_after: int
    active: bool = True


@dataclass(frozen=True)
class ApprovedPair:
    payload: bytes
    signature: bytes


def pair_config(value):
    import json
    c = validate_configuration(json.dumps(value['configuration'], separators=(',', ':')).encode())
    if c['role'] != 'target':
        raise ValueError('Pair approval must carry target configuration')
    refs = {role: dict(c[role], state=c[role + 'State'], binding=c[role + 'Binding'], key=value[role + 'Key']) for role in OPERATIONS}
    for ref in refs.values():
        endpoint(ref)
    if c['initiator'] == c['target']:
        raise ValueError('Distinct pair devices required')
    return c, refs


def active_pair(pair, link, identities, *, time, trust_policy):
    if not isinstance(pair, ApprovedPair) or not isinstance(link, ActiveLink) or link.active is not True:
        raise ValueError('Trusted active link and approved pair required')
    _, value, _ = parse(dict(payload=base64.b64encode(pair.payload).decode(), signature=pair.signature.hex()), 'pair-approval')
    c, refs = pair_config(value)
    verify('pair-approval', pair.payload, pair.signature, refs['target']['key'])
    if (value['link'], value['family'], value['mailbox'], value['delegationDigest'], c['account'], c['service'], c['prefix'], refs['target']) != (link.link, link.family, link.mailbox, link.delegation, link.account, link.service, link.prefix, link.target):
        raise ValueError('Approval must match retained linked account/delegation')
    current(c, time, c['limits'])
    if not c['notBefore'] <= value['notBefore'] <= value['notAfter'] <= c['notAfter']:
        raise ValueError('Approval interval outside grant')
    if not link.not_before <= time[0] <= time[1] <= link.not_after or not link.not_before <= c['notBefore'] <= c['notAfter'] <= link.not_after:
        raise ValueError('Link/family lifetime')
    if trust_policy not in ('allow-unverified', 'require-verification'):
        raise ValueError('Explicit identity trust policy required')
    clock = dict(earliest=str(time[0]), latest=str(time[1]))
    with authority_snapshot(identities):
        for ref in refs.values():
            auth = authorize(identities, ref, 'receive', clock, trust_policy)
            if not auth['before'] <= c['notBefore'] <= c['notAfter'] <= auth['after']:
                raise ValueError('Retained pair binding lifetime exceeded')
    return value, c, refs


def approve_pair(proof, link, identities, *, prepared_payload, time, trust_policy):
    raw, value, signature = parse(proof, 'pair-approval')
    if raw != prepared_payload:
        raise ValueError('Exact retained preparation required')
    pair = ApprovedPair(raw, signature)
    _, c, _ = active_pair(pair, link, identities, time=time, trust_policy=trust_policy)
    current(value, time, c['limits'])
    if not c['notBefore'] <= value['notBefore'] <= value['notAfter'] <= c['notAfter']:
        raise ValueError('Approval interval outside grant')
    return pair


def role_config(pair, link, identities, role, *, time, trust_policy, grant_active=False):
    if grant_active is not True or role not in OPERATIONS:
        raise ValueError('Trusted active grant and exact role required')
    _, c, _ = active_pair(pair, link, identities, time=time, trust_policy=trust_policy)
    return dict(c, role=role, operations=OPERATIONS[role][:])


def role_request(proof, pair, link, identities, *, time, trust_policy, grant_active=False):
    raw, value, signature = parse(proof, 'role-request')
    c = role_config(pair, link, identities, value['role'], time=time, trust_policy=trust_policy, grant_active=grant_active)
    approval = decode(pair.payload, max_bytes=262144, max_depth=32)
    _, refs = pair_config(approval)
    for field, expected in [('approvalDigest', wire_hash(pair.payload)), ('grant', c['grant']), ('service', c['service']), ('prefix', c['prefix']), ('device', refs[value['role']])]:
        if value[field] != expected:
            raise ValueError('Role request differs from approved pair')
    current(value, time, c['limits'])
    if not c['notBefore'] <= value['notBefore'] <= value['notAfter'] <= c['notAfter']:
        raise ValueError('Role request lifetime')
    verify('role-request', raw, signature, refs[value['role']]['key'])
    return value


def credential_proof(proof, request, pair, link, identities, *, retained_challenge, time, trust_policy, grant_active=False):
    asked = role_request(request, pair, link, identities, time=time, trust_policy=trust_policy, grant_active=grant_active)
    raw, value, signature = parse(proof, 'role-credential')
    if raw != retained_challenge:
        raise ValueError('Exact retained credential challenge required')
    for field in ('request', 'approvalDigest', 'grant', 'service', 'prefix', 'role', 'device'):
        if value[field] != asked[field]:
            raise ValueError('Credential challenge/request mismatch')
    if value['account'] != link.account or not asked['notBefore'] <= value['notBefore'] <= value['notAfter'] <= asked['notAfter']:
        raise ValueError('Credential account/lifetime')
    c = role_config(pair, link, identities, value['role'], time=time, trust_policy=trust_policy, grant_active=grant_active)
    current(value, time, c['limits'])
    verify('role-credential', raw, signature, value['device']['key'])
    return c
