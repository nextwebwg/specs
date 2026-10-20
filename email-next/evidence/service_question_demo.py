"""Synthetic loopback client: signed SMTP source and actual TLS service effect."""
import json,secrets
from http.server import BaseHTTPRequestHandler,HTTPServer
from test_joined_service import JoinedService

if __name__=='__main__':
    JoinedService.setUpClass();fixture=JoinedService();fixture.setUp();fixture.setup_flow();session=secrets.token_hex(32)
    args=fixture.args;view=fixture.flow.view(args[1],args[2],time=fixture.time)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send(self,status,body,kind='application/json'):
            self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def do_GET(self):
            if self.path!='/':return self.send(404,b'{}')
            data=json.dumps(view).replace('<','\\u003c')
            script='''const view=VIEW;document.querySelector('h1').textContent=view.text;document.querySelector('p').textContent='Answer sent to '+view.service;for(const option of view.options){const button=document.createElement('button');button.textContent=option.label;button.onclick=async()=>{button.disabled=true;try{const r=await fetch('/activate',{method:'POST',headers:{'X-Session':SESSION,'Content-Type':'application/json'},body:JSON.stringify({option:option.id,sourceToken:view.sourceToken})});const v=await r.json();document.querySelector('[role=status]').textContent=r.ok?'Service result: '+v.state:'Action held';}catch{document.querySelector('[role=status]').textContent='Outcome uncertain';}};document.querySelector('main').append(button);}'''.replace('VIEW',data).replace('SESSION',json.dumps(session))
            self.send(200,('<meta charset="utf-8"><title>Service question</title><main><h1></h1><p></p><div role="status"></div></main><script type="module">'+script+'</script>').encode(),'text/html; charset=utf-8')
        def do_POST(self):
            if self.path!='/activate' or self.headers.get('X-Session')!=session:return self.send(403,b'{}')
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=1024 or self.headers.get('Content-Type')!='application/json':raise ValueError()
                value=json.loads(self.rfile.read(size))
                if not isinstance(value,dict) or set(value)!={'option','sourceToken'} or not all(isinstance(x,str) for x in value.values()):raise ValueError()
                result=fixture.flow.activate('browserclick',args[1],args[2],value['option'],value['sourceToken'],time=fixture.time)
                self.send(200,json.dumps(dict(result,effects=fixture.count())).encode())
            except ValueError:self.send(409,b'{}')
    server=HTTPServer(('127.0.0.1',0),Handler);print(json.dumps(dict(url='http://127.0.0.1:'+str(server.server_port))),flush=True)
    try:server.serve_forever()
    finally:server.server_close();fixture.doCleanups();fixture.tearDown();JoinedService.tearDownClass()
