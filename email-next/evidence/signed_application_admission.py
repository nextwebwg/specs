"""Real signed device agreement with atomic local-carrier MLS admission.

The carrier remains provider_mls's test-only invitation, not a new public wire
format. Identity and mailbox association decisions are independently retained.
"""
import base64
import hashlib
import json
import subprocess
from pathlib import Path
from application_agreement import profile
from application_support import supports
from event_encoding import decode_event,encode_event
from mailbox_association_store import MailboxAssociationStore
from passive_discovery import decode_passive_discovery
from passive_discovery_verify import verify_passive_discovery
from provider_mls import Admission
from mls_receive import LockedIdentity
from membership_episodes import install


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()

class SignedApplicationAdmission(Admission):
    def __init__(self,identity,binary):
        super().__init__(identity,binary)
        self.associations=MailboxAssociationStore(identity)
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS application_admissions(reference TEXT PRIMARY KEY,request BLOB NOT NULL,context BLOB NOT NULL,evidence BLOB NOT NULL,result BLOB NOT NULL);
          CREATE TABLE IF NOT EXISTS application_admission_devices(reference TEXT NOT NULL,credential TEXT NOT NULL,evidence BLOB NOT NULL,PRIMARY KEY(reference,credential));
        ''')

    def accept_signed(self,reference,invitation,*,selected,expected_group,expected_context,creator,time,trust_policy,configured_endpoint_ordering=False,crash=None):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            result=self._accept_signed_locked(reference,invitation,selected=selected,expected_group=expected_group,expected_context=expected_context,creator=creator,time=time,trust_policy=trust_policy,configured_endpoint_ordering=configured_endpoint_ordering,crash=crash)
            self.db.execute('COMMIT')
            if crash:crash('after-commit')
            return result
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise

    def _accept_signed_locked(self,reference,invitation,*,selected,expected_group,expected_context,creator,time,trust_policy,configured_endpoint_ordering=False,crash=None,stage=None):
        if not self.db.in_transaction:raise ValueError('Caller transaction required')
        if trust_policy not in ('allow-unverified','require-verification'):raise ValueError('Trust policy')
        context=decode_event(expected_context)['value']
        application=context.get('application');encoded=profile(application)
        if any(op not in ({'answer','message','question','reaction','reaction-withdraw'}|({'attachment-message'} if application.get('payload')=='mime-contribution-v0' else set())) for op in application['operations']):raise ValueError('Unadvertised application operation')
        request_check=dict(context=context,application=application,ordering=configured_endpoint_ordering)
        script="import {validateConversationContext} from './conversation-context.mjs';let s='';for await(const c of process.stdin)s+=c;const v=JSON.parse(s);process.stdout.write(String(['2','3'].includes(v.context.version)&&validateConversationContext(v.context,{configuredApplication:v.application,configuredEndpointOrdering:v.ordering})));"
        checked=subprocess.run(['node','--input-type=module','-e',script],cwd=Path(__file__).parent,input=json.dumps(request_check),capture_output=True,text=True,check=True,timeout=10)
        if checked.stdout!='true':raise ValueError('Selected context')
        if not isinstance(selected,list) or not selected:raise ValueError('Device coverage')
        items=[];seen=set()
        for choice in selected:
            if not isinstance(choice,dict) or set(choice)!={'wrapper','mailbox','generation','digest'}:raise ValueError('Selection shape')
            decoded=decode_passive_discovery(choice['wrapper']);a=decoded['assertion'];v=a['value']
            if v['version']!=('2' if context['version']=='3' else '1') or choice['mailbox']!=v['mailbox'] or choice['digest']!=a['digest']:raise ValueError('Assertion selection')
            credential=(b'email-next/device/v0\0'+bytes.fromhex(v['principal'][5:])+bytes.fromhex(v['device'][5:])).hex()
            if credential in seen:raise ValueError('Duplicate device')
            seen.add(credential)
            mode=context['ordering']['kind']
            if not supports(v,application,mode):raise ValueError('No per-device application intersection')
            items.append((choice,decoded,credential))
        items.sort(key=lambda x:x[2])
        request=canonical(dict(reference=reference,invitation=encode_event(invitation).hex(),group=expected_group,context=expected_context.hex(),creator=creator,trustPolicy=trust_policy,ordering=configured_endpoint_ordering,
            selections=[dict(mailbox=c['mailbox'],generation=c['generation'],payload=d['assertion']['octets'].hex(),signature=d['signature'].hex()) for c,d,_ in items]))
        old=self.db.execute('SELECT request,result FROM application_admissions WHERE reference=?',(reference,)).fetchone()
        if old:
            if old[0]!=request:raise ValueError('Signed admission retry conflict')
            return json.loads(old[1])
        row=self.db.execute('SELECT device,invitation FROM provider_mls_admission WHERE reference=?',(reference,)).fetchone()
        if not row or row[1] is not None:raise ValueError('Unknown or consumed package')
        device=json.loads(row[0]);proofs=[];peers=[]
        for choice,decoded,credential in items:
            decision=verify_passive_discovery(choice['wrapper'],LockedIdentity(self.identity),time=time,trust_policy=trust_policy)
            if decision.get('status')!='snapshot-authorized-unverified':raise ValueError('Signed authority: '+decision.get('status','invalid'))
            a=decoded['assertion'];v=a['value']
            stored=self.db.execute('SELECT assertion,signature,signing_key FROM mailbox_observations WHERE mailbox=? AND digest=?',(choice['mailbox'],choice['digest'])).fetchone()
            if not stored or stored[0]!=a['octets'] or stored[1]!=decoded['signature']:raise ValueError('Retained proof mismatch')
            association=self.associations._current(choice['mailbox'])
            if not association or not association['enabled'] or association['generation']!=choice['generation'] or association['principal']!=v['principal']:raise ValueError('Changed mailbox association')
            eligible=self.associations.eligible_observation_locked(choice['mailbox'],choice['digest'],time)
            if not eligible or eligible['key']!=stored[2].hex():raise ValueError('Ineligible observation')
            if credential==creator:
                authority=LockedIdentity(self.identity).check_device(bytes.fromhex(credential),stored[2],role='send',time=time,trust_policy=trust_policy)
                if authority.get('status')!='authorized-unverified':raise ValueError('Creator send authority')
            if credential==device['identity'] and a['key_package_octets']!=bytes.fromhex(device['package']):raise ValueError('Advertised package mismatch')
            proof=dict(credential=credential,signatureKey=stored[2].hex(),principal=v['principal'],device=v['device'],record=v['record'],assertion=a['octets'].hex(),digest=a['digest'],signature=decoded['signature'].hex(),head=decision['head'],binding=decision['binding'],notBefore=v['notBefore'],notAfter=v['notAfter'],mailbox=choice['mailbox'],generation=association['generation'],decision=association['decisionId'],anchor=association['identityAnchor'],application=application,ordering=mode)
            proofs.append(proof);peers.append(dict(identity=credential,key=stored[2].hex(),state=decision['head'],binding=decision['binding']))
        if creator not in seen or device['identity'] not in seen:raise ValueError('Creator/target coverage')
        if context['ordering']['kind']=='designated-member-v0':
            writer=(b'email-next/device/v0\0'+bytes.fromhex(context['ordering']['principal'][5:])+bytes.fromhex(context['ordering']['device'][5:])).hex()
            if writer not in seen:raise ValueError('Ordering device absent')
        joined=(stage(peers) if stage is not None else self._accept_locked(reference,invitation,peers=peers,expected_group=expected_group,expected_context=expected_context,time=time,trust_policy=trust_policy))
        creator_key=next(p['key'] for p in peers if p['identity']==creator)
        if joined['signerIdentity']!=creator or joined['signerKey']!=creator_key:raise ValueError('Welcome signer')
        for proof in proofs:
            if self.db.execute('SELECT 1 FROM mls_application_agreement WHERE group_id=? AND credential=?',(expected_group,proof['credential'])).fetchone():raise ValueError('Existing agreement')
            self.db.execute('INSERT INTO application_admission_devices VALUES(?,?,?)',(reference,proof['credential'],canonical(proof)))
            self.db.execute('INSERT INTO mls_application_agreement VALUES(?,?,?,?)',(expected_group,proof['credential'],proof['signatureKey'],encoded))
            self.db.execute("INSERT INTO mls_application_agreement_provenance VALUES(?,?,'signed-admission',?)",(expected_group,proof['credential'],reference))
        install(self.db,joined,'signed-application:'+reference)
        self.db.execute('INSERT INTO application_admissions VALUES(?,?,?,?,?)',(reference,request,expected_context,canonical(dict(time=time,devices=proofs)),canonical(joined)))
        if crash:crash('before-commit')
        return joined
