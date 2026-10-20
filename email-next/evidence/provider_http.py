"""Loopback-only configured HTTPS experiment; not a general HTTP server.

One bounded HTTP/1.1 request per TLS connection, no redirects or token issuance.
Configured credential records and accepted identity keys are caller authority.
Atomic store outcomes distinguish creation from exact retries. No PKIX revocation,
credential provisioning, distributed quota, GC or restore recovery is claimed.
"""
from service_tls import require_http11_protocol
from contextlib import closing
import hashlib
import hmac
import json
import re
import socket
import sqlite3
import ssl
import threading
import time as monotonic_time
from urllib.parse import urlsplit
from provider_control import validate_configuration, current, integer
from passive_discovery import hexadecimal, mailbox_syntax
from provider_store import ProviderStore, QuotaExceeded, ExchangeConflict, AdmissionExpired


def encoded(value):
    return json.dumps(value,separators=(',',':')).encode()


class ProviderHTTP:
    def __init__(self, path, credentials, certfile, keyfile, clock, *, timeout=3, max_header_bytes=16384):
        self.path=path;self.credentials=credentials;self.clock=clock;self.timeout=timeout
        self.max_header_bytes=max_header_bytes
        if not credentials:raise ValueError('Credentials required')
        for token,record in credentials.items():
            if not isinstance(token,str) or not re.fullmatch(r'[A-Za-z0-9._~+/-]+=*',token):raise ValueError('Token spelling')
            if set(record)!={'configuration','notBefore','notAfter','initiatorKey','targetKey','targetMailbox'}:raise ValueError('Credential record schema')
            configuration=validate_configuration(encoded(record['configuration']))
            before,after=integer(record['notBefore']),integer(record['notAfter'])
            if not configuration['notBefore']<=before<=after<=configuration['notAfter']:raise ValueError('Credential lifetime')
            if not all(hexadecimal(record[k],64) for k in ('initiatorKey','targetKey')):raise ValueError('Configured key spelling')
            if mailbox_syntax(record['targetMailbox'])!='syntax-valid':raise ValueError('Mailbox mapping unsupported')
        self.origin=next(iter(credentials.values()))['configuration']['service']
        self.prefix=urlsplit(next(iter(credentials.values()))['configuration']['prefix']).path
        if any(r['configuration']['service']!=self.origin or urlsplit(r['configuration']['prefix']).path!=self.prefix for r in credentials.values()):
            raise ValueError('One origin and prefix per adapter')
        self.authority=urlsplit(self.origin).netloc
        self.max_body=max(r['configuration']['limits']['maxWrapperBytes'] for r in credentials.values())
        self.fail_limit=min(r['configuration']['limits']['failedAuthenticationPerSourcePerMinute'] for r in credentials.values())
        self.context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.minimum_version=ssl.TLSVersion.TLSv1_3
        self.context.load_cert_chain(certfile,keyfile);self.context.set_alpn_protocols(['http/1.1'])
        self.socket=socket.socket();self.socket.bind(('127.0.0.1',0));self.socket.listen(8);self.socket.settimeout(.1)
        self.port=self.socket.getsockname()[1];self.stop_event=threading.Event()
        self.thread=threading.Thread(target=self._serve,daemon=True)
        with closing(sqlite3.connect(path)) as db, db:
            db.execute('CREATE TABLE IF NOT EXISTS http_budget (kind TEXT, subject TEXT, instant INTEGER)')
            db.execute('CREATE TABLE IF NOT EXISTS http_clock (id INTEGER PRIMARY KEY, instant INTEGER)')

    def start(self):self.thread.start();return self
    def close(self):self.stop_event.set();self.thread.join(self.timeout+2);self.socket.close()

    def _budget(self,kind,subject,limit,now,*,consume=True):
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            old=db.execute('SELECT instant FROM http_clock WHERE id=1').fetchone()
            if old and now<old[0]:raise ValueError('HTTP accounting clock rollback')
            db.execute('INSERT INTO http_clock VALUES(1,?) ON CONFLICT(id) DO UPDATE SET instant=excluded.instant',(now,))
            db.execute('DELETE FROM http_budget WHERE instant<=?',(now-60,))
            rows=db.execute('SELECT instant FROM http_budget WHERE kind=? AND subject=? ORDER BY instant',(kind,subject)).fetchall()
            if len(rows)>=limit:raise QuotaExceeded(rows[0][0]+60-now)
            if consume:db.execute('INSERT INTO http_budget VALUES(?,?,?)',(kind,subject,now))

    def _serve(self):
        while not self.stop_event.is_set():
            try:raw,address=self.socket.accept()
            except socket.timeout:continue
            except OSError:break
            raw.settimeout(self.timeout)
            try:
                with self.context.wrap_socket(raw,server_side=True) as conn:
                    try:require_http11_protocol(conn)
                    except ValueError:continue
                    try:status,body,extra=self._request(conn,address[0])
                    except QuotaExceeded as e:status,body,extra=429,{'error':'rateLimited'},{'Retry-After':str(e.retry_after)}
                    except (ValueError,UnicodeError,json.JSONDecodeError):status,body,extra=400,{'error':'invalid'},{}
                    except (socket.timeout,ConnectionError):continue
                    except Exception:status,body,extra=503,{'error':'unavailable'},{}
                    data=encoded(body)
                    header=f'HTTP/1.1 {status} Result\r\nContent-Type: application/json\r\nCache-Control: no-store\r\nConnection: close\r\nContent-Length: {len(data)}\r\n'
                    header+=''.join(f'{k}: {v}\r\n' for k,v in extra.items())
                    conn.sendall(header.encode('ascii')+b'\r\n'+data)
            except (ssl.SSLError,OSError):raw.close()

    def _request(self,conn,source):
        deadline=monotonic_time.monotonic()+self.timeout
        def receive(size):
            remaining=deadline-monotonic_time.monotonic()
            if remaining<=0:raise socket.timeout('Request deadline')
            conn.settimeout(remaining)
            return conn.recv(size)
        data=b''
        while b'\r\n\r\n' not in data:
            if len(data)>=self.max_header_bytes:raise ValueError('Header limit')
            chunk=receive(min(1024,self.max_header_bytes-len(data)))
            if not chunk:raise ValueError('Incomplete headers')
            data+=chunk
        head,body=data.split(b'\r\n\r\n',1)
        lines=head.decode('ascii').split('\r\n')
        match=re.fullmatch(r'(GET|PUT|POST|DELETE|HEAD|OPTIONS|PATCH) ([^\x00-\x20\x7f]+) HTTP/1.1',lines[0])
        if not match:raise ValueError('Request line')
        method,path=match.groups();headers={}
        for line in lines[1:]:
            if ':' not in line:raise ValueError('Header')
            name,value=line.split(':',1);name=name.lower()
            if not re.fullmatch(r'[a-z0-9!#$%&\'*+.^_`|~-]+',name) or name in headers or any((ord(c)<32 and c!='\t') or ord(c)==127 for c in value):raise ValueError('Ambiguous header')
            headers[name]=value.strip(' \t')
        if headers.get('host')!=self.authority or 'transfer-encoding' in headers or 'expect' in headers:raise ValueError('Authority/framing')
        length=headers.get('content-length','0')
        if not re.fullmatch(r'0|[1-9][0-9]{0,8}',length):raise ValueError('Content length')
        length=int(length)
        if length>self.max_body:return 413,{'error':'tooLarge'},{}
        if method=='GET' and length:raise ValueError('GET body')
        now=self.clock();self._budget('failure',source,self.fail_limit,now[0],consume=False)
        auth=headers.get('authorization','');record=None;credential_id=None
        # RFC6750: no applicable credentials has a challenge without an error.
        scheme=re.split(r'[ \t]',auth,maxsplit=1)[0]
        if not auth or scheme.lower()!='bearer':
            self._budget('failure',source,self.fail_limit,now[0])
            return 401,{'error':'unauthorized'},{'WWW-Authenticate':'Bearer'}
        # The scheme is case-insensitive; the selected profile emits one space.
        match=re.fullmatch(r'(?i:Bearer) +([A-Za-z0-9._~+/-]+=*)',auth)
        if match is None:
            self._budget('failure',source,self.fail_limit,now[0])
            return 400,{'error':'invalid'},{'WWW-Authenticate':'Bearer error="invalid_request"'}
        supplied=match[1]
        for token,candidate in self.credentials.items():
            if hmac.compare_digest(supplied,token):record=candidate;credential_id=hashlib.sha256(token.encode()).hexdigest()
        if record is None or not record['notBefore']<=now[0]<=now[1]<=record['notAfter']:
            self._budget('failure',source,self.fail_limit,now[0])
            return 401,{'error':'unauthorized'},{'WWW-Authenticate':'Bearer error="invalid_token"'}
        c=record['configuration'];current(c,now,c['limits'])
        self._budget('credential',credential_id,c['limits']['requestsPerMinute'],now[0])
        if length>c['limits']['maxWrapperBytes']:return 413,{'error':'tooLarge'},{}
        if headers.get('content-encoding') is not None or (method=='PUT' and headers.get('content-type')!='application/json'):
            return 415,{'error':'unsupportedRepresentation'},{}
        if not path.startswith(self.prefix):return 404,{'error':'notFound'},{}
        suffix=path[len(self.prefix):]
        route=re.fullmatch(r'exchanges/([0-9a-f]{64})(/(request|response))?',suffix)
        pending=re.fullmatch(r'pending(?:\?after=([0-9a-f]{64}))?',suffix)
        if suffix=='configuration':allowed='GET';operation='configuration-read'
        elif pending:allowed='GET';operation='pending-read'
        elif route:allowed='PUT' if route[3] else 'GET';operation={'request':'request-write','response':'response-write',None:'exchange-read'}[route[3]]
        else:return 404,{'error':'notFound'},{}
        if method!=allowed:return 405,{'error':'invalid'},{'Allow':allowed}
        if operation not in c['operations']:return 403,{'error':'unauthorized'},{'WWW-Authenticate':'Bearer error="insufficient_scope"'}
        while len(body)<length:
            chunk=receive(min(65536,length-len(body)))
            if not chunk:raise ValueError('Incomplete body')
            body+=chunk
        if len(body)!=length:raise ValueError('Trailing/pipelined bytes')
        now=self.clock()
        if not record['notBefore']<=now[0]<=now[1]<=record['notAfter']:
            return 401,{'error':'unauthorized'},{'WWW-Authenticate':'Bearer error="invalid_token"'}
        current(c,now,c['limits'])
        store=ProviderStore(self.path)
        try:
            status=200
            if suffix=='configuration':result=c
            elif pending:result=store.pending(c,time=now,after=pending[1])
            else:
                identifier=route[1]
                if route[3]=='request':
                    result=store.put_request(c,record['initiatorKey'],identifier,body,time=now);status=201 if result['created'] else 200
                elif route[3]=='response':
                    result=store.put_response(c,record['initiatorKey'],record['targetKey'],identifier,body,time=now,target_mailbox=record['targetMailbox']);status=201 if result['created'] else 200
                else:result=store.get(c,identifier,time=now)
                result={'profile':c['profile'],'id':identifier,'request':json.loads(result['request']),
                    'response':json.loads(result['response']) if result['response'] else None,'status':result['status']}
            if len(encoded(result))>c['limits']['maxResponseBytes']:return 503,{'error':'unavailable'},{}
            return status,result,{}
        except KeyError:return 404,{'error':'notFound'},{}
        except ExchangeConflict:return 409,{'error':'conflict'},{}
        except AdmissionExpired:return 409,{'error':'conflict'},{}
        finally:store.close()
