"""Current signed final-roster support; never retroactive intermediate support."""
import hashlib
import json
from passive_discovery import decode_passive_discovery
from passive_discovery_verify import verify_passive_discovery
from application_support import supports
from application_agreement import profile
from mls_receive import LockedIdentity
import transition_support as support


def validate(coordinator,wrappers,final,initial,origin,time):
    ctx=json.loads(bytes.fromhex(final['context']))
    if ctx['version']=='1':
        if wrappers:raise ValueError('No application support in context1')
        return []
    old={(m['identity'],m['key']) for m in initial['members']};now={(m['identity'],m['key']) for m in final['members']}
    records=[];seen=set()
    for wrapper in wrappers:
        decoded=decode_passive_discovery(wrapper);a=decoded['assertion'];v=a['value']
        credential=(b'email-next/device/v0\0'+bytes.fromhex(v['principal'][5:])+bytes.fromhex(v['device'][5:])).hex()
        binding=next((b['value'] for b in decoded['identity']['bindings'] if b['digest']==v['binding']),None)
        if binding is None:raise ValueError('Support binding')
        pair=credential,binding['signingKey']
        if pair not in now-old or pair in seen:raise ValueError('Exact final added support coverage')
        seen.add(pair)
        checked=verify_passive_discovery(wrapper,LockedIdentity(coordinator.identity),time=time,trust_policy='allow-unverified')
        if checked.get('status')!='snapshot-authorized-unverified':raise ValueError('Current final support authority')
        if not supports(v,ctx['application'],'designated-member-v0'):raise ValueError('Final selected profile support')
        records.append(dict(credential=pair[0],key=pair[1],wrapper=wrapper.hex(),head=checked.get('head'),assertion=a['digest']))
    for member in final['members']:
        pair=member['identity'],member['key']
        if pair in seen:continue
        if coordinator.receiver.application_agreement.resolve(final['group'],[member],instance=origin)!=ctx['application']:raise ValueError('Actual final application support required')
    return records


def install(coordinator,records,final,origin,time,chain):
    db=coordinator.db;ctx=json.loads(bytes.fromhex(final['context']));application=ctx.get('application')
    for item in records:
        credential,key=item['credential'],item['key'];group=final['group']
        admission=support.episode(db,group,credential,key)
        record=dict(group=group,credential=credential,key=key,context=final['context'],episode=admission,kind='signed-current-confirmation',epoch=final['epoch'],predecessor=final['predecessor'],time=dict(time),wrapper=item['wrapper'],application=application,confirmation='atomic-remediation-final',chain=chain)
        raw=support.canonical(record);ident=hashlib.sha256(raw).hexdigest()
        db.execute('INSERT OR IGNORE INTO mls_support_records VALUES(?,?)',(ident,raw))
        db.execute('INSERT INTO mls_support_selected VALUES(?,?,?) ON CONFLICT(group_id,credential) DO UPDATE SET record=excluded.record',(group,credential,ident))
        db.execute('INSERT INTO mls_support_episodes VALUES(?,?,?,?,?)',(group,credential,key,admission,ident))
        encoded=profile(application)
        if origin:
            previous=db.execute('SELECT signature_key,application FROM mls_instance_agreements WHERE instance=? AND credential=?',(origin,credential)).fetchone()
            if previous and previous!=(key,encoded):raise ValueError('Immutable support conflict')
            db.execute('INSERT OR IGNORE INTO mls_instance_agreements VALUES(?,?,?,?,?,?)',(origin,credential,key,encoded,'signed-remediation-current',chain))
        else:
            previous=db.execute('SELECT signature_key,application FROM mls_application_agreement WHERE group_id=? AND credential=?',(group,credential)).fetchone()
            if previous and previous!=(key,encoded):raise ValueError('Immutable support conflict')
            db.execute('INSERT OR IGNORE INTO mls_application_agreement VALUES(?,?,?,?)',(group,credential,key,encoded))
            db.execute('INSERT OR IGNORE INTO mls_application_agreement_provenance VALUES(?,?,?,?)',(group,credential,'signed-remediation-current',chain))
