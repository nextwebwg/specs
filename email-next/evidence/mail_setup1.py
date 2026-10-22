"""Exact mailbox-setup1 signed records and assertion9 candidate checks.

No MIME/DKIM/envelope/association, local issuance/custody/journal, sealed-control-v1,
MLS invitation/admission, private content release or complete mailbox journey.
"""
from mail_setup import decode_version, verify_version


def decode(raw, kind):
    return decode_version(raw, kind, version='1')


def verify(raw, kind, identity, binary, *, time, trust_policy, request=None):
    return verify_version(raw, kind, identity, binary, time=time,
                          trust_policy=trust_policy, request=request, version='1')


def live_candidate(raw, request, identity, binary, *, time, started, maximum_age,
                   expected_source, expected_target):
    """Check signed evidence and age; trusted retained-attempt facts are external.

    This does not create/resolve a durable attempt, check its cancellation or
    policy generation, validate mailbox/sealed carriage, or authorize release.
    Current identity0 fixtures support the bounded component only.
    """
    from passive_discovery import uint64

    if type(maximum_age) is not int or not 0 < maximum_age < 2**64:
        raise ValueError('Explicit positive maximum age required')
    if not isinstance(started, dict) or set(started) != {'earliest', 'latest'}:
        raise ValueError('Original creation interval required')
    beginning, end = uint64(started['earliest']), uint64(started['latest'])
    if beginning > end:
        raise ValueError('Ordered original creation interval required')
    for expected in [expected_source, expected_target]:
        if not isinstance(expected, dict) or set(expected) != {'principal', 'device'}:
            raise ValueError('Exact independently selected endpoint required')
    original = verify(request, 'request', identity, binary, time=time,
                      trust_policy='allow-unverified')
    candidate = verify(raw, 'response', identity, binary, time=time,
                       trust_policy='allow-unverified', request=request)
    for actual, expected in [(original['actor'], expected_source),
                             (candidate['actor'], expected_target)]:
        if {name: actual[name] for name in ('principal', 'device')} != expected:
            raise ValueError('Independently selected source/target required')
    before, after = uint64(original['record']['notBefore']), uint64(original['record']['notAfter'])
    if not before <= beginning <= end <= after:
        raise ValueError('Creation interval outside original request')
    if uint64(time['earliest']) < beginning or uint64(time['latest']) < end:
        raise ValueError('Clock moved backward since original attempt')
    if uint64(time['latest']) - beginning > maximum_age:
        raise ValueError('Live attempt outside original age window')
    current = identity.current_state(candidate['actor']['principal'])
    if current['conflicted'] or current['head'] != candidate['actor']['state']:
        raise ValueError('Live response requires exact current target head')
    return dict(status='mailbox-live-response-candidate-only',
                requestDigest=original['payloadDigest'],
                responseDigest=candidate['payloadDigest'],
                actor=candidate['actor'], mailbox_verified=False)
