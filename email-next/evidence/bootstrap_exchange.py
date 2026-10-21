"""Content-free bootstrap component, not public OAuth/HTTP or MLS admission.

Account/descriptor/recipient-slot facts are trusted service inputs, never message
booleans. Advertisements get exact public syntax/signature checks here, not full
identity-bundle/MLS KeyPackage validation. A ready result remains a candidate and
cannot release human content. Source and target identity stores are separate.
"""
import base64
from dataclasses import dataclass
import hashlib
import struct

from event_encoding import decode_event,encode_event
from identity_bundle import decode_identity_bundle
from history_transfer import endpoint,authority_snapshot
from passive_discovery import uint64
from email2_mailbox import validate as validate_mailbox,selected_domain
from relay_routes import exact,hex_value,origin,current
from suite_modules import validate_offers
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

FIELDS={
 'source':'version purpose preparation request source issuer delegation accountSource senderMailbox sender targetMailbox targetService conversation advertisement nonce notBefore notAfter',
 'inspect':'version purpose issuer exchange sourceDigest nonce notBefore notAfter',
 'cancel':'version purpose issuer exchange sourceDigest nonce notBefore notAfter',
 'response':'version purpose response issuer exchange sourceDigest nonce mailbox device advertisement relayDomain notBefore notAfter',
 'publication':'version purpose publication issuer mailbox device advertisement relayDomain scope notBefore notAfter',
}


def b64(value):
    if not isinstance(value,str) or len(value)>1398104:raise ValueError('Bounded base64 required')
    try:raw=base64.b64decode(value,validate=True)
    except (TypeError,ValueError) as error:raise ValueError('Bootstrap base64') from error
    if base64.b64encode(raw).decode()!=value:raise ValueError('Canonical bootstrap base64')
    return raw


def frame(kind,raw):
    if kind not in FIELDS:raise ValueError('Bootstrap kind')
    return ('email2/bootstrap/'+kind+'/v0').encode()+b'\0'+struct.pack('>I',len(raw))+raw


def verify(kind,raw,sig,key):
    hex_value(key)
    try:Ed25519PublicKey.from_public_bytes(bytes.fromhex(key)).verify(sig,frame(kind,raw))
    except InvalidSignature as error:raise ValueError('Bootstrap signature') from error


def signed(kind,raw,key):
    value=dict(payload=base64.b64encode(raw).decode(),signature=key.sign(frame(kind,raw)).hex())
    parse(value,kind);return value


def mailbox(value):
    validate_mailbox(value)


def parse(proof,kind):
    exact(proof,'payload signature');raw=b64(proof['payload']);hex_value(proof['signature'],128)
    v=decode_event(raw,max_octets=262144)['value'];exact(v,FIELDS[kind])
    if v['version']!='0' or v['purpose']!='bootstrap-'+kind:raise ValueError('Bootstrap purpose/version')
    origin(v['issuer']);before,after=uint64(v['notBefore']),uint64(v['notAfter'])
    if after<before:raise ValueError('Bootstrap interval')
    if kind=='source':
        if after-before>600:raise ValueError('Fixed source deadline')
        for k in ['preparation','request','conversation']:hex_value(v[k],32)
        for k in ['source','delegation','accountSource','nonce']:hex_value(v[k])
        for k in ['senderMailbox','targetMailbox']:mailbox(v[k])
        origin(v['targetService']);endpoint(v['sender']);b64(v['advertisement'])
    elif kind in ['inspect','cancel']:
        for k in ['exchange','sourceDigest','nonce']:hex_value(v[k])
    else:
        endpoint(v['device']);mailbox(v['mailbox']);b64(v['advertisement'])
        if v['relayDomain']!='':mailbox('x@'+v['relayDomain'])
        hex_value(v['response' if kind=='response' else 'publication'],32)
        if kind=='response':
            for k in ['exchange','sourceDigest','nonce']:hex_value(v[k])
        elif v['scope']!='automatic-first-contact' or after-before>604800:raise ValueError('Publication scope/lifetime')
    return raw,v,bytes.fromhex(proof['signature'])


def interval(v,time):
    if not isinstance(time,tuple) or len(time)!=2 or any(type(t) is not int for t in time) or not 0<=time[0]<=time[1]<2**64:
        raise ValueError('Credible current-time interval required')
    if not int(v['notBefore'])<=time[0]<=time[1]<=int(v['notAfter']):raise ValueError('Bootstrap not current')


def advertisement(encoded,actor,address,time,*,package=False):
    # Supplemental assertion8 checks; no accepted identity anchor is installed.
    wrapper=decode_event(b64(encoded))['value'];exact(wrapper,'payload signature identity')
    raw=b64(wrapper['payload']);v=decode_event(raw)['value']
    exact(v,'version purpose record principal device state binding mailbox notBefore notAfter features keyPackage applications orderingExchanges')
    if v['version']!='8' or v['purpose']!='passive-discovery':raise ValueError('Required assertion8')
    for k in ['principal','device','state','binding']:
        if v[k]!=actor[k]:raise ValueError('Assertion endpoint mismatch')
    hex_value(v['record'],32);mailbox(v['mailbox'])
    if v['mailbox']!=address or v['features']!=['mls-1-0001'] or v['orderingExchanges']!=[dict(format='quorum-exchange-experiment',version='2')]:
        raise ValueError('Exact advertisement mailbox/features')
    validate_offers(v['applications']);interval(v,time)
    if uint64(v['notAfter'])-uint64(v['notBefore'])>604800:raise ValueError('Advertisement lifetime')
    identity=decode_identity_bundle(encode_event(wrapper['identity']))
    if identity['principal']!=actor['principal'] or not any(s['digest']==actor['state'] for s in identity['states']) or not any(b['digest']==actor['binding'] for b in identity['bindings']):
        raise ValueError('Assertion bundle references')
    hex_value(wrapper['signature'],128)
    data=b'email-next/passive-discovery/v8\0'+struct.pack('>I',len(raw))+raw
    try:Ed25519PublicKey.from_public_bytes(bytes.fromhex(actor['key'])).verify(bytes.fromhex(wrapper['signature']),data)
    except InvalidSignature as error:raise ValueError('Assertion signature') from error
    kp=v['keyPackage']
    if not isinstance(kp,list) or len(kp)>1 or (package and len(kp)!=1):raise ValueError('Admission material required')
    decoded=[b64(item) for item in kp]
    if any(not data for data in decoded):raise ValueError('Empty package')
    return v,decoded


@dataclass(frozen=True)
class SourceAccount:
    domain:str
    issuer:str
    delegation:str
    mailbox:str
    sender:dict
    account_source:str
    active:bool=True
    not_before:int=10
    not_after:int=100


@dataclass(frozen=True)
class SourceObservation:
    domain:str
    issuer:str
    delegation:str
    proof:dict
    active:bool=True


@dataclass(frozen=True)
class RecipientSlot:
    account:str  # Trusted incarnation/link/family namespace, not a supplied mailbox ID.
    mailbox:str
    device:dict
    enabled:bool=True
    device_enabled:bool=True
    active:bool=True
    relay_domain:str=''


def authorize_source(proof,account,identities,*,retained_preparation,target_domain,target_service,time=(20,21)):
    raw,v,sig=parse(proof,'source')
    if not isinstance(account,SourceAccount) or not account.active or raw!=retained_preparation:
        raise ValueError('Own active account and original preparation required')
    if (v['issuer']!=account.issuer or v['delegation']!=account.delegation or v['accountSource']!=account.account_source
            or v['senderMailbox']!=account.mailbox or v['sender']!=account.sender
            or selected_domain(v['senderMailbox'])!=account.domain or selected_domain(v['targetMailbox'])!=target_domain
            or v['targetService']!=target_service or int(v['notBefore'])<account.not_before or int(v['notAfter'])>account.not_after):
        raise ValueError('Authoritative account/delegation/target scope')
    interval(v,time);verify('source',raw,sig,account.sender['key'])
    with authority_snapshot(identities):
        for role in ['send','receive']:
            bound=current(identities,account.sender,role,time,'allow-unverified')
            if int(v['notBefore'])<bound['before'] or int(v['notAfter'])>bound['after']:raise ValueError('Source device lifetime')
        ad,_=advertisement(v['advertisement'],v['sender'],v['senderMailbox'],time)
        if int(v['notBefore'])<int(ad['notBefore']) or int(v['notAfter'])>int(ad['notAfter']):raise ValueError('Source advertisement interval')
    return SourceObservation(account.domain,account.issuer,account.delegation,proof)


def handle(v):
    issuer=v['issuer'].encode()
    return hashlib.sha256(b'email2/bootstrap/exchange/v0\0'+struct.pack('>I',len(issuer))+issuer+bytes.fromhex(v['source'])).hexdigest()


class BootstrapExchange:
    def __init__(self,identities,issuer,domain):
        origin(issuer);mailbox('x@'+domain)
        self.identity=identities;self.db=identities.db;self.issuer=issuer;self.domain=domain
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS bootstrap_exchange(exchange TEXT PRIMARY KEY,raw BLOB NOT NULL,signature BLOB NOT NULL,
            state TEXT NOT NULL,account TEXT,mailbox TEXT,device TEXT);
          CREATE TABLE IF NOT EXISTS bootstrap_response(exchange TEXT NOT NULL,device TEXT NOT NULL,
            raw BLOB NOT NULL,signature BLOB NOT NULL,PRIMARY KEY(exchange,device));
          CREATE TABLE IF NOT EXISTS bootstrap_package(digest TEXT PRIMARY KEY,exchange TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS bootstrap_publication(account TEXT NOT NULL,device TEXT NOT NULL,publication TEXT NOT NULL,
            raw BLOB NOT NULL,signature BLOB NOT NULL,withdrawn INTEGER NOT NULL,
            PRIMARY KEY(account,device,publication));
          CREATE TABLE IF NOT EXISTS bootstrap_allocation(exchange TEXT NOT NULL,device TEXT NOT NULL,account TEXT NOT NULL,
            publication TEXT NOT NULL,PRIMARY KEY(exchange,device));
          CREATE TABLE IF NOT EXISTS bootstrap_block(account TEXT NOT NULL,issuer TEXT NOT NULL,source TEXT NOT NULL,principal TEXT NOT NULL,PRIMARY KEY(account,issuer,source,principal));
        ''')

    def _live(self,source,fetch,time):
        raw,v,sig=parse(source,'source')
        if v['targetService']!=self.issuer or selected_domain(v['targetMailbox'])!=self.domain:
            raise ValueError('Selected destination mismatch')
        live=fetch(selected_domain(v['senderMailbox']),v['issuer'],v['source'],source)
        if (not isinstance(live,SourceObservation) or not live.active or live.proof!=source or live.domain!=selected_domain(v['senderMailbox'])
                or live.issuer!=v['issuer'] or live.delegation!=v['delegation']):raise ValueError('Fresh source account inspection required')
        verify('source',raw,sig,v['sender']['key']);interval(v,time)
        advertisement(v['advertisement'],v['sender'],v['senderMailbox'],time)
        return raw,v,sig

    def post(self,source,*,fetch,time=(20,21),crash=None):
        raw,v,sig=self._live(source,fetch,time);exchange=handle(v)
        # Public admission never consults recipient existence or eligibility.
        with authority_snapshot(self.identity):
            old=self.db.execute('SELECT raw,signature FROM bootstrap_exchange WHERE exchange=?',(exchange,)).fetchone()
            if old and old!=(raw,sig):raise ValueError('Authenticated request conflict')
            if not old:
                self.db.execute('INSERT INTO bootstrap_exchange VALUES(?,?,?,?,?,?,?)',
                    (exchange,raw,sig,'pending',None,v['targetMailbox'],None))
            if crash:crash('before-request-commit')
        return dict(exchange=exchange,state='pending')

    def _blocked(self,account,source):
        return self.db.execute('SELECT 1 FROM bootstrap_block WHERE account=? AND ((issuer=? AND source=?) OR principal=?)',
                               (account,source['issuer'],source['accountSource'],source['sender']['principal'])).fetchone() is not None

    def block(self,slot,exchange):
        with authority_snapshot(self.identity):
            row=self.db.execute('SELECT raw,account FROM bootstrap_exchange WHERE exchange=?',(exchange,)).fetchone()
            if row is None or not isinstance(slot,RecipientSlot) or not slot.active or row[1]!=slot.account:
                raise ValueError('Own-account retained exchange required for block')
            source=decode_event(row[0])['value']
            self.db.execute('INSERT OR IGNORE INTO bootstrap_block VALUES(?,?,?,?)',
                            (slot.account,source['issuer'],source['accountSource'],source['sender']['principal']))

    def dispatch(self,exchange,*,fetch,lookup,time=(20,21)):
        """Private asynchronous worker; result never becomes public POST status."""
        with authority_snapshot(self.identity):
            row=self.db.execute('SELECT raw,signature,state,account FROM bootstrap_exchange WHERE exchange=?',(exchange,)).fetchone()
            if row is None or row[2]=='cancelled':return False
            source=dict(payload=base64.b64encode(row[0]).decode(),signature=row[1].hex())
            _,v,_=self._live(source,fetch,time)
            slot=lookup(v['targetMailbox'])
            if not isinstance(slot,RecipientSlot) or not(slot.active and slot.enabled and slot.device_enabled) or slot.mailbox!=v['targetMailbox']:return False
            if self._blocked(slot.account,v):return False
            if row[3] is not None and row[3]!=slot.account:raise ValueError('Recipient namespace changed')
            self.db.execute('UPDATE bootstrap_exchange SET account=?,device=? WHERE exchange=?',(slot.account,slot.device['device'],exchange))
            return True

    def _publication(self,proof,slot,time):
        raw,v,sig=parse(proof,'publication')
        if not isinstance(slot,RecipientSlot) or not(slot.active and slot.enabled and slot.device_enabled):
            raise ValueError('Own enabled publication account/device required')
        if (v['issuer']!=self.issuer or v['mailbox']!=slot.mailbox or selected_domain(slot.mailbox)!=self.domain or v['device']!=slot.device
                or v['relayDomain']!=slot.relay_domain):raise ValueError('Publication account/device/service/relay scope')
        verify('publication',raw,sig,slot.device['key']);interval(v,time)
        bound=current(self.identity,slot.device,'receive',time,'allow-unverified')
        ad,packages=advertisement(v['advertisement'],slot.device,slot.mailbox,time,package=True)
        if int(v['notBefore'])<max(bound['before'],int(ad['notBefore'])) or int(v['notAfter'])>min(bound['after'],int(ad['notAfter'])):
            raise ValueError('Publication authority interval')
        return raw,v,sig,packages

    def publish(self,proof,*,slot,time=(20,21),crash=None):
        with authority_snapshot(self.identity):
            raw,v,sig,_=self._publication(proof,slot,time)
            old=self.db.execute('SELECT raw,signature,withdrawn FROM bootstrap_publication WHERE account=? AND device=? AND publication=?',
                                (slot.account,slot.device['device'],v['publication'])).fetchone()
            if old:
                if old[:2]!=(raw,sig):raise ValueError('Authenticated publication conflict')
                return 'duplicate-withdrawn-publication' if old[2] else 'duplicate-publication'
            self.db.execute('INSERT INTO bootstrap_publication VALUES(?,?,?,?,?,0)',
                            (slot.account,slot.device['device'],v['publication'],raw,sig))
            if crash:crash('before-publication-commit')
            return 'stored-publication-candidate'

    def withdraw(self,publication,*,slot):
        hex_value(publication,32)
        if not isinstance(slot,RecipientSlot) or not slot.active:raise ValueError('Own active account required')
        with authority_snapshot(self.identity):
            self.db.execute('UPDATE bootstrap_publication SET withdrawn=1 WHERE account=? AND device=? AND publication=?',
                            (slot.account,slot.device['device'],publication))

    def _published(self,exchange,slot,time,crash):
        # Called only after source possession/liveness and recipient policy checks,
        # in the same write transaction as the eventual allocation commitment.
        allocated=self.db.execute('SELECT account,publication FROM bootstrap_allocation WHERE exchange=? AND device=?',
                                  (exchange,slot.device['device'])).fetchone()
        rows=self.db.execute('SELECT publication,raw,signature,withdrawn FROM bootstrap_publication WHERE account=? AND device=? ORDER BY publication',
                             (slot.account,slot.device['device'])).fetchall()
        if allocated:
            if allocated[0]!=slot.account:return []
            rows=[row for row in rows if row[0]==allocated[1]]
        for publication,raw,sig,withdrawn in rows:
            if withdrawn:continue
            proof=dict(payload=base64.b64encode(raw).decode(),signature=sig.hex())
            try:_,_,_,packages=self._publication(proof,slot,time)
            except ValueError:continue
            digests=[hashlib.sha256(package).hexdigest() for package in packages]
            if any((used:=self.db.execute('SELECT exchange FROM bootstrap_package WHERE digest=?',(digest,)).fetchone())
                   and used[0]!=exchange for digest in digests):continue
            if not allocated:
                for digest in digests:self.db.execute('INSERT OR IGNORE INTO bootstrap_package VALUES(?,?)',(digest,exchange))
                self.db.execute('INSERT INTO bootstrap_allocation VALUES(?,?,?,?)',
                                (exchange,slot.device['device'],slot.account,publication))
                if crash:crash('before-allocation-commit')
            return [proof]
        # An old allocation never switches to another pool entry on retry, even
        # after expiry/withdrawal. New material needs a fresh response or exchange.
        return []

    def _read(self,proof,kind,fetch,time):
        raw,p,sig=parse(proof,kind)
        row=self.db.execute('SELECT raw,signature,state,account,mailbox,device FROM bootstrap_exchange WHERE exchange=?',(p['exchange'],)).fetchone()
        if row is None or p['issuer']!=self.issuer or hashlib.sha256(row[0]).hexdigest()!=p['sourceDigest']:raise ValueError('Unknown scoped exchange')
        source=dict(payload=base64.b64encode(row[0]).decode(),signature=row[1].hex())
        _,v,_=self._live(source,fetch,time)
        verify(kind,raw,sig,v['sender']['key']);interval(p,time)
        if int(p['notBefore'])<int(v['notBefore']) or int(p['notAfter'])>int(v['notAfter']):raise ValueError('Inspection/cancel interval')
        return p,row,v

    def inspect(self,proof,*,fetch,lookup,time=(20,21),crash=None):
        with authority_snapshot(self.identity):
            p,row,source=self._read(proof,'inspect',fetch,time)
            slot=lookup(row[4])
            eligible=isinstance(slot,RecipientSlot) and slot.active and slot.enabled and slot.device_enabled and (slot.account,slot.mailbox,slot.device['device'])==row[3:] and not self._blocked(slot.account,source)
            rows=[] if row[2]=='cancelled' or not eligible else self.db.execute('SELECT raw,signature FROM bootstrap_response WHERE exchange=? ORDER BY device',(p['exchange'],)).fetchall()
            current_rows=[]
            for raw,sig in rows:
                result=decode_event(raw)['value']
                try:
                    if result['device']!=slot.device or result['relayDomain']!=slot.relay_domain:raise ValueError('Recipient changed')
                    interval(result,time);current(self.identity,slot.device,'receive',time,'allow-unverified')
                except ValueError:continue
                current_rows.append((raw,sig))
            rows=current_rows
            publications=self._published(p['exchange'],slot,time,crash) if not rows and eligible and row[2]!='cancelled' else []
            return dict(exchange=p['exchange'],sourceDigest=p['sourceDigest'],state='ready' if rows or publications else 'pending',
                        responses=[dict(payload=base64.b64encode(raw).decode(),signature=sig.hex()) for raw,sig in rows],publications=publications,routes=[])

    def respond(self,proof,*,slot,fetch,time=(20,21),crash=None):
        raw,r,sig=parse(proof,'response')
        with authority_snapshot(self.identity):
            row=self.db.execute('SELECT raw,signature,state,account,mailbox,device FROM bootstrap_exchange WHERE exchange=?',(r['exchange'],)).fetchone()
            if row is None or row[2]=='cancelled' or not isinstance(slot,RecipientSlot) or not(slot.active and slot.enabled and slot.device_enabled):raise ValueError('No eligible response slot')
            if (row[3:]!=(slot.account,slot.mailbox,slot.device['device']) or r['device']!=slot.device or r['mailbox']!=slot.mailbox
                    or r['issuer']!=self.issuer or r['relayDomain']!=slot.relay_domain or r['sourceDigest']!=hashlib.sha256(row[0]).hexdigest()):raise ValueError('Own linked device/mailbox and source scope required')
            source=dict(payload=base64.b64encode(row[0]).decode(),signature=row[1].hex())
            _,v,_=self._live(source,fetch,time)
            if self._blocked(slot.account,v):raise ValueError('Source account/peer blocked')
            if r['nonce']!=v['nonce'] or int(r['notBefore'])<int(v['notBefore']) or int(r['notAfter'])>int(v['notAfter']):raise ValueError('Exact source challenge')
            verify('response',raw,sig,slot.device['key']);interval(r,time)
            bound=current(self.identity,slot.device,'receive',time,'allow-unverified')
            ad,packages=advertisement(r['advertisement'],slot.device,slot.mailbox,time,package=True)
            if int(r['notBefore'])<max(bound['before'],int(ad['notBefore'])) or int(r['notAfter'])>min(bound['after'],int(ad['notAfter'])):raise ValueError('Response authority interval')
            old=self.db.execute('SELECT raw,signature FROM bootstrap_response WHERE exchange=? AND device=?',(r['exchange'],slot.device['device'])).fetchone()
            if old:
                if old!=(raw,sig):raise ValueError('Authenticated response conflict')
                return 'duplicate-response'
            for data in packages:
                digest=hashlib.sha256(data).hexdigest()
                used=self.db.execute('SELECT exchange FROM bootstrap_package WHERE digest=?',(digest,)).fetchone()
                if used and used[0]!=r['exchange']:raise ValueError('Disclosed package cannot be reallocated')
                self.db.execute('INSERT OR IGNORE INTO bootstrap_package VALUES(?,?)',(digest,r['exchange']))
            self.db.execute('INSERT INTO bootstrap_response VALUES(?,?,?,?)',(r['exchange'],slot.device['device'],raw,sig))
            if crash:crash('before-response-commit')
            return 'stored-response-candidate'

    def cancel(self,proof,*,fetch,time=(20,21)):
        with authority_snapshot(self.identity):
            p,_,_=self._read(proof,'cancel',fetch,time)
            self.db.execute("UPDATE bootstrap_exchange SET state='cancelled' WHERE exchange=?",(p['exchange'],))
