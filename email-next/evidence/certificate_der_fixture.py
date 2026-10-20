"""Small DER fixture transformer, never a production certificate parser."""
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec,padding

def tlv(tag,body):
 n=len(body);size=n.to_bytes((n.bit_length()+7)//8 or 1,'big')
 return bytes([tag])+(bytes([n]) if n<128 else bytes([128+len(size)])+size)+body

def children(raw):
 if raw[0]!=0x30:raise ValueError('fixture sequence')
 def take(data,offset):
  start=offset;offset+=1;n=data[offset];offset+=1
  if n&128:k=n&127;n=int.from_bytes(data[offset:offset+k],'big');offset+=k
  return data[start:offset+n],offset+n,offset
 _,end,body=take(raw,0)
 if end!=len(raw):raise ValueError('fixture trailing data')
 result=[]
 while body<end:item,body,_=take(raw,body);result.append(item)
 return result

def seq(items):return tlv(0x30,b''.join(items))

def pem(der):
 text=base64.b64encode(der).decode();return ('-----BEGIN CERTIFICATE-----\n'+'\n'.join(text[i:i+64] for i in range(0,len(text),64))+'\n-----END CERTIFICATE-----\n').encode()

def mutate_signed(cert,issuer,kind,mutation):
 outer=children(cert);tbs=children(outer[0])
 # Explicit version is present in these v3 fixtures; signature index2, SPKI6.
 if mutation=='signature-null':
  algorithm=seq(children(outer[1])+[b'\x05\x00']);outer[1]=algorithm;tbs[2]=algorithm
 elif mutation=='pss-salt-mismatch':
  alg=children(outer[1]);params=children(alg[1]);params=[tlv(0xa2,tlv(2,b'\x01')) if item[0]==0xa2 else item for item in params];algorithm=seq([alg[0],seq(params)]);outer[1]=algorithm;tbs[2]=algorithm
 elif mutation in ('ec-null','ec-absent','point-hybrid'):
  spki=children(tbs[6]);alg=children(spki[0])
  if mutation=='ec-null':spki[0]=seq([alg[0],b'\x05\x00'])
  elif mutation=='ec-absent':spki[0]=seq([alg[0]])
  else:
   # P256 bitstring has one-byte length: unused-bit byte then point prefix.
   point=bytearray(spki[1]);point[3]=6;spki[1]=bytes(point)
  tbs[6]=seq(spki)
 else:raise ValueError('fixture mutation')
 outer[0]=seq(tbs)
 signature=issuer.sign(outer[0],padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=32),hashes.SHA256()) if kind=='rsa' else issuer.sign(outer[0],ec.ECDSA(hashes.SHA256())) if kind=='ec' else issuer.sign(outer[0])
 outer[2]=tlv(3,b'\0'+signature)
 return seq(outer)
