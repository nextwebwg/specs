"""Strict request/result binding experiment; no HTTP, token or action authority.

A successful binding only compares bytes and fields. The caller still needs an
accepted action descriptor, authenticated transport and service authorization.
"""
import hashlib
import re
from event_encoding import decode_event

REQUEST_KEYS = {'version', 'purpose', 'submission', 'action', 'question',
                'principal', 'option', 'replaces'}
RESULT_KEYS = REQUEST_KEYS | {'service', 'requestDigest', 'outcome', 'reason'}
REASONS = {'pending': {'processing', 'reconciling'}, 'confirmed': {'applied'},
           'rejected': {'action-expired', 'option-not-allowed',
                        'replacement-not-current', 'not-applied'}}


def identifier(value, prefix='', size=32):
    return (isinstance(value, str) and value.startswith(prefix) and
            re.fullmatch('[0-9a-f]{%d}' % size, value[len(prefix):]) is not None and
            value[len(prefix):] != '0' * size)


def reference(value):
    return (isinstance(value, dict) and set(value) == {'principal', 'event', 'conversation'} and
            identifier(value['principal'], 'enp0:', 64) and
            identifier(value['event']) and identifier(value['conversation']))


def request_fields(value):
    return (value['version'] == '0' and identifier(value['submission']) and
            identifier(value['action']) and reference(value['question']) and
            identifier(value['principal'], 'enp0:', 64) and identifier(value['option']) and
            isinstance(value['replaces'], list) and len(value['replaces']) <= 1 and
            all(identifier(item) and item != value['submission'] for item in value['replaces']))


def decode_request(octets):
    parsed = decode_event(octets)
    value = parsed['value']
    if set(value) != REQUEST_KEYS or value['purpose'] != 'service-answer-submit' or not request_fields(value):
        raise ValueError('Invalid service request shape')
    return parsed


def bind_result(result_octets, request_octets, *, expected_service):
    """expected_service comes from a separately validated action descriptor.

    No receipt is trusted merely because its service string matches. Returned
    octets must retain their real transport provenance at the integration layer.
    """
    if not isinstance(expected_service, str) or not expected_service:
        raise ValueError('Expected separately validated service origin')
    request = decode_request(request_octets)['value']
    parsed = decode_event(result_octets)
    value = parsed['value']
    if set(value) != RESULT_KEYS or value['purpose'] != 'service-answer-result' or not request_fields(value):
        raise ValueError('Invalid service result shape')
    if not isinstance(value['outcome'], str) or value['outcome'] not in REASONS:
        raise ValueError('Invalid outcome')
    if not isinstance(value['reason'], str) or value['reason'] not in REASONS[value['outcome']]:
        raise ValueError('Invalid outcome reason')
    if value['service'] != expected_service or value['requestDigest'] != hashlib.sha256(request_octets).hexdigest():
        raise ValueError('Service or exact request digest mismatch')
    for key in REQUEST_KEYS - {'purpose'}:
        if value[key] != request[key]:
            raise ValueError('Request binding mismatch: ' + key)
    return {'status': 'bound-unverified', 'octets': parsed['octets'], 'value': value}
