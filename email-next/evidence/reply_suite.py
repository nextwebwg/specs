"""Reply-aware tuple selection from trusted decoded device evidence only.

Shared operation-block/closure grammar is reused without rewriting original
assertions or treating an older signature as a new one. No signature, package,
context, invitation, carrier, provider or release validation is supplied here.
"""
from suite_modules import application as old_application, offers as old_offers
from suite_modules import modules_for as old_modules_for
from suite_modules import validate_all_offers as old_validate_all_offers
from suite_modules import select as old_select, STREAM, QUORUM, MODULES


def _new(value):
    return dict(value, envelopeVersion='5', payload='mime-suite-v1')


def _grammar(value, *, offer=False):
    fields = {'envelopeVersion', 'payload', 'operations'} | ({'ordering'} if offer else set())
    if (not isinstance(value, dict) or set(value) != fields
            or value['envelopeVersion'] != '5' or value['payload'] != 'mime-suite-v1'):
        raise ValueError('Exact reply-aware application required')
    # This is an internal operation-grammar input, never an old assertion.
    grammar = dict(value, envelopeVersion='4', payload='mime-suite-v0')
    old_modules_for(grammar, offer=offer)
    return grammar


def application(modules=()):
    return _new(old_application(modules))


def offers(modules=(), *, managed_modules=None):
    return [_new(item) for item in old_offers(modules, managed_modules=managed_modules)]


def validate_all_offers(value):
    if not isinstance(value, list):
        raise ValueError('Exact offer array required')
    return old_validate_all_offers([_grammar(item, offer=True) for item in value])


def select(device_offers, *, ordering=STREAM):
    if not isinstance(device_offers, list) or not device_offers:
        raise ValueError('Every selected device needs original signed support')
    normalized = []
    for value in device_offers:
        validate_all_offers(value)
        normalized.append([_grammar(item, offer=True) for item in value])
    return _new(old_select(normalized, ordering=ordering))


def exchanges(value):
    supported = validate_all_offers(value)
    result = [dict(format='sender-stream-control', version='1')]
    if QUORUM in supported:
        result.insert(0, dict(format='quorum-exchange-experiment', version='3'))
    return result
