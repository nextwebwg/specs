"""Local freshness gate, not full send/admission authorization or trusted time.

Uses accepted IdentityStore state and actual assertion8/bootstrap signatures.
Local policy/account/clock inputs are trusted adapter facts. Network account
permission, complete MLS packages, association/verification and release checks
remain owning validators. The returned result is a transaction snapshot only.
"""
import base64
from dataclasses import dataclass
import hashlib
import json

from event_encoding import encode_event,decode_event
from identity_bundle import decode_identity_bundle
from history_transfer import authority_snapshot
from relay_routes import current,hex_value
from bootstrap_exchange import parse,verify,interval,advertisement,handle
from passive_discovery import uint64


@dataclass(frozen=True)
class Policy:
    revision:str
    mode:str='cached-continuity'
    maximum_age:int|None=None
    maximum_uncertainty:int|None=None

    def check(self):
        hex_value(self.revision,32)
        if self.mode not in ['cached-continuity','recent-checkpoint','live-confirmation']:raise ValueError('Freshness mode')
        if self.mode=='cached-continuity':
            if self.maximum_age is not None:raise ValueError('Cached mode has no implicit age window')
        elif type(self.maximum_age) is not int or not 0<self.maximum_age<2**64:raise ValueError('Explicit positive maximum age required')
        if self.maximum_uncertainty is not None and (type(self.maximum_uncertainty) is not int or not 0<=self.maximum_uncertainty<2**64):
            raise ValueError('Explicit clock uncertainty bound')


def clock_interval(clock,policy):
    policy.check()
    if not isinstance(clock,tuple) or len(clock)!=2 or any(type(t) is not int or not 0<=t<2**64 for t in clock) or clock[0]>clock[1]:
        raise ValueError('Credible complete clock interval required')
    if policy.maximum_uncertainty is not None and clock[1]-clock[0]>policy.maximum_uncertainty:
        raise ValueError('Clock uncertainty exceeds local policy')


def policy_bytes(policy):
    policy.check()
    # Local journal encoding, not an incoming record or interoperability format.
    return json.dumps(policy.__dict__,sort_keys=True,separators=(',',':')).encode()


def _wrapper(raw,sig):
    return dict(payload=base64.b64encode(raw).decode(),signature=sig.hex())


class FreshnessGate:
    def __init__(self,identities,*,account,own_principal,own_device):
        if type(account) is not str or not account:raise ValueError('Trusted local account namespace required')
        self.ids=identities;self.db=identities.db;self.account=account
        self.own_principal=own_principal;self.own_device=own_device
        self.db.execute('''CREATE TABLE IF NOT EXISTS freshness_attempt(account TEXT NOT NULL,operation TEXT NOT NULL,
          policy BLOB NOT NULL,source BLOB NOT NULL,signature BLOB NOT NULL,earliest TEXT NOT NULL,latest TEXT NOT NULL,
          cancelled INTEGER NOT NULL,PRIMARY KEY(account,operation))''')

    def _own(self,source,clock):
        if (source['sender']['principal'],source['sender']['device'])!=(self.own_principal,self.own_device):
            raise ValueError('Selected own account/device required')
        for role in ['send','receive']:
            bound=current(self.ids,source['sender'],role,clock,'allow-unverified')
            if int(source['notBefore'])<bound['before'] or int(source['notAfter'])>bound['after']:
                raise ValueError('Source binding lifetime')
        ad,_=advertisement(source['advertisement'],source['sender'],source['senderMailbox'],clock)
        if int(source['notBefore'])<int(ad['notBefore']) or int(source['notAfter'])>int(ad['notAfter']):
            raise ValueError('Source advertisement lifetime')

    def prepare_bootstrap(self,operation,policy,source,*,clock):
        hex_value(operation,32);clock_interval(clock,policy)
        if policy.mode!='live-confirmation':raise ValueError('Live attempt requires selected live policy')
        raw,v,sig=parse(source,'source');verify('source',raw,sig,v['sender']['key']);interval(v,clock)
        with authority_snapshot(self.ids):
            self._own(v,clock)
            old=self.db.execute('SELECT policy,source,signature,earliest,latest FROM freshness_attempt WHERE account=? AND operation=?',
                                (self.account,operation)).fetchone()
            if old:
                if old[:3]!=(policy_bytes(policy),raw,sig):raise ValueError('Immutable local attempt conflict')
                # Retry never advances the clock anchor or clears cancellation.
                return 'retained-attempt'
            self.db.execute('INSERT INTO freshness_attempt VALUES(?,?,?,?,?,?,?,0)',
                            (self.account,operation,policy_bytes(policy),raw,sig,str(clock[0]),str(clock[1])))
        return 'stored-attempt'

    def cancel(self,operation):
        hex_value(operation,32)
        with authority_snapshot(self.ids):
            self.db.execute('UPDATE freshness_attempt SET cancelled=1 WHERE account=? AND operation=?',(self.account,operation))

    def _checkpoint(self,actor,clock,policy):
        row=self.db.execute('SELECT bundle FROM identity_transitions WHERE principal=? AND digest=? AND accepted=1',
                            (actor['principal'],actor['state'])).fetchone()
        if row:
            records=decode_identity_bundle(row[0])['states']
            state=next(s['value'] for s in records if s['digest']==actor['state'])
        else:
            row=self.db.execute('SELECT record FROM claims WHERE principal=? AND digest=?',(actor['principal'],actor['state'])).fetchone()
            if not row:raise ValueError('Accepted checkpoint bytes required')
            state=decode_event(base64.b64decode(json.loads(row[0])['state'],validate=True))['value']
        issued=uint64(state['issuedAt'])
        if issued>clock[0] or clock[1]-issued>policy.maximum_age:raise ValueError('Checkpoint outside explicit age window')
        return actor['state']

    def evaluate(self,policy,actor,mailbox,encoded_advertisement,*,clock,operation=None,response=None):
        clock_interval(clock,policy)
        with authority_snapshot(self.ids):
            bound=current(self.ids,actor,'receive',clock,'allow-unverified')
            ad,_=advertisement(encoded_advertisement,actor,mailbox,clock)
            evidence=''
            if policy.mode=='recent-checkpoint':evidence=self._checkpoint(actor,clock,policy)
            elif policy.mode=='live-confirmation':
                hex_value(operation,32)
                row=self.db.execute('SELECT policy,source,signature,earliest,latest,cancelled FROM freshness_attempt WHERE account=? AND operation=?',
                                    (self.account,operation)).fetchone()
                if row is None or row[0]!=policy_bytes(policy) or row[5]:raise ValueError('Current outstanding local attempt required')
                if clock[0]<int(row[3]) or clock[1]<int(row[4]):raise ValueError('Clock moved backward since attempt')
                if clock[1]-int(row[3])>policy.maximum_age:raise ValueError('Live attempt outside explicit age window')
                source=_wrapper(row[1],row[2]);_,s,_=parse(source,'source')
                self._own(s,clock);interval(s,clock)
                raw,r,sig=parse(response,'response');verify('response',raw,sig,actor['key']);interval(r,clock)
                if (r['issuer']!=s['targetService'] or r['exchange']!=handle(s)
                        or r['sourceDigest']!=hashlib.sha256(row[1]).hexdigest() or r['nonce']!=s['nonce']
                        or r['device']!=actor or r['mailbox']!=s['targetMailbox']
                        or r['advertisement']!=encoded_advertisement or ad['mailbox']!=s['targetMailbox']):
                    raise ValueError('Exact locally outstanding challenge/target evidence required')
                if (int(r['notBefore'])<int(s['notBefore']) or int(r['notAfter'])>min(int(s['notAfter']),int(ad['notAfter']),bound['after'])
                        or int(r['notBefore'])<max(int(ad['notBefore']),bound['before'])):
                    raise ValueError('Live evidence authority interval')
                evidence=hashlib.sha256(raw).hexdigest()
            return dict(status='freshness-satisfied-only',mode=policy.mode,head=actor['state'],binding=actor['binding'],evidence=evidence)
