"""Retained context7 admission and epoch binding, never a network boolean."""
import hashlib,json
from group_instances import optional_current

def initialize(db):
    from quorum_join import initialize as initialize_join
    initialize_join(db)
    db.execute('CREATE TABLE IF NOT EXISTS mls_quorum_admission(instance TEXT PRIMARY KEY,group_id TEXT NOT NULL,previous TEXT NOT NULL,context TEXT NOT NULL,commitment TEXT NOT NULL)')

def check_initial_witnesses(context,members):
    from ordering_mls import context_valid
    context_valid(context)
    if context['ordering']['generation']!='0':raise ValueError('Initial quorum generation')
    for w in context['ordering']['witnesses']:
        if not any(all(m[k]==w[k] for k in ('principal','device','signingKey','state','binding')) for m in members):raise ValueError('Initial witness binding')

def install_initial(db,instance,roster,joined):
    import base64
    context=base64.b64decode(roster['context']).hex()
    if hashlib.sha256(bytes.fromhex(joined['groupContext'])).hexdigest()!=roster['resultGroupContextDigest']:raise ValueError('Initial quorum commitment')
    from ordering_certificates import encode
    db.execute('INSERT INTO qo_genesis VALUES(?,?,?)',(instance,instance,encode(roster)))
    db.execute('INSERT INTO mls_quorum_admission VALUES(?,?,?,?,?)',(instance,joined['group'],'genesis',context,joined['groupContext']))

def accepted(db,group,context=None):
    current=optional_current(db,group)
    if not current or current['status']!='active':return False
    row=db.execute('SELECT context FROM mls_quorum_admission WHERE instance=? AND group_id=?',(current['instance'],group)).fetchone()
    return bool(row and (context is None or row[0]==context))
