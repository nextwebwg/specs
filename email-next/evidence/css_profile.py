"""Experimental inline declaration filter; not an HTML sanitizer."""
import tinycss2

KEYWORDS = {
    'font-family': 'serif sans-serif monospace',
    'font-style': 'normal italic', 'font-weight': 'normal bold 400 700',
    'font-size': '0.75rem 0.875rem 1rem 1.125rem 1.25rem 1.5rem 2rem',
    'line-height': 'normal 1 1.25 1.5 1.75 2',
    'text-align': 'start end left right center',
    'text-decoration-line': 'none underline line-through',
    'white-space': 'normal pre-wrap', 'overflow-wrap': 'normal anywhere',
    'border-width': '0 1px 2px 3px', 'border-style': 'none solid dashed dotted',
    'border-collapse': 'separate collapse', 'vertical-align': 'baseline top middle bottom',
}
for family in ('margin', 'padding'):
    for side in ('top', 'right', 'bottom', 'left'):
        KEYWORDS[f'{family}-{side}'] = '0 0.25rem 0.5rem 1rem 1.5rem 2rem'
COLORS = {'color', 'background-color', 'border-color'}


def filter_style(source):
    """Return a fresh safe declaration string, never the original CSS.

    No resource bounds, HTML parsing, layout or accessibility guarantees.
    """
    # Match CSS input preprocessing so parser coordinates refer to this text.
    source = source.replace('\r\n', '\n').replace('\r', '\n').replace('\f', '\n').replace('\0', '\ufffd')
    source = ''.join('\ufffd' if 0xd800 <= ord(c) <= 0xdfff else c for c in source)
    lines = source.split('\n')
    def suffix(node):
        return lines[node.source_line - 1][node.source_column - 1:]
    accepted = {}
    for item in tinycss2.parse_declaration_list(source, skip_comments=True, skip_whitespace=True):
        if item.type != 'declaration' or item.important:
            continue
        name = item.lower_name
        # AST names are unescaped. Compare the original spelling to reject escapes.
        if suffix(item)[:len(name)].lower() != name:
            continue
        tokens = [t for t in item.value if t.type not in ('comment', 'whitespace')]
        if len(tokens) != 1:
            continue
        token = tokens[0]
        value = None
        if name in COLORS:
            if token.type == 'hash' and len(token.value) in (3, 6) and all(c in '0123456789abcdefABCDEF' for c in token.value):
                value = '#' + token.value.lower()
            elif name == 'background-color' and token.type == 'ident' and token.lower_value == 'transparent':
                value = 'transparent'
        elif name in KEYWORDS:
            if token.type == 'ident':
                candidate = token.lower_value
                if candidate[:1].isdigit():
                    # Escaped identifiers are not literal CSS numeric tokens.
                    continue
            elif token.type in ('number', 'dimension'):
                candidate = token.serialize()
                # Numeric spellings are literal, including units and leading signs.
                if suffix(token)[:len(candidate)] != candidate:
                    continue
            else:
                continue
            if candidate in KEYWORDS[name].split():
                value = candidate
        if value is not None:
            accepted[name] = value
    return ';'.join(f'{name}:{value}' for name, value in accepted.items())
