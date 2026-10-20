"""Internal authenticated-epoch payload dispatch, never content sniffing."""
import json
import subprocess
from pathlib import Path
from event_encoding import decode_event
from protected_carrier import inspect_carrier,package_carrier

# Adjustable experiment acceptance budgets; parsing allocation limits differ.
DEFAULT_LIMITS=dict(max_wire_bytes=1048576,max_decoded_bytes=1048576,max_parts=64,max_depth=3)

def selected_format(context,agreement,*,configured_ordering=False,configured_quorum_ordering=False):
    script="""import {validateConversationContext} from './conversation-context.mjs';
let s='';for await(const c of process.stdin)s+=c;const v=JSON.parse(s);
process.stdout.write(validateConversationContext(v.context,{configuredApplication:v.agreement,configuredEndpointOrdering:v.ordering,configuredQuorumOrdering:v.quorum})?'valid':'invalid');"""
    check=subprocess.run(['node','--input-type=module','-e',script],cwd=Path(__file__).parent,input=json.dumps(dict(context=context,agreement=agreement,ordering=configured_ordering,quorum=configured_quorum_ordering)),text=True,capture_output=True,check=True,timeout=10)
    if check.stdout!='valid':raise ValueError('Unagreed application payload context')
    return context['application']['payload'] if context['version'] in ('3','4','5','6','7') else 'raw-event-v0'

def encode(sender,application,context,agreement,*,configured_ordering=False,configured_quorum_ordering=False,limits=None,resources=None):
    kind=selected_format(context,agreement,configured_ordering=configured_ordering,configured_quorum_ordering=configured_quorum_ordering)
    if kind=='raw-event-v0':
        if resources is not None:raise ValueError('Resources require MIME payload')
        return application,dict(format=kind)
    if kind=='mime-rich-v0' and decode_event(application)['value']['operation']['kind']=='rich-message':
        from rich_presentation import project as project_rich
        from rich_carrier import package_rich
        event=decode_event(application)['value'];project_rich(event['operation'],event['event'],authoring=True)
        entity=package_rich(application,resources or {},**{k:v for k,v in (DEFAULT_LIMITS if limits is None else limits).items() if k!='max_depth'})
        return entity,dict(format=kind,layout='rich-body')
    from plaintext_projection import project
    projection=project(sender,application)['projection']
    if decode_event(application)['value']['operation']['kind']=='attachment-message':
        from protected_attachment_carrier import package_attachment_carrier
        if not isinstance(resources,dict):raise ValueError('Attachment resources required')
        entity=package_attachment_carrier(application,projection['text'],projection['html'],resources,**{k:v for k,v in (DEFAULT_LIMITS if limits is None else limits).items() if k!='max_depth'})
    else:
        if resources is not None:raise ValueError('Unexpected resources')
        entity=package_carrier(application,projection['text'],projection['html'],**(DEFAULT_LIMITS if limits is None else limits))
    return entity,dict(format=kind,layout='attachments' if resources is not None else 'ordinary-alternatives')

def decode(payload,context,agreement,*,configured_ordering=False,configured_quorum_ordering=False,limits=None):
    kind=selected_format(context,agreement,configured_ordering=configured_ordering,configured_quorum_ordering=configured_quorum_ordering)
    if kind=='raw-event-v0':
        decode_event(payload)
        return payload,dict(format=kind)
    budget=DEFAULT_LIMITS if limits is None else limits
    if not isinstance(payload,bytes) or len(payload)>budget['max_wire_bytes']:raise ValueError('Payload bound')
    from email.parser import BytesParser
    from email import policy
    try:root=BytesParser(policy=policy.default).parsebytes(payload)
    except RecursionError as error:raise ValueError('Excessive carrier structure') from error
    children=list(root.iter_parts())
    body=list(root.iter_parts())[0] if root.get_content_type()=='multipart/mixed' and children else root
    body_children=list(body.iter_parts())
    rich_layout=kind=='mime-rich-v0' and len(body_children)==3 and (body_children[1].get_content_type()=='multipart/related' or body_children[2].get_content_type()=='application/vnd.threadlabs.email-next-event+json')
    if rich_layout:
        # Direct event discriminator only, never recursive search or format fallback.
        candidate=decode_event(body_children[2].get_payload(decode=True))['value']
        if candidate.get('operation',{}).get('kind')=='rich-message':
            from rich_carrier import inspect_rich
            selected=inspect_rich(payload,**{k:v for k,v in budget.items() if k!='max_depth'})
            images=[dict(p,role='embedded',mediaType=t) for p,t in zip(selected['embedded'],selected['embeddedTypes'])]
            files=[dict(p,role='attachment') for p in selected['attachments']]
            return selected['event']['octets'],dict(format=kind,layout='rich-body',plain=selected['plain'].decode('utf8'),html=selected['html'].decode('utf8'),resources=images+files,projections=selected['attachmentProjections'])
    attachment=root.get_content_type()=='multipart/mixed' and children and children[0].get_content_type()=='multipart/alternative'
    if attachment:
        from protected_attachment_carrier import inspect_attachment_carrier
        selected=inspect_attachment_carrier(payload,**{k:v for k,v in budget.items() if k!='max_depth'})
    else:selected=inspect_carrier(payload,**budget)
    return selected['event']['octets'],dict(format=kind,layout=selected.get('layout','attachments'),pairing=selected.get('pairing'),resources=selected.get('resources',[]),projections=selected.get('projections',[]),
        plain=selected['plain'].decode('utf8'),html=selected['html'].decode('utf8'))

def projection_diagnostic(receiver,application,representation):
    """Compare deterministic readable bytes only after normal journal admission.

    A mismatch does not invalidate an independently admitted structured event.
    No HTML from this comparison is rendered or executed here.
    """
    if representation.get('format') not in ('mime-contribution-v0','mime-rich-v0'):return None
    event=decode_event(application)['value']
    if event['operation']['kind']=='rich-message':
        from mime_package import contribution_alternatives,_decode_alternatives
        alt=contribution_alternatives(application,event['operation']['text'],event['operation']['html'])
        decoded,_=_decode_alternatives(list(alt.iter_parts()),1048576)
        return 'matched' if representation['plain']==decoded[0].decode('utf8') and representation['html']==decoded[1].decode('utf8') else 'mismatch'
    from types import SimpleNamespace
    from plaintext_projection import project
    try:
        projected=project(SimpleNamespace(receiver=receiver),application)['projection']
        expected=inspect_carrier(package_carrier(application,projected['text'],projected['html'],**DEFAULT_LIMITS),**DEFAULT_LIMITS)
    except ValueError:return 'dependencies-pending'
    return 'matched' if all(representation[k]==expected[k].decode('utf8') for k in ('plain','html')) else 'mismatch'
