"""Trusted display data derived only from accepted retained application bytes.

Outer headers remain separately labelled transport observations and never provide
reply authority. This is semantic envelope3 presentation, not RFC9788 parsing.
"""
import hashlib,json
from datetime import datetime,timezone
from email import policy
from email.parser import BytesParser
from event_encoding import decode_event

def transport_details(wire):
    if not isinstance(wire,bytes) or len(wire)>2097152:raise ValueError('Transport display bound')
    message=BytesParser(policy=policy.default).parsebytes(wire)
    return dict(protection='unprotected-transport',fields={name:[str(value) for value in message.get_all(name,[])] for name in ('From','To','Cc','Subject','Date','Reply-To','References','In-Reply-To')})

def authored_date(value):
    if value=='':return dict(source='',display='Not stated',trustedClock=False)
    try:
        seconds=int(value)
        # Avoid host-dependent overflow/truncation before converting to a date.
        if seconds>253402300799:raise OverflowError()
        display=datetime.fromtimestamp(seconds,timezone.utc).isoformat()
    except (ValueError,OverflowError,OSError):display='Unavailable'
    return dict(source=value,display=display,trustedClock=False)

def describe(receiver,reference,*,carrier,transport_wire):
    rows=[r for r in receiver.journal.snapshot(reference['conversation']) if r['reference']==reference]
    if len(rows)!=1 or rows[0]['state']!='recorded':raise ValueError('Accepted contribution required')
    raw=rows[0]['octets'][0]
    row=receiver.db.execute('SELECT application,evidence FROM mls_receives WHERE digest=?',(carrier,)).fetchone()
    accepted=receiver.db.execute('SELECT state FROM mls_application_acceptance WHERE digest=?',(hashlib.sha256(raw).hexdigest(),)).fetchone()
    if not row or row[0]!=raw or accepted!=('accepted',):raise ValueError('Accepted carrier required')
    event=decode_event(raw)['value'];context=decode_event(bytes.fromhex(json.loads(row[1])['snapshot']['context']))['value']
    details=transport_details(transport_wire)
    if event['version']!='3' or context['version'] not in ('6','7'):
        return dict(state='older-profile',notice='Outer subject and date are not authenticated by this profile.',authorPrincipal=event['principal'],audience=event['audience'],transport=details)
    from private_copy import check_roster
    check_roster(context,event['audience']);p=event['presentation']
    return dict(state='authenticated-presentation',subject=p['subject'],authoredAt=authored_date(p['authoredAt']),authorPrincipal=event['principal'],to=p['to'],cc=p['cc'],audience=event['audience'],conversation=event['conversation'],replyAudience=event['audience'],delivery=context['delivery'],transport=details,notice='Subject and recipient roles are protected. The stated date is the author’s claim.')

def provisional(wire):
    return dict(state='provisional-transport',notice='Protected contribution not yet accepted. Transport headers are unverified; no reply or action is authorized.',transport=transport_details(wire))
