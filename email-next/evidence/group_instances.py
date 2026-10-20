"""Explicit local instance migration. No inferred admission or secret checkpoint copy."""
import hashlib
import json

def encoded(value):return json.dumps(value,separators=(',',':')).encode()

def initialize(db):
    if db.in_transaction:raise ValueError('Initialize outside transaction')
    db.executescript('''
      CREATE TABLE IF NOT EXISTS mls_group_instances(instance TEXT PRIMARY KEY,group_id TEXT NOT NULL,admission_digest TEXT NOT NULL,provenance TEXT NOT NULL,status TEXT NOT NULL CHECK(status IN ('active','inactive')),terminal_decision TEXT);
      CREATE UNIQUE INDEX IF NOT EXISTS mls_one_active_instance ON mls_group_instances(group_id) WHERE status='active';
      CREATE TABLE IF NOT EXISTS mls_checkpoint_instance(id INTEGER PRIMARY KEY CHECK(id=1),instance TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS mls_receive_instance(digest TEXT PRIMARY KEY,instance TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS mls_instance_agreements(instance TEXT NOT NULL,credential TEXT NOT NULL,signature_key TEXT NOT NULL,application TEXT NOT NULL,provenance_kind TEXT NOT NULL,admission_ref TEXT,PRIMARY KEY(instance,credential));
      CREATE TABLE IF NOT EXISTS mls_episode_instance(group_id TEXT NOT NULL,identity TEXT NOT NULL,key TEXT NOT NULL,admission TEXT NOT NULL,instance TEXT NOT NULL,PRIMARY KEY(group_id,identity,key,admission));
      CREATE TABLE IF NOT EXISTS mls_instance_schema(id INTEGER PRIMARY KEY CHECK(id=1),version INTEGER NOT NULL);
    ''')

def current(db,group):
    row=db.execute('SELECT i.instance,i.group_id,i.status FROM mls_checkpoint_instance c JOIN mls_group_instances i ON c.instance=i.instance WHERE c.id=1').fetchone()
    if not row or row[1]!=group:raise ValueError('Instance migration required')
    return dict(instance=row[0],group=row[1],status=row[2])

class GroupInstances:
    def __init__(self,db):self.db=db;initialize(db)
    def migrate_configured(self,coordinator,*,crash=None):
        """Only an explicitly installed configured-v1 fixture with retained evidence.

        Real admission migration has a separate proof source; caller JSON cannot
        label itself verified or supply replacement snapshots.
        """
        if coordinator.db is not self.db:raise ValueError('Shared coordinator required')
        db=self.db;db.execute('BEGIN IMMEDIATE')
        try:
            cp=db.execute('SELECT group_id FROM mls_checkpoint WHERE id=1').fetchone()
            if not cp:raise ValueError('Missing checkpoint')
            group=cp[0]
            if db.execute('SELECT 1 FROM mls_checkpoint_instance WHERE id=1').fetchone():
                value=current(db,group);db.execute('COMMIT');return value
            periods=db.execute('SELECT identity,key,start_epoch,end_epoch,admission,removal FROM mls_membership_episode WHERE group_id=?',(group,)).fetchall()
            initial={p[4] for p in periods if p[4].startswith('configured-install:')}
            if len(initial)!=1:raise ValueError('Ambiguous initial admission evidence')
            admission=next(iter(initial));snapshots={}
            def retain(snapshot):
                if snapshot['group']!=group:raise ValueError('Foreign retained group')
                epoch=snapshot['epoch'];old=snapshots.get(epoch)
                if old is not None and old!=snapshot:raise ValueError('Ambiguous retained epoch')
                snapshots[epoch]=snapshot
            for raw, in db.execute('SELECT state FROM gt_decision'):
                record=json.loads(raw);retain(record['before']);retain(record['after'])
                if not record.get('authorization'):raise ValueError('Missing accepted decision authority')
            for result,raw in db.execute('SELECT result,evidence FROM gt_receive'):
                if result=='accepted':retain(json.loads(raw))
            terminal=db.execute('SELECT decision,snapshot FROM mls_group_inactive WHERE group_id=?',(group,)).fetchone()
            if terminal:
                if not db.execute("SELECT 1 FROM gt_receive WHERE digest=? AND result='accepted'",(terminal[0],)).fetchone():raise ValueError('Missing terminal receipt')
                end=json.loads(terminal[1]);status='inactive';end_epoch=end['epoch']
            else:
                end=coordinator.live()['snapshot'];retain(end);status='active';end_epoch=end['epoch']
            starts=[s for s in snapshots.values() if 'configured-install:'+hashlib.sha256(encoded(s)).hexdigest()==admission]
            if len(starts)!=1:raise ValueError('Missing authenticated installation snapshot')
            start=starts[0];ctx=json.loads(bytes.fromhex(start['context']))
            if ctx.get('version')!='1' or ctx.get('ordering',{}).get('kind')!='designated-member-v0':raise ValueError('Unsupported migration provenance')
            expected={(m['identity'],m['key']) for m in start['members']}
            actual={(p[0],p[1]) for p in periods if p[4]==admission and p[2]==start['epoch']}
            if actual!=expected:raise ValueError('Initial episode mismatch')
            for identity,key,begin,finish,source,removal in periods:
                if int(begin)<int(start['epoch']) or int(begin)>int(end_epoch):raise ValueError('Episode outside known history')
                if source!=admission:
                    row=db.execute('SELECT state FROM gt_decision WHERE digest=?',(source,)).fetchone()
                    if not row:raise ValueError('Missing admission decision')
                    decision=json.loads(row[0]);old={(m['identity'],m['key']) for m in decision['before']['members']};new={(m['identity'],m['key']) for m in decision['after']['members']}
                    if (identity,key) not in new-old or decision['after']['epoch']!=begin:raise ValueError('Admission episode mismatch')
                if finish is not None:
                    if not removal or int(finish)<=int(begin):raise ValueError('Ended episode evidence')
                    row=db.execute('SELECT state FROM gt_decision WHERE digest=?',(removal,)).fetchone()
                    if row:
                        decision=json.loads(row[0]);old={(m['identity'],m['key']) for m in decision['before']['members']};new={(m['identity'],m['key']) for m in decision['after']['members']}
                        if (identity,key) not in old-new or decision['after']['epoch']!=finish:raise ValueError('Removal episode mismatch')
                    elif not terminal or terminal[0]!=removal or end_epoch!=finish or (identity,key) in {(m['identity'],m['key']) for m in end['members']}:raise ValueError('Missing removal evidence')
            # This configured-v1 profile has no application selection. Copying
            # mutable newer agreement rows into its past would invent provenance.
            if db.execute('SELECT 1 FROM mls_application_agreement WHERE group_id=?',(group,)).fetchone():raise ValueError('Unexpected agreement requires explicit migration')
            instance=hashlib.sha256(b'email-next/local-configured-instance/v0\0'+bytes.fromhex(group)+bytes.fromhex(admission.split(':',1)[1])).hexdigest()
            db.execute('INSERT INTO mls_group_instances VALUES(?,?,?,?,?,?)',(instance,group,admission,'configured-install',status,terminal[0] if terminal else None))
            db.execute('INSERT INTO mls_checkpoint_instance VALUES(1,?)',(instance,))
            for identity,key,begin,finish,source,removal in periods:db.execute('INSERT INTO mls_episode_instance VALUES(?,?,?,?,?)',(group,identity,key,source,instance))
            if crash:crash('after-instance')
            for digest,wire,evidence in db.execute('SELECT digest,wire,evidence FROM mls_receives'):
                e=json.loads(evidence);p=e['processed'];s=e['snapshot'];known=snapshots.get(s['epoch'])
                if hashlib.sha256(wire).hexdigest()!=digest or p['group']!=group or s['group']!=group or p['epoch']!=s['epoch'] or not known:raise ValueError('Ambiguous retained receive evidence')
                members=[str(m['index'])+':'+m['identity']+':'+m['key'] for m in known['members']]
                if s['members']!=members or s['context']!=known['context']:raise ValueError('Retained receive snapshot mismatch')
                db.execute('INSERT INTO mls_receive_instance VALUES(?,?)',(digest,instance))
            db.execute('INSERT INTO mls_instance_schema VALUES(1,1) ON CONFLICT(id) DO UPDATE SET version=1')
            if crash:crash('before-commit')
            db.execute('COMMIT');return dict(instance=instance,group=group,status=status)
        except BaseException:
            if db.in_transaction:db.execute('ROLLBACK')
            raise

def optional_current(db,group):
    if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='mls_checkpoint_instance'").fetchone():return None
    if not db.execute('SELECT 1 FROM mls_checkpoint_instance').fetchone():
        if db.execute('SELECT 1 FROM mls_group_instances').fetchone():raise ValueError('Instance pointer missing')
        return None
    return current(db,group)

def receive_origin(db,digest,group):
    present=optional_current(db,group)
    if present is None:return None
    row=db.execute('SELECT instance FROM mls_receive_instance WHERE digest=?',(digest,)).fetchone()
    if not row:raise ValueError('Receive instance migration required')
    return row[0]

def record_receive(db,digest,group):
    present=optional_current(db,group)
    if present:
        if present['status']!='active':raise ValueError('Inactive instance')
        db.execute('INSERT INTO mls_receive_instance VALUES(?,?)',(digest,present['instance']))

def note_transition(db,result,decision):
    present=optional_current(db,result['before']['group'])
    if not present:return
    if present['status']!='active':raise ValueError('Inactive instance')
    for identity,key,admission in db.execute('SELECT identity,key,admission FROM mls_membership_episode WHERE group_id=? AND admission=?',(present['group'],decision)):
        db.execute('INSERT INTO mls_episode_instance VALUES(?,?,?,?,?)',(present['group'],identity,key,admission,present['instance']))
    if result.get('selfRemoved'):
        db.execute("UPDATE mls_group_instances SET status='inactive',terminal_decision=? WHERE instance=?",(decision,present['instance']))

def admission_instance(payload,signature):
    if not isinstance(payload,bytes) or not isinstance(signature,bytes) or len(signature)!=64:raise ValueError('Exact admission proof bytes')
    return hashlib.sha256(b'email-next/local-membership-instance/v0\0'+len(payload).to_bytes(4,'big')+payload+signature).hexdigest()

def install_rejoin_locked(db,joined,*,payload,signature,admission):
    """Internal post-verification seam. Caller validates signed admission and MLS.

    Does not grant authority or consume the package. The caller commits all proof,
    package, checkpoint and episode writes together or rolls the transaction back.
    """
    if not db.in_transaction:raise ValueError('Caller transaction required')
    from membership_episodes import install
    from mls_receive import FORMAT
    old=current(db,joined['group'])
    if old['status']!='inactive':raise ValueError('Rejoin requires inactive instance')
    terminal=db.execute('SELECT decision,snapshot FROM mls_group_inactive WHERE group_id=?',(joined['group'],)).fetchone()
    if not terminal:raise ValueError('Missing retained terminal evidence')
    snapshot=json.loads(terminal[1])
    if int(joined['epoch'])<=int(snapshot['epoch']):raise ValueError('Rejoin cannot restore old epoch')
    instance=admission_instance(payload,signature)
    db.execute('INSERT INTO mls_group_instances VALUES(?,?,?,?,?,NULL)',(instance,joined['group'],admission,'established-invitation','active'))
    db.execute('CREATE TABLE IF NOT EXISTS mls_instance_terminal(instance TEXT PRIMARY KEY,decision TEXT NOT NULL,snapshot BLOB NOT NULL)')
    db.execute('INSERT INTO mls_instance_terminal VALUES(?,?,?)',(old['instance'],terminal[0],terminal[1]))
    db.execute('DELETE FROM mls_group_inactive WHERE group_id=?',(joined['group'],))
    db.execute('UPDATE mls_checkpoint SET revision=revision+1,format=?,snapshot=? WHERE id=1 AND group_id=?',(FORMAT,json.dumps(joined['checkpoint']).encode(),joined['group']))
    db.execute('UPDATE mls_checkpoint_instance SET instance=? WHERE id=1',(instance,))
    install(db,joined,admission)
    for member in joined['members']:
        db.execute('INSERT INTO mls_episode_instance VALUES(?,?,?,?,?)',(joined['group'],member['identity'],member['key'],admission,instance))
    return instance
