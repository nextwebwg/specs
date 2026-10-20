import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
import unicode17_provider as implementation
from unicode17_provider import ICU17,isolated_idna,ProviderError
from idna17_acceptance import validate_domain
CONFIG=os.environ.get('EMAIL_NEXT_IDNA17_TEST_CONFIG')
@unittest.skipUnless(CONFIG,'Explicit ICU17 test deployment configuration required')
class IDNA17Tests(unittest.TestCase):
 def setUp(self):
  self.cfg=json.loads(Path(CONFIG).read_text());self.env=patch.dict(os.environ,{'EMAIL_NEXT_IDNA17_CONFIG':CONFIG});self.env.start();self.addCleanup(self.env.stop)
 def test_real_consumers(self):
  from passive_discovery import mailbox_syntax
  from service_tls import validate_reference_host
  self.assertEqual(mailbox_syntax('Case.Sensitive@xn--bcher-kva.example'),'syntax-valid')
  self.assertEqual(validate_reference_host('xn--bcher-kva.example'),'xn--bcher-kva.example')
 def test_real_signed_alabel_remains_unverified_identity(self):
  import subprocess
  from identity_store import IdentityStore
  from event_encoding import encode_event
  from passive_discovery_verify import verify_passive_discovery
  fixture=json.loads(subprocess.run(['node',str(Path(__file__).with_name('make-passive-discovery-fixture.mjs'))],capture_output=True,text=True,check=True).stdout)
  with tempfile.TemporaryDirectory() as td:
   store=IdentityStore(Path(td)/'identity.sqlite')
   try:
    store.observe(fixture['genesis'],first_contact_policy='allow-unverified')
    result=verify_passive_discovery(encode_event(fixture['validAlabel']),store,time={'earliest':'20','latest':'21'},trust_policy='allow-unverified')
    self.assertEqual(result['status'],'snapshot-authorized-unverified');self.assertFalse(result['mailbox_verified']);self.assertFalse(result['mls_validated'])
   finally:store.close()
 def test_wrong_library_version(self):
  real=ctypes.CDLL(self.cfg['library'])
  class Proxy:
   def __getattr__(self,name):
    if name=='u_getUnicodeVersion_78':
     def wrong(a):a[0]=16
     return wrong
    return getattr(real,name)
  with patch.object(implementation.C,'CDLL',return_value=Proxy()),self.assertRaisesRegex(ProviderError,'version mismatch'):ICU17(self.cfg)
 def test_byte_order_guard(self):
  with patch.object(implementation.sys,'byteorder','big' if sys.byteorder=='little' else 'little'),self.assertRaisesRegex(ProviderError,'byte order'):ICU17(self.cfg)
 def test_library_must_be_in_hash_set(self):
  cfg=dict(self.cfg,libraries={})
  with self.assertRaisesRegex(ProviderError,'hash-pinned'):ICU17(cfg)
 def test_wrong_table_and_cleanup(self):
  before=set(sys.modules)
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);shutil.copytree(Path(self.cfg['idna_root'])/'idna',root/'idna',ignore=shutil.ignore_patterns('__pycache__'))
   f=root/'idna/idnadata.py';f.write_text(f.read_text().replace('__version__ = "17.0.0"','__version__ = "16.0.0"'))
   cfg=dict(self.cfg,idna_root=str(root),idna_files={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'idna').glob('*.py')})
   with self.assertRaisesRegex(ProviderError,'data version'):isolated_idna(ICU17(cfg),cfg)
  self.assertEqual([x for x in set(sys.modules)-before if x.startswith('_email_next_private_idna17_')],[])
 def test_utf16_supplementary(self):
  u=ICU17(self.cfg);self.assertEqual(u.normalize('NFC','x\U0001e6c0'), 'x\U0001e6c0');self.assertEqual(u.casefold('ß'),'ss')
 def test_malformed_punycode(self):
  for label in ['xn--','xn--a','xn--abc-','xn--0','xn--zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz','xn--a-ecp','xn--ib9b']:
   with self.subTest(label=label),self.assertRaises((UnicodeError,ValueError)):validate_domain(label+'.example')
 def test_domain_bidi(self):
  rtl='xn--'+ 'אב'.encode('punycode').decode();self.assertTrue(validate_domain('abc.'+rtl))
  with self.assertRaises(UnicodeError):validate_domain('1abc.'+rtl)
 def test_no_mapping_or_normalization(self):
  for domain in ['EXAMPLE.com','a。com','xn--'+ 'e\u0301'.encode('punycode').decode()+'.com']:
   with self.assertRaises((UnicodeError,ValueError)):validate_domain(domain)
if __name__=='__main__':unittest.main()
