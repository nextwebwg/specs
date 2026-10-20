"""Project a browser-captured tree and the same bytes through html5lib; no browser authority claims."""
import json,sys
import html5lib
from xml.etree.ElementTree import Element
from html_tree import project_tree

def convert(node):
    result=Element(node['tag'],node.get('attributes',{}));previous=None
    for child in node['children']:
        if isinstance(child,str):
            if previous is None:result.text=(result.text or '')+child
            else:previous.tail=(previous.tail or '')+child
        else:
            previous=convert(child);result.append(previous)
    return result

def raw_tree(node):
    if not isinstance(node.tag,str):return {'tag':'#other','children':[]}
    children=[]
    if node.text:children.append(node.text)
    for child in node:
        children.append(raw_tree(child))
        if child.tail:children.append(child.tail)
    return {'tag':node.tag,'attributes':dict(node.attrib),'children':children}

def main():
    result=[]
    for fixture in json.load(sys.stdin):
        opts=dict(mime_charset='utf-8',max_bytes=16384,max_nodes=500,max_depth=100)
        legacy=project_tree(fixture['source'].encode(),**opts)['tree']
        browser=project_tree(fixture['source'].encode(),parser_adapter=lambda text:(convert(fixture['root']),[]),**opts)['tree']
        raw=raw_tree(html5lib.HTMLParser(namespaceHTMLElements=True).parse(fixture['source'],scripting=False))
        result.append({'name':fixture['name'],'equal':legacy==browser,'rawEqual':raw==fixture['root'],'html5lib':legacy,'chromium':browser,'rawHtml5lib':raw,'rawChromium':fixture['root']})
    json.dump(result,sys.stdout,ensure_ascii=False)
if __name__=='__main__':main()
