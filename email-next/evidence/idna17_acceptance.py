"""Configured strict IDNA17 experiment, not mailbox ownership or safety certification."""
import json
import os
from functools import lru_cache
from pathlib import Path
from unicode17_provider import ICU17,isolated_idna,ProviderError

@lru_cache(maxsize=4)
def _load(exact_config):
    cfg=json.loads(exact_config);provider=ICU17(cfg);core,data=isolated_idna(provider,cfg)
    return provider,core

def validate_domain(domain):
    """Return False only when deployment provider is absent; malformed input raises."""
    if type(domain) is not str or not domain.isascii() or domain!=domain.lower() or not domain or len(domain)>253:
        raise ValueError('Canonical lowercase ASCII domain required')
    labels=domain.split('.')
    for label in labels:
        if not 1<=len(label)<=63 or label[0]=='-' or label[-1]=='-' or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in label):
            raise ValueError('Invalid DNS label')
    config=os.environ.get('EMAIL_NEXT_IDNA17_CONFIG')
    if not config:return False
    provider,core=_load(Path(config).read_bytes());decoded=[]
    for label in labels:
        text=core.ulabel(label.encode('ascii'))
        if core.alabel(text).decode('ascii')!=label:raise ValueError('Noncanonical A-label roundtrip')
        decoded.append(text)
    if any(provider.bidirectional(c) in ('R','AL','AN') for text in decoded for c in text):
        for text in decoded:core.check_bidi(text,check_ltr=True)
    return True
