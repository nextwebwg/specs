"""Local HTTPS hosted routes. Configured fixture, not a hardened public server."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from http_framing import FixedHTTPHandler
from service_tls import require_http11_protocol
from urllib.parse import urlsplit
import re
import secrets
from pathlib import Path

SCRIPT=Path(__file__).with_name('hosted-response.js').read_text()+r'''(()=>{'use strict';let credential=location.hash.slice(1);history.replaceState(null,'',location.pathname);const grant=location.pathname.split('/').pop();const status=document.getElementById('status');const open=document.getElementById('open');const reply=document.getElementById('reply');const text=document.getElementById('text');let retained;const exact=(o,keys)=>o&&typeof o==='object'&&!Array.isArray(o)&&Object.keys(o).length===keys.length&&keys.every(k=>Object.hasOwn(o,k));
if(!/^[A-Za-z0-9_-]{43}$/.test(credential)){credential='';open.disabled=true;status.textContent='Reopen the original invitation.';}
async function request(path,body){const response=await fetch(path,{method:body?'POST':'GET',credentials:'omit',redirect:'error',cache:'no-store',headers:{Authorization:'Bearer '+credential,Accept:'application/json',...(body?{'Content-Type':'application/json'}:{})},body});if(!response.ok){const error=Error('Access unavailable');error.status=response.status;throw error;}if(response.headers.get('content-type')!=='application/json'||response.headers.get('cache-control')!=='no-store')throw Error();return readHostedJSON(response);}
open.addEventListener('click',async()=>{try{const result=await request('/v0/grants/'+grant+'/content');if(!exact(result,['version','purpose','grant','contribution','content','attribution'])||!exact(result.content,['kind','text'])||result.version!=='0'||result.purpose!=='hosted-content'||result.grant!==grant||result.attribution!=='provider-hosted'||result.content?.kind!=='text'||typeof result.content.text!=='string')throw Error();document.getElementById('content').textContent=result.content.text;status.textContent='Provider-hosted content';reply.disabled=false;}catch{status.textContent='Access unavailable';}});
reply.addEventListener('click',async()=>{if(!text.value.trim())return;if(!retained){const id=crypto.randomUUID().replaceAll('-','');retained=JSON.stringify({version:'0',purpose:'hosted-holder-reply',operation:id,text:text.value});}try{const result=await request('/v0/grants/'+grant+'/replies',retained);const expected=JSON.parse(retained);const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(retained))),b=>b.toString(16).padStart(2,'0')).join('');if(!exact(result,['version','purpose','service','grant','operation','requestDigest','outcome','reason','attribution'])||result.version!=='0'||result.purpose!=='hosted-holder-result'||result.service!==location.origin||result.grant!==grant||result.operation!==expected.operation||result.requestDigest!==digest||result.outcome!=='confirmed'||result.attribution!=='grant-holder'||result.reason!=='stored')throw Error();status.textContent='Reply stored from grant holder';}catch(error){if(error.status===413){retained=undefined;status.textContent='Reply is too large. Shorten it and try again.';}else status.textContent='Reply confirmation unavailable';}});})();'''

def make_hosted_server(store,context):
    context.set_alpn_protocols(['http/1.1'])
    class Handler(FixedHTTPHandler):
        def handle(self):
            try: require_http11_protocol(self.connection)
            except ValueError: return
            super().handle()
        def expected_authority(self):return urlsplit(store.service).netloc
        protocol_version='HTTP/1.1'
        def log_message(self,*args):pass
        def handle_request(self):
            self.connection.settimeout(5)
            code,body,kind=404,b'','application/json'
            nonce=secrets.token_hex(16)
            if self.command in ('GET','HEAD') and re.fullmatch('/g/[0-9a-f]{32}',self.path):
                body=('<!doctype html><meta charset="utf-8"><title>Hosted contribution</title><button id="open">Open contribution</button><p id="status"></p><pre id="content"></pre><textarea id="text" aria-label="Reply"></textarea><button id="reply" disabled>Send holder reply</button><script nonce="'+nonce+'">'+SCRIPT+'</script>').encode();code=200;kind='text/html; charset=utf-8'
            else:
                headers=self.headers.get_all('Authorization',[])
                token=headers[0][7:] if len(headers)==1 and headers[0].startswith('Bearer ') else ''
                raw=b'';valid=True
                if self.command=='POST':
                    lengths=self.headers.get_all('Content-Length',[])
                    valid=len(lengths)==1 and lengths[0].isdigit() and int(lengths[0])<=1048576 and self.headers.get('Content-Type')=='application/json' and not self.headers.get('Content-Encoding') and not self.headers.get('Transfer-Encoding')
                    if valid:raw=self.rfile.read(int(lengths[0]));valid=len(raw)==int(lengths[0])
                if not valid:code=400
                elif self.command=='POST' and self.path=='/v0/grants':code,body=store.manage(raw,token,'hosted-grant-create')
                elif self.command=='GET' and (match:=re.fullmatch('/v0/operations/([0-9a-f]{32})',self.path)):code,body=store.lookup(match[1],token)
                elif (match:=re.fullmatch('/v0/grants/([0-9a-f]{32})/(content|revoke|replies|reply-records|reply-exports)(?:/([0-9a-f]{32}))?',self.path)):
                    grant,operation,identity=match.groups()
                    if operation=='content' and self.command=='GET' and not identity:code,body=store.retrieve(grant,token)
                    elif operation=='revoke' and self.command=='POST' and not identity:
                        from hosted_access import parse
                        try:valid=parse(raw,'hosted-grant-revoke')['grant']==grant
                        except ValueError:valid=False
                        code,body=store.manage(raw,token,'hosted-grant-revoke') if valid else (400,b'')
                    elif operation=='replies' and self.command=='POST' and not identity:code,body=store.reply(grant,raw,token)
                    elif operation=='replies' and self.command=='GET' and identity:code,body=store.reply_status(grant,identity,token)
                    elif operation=='reply-exports' and self.command=='GET' and identity:code,body=store.export_reply(grant,identity,token)
                    elif operation=='reply-records' and self.command=='GET' and identity:code,body=store.management_reply(grant,identity,token)
            self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('Referrer-Policy','no-referrer');self.send_header('Connection','close')
            self.send_header('Content-Security-Policy',"default-src 'none';script-src 'nonce-"+nonce+"';connect-src 'self';base-uri 'none';form-action 'none';frame-ancestors 'none'")
            if code==401:self.send_header('WWW-Authenticate','Bearer realm="hosted"')
            self.end_headers()
            if self.command!='HEAD':self.wfile.write(body)
            self.close_connection=True
        do_GET=handle_request
        do_POST=handle_request
        do_HEAD=handle_request
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.socket=context.wrap_socket(server.socket,server_side=True)
    return server
