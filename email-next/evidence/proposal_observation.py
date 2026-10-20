"""Durable selected-profile proposal observations; raw carriers never write here."""
import json

PROVENANCE='openmls-0.9.1/validated-proposals-v1'

def initialize(db):
    db.execute("CREATE TABLE IF NOT EXISTS qo_proposal_observation(group_id TEXT NOT NULL,epoch TEXT NOT NULL,predecessor TEXT NOT NULL,candidate TEXT NOT NULL,proposal_count INTEGER NOT NULL CHECK(proposal_count>=0),PRIMARY KEY(group_id,predecessor,candidate))")

def observe_locked(db,candidate,result):
    if not db.in_transaction:raise ValueError('Proposal observation transaction required')
    count=result.get('proposalCount')
    if type(count)!=int or count<0:raise ValueError('Validated library proposal count required')
    before=result['before']
    db.execute('INSERT OR IGNORE INTO qo_proposal_observation VALUES(?,?,?,?,?)',(before['group'],before['epoch'],before['predecessor'],candidate,count))

def check_send(db,metadata):
    """Only accepted epoch advance/terminal retirement ends an active-scope hold.

    Historical rows remain durable. Never infer old proposal validity from raw
    exchange receipt or repair legacy staged provenance using a JSON hint.
    """
    context=json.loads(bytes.fromhex(metadata['context']))
    if context.get('version')!='7':return
    tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('qo_staged','qo_proposal_observation')")}
    if 'qo_staged' in tables:
        for raw, in db.execute('SELECT state FROM qo_staged'):
            retained=json.loads(raw);before=retained['before']
            if (before['group'],before['epoch'])==(metadata['group'],metadata['epoch']) and retained.get('proposalObservation')!=PROVENANCE:
                raise ValueError('Legacy proposal observation requires fresh admission')
    if 'qo_proposal_observation' in tables and db.execute('SELECT 1 FROM qo_proposal_observation WHERE group_id=? AND epoch=? AND proposal_count>0',(metadata['group'],metadata['epoch'])).fetchone():
        raise ValueError('Observed proposals await certified epoch advance')
