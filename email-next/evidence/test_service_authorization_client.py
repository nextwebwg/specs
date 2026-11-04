from vault_fixture import fresh_key
import json,secrets,tempfile,unittest,subprocess,sys
from pathlib import Path
from urllib.parse import urlencode
from event_encoding import encode_event
from service_authorization import SCOPES
from vault_fixture import NativeAuthorization

class NativeClaims(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)/'vault.sqlite';self.key=fresh_key(self.path)
        origin='https://service.example';self.reg=encode_event(dict(version='0',purpose='service-authorization-registration',registration='1'*32,generation='1',issuer=origin,service=origin,clientId='native',authorization=origin+'/authorize',token=origin+'/token',linkChallenge=origin+'/link/challenge',linkComplete=origin+'/link/complete',redirectPath='/mail/oauth/callback',scopes=SCOPES))
        self.client=NativeAuthorization(self.path,self.reg,key=self.key,clock=lambda:100);self.addCleanup(self.client.close)
        self.redirect='http://127.0.0.1:12345/mail/oauth/callback';_,self.attempt=self.client.start(self.redirect)
        self.response=dict(access_token='fixture-access',refresh_token='fixture-refresh',token_type='Bearer',expires_in=60,scope=' '.join(SCOPES))
    def test_scope_set_and_token_response_types(self):
        self.client.accept_tokens(dict(self.response,scope=' '.join(reversed(SCOPES)),token_type='bEaReR'),expected_attempt=self.attempt)
        for changed in [dict(scope=' '.join(SCOPES+SCOPES[:1])),dict(scope=' '.join(SCOPES[:-1])),dict(scope=' '.join(SCOPES+['extra'])),dict(scope='  '.join(SCOPES)),dict(token_type=None),dict(token_type=42),dict(expires_in=True),dict(refresh_token=None)]:
            with self.assertRaisesRegex(ValueError,'Token response'):self.client.accept_tokens(dict(self.response,**changed),expected_attempt=self.attempt)
    def contend(self,refresh):
        if refresh:self.client.accept_tokens(self.response,expected_attempt=self.attempt)
        config=dict(path=str(self.path),registration=self.reg.decode(),key=self.key.hex(),attempt=self.attempt,url=self.redirect+'?'+urlencode(dict(code='one-code',state=self.attempt,iss='https://service.example')),response=self.response,refresh=refresh,calls=str(Path(self.tmp.name)/'calls'))
        script="""import sys,json,time
from vault_fixture import NativeAuthorization
v=json.load(sys.stdin);c=NativeAuthorization(v['path'],v['registration'].encode(),key=bytes.fromhex(v['key']),clock=lambda:100)
def exchange(*args):
 with open(v['calls'],'ab') as f:f.write(b'exchange\\n')
 time.sleep(.2)
 return v['response']
try:
 if v['refresh']:c.refresh(exchange)
 else:c.callback(v['attempt'],v['url'],exchange)
 print('claimed')
except ValueError:print('held')
finally:c.close()
"""
        processes=[subprocess.Popen([sys.executable,'-c',script],cwd=Path(__file__).parent,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for _ in range(2)]
        try:
            for process in processes:process.stdin.write(json.dumps(config));process.stdin.close()
            results=[]
            for process in processes:
                self.assertEqual(process.wait(timeout=15),0);results.append(process.stdout.read().strip());self.assertEqual(process.stderr.read(),'')
            self.assertEqual(sorted(results),['claimed','held']);self.assertEqual(Path(config['calls']).read_bytes(),b'exchange\n')
        finally:
            for process in processes:
                if process.poll() is None:process.kill();process.wait()
                process.stdout.close();process.stderr.close()
    def test_two_processes_claim_one_code_exchange(self):self.contend(False)
    def test_two_processes_claim_one_refresh_exchange(self):self.contend(True)
    def test_new_selection_prevents_late_response_overwrite(self):
        url=self.redirect+'?'+urlencode(dict(code='old',state=self.attempt,iss='https://service.example'))
        def exchange(*args):self.client.start(self.redirect);return self.response
        with self.assertRaisesRegex(ValueError,'Changed account selection'):self.client.callback(self.attempt,url,exchange)
        with self.assertRaisesRegex(ValueError,'Missing'):self.client.get('tokens')

    def test_pending_new_account_cannot_refresh_old_account(self):
        self.client.accept_tokens(self.response,expected_attempt=self.attempt);self.client.start(self.redirect)
        def forbidden(*args):raise AssertionError('No old-account renewal')
        with self.assertRaisesRegex(ValueError,'Refresh held'):self.client.refresh(forbidden)
        with self.assertRaisesRegex(ValueError,'Credential held'):self.client.access_token()

    def test_explicit_restore_writer_migration(self):
        from service_authorization_client import NativeAuthorization as Real
        from vault_key_owner import VaultKeyOwner
        legacy=Real(self.path,self.reg,key=self.key,clock=lambda:100)
        self.addCleanup(legacy.close)
        original=legacy.get(self.attempt)
        with self.assertRaisesRegex(ValueError,'owner-required'):legacy.put('new',{'secret':'held'})
        owner=VaultKeyOwner(Path(self.tmp.name)/'fresh-owner.sqlite');key=owner.provision()
        legacy.migrate_writer(key=key,writer_owner=owner)
        self.assertEqual(legacy.get(self.attempt),original)
        legacy.put('new',{'secret':'accepted'})
        reopened=Real(self.path,self.reg,key=key,clock=lambda:100,writer_owner=owner)
        self.addCleanup(reopened.close)
        self.assertEqual(reopened.get('new'),{'secret':'accepted'})
