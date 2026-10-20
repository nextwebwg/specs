"""Explicit local authorization of provider disclosure before later mail delivery.

All plan, author and hosted records share a canonical SQLite database. No incoming
message can provision a plan. Current local checks do not guarantee remote activity.
"""
import hashlib
import json
import subprocess
from pathlib import Path
from event_encoding import decode_event
from hosted_access import parse
from passive_discovery import mailbox_syntax
from provider_mls import call
from hosted_projection import hosted_source_text


def _canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))

def validate_local_shape(application):
    value=decode_event(application)['value']
    checked=subprocess.run(['node',str(Path(__file__).with_name('check-decoded-envelope.mjs'))],input=application,capture_output=True,check=True,timeout=10)
    if json.loads(checked.stdout)!={'shapeValid':True}:raise ValueError('Local application shape')
    return value

def check_plans(db,application,revision):
    from private_copy_plan import check
    check(db,application,revision)
    value=decode_event(application)['value'];declared=value.get('disclosures',[]);digest=hashlib.sha256(application).hexdigest()
    hosts=[item['service'] for item in declared if item.get('kind')=='provider-hosted']
    has_table=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='hosted_disclosure_plans'").fetchone()
    rows=db.execute('SELECT service,application,policy_revision,enabled FROM hosted_disclosure_plans WHERE digest=? ORDER BY service',(digest,)).fetchall() if has_table else []
    if [r[0] for r in rows]!=hosts or any(r[1]!=application or r[2]!=revision or r[3]!=1 for r in rows):raise ValueError('Hosted disclosure plans required')
    if any(item.get('kind')=='plaintext-email' for item in declared):
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='plaintext_plans'").fetchone():raise ValueError('Plaintext disclosure plan required')
        row=db.execute('SELECT application,policy_revision FROM plaintext_plans WHERE digest=?',(digest,)).fetchone()
        if row!=(application,revision):raise ValueError('Plaintext disclosure plan required')
    return {'digest':digest,'hosts':hosts}


def check_original(sender,db,create_operation,time):
    if not db.in_transaction:raise ValueError('Transaction required')
    binding=db.execute('SELECT digest,service,grant_id,request_digest,route,source_text FROM hosted_disclosure_grants WHERE create_operation=?',(create_operation,)).fetchone()
    if not binding:raise ValueError('Bound hosted plan required')
    digest,service,grant,request_digest,route,source_text=binding
    plan=db.execute('SELECT application,policy_revision,enabled FROM hosted_disclosure_plans WHERE digest=? AND service=?',(digest,service)).fetchone()
    if not plan or plan[2]!=1:raise ValueError('Inactive hosted plan')
    if source_text is None or hosted_source_text(plan[0])!=source_text:raise ValueError('Changed hosted formatter')
    prepared=db.execute('SELECT p.id,p.application,p.request,p.metadata,p.dependencies,p.policy_revision FROM local_author_evidence a JOIN sender_prepared p ON p.id=a.delivery WHERE a.digest=?',(digest,)).fetchone()
    if not prepared or prepared[1]!=plan[0]:raise ValueError('Prepared local author required')
    policy=db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone()
    if not policy or policy[0]!=plan[1] or policy[0]!=prepared[5]:raise ValueError('Changed disclosure policy')
    check_plans(db,plan[0],policy[0])
    checkpoint=db.execute('SELECT group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
    if not checkpoint:raise ValueError('Current group required')
    metadata=call(sender.binary,op='inspect-send',checkpoint=json.loads(checkpoint[1]),group=checkpoint[0],key=json.loads(prepared[2])['key'])['metadata']
    if _canonical(metadata)!=prepared[3] or _canonical(sender._authority(metadata,time,json.loads(policy[1])['trustPolicy']))!=prepared[4]:raise ValueError('Changed hosted author/context')
    return dict(application=plan[0],delivery=prepared[0],service=service,grant=grant,requestDigest=request_digest,route=json.loads(route))


class HostedDisclosure:
    def __init__(self,sender,hosted):
        self.sender=sender;self.hosted=hosted;self.db=sender.db
        if self.db.in_transaction:raise ValueError('Initialize outside transaction')
        if Path(self.db.execute('PRAGMA database_list').fetchone()[2]).resolve()!=Path(hosted.path).resolve():raise ValueError('Shared canonical database required')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS hosted_disclosure_plans(digest TEXT,service TEXT,application BLOB,policy_revision INTEGER,enabled INTEGER,authorization TEXT,PRIMARY KEY(digest,service));
        CREATE TABLE IF NOT EXISTS hosted_disclosure_grants(create_operation TEXT PRIMARY KEY,digest TEXT,service TEXT,grant_id TEXT,request_digest TEXT,route TEXT,source_text TEXT,UNIQUE(service,grant_id));''')
        if 'source_text' not in [r[1] for r in self.db.execute('PRAGMA table_info(hosted_disclosure_grants)')]:self.db.execute('ALTER TABLE hosted_disclosure_grants ADD COLUMN source_text TEXT')
    def authorize(self,application,grants):
        """Local author decision authorizing provider access before later mail delivery.

        grants maps retained create-operation IDs to explicit sender/recipient mailbox routes.
        """
        value=validate_local_shape(application);service=self.hosted.vault.service
        if value.get('version')!='1' or value.get('principal')!=self.hosted.vault.owner or value.get('operation',{}).get('kind') not in ('message','question'):raise ValueError('Local message/question required')
        if {'kind':'provider-hosted','service':service,'model':'bearer'} not in value.get('disclosures',[]):raise ValueError('Hosted descriptor required')
        if not isinstance(grants,dict) or not grants:raise ValueError('Explicit grant routes required')
        digest=hashlib.sha256(application).hexdigest();self.db.execute('BEGIN IMMEDIATE')
        try:
            policy=self.db.execute('SELECT revision FROM sender_policy WHERE id=1').fetchone()
            if not policy:raise ValueError('Configure author policy')
            bindings=[]
            for operation,route in sorted(grants.items()):
                if not isinstance(route,dict) or set(route)!={'fromAddress','recipientAddress'}:raise ValueError('Explicit route')
                for address in route.values():mailbox_syntax(address)
                row=self.db.execute('SELECT grant_id,purpose FROM outgoing WHERE operation=?',(operation,)).fetchone()
                if not row or row[1]!='hosted-grant-create':raise ValueError('Retained create required')
                raw=self.hosted.vault.get(self.db,operation,row[1],row[0]);req=parse(raw,row[1])
                if req['version']!='1' or req['contribution']!={k:value[k] for k in ('principal','conversation','event')} or req['content']!={'kind':'text','text':hosted_source_text(application)}:raise ValueError('Exact hosted content binding')
                self.hosted.vault.get(self.db,'observer-template:'+operation,'hosted-observer-template',row[0])
                bindings.append((operation,digest,service,req['grant'],hashlib.sha256(raw).hexdigest(),_canonical(route),req['content']['text']))
            old=self.db.execute('SELECT application,policy_revision,enabled FROM hosted_disclosure_plans WHERE digest=? AND service=?',(digest,service)).fetchone()
            if old:
                prior=self.db.execute('SELECT create_operation,digest,service,grant_id,request_digest,route,source_text FROM hosted_disclosure_grants WHERE digest=? AND service=? ORDER BY create_operation',(digest,service)).fetchall()
                if old!=(application,policy[0],1) or prior!=bindings:raise ValueError('Immutable disclosure plan conflict')
            else:
                self.db.execute('INSERT INTO hosted_disclosure_plans VALUES(?,?,?,?,1,?)',(digest,service,application,policy[0],'provider-access-before-delivery'))
                self.db.executemany('INSERT INTO hosted_disclosure_grants VALUES(?,?,?,?,?,?,?)',bindings)
            self.db.execute('COMMIT');return digest
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def withdraw(self,digest):
        self.db.execute('UPDATE hosted_disclosure_plans SET enabled=0 WHERE digest=? AND service=?',(digest,self.hosted.vault.service))
