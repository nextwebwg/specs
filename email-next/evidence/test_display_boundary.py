"""Accepted-record adapter fixture only, not context7 application admission."""
import unittest,sqlite3,json,hashlib
from types import SimpleNamespace
from contextlib import closing
from event_encoding import encode_event
from managed_presentation import describe
from private_copy import check_roster
from private_copy_view import describe as private_describe

class DisplayBoundary(unittest.TestCase):
    def test_exact_context7_display_and_private_roles(self):
        a='enp0:'+'1'*64;b='enp0:'+'2'*64;reference={'conversation':'1'*32,'event':'2'*32}
        event={'version':'3','principal':a,'audience':[a,b],'conversation':'1'*32,'disclosures':[], 'presentation':{'subject':'Protected','authoredAt':'0','to':[b],'cc':[]}}
        raw=encode_event(event)
        context={'version':'7','delivery':{'kind':'private-copy-v0','originator':a,'recipient':b}}
        with closing(sqlite3.connect(':memory:')) as db:
            db.execute('CREATE TABLE mls_receives(digest TEXT,application BLOB,evidence TEXT)');db.execute('CREATE TABLE mls_application_acceptance(digest TEXT,state TEXT)')
            db.execute('INSERT INTO mls_receives VALUES(?,?,?)',('carrier',raw,json.dumps({'snapshot':{'context':encode_event(context).hex()}})))
            db.execute('INSERT INTO mls_application_acceptance VALUES(?,?)',(hashlib.sha256(raw).hexdigest(),'accepted'))
            receiver=SimpleNamespace(db=db,journal=SimpleNamespace(snapshot=lambda _: [{'reference':reference,'state':'recorded','octets':[raw]}]))
            result=describe(receiver,reference,carrier='carrier',transport_wire=b'Subject: forged\r\n\r\n')
            self.assertEqual(result['subject'],'Protected');self.assertEqual(result['state'],'authenticated-presentation')
            self.assertEqual(private_describe(receiver,reference,carrier='carrier',local_principal=b)['replyPrincipal'],a)
            with self.assertRaises(ValueError):check_roster(context,[a])
            context['version']='8';db.execute('UPDATE mls_receives SET evidence=?',(json.dumps({'snapshot':{'context':encode_event(context).hex()}}),))
            self.assertEqual(describe(receiver,reference,carrier='carrier',transport_wire=b'\r\n')['state'],'older-profile')
            db.execute("UPDATE mls_application_acceptance SET state='pending'")
            with self.assertRaises(ValueError):describe(receiver,reference,carrier='carrier',transport_wire=b'\r\n')
if __name__=='__main__':unittest.main()
