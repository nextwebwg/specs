"""Trusted local exact-byte sharing authorization; never a received capability.

Each group has its own sender database. Per-route authorization is durable, not a
cross-database or SMTP transaction. A prepared peer copy is not delivery success.
"""
import hashlib,json
from event_encoding import decode_event
from hosted_disclosure import validate_local_shape

def initialize(db):
    db.execute('CREATE TABLE IF NOT EXISTS private_copy_plans(digest TEXT PRIMARY KEY,application BLOB NOT NULL,policy_revision INTEGER NOT NULL,plan BLOB NOT NULL)')

def authorize(sender,application,*,other_copies,expected_revision):
    """Called by the trusted composer after exact content/metadata permission.

    Other copies are complete authored event bytes, retained locally, never sent
    as hidden history. A foreign author cannot be transplanted by this API.
    """
    value=validate_local_shape(application)
    if value['version'] not in ('2','3') or {'kind':'separate-protected-copy'} not in value['disclosures']:raise ValueError('Separate disclosure required')
    if not isinstance(other_copies,list) or not other_copies or any(not isinstance(x,bytes) for x in other_copies):raise ValueError('Exact other copies required')
    peers=[];seen=set()
    for raw in other_copies:
        peer=validate_local_shape(raw)
        if peer['version']!=value['version'] or peer['principal']!=value['principal'] or peer['conversation']==value['conversation'] or peer['event']==value['event'] or set(peer['audience'])==set(value['audience']) or {'kind':'separate-protected-copy'} not in peer['disclosures']:raise ValueError('Independent authored copy required')
        digest=hashlib.sha256(raw).hexdigest()
        if digest in seen:raise ValueError('Duplicate copy')
        seen.add(digest);peers.append(raw.hex())
    # Target-dependent source operations must be readable exports, not foreign references.
    for item in [value,*[decode_event(x)['value'] for x in other_copies]]:
        op=item['operation']
        if op['kind'] not in ('message','question','attachment-message','rich-message') or op.get('replyTo',[]):raise ValueError('Copy requires self-contained authored content')
    plan=json.dumps(sorted(peers),separators=(',',':')).encode();digest=hashlib.sha256(application).hexdigest();db=sender.db
    initialize(db)
    if db.in_transaction:raise ValueError('Own authorization transaction required')
    db.execute('BEGIN IMMEDIATE')
    try:
        revision=db.execute('SELECT revision FROM sender_policy WHERE id=1').fetchone()
        if revision!=(expected_revision,):raise ValueError('Changed policy')
        old=db.execute('SELECT application,policy_revision,plan FROM private_copy_plans WHERE digest=?',(digest,)).fetchone()
        if old and (old[0],old[2])!=(application,plan):raise ValueError('Immutable copy authorization')
        db.execute('INSERT INTO private_copy_plans VALUES(?,?,?,?) ON CONFLICT(digest) DO UPDATE SET policy_revision=excluded.policy_revision',(digest,application,expected_revision,plan));db.execute('COMMIT')
    except BaseException:db.execute('ROLLBACK');raise
    return digest

def check(db,application,revision):
    value=decode_event(application)['value']
    if {'kind':'separate-protected-copy'} not in value.get('disclosures',[]):return
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='private_copy_plans'").fetchone():raise ValueError('Private copy disclosure plan required')
    row=db.execute('SELECT application,policy_revision FROM private_copy_plans WHERE digest=?',(hashlib.sha256(application).hexdigest(),)).fetchone()
    if row!=(application,revision):raise ValueError('Private copy disclosure plan required')
