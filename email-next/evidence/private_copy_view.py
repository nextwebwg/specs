"""Private-copy labels from an accepted retained carrier, never outer headers."""
import hashlib,json
from event_encoding import decode_event
from private_copy import check_roster

def describe(receiver,reference,*,carrier,local_principal):
    rows=[r for r in receiver.journal.snapshot(reference['conversation']) if r['reference']==reference]
    if len(rows)!=1 or rows[0]['state']!='recorded':raise ValueError('Accepted private copy required')
    raw=rows[0]['octets'][0];row=receiver.db.execute('SELECT application,evidence FROM mls_receives WHERE digest=?',(carrier,)).fetchone()
    accepted=receiver.db.execute('SELECT state FROM mls_application_acceptance WHERE digest=?',(hashlib.sha256(raw).hexdigest(),)).fetchone()
    if not row or row[0]!=raw or accepted!=('accepted',):raise ValueError('Accepted carrier required')
    evidence=json.loads(row[1]);snapshot=evidence['snapshot'];context=decode_event(bytes.fromhex(snapshot['context']))['value']
    event=decode_event(raw)['value'];check_roster(context,event['audience'])
    if local_principal not in event['audience']:raise ValueError('Local principal outside audience')
    delivery=context.get('delivery',{})
    if context.get('version') not in ('5','6','7') or delivery.get('kind')!='private-copy-v0':return None
    peer=delivery['originator'] if local_principal==delivery['recipient'] else delivery['recipient']
    return dict(label='Private copy',replyPrincipal=peer,notice='Reply stays in this private conversation. Sending to other people can reveal your participation.',sharing='Planned sharing with a separate protected audience.' if {'kind':'separate-protected-copy'} in event['disclosures'] else 'No additional sharing declared. This does not prevent later copying.')
