"""Established v1 support proofs: selection is inviter-attested, authority is local."""
import json
import subprocess
from pathlib import Path
from event_encoding import encode_event
from passive_discovery import decode_passive_discovery,hexadecimal,uint64
from passive_discovery_verify import verify_passive_discovery
from provider_control import exact,verify_signature
from application_agreement import profile
from application_support import supports

def proofs(wrapper,value,context):
    application=context['application'];profile(application)
    check=subprocess.run(['node',str(Path(__file__).with_name('check-transition-context.mjs'))],input=json.dumps(dict(context=context,application=application)),text=True,capture_output=True,check=True,timeout=10)
    if context['version']=='7':
        from ordering_mls import context_valid
        context_valid(context)
    elif check.stdout!='valid':raise ValueError('Established application context')
    refs=value['applicationAssertions'];items=wrapper['applicationAssertions'];members=value['members']
    if not isinstance(refs,list) or not isinstance(items,list) or len(refs)!=len(members) or len(items)!=len(members):raise ValueError('Application proof coverage')
    decoded=[]
    for ref,item,member in zip(refs,items,members):
        exact(ref,{'principal','device','digest','signature'})
        pair=(member['principal'],member['device'])
        if (ref['principal'],ref['device'])!=pair or not hexadecimal(ref['digest'],64) or not hexadecimal(ref['signature'],128):raise ValueError('Application proof reference')
        d=decode_passive_discovery(encode_event(item));a=d['assertion'];v=a['value']
        if v['version']!=('7' if value['version']=='7' else {'2':'1','3':'2','4':'3','5':'4','6':'5','7':'6'}.get(context['version'])) or (v['principal'],v['device'])!=pair or a['digest']!=ref['digest'] or d['signature'].hex()!=ref['signature']:raise ValueError('Application proof binding')
        if not supports(v,application,context['ordering']['kind']):raise ValueError('Application support')
        # Historical assertion expiry/state is deliberately not current authority.
        verify_signature(a['octets'],ref['signature'],member['signingKey'],('email-next/passive-discovery/v'+v['version']).encode()+b'\0')
        if pair==(value['target']['principal'],value['target']['device']):
            if any(v[k]!=value['target'][k] for k in ('state','binding','mailbox')) or uint64(v['notBefore'])>uint64(value['notBefore']) or uint64(v['notAfter'])<uint64(value['notAfter']):raise ValueError('Fresh target support interval/binding')
        decoded.append(d)
    return decoded

def current_target(wrapper,value,context,locked,interval,trust,package):
    items=proofs(wrapper,value,context)
    for item,decoded,member in zip(wrapper['applicationAssertions'],items,value['members']):
        is_target=(member['principal'],member['device'])==(value['target']['principal'],value['target']['device'])
        if is_target or context['version']=='7':
            if (is_target and decoded['assertion']['key_package_octets']!=package) or verify_passive_discovery(encode_event(item),locked,time=interval,trust_policy=trust).get('status')!='snapshot-authorized-unverified':raise ValueError('Current target application proof')
    return items

def initialize(db):
    db.execute('CREATE TABLE IF NOT EXISTS mls_established_support(instance TEXT NOT NULL,credential TEXT NOT NULL,evidence BLOB NOT NULL,PRIMARY KEY(instance,credential))')

def install(db,instance,wrapper,value,context):
    if value['version']=='7':
        import base64
        from quorum_exchange_support import initialize,retain_locked
        initialize(db)
        selected=list(wrapper['applicationAssertions'])
        retain_locked(db,base64.b64decode(value['group']).hex(),selected,[decode_passive_discovery(encode_event(item))['assertion']['digest'] for item in selected])
    for member,item in zip(value['members'],wrapper['applicationAssertions']):
        credential=(b'email-next/device/v0\0'+bytes.fromhex(member['principal'][5:])+bytes.fromhex(member['device'][5:])).hex()
        db.execute('INSERT INTO mls_instance_agreements VALUES(?,?,?,?,?,?)',(instance,credential,member['signingKey'],profile(context['application']),'signed-quorum-current-selection' if context['version']=='7' else 'signed-established-inviter-selection',value['decision']))
        evidence=dict(selectionAuthority='quorum-certified-current-selection' if context['version']=='7' else 'inviter-attested-historical-selection',wrapper=item,invitation=value['invitation'],decision=value['decision'],application=context['application'])
        db.execute('INSERT INTO mls_established_support VALUES(?,?,?)',(instance,credential,json.dumps(evidence,sort_keys=True,separators=(',',':')).encode()))
