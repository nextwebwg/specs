"""Existing inert HTML/CSS projection and scoped decoder joined to rich operations."""
import json,re,subprocess
from pathlib import Path
from urllib.parse import unquote
from html_tree import project_tree,ALLOWED
from css_profile import KEYWORDS,COLORS
from image_decode import DecodeLimits
from scoped_image_decode import resolve_and_decode_image
HERE=Path(__file__).parent

def project(operation,event,*,parts=None,authoring=False):
    from parser_process import ParserFailure
    try:result=project_tree(operation['html'].encode(),mime_charset='utf-8',max_bytes=1048576,max_nodes=10000,max_depth=64)
    except ParserFailure:
        if authoring:raise
        return dict(state='plain-only',text=operation['text'],diagnostics=['parser-resource-failure'])
    allowed={x['resource']:x['mediaType'] for x in operation['embedded']};diagnostics=list(result['diagnostics']);text=[];nodes=[]
    def visit(items):
        for node in items:
            if isinstance(node,str):
                if node.strip():text.append(node.strip())
                continue
            nodes.append(node)
            if node['element']=='img':
                alt=node.get('attributes',{}).get('alt','');candidate=node.get('imageCandidate','')
                if alt:text.append(alt)
                try:match=re.fullmatch(r'([0-9a-f]{32})\.'+re.escape(event)+r'@resources\.email-next\.invalid',unquote(candidate[4:])) if candidate[:4].lower()=='cid:' else None
                except ValueError:match=None
                if not match or match[1] not in allowed:diagnostics.append('image-role-or-scope')
            visit(node['children'])
    visit(result['tree'])
    # These URLs were deliberately withheld from DOM attributes. Only the
    # corresponding typed candidate may pass to the independent resolver.
    for node in nodes:
        for candidate, diagnostic in (('imageCandidate','removed-attribute:src'),('navigationCandidate','removed-attribute:href')):
            if candidate in node and diagnostic in diagnostics:diagnostics.remove(diagnostic)
    if result['encodingState']!='consistent':diagnostics.append('encoding')
    normalized=' '.join(operation['text'].split());omitted=[t for t in text if ' '.join(t.split()) not in normalized]
    if authoring and (diagnostics or omitted):raise ValueError('Rich authoring requires conforming HTML and complete readable text')
    if diagnostics:return dict(state='plain-only',text=operation['text'],diagnostics=diagnostics)
    script="import {bindNavigation} from './html-navigation.mjs';let s='';for await(const c of process.stdin)s+=c;process.stdout.write(JSON.stringify(bindNavigation(JSON.parse(s))));"
    bound=subprocess.run(['node','--input-type=module','-e',script],cwd=HERE,input=json.dumps(result['tree']),text=True,capture_output=True,check=True,timeout=10)
    tree=json.loads(bound.stdout)['tree'];images={};counter=0
    def pixels(items):
        nonlocal counter
        for node in items:
            if isinstance(node,str):continue
            counter+=1;node['nodeId']=str(counter)
            if node['element']=='img':
                image=resolve_and_decode_image(node.pop('imageCandidate',''),event,operation['manifest'],parts or [],alt=node.get('attributes',{}).get('alt',''),resource_limits=dict(maxBytes=1048576,maxChunks=1,maxInputBytes=1048576),decode_limits=DecodeLimits(1048576,2048,2048,1048576,4194304,5),bridge_max_bytes=4194304)
                if image['state']=='pixels':
                    p=image['pixels'];images[node['nodeId']]=dict(state='pixels',width=p.width,height=p.height,rgba=list(p.rgba))
                else:images[node['nodeId']]=dict(state='alt',reason=image.get('reason'))
            pixels(node['children'])
    pixels(tree)
    return dict(state='rich',text=operation['text'],tree=tree,images=images,diagnostics=diagnostics,plainReview=dict(omittedText=omitted,semanticEquivalenceVerified=False))

def configuration():
    return dict(policy=dict(elements=sorted(ALLOWED),keywords=KEYWORDS,colors=sorted(COLORS)),baseline=(HERE/'presentation-defaults.css').read_text(),limits=dict(maxNodes=10000,maxDepth=64,maxText=1048576,maxWidth=2048,maxHeight=2048,maxPixels=1048576,maxTotalPixels=1048576,maxImages=16))
