"""Bounded direct-scope invitation MIME fixture; selection grants no authority."""
import base64
import re
import quopri
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
MEDIA='application/vnd.email-next.mls-invitation+json'
NOTICE='A compatible configured client can review this request to start a protected conversation. Reading or replying to this notice does not join.\n'
MAX=6*1024*1024


def package(octets):
    """Test fixture only: placeholder addresses are not a production delivery generator."""
    if not isinstance(octets,bytes) or len(octets)>4*1024*1024:raise ValueError('Invitation size')
    message=EmailMessage(policy=policy.SMTP)
    message['From']='creator@example.invalid';message['To']='target@example.invalid'
    message['Subject']='Protected conversation invitation'
    message.set_content(NOTICE,charset='utf-8',cte='7bit')
    message.add_attachment(octets,maintype='application',subtype='vnd.email-next.mls-invitation+json',cte='base64')
    wire=message.as_bytes()
    if len(wire)>MAX:raise ValueError('Wire limit')
    return wire


def _headers(part, required=()):
    # Headerregistry defects are separate from the message parser's defects.
    for name in ('MIME-Version','Content-Type','Content-Disposition','Content-Transfer-Encoding'):
        values=part.get_all(name,[])
        if len(values)>1 or (name in required and len(values)!=1):raise ValueError('Ambiguous singleton')
        if values and getattr(values[0],'defects',()):raise ValueError('Malformed header')
    for name in ('Content-Type','Content-Disposition'):
        params=part.get_params(header=name,failobj=[]) or []
        keys=[key.lower() for key,_ in params[1:]]
        if len(keys)!=len(set(keys)):raise ValueError('Duplicate parameter')


def _decode(part):
    # Preserve non-ASCII source bytes for strict UTF-8 validation after transfer decoding.
    encoding=str(part.get('Content-Transfer-Encoding','7bit')).lower()
    try:
        raw=part.get_payload(decode=True) if encoding in ('7bit','8bit','binary') else part.get_payload().encode('ascii','surrogateescape')
    except (UnicodeError,AttributeError) as error:raise ValueError('Invalid payload') from error
    if encoding=='base64':
        compact=re.sub(rb'[ \t\r\n]',b'',raw)
        try:decoded=base64.b64decode(compact,validate=True)
        except ValueError as error:raise ValueError('Invalid base64') from error
        if base64.b64encode(decoded)!=compact:raise ValueError('Noncanonical base64')
    elif encoding=='quoted-printable':
        if re.search(rb'=(?![0-9A-Fa-f]{2}|\r\n)',raw) or any(byte>127 for byte in raw):raise ValueError('Invalid quoted-printable')
        decoded=quopri.decodestring(raw)
    elif encoding in ('7bit','8bit','binary'):
        if encoding=='7bit' and any(byte>127 for byte in raw):raise ValueError('Invalid 7bit')
        decoded=raw
    else:raise ValueError('Unknown transfer encoding')
    if len(decoded)>MAX:raise ValueError('Decoded limit')
    return decoded


def select(wire):
    if not isinstance(wire,bytes) or len(wire)>MAX:raise ValueError('Wire limit')
    root=BytesParser(policy=policy.default).parsebytes(wire)
    _headers(root,('MIME-Version','Content-Type'))
    if root.defects or root.get_content_type()!='multipart/mixed' or root.get_all('MIME-Version',[])!=['1.0']:raise ValueError('Outer scope')
    if str(root.get('Content-Transfer-Encoding','7bit')).lower() not in ('7bit','8bit','binary'):raise ValueError('Multipart encoding')
    parts=list(root.iter_parts())
    if len(parts)!=2 or any(p.is_multipart() or p.defects for p in parts):raise ValueError('Direct children')
    notice,part=parts
    _headers(notice,('Content-Type',))
    if notice.get_content_type()!='text/plain' or notice.get_content_charset()!='utf-8' or len(notice.get_params())!=2:raise ValueError('Notice')
    try:_decode(notice).decode('utf-8',errors='strict')
    except UnicodeError as error:raise ValueError('Invalid notice UTF-8') from error
    _headers(part,('Content-Type','Content-Disposition','Content-Transfer-Encoding'))
    if part.get_content_type()!=MEDIA or len(part.get_params())!=1 or part.get_content_disposition()!='attachment' or str(part['Content-Transfer-Encoding']).lower()!='base64':raise ValueError('Carrier')
    decoded=_decode(part)
    if len(decoded)>4*1024*1024:raise ValueError('Encoding/size')
    return decoded
