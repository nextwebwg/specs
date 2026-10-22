"""Partial inert projection experiment; navigation/resources/rendering are not implemented."""
import html5lib
from html_attributes import filter_attributes
HTML='{http://www.w3.org/1999/xhtml}'
ALLOWED=set('a abbr b bdi blockquote br caption code col colgroup dd del div dl dt em h1 h2 h3 h4 h5 h6 hr i img li ol p pre s small span strong sub sup table tbody td th thead tfoot tr u ul wbr'.split())
DROP=set('script style template iframe frame frameset object embed applet noscript textarea select option button input video audio source track canvas'.split())

def project_tree(octets,*,mime_charset,max_bytes,max_nodes,max_depth,parser_adapter=None,process_limits=None):
    if not isinstance(octets,bytes) or any(type(n)is not int or n<0 for n in (max_bytes,max_nodes,max_depth)):raise ValueError('invalid input or limits')
    if not isinstance(mime_charset,str) or mime_charset.lower()!='utf-8':raise ValueError('explicit UTF-8 MIME charset required')
    if len(octets)>max_bytes:raise ValueError('input limit')
    text=octets.decode('utf-8',errors='strict')
    if parser_adapter is not None:
        # A trusted explicit adapter owns its parsing isolation. Its bounded tree
        # still passes the same projection/semantic checks here.
        return _project_tree_local(octets,mime_charset=mime_charset,max_bytes=max_bytes,max_nodes=max_nodes,max_depth=max_depth,parser_adapter=parser_adapter)
    import json,sys
    from pathlib import Path
    from dataclasses import asdict
    from parser_process import ParserLimits,ParserFailure,run_parser
    limits=ParserLimits() if process_limits is None else process_limits
    if not isinstance(limits,ParserLimits):raise ValueError('ParserLimits required')
    request=json.dumps(dict(text=text,max_bytes=max_bytes,max_nodes=max_nodes,max_depth=max_depth)).encode()
    raw=run_parser([sys.executable,str(Path(__file__).with_name('html_projection_worker.py')),json.dumps(asdict(limits))],request,limits)
    result=json.loads(raw)
    if result=={'failure':'unpreserved-direction-boundary'}:
        raise ParserFailure('unpreserved-direction-boundary')
    return result

def _project_tree_local(octets,*,mime_charset,max_bytes,max_nodes,max_depth,parser_adapter=None):
    if not isinstance(octets,bytes) or any(type(n) is not int or n<0 for n in [max_bytes,max_nodes,max_depth]):
        raise ValueError('invalid input or limits')
    if not isinstance(mime_charset,str) or mime_charset.lower()!='utf-8':
        raise ValueError('explicit UTF-8 MIME charset required')
    if len(octets)>max_bytes:raise ValueError('input limit')
    text=octets.decode('utf-8',errors='strict')
    if parser_adapter is None:
        parser=html5lib.HTMLParser(namespaceHTMLElements=True)
        root=parser.parse(text,scripting=False)
        parse_errors=parser.errors
    else:
        root,parse_errors=parser_adapter(text)
    stack=[(root,1)];count=0
    while stack:
        node,depth=stack.pop();count+=1
        if count>max_nodes or depth>max_depth:raise ValueError('tree limit')
        stack.extend((child,depth+1) for child in node)
    # This pinned parser's recovery can relocate content out of these containers.
    # Refuse the experimental projection rather than claiming subtree removal.
    if parser_adapter is None and any(node.tag in (HTML+'template',HTML+'noscript') for node in root.iter()):
        raise ValueError('unsupported parser context: template or noscript')
    if any(error[1]=='disallowed-content-in-noscript-in-head' for error in parse_errors):
        raise ValueError('unsupported parser context: malformed head noscript')
    body=root.find(HTML+'body')
    diagnostics=[]
    encoding_state='consistent'
    for node in root.iter(HTML+'meta'):
        attrs=node.attrib
        if set(attrs)!={'charset'} or attrs.get('charset','').lower()!='utf-8':
            encoding_state='nonconforming'
            diagnostics.append('unsupported-or-conflicting-meta')
    # Duplicate attributes are already collapsed by HTML parsing. Do not treat
    # that chosen value as evidence that all original declarations agreed.
    if any(error[1]=='duplicate-attribute' for error in parse_errors):
        encoding_state='nonconforming'
        diagnostics.append('duplicate-source-attribute')
    def own_direction(node):
        value=node.attrib.get('dir','').lower()
        return value if value in ('ltr','rtl','auto') else None
    def children(node,inherited_language=None,output_language=None,inherited_title=None,output_title=None):
        language=node.attrib.get('lang',inherited_language)
        title=node.attrib.get('title',inherited_title)
        def text_node(text):
            # Removed wrappers can carry language and advisory titles for bare text.
            # Use an inert span for text; whitespace alone must not introduce
            # spans into table structure. Empty titles cancel ancestor advice.
            attrs={}
            if language is not None and language != output_language:attrs['lang']=language
            if title is not None and title != output_title:attrs['title']=title
            if attrs and text.strip():
                return {'element':'span','attributes':attrs,'children':[text]}
            return text
        result=[text_node(node.text)] if node.text else []
        for child in node:
            tag=child.tag
            if not isinstance(tag,str) or not tag.startswith(HTML):
                diagnostics.append('removed-comment-or-foreign-subtree')
            else:
                name=tag[len(HTML):]
                if name in DROP:diagnostics.append('removed-subtree:'+name)
                elif name in ALLOWED:
                    attributes,rejected=filter_attributes(name,child.attrib)
                    diagnostics.extend('removed-attribute:'+a for a in rejected)
                    if language is not None and 'lang' not in attributes:
                        attributes['lang']=language
                    if title is not None and 'title' not in attributes:
                        attributes['title']=title
                    projected={'element':name,'children':children(child,language,child.attrib.get('lang',language),title,child.attrib.get('title',title))}
                    if attributes:projected['attributes']=attributes
                    if name=='a' and 'href' in child.attrib:
                        # Inert intermediate data, never a DOM attribute.
                        projected['navigationCandidate']=child.attrib['href']
                    if name=='img':
                        if 'alt' not in child.attrib:
                            diagnostics.append('missing-image-alt')
                        if 'src' in child.attrib:
                            # Preserve only for a later authenticated resource
                            # resolver. The serializer never installs this URL.
                            projected['imageCandidate']=child.attrib['src']
                    result.append(projected)
                elif name=='form' and own_direction(child) and node.tag in {HTML+n for n in ('body','div','blockquote','td','th','li','dd')}:
                    # Preserve one direction boundary, especially auto's scan;
                    # copying dir to descendants would change their isolation.
                    attrs={'dir':own_direction(child)}
                    if 'lang' in child.attrib:attrs['lang']=child.attrib['lang']
                    if child.attrib.get('title',title) is not None:attrs['title']=child.attrib.get('title',title)
                    result.append({'element':'div','attributes':attrs,
                        'children':children(child,language,child.attrib.get('lang',output_language),title,child.attrib.get('title',title))})
                    diagnostics.append('inert-direction-wrapper:form')
                else:
                    if own_direction(child):
                        # Unwrapping can change inherited/auto direction and
                        # isolation. No context-safe replacement is selected for
                        # this source wrapper; never return a partial rich view.
                        raise ValueError('unpreserved-direction-boundary:'+name)
                    diagnostics.append('unwrapped:'+name);result.extend(children(child,language,output_language,title,output_title))
            if child.tail:result.append(text_node(child.tail))
        return result
    tree=children(body,root.attrib.get('lang'),inherited_title=root.attrib.get('title')) if body is not None else []
    # Auto examines filtered message content, never the client preview's title.
    # Separate body/html boundaries preserve explicit nested overrides.
    for context in (body,root):
        if context is not None and own_direction(context):
            tree=[{'element':'div','attributes':{'dir':own_direction(context)},'children':tree}]
    return {'tree':tree,
            'diagnostics':diagnostics,'parseErrors':parse_errors,'encodingState':encoding_state}
