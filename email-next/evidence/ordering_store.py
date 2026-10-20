"""Private durable vote store; caller must quarantine restored/cloned signing state."""
from contextlib import closing
import os
from pathlib import Path
import sqlite3
from ordering_certificates import Proof,unsigned,sign,encode,decode_event,digest
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat

class VoteStore:
    def __init__(self,path,*,scope,keys,f,signer,key,create=False):
        self.path=str(Path(path).resolve());self.pid=os.getpid()
        self.scope=scope;self.keys=keys;self.f=f;self.signer=signer;self.key=key
        if signer not in keys or key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw).hex()!=keys[signer]:raise ValueError("signer key mismatch")
        config=digest({"scope":scope,"keys":keys,"faultBound":str(f)})
        if not create and not Path(self.path).exists():raise ValueError('missing signing history')
        with closing(sqlite3.connect(self.path)) as db:
            db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA synchronous=FULL')
            if create:
                with db:
                    db.execute('CREATE TABLE state(scope TEXT PRIMARY KEY, signer TEXT, config TEXT, minimum TEXT, prepared BLOB)')
                    db.execute('CREATE TABLE votes(kind TEXT, view TEXT, bytes BLOB, candidate TEXT, proof BLOB NOT NULL, PRIMARY KEY(kind,view))')
                    db.execute('INSERT INTO state VALUES(?,?,?,?,?)',(scope,signer,config,'0',b''))
            db.execute('CREATE TABLE IF NOT EXISTS candidate_dependencies(id TEXT PRIMARY KEY,bytes BLOB NOT NULL)')
            row=db.execute('SELECT scope,signer,config FROM state').fetchone()
            if row!=(scope,signer,config):raise ValueError('store binding')
    def proof(self,raw):return Proof(raw,scope=self.scope,keys=self.keys,f=self.f)
    def retained_proof(self,kind,view):
        with closing(sqlite3.connect(self.path)) as db:
            row=db.execute('SELECT proof FROM votes WHERE kind=? AND view=?',(kind,str(view))).fetchone()
            if row is None:raise ValueError('unknown vote')
            return row[0]
    def retained_candidates(self,raw):
        """Exact public bodies needed by a fully verified retained proof graph."""
        proof=self.proof(raw)
        required=sorted({o['body']['candidate'] for o in proof.nodes.values() if o['body']['kind']=='proposal'})
        with closing(sqlite3.connect(self.path)) as db:
            values=[]
            for ident in required:
                row=db.execute('SELECT bytes FROM candidate_dependencies WHERE id=?',(ident,)).fetchone()
                if row is None:raise ValueError('Missing exact candidate dependency')
                values.append(row[0])
            return values
    def vote(self,kind,raw=None,*,target=None,authority,crash=None,candidate_bytes=None):
        if os.getpid()!=self.pid:raise ValueError('forked signer')
        if kind not in ('prepare','commit','report'):raise ValueError('vote kind')
        proof=self.proof(raw) if raw is not None else None
        if kind!='report' and (proof is None or proof.result['kind']!={'prepare':'proposal','commit':'prepared'}[kind]):raise ValueError('input proof')
        view=target if kind=='report' else proof.result['view']
        if type(view) is not int or not 0<=view<2**64:raise ValueError('view')
        with closing(sqlite3.connect(self.path,isolation_level=None)) as db:
            db.execute('PRAGMA synchronous=FULL');db.execute('BEGIN IMMEDIATE')
            try:
                if not authority():raise ValueError('current authority veto')
                if candidate_bytes is not None:
                    from ordering_mls import candidate_id
                    from ordering_scope import scope_digest
                    if not isinstance(candidate_bytes,list):raise ValueError('Candidate dependency list')
                    incoming={}
                    for raw_candidate in candidate_bytes:
                        value=decode_event(raw_candidate)['value']
                        if encode(value)!=raw_candidate or scope_digest(value['plan']['scope'])!=self.scope:raise ValueError('Candidate dependency bytes/scope')
                        ident=candidate_id(value)
                        if ident in incoming:raise ValueError('Duplicate candidate dependency')
                        incoming[ident]=raw_candidate
                    required={o['body']['candidate'] for o in proof.nodes.values() if o['body']['kind']=='proposal'} if proof else set()
                    if not set(incoming).issubset(required):raise ValueError('Extra candidate dependency')
                    for ident in required:
                        old=db.execute('SELECT bytes FROM candidate_dependencies WHERE id=?',(ident,)).fetchone()
                        raw_candidate=incoming.get(ident)
                        if old and raw_candidate is not None and old[0]!=raw_candidate:raise ValueError('Candidate dependency conflict')
                        if not old and raw_candidate is None:raise ValueError('Missing exact candidate dependency')
                        if not old:db.execute('INSERT INTO candidate_dependencies VALUES(?,?)',(ident,raw_candidate))
                minimum,retained=db.execute('SELECT minimum,prepared FROM state').fetchone();minimum=int(minimum)
                prior=db.execute('SELECT bytes,candidate FROM votes WHERE kind=? AND view=?',(kind,str(view))).fetchone()
                candidate=proof.result['candidate'] if proof else ''
                if prior:
                    if kind!='report' and prior[1]!=candidate:raise ValueError('equivocation refused')
                    db.execute('COMMIT');return prior[0]
                if view<minimum or (kind=='report' and view<=minimum):raise ValueError('fenced view')
                previous=self.proof(retained) if retained else None
                if kind=='prepare':
                    if previous:
                        p=previous.result;highest=proof.result['highest']
                        if p['view']>highest or (p['view']==highest and p['candidate']!=candidate):raise ValueError('local prepared lock')
                    fields={'proposal':proof.root}
                elif kind=='commit':
                    local=db.execute("SELECT candidate FROM votes WHERE kind='prepare' AND view=?",(str(view),)).fetchone()
                    if local!=(candidate,):raise ValueError('missing local prepare')
                    if previous and previous.result['view']>view:raise ValueError('older prepared')
                    db.execute('UPDATE state SET prepared=?',(raw,));fields={'prepared':proof.root}
                else:
                    fields={'prepared':previous.root if previous else ''}
                    db.execute('UPDATE state SET minimum=?',(str(view),))
                result=encode(sign(unsigned(kind,self.scope,view,self.signer,**fields),self.key))
                db.execute('INSERT INTO votes VALUES(?,?,?,?,?)',(kind,str(view),result,candidate,raw if raw is not None else retained))
                if crash:crash('before-durable')
                db.execute('COMMIT')
                if crash:crash('after-durable')
                return result
            except BaseException:
                if db.in_transaction:db.execute('ROLLBACK')
                raise
