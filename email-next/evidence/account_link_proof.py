"""Shared account-link proof checks with trusted module/account preparations.

No OAuth authentication, mailbox membership discovery, descriptor DNS validation,
first-contact pin installation, challenge consumption or link activation is supplied.
Those service-journal/account facts must be authoritative before this check.
"""
import base64
from dataclasses import dataclass
import hashlib

from email2_mailbox import selected_domain, validate as validate_mailbox
from history_transfer import authorize, authority_snapshot, endpoint
from provider_control import decode, exact, integer
from provider_discovery import bounded, current, native_profile
from provider_grants import PROFILE, hex_value, verify

PURPOSES = {'provider': 'provider-service-discovery',
            'relay': 'relay-service-discovery', 'bootstrap': 'bootstrap-service-discovery'}
LINK_SCOPES = {'provider': 'mail.provider.link', 'relay': 'mail.relay.link',
               'bootstrap': 'mail.setup.link'}
FIELDS = set('profile purpose challenge request nonce delegationDigest service account family mailbox device notBefore notAfter'.split())


@dataclass(frozen=True)
class PreparedLink:
    module: str
    token_module: str
    descriptor: bytes
    payload: bytes
    account: str
    family: str
    scopes: tuple
    not_before: int
    not_after: int
    active: bool = True


def account_link_proof(proof, prepared, identities, *, time, trust_policy):
    if trust_policy not in ('allow-unverified', 'require-verification'):
        raise ValueError('Explicit account-link identity policy required')
    if not isinstance(prepared, PreparedLink) or prepared.active is not True:
        raise ValueError('Trusted active account-link preparation required')
    if prepared.module not in PURPOSES or prepared.token_module != prepared.module:
        raise ValueError('Exact authenticated module required')
    scopes = native_profile(prepared.module, list(prepared.scopes))
    if LINK_SCOPES[prepared.module] not in scopes:
        raise ValueError('Module account-link scope required')
    if (type(time) is not tuple or len(time) != 2 or
            not all(type(t) is int for t in time)):
        raise ValueError('Credible clock interval required')
    for t in (*time, prepared.not_before, prepared.not_after):
        integer(t)
    if not prepared.not_before <= time[0] <= time[1] <= prepared.not_after:
        raise ValueError('Current account/family interval required')
    descriptor = bounded(prepared.descriptor)
    if descriptor.get('purpose') != PURPOSES[prepared.module] or descriptor.get('version') != '0':
        raise ValueError('Module descriptor purpose required')
    current(descriptor, time)
    exact(proof, {'payload', 'signature'})
    if type(proof['payload']) is not str or len(proof['payload']) > 349528:
        raise ValueError('Account-link proof budget')
    try:
        raw = base64.b64decode(proof['payload'], validate=True)
    except (ValueError, TypeError) as error:
        raise ValueError('Account-link base64') from error
    if base64.b64encode(raw).decode() != proof['payload']:
        raise ValueError('Canonical account-link base64')
    hex_value(proof['signature'], 128)
    value = decode(raw, max_bytes=262144, max_depth=32)
    exact(value, FIELDS)
    if value['profile'] != PROFILE or value['purpose'] != 'provider-account-link':
        raise ValueError('Shared account-link profile and purpose required')
    for name in ['challenge', 'request']:
        hex_value(value[name], 32, nonzero=True)
    for name in ['nonce', 'delegationDigest', 'account', 'family']:
        hex_value(value[name])
    integer(value['notBefore']); integer(value['notAfter'])
    endpoint(value['device']); validate_mailbox(value['mailbox'])
    if raw != prepared.payload:
        raise ValueError('Original retained account-link challenge required')
    if (value['delegationDigest'] != hashlib.sha256(prepared.descriptor).hexdigest() or
            value['service'] != descriptor['service'] or
            (value['account'], value['family']) != (prepared.account, prepared.family)):
        raise ValueError('Exact module delegation/account/family required')
    if prepared.module != 'relay' and selected_domain(value['mailbox']) != descriptor['domain']:
        raise ValueError('Selected mailbox-domain delegation required')
    if not prepared.not_before <= value['notBefore'] <= time[0] <= time[1] <= value['notAfter'] <= prepared.not_after:
        raise ValueError('Original account-link interval required')
    verify('account-link', raw, bytes.fromhex(proof['signature']), value['device']['key'])
    clock = dict(earliest=str(time[0]), latest=str(time[1]))
    with authority_snapshot(identities):
        auth = authorize(identities, value['device'], 'receive', clock, trust_policy)
        if not auth['before'] <= value['notBefore'] <= value['notAfter'] <= auth['after']:
            raise ValueError('Account-link device interval exceeded')
    return dict(module=prepared.module, requestDigest=hashlib.sha256(raw).hexdigest(),
                principal=value['device']['principal'], device=value['device']['device'])


def decode_account_status(raw, *, kind, preparation=None):
    """Parse exact inspection records; caller owns TLS/auth and reset reconciliation."""
    if kind == 'account':
        fields = {'profile', 'purpose', 'account', 'family', 'principal'}
        purpose = 'provider-account-state'
        if preparation is not None:
            raise ValueError('Account read has no preparation')
    elif kind == 'reset':
        fields = {'profile', 'purpose', 'preparation', 'outcome', 'account'}
        purpose = 'provider-account-reset-state'
        hex_value(preparation, 32, nonzero=True)
    else:
        raise ValueError('Explicit inspection route kind required')
    value = decode(raw, max_bytes=4194304, max_depth=32)
    exact(value, fields)
    if value['profile'] != PROFILE or value['purpose'] != purpose:
        raise ValueError('Inspection profile/purpose')
    hex_value(value['account'])
    if kind == 'account':
        hex_value(value['family'])
        principal = value['principal']
        if principal != '':
            if type(principal) is not str or not principal.startswith('enp0:'):
                raise ValueError('Linked principal')
            hex_value(principal[5:], 64, nonzero=True)
    else:
        if value['preparation'] != preparation:
            raise ValueError('Original reset preparation required')
        if value['outcome'] not in ('pending', 'completed', 'expired'):
            raise ValueError('Exact reset outcome required')
    return value
