import base64
import json
import os
import unittest
from pathlib import Path
from event_encoding import serialize_json,encode_event,decode_event,MAX_EVENT_OCTETS
from hosted_reply_admission import template_limit,retain_template,fill_template
from hosted_reply_export import HostedReplyExporter,EXPORT_MAX
import test_hosted_release

class HostedExportTests(unittest.TestCase):
    setUpClass=classmethod(test_hosted_release.HostedReleaseTests.setUpClass.__func__)
    tearDownClass=classmethod(test_hosted_release.HostedReleaseTests.tearDownClass.__func__)
    setUp=test_hosted_release.HostedReleaseTests.setUp
    stop=test_hosted_release.HostedReleaseTests.stop
    def configure_v1(self):
        self.template=serialize_json(dict(version='1',purpose='contribution',event='1'*32,conversation=self.f.configuration['contribution']['conversation'],principal=self.f.store.owner,audience=[self.f.store.owner],disclosures=[],operation=dict(kind='hosted-holder-observation',text='',target=self.f.configuration['contribution'],service=self.f.store.service,attribution='grant-holder')))
        self.limit=template_limit(self.template)
        self.req=dict(self.f.req,version='1',operation='a'*32,grant='b'*32,replyTextLimit=str(self.limit));self.raw=encode_event(self.req)
        self.f.store.configuration=dict(self.f.configuration,replyTextLimit=str(self.limit))
        self.sender.retain(self.raw);retain_template(self.sender,'a'*32,self.template)
        self.assertEqual(self.client.request('a'*32,'management')['http'],200)
        return self.req['grant']
    def reply(self,grant,text='PRIVATE_EXPORTED_REPLY_MARKER'):
        raw=encode_event(dict(version='0',purpose='hosted-holder-reply',operation='9'*32,text=text))
        self.assertEqual(self.f.store.reply(grant,raw,self.f.secret)[0],200)
        return raw
    def test_actual_escaped_boundary_and_no_precommit_receipt(self):
        grant=self.configure_v1();unit='/"\\\n🦀';width=len(serialize_json(unit))-2
        count,remainder=divmod(self.limit-2,width);text=unit*count+'x'*remainder
        self.assertEqual(len(serialize_json(text)),self.limit)
        self.assertEqual(len(fill_template(self.template,text,'c'*32)),MAX_EVENT_OCTETS)
        oversized=encode_event(dict(version='0',purpose='hosted-holder-reply',operation='8'*32,text=text+'x'))
        self.assertEqual(self.f.store.reply(grant,oversized,self.f.secret)[0],413)
        with self.f.store.db() as db:self.assertEqual(db.execute('SELECT count(*) FROM replies').fetchone()[0],0)
        self.reply(grant,text)
        with self.assertRaises(ValueError):fill_template(self.template,text+'x','c'*32)
    def test_real_export_provenance_after_revoke_and_encrypted_wal(self):
        grant=self.configure_v1();raw=self.reply(grant);exporter=HostedReplyExporter(self.client)
        with self.sender.db() as db:db.execute('PRAGMA journal_mode=WAL')
        with self.f.store.db() as db:db.execute('PRAGMA journal_mode=WAL')
        revoke=encode_event(dict(version='0',purpose='hosted-grant-revoke',operation='8'*32,grant=grant))
        self.f.store.manage(revoke,'management','hosted-grant-revoke')
        self.assertEqual(self.f.store.reply_status(grant,'9'*32,self.f.secret)[0],403)
        result=exporter.fetch('a'*32,'9'*32,'management');self.assertEqual(result['state'],'observed')
        with self.sender.db() as db:
            stored=self.sender.vault.get(db,'export:'+result['evidence'],'hosted-reply-export',grant)
        self.assertEqual(base64.urlsafe_b64decode(json.loads(stored)['request']+'=='),raw)
        self.assertEqual(exporter.fetch('a'*32,'9'*32,self.f.secret)['http'],401)
        self.f.store.management_grant['owner']='enp0:'+'d'*64
        self.assertEqual(exporter.fetch('a'*32,'9'*32,'management')['http'],401)
        for path in self.f.root.iterdir():
            if path.is_file():
                data=path.read_bytes();self.assertNotIn(b'PRIVATE_EXPORTED_REPLY_MARKER',data);self.assertNotIn(self.f.secret.encode(),data)
    def test_maximum_exact_request_wrapper_and_longest_origin(self):
        self.f.store.service='https://'+'a'*63+'.'+'b'*63+'.'+'c'*63+'.'+'d'*61+':65535'
        self.f.store.management_grant['service']=self.f.store.service
        self.assertEqual(self.f.create()[0],200)
        raw=encode_event(dict(version='0',purpose='hosted-holder-reply',operation='9'*32,text='x'))
        raw=b' '*(MAX_EVENT_OCTETS-len(raw))+raw
        self.assertEqual(self.f.store.reply('7'*32,raw,self.f.secret)[0],200)
        code,body=self.f.store.export_reply('7'*32,'9'*32,'management');self.assertEqual(code,200)
        self.assertGreater(len(body),MAX_EVENT_OCTETS);self.assertLessEqual(len(body),EXPORT_MAX)
        parsed=decode_event(body,max_octets=EXPORT_MAX)['value']
        self.assertEqual(base64.urlsafe_b64decode(parsed['request']+'=='),raw)
        with self.assertRaises(ValueError):decode_event(body)
    def test_missing_template_and_malformed_export_never_create_authority(self):
        grant=self.configure_v1();self.reply(grant);exporter=HostedReplyExporter(self.client)
        original=self.f.store.export_reply
        def malformed(*args):
            code,body=original(*args);value=json.loads(body);value['receipt']['requestDigest']='f'*64
            return code,serialize_json(value)
        self.f.store.export_reply=malformed
        with self.assertRaises(ValueError):exporter.fetch('a'*32,'9'*32,'management')
        with self.sender.db() as db:self.assertEqual(db.execute('SELECT count(*) FROM hosted_exports').fetchone()[0],0)
        with self.sender.db() as db:db.execute("DELETE FROM vault WHERE purpose='hosted-observer-template'")
        with self.assertRaises(ValueError):self.client.request('a'*32,'management')
    def test_template_is_immutable_and_old_v0_is_not_upgraded(self):
        self.configure_v1();changed=json.loads(self.template);changed['disclosures']=[{'kind':'plaintext-email'}]
        with self.assertRaises(ValueError):retain_template(self.sender,'a'*32,serialize_json(changed))
        self.f.store.configuration=self.f.configuration;self.assertEqual(self.f.create()[0],200)
        self.assertNotIn('replyTextLimit',json.loads(self.f.raw))

    def test_export_crashes_around_atomic_encrypted_provenance(self):
        import subprocess,sys
        self.configure_v1();self.reply('b'*32)
        script="""import os,sys
from vault_fixture import HostedSender
from hosted_management import HostedManagementClient
from hosted_reply_export import HostedReplyExporter
s=HostedSender(sys.argv[1],key=bytes.fromhex(sys.argv[2]),service=sys.argv[3],owner=sys.argv[4])
c=HostedManagementClient(s,ca_file=sys.argv[5],address=('127.0.0.1',int(sys.argv[6])))
HostedReplyExporter(c).fetch('a'*32,'9'*32,'management',crash=lambda point:os._exit(77) if point==sys.argv[7] else None)
"""
        for point,count in [('before-commit',0),('after-commit',1)]:
            result=subprocess.run([sys.executable,'-c',script,self.sender.path,self.f.keys[2].hex(),self.f.store.service,self.f.store.owner,self.client.ca,str(self.server.server_port),point],cwd=Path(__file__).parent)
            self.assertEqual(result.returncode,77)
            with self.sender.db() as db:
                self.assertEqual(db.execute('SELECT count(*) FROM hosted_exports').fetchone()[0],count)
                self.assertEqual(db.execute("SELECT count(*) FROM vault WHERE purpose='hosted-reply-export'").fetchone()[0],count)
    def test_bound_authenticated_different_request_is_conflict(self):
        self.configure_v1();self.reply('b'*32);exporter=HostedReplyExporter(self.client)
        exporter.fetch('a'*32,'9'*32,'management');original=self.f.store.export_reply
        def different(*args):
            import hashlib
            code,body=original(*args);value=json.loads(body)
            raw=encode_event(dict(version='0',purpose='hosted-holder-reply',operation='9'*32,text='Different historical text'))
            value['request']=base64.urlsafe_b64encode(raw).rstrip(b'=').decode();value['receipt']['requestDigest']=hashlib.sha256(raw).hexdigest()
            return code,serialize_json(value)
        self.f.store.export_reply=different
        self.assertEqual(exporter.fetch('a'*32,'9'*32,'management')['state'],'conflict')
        with self.sender.db() as db:self.assertEqual(db.execute("SELECT count(*) FROM hosted_exports WHERE state='conflict'").fetchone()[0],2)

if __name__=='__main__':unittest.main()
