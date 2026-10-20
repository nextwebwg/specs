"""Loopback conversation demonstration over the joined test deployment.

Uses synthetic configured accounts and loopback SMTP. No real mailboxes, public
capability negotiation, browser account authentication or production hosting.
"""
import argparse
import json
import secrets
from urllib.parse import urlsplit,parse_qs
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
from email.message import EmailMessage
from email import policy
from email.parser import BytesParser
from test_joined_questions import JoinedQuestions
from test_sender_release import LocalSMTP
from client_flow import ClientFlow
from journal_button_view import derive_button_view
from journal_reaction_view import derive_reaction_view
from sender_worker import SenderWorker
from plaintext_release import PlaintextRelease

class Demo:
    def __init__(self, *, mime=False, rich=False, signed_rich=False):
        self.fixture=JoinedQuestions()
        if mime:
            self.fixture.context_version='4' if rich else '3'
            self.fixture.selected_payload='mime-rich-v0' if rich else 'mime-contribution-v0'
        self.fixture.selected_operations=(['answer','attachment-message','message','question','reaction','reaction-withdraw'] if mime else ['answer','message','question','reaction','reaction-withdraw']);self.fixture.selected_operations+=['rich-message'] if rich else [];self.fixture.setUp();f=self.fixture
        self.sandbox_nonce=secrets.token_hex(32);self.nonce=secrets.token_hex(32);self.question=f.question();self.question['disclosures']=[{'kind':'plaintext-email'}]
        self.ref={k:self.question[k] for k in ('principal','conversation','event')}
        fallback=PlaintextRelease(f.senders[0]);fallback.authorize(json.dumps(self.question).encode(),['legacy@example.invalid'])
        f.prepare(0,self.question);fallback.prepare('legacycopy',self.question['event'])
        self.transport(0,self.question['event'],lambda wire:f.receive(1,wire))
        self.legacy_source=None
        self.transport(0,'legacycopy',lambda wire:setattr(self,'legacy_source',wire),plain=True)
        self.answer_wire=None;self.legacy_reply=None;self.timeline=[];self.reply_originals={}
        ordinary=BytesParser(policy=policy.default).parsebytes(self.legacy_source)
        self.legacy_question=dict(id=str(ordinary.get('Message-ID','')),text=ordinary.get_body(preferencelist=('plain',)).get_content())
        self.attachments=[];self.downloads={};self.reaction_targets={};self.ordinary_reactions={};self.ordinary_reaction_actions={}
        self.rich_messages=[];self.rich_selections={}
        if mime:self.add_attachments()
        if rich:self.add_rich()
        self.signed_rich_fixture=None
        if signed_rich:
            from test_signed_rich import SignedRich
            fixture=SignedRich();fixture.setUp();self.signed_rich_fixture=fixture;fixture.test_signed_roster_smtp_then_rich_resource()
            token=secrets.token_hex(32);self.rich_selections[token]=(fixture.display_reference,fixture.display_carrier,fixture.display_receiver);self.rich_messages.append(dict(text=fixture.display_text,selection=token))
        for card in self.rich_messages:
            target=secrets.token_hex(24);card['reactionTarget']=target;self.reaction_targets[target]=dict(thread='project',mode='unavailable',token='')
        self.activity=0
        self.threads={};self.reply_targets={};self.thread_targets={}
        # Trusted synthetic account configuration, never addresses supplied by a browser.
        # Both composer accounts use ordinary mail; neither grants MLS authorship.
        self.sender_accounts={'personal':dict(id='personal',address='carol@example.invalid',label='Personal',enabled=True),'work':dict(id='work',address='carol@work.example.invalid',label='Work',enabled=True)}
        self.contacts={'alice@example.invalid':'Alice','bob@example.invalid':'Bob','carol@example.invalid':'Carol','carol@work.example.invalid':'Carol','maya@example.invalid':'Maya Chen','sam@example.invalid':'Sam Rivera'}
        self.threads['project']=dict(id='project',title='Alice, Bob',participants=[self.person(a) for a in ('alice@example.invalid','bob@example.invalid','carol@example.invalid')],contact=True,timeline=self.timeline,preview=self.question['operation']['text'],activity=0)
        self.question_target=self.register_target('project',self.legacy_source,'Alice',self.question['operation']['text'])
        self.reaction_targets[self.question_target]=dict(thread='project',mode='protected',reference=self.ref)
        self.touch('project',self.question['operation']['text'])
        self.seed_thread('maya','maya@example.invalid','Lunch tomorrow?','Would noon work for lunch tomorrow?')
        self.seed_thread('sam','sam@example.invalid','Weekend plans','The trail is open again. Shall we go Saturday?')
        self.seed_thread('other','delivery@example.invalid','Delivery update','Your synthetic demo delivery is scheduled for tomorrow.')

    def register_target(self,thread_id,raw,sender,text,parent=None):
        parsed=BytesParser(policy=policy.default).parsebytes(raw)
        ids=parsed.get_all('Message-ID',[])
        if len(ids)!=1:raise ValueError('Received target lacks unique Message-ID')
        if parent is None:
            parents=[k for k,v in self.reply_targets.items() if v['thread']==thread_id and v['messageId']==str(parsed.get('In-Reply-To',''))]
            parent=parents[0] if len(parents)==1 else None
        if parent is not None and (parent not in self.reply_targets or self.reply_targets[parent]['thread']!=thread_id):raise ValueError('Reply navigation parent')
        target=secrets.token_hex(24)
        self.reply_targets[target]=dict(thread=thread_id,messageId=str(ids[0]),references=str(parsed.get('References','')),sender=sender,text=text,parent=parent)
        self.thread_targets.setdefault(thread_id,[]).append(target)
        self.reaction_targets[target]=dict(thread=thread_id,mode='ordinary',messageId=str(ids[0]),token=secrets.token_hex(24))
        return target
    def targets(self,thread_id):
        return [dict(id=id,sender=self.reply_targets[id]['sender'],text=self.reply_targets[id]['text'],parent=self.reply_targets[id]['parent']) for id in self.thread_targets.get(thread_id,[])]
    def person(self,address):
        return dict(name=self.contacts.get(address,address),address=address,contact=address in self.contacts)
    def thread(self,id):
        if not isinstance(id,str) or id not in self.threads:raise ValueError('Unknown conversation')
        return self.threads[id]
    def touch(self,id,text):
        self.activity+=1;self.threads[id]['activity']=self.activity;self.threads[id]['preview']=text
    def summaries(self):
        return [{k:t[k] for k in ('id','title','preview','contact','activity')} for t in sorted(self.threads.values(),key=lambda t:t['activity'],reverse=True)]
    def seed_thread(self,id,address,subject,text):
        from smtp_loopback import roundtrip
        m=EmailMessage(policy=policy.SMTP);m['From']=address;m['To']='carol@example.invalid';m['Subject']=subject;m['Message-ID']='<'+secrets.token_hex(16)+'@example.invalid>';m.set_content(text,charset='utf-8')
        raw=roundtrip(m.as_bytes());parsed=BytesParser(policy=policy.default).parsebytes(raw);source=secrets.token_hex(16);self.reply_originals[source]=raw
        participants=[self.person(address),self.person('carol@example.invalid')]
        self.threads[id]=dict(id=id,title=self.contacts.get(address,subject),participants=participants,contact=all(p['contact'] for p in participants),timeline=[dict(kind='ordinary',text=parsed.get_content(),id=source,parent='',sender=participants[0]['name'],address=address,protected=False)],legacyQuestion=dict(id=str(parsed['Message-ID']),text=parsed.get_content()),preview='',activity=0,subject=subject)
        self.threads[id]['timeline'][0]['replyTarget']=self.register_target(id,raw,participants[0]['name'],parsed.get_content())
        self.touch(id,parsed.get_content())

    def add_rich(self):
        import hashlib,io
        from PIL import Image
        from mls_mime import unpack
        f=self.fixture;resource='d'*32;stream=io.BytesIO();Image.new('RGB',(2,2),'blue').save(stream,format='PNG');data=stream.getvalue()
        event=f.event(0,'9',dict(kind='rich-message',text='Project update Blue project diagram',html='<!doctype html><html><head><meta charset="utf-8"></head><body><h2>Project update</h2><img alt="Blue project diagram" src="cid:'+resource+'.'+'9'*32+'@resources.email-next.invalid"></body></html>',presentation='html-css-v0',replyTo=[],manifest=[dict(id=resource,size=str(len(data)),sha256=hashlib.sha256(data).hexdigest())],embedded=[dict(resource=resource,mediaType='image/png')],attachments=[]))
        f.senders[0].prepare(event['event'],json.dumps(event).encode(),key=f.devices[0]['key'],envelope_sender='alice@example.invalid',recipients=['bob@example.invalid'],time=f.time,resources={resource:data})
        def receive(wire):
            f.receive(1,wire);token=secrets.token_hex(32);self.rich_selections[token]=({k:event[k] for k in ('principal','conversation','event')},hashlib.sha256(unpack(wire)).hexdigest());self.rich_messages.append(dict(text=event['operation']['text'],selection=token))
        self.transport(0,event['event'],receive)
    def rich(self,value):
        from received_rich import render
        from rich_presentation import configuration
        if not isinstance(value,dict) or set(value)!={'selection'} or not isinstance(value['selection'],str) or value['selection'] not in self.rich_selections:raise ValueError('Unknown rich selection')
        selected=self.rich_selections[value['selection']];reference,carrier=selected[:2]
        receiver=selected[2] if len(selected)==3 else self.fixture.senders[1].receiver
        return dict(presentation=render(receiver,reference,carrier=carrier),configuration={**configuration(),'sandboxNonce':self.sandbox_nonce})

    def add_attachments(self):
        import hashlib,base64
        from provider_mls import call
        from mls_mime import package,unpack
        from received_attachments import view
        f=self.fixture;resource='c'*32;data=b'From: nested@example.invalid\r\n\r\nOpaque attachment bytes.'
        for index in range(2):
            event=f.event(0,str(index+7),dict(kind='attachment-message',text='Attached source',replyTo=[],
                manifest=[dict(id=resource,size=str(len(data)),sha256=hashlib.sha256(data).hexdigest())],
                attachments=[dict(resource=resource,name='<img src=x onerror=alert(1)>\r\nX-Evil: yes.eml',mediaType='message/rfc822',description='Opaque file; download deliberately')]))
            f.senders[0].prepare(event['event'],json.dumps(event).encode(),key=f.devices[0]['key'],envelope_sender='alice@example.invalid',recipients=['bob@example.invalid'],time=f.time,resources={resource:data})
            entity=f.identities[0].db.execute('SELECT payload FROM sender_payloads WHERE delivery=?',(event['event'],)).fetchone()[0]
            root=BytesParser(policy=policy.SMTP).parsebytes(entity)
            root.get_payload()[1].set_param('filename','different-name.bin',header='Content-Disposition')
            if index:root.get_payload()[1].set_payload(base64.b64encode(b'x'*len(data)).decode())
            db=f.identities[0].db;checkpoint=json.loads(db.execute('SELECT snapshot FROM mls_checkpoint').fetchone()[0])
            sent=call(f.binary,op='send',checkpoint=checkpoint,key=f.devices[0]['key'],group=f.group,application=root.as_bytes().hex())
            db.execute('UPDATE mls_checkpoint SET revision=revision+1,snapshot=?',(json.dumps(sent['checkpoint']).encode(),))
            from smtp_loopback import roundtrip
            wire=roundtrip(package(bytes.fromhex(sent['wire'])));f.receive(1,wire)
            reference={k:event[k] for k in ('principal','conversation','event')};shown=view(f.senders[1].receiver,reference)['attachments'][0]
            token=secrets.token_hex(32) if shown['state']=='available' else None
            if token:self.downloads[token]=(reference,resource,hashlib.sha256(unpack(wire)).hexdigest())
            mismatch=any(m['state']=='mismatch' for d in shown['diagnostics'] for m in d['metadata'])
            integrity=sorted({r['state'] for d in shown['diagnostics'] for r in d['resources']})
            reaction_target=secrets.token_hex(24);self.reaction_targets[reaction_target]=dict(thread='project',mode='protected',reference=reference)
            self.attachments.append(dict(reactionTarget=reaction_target,name=shown['description']['name'],description=shown['description']['description'],state=shown['state'],integrity=', '.join(integrity),metadata='MIME filename differs from authenticated description' if mismatch else 'MIME metadata matches',selection=token))

    def download(self,value):
        from received_attachments import read
        if not isinstance(value,dict) or set(value)!={'selection'} or not isinstance(value['selection'],str) or value['selection'] not in self.downloads:raise ValueError('Unknown download selection')
        reference,resource,carrier=self.downloads[value['selection']]
        return read(self.fixture.senders[1].receiver,reference,resource,carrier=carrier)

    def transport(self,who,delivery,receive,plain=False):
        smtp=LocalSMTP()
        with SenderWorker(self.fixture.senders[who]) as worker:
            (worker.submit_plaintext if plain else worker.submit)(delivery,port=smtp.port,time=self.fixture.time)
        smtp.done();receive(smtp.wire);return smtp.wire
    def state(self,thread_id='project'):
        selected=self.thread(thread_id)
        meta={k:selected[k] for k in ('id','title','participants','contact')}
        if thread_id!='project':
            return dict(reactionTargets=self.reaction_controls(thread_id),senderAccounts=list(self.sender_accounts.values()),questionReplyTarget=None,replyTargets=self.targets(thread_id),selectedThread=meta,threads=self.summaries(),timeline=[{**r,'reactionTarget':r.get('replyTarget')} for r in selected['timeline']],legacyQuestion=selected['legacyQuestion'],nonce=self.nonce,question=None,answers=[],attachments=[],richMessages=[],legacyReply=None,reactions=0,ownReactions=0,reactionGroups=[])
        f=self.fixture;view=derive_button_view(f.senders[1].receiver.journal,self.ref)
        answers=[]
        for row in f.senders[0].receiver.journal.snapshot(self.ref['conversation']):
            if row['state']!='recorded':continue
            event=json.loads(row['octets'][0])
            if event['operation']['kind']=='answer':answers.append(next(o['label'] for o in self.question['operation']['options'] if o['id']==event['operation']['option']))
        reactions=derive_reaction_view(f.senders[0].receiver.journal,self.ref);local=derive_reaction_view(f.senders[1].receiver.journal,self.ref)
        from client_reactions import active_events
        grouped={}
        for ref,emoji in active_events(f.senders[0].receiver.journal,self.ref,reactions):grouped.setdefault(emoji,set()).add(ref['principal'])
        reaction_groups=[dict(emoji=e,count=len(authors),mine=f.principals[1] in authors) for e,authors in sorted(grouped.items())]
        return dict(reactionTargets=self.reaction_controls(thread_id),senderAccounts=list(self.sender_accounts.values()),replyTargets=self.targets(thread_id),questionReplyTarget=self.question_target,reactionGroups=reaction_groups,selectedThread=meta,threads=self.summaries(),legacyQuestion=self.legacy_question,timeline=[{**r,'reactionTarget':r.get('replyTarget'),'sender':r.get('sender','Bob' if r['kind']=='answer' else 'Carol'),'protected':r['kind']!='ordinary'} for r in self.timeline],richMessages=self.rich_messages,attachments=self.attachments,question=self.question['operation'],token=view['sourceToken'],answers=answers,legacyReply=self.legacy_reply,nonce=self.nonce,reactions=len(reactions['active']),reactionToken=local['sourceToken'],ownReactions=len([r for r in local['active'] if r['principal']==f.principals[1]]))
    def answer(self,value):
        if set(value)!={'action','option','token'}:raise ValueError('Action shape')
        f=self.fixture;client=ClientFlow(f.senders[1],key=f.devices[1]['key'],envelope_sender='bob@example.invalid',recipients=['alice@example.invalid'])
        self.answer_wire=client.answer(value['action'],self.ref,value['option'],value['token'],time=f.time)
        # A completed action remains readable on HTTP retry without resubmitting SMTP.
        SenderWorker(f.senders[1])  # Initialize durable attempt schema before lookup.
        prior=f.identities[1].db.execute("SELECT 1 FROM sender_attempts WHERE delivery=? AND kind='application-v0' AND state='accepted'",(value['action'],)).fetchone()
        if not prior:
            received=self.transport(1,value['action'],lambda wire:f.receive(0,wire))
            label=next(o['label'] for o in self.question['operation']['options'] if o['id']==value['option'])
            target=self.register_target('project',received,'Bob',label,parent=self.question_target)
            event=json.loads(f.identities[1].db.execute('SELECT event FROM client_actions WHERE id=?',(value['action'],)).fetchone()[0]);self.reaction_targets[target]=dict(thread='project',mode='protected',reference={k:event[k] for k in ('principal','conversation','event')})
            self.timeline.append(dict(kind='answer',text=label,sender='Bob',protected=True,replyTarget=target));self.touch('project',label)
    def reaction_controls(self,thread_id):
        from client_reactions import active_events
        controls=[];f=self.fixture
        for target,record in self.reaction_targets.items():
            if record['thread']!=thread_id:continue
            grouped={}
            if record['mode']=='unavailable':
                controls.append(dict(target=target,mode='unavailable',token='',canWithdraw=False,groups=[]));continue
            if record['mode']=='protected':
                ref=record['reference'];view=derive_reaction_view(f.senders[1].receiver.journal,ref)
                for r,e in active_events(f.senders[1].receiver.journal,ref,view):grouped.setdefault(e,set()).add(r['principal'])
                mine=f.principals[1];token=view['sourceToken']
            else:
                for row in self.ordinary_reactions.get(target,[]):grouped.setdefault(row['emoji'],set()).add(row['address'])
                mine={a['address'] for a in self.sender_accounts.values()};token=record['token']
            controls.append(dict(target=target,mode=record['mode'],token=token,canWithdraw=record['mode']=='protected',groups=[dict(emoji=e,count=len(authors),mine=bool(authors & mine) if isinstance(mine,set) else mine in authors) for e,authors in sorted(grouped.items())]))
        return controls
    def react(self,value,withdraw=False,thread_id='project'):
        if not isinstance(value,dict) or set(value)-{'action','token','emoji','target','account'} or not {'action','token'}<=set(value):raise ValueError('Action shape')
        emoji=value.get('emoji',None if withdraw else '👍')
        from client_reactions import EMOJI
        if (not withdraw and emoji is None) or (emoji is not None and (not isinstance(emoji,str) or emoji not in EMOJI)):raise ValueError('Reaction emoji')
        target=value.get('target',self.question_target)
        if not isinstance(target,str) or target not in self.reaction_targets or self.reaction_targets[target]['thread']!=thread_id:raise ValueError('Reaction target')
        record=self.reaction_targets[target]
        if record['mode']=='unavailable':raise ValueError('Protected reaction target unsupported')
        if record['mode']=='ordinary':
            account_id=value.get('account','personal')
            if not isinstance(account_id,str):raise ValueError('Sending account unavailable')
            account=self.sender_accounts.get(account_id)
            if not account or not account['enabled']:raise ValueError('Sending account unavailable')
            if withdraw:raise ValueError('Ordinary reaction withdrawal unsupported')
            if not isinstance(value['action'],str) or not value['action'].isalnum() or len(value['action'])>128:raise ValueError('Action ID')
            request=json.dumps(value,sort_keys=True);old=self.ordinary_reaction_actions.get(value['action'])
            if old:
                if old['request']!=request:raise ValueError('Action ID conflict')
                return
            if value['token']!=record['token']:raise ValueError('Changed reaction snapshot')
            from smtp_loopback import roundtrip
            message=EmailMessage(policy=policy.SMTP);message['From']=account['address'];message['To']=', '.join(p['address'] for p in self.thread(thread_id)['participants'] if p['address']!='carol@example.invalid');message['Subject']='Reaction';message['Message-ID']='<'+secrets.token_hex(16)+'@example.invalid>';message['In-Reply-To']=record['messageId'];message.set_content(emoji,charset='utf-8');message['Content-Disposition']='reaction'
            raw=roundtrip(message.as_bytes());parsed=BytesParser(policy=policy.default).parsebytes(raw)
            if parsed.get_content_disposition()!='reaction' or str(parsed['In-Reply-To'])!=record['messageId']:raise ValueError('Reaction delivery mismatch')
            source=secrets.token_hex(16);self.reply_originals[source]=raw
            self.ordinary_reaction_actions[value['action']]=dict(request=request,source=source)
            self.ordinary_reactions.setdefault(target,[]).append(dict(emoji=emoji,address=account['address'],source=source));record['token']=secrets.token_hex(24);self.touch(thread_id,'Reacted '+emoji);return
        if 'account' in value:raise ValueError('Ordinary account does not authorize protected reaction')
        f=self.fixture;client=ClientFlow(f.senders[1],key=f.devices[1]['key'],envelope_sender='bob@example.invalid',recipients=['alice@example.invalid']);ref=record['reference']
        if withdraw:client.withdraw_reactions(value['action'],ref,value['token'],time=f.time,emoji=emoji)
        else:client.react(value['action'],ref,emoji,value['token'],time=f.time)
        SenderWorker(f.senders[1])
        prior=f.identities[1].db.execute("SELECT 1 FROM sender_attempts WHERE delivery=? AND kind='application-v0' AND state='accepted'",(value['action'],)).fetchone()
        if not prior:self.transport(1,value['action'],lambda wire:f.receive(0,wire));self.touch('project','Reaction removed' if withdraw else 'Reacted '+emoji)
    def reply(self,value,thread_id='project'):
        selected=self.thread(thread_id)
        if not isinstance(value,dict) or set(value)-{'text','replyTo','subject','account'} or 'text' not in value or not isinstance(value['text'],str) or not value['text'].strip() or len(value['text'])>4096:raise ValueError('Reply text')
        account_id=value.get('account','personal')
        if not isinstance(account_id,str) or account_id not in self.sender_accounts or not self.sender_accounts[account_id]['enabled']:raise ValueError('Sending account unavailable')
        account=self.sender_accounts[account_id]
        own_addresses={a['address'] for a in self.sender_accounts.values()}
        new='replyTo' in value and value['replyTo'] is None
        parent=None
        if new:
            subject=value.get('subject')
            if not isinstance(subject,str) or not subject.strip() or len(subject)>200 or any(c in subject for c in '\r\n'):raise ValueError('New conversation subject')
        else:
            if 'subject' in value:raise ValueError('Subject only for new conversation')
            ids=self.thread_targets.get(thread_id,[])
            target=value.get('replyTo',ids[-1] if ids else None)
            if not isinstance(target,str) or target not in self.reply_targets or self.reply_targets[target]['thread']!=thread_id:raise ValueError('Unknown reply target')
            parent=self.reply_targets[target];subject='Re: '+selected.get('subject','Question')
        message=EmailMessage(policy=policy.SMTP);message['From']=account['address']
        recipients=[p['address'] for p in selected['participants'] if p['address'] not in own_addresses]
        message['To']=', '.join(recipients);message['Subject']=subject;message['Message-ID']='<'+secrets.token_hex(16)+'@example.invalid>'
        if parent:
            message['In-Reply-To']=parent['messageId'];message['References']=' '.join(x for x in (parent['references'],parent['messageId']) if x)
        message.set_content(value['text'],charset='utf-8')
        from smtp_loopback import roundtrip
        raw=roundtrip(message.as_bytes());parsed=BytesParser(policy=policy.default).parsebytes(raw)
        if new:
            thread_id=secrets.token_hex(16)
            title=', '.join(p['name'] for p in selected['participants'] if p['address'] not in own_addresses)
            selected=dict(id=thread_id,title=title,participants=list(selected['participants']),contact=all(p['contact'] for p in selected['participants']),timeline=[],legacyQuestion=dict(id=str(parsed['Message-ID']),text=parsed.get_content()),preview='',activity=0,subject=subject)
            self.threads[thread_id]=selected
        source=secrets.token_hex(16);self.reply_originals[source]=raw
        reply_target=self.register_target(thread_id,raw,'Carol',parsed.get_content())
        selected['timeline'].append(dict(kind='ordinary',text=parsed.get_content(),id=source,parent=str(parsed.get('In-Reply-To','')),parentText=parent['text'] if parent else None,sender='Carol',address=account['address'],protected=False,replyTarget=reply_target))
        if thread_id=='project':self.legacy_reply=parsed.get_content();self.reply_source=raw
        self.touch(thread_id,parsed.get_content())
        return thread_id
    def close(self):
        if self.signed_rich_fixture:self.signed_rich_fixture.tearDown()
        self.fixture.tearDown()


def serve(port=0, *, mime=False, rich=False, signed_rich=False):
    demo=Demo(mime=mime or rich,rich=rich,signed_rich=signed_rich)
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup();self.connection.settimeout(5)
        def log_message(self,*args):pass
        def valid_host(self):
            return self.headers.get_all('Host',[])==[f'127.0.0.1:{self.server.server_port}']
        def send(self,status,body,media,download=False):
            self.send_response(status)
            if download:self.send_header('Content-Disposition','attachment; filename=attachment.bin')
            self.send_header('Content-Type',media);self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Security-Policy',f"default-src 'self'; script-src 'self' 'nonce-{demo.sandbox_nonce}'; style-src 'self' 'nonce-{demo.sandbox_nonce}'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'");self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def do_GET(self):
            if not self.valid_host():return self.send(403,b'Local host required','text/plain')
            route=urlsplit(self.path)
            if route.path=='/state':
                try:
                    query=parse_qs(route.query,keep_blank_values=True)
                    if set(query)-{'thread'} or len(query.get('thread',['project']))!=1:raise ValueError('Thread selection')
                    return self.send(200,json.dumps(demo.state(query.get('thread',['project'])[0])).encode(),'application/json')
                except ValueError:return self.send(404,b'Unknown conversation','text/plain')
            if self.path=='/legacy.eml':return self.send(200,demo.legacy_source,'message/rfc822')
            if self.path.startswith('/original/') and self.path.endswith('.eml'):
                raw=demo.reply_originals.get(self.path[len('/original/'):-4])
                return self.send(200,raw,'message/rfc822') if raw is not None else self.send(404,b'Not found','text/plain')
            files={**{('/'+n):n for n in ('browser-render-host.mjs','browser-render-runtime.mjs','navigation-url.mjs','legacy-quotes.mjs')},'/':'client-flow.html','/client-flow.mjs':'client-flow.mjs','/client-flow.css':'client-flow.css'}
            if self.path not in files:return self.send(404,b'Not found','text/plain')
            name=files[self.path];self.send(200,Path(__file__).with_name(name).read_bytes(),{'html':'text/html; charset=utf-8','mjs':'text/javascript; charset=utf-8','css':'text/css; charset=utf-8'}[name.rsplit('.',1)[1]])
        def do_POST(self):
            if not self.valid_host():return self.send(403,b'Local host required','text/plain')
            expected=f'http://127.0.0.1:{self.server.server_port}'
            if self.headers.get('Origin')!=expected or self.headers.get('X-Client-Session')!=demo.nonce:return self.send(403,b'Local session required','text/plain')
            try:
                if self.headers.get('Content-Type')!='application/json' or self.headers.get('Transfer-Encoding') or len(self.headers.get_all('Content-Length',[]))!=1:raise ValueError('Request framing')
                length=int(self.headers['Content-Length'])
                if not 0<length<=16384:raise ValueError('Request bound')
                value=json.loads(self.rfile.read(length))
                ids=self.headers.get_all('X-Conversation-ID',[])
                if len(ids)>1:raise ValueError('Conversation header')
                thread_id=ids[0] if ids else 'project';demo.thread(thread_id)
                if thread_id!='project' and self.path not in ('/reply','/react','/withdraw'):raise ValueError('Ordinary conversation only supports replies')
                if self.path=='/rich':return self.send(200,json.dumps(demo.rich(value)).encode(),'application/json')
                if self.path=='/download':return self.send(200,demo.download(value),'application/octet-stream',download=True)
                if self.path=='/answer':demo.answer(value)
                elif self.path=='/reply':thread_id=demo.reply(value,thread_id)
                elif self.path=='/react':demo.react(value,thread_id=thread_id)
                elif self.path=='/withdraw':demo.react(value,withdraw=True,thread_id=thread_id)
                else:return self.send(404,b'Not found','text/plain')
                self.send(200,json.dumps(demo.state(thread_id)).encode(),'application/json')
            except (ValueError,KeyError,TypeError):self.send(409,b'Action held. Refresh the conversation before retrying.','text/plain')
    server=HTTPServer(('127.0.0.1',port),Handler)
    return server,demo

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=0);parser.add_argument('--mime',action='store_true');parser.add_argument('--rich',action='store_true');parser.add_argument('--signed-rich',action='store_true');args=parser.parse_args()
    import signal
    def stop(signum,frame):raise SystemExit(0)
    signal.signal(signal.SIGTERM,stop)
    server,demo=serve(args.port,mime=args.mime,rich=args.rich,signed_rich=args.signed_rich);print(f'http://127.0.0.1:{server.server_port}',flush=True)
    try:server.serve_forever()
    finally:server.server_close();demo.close()
