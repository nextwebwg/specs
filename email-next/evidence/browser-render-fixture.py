"""Real projection/navigation/scoped-image fixture; no signature verification."""
import base64
import hashlib
import io
import json
from pathlib import Path
import subprocess
from PIL import Image
from html_tree import project_tree,ALLOWED
from css_profile import KEYWORDS,COLORS
from image_decode import DecodeLimits
from scoped_image_decode import resolve_and_decode_image
HERE=Path(__file__).parent
EVENT='1'*32
ID='2'*32
CID=f'{ID}.{EVENT}@resources.email-next.invalid'
html=f'''<div lang="fr" dir="rtl"><h2>Meeting &lt;script&gt;bad()&lt;/script&gt;</h2><p>Hello <a href="https://example.invalid/destination" style="color:#fff;text-decoration-line:none">Visit destination</a></p><script>window.senderExecuted=true</script><img alt="Blue square" src="cid:{CID}" width="4096"><img alt="Missing picture" src="https://example.invalid/tracker"><ol start="3"><li>Third</li></ol><table><caption>Schedule</caption><tr><th scope="col">Day</th><td>Thursday</td></tr></table><p style="font-size:1.5rem;line-height:1.75;border-style:dotted;background-color:#abc">Styled text</p></div>'''.encode()
result=project_tree(html,mime_charset='utf-8',max_bytes=10000,max_nodes=1000,max_depth=30)
script="import {bindNavigation} from './html-navigation.mjs';import{readFileSync}from'node:fs';process.stdout.write(JSON.stringify(bindNavigation(JSON.parse(readFileSync(0,'utf8')))));"
result['tree']=json.loads(subprocess.run(['node','--input-type=module','-e',script],cwd=HERE,input=json.dumps(result['tree']),capture_output=True,text=True,check=True).stdout)['tree']
stream=io.BytesIO();Image.new('RGB',(2,2),'blue').save(stream,format='PNG');encoded=stream.getvalue()
manifest=[dict(id=ID,size=str(len(encoded)),sha256=hashlib.sha256(encoded).hexdigest())]
parts=[dict(contentId=CID,mediaType='image/png',bytes=encoded)]
images={};counter=0

def visit(nodes):
    global counter
    for node in nodes:
        if isinstance(node,str):continue
        counter+=1;node['nodeId']=str(counter)
        if node['element']=='img':
            image=resolve_and_decode_image(node.pop('imageCandidate',''),EVENT,manifest,parts,alt=node.get('attributes',{}).get('alt',''),resource_limits={'maxBytes':10000,'maxChunks':1,'maxInputBytes':10000},decode_limits=DecodeLimits(10000,64,64,4096,16384,5),bridge_max_bytes=30000)
            if image['state']=='pixels':
                p=image['pixels'];images[node['nodeId']]=dict(state='pixels',width=p.width,height=p.height,rgba=list(p.rgba))
            else:images[node['nodeId']]=dict(state='alt')
        visit(node['children'])
visit(result['tree'])
direction=project_tree('<html dir=auto><head><title>Latin title</title></head><body><div dir=rtl><bdi>abc</bdi><div dir=auto>123...</div></div><p>שלום</p></body></html>'.encode(),mime_charset='utf-8',max_bytes=10000,max_nodes=1000,max_depth=30)['tree']
visit(direction)
print(json.dumps(dict(tree=result['tree'],directionTree=direction,images=images,policy=dict(elements=sorted(ALLOWED),keywords=KEYWORDS,colors=sorted(COLORS)),baseline=(HERE/'presentation-defaults.css').read_text(),limits=dict(maxNodes=10000,maxDepth=100,maxText=100000,maxWidth=64,maxHeight=64,maxPixels=4096,maxTotalPixels=4096,maxImages=16))))
