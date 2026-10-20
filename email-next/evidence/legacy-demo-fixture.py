"""Parse the explicit synthetic single-part UTF-8 plain/HTML MIME fixture inventory."""
import base64
from email import policy
from email.parser import BytesParser
import hashlib
import json
from pathlib import Path
import re
ROOT=Path(__file__).with_name('legacy-demo-data')
def load():
    inventory=json.loads((ROOT/'inventory.json').read_text());messages={}
    for name in inventory['messages']:
        if not re.fullmatch('[a-z-]+',name):raise ValueError('Fixture name')
        raw=(ROOT/(name+'.eml')).read_bytes();m=BytesParser(policy=policy.default).parsebytes(raw)
        if m.is_multipart() or m.get_content_type() not in ('text/plain','text/html') or m.get_content_charset()!='utf-8':raise ValueError('Unsupported demo MIME')
        decoded=m.get_payload(decode=True);text=decoded.decode('utf-8','strict')
        ids=m.get_all('Message-ID',[]);refs=m.get_all('References',[]);reply=m.get_all('In-Reply-To',[])
        diagnostics=[str(x) for x in m.defects]
        valid=len(ids)==1 and str(ids[0])==f'<{name}@demo.invalid>' and len(refs)<=1 and len(reply)<=1
        parents=[]
        if valid:
            reference=str(refs[0]) if refs else ''
            tokens=re.findall(r'<([a-z-]+)@demo.invalid>',reference)
            if reference and ' '.join(f'<{x}@demo.invalid>' for x in tokens)!=reference:valid=False
            if reply and str(reply[0]) not in [f'<{x}@demo.invalid>' for x in tokens]:valid=False
            parents=tokens if valid else []
        if not valid:diagnostics.append('unresolved-fixture-relationship')
        messages[name]=dict(id=name,mediaType=m.get_content_type(),sender=str(m['From']),date=str(m['Date']),text=text,format=m.get_param('format') or 'fixed',delsp=m.get_param('delsp') or 'no',parents=parents,diagnostics=diagnostics,original=raw.decode('ascii'),sha256=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode())
    return dict(messages=messages,scenarios=inventory['scenarios'])
if __name__=='__main__':print(json.dumps(load()))
