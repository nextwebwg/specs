"""Real QR-approved enrollment -> signed request -> age -> durable private stage.

No contact-store activation, provider login, or complete send-ready claim.
"""
import base64
import copy
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from event_encoding import encode_event
from pairing_setup import SetupTransfer,unpack,sha,b64,configuration
from provider_mls import make_device,sign
import test_remote_pairing as pairing_tests


class PairingSetupTests(unittest.TestCase):
    tearDown=pairing_tests.RemotePairing.tearDown
    request=pairing_tests.RemotePairing.request
    commit=pairing_tests.RemotePairing.commit
    pair=pairing_tests.RemotePairing.pair
    def setUp(self):
        pairing_tests.RemotePairing.setUp(self);self.pair()
        self.source=SetupTransfer(self.old,self.a,self.binary,age='/opt/homebrew/bin/age',staging_parent=self.root)
        self.target=SetupTransfer(self.new,self.b,self.binary,age='/opt/homebrew/bin/age',staging_parent=self.root)
        self.key=self.root/'setup-key'
        subprocess.run(['/opt/homebrew/bin/age-keygen','-o',str(self.key)],capture_output=True,check=True)
        self.recipient=subprocess.run(['/opt/homebrew/bin/age-keygen','-y',str(self.key)],capture_output=True,check=True).stdout.strip().decode()
        self.transfer='a'*32;now=self.time['latest']
        self.wire=self.target.request(self.transfer,self.session,self.recipient,not_before=now,not_after=str(int(now)+30),time=self.time)
        peer=make_device(self.binary,4,5);record=peer['record'];anchor=sha(base64.b64decode(record['state']))
        public=dict(version='0',purpose='identity-bundle',principal=peer['principal'],states=[dict(payload=record['state'],signature=record['stateProof'])],bindings=[dict(payload=record['binding'],authorization=record['authorization'],possession=record['possession'])])
        self.preferences=dict(trust='allow-unverified',ordinary=False,hosted=False,freshness='cached-continuity',maximumAge='',maximumUncertainty='')
        self.selected=dict(contacts=[dict(mailbox='friend@example.invalid',principal=peer['principal'],anchor=anchor,head=anchor,bundle=b64(encode_event(public)),generation='2',enabled=True,verification=[],policy=self.preferences)],defaults=self.preferences)

    def row(self,which):
        return which.db.execute('SELECT request,response,configuration,receipt,cancelled FROM pairing_setup WHERE account=? AND transfer=?',('local-account',self.transfer)).fetchone()
    def release(self,**kwargs):return self.source.release(self.wire,self.selected,time=self.time,**kwargs)
    def resign(self,value,kind='response',device=None):
        raw=encode_event(value)
        return encode_event(dict(payload=b64(raw),signature=sign(self.binary,device or self.a,'email2/pairing-setup/'+kind+'/v0',raw)))
    def revoke_target(self):
        bundle=copy.deepcopy(self.bundle);state=json.loads(base64.b64decode(bundle['states'][0]['payload']))
        state.update(record='9'*32,revision=str(int(state['revision'])+1),previous=[self.head],revoked=[self.b['device']],bindings=[x for x in state['bindings'] if x['device']!=self.b['device']])
        raw=encode_event(state);bundle['states'].insert(0,dict(payload=b64(raw),signature=sign(self.binary,self.a,'email-next/identity-state/v0',raw)))
        for store in self.stores:
            self.assertEqual(store.accept_successor(encode_event(bundle),candidate_digest=sha(raw),time=self.time)['status'],'accepted-unverified')

    def test_real_confidential_transfer_is_only_staged_and_retries_are_identical(self):
        response=self.release();self.assertNotIn(b'friend@example.invalid',response)
        self.assertEqual(self.release(),response)
        receipt=self.target.stage(response,self.key,time=self.time)
        self.assertEqual(unpack(receipt,'receipt')[1]['result'],'staged')
        self.key.unlink()  # Transfer secret may retire once authenticated staging commits.
        self.assertEqual(self.target.stage(response,self.key,time=self.time),receipt)
        self.assertEqual(json.loads(self.row(self.target)[2]),self.selected)
        self.assertEqual(self.stores[1].db.execute('SELECT count(*) FROM pins').fetchone()[0],1)
        self.assertEqual(list(self.root.glob('.pairing-setup-*')),[])
        self.assertNotIn(b'AGE-SECRET-KEY',response)

    def test_request_is_bound_to_exact_pairing_and_new_device(self):
        _,request,_,_=unpack(self.wire,'request')
        for field in ['session','pairingResult']:
            changed=dict(request);changed[field]='0'*64
            with self.assertRaises(ValueError):self.source.release(self.resign(changed,'request',self.b),self.selected,time=self.time)
        changed=copy.deepcopy(request);changed['target']['device']=self.a['device']
        with self.assertRaises(ValueError):self.source.release(self.resign(changed,'request',self.b),self.selected,time=self.time)
        self.assertIsNone(self.row(self.source))

    def test_wrong_signature_purpose_and_ciphertext_do_not_install_or_poison(self):
        response=self.release();_,value,_,_=unpack(response,'response')
        bad=self.resign(value,'receipt')
        with self.assertRaises(ValueError):self.target.stage(bad,self.key,time=self.time)
        altered=dict(value);data=bytearray(base64.b64decode(value['ciphertext']));data[-1]^=1;altered['ciphertext']=b64(bytes(data))
        with self.assertRaises(ValueError):self.target.stage(self.resign(altered),self.key,time=self.time)
        self.assertIsNone(self.row(self.target)[2]);self.target.stage(response,self.key,time=self.time)

    def test_authenticated_changed_response_and_snapshot_conflict(self):
        response=self.release();self.target.stage(response,self.key,time=self.time)
        changed=copy.deepcopy(self.selected);changed['defaults']=dict(self.preferences,ordinary=True)
        with self.assertRaises(ValueError):self.source.release(self.wire,changed,time=self.time)
        _,value,_,_=unpack(response,'response');value['ciphertext']=b64(base64.b64decode(value['ciphertext'])+b'\0')
        with self.assertRaises(ValueError):self.target.stage(self.resign(value),self.key,time=self.time)
        self.assertEqual(json.loads(self.row(self.target)[2]),self.selected)
        self.assertEqual(self.stores[1].db.execute('SELECT count(*) FROM pairing_setup_conflicts').fetchone()[0],2)
        with self.assertRaises(ValueError):self.target.stage(response,self.key,time=self.time)

    def test_crash_before_source_and_target_commit_is_atomic(self):
        def fail(_):raise RuntimeError('crash')
        with self.assertRaises(RuntimeError):self.release(crash=fail)
        self.assertIsNone(self.row(self.source))
        response=self.release()
        with self.assertRaises(RuntimeError):self.target.stage(response,self.key,time=self.time,crash=fail)
        self.assertIsNone(self.row(self.target)[2]);self.assertIsNone(self.row(self.target)[3])
        self.target.stage(response,self.key,time=self.time)

    def test_revocation_blocks_release_and_acceptance(self):
        response=self.release();self.revoke_target()
        with self.assertRaises(ValueError):self.release()
        with self.assertRaises(ValueError):self.target.stage(response,self.key,time=self.time)
        self.assertIsNone(self.row(self.target)[2])

    def test_deadline_and_local_cancellation_do_not_reset(self):
        response=self.release();later=dict.fromkeys(('earliest','latest'),str(int(self.time['latest'])+31))
        with self.assertRaises(ValueError):self.target.stage(response,self.key,time=later)
        self.target.cancel(self.transfer)
        with self.assertRaises(ValueError):self.target.stage(response,self.key,time=self.time)
        with self.assertRaises(ValueError):self.target.request(self.transfer,self.session,self.recipient,not_before=self.time['latest'],not_after=str(int(self.time['latest'])+60),time=self.time)
        self.assertIsNone(self.row(self.target)[2])

    def test_private_keys_history_and_unknown_preferences_are_not_schema_members(self):
        for field in ['messages','checkpoint','privateKey','accessToken']:
            changed=dict(self.selected);changed[field]='do not transfer'
            with self.assertRaises(ValueError):self.source.release(self.wire,changed,time=self.time)
        changed=copy.deepcopy(self.selected);changed['defaults']['unrecognized']=True
        with self.assertRaises(ValueError):configuration(changed)
        self.assertIsNone(self.row(self.source))

    def test_verification_scope_dates_and_withdrawal_are_not_upgraded(self):
        c=self.selected['contacts'][0]
        c['verification']=[dict(id='b'*32,originDevice=self.a['device'],mechanism='human-comparison-v0',anchor=c['anchor'],notBefore=self.time['earliest'],notAfter=self.time['latest'],continuity='anchor-only',status='withdrawn',revision='3')]
        response=self.release();self.target.stage(response,self.key,time=self.time)
        self.assertEqual(json.loads(self.row(self.target)[2])['contacts'][0]['verification'],c['verification'])
        self.assertEqual(self.stores[1].db.execute("SELECT count(*) FROM sqlite_master WHERE name='human_verification_evidence'").fetchone()[0],0)

    def test_time_spent_encrypting_or_decrypting_cannot_extend_the_original_deadline(self):
        with patch('pairing_setup.monotonic_ns',side_effect=[0,31000000000]):
            with self.assertRaises(ValueError):self.release()
        self.assertIsNone(self.row(self.source))
        response=self.release()
        with patch('pairing_setup.monotonic_ns',side_effect=[0,31000000000]):
            with self.assertRaises(ValueError):self.target.stage(response,self.key,time=self.time)
        self.assertIsNone(self.row(self.target)[2]);self.assertIsNone(self.row(self.target)[3])

    def test_wrong_native_identity_cannot_unlock_and_plugins_are_not_executed(self):
        response=self.release();other=self.root/'wrong-key'
        subprocess.run(['/opt/homebrew/bin/age-keygen','-o',str(other)],capture_output=True,check=True)
        with self.assertRaises(ValueError):self.target.stage(response,other,time=self.time)
        other.write_text('AGE-PLUGIN-FAKE-1SECRET\n')
        with self.assertRaises(ValueError):self.target.stage(response,other,time=self.time)
        self.assertIsNone(self.row(self.target)[2])

    def test_reopen_preserves_exact_outbox_and_staging_receipt(self):
        response=self.release();receipt=self.target.stage(response,self.key,time=self.time)
        # Reopen real stores rather than reconstructing accepted state from mail.
        from identity_store import IdentityStore
        from remote_pairing import Pairing
        for i,path,device in [(0,self.root/'0.sqlite',self.a),(1,self.root/'unpaired.sqlite',self.b)]:
            self.stores[i].close();self.stores[i]=IdentityStore(path)
            transfer=SetupTransfer(Pairing(self.stores[i],account='local-account'),device,self.binary,age='/opt/homebrew/bin/age',staging_parent=self.root)
            if i==0:self.assertEqual(transfer.release(self.wire,self.selected,time=self.time),response)
            else:self.assertEqual(transfer.stage(response,self.key,time=self.time),receipt)

if __name__=='__main__':unittest.main()
