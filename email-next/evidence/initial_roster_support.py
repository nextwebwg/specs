"""Reuse accepted initial-roster proofs only within their uninterrupted episode."""
import json
from event_encoding import encode_event
from invitation_mime import select
from initial_roster import parse,sha,credential
from application_agreement import profile
import group_instances as instances

def bootstrap_locked(db,before,member):
    if not db.in_transaction:raise ValueError('Caller transaction required')
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='initial_rosters'").fetchone():return None
    current=instances.optional_current(db,before['group'])
    if not current or current['status']!='active':return None
    row=db.execute('SELECT creation,request,roster_payload,roster_signature,context,role FROM initial_rosters WHERE anchor=?',(current['instance'],)).fetchone()
    if not row:return None
    creation,request,raw,signature,context,role=row
    if role=='creator':
        source=db.execute('SELECT wire FROM initial_roster_prepared WHERE creation=? ORDER BY target LIMIT 1',(creation,)).fetchone()
        if not source:raise ValueError('Missing retained targeted roster')
        wrapper=select(source[0])
    elif role=='recipient':wrapper=request
    else:raise ValueError('Unknown roster admission role')
    p=parse(wrapper)
    if p['roster_raw']!=raw or p['outer']['roster']['signature']!=signature or p['anchor']!=current['instance'] or p['group'].hex()!=before['group'] or context.hex()!=before['context'] or p['context_raw']!=context or p['context']['ordering']['kind']!='designated-member-v0':raise ValueError('Original roster context/instance mismatch')
    source=db.execute('SELECT key,proof,agreement,episode FROM initial_roster_members WHERE creation=? AND credential=?',(creation,member['identity'])).fetchone()
    if not source:raise ValueError('Missing original member support')
    key,proof,agreement,admission=source
    from transition_support import episode,canonical
    if episode(db,before['group'],member['identity'],member['key'])!=admission:raise ValueError('Original roster membership ended')
    actual=db.execute('SELECT signature_key,application,provenance_kind,admission_ref FROM mls_instance_agreements WHERE instance=? AND credential=?',(current['instance'],member['identity'])).fetchone()
    if key!=member['key'] or agreement!=profile(p['context']['application']) or actual!=(key,agreement,'signed-initial-roster',creation):raise ValueError('Original roster key/profile provenance mismatch')
    selected=next((w for w,d in zip(p['outer']['applicationAssertions'],p['proofs']) if credential(d['assertion']['value'])==member['identity']),None)
    if selected!=json.loads(proof):raise ValueError('Original roster proof mismatch')
    record=dict(group=before['group'],credential=member['identity'],key=key,context=before['context'],episode=admission,kind='signed-initial-roster',epoch='1',instance=current['instance'],source=sha(raw),wrapper=encode_event(selected).hex(),application=p['context']['application'])
    encoded=canonical(record);ident=sha(encoded)
    db.execute('INSERT OR IGNORE INTO mls_support_records VALUES(?,?)',(ident,encoded));db.execute('INSERT INTO mls_support_selected VALUES(?,?,?)',(before['group'],member['identity'],ident));return ident
