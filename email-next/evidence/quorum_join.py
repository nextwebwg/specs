"""Pinned-genesis quorum history verification; no historical MLS decryption."""
import base64,hashlib,json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from event_encoding import encode_event
from initial_roster import parse as parse_initial,credential
from passive_discovery import canonical_base64,uint64,hexadecimal,decode_passive_discovery
from passive_discovery_verify import verify_passive_discovery
from provider_control import exact
from ordering_certificates import Proof,encode
from ordering_scope import scope_digest,decision_identity,octets
from ordering_mls import context_valid,candidate_id,admin_material
from mls_receive import LockedIdentity

def initialize(db):
    db.executescript('''CREATE TABLE IF NOT EXISTS qo_trusted_genesis(anchor TEXT PRIMARY KEY,roster BLOB NOT NULL);
    CREATE TABLE IF NOT EXISTS qo_genesis(instance TEXT PRIMARY KEY,anchor TEXT NOT NULL,roster BLOB NOT NULL);
    CREATE TABLE IF NOT EXISTS qo_history(decision TEXT PRIMARY KEY,carrier BLOB NOT NULL);
    CREATE TABLE IF NOT EXISTS qo_join_support(identity TEXT PRIMARY KEY,key TEXT NOT NULL,wrapper BLOB NOT NULL);''')

def import_anchor(identity,wrapper,*,expected_anchor,allow_creator,expected_context,intended_members,time):
    """Explicit independent selection. Never joins or consumes any package."""
    p=parse_initial(wrapper)
    if p['value']['version'] not in ('6','7') or p['anchor']!=expected_anchor or p['context_raw']!=expected_context or p['roster']['creator']['principal']!=allow_creator:raise ValueError('Independent genesis selection')
    actual=[{k:m[k] for k in ('principal','device','signingKey')} for m in p['roster']['members']]
    if actual!=intended_members:raise ValueError('Independent genesis roster')
    initialize(identity.db);identity.db.execute('BEGIN IMMEDIATE')
    try:
        for member in p['roster']['members']:
            check_current(identity,member,time,role='send' if member['kind']=='creator' else 'receive')
        old=identity.db.execute('SELECT roster FROM qo_trusted_genesis WHERE anchor=?',(expected_anchor,)).fetchone()
        if old and old!=(p['roster_raw'],):raise ValueError('Genesis conflict')
        identity.db.execute('INSERT OR IGNORE INTO qo_trusted_genesis VALUES(?,?)',(expected_anchor,p['roster_raw']))
        identity.db.execute('COMMIT')
    except BaseException:
        if identity.db.in_transaction:identity.db.execute('ROLLBACK')
        raise

def check_current(identity,member,time,role='receive'):
    ident=credential(member);checked=LockedIdentity(identity).check_device(bytes.fromhex(ident),bytes.fromhex(member['signingKey']),role=role,time=time,trust_policy='allow-unverified')
    if checked.get('status')!='authorized-unverified' or checked['head']!=member['state'] or checked['binding']!=member['binding']:raise ValueError('Current quorum path authority')

def verify_path(identity,roster,path,*,time):
    return _verify_path(identity,roster,path,time=time,witness_check=check_current)

def verify_recovery_path(identity,roster,path,*,time):
    from quorum_recovery_identity import check_witness
    return _verify_path(identity,roster,path,time=time,witness_check=check_witness)

def _verify_path(identity,roster,path,*,time,witness_check):
    if not isinstance(path,list) or not path:raise ValueError('Complete ordering path required')
    context=json.loads(canonical_base64(roster['context']));context_valid(context)
    previous='genesis';epoch='1';group=canonical_base64(roster['group']).hex();predecessor_hash=roster['resultGroupContextDigest'];members={credential(m):m['signingKey'] for m in roster['members']}
    for edge in path:
        exact(edge,{'candidate','proof'});candidate=edge['candidate'];exact(candidate,{'plan','approval'});plan=candidate['plan'];approval=candidate['approval']
        exact(plan,{'version','purpose','scope','commit','result','welcomes'})
        if (plan['version'],plan['purpose'])!=('0','ordering-candidate'):raise ValueError('Candidate version')
        scope=plan['scope'];sd=scope_digest(scope)
        if scope['previousDecision']!=previous or scope['group']!=group or scope['conversation']!=context['conversation'] or scope['slot']!=str(uint64(epoch)+1) or scope['ordering']!=context['ordering'] or hashlib.sha256(octets(scope['predecessor'])).hexdigest()!=predecessor_hash:raise ValueError('Ordering ancestry')
        keys={w['principal']+'|'+w['device']:w['signingKey'] for w in context['ordering']['witnesses']}
        for w in context['ordering']['witnesses']:
            if members.get(credential(w))!=w['signingKey']:raise ValueError('Witness predecessor roster')
            witness_check(identity,w,time)
        proof=Proof(canonical_base64(edge['proof']),scope=sd,keys=keys,f=int(context['ordering']['faultBound']));cid=candidate_id(candidate)
        if proof.result['kind']!='decision' or proof.result['candidate']!=cid:raise ValueError('Certified candidate')
        exact(approval,{'signer','signature'});author=approval['signer']
        if author not in members or 'enp0:'+author[42:106] not in context['administrators'] or not hexadecimal(approval['signature'],128):raise ValueError('Predecessor administrator')
        try:Ed25519PublicKey.from_public_bytes(bytes.fromhex(members[author])).verify(bytes.fromhex(approval['signature']),admin_material(plan))
        except Exception as error:raise ValueError('Administrator proof') from error
        octets(plan['commit']);result=plan['result'];exact(result,{'group','epoch','predecessor','context','members'})
        if result['group']!=group or result['epoch']!=scope['slot']:raise ValueError('Result epoch/group')
        next_context=json.loads(octets(result['context']));context_valid(next_context)
        for field in ('version','purpose','conversation','profile','administrators','application','delivery'):
            if next_context[field]!=context[field]:raise ValueError('Unselected context change')
        if next_context['ordering']!=context['ordering'] and uint64(next_context['ordering']['generation'])!=uint64(context['ordering']['generation'])+1:raise ValueError('Policy generation')
        next_members={};indices=set()
        if not isinstance(result['members'],list) or not result['members']:raise ValueError('Result members')
        for m in result['members']:
            exact(m,{'index','identity','key'})
            if uint64(m['index'])>=2**32:raise ValueError('Member index')
            if not hexadecimal(m['identity'],170) or not m['identity'].startswith(b'email-next/device/v0\0'.hex()) or not hexadecimal(m['key'],64) or m['identity'] in next_members or m['index'] in indices:raise ValueError('Result member')
            indices.add(m['index']);next_members[m['identity']]=m['key']
        principals=sorted({'enp0:'+i[42:106] for i in next_members})
        from private_copy import check_roster
        check_roster(next_context,principals)
        if not set(next_context['administrators']).issubset(principals):raise ValueError('Administrator outside result')
        for w in next_context['ordering']['witnesses']:
            if next_members.get(credential(w))!=w['signingKey']:raise ValueError('New witness outside result')
        if any(next_members[i]!=members[i] for i in set(next_members)&set(members)):raise ValueError('Unselected identity key replacement')
        added=sorted(set(next_members)-set(members));welcomes=plan['welcomes']
        if added:
            if not isinstance(welcomes,list) or len(welcomes)!=1:raise ValueError('Welcome coverage')
            exact(welcomes[0],{'recipients','bytes'})
            if welcomes[0]['recipients']!=added:raise ValueError('Welcome recipients')
            octets(welcomes[0]['bytes'])
        elif welcomes!=[]:raise ValueError('Unexpected Welcome')
        previous=decision_identity(scope,cid);predecessor_hash=hashlib.sha256(octets(result['predecessor'])).hexdigest();context=next_context;epoch=result['epoch'];members=next_members
    return dict(decision=previous,candidate=path[-1]['candidate'],context=context,members=members,added=added)

def verify_invitation_locked(identity,value,binary,*,time):
    row=identity.db.execute('SELECT roster FROM qo_trusted_genesis WHERE anchor=?',(value['genesis'],)).fetchone()
    if not row:raise ValueError('Independently accepted genesis required')
    path=value['orderingPath']
    if value['version']=='7':
        from quorum_exchange_support import historical_edge
        for edge in path:historical_edge(edge)
        path=[{k:edge[k] for k in ('candidate','proof')} for edge in path]
    result=verify_path(identity,json.loads(row[0]),path,time=time);plan=result['candidate']['plan'];final=plan['result'];target=credential(value['target'])
    if result['added']!=[target] or result['decision']!=value['decision'] or final['group']!=binary['group'].hex() or final['epoch']!=value['epoch'] or final['context']!=binary['context'].hex() or plan['welcomes'][0]['bytes']!=binary['welcome'].hex():raise ValueError('Final certified invitation')
    if hashlib.sha256(octets(final['predecessor'])).hexdigest()!=value['resultGroupContextDigest'] or hashlib.sha256(octets(plan['scope']['predecessor'])).hexdigest()!=value['previousGroupContextDigest'] or uint64(value['previousEpoch'])+1!=uint64(final['epoch']):raise ValueError('Certified context commitments')
    if result['members']!={credential(m):m['signingKey'] for m in value['members']}:raise ValueError('Certified final roster')
    return row[0]
