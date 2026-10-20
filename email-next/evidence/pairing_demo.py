"""Two local client surfaces backed by real pairing; no real account access."""
import base64,io,json,secrets
from http.server import HTTPServer,BaseHTTPRequestHandler
from pathlib import Path
import qrcode
from remote_pairing import commitment
from test_remote_pairing import RemotePairing
from own_devices import OwnDevices
from event_encoding import encode_event

def main():
    fixture=RemotePairing();fixture.setUp();nonce=secrets.token_hex(32);done=False
    def qr(value):
        out=io.BytesIO();qrcode.make(value).save(out,format='PNG');return 'data:image/png;base64,'+base64.b64encode(out.getvalue()).decode()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            if self.headers.get('Host')!='127.0.0.1:'+str(self.server.server_port):self.send_error(403);return
            if self.path=='/':
                data=Path(__file__).with_name('pairing-demo.html').read_bytes().replace(b'CLIENT_NONCE',nonce.encode());mime='text/html'
            elif self.path=='/state':
                request=fixture.new._row(fixture.session)[2] if fixture.stores[1].db.execute('SELECT 1 FROM pairing_sessions').fetchone() else None
                values=dict(offer='email-next-pairing:offer:'+commitment('offer',fixture.offer),request='email-next-pairing:request:'+commitment('request',request) if request else None,mailbox=fixture.mailbox,complete=fixture.new.result(fixture.session) is not None if request else False)
                values['offerQR']=qr(values['offer']);values['requestQR']=qr(values['request']) if request else None
                data=json.dumps(values).encode();mime='application/json'
            else:self.send_error(404);return
            self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
        def do_POST(self):
            if self.headers.get('Host')!='127.0.0.1:'+str(self.server.server_port) or self.headers.get('X-Pairing-Client')!=nonce:self.send_error(403);return
            try:
                n=int(self.headers.get('Content-Length','0'))
                if not 0<n<4096:raise ValueError('Request bound')
                value=json.loads(self.rfile.read(n))
                if self.path=='/confirm-offer':
                    if value.get('independent') is not True:raise ValueError('Confirm the independent device/channel')
                    code=value['code'];prefix='email-next-pairing:offer:'
                    if not code.startswith(prefix):raise ValueError('Scan the existing device offer')
                    fixture.new.confirm_offer(fixture.channel.transfer(fixture.session,'offer'),fixture.channel.transfer(fixture.session,'anchor'),comparison=code[len(prefix):],channel='independent-full-comparison',time=fixture.time)
                    request=fixture.new.request(fixture.session,fixture.b,binary=fixture.binary,time=fixture.time);fixture.channel.transfer(fixture.session,'request',request)
                elif self.path=='/confirm-request':
                    if value.get('independent') is not True:raise ValueError('Confirm the independent device/channel')
                    prefix='email-next-pairing:request:';code=value['code']
                    if not code.startswith(prefix):raise ValueError('Scan the new device request')
                    request=fixture.channel.transfer(fixture.session,'request');result=fixture.old.commit(fixture.session,request,owner=fixture.owner,device=fixture.a,binary=fixture.binary,comparison=code[len(prefix):],channel='independent-full-comparison',time=fixture.time)
                    fixture.channel.transfer(fixture.session,'result',result);fixture.new.accept(fixture.session,fixture.channel.transfer(fixture.session,'result'),time=fixture.time)
                    fixture.bundle=json.loads(base64.b64decode(json.loads(result)['bundle']));fixture.raw=encode_event(fixture.bundle);fixture.head=json.loads(result)['head']
                    fixture.owners=[fixture.owner,OwnDevices(fixture.stores[1],account='local-account',principal=fixture.a['principal'],local_device=fixture.b['device'],mailboxes=[fixture.mailbox])]
                elif self.path=='/delivery':
                    if fixture.new.result(fixture.session) is None:raise ValueError('Pair both devices first')
                    fixture.pair=lambda:None;fixture.test_actual_protected_delivery_after_remote_pairing()
                else:raise ValueError('Unknown local action')
                body=json.dumps(dict(ok=True)).encode();self.send_response(200)
            except Exception as exc:body=json.dumps(dict(ok=False,error=str(exc))).encode();self.send_response(400)
            self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    server=HTTPServer(('127.0.0.1',0),Handler)
    print('http://127.0.0.1:'+str(server.server_port),flush=True)
    import signal
    def stop(*args):raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM,stop)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close();fixture.doCleanups();fixture.tearDown()
if __name__=='__main__':main()
