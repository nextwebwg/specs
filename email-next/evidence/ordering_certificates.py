"""Private signed-certificate experiment; no MLS or authority-discovery claim."""
import hashlib
import json
import re
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from event_encoding import decode_event

HEX=re.compile(r'[0-9a-f]{64}\Z')
KINDS={'proposal':{'candidate','newView'},'prepare':{'proposal'},
       'prepared':{'proposal','prepares'},'commit':{'prepared'},
       'decision':{'prepared','commits'},'report':{'prepared'},'new-view':{'reports'}}

def encode(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(v):return hashlib.sha256(encode(v)).hexdigest()
def domain(kind):return ('email-next/ordering-experiment/'+kind+'/v0\0').encode('ascii')
def material(body):
    raw=encode(body)
    return domain(body['kind'])+len(raw).to_bytes(4,'big')+raw

def sign(body,key):
    if body['kind'] not in KINDS:raise ValueError('purpose')
    return {'body':body,'signature':key.sign(material(body)).hex()}

def unsigned(kind,scope,view,signer,**fields):
    return dict(version='0',kind=kind,scope=scope,view=str(view),signer=signer,**fields)

class ProofLimit(ValueError):
    """Unsupported local resource size; no partial acceptance or maliciousness claim."""

class Proof:
    """Exact bounded DAG. Public keys/scope supplied by accepted predecessor policy.

    Limits are adjustable local experiment resources; overflow rejects the whole
    input, not part of its quorum. They allocate no new wire-level quotas.
    """
    def __init__(self,raw,*,scope,keys,f,max_bytes=1048576,max_nodes=4096,max_depth=64):
        value=decode_event(raw,max_octets=max_bytes)["value"]
        if encode(value)!=raw or not isinstance(value,dict) or set(value)!={'root','objects'}:raise ValueError('exact envelope')
        if not isinstance(value['objects'],list) or not 0<len(value['objects'])<=max_nodes:raise ProofLimit('unsupported-size: node limit')
        if type(f) is not int or f<0 or len(keys)<3*f+1:raise ValueError('fault policy')
        self.keys=keys;self.scope=scope;self.q=(len(keys)+f)//2+1;self.order=sorted(keys)
        self.nodes={};self.cache={};self.active=set();self.max_depth=max_depth
        for obj in value['objects']:
            if not isinstance(obj,dict) or set(obj)!={'body','signature'}:raise ValueError('object shape')
            h=digest(obj)
            if h in self.nodes:raise ValueError('duplicate object')
            self.nodes[h]=obj
        self.root=value['root']
        self.result=self.verify(self.root)
        # Even unrelated bundled objects must validate; no hidden partial acceptance.
        for h in self.nodes:self.verify(h)
    def verify(self,h,depth=0):
        if depth>self.max_depth:raise ProofLimit('unsupported-size: proof depth')
        if not isinstance(h,str) or not HEX.fullmatch(h) or h not in self.nodes:raise ValueError('missing reference')
        if h in self.cache:return self.cache[h]
        if h in self.active:raise ValueError('cycle')
        self.active.add(h)
        obj=self.nodes[h];b=obj['body']
        if not isinstance(b,dict) or not isinstance(b.get('kind'),str) or b.get('kind') not in KINDS:raise ValueError('kind')
        kind=b['kind']
        if set(b)!={'version','kind','scope','view','signer'}|KINDS[kind]:raise ValueError('fields')
        if b['version']!='0' or b['scope']!=self.scope or not isinstance(b['signer'],str) or b['signer'] not in self.keys:raise ValueError('scope/signer')
        if not isinstance(b['view'],str) or not re.fullmatch(r'0|[1-9][0-9]{0,19}',b['view']) or int(b['view'])>=2**64:raise ValueError('view')
        v=int(b['view'])
        if not isinstance(obj['signature'],str) or not re.fullmatch(r'[0-9a-f]{128}',obj['signature']):raise ValueError('signature')
        try:Ed25519PublicKey.from_public_bytes(bytes.fromhex(self.keys[b['signer']])).verify(bytes.fromhex(obj['signature']),material(b))
        except Exception as e:raise ValueError('invalid signature') from e
        def ref(name,expected):
            result=self.verify(b[name],depth+1)
            if result['kind']!=expected:raise ValueError('reference purpose')
            return result
        def quorum(name,expected):
            refs=b[name]
            if not isinstance(refs,list) or len(refs)!=self.q or any(not isinstance(x,str) for x in refs) or refs!=sorted(set(refs)):raise ValueError('quorum list')
            rs=[self.verify(x,depth+1) for x in refs]
            if len({x['signer'] for x in rs})!=self.q or any(x['kind']!=expected or x['view']!=v for x in rs):raise ValueError('quorum identity/view')
            return rs
        result=dict(kind=kind,view=v,signer=b['signer'],candidate='',highest=-1)
        if kind=='proposal':
            if b['signer']!=self.order[v%len(self.order)] or not isinstance(b['candidate'],str) or not HEX.fullmatch(b['candidate']):raise ValueError('proposal')
            if v==0:
                if b['newView']!='':raise ValueError('initial justification')
            else:
                nv=ref('newView','new-view')
                if nv['view']!=v or (nv['candidate'] and nv['candidate']!=b['candidate']):raise ValueError('new-view choice')
                result['highest']=nv['highest']
            result['candidate']=b['candidate']
        elif kind in ('prepare','prepared'):
            p=ref('proposal','proposal')
            if p['view']!=v:raise ValueError('proposal view')
            if kind=='prepared':
                qs=quorum('prepares','prepare')
                if any(x['proposal']!=b['proposal'] for x in qs):raise ValueError('prepare binding')
            result.update(candidate=p['candidate'],proposal=b['proposal'],highest=p['highest'])
        elif kind in ('commit','decision'):
            p=ref('prepared','prepared')
            if p['view']!=v:raise ValueError('prepared view')
            if kind=='decision':
                qs=quorum('commits','commit')
                if any(x['candidate']!=p['candidate'] for x in qs):raise ValueError('commit binding')
            result['candidate']=p['candidate']
        elif kind=='report':
            if v==0:raise ValueError('report view')
            if b['prepared']!='':
                p=ref('prepared','prepared')
                if p['view']>=v:raise ValueError('nondecreasing view')
                result.update(candidate=p['candidate'],highest=p['view'])
        elif kind=='new-view':
            if v==0 or b['signer']!=self.order[v%len(self.order)]:raise ValueError('coordinator')
            qs=quorum('reports','report');highest=max(x['highest'] for x in qs)
            values={x['candidate'] for x in qs if x['highest']==highest}
            if len(values)!=1:raise ValueError('conflicting prepared certificates')
            result.update(candidate=next(iter(values)),highest=highest)
        self.active.remove(h);self.cache[h]=result
        return result

def bundle(root,objects):
    return encode({'root':root,'objects':sorted(objects,key=digest)})
