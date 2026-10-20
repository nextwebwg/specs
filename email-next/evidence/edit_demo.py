"""Synthetic signed SMTP edits, immutable originals and explicit conflict resolution."""
import json,secrets
from http.server import BaseHTTPRequestHandler,HTTPServer
from test_joined_edits import JoinedEdits
from journal_edit_view import view
from client_edits import prepare
from sender_worker import SenderWorker
from test_sender_release import LocalSMTP
from mls_mime import unpack

if __name__=='__main__':
    demo=JoinedEdits();demo.setUp();root=demo.event();root['operation']['text']='Meet Tuesday';demo.send(root);reference=demo.ref(root);session=secrets.token_hex(32);sequence=0
    def state():
        local=view(demo.sender.receiver,reference);shown=view(demo.peer_sender.receiver,reference)
        return dict(sourceToken=local['sourceToken'],heads=shown.get('heads',[]),versions=[dict(reference=r['ref'],state=r['state'],text=r.get('event',{}).get('operation',{}).get('text','')) for r in shown.get('results',[])],status='Conflict: choose a resolution' if len(shown.get('heads',[]))>1 else 'Edited' if shown.get('heads')!=[reference] else 'Original')
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send(self,code,value,kind='application/json'):
            raw=value if isinstance(value,bytes) else json.dumps(value).encode();self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        def do_GET(self):
            if self.path=='/state':return self.send(200,state())
            if self.path!='/':return self.send(404,{})
            script='''const session=SESSION;let sourceToken;async function update(){const s=await(await fetch('/state')).json();sourceToken=s.sourceToken;document.querySelector('[role=status]').textContent=s.status;const list=document.querySelector('#versions');list.replaceChildren();for(const v of s.versions){const p=document.createElement('p');p.textContent=v.text+' — '+(s.heads.some(h=>h.event===v.reference.event)?'Current version':'Earlier version');list.append(p);}}for(const kind of ['edit','branch','resolve'])document.querySelector('#'+kind).onclick=async()=>{const r=await fetch('/'+kind,{method:'POST',headers:{'X-Session':session,'Content-Type':'application/json'},body:JSON.stringify({text:document.querySelector('#text').value,sourceToken})});if(r.ok)await update();else document.querySelector('[role=status]').textContent='Changed context: refresh before editing';};update();'''.replace('SESSION',json.dumps(session))
            self.send(200,('<meta charset="utf-8"><title>Message edits</title><h1>Correct a message</h1><p>Synthetic signed conversation. Earlier versions remain available; replies keep their original targets.</p><label>Replacement text <input id="text"></label><button id="edit">Send correction</button><button id="branch">Send competing correction</button><button id="resolve">Resolve all shown versions</button><div role="status"></div><section id="versions"></section><script type="module">'+script+'</script>').encode(),'text/html; charset=utf-8')
        def do_POST(self):
            global sequence
            if self.headers.get('X-Session')!=session:return self.send(403,{})
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=8192 or self.headers.get('Transfer-Encoding') or self.headers.get('Content-Type')!='application/json':raise ValueError('Framing')
                body=json.loads(self.rfile.read(length))
                if set(body)!={'text','sourceToken'} or not isinstance(body['text'],str):raise ValueError('Edit request')
                current=view(demo.sender.receiver,reference)
                if self.path not in ('/edit','/branch','/resolve'):return self.send(404,{})
                parents=current['heads'] if self.path=='/resolve' else [reference]
                sequence+=1;identifier='editdemo'+str(sequence)
                wire=prepare(demo.sender,identifier,reference,parents,body['text'],body['sourceToken'],key=demo.f.creator['key'],address=demo.source,recipients=[demo.destination],time=demo.time)
                smtp=LocalSMTP()
                with SenderWorker(demo.sender) as worker:worker.submit(identifier,port=smtp.port,time=demo.time)
                smtp.done();result=demo.peer_sender.receiver.receive(unpack(smtp.wire),time=demo.time,trust_policy='allow-unverified')
                if result['applicationState']!='accepted':raise ValueError('Edit held')
                self.send(200,state())
            except (ValueError,KeyError,TypeError):self.send(409,dict(state='held'))
    server=HTTPServer(('127.0.0.1',0),Handler);print(json.dumps(dict(url='http://127.0.0.1:'+str(server.server_port))),flush=True)
    try:server.serve_forever()
    finally:server.server_close();demo.tearDown()
