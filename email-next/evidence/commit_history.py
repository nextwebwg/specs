"""Public-data history for configured-writer add/self-update catch-up.

No SMTP release permission, old secret checkpoint, removal/rejoin or consensus.
Limits are explicit adjustable local inputs, not protocol limits.
"""
import hashlib
import json
from mls_receive import LockedIdentity,MlsReceive

def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def initialize(db):
    db.executescript('''
      CREATE TABLE IF NOT EXISTS commit_history_policy(id INTEGER PRIMARY KEY CHECK(id=1),max_count INTEGER NOT NULL,max_bytes INTEGER NOT NULL);
      CREATE TABLE IF NOT EXISTS commit_history(digest TEXT PRIMARY KEY,predecessor TEXT UNIQUE NOT NULL,record BLOB NOT NULL);
      CREATE TABLE IF NOT EXISTS commit_history_pin(owner TEXT NOT NULL,digest TEXT NOT NULL,state TEXT NOT NULL,PRIMARY KEY(owner,digest));
    ''')
def retain_decision_locked(db,result):
    """Called only from successful configured decision/receive transaction."""
    if not db.in_transaction:raise ValueError('Decision transaction required')
    if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='commit_history_policy'").fetchone():return
    policy=db.execute('SELECT max_count,max_bytes FROM commit_history_policy WHERE id=1').fetchone()
    if not policy:return
    record={k:result[k] for k in ('before','after','sender','wire','authorization')}
    wire=bytes.fromhex(record['wire']);identifier=hashlib.sha256(wire).hexdigest();raw=encoded(record)
    old=db.execute('SELECT record FROM commit_history WHERE digest=?',(identifier,)).fetchone()
    if old:
        if old[0]!=raw:raise ValueError('History byte conflict')
        return
    count,size=db.execute('SELECT count(*),coalesce(sum(length(record)),0) FROM commit_history').fetchone()
    if count+1>policy[0] or size+len(raw)>policy[1]:raise ValueError('History retention budget')
    db.execute('INSERT INTO commit_history VALUES(?,?,?)',(identifier,record['before']['predecessor'],raw))

class CommitHistory:
    def __init__(self,coordinator,*,max_count,max_bytes):
        self.coordinator=coordinator;self.identity=coordinator.identity;self.db=coordinator.db
        if self.db.in_transaction:raise ValueError('Initialize outside transaction')
        if any(type(v)!=int or not 1<=v<2**63 for v in (max_count,max_bytes)):raise ValueError('Explicit local limits')
        initialize(self.db)
        prior=self.db.execute('SELECT max_count,max_bytes FROM commit_history_policy WHERE id=1').fetchone()
        if prior and prior!=(max_count,max_bytes):raise ValueError('Retained policy differs; explicit migration required')
        self.db.execute('INSERT OR IGNORE INTO commit_history_policy VALUES(1,?,?)',(max_count,max_bytes))
    def path(self,start,*,target_identity,target_key,time,trust_policy):
        MlsReceive._policy(time,trust_policy)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            result=self.path_locked(start,target_identity=target_identity,target_key=target_key,time=time,trust_policy=trust_policy)
            self.db.execute('COMMIT');return result
        except BaseException:
            self.db.execute('ROLLBACK');raise
    def path_locked(self,start,*,target_identity,target_key,time,trust_policy):
        if not self.db.in_transaction:raise ValueError('Caller transaction required')
        MlsReceive._policy(time,trust_policy)
        if trust_policy!='allow-unverified':raise ValueError('Verification required')
        current=self.coordinator.live()['snapshot'];cursor=start;steps=[];seen=set();ordering=None
        target=(target_identity,target_key)
        if target not in {(m['identity'],m['key']) for m in current['members']}:raise ValueError('Target not current member')
        while cursor!=current['predecessor']:
            if cursor in seen:raise ValueError('History cycle')
            seen.add(cursor)
            row=self.db.execute('SELECT digest,record FROM commit_history WHERE predecessor=?',(cursor,)).fetchone()
            if not row:raise ValueError('History unavailable')
            identifier,raw=row;record=json.loads(raw)
            if hashlib.sha256(bytes.fromhex(record['wire'])).hexdigest()!=identifier or record['before']['predecessor']!=cursor:raise ValueError('History byte binding')
            before,after=record['before'],record['after']
            if steps and before!=steps[-1]['record']['after']:raise ValueError('Broken full-context ancestry')
            # 'context' is the application extension. Full epoch-bound GroupContext
            # bytes are 'predecessor' and connect each after to the next before.
            config=json.loads(bytes.fromhex(before['context']))
            stable={k:config.get(k) for k in ('version','purpose','conversation','profile','administrators','ordering')}
            if ordering is None:ordering=stable
            if stable!=ordering or before['group']!=current['group'] or after['group']!=current['group']:raise ValueError('Changed ordering/group')
            if target not in {(m['identity'],m['key']) for m in before['members']} or target not in {(m['identity'],m['key']) for m in after['members']}:raise ValueError('Target not continuously present')
            allowed={(m['identity'],m['key']) for m in after['members']}-{(m['identity'],m['key']) for m in before['members']}
            # Reuse the existing supported-transition and current authority policy;
            # the accepted ledger is the historical addition-admission evidence.
            self.coordinator._authorize(record,allowed,time,historical=True)
            signer=next(m for m in before['members'] if m['identity']==record['sender'])
            checked=LockedIdentity(self.identity).check_device(bytes.fromhex(signer['identity']),bytes.fromhex(signer['key']),role='send',time=time,trust_policy=trust_policy)
            if checked.get('status')!='authorized-unverified':raise ValueError('Current committer send authority')
            steps.append({'decision':identifier,'record':record});cursor=after['predecessor']
        if steps and steps[-1]['record']['after']!=current:raise ValueError('Current context mismatch')
        authority=LockedIdentity(self.identity)
        for member in current['members']:
            checked=authority.check_device(bytes.fromhex(member['identity']),bytes.fromhex(member['key']),role='receive',time=time,trust_policy=trust_policy)
            if checked.get('status')!='authorized-unverified':raise ValueError('Current identity in roster')
        return {'mode':'configured-history-v0','start':start,'tip':current['predecessor'],'group':current['group'],'target':{'identity':target_identity,'key':target_key},'steps':steps,'sendAuthorized':False}
    def pin_locked(self,owner,decisions,*,state):
        if not self.db.in_transaction or state not in ('active','uncertain'):raise ValueError('Pin transaction/state')
        if not isinstance(owner,str) or not owner:raise ValueError('Pin owner')
        for identifier in decisions:
            if not self.db.execute('SELECT 1 FROM commit_history WHERE digest=?',(identifier,)).fetchone():raise ValueError('History unavailable')
            self.db.execute('INSERT OR REPLACE INTO commit_history_pin VALUES(?,?,?)',(owner,identifier,state))
    def prune(self,identifier):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            if self.db.execute('SELECT 1 FROM commit_history_pin WHERE digest=?',(identifier,)).fetchone():raise ValueError('Active or uncertain history')
            self.db.execute('DELETE FROM commit_history WHERE digest=?',(identifier,));self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise
