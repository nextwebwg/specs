"""Current exact signed tuple/package support for quorum admission."""
import json
from pathlib import Path
from event_encoding import encode_event
from passive_discovery import decode_passive_discovery
from passive_discovery_verify import verify_passive_discovery
from passive_discovery_package import validate_package
from initial_roster import credential
from application_agreement import profile
from application_support import supports
from mls_receive import LockedIdentity
from ordering_certificates import encode
from ordering_scope import decision_identity
from ordering_mls import candidate_id
import group_instances

def validate(group,wrapper,*,time):
    d=decode_passive_discovery(wrapper);a=d['assertion'];v=a['value'];context=json.loads(bytes.fromhex(group.live()[1]['snapshot']['context']))
    if not supports(v,context['application'],'endpoint-quorum-v0'):raise ValueError('Current quorum tuple')
    has_table=group.db.execute("SELECT 1 FROM sqlite_master WHERE name='qo_signed_exchange_support'").fetchone()
    signed_mode=bool(has_table and group.db.execute('SELECT 1 FROM qo_signed_exchange_support WHERE group_id=?',(group.live()[1]['snapshot']['group'],)).fetchone())
    if v['version']!=('7' if signed_mode else '6'):raise ValueError('Exact quorum lifecycle assertion version')
    checked=verify_passive_discovery(wrapper,LockedIdentity(group.identity),time=time,trust_policy='allow-unverified')
    if checked.get('status')!='snapshot-authorized-unverified':raise ValueError('Current joining assertion')
    binding=next(b['value'] for b in d['identity']['bindings'] if b['digest']==v['binding']);key=binding['signingKey']
    if a['key_package_octets'] is None or validate_package(a['key_package_octets'],principal=v['principal'],device=v['device'],accepted_signing_key=bytes.fromhex(key),earliest=time['earliest'],latest=time['latest'],executable=Path(group.binary).with_name('validate-discovery-package'))!={'status':'package-valid'}:raise ValueError('Current joining package')
    return credential(v),key,context['application'],d

def confirm(group,wrapper,*,time):
    group.db.execute('BEGIN IMMEDIATE')
    try:
        ident,key,application,d=validate(group,wrapper,time=time)
        group.db.execute('INSERT INTO qo_join_support VALUES(?,?,?) ON CONFLICT(identity) DO UPDATE SET key=excluded.key,wrapper=excluded.wrapper',(ident,key,wrapper));group.db.execute('COMMIT')
    except BaseException:
        if group.db.in_transaction:group.db.execute('ROLLBACK')
        raise

def current_added(group,members,*,time):
    records=[]
    for m in members:
        row=group.db.execute('SELECT key,wrapper FROM qo_join_support WHERE identity=?',(m['identity'],)).fetchone()
        if not row or row[0]!=m['key']:raise ValueError('Joining evidence required')
        ident,key,application,d=validate(group,row[1],time=time)
        if (ident,key)!=(m['identity'],m['key']):raise ValueError('Joining binding')
        records.append((m,row[1],application))
    return records

def install_support_locked(group,members,*,time,decision):
    current=group_instances.current(group.db,group.live()[1]['snapshot']['group'])
    for m,wrapper,application in current_added(group,members,time=time):
        group.db.execute('INSERT INTO mls_instance_agreements VALUES(?,?,?,?,?,?)',(current['instance'],m['identity'],m['key'],profile(application),'signed-quorum-admission',decision))

def retain_path_locked(db,path):
    import base64
    for edge in path:
        candidate=edge['candidate'];proof=base64.b64decode(edge['proof']);decision=decision_identity(candidate['plan']['scope'],candidate_id(candidate))
        carrier=encode(dict(version='2' if 'witnessAssertions' in edge else '0',purpose='quorum-control-experiment',candidate=candidate,proof=proof.hex(),**({k:edge[k] for k in ('applicationAssertions','witnessAssertions')} if 'witnessAssertions' in edge else {})))
        old=db.execute('SELECT carrier FROM qo_history WHERE decision=?',(decision,)).fetchone()
        if old:
            retained=json.loads(old[0])
            if retained['candidate']!=candidate:raise ValueError('Retained path conflict')
            from ordering_certificates import Proof
            from ordering_scope import scope_digest
            scope=candidate['plan']['scope'];keys={w['principal']+'|'+w['device']:w['signingKey'] for w in scope['ordering']['witnesses']}
            for raw in (proof,bytes.fromhex(retained['proof'])):
                parsed=Proof(raw,scope=scope_digest(scope),keys=keys,f=int(scope['ordering']['faultBound']))
                if parsed.result['kind']!='decision' or parsed.result['candidate']!=candidate_id(candidate):raise ValueError('Equivalent proof binding')
        db.execute('INSERT OR IGNORE INTO qo_history VALUES(?,?)',(decision,carrier))

def stage_carried_locked(group,wrappers,members,*,time):
    if not isinstance(wrappers,list):raise ValueError('Assertion coverage')
    decoded=[decode_passive_discovery(encode_event(w)) for w in wrappers]
    identities=[credential(d['assertion']['value']) for d in decoded]
    if identities!=sorted(set(identities)) or identities!=sorted(m['identity'] for m in members):raise ValueError('Exact added assertion coverage')
    keys={m['identity']:m['key'] for m in members}
    for wrapper in wrappers:
        raw=encode_event(wrapper);ident,key,application,d=validate(group,raw,time=time)
        if keys.get(ident)!=key:raise ValueError('Resulting assertion key')
        group.db.execute('INSERT INTO qo_join_support VALUES(?,?,?) ON CONFLICT(identity) DO UPDATE SET key=excluded.key,wrapper=excluded.wrapper',(ident,key,raw))

def check_add_references(group,result,*,time):
    old={m['identity'] for m in result['before']['members']};added=[m for m in result['after']['members'] if m['identity'] not in old]
    records=current_added(group,added,time=time);references=[]
    from provider_mls import call
    state=group.live()[1]
    for m,wrapper,application in records:
        package=decode_passive_discovery(wrapper)['assertion']['key_package_octets']
        references.append(call(Path(group.binary).with_name('provider-mls'),op='package-reference',checkpoint=state['checkpoint'],key=group.device['key'],package=package.hex())['reference'])
    actual=result.get('additions',[])
    if actual!=sorted(set(actual)) or sorted(references)!=actual:raise ValueError('Actual Add KeyPackageRef mismatch')
    return [json.loads(w) for m,w,a in sorted(records,key=lambda row:row[0]['identity'])]
