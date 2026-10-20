"""Experimental identity proof carrier; decoding alone grants no authority."""
import base64
import binascii
import hashlib
import re
from event_encoding import decode_event,encode_event
from genesis_pipeline import pipeline

HEX_SIGNATURE=re.compile(r'[0-9a-f]{128}\Z')
PRINCIPAL=re.compile(r'enp0:[0-9a-f]{64}\Z')

def decode_identity_bundle(octets):
    wrapper=decode_event(octets)
    value=wrapper['value']
    if set(value)!= {'version','purpose','principal','states','bindings'} or value['version']!='0' or value['purpose']!='identity-bundle':
        raise ValueError('Invalid identity bundle shape')
    principal=value['principal']
    if not isinstance(principal,str) or not PRINCIPAL.fullmatch(principal) or principal=='enp0:'+'0'*64:
        raise ValueError('Invalid principal')
    if not isinstance(value['states'],list) or not isinstance(value['bindings'],list) or not (value['states'] or value['bindings']):
        raise ValueError('Nonempty record collection required')
    result={'octets':octets,'principal':principal,'states':[],'bindings':[]}
    for collection,purpose,proofs in [('states','identity-state',('signature',)),('bindings','device-binding',('authorization','possession'))]:
        seen=set()
        for entry in value[collection]:
            if not isinstance(entry,dict) or set(entry)!= {'payload',*proofs}:
                raise ValueError('Invalid proof entry')
            if not all(isinstance(entry[p],str) and HEX_SIGNATURE.fullmatch(entry[p]) for p in proofs):
                raise ValueError('Invalid proof encoding')
            encoded=entry['payload']
            if not isinstance(encoded,str):raise ValueError('Expected base64 string')
            try:raw=base64.b64decode(encoded,validate=True)
            except (ValueError,binascii.Error) as error:raise ValueError('Invalid payload base64') from error
            if base64.b64encode(raw).decode('ascii')!=encoded:raise ValueError('Noncanonical payload base64')
            decoded=decode_event(raw)
            if decoded['value'].get('purpose')!=purpose or decoded['value'].get('version')!='0' or decoded['value'].get('principal')!=principal:
                raise ValueError('Record scope mismatch')
            digest=hashlib.sha256(raw).hexdigest()
            if digest in seen:raise ValueError('Duplicate payload in bundle')
            seen.add(digest)
            result[collection].append({'octets':raw,'value':decoded['value'],'digest':digest,**{p:entry[p] for p in proofs}})
    return result

def verify_genesis_bundle(octets,*,time):
    decoded=decode_identity_bundle(octets)
    if len(decoded['states'])!=1 or len(decoded['bindings'])!=1:
        raise ValueError('Genesis verifier requires one state and one binding')
    state,binding=decoded['states'][0],decoded['bindings'][0]
    return pipeline({'state':base64.b64encode(state['octets']).decode('ascii'),
                     'binding':base64.b64encode(binding['octets']).decode('ascii'),
                     'stateProof':state['signature'],'authorization':binding['authorization'],
                     'possession':binding['possession'],'time':time})

def verify_successor_bundle(octets,*,accepted_digest,candidate_digest,time):
    """accepted_digest must come from previously accepted local state, not this bundle."""
    import json
    import subprocess
    from pathlib import Path
    for digest in [accepted_digest,candidate_digest]:
        if not isinstance(digest,str) or not re.fullmatch(r'[0-9a-f]{64}',digest):
            raise ValueError('Invalid state digest')
    decoded=decode_identity_bundle(octets)
    request={'acceptedDigest':accepted_digest,'candidateDigest':candidate_digest,'time':time}
    for collection in ['states','bindings']:
        request[collection]=[{**{k:v for k,v in entry.items() if k!='octets'},
                              'base64':base64.b64encode(entry['octets']).decode('ascii')}
                             for entry in decoded[collection]]
    response=subprocess.run(['node',str(Path(__file__).with_name('check-successor.mjs'))],
                            input=json.dumps(request),capture_output=True,text=True,check=True)
    return json.loads(response.stdout)
