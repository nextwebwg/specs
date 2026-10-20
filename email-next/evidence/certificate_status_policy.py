"""Synthetic status-policy experiment, NOT an OCSP or certificate validator.

Inputs model observations already authenticated by an established backend. This
module has no public service integration and must not accept message JSON as
backend evidence. Tests join these synthetic decisions to a real TLS socket;
that does not establish acquisition, signature validation, or platform compliance.
"""
from dataclasses import dataclass
from hashlib import sha256

MAX_AGE = 7 * 86400
FUTURE_SKEW = 300

@dataclass(frozen=True)
class Observation:
    peer_digest: str
    policy_revision: str
    certificate_expiry: int
    status: str = 'unavailable'
    this_update: int | None = None
    produced_at: int | None = None
    next_update: int | None = None
    staple_present: bool = False
    staple_required: bool = False
    exception: str = 'absent'
    nonce: str = 'not-requested'

@dataclass(frozen=True)
class Decision:
    permitted: bool
    status: str
    reason: str
    expires: int | None = None


def decide(observation, *, now, credible_clock, mode, policy_revision,
           resumed=False, max_age=MAX_AGE, future_skew=FUTURE_SKEW):
    """Evaluate synthetic observations; no certificate/signature authentication."""
    if mode not in ('web-compatible', 'fresh-status-required'):
        raise ValueError('unknown status mode')
    if type(now) is not int or type(max_age) is not int or not 0 < max_age <= MAX_AGE:
        raise ValueError('invalid time/age')
    if type(future_skew) is not int or not 0 <= future_skew <= FUTURE_SKEW:
        raise ValueError('invalid skew')
    def deny(reason):return Decision(False, 'held', reason)
    if credible_clock is not True:return deny('unreliable-clock')
    if observation.policy_revision != policy_revision:return deny('policy-changed')
    if now >= observation.certificate_expiry:return deny('certificate-expired')
    if observation.exception not in ('absent', 'valid', 'invalid'):raise ValueError('exception')
    if observation.exception == 'invalid':return deny('invalid-noRevAvail')
    if observation.status not in ('good', 'revoked', 'unknown', 'unavailable', 'invalid'):raise ValueError('status')
    if observation.status == 'revoked':return deny('revoked')
    if observation.staple_required and resumed:return deny('full-handshake-required')
    if observation.staple_required and not observation.staple_present:return deny('missing-required-staple')
    fresh = observation.status == 'good'
    if fresh:
        fields = (observation.this_update, observation.produced_at)
        if any(type(v) is not int for v in fields):fresh=False
        else:
            fresh = (observation.this_update <= now + future_skew
                     and observation.produced_at <= now + future_skew
                     and now - observation.this_update <= max_age)
            if observation.next_update is not None:
                fresh = fresh and type(observation.next_update) is int and observation.this_update <= observation.next_update and now < observation.next_update
        if observation.nonce == 'mismatch':fresh=False
    if observation.staple_present and not fresh:return deny('unacceptable-peer-staple')
    if observation.exception == 'valid':
        return Decision(True, 'exception', 'noRevAvail', observation.certificate_expiry)
    if fresh:
        # Maximum age is inclusive; integer-epoch expiry is the next second.
        expiry=min(observation.certificate_expiry, observation.this_update+max_age+1)
        if observation.next_update is not None:expiry=min(expiry,observation.next_update)
        return Decision(True,'good','fresh-evidence',expiry)
    if mode == 'fresh-status-required':return deny('status-not-established')
    return Decision(True,'indeterminate','compatible-status-unavailable',observation.certificate_expiry)


def send_fixture_probe(sock, observation, **policy):
    """Test-only same-socket gate. Sends a fixed noncredential marker, never HTTP.

    A peer hash ties synthetic fixture observations to the socket. It is NOT a
    substitute for an authenticated backend providing actual status evidence.
    """
    if sha256(sock.getpeercert(binary_form=True)).hexdigest() != observation.peer_digest:
        return Decision(False,'held','different-peer')
    result=decide(observation, resumed=sock.session_reused, **policy)
    if result.permitted:sock.sendall(b'STATUS-POLICY-PROBE')
    return result
