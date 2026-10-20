"""Local synthetic restore UI; no arbitrary path accepted over HTTP."""
import json,secrets,signal
from pathlib import Path
from http.server import HTTPServer,BaseHTTPRequestHandler
from test_safe_restore import SafeRestore

def main():
    fixture=SafeRestore();fixture.setUp();nonce=secrets.token_hex(32);workspace=fixture.workspace
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def allowed(self):return self.headers.get('Host')=='127.0.0.1:'+str(self.server.server_port)
        def do_GET(self):
            if not self.allowed() or self.path!='/':self.send_error(404);return
            data=Path(__file__).with_name('restore-demo.html').read_bytes().replace(b'CLIENT_NONCE',nonce.encode());self.reply(200,data,'text/html')
        def reply(self,code,data,mime='application/json'):
            self.send_response(code);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
        def do_POST(self):
            if not self.allowed() or self.headers.get('X-Restore-Client')!=nonce:self.send_error(403);return
            try:
                n=int(self.headers.get('Content-Length','0'))
                if not 0<n<1024:raise ValueError('Request size')
                value=json.loads(self.rfile.read(n));result={}
                if self.path=='/import':workspace.import_history(fixture.source);result={'rows':workspace.view()}
                elif self.path=='/pair':workspace.start_fresh(fixture.binary,principal=fixture.f.a['principal'])
                elif self.path=='/new':
                    if value.get('confirmed') is not True:raise ValueError('Confirm that contacts must accept your new identity')
                    device=workspace.start_fresh(fixture.binary);workspace.activate_new_identity(time=dict.fromkeys(('earliest','latest'),str(device['time'])))
                else:raise ValueError('Unknown local action')
                self.reply(200,json.dumps(result).encode())
            except Exception as exc:self.reply(400,json.dumps({'error':str(exc)}).encode())
    server=HTTPServer(('127.0.0.1',0),Handler);print('http://127.0.0.1:'+str(server.server_port),flush=True)
    def stop(*args):raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM,stop)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close();fixture.doCleanups()
if __name__=='__main__':main()
