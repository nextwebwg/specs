"""Experimental same-operator opaque OAuth grant and account-link store.

Account authentication is a trusted external boundary; simulated tests call
approve_account explicitly. No mailbox identity or OAuth subject inference.
"""
import base64,hashlib,json,re,secrets,sqlite3
from contextlib import contextmanager
from urllib.parse import urlsplit,parse_qsl
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
from event_encoding import decode_event,encode_event
from identity_bundle import decode_identity_bundle
from identity_store import IdentityStore
SCOPES=['mail.service.link','mail.service.status','mail.service.submit']
DOMAIN=b'email-next/service-account-link/v0\0'
def digest(raw):return hashlib.sha256(raw).hexdigest()
def b64url(raw):return base64.urlsafe_b64encode(raw).decode().rstrip('=')
def exact_scope(value):
    # OAuth scopes are unordered; this profile additionally rejects duplicates.
    if not isinstance(value,str) or not re.fullmatch(r'[\x21\x23-\x5b\x5d-\x7e]+(?: [\x21\x23-\x5b\x5d-\x7e]+)*',value):return False
    tokens=value.split(' ')
    return len(tokens)==len(set(tokens)) and set(tokens)==set(SCOPES)

def random_token():return b64url(secrets.token_bytes(32))
def exact(v,keys):
    if not isinstance(v,dict) or set(v)!=set(keys.split()):raise ValueError('Exact schema')
def hexvalue(v,n):return isinstance(v,str) and re.fullmatch('[0-9a-f]{%d}'%n,v) is not None
def u64(v):return isinstance(v,str) and re.fullmatch('0|[1-9][0-9]{0,19}',v) is not None and int(v)<2**64
def redirect_ok(uri,path):
    try:
        p=urlsplit(uri)
        return p.scheme=='http' and p.hostname in ('127.0.0.1','::1') and p.port is not None and 0<p.port<65536 and p.path==path and not p.query and not p.fragment and not p.username and p.netloc==('['+p.hostname+']' if ':' in p.hostname else p.hostname)+':'+str(p.port)
    except (ValueError,TypeError):return False

def registration(raw):
    v=decode_event(raw)['value'];exact(v,'version purpose registration generation service issuer clientId authorization token linkChallenge linkComplete redirectPath scopes')
    if v['version']!='0' or v['purpose']!='service-authorization-registration' or not hexvalue(v['registration'],32) or v['registration']=='0'*32 or not u64(v['generation']) or v['generation']=='0' or v['issuer']!=v['service'] or v['redirectPath']!='/mail/oauth/callback' or v['scopes']!=SCOPES or not isinstance(v['clientId'],str) or not re.fullmatch('[\x21-\x7e]{1,256}',v['clientId']):raise ValueError('Registration shape')
    # Reuse the selected canonical origin/path contract, not URL normalization.
    import subprocess
    from pathlib import Path
    script="import{isServiceOrigin,isServiceEndpoint}from'./service-question.mjs';let s='';for await(const c of process.stdin)s+=c;const v=JSON.parse(s);process.stdout.write(isServiceOrigin(v.service)&&['authorization','token','linkChallenge','linkComplete'].every(k=>isServiceEndpoint(v[k],v.service))?'yes':'no');"
    checked=subprocess.run(['node','--input-type=module','-e',script],cwd=Path(__file__).parent,input=json.dumps(v),capture_output=True,text=True,timeout=10,check=True)
    if checked.stdout!='yes' or len({v[k] for k in ('authorization','token','linkChallenge','linkComplete')})!=4:raise ValueError('Registration endpoints')
    return v

def oauth_json(raw):
    from event_encoding import check_limits
    check_limits(raw)
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise ValueError('Duplicate JSON name')
            result[k]=v
        return result
    def bad(value):raise ValueError('Invalid JSON constant')
    return json.loads(raw.decode('utf8'),object_pairs_hook=pairs,parse_constant=bad)

class GrantError(ValueError):
    def __init__(self,status,error=None):super().__init__('Grant unavailable');self.status=status;self.error=error

class OAuthError(ValueError):
    def __init__(self,code):super().__init__(code);self.code=code

class AuthorizationStore:
    def __init__(self,path,registration_bytes,*,clock,code_lifetime=120,challenge_lifetime=120,access_lifetime=600,refresh_lifetime=86400):
        self.identity=IdentityStore(path);self.db=self.identity.db;self.registration_bytes=registration_bytes;self.registration=registration(registration_bytes);self.clock=clock
        self.limits=(code_lifetime,challenge_lifetime,access_lifetime,refresh_lifetime)
        if any(type(x)is not int or not 0<x<=2**31 for x in self.limits):raise ValueError('Lifetime configuration')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS sa_codes(code TEXT PRIMARY KEY,data TEXT,used INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS sa_families(id TEXT PRIMARY KEY,data TEXT,active INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS sa_tokens(hash TEXT PRIMARY KEY,family TEXT,kind TEXT,expiry INTEGER,used INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS sa_challenges(id TEXT PRIMARY KEY,family TEXT,payload BLOB,signature TEXT,receipt BLOB);
        CREATE TABLE IF NOT EXISTS sa_links(family TEXT PRIMARY KEY,principal TEXT,device TEXT,state TEXT,binding TEXT,link TEXT,generation TEXT);
        CREATE TABLE IF NOT EXISTS sa_action_accounts(service TEXT,action TEXT,principal TEXT,account TEXT NOT NULL,PRIMARY KEY(service,action,principal));
        CREATE TABLE IF NOT EXISTS sa_configuration(id INTEGER PRIMARY KEY CHECK(id=1),raw BLOB);''')
        old=self.db.execute('SELECT raw FROM sa_configuration WHERE id=1').fetchone()
        if old and old[0]!=registration_bytes:
            with self.transaction():
                self.db.execute('UPDATE sa_families SET active=0');self.db.execute('DELETE FROM sa_codes');self.db.execute('UPDATE sa_configuration SET raw=?',(registration_bytes,))
        elif not old:self.db.execute('INSERT INTO sa_configuration VALUES(1,?)',(registration_bytes,))
    def close(self):self.identity.close()
    @contextmanager
    def transaction(self):
        self.db.execute('BEGIN IMMEDIATE')
        try:yield;self.db.execute('COMMIT')
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def now(self):
        v=self.clock()
        if type(v)is not int or v<0 or v>=2**63:raise ValueError('Credible server clock')
        return v
    def approve_account(self,params,*,authenticated_account):
        """Trusted account-consent adapter only; never a public body account field."""
        required={'response_type','client_id','redirect_uri','scope','state','code_challenge','code_challenge_method'}
        if not isinstance(params,dict) or not required<=set(params):raise ValueError('Authorization request')
        r=self.registration
        if not isinstance(authenticated_account,str) or not authenticated_account or params['response_type']!='code' or params['client_id']!=r['clientId'] or not redirect_ok(params['redirect_uri'],r['redirectPath']) or not exact_scope(params['scope']) or params['code_challenge_method']!='S256' or not re.fullmatch('[A-Za-z0-9_-]{43}',params['code_challenge']) or not re.fullmatch('[A-Za-z0-9_-]{43}',params['state']):raise ValueError('Authorization request')
        code=random_token();data=dict(account=authenticated_account,client=r['clientId'],redirect=params['redirect_uri'],challenge=params['code_challenge'],expiry=self.now()+self.limits[0],registration=digest(self.registration_bytes))
        self.db.execute('INSERT INTO sa_codes VALUES(?,?,0)',(digest(code.encode()),json.dumps(data)))
        return dict(code=code,state=params['state'],iss=r['issuer'])
    def _mint(self,family):
        access=random_token();refresh=random_token();now=self.now()
        self.db.execute('INSERT INTO sa_tokens VALUES(?,?,?,?,0)',(digest(access.encode()),family,'access',now+self.limits[2]))
        self.db.execute('INSERT INTO sa_tokens VALUES(?,?,?,?,0)',(digest(refresh.encode()),family,'refresh',now+self.limits[3]))
        return dict(access_token=access,refresh_token=refresh,token_type='Bearer',expires_in=self.limits[2],scope=' '.join(SCOPES))
    def token(self,params):
        if not isinstance(params,dict) or params.get('client_id')!=self.registration['clientId']:raise OAuthError('invalid_client')
        compromised=False
        with self.transaction():
            if params.get('grant_type')=='authorization_code':
                if not {'grant_type','client_id','code','redirect_uri','code_verifier'}<=set(params):raise OAuthError('invalid_request')
                row=self.db.execute('SELECT data,used FROM sa_codes WHERE code=?',(digest(params['code'].encode()),)).fetchone()
                if not row:raise OAuthError('invalid_grant')
                if row[1]:
                    self.db.execute("UPDATE sa_families SET active=0 WHERE json_extract(data,'$.codeHash')=?",(digest(params['code'].encode()),));self.db.execute('COMMIT')
                    raise OAuthError('invalid_grant')
                data=json.loads(row[0]);v=params['code_verifier']
                if not isinstance(v,str) or not re.fullmatch('[A-Za-z0-9._~-]{43,128}',v) or b64url(hashlib.sha256(v.encode()).digest())!=data['challenge'] or data['redirect']!=params['redirect_uri'] or data['expiry']<self.now() or data['registration']!=digest(self.registration_bytes):raise OAuthError('invalid_grant')
                family=secrets.token_hex(32);data.update(codeHash=digest(params['code'].encode()),scopes=SCOPES,issuer=self.registration['issuer'],audience=self.registration['service'])
                self.db.execute('INSERT INTO sa_families VALUES(?,?,1)',(family,json.dumps(data)));self.db.execute('UPDATE sa_codes SET used=1 WHERE code=?',(digest(params['code'].encode()),));result=self._mint(family)
            elif params.get('grant_type')=='refresh_token':
                if not {'grant_type','client_id','refresh_token'}<=set(params) or ('scope'in params and not exact_scope(params['scope'])):raise OAuthError('invalid_scope')
                hashed=digest(params['refresh_token'].encode());row=self.db.execute("SELECT family,expiry,used FROM sa_tokens WHERE hash=? AND kind='refresh'",(hashed,)).fetchone()
                if not row:raise OAuthError('invalid_grant')
                family,expiry,used=row
                active=self.db.execute('SELECT active FROM sa_families WHERE id=?',(family,)).fetchone()
                if used:
                    self.db.execute('UPDATE sa_families SET active=0 WHERE id=?',(family,));compromised=True;result=None
                elif expiry<self.now() or active!=(1,):raise OAuthError('invalid_grant')
                else:self.db.execute('UPDATE sa_tokens SET used=1 WHERE hash=?',(hashed,));result=self._mint(family)
            else:raise OAuthError('unsupported_grant_type')
        if compromised:raise OAuthError('invalid_grant')
        return result
    def grant(self,token,scope):
        if not isinstance(token,str):raise GrantError(401,'invalid_token')
        row=self.db.execute("SELECT family,expiry FROM sa_tokens WHERE hash=? AND kind='access'",(digest(token.encode()),)).fetchone()
        if not row or row[1]<self.now():raise GrantError(401,'invalid_token')
        data=self.db.execute('SELECT data,active FROM sa_families WHERE id=?',(row[0],)).fetchone();v=json.loads(data[0])
        if scope not in v['scopes']:raise GrantError(403,'insufficient_scope')
        if not data[1] or v['audience']!=self.registration['service'] or v['issuer']!=self.registration['issuer'] or v['registration']!=digest(self.registration_bytes):raise GrantError(401,'invalid_token')
        return row[0],v
    def challenge(self,raw,token):
        v=decode_event(raw)['value'];exact(v,'version purpose registrationDigest principal device state binding')
        if v['version']!='0' or v['purpose']!='service-account-link-request' or v['registrationDigest']!=digest(self.registration_bytes) or not re.fullmatch('enp0:[0-9a-f]{64}',v['principal']) or not re.fullmatch('end0:[0-9a-f]{64}',v['device']) or any(not hexvalue(v[k],64) for k in ('state','binding')):raise ValueError('Challenge fields')
        with self.transaction():
            family,_=self.grant(token,'mail.service.link');now=self.now();r=self.registration
            value=dict(v,purpose='service-account-link',challenge=secrets.token_hex(16),nonce=secrets.token_hex(32),issuer=r['issuer'],service=r['service'],clientId=r['clientId'],grantBinding=family,notBefore=str(now),notAfter=str(now+self.limits[1]));payload=encode_event(value)
            self.db.execute('INSERT INTO sa_challenges VALUES(?,?,?,NULL,NULL)',(value['challenge'],family,payload))
        return payload
    def _identity(self,bundle,challenge,time):
        b=decode_identity_bundle(encode_event(bundle));p=challenge['principal']
        if b['principal']!=p:raise ValueError('Identity principal')
        roots=[s for s in b['states'] if s['value'].get('revision')=='0']
        if not self.identity.current_state(p)['head']:
            if len(roots)!=1:raise ValueError('Genesis required')
            root=roots[0];entry=next((x for x in b['bindings'] if x['digest']==root['value']['bindings'][0]['digest']),None)
            if not entry:raise ValueError('Genesis binding')
            record=dict(state=base64.b64encode(root['octets']).decode(),binding=base64.b64encode(entry['octets']).decode(),stateProof=root['signature'],authorization=entry['authorization'],possession=entry['possession'],time=time)
            if self.identity._observe_locked(record,first_contact_policy='allow-unverified')['status']!='pinned-unverified':raise ValueError('Genesis authorization')
        for state in sorted(b['states'],key=lambda s:int(s['value']['revision'])):
            if state['value']['revision']=='0':continue
            outcome=self.identity._accept_locked(encode_event(bundle),p,state,time)
            if outcome['status'] not in ('accepted-unverified','already-recorded'):raise ValueError('Identity successor unavailable')
        binding=next((x for x in b['bindings'] if x['digest']==challenge['binding']),None)
        if not binding or binding['value']['device']!=challenge['device']:raise ValueError('Link binding')
        key=bytes.fromhex(binding['value']['signingKey'])
        auth=self.identity._check_device_locked(p,challenge['device'],key,'send',time,'allow-unverified')
        if auth['status']!='authorized-unverified' or auth['head']!=challenge['state'] or auth['binding']!=challenge['binding']:raise ValueError('Current link authority')
        return key
    def complete(self,raw,token):
        w=decode_event(raw)['value'];exact(w,'payload signature identity')
        try:
            payload=base64.b64decode(w['payload'],validate=True)
            if base64.b64encode(payload).decode()!=w['payload'] or not hexvalue(w['signature'],128):raise ValueError()
            c=decode_event(payload)['value']
        except (TypeError,ValueError) as e:raise ValueError('Link proof encoding') from e
        b=decode_identity_bundle(encode_event(w['identity']))
        with self.transaction():
            family,_=self.grant(token,'mail.service.link');row=self.db.execute('SELECT family,payload,signature,receipt FROM sa_challenges WHERE id=?',(c.get('challenge'),)).fetchone()
            if not row or row[0]!=family or row[1]!=payload:raise ValueError('Challenge binding')
            if row[3] is not None:
                if row[2]!=w['signature']:raise ValueError('Changed link proof')
                return row[3]
            now=self.now()
            if not int(c['notBefore'])<=now<=int(c['notAfter']):raise ValueError('Expired link challenge')
            # Verify candidate signature before installing any identity observations.
            candidate=next((x for x in b['bindings'] if x['digest']==c['binding']),None)
            if not candidate:raise ValueError('Link binding absent')
            try:Ed25519PublicKey.from_public_bytes(bytes.fromhex(candidate['value']['signingKey'])).verify(bytes.fromhex(w['signature']),DOMAIN+len(payload).to_bytes(4,'big')+payload)
            except (InvalidSignature,ValueError) as e:raise ValueError('Invalid link signature') from e
            known=self.identity.current_state(c['principal'])['head'] is not None
            try:self._identity(w['identity'],c,dict(earliest=c['notBefore'],latest=c['notAfter']))
            except ValueError:
                # Valid known-principal transitions/conflicts survive a held link;
                # a failed first-contact link never leaves a partial new pin.
                if known:self.db.execute('COMMIT')
                raise
            existing=self.db.execute('SELECT principal FROM sa_links WHERE family=?',(family,)).fetchone()
            if existing:raise ValueError('Explicit unlink required')
            link=secrets.token_hex(16);receipt=encode_event(dict(version='0',purpose='service-account-link-result',challenge=c['challenge'],requestDigest=digest(payload),service=c['service'],principal=c['principal'],link=link,generation='1',outcome='linked'))
            self.db.execute('INSERT INTO sa_links VALUES(?,?,?,?,?,?,?)',(family,c['principal'],c['device'],c['state'],c['binding'],link,'1'));self.db.execute('UPDATE sa_challenges SET signature=?,receipt=? WHERE id=?',(w['signature'],receipt,c['challenge']))
            return receipt
    def provision_action_account(self,action,principal,account):
        """Trusted operator fixture seam; never called by HTTP/link/submission input.

        Account is an internal non-reassigned incarnation handle. A service action
        cannot silently move its principal's effects/history to another account.
        """
        if action.get('service')!=self.registration['service'] or principal not in action.get('principals',[]) or not isinstance(account,str) or not account:raise ValueError('Action account provisioning')
        key=(action['service'],action['action'],principal)
        with self.transaction():
            old=self.db.execute('SELECT account FROM sa_action_accounts WHERE service=? AND action=? AND principal=?',key).fetchone()
            if old and old!=(account,):raise ValueError('Immutable action account')
            self.db.execute('INSERT OR IGNORE INTO sa_action_accounts VALUES(?,?,?,?)',(*key,account))

    def authorize_service(self,token,action,scope):
        with self.transaction():return self._authorize_service_locked(token,action,scope)
    def _authorize_service_locked(self,token,action,scope):
        try:
            family,grant=self.grant(token,'mail.service.'+scope);row=self.db.execute('SELECT principal,device,state,binding FROM sa_links WHERE family=?',(family,)).fetchone()
            if not row or row[0] not in action['principals'] or action['service']!=self.registration['service']:return None,403
            account=self.db.execute('SELECT account FROM sa_action_accounts WHERE service=? AND action=? AND principal=?',(action['service'],action['action'],row[0])).fetchone()
            if account!=(grant['account'],):return None,403
            current=self.identity.current_state(row[0])
            if current['conflicted']:return None,403
            entry=self.db.execute('SELECT bundle FROM identity_transitions WHERE principal=? AND digest=? AND accepted=1',(row[0],current['head'])).fetchone()
            if entry:
                bundle=decode_identity_bundle(entry[0]);state=next(s['value'] for s in bundle['states'] if s['digest']==current['head']);chosen=next((b['digest'] for b in state['bindings'] if b['device']==row[1]),None);binding=next((b['value'] for b in bundle['bindings'] if b['digest']==chosen),None)
            else:
                entry=self.db.execute('SELECT record FROM claims WHERE principal=? AND digest=?',(row[0],current['head'])).fetchone();binding=decode_event(base64.b64decode(json.loads(entry[0])['binding']))['value'] if entry else None
            if not binding:return None,403
            now=str(self.now());auth=self.identity._check_device_locked(row[0],row[1],bytes.fromhex(binding['signingKey']),'send',dict(earliest=now,latest=now),'allow-unverified')
            if auth['status']!='authorized-unverified':return None,403
            # A fresh current binding is not authority to reuse a link signed
            # under the old binding. Preserve unchanged ancestry only.
            from history_transfer import authorize
            try:authorize(self.identity,dict(principal=row[0],device=row[1],state=row[2],binding=row[3],key=binding['signingKey']),'send',dict(earliest=now,latest=now),'allow-unverified')
            except ValueError:return None,403
            return row[0],200
        except GrantError as error:return None,error.status
        except ValueError:return None,401
    def unlink(self,token):
        with self.transaction():
            family,_=self.grant(token,'mail.service.link');self.db.execute('UPDATE sa_families SET active=0 WHERE id=?',(family,))
