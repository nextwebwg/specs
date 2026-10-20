"""Current signed assertion7 exchange support, separate from voting authority."""
import json
from ordering_certificates import encode
from passive_discovery import decode_passive_discovery
from passive_discovery_verify import verify_passive_discovery
from initial_roster import credential
from mls_receive import LockedIdentity
from application_support import supports

def initialize(db):
    db.execute('CREATE TABLE IF NOT EXISTS qo_signed_exchange_support(group_id TEXT NOT NULL,identity TEXT NOT NULL,wrapper BLOB NOT NULL,digest TEXT NOT NULL,PRIMARY KEY(group_id,identity))')

def check(identity,wrapper,context,witness,*,time):
    d=decode_passive_discovery(encode(wrapper));a=d['assertion'];v=a['value']
    if v['version']!='7' or v['orderingExchanges']!=[{'format':'quorum-exchange-experiment','version':'1'}] or not supports(v,context['application'],'endpoint-quorum-v0'):raise ValueError('Exact signed exchange1 support')
    if any(v[k]!=witness[k] for k in ('principal','device','state','binding')):raise ValueError('Witness assertion binding')
    binding=next((b['value'] for b in d['identity']['bindings'] if b['digest']==v['binding']),None)
    if binding is None or binding['signingKey']!=witness['signingKey']:raise ValueError('Witness assertion key')
    locked=LockedIdentity(identity)
    if verify_passive_discovery(encode(wrapper),locked,time=time,trust_policy='allow-unverified').get('status')!='snapshot-authorized-unverified':raise ValueError('Current signed exchange support')
    status=locked.check_device(bytes.fromhex(credential(v)),bytes.fromhex(witness['signingKey']),role='send',time=time,trust_policy='allow-unverified')
    if status.get('status')!='authorized-unverified':raise ValueError('Current witness send role')
    return a['digest']

def shape(wrappers,context):
    if not isinstance(wrappers,list):raise ValueError('Complete witness assertions')
    witnesses=context['ordering']['witnesses'];pairs=[(w['principal'],w['device']) for w in witnesses]
    decoded=[decode_passive_discovery(encode(w))['assertion']['value'] for w in wrappers]
    actual=[(v['principal'],v['device']) for v in decoded]
    if actual!=sorted(set(actual)) or actual!=pairs:raise ValueError('Complete exact witness assertion coverage')
    if any(v['version']!='7' for v in decoded):raise ValueError('Witness assertion7 required')
    return witnesses

def complete(identity,wrappers,context,*,time):
    witnesses=shape(wrappers,context)
    return [check(identity,wrapper,context,witness,time=time) for wrapper,witness in zip(wrappers,witnesses)]

def retain_locked(db,group,wrappers,digests):
    if not db.in_transaction:raise ValueError('Caller transaction required')
    for wrapper,digest in zip(wrappers,digests):
        v=decode_passive_discovery(encode(wrapper))['assertion']['value']
        db.execute('INSERT INTO qo_signed_exchange_support VALUES(?,?,?,?) ON CONFLICT(group_id,identity) DO UPDATE SET wrapper=excluded.wrapper,digest=excluded.digest',(group,credential(v),encode(wrapper),digest))

def current(group,*,time,context=None):
    state=group.live()[1]['snapshot'];context=context or json.loads(bytes.fromhex(state['context']));result=[]
    for witness in context['ordering']['witnesses']:
        row=group.db.execute('SELECT wrapper FROM qo_signed_exchange_support WHERE group_id=? AND identity=?',(state['group'],credential(witness))).fetchone()
        if row is None:
            # A separately authenticated Add observation is capability evidence,
            # not a grant of witness membership. Complete rechecks authority.
            row=group.db.execute('SELECT wrapper FROM qo_join_support WHERE identity=?',(credential(witness),)).fetchone()
        if row is None:raise ValueError('Signed exchange support required')
        result.append(json.loads(row[0]))
    complete(group.identity,result,context,time=time);return result

def historical_edge(edge):
    """Authenticate complete historical supplements without renewing their expiry.

    Final admission separately requires current member/witness evidence. Forwarded
    historical carriers must pass the receiver's current checks before effects.
    """
    import base64
    from provider_control import exact,verify_signature
    from ordering_carrier import package,select_object
    exact(edge,{'candidate','proof','applicationAssertions','witnessAssertions'})
    proof=base64.b64decode(edge['proof'],validate=True)
    carrier=encode(dict(version='2',purpose='quorum-control-experiment',candidate=edge['candidate'],proof=proof.hex(),applicationAssertions=edge['applicationAssertions'],witnessAssertions=edge['witnessAssertions']))
    select_object(package(carrier))
    plan=edge['candidate']['plan'];context=json.loads(bytes.fromhex(plan['result']['context']));members={m['identity']:m['key'] for m in plan['result']['members']}
    expected=plan['welcomes'][0]['recipients'] if plan['welcomes'] else []
    actual=[credential(decode_passive_discovery(encode(w))['assertion']['value']) for w in edge['applicationAssertions']]
    if actual!=expected:raise ValueError('Historical Add assertion coverage')
    for wrapper in edge['applicationAssertions']+edge['witnessAssertions']:
        d=decode_passive_discovery(encode(wrapper));v=d['assertion']['value'];key=members.get(credential(v))
        if v['version']!='7' or key is None or not supports(v,context['application'],'endpoint-quorum-v0'):raise ValueError('Historical supplemental support')
        verify_signature(d['assertion']['octets'],d['signature'].hex(),key,b'email-next/passive-discovery/v7\0')
    for wrapper,witness in zip(edge['witnessAssertions'],context['ordering']['witnesses']):
        v=decode_passive_discovery(encode(wrapper))['assertion']['value']
        if any(v[k]!=witness[k] for k in ('principal','device','state','binding')):raise ValueError('Historical witness binding')
