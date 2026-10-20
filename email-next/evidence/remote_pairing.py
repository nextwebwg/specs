"""Experimental public-evidence pairing. Trusted comparisons are local UI input.

No received record confirms itself, enables publication or transfers private keys.
Session expiry and device grant validity are separate adjustable client choices.
"""
import base64,hashlib,json,re,secrets
from event_encoding import encode_event,decode_event
from identity_bundle import decode_identity_bundle
from own_devices import OwnDevices,packed,digest
from mls_receive import LockedIdentity,MlsReceive
from provider_control import verify_signature
from provider_mls import sign

OFFER=set('version purpose session principal head authorizer anchorBundleDigest mailboxes roles notBefore notAfter grantNotBefore grantNotAfter'.split())
REQUEST=set('version purpose session offerDigest binding possession'.split())
def commitment(kind,raw):
    if kind not in ('offer','request'):raise ValueError('Pairing commitment purpose')
    return hashlib.sha256(('email-next/pairing-'+kind+'-experiment/v0\0').encode()+raw).hexdigest()
def b64(raw):return base64.b64encode(raw).decode()
def un64(s):
    raw=base64.b64decode(s,validate=True)
    if b64(raw)!=s:raise ValueError('Canonical base64')
    return raw

def interval(before,after,time):
    MlsReceive._policy(dict(earliest=before,latest=after),'allow-unverified');MlsReceive._policy(time,'allow-unverified')
    if not int(before)<=int(time['earliest'])<=int(time['latest'])<=int(after):raise ValueError('Pairing validity interval')
def decode_offer(raw):
    v=decode_event(raw)['value']
    if set(v)!=OFFER or v['version']!='0' or v['purpose']!='own-device-pairing-offer' or not re.fullmatch('[0-9a-f]{64}',v['session']):raise ValueError('Pairing offer schema')
    if not isinstance(v['roles'],list) or not v['roles'] or v['roles']!=sorted(set(v['roles'])) or not set(v['roles'])<=set(('send','receive','enroll','revoke')):raise ValueError('Pairing roles')
    from passive_discovery import mailbox_syntax
    if not isinstance(v['mailboxes'],list) or not v['mailboxes'] or v['mailboxes']!=sorted(set(v['mailboxes'])):raise ValueError('Pairing mailboxes')
    for m in v['mailboxes']:mailbox_syntax(m)
    for a,z in [('notBefore','notAfter'),('grantNotBefore','grantNotAfter')]:MlsReceive._policy(dict(earliest=v[a],latest=v[z]),'allow-unverified')
    return v

def request_binding(raw,offer):
    r=decode_event(raw)['value'];o=decode_offer(offer)
    if set(r)!=REQUEST or (r['version'],r['purpose'],r['session'],r['offerDigest'])!=('0','own-device-pairing-request',o['session'],commitment('offer',offer)):raise ValueError('Pairing request scope')
    binding=un64(r['binding']);v=decode_event(binding)['value']
    expected=set('version purpose record principal device signingKey roles notBefore notAfter authority'.split())
    if set(v)!=expected or v['version']!='0' or v['purpose']!='device-binding' or v['principal']!=o['principal'] or v['authority']!={'kind':'state','digest':o['head']} or v['roles']!=o['roles'] or (v['notBefore'],v['notAfter'])!=(o['grantNotBefore'],o['grantNotAfter']):raise ValueError('Exact offered binding')
    if not re.fullmatch('end0:[0-9a-f]{64}',v['device']) or v['device']=='end0:'+'0'*64:raise ValueError('Device identifier')
    verify_signature(binding,r['possession'],v['signingKey'],b'email-next/device-possession/v0\0')
    return r,binding,v

class Pairing:
    def __init__(self,identity,*,account,max_bytes=1048576):
        self.identity=identity;self.db=identity.db;self.account=account;self.max_bytes=max_bytes
        if self.db.in_transaction:raise ValueError('Initialize outside transaction')
        if not isinstance(account,str) or not account or type(max_bytes)!=int or max_bytes<1:raise ValueError('Local pairing configuration')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS pairing_sessions(account TEXT NOT NULL,session TEXT NOT NULL,offer BLOB NOT NULL,anchor BLOB NOT NULL,request BLOB,status TEXT NOT NULL,result BLOB,PRIMARY KEY(account,session));''')
    def _row(self,session):
        row=self.db.execute('SELECT offer,anchor,request,status,result FROM pairing_sessions WHERE account=? AND session=?',(self.account,session)).fetchone()
        if not row:raise ValueError('Unknown pairing session')
        return row
    def _bound(self,*raw):
        if any(not isinstance(x,bytes) or len(x)>self.max_bytes for x in raw):raise ValueError('Pairing input bound')
    def offer(self,owner,anchor,*,roles,session_before,session_after,grant_before,grant_after,time):
        self._bound(anchor)
        if owner.db is not self.db or owner.config['account']!=self.account:raise ValueError('Same account database required')
        interval(session_before,session_after,time);interval(grant_before,grant_after,time)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            head,state,bindings=owner._state();binding=next(bindings[r['digest']] for r in state['bindings'] if r['device']==owner.config['localDevice'])
            credential=b'email-next/device/v0\0'+bytes.fromhex(owner.config['principal'][5:])+bytes.fromhex(owner.config['localDevice'][5:])
            if LockedIdentity(self.identity).check_device(credential,bytes.fromhex(binding['signingKey']),role='enroll',time=time,trust_policy='allow-unverified')['status']!='authorized-unverified':raise ValueError('Current enrollment authority required')
            interval(binding['notBefore'],binding['notAfter'],dict(earliest=grant_before,latest=grant_after))
            interval(binding['notBefore'],binding['notAfter'],dict(earliest=session_before,latest=session_after))
            if not set(roles)<=set(binding['roles']):raise ValueError('Cannot grant new authority')
            decoded=decode_identity_bundle(anchor)
            if decoded['principal']!=owner.config['principal'] or head not in [s['digest'] for s in decoded['states']]:raise ValueError('Exact current anchor evidence')
            v=dict(version='0',purpose='own-device-pairing-offer',session=secrets.token_hex(32),principal=owner.config['principal'],head=head,authorizer=owner.config['localDevice'],anchorBundleDigest=digest(anchor),mailboxes=owner.config['mailboxes'],roles=roles,notBefore=session_before,notAfter=session_after,grantNotBefore=grant_before,grantNotAfter=grant_after)
            raw=encode_event(v);decode_offer(raw)
            self.db.execute('INSERT INTO pairing_sessions VALUES(?,?,?,?,NULL,?,NULL)',(self.account,v['session'],raw,anchor,'offered'));self.db.execute('COMMIT');return raw
        except BaseException:self.db.execute('ROLLBACK');raise
    def confirm_offer(self,offer,anchor,*,comparison,channel,time):
        """Trusted scan/full comparison event, not callable by relay ingestion."""
        self._bound(offer,anchor);o=decode_offer(offer)
        if channel not in ('independent-qr','independent-full-comparison') or comparison!=commitment('offer',offer) or digest(anchor)!=o['anchorBundleDigest']:raise ValueError('Independent offer confirmation required')
        interval(o['notBefore'],o['notAfter'],time);decoded=decode_identity_bundle(anchor)
        if decoded['principal']!=o['principal']:raise ValueError('Anchor principal')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            prior=self.db.execute('SELECT offer,anchor,status FROM pairing_sessions WHERE account=? AND session=?',(self.account,o['session'])).fetchone()
            if prior:
                if prior[:2]!=(offer,anchor) or prior[2] in ('withdrawn','expired'):raise ValueError('Session conflict')
                self.db.execute('COMMIT');return o['session']
            genesis=next(s for s in decoded['states'] if s['value']['revision']=='0');g=genesis['value'];ref=g['bindings'][0];binding=next(b for b in decoded['bindings'] if b['digest']==ref['digest'])
            record=dict(state=b64(genesis['octets']),binding=b64(binding['octets']),stateProof=genesis['signature'],authorization=binding['authorization'],possession=binding['possession'],time=dict.fromkeys(('earliest','latest'),g['issuedAt']))
            if self.identity._observe_locked(record,first_contact_policy='allow-unverified')['status']!='pinned-unverified':raise ValueError('Existing anchor conflict')
            for state in sorted(decoded['states'],key=lambda s:int(s['value']['revision'])):
                if state['value']['revision']=='0':continue
                accepted=self.identity._accept_locked(anchor,o['principal'],state,time)
                if accepted['status'] not in ('accepted-unverified','already-recorded'):raise ValueError('Anchor chain unresolved')
            head=self.identity.current_state(o['principal'])
            if head['head']!=o['head'] or head['conflicted']:raise ValueError('Confirmed head conflict')
            self.db.execute('INSERT INTO pairing_sessions VALUES(?,?,?,?,NULL,?,NULL)',(self.account,o['session'],offer,anchor,'confirmed-offer'));self.db.execute('COMMIT');return o['session']
        except BaseException:self.db.execute('ROLLBACK');raise
    def request(self,session,device,*,binary,time):
        offer,anchor,old,status,result=self._row(session);o=decode_offer(offer)
        if status not in ('confirmed-offer','requested'):raise ValueError('Offer confirmation required')
        if old:return old
        interval(o['notBefore'],o['notAfter'],time)
        if device['principal']!=o['principal']:raise ValueError('Device account')
        value=dict(version='0',purpose='device-binding',record=secrets.token_hex(16),principal=o['principal'],device=device['device'],signingKey=device['key'],roles=o['roles'],notBefore=o['grantNotBefore'],notAfter=o['grantNotAfter'],authority=dict(kind='state',digest=o['head']))
        binding=encode_event(value);raw=encode_event(dict(version='0',purpose='own-device-pairing-request',session=session,offerDigest=commitment('offer',offer),binding=b64(binding),possession=sign(binary,device,'email-next/device-possession/v0',binding)))
        request_binding(raw,offer)
        changed=self.db.execute('UPDATE pairing_sessions SET request=?,status=? WHERE account=? AND session=? AND status=? AND request IS NULL',(raw,'requested',self.account,session,'confirmed-offer')).rowcount
        if changed!=1:raise ValueError('Pairing state changed')
        return raw
    def commit(self,session,request,*,owner,device,binary,comparison,channel,time,crash=None):
        self._bound(request)
        if owner.db is not self.db or owner.config['account']!=self.account or owner.config['localDevice']!=device['device']:raise ValueError('Local enrollment account/device')
        if channel not in ('independent-qr','independent-full-comparison') or comparison!=commitment('request',request):raise ValueError('Independent request confirmation required')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            offer,anchor,old,status,result=self._row(session);o=decode_offer(offer);r,binding,v=request_binding(request,offer)
            if result:
                if old!=request:raise ValueError('Request retry conflict')
                self.db.execute('COMMIT');return result
            if status!='offered':raise ValueError('Session not available')
            interval(o['notBefore'],o['notAfter'],time);interval(o['grantNotBefore'],o['grantNotAfter'],time)
            head,state,_=owner._state()
            if head!=o['head'] or device['principal']!=o['principal'] or device['device']!=o['authorizer']:raise ValueError('Offer head/authorizer changed')
            if v['device'] in state['revoked'] or v['device'] in [b['device'] for b in state['bindings']]:raise ValueError('New device required')
            bundle=json.loads(anchor);nxt=dict(state,record=secrets.token_hex(16),revision=str(int(state['revision'])+1),issuedAt=time['latest'],previous=[head],bindings=sorted(state['bindings']+[dict(device=v['device'],digest=digest(binding))],key=lambda x:x['device']),signer=device['device'])
            raw=encode_event(nxt);bundle['states'].insert(0,dict(payload=b64(raw),signature=sign(binary,device,'email-next/identity-state/v0',raw)));bundle['bindings'].append(dict(payload=b64(binding),authorization=sign(binary,device,'email-next/device-binding/v0',binding),possession=r['possession']))
            public=encode_event(bundle)
            self.db.execute('INSERT INTO own_approval VALUES(?,?,?,NULL)',('pairing:'+session,head,binding))
            owner._commit_enrollment_locked('pairing:'+session,public,candidate_digest=digest(raw),time=time)
            result=encode_event(dict(version='0',purpose='own-device-pairing-result',session=session,requestDigest=commitment('request',request),head=digest(raw),bundle=b64(public)))
            self.db.execute('UPDATE pairing_sessions SET request=?,status=?,result=? WHERE account=? AND session=?',(request,'committed',result,self.account,session))
            if crash:crash('before-commit')
            self.db.execute('COMMIT');return result
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def accept(self,session,result,*,time,crash=None):
        self._bound(result);value=decode_event(result)['value']
        if set(value)!=set('version purpose session requestDigest head bundle'.split()) or (value['version'],value['purpose'],value['session'])!=('0','own-device-pairing-result',session):raise ValueError('Pairing result schema')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            offer,anchor,request,status,prior=self._row(session)
            if prior:
                if prior!=result:raise ValueError('Result conflict')
                self.db.execute('COMMIT');return dict(status='already-received',head=value['head'])
            if status!='requested' or value['requestDigest']!=commitment('request',request):raise ValueError('Pairing result request')
            o=decode_offer(offer);r,binding,v=request_binding(request,offer);raw=un64(value['bundle']);bundle=decode_identity_bundle(raw)
            state=next(s for s in bundle['states'] if s['digest']==value['head']);old=next(s['value'] for s in bundle['states'] if s['digest']==o['head'])
            if state['value']['previous']!=[o['head']] or state['value']['signer']!=o['authorizer'] or state['value']['revoked']!=old['revoked'] or state['value']['bindings']!=sorted(old['bindings']+[dict(device=v['device'],digest=digest(binding))],key=lambda b:b['device']):raise ValueError('Exact enrollment successor')
            if not any(b['octets']==binding and b['possession']==r['possession'] for b in bundle['bindings']):raise ValueError('Exact new binding required')
            interval(o['notBefore'],o['notAfter'],dict.fromkeys(('earliest','latest'),state['value']['issuedAt']))
            outcome=self.identity._accept_locked(raw,o['principal'],state,time)
            if outcome['status'] not in ('accepted-unverified','already-recorded'):raise ValueError('Enrollment unavailable')
            credential=b'email-next/device/v0\0'+bytes.fromhex(o['principal'][5:])+bytes.fromhex(v['device'][5:])
            for role in v['roles']:
                if LockedIdentity(self.identity).check_device(credential,bytes.fromhex(v['signingKey']),role=role,time=time,trust_policy='allow-unverified')['status']!='authorized-unverified':raise ValueError('Current enrolled-device authority unavailable')
            self.db.execute('UPDATE pairing_sessions SET status=?,result=? WHERE account=? AND session=?',('received',result,self.account,session))
            if crash:crash('before-receipt')
            self.db.execute('COMMIT');return dict(status='received',head=value['head'])
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def withdraw(self,session):
        changed=self.db.execute("UPDATE pairing_sessions SET status='withdrawn' WHERE account=? AND session=? AND status IN ('offered','confirmed-offer','requested')",(self.account,session)).rowcount
        return 'withdrawn' if changed else 'already-terminal'
    def result(self,session):return self._row(session)[4]
