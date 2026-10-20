"""Explicit local experiment policy and logical live-row secret retirement.

No physical erasure guarantee: SQLite pages/WAL, backups and process memory are
outside this adapter. Maintenance never runs on an unconfigured database.
"""
import hashlib
import json
from pathlib import Path
import group_instances as instances

FIELDS={'maxPastEpochs','maxAgeSeconds','maxCheckpointBytes','outOfOrderTolerance','maximumForwardDistance'}

def encoded(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()

def validate(policy,*,epoch_ceiling=32):
    if not isinstance(policy,dict) or set(policy)!=FIELDS or any(type(v)!=int or v<0 for v in policy.values()):raise ValueError('Retention policy')
    if policy['maxPastEpochs']>epoch_ceiling or policy['outOfOrderTolerance']>2**32-1 or policy['maximumForwardDistance']>2**32-1 or policy['maxCheckpointBytes']==0:raise ValueError('Retention policy bound')
    return dict(policy)

def initialize(db):
    db.executescript('''
      CREATE TABLE IF NOT EXISTS mls_retention_policy(group_id TEXT PRIMARY KEY,revision INTEGER NOT NULL,policy BLOB NOT NULL,watermark INTEGER NOT NULL,cutoff INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS mls_retention_journal(group_id TEXT NOT NULL,revision INTEGER NOT NULL,watermark INTEGER NOT NULL,reason TEXT NOT NULL,details BLOB NOT NULL);
      CREATE TABLE IF NOT EXISTS mls_retained_epoch(instance TEXT NOT NULL,group_id TEXT NOT NULL,epoch TEXT NOT NULL,snapshot BLOB NOT NULL,PRIMARY KEY(instance,group_id,epoch));
      CREATE TABLE IF NOT EXISTS mls_retired_candidate(digest TEXT PRIMARY KEY,predecessor TEXT NOT NULL,packages BLOB NOT NULL,public_state BLOB NOT NULL,reason TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS mls_secret_copy_schema(id INTEGER PRIMARY KEY CHECK(id=1),version INTEGER NOT NULL);
    ''')

def clock(time):
    if not isinstance(time,dict) or set(time)!={'earliest','latest'} or any(not isinstance(v,str) or not v.isascii() or not v.isdecimal() or (len(v)>1 and v[0]=='0') for v in time.values()):raise ValueError('Credible retention clock required')
    lo,hi=int(time['earliest']),int(time['latest'])
    if not 0<=lo<=hi<=2**63-1:raise ValueError('Retention clock range')
    return lo,hi

def origin(db,group):
    present=instances.optional_current(db,group)
    return present['instance'] if present else 'configured:'+group

def retain_snapshot(db,snapshot):
    """Caller supplies an installed/authenticated MLS snapshot in its transaction."""
    if not db.in_transaction:raise ValueError('Caller transaction required')
    group=snapshot['group']
    if not db.execute('SELECT 1 FROM mls_retention_policy WHERE group_id=?',(group,)).fetchone():return
    # Canonical receive shape; GroupContext predecessor is retained separately in
    # accepted decision evidence, never confused with application context bytes.
    members=snapshot['members']
    if members and isinstance(members[0],dict):members=[f"{m['index']}:{m['identity']}:{m['key']}" for m in members]
    value=dict(group=group,epoch=snapshot['epoch'],context=snapshot['context'],members=members,predecessor=snapshot['predecessor'])
    key=(origin(db,group),group,value['epoch']);raw=encoded(value)
    row=db.execute('SELECT snapshot FROM mls_retained_epoch WHERE instance=? AND group_id=? AND epoch=?',key).fetchone()
    if row and row[0]!=raw:raise ValueError('Conflicting accepted epoch snapshot')
    db.execute('INSERT OR IGNORE INTO mls_retained_epoch VALUES(?,?,?,?)',(*key,raw))

def historical_snapshot(db,group,epoch):
    row=db.execute('SELECT snapshot FROM mls_retained_epoch WHERE instance=? AND group_id=? AND epoch=?',(origin(db,group),group,epoch)).fetchone()
    return json.loads(row[0]) if row else None

def _has(db,table):return bool(db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone())

def retire_copies(db,group,reason,*,retire_candidates=False):
    """Exact known storage fields only; never recurse into contribution payloads."""
    count=0
    for table in ('gt_decision','gt_outbox','gt_candidate'):
        if not _has(db,table):continue
        for ident,raw in db.execute(f'SELECT digest,state FROM {table}').fetchall():
            value=json.loads(raw)
            if value.get('before',{}).get('group')!=group:continue
            decided=_has(db,'gt_decision') and db.execute('SELECT 1 FROM gt_decision WHERE digest=?',(ident,)).fetchone()
            if table=='gt_candidate' and not decided and not retire_candidates:continue
            if table=='gt_candidate' and not decided:
                public=dict(value);public.pop('checkpoint',None);public.pop('unmerged',None);public['retainedResultVersion']='public-v1'
                packages=db.execute('SELECT packages FROM gt_candidate WHERE digest=?',(ident,)).fetchone()[0]
                db.execute('INSERT OR IGNORE INTO mls_retired_candidate VALUES(?,?,?,?,?)',(ident,value['before']['predecessor'],packages,encoded(public),reason))
                db.execute('INSERT OR IGNORE INTO gt_abandoned VALUES(?,?,?)',(ident,value['before']['predecessor'],'retired-secret-policy:'+reason))
                db.execute('DELETE FROM gt_candidate WHERE digest=?',(ident,));count+=1;continue
            if any(k in value for k in ('checkpoint','unmerged')):
                value.pop('checkpoint',None);value.pop('unmerged',None);value['retainedResultVersion']='public-v1'
                db.execute(f'UPDATE {table} SET state=? WHERE digest=?',(encoded(value),ident));count+=1
    if _has(db,'provider_mls_admission'):
        for ref,device,invitation,joined in db.execute('SELECT reference,device,invitation,joined FROM provider_mls_admission').fetchall():
            if invitation is None:
                # Pinned memory-storage labels are prepended to serialized keys.
                # Unconsumed admission material is not silently destroyed.
                d=json.loads(device)
                if any(bytes.fromhex(row[0]).startswith((b'GroupState',b'EpochSecrets',b'MessageSecrets',b'ResumptionPsk')) for row in d.get('checkpoint',[])):
                    raise ValueError('Unconsumed package carries group secrets; explicit migration required')
                continue
            if joined is None:raise ValueError('Consumed package lacks public admission result')
            result=json.loads(joined)
            if result.get('group')!=group:continue
            d=json.loads(device);changed=False
            for value in (d,result):
                if 'checkpoint' in value:value.pop('checkpoint');value['privateState']='retired';changed=True
            if changed:
                db.execute('UPDATE provider_mls_admission SET device=?,joined=? WHERE reference=?',(encoded(d),encoded(result),ref));count+=1
    if _has(db,'application_admissions'):
        for ref,raw in db.execute('SELECT reference,result FROM application_admissions').fetchall():
            result=json.loads(raw)
            if result.get('group')==group and 'checkpoint' in result:
                result.pop('checkpoint');result['privateState']='retired';db.execute('UPDATE application_admissions SET result=? WHERE reference=?',(encoded(result),ref));count+=1
    db.execute('INSERT INTO mls_secret_copy_schema VALUES(1,1) ON CONFLICT(id) DO UPDATE SET version=1')
    return count

def maintain_locked(db,binary,time,*,checkpoint=None,crash=None):
    if not db.in_transaction:raise ValueError('Caller transaction required')
    row=db.execute('SELECT revision,group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
    if not row:return None
    if _has(db,'mls_retention_retired') and db.execute('SELECT 1 FROM mls_retention_retired WHERE group_id=?',(row[1],)).fetchone():return dict(status='retired',checkpoint=json.loads(row[2]),droppedAllPast=True)
    setting=db.execute('SELECT revision,policy,watermark,cutoff FROM mls_retention_policy WHERE group_id=?',(row[1],)).fetchone()
    if not setting:return None
    lo,hi=clock(time)
    if hi<setting[2]:raise ValueError('Retention clock rollback')
    policy=json.loads(setting[1]);cutoff=max(setting[3],max(0,hi-policy['maxAgeSeconds']))
    from provider_mls import call
    result=call(Path(binary).with_name('retention-staged'),checkpoint=json.loads(row[2]) if checkpoint is None else checkpoint,group=row[1],policy=policy,cutoff=cutoff)
    if result.get('status') not in ('maintained','retired'):raise ValueError('Retention worker rejected')
    changed=result['checkpoint']!=json.loads(row[2])
    copies=retire_copies(db,row[1],str(setting[0]),retire_candidates=changed)
    retain_snapshot(db,result['snapshot'])
    if changed:db.execute('UPDATE mls_checkpoint SET revision=revision+1,snapshot=? WHERE id=1',(encoded(result['checkpoint']),))
    db.execute('UPDATE mls_retention_policy SET watermark=?,cutoff=? WHERE group_id=?',(hi,cutoff,row[1]))
    db.execute('INSERT INTO mls_retention_journal VALUES(?,?,?,?,?)',(row[1],setting[0],hi,result['status'],encoded(dict(copies=copies,droppedAllPast=result['droppedAllPast']))))
    if result['status']=='retired':
        db.execute('CREATE TABLE IF NOT EXISTS mls_retention_retired(group_id TEXT PRIMARY KEY,reason TEXT NOT NULL)')
        db.execute("INSERT OR REPLACE INTO mls_retention_retired VALUES(?,'storage-budget')",(row[1],))
    if crash:crash('before-retention-commit')
    return result

class SecretRetention:
    def __init__(self,receiver):self.receiver=receiver;self.db=receiver.db;initialize(self.db)
    def configure(self,policy,*,time,expected_revision=0,epoch_ceiling=32,crash=None):
        policy=validate(policy,epoch_ceiling=epoch_ceiling);lo,hi=clock(time);db=self.db;db.execute('BEGIN IMMEDIATE')
        try:
            row=db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
            if not row:raise ValueError('Accepted group required')
            old=db.execute('SELECT revision,watermark,cutoff FROM mls_retention_policy WHERE group_id=?',(row[0],)).fetchone()
            if (old[0] if old else 0)!=expected_revision:raise ValueError('Retention policy revision')
            if old and hi<old[1]:raise ValueError('Retention clock rollback')
            db.execute('INSERT INTO mls_retention_policy VALUES(?,?,?,?,?) ON CONFLICT(group_id) DO UPDATE SET revision=excluded.revision,policy=excluded.policy',(row[0],expected_revision+1,encoded(policy),hi,old[2] if old else 0))
            result=maintain_locked(db,self.receiver.binary,time,crash=crash);db.execute('COMMIT')
            if crash:crash('after-retention-commit')
            return result['status']
        except BaseException:
            if db.in_transaction:db.execute('ROLLBACK')
            raise
    def maintain(self,*,time,crash=None):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            result=maintain_locked(self.db,self.receiver.binary,time,crash=crash);self.db.execute('COMMIT');return result
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
