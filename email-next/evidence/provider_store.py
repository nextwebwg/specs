"""Durable exchange experiment, not a provider service.

Caller supplies authenticated credential role, validated configuration and keys.
One database represents one configured service origin/prefix. Admission budgets and
immutable snapshot pages are durable; no retention garbage collection is supplied.
No token verification, HTTP per-credential/failed-auth counters, grant revocation,
backup/restore detection, HTTP handling or identity/MLS authorization is supplied.
"""
import json
import sqlite3
import secrets
from provider_control import validate_request, validate_response, current, validate_configuration


class ExchangeConflict(ValueError):
    pass


class AdmissionExpired(ValueError):
    pass


class QuotaExceeded(ValueError):
    def __init__(self, retry_after):
        super().__init__('Quota exhausted')
        self.retry_after=max(1,int(retry_after))


class ProviderStore:
    def __init__(self, path):
        self.db=sqlite3.connect(path,isolation_level=None)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('''CREATE TABLE IF NOT EXISTS exchanges (
            account TEXT NOT NULL, grant_id TEXT NOT NULL, id TEXT NOT NULL,
            configuration BLOB NOT NULL, request BLOB NOT NULL, response BLOB,
            expires INTEGER NOT NULL, expired INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY(account,grant_id,id))''')

        self.db.execute('CREATE TABLE IF NOT EXISTS grants (account TEXT, grant_id TEXT, configuration BLOB NOT NULL, PRIMARY KEY(account,grant_id))')
        self.db.execute('CREATE TABLE IF NOT EXISTS admissions (account TEXT, grant_id TEXT, instant INTEGER NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS accounting_clock (singleton INTEGER PRIMARY KEY, instant INTEGER NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS polls (account TEXT, grant_id TEXT, instant INTEGER NOT NULL, PRIMARY KEY(account,grant_id))')
        self.db.execute('CREATE TABLE IF NOT EXISTS cursor_pages (token TEXT PRIMARY KEY, account TEXT NOT NULL, grant_id TEXT NOT NULL, expires INTEGER NOT NULL, ids TEXT NOT NULL, snapshot TEXT NOT NULL, next_token TEXT)')

    def close(self):
        self.db.close()

    def _scope(self, config, role, time):
        # Revalidate caller configuration, but do not mistake it for token authentication.
        c=validate_configuration(json.dumps(config,separators=(',',':')).encode())
        if c['role'] != role: raise PermissionError('Credential role mismatch')
        current(c,time,c['limits'])
        shared={k:v for k,v in c.items() if k not in ('role','operations')}
        serialized=json.dumps(shared,sort_keys=True,separators=(',',':')).encode()
        return serialized

    def _expire(self,config,identifier,time):
        shared=json.dumps({k:v for k,v in config.items() if k not in ('role','operations')},sort_keys=True,separators=(',',':')).encode()
        self.db.execute('UPDATE exchanges SET expired=1 WHERE account=? AND grant_id=? AND id=? AND configuration=? AND response IS NULL AND expires<?',
            (config['account'],config['grant'],identifier,shared,time[0]))

    def _accounting(self,config,shared,time):
        """Inside BEGIN IMMEDIATE; first-seen configurations freeze local limits."""
        now=time[0]
        clock=self.db.execute('SELECT instant FROM accounting_clock WHERE singleton=1').fetchone()
        if clock and now<clock[0]:raise ValueError('Accounting clock rollback')
        self.db.execute('INSERT INTO accounting_clock VALUES(1,?) ON CONFLICT(singleton) DO UPDATE SET instant=excluded.instant',(now,))
        previous=self.db.execute('SELECT configuration FROM grants WHERE account=? AND grant_id=?',(config['account'],config['grant'])).fetchone()
        if previous and previous[0]!=shared:raise ExchangeConflict('Grant configuration changed')
        for account,raw in self.db.execute('SELECT account,configuration FROM grants'):
            other=json.loads(raw)
            if (other['service'],other['prefix'])!=(config['service'],config['prefix']):raise ExchangeConflict('Different service database')
            fields=['maxPendingPerService','newRequestsPerServicePerMinute']
            if account==config['account']:fields+=['maxPendingPerAccount','newRequestsPerAccountPerMinute']
            if any(other['limits'][f]!=config['limits'][f] for f in fields):raise ExchangeConflict('Aggregate limits disagree')
        self.db.execute('INSERT OR IGNORE INTO grants VALUES(?,?,?)',(config['account'],config['grant'],shared))
        self.db.execute('UPDATE exchanges SET expired=1 WHERE response IS NULL AND expires<?',(now,))
        self.db.execute('DELETE FROM admissions WHERE instant<=?',(now-60,))
        self.db.execute('DELETE FROM cursor_pages WHERE expires<?',(now,))
        return now

    def _admission_budget(self,c,now):
        limits=c['limits']
        scopes=[('account=? AND grant_id=?',(c['account'],c['grant']),'maxPendingPerGrant','newRequestsPerMinute'),
                ('account=?',(c['account'],),'maxPendingPerAccount','newRequestsPerAccountPerMinute'),
                ('1=1',(),'maxPendingPerService','newRequestsPerServicePerMinute')]
        for where,args,pending,rate in scopes:
            count=self.db.execute('SELECT count(*) FROM exchanges WHERE '+where+' AND response IS NULL AND expired=0',args).fetchone()[0]
            if count>=limits[pending]:raise QuotaExceeded(limits['minPollIntervalSeconds'])
            instants=[r[0] for r in self.db.execute('SELECT instant FROM admissions WHERE '+where+' ORDER BY instant',args)]
            if len(instants)>=limits[rate]:raise QuotaExceeded(instants[0]+60-now)

    def pending(self,config,*,time,after=None):
        shared=self._scope(config,'target',time)
        if after is not None:
            from passive_discovery import hexadecimal
            if not hexadecimal(after,64):raise ValueError('Cursor spelling')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            now=self._accounting(config,shared,time);c=config;l=c['limits']
            if after is None:
                last=self.db.execute('SELECT instant FROM polls WHERE account=? AND grant_id=?',(c['account'],c['grant'])).fetchone()
                if last and now-last[0]<l['minPollIntervalSeconds']:raise QuotaExceeded(l['minPollIntervalSeconds']-(now-last[0]))
                active=self.db.execute('SELECT count(DISTINCT snapshot) FROM cursor_pages WHERE account=? AND grant_id=?',(c['account'],c['grant'])).fetchone()[0]
                if active>=l['maxActiveCursorsPerGrant']:raise QuotaExceeded(l['minPollIntervalSeconds'])
                ids=[r[0] for r in self.db.execute('SELECT id FROM exchanges WHERE account=? AND grant_id=? AND response IS NULL AND expired=0 ORDER BY id',(c['account'],c['grant']))]
                if len(ids)>l['maxPendingPerGrant']:raise ValueError('Pending bound inconsistent')
                pages=[ids[i:i+l['pendingPageSize']] for i in range(0,len(ids),l['pendingPageSize'])] or [[]]
                tokens=[secrets.token_hex(32) for _ in pages]
                snapshot=secrets.token_hex(32);expires=now+l['cursorLifetimeSeconds']
                # Immutable subsequent pages make lost-response retries recoverable.
                for i in range(1,len(pages)):
                    self.db.execute('INSERT INTO cursor_pages VALUES(?,?,?,?,?,?,?)',(tokens[i],c['account'],c['grant'],expires,json.dumps(pages[i]),snapshot,tokens[i+1] if i+1<len(pages) else None))
                ids=pages[0];token=tokens[1] if len(pages)>1 else None
                self.db.execute('INSERT INTO polls VALUES(?,?,?) ON CONFLICT(account,grant_id) DO UPDATE SET instant=excluded.instant',(c['account'],c['grant'],now))
            else:
                row=self.db.execute('SELECT ids,expires,next_token FROM cursor_pages WHERE token=? AND account=? AND grant_id=?',(after,c['account'],c['grant'])).fetchone()
                if row is None or row[1]<time[1]:raise ValueError('Unknown or expired cursor')
                ids=json.loads(row[0]);token=row[2]
            selected=[]
            for identifier in ids:
                row=self._row(c,identifier)
                if row is not None and row[2] is None and not row[4]:selected.append(identifier)
            self.db.execute('COMMIT')
            return {'profile':c['profile'],'ids':selected,'next':token}
        except BaseException:
            self.db.execute('ROLLBACK');raise

    def _row(self, config, identifier):
        return self.db.execute('SELECT configuration,request,response,expires,expired FROM exchanges WHERE account=? AND grant_id=? AND id=?',
            (config['account'],config['grant'],identifier)).fetchone()

    def _result(self,row,time):
        if row is None: raise KeyError('Unknown exchange')
        status='responded' if row[2] is not None else ('expired' if row[4] or time[0]>row[3] else 'pending')
        return {'status':status,'request':row[1],'response':row[2],
                'effects_applied':False,'identity_authorized':False}

    def put_request(self, config, public_key, identifier, octets, *, time):
        shared=self._scope(config,'initiator',time)
        validated=validate_request(octets,config,public_key,route_id=identifier,time=time)
        self._expire(config,identifier,time)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            now=self._accounting(config,shared,time)
            row=self._row(config,identifier)
            if row:
                if row[0]!=shared or row[1]!=octets: raise ExchangeConflict('Immutable request collision')
                result=self._result(row,time)
                result['created']=False
            else:
                if validated['new_admission_time']!='within-intervals': raise ValueError('Request not current')
                self._admission_budget(config,now)
                self.db.execute('INSERT INTO admissions VALUES(?,?,?)',(config['account'],config['grant'],now))
                self.db.execute('INSERT INTO exchanges (account,grant_id,id,configuration,request,response,expires) VALUES (?,?,?,?,?,?,?)',
                    (config['account'],config['grant'],identifier,shared,octets,None,validated['value']['notAfter']))
                result=self._result(self._row(config,identifier),time)
                result['created']=True
            self.db.execute('COMMIT');return result
        except BaseException:
            self.db.execute('ROLLBACK');raise

    def put_response(self, config, initiator_key, target_key, identifier, octets, *, time, target_mailbox):
        shared=self._scope(config,'target',time)
        # Keep selection, validation and commit under one write transaction.
        self._expire(config,identifier,time)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row=self._row(config,identifier)
            if row is None: raise KeyError('Unknown exchange')
            if row[0]!=shared: raise ExchangeConflict('Grant configuration changed')
            validated=validate_response(octets,row[1],config,initiator_key,target_key,
                route_id=identifier,time=time,target_mailbox=target_mailbox)
            if row[2] is not None:
                if row[2]!=octets: raise ExchangeConflict('Immutable response collision')
            else:
                if row[4] or validated['new_admission_time']!='within-intervals': raise AdmissionExpired('Response not current')
                self.db.execute('UPDATE exchanges SET response=? WHERE account=? AND grant_id=? AND id=?',
                    (octets,config['account'],config['grant'],identifier))
            result=self._result(self._row(config,identifier),time)
            result['created']=row[2] is None
            self.db.execute('COMMIT');return result
        except BaseException:
            self.db.execute('ROLLBACK');raise

    def get(self,config,identifier,*,time):
        if config.get('role') not in ('initiator','target'):raise PermissionError('Credential role')
        shared=self._scope(config,config['role'],time)
        self._expire(config,identifier,time)
        row=self._row(config,identifier)
        if row is not None and row[0]!=shared:raise ExchangeConflict('Grant configuration changed')
        return self._result(row,time)
