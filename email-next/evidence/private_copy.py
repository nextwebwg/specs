"""Authenticated private-copy roster invariant, not an outer-header inference."""
def check_roster(context,principals):
    if context.get('version') not in ('5','6','7'):return
    value=context.get('delivery')
    if not isinstance(value,dict):raise ValueError('Delivery role')
    if value=={'kind':'ordinary-v0'}:return
    if set(value)!={'kind','originator','recipient'} or value['kind']!='private-copy-v0' or value['originator']==value['recipient'] or set(principals)!={value['originator'],value['recipient']}:raise ValueError('Private copy principal roster')
