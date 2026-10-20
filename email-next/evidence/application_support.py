"""Exact signed assertion coverage; syntax/support does not establish authority."""
from application_tuples import covers

def supports(value,application,ordering):
    if 'payload' in application:
        version=('7' if value.get('version')=='7' else '6') if ordering=='endpoint-quorum-v0' else '5' if application.get('envelopeVersion')=='3' else '4' if application.get('envelopeVersion')=='2' else '3' if application.get('payload')=='mime-rich-v0' else '2'
        return value.get('version')==version and covers(value['applications'],application,ordering,version=version)
    if value.get('version')!='1':return False
    descriptor=next((x for x in value['applications'] if x['envelopeVersion']==application['envelopeVersion']),None)
    return bool(descriptor and set(application['operations'])<=set(descriptor['operations']) and ordering in descriptor['ordering'])
