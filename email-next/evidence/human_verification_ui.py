"""Loopback-only trusted confirmation surface; bearer is local UI capability, not peer proof."""
import hmac,json,secrets,threading
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
from identity_store import IdentityStore
from human_verification import HumanVerification

class ConfirmationUI:
    def __init__(self,path,*,account,local_principal,session,comparison,time,not_before,not_after,continuity,clock=None):
        import time as local_time
        self.clock=clock or (lambda:dict.fromkeys(('earliest','latest'),str(int(local_time.time()))))
        self.path=path;self.account=account;self.local_principal=local_principal;self.session=session;self.comparison=comparison
        self.options=dict(time=time,not_before=not_before,not_after=not_after,continuity=continuity);self.token=secrets.token_urlsafe(32);self.decision=secrets.token_hex(16)
        owner=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def send(self,status,data,kind='application/json'):
                payload=json.dumps(data).encode() if kind=='application/json' else data
                self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(payload)));self.send_header('Cache-Control','no-store');self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'");self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(payload)
            def trusted(self):
                return self.headers.get('Host')==owner.host and hmac.compare_digest(self.headers.get('X-Local-Verification',''),owner.token) and self.headers.get('Origin') in (None,owner.origin)
            def do_GET(self):
                if self.headers.get('Host')!=owner.host:return self.send(403,dict(error='Local host required'))
                if self.path=='/':return self.send(200,Path(__file__).with_name('human-verification.html').read_bytes(),'text/html; charset=utf-8')
                if self.path=='/ui.js':return self.send(200,Path(__file__).with_name('human-verification-ui.js').read_bytes(),'text/javascript; charset=utf-8')
                if self.path=='/session' and self.trusted():return self.send(200,dict(comparison=owner.comparison,explanation='Verification uses this client’s configured validity and ordinary account-continuity policy. You can withdraw it in the client.'))
                self.send(403,dict(error='Local UI capability required'))
            def do_POST(self):
                if self.path!='/confirm' or not self.trusted() or self.headers.get('Origin')!=owner.origin:return self.send(403,dict(error='Trusted local confirmation required'))
                try:
                    size=int(self.headers.get('Content-Length','0'))
                    if not 0<size<=16384 or self.headers.get('Content-Type')!='application/json':raise ValueError('Bounded JSON required')
                    body=json.loads(self.rfile.read(size))
                    if not isinstance(body,dict) or set(body)!={'comparison','channel','independentlyConfirmed'} or body['independentlyConfirmed'] is not True:raise ValueError('Explicit independent comparison required')
                    identity=IdentityStore(owner.path)
                    try:
                        verifier=HumanVerification(identity,account=owner.account,local_principal=owner.local_principal)
                        result=verifier.confirm(owner.decision,owner.session,body['comparison'],channel=body['channel'],**dict(owner.options,time=owner.clock()))
                    finally:identity.close()
                    self.send(200,result)
                except (ValueError,KeyError,TypeError) as error:self.send(400,dict(error=str(error)))
        self.server=HTTPServer(('127.0.0.1',0),Handler);self.host='127.0.0.1:'+str(self.server.server_port);self.origin='http://'+self.host;self.url=self.origin+'/#'+self.token
    def start(self):self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();return self
    def close(self):self.server.shutdown();self.server.server_close();self.thread.join()
