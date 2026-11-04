"""QR wire binding only; not scanning, independent confirmation or relay authority."""
import hashlib
import struct
from event_encoding import decode_event
from hosted_access import valid_credential
from provider_discovery import urls,uint
from service_authorization import hexvalue

OFFER=set('version purpose service prefix session token offerDigest anchorBundleDigest notAfter'.split())
RETURN=set('version purpose service prefix session transportDigest offerDigest requestDigest notAfter'.split())


def descriptor(raw, *, returning=False):
    value=decode_event(raw,max_octets=2048)['value']
    if set(value)!=(RETURN if returning else OFFER) or value['version']!='0' or value['purpose']!=('pairing-rendezvous-request' if returning else 'pairing-rendezvous-offer'):
        raise ValueError('Exact rendezvous QR shape')
    if not hexvalue(value['session'],64) or value['session']=='0'*64:raise ValueError('Session')
    uint(value['notAfter']);urls(value['service'],prefixes=[value['prefix']])
    hashes=('transportDigest','offerDigest','requestDigest') if returning else ('offerDigest','anchorBundleDigest')
    if any(not hexvalue(value[k],64) for k in hashes):raise ValueError('Exact commitment')
    if not returning and not valid_credential(value['token']):raise ValueError('Target slot token')
    return value


def transport_digest(raw):
    descriptor(raw)
    return hashlib.sha256(b'email2/pairing-rendezvous-qr/v0\0'+struct.pack('>I',len(raw))+raw).hexdigest()


def check_return(raw, *, original_offer_qr):
    offer=descriptor(original_offer_qr);reply=descriptor(raw,returning=True)
    if any(reply[k]!=offer[k] for k in ('service','prefix','session','offerDigest','notAfter')) or reply['transportDigest']!=transport_digest(original_offer_qr):
        raise ValueError('Return QR differs from retained transport')
    return {'status':'rendezvous-wire-only','value':reply,'original':raw}
