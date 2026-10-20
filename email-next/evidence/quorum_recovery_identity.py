"""Recovery-only unchanged binding under demonstrably accepted identity ancestry."""
import base64,json
from identity_bundle import decode_identity_bundle
from initial_roster import credential
from mls_receive import LockedIdentity

def check_witness(identity,witness,time):
    if not identity.db.in_transaction:raise ValueError('Caller transaction required')
    status=LockedIdentity(identity).check_device(bytes.fromhex(credential(witness)),bytes.fromhex(witness['signingKey']),role='send',time=time,trust_policy='allow-unverified')
    if status.get('status')!='authorized-unverified' or status.get('binding')!=witness['binding']:raise ValueError('Current unchanged witness binding')
    cursor=status['head'];seen=set()
    while cursor!=witness['state']:
        if cursor in seen:raise ValueError('Identity ancestry cycle')
        seen.add(cursor)
        row=identity.db.execute('SELECT previous,bundle FROM identity_transitions WHERE principal=? AND digest=? AND accepted=1',(witness['principal'],cursor)).fetchone()
        if not row:raise ValueError('Accepted witness ancestry required')
        transition=decode_identity_bundle(row[1]);accepted=next(s['value'] for s in transition['states'] if s['digest']==cursor)
        selected=next((b for b in accepted['bindings'] if b['device']==witness['device']),None)
        if not selected or selected['digest']!=witness['binding'] or witness['device'] in accepted['revoked']:raise ValueError('Witness binding continuity')
        cursor=row[0]
    row=identity.db.execute('SELECT bundle FROM identity_transitions WHERE principal=? AND digest=? AND accepted=1',(witness['principal'],cursor)).fetchone()
    if row:
        bundle=decode_identity_bundle(row[0]);state=next(s['value'] for s in bundle['states'] if s['digest']==cursor);bindings={b['digest']:b['value'] for b in bundle['bindings']}
    else:
        pin=identity.db.execute('SELECT digest FROM pins WHERE principal=?',(witness['principal'],)).fetchone()
        row=identity.db.execute('SELECT record FROM claims WHERE principal=? AND digest=?',(witness['principal'],cursor)).fetchone()
        if not row or pin!=(cursor,):raise ValueError('Accepted historical witness state')
        record=json.loads(row[0]);state=json.loads(base64.b64decode(record['state']));raw=base64.b64decode(record['binding']);import hashlib
        bindings={hashlib.sha256(raw).hexdigest():json.loads(raw)}
    selected=next((b for b in state['bindings'] if b['device']==witness['device']),None);binding=bindings.get(witness['binding'])
    if not selected or selected['digest']!=witness['binding'] or not binding or binding['device']!=witness['device'] or binding['signingKey']!=witness['signingKey'] or witness['device'] in state['revoked']:raise ValueError('Historical unchanged witness binding')
    return status
