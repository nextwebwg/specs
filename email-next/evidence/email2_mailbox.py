"""Email/2 bare-mailbox spelling, equality and transport classification.

No header parser, account ownership, DNS resolver or delivery authority. User-input
construction is distinct from signed-wire validation. Only domains use IDNA;
local-part Unicode and case are never normalized. A-label/U-label processing needs
the already selected coherent Unicode17 provider, not Python's IDNA2003 codec.
"""
import os
from pathlib import Path

from passive_discovery import ATEXT
from idna17_acceptance import validate_domain,_load


class IDNAUnavailable(ValueError):pass


def _text(value):
    if type(value) is not str:raise ValueError('Mailbox text required')
    try:value.encode('utf-8','strict')
    except UnicodeError as error:raise ValueError('Unicode scalar values required') from error


def _provider():
    config=os.environ.get('EMAIL_NEXT_IDNA17_CONFIG')
    if not config:raise IDNAUnavailable('Coherent Unicode17 IDNA provider required')
    return _load(Path(config).read_bytes())


def domain(value,*,input_form=False):
    _text(value)
    if not value or len(value.encode('utf-8'))>1024 or value.endswith('.'):
        raise ValueError('Bounded DNS domain without root dot required')
    if input_form:
        # ASCII case is DNS-insensitive. No Unicode compatibility/case mapping,
        # alternate separator mapping, or local-part transformation is selected.
        value=''.join(chr(ord(c)+32) if 'A'<=c<='Z' else c for c in value)
        if not value.isascii():
            provider,core=_provider()
            labels=value.split('.')
            if any(provider.normalize('NFC',label)!=label for label in labels):
                raise ValueError('IDNA U-label must already be NFC')
            value='.'.join(core.alabel(label).decode('ascii') for label in labels)
    if not value.isascii() or value!=value.lower() or len(value)>253:
        raise ValueError('Canonical lowercase ASCII domain required')
    labels=value.split('.')
    for label in labels:
        if (not 1<=len(label)<=63 or label[0]=='-' or label[-1]=='-'
                or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in label)
                or (label[2:4]=='--' and not label.startswith('xn--'))):
            raise ValueError('Canonical DNS/IDNA label required')
    if sum(1+len(label) for label in labels)+1>255:raise ValueError('DNS wire limit')
    if any(label.startswith('xn--') for label in labels) and not validate_domain(value):
        raise IDNAUnavailable('A-label validation unavailable')
    return value


def _dot_atom(value):
    return bool(value) and all(atom and all(c in ATEXT or ord(c)>=128 for c in atom) for atom in value.split('.'))


def _local(value):
    if not value or len(value.encode('utf-8'))>64:raise ValueError('SMTP local-part octet bound')
    if not value.startswith('"'):
        if not _dot_atom(value):raise ValueError('SMTPUTF8 dot-string required')
        return value
    if len(value)<2 or not value.endswith('"'):raise ValueError('Closed quoted local part required')
    result=[];i=1
    while i<len(value)-1:
        c=value[i]
        if c=='\\':
            i+=1
            if i>=len(value)-1 or not 32<=ord(value[i])<=126:raise ValueError('SMTP ASCII quoted pair required')
            c=value[i]
        elif c=='"' or ord(c)<32 or ord(c)==127:raise ValueError('SMTP quoted content required')
        result.append(c);i+=1
    return ''.join(result)


def construct(value):
    """Canonicalize an already extracted bare input, never a received signature."""
    _text(value)
    if len(value.encode('utf-8'))>1280 or '@' not in value:raise ValueError('Bounded bare mailbox required')
    local,host=value.rsplit('@',1)
    logical=_local(local);host=domain(host,input_form=True)
    spelling=logical if _dot_atom(logical) else '"'+logical.replace('\\','\\\\').replace('"','\\"')+'"'
    mailbox=spelling+'@'+host
    if len(spelling.encode('utf-8'))>64 or len(mailbox.encode('utf-8'))+2>256:raise ValueError('SMTP mailbox/path octet bound')
    return mailbox


def validate(value):
    """Require exact canonical signed spelling; do not rewrite retained bytes."""
    _text(value)
    # This also checks the configured A-label validator, when one is required.
    if construct(value)!=value:raise ValueError('Noncanonical signed mailbox')
    return value


def selected_domain(value):
    return validate(value).rsplit('@',1)[1]


def requires_smtputf8(value):
    validate(value)
    return not value.rsplit('@',1)[0].isascii()
