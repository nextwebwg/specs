"""Authenticated-resource caller boundary -> real Node binding -> isolated pixels.

No signatures are checked here. Caller supplies an authenticated manifest/event
and parts from exactly one selected compound. MIME mediaType is a parsed hint;
byte signature checks precede full decoding. Failure retains caller alt text.
"""
import base64
import json
from pathlib import Path
import subprocess
import tempfile
from image_decode import decode_image,DecodeError,DecodeLimits


def resolve_and_decode_image(candidate,event,manifest,parts,*,alt,resource_limits,decode_limits,bridge_max_bytes):
    """Return pixels or inert alt fallback. Explicit local limits are adjustable."""
    if not isinstance(alt,str):raise ValueError('Alt text must be a string')
    if not isinstance(decode_limits,DecodeLimits):raise ValueError('Explicit decoder limits required')
    decode_limits.validate()
    if type(bridge_max_bytes)is not int or bridge_max_bytes<=0:raise ValueError('Positive bridge bound required')
    def fallback(reason):return {'state':'alt','alt':alt,'reason':reason}
    if not isinstance(parts,list):return fallback('invalid-parts')
    prepared=[];encoded_total=0
    for part in parts:
        if not isinstance(part,dict) or not isinstance(part.get('bytes'),bytes):return fallback('invalid-part')
        if len(part['bytes'])>decode_limits.max_encoded:return fallback('encoded-size')
        encoded_total+=len(part['bytes'])
        if encoded_total>bridge_max_bytes:return fallback('bridge-input-size')
        prepared.append({'contentId':part.get('contentId'),'mediaType':part.get('mediaType'),'bytes':base64.b64encode(part['bytes']).decode('ascii')})
    request=json.dumps(dict(candidate=candidate,event=event,manifest=manifest,parts=prepared,limits=resource_limits)).encode()
    if len(request)>bridge_max_bytes:return fallback('bridge-input-size')
    with tempfile.TemporaryFile() as output:
        try:
            process=subprocess.run(['node',str(Path(__file__).with_name('resolve-image-decode.mjs'))],input=request,stdout=output,stderr=subprocess.DEVNULL,timeout=decode_limits.timeout_seconds,check=False)
        except subprocess.TimeoutExpired:return fallback('binding-timeout')
        if process.returncode or output.tell()>bridge_max_bytes:return fallback('binding-failed')
        output.seek(0)
        try:result=json.loads(output.read(bridge_max_bytes+1))
        except ValueError:return fallback('binding-failed')
    if result.get('state')!='bound-image-candidate':return fallback(result.get('state','binding-failed'))
    try:
        encoded=base64.b64decode(result['bytes'],validate=True)
        pixels=decode_image(encoded,result['mediaType'],decode_limits)
    except (DecodeError,ValueError,KeyError):return fallback('decode-rejected')
    return {'state':'pixels','alt':alt,'pixels':pixels}
