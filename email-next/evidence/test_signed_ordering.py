import json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from ordering_certificates import *
from ordering_store import VoteStore

class Fixture:
    def __init__(self):
        self.private={str(i):Ed25519PrivateKey.from_private_bytes(bytes([i+1])*32) for i in range(4)}
        self.keys={i:k.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw).hex() for i,k in self.private.items()}
        self.scope='c'*64;self.a='a'*64;self.b='b'*64;self.objects=[]
    def add(self,kind,view,signer,**fields):
        o=sign(unsigned(kind,self.scope,view,signer,**fields),self.private[signer]);self.objects.append(o);return digest(o)
    def proposal(self,view=0,value=None,new=''):
        return self.add('proposal',view,str(view%4),candidate=value or self.a,newView=new)
    def prepared(self,p,view=0):
        votes=[self.add('prepare',view,str(i),proposal=p) for i in range(3)]
        return self.add('prepared',view,'0',proposal=p,prepares=sorted(votes))
    def proof(self,root):return bundle(root,self.objects)
    def verify(self,root):return Proof(self.proof(root),scope=self.scope,keys=self.keys,f=1)

class SignedTests(unittest.TestCase):
    def test_recursive_new_view_and_delayed_decision(self):
        f=Fixture();p=f.proposal();pc=f.prepared(p)
        commits=[f.add('commit',0,str(i),prepared=pc) for i in range(3)]
        # Faulty witness3 withholds evidence; remaining reports carry it.
        reports=[f.add('report',1,str(i),prepared=pc if i!=3 else '') for i in (0,1,3)]
        nv=f.add('new-view',1,'1',reports=sorted(reports))
        p1=f.proposal(1,new=nv);pc1=f.prepared(p1,1)
        self.assertEqual(f.verify(pc1).result['candidate'],f.a)
        decision=f.add('decision',0,'0',prepared=pc,commits=sorted(commits))
        self.assertEqual(f.verify(decision).result['candidate'],f.a)
        bad=f.proposal(1,value=f.b,new=nv)
        with self.assertRaises(ValueError):f.verify(bad)
    def test_signature_domain_scope_and_exact_parser(self):
        f=Fixture();p=f.proposal();raw=f.proof(p)
        for bad in [raw+b' ',raw.replace(b'"root":',b'"root":"x","root":',1)]:
            with self.assertRaises(ValueError):Proof(bad,scope=f.scope,keys=f.keys,f=1)
        with self.assertRaises(ValueError):Proof(raw,scope='d'*64,keys=f.keys,f=1)
        o=f.objects[0];o['signature']=f.private['0'].sign(b'wrong-purpose'+material(o['body'])).hex()
        with self.assertRaises(ValueError):f.verify(digest(o))
    def test_missing_justification_and_recursive_tamper(self):
        f=Fixture();p=f.proposal(1)
        with self.assertRaises(ValueError):f.verify(p)
        f=Fixture();p=f.proposal();pc=f.prepared(p)
        reports=[f.add('report',1,str(i),prepared=pc) for i in range(3)]
        nv=f.add('new-view',1,'1',reports=sorted(reports));p1=f.proposal(1,new=nv)
        f.objects[1]['signature']='0'*128
        with self.assertRaises(ValueError):f.verify(p1)
    def test_duplicate_witness_and_whole_bundle_limit(self):
        f=Fixture();p=f.proposal();vote=f.add('prepare',0,'0',proposal=p)
        pc=f.add('prepared',0,'0',proposal=p,prepares=[vote]*3)
        with self.assertRaises(ValueError):f.verify(pc)
        f=Fixture();p=f.proposal()
        for args in ({'max_bytes':10},{'max_nodes':0},{'max_depth':-1}):
            with self.assertRaises(ValueError):Proof(f.proof(p),scope=f.scope,keys=f.keys,f=1,**args)
    def test_signed_equivocation_and_mixed_commit_votes(self):
        f=Fixture();pa=f.proposal();pb=f.proposal(value=f.b)
        # Coordinator can sign both; no quorum certificate follows from that alone.
        self.assertNotEqual(f.verify(pa).result['candidate'],f.verify(pb).result['candidate'])
        pca=f.prepared(pa);pcb=f.prepared(pb)
        commits=[f.add('commit',0,'0',prepared=pca),f.add('commit',0,'1',prepared=pca),f.add('commit',0,'2',prepared=pcb)]
        d=f.add('decision',0,'0',prepared=pca,commits=sorted(commits))
        with self.assertRaises(ValueError):f.verify(d)
    def test_store_fencing_and_authority_veto(self):
        f=Fixture();p=f.proposal();pc=f.prepared(p)
        with tempfile.TemporaryDirectory() as t:
            store=VoteStore(Path(t)/'votes',scope=f.scope,keys=f.keys,f=1,signer='0',key=f.private['0'],create=True)
            first=store.vote('prepare',f.proof(p),authority=lambda:True)
            self.assertEqual(first,store.vote('prepare',f.proof(p),authority=lambda:True))
            store.vote('commit',f.proof(pc),authority=lambda:True)
            report=decode_event(store.vote('report',target=1,authority=lambda:True))['value']
            self.assertEqual(report['body']['prepared'],pc)
            with self.assertRaises(ValueError):store.vote('prepare',f.proof(p),authority=lambda:False)
            # A previously emitted exact vote is retained evidence, not new authority.
            self.assertEqual(first,store.vote('prepare',f.proof(p),authority=lambda:True))
            with self.assertRaises(ValueError):VoteStore(Path(t)/'lost',scope=f.scope,keys=f.keys,f=1,signer='0',key=f.private['0'])
    def test_signed_omitted_local_prepared_holds(self):
        f=Fixture();p=f.proposal();pc=f.prepared(p)
        with tempfile.TemporaryDirectory() as t:
            store=VoteStore(Path(t)/'votes',scope=f.scope,keys=f.keys,f=1,signer='0',key=f.private['0'],create=True)
            store.vote('prepare',f.proof(p),authority=lambda:True)
            store.vote('commit',f.proof(pc),authority=lambda:True)
            reports=[f.add('report',1,str(i),prepared='') for i in (1,2,3)]
            nv=f.add('new-view',1,'1',reports=sorted(reports));pb=f.proposal(1,value=f.b,new=nv)
            self.assertEqual(f.verify(pb).result['candidate'],f.b)
            with self.assertRaisesRegex(ValueError,'prepared lock'):store.vote('prepare',f.proof(pb),authority=lambda:True)
            self.assertEqual(Proof(store.retained_proof('commit',0),scope=f.scope,keys=f.keys,f=1).root,pc)
            report=decode_event(store.vote('report',target=2,authority=lambda:True))['value']
            self.assertEqual(report['body']['prepared'],pc)

    def test_real_process_crash_boundaries(self):
        f=Fixture();p=f.proposal()
        program='''
import os,sys,json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from ordering_store import VoteStore
cfg=json.loads(Path(sys.argv[1]).read_text())
s=VoteStore(cfg['db'],scope=cfg['scope'],keys=cfg['keys'],f=1,signer='0',key=Ed25519PrivateKey.from_private_bytes(bytes([1])*32))
def crash(point):
 if point==sys.argv[2]:os._exit(23)
out=s.vote('prepare',Path(cfg['proof']).read_bytes(),authority=lambda:True,crash=crash)
sys.stdout.buffer.write(out);sys.stdout.buffer.flush()
if sys.argv[2]=='after-publication':os._exit(24)
'''
        for point in ('before-durable','after-durable','after-publication'):
            with self.subTest(point=point),tempfile.TemporaryDirectory() as t:
                t=Path(t);db=t/'votes'
                VoteStore(db,scope=f.scope,keys=f.keys,f=1,signer='0',key=f.private['0'],create=True)
                (t/'proof').write_bytes(f.proof(p));(t/'config').write_text(json.dumps(dict(db=str(db),scope=f.scope,keys=f.keys,proof=str(t/'proof'))))
                child=subprocess.run([sys.executable,'-c',program,str(t/'config'),point],cwd=Path(__file__).resolve().parent,capture_output=True,check=False)
                self.assertEqual(child.returncode,24 if point=='after-publication' else 23,child.stderr)
                import sqlite3
                from contextlib import closing
                with closing(sqlite3.connect(db)) as conn:self.assertEqual(conn.execute('SELECT count(*) FROM votes').fetchone()[0],0 if point=='before-durable' else 1)
                retry=subprocess.run([sys.executable,'-c',program,str(t/'config'),'none'],cwd=Path(__file__).resolve().parent,capture_output=True,check=True)
                obj=decode_event(retry.stdout)["value"]
                if point=='after-publication':self.assertEqual(child.stdout,retry.stdout)
                self.assertEqual(obj['body']['proposal'],p)
                import sqlite3
                from contextlib import closing
                with closing(sqlite3.connect(db)) as conn:self.assertEqual(conn.execute('SELECT count(*) FROM votes').fetchone()[0],1)

if __name__=='__main__':unittest.main()
