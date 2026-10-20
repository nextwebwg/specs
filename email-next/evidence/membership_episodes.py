"""Local configured-group membership episodes; never admission from network claims."""
import json

def initialize(db):
    db.executescript('''
      CREATE TABLE IF NOT EXISTS mls_membership_episode(group_id TEXT NOT NULL,identity TEXT NOT NULL,key TEXT NOT NULL,start_epoch TEXT NOT NULL,end_epoch TEXT,admission TEXT NOT NULL,removal TEXT,PRIMARY KEY(group_id,identity,key,admission));
      CREATE TABLE IF NOT EXISTS mls_group_inactive(group_id TEXT PRIMARY KEY,decision TEXT NOT NULL,snapshot BLOB NOT NULL);
    ''')

def install(db,snapshot,admission):
    for member in snapshot['members']:
        db.execute('INSERT INTO mls_membership_episode VALUES(?,?,?,?,NULL,?,NULL)',(snapshot['group'],member['identity'],member['key'],snapshot['epoch'],admission))

def transition(db,result,decision):
    before,after=result['before'],result['after'];group=before['group']
    old={(m['identity'],m['key']) for m in before['members']};new={(m['identity'],m['key']) for m in after['members']}
    from group_instances import optional_current
    current=optional_current(db,group)
    for identity,key in old-new:
        if current:
            changed=db.execute('UPDATE mls_membership_episode SET end_epoch=?,removal=? WHERE group_id=? AND identity=? AND key=? AND end_epoch IS NULL AND admission IN (SELECT admission FROM mls_episode_instance WHERE group_id=? AND identity=? AND key=? AND instance=?)',(after['epoch'],decision,group,identity,key,group,identity,key,current['instance'])).rowcount
        else:
            changed=db.execute('UPDATE mls_membership_episode SET end_epoch=?,removal=? WHERE group_id=? AND identity=? AND key=? AND end_epoch IS NULL',(after['epoch'],decision,group,identity,key)).rowcount
        if changed!=1:raise ValueError('Missing unique membership episode')
    for identity,key in new-old:
        db.execute('INSERT INTO mls_membership_episode VALUES(?,?,?,?,NULL,?,NULL)',(group,identity,key,after['epoch'],decision))
    from group_instances import note_transition
    note_transition(db,result,decision)
    if result.get('selfRemoved'):
        db.execute('INSERT INTO mls_group_inactive VALUES(?,?,?)',(group,decision,json.dumps(dict(terminal=True,**{k:after[k] for k in ('group','epoch','context','members')}))))

def permits(db,group,identity,key,epoch):
    if db.execute('SELECT 1 FROM mls_group_inactive WHERE group_id=?',(group,)).fetchone():return False
    # Non-transition comparison fixtures have no episode ledger yet.
    if not db.execute('SELECT 1 FROM mls_membership_episode WHERE group_id=?',(group,)).fetchone():
        return db.execute('SELECT 1 FROM mls_configured_context WHERE group_id=?',(group,)).fetchone() is None
    from group_instances import optional_current
    instance=optional_current(db,group)
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='mls_remediation_epoch_hold'").fetchone() and db.execute("SELECT 1 FROM mls_remediation_epoch_hold WHERE (instance=? OR instance='') AND group_id=? AND epoch=?",(instance['instance'] if instance else '',group,str(epoch))).fetchone():return False
    if instance:
        if instance['status']!='active':return False
        rows=db.execute('SELECT e.start_epoch FROM mls_membership_episode e JOIN mls_episode_instance i ON e.group_id=i.group_id AND e.identity=i.identity AND e.key=i.key AND e.admission=i.admission WHERE e.group_id=? AND e.identity=? AND e.key=? AND e.end_epoch IS NULL AND i.instance=?',(group,identity,key,instance['instance'])).fetchall()
        return len(rows)==1 and int(rows[0][0])<=int(epoch)
    rows=db.execute('SELECT start_epoch FROM mls_membership_episode WHERE group_id=? AND identity=? AND key=? AND end_epoch IS NULL',(group,identity,key)).fetchall()
    return len(rows)==1 and int(rows[0][0])<=int(epoch)

def permits_processed(db,processed,snapshot):
    rows=[m.split(':') for m in snapshot['members']]
    match=[m for m in rows if m[0]==processed['sender'] and m[1]==processed['credential']]
    return len(match)==1 and permits(db,processed['group'],match[0][1],match[0][2],processed['epoch'])
