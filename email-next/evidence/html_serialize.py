"""Serialize the internal filtered tree as an inert preview, not a client host."""
from html import escape
from html_tree import ALLOWED
VOID={'br','col','hr','img','wbr'}

def serialize_preview(tree):
    def render(node):
        if isinstance(node,str):return escape(node,quote=False).replace('\r','&#13;')
        name=node['element']
        if name not in ALLOWED:raise ValueError('unexpected element')
        # Input must come from the filter; raw navigation candidates never become
        # href/src. The preview intentionally provides no navigation or image load.
        attributes=node.get('attributes',{})
        rendered=[]
        for key,value in attributes.items():
            if key not in {'title','lang','dir','style','alt','width','height','start','reversed','value','colspan','rowspan','scope','span'}:
                raise ValueError('unexpected attribute')
            rendered.append(' '+key+'="'+escape(value,quote=True).replace('\r','&#13;')+'"')
        opening='<'+name+''.join(rendered)+'>'
        if name in VOID:
            if node['children']:raise ValueError('void children')
            return opening
        content=''.join(render(child) for child in node['children'])
        # Fresh preview generation preserves projected text across reparsing:
        # HTML consumes one immediate LF after a pre start tag.
        if name=='pre' and content.startswith('\n'):content='\n'+content
        return opening+content+'</'+name+'>'
    body=''.join(render(node) for node in tree)
    return ('<!doctype html><html><head><meta charset="utf-8">'
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">'
            '<title>Unverified message preview</title></head><body>'+body+'</body></html>')
