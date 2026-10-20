"""Configured local provider-to-MLS integration, not a public invitation binding.

Secret checkpoints are local only. Welcome/tree JSON is a test transport envelope.
No network invitation authorization is inferred; expected peers/context are local
configured policy. Public ownership, production outbox and restore are excluded.
"""
import base64
import hashlib
import json
from pathlib import Path
from mls_receive import worker_call, LockedIdentity, MlsReceive, FORMAT
from passive_discovery_package import validate_package
from mls_identity import prepare
from event_encoding import encode_event


def call(binary,**request):
    result=worker_call(binary,request)
    if result.get('status')=='worker-rejected':raise ValueError('MLS worker rejected')
    return result


def sign(binary,device,domain,payload):
    return call(binary,op='sign',checkpoint=device['checkpoint'],key=device['key'],domain=domain,payload=payload.hex())['signature']


def make_device(binary,a,d):
    identity=b'email-next/device/v0\0'+bytes([a])*32+bytes([d])*32
    device=call(binary,op='prepare',identity=identity.hex());device['identity']=identity.hex()
    binding,state=prepare(identity.hex(),device['key'],device['time'])
    device['record']={'binding':base64.b64encode(binding).decode(),'state':base64.b64encode(state).decode(),
        'authorization':sign(binary,device,'email-next/device-binding/v0',binding),
        'possession':sign(binary,device,'email-next/device-possession/v0',binding),
        'stateProof':sign(binary,device,'email-next/identity-state/v0',state),
        'time':{'earliest':str(device['time']),'latest':str(device['time'])}}
    device['binding']=hashlib.sha256(binding).hexdigest();device['state']=hashlib.sha256(state).hexdigest()
    device['principal']='enp0:'+identity[21:53].hex();device['device']='end0:'+identity[53:].hex()
    return device


def advertisement(binary,device,mailbox):
    r=device['record'];now=device['time']
    value=dict(version='0',purpose='passive-discovery',record='3'*32,principal=device['principal'],
      device=device['device'],state=device['state'],binding=device['binding'],mailbox=mailbox,
      notBefore=str(now-60),notAfter=str(now+600),features=['mls-1-0001'],
      keyPackage=[base64.b64encode(bytes.fromhex(device['package'])).decode()])
    payload=encode_event(value)
    return {'payload':base64.b64encode(payload).decode(),'signature':sign(binary,device,'email-next/passive-discovery/v0',payload),
      'identity':dict(version='0',purpose='identity-bundle',principal=device['principal'],
       states=[{'payload':r['state'],'signature':r['stateProof']}],
       bindings=[{'payload':r['binding'],'authorization':r['authorization'],'possession':r['possession']}])}


class Admission:
    def __init__(self,identity,binary):
        self.identity=identity;self.db=identity.db;self.binary=binary
        self.receiver=MlsReceive(identity,Path(binary).with_name('receive-staged'))
        self.db.execute('CREATE TABLE IF NOT EXISTS provider_mls_admission(reference TEXT PRIMARY KEY, device BLOB NOT NULL, invitation BLOB, joined BLOB)')
    def publish_local(self,device):
        self.db.execute('INSERT INTO provider_mls_admission VALUES(?,?,NULL,NULL)',(device['reference'],json.dumps(device).encode()))
    def accept(self,reference,invitation,*,peers,expected_group,expected_context,time,crash=None):
        """peers/group/context are independently authorized local test policy."""
        raw=encode_event(invitation)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            joined=self._accept_locked(reference,invitation,peers=peers,expected_group=expected_group,expected_context=expected_context,time=time,trust_policy='allow-unverified',crash=crash)
            self.db.execute('COMMIT')
            if crash:crash('after-commit')
            return joined
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise

    def _accept_locked(self,reference,invitation,*,peers,expected_group,expected_context,time,trust_policy,crash=None):
        """Internal seam; caller owns transaction and any additional proof records."""
        if not self.db.in_transaction:raise ValueError('Caller transaction required')
        if trust_policy not in ('allow-unverified','require-verification'):raise ValueError('Trust policy')
        raw=encode_event(invitation)
        row=self.db.execute('SELECT device,invitation,joined FROM provider_mls_admission WHERE reference=?',(reference,)).fetchone()
        if row is None:raise ValueError('Unknown package')
        if row[1] is not None:
            if row[1]!=raw:raise ValueError('Package consumed')
            return json.loads(row[2])
        device=json.loads(row[0]);locked=LockedIdentity(self.identity)
        for peer in peers:
            decision=locked.check_device(bytes.fromhex(peer['identity']),bytes.fromhex(peer['key']),role='receive',time=time,trust_policy=trust_policy)
            if decision.get('status')!='authorized-unverified' or decision['head']!=peer['state'] or decision['binding']!=peer['binding']:raise ValueError('Current authority')
        checked=validate_package(bytes.fromhex(device['package']),principal=device['principal'],device=device['device'],accepted_signing_key=bytes.fromhex(device['key']),earliest=time['earliest'],latest=time['latest'],executable=Path(self.binary).with_name('validate-discovery-package'))
        if checked!={'status':'package-valid'}:raise ValueError('Package validity')
        if reference!=invitation['reference']:raise ValueError('Package reference')
        joined=call(self.binary,op='join',checkpoint=device['checkpoint'],key=device['key'],welcome=invitation['welcome'],tree=invitation['tree'])
        expected=sorted((p['identity'],p['key']) for p in peers)
        if sorted((p['identity'],p['key']) for p in joined['members'])!=expected or joined['group']!=expected_group or bytes.fromhex(joined['context'])!=expected_context:raise ValueError('Admission policy')
        if crash:crash('before-commit')
        self.db.execute('INSERT INTO mls_checkpoint VALUES(1,0,?,?,?)',(FORMAT,joined['group'],json.dumps(joined['checkpoint']).encode()))
        self.db.execute('UPDATE provider_mls_admission SET invitation=?,joined=? WHERE reference=?',(raw,json.dumps(joined).encode(),reference))
        return joined
