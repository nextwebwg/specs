"""Configuration2 bytes and ordinary-selection syntax candidates only.

No pairing/part signature, age, identity, historical managed proof, complete
configuration, transaction, trust reconciliation, admission or send readiness.
Original bytes are preserved; old context/chunk entry points remain version-fixed.
"""
import hashlib
from event_encoding import decode_event
from pairing_configuration_v1 import (CHUNK, manifest_version, frame_chunk_version,
                                      assemble_version)
from passive_discovery import canonical_base64
from suite_context import principal, check_roster_version

BINDINGS = {'email2-conversation-v0': ('8', '5', '8'),
            'mail-conversation-v1': ('9', '6', '9')}
MAGIC = b'EML2CFG2'


def manifest(raw, *, max_bytes, max_parts):
    return manifest_version(raw, max_bytes=max_bytes, max_parts=max_parts, version='2')


def frame_chunk(index, count, data):
    return frame_chunk_version(index, count, data, version='2')


def assemble(raw_manifest, parts, *, max_bytes, max_parts):
    return assemble_version(raw_manifest, parts, max_bytes=max_bytes, max_parts=max_parts, version='2')


def inspect_ordinary_selection(raw, *, own_principal):
    principal(own_principal)
    record = decode_event(raw)['value']
    if (set(record) != {'kind', 'agreement', 'conversation', 'principals', 'delivery', 'context', 'contextDigest'}
            or record['kind'] != 'ordinary-v0' or not isinstance(record['agreement'], str)
            or record['agreement'] not in BINDINGS):
        raise ValueError('Exact configuration2 ordinary selection required')
    original = canonical_base64(record['context'])
    if hashlib.sha256(original).hexdigest() != record['contextDigest']:
        raise ValueError('Original context commitment required')
    context = decode_event(original)['value']
    version, _, _ = BINDINGS[record['agreement']]
    people = record['principals']
    if (not isinstance(people, list) or not people
            or any(not isinstance(who, str) for who in people)
            or people != sorted(set(people)) or own_principal not in people):
        raise ValueError('Canonical audience including paired account required')
    check_roster_version(context, people, version=version)
    if (context['ordering']['kind'] != 'sender-stream-v0'
            or context['conversation'] != record['conversation']
            or context['delivery'] != record['delivery']):
        raise ValueError('Exact ordinary conversation and delivery required')
    return dict(status='ordinary-selection-syntax-only', original=raw,
                original_context=original, agreement=record['agreement'])
