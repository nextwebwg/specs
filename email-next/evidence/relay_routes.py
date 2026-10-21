"""Configured relay grant and durable admission component.

AccountLink and SourceObservation are trusted service-adapter/journal inputs,
never accepted from mail JSON. No OAuth, discovery, provider HTTP, SMTP extraction,
source-permission issuance or production mailbox adapter is implemented. Identity
checks, route/replay state and local inbox intents share one SQLite transaction.
"""
import base64
from dataclasses import dataclass
import hashlib
import re
import struct

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from event_encoding import decode_event
from history_transfer import endpoint, authorize, authority_snapshot
from passive_discovery import uint64
from email2_mailbox import validate as validate_mailbox, selected_domain
from provider_control import decode as bounded_json

FIELDS = {
 'source-permission': 'version purpose preparation request nonce permission domain issuer delegation source incarnation sender recipient conversation routeKey targetService senderMode outerFrom notBefore notAfter maxCarrierBytes',
 'route-approval': 'version purpose preparation request nonce issuer delegation route alias recipient sender conversation sourceDomain sourceService sourcePermission sourceDigest routeKey notBefore notAfter maxCarrierBytes',
 'delivery': 'version purpose issuer route delivery alias outerFrom mailFrom messageId carrierSha256 carrierBytes notBefore notAfter',
}


def exact(value, fields):
    if not isinstance(value,dict) or set(value)!=set(fields.split()):
        raise ValueError('Exact relay object required')


def hex_value(value, n=64):
    if not isinstance(value,str) or not re.fullmatch(r'[0-9a-f]{%d}'%n,value) or int(value,16)==0:
        raise ValueError('Nonzero relay identifier/key required')


def origin(value):
    # Narrow fixture origin subset, no arbitrary URL/network adapter or A-label claim.
    if not isinstance(value,str) or not re.fullmatch(r'https://[a-z0-9]+(?:[.-][a-z0-9]+)*',value):
        raise ValueError('Configured HTTPS origin required')


def mailbox(value):
    validate_mailbox(value)


def frame(kind, raw):
    if kind not in FIELDS:
        raise ValueError('Relay signature kind')
    return ('email2/relay/'+kind+'/v0').encode()+b'\0'+struct.pack('>I',len(raw))+raw


def proof(kind, raw, key):
    result=dict(payload=base64.b64encode(raw).decode(),signature=key.sign(frame(kind,raw)).hex())
    parse(result,kind)
    return result


def parse(value, kind):
    exact(value,'payload signature')
    if not isinstance(value['payload'],str) or len(value['payload'])>349528:
        raise ValueError('Relay wrapper bound')
    try:raw=base64.b64decode(value['payload'],validate=True)
    except (ValueError,TypeError) as error:raise ValueError('Relay base64') from error
    if base64.b64encode(raw).decode()!=value['payload']:
        raise ValueError('Canonical relay base64')
    hex_value(value['signature'],128)
    limit=8192 if kind=='delivery' else 262144
    bounded_json(raw,max_bytes=limit,max_depth=16 if kind=='delivery' else 32)
    v=decode_event(raw,max_octets=limit)['value'];exact(v,FIELDS[kind])
    if v['version']!='0' or v['purpose']!='relay-'+kind:
        raise ValueError('Relay version/purpose')
    if uint64(v['notBefore'])>uint64(v['notAfter']):
        raise ValueError('Relay interval')
    origin(v['issuer'])
    if kind!='delivery':
        for k in ['preparation','request','conversation']:hex_value(v[k],32)
        for k in ['nonce','delegation','routeKey']:hex_value(v[k])
        if uint64(v['maxCarrierBytes'])==0:raise ValueError('Positive carrier limit')
        endpoint(v['sender'])
    if kind=='source-permission':
        for k in ['permission','source','incarnation']:hex_value(v[k])
        mailbox('r@'+v['domain'])
        if not isinstance(v['recipient'],str) or not re.fullmatch('enp0:[0-9a-f]{64}',v['recipient']) or int(v['recipient'][5:],16)==0:
            raise ValueError('Recipient principal')
        if v['targetService']!='':origin(v['targetService'])
        if v['senderMode'] not in ['shared-relay','personal-source'] or (v['targetService']=='' and v['senderMode']!='shared-relay'):
            raise ValueError('Source mode/destination')
        mailbox(v['outerFrom'])
    elif kind=='route-approval':
        for k in ['route','sourcePermission','sourceDigest']:hex_value(v[k])
        endpoint(v['recipient']);mailbox('r@'+v['sourceDomain']);origin(v['sourceService']);mailbox(v['alias'])
    else:
        hex_value(v['route']);hex_value(v['delivery'],32);hex_value(v['carrierSha256'])
        for k in ['alias','outerFrom','mailFrom']:mailbox(v[k])
        if uint64(v['carrierBytes'])==0:raise ValueError('Positive carrier bytes')
        if not isinstance(v['messageId'],str) or not re.fullmatch(r'<[A-Za-z0-9.-]+@[a-z0-9]+(?:[.-][a-z0-9]+)*>',v['messageId']):
            raise ValueError('Configured opaque Message-ID required')
    return raw,v,bytes.fromhex(value['signature'])


def verify(kind, raw, signature, key):
    hex_value(key)
    try:Ed25519PublicKey.from_public_bytes(bytes.fromhex(key)).verify(signature,frame(kind,raw))
    except InvalidSignature as error:raise ValueError('Relay proof signature') from error


def interval(v, time):
    low,high=map(int,time)
    if not int(v['notBefore'])<=low<=high<=int(v['notAfter']):
        raise ValueError('Relay authority expired/not current')


def current(store, ref, role, time, policy):
    checked=authorize(store,ref,role,dict(earliest=str(time[0]),latest=str(time[1])),policy)
    if checked['head']!=ref['state']:
        raise ValueError('Exact relay identity head changed')
    return checked


@dataclass(frozen=True)
class AccountLink:
    account: str
    incarnation: str
    link: str
    family: str
    recipient: dict
    not_before: int=10
    not_after: int=100
    active: bool=True


@dataclass(frozen=True)
class SourceObservation:
    origin: str
    permission: dict
    domain: str
    delegation: str
    roles: tuple=('accountability','sender-mask')
    active: bool=True


class RelayRoutes:
    def __init__(self, identity, issuer, *, alias_domain, delegation):
        origin(issuer)
        mailbox('r@'+alias_domain);hex_value(delegation)
        self.identity=identity;self.db=identity.db;self.issuer=issuer
        self.alias_domain=alias_domain;self.delegation=delegation
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS relay_route(route TEXT PRIMARY KEY,alias TEXT UNIQUE NOT NULL,
            account TEXT NOT NULL,incarnation TEXT NOT NULL,link TEXT NOT NULL,family TEXT NOT NULL,
            source_service TEXT NOT NULL,source_handle TEXT NOT NULL,raw BLOB NOT NULL,signature BLOB NOT NULL,
            active INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS relay_delivery(route TEXT NOT NULL,delivery TEXT NOT NULL,
            raw BLOB NOT NULL,signature BLOB NOT NULL,carrier BLOB NOT NULL,PRIMARY KEY(route,delivery));
          CREATE TABLE IF NOT EXISTS relay_inbox_intent(route TEXT NOT NULL,delivery TEXT NOT NULL,
            account TEXT NOT NULL,carrier BLOB NOT NULL,PRIMARY KEY(route,delivery));
          CREATE TABLE IF NOT EXISTS relay_peer_block(account TEXT NOT NULL,principal TEXT NOT NULL,PRIMARY KEY(account,principal));
          CREATE TABLE IF NOT EXISTS relay_block(account TEXT NOT NULL,service TEXT NOT NULL,
            source_handle TEXT NOT NULL,PRIMARY KEY(account,service,source_handle));
        ''')

    def _link(self, link, grant, time, row=None):
        if not isinstance(link,AccountLink) or not link.active or not link.not_before<=time[0]<=time[1]<=link.not_after or link.recipient!=grant['recipient'] or int(grant['notBefore'])<link.not_before or int(grant['notAfter'])>link.not_after:
            raise ValueError('Current account/link required')
        if row and tuple(row[:4])!=(link.account,link.incarnation,link.link,link.family):
            raise ValueError('Account incarnation/family mismatch')

    def _source(self, grant, fetch, time, policy):
        # Adapter must perform a fresh, selected-origin TLS fetch, not decode facts
        # from a received record. Call occurs for every new use, not exact dedup.
        observation=fetch(grant['sourceDomain'],grant['sourceService'],grant['sourcePermission'])
        if not isinstance(observation,SourceObservation) or not observation.active or observation.origin!=grant['sourceService']:
            raise ValueError('Fresh active source observation required')
        raw,v,sig=parse(observation.permission,'source-permission')
        if (v['issuer']!=observation.origin or v['domain']!=observation.domain or grant['sourceDomain']!=observation.domain or v['delegation']!=observation.delegation or 'accountability' not in observation.roles
                or hashlib.sha256(raw).hexdigest()!=grant['sourceDigest']
                or v['permission']!=grant['sourcePermission'] or v['targetService']!=grant['issuer']
                or v['sender']!=grant['sender'] or v['recipient']!=grant['recipient']['principal']
                or v['conversation']!=grant['conversation'] or v['routeKey']!=grant['routeKey']
                or int(grant['notBefore'])<int(v['notBefore']) or int(grant['notAfter'])>int(v['notAfter'])
                or int(grant['maxCarrierBytes'])>int(v['maxCarrierBytes'])):
            raise ValueError('Exact source/route binding')
        mailbox('r@'+observation.domain)
        if v['senderMode']=='shared-relay' and ('sender-mask' not in observation.roles or selected_domain(v['outerFrom'])!=observation.domain):
            raise ValueError('Source relay domain/role mismatch')
        verify('source-permission',raw,sig,v['sender']['key'])
        interval(v,time)
        for role in ['send','receive']:
            bound=authorize(self.identity,v['sender'],role,dict(earliest=str(time[0]),latest=str(time[1])),policy)
            if int(v['notBefore'])<bound['before'] or int(v['notAfter'])>bound['after']:
                raise ValueError('Source interval exceeds device authority')
        return v,observation.domain

    def activate(self, approval, *, retained_preparation, link, fetch, time=(20,21), policy='allow-unverified'):
        raw,g,sig=parse(approval,'route-approval')
        if (raw!=retained_preparation or g['issuer']!=self.issuer or g['delegation']!=self.delegation
                or not re.fullmatch('r-[0-9a-f]{32}@'+re.escape(self.alias_domain),g['alias'])
                or int(g['alias'].split('@')[0][2:],16)==0):
            raise ValueError('Retained destination preparation required')
        with authority_snapshot(self.identity):
            self._link(link,g,time);interval(g,time)
            verify('route-approval',raw,sig,g['recipient']['key'])
            bound=authorize(self.identity,g['recipient'],'receive',dict(earliest=str(time[0]),latest=str(time[1])),policy)
            if int(g['notBefore'])<bound['before'] or int(g['notAfter'])>bound['after']:
                raise ValueError('Recipient interval exceeds device authority')
            source,_=self._source(g,fetch,time,policy)
            if (self.db.execute('SELECT 1 FROM relay_block WHERE account=? AND service=? AND source_handle=?',
                                (link.account,g['sourceService'],source['source'])).fetchone()
                    or self.db.execute('SELECT 1 FROM relay_peer_block WHERE account=? AND principal=?',
                                       (link.account,g['sender']['principal'])).fetchone()):
                raise ValueError('Source account/peer blocked')
            old=self.db.execute('SELECT raw,signature,active,account,incarnation,link,family FROM relay_route WHERE route=?',(g['route'],)).fetchone()
            if old:
                if old[:2]!=(raw,sig) or old[3:]!=(link.account,link.incarnation,link.link,link.family) or not old[2]:
                    raise ValueError('Route conflict/withdrawn')
                return 'duplicate-active-route'
            try:self.db.execute('INSERT INTO relay_route VALUES(?,?,?,?,?,?,?,?,?,?,1)',
                                (g['route'],g['alias'],link.account,link.incarnation,link.link,link.family,g['sourceService'],source['source'],raw,sig))
            except Exception as error:
                import sqlite3
                if isinstance(error,sqlite3.IntegrityError):raise ValueError('Alias never reassigned') from error
                raise
            return 'route-activated'

    def admit(self, delivery, carrier, *, observed, link, fetch, time=(20,21), policy='allow-unverified', crash=None):
        raw,d,sig=parse(delivery,'delivery')
        if not isinstance(carrier,bytes) or len(carrier)!=int(d['carrierBytes']) or hashlib.sha256(carrier).hexdigest()!=d['carrierSha256']:
            raise ValueError('Exact opaque carrier required')
        exact(observed,'alias outerFrom mailFrom messageId')
        if any(observed[k]!=d[k] for k in observed) or d['issuer']!=self.issuer:
            raise ValueError('Actual envelope/header mismatch')
        with authority_snapshot(self.identity):
            row=self.db.execute('SELECT account,incarnation,link,family,raw,active FROM relay_route WHERE route=?',(d['route'],)).fetchone()
            if row is None:raise ValueError('Unknown route')
            grant=decode_event(row[4])['value']
            if d['alias']!=grant['alias']:raise ValueError('Route alias mismatch')
            verify('delivery',raw,sig,grant['routeKey'])
            old=self.db.execute('SELECT raw,signature,carrier FROM relay_delivery WHERE route=? AND delivery=?',(d['route'],d['delivery'])).fetchone()
            if old:
                if old!=(raw,sig,carrier):raise ValueError('Authenticated delivery conflict')
                return 'duplicate-previously-accepted'
            self._link(link,grant,time,row[:4])
            if not row[5]:raise ValueError('Route withdrawn')
            interval(grant,time);interval(d,time)
            if int(d['notBefore'])<int(grant['notBefore']) or int(d['notAfter'])>int(grant['notAfter']) or len(carrier)>int(grant['maxCarrierBytes']):
                raise ValueError('Delivery scope/bound')
            authorize(self.identity,grant['recipient'],'receive',dict(earliest=str(time[0]),latest=str(time[1])),policy)
            source,source_domain=self._source(grant,fetch,time,policy)
            if source['senderMode']=='shared-relay' and (d['mailFrom']!='b-'+d['delivery']+'@'+source_domain or d['messageId']!='<m-'+d['delivery']+'@'+source_domain+'>'):
                raise ValueError('Source opaque bounce/Message-ID mismatch')
            if d['outerFrom']!=source['outerFrom']:
                raise ValueError('Source From mismatch')
            if (self.db.execute('SELECT 1 FROM relay_block WHERE account=? AND service=? AND source_handle=?',
                                (link.account,grant['sourceService'],source['source'])).fetchone()
                    or self.db.execute('SELECT 1 FROM relay_peer_block WHERE account=? AND principal=?',
                                       (link.account,grant['sender']['principal'])).fetchone()):
                raise ValueError('Source account/peer blocked')
            self.db.execute('INSERT INTO relay_delivery VALUES(?,?,?,?,?)',(d['route'],d['delivery'],raw,sig,carrier))
            self.db.execute('INSERT INTO relay_inbox_intent VALUES(?,?,?,?)',(d['route'],d['delivery'],link.account,carrier))
            if crash:crash('before-accept-commit')
            return 'accepted-local-inbox-intent'

    def revoke(self, account, route):
        with authority_snapshot(self.identity):
            self.db.execute('UPDATE relay_route SET active=0 WHERE account=? AND route=?',(account,route))

    def block(self, account, service, source):
        with authority_snapshot(self.identity):
            if not self.db.execute('SELECT 1 FROM relay_route WHERE account=? AND source_service=? AND source_handle=?',(account,service,source)).fetchone():
                raise ValueError('Account-owned source evidence required')
            rows=self.db.execute('SELECT raw FROM relay_route WHERE account=? AND source_service=? AND source_handle=?',(account,service,source)).fetchall()
            for row in rows:
                principal=decode_event(row[0])['value']['sender']['principal']
                self.db.execute('INSERT OR IGNORE INTO relay_peer_block VALUES(?,?)',(account,principal))
            self.db.execute('INSERT OR IGNORE INTO relay_block VALUES(?,?,?)',(account,service,source))
            self.db.execute('UPDATE relay_route SET active=0 WHERE account=? AND source_service=? AND source_handle=?',(account,service,source))
