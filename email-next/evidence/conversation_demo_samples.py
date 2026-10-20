"""Synthetic conversation samples delivered through the loopback SMTP fixture."""
import secrets
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from smtp_loopback import roundtrip


def populate(demo):
    def add(text, address, subject, parent=None):
        prior=demo.reply_targets[parent] if parent else None
        message=EmailMessage(policy=policy.SMTP)
        message['From']=address
        message['To']='sam@example.invalid' if address=='carol@example.invalid' else 'carol@example.invalid'
        message['Subject']=('Re: ' if prior else '')+subject
        message['Message-ID']='<'+secrets.token_hex(16)+'@example.invalid>'
        if prior:
            message['In-Reply-To']=prior['messageId']
            message['References']=' '.join(x for x in (prior['references'],prior['messageId']) if x)
        message.set_content(text,charset='utf-8')
        raw=roundtrip(message.as_bytes())
        parsed=BytesParser(policy=policy.default).parsebytes(raw)
        source=secrets.token_hex(16)
        demo.reply_originals[source]=raw
        target=demo.register_target('sam',raw,demo.contacts[address],parsed.get_content())
        demo.threads['sam']['timeline'].append(dict(kind='ordinary',text=parsed.get_content(),id=source,
            parent=str(parsed.get('In-Reply-To','')),parentText=prior['text'] if prior else None,
            sender=demo.contacts[address],address=address,protected=False,replyTarget=target))
        demo.touch('sam',parsed.get_content())
        return target

    hike=demo.thread_targets['sam'][0]
    early=add('Yes! Could we get an early start? I can drive.','carol@example.invalid','Weekend plans',hike)
    add('8:30 at the north entrance? That should give us the trail before it gets busy.','sam@example.invalid','Weekend plans',early)
    photos=add('Photos from the coast\nI finally sorted last weekend’s pictures. There are a few really good ones of all of us.','sam@example.invalid','Photos from the coast')
    album=add('Please send the album when it’s ready — I’d love the one by the lighthouse.','carol@example.invalid','Photos from the coast',photos)
    add('Will do. I’m putting the full-resolution versions in tonight.','sam@example.invalid','Photos from the coast',album)
    dinner=add('Dinner after the hike?\nMaya mentioned the little place near the station.','carol@example.invalid','Dinner after the hike')
    add('Absolutely. I’ll ask Maya to join us. Shall I book for 6?','sam@example.invalid','Dinner after the hike',dinner)
    add('One more thing for Saturday: the north car park is closed. Let’s meet at the café instead.','sam@example.invalid','Weekend plans',hike)
