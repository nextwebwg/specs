"""Configured established Welcome admission; predecessor claims are inviter assertions."""
import base64
import hashlib
import json
from pathlib import Path
from provider_control import decode,exact,participant,verify_signature
from passive_discovery import canonical_base64,hexadecimal,uint64,mailbox_syntax
from identity_bundle import decode_identity_bundle
from event_encoding import encode_event
from provider_mls import Admission,call
from passive_discovery_package import validate_package
from mls_receive import LockedIdentity,FORMAT,MlsReceive
import group_instances as instances
import membership_episodes as episodes
import established_support
DOMAIN=b'email-next/mls-established-membership-invitation/v0\0'
FIELDS=set('version purpose invitation profile conversation creator target group previousEpoch epoch previousGroupContextDigest resultGroupContextDigest decision keyPackageRef keyPackageDigest notBefore notAfter context applicationContextDigest members welcome'.split())
def sha(raw):return hashlib.sha256(raw).hexdigest()
def b64(raw):return base64.b64encode(raw).decode()

def parse(octets):
    wrapper=decode(octets,max_bytes=4*1024*1024,max_depth=32)
    raw=canonical_base64(wrapper['payload']);v=decode(raw,max_bytes=2*1024*1024,max_depth=32)
    extra={'applicationAssertions'} if v.get('version') in ('1','2','3','4','5','6','7') else set()
    exact(wrapper,{'payload','signature','identity'}|extra);exact(v,FIELDS|extra|({'genesis','orderingPath'} if v.get('version') in ('6','7') else set()))
    if v['version'] not in ('0','1','2','3','4','5','6','7') or (v['purpose'],v['profile'])!=('mls-established-membership-invitation','mls-1-0001'):raise ValueError('Established profile')
    for field in ('invitation','conversation'):
        if not hexadecimal(v[field],32) or v[field]=='0'*32:raise ValueError('Object ID')
    for who in ('creator','target'):
        exact(v[who],{'principal','device','state','binding'}|({'mailbox'} if who=='target' else set()));participant({k:v[who][k] for k in ('principal','device')})
        if not all(hexadecimal(v[who][k],64) for k in ('state','binding')):raise ValueError('Identity digest')
    if mailbox_syntax(v['target']['mailbox'])!='syntax-valid':raise ValueError('Mailbox syntax')
    for field in ('previousGroupContextDigest','resultGroupContextDigest','decision','keyPackageDigest','applicationContextDigest'):
        if not hexadecimal(v[field],64):raise ValueError('Digest')
    if uint64(v['epoch'])!=uint64(v['previousEpoch'])+1:raise ValueError('Epoch relation')
    if uint64(v['notAfter'])<uint64(v['notBefore']):raise ValueError('Validity order')
    binary={k:canonical_base64(v[k]) for k in ('group','keyPackageRef','context','welcome')}
    if any(not x for x in binary.values()) or len(binary['welcome'])>1048576:raise ValueError('Byte bounds')
    if sha(binary['context'])!=v['applicationContextDigest']:raise ValueError('Application context digest')
    context=decode(binary['context'],max_bytes=1048576,max_depth=32);exact(context,{'version','purpose','conversation','profile','administrators','ordering'}|({'application'} if extra else set())|({'delivery'} if v['version'] in ('4','5','6','7') else set()))
    if (context['version'],context['purpose'],context['conversation'],context['profile'])!=({'0':'1','1':'2','2':'3','3':'4','4':'5','5':'6','6':'7','7':'7'}[v['version']],'conversation-context',v['conversation'],v['profile']):raise ValueError('Context')
    if v['version'] in ('6','7'):
        if not hexadecimal(v['genesis'],64) or not isinstance(v['orderingPath'],list) or not v['orderingPath']:raise ValueError('Quorum ancestry fields')
        from ordering_mls import context_valid
        context_valid(context)
    else:
        exact(context['ordering'],{'kind','principal','device'})
        if context['ordering']!={'kind':'designated-member-v0','principal':v['creator']['principal'],'device':v['creator']['device']}:raise ValueError('Configured creator')
    if not isinstance(context['administrators'],list) or not all(isinstance(a,str) for a in context['administrators']) or context['administrators']!=sorted(set(context['administrators'])) or v['creator']['principal'] not in context['administrators']:raise ValueError('Administrators')
    if not isinstance(v['members'],list) or not v['members']:raise ValueError('Roster')
    pairs=[]
    for member in v['members']:
        exact(member,{'principal','device','signingKey','state','binding'});participant({k:member[k] for k in ('principal','device')})
        if not all(hexadecimal(member[k],64) for k in ('signingKey','state','binding')):raise ValueError('Member digest/key')
        pairs.append((member['principal'],member['device']))
    if pairs!=sorted(set(pairs)) or not set(context['administrators']).issubset({p for p,d in pairs}):raise ValueError('Roster ordering/admin')
    from private_copy import check_roster
    check_roster(context,[p for p,d in pairs])
    if extra:
        from application_payload import selected_format
        selected_format(context,context['application'],configured_ordering=True,configured_quorum_ordering=v['version'] in ('6','7'))
        established_support.proofs(wrapper,v,context)
    if not hexadecimal(wrapper['signature'],128):raise ValueError('Signature')
    bundle=decode_identity_bundle(encode_event(wrapper['identity']))
    if bundle['principal']!=v['creator']['principal']:raise ValueError('Creator bundle')
    return wrapper,raw,v,binary,bundle

class EstablishedAdmission(Admission):
    def __init__(self,identity,binary):
        super().__init__(identity,binary);instances.initialize(self.db);established_support.initialize(self.db)
        self.db.execute('CREATE TABLE IF NOT EXISTS membership_invitation_acceptance(principal TEXT NOT NULL,id TEXT NOT NULL,payload BLOB NOT NULL,signature TEXT NOT NULL,instance TEXT NOT NULL,result BLOB NOT NULL,PRIMARY KEY(principal,id))')
    def accept_message(self,octets,*,target,mailbox,allow_creator,expected_context,time,trust_policy='allow-unverified',crash=None):
        MlsReceive._policy(time,trust_policy);w,raw,v,binary,bundle=parse(octets)
        if not isinstance(expected_context,bytes) or binary['context']!=expected_context:raise ValueError('Independently selected context mismatch')
        if any(v['target'][k]!=target[k] for k in ('principal','device')) or v['target']['mailbox']!=mailbox:raise ValueError('Local target mismatch')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT payload,signature,result FROM membership_invitation_acceptance WHERE principal=? AND id=?',(v['creator']['principal'],v['invitation'])).fetchone()
            if old:
                if old[0]!=raw or old[1]!=w['signature']:raise ValueError('Invitation replay conflict')
                self.db.execute('COMMIT');return json.loads(old[2])
            if v['creator']['principal']!=allow_creator:raise ValueError('Creator not locally authorized')
            candidate=next((b for b in bundle['bindings'] if b['digest']==v['creator']['binding']),None)
            if candidate is None:raise ValueError('Creator binding missing')
            creator_key=candidate['value']['signingKey'];verify_signature(raw,w['signature'],creator_key,('email-next/mls-established-membership-invitation/v'+v['version']).encode()+b'\0')
            if uint64(time['earliest'])<uint64(v['notBefore']) or uint64(time['latest'])>uint64(v['notAfter']):raise ValueError('Invitation validity')
            interval={'earliest':v['notBefore'],'latest':v['notAfter']}
            locked=LockedIdentity(self.identity);expected=[]
            for member in v['members']:
                identity=(b'email-next/device/v0\0'+bytes.fromhex(member['principal'][5:])+bytes.fromhex(member['device'][5:])).hex()
                checked=locked.check_device(bytes.fromhex(identity),bytes.fromhex(member['signingKey']),role='receive',time=interval,trust_policy=trust_policy)
                if checked.get('status')!='authorized-unverified' or checked['head']!=member['state'] or checked['binding']!=member['binding']:raise ValueError('Current member authority')
                expected.append((identity,member['signingKey']))
                for role in ('creator','target'):
                    who=v[role]
                    if (member['principal'],member['device'])==(who['principal'],who['device']) and any(member[k]!=who[k] for k in ('state','binding')):raise ValueError('Named member state')
            creator_identity=(b'email-next/device/v0\0'+bytes.fromhex(v['creator']['principal'][5:])+bytes.fromhex(v['creator']['device'][5:])).hex()
            if (creator_identity,creator_key) not in expected:raise ValueError('Creator outside roster')
            checked=locked.check_device(bytes.fromhex(creator_identity),bytes.fromhex(creator_key),role='send',time=interval,trust_policy=trust_policy)
            if checked.get('status')!='authorized-unverified' or checked['head']!=v['creator']['state'] or checked['binding']!=v['creator']['binding']:raise ValueError('Current creator send authority')
            reference=binary['keyPackageRef'].hex();row=self.db.execute('SELECT device,invitation FROM provider_mls_admission WHERE reference=?',(reference,)).fetchone()
            if not row or row[1] is not None:raise ValueError('Missing/unavailable package')
            device=json.loads(row[0])
            if (device['principal'],device['device'],device['key'])!=(target['principal'],target['device'],target['key']) or (device['identity'],device['key']) not in expected or sha(bytes.fromhex(device['package']))!=v['keyPackageDigest']:raise ValueError('Package target/digest')
            if validate_package(bytes.fromhex(device['package']),principal=device['principal'],device=device['device'],accepted_signing_key=bytes.fromhex(device['key']),earliest=interval['earliest'],latest=interval['latest'],executable=Path(self.binary).with_name('validate-discovery-package'))!={'status':'package-valid'}:raise ValueError('Package validity')
            if v['version'] in ('1','2','3','4','5','6','7'):established_support.current_target(w,v,json.loads(binary['context']),locked,interval,trust_policy,bytes.fromhex(device['package']))
            if v['version'] in ('6','7'):
                from quorum_join import verify_invitation_locked
                genesis_roster=verify_invitation_locked(self.identity,v,binary,time=interval)
            joined=call(self.binary,op='join-embedded',checkpoint=device['checkpoint'],key=device['key'],welcome=binary['welcome'].hex(),reference=reference)
            if (joined['group'],joined['epoch'],joined['context'],joined['signerIdentity'],joined['signerKey'])!=(binary['group'].hex(),v['epoch'],binary['context'].hex(),creator_identity,creator_key) or sorted((m['identity'],m['key']) for m in joined['members'])!=sorted(expected) or sha(bytes.fromhex(joined['groupContext']))!=v['resultGroupContextDigest']:raise ValueError('Authenticated Welcome mismatch')
            # Earlier versions retain inviter-only predecessor assertions. Version6
            # verifies anchored certificates, not historical MLS decryption.
            instance=instances.admission_instance(raw,bytes.fromhex(w['signature']));admission='established:'+sha(raw)
            cp=self.db.execute('SELECT group_id FROM mls_checkpoint WHERE id=1').fetchone()
            if cp:
                if cp[0]!=joined['group']:raise ValueError('Existing other group')
                terminal=self.db.execute('SELECT snapshot FROM mls_group_inactive WHERE group_id=?',(joined['group'],)).fetchone()
                if not terminal or json.loads(terminal[0])['context']!=joined['context']:raise ValueError('Rejoin context/terminal evidence')
                instances.install_rejoin_locked(self.db,joined,payload=raw,signature=bytes.fromhex(w['signature']),admission=admission)
            else:
                if self.db.execute('SELECT 1 FROM mls_group_instances').fetchone():raise ValueError('Ambiguous existing instances')
                self.db.execute('INSERT INTO mls_group_instances VALUES(?,?,?,?,?,NULL)',(instance,joined['group'],admission,'established-invitation','active'))
                self.db.execute('INSERT INTO mls_checkpoint VALUES(1,0,?,?,?)',(FORMAT,joined['group'],json.dumps(joined['checkpoint']).encode()))
                self.db.execute('INSERT INTO mls_checkpoint_instance VALUES(1,?)',(instance,));episodes.install(self.db,joined,admission)
                for m in joined['members']:self.db.execute('INSERT INTO mls_episode_instance VALUES(?,?,?,?,?)',(joined['group'],m['identity'],m['key'],admission,instance))
            if v['version'] in ('1','2','3','4','5','6','7'):established_support.install(self.db,instance,w,v,json.loads(binary['context']))
            if v['version'] in ('6','7'):
                self.db.execute('INSERT INTO mls_quorum_admission VALUES(?,?,?,?,?)',(instance,joined['group'],v['decision'],joined['context'],joined['groupContext']))
                self.db.execute('INSERT INTO qo_genesis VALUES(?,?,?)',(instance,v['genesis'],genesis_roster))
                from quorum_join_support import retain_path_locked
                retain_path_locked(self.db,v['orderingPath'])
            else:self.db.execute("INSERT OR IGNORE INTO mls_configured_context VALUES(?,'configured-endpoint-v0')",(joined['group'],))
            self.db.execute('INSERT INTO mls_instance_schema VALUES(1,1) ON CONFLICT(id) DO UPDATE SET version=1')
            self.db.execute('UPDATE provider_mls_admission SET invitation=?,joined=? WHERE reference=?',(raw,json.dumps(joined).encode(),reference))
            result=dict(instance=instance,group=joined['group'],epoch=joined['epoch'],status='accepted-unverified',historyShared=False)
            self.db.execute('INSERT INTO membership_invitation_acceptance VALUES(?,?,?,?,?,?)',(v['creator']['principal'],v['invitation'],raw,w['signature'],instance,json.dumps(result)))
            if crash:crash('before-commit')
            self.db.execute('COMMIT');return result
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
