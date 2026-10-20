"""Bounded local HTTP/1.1 fixture. Login/consent is deliberately external.

approve_account is invoked by a simulated trusted account-authentication adapter,
never by an HTTP body account identifier. Resource and issuer share one store.
"""
import json
from http.server import ThreadingHTTPServer
from urllib.parse import urlsplit,parse_qsl,urlencode
from http_framing import FixedHTTPHandler
from service_tls import require_http11_protocol
from service_authorization import AuthorizationStore,OAuthError,GrantError,redirect_ok
from service_execution import ServiceStore
from event_encoding import decode_event,encode_event

class LinkedServiceStore(ServiceStore):
    def authorized(self,token,action,scope):
        if not getattr(self,'authorization_config',None):return None,401
        path,raw,clock=self.authorization_config;auth=AuthorizationStore(path,raw,clock=clock)
        try:return auth.authorize_service(token,action,scope)
        finally:auth.close()

def bearer(headers):
    import re
    values=headers.get_all('Authorization',[])
    if not values:raise GrantError(401)
    if len(values)!=1:raise GrantError(400,'invalid_request')
    scheme,space,rest=values[0].partition(' ')
    if scheme.lower()!='bearer':raise GrantError(401)
    if not space or not re.fullmatch(r" +[A-Za-z0-9._~+/-]+=*",' '+rest):raise GrantError(400,'invalid_request')
    return rest.lstrip(' ')

def make_authorization_server(store,tls_context,*,drop_link_response=False,simulated_account=None,max_pending_consents=64,consent_lifetime=300):
    if any(type(v) is not int or v<=0 for v in (max_pending_consents,consent_lifetime)):raise ValueError('Consent limits')
    tls_context.set_alpn_protocols(['http/1.1'])
    consents={}
    class Handler(FixedHTTPHandler):
        protocol_version='HTTP/1.1'
        def log_message(self,*args):pass
        def expected_authority(self):return urlsplit(store.action()['service']).netloc
        def handle(self):
            try:require_http11_protocol(self.connection)
            except ValueError:return
            super().handle()
        def handle_request(self):
            self.connection.settimeout(5);body=b'';status=400;auth=None;token_endpoint=False;challenge=None
            try:
                if self.headers.get('Transfer-Encoding') or self.headers.get('Content-Encoding'):raise ValueError('Framing')
                sizes=self.headers.get_all('Content-Length',[])
                if len(sizes)!=1 or not sizes[0].isdigit() or not 0<int(sizes[0])<=1048576:raise ValueError('Length')
                raw=self.rfile.read(int(sizes[0]))
                if len(raw)!=int(sizes[0]):raise ValueError('Truncated')
                if not getattr(store,'authorization_config',None):raise ValueError('No authorization configuration')
                path,config,clock=store.authorization_config;auth=AuthorizationStore(path,config,clock=clock);r=auth.registration
                tokens=self.headers.get_all('Authorization',[]);token=tokens[0][7:] if len(tokens)==1 and tokens[0].startswith('Bearer ') else None
                if simulated_account is not None and self.path==urlsplit(r['authorization']).path:
                    if self.headers.get('Content-Type')!='application/x-www-form-urlencoded':raise ValueError('Consent media')
                    pairs=parse_qsl(raw.decode('ascii'),strict_parsing=True)
                    if len(pairs)!=1 or pairs[0][0]!='consent':raise ValueError('Consent action')
                    pending=consents.pop(pairs[0][1],None)
                    if not pending or pending['expiry']<clock():raise ValueError('Consent expired')
                    result=auth.approve_account(pending['params'],authenticated_account=simulated_account)
                    destination=pending['params']['redirect_uri']+'?'+urlencode(result)
                    self.send_response(303);self.send_header('Location',destination);self.send_header('Cache-Control','no-store');self.send_header('Referrer-Policy','no-referrer');self.send_header('Content-Length','0');self.send_header('Connection','close');self.end_headers();self.close_connection=True;return
                if self.path==urlsplit(r['token']).path:
                    token_endpoint=True
                    if self.headers.get('Content-Type')!='application/x-www-form-urlencoded':raise ValueError('Token media')
                    pairs=parse_qsl(raw.decode('ascii'),keep_blank_values=True,strict_parsing=True);params={}
                    base={'grant_type','client_id','code','redirect_uri','code_verifier','refresh_token','scope'}
                    for k,v in pairs:
                        if k in params and k in base:raise ValueError('Duplicate token parameter')
                        params[k]=v
                    result=auth.token(params);body=json.dumps(result,separators=(",",":")).encode();status=200
                elif self.path==urlsplit(r['linkChallenge']).path:
                    if self.headers.get('Content-Type')!='application/json':raise ValueError('Link media')
                    token=bearer(self.headers);body=auth.challenge(raw,token);status=200
                elif self.path==urlsplit(r['linkComplete']).path:
                    if self.headers.get('Content-Type')!='application/json':raise ValueError('Link media')
                    token=bearer(self.headers);body=auth.complete(raw,token);status=200
                    if drop_link_response() if callable(drop_link_response) else drop_link_response:self.close_connection=True;return
                elif self.path==store.action()['submitPath']:
                    if self.headers.get('Content-Type')!='application/json':raise ValueError('Submit media')
                    token=bearer(self.headers);status,body=store.submit(raw,token)
                    if status in (401,403):challenge='Bearer'+(' error="invalid_token"' if status==401 else ' error="insufficient_scope"')
                else:status=404
            except (ValueError,TypeError,KeyError,UnicodeError) as error:
                body=encode_event(dict(error=error.code if isinstance(error,OAuthError) else 'invalid_request')) if token_endpoint else b'';status=error.status if isinstance(error,GrantError) else 400
                if isinstance(error,GrantError):challenge='Bearer'+(' error="'+error.error+'"' if error.error else '')
            finally:
                if auth:auth.close()
            self.send_response(status)
            if challenge:self.send_header('WWW-Authenticate',challenge)
            self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.send_header('Connection','close');self.end_headers();self.wfile.write(body);self.close_connection=True
        do_POST=handle_request
        def do_GET(self):
            challenge=None;body=b''
            if simulated_account is not None and getattr(store,'authorization_config',None):
                path,config,clock=store.authorization_config
                r=json.loads(config)
                if urlsplit(self.path).path==urlsplit(r['authorization']).path:
                    import html,secrets
                    try:
                        for key in [k for k,v in consents.items() if v['expiry']<clock()]:del consents[key]
                        if len(self.path)>8192 or len(consents)>=max_pending_consents:raise ValueError('Consent budget')
                        pairs=parse_qsl(urlsplit(self.path).query,keep_blank_values=True,strict_parsing=True);params={}
                        for k,v in pairs:
                            if k in params:raise ValueError('Duplicate consent parameter')
                            params[k]=v
                        if not redirect_ok(params.get('redirect_uri'),r['redirectPath']):raise ValueError('Consent redirect')
                        nonce=secrets.token_hex(32);consents[nonce]=dict(params=params,expiry=clock()+consent_lifetime)
                        body=('<!doctype html><meta charset="utf-8"><title>Synthetic service consent</title><h1>Connect the demo booking account?</h1><p>This is simulated account authentication and consent. No real account or password is used.</p><p>Account: '+html.escape(simulated_account)+'</p><form method="post" action="'+html.escape(urlsplit(r['authorization']).path,quote=True)+'"><input type="hidden" name="consent" value="'+nonce+'"><button>Authorize demo account</button></form>').encode()
                        self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Referrer-Policy','no-referrer');self.send_header('X-Frame-Options','DENY');self.send_header('Content-Security-Policy',"default-src 'none'; form-action 'self' http:; frame-ancestors 'none'");self.send_header('Content-Length',str(len(body)));self.send_header('Connection','close');self.end_headers();self.wfile.write(body);self.close_connection=True;return
                    except ValueError:
                        self.send_response(400);self.send_header('Content-Length','0');self.end_headers();return
            try:
                import re
                self.connection.settimeout(5)
                if self.headers.get('Content-Length') or self.headers.get('Transfer-Encoding'):raise ValueError('GET body')
                prefix=store.action()['statusPrefix'];suffix=self.path[len(prefix):] if self.path.startswith(prefix) else ''
                if not re.fullmatch('[0-9a-f]{32}',suffix):raise ValueError('Status path')
                status,body=store.status(suffix,bearer(self.headers))
                if status in (401,403):challenge='Bearer error="'+('invalid_token' if status==401 else 'insufficient_scope')+'"'
            except GrantError as error:
                status=error.status;challenge='Bearer'+(' error="'+error.error+'"' if error.error else '')
            except ValueError:status=400
            self.send_response(status)
            if challenge:self.send_header('WWW-Authenticate',challenge)
            self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.send_header('Connection','close');self.end_headers();self.wfile.write(body);self.close_connection=True
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.socket=tls_context.wrap_socket(server.socket,server_side=True);return server
