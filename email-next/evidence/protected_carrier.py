# SPDX-FileCopyrightText: 2026 Threadlabs Studio
# SPDX-License-Identifier: MIT
"""Strict candidate MIME entity codec; no negotiation or authenticated admission.

Callers must select this format explicitly. This module never sniffs an existing
raw-event payload and does not establish that supplied prose matches an event.
"""
from mime_package import (_decode_alternatives,
                          contribution_alternatives, EVENT_MEDIA_TYPE)
from reaction_mime import inspect_reaction_package, package_reaction
from email.parser import BytesParser
from email import policy
from event_encoding import decode_event


def inspect_carrier(octets, *, max_wire_bytes, max_parts, max_decoded_bytes, max_depth=3):
    limits = dict(max_wire_bytes=max_wire_bytes, max_parts=max_parts,
                  max_decoded_bytes=max_decoded_bytes)
    if any(type(n) is not int or n<0 for n in (max_wire_bytes,max_parts,max_decoded_bytes,max_depth)) or not isinstance(octets,bytes) or len(octets)>max_wire_bytes:
        raise ValueError('invalid input or limits')
    if b'\r\n\r\n' not in octets:
        raise ValueError('MIME entity requires CRLF headers')
    # The generated profile uses CRLF throughout; base64 carries arbitrary content.
    if b'\n' in octets.replace(b'\r\n', b'') or b'\r' in octets.replace(b'\r\n', b''):
        raise ValueError('noncanonical MIME line endings')
    # BytesParser allocates its tree before these structural checks. Only the
    # wire-byte limit precedes parsing; this is not a streaming allocation bound.
    try:root = BytesParser(policy=policy.default).parsebytes(octets)
    except RecursionError as error:raise ValueError('excessive MIME structure') from error
    nodes=[];pending=[(root,1)]
    while pending:
        part,depth=pending.pop()
        if depth>max_depth or len(nodes)>=max_parts or part.defects:raise ValueError('invalid or excessive MIME structure')
        nodes.append(part)
        if part.is_multipart():pending.extend((child,depth+1) for child in part.get_payload())
    mixed = root.get_content_type() == 'multipart/mixed'
    for part in nodes:
        if len(part.get_all('Content-Type',[]))!=1:raise ValueError('one content type required')
        names = [name.lower() for name, _ in part.raw_items()]
        allowed = {'content-type', 'mime-version'}
        if not part.is_multipart():
            allowed.add('content-transfer-encoding')
        if part is root and mixed:
            allowed.add('in-reply-to')
        reaction = mixed and part is root.get_payload()[0]
        if reaction:
            allowed.add('content-disposition')
        if len(names) != len(set(names)) or set(names) - allowed:
            raise ValueError('unexpected or duplicate carrier header')
        if any(getattr(value, 'defects', ()) for _, value in part.items()):
            raise ValueError('malformed carrier header')
        versions = list(map(str, part.get_all('MIME-Version', [])))
        if versions not in ([], ['1.0']) or (part is root and versions != ['1.0']):
            raise ValueError('invalid MIME version')
        params = part.get_params()
        if part.is_multipart():
            if (len(params) != 2 or params[1][0] != 'boundary' or
                    not part.get_boundary() or part.preamble not in (None, '') or
                    part.epilogue not in (None, '')):
                raise ValueError('unexpected multipart parameters or surrounding content')
        elif part.get_content_type() in ('text/plain', 'text/html'):
            if params != [(part.get_content_type(), ''), ('charset', 'utf-8')]:
                raise ValueError('text must explicitly select UTF-8')
        elif part.get_content_type() != EVENT_MEDIA_TYPE or len(params) != 1:
            raise ValueError('unsupported carrier leaf')
    if mixed:
        children=list(root.iter_parts())
        if len(children)!=2 or children[1].get_content_type()!='multipart/alternative' or children[0].is_multipart():raise ValueError('unsupported reaction structure')
        if any(p.is_multipart() for p in children[1].iter_parts()):raise ValueError('nested alternatives unsupported')
        result = inspect_reaction_package(octets, **limits)
    elif root.get_content_type() == 'multipart/alternative':
        if any(p.is_multipart() for p in root.iter_parts()):raise ValueError('nested alternatives unsupported')
        decoded, _ = _decode_alternatives(list(root.iter_parts()), max_decoded_bytes)
        result = dict(event=decode_event(decoded[2]), plain=decoded[0], html=decoded[1],
                      layout='ordinary-alternatives')
    else:
        raise ValueError('unsupported carrier root')
    if 'reactionPart' in result:result['reactionPart'].decode('utf-8',errors='strict')
    result['plain'].decode('utf-8', errors='strict')
    result['html'].decode('utf-8', errors='strict')
    result['entity'] = octets
    return result


def package_carrier(event_bytes, plain, html, *, target_message_id=None, **limits):
    if target_message_id is not None:
        entity=package_reaction(event_bytes,plain,html,target_message_id=target_message_id)
    else:entity = contribution_alternatives(event_bytes, plain, html).as_bytes()
    inspect_carrier(entity, **limits)
    return entity
