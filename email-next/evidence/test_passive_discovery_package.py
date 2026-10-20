"""Real Rust fixture -> Python adapter -> bounded Rust validation; no enrollment."""
import os
from pathlib import Path
import subprocess
import unittest
from passive_discovery_package import validate_package

class PackageAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory=os.environ.get('EMAIL_NEXT_MLS_BIN_DIR')
        if not directory:raise RuntimeError('Set EMAIL_NEXT_MLS_BIN_DIR to the existing Cargo debug directory')
        cls.validator=Path(directory)/'validate-discovery-package'
        fixture=subprocess.run([str(Path(directory)/'discovery-package-fixture')],capture_output=True,check=True)
        cls.package=fixture.stdout
        key,time=fixture.stderr.decode().splitlines()
        cls.key=bytes.fromhex(key);cls.time=time
    def call(self,data=None,**changes):
        args=dict(principal='enp0:'+'01'*32,device='end0:'+'02'*32,accepted_signing_key=self.key,
                  earliest=self.time,latest=self.time,executable=self.validator)
        args.update(changes)
        return validate_package(self.package if data is None else data,**args)
    def test_actual_package_end_to_end(self):
        self.assertEqual(self.call(),{'status':'package-valid'})
    def test_tamper_trailing_wrong_identity_key_and_time(self):
        for data in [self.package+b'\0',self.package[:-1]+bytes([self.package[-1]^1]),b'not MLS']:
            self.assertEqual(self.call(data)['status'],'rejected')
        self.assertEqual(self.call(device='end0:'+'03'*32)['reason'],'credential-identity')
        self.assertEqual(self.call(accepted_signing_key=b'\x09'*32)['reason'],'signing-key')
        self.assertEqual(self.call(latest=str(int(self.time)+1000))['reason'],'lifetime-interval')
    def test_size_bound_in_adapter_and_direct_cli(self):
        large=b'0'*1048577
        self.assertEqual(self.call(large),{'status':'rejected','reason':'size'})
        result=subprocess.run([str(self.validator),'01'*32,'02'*32,self.key.hex(),self.time,self.time],input=large,capture_output=True)
        self.assertEqual(result.returncode,1);self.assertIn(b'"size"',result.stdout)
    def test_canonical_arguments(self):
        with self.assertRaises(ValueError):self.call(earliest='01')
        result=subprocess.run([str(self.validator),'01'*32,'02'*32,self.key.hex(),'01',self.time],input=self.package,capture_output=True)
        self.assertEqual(result.returncode,1);self.assertIn(b'argument-time',result.stdout)
