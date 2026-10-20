"""Trusted local configured application agreement; never a network capability claim."""
import json
import re


def profile(value):
    if isinstance(value,dict) and set(value)=={'envelopeVersion','payload','operations'}:
        from application_tuples import validate_tuples
        # Syntax only: actual ordering is checked against the authenticated context.
        validate_tuples([dict(value,ordering='fixed-roster-v0')],version='5' if value['envelopeVersion']=='3' else '4' if value['envelopeVersion']=='2' else '3' if value['payload']=='mime-rich-v0' else '2')
        return json.dumps(value,sort_keys=True,separators=(',',':'))
    if not isinstance(value,dict) or set(value)!={'envelopeVersion','operations'} or value['envelopeVersion']!='1':raise ValueError('Application profile')
    ops=value['operations']
    if not isinstance(ops,list) or not ops or any(type(x)!=str or x not in ('answer','hosted-holder-observation','message','question','reaction','reaction-withdraw') for x in ops) or ops!=sorted(set(ops)):raise ValueError('Application operations')
    return json.dumps(value,sort_keys=True,separators=(',',':'))


class ApplicationAgreement:
    def __init__(self,db):
        self.db=db
        db.execute('CREATE TABLE IF NOT EXISTS mls_application_agreement(group_id TEXT NOT NULL,credential TEXT NOT NULL,signature_key TEXT NOT NULL,application TEXT NOT NULL,PRIMARY KEY(group_id,credential))')
        db.execute('CREATE TABLE IF NOT EXISTS mls_application_agreement_provenance(group_id TEXT NOT NULL,credential TEXT NOT NULL,kind TEXT NOT NULL,admission TEXT,PRIMARY KEY(group_id,credential))')

    def configure_device(self,group,credential,signature_key,application):
        """Local setup only. Caller selects exact device/key; no ownership assertion."""
        if not isinstance(group,str) or not re.fullmatch('(?:[0-9a-f]{2})+',group):raise ValueError('Group')
        if not isinstance(credential,str) or not re.fullmatch('[0-9a-f]{170}',credential) or bytes.fromhex(credential)[:21]!=b'email-next/device/v0\0':raise ValueError('Credential')
        if not isinstance(signature_key,str) or not re.fullmatch('[0-9a-f]{64}',signature_key):raise ValueError('Signature key')
        encoded=profile(application)
        if self.db.in_transaction:raise ValueError('Configure outside transaction')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            previous=self.db.execute('SELECT kind FROM mls_application_agreement_provenance WHERE group_id=? AND credential=?',(group,credential)).fetchone()
            if previous and previous[0]!='configured-local':raise ValueError('Signed agreement requires a new admission or reviewed transition')
            self.db.execute('INSERT INTO mls_application_agreement VALUES(?,?,?,?) ON CONFLICT(group_id,credential) DO UPDATE SET signature_key=excluded.signature_key,application=excluded.application',(group,credential,signature_key,encoded))

            self.db.execute("INSERT OR IGNORE INTO mls_application_agreement_provenance VALUES(?,?,'configured-local',NULL)",(group,credential))
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK');raise

    def resolve(self,group,members,*,instance=None):
        """members comes from authenticated MLS metadata, never browser fields."""
        agreed=None
        if not members:return None
        seen=set()
        for member in members:
            credential,key=member['identity'],member['key']
            if credential in seen:return None
            seen.add(credential)
            if instance is None:
                row=self.db.execute('SELECT signature_key,application FROM mls_application_agreement WHERE group_id=? AND credential=?',(group,credential)).fetchone()
            else:
                row=self.db.execute('SELECT signature_key,application FROM mls_instance_agreements WHERE instance=? AND credential=?',(instance,credential)).fetchone()
            if not row or row[0]!=key or (agreed is not None and row[1]!=agreed):return None
            agreed=row[1]
        return json.loads(agreed)
