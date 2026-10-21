"""Confidential post-enrollment setup transfer, not a ready-to-send client.

Uses the retained independently confirmed Pairing result and real age encryption.
Accepted plaintext is a private staging record, never an automatic pin/verification
installer. Provider login, contact-store reconciliation and group admission remain
separate integrations. Paths, signer handles and selected export data are local.
"""
import base64
import hashlib
import re
from pathlib import Path
import struct
import subprocess
import tempfile
from time import monotonic_ns

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from correspondence_archive import decrypted_age,exact,oid,digest,uint
from event_encoding import decode_event,encode_event
from history_transfer import RECIPIENT,authorize
from identity_bundle import decode_identity_bundle
from passive_discovery import canonical_base64
from provider_mls import sign
from remote_pairing import decode_offer,request_binding
from email2_mailbox import validate as mailbox

LIMIT=1048576
FIELDS={
 'request':'version purpose transfer session pairingResult source target recipient notBefore notAfter',
 'response':'version purpose transfer session pairingResult request ciphertext',
 'receipt':'version purpose transfer session pairingResult request response result',
}


def sha(raw):return hashlib.sha256(raw).hexdigest()
def b64(raw):return base64.b64encode(raw).decode()
def frame(kind,raw):return ('email2/pairing-setup/'+kind+'/v0').encode()+b'\0'+struct.pack('>I',len(raw))+raw


def unpack(wire,kind):
    outer=decode_event(wire,max_octets=4*LIMIT)['value'];exact(outer,'payload signature')
    raw=canonical_base64(outer['payload']);v=decode_event(raw,max_octets=2*LIMIT)['value'];exact(v,FIELDS[kind])
    if v['version']!='0' or v['purpose']!='pairing-setup-'+kind:raise ValueError('Setup purpose/version')
    oid(v['transfer']);digest(v['session']);digest(v['pairingResult'])
    signature=outer['signature']
    if type(signature) is not str or len(signature)!=128:raise ValueError('Setup signature spelling')
    try:sig=bytes.fromhex(signature)
    except ValueError as error:raise ValueError('Setup signature spelling') from error
    if sig.hex()!=signature:raise ValueError('Setup signature spelling')
    if kind=='request':
        if type(v['recipient']) is not str or not RECIPIENT.fullmatch(v['recipient']):raise ValueError('Native setup recipient')
        if uint(v['notAfter'])<uint(v['notBefore']):raise ValueError('Setup interval')
    else:
        digest(v['request'])
        if kind=='response':
            if len(canonical_base64(v['ciphertext']))>LIMIT:raise ValueError('Setup ciphertext limit')
        else:
            digest(v['response'])
            if v['result'] not in ('staged','installed'):raise ValueError('Setup receipt result')
    return raw,v,sig,sha(frame(kind,raw)+sig)


def policy(v):
    exact(v,'trust ordinary hosted freshness maximumAge maximumUncertainty')
    if v['trust'] not in ('allow-unverified','require-verification') or type(v['ordinary']) is not bool or type(v['hosted']) is not bool:raise ValueError('Setup policy')
    if v['freshness'] not in ('cached-continuity','recent-checkpoint','live-confirmation'):raise ValueError('Setup freshness')
    if v['freshness']=='cached-continuity':
        if v['maximumAge']!='':raise ValueError('Cached mode has no implicit age')
    elif uint(v['maximumAge'])==0:raise ValueError('Positive freshness age')
    if v['maximumUncertainty']!='':uint(v['maximumUncertainty'])


def elapsed_interval(clock,started):
    # Account for local crypto/staging time; callers still supply trusted initial time.
    elapsed=monotonic_ns()-started
    if elapsed<0:raise ValueError('Unresolved monotonic clock')
    return dict(earliest=str(uint(clock['earliest'])+elapsed//1000000000),
                latest=str(uint(clock['latest'])+(elapsed+999999999)//1000000000))


def configuration(value):
    exact(value,'contacts defaults');policy(value['defaults'])
    if type(value['contacts']) is not list:raise ValueError('Setup contacts')
    addresses=[];origins={}
    for c in value['contacts']:
        exact(c,'mailbox principal anchor head bundle generation enabled verification policy')
        mailbox(c['mailbox']);addresses.append(c['mailbox']);digest(c['anchor']);digest(c['head']);uint(c['generation'])
        if type(c['enabled']) is not bool:raise ValueError('Association status')
        bundle=decode_identity_bundle(canonical_base64(c['bundle']))
        if bundle['principal']!=c['principal'] or c['anchor'] not in [s['digest'] for s in bundle['states']] or c['head'] not in [s['digest'] for s in bundle['states']]:raise ValueError('Contact evidence references')
        policy(c['policy'])
        if type(c['verification']) is not list:raise ValueError('Verification list')
        ids=[]
        for proof in c['verification']:
            exact(proof,'id originDevice mechanism anchor notBefore notAfter continuity status revision')
            oid(proof['id']);digest(proof['anchor']);uint(proof['revision'])
            if type(proof['originDevice']) is not str or not re.fullmatch(r'end0:[0-9a-f]{64}',proof['originDevice']) or proof['originDevice']=='end0:'+'0'*64:raise ValueError('Original comparison device')
            ids.append((proof['originDevice'],proof['id']))
            scope=(c['mailbox'],c['principal'],proof['anchor'],proof['notBefore'],proof['notAfter'],proof['continuity'])
            key=(proof['originDevice'],proof['id'])
            if key in origins and origins[key]!=scope:raise ValueError('Original verification decision has conflicting scope')
            origins[key]=scope
            if proof['mechanism']!='human-comparison-v0' or proof['continuity'] not in ('anchor-only','ordinary-authorized-descendants') or proof['status'] not in ('accepted','withdrawn') or uint(proof['notAfter'])<uint(proof['notBefore']):raise ValueError('Verification scope')
            if proof['anchor'] not in [s['digest'] for s in bundle['states']]:raise ValueError('Verification anchor missing')
        if ids!=sorted(set(ids)):raise ValueError('Sorted unique verification records')
    if addresses!=sorted(set(addresses)):raise ValueError('Sorted unique contact mailboxes')
    return value


class SetupTransfer:
    def __init__(self,pairing,device,binary,*,age='age',staging_parent):
        self.pairing=pairing;self.device=device;self.binary=binary;self.age=str(age)
        self.ids=pairing.identity;self.db=pairing.db;self.parent=Path(staging_parent)
        if self.db.in_transaction or not self.parent.is_dir():raise ValueError('Trusted setup configuration')
        self.db.execute('''CREATE TABLE IF NOT EXISTS pairing_setup(account TEXT NOT NULL,transfer TEXT NOT NULL,
          request BLOB NOT NULL,response BLOB,configuration BLOB,receipt BLOB,cancelled INTEGER NOT NULL,
          PRIMARY KEY(account,transfer))''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS pairing_setup_conflicts(account TEXT NOT NULL,transfer TEXT NOT NULL,reference TEXT NOT NULL,wire BLOB NOT NULL,PRIMARY KEY(account,transfer,reference))''')

    def _pair(self,session,time):
        offer,anchor,request,status,result=self.pairing._row(session)
        if status not in ('committed','received') or result is None:raise ValueError('Accepted local pairing result required')
        o=decode_offer(offer);_,_,new=request_binding(request,offer);r=decode_event(result)['value']
        bundle=decode_identity_bundle(canonical_base64(r['bundle']));head=r['head']
        state=next(s['value'] for s in bundle['states'] if s['digest']==head)
        def endpoint(device):
            ref=next(x for x in state['bindings'] if x['device']==device)
            b=next(x['value'] for x in bundle['bindings'] if x['digest']==ref['digest'])
            return dict(principal=o['principal'],device=device,state=head,binding=ref['digest'],key=b['signingKey'])
        source,target=endpoint(o['authorizer']),endpoint(new['device'])
        # This retains unchanged accepted ancestry, never a revoked binding.
        a=authorize(self.ids,source,'enroll',time,'allow-unverified');b=authorize(self.ids,target,'send',time,'allow-unverified')
        if self.device['device'] not in (source['device'],target['device']) or self.device['principal']!=o['principal']:raise ValueError('Local paired endpoint')
        return dict(source=source,target=target,pairingResult=sha(result),session=session),max(a['before'],b['before'],uint(state['issuedAt'])),min(a['after'],b['after'])

    def _verify(self,wire,kind,key):
        raw,v,sig,reference=unpack(wire,kind)
        try:Ed25519PublicKey.from_public_bytes(bytes.fromhex(key)).verify(sig,frame(kind,raw))
        except InvalidSignature as error:raise ValueError('Setup signature') from error
        return v,reference

    def _request(self,wire,time):
        _,v,_,_=unpack(wire,'request')
        if self.db.execute('SELECT 1 FROM pairing_setup_conflicts WHERE account=? AND transfer=?',(self.pairing.account,v['transfer'])).fetchone():raise ValueError('Authenticated setup conflict held')
        pair,before,after=self._pair(v['session'],time)
        if any(v[k]!=pair[k] for k in pair):raise ValueError('Exact accepted pairing required')
        lo,hi=uint(time['earliest']),uint(time['latest'])
        if not before<=uint(v['notBefore'])<=lo<=hi<=uint(v['notAfter'])<=after:raise ValueError('Original setup interval')
        _,reference=self._verify(wire,'request',pair['target']['key']);return v,reference,pair

    def _sign(self,kind,value):
        raw=encode_event(value)
        return encode_event(dict(payload=b64(raw),signature=sign(self.binary,self.device,'email2/pairing-setup/'+kind+'/v0',raw)))

    def request(self,transfer,session,recipient,*,not_before,not_after,time):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            pair,_,_=self._pair(session,time)
            if self.device['device']!=pair['target']['device']:raise ValueError('New device request required')
            v=dict(version='0',purpose='pairing-setup-request',transfer=transfer,**pair,recipient=recipient,notBefore=not_before,notAfter=not_after)
            wire=self._sign('request',v);self._request(wire,time)
            old=self.db.execute('SELECT request,cancelled FROM pairing_setup WHERE account=? AND transfer=?',(self.pairing.account,transfer)).fetchone()
            if old:
                if old[0]!=wire or old[1]:raise ValueError('Immutable or cancelled setup request')
                self.db.execute('COMMIT');return old[0]
            self.db.execute('INSERT INTO pairing_setup VALUES(?,?,?,NULL,NULL,NULL,0)',(self.pairing.account,transfer,wire));self.db.execute('COMMIT');return wire
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise

    def release(self,request,selected,*,time,crash=None):
        # selected is a trusted local consistent export, not an incoming body.
        started=monotonic_ns()
        configuration(selected);plain=encode_event(selected)
        if len(plain)>LIMIT//2:raise ValueError('Setup plaintext limit')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            r,reference,pair=self._request(request,time)
            if self.device['device']!=pair['source']['device']:raise ValueError('Approving source required')
            old=self.db.execute('SELECT request,response,configuration,cancelled FROM pairing_setup WHERE account=? AND transfer=?',(self.pairing.account,r['transfer'])).fetchone()
            if old:
                if old[0]!=request or old[2]!=plain or old[3]:raise ValueError('Immutable setup snapshot')
                self.db.execute('COMMIT');return old[1]
            encrypted=subprocess.run([self.age,'--encrypt','--recipient',r['recipient']],input=plain,capture_output=True,timeout=30)
            if encrypted.returncode or len(encrypted.stdout)>LIMIT:raise ValueError('Setup encryption failed')
            v=dict(version='0',purpose='pairing-setup-response',transfer=r['transfer'],session=r['session'],pairingResult=r['pairingResult'],request=reference,ciphertext=b64(encrypted.stdout))
            response=self._sign('response',v);self._verify(response,'response',pair['source']['key'])
            self._request(request,elapsed_interval(time,started))
            self.db.execute('INSERT INTO pairing_setup VALUES(?,?,?,?,?,NULL,0)',(self.pairing.account,r['transfer'],request,response,plain))
            if crash:crash('before-release-commit')
            self.db.execute('COMMIT');return response
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise

    def stage(self,response,identity_file,*,time,crash=None):
        started=monotonic_ns()
        _,v,_,_=unpack(response,'response')
        row=self.db.execute('SELECT request,response,receipt,cancelled FROM pairing_setup WHERE account=? AND transfer=?',(self.pairing.account,v['transfer'])).fetchone()
        if not row or row[3]:raise ValueError('Retained active local request required')
        # Decrypt/authenticate completely outside the write transaction.
        r,reference,pair=self._request(row[0],time)
        if self.device['device']!=pair['target']['device']:raise ValueError('Requested target required')
        value,response_ref=self._verify(response,'response',pair['source']['key'])
        if any(value[k]!=r[k] for k in ('transfer','session','pairingResult')) or value['request']!=reference:raise ValueError('Response request binding')
        if row[1]:
            if row[1]!=response:
                self.db.execute('BEGIN IMMEDIATE')
                try:
                    self._request(row[0],elapsed_interval(time,started))
                    for wire in [row[1],response]:
                        ref=unpack(wire,'response')[3]
                        self.db.execute('INSERT OR IGNORE INTO pairing_setup_conflicts VALUES(?,?,?,?)',(self.pairing.account,r['transfer'],ref,wire))
                    self.db.execute('COMMIT')
                except BaseException:
                    if self.db.in_transaction:self.db.execute('ROLLBACK')
                    raise
                raise ValueError('Authenticated setup response conflict')
            return row[2]
        # Check that this local key file belongs to the signed request recipient.
        with Path(identity_file).open('rb') as source:identity=source.read(4097)
        keys=[line for line in identity.splitlines() if line and not line.startswith(b'#')]
        if len(identity)>4096 or len(keys)!=1 or not re.fullmatch(rb'AGE-SECRET-KEY-1[0-9A-Z]+',keys[0]):raise ValueError('One native local setup identity required')
        recipient=subprocess.run([str(Path(self.age).with_name('age-keygen')),'-y',str(identity_file)],capture_output=True,timeout=10)
        if recipient.returncode or recipient.stdout.strip().decode()!=r['recipient']:raise ValueError('Wrong local setup identity')
        with tempfile.TemporaryDirectory(prefix='.pairing-setup-',dir=self.parent) as temp:
            path=Path(temp)/'setup.age';path.write_bytes(canonical_base64(value['ciphertext']))
            with decrypted_age(path,identity_file,temp,age=self.age,max_ciphertext=LIMIT,max_plaintext=LIMIT//2) as (clear,_,__):
                plain=clear.read_bytes();configuration(decode_event(plain)['value'])
        self.db.execute('BEGIN IMMEDIATE')
        try:
            r,reference,pair=self._request(row[0],elapsed_interval(time,started))
            current=self.db.execute('SELECT request,response,cancelled FROM pairing_setup WHERE account=? AND transfer=?',(self.pairing.account,r['transfer'])).fetchone()
            if current!=(row[0],None,0):raise ValueError('Setup changed during decryption')
            receipt=self._sign('receipt',dict(version='0',purpose='pairing-setup-receipt',transfer=r['transfer'],session=r['session'],pairingResult=r['pairingResult'],request=reference,response=response_ref,result='staged'))
            self._verify(receipt,'receipt',pair['target']['key'])
            self.db.execute('UPDATE pairing_setup SET response=?,configuration=?,receipt=? WHERE account=? AND transfer=?',(response,plain,receipt,self.pairing.account,r['transfer']))
            if crash:crash('before-stage-commit')
            self.db.execute('COMMIT');return receipt
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise

    def cancel(self,transfer):
        # Local cancellation only; it cannot recall already exported configuration.
        self.db.execute('UPDATE pairing_setup SET cancelled=1 WHERE account=? AND transfer=?',(self.pairing.account,transfer))
