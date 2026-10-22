"""Reply-intent record/destination component, not event or sending authority.

Callers supply an independently accepted source and authenticated actor. This
module neither accepts envelope5 nor negotiates it; preserving that boundary
prevents a successful JSON check from becoming a send grant or graph edge.
"""
import re
from event_encoding import decode_event

TARGETS = frozenset(['message', 'attachment-message', 'rich-message', 'reply-message',
                     'question', 'service-question', 'hosted-holder-observation'])
NON_TARGETS = frozenset(['answer', 'reaction', 'reaction-withdraw', 'edit'])


def principal(value):
    if (not isinstance(value, str) or not re.fullmatch(r'enp0:[0-9a-f]{64}', value)
            or value == 'enp0:' + '0'*64):
        raise ValueError('Nonzero principal required')
    return value


def source_scope(author, audience):
    principal(author)
    if not isinstance(audience, list) or not audience:
        raise ValueError('Explicit source audience required')
    for who in audience:
        principal(who)
    if len(set(audience)) != len(audience) or author not in audience:
        raise ValueError('Distinct audience including author required')


def validate(record, *, operation, author, audience):
    source_scope(author, audience)
    if not isinstance(record, dict) or record.get('version') != '0':
        raise ValueError('Exact reply-intent version required')
    kind = record.get('kind')
    fields = {'version', 'kind'}
    if kind == 'discussion':
        fields |= {'participants', 'privateReplies'}
    elif kind not in ('private', 'none', 'not-applicable'):
        raise ValueError('Unknown reply intent')
    if set(record) != fields:
        raise ValueError('Exact reply-intent members required')
    if operation in TARGETS:
        if kind == 'not-applicable':
            raise ValueError('Reply target needs explicit written-reply intent')
    elif operation in NON_TARGETS:
        if kind != 'not-applicable':
            raise ValueError('Non-target operation cannot acquire a composer')
    else:
        raise ValueError('Unknown operation')
    if kind == 'discussion':
        people = record['participants']
        if not isinstance(people, list) or not people:
            raise ValueError('Nonempty participants required')
        for who in people:
            principal(who)
        if (people != sorted(set(people)) or author not in people
                or not set(people) <= set(audience)):
            raise ValueError('Canonical participants within source audience required')
        if type(record['privateReplies']) is not bool:
            raise ValueError('Boolean privateReplies required')
    return kind


def inspect_record(octets, *, operation, author, audience):
    parsed = decode_event(octets)
    validate(parsed['value'], operation=operation, author=author, audience=audience)
    return dict(state='candidate-reply-intent', octets=octets, record=parsed['value'])


def destination(record, *, operation, author, audience, actor, action):
    """Resolve a permitted local action; output is not live authorization.

    Private results need a separately authorized root/context. Discussion results
    still need target, membership, association, disclosure and release checks.
    """
    kind = validate(record, operation=operation, author=author, audience=audience)
    principal(actor)
    if actor not in audience:
        raise ValueError('Actor outside accepted source audience')
    if action == 'discussion':
        if kind != 'discussion' or actor not in record['participants']:
            raise ValueError('Discussion reply unavailable')
        return list(record['participants'])
    if action == 'private':
        if kind != 'private' and not (kind == 'discussion' and record['privateReplies']):
            raise ValueError('Private reply unavailable')
        return sorted({actor, author})
    raise ValueError('Explicit supported action required')
