"""Actual fixed-suite HPKE plus accepted Ed25519 sender; no owning MLS effects."""
import base64
import copy
import os
import json
import subprocess
from pathlib import Path
import tempfile
import unittest

from event_encoding import encode_event
from archive_set import account_index
from identity_store import IdentityStore
from provider_mls import make_device,advertisement,sign
from mls_mime import package,unpack
from smtp_loopback import roundtrip
from sealed_control import native,key_descriptor,frame,unframe,seal,open_candidate


class SealedControlTests(unittest.TestCase):
    def setUp(self):
        self.provider=Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR'])/'provider-mls';self.binary=self.provider.with_name('sealed-control')
        self.alice=make_device(self.provider,1,2);self.bob=make_device(self.provider,3,4)
        self.now=max(self.alice['time'],self.bob['time']);self.time=dict(earliest=str(self.now),latest=str(self.now))
        self.secret=native(self.binary,op='generate')
        self.descriptor=dict(id=self.secret['id'],publicKey=self.secret['publicKey'],notBefore=str(self.now-1),notAfter=str(self.now+60),receiveUntil=str(self.now+120))
        self.recipient={k:self.bob[k] for k in ('principal','device')}
        self.body=b'{"mailbox":"bob@private.example","sender":"alice@private.example"}'
        self.value=dict(version='0',purpose='sealed-control-intent',record='5'*32,sender={k:self.alice[k] for k in ('principal','device','state','binding')},recipient=self.recipient,key=self.secret['id'],kind='initial-invitation',body=base64.b64encode(self.body).decode(),notBefore=str(self.now),notAfter=str(self.now+30))
        self.bundle=encode_event(advertisement(self.provider,self.alice,'alice@example.org')['identity'])
        self.temp=tempfile.TemporaryDirectory();self.identity=IdentityStore(Path(self.temp.name)/'identity.sqlite');self.identity.observe(self.alice['record'],first_contact_policy='allow-unverified')

    def tearDown(self):self.identity.close();self.temp.cleanup()

    def signed(self,value=None):
        raw=encode_event(self.value if value is None else value)
        signature=bytes.fromhex(sign(self.provider,self.alice,'email2/sealed-control-intent/v0',raw))
        return frame(raw,signature,self.bundle)

    def encrypted(self,plain=None):return seal(self.binary,self.descriptor,self.signed() if plain is None else plain,time=self.time,recipient=self.recipient)

    def opened(self,wire,**changes):
        args=dict(descriptor=self.descriptor,private_key=self.secret['privateKey'],recipient=self.recipient,identity=self.identity,time=self.time,expected_kind='initial-invitation');args.update(changes)
        return open_candidate(self.binary,wire,**args)

    def test_actual_hpke_hides_mailboxes_and_retains_original_signed_body(self):
        plain=self.signed();wire=self.encrypted(plain)
        self.assertEqual(wire[:8],b'EML2CTL0');self.assertNotIn(b'private.example',wire);self.assertNotIn(self.alice['principal'].encode(),wire)
        self.assertEqual(unpack(roundtrip(package(wire))),wire)
        candidate=self.opened(wire)
        self.assertEqual(candidate['status'],'sealed-control-candidate-only');self.assertEqual(candidate['original_body'],self.body)
        self.assertEqual(candidate['original_intent'],unframe(plain)[0])
        self.assertNotEqual(wire,self.encrypted(plain)) # Native fresh encapsulation.

    def test_header_encapsulation_ciphertext_and_framing_tamper_all_fail(self):
        wire=self.encrypted()
        for offset in (0,8,24,56,60,len(wire)-1):
            changed=bytearray(wire);changed[offset]^=1
            with self.subTest(offset=offset),self.assertRaises(ValueError):self.opened(bytes(changed))
        for changed in (wire[:-1],wire+b'x'):
            with self.assertRaises(ValueError):self.opened(changed)

    def test_other_private_key_recipient_or_protocol_kind_cannot_open_as_selected(self):
        wire=self.encrypted();other=native(self.binary,op='generate')
        with self.assertRaises(ValueError):self.opened(wire,private_key=other['privateKey'])
        with self.assertRaises(ValueError):self.opened(wire,recipient={k:self.alice[k] for k in ('principal','device')})
        with self.assertRaises(ValueError):self.opened(wire,expected_kind='stream-control')

    def test_hpke_success_does_not_authenticate_sender_signature(self):
        raw,sig,identity=unframe(self.signed());bad=bytes([sig[0]^1])+sig[1:]
        with self.assertRaises(ValueError):self.opened(self.encrypted(frame(raw,bad,identity)))
        value=copy.deepcopy(self.value);value['body']=base64.b64encode(b'changed original control').decode()
        with self.assertRaises(ValueError):self.opened(self.encrypted(frame(encode_event(value),sig,identity)))

    def test_unknown_identity_is_not_installed_from_encrypted_proof(self):
        unknown=IdentityStore(Path(self.temp.name)/'unknown.sqlite')
        try:
            with self.assertRaisesRegex(ValueError,'accepted sender'):self.opened(self.encrypted(),identity=unknown)
            self.assertIsNone(unknown.current_state(self.alice['principal'])['head'])
        finally:unknown.close()

    def test_late_receiving_does_not_reopen_creation_or_extend_local_deadline(self):
        wire=self.encrypted();late=dict(earliest=str(self.now+61),latest=str(self.now+61))
        self.assertEqual(self.opened(wire,time=late,recipient=self.recipient)['original_body'],self.body)
        with self.assertRaises(ValueError):seal(self.binary,self.descriptor,self.signed(),time=late,recipient=self.recipient)
        with self.assertRaises(ValueError):self.opened(wire,time=dict(earliest=str(self.now+120),latest=str(self.now+121)))

    def test_expired_current_sender_cannot_be_excused_by_old_signed_interval(self):
        descriptor=dict(self.descriptor,receiveUntil=str(self.now+5000))
        wire=seal(self.binary,descriptor,self.signed(),time=self.time,recipient=self.recipient)
        with self.assertRaisesRegex(ValueError,'accepted sender'):self.opened(wire,descriptor=descriptor,time=dict(earliest=str(self.now+3601),latest=str(self.now+3601)))

    def test_producer_checks_independently_selected_recipient_before_encryption(self):
        value=copy.deepcopy(self.value);value['recipient']={k:self.alice[k] for k in ('principal','device')}
        with self.assertRaisesRegex(ValueError,'recipient selection'):self.encrypted(self.signed(value))

    def test_inner_frame_and_unselected_key_are_not_repaired(self):
        plain=self.signed()
        for bad in (plain[:-1],plain+b'x',b'bad'+plain):
            with self.assertRaises(ValueError):unframe(bad)
        with self.assertRaises(ValueError):key_descriptor(dict(self.descriptor,publicKey='0'*64))
        with self.assertRaises(ValueError):seal(self.binary,dict(self.descriptor,id='1'*32),plain,time=self.time,recipient=self.recipient)

    def history_case(self, kind):
        def endpoint(device):
            ref={k:device[k] for k in ('principal','device','state','binding')}
            ref['key']=json.loads(base64.b64decode(device['record']['binding']))['signingKey']
            return ref
        alice,bob=endpoint(self.alice),endpoint(self.bob)
        actor_side='source' if kind in ('history-grant','history-source-cancel') else 'target'
        record_kind='cancel' if kind.endswith('-cancel') else kind.removeprefix('history-')
        value=dict(version='0',purpose='history-transfer-'+record_kind,transfer='a'*32,
                   source=alice if actor_side=='source' else bob,target=bob if actor_side=='source' else alice,
                   notBefore=str(self.now),notAfter=str(self.now+30))
        if record_kind=='request':
            keyfile=Path(self.temp.name)/'history-age-key'
            subprocess.run(['age-keygen','-o',str(keyfile)],capture_output=True,check=True)
            recipient=subprocess.run(['age-keygen','-y',str(keyfile)],capture_output=True,check=True).stdout.strip().decode()
            value.update(recipient=recipient,accounts=[],deliveries=[],receipt='import-result')
        elif record_kind=='grant':
            value.update(request='1'*64,scope=[dict(id='b'*32,principal='',selection='c'*32,mode='all-retained',cutoff='1',entries='0',digest=account_index([]))],
                         archive='d'*32,set='e'*32,verificationKey='2'*64,catalog=dict(sha256='3'*64,size='100'),complete=True)
        elif record_kind=='receipt':value.update(grant='4'*64,catalog='3'*64,result='imported')
        else:value.update(request='1'*64,grant='',by=actor_side)
        return record_kind,value

    def history_intent(self, kind, value):
        record_kind='cancel' if kind.endswith('-cancel') else kind.removeprefix('history-')
        raw=encode_event(value)
        wrapper=encode_event(dict(payload=base64.b64encode(raw).decode(),signature=sign(self.provider,self.alice,'email2/history-transfer/'+record_kind+'/v0',raw)))
        return dict(self.value,kind=kind,body=base64.b64encode(wrapper).decode()),wrapper

    def test_all_five_history_kinds_preserve_original_signed_records_without_admission(self):
        for kind in ['history-request','history-grant','history-receipt','history-source-cancel','history-target-cancel']:
            with self.subTest(kind=kind):
                _,value=self.history_case(kind);intent,wrapper=self.history_intent(kind,value)
                wire=unpack(roundtrip(package(self.encrypted(self.signed(intent)))))
                candidate=self.opened(wire,expected_kind=kind)
                self.assertEqual(candidate['status'],'sealed-control-candidate-only')
                self.assertEqual(candidate['original_body'],wrapper)
                self.assertNotIn(self.alice['principal'].encode(),wire)
                self.assertNotIn(value['transfer'].encode(),wire)
                # Plausible placeholder parent references are only candidates:
                # no grant, archive import or peer trust is installed here.
                self.assertIsNone(self.identity.current_state(self.bob['principal'])['head'])

    def test_history_actor_peer_cancel_interval_and_original_signature_bind_before_sealing(self):
        kind='history-target-cancel';_,value=self.history_case(kind)
        intent,wrapper=self.history_intent(kind,value)
        bad_intents=[dict(intent,recipient={k:self.alice[k] for k in ('principal','device')}),
                     dict(intent,sender=dict(intent['sender'],state='0'*64)),
                     dict(intent,notAfter=str(self.now+31)),dict(intent,kind='history-source-cancel')]
        parsed=json.loads(wrapper);parsed['signature']='0'*128
        bad_intents.append(dict(intent,body=base64.b64encode(encode_event(parsed)).decode()))
        for bad in bad_intents:
            with self.subTest(bad=bad['kind']),self.assertRaises(ValueError):self.encrypted(self.signed(bad))


    def test_signed_inner_history_key_cannot_substitute_for_accepted_outer_actor_key(self):
        kind='history-target-cancel';_,value=self.history_case(kind)
        value['target']['key']=json.loads(base64.b64decode(self.bob['record']['binding']))['signingKey']
        raw=encode_event(value)
        wrapper=encode_event(dict(payload=base64.b64encode(raw).decode(),signature=sign(self.provider,self.bob,'email2/history-transfer/cancel/v0',raw)))
        intent=dict(self.value,kind=kind,body=base64.b64encode(wrapper).decode())
        with self.assertRaisesRegex(ValueError,'original/outer signing key'):self.encrypted(self.signed(intent))



if __name__=='__main__':unittest.main()
