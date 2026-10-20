"""Exact experimental initial3 common roster codec; no current authority inference."""
import hashlib
import json
from provider_control import decode,exact,participant,verify_signature
from passive_discovery import canonical_base64,hexadecimal,uint64,mailbox_syntax,decode_passive_discovery
from identity_bundle import decode_identity_bundle
from event_encoding import encode_event
from application_support import supports

ROSTER_DOMAIN=b'email-next/mls-initial-roster/v0\0'
INVITATION_DOMAIN=b'email-next/mls-new-conversation-invitation/v3\0'
ANCHOR_DOMAIN=b'email-next/initial-roster-anchor/v0\0'
ROSTER_FIELDS=set('version purpose creation profile conversation creator intendedPrincipals group epoch context applicationContextDigest members notBefore notAfter welcome resultGroupContextDigest'.split())
INVITATION_FIELDS=set('version purpose invitation creation rosterDigest rosterSignature creator target notBefore notAfter'.split())
DEFAULT_LIMITS=dict(max_wrapper=4194304,max_payload=2097152,max_depth=32)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def anchor(raw,signature):
    if not isinstance(raw,bytes) or not isinstance(signature,bytes) or len(signature)!=64:raise ValueError('Anchor input')
    return sha(ANCHOR_DOMAIN+len(raw).to_bytes(8,'big')+raw+len(signature).to_bytes(8,'big')+signature)
def credential(value):return (b'email-next/device/v0\0'+bytes.fromhex(value['principal'][5:])+bytes.fromhex(value['device'][5:])).hex()
def named(value):
    exact(value,{'principal','device','state','binding'});participant({k:value[k] for k in ('principal','device')})
    if any(not hexadecimal(value[k],64) for k in ('state','binding')):raise ValueError('Named binding digest')
def identifier(value):
    if not hexadecimal(value,32) or value=='0'*32:raise ValueError('Object identifier')

def parse(octets,*,limits=None):
    limits=DEFAULT_LIMITS if limits is None else limits
    outer=decode(octets,max_bytes=limits['max_wrapper'],max_depth=limits['max_depth']);exact(outer,{'payload','signature','identity','roster','applicationAssertions'})
    exact(outer['roster'],{'payload','signature'})
    raw=canonical_base64(outer['payload']);roster_raw=canonical_base64(outer['roster']['payload'])
    value=decode(raw,max_bytes=limits['max_payload'],max_depth=limits['max_depth']);roster=decode(roster_raw,max_bytes=limits['max_payload'],max_depth=limits['max_depth'])
    exact(value,INVITATION_FIELDS);exact(roster,ROSTER_FIELDS)
    if value['version'] not in ('3','4','5','6','7') or value['purpose']!='mls-new-conversation-invitation' or (roster['version'],roster['purpose'],roster['profile'],roster['epoch'])!=('4' if value['version']=='7' else '3' if value['version']=='6' else '2' if value['version']=='5' else '1' if value['version']=='4' else '0','mls-initial-roster','mls-1-0001','1'):raise ValueError('Initial roster version/profile')
    for field in ('creation','conversation'):identifier(roster[field])
    identifier(value['invitation'])
    if not all(hexadecimal(x,128) for x in (outer['signature'],outer['roster']['signature'],value['rosterSignature'])):raise ValueError('Signature encoding')
    if value['creation']!=roster['creation'] or value['rosterDigest']!=sha(roster_raw) or value['rosterSignature']!=outer['roster']['signature']:raise ValueError('Exact common roster reference')
    named(roster['creator']);named(value['creator'])
    if value['creator']!=roster['creator']:raise ValueError('Creator mismatch')
    lo,hi=uint64(roster['notBefore']),uint64(roster['notAfter'])
    if hi<lo or (value['notBefore'],value['notAfter'])!=(roster['notBefore'],roster['notAfter']):raise ValueError('Common interval')
    group=canonical_base64(roster['group']);welcome=canonical_base64(roster['welcome']);context_raw=canonical_base64(roster['context'])
    if not group or not welcome or sha(context_raw)!=roster['applicationContextDigest'] or not hexadecimal(roster['resultGroupContextDigest'],64):raise ValueError('Roster byte/digest binding')
    context=decode(context_raw,max_bytes=limits['max_payload'],max_depth=limits['max_depth']);exact(context,{'version','purpose','conversation','profile','administrators','application','ordering'}|({'delivery'} if value['version'] in ('4','5','6','7') else set()))
    if not isinstance(context['application'],dict):raise ValueError('Application object required')
    if context['version'] not in (('7',) if value['version'] in ('6','7') else ('6',) if value['version']=='5' else ('5',) if value['version']=='4' else ('3','4')) or (context['version'] in ('4','5','6','7'))!=(context['application'].get('payload')=='mime-rich-v0') or context['purpose']!='conversation-context' or context['conversation']!=roster['conversation'] or context['profile']!=roster['profile'] or context['administrators']!=[roster['creator']['principal']]:raise ValueError('Initial roster context')
    modes=[{'kind':'fixed-roster-v0'},dict(kind='designated-member-v0',principal=roster['creator']['principal'],device=roster['creator']['device'])]
    if context['version']!='7' and context['ordering'] not in modes:raise ValueError('Initial ordering')
    members=roster['members'];proofs=outer['applicationAssertions']
    if not isinstance(members,list) or len(members)<2 or not isinstance(proofs,list) or len(proofs)!=len(members):raise ValueError('Complete device coverage')
    pairs=[];references=[];decoded=[];creator=None
    for m,proof in zip(members,proofs):
        if not isinstance(m,dict) or m.get('kind') not in ('creator','joiner'):raise ValueError('Member kind')
        exact(m,{'kind','principal','device','signingKey','state','binding','assertion'}|({'keyPackageRef','keyPackageDigest'} if m['kind']=='joiner' else set()))
        named({k:m[k] for k in ('principal','device','state','binding')});pairs.append((m['principal'],m['device']))
        if not hexadecimal(m['signingKey'],64):raise ValueError('Member key')
        exact(m['assertion'],{'digest','signature'})
        d=decode_passive_discovery(encode_event(proof));a=d['assertion'];v=a['value']
        if v['version']!=('7' if value['version']=='7' else '6' if context['version']=='7' else '5' if context['version']=='6' else '4' if context['version']=='5' else '3' if context['version']=='4' else '2') or any(v[k]!=m[k] for k in ('principal','device','state','binding')) or m['assertion']!=dict(digest=a['digest'],signature=d['signature'].hex()):raise ValueError('Exact member proof')
        if not supports(v,context['application'],context['ordering']['kind']):raise ValueError('Exact device tuple support')
        if not uint64(v['notBefore'])<=lo<=hi<=uint64(v['notAfter']):raise ValueError('Assertion interval')
        verify_signature(a['octets'],d['signature'].hex(),m['signingKey'],('email-next/passive-discovery/v'+v['version']).encode()+b'\0')
        binding=next((b for b in d['identity']['bindings'] if b['digest']==m['binding']),None)
        if not binding or binding['value']['signingKey']!=m['signingKey'] or not uint64(binding['value']['notBefore'])<=lo<=hi<=uint64(binding['value']['notAfter']):raise ValueError('Proof binding/interval')
        if m['kind']=='creator':
            if creator is not None or {k:m[k] for k in ('principal','device','state','binding')}!=roster['creator']:raise ValueError('Unique creator')
            creator=m
        else:
            reference=canonical_base64(m['keyPackageRef'])
            if not reference or a['key_package_octets'] is None or sha(a['key_package_octets'])!=m['keyPackageDigest']:raise ValueError('Package proof bytes')
            references.append(reference.hex())
        decoded.append(d)
    if creator is None or pairs!=sorted(set(pairs)) or len(references)!=len(set(references)):raise ValueError('Unique ordered roster')
    principals=sorted({p for p,d in pairs})
    from private_copy import check_roster
    check_roster(context,principals)
    if context.get('delivery',{}).get('kind')=='private-copy-v0' and context['delivery']['originator']!=roster['creator']['principal']:raise ValueError('Private copy originator must create group')
    from application_payload import selected_format
    selected_format(context,context['application'],configured_ordering=True,configured_quorum_ordering=context['version']=='7')
    if context['version']=='7':
        from quorum_admission import check_initial_witnesses
        check_initial_witnesses(context,members)
    if roster['intendedPrincipals']!=principals:raise ValueError('Declared principal coverage')
    target=value['target'];exact(target,{'principal','device','mailbox','keyPackageRef'});participant({k:target[k] for k in ('principal','device')})
    if mailbox_syntax(target['mailbox'])!='syntax-valid':raise ValueError('Target mailbox')
    target_index=next((i for i,m in enumerate(members) if (m['principal'],m['device'])==(target['principal'],target['device'])),None)
    if target_index is None or members[target_index]['kind']!='joiner' or members[target_index]['keyPackageRef']!=target['keyPackageRef'] or decoded[target_index]['assertion']['value']['mailbox']!=target['mailbox']:raise ValueError('Target roster/package/mailbox')
    identity=decode_identity_bundle(encode_event(outer['identity']))
    if identity['principal']!=creator['principal']:raise ValueError('Creator identity bundle')
    verify_signature(roster_raw,outer['roster']['signature'],creator['signingKey'],('email-next/mls-initial-roster/v'+roster['version']).encode()+b'\0')
    verify_signature(raw,outer['signature'],creator['signingKey'],('email-next/mls-new-conversation-invitation/v'+value['version']).encode()+b'\0')
    return dict(outer=outer,value=value,roster=roster,raw=raw,roster_raw=roster_raw,anchor=anchor(roster_raw,bytes.fromhex(outer['roster']['signature'])),context=context,context_raw=context_raw,group=group,welcome=welcome,proofs=decoded,references=sorted(references),target_index=target_index)
