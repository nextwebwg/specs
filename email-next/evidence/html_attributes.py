"""Partial attribute stage. Navigation and image sources remain disabled; language labels are preserved, not certified."""
import re
from css_profile import filter_style

def bounded_integer(value,low,high,signed=False):
    if not re.fullmatch(r'[+-]?[0-9]+' if signed else r'[0-9]+',value):return None
    digits=value.lstrip('+-').lstrip('0') or '0'
    if len(digits)>10:return None
    number=int(('-' if value.startswith('-') else '')+digits)
    return str(number) if low<=number<=high else None

def filter_attributes(element,attributes):
    result={};rejected=[]
    for name,value in attributes.items():
        accepted=None
        if name in ('title','lang'):accepted=value
        elif name=='dir' and value.lower() in ('ltr','rtl','auto'):accepted=value.lower()
        elif name=='style':accepted=filter_style(value) or None
        elif element=='img' and name=='alt':accepted=value
        elif element=='img' and name in ('width','height'):accepted=bounded_integer(value,1,4096)
        elif element in ('td','th') and name in ('colspan','rowspan'):accepted=bounded_integer(value,1,1000)
        elif element in ('col','colgroup') and name=='span':accepted=bounded_integer(value,1,1000)
        elif (element=='ol' and name=='start') or (element=='li' and name=='value'):
            accepted=bounded_integer(value,-2147483648,2147483647,True)
        elif element=='ol' and name=='reversed':accepted=''
        elif element=='th' and name=='scope' and value.lower() in ('row','col','rowgroup','colgroup'):accepted=value.lower()
        if accepted is None:rejected.append(name)
        else:result[name]=accepted
    return result,rejected
