"""Extract inert discovery bytes; no signature, identity installation or network."""
import base64
import binascii
from email import policy
from email.parser import BytesParser
import re

MEDIA_TYPE = 'application/vnd.threadlabs.email-next-discovery+json'
MAX_DECODED = 1048576

def extract_discovery(octets, *, max_wire_bytes, max_parts):
    if not isinstance(octets, bytes) or any(type(n) is not int or n < 0
                                           for n in (max_wire_bytes, max_parts)):
        raise ValueError('invalid input or limits')
    if len(octets) > max_wire_bytes:
        return {'state': 'limit-exceeded'}
    root = BytesParser(policy=policy.default).parsebytes(octets)
    if root.defects or len(root.get_all('Content-Type', [])) != 1:
        return {'state': 'invalid'}
    if root.get_content_type() != 'multipart/mixed':
        return {'state': 'absent'}
    if root.get_all('MIME-Version', []) != ['1.0']:
        return {'state': 'invalid'}
    parts = list(root.iter_parts())
    if len(parts) > max_parts:
        return {'state': 'limit-exceeded'}
    candidates = []
    for part in parts:
        # An ambiguous Content-Type cannot be resolved by parser first/last wins.
        headers = part.get_all('Content-Type', [])
        if len(headers) > 1:
            return {'state': 'invalid'}
        if part.get_content_type() == MEDIA_TYPE:
            candidates.append(part)
    if not candidates:
        return {'state': 'absent'}
    if len(candidates) > 1:
        return {'state': 'ambiguous'}
    part = candidates[0]
    if part.defects or part.is_multipart():
        return {'state': 'invalid'}
    for name in ('Content-Type', 'Content-Transfer-Encoding', 'Content-Disposition'):
        values = part.get_all(name, [])
        if len(values) != 1 or getattr(values[0], 'defects', ()):
            return {'state': 'invalid'}
    if len(part.get_params()) != 1 or part.get_content_disposition() != 'attachment':
        return {'state': 'invalid'}
    if str(part['Content-Transfer-Encoding']).lower() != 'base64':
        return {'state': 'invalid'}
    payload = part.get_payload(decode=False)
    if not isinstance(payload, str):
        return {'state': 'invalid'}
    try:
        compact = re.sub(rb'[ \t\r\n]', b'', payload.encode('ascii'))
        if len(compact) > 4 * ((MAX_DECODED + 2) // 3):
            return {'state': 'limit-exceeded'}
        decoded = base64.b64decode(compact, validate=True)
        if len(decoded) > MAX_DECODED:
            return {'state': 'limit-exceeded'}
        if base64.b64encode(decoded) != compact:
            return {'state': 'invalid'}
    except (UnicodeError, binascii.Error, ValueError):
        return {'state': 'invalid'}
    return {'state': 'candidate', 'octets': decoded}
