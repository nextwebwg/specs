# SPDX-FileCopyrightText: 2026 Threadlabs Studio
# SPDX-License-Identifier: MIT
"""Candidate protected attachment structure; resource authority is checked later.

Decoded inventory is untrusted until the event/manifest receiver validates it.
Wire bounds precede parsing; part/decoded bounds are acceptance checks, not
claims about peak parser allocation. No nested message is interpreted.
"""
from email import policy
from email.parser import BytesParser
from mime_package import inspect_attachment_package, package_attachment
from protected_carrier import inspect_carrier


def inspect_attachment_carrier(octets, *, max_wire_bytes, max_parts, max_decoded_bytes):
    limits = dict(max_wire_bytes=max_wire_bytes, max_parts=max_parts,
                  max_decoded_bytes=max_decoded_bytes)
    if (not isinstance(octets, bytes) or any(type(n) is not int or n < 0 for n in limits.values())
            or len(octets) > max_wire_bytes):
        raise ValueError('invalid carrier input or limits')
    bare = octets.replace(b'\r\n', b'')
    if b'\r\n\r\n' not in octets or b'\r' in bare or b'\n' in bare:
        raise ValueError('carrier requires CRLF')
    root = BytesParser(policy=policy.default).parsebytes(octets)
    if root.get_content_type() != 'multipart/mixed' or root.defects:
        raise ValueError('attachment root required')
    names = [n.lower() for n, _ in root.raw_items()]
    if (len(names) != len(set(names)) or set(names) != {'mime-version', 'content-type'}
            or str(root['MIME-Version']) != '1.0'
            or getattr(root['Content-Type'], 'defects', ())
            or len(root.get_params()) != 2 or root.get_params()[1][0] != 'boundary'
            or not root.get_boundary() or root.preamble not in (None, '')
            or root.epilogue not in (None, '')):
        raise ValueError('ambiguous attachment root')
    children = list(root.iter_parts())
    if len(children) < 2 or len(children) + 4 > max_parts:
        raise ValueError('missing or excessive attachment parts')
    if children[0].get_content_type() != 'multipart/alternative':
        raise ValueError('direct body alternatives required')
    inspect_carrier(children[0].as_bytes(policy=policy.SMTP), **limits)
    for part in children[1:]:
        names = [n.lower() for n, _ in part.raw_items()]
        allowed = {'mime-version', 'content-type', 'content-transfer-encoding',
                   'content-id', 'content-disposition'}
        if (part.is_multipart() or part.get_content_maintype() in ('message', 'multipart')
                or part.defects or len(names) != len(set(names)) or set(names) != allowed
                or any(getattr(v, 'defects', ()) for _, v in part.items())
                or str(part['MIME-Version']) != '1.0' or len(part.get_params()) != 1
                or part.get_content_disposition() != 'attachment'
                or len(part.get_params(header='Content-Disposition')) != 2
                or part.get_params(header='Content-Disposition')[1][0] != 'filename'):
            raise ValueError('unsupported attachment leaf')
    result = inspect_attachment_package(octets, **limits)
    result['entity'] = octets
    # Metadata is preserved for comparison with authenticated attachment claims;
    # neither it nor a matching filename grants resource authority.
    result['projections'] = [dict(mediaType=p.get_content_type(), filename=p.get_filename())
                             for p in children[1:]]
    return result


def package_attachment_carrier(event_bytes, plain, html, resources, **limits):
    root = BytesParser(policy=policy.SMTP).parsebytes(
        package_attachment(event_bytes, plain, html, resources))
    root['MIME-Version'] = '1.0'
    entity = root.as_bytes()
    inspect_attachment_carrier(entity, **limits)
    return entity


def compare_attachment_projections(selected, validated_event):
    """Compare header projections after independent operation validation.

    This diagnostic grants neither author authority nor byte-integrity status.
    Match by scoped resource identifier, never array position or filename.
    """
    from mime_package import mime_filename
    result = []
    for description in validated_event['operation']['attachments']:
        cid = description['resource'] + '.' + validated_event['event'] + '@resources.email-next.invalid'
        matches = [i for i, part in enumerate(selected['resources']) if part['contentId'] == cid]
        if len(matches) != 1:
            result.append(dict(resource=description['resource'], state='missing' if not matches else 'ambiguous'))
            continue
        actual = selected['projections'][matches[0]]
        claimed = description['mediaType']
        expected_type = 'application/octet-stream' if claimed.split('/')[0] in ('message', 'multipart') else claimed
        differences = []
        if actual['mediaType'] != expected_type:
            differences.append('mediaType')
        if actual['filename'] != mime_filename(description['name']):
            differences.append('filename')
        result.append(dict(resource=description['resource'], state='mismatch' if differences else 'matched',
                           differences=differences))
    return result
