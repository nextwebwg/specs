"""Explicit context8/9 syntax; old public entry points remain8-only; no MLS, identity, invitation or mode-pin authority."""
from initial_roster import identifier
from passive_discovery import hexadecimal,uint64
from provider_control import exact,participant
from suite_modules import modules_for,STREAM,QUORUM


def principal(value):
    participant(dict(principal=value,device='end0:'+'1'*64))


def validate(value):
    return validate_version(value,version='8')


def validate_version(value,*,version):
    if version not in ('8','9'):raise ValueError('Explicit supported context version required')
    exact(value,set('version purpose conversation profile administrators application ordering delivery'.split()))
    if (value['version'],value['purpose'],value['profile'])!=(version,'conversation-context','mls-1-0001'):raise ValueError('Exact selected context required')
    identifier(value['conversation'])
    if version=='9':
        from reply_suite import _grammar
        _grammar(value['application'])
    else:modules_for(value['application'])
    admins=value['administrators']
    if not isinstance(admins,list) or not admins or any(not isinstance(p,str) for p in admins) or admins!=sorted(set(admins)):raise ValueError('Sorted unique administrators')
    for p in admins:principal(p)
    delivery=value['delivery']
    if not isinstance(delivery,dict):raise ValueError('Delivery object required')
    if delivery.get('kind')=='ordinary-v0':exact(delivery,{'kind'})
    elif delivery.get('kind')=='private-copy-v0':
        exact(delivery,{'kind','originator','recipient'})
        for key in ('originator','recipient'):principal(delivery[key])
        if delivery['originator']==delivery['recipient']:raise ValueError('Distinct private-copy principals')
    else:raise ValueError('Known delivery contract required')
    order=value['ordering']
    if not isinstance(order,dict):raise ValueError('Ordering object required')
    if order.get('kind')==STREAM:
        exact(order,{'kind','stream','owner'});identifier(order['stream'])
        owner=order['owner'];exact(owner,{'principal','device','signingKey','state','binding'})
        participant({k:owner[k] for k in ('principal','device')})
        if any(not hexadecimal(owner[k],64) for k in ('signingKey','state','binding')):raise ValueError('Exact birth key/binding references')
        if admins!=[owner['principal']]:raise ValueError('Sole owner-principal administration')
        if delivery['kind']=='private-copy-v0' and owner['principal'] not in (delivery['originator'],delivery['recipient']):raise ValueError('Private-copy owner outside role pair')
    elif order.get('kind')==QUORUM:
        exact(order,{'kind','generation','faultBound','witnesses'});uint64(order['generation']);f=uint64(order['faultBound']);w=order['witnesses']
        if not isinstance(w,list) or not w or len(w)<3*f+1:raise ValueError('Quorum fault-bound coverage')
        names=[]
        for witness in w:
            exact(witness,{'principal','device','signingKey','state','binding'});participant({k:witness[k] for k in ('principal','device')})
            if any(not hexadecimal(witness[k],64) for k in ('signingKey','state','binding')):raise ValueError('Witness references')
            names.append(witness['principal'])
        if names!=sorted(set(names)):raise ValueError('Unique ordered witness principals')
    else:raise ValueError('Unknown current ordering')
    return value


def check_private_stream_role(value, *, expected_delivery, established):
    """Trusted expected selection only; no proof, membership or installation.

    A caller must resolve retained accepted private-context provenance before
    passing established=True. Neither input is inferred from an invitation.
    """
    validate(value)
    if (type(established) is not bool or value['ordering']['kind']!=STREAM or
            value['delivery'].get('kind')!='private-copy-v0' or
            value['delivery']!=expected_delivery):raise ValueError('Expected private stream selection')
    if not established and value['ordering']['owner']['principal']!=value['delivery']['originator']:
        raise ValueError('Original private-copy source must be originator')
    return {'status':'private-role-selection-only'}


def check_roster(value, principals):
    """Exact context/roster consistency only, not native MLS or account proof."""
    return check_roster_version(value,principals,version='8')


def check_roster_version(value,principals,*,version):
    validate_version(value,version=version)
    if not isinstance(principals,list) or not principals:raise ValueError('Principal audience required')
    for p in principals:principal(p)
    if len(set(principals))!=len(principals):raise ValueError('Unique principal audience')
    if not set(value['administrators']).issubset(principals):raise ValueError('Administrator outside audience')
    delivery=value['delivery']
    if (delivery['kind']=='private-copy-v0' and
            set(principals)!={delivery['originator'],delivery['recipient']}):
        raise ValueError('Exact private-copy audience required')
    return {'status':'context-roster-only'}
