"""Version-1 initial invitation: exact signed discovery plus embedded MLS Welcome.

Two devices, fixed roster. Version-0 parsing/admission remains in mls_invitation.
"""
import hashlib
import json
from pathlib import Path
from provider_control import decode,exact,participant,verify_signature
from passive_discovery import canonical_base64,hexadecimal,uint64,mailbox_syntax,decode_passive_discovery
from identity_bundle import decode_identity_bundle
from event_encoding import encode_event
from mls_invitation import FIELDS
from signed_application_admission import SignedApplicationAdmission
from passive_discovery_package import validate_package
from provider_mls import call
from mls_receive import FORMAT

DOMAIN=b'email-next/mls-new-conversation-invitation/v1\0'


def parse(octets):
    wrapper=decode(octets,max_bytes=4*1024*1024,max_depth=32)
    exact(wrapper,{'payload','signature','identity','applicationAssertions'})
    raw=canonical_base64(wrapper['payload']);v=decode(raw,max_bytes=2*1024*1024,max_depth=32)
    exact(v,FIELDS|{'applicationAssertions'})
    if v['version'] not in ('1','2') or v['purpose']!='mls-new-conversation-invitation' or v['profile']!='mls-1-0001' or v['epoch']!='1':raise ValueError('Profile')
    for name in ('invitation','conversation'):
        if not hexadecimal(v[name],32) or v[name]=='0'*32:raise ValueError('Object identifier')
    for name in ('creator','target'):
        exact(v[name],{'principal','device','state','binding'}|({'mailbox'} if name=='target' else set()))
        participant({k:v[name][k] for k in ('principal','device')})
        if not all(hexadecimal(v[name][k],64) for k in ('state','binding')):raise ValueError('Identity digest')
    if v['creator']['principal']==v['target']['principal']:raise ValueError('Distinct principals')
    if mailbox_syntax(v['target']['mailbox'])!='syntax-valid':raise ValueError('Target mailbox')
    before,after=uint64(v['notBefore']),uint64(v['notAfter'])
    if after<before:raise ValueError('Lifetime')
    binary={k:canonical_base64(v[k]) for k in ('group','keyPackageRef','context','welcome')}
    if any(not value for value in binary.values()) or len(binary['welcome'])>1048576:raise ValueError('Protocol byte bound')
    if not hexadecimal(wrapper['signature'],128):raise ValueError('Signature')
    bundle=decode_identity_bundle(encode_event(wrapper['identity']))
    if bundle['principal']!=v['creator']['principal']:raise ValueError('Creator bundle')
    context=decode(binary['context'],max_bytes=1048576,max_depth=32)
    exact(context,{'version','purpose','conversation','profile','administrators','application','ordering'})
    ordering={'kind':'fixed-roster-v0'} if v['version']=='1' or context.get('ordering')=={'kind':'fixed-roster-v0'} else dict(kind='designated-member-v0',principal=v['creator']['principal'],device=v['creator']['device'])
    allowed=(v['version']=='1' and context['version']=='2' and ordering=={'kind':'fixed-roster-v0'}) or (v['version']=='2' and (context['version']=='3' or (context['version']=='2' and ordering['kind']=='designated-member-v0')))
    if not allowed or context['purpose']!='conversation-context' or context['conversation']!=v['conversation'] or context['profile']!=v['profile'] or context['administrators']!=[v['creator']['principal']] or context['ordering']!=ordering:raise ValueError('Application context')
    refs=v['applicationAssertions'];proofs=wrapper['applicationAssertions']
    if not isinstance(refs,list) or len(refs)!=2 or not isinstance(proofs,list) or len(proofs)!=2:raise ValueError('Proof coverage')
    expected=sorted((v[name]['principal'],v[name]['device']) for name in ('creator','target'))
    decoded=[]
    for ref,proof,pair in zip(refs,proofs,expected):
        exact(ref,{'principal','device','digest','signature'})
        if (ref['principal'],ref['device'])!=pair or not hexadecimal(ref['digest'],64) or not hexadecimal(ref['signature'],128):raise ValueError('Proof reference')
        d=decode_passive_discovery(encode_event(proof));a=d['assertion'];value=a['value']
        who=v['creator'] if pair==(v['creator']['principal'],v['creator']['device']) else v['target']
        if value['version']!=('2' if context['version']=='3' else '1') or (value['principal'],value['device'])!=pair or a['digest']!=ref['digest'] or d['signature'].hex()!=ref['signature'] or value['state']!=who['state'] or value['binding']!=who['binding']:raise ValueError('Proof binding')
        if 'mailbox' in who and value['mailbox']!=who['mailbox']:raise ValueError('Proof mailbox')
        if before<uint64(value['notBefore']) or after>uint64(value['notAfter']):raise ValueError('Proof lifetime')
        from application_support import supports
        if not supports(value,context['application'],context['ordering']['kind']):raise ValueError('Exact application tuple support')
        decoded.append(d)
    return wrapper,raw,v,binary,bundle,decoded


class ApplicationInvitationAdmission(SignedApplicationAdmission):
    def __init__(self,identity,binary):
        super().__init__(identity,binary)
        self.db.execute('CREATE TABLE IF NOT EXISTS initial_invitation_proofs(principal TEXT NOT NULL,id TEXT NOT NULL,wrapper BLOB NOT NULL,PRIMARY KEY(principal,id))')
        self.db.execute('CREATE TABLE IF NOT EXISTS application_invitation_acceptance(principal TEXT NOT NULL,id TEXT NOT NULL,payload BLOB NOT NULL,signature TEXT NOT NULL,result BLOB NOT NULL,PRIMARY KEY(principal,id))')
        from signed_initial_instances import initialize
        initialize(self.db)

    def accept_message(self,octets,*,target,mailbox,allow_creator,selections,time,trust_policy,crash=None,expected_context=None):
        if trust_policy not in ('allow-unverified','require-verification'):raise ValueError('Trust policy')
        wrapper,raw,v,binary,bundle,proofs=parse(octets)
        if v['version']=='2' and (not isinstance(expected_context,bytes) or expected_context!=binary['context']):raise ValueError('Independently selected initial context required')
        if v['creator']['principal']!=allow_creator:raise ValueError('Creator not locally authorized')
        if any(v['target'][k]!=target[k] for k in ('principal','device')) or v['target']['mailbox']!=mailbox:raise ValueError('Target mismatch')
        if not isinstance(selections,list) or len(selections)!=2:raise ValueError('Local selection coverage')
        selected=[]
        for ref,proof in zip(v['applicationAssertions'],wrapper['applicationAssertions']):
            matches=[s for s in selections if isinstance(s,dict) and set(s)=={'principal','device','mailbox','generation'} and (s['principal'],s['device'])==(ref['principal'],ref['device'])]
            if len(matches)!=1:raise ValueError('Local device selection')
            selected.append(dict(wrapper=encode_event(proof),mailbox=matches[0]['mailbox'],generation=matches[0]['generation'],digest=ref['digest']))
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT payload,signature,result FROM application_invitation_acceptance WHERE principal=? AND id=?',(allow_creator,v['invitation'])).fetchone()
            if old:
                if old[0]!=raw or old[1]!=wrapper['signature']:raise ValueError('Invitation collision')
                self.db.execute('COMMIT');return json.loads(old[2])
            candidate=next((b for b in bundle['bindings'] if b['digest']==v['creator']['binding']),None)
            if not candidate:raise ValueError('Creator binding')
            key=candidate['value'].get('signingKey');verify_signature(raw,wrapper['signature'],key,DOMAIN if v['version']=='1' else b'email-next/mls-new-conversation-invitation/v2\0')
            lo,hi=uint64(time['earliest']),uint64(time['latest'])
            if not uint64(v['notBefore'])<=lo<=hi<=uint64(v['notAfter']):raise ValueError('Invitation validity')
            for d in proofs:
                binding=next((b for b in d['identity']['bindings'] if b['digest']==d['assertion']['value']['binding']),None)
                if not binding or uint64(v['notBefore'])<uint64(binding['value']['notBefore']) or uint64(v['notAfter'])>uint64(binding['value']['notAfter']):raise ValueError('Binding lifetime')
            reference=binary['keyPackageRef'].hex();creator=(b'email-next/device/v0\0'+bytes.fromhex(v['creator']['principal'][5:])+bytes.fromhex(v['creator']['device'][5:])).hex()
            def stage(peers):
                row=self.db.execute('SELECT device,invitation FROM provider_mls_admission WHERE reference=?',(reference,)).fetchone()
                if not row or row[1] is not None:raise ValueError('Package consumed')
                device=json.loads(row[0])
                if device['identity']!=target['identity'] or device['key']!=target['key']:raise ValueError('Local package target')
                if validate_package(bytes.fromhex(device['package']),principal=target['principal'],device=target['device'],accepted_signing_key=bytes.fromhex(target['key']),earliest=v['notBefore'],latest=v['notAfter'],executable=Path(self.binary).with_name('validate-discovery-package'))!={'status':'package-valid'}:raise ValueError('Actual package lifetime or validity')
                joined=call(self.binary,op='join-embedded',checkpoint=device['checkpoint'],key=device['key'],welcome=binary['welcome'].hex(),reference=reference)
                if joined['signerIdentity']!=creator or joined['signerKey']!=key or joined['epoch']!='1' or joined['group']!=binary['group'].hex() or bytes.fromhex(joined['context'])!=binary['context'] or sorted((m['identity'],m['key']) for m in joined['members'])!=sorted((m['identity'],m['key']) for m in peers):raise ValueError('Authenticated group binding')
                self.db.execute('INSERT INTO mls_checkpoint VALUES(1,0,?,?,?)',(FORMAT,joined['group'],json.dumps(joined['checkpoint']).encode()))
                self.db.execute('UPDATE provider_mls_admission SET invitation=?,joined=? WHERE reference=?',(encode_event({'payload':wrapper['payload'],'signature':wrapper['signature']}),json.dumps(joined).encode(),reference))
                return joined
            joined=self._accept_signed_locked(reference,{'payload':wrapper['payload'],'signature':wrapper['signature']},selected=selected,expected_group=binary['group'].hex(),expected_context=binary['context'],creator=creator,time=time,trust_policy=trust_policy,configured_endpoint_ordering=json.loads(binary['context'])['ordering']['kind']=='designated-member-v0',stage=stage)
            if json.loads(binary['context'])['ordering']['kind']=='designated-member-v0':self.db.execute("INSERT INTO mls_configured_context VALUES(?,'configured-endpoint-v0')",(joined['group'],))
            result=dict(status='admitted-unverified',group=joined['group'],invitation=v['invitation'],mailbox_verified=False)
            self.db.execute('INSERT INTO application_invitation_acceptance VALUES(?,?,?,?,?)',(allow_creator,v['invitation'],raw,wrapper['signature'],json.dumps(result).encode()))
            if v['version']=='2':self.db.execute('INSERT INTO initial_invitation_proofs VALUES(?,?,?)',(allow_creator,v['invitation'],octets))
            from signed_initial_instances import qualify_signed_initial_locked
            qualify_signed_initial_locked(self.db,self.binary,local_key=target['key'])
            if crash:crash('before-commit')
            self.db.execute('COMMIT')
            if crash:crash('after-commit')
            return result
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
