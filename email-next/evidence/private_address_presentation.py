"""Address-metadata component probe, not full envelope/operation acceptance.

The caller supplies independently authenticated MLS context/sender/audience. This
module does not admit groups, accept identity state, render HTML or authorize a
route. Its candidate result must pass the remaining application gates before UI
use. Association rows below are trusted local fixture inputs, never message flags.
"""
import re
from event_encoding import decode_event
from passive_discovery import uint64
from email2_mailbox import validate as mailbox
from suite_modules import modules_for, application, MODULES

APPLICATION = application(MODULES)
ENVELOPE_FIELDS = set('version purpose event conversation principal audience operation disclosures presentation'.split())


def exact(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError('Exact object members required')


def principal(value):
    if not isinstance(value, str) or not re.fullmatch(r'enp0:[0-9a-f]{64}', value) or value == 'enp0:' + '0'*64:
        raise ValueError('Nonzero principal required')
    return value


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{32}', value) or value == '0'*32:
        raise ValueError('Nonzero ObjectId required')


def principal_array(value, *, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError('Principal array required')
    for item in value:
        principal(item)
    if len(set(value)) != len(value):
        raise ValueError('Duplicate principal')


def inspect_metadata(octets):
    """Preserve original bytes and validate only envelope/address metadata shape.

    Operation semantics, disclosure schemas and MIME/resource acceptance remain
    owning validators' work. No value returned here authorizes an effect.
    """
    parsed = decode_event(octets)
    event = parsed['value']
    exact(event, ENVELOPE_FIELDS)
    if event['version'] != '4' or event['purpose'] != 'contribution':
        raise ValueError('Envelope4 contribution required')
    identifier(event['event']); identifier(event['conversation'])
    author = principal(event['principal'])
    principal_array(event['audience'], nonempty=True)
    if author not in event['audience'] or not isinstance(event['operation'], dict) or not isinstance(event['disclosures'], list):
        raise ValueError('Envelope metadata')
    p = event['presentation']
    exact(p, ['subject', 'authoredAt', 'to', 'cc', 'addresses'])
    if not isinstance(p['subject'], str) or any(ord(c)<32 or 127<=ord(c)<=159 for c in p['subject']):
        raise ValueError('Subject control characters')
    if p['authoredAt'] != '':
        uint64(p['authoredAt'])
    principal_array(p['to']); principal_array(p['cc'])
    if set(p['to']) & set(p['cc']) or set([author] + p['to'] + p['cc']) != set(event['audience']):
        raise ValueError('Principal roles/audience')
    a = p['addresses']
    exact(a, ['from', 'to', 'cc'])
    identities = {mailbox(a['from']): author}
    seen_recipients = set()
    for role in ['to', 'cc']:
        if not isinstance(a[role], list):
            raise ValueError('Address array required')
        order = []
        for entry in a[role]:
            exact(entry, ['principal', 'mailbox'])
            who, address = principal(entry['principal']), mailbox(entry['mailbox'])
            if address in seen_recipients:
                raise ValueError('Duplicate recipient address')
            seen_recipients.add(address)
            if address in identities and identities[address] != who:
                raise ValueError('One mailbox cannot name different principals')
            identities[address] = who
            if who not in order:
                order.append(who)
        if order != p[role]:
            raise ValueError('Address order/role projection')
    return dict(state='candidate-address-metadata', octets=octets, event=event)


def check_context(parsed, context, *, author, audience):
    """Compare configured authenticated dependencies; not context-schema validation."""
    event = parsed['event']
    principal_array(audience, nonempty=True)
    if (context.get('version') != '8' or context.get('purpose') != 'conversation-context'
            or context.get('conversation') != event['conversation']
            or principal(author) != event['principal'] or set(audience) != set(event['audience'])):
        raise ValueError('Authenticated context mismatch')
    modules_for(context.get('application'))
    if event['operation'].get('kind') not in context['application']['operations']:
        raise ValueError('Operation absent from selected agreement')
    return parsed


def assurance_rows(parsed, associations):
    """Only for a caller that has completed full application acceptance.

    This pure component never maps claimed mailboxes to contact names. A matching
    local association supplies its own recorded assurance, not ownership inferred
    from encryption. Source rows are configured fixtures, not verified evidence.
    """
    for address, row in associations.items():
        mailbox(address)
        exact(row, ['principal', 'assurance'])
        principal(row['principal'])
        if row['assurance'] not in ['unverified', 'human-confirmed']:
            raise ValueError('Explicit local association assurance required')
    event = parsed['event']; a = event['presentation']['addresses']
    def describe(who, address):
        row = associations.get(address)
        state = 'author-stated-address' if row is None else ('address-conflict' if row['principal'] != who else 'matched-local-association')
        return dict(principal=who, mailbox=address, state=state,
                    assurance=row['assurance'] if state == 'matched-local-association' else 'none')
    return dict(author=describe(event['principal'], a['from']),
                to=[describe(x['principal'], x['mailbox']) for x in a['to']],
                cc=[describe(x['principal'], x['mailbox']) for x in a['cc']])
