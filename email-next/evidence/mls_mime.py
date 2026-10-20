"""Opaque-attachment transport fixture, not the final Email Next MIME binding."""
import base64
import binascii
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
import sys
MAX_PAYLOAD=1048576
MAX_WIRE=2097152

def package(payload):
    if not isinstance(payload,bytes) or len(payload)>MAX_PAYLOAD:raise ValueError('Payload bound')
    message=EmailMessage(policy=policy.SMTP)
    message['From']='alice@example.invalid'
    message['To']='bob@example.invalid'
    message['Subject']='Protected-message transport fixture'
    message.set_content('This test attachment contains opaque protocol bytes.\n',charset='utf-8')
    message.add_attachment(payload,maintype='application',subtype='octet-stream',filename='protocol.bin',cte='base64')
    return message.as_bytes()

def unpack(wire):
    if not isinstance(wire,bytes) or len(wire)>MAX_WIRE:raise ValueError('Wire bound')
    message=BytesParser(policy=policy.default).parsebytes(wire)
    if any(p.defects for p in message.walk()):raise ValueError('MIME defects')
    if len(message.get_all('Content-Type',[]))!=1 or message.get_content_type()!='multipart/mixed':raise ValueError('Envelope')
    parts=list(message.iter_parts())
    if len(parts)!=2 or parts[0].get_content_type()!='text/plain':raise ValueError('Fixture layout')
    attachment=parts[1]
    if attachment.is_multipart() or len(attachment.get_all('Content-Type',[]))!=1 or attachment.get_content_type()!='application/octet-stream':raise ValueError('Opaque part')
    if attachment.get_all('Content-Transfer-Encoding',[])!=['base64']:raise ValueError('Transfer encoding')
    body=attachment.get_payload()
    if not isinstance(body,str):raise ValueError('Payload type')
    compact=''.join(body.split())
    try:payload=base64.b64decode(compact,validate=True)
    except (ValueError,binascii.Error) as error:raise ValueError('Invalid base64') from error
    if base64.b64encode(payload).decode('ascii')!=compact or len(payload)>MAX_PAYLOAD:raise ValueError('Payload encoding/bound')
    return payload

if __name__=='__main__':
    original=sys.stdin.buffer.read(MAX_PAYLOAD+1)
    from smtp_loopback import roundtrip
    sys.stdout.buffer.write(unpack(roundtrip(package(original))))
