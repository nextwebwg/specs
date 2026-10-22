"""Public hosted wire decoding only; never account, identity or upload authority.

Expected service/owner/principal must come from the caller's trusted selection,
not these bytes. No OAuth, link verification, cursor authentication, snapshot
storage, effect execution or hosted-management-v1 conformance is implemented.
"""
import re
from event_encoding import decode_event, encode_event
from hosted_access import CREATE, parse, epoch, exact
from service_answer import identifier, reference


def owner_handle(value):
    return identifier(value, size=64)


def continuation(value):
    return (isinstance(value, str) and len(value) <= 2048 and
            all(0x21 <= ord(c) <= 0x7e for c in value))


def create_request(raw, *, owner, principal):
    value = decode_event(raw)['value']
    if (not exact(value, CREATE | {'replyTextLimit', 'ownerBinding', 'link', 'generation'}) or
            value['version'] != '2' or not owner_handle(owner) or
            not identifier(principal, 'enp0:', 64) or value['ownerBinding'] != owner or
            not identifier(value['link']) or not epoch(value['generation']) or
            value['generation'] == '0'):
        raise ValueError('Public create shape or expected owner')
    # Reuse the historical content grammar, not its configured authorization.
    # Only the returned original bytes, never this projection, identify a retry.
    historical = {key: item for key, item in value.items()
                  if key not in ('ownerBinding', 'link', 'generation')}
    historical['version'] = '1'
    parsed = parse(encode_event(historical), 'hosted-grant-create')
    if parsed['contribution']['principal'] != principal:
        raise ValueError('Public create principal mismatch')
    return {'status': 'wire-only', 'value': value, 'original': raw}


def feed_page(raw, *, service, collection, owner=None, grant=None):
    purposes = {'owners': 'hosted-owner-index', 'grants': 'hosted-grant-index',
                'replies': 'hosted-reply-events'}
    if collection not in purposes:
        raise ValueError('Unknown collection')
    keys = {'version', 'purpose', 'service', 'items', 'next', 'checkpoint'}
    if collection != 'owners':
        if not owner_handle(owner):
            raise ValueError('Expected owner required')
        keys.add('ownerBinding')
    if collection == 'replies':
        if not identifier(grant):
            raise ValueError('Expected grant required')
        keys.add('grant')
    value = decode_event(raw)['value']
    if (not exact(value, keys) or value['version'] != '1' or
            value['purpose'] != purposes[collection] or value['service'] != service or
            not isinstance(value['items'], list) or
            not continuation(value['next']) or not continuation(value['checkpoint']) or
            bool(value['next']) == bool(value['checkpoint'])):
        raise ValueError('Feed shape, correlation or completion sentinel')
    if collection != 'owners' and value['ownerBinding'] != owner:
        raise ValueError('Feed owner mismatch')
    if collection == 'replies' and value['grant'] != grant:
        raise ValueError('Feed grant mismatch')
    for item in value['items']:
        if collection == 'owners':
            valid = (exact(item, {'ownerBinding', 'principal'}) and
                     owner_handle(item['ownerBinding']) and
                     identifier(item['principal'], 'enp0:', 64))
        elif collection == 'grants':
            valid = (exact(item, {'grant', 'contribution', 'expiry', 'state'}) and
                     identifier(item['grant']) and reference(item['contribution']) and
                     item['state'] in ('created', 'revoked') and
                     (item['expiry'] == {'kind': 'none'} or
                      (exact(item['expiry'], {'kind', 'epoch'}) and
                       item['expiry']['kind'] == 'at' and epoch(item['expiry']['epoch']))))
        else:
            valid = (exact(item, {'version', 'purpose', 'service', 'grant', 'operation',
                                 'requestDigest', 'outcome', 'reason', 'attribution'}) and
                     item['version'] == '0' and item['purpose'] == 'hosted-holder-result' and
                     item['service'] == service and item['grant'] == grant and
                     identifier(item['operation']) and
                     isinstance(item['requestDigest'], str) and
                     re.fullmatch('[0-9a-f]{64}', item['requestDigest']) is not None and
                     item['outcome'] == 'confirmed' and item['reason'] == 'stored' and
                     item['attribution'] == 'grant-holder')
        if not valid:
            raise ValueError('Feed item shape or correlation')
    return {'status': 'wire-only', 'value': value, 'original': raw}
