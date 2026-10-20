"""Candidate generated layouts only; no authentication, target discovery or effects."""
import base64
import binascii
import json
from pathlib import Path
import re
from email.message import EmailMessage
from event_encoding import decode_event
from mime_package import POLICY, contribution_alternatives, _parse_package, _decode_alternatives

EMOJI = frozenset(json.loads((Path(__file__).parent/'unicode-17/fully-qualified.json').read_text()))
# Deliberately narrow ASCII generation spelling, not a complete RFC5322 parser.
ATOM = r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+"
MSGID = re.compile(r'<'+ATOM+r'(?:\.'+ATOM+r')*@(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)*>')

def _message_id(value):
    if not isinstance(value,str) or not MSGID.fullmatch(value):
        raise ValueError('unsupported or ambiguous target Message-ID')
    return value

def _id(value, principal=False):
    prefix='enp0:' if principal else ''
    size=64 if principal else 32
    return isinstance(value,str) and re.fullmatch(prefix+'[0-9a-f]{'+str(size)+'}',value) is not None and value[len(prefix):]!='0'*size

def _reference(value):
    return isinstance(value,dict) and set(value)=={'principal','conversation','event'} and _id(value['principal'],True) and _id(value['conversation']) and _id(value['event'])

def _event(octets):
    parsed=decode_event(octets); event=parsed['value'];op=event.get('operation')
    if not isinstance(op,dict) or not _reference(op.get('target')):
        raise ValueError('reaction operation required')
    if op.get('kind')=='reaction':
        if set(op)!={'kind','target','emoji'} or not isinstance(op['emoji'],str) or op['emoji'] not in EMOJI:
            raise ValueError('invalid reaction')
    elif op.get('kind')=='reaction-withdraw':
        refs=op.get('reactions')
        if set(op)!={'kind','target','reactions'} or not isinstance(refs,list) or not refs or not all(_reference(r) for r in refs) or len({json.dumps(r,sort_keys=True) for r in refs})!=len(refs):
            raise ValueError('invalid withdrawal')
    else:raise ValueError('wrong operation')
    # Structural selection only. Full envelope, target authority and withdrawal
    # ownership are checked by the authenticated receiving path, not MIME.
    return parsed

def package_reaction(event_bytes, plain, html, *, target_message_id=None):
    """Caller supplies projected alternatives and any known transport mapping.

    This function cannot prove that the supplied mapping names the target or that
    arbitrary plain/html arguments agree with the event. It creates no authority.
    """
    op=_event(event_bytes)['value']['operation']
    alternatives=contribution_alternatives(event_bytes,plain,html)
    if op['kind']=='reaction-withdraw' or target_message_id is None:
        if target_message_id is not None:alternatives['In-Reply-To']=_message_id(target_message_id)
        return alternatives.as_bytes()
    root=EmailMessage(policy=POLICY);root.make_mixed();root['MIME-Version']='1.0'
    root['In-Reply-To']=_message_id(target_message_id)
    part=EmailMessage(policy=POLICY)
    part.set_content((op['emoji']+'\r\n').encode(),maintype='text',subtype='plain',cte='base64')
    part.set_param('charset','utf-8');part['Content-Disposition']='reaction'
    root.attach(part);root.attach(alternatives)
    return root.as_bytes()

def inspect_reaction_package(octets, *, max_wire_bytes, max_parts, max_decoded_bytes):
    """Returns untrusted exact candidate bytes, never a received reaction effect."""
    root=_parse_package(octets,max_wire_bytes,max_parts,max_decoded_bytes)
    if list(map(str,root.get_all('MIME-Version',[])))!=['1.0']:
        raise ValueError('ambiguous MIME version')
    if root.get_content_type()=='multipart/alternative':
        decoded,_=_decode_alternatives(list(root.iter_parts()),max_decoded_bytes)
        event=_event(decoded[2])
        return {'event':event,'plain':decoded[0],'html':decoded[1],'layout':'ordinary-alternatives'}
    if root.get_content_type()!='multipart/mixed':raise ValueError('wrong reaction root')
    children=list(root.iter_parts())
    if len(children)!=2 or children[1].get_content_type()!='multipart/alternative':
        raise ValueError('wrong reaction children')
    first=children[0]
    if first.is_multipart() or first.get_content_type()!='text/plain' or first.get_params()!=[('text/plain',''),('charset','utf-8')]:
        raise ValueError('wrong reaction part type')
    if list(map(str,first.get_all('Content-Disposition',[])))!=['reaction'] or list(map(str,first.get_all('Content-Transfer-Encoding',[])))!=['base64']:
        raise ValueError('ambiguous reaction part headers')
    targets=root.get_all('In-Reply-To',[])
    if len(targets)!=1:raise ValueError('one transport target required')
    target=_message_id(str(targets[0]))
    try:
        compact=re.sub(rb'[ \t\r\n]',b'',first.get_payload(decode=False).encode('ascii'))
        data=base64.b64decode(compact,validate=True)
        if base64.b64encode(data)!=compact:raise ValueError('noncanonical base64')
    except (UnicodeError,binascii.Error,AttributeError) as error:raise ValueError('invalid reaction encoding') from error
    if len(data)>max_decoded_bytes:raise ValueError('decoded limit exceeded')
    decoded,_=_decode_alternatives(list(children[1].iter_parts()),max_decoded_bytes-len(data))
    event=_event(decoded[2]);op=event['value']['operation']
    if op['kind']!='reaction':raise ValueError('withdrawal cannot have reaction part')
    # A projection discrepancy does not erase independently verifiable event bytes.
    paired=data==(op['emoji']+'\r\n').encode('utf-8')
    return {'event':event,'plain':decoded[0],'html':decoded[1],'layout':'reaction-pair',
            'transportTarget':target,'reactionPart':data,'pairing':'matched' if paired else 'mismatch'}
