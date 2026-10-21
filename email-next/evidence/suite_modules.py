"""Exact protected-operation module selection; no signature/admission authority.

Inputs are already decoded trusted selected device assertions at the caller's
boundary. This component validates their tuple grammar/closure only. A raw offer
or the result here never grants identity, package, membership or release rights.
"""
from itertools import combinations

CORE = frozenset(['attachment-message', 'message', 'reply-message', 'rich-message'])
MODULES = {'answers': frozenset(['answer','question']),
           'reactions': frozenset(['reaction','reaction-withdraw']),
           'corrections': frozenset(['edit'])}


def application(modules=()):
    names=frozenset(modules)
    if not names <= MODULES.keys():
        raise ValueError('Unknown module')
    return dict(envelopeVersion='4',payload='mime-suite-v0',
                operations=sorted(CORE.union(*(MODULES[name] for name in names))))


def modules_for(value, *, offer=False):
    fields={'envelopeVersion','payload','operations'} | ({'ordering'} if offer else set())
    if not isinstance(value,dict) or set(value)!=fields or value['envelopeVersion']!='4' or value['payload']!='mime-suite-v0':
        raise ValueError('Exact application required')
    if offer and value['ordering']!='endpoint-quorum-v0':
        raise ValueError('Exact ordering required')
    ops=value['operations']
    if not isinstance(ops,list) or any(not isinstance(op,str) for op in ops) or ops!=sorted(set(ops)) or not CORE<=set(ops):
        raise ValueError('Complete sorted protected core required')
    chosen=set();known=set(CORE)
    for name,block in MODULES.items():
        if set(ops)&block:
            if not block<=set(ops):
                raise ValueError('Partial module')
            chosen.add(name);known.update(block)
    if set(ops)!=known:
        raise ValueError('Unknown operation')
    return frozenset(chosen)


def offers(modules=()):
    names=sorted(frozenset(modules))
    # application() validates even the empty combination of an invalid input.
    application(names)
    result=[dict(application(subset),ordering='endpoint-quorum-v0')
            for size in range(len(names)+1) for subset in combinations(names,size)]
    return sorted(result,key=lambda item:tuple(item['operations']))


def validate_offers(value):
    if not isinstance(value,list) or not 1<=len(value)<=8:
        raise ValueError('Bounded offer array')
    supported=frozenset().union(*(modules_for(item,offer=True) for item in value))
    if value!=offers(supported):
        raise ValueError('Exact sorted module-subset closure required')
    return supported


def select(device_offers):
    if not isinstance(device_offers,list) or not device_offers:
        raise ValueError('Every selected device needs its signed offer')
    supported=[validate_offers(value) for value in device_offers]
    common=frozenset.intersection(*supported)
    return application(common)
