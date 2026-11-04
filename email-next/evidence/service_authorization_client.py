"""Native authorization state and direct TLS adapter; browser launch is caller-owned.

Secret rows use an externally supplied vault key. This is not a platform keychain.
"""
import json,secrets,socket,sqlite3,hashlib,http.client
from urllib.parse import urlencode,urlsplit,parse_qsl
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from service_authorization import registration,digest,random_token,b64url,SCOPES,redirect_ok,oauth_json,exact_scope
from event_encoding import encode_event,decode_event
from service_tls import wrap_http11_socket
from http_framing import read_fixed_response

def bind_loopback(path='/mail/oauth/callback'):
    """Try both literal loopback families, selecting one actual bound listener."""
    failures=[]
    for family,address,host in [(socket.AF_INET6,('::1',0),'[::1]'),(socket.AF_INET,('127.0.0.1',0),'127.0.0.1')]:
        sock=socket.socket(family,socket.SOCK_STREAM)
        try:
            sock.bind(address);sock.listen(1);return sock,'http://'+host+':'+str(sock.getsockname()[1])+path
        except OSError as error:failures.append(error);sock.close()
    raise OSError('No supported loopback listener') from failures[-1]

class NativeAuthorization:
    def __init__(self,path,registration_bytes,*,key,clock,attempt_lifetime=300,max_callback_bytes=8192,writer_owner=None):
        if not isinstance(key,bytes) or len(key)!=32 or type(attempt_lifetime)is not int or attempt_lifetime<=0:raise ValueError('Vault configuration')
        if writer_owner is not None: writer_owner.check_application(path)
        self.writer_owner=writer_owner;self.vault_key=key
        self.db=sqlite3.connect(path,isolation_level=None);self.aes=AESGCM(key);self.raw=registration_bytes;self.config=registration(registration_bytes);self.clock=clock;self.lifetime=attempt_lifetime;self.max_callback_bytes=max_callback_bytes
        if type(max_callback_bytes)is not int or max_callback_bytes<=0:raise ValueError('Callback budget')
        self.db.executescript('CREATE TABLE IF NOT EXISTS auth_secret(id TEXT PRIMARY KEY,encrypted BLOB);')
    def close(self):self.db.close()
    def put(self,id,value):
        if self.writer_owner is None: raise ValueError('writer-key-owner-required')
        nonce=self.writer_owner.reserve(self.vault_key);body=nonce+self.aes.encrypt(nonce,json.dumps(value,separators=(",",":"),ensure_ascii=True).encode(),id.encode());self.db.execute('INSERT OR REPLACE INTO auth_secret VALUES(?,?)',(id,body))
    def get(self,id):
        row=self.db.execute('SELECT encrypted FROM auth_secret WHERE id=?',(id,)).fetchone()
        if not row:raise ValueError('Missing authorization state')
        return oauth_json(self.aes.decrypt(row[0][:12],row[0][12:],id.encode()))
    def migrate_writer(self, *, key, writer_owner):
        """Explicit legacy/restore migration; old writer remains on rollback."""
        path=self.db.execute('PRAGMA database_list').fetchone()[2]
        writer_owner.check_application(path)
        cipher=AESGCM(key)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            for id,encrypted in self.db.execute('SELECT id,encrypted FROM auth_secret').fetchall():
                raw=self.aes.decrypt(encrypted[:12],encrypted[12:],id.encode())
                nonce=writer_owner.reserve(key)
                body=nonce+cipher.encrypt(nonce,raw,id.encode())
                self.db.execute('UPDATE auth_secret SET encrypted=? WHERE id=?',(body,id))
            self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
        self.aes=cipher;self.vault_key=key;self.writer_owner=writer_owner
    def now(self):
        v=self.clock()
        if type(v)is not int or v<0:raise ValueError('Credible client clock')
        return v
    def start(self,redirect):
        if not redirect_ok(redirect,self.config['redirectPath']):raise ValueError('Redirect')
        state=random_token();verifier=random_token();params=dict(response_type='code',client_id=self.config['clientId'],redirect_uri=redirect,scope=' '.join(SCOPES),state=state,code_challenge=b64url(hashlib.sha256(verifier.encode()).digest()),code_challenge_method='S256')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            self.put(state,dict(registration=digest(self.raw),redirect=redirect,verifier=verifier,expiry=self.now()+self.lifetime,state='pending'));self.put('active-attempt',dict(id=state));self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK');raise
        return self.config['authorization']+'?'+urlencode(params),state
    def callback(self,attempt,url,exchange):
        if not isinstance(url,str) or len(url.encode('utf8'))>self.max_callback_bytes:raise ValueError('Callback budget')
        p=urlsplit(url);pairs=parse_qsl(p.query,keep_blank_values=True,strict_parsing=True);values={}
        for k,v in pairs:
            if k in values and k in ('code','state','iss','error','error_description','error_uri'):raise ValueError('Duplicate OAuth parameter')
            values[k]=v
        self.db.execute('BEGIN IMMEDIATE')
        try:
            saved=self.get(attempt)
            actual=p._replace(query='',fragment='').geturl()
            if self.get('active-attempt')['id']!=attempt or saved['state']!='pending' or saved['registration']!=digest(self.raw) or saved['expiry']<self.now() or actual!=saved['redirect'] or p.fragment or values.get('state')!=attempt or values.get('iss')!=self.config['issuer']:raise ValueError('Callback binding')
            if ('code'in values)==('error'in values):raise ValueError('Ambiguous callback')
            if 'code'in values and not values['code']:raise ValueError('Empty code')
            saved['state']='consumed';self.put(attempt,saved);self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
        if 'error'in values:raise ValueError('Authorization denied')
        # No SQLite lock spans the network. A new selected attempt also prevents
        # a late successful response from overwriting a newer account selection.
        result=exchange(self.config['token'],dict(grant_type='authorization_code',code=values['code'],client_id=self.config['clientId'],redirect_uri=saved['redirect'],code_verifier=saved['verifier']))
        self.accept_tokens(result,expected_attempt=attempt);return result['access_token']
    def accept_tokens(self,value,*,expected_attempt,expected_refresh=None):
        if not isinstance(value,dict) or not isinstance(value.get('token_type'),str) or value['token_type'].lower()!='bearer' or not exact_scope(value.get('scope')) or type(value.get('expires_in'))is not int or value['expires_in']<=0 or any(not isinstance(value.get(k),str) or not value[k] for k in ('access_token','refresh_token')):raise ValueError('Token response')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            if self.get('active-attempt')['id']!=expected_attempt:raise ValueError('Changed account selection')
            if expected_refresh is not None:
                old=self.get('tokens')
                if old.get('refreshState')!='uncertain' or old['refresh_token']!=expected_refresh:raise ValueError('Changed refresh selection')
            self.put('tokens',dict(value,attempt=expected_attempt,registration=digest(self.raw),expiresAt=self.now()+value['expires_in']));self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def access_token(self):
        saved=self.get('tokens')
        if saved.get('attempt')!=self.get('active-attempt')['id'] or saved.get('registration')!=digest(self.raw) or saved.get('refreshState','ready')!='ready' or saved['expiresAt']<self.now():raise ValueError('Credential held')
        return saved['access_token']
    def refresh(self,exchange):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.get('tokens');attempt=self.get('active-attempt')['id']
            if old.get('attempt')!=attempt or old.get('registration')!=digest(self.raw) or old.get('refreshState','ready')!='ready':raise ValueError('Refresh held')
            old['refreshState']='uncertain';self.put('tokens',old);self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
        result=exchange(self.config['token'],dict(grant_type='refresh_token',refresh_token=old['refresh_token'],client_id=self.config['clientId'],scope=' '.join(SCOPES)))
        self.accept_tokens(result,expected_attempt=attempt,expected_refresh=old['refresh_token']);return result['access_token']

class AuthorizationHTTPS:
    def __init__(self,registration_bytes,*,ca_file,address):self.config=registration(registration_bytes);self.ca=ca_file;self.address=address
    def post(self,url,value,*,token=None,form=False):
        if url not in [self.config[k] for k in ('token','linkChallenge','linkComplete')]:raise ValueError('Unregistered endpoint')
        p=urlsplit(url);body=urlencode(value).encode() if form else encode_event(value)
        headers={'Content-Type':'application/x-www-form-urlencoded' if form else 'application/json','Accept':'application/json','Cache-Control':'no-store','Connection':'close'}
        if token is not None:
            if not isinstance(token,str) or not token or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~+/=' for c in token):raise ValueError('Bearer syntax')
            headers['Authorization']='Bearer '+token
        conn=http.client.HTTPConnection(p.hostname,p.port or 443,timeout=5);sock=socket.create_connection(self.address,timeout=5)
        try:
            conn.sock=wrap_http11_socket(sock,reference_host=p.hostname,trusted_ca_file=self.ca);conn.request('POST',p.path,body=body,headers=headers);response=conn.getresponse();raw=read_fixed_response(response,1048576)
            if response.status!=200 or response.getheader('Content-Type')!='application/json' or response.getheader('Cache-Control')!='no-store':raise ValueError('Authorization HTTP response')
            return oauth_json(raw)
        finally:conn.close();sock.close()
    def exchange(self,url,value):return self.post(url,value,form=True)

def link_account(client,https,*,device,identity_bundle,identity_store,binary,token,time):
    """Trusted account-link action, never called from passive message rendering.

The caller selected the principal after account consent. Transport is the fixed
registered HTTPS adapter; its challenge is still fully checked before signing.
"""
    import base64
    from identity_bundle import decode_identity_bundle
    from provider_mls import sign
    from service_authorization import exact,u64,hexvalue
    if type(https)is not AuthorizationHTTPS or https.config!=client.config:raise ValueError('Registered authorization transport')
    authority=identity_store.check_device(bytes.fromhex(device['identity']),bytes.fromhex(device['key']),role='send',time=time,trust_policy='allow-unverified')
    if authority['status']!='authorized-unverified':raise ValueError('Current signing authority')
    request=dict(version='0',purpose='service-account-link-request',registrationDigest=digest(client.raw),principal=device['principal'],device=device['device'],state=authority['head'],binding=authority['binding'])
    challenge=https.post(client.config['linkChallenge'],request,token=token)
    exact(challenge,'version purpose registrationDigest principal device state binding challenge nonce issuer service clientId grantBinding notBefore notAfter')
    if any(challenge[k]!=v for k,v in request.items() if k!='purpose') or challenge['purpose']!='service-account-link' or any(challenge[k]!=client.config[k] for k in ('issuer','service','clientId')) or not hexvalue(challenge['challenge'],32) or any(not hexvalue(challenge[k],64) for k in ('nonce','grantBinding')) or not all(u64(challenge[k]) for k in ('notBefore','notAfter')):raise ValueError('Challenge correspondence')
    if not int(challenge['notBefore'])<=int(time['earliest'])<=int(time['latest'])<=int(challenge['notAfter']):raise ValueError('Challenge time')
    interval=dict(earliest=challenge['notBefore'],latest=challenge['notAfter'])
    authority=identity_store.check_device(bytes.fromhex(device['identity']),bytes.fromhex(device['key']),role='send',time=interval,trust_policy='allow-unverified')
    if authority['status']!='authorized-unverified' or authority['head']!=challenge['state'] or authority['binding']!=challenge['binding']:raise ValueError('Challenge binding interval')
    raw=encode_event(challenge);proof=dict(payload=base64.b64encode(raw).decode(),signature=sign(binary,device,'email-next/service-account-link/v0',raw),identity=identity_bundle)
    client.put('link-pending',dict(proof=proof,registration=digest(client.raw)))
    receipt=https.post(client.config['linkComplete'],proof,token=token)
    return finish_link(client,proof,receipt)

def finish_link(client,proof,receipt):
    import base64
    from service_authorization import exact,hexvalue,u64
    raw=base64.b64decode(proof['payload'],validate=True);challenge=decode_event(raw)['value']
    exact(receipt,'version purpose challenge requestDigest service principal link generation outcome')
    if receipt['version']!='0' or receipt['purpose']!='service-account-link-result' or receipt['challenge']!=challenge['challenge'] or receipt['requestDigest']!=digest(raw) or receipt['service']!=client.config['service'] or receipt['principal']!=challenge['principal'] or receipt['outcome']!='linked' or not hexvalue(receipt['link'],32) or not u64(receipt['generation']) or receipt['generation']=='0':raise ValueError('Link receipt binding')
    client.put('link',dict(proof=proof,receipt=receipt));return proof,receipt

def retry_link(client,https,token):
    if type(https)is not AuthorizationHTTPS or https.config!=client.config:raise ValueError('Registered authorization transport')
    pending=client.get('link-pending')
    if pending['registration']!=digest(client.raw):raise ValueError('Changed registration')
    receipt=https.post(client.config['linkComplete'],pending['proof'],token=token)
    return finish_link(client,pending['proof'],receipt)

def receive_loopback_callback(listener,redirect,*,timeout=30,max_bytes=8192):
    """One bounded literal-loopback HTTP callback; no token exchange in this reader."""
    if type(timeout) not in (int,float) or not 0<timeout<=300 or type(max_bytes)is not int or max_bytes<1:raise ValueError('Callback limits')
    expected=urlsplit(redirect)
    if not redirect_ok(redirect,expected.path):raise ValueError('Callback redirect')
    listener.settimeout(timeout);connection,_=listener.accept()
    with connection:
        connection.settimeout(timeout);data=b''
        while b'\r\n\r\n' not in data:
            part=connection.recv(min(1024,max_bytes-len(data)+1))
            if not part:raise ValueError('Incomplete callback')
            data+=part
            if len(data)>max_bytes:raise ValueError('Callback budget')
        head,body=data.split(b'\r\n\r\n',1)
        if body:raise ValueError('Callback body')
        lines=head.decode('ascii').split('\r\n');request=lines.pop(0).split(' ')
        if len(request)!=3 or request[0]!='GET' or request[2]!='HTTP/1.1' or not request[1].startswith('/') or request[1].startswith('//') or '#'in request[1]:raise ValueError('Callback request')
        headers={}
        for line in lines:
            name,separator,value=line.partition(':');name=name.lower()
            if not separator or name in headers or not re_header_name(name):raise ValueError('Callback header')
            headers[name]=value.strip()
        if headers.get('host')!=expected.netloc or 'transfer-encoding'in headers or 'content-length'in headers:raise ValueError('Callback authority')
        # Fixed content neither echoes credentials nor loads external resources.
        body=b'You may return to your email client.'
        connection.sendall(b'HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nCache-Control: no-store\r\nReferrer-Policy: no-referrer\r\nConnection: close\r\nContent-Length: '+str(len(body)).encode()+b'\r\n\r\n'+body)
        return expected.scheme+'://'+expected.netloc+request[1]

def re_header_name(value):
    import re
    return re.fullmatch("[!#$%&'*+.^_`|~0-9a-z-]+",value) is not None
