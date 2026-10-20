"""Complete ordinary rich-copy disclosure; no structured event alternative."""
import base64,hashlib
from email import policy
from email.parser import BytesParser
from rich_carrier import package_rich
from rich_presentation import project
from event_encoding import decode_event

def preview(application,resources):
    event=decode_event(application)['value'];project(event['operation'],event['event'],authoring=True)
    entity=BytesParser(policy=policy.SMTP).parsebytes(package_rich(application,resources,max_wire_bytes=2097152,max_parts=64,max_decoded_bytes=1048576))
    alternatives=entity.get_payload()[0] if entity.get_content_type()=='multipart/mixed' else entity
    alternatives.set_payload(alternatives.get_payload()[:2])
    digest=hashlib.sha256(application).hexdigest()
    for index,part in enumerate(entity.walk()):
        if part.is_multipart():part.set_boundary('ordinary-'+digest+'-'+str(index))
    wire=entity.as_bytes()
    return dict(format='rich-copy-v1',entityBase64=base64.b64encode(wire).decode(),entitySha256=hashlib.sha256(wire).hexdigest(),structuredAlternative=False)
