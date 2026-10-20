import base64
import hashlib
import json
import os
from pathlib import Path
import unittest
from provider_mls import make_device,advertisement,sign,call
from test_group_transitions import enroll
from event_encoding import encode_event
from passive_discovery import decode_passive_discovery
from initial_roster import parse,anchor,sha

def b64(raw):return base64.b64encode(raw).decode()
class InitialRosterTests(unittest.TestCase):
    def setUp(self):
        self.binary=Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR'])/'provider-mls';self.devices=[];self.bundles={};self.heads={}
        for seed in [1,3,5]:
            first=make_device(self.binary,seed,seed+1);second=make_device(self.binary,seed,seed+10);bundle,head=enroll(self.binary,first,second)
            self.devices.extend([first,second]);self.bundles[first['principal']]=bundle;self.heads[first['principal']]=head
        self.creator=self.devices[0];self.devices.sort(key=lambda d:(d['principal'],d['device']));self.time=str(max(d['time'] for d in self.devices));self.context=dict(version='3',purpose='conversation-context',conversation='2'*32,profile='mls-1-0001',administrators=[self.creator['principal']],application=getattr(self,'application',dict(envelopeVersion='1',payload='mime-contribution-v0',operations=['message'])),ordering=dict(kind='designated-member-v0',principal=self.creator['principal'],device=self.creator['device']))
        if self.context['application']['payload']=='mime-rich-v0':self.context['version']='4'
        self.proofs=[];members=[]
        for i,device in enumerate(self.devices):
            bundle=self.bundles[device['principal']];wrapper=advertisement(self.binary,device,f'device{i}@example.invalid');v=json.loads(base64.b64decode(wrapper['payload']))
            binding=next(b for b in bundle['bindings'] if json.loads(base64.b64decode(b['payload']))['device']==device['device'])
            v.update(version='3' if self.context['version']=='4' else '2',state=self.heads[device['principal']],binding=sha(base64.b64decode(binding['payload'])),applications=[dict(self.context['application'],ordering='designated-member-v0')])
            raw=encode_event(v);wrapper.update(payload=b64(raw),signature=sign(self.binary,device,'email-next/passive-discovery/v'+v['version'],raw),identity=bundle);self.proofs.append(wrapper)
            member=dict(kind='creator' if device is self.creator else 'joiner',principal=device['principal'],device=device['device'],signingKey=device['key'],state=v['state'],binding=v['binding'],assertion=dict(digest=sha(raw),signature=wrapper['signature']))
            if device is not self.creator:member.update(keyPackageRef=b64(bytes.fromhex(device['reference'])),keyPackageDigest=sha(bytes.fromhex(device['package'])))
            members.append(member)
        joiners=[d for d in self.devices if d is not self.creator]
        self.created=call(self.binary,op='create-initial-roster',checkpoint=self.creator['checkpoint'],key=self.creator['key'],identity=self.creator['identity'],context=encode_event(self.context).hex(),packages=[d['package'] for d in joiners])
        self.roster=dict(version='0',purpose='mls-initial-roster',creation='3'*32,profile='mls-1-0001',conversation='2'*32,creator={k:members[self.devices.index(self.creator)][k] for k in ('principal','device','state','binding')},intendedPrincipals=sorted({d['principal'] for d in self.devices}),group=b64(bytes.fromhex(self.created['group'])),epoch='1',context=b64(encode_event(self.context)),applicationContextDigest=sha(encode_event(self.context)),members=members,notBefore=self.time,notAfter=str(int(self.time)+30),welcome=b64(bytes.fromhex(self.created['welcome'])),resultGroupContextDigest=sha(bytes.fromhex(self.created['groupContext'])))
    def wrapper(self,target,*,roster=None):
        roster=self.roster if roster is None else roster;raw=encode_event(roster);sig=sign(self.binary,self.creator,'email-next/mls-initial-roster/v0',raw)
        index=self.devices.index(target);mailbox=json.loads(base64.b64decode(self.proofs[index]['payload']))['mailbox']
        value=dict(version='3',purpose='mls-new-conversation-invitation',invitation=f'{index+1:032x}',creation=roster['creation'],rosterDigest=sha(raw),rosterSignature=sig,creator=roster['creator'],target=dict(principal=target['principal'],device=target['device'],mailbox=mailbox,keyPackageRef=b64(bytes.fromhex(target['reference']))),notBefore=roster['notBefore'],notAfter=roster['notAfter'])
        payload=encode_event(value);return encode_event(dict(payload=b64(payload),signature=sign(self.binary,self.creator,'email-next/mls-new-conversation-invitation/v3',payload),identity=self.bundles[self.creator['principal']],roster=dict(payload=b64(raw),signature=sig),applicationAssertions=self.proofs))
    def test_three_principals_two_devices_each_share_exact_roster_and_targeted_join(self):
        anchors=set()
        for device in self.devices:
            if device is self.creator:continue
            parsed=parse(self.wrapper(device));anchors.add(parsed['anchor'])
            joined=call(self.binary,op='join-initial-roster',checkpoint=device['checkpoint'],key=device['key'],identity=device['identity'],reference=device['reference'],references=parsed['references'],welcome=self.created['welcome'])
            self.assertEqual(joined['groupContext'],self.created['groupContext']);self.assertEqual(sorted((m['identity'],m['key']) for m in joined['members']),sorted((d['identity'],d['key']) for d in self.devices))
        self.assertEqual(len(anchors),1)
    def test_exact_signature_reference_and_anchor_framing(self):
        target=next(d for d in self.devices if d is not self.creator);raw=self.wrapper(target);parsed=parse(raw)
        expected=hashlib.sha256(b'email-next/initial-roster-anchor/v0\0'+len(parsed['roster_raw']).to_bytes(8,'big')+parsed['roster_raw']+(64).to_bytes(8,'big')+bytes.fromhex(parsed['outer']['roster']['signature'])).hexdigest();self.assertEqual(parsed['anchor'],expected)
        changed=json.loads(raw);v=json.loads(base64.b64decode(changed['payload']));v['rosterSignature']='f'*128;changed['payload']=b64(encode_event(v))
        with self.assertRaisesRegex(ValueError,'Exact common roster reference'):parse(encode_event(changed))
        with self.assertRaisesRegex(ValueError,'principal coverage'):parse(self.wrapper(target,roster=dict(self.roster,intendedPrincipals=[self.creator['principal']])))
    def test_wrong_target_and_ambiguous_local_package_provider_reject(self):
        a,b=[d for d in self.devices if d is not self.creator][:2];parsed=parse(self.wrapper(a))
        args=dict(op='join-initial-roster',key=a['key'],identity=a['identity'],references=parsed['references'],welcome=self.created['welcome'])
        with self.assertRaisesRegex(ValueError,'worker rejected'):call(self.binary,checkpoint=a['checkpoint'],reference=b['reference'],**args)
        combined=dict(a['checkpoint']);combined.update(dict(b['checkpoint']))
        with self.assertRaisesRegex(ValueError,'worker rejected'):call(self.binary,checkpoint=sorted(combined.items()),reference=a['reference'],**args)
        self.assertEqual(call(self.binary,checkpoint=a['checkpoint'],reference=a['reference'],**args)['group'],self.created['group'])
    def test_missing_or_extra_secret_reference_rejects_without_consumption(self):
        target=next(d for d in self.devices if d is not self.creator);parsed=parse(self.wrapper(target));args=dict(op='join-initial-roster',checkpoint=target['checkpoint'],key=target['key'],identity=target['identity'],reference=target['reference'],welcome=self.created['welcome'])
        for refs in [parsed['references'][:-1],sorted(parsed['references']+['ff'*32])]:
            with self.assertRaises(ValueError):call(self.binary,references=refs,**args)
        self.assertEqual(call(self.binary,references=parsed['references'],**args)['group'],self.created['group'])
