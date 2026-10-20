"""Account-local mailbox retrieval; sources convey bytes, never transition authority.

Limits are adjustable implementation inputs. No remote request protocol or writer
failover. The caller explicitly configures sources, exact permitted additions and
past-secret retirement policy. Invalid inputs never consume live MLS state.
"""
import hashlib
import math
import json
import sqlite3
import time as clock
from pathlib import Path
from remediation_chain import RemediationChain,POLICY,members
from transition_carrier import parse,check_binding
from transition_mime import select
from discovery_mime import extract_discovery
from group_transitions import encode,ids
from mls_receive import MlsReceive
import group_instances as instances
import remediation_support


def digest(raw):return hashlib.sha256(raw).hexdigest()

class MailSpool:
    """Configured local mailbox stand-in; append actual received MIME octets.

    Sequence numbers, not message names or arrival headers, provide stable scan
    cursors. This is not a deployed IMAP/JMAP adapter.
    """
    def __init__(self,path):
        self.db=sqlite3.connect(Path(path),isolation_level=None)
        self.db.execute('CREATE TABLE IF NOT EXISTS mail(id INTEGER PRIMARY KEY AUTOINCREMENT,wire BLOB NOT NULL)')
    def append(self,wire):
        if not isinstance(wire,bytes):raise ValueError('MIME octets')
        return self.db.execute('INSERT INTO mail(wire) VALUES(?)',(wire,)).lastrowid
    def scan(self,cursor,*,max_messages,max_bytes):
        out=[];size=0
        for ident,raw in self.db.execute('SELECT id,wire FROM mail WHERE id>? ORDER BY id LIMIT ?',(cursor,max_messages)):
            if len(raw)>max_bytes:raise ValueError('Source message exceeds byte budget')
            if size+len(raw)>max_bytes:break
            out.append((ident,raw));size+=len(raw)
        return out
    def close(self):self.db.close()

class RecoveryRetrieval:
    def __init__(self,coordinator,sources,*,max_messages=128,max_bytes=8*1024*1024,max_steps=16,max_candidates=64,max_seconds=30):
        if not isinstance(sources,dict) or not sources or any(not isinstance(k,str) or not k for k in sources):raise ValueError('Configured sources required')
        if any(type(n)!=int or n<1 for n in (max_messages,max_bytes,max_steps,max_candidates)):raise ValueError('Local limits')
        if type(max_seconds) not in (int,float) or not (math.isfinite(max_seconds) and max_seconds>0):raise ValueError('Local time budget')
        self.max_seconds=max_seconds
        self.g=coordinator;self.db=coordinator.db;self.sources=sources
        self.limits=(max_messages,max_bytes,max_steps,max_candidates)
        self.recovery=RemediationChain(coordinator,max_steps=max_steps,max_bytes=max_bytes)
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS recovery_source(id TEXT PRIMARY KEY,cursor INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS recovery_mail(digest TEXT PRIMARY KEY,wire BLOB NOT NULL,carrier BLOB);
          CREATE TABLE IF NOT EXISTS recovery_origin(source TEXT NOT NULL,position INTEGER NOT NULL,digest TEXT NOT NULL,PRIMARY KEY(source,position));
          CREATE TABLE IF NOT EXISTS recovery_support(digest TEXT PRIMARY KEY,wrapper BLOB NOT NULL);
          CREATE TABLE IF NOT EXISTS recovery_job(id TEXT PRIMARY KEY,request BLOB NOT NULL,state TEXT NOT NULL,chosen BLOB,result BLOB);
        ''')
    def add_support(self,wrapper):
        # Untrusted cache: verification happens against current authority in run.
        if not isinstance(wrapper,bytes) or len(wrapper)>self.limits[1]:raise ValueError('Support bytes')
        count,size=self.db.execute('SELECT count(*),coalesce(sum(length(wrapper)),0) FROM recovery_support').fetchone()
        if not self.db.execute('SELECT 1 FROM recovery_support WHERE digest=?',(digest(wrapper),)).fetchone() and (count>=self.limits[0] or size+len(wrapper)>self.limits[1]):raise ValueError('Support budget')
        self.db.execute('INSERT OR IGNORE INTO recovery_support VALUES(?,?)',(digest(wrapper),wrapper))
    def schedule(self,identifier,*,allowed,policy=None):
        if not isinstance(identifier,str) or not identifier:raise ValueError('Job ID')
        if self.db.in_transaction:raise ValueError('Transaction already active')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT request FROM recovery_job WHERE id=?',(identifier,)).fetchone()
            if old:
                prior=json.loads(old[0])
                if prior['allowed']!=[list(p) for p in sorted(allowed)] or prior['policy']!=policy:raise ValueError('Job policy conflict')
                self.db.execute('COMMIT');return identifier
            live=self.g.live();group=live['snapshot']['group'];inst=instances.optional_current(self.db,group)
            request=dict(group=group,instance=inst['instance'] if inst else None,predecessor=live['snapshot']['predecessor'],allowed=sorted(allowed),policy=policy)
            self.db.execute('INSERT INTO recovery_job VALUES(?,?,?,NULL,NULL)',(identifier,encode(request),'collecting'))
            self.db.execute('COMMIT');return identifier
        except BaseException:
            self.db.execute('ROLLBACK');raise
    def collect(self,*,crash=None):
        """No source I/O while holding the account's write transaction."""
        reports={};count_limit,byte_limit,_,_=self.limits
        for name,source in self.sources.items():
            row=self.db.execute('SELECT cursor FROM recovery_source WHERE id=?',(name,)).fetchone();cursor=row[0] if row else 0
            try:batch=source.scan(cursor,max_messages=count_limit,max_bytes=byte_limit)
            except Exception as exc:
                reports[name]={'status':'unavailable','reason':type(exc).__name__};continue
            if not isinstance(batch,list) or len(batch)>count_limit:raise ValueError('Source batch')
            total=0;last=cursor;parsed=[]
            for pos,wire in batch:
                if type(pos)!=int or pos<=last or not isinstance(wire,bytes):raise ValueError('Source order/bytes')
                last=pos;total+=len(wire)
                if total>byte_limit:raise ValueError('Source bytes')
                try:carrier=select(wire);parse(carrier)
                except (ValueError,TypeError):carrier=None
                discovery=extract_discovery(wire,max_wire_bytes=byte_limit,max_parts=count_limit)
                wrapper=discovery['octets'] if discovery['state']=='candidate' else None
                parsed.append((pos,wire,carrier,wrapper))
            self.db.execute('BEGIN IMMEDIATE')
            try:
                fresh=self.db.execute('SELECT cursor FROM recovery_source WHERE id=?',(name,)).fetchone()
                if (fresh[0] if fresh else 0)!=cursor:raise ValueError('Source cursor changed')
                count,size=self.db.execute('SELECT count(*),coalesce(sum(length(wire)),0) FROM recovery_mail').fetchone()
                unique={digest(w):w for _,w,_,_ in parsed if not self.db.execute('SELECT 1 FROM recovery_mail WHERE digest=?',(digest(w),)).fetchone()}
                if count+len(unique)>count_limit or size+sum(map(len,unique.values()))>byte_limit:raise ValueError('Retained mailbox budget')
                for pos,wire,carrier,wrapper in parsed:
                    ident=digest(wire)
                    self.db.execute('INSERT OR IGNORE INTO recovery_mail VALUES(?,?,?)',(ident,wire,carrier))
                    self.db.execute('INSERT INTO recovery_origin VALUES(?,?,?)',(name,pos,ident))
                    if wrapper is not None:self.add_support(wrapper)
                self.db.execute('INSERT INTO recovery_source VALUES(?,?) ON CONFLICT(id) DO UPDATE SET cursor=excluded.cursor',(name,last))
                if crash:crash('before-source-commit')
                self.db.execute('COMMIT');reports[name]={'status':'collected','messages':len(batch)}
            except BaseException:
                self.db.execute('ROLLBACK');raise
        return reports
    def _designated_writer(self,transition,state,time):
        if transition.get('unsupported') or transition.get('before')!=state['snapshot']:return False
        ctx=json.loads(bytes.fromhex(state['snapshot']['context']));ordering=ctx.get('ordering',{})
        if ordering.get('kind')!='designated-member-v0' or ids(transition['sender'])!=(ordering.get('principal'),ordering.get('device')):return False
        pairs=[p for p in members(state['snapshot']) if p[0]==transition['sender']]
        return len(pairs)==1 and self.recovery._current(pairs[0],'send',time).get('status')=='authorized-unverified'
    def _status(self,job,status,reason=None):
        result=dict(status=status)
        if reason:result['reason']=reason
        self.db.execute('UPDATE recovery_job SET state=?,result=? WHERE id=?',(status,encode(result),job));return result
    def refresh(self,job,*,time,crash=None):
        """Account synchronization trigger: fetch then attempt atomic recovery."""
        sources=self.collect()
        return {'sources':sources,'recovery':self.run(job,time=time,crash=crash)}

    def cancel(self,job):
        self.db.execute("UPDATE recovery_job SET state='cancelled' WHERE id=? AND state!='accepted'",(job,))

    def run(self,job,*,time,crash=None):
        MlsReceive._policy(time,'allow-unverified');deadline=clock.monotonic()+self.max_seconds
        def budget():
            if clock.monotonic()>deadline:raise ValueError('Recovery time budget')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row=self.db.execute('SELECT request,state,chosen,result FROM recovery_job WHERE id=?',(job,)).fetchone()
            if not row:raise ValueError('Unknown job')
            request=json.loads(row[0]);allowed={tuple(p) for p in request['allowed']}
            if row[1]=='cancelled':
                self.db.execute('COMMIT');return {'status':'cancelled'}
            if row[1]=='accepted':
                self.db.execute('COMMIT');return json.loads(row[3])
            state=self.g.live();start=state['snapshot'];inst=instances.optional_current(self.db,start['group'])
            if (start['group'],start['predecessor'],inst['instance'] if inst else None)!=(request['group'],request['predecessor'],request['instance']):
                result=self._status(job,'obsolete');self.db.execute('COMMIT');return result
            if request['policy']!=POLICY:
                result=self._status(job,'waiting-for-policy');self.db.execute('COMMIT');return result
            if row[2]:chosen=json.loads(row[2])
            else:
                raw_candidates=[r[0] for r in self.db.execute('SELECT carrier FROM recovery_mail WHERE carrier IS NOT NULL')]
                raw_candidates += [r[0] for r in self.db.execute('SELECT carrier FROM gt_pending WHERE carrier IS NOT NULL')]
                candidates={digest(raw):raw for raw in raw_candidates}
                if len(candidates)>self.limits[3]:
                    result=self._status(job,'held','candidate-budget');self.db.execute('COMMIT');return result
                chain=[];support=[];failure='waiting-for-gap'
                for _ in range(self.limits[2]):
                    successors={}
                    for raw in candidates.values():
                        value,wire=parse(raw)
                        try:
                            check_binding(value,state['snapshot'])
                            budget()
                            transition=self.g.invoke('receive',state,wire=wire.hex())
                        except (ValueError,RuntimeError) as exc:
                            if str(exc)=='Recovery time budget':raise
                            continue
                        # Count authenticated forks BEFORE policy selection. An
                        # unauthorized branch must not hide writer equivocation.
                        if self._designated_writer(transition,state,time):successors.setdefault(digest(wire),(raw,transition))
                    if len(successors)>1:
                        result=self._status(job,'conflict','authenticated-successors');self.db.execute('COMMIT');return result
                    if not successors:break
                    raw,transition=next(iter(successors.values()))
                    try:self.recovery._structure(transition,allowed,time)
                    except ValueError as exc:
                        result=self._status(job,'held',str(exc));self.db.execute('COMMIT');return result
                    chain.append(raw);state={'checkpoint':transition['checkpoint'],'snapshot':transition['after']}
                    if any(self.recovery._current(p,'receive',time).get('status')!='authorized-unverified' for p in members(transition['after'])):
                        failure='waiting-for-gap';continue
                    # Choose one exact current proof per final added device;
                    # arbitrary/expired cached wrappers cannot poison selection.
                    support=[];seen=set();needed=members(transition['after'])-members(start)
                    from passive_discovery import decode_passive_discovery
                    from passive_discovery_verify import verify_passive_discovery
                    from application_support import supports
                    from mls_receive import LockedIdentity
                    ctx=json.loads(bytes.fromhex(transition['after']['context']))
                    for wrapper, in self.db.execute('SELECT wrapper FROM recovery_support ORDER BY digest'):
                        try:
                            decoded=decode_passive_discovery(wrapper);v=decoded['assertion']['value']
                            credential=(b'email-next/device/v0\0'+bytes.fromhex(v['principal'][5:])+bytes.fromhex(v['device'][5:])).hex()
                            binding=next(b['value'] for b in decoded['identity']['bindings'] if b['digest']==v['binding']);pair=(credential,binding['signingKey'])
                            if pair not in needed or pair in seen or ctx['version']=='1':continue
                            if not supports(v,ctx['application'],'designated-member-v0'):continue
                            if verify_passive_discovery(wrapper,LockedIdentity(self.g.identity),time=time,trust_policy='allow-unverified').get('status')!='snapshot-authorized-unverified':continue
                            support.append(wrapper);seen.add(pair)
                        except (ValueError,KeyError,StopIteration):continue
                    try:remediation_support.validate(self.g,support,transition['after'],start,request['instance'],time)
                    except ValueError:
                        failure='waiting-for-support';continue
                    # Continue to detect any next authenticated fork before
                    # choosing a complete reachable endpoint.
                    failure=None
                else:
                    result=self._status(job,'held','step-budget');self.db.execute('COMMIT');return result
                if not chain or failure:
                    result=self._status(job,failure or 'waiting-for-gap');self.db.execute('COMMIT');return result
                chosen=dict(carriers=[c.hex() for c in chain],support=[w.hex() for w in support])
                self.db.execute('UPDATE recovery_job SET chosen=?,state=? WHERE id=?',(encode(chosen),'ready',job))
            # Ready input survives crashes and never silently selects new proofs.
            self.db.execute('COMMIT')
            if crash:crash('after-ready')
            self.db.execute('BEGIN IMMEDIATE')
            completed=self.db.execute('SELECT state,result FROM recovery_job WHERE id=?',(job,)).fetchone()
            if completed[0]=='cancelled':
                self.db.execute('COMMIT');return {'status':'cancelled'}
            if completed[0]=='accepted':
                self.db.execute('COMMIT');return json.loads(completed[1])
            now=self.g.live()['snapshot'];current=instances.optional_current(self.db,now['group'])
            if (now['group'],now['predecessor'],current['instance'] if current else None)!=(request['group'],request['predecessor'],request['instance']):
                result=self._status(job,'obsolete');self.db.execute('COMMIT');return result
            # A newly fetched authenticated branch can hold an already ready
            # request. It cannot replace its selected proof or carrier bytes.
            probe=self.g.live()
            known_rows=list(self.db.execute('SELECT carrier FROM recovery_mail WHERE carrier IS NOT NULL'))+list(self.db.execute('SELECT carrier FROM gt_pending WHERE carrier IS NOT NULL'))
            known={digest(raw):raw for raw, in known_rows}
            if len(known)>self.limits[3]:
                result=self._status(job,'held','candidate-budget');self.db.execute('COMMIT');return result
            for raw in chosen['carriers']:
                authentic=set()
                for candidate in known.values():
                    budget();value,wire=parse(candidate)
                    try:
                        check_binding(value,probe['snapshot']);candidate_result=self.g.invoke('receive',probe,wire=wire.hex())
                    except (ValueError,RuntimeError):continue
                    if self._designated_writer(candidate_result,probe,time):authentic.add(digest(wire))
                if len(authentic)>1:
                    result=self._status(job,'conflict','authenticated-successors');self.db.execute('COMMIT');return result
                selected=bytes.fromhex(raw);value,wire=parse(selected);check_binding(value,probe['snapshot'])
                transition=self.g.invoke('receive',probe,wire=wire.hex());probe={'checkpoint':transition['checkpoint'],'snapshot':transition['after']}
            result=self.recovery.receive([bytes.fromhex(c) for c in chosen['carriers']],allowed=allowed,time=time,expected_predecessor=request['predecessor'],policy=request['policy'],final_support=[bytes.fromhex(w) for w in chosen['support']],_in_transaction=True)
            self.db.execute('UPDATE recovery_job SET state=?,result=? WHERE id=?',('accepted',encode(result),job))
            if crash:crash('before-commit')
            self.db.execute('COMMIT')
            if crash:crash('after-commit')
            return result
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
