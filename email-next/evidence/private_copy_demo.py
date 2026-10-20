"""Loopback synthetic signed/SMTP private-copy client demonstration, not mailbox access."""
import json,secrets
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
from test_private_copy_fanout import PrivateFanout
from client_flow import ClientFlow
from journal_button_view import derive_button_view
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from mls_mime import unpack

if __name__=='__main__':
    fixture=PrivateFanout();fixture.setUp();fixture.test_independent_question_copies_real_smtp_and_private_answer();token=secrets.token_hex(32)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send(self,status,body,kind='application/json'):
            self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def do_GET(self):
            if self.path=='/':
                data=json.dumps(fixture.presentation).replace('<','\\u003c')
                html='<meta charset="utf-8"><title>Private copy experiment</title><main></main><script type="module">import{mountPrivateCopy}from"/private-copy-ui.mjs";mountPrivateCopy(document.querySelector("main"),'+data+',async()=>{const r=await fetch("/reply",{method:"POST",headers:{"X-Session":"'+token+'","Content-Type":"application/json"},body:"{}"});if(!r.ok)throw Error();return r.json();});</script>'
                return self.send(200,html.encode(),'text/html; charset=utf-8')
            if self.path=='/private-copy-ui.mjs':return self.send(200,Path(__file__).with_name('private-copy-ui.mjs').read_bytes(),'text/javascript')
            self.send(404,b'{}')
        def do_POST(self):
            if self.path!='/reply' or self.headers.get('X-Session')!=token:return self.send(403,b'{}')
            if self.headers.get('Content-Length')!='2' or self.rfile.read(2)!=b'{}':return self.send(400,b'{}')
            try:
                g=fixture.groups[1];ref={k:fixture.events[1][k] for k in ('principal','conversation','event')};view=derive_button_view(g['receiver'].receiver.journal,ref)
                client=ClientFlow(g['receiver'],key=g['target']['key'],envelope_sender=g['target_address'],recipients=[g['source']])
                retained=g['receiver'].db.execute("SELECT source_token FROM client_actions WHERE id='browseranswer'").fetchone()
                wire=client.answer('browseranswer',ref,'a'*32,retained[0] if retained else view['sourceToken'],time=fixture.time)
                previous=g['receiver'].db.execute("SELECT 1 FROM sender_attempts WHERE delivery='browseranswer' AND state='accepted'").fetchone()
                if not previous:
                    smtp=LocalSMTP()
                    with SenderWorker(g['receiver']) as worker:worker.submit('browseranswer',port=smtp.port,time=fixture.time)
                    smtp.done();g['sender'].receiver.receive(unpack(smtp.wire),time=fixture.time,trust_policy='allow-unverified')
                visible={k:fixture.events[0][k] for k in ('principal','conversation','event')};count=len(derive_button_view(fixture.groups[0]['sender'].receiver.journal,visible)['heads'])
                self.send(200,json.dumps(dict(visibleAnswers=count)).encode())
            except ValueError:self.send(409,b'{}')
    server=HTTPServer(('127.0.0.1',0),Handler);print(json.dumps(dict(url='http://127.0.0.1:'+str(server.server_port))),flush=True)
    try:server.serve_forever()
    finally:server.server_close();fixture.tearDown()
