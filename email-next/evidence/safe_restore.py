"""Managed restoration: history-only import and fresh-key activation.

Source paths are explicit local UI selections, never message/relay input. No
source checkpoint, queue, vote, identity pin or key is installed in the live DB.
This cannot detect arbitrary rollback of the entire trusted application profile.
"""
import base64,hashlib,json,secrets,sqlite3,time as clock
from contextlib import closing
from pathlib import Path
from identity_store import IdentityStore
from event_encoding import encode_event,decode_event
from provider_mls import call,sign
from mls_identity import prepare
from mls_receive import LockedIdentity,MlsReceive

class RestoreWorkspace:
    def __init__(self,path,*,create=False,max_rows=10000,max_bytes=16*1024*1024,max_item_bytes=1024*1024,max_seconds=10):
        self.path=Path(path).resolve();self.limits=(max_rows,max_bytes,max_item_bytes,max_seconds)
        if any(type(x)!=int or x<1 for x in self.limits):raise ValueError('Adjustable restore limits')
        if create:self.path.mkdir(parents=False,exist_ok=False)
        elif not (self.path/'live.sqlite').is_file() or not (self.path/'history.sqlite').is_file():raise ValueError('Existing managed workspace required')
        self.identity=IdentityStore(self.path/'live.sqlite');self.db=self.identity.db
        self.db.executescript('''CREATE TABLE IF NOT EXISTS restore_state(id INTEGER PRIMARY KEY CHECK(id=1),mode TEXT NOT NULL,device BLOB,activation BLOB);''')
        if create:self.db.execute("INSERT INTO restore_state VALUES(1,'archive-only',NULL,NULL)")
        if self.db.execute('SELECT count(*) FROM restore_state').fetchone()[0]!=1:raise ValueError('Managed restore state required')
        self.history=sqlite3.connect(self.path/'history.sqlite',isolation_level=None)
        self.history.executescript('''CREATE TABLE IF NOT EXISTS imported_history(digest TEXT PRIMARY KEY,source TEXT NOT NULL,conversation TEXT NOT NULL,principal TEXT NOT NULL,event TEXT NOT NULL,octets BLOB NOT NULL);CREATE TABLE IF NOT EXISTS imports(source TEXT PRIMARY KEY,result BLOB NOT NULL);''')
    def close(self):self.history.close();self.identity.close()
    def import_history(self,source,*,crash=None):
        source=Path(source).resolve(strict=True)
        if source.is_relative_to(self.path):raise ValueError('Source must be separate from destination')
        max_rows,max_bytes,max_item,max_seconds=self.limits;started=clock.monotonic()
        def budget():
            if clock.monotonic()-started>max_seconds:raise ValueError('Restore time budget')
        def progress():return int(clock.monotonic()-started>max_seconds)
        self.history.execute('BEGIN IMMEDIATE')
        try:
            # sqlite_uri escaping is provided by pathlib; no source SQL executed.
            with closing(sqlite3.connect(source.as_uri()+'?mode=ro',uri=True)) as db:
                db.enable_load_extension(False);db.execute('PRAGMA query_only=ON');db.execute('PRAGMA trusted_schema=OFF')
                db.setlimit(sqlite3.SQLITE_LIMIT_LENGTH,max_item+4096);db.set_progress_handler(progress,1000)
                db.execute('BEGIN')
                table=next((r for r in db.execute('PRAGMA table_list') if r[1]=='contributions'),None)
                schema=db.execute("SELECT type,sql FROM sqlite_master WHERE name='contributions'").fetchone()
                if not table or table[2]!='table' or not schema or schema[0]!='table' or 'VIRTUAL TABLE' in schema[1].upper():raise ValueError('Ordinary history table required; views/virtual tables rejected')
                columns=list(db.execute('PRAGMA table_xinfo(contributions)'))
                if [r[1] for r in columns]!=['conversation','principal','event','octets'] or any(r[6] for r in columns):raise ValueError('Unsupported history schema')
                count=db.execute('SELECT count(*) FROM (SELECT 1 FROM contributions LIMIT ?)',(max_rows+1,)).fetchone()[0]
                if count>max_rows:raise ValueError('Restore row budget')
                # length() is checked before selecting each blob. No whole source
                # or private-state dump enters Python memory.
                used=0;h=hashlib.sha256();records=[]
                for rowid,size in db.execute('SELECT rowid,length(octets) FROM contributions ORDER BY rowid'):
                    budget()
                    if type(size)!=int or size>max_item or used+size>max_bytes:raise ValueError('Restore byte budget')
                    conversation,principal,event,raw=db.execute('SELECT conversation,principal,event,octets FROM contributions WHERE rowid=?',(rowid,)).fetchone()
                    if not isinstance(raw,bytes):raise ValueError('Historical event bytes required')
                    value=decode_event(raw)['value']
                    if any(not isinstance(x,str) or len(x)>256 for x in (conversation,principal,event)) or any(value.get(k)!=v for k,v in zip(('conversation','principal','event'),(conversation,principal,event))):raise ValueError('Historical reference mismatch')
                    digest=hashlib.sha256(raw).hexdigest();h.update(bytes.fromhex(digest));records.append((digest,conversation,principal,event,raw));used+=size
                identity=h.hexdigest();result=dict(sourceDigest=identity,records=len(records),bytes=used,protection='imported-history-not-reverified',excludedLiveState=True)
                for digest,conversation,principal,event,raw in records:
                    budget();self.history.execute('INSERT OR IGNORE INTO imported_history VALUES(?,?,?,?,?,?)',(digest,identity,conversation,principal,event,raw))
                self.history.execute('INSERT OR IGNORE INTO imports VALUES(?,?)',(identity,json.dumps(result).encode()))
            if crash:crash('before-import-commit')
            self.history.execute('COMMIT');return result
        except BaseException:
            if self.history.in_transaction:self.history.execute('ROLLBACK')
            raise
    def view(self):
        return [dict(digest=d,principal=p,event=e,text=decode_event(raw)['value'].get('operation',{}).get('text','Imported structured content'),status='Imported history — not reverified',actions=False) for d,p,e,raw in self.history.execute('SELECT digest,principal,event,octets FROM imported_history ORDER BY digest')]
    def status(self):return self.db.execute('SELECT mode FROM restore_state WHERE id=1').fetchone()[0]
    def start_fresh(self,binary,*,principal=None):
        """Trusted choice: existing account pairing, or explicit new identity."""
        if principal is not None and (len(principal)!=69 or not principal.startswith('enp0:')):raise ValueError('Existing account identifier')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            mode,retained=self.db.execute('SELECT mode,device FROM restore_state').fetchone()
            if mode!='archive-only':raise ValueError('Fresh setup already selected')
            path='pairing' if principal is not None else 'new-identity'
            principal=principal or 'enp0:'+secrets.token_hex(32);device_id='end0:'+secrets.token_hex(32)
            credential=b'email-next/device/v0\0'+bytes.fromhex(principal[5:])+bytes.fromhex(device_id[5:])
            device=call(binary,op='prepare',identity=credential.hex());device.update(identity=credential.hex(),principal=principal,device=device_id)
            binding,state=prepare(device['identity'],device['key'],device['time'])
            device['record']=dict(binding=base64.b64encode(binding).decode(),state=base64.b64encode(state).decode(),authorization=sign(binary,device,'email-next/device-binding/v0',binding),possession=sign(binary,device,'email-next/device-possession/v0',binding),stateProof=sign(binary,device,'email-next/identity-state/v0',state),time=dict.fromkeys(('earliest','latest'),str(device['time'])))
            device.update(binding=hashlib.sha256(binding).hexdigest(),state=hashlib.sha256(state).hexdigest())
            self.db.execute("UPDATE restore_state SET mode='needs-reconnect',device=?,activation=? WHERE id=1",(json.dumps(device).encode(),json.dumps(dict(path=path)).encode()));self.db.execute('COMMIT');return device
        except BaseException:self.db.execute('ROLLBACK');raise
    def activate_pairing(self,pairing,session,*,time,crash=None):
        """Accept only actual receipt for this workspace's fresh exact key."""
        if pairing.db is not self.db:raise ValueError('Same fresh database required')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            mode,raw=self.db.execute('SELECT mode,device FROM restore_state').fetchone();device=json.loads(raw) if raw else None
            if mode!='needs-reconnect' or json.loads(self.db.execute('SELECT activation FROM restore_state').fetchone()[0])['path']!='pairing':raise ValueError('Fresh enrollment required')
            offer,anchor,request,status,result=pairing._row(session)
            if status!='received' or not result:raise ValueError('Actual pairing receipt required')
            from remote_pairing import request_binding
            _,binding,value=request_binding(request,offer)
            if (value['principal'],value['device'],value['signingKey'])!=(device['principal'],device['device'],device['key']):raise ValueError('Pairing for different fresh device')
            self._current(device,time)
            receipt=dict(kind='paired-fresh-device',session=session,result=hashlib.sha256(result).hexdigest())
            self.db.execute("UPDATE restore_state SET mode='active-fresh-device',activation=? WHERE id=1",(json.dumps(receipt).encode(),));
            if crash:crash('before-activation-commit')
            self.db.execute('COMMIT');return receipt
        except BaseException:self.db.execute('ROLLBACK');raise
    def activate_new_identity(self,*,time,crash=None):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            mode,raw=self.db.execute('SELECT mode,device FROM restore_state').fetchone()
            if mode!='needs-reconnect' or json.loads(self.db.execute('SELECT activation FROM restore_state').fetchone()[0])['path']!='new-identity':raise ValueError('Explicit new identity choice required')
            device=json.loads(raw);record=dict(device['record'],time=time)
            if self.identity._observe_locked(record,first_contact_policy='allow-unverified')['status']!='pinned-unverified':raise ValueError('New identity unavailable')
            self.db.execute("UPDATE restore_state SET mode='new-identity-needs-contact-approval',activation=? WHERE id=1",(json.dumps(dict(kind='new-identity',principal=device['principal'])).encode(),))
            if crash:crash('before-activation-commit')
            self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise
    def _current(self,device,time):
        for role in ('send','receive'):
            if LockedIdentity(self.identity).check_device(bytes.fromhex(device['identity']),bytes.fromhex(device['key']),role=role,time=time,trust_policy='allow-unverified')['status']!='authorized-unverified':raise ValueError('Fresh device current authority unavailable')
    def sender(self,binary,*,time):
        if self.status() not in ('active-fresh-device','new-identity-needs-contact-approval'):raise ValueError('Imported history needs reconnect; sending unavailable')
        device=json.loads(self.db.execute('SELECT device FROM restore_state').fetchone()[0]);self._current(device,time)
        from sender_release import SenderRelease
        return SenderRelease(self.identity,binary)
    def voter(self,*args,**kwargs):raise ValueError('Imported voting state is never activated; fresh witness authorization required')
