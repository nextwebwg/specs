"""Transaction-scoped local mailbox selection; never independent ownership proof."""
from passive_discovery import mailbox_syntax,uint64,hexadecimal

def targets(value,recipients):
    if value is None:return None
    if not isinstance(value,list) or len(value)!=len(recipients):raise ValueError('Association target coverage')
    seen=set();result=[]
    for item in value:
        if not isinstance(item,dict) or set(item)!={'mailbox','generation','principal','observation'}:raise ValueError('Association target shape')
        mailbox_syntax(item['mailbox']);uint64(item['generation'])
        if item['mailbox'] in seen or item['mailbox'] not in recipients:raise ValueError('Association target coverage')
        if not isinstance(item['principal'],str) or not item['principal'].startswith('enp0:') or not hexadecimal(item['principal'][5:],64):raise ValueError('Association principal')
        if not hexadecimal(item['observation'],64):raise ValueError('Association observation')
        seen.add(item['mailbox']);result.append(dict(item))
    return sorted(result,key=lambda x:x['mailbox'])

def check_locked(store,selected,metadata,time,trust_policy,*,verification=False):
    if not store.db.in_transaction:raise ValueError('Caller transaction required')
    if trust_policy!='allow-unverified' and not (trust_policy=='require-verification' and verification):raise ValueError('Association verification-required')
    result=[]
    for target in selected:
        current=store._current(target['mailbox'])
        if not current or not current['enabled'] or current['generation']!=target['generation'] or current['principal']!=target['principal']:raise ValueError('Changed mailbox association')
        evidence=store.eligible_observation_locked(target['mailbox'],target['observation'],time)
        if not evidence or evidence['assertion']['principal']!=target['principal']:raise ValueError('Ineligible mailbox observation')
        v=evidence['assertion'];credential=(b'email-next/device/v0\0'+bytes.fromhex(v['principal'][5:])+bytes.fromhex(v['device'][5:])).hex()
        if not any(m['identity']==credential and m['key']==evidence['key'] for m in metadata['members']):raise ValueError('Mailbox device outside group')
        verified=None
        if trust_policy=='require-verification':
            from human_verification import resolve_locked
            verified=resolve_locked(store.identity,target['mailbox'],target['principal'],time)
            if verified['status']!='verified-for-use':raise ValueError('Exact mailbox verification-required')
        result.append(dict(target,decision=current['decisionId'],device=v['device'],record=v['record'],key=evidence['key'],head=evidence['head'],binding=evidence['binding'],status='associated-unverified',**({'verification':verified} if verified else {})))
    return result
