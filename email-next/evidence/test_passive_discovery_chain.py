"""Real package+advertisement+accepted local identity; still no atomic admission."""
import base64
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from event_encoding import encode_event
from identity_store import IdentityStore
from passive_discovery import decode_passive_discovery
from passive_discovery_verify import verify_passive_discovery
from passive_discovery_package import validate_package

class PassiveDiscoveryChainTests(unittest.TestCase):
    def test_real_chain_and_substitution_failures(self):
        directory=Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR'])
        fixture=json.loads(subprocess.run([str(directory/'discovery-chain-fixture')],capture_output=True,check=True).stdout)
        principal='enp0:'+'01'*32
        wrapper={'payload':fixture['assertion'],'signature':fixture['signature'],
                 'identity':{'version':'0','purpose':'identity-bundle','principal':principal,
                             'states':[{'payload':fixture['state'],'signature':fixture['stateProof']}],
                             'bindings':[{'payload':fixture['binding'],'authorization':fixture['authorization'],'possession':fixture['possession']}]}}
        octets=encode_event(wrapper);time={'earliest':fixture['time'],'latest':fixture['time']}
        with tempfile.TemporaryDirectory() as temporary:
            store=IdentityStore(Path(temporary)/'identity.sqlite')
            try:
                record={key:fixture[key] for key in ['binding','state','authorization','possession','stateProof']}
                record['time']=time
                self.assertEqual(store.observe(record,first_contact_policy='allow-unverified')['status'],'pinned-unverified')
                decision=verify_passive_discovery(octets,store,time=time,trust_policy='allow-unverified')
                self.assertEqual(decision['status'],'snapshot-authorized-unverified')
                parsed=decode_passive_discovery(octets)['assertion']
                self.assertEqual(parsed['digest'],decision['assertion'])
                # Resolve the key from the accepted store record, not an unsigned
                # argument or the incoming identity wrapper. Snapshot can go stale.
                stored=store.db.execute('SELECT record FROM claims WHERE principal=? AND digest=?',(principal,decision['head'])).fetchone()
                accepted=json.loads(base64.b64decode(json.loads(stored[0])['binding']))
                args=dict(principal=principal,device=parsed['value']['device'],accepted_signing_key=bytes.fromhex(accepted['signingKey']),earliest=time['earliest'],latest=time['latest'],executable=directory/'validate-discovery-package')
                self.assertEqual(validate_package(parsed['key_package_octets'],**args),{'status':'package-valid'})
                # A different, independently valid package uses a different key.
                substituted=subprocess.run([str(directory/'discovery-package-fixture')],capture_output=True,check=True).stdout
                self.assertEqual(validate_package(substituted,**args)['reason'],'signing-key')
                assertion=json.loads(base64.b64decode(wrapper['payload']))
                assertion['keyPackage']=[base64.b64encode(substituted).decode()]
                wrapper['payload']=base64.b64encode(encode_event(assertion)).decode()
                rejected=verify_passive_discovery(encode_event(wrapper),store,time=time,trust_policy='allow-unverified')
                self.assertEqual(rejected,{'status':'invalid','reason':'assertion-proof'})
                self.assertFalse(decision['mailbox_verified'])
            finally:
                store.close()
