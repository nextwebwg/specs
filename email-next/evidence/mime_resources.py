"""Experimental flat resource-container parser; no crypto or legacy MIME claim."""
import base64
import binascii
from email import policy
from email.parser import BytesParser
import re

CID = re.compile(r'<[0-9a-f]{32}\.[0-9a-f]{32}@resources\.email-next\.invalid>\Z')

def parse_resources(octets, *, max_wire_bytes, max_parts, max_decoded_bytes):
    limits=(max_wire_bytes,max_parts,max_decoded_bytes)
    if any(type(n) is not int or n<0 for n in limits) or not isinstance(octets,bytes):
        raise ValueError('invalid input or limits')
    if len(octets)>max_wire_bytes:
        raise ValueError('wire limit exceeded')
    root=BytesParser(policy=policy.default).parsebytes(octets)
    if root.defects or len(root.get_all('Content-Type',[]))!=1 or root.get_content_type()!='multipart/mixed':
        raise ValueError('invalid container')
    # The fixture deliberately permits only a flat container, not arbitrary recursion.
    parts=list(root.iter_parts())
    if len(parts)>max_parts:
        raise ValueError('part limit exceeded')
    result=[]
    total=0
    for part in parts:
        if part.defects or part.is_multipart():
            raise ValueError('invalid or nested resource')
        for header in ['Content-ID','Content-Type','Content-Transfer-Encoding']:
            values=part.get_all(header,[])
            if len(values)!=1 or getattr(values[0],'defects',()):
                raise ValueError('missing, repeated or malformed header')
        cid=str(part['Content-ID'])
        if not CID.fullmatch(cid):
            raise ValueError('noncanonical resource identifier')
        if str(part['Content-Transfer-Encoding']).lower()!='base64':
            raise ValueError('unsupported transfer encoding')
        payload=part.get_payload(decode=False)
        if not isinstance(payload,str):
            raise ValueError('invalid payload')
        try:
            encoded=payload.encode('ascii')
            # Only MIME folding whitespace is removed; other garbage must fail.
            compact=re.sub(rb'[ \t\r\n]',b'',encoded)
            decoded=base64.b64decode(compact,validate=True)
            if base64.b64encode(decoded)!=compact:
                raise ValueError('noncanonical base64')
        except (UnicodeError,binascii.Error) as error:
            raise ValueError('invalid base64') from error
        total+=len(decoded)
        if total>max_decoded_bytes:
            raise ValueError('decoded limit exceeded')
        result.append({'contentId':cid[1:-1],'bytes':decoded})
    return result
