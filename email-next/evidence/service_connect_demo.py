"""Reviewable synthetic account consent; not a native browser/keychain adapter."""
import hashlib,json,secrets,threading,uuid
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
import test_service_authorization as fixture
from vault_fixture import NativeAuthorization
from service_authorization_client import bind_loopback,receive_loopback_callback,link_account
from event_encoding import encode_event,decode_event
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from mls_mime import unpack

if __name__=='__main__':
    fixture.ServiceAuthorization.setUpClass();demo=fixture.ServiceAuthorization();demo.simulated_account='Demo booking account';demo.setUp();session=secrets.token_hex(32);state=dict(stage='disconnected');listeners=[];threads=[]
    def callback(listener,redirect,attempt):
        client=NativeAuthorization(demo.root/'vault.sqlite',demo.reg,key=demo.key,clock=lambda:demo.now)
        try:
            url=receive_loopback_callback(listener,redirect);client.callback(attempt,url,demo.https.exchange);state.update(stage='signed-in')
        except Exception as error:state.update(stage='held',reason=type(error).__name__+': '+str(error))
        finally:client.close();listener.close()
    def deliver_question():
        f=demo.f;old=f.args[1];record=next(r for r in f.peer_sender.receiver.journal.snapshot(old['conversation']) if r['reference']==old);event=decode_event(record['octets'][0])['value'];event['event']=uuid.uuid4().hex;ref={k:event[k] for k in ('principal','conversation','event')};event['operation']['serviceAction']['question']=ref
        with f.store.connect() as db:
            action=json.loads(db.execute('SELECT data FROM action').fetchone()[0]);action['question']=ref;db.execute('UPDATE action SET data=?',(json.dumps(action),))
        wire=f.sender.prepare('9'*32,encode_event(event),key=f.f.creator['key'],envelope_sender=f.source,recipients=[f.destination],time=f.time)
        smtp=LocalSMTP()
        with SenderWorker(f.sender) as worker:worker.submit('9'*32,port=smtp.port,time=f.time)
        smtp.done();payload=unpack(smtp.wire);result=f.peer_sender.receiver.receive(payload,time=f.time,trust_policy='allow-unverified')
        if result['applicationState']!='accepted':raise ValueError('Question not accepted')
        carrier=hashlib.sha256(payload).hexdigest();view=f.flow.view(ref,carrier,time=f.time);f.args=('8'*32,ref,carrier,view['options'][0]['id'],view['sourceToken'])
        state.update(stage='linked',question=view)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send(self,code,value,kind='application/json'):
            raw=value if isinstance(value,bytes) else json.dumps(value).encode();self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        def do_GET(self):
            if self.path=='/state':return self.send(200,state)
            if self.path!='/':return self.send(404,{})
            script='''const session=SESSION;const status=document.querySelector('[role=status]');async function post(path){const r=await fetch(path,{method:'POST',headers:{'X-Session':session,'Content-Type':'application/json'},body:'{}'});if(!r.ok)throw Error('held');return r.json();}document.querySelector('#connect').onclick=async()=>{const v=await post('/connect');const a=document.querySelector('#external');a.href=v.url;a.hidden=false;status.textContent='Open separate service consent';};document.querySelector('#link').onclick=async()=>{await post('/link');await update();};document.querySelector('#answer').onclick=async()=>{const v=await post('/answer');status.textContent='Service result: '+v.state+'; effects: '+v.effects;};async function update(){const s=await(await fetch('/state')).json();document.querySelector('#link').hidden=s.stage!=='signed-in';document.querySelector('#answer').hidden=!['linked','answered'].includes(s.stage);if(s.question)document.querySelector('#question').textContent=s.question.text;if(s.stage==='signed-in')status.textContent='Signed in. Choose whether to link this principal.';if(s.stage==='linked')status.textContent='Principal linked. Protected question received over SMTP.';}setInterval(update,300);'''.replace('SESSION',json.dumps(session))
            html='<meta charset="utf-8"><title>Connect a service</title><main><h1>Service account connection</h1><p>Synthetic demonstration: separate service consent, no real account or password.</p><button id="connect">Connect service</button><a id="external" hidden target="_blank" rel="noopener noreferrer">Open service in external browser</a><button id="link" hidden>Link my Email Next principal</button><h2 id="question"></h2><button id="answer" hidden>Reserve seat</button><div role="status"></div></main><script type="module">'+script+'</script>'
            self.send(200,html.encode(),'text/html; charset=utf-8')
        def do_POST(self):
            if self.headers.get('X-Session')!=session:return self.send(403,{})
            if self.headers.get('Content-Length')!='2' or self.rfile.read(2)!=b'{}':return self.send(400,{})
            try:
                if self.path=='/connect':
                    if state['stage']!='disconnected':raise ValueError('Pending connection')
                    listener,redirect=bind_loopback();listeners.append(listener);url,attempt=demo.client.start(redirect);state.update(stage='connecting');t=threading.Thread(target=callback,args=(listener,redirect,attempt),daemon=True);threads.append(t);t.start();return self.send(200,dict(url=url))
                if self.path=='/link':
                    if state['stage']!='signed-in':raise ValueError('Sign in first')
                    token=demo.client.access_token();f=demo.f
                    link_account(demo.client,demo.https,device=f.peer,identity_bundle=f.f.bundles[f.peer['principal']],identity_store=f.peer_identity,binary=f.f.binary,token=token,time=f.time)
                    f.credential[0]=token;deliver_question();return self.send(200,dict(stage='linked'))
                if self.path=='/answer':
                    if state['stage'] not in ('linked','answered'):raise ValueError('Link first')
                    result=demo.f.flow.activate(*demo.f.args,time=demo.f.time);state.update(stage='answered');return self.send(200,dict(result,effects=demo.f.count()))
                self.send(404,{})
            except ValueError as error:
                state.update(stage='held',reason=str(error));self.send(409,dict(state='held'))
    server=HTTPServer(('127.0.0.1',0),Handler);print(json.dumps(dict(url='http://127.0.0.1:'+str(server.server_port))),flush=True)
    try:server.serve_forever()
    finally:
        server.server_close()
        for listener in listeners:listener.close()
        for t in threads:t.join(1)
        demo.doCleanups();fixture.ServiceAuthorization.tearDownClass()
