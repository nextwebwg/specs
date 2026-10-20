"""Minimal invitation outbox. Explicit configured SMTP fixture, no retry on ambiguity."""
from email.message import EmailMessage
from email.policy import SMTP
from hosted_access import parse

def prepare(sender, operation, *, from_address, recipient_address):
    # Addresses are supplied by trusted route configuration, never message data.
    req=parse(sender.load(operation),'hosted-grant-create')
    message=EmailMessage(policy=SMTP)
    message['From']=from_address;message['To']=recipient_address
    message['Subject']='A hosted contribution is available'
    message['Message-ID']='<'+req['operation']+'@hosted.example.invalid>'
    message.set_content('A provider-hosted contribution is available. Anyone holding this link can access it while authorized.\n\n'+sender.vault.service+'/g/'+req['grant']+'#'+req['credential']+'\n\nOpening the page submits no answer.\n')
    wire=message.as_bytes()
    with sender.db() as db:
        db.execute('CREATE TABLE IF NOT EXISTS notifications(operation TEXT PRIMARY KEY,grant_id TEXT,state TEXT)')
        sender.vault.put(db,'notification:'+operation,'hosted-notification',req['grant'],wire)
        db.execute('INSERT OR IGNORE INTO notifications VALUES(?,?,?)',(operation,req['grant'],'prepared'))
    return wire

def submit(sender,operation,*,confirmed_creation,transport):
    """Caller supplies directly authenticated, bound creation result from its adapter.

    This boundary does not validate HTTPS provenance. Integration is still required.
    """
    req=parse(sender.load(operation),'hosted-grant-create')
    import hashlib
    expected=dict(version='0',purpose='hosted-management-result',service=sender.vault.service,owner=sender.vault.owner,operation=operation,grant=req['grant'],requestDigest=hashlib.sha256(sender.load(operation)).hexdigest(),outcome='confirmed',reason='created')
    if confirmed_creation!=expected:raise ValueError('creation binding')
    with sender.db() as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT grant_id,state FROM notifications WHERE operation=?',(operation,)).fetchone()
        if not row or row[1]!='prepared':raise ValueError('notification not eligible; reconcile prior attempt')
        wire=sender.vault.get(db,'notification:'+operation,'hosted-notification',row[0])
        db.execute("UPDATE notifications SET state='submission-uncertain' WHERE operation=?",(operation,))
    result=transport(wire)
    with sender.db() as db:db.execute("UPDATE notifications SET state='smtp-submitted' WHERE operation=?",(operation,))
    return result
