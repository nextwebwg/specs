"""Exact protected-operation module selection; no signature/admission authority.

Inputs are already decoded trusted selected device assertions at the caller's
boundary. This component validates their tuple grammar/closure only. A raw offer
or the result here never grants identity, package, membership or release rights.
"""
from itertools import combinations

STREAM = 'sender-stream-v0'
QUORUM = 'endpoint-quorum-v0'
ORDERINGS = frozenset([STREAM,QUORUM])

CORE = frozenset(['attachment-message', 'message', 'reply-message', 'rich-message'])
MODULES = {'answers': frozenset(['answer','question']),
           'reactions': frozenset(['reaction','reaction-withdraw']),
           'corrections': frozenset(['edit']),
           'service-actions': frozenset(['service-question']),
           'hosted-replies': frozenset(['hosted-holder-observation'])}


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
    if offer and (not isinstance(value['ordering'],str) or value['ordering'] not in ORDERINGS):
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


def _closure(modules, ordering):
    names=sorted(frozenset(modules))
    application(names)
    return [dict(application(subset),ordering=ordering)
            for size in range(len(names)+1) for subset in combinations(names,size)]


def offers(modules=(), *, managed_modules=None):
    """Ordinary streams are required; managed support is independently optional."""
    result=_closure(modules,STREAM)
    if managed_modules is not None:result+=_closure(managed_modules,QUORUM)
    return sorted(result,key=lambda item:(item['ordering'],tuple(item['operations'])))


def validate_all_offers(value):
    if not isinstance(value,list) or not 1<=len(value)<=64:
        raise ValueError('Bounded offer array')
    supported={}
    for item in value:
        modules=modules_for(item,offer=True)
        supported[item['ordering']]=supported.get(item['ordering'],frozenset())|modules
    if STREAM not in supported:raise ValueError('Required ordinary-stream support')
    expected=offers(supported[STREAM],managed_modules=supported.get(QUORUM))
    if value!=expected:raise ValueError('Exact sorted per-ordering module-subset closure required')
    return supported


def validate_offers(value, *, ordering=STREAM):
    if not isinstance(ordering,str) or ordering not in ORDERINGS:raise ValueError('Unknown ordering')
    supported=validate_all_offers(value)
    if ordering not in supported:raise ValueError('Selected ordering absent')
    return supported[ordering]


def exchanges(value):
    supported=validate_all_offers(value)
    result=[dict(format='sender-stream-control',version='0')]
    if QUORUM in supported:result.insert(0,dict(format='quorum-exchange-experiment',version='2'))
    return result


def select(device_offers, *, ordering=STREAM):
    if not isinstance(device_offers,list) or not device_offers:
        raise ValueError('Every selected device needs its signed offer')
    supported=[validate_offers(value,ordering=ordering) for value in device_offers]
    return application(frozenset.intersection(*supported))
