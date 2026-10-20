"""Candidate rich-body MIME layout; selection supplies no author authority."""
from email import policy
from email.message import EmailMessage
from mime_package import contribution_alternatives,package_attachment,_parse_package,_decode_alternatives
from mime_resources import parse_resources
from event_encoding import decode_event

def package_rich(event_bytes,resources,*,max_wire_bytes,max_parts,max_decoded_bytes):
    event=decode_event(event_bytes)['value'];op=event['operation']
    if op.get('kind')!='rich-message':raise ValueError('Rich operation')
    expected={x['id']:x for x in op['manifest']}
    import hashlib
    if set(resources)!=set(expected):raise ValueError('Resource inventory')
    for key,data in resources.items():
        if not isinstance(data,bytes) or str(len(data))!=expected[key]['size'] or hashlib.sha256(data).hexdigest()!=expected[key]['sha256']:raise ValueError('Resource integrity')
    alternatives=contribution_alternatives(event_bytes,op['text'],op['html'])
    if op['embedded']:
        related=EmailMessage(policy=policy.SMTP);related.make_related();related.set_param('type','text/html')
        related.attach(alternatives.get_payload()[1])
        for image in op['embedded']:
            part=EmailMessage(policy=policy.SMTP);part.set_content(resources[image['resource']],maintype='image',subtype=image['mediaType'].split('/')[1],cte='base64')
            part['Content-ID']='<'+image['resource']+'.'+event['event']+'@resources.email-next.invalid>';part['Content-Disposition']='inline';related.attach(part)
        alternatives.get_payload()[1]=related
    if op['attachments']:
        # Reuse exact independent-attachment header projection, never reinterpret files.
        shadow=dict(event,operation=dict(kind='attachment-message',text=op['text'],replyTo=op['replyTo'],manifest=[expected[x['resource']] for x in op['attachments']],attachments=op['attachments']))
        from event_encoding import encode_event
        from email.parser import BytesParser
        generated=BytesParser(policy=policy.SMTP).parsebytes(package_attachment(encode_event(shadow),op['text'],op['html'],{x['resource']:resources[x['resource']] for x in op['attachments']}))
        root=EmailMessage(policy=policy.SMTP);root.make_mixed();root.attach(alternatives)
        for part in list(generated.iter_parts())[1:]:root.attach(part)
    else:root=alternatives
    if not root.get('MIME-Version'):root['MIME-Version']='1.0'
    wire=root.as_bytes();inspect_rich(wire,max_wire_bytes=max_wire_bytes,max_parts=max_parts,max_decoded_bytes=max_decoded_bytes);return wire

def inspect_rich(octets,*,max_wire_bytes,max_parts,max_decoded_bytes):
    if any(type(v) is not int or v<1 for v in (max_wire_bytes,max_parts,max_decoded_bytes)):raise ValueError('Positive integer carrier limits required')
    if not isinstance(octets,bytes) or len(octets)>max_wire_bytes:raise ValueError('Wire bound')
    bare=octets.replace(b'\r\n',b'')
    if b'\r\n\r\n' not in octets or b'\n' in bare or b'\r' in bare:raise ValueError('CRLF required')
    try:root=_parse_package(octets,max_wire_bytes,max_parts,max_decoded_bytes)
    except RecursionError as error:raise ValueError('Unsupported MIME depth') from error
    if root.get_all('MIME-Version',[])!=['1.0']:raise ValueError('MIME version')
    independent=[]
    if root.get_content_type()=='multipart/mixed':
        children=list(root.iter_parts())
        if len(children)<2:raise ValueError('Empty attachment inventory')
        alternatives=children[0];independent=children[1:]
    else:alternatives=root
    if alternatives.get_content_type()!='multipart/alternative':raise ValueError('Alternative root')
    children=list(alternatives.iter_parts())
    if len(children)!=3:raise ValueError('Three alternatives required')
    embedded=[];html=children[1]
    if html.get_content_type()=='multipart/related':
        if html.get_param('type')!='text/html' or html.get_param('start') is not None:raise ValueError('Related root profile')
        inner=list(html.iter_parts())
        if len(inner)<2:raise ValueError('Missing embedded inventory')
        html=inner[0];embedded=inner[1:]
    decoded,remaining=_decode_alternatives([children[0],html,children[2]],max_decoded_bytes)
    for text in decoded[:2]:text.decode('utf8','strict')
    event=decode_event(decoded[2])
    if event['value'].get('operation',{}).get('kind')!='rich-message':raise ValueError('Rich operation required')
    resource_nodes=embedded+independent
    for part in root.walk():
        names=[name.lower() for name,_ in part.raw_items()]
        allowed={'content-type','mime-version'}|({'content-transfer-encoding'} if not part.is_multipart() else set())
        if part in resource_nodes:allowed|={'content-id','content-disposition'}
        if len(names)!=len(set(names)) or set(names)-allowed or any(getattr(v,'defects',()) for _,v in part.items()):raise ValueError('Carrier headers')
        if part.is_multipart():
            params=dict(part.get_params()[1:]);expected={'boundary','type'} if part.get_content_type()=='multipart/related' else {'boundary'}
            if set(params)!=expected or not part.get_boundary() or part.preamble not in (None,'') or part.epilogue not in (None,''):raise ValueError('Multipart parameters')
        elif part in resource_nodes:
            if part.get_content_maintype() in ('message','multipart') or len(part.get_params())!=1:raise ValueError('Opaque resource type')
            disposition=part.get_content_disposition()
            if part in embedded and (part.get_content_type() not in ('image/png','image/jpeg') or disposition!='inline' or len(part.get_params(header='Content-Disposition'))!=1):raise ValueError('Embedded image projection')
            if part in independent and (disposition!='attachment' or len(part.get_params(header='Content-Disposition'))!=2 or part.get_params(header='Content-Disposition')[1][0]!='filename'):raise ValueError('Attachment projection')
        elif part.get_content_type() in ('text/plain','text/html') and part.get_params()!=[(part.get_content_type(),''),('charset','utf-8')]:raise ValueError('UTF8 text required')
    def resources(parts,budget):
        if not parts:return []
        container=EmailMessage(policy=policy.SMTP);container.make_mixed()
        for p in parts:container.attach(p)
        raw=container.as_bytes();return parse_resources(raw,max_wire_bytes=len(raw),max_parts=max_parts,max_decoded_bytes=budget)
    images=resources(embedded,remaining);remaining-=sum(len(p['bytes']) for p in images)
    files=resources(independent,remaining)
    return dict(entity=octets,event=event,plain=decoded[0],html=decoded[1],embedded=images,attachments=files,
        embeddedTypes=[p.get_content_type() for p in embedded],attachmentProjections=[dict(mediaType=p.get_content_type(),filename=p.get_filename()) for p in independent])
