"""New two-device invitation experiment. No established-group admission or ownership proof."""
import base64
import json
from pathlib import Path
from provider_control import decode, exact, participant, verify_signature
from passive_discovery import canonical_base64, hexadecimal, uint64, mailbox_syntax
from identity_bundle import decode_identity_bundle
from event_encoding import encode_event
from provider_mls import Admission, call
from mls_receive import LockedIdentity, FORMAT
from passive_discovery_package import validate_package
DOMAIN=b'email-next/mls-new-conversation-invitation/v0\0'
FIELDS=set('version purpose invitation profile conversation creator target group epoch keyPackageRef notBefore notAfter context welcome'.split())


def parse(octets):
    wrapper=decode(octets,max_bytes=4*1024*1024,max_depth=32)
    exact(wrapper,{'payload','signature','identity'})
    raw=canonical_base64(wrapper['payload']);v=decode(raw,max_bytes=2*1024*1024,max_depth=32)
    exact(v,FIELDS)
    if v['version']!='0' or v['purpose']!='mls-new-conversation-invitation' or v['profile']!='mls-1-0001' or v['epoch']!='1':raise ValueError('Profile')
    for field in ['invitation','conversation']:
        if not hexadecimal(v[field],32) or v[field]=='0'*32:raise ValueError('Object identifier')
    for name in ['creator','target']:
        keys={'principal','device','state','binding'}|({'mailbox'} if name=='target' else set())
        exact(v[name],keys);participant({k:v[name][k] for k in ['principal','device']})
        if not all(hexadecimal(v[name][k],64) for k in ['state','binding']):raise ValueError('Identity digest')
    if v['creator']['principal']==v['target']['principal']:raise ValueError('Distinct accounts required')
    if mailbox_syntax(v['target']['mailbox'])!='syntax-valid':raise ValueError('Mailbox dependency')
    before,after=uint64(v['notBefore']),uint64(v['notAfter'])
    if after<before:raise ValueError('Lifetime')
    binary={k:canonical_base64(v[k]) for k in ['group','keyPackageRef','context','welcome']}
    if any(not b for b in binary.values()) or len(binary['welcome'])>1048576:raise ValueError('Protocol byte bound')
    if not hexadecimal(wrapper['signature'],128):raise ValueError('Signature')
    bundle=decode_identity_bundle(encode_event(wrapper['identity']))
    if bundle['principal']!=v['creator']['principal']:raise ValueError('Identity scope')
    context=decode(binary['context'],max_bytes=1048576,max_depth=32)
    if context!={'version':'0','purpose':'conversation-context','conversation':v['conversation'],'profile':v['profile'],'administrators':[v['creator']['principal']]}:raise ValueError('Context')
    return wrapper,raw,v,binary,bundle


class InvitationAdmission(Admission):
    def __init__(self,identity,binary):
        super().__init__(identity,binary)
        self.db.execute('CREATE TABLE IF NOT EXISTS invitation_acceptance(principal TEXT, id TEXT, payload BLOB NOT NULL, signature TEXT NOT NULL, result BLOB NOT NULL, PRIMARY KEY(principal,id))')
    def accept_message(self,octets,*,target,mailbox,allow_creator,time):
        """allow_creator is local explicit policy principal, never inferred from mail."""
        wrapper,raw,v,binary,bundle=parse(octets)
        for field in ['principal','device']:
            if v['target'][field]!=target[field]:raise ValueError('Target mismatch')
        if v['target']['mailbox']!=mailbox:raise ValueError('Mailbox association')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            previous=self.db.execute('SELECT payload,signature,result FROM invitation_acceptance WHERE principal=? AND id=?',(v['creator']['principal'],v['invitation'])).fetchone()
            if previous and previous[0]==raw and previous[1]==wrapper['signature']:
                self.db.execute('COMMIT');return json.loads(previous[2])
            candidate=next((b for b in bundle['bindings'] if b['digest']==v['creator']['binding']),None)
            if candidate is None:raise ValueError('Missing creator binding')
            key=candidate['value'].get('signingKey')
            verify_signature(raw,wrapper['signature'],key,DOMAIN)
            if v['creator']['principal']!=allow_creator:raise ValueError('Invitation not locally authorized')
            locked=LockedIdentity(self.identity)
            for who,role,keybytes in [(v['creator'],'send',bytes.fromhex(key)),(v['target'],'receive',bytes.fromhex(target['key']))]:
                credential=b'email-next/device/v0\0'+bytes.fromhex(who['principal'][5:])+bytes.fromhex(who['device'][5:])
                decision=locked.check_device(credential,keybytes,role=role,time=time,trust_policy='allow-unverified')
                if decision.get('status')!='authorized-unverified' or decision['head']!=who['state'] or decision['binding']!=who['binding']:raise ValueError('Current identity authority')
            if previous:raise ValueError('Authenticated invitation collision')
            if self.db.execute('SELECT 1 FROM mls_checkpoint').fetchone():raise ValueError('Existing group in single-group store')
            lo,hi=uint64(time['earliest']),uint64(time['latest'])
            if not uint64(v['notBefore'])<=lo<=hi<=uint64(v['notAfter']):raise ValueError('Invitation expired')
            target_binding=json.loads(base64.b64decode(target['record']['binding']))
            if uint64(v['notAfter'])>min(uint64(candidate['value']['notAfter']),uint64(target_binding['notAfter'])):raise ValueError('Binding lifetime')
            reference=binary['keyPackageRef'].hex()
            row=self.db.execute('SELECT device,invitation FROM provider_mls_admission WHERE reference=?',(reference,)).fetchone()
            if row is None or row[1] is not None:raise ValueError('Unknown or consumed package')
            device=json.loads(row[0])
            checked=validate_package(bytes.fromhex(device['package']),principal=target['principal'],device=target['device'],accepted_signing_key=bytes.fromhex(target['key']),earliest=time['earliest'],latest=v['notAfter'],executable=Path(self.binary).with_name('validate-discovery-package'))
            if checked!={'status':'package-valid'}:raise ValueError('Package validity')
            joined=call(self.binary,op='join-embedded',checkpoint=device['checkpoint'],key=device['key'],welcome=binary['welcome'].hex(),reference=reference)
            creator_identity=(b'email-next/device/v0\0'+bytes.fromhex(v['creator']['principal'][5:])+bytes.fromhex(v['creator']['device'][5:])).hex()
            if joined['signerIdentity']!=creator_identity or joined['signerKey']!=key:raise ValueError('Wrong Welcome signer')
            expected=sorted([(creator_identity,key),(target['identity'],target['key'])])
            if sorted((m['identity'],m['key']) for m in joined['members'])!=expected or joined['group']!=binary['group'].hex() or joined['epoch']!='1' or bytes.fromhex(joined['context'])!=binary['context']:raise ValueError('Group binding')
            self.db.execute('INSERT INTO mls_checkpoint VALUES(1,0,?,?,?)',(FORMAT,joined['group'],json.dumps(joined['checkpoint']).encode()))
            pair=encode_event({'payload':wrapper['payload'],'signature':wrapper['signature']})
            self.db.execute('UPDATE provider_mls_admission SET invitation=?,joined=? WHERE reference=?',(pair,json.dumps(joined).encode(),reference))
            result={'status':'admitted-unverified','group':joined['group'],'invitation':v['invitation'],'mailbox_verified':False}
            self.db.execute('INSERT INTO invitation_acceptance VALUES(?,?,?,?,?)',(v['creator']['principal'],v['invitation'],raw,wrapper['signature'],json.dumps(result).encode()))
            self.db.execute('COMMIT');return result
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
