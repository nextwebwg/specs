"""Post-verification DER profile check, not a path/signature validator.

Bounds apply after the TLS backend allocated its chain. Unknown algorithms stay
under backend policy. Returned trust anchors receive encoding checks only; their
self-signatures are not the source of trust.
"""
# RFC5758 ECDSA SHA2 and DSA SHA224/256; RFC8410 Ed25519/448.
ABSENT = {bytes.fromhex(x) for x in (
 '2a8648ce3d040301','2a8648ce3d040302','2a8648ce3d040303','2a8648ce3d040304',
 '608648016503040301','608648016503040302','2b6570','2b6571')}

def item(raw,offset,end):
 start=offset
 if offset+2>end:raise ValueError('Certificate DER structure')
 tag=raw[offset];offset+=1;n=raw[offset];offset+=1
 if n&128:
  count=n&127
  if count==0 or count>4 or offset+count>end or raw[offset]==0:raise ValueError('Certificate DER length')
  n=int.from_bytes(raw[offset:offset+count],'big');offset+=count
  if n<128:raise ValueError('Certificate DER nonminimal length')
 stop=offset+n
 if stop>end:raise ValueError('Certificate DER truncated')
 return tag,offset,stop,start

def members(raw,start,end):
 while start<end:
  tag,body,stop,begin=item(raw,start,end);yield tag,body,stop,begin;start=stop

def check_identifier(raw,field):
 tag,start,end,_=field
 if tag!=0x30:raise ValueError('Certificate algorithm structure')
 values=list(members(raw,start,end))
 if not values or values[0][0]!=6 or len(values)>2:raise ValueError('Certificate algorithm structure')
 _,a,b,_=values[0]
 if raw[a:b] in ABSENT and len(values)!=1:raise ValueError('Certificate signature parameters must be absent')

def check_der(raw):
 tag,start,end,_=item(raw,0,len(raw))
 if tag!=0x30 or end!=len(raw):raise ValueError('Certificate DER root')
 fields=list(members(raw,start,end))
 if len(fields)!=3 or fields[0][0]!=0x30 or fields[2][0]!=3:raise ValueError('Certificate structure')
 check_identifier(raw,fields[1])
 tbs=list(members(raw,fields[0][1],fields[0][2]))
 index=2 if tbs and tbs[0][0]==0xa0 else 1
 if len(tbs)<=index:raise ValueError('Certificate TBS structure')
 check_identifier(raw,tbs[index])

def check_verified_chain(sock,*,max_chain_certificates=32,max_certificate_bytes=1024*1024):
 for value in (max_chain_certificates,max_certificate_bytes):
  if type(value)is not int or value<=0:raise ValueError('Certificate check budget')
 getter=getattr(sock,'get_verified_chain',None)
 if not callable(getter):raise RuntimeError('Authenticated certificate chain unavailable')
 chain=getter()
 if not isinstance(chain,list) or not chain or len(chain)>max_chain_certificates:raise ValueError('Authenticated certificate chain shape')
 for der in chain:
  if not isinstance(der,bytes) or not der or len(der)>max_certificate_bytes:raise ValueError('Certificate DER budget/shape')
  check_der(der)
