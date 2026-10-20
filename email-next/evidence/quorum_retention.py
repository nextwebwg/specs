"""Logical local candidate-secret retirement after a certified slot decision.

Public history and durable signing records are retained. No physical erasure or
bounded offline-history pruning is claimed by this helper.
"""
import json
from ordering_certificates import encode

def decided_locked(db,*,group,predecessor,decision):
    if not db.in_transaction:raise ValueError('Caller transaction required')
    if not db.execute('SELECT 1 FROM qo_decision WHERE identity=?',(decision,)).fetchone():raise ValueError('Certified decision required')
    retired=[]
    for ident,raw in db.execute('SELECT candidate,state FROM qo_staged').fetchall():
        record=json.loads(raw);before=record['before']
        if (before['group'],before['predecessor'])!=(group,predecessor):continue
        # Release/history require public before/after, Commit, Welcome and sender.
        # They do not require the stale candidate checkpoint or staged secrets.
        for field in ('checkpoint','unmerged','localStaged','localStageBinding'):record.pop(field,None)
        record['secretRetirementDecision']=decision
        db.execute('UPDATE qo_staged SET state=? WHERE candidate=?',(encode(record),ident));retired.append(ident)
    return retired
