"""V1 manifest/chunk assembly from trusted decrypted-part inputs only.

No signature, age, identity, selection, full configuration schema, transaction or
live trust installation. Result is bytes-only, never staged/installed/send-ready.
"""
import hashlib
import struct
from event_encoding import decode_event
from provider_discovery import uint
from service_authorization import hexvalue

CHUNK=65536
MAGIC=b'EML2CFG1'


def manifest(raw, *, max_bytes, max_parts):
    return manifest_version(raw,max_bytes=max_bytes,max_parts=max_parts,version='1')


def manifest_version(raw, *, max_bytes, max_parts,version):
    if version not in ('1','2'):raise ValueError('Explicit supported configuration version')
    if type(max_bytes) is not int or max_bytes<=0 or type(max_parts) is not int or max_parts<=0:
        raise ValueError('Positive finite caller budgets')
    value=decode_event(raw,max_octets=1048576)['value']
    if set(value)!=set('version purpose bytes sha256 parts'.split()) or value['version']!=version or value['purpose']!='pairing-configuration-manifest':
        raise ValueError('Exact selected manifest')
    total=uint(value['bytes'],positive=True);parts=value['parts']
    if total>max_bytes or not isinstance(parts,list) or not 1<=len(parts)<=max_parts:raise ValueError('Aggregate processing budget')
    if not (len(parts)-1)*CHUNK<total<=len(parts)*CHUNK or not hexvalue(value['sha256'],64):raise ValueError('Configuration length/commitment')
    references=[]
    for index,item in enumerate(parts):
        if not isinstance(item,dict) or set(item)!={'index','reference'} or item['index']!=str(index) or not hexvalue(item['reference'],64):
            raise ValueError('Contiguous exact part references')
        references.append(item['reference'])
    if len(set(references))!=len(references):raise ValueError('Distinct signed parts')
    return value


def frame_chunk(index,count,data):
    return frame_chunk_version(index,count,data,version='1')


def frame_chunk_version(index,count,data,*,version):
    if version not in ('1','2'):raise ValueError('Explicit supported chunk version')
    if type(index) is not int or type(count) is not int or not 0<=index<count<2**64 or not isinstance(data,bytes) or not 1<=len(data)<=CHUNK:
        raise ValueError('Chunk frame bounds')
    if index<count-1 and len(data)!=CHUNK:raise ValueError('Full non-final chunk')
    return b'EML2CFG'+version.encode()+struct.pack('>QQI',index,count,len(data))+data


def assemble(raw_manifest, parts, *, max_bytes, max_parts):
    """parts contains already authenticated/decrypted (index,reference,bytes).

    The caller must produce these values through the original signed v1 part and
    age validators; ordinary received tuples have no authority to call installation.
    """
    return assemble_version(raw_manifest,parts,max_bytes=max_bytes,max_parts=max_parts,version='1')


def assemble_version(raw_manifest,parts,*,max_bytes,max_parts,version):
    value=manifest_version(raw_manifest,max_bytes=max_bytes,max_parts=max_parts,version=version)
    magic=b'EML2CFG'+version.encode()
    if not isinstance(parts,list) or len(parts)!=len(value['parts']):raise ValueError('Complete part set required')
    retained={}
    for index,reference,raw in parts:
        if type(index) is not int or not 0<=index<len(value['parts']) or index in retained or reference!=value['parts'][index]['reference']:
            raise ValueError('Exact unique part binding')
        if not isinstance(raw,bytes) or len(raw)<28 or raw[:8]!=magic:raise ValueError('Chunk magic/header')
        actual,count,length=struct.unpack('>QQI',raw[8:28]);data=raw[28:]
        if actual!=index or count!=len(parts) or len(data)!=length or not 1<=length<=CHUNK or (index<count-1 and length!=CHUNK):
            raise ValueError('Chunk scope/length')
        retained[index]=data
    # Check the aggregate before allocating the contiguous result, not afterward.
    if sum(map(len,retained.values()))!=int(value['bytes']):
        raise ValueError('Whole configuration length before allocation')
    result=b''.join(retained[index] for index in range(len(parts)))
    if len(result)!=int(value['bytes']) or hashlib.sha256(result).hexdigest()!=value['sha256']:raise ValueError('Whole configuration commitment')
    # UTF-8 is validated only after assembly: a scalar can span chunk boundaries.
    result.decode('utf-8','strict')
    return {'status':'configuration-bytes-only','original':result}
