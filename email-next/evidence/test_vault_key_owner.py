import os,sqlite3,tempfile,unittest,subprocess,sys
from pathlib import Path
from unittest.mock import patch
from vault_key_owner import VaultKeyOwner,MAX_INVOCATIONS
from hosted_vault import HostedVault

class WriterOwnerTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.owner=VaultKeyOwner(self.root/'owner');self.key=self.owner.provision(ceiling=2)
 def test_separate_processes_share_budget(self):
  script="from vault_key_owner import VaultKeyOwner;import sys;VaultKeyOwner(sys.argv[1]).reserve(bytes.fromhex(sys.argv[2]))"
  procs=[subprocess.Popen([sys.executable,'-c',script,self.owner.path,self.key.hex()],cwd=Path(__file__).parent,stdout=subprocess.PIPE,stderr=subprocess.PIPE) for _ in range(3)]
  results=[(p.communicate(),p.returncode) for p in procs]
  self.assertEqual(sorted(code for _,code in results),[0,0,1])
 def test_process_death_after_reservation_consumes_allowance(self):
  # Simulate death before ciphertext exists: a committed reservation is not refunded.
  script="from vault_key_owner import VaultKeyOwner;import os,sys;VaultKeyOwner(sys.argv[1]).reserve(bytes.fromhex(sys.argv[2]));os._exit(23)"
  child=subprocess.run([sys.executable,'-c',script,self.owner.path,self.key.hex()],cwd=Path(__file__).parent,capture_output=True,timeout=15)
  self.assertEqual(child.returncode,23,child.stderr)
  reopened=VaultKeyOwner(self.owner.path)
  reopened.reserve(self.key)
  with self.assertRaisesRegex(ValueError,'exhausted'):reopened.reserve(self.key)
 def test_rollback_restart_and_retry(self):
  db=sqlite3.connect(self.root/'app');self.addCleanup(db.close);HostedVault.schema(db);db.commit()
  v=HostedVault(self.key,'a','sender-request','s','o',writer_owner=self.owner)
  db.execute('BEGIN');v.put(db,'first','p','g',b'one');db.rollback()
  v=HostedVault(self.key,'b','sender-request','s','o',writer_owner=VaultKeyOwner(self.owner.path))
  v.put(db,'second','p','g',b'two');db.commit();v.put(db,'second','p','g',b'two')
  with self.assertRaisesRegex(ValueError,'exhausted'):v.put(db,'third','p','g',b'three')
 def test_rng_failure_collision_and_decrypt_only(self):
  with patch('vault_key_owner.secrets.token_bytes',side_effect=OSError('rng')):
   with self.assertRaises(OSError):self.owner.reserve(self.key)
  with patch('vault_key_owner.secrets.token_bytes',return_value=b'a'*12):
   self.owner.reserve(self.key)
   with self.assertRaisesRegex(ValueError,'repeated'):self.owner.reserve(self.key)
  self.owner.retire(self.key)
  with self.assertRaisesRegex(ValueError,'unavailable'):self.owner.reserve(self.key)
 def test_aliases_and_invalid_limits(self):
  alias=self.root/'alias';alias.symlink_to(self.owner.path)
  hard=self.root/'hard';os.link(self.owner.path,hard)
  for p in (self.owner.path,alias,hard):
   with self.assertRaisesRegex(ValueError,'separate'):self.owner.check_application(p)
  for v in (True,-1,1.5,float('nan'),MAX_INVOCATIONS+1):
   with self.assertRaises(ValueError):self.owner.provision(ceiling=v)
 def test_missing_owner_does_not_authorize_old_key(self):
  other=VaultKeyOwner(self.root/'restored-owner')
  with self.assertRaisesRegex(ValueError,'fresh provisioning'):other.reserve(self.key)
  fresh=other.provision();self.assertNotEqual(fresh,self.key);other.reserve(fresh)

 def test_restore_clone_and_explicit_legacy_migration(self):
  import shutil
  key=self.owner.provision(ceiling=5)
  path=self.root/'original';db=sqlite3.connect(path);self.addCleanup(db.close);HostedVault.schema(db);db.commit()
  v=HostedVault(key,'old','sender-request','s','o',writer_owner=self.owner)
  v.put(db,'one','p','g',b'original');db.commit()
  clone=self.root/'clone';shutil.copyfile(path,clone)
  v.put(db,'two','p','g',b'later');db.commit()
  other=sqlite3.connect(clone);self.addCleanup(other.close)
  v.put(other,'three','p','g',b'clone');other.commit()
  legacy=HostedVault(key,'old','sender-request','s','o')
  self.assertEqual(legacy.get(other,'one','p','g'),b'original')
  with self.assertRaisesRegex(ValueError,'owner-required'):legacy.put(other,'four','p','g',b'new')
  replacement=self.owner.provision()
  with self.assertRaisesRegex(ValueError,'application transaction'):legacy.migrate(other,key=replacement,key_id='fresh',writer_owner=self.owner)
  self.assertEqual(legacy.get(other,'one','p','g'),b'original')
  other.execute('BEGIN');new=legacy.migrate(other,key=replacement,key_id='fresh',writer_owner=self.owner);other.rollback()
  self.assertEqual(legacy.get(other,'one','p','g'),b'original')
  other.execute('BEGIN');new=legacy.migrate(other,key=replacement,key_id='fresh',writer_owner=self.owner);other.commit()
  self.assertEqual(new.get(other,'one','p','g'),b'original')
  self.owner.retire(key)
  with self.assertRaisesRegex(ValueError,'unavailable'):v.put(db,'five','p','g',b'held')
