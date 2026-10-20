"""Local packaging experiment, not a registered media type or encrypted sender."""
from email.message import EmailMessage
from email import policy
import hashlib
from event_encoding import decode_event

POLICY=policy.SMTP
# Unregistered candidate, used only under this experiment's explicit profile.
EVENT_SUBTYPE='vnd.threadlabs.email-next-event+json'
EVENT_MEDIA_TYPE='application/'+EVENT_SUBTYPE

def mime_filename(name):
    # Header projection only; never a guarantee of filesystem-safe storage.
    return ''.join('_' if ord(c)<32 or ord(c)==127 else c for c in name) or 'attachment'


def contribution_alternatives(event_bytes, plain, html):
    """Package already validated/projected data; does not establish their binding."""
    decode_event(event_bytes)
    alternatives=EmailMessage(policy=POLICY)
    alternatives.set_content(plain,charset='utf-8',cte='base64')
    alternatives.add_alternative(html,subtype='html',charset='utf-8',cte='base64')
    structured=EmailMessage(policy=POLICY)
    # The candidate name is not an assignment or evidence of recipient capability.
    structured.set_content(event_bytes,maintype='application',subtype=EVENT_SUBTYPE,cte='base64')
    alternatives.attach(structured)
    return alternatives


def package_attachment(event_bytes, plain, html, resources):
    event=decode_event(event_bytes)['value']
    operation=event['operation']
    if operation.get('kind')!='attachment-message':
        raise ValueError('attachment-message required')
    # Full operation validation and readable projection precede this fixture adapter.
    manifest=operation['manifest']
    expected={item['id']:item for item in manifest}
    if len(expected)!=len(manifest) or set(resources)!=set(expected):
        raise ValueError('resource inventory mismatch')
    descriptions={item['resource']:item for item in operation['attachments']}
    if len(descriptions)!=len(operation['attachments']) or set(descriptions)!=set(expected):
        raise ValueError('description inventory mismatch')
    for identifier,data in resources.items():
        item=expected[identifier]
        if not isinstance(data,bytes) or str(len(data))!=item['size'] or hashlib.sha256(data).hexdigest()!=item['sha256']:
            raise ValueError('resource integrity mismatch')
    root=EmailMessage(policy=POLICY)
    root.make_mixed()
    alternatives=contribution_alternatives(event_bytes, plain, html)
    root.attach(alternatives)
    for description in operation['attachments']:
        identifier=description['resource']
        maintype,subtype=description['mediaType'].split('/',1)
        # Composite media stay opaque resources; do not expose a nested MIME tree.
        if maintype in ('message','multipart'):
            maintype,subtype='application','octet-stream'
        part=EmailMessage(policy=POLICY)
        part.set_content(resources[identifier],maintype=maintype,subtype=subtype,cte='base64')
        part['Content-ID']=f"<{identifier}.{event['event']}@resources.email-next.invalid>"
        part.add_header('Content-Disposition','attachment',filename=mime_filename(description['name']))
        root.attach(part)
    return root.as_bytes()


def _parse_package(octets, max_wire_bytes, max_parts, max_decoded_bytes):
    from email.parser import BytesParser
    if (not isinstance(octets,bytes) or any(type(n) is not int or n<0 for n in
            [max_wire_bytes,max_parts,max_decoded_bytes]) or len(octets)>max_wire_bytes):
        raise ValueError('invalid input or limits')
    root=BytesParser(policy=policy.default).parsebytes(octets)
    nodes=list(root.walk())
    if len(nodes)>max_parts or any(p.defects for p in nodes):
        raise ValueError('invalid or excessive MIME structure')
    for part in nodes:
        if len(part.get_all('Content-Type',[]))!=1 or getattr(part['Content-Type'],'defects',()):
            raise ValueError('ambiguous content type')
    return root


def _decode_alternatives(alternatives, max_decoded_bytes):
    import base64
    import binascii
    import re
    if [p.get_content_type() for p in alternatives]!=['text/plain','text/html',EVENT_MEDIA_TYPE]:
        raise ValueError('ambiguous alternatives')
    # get_content_type ignores parameters; inspect them explicitly before activation.
    if len(alternatives[2].get_params(header='Content-Type',failobj=[]))!=1:
        raise ValueError('event media parameters are not supported')
    decoded=[]
    remaining=max_decoded_bytes
    for part in alternatives:
        if part.is_multipart() or len(part.get_all('Content-Transfer-Encoding',[]))!=1 or str(part['Content-Transfer-Encoding']).lower()!='base64':
            raise ValueError('unsupported alternative encoding')
        try:
            raw=part.get_payload(decode=False).encode('ascii')
            compact=re.sub(rb'[ \t\r\n]',b'',raw)
            data=base64.b64decode(compact,validate=True)
            if base64.b64encode(data)!=compact:
                raise ValueError('noncanonical encoding')
        except (UnicodeError,binascii.Error,AttributeError) as error:
            raise ValueError('invalid alternative encoding') from error
        remaining-=len(data)
        if remaining<0:
            raise ValueError('decoded limit exceeded')
        decoded.append(data)
    return decoded, remaining


def inspect_contribution_package(octets, *, max_wire_bytes, max_parts, max_decoded_bytes):
    """Select the standalone alternative layout; all returned data is untrusted."""
    root=_parse_package(octets,max_wire_bytes,max_parts,max_decoded_bytes)
    if root.get_content_type()!='multipart/alternative':
        raise ValueError('wrong contribution root')
    decoded,_=_decode_alternatives(list(root.iter_parts()),max_decoded_bytes)
    return {'event':decode_event(decoded[2]),'plain':decoded[0],'html':decoded[1]}


def inspect_attachment_package(octets, *, max_wire_bytes, max_parts, max_decoded_bytes):
    """Recognize only the generated fixture layout; returns UNAUTHENTICATED data."""
    from mime_resources import parse_resources
    root=_parse_package(octets,max_wire_bytes,max_parts,max_decoded_bytes)
    if root.get_content_type()!='multipart/mixed':
        raise ValueError('wrong root')
    children=list(root.iter_parts())
    if len(children)<2 or children[0].get_content_type()!='multipart/alternative':
        raise ValueError('missing contribution or attachments')
    decoded,remaining=_decode_alternatives(list(children[0].iter_parts()),max_decoded_bytes)
    event=decode_event(decoded[2])
    operation=event['value'].get('operation')
    if not isinstance(operation,dict) or operation.get('kind')!='attachment-message':
        raise ValueError('wrong operation')
    container=EmailMessage(policy=POLICY);container.make_mixed()
    for child in children[1:]:
        container.attach(child)
    serialized=container.as_bytes()
    resources=parse_resources(serialized,max_wire_bytes=len(serialized),
                              max_parts=max_parts,max_decoded_bytes=remaining)
    # No media sniffing, HTML activation, identity validation or cryptography here.
    return {'event':event,'plain':decoded[0],'html':decoded[1],'resources':resources}
