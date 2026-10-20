from unicode17_provider import HERE, ICU17,isolated_idna
from pathlib import Path
import json,time,hashlib
W=Path(__import__('os').environ['EMAIL_NEXT_UCD17_DIRECTORY'])
cfg=__import__('json').loads(Path(__import__('os').environ['EMAIL_NEXT_IDNA17_CONFIG']).read_text());u=ICU17(cfg);core,data=isolated_idna(u,cfg);start=time.monotonic();counts={}
for name,digest in json.loads(Path(__file__).with_name('ucd17-source-hashes.json').read_text()).items():
 assert hashlib.sha256((W/name).read_bytes()).hexdigest()==digest,('Source hash',name)
def rows(file):
 for l in (W/file).read_text().split('\n'):
  l=l.split('#')[0].strip()
  if l and not l.startswith('@'):yield [x.strip() for x in l.split(';')]
def seq(x):return ''.join(chr(int(c,16)) for c in x.split())
n=0
for r in rows('NormalizationTest.txt'):
 c=list(map(seq,r[:5]));n+=1
 for form,expected in [('NFC',[c[1]]*3+[c[3]]*2),('NFD',[c[2]]*3+[c[4]]*2),('NFKC',[c[3]]*5),('NFKD',[c[4]]*5)]:
  for x,y in zip(c,expected):assert u.normalize(form,x)==y,(form,n)
counts['normalization_rows']=n;print(counts,flush=True)
fold={int(r[0],16):seq(r[2]) for r in rows('CaseFolding.txt') if r[1] in ('C','F')}
for cp in range(0x110000):
 if 0xD800<=cp<=0xDFFF:continue
 assert u.casefold(chr(cp))==fold.get(cp,chr(cp)),('casefold',hex(cp))
counts['casefold_scalars']=0x110000-2048;print(counts,flush=True)
# Independent RFC5892 category derivation from pinned UCD; no production copy.
def sets(file):
 d={}
 for r in rows(file):
  a=r[0].split('..');lo=int(a[0],16);hi=int(a[-1],16);d.setdefault(r[1],set()).update(range(lo,hi+1))
 return d
props=sets('PropList.txt');derived=sets('DerivedCoreProperties.txt');blocks=sets('Blocks.txt');hangul=sets('HangulSyllableType.txt');scripts=sets('Scripts.txt');joining=sets('extracted/DerivedJoiningType.txt')
exceptions={}
for value,cps in [('PVALID',[0xDF,0x3C2,0x6FD,0x6FE,0xF0B,0x3007]),('CONTEXTO',[0xB7,0x375,0x5F3,0x5F4,0x30FB,*range(0x660,0x66A),*range(0x6F0,0x6FA)]),('DISALLOWED',[0x640,0x7FA,0x302E,0x302F,0x3031,0x3032,0x3033,0x3034,0x3035,0x303B])]:
 for cp in cps:exceptions[cp]=value
ignblocks=set().union(*(blocks[x] for x in ['Combining Diacritical Marks for Symbols','Musical Symbols','Ancient Greek Musical Notation']))
oldhangul=set().union(*(hangul.get(x,set()) for x in ['L','V','T']))
ig=derived['Default_Ignorable_Code_Point']|props['White_Space']|props['Noncharacter_Code_Point']
# Build direct general-category/ccc data including First/Last ranges.
gc=['Cn']*0x110000;ccc=bytearray(0x110000);pending=None
for r in rows('UnicodeData.txt'):
 cp=int(r[0],16)
 if r[1].endswith(', First>'):pending=cp;continue
 lo=pending if r[1].endswith(', Last>') else cp;pending=None
 for x in range(lo,cp+1):gc[x]=r[2];ccc[x]=int(r[3])
for cp in range(0x110000):
 if 0xD800<=cp<=0xDFFF:continue
 c=chr(cp);assert u.category(c)==gc[cp],('gc',hex(cp));assert u.combining(c)==ccc[cp],('ccc',hex(cp))
 if cp in exceptions:v=exceptions[cp]
 elif gc[cp]=='Cn' and cp not in props['Noncharacter_Code_Point']:v='UNASSIGNED'
 elif cp in range(0x61,0x7B) or cp in range(0x30,0x3A) or cp==0x2D:v='PVALID'
 elif cp in props['Join_Control']:v='CONTEXTJ'
 elif u.normalize('NFKC',u.casefold(u.normalize('NFKC',c)))!=c:v='DISALLOWED'
 elif cp in ig or cp in ignblocks or cp in oldhangul:v='DISALLOWED'
 elif gc[cp] in ('Ll','Lu','Lo','Nd','Lm','Mn','Mc'):v='PVALID'
 else:v='DISALLOWED'
 actual=next((k for k,ran in data.codepoint_classes.items() if core.intranges_contain(cp,ran)),'DISALLOWED')
 assert actual==(v if v!='UNASSIGNED' else 'DISALLOWED'),('idna',hex(cp),v,actual)
 for script,ran in data.scripts.items():assert core.intranges_contain(cp,ran)==(cp in scripts[script]),('script',script,hex(cp))
 jt=next((k for k,s in joining.items() if cp in s),'U');assert data.joining_types().get(cp,ord('U'))==ord(jt),('joining',hex(cp))
counts['derived_property_scalars']=0x110000-2048
counts['seconds']=round(time.monotonic()-start,3);counts['source_hashes']={str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in W.rglob('*.txt')};Path(__import__('os').environ['EMAIL_NEXT_IDNA17_RESULTS']).write_text(json.dumps(counts,indent=2)+'\n');print({k:v for k,v in counts.items() if k!='source_hashes'})
