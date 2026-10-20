"""Configured v2 transition support; membership policy is a separate authority."""
import json
import hashlib
from passive_discovery import decode_passive_discovery
from pathlib import Path
import subprocess
import group_instances as instances
import transition_support as support
from passive_discovery_verify import verify_passive_discovery
from mls_receive import LockedIdentity
from application_agreement import profile


def authorize(coordinator,result,context,*,historical=False,time=None):
    receiver=coordinator.receiver if hasattr(coordinator,'receiver') else coordinator.sender.receiver
    db=coordinator.db;group=result['before']['group'];application=context['application'];encoded=profile(application)
    selected=instances.optional_current(db,group);origin=selected['instance'] if selected else None
    if historical:
        proof=result.get('authorization',{}).get('applicationAgreement')
        if not isinstance(proof,dict) or proof.get('application')!=application or set(proof) not in ({'instance','application'},{'instance','application','version','devices'}):raise ValueError('Historical application agreement')
        if 'version' in proof:support.wrappers(db,result)
        origin=proof['instance']
    before=result['before']['members'];after=result['after']['members']
    if receiver.application_agreement.resolve(group,before,instance=origin)!=application:raise ValueError('Predecessor application agreement')
    old={(m['identity'],m['key']) for m in before}
    signed=None if historical else support.selected(db,result,time=time)
    for member in after:
        identity,key=member['identity'],member['key']
        if (identity,key) in old:continue
        if historical:
            agreed=receiver.application_agreement.resolve(group,[member],instance=origin)
            if agreed!=application:raise ValueError('Historical added agreement')
        elif signed is not None:
            ref=next(r for r in signed if r['credential']==identity);record=support.load(db,ref['record'])
            candidate=db.execute('SELECT packages FROM gt_candidate WHERE digest=?',(hashlib.sha256(bytes.fromhex(result['wire'])).hexdigest(),)).fetchone() if 'wire' in result else None
            if candidate:
                package=decode_passive_discovery(bytes.fromhex(record['wrapper']))['assertion']['key_package_octets']
                if package is None or package.hex() not in json.loads(candidate[0]):raise ValueError('Signed target candidate package mismatch')
            if verify_passive_discovery(bytes.fromhex(record['wrapper']),LockedIdentity(coordinator.identity),time=time,trust_policy='allow-unverified').get('status')!='snapshot-authorized-unverified':raise ValueError('Current signed target support')
        else:
            row=db.execute('SELECT a.signature_key,a.application,p.kind FROM mls_application_agreement a JOIN mls_application_agreement_provenance p USING(group_id,credential) WHERE a.group_id=? AND a.credential=?',(group,identity)).fetchone()
            if row!=(key,encoded,'configured-local'):raise ValueError('Configured added-device support required')
    result_check=subprocess.run(['node',str(Path(__file__).with_name('check-transition-context.mjs'))],input=json.dumps(dict(context=context,application=application)),text=True,capture_output=True,check=True,timeout=10)
    if result_check.stdout!='valid':raise ValueError('Transition context')
    return dict(instance=origin,application=application,**({'version':'signed-device-support-v1','devices':signed} if signed is not None else {}))


def install(coordinator,result,decision):
    proof=result.get('authorization',{}).get('applicationAgreement')
    if not proof:return
    signed=proof.get('version')=='signed-device-support-v1'
    if signed:
        for ref in proof['devices']:
            if (ref['credential'],ref['key']) not in {(m['identity'],m['key']) for m in result['before']['members']}:
                coordinator.db.execute('INSERT INTO mls_support_episodes VALUES(?,?,?,?,?)',(result['after']['group'],ref['credential'],ref['key'],decision,ref['record']))
                if proof['instance'] is None:
                    prior=coordinator.db.execute('SELECT signature_key,application FROM mls_application_agreement WHERE group_id=? AND credential=?',(result['after']['group'],ref['credential'])).fetchone()
                    if prior and prior!=(ref['key'],profile(proof['application'])):raise ValueError('Existing selected agreement conflict')
                    coordinator.db.execute('INSERT INTO mls_application_agreement VALUES(?,?,?,?) ON CONFLICT(group_id,credential) DO UPDATE SET signature_key=excluded.signature_key,application=excluded.application',(result['after']['group'],ref['credential'],ref['key'],profile(proof['application'])))
                    coordinator.db.execute("INSERT INTO mls_application_agreement_provenance VALUES(?,?,'signed-transition',?) ON CONFLICT(group_id,credential) DO UPDATE SET kind=excluded.kind,admission=excluded.admission",(result['after']['group'],ref['credential'],decision))
    if proof['instance'] is None:return
    db=coordinator.db;old={(m['identity'],m['key']) for m in result['before']['members']};encoded=profile(proof['application'])
    for member in result['after']['members']:
        if (member['identity'],member['key']) in old:continue
        row=db.execute('SELECT signature_key,application,provenance_kind,admission_ref FROM mls_instance_agreements WHERE instance=? AND credential=?',(proof['instance'],member['identity'])).fetchone()
        expected=(member['key'],encoded,'signed-transition' if signed else 'configured-transition',decision)
        if row and row!=expected and not (signed and row[:2]==expected[:2]):raise ValueError('Immutable instance agreement conflict')
        # Same-key/profile return keeps the original instance agreement; the new
        # signed source is retained above under its distinct membership period.
        db.execute('INSERT OR IGNORE INTO mls_instance_agreements VALUES(?,?,?,?,?,?)',(proof['instance'],member['identity'],*expected))
