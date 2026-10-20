"""Local HTTP public-evidence demonstrator; not a production account service."""
import re,sqlite3,threading,urllib.request
from contextlib import closing
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
class Relay:
    def __init__(self,path,*,max_bytes=1048576):
        self.path=path;self.max_bytes=max_bytes
        with closing(sqlite3.connect(path,isolation_level=None)) as db:db.execute('CREATE TABLE IF NOT EXISTS transfers(path TEXT PRIMARY KEY,bytes BLOB NOT NULL)')
        outer=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):self.handle_record(False)
            def do_PUT(self):self.handle_record(True)
            def handle_record(self,write):
                if not re.fullmatch('/[0-9a-f]{64}/(offer|anchor|request|result)',self.path):self.send_error(404);return
                with closing(sqlite3.connect(outer.path,isolation_level=None)) as db:
                    old=db.execute('SELECT bytes FROM transfers WHERE path=?',(self.path,)).fetchone()
                    if write:
                        try:n=int(self.headers.get('Content-Length','-1'))
                        except ValueError:n=-1
                        if not 0<=n<=outer.max_bytes:self.send_error(413);return
                        self.connection.settimeout(5);raw=self.rfile.read(n)
                        if len(raw)!=n:self.send_error(400);return
                        if old and old[0]!=raw:self.send_error(409);return
                        db.execute('INSERT OR IGNORE INTO transfers VALUES(?,?)',(self.path,raw));body=b'queued'
                    else:
                        if not old:self.send_error(404);return
                        body=old[0]
                self.send_response(200);self.send_header('Content-Type','application/octet-stream');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);self.server.daemon_threads=True
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.origin='http://127.0.0.1:'+str(self.server.server_port)
    def close(self):self.server.shutdown();self.server.server_close();self.thread.join()
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args):return None
class Channel:
    def __init__(self,origin,*,max_bytes=1048576,timeout=5):
        p=urlsplit(origin)
        if p.scheme!='http' or p.hostname!='127.0.0.1' or not p.port or p.path not in ('','/') or p.query or p.fragment or p.username:raise ValueError('Explicit loopback relay only')
        self.origin=origin.rstrip('/');self.max_bytes=max_bytes;self.timeout=timeout;self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
    def transfer(self,session,kind,raw=None):
        if not re.fullmatch('[0-9a-f]{64}',session) or kind not in ('offer','anchor','request','result'):raise ValueError('Transfer path')
        if raw is not None and (not isinstance(raw,bytes) or len(raw)>self.max_bytes):raise ValueError('Transfer bound')
        request=urllib.request.Request(self.origin+'/'+session+'/'+kind,data=raw,method='GET' if raw is None else 'PUT')
        with self.opener.open(request,timeout=self.timeout) as response:
            data=response.read(self.max_bytes+1)
            if len(data)>self.max_bytes:raise ValueError('Response bound')
            return data
