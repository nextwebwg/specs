from unicode17_provider import HERE, ICU17
from pathlib import Path
import json
u=ICU17(__import__('json').loads(Path(__import__('os').environ['EMAIL_NEXT_IDNA17_CONFIG']).read_text()));p=Path(__import__('os').environ['EMAIL_NEXT_UCD17_DIRECTORY']);aliases={}
for line in (p/'PropertyValueAliases.txt').read_text().split('\n'):
 r=[x.strip() for x in line.split('#')[0].split(';')]
 if r[0]=='bc':
  for x in r[1:]:aliases[x]=r[1]
bidi=['L']*0x110000;explicit=[]
for line in (p/'extracted/DerivedBidiClass.txt').read_text().split('\n'):
 if line.startswith('# @missing:'):text=line.split(':',1)[1]
 else:
  text=line.split('#')[0].strip()
  if not text:continue
  explicit.append(text);continue
 r=[x.strip() for x in text.split(';')];a=r[0].split('..');lo=int(a[0],16);hi=int(a[-1],16);bidi[lo:hi+1]=[aliases[r[1]]]*(hi-lo+1)
for text in explicit:
 r=[x.strip() for x in text.split(';')];a=r[0].split('..');lo=int(a[0],16);hi=int(a[-1],16);bidi[lo:hi+1]=[aliases[r[1]]]*(hi-lo+1)
for cp in range(0x110000):
 if 0xD800<=cp<=0xDFFF:continue
 assert u.bidirectional(chr(cp))==bidi[cp],hex(cp)
print('Bidi_Class:1112064 scalar comparisons passed')
