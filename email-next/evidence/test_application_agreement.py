import sqlite3
import tempfile
import unittest
from pathlib import Path
from application_agreement import ApplicationAgreement

class AgreementTests(unittest.TestCase):
    def test_persisted_exact_device_key_profile_and_complete_roster(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'agreement.sqlite';db=sqlite3.connect(path,isolation_level=None);store=ApplicationAgreement(db)
            a={'identity':(b'email-next/device/v0\0'+bytes([1])*64).hex(),'key':'02'*32}
            b={'identity':(b'email-next/device/v0\0'+bytes([3])*64).hex(),'key':'04'*32}
            profile={'envelopeVersion':'1','operations':['answer','message','question']}
            store.configure_device('aa',a['identity'],a['key'],profile)
            self.assertIsNone(store.resolve('aa',[a,b]))
            store.configure_device('aa',b['identity'],b['key'],profile)
            db.close();db=sqlite3.connect(path,isolation_level=None);store=ApplicationAgreement(db)
            self.assertEqual(store.resolve('aa',[a,b]),profile)
            self.assertIsNone(store.resolve('bb',[a,b]))
            self.assertIsNone(store.resolve('aa',[a,{**b,'key':'05'*32}]))
            store.configure_device('aa',b['identity'],b['key'],{'envelopeVersion':'1','operations':['message']})
            self.assertIsNone(store.resolve('aa',[a,b]));db.close()
