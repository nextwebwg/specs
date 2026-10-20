"""Bounded ordinary MIME carrier for configured quorum-control experiment."""
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from event_encoding import decode_event,EventLimitExceeded
from ordering_certificates import encode,ProofLimit
MAX_MESSAGE=2097152
MAX_CONTENT=1048576

def package(content):
    if len(content)>MAX_CONTENT:raise EventLimitExceeded('unsupported-size')
    value=decode_event(content)['value']
    if encode(value)!=content:raise ValueError('exact control bytes')
    mail=EmailMessage(policy=policy.SMTP)
    mail['From']='ordering-fixture@example.invalid';mail['To']='recipient-fixture@example.invalid'
    mail['Subject']='Configured group control'
    mail.set_content('This message carries a configured Email Next group transition.')
    mail.add_attachment(content,maintype='application',subtype='json',filename='quorum-control.json')
    raw=mail.as_bytes()
    if len(raw)>MAX_MESSAGE:raise EventLimitExceeded('unsupported-size')
    return raw

def select_object(raw):
    if not isinstance(raw,bytes):raise ValueError('exact mail bytes')
    if len(raw)>MAX_MESSAGE:raise EventLimitExceeded('unsupported-size')
    mail=BytesParser(policy=policy.default).parsebytes(raw)
    parts=list(mail.iter_parts())
    if mail.defects or mail.get_content_type()!='multipart/mixed' or len(parts)!=2:raise ValueError('control MIME')
    if parts[0].get_content_type()!='text/plain' or parts[1].get_content_type()!='application/json' or any(p.defects or p.is_multipart() for p in parts):raise ValueError('control selection')
    data=parts[1].get_payload(decode=True)
    if len(data)>MAX_CONTENT:raise EventLimitExceeded('unsupported-size')
    value=decode_event(data)['value']
    if encode(value)!=data or value.get('version') not in ('0','1','2') or set(value)!=({'version','purpose','candidate','proof'}|({'applicationAssertions'} if value.get('version') in ('1','2') else set())|({'witnessAssertions'} if value.get('version')=='2' else set())) or value['purpose']!='quorum-control-experiment':raise ValueError('control object')
    if value['version'] in ('1','2'):
        from passive_discovery import decode_passive_discovery
        from initial_roster import credential
        wrappers=value['applicationAssertions']
        if not isinstance(wrappers,list):raise ValueError('Assertion array')
        identities=[]
        for w in wrappers:
            d=decode_passive_discovery(encode(w));v=d['assertion']['value']
            if v['version']!=('7' if value['version']=='2' else '6') or d['assertion']['key_package_octets'] is None:raise ValueError('Assertion6 package required')
            identities.append(credential(v))
        if identities!=sorted(set(identities)):raise ValueError('Unique sorted assertions')
    if value['version']=='2':
        from quorum_exchange_support import shape
        import json
        shape(value['witnessAssertions'],json.loads(bytes.fromhex(value['candidate']['plan']['result']['context'])))
    proof=value['proof']
    if not isinstance(proof,str) or len(proof)%2 or any(c not in '0123456789abcdef' for c in proof):raise ValueError('proof encoding')
    return value

def select(raw):
    value=select_object(raw)
    return value['candidate'],bytes.fromhex(value['proof'])

def receive(group,raw,*,time):
    try:
        value=select_object(raw)
        if value['version'] in ('1','2'):
            from admitted_quorum import AdmittedQuorum
            if type(group) is not AdmittedQuorum:raise ValueError('Admitted carrier1 handler required')
        options={'application_assertions':value['applicationAssertions']} if value['version'] in ('1','2') else {}
        if value['version']=='2':options['witness_assertions']=value['witnessAssertions']
        from admitted_quorum import AdmittedQuorum
        if type(group) is AdmittedQuorum:
            if value['version']=='2' and not group.db.execute('SELECT 1 FROM qo_signed_exchange_support WHERE group_id=?',(value['candidate']['plan']['scope']['group'],)).fetchone():raise ValueError('Carrier2 requires signed exchange lifecycle')
            if value['version']!='2' and group.db.execute('SELECT 1 FROM qo_signed_exchange_support WHERE group_id=?',(value['candidate']['plan']['scope']['group'],)).fetchone():raise ValueError('Signed exchange lifecycle requires carrier2')
            return group.install(value['candidate'],bytes.fromhex(value['proof']),time=time,report=True,**options)
        decision=group.install(value['candidate'],bytes.fromhex(value['proof']),time=time,**options)
    except (EventLimitExceeded,ProofLimit):return {'status':'unsupported-size','accepted':False}
    return {'status':'accepted','decision':decision}
