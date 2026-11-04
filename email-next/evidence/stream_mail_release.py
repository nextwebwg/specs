"""Configured source-to-loopback-mail release; no current-suite transport claim.

All routes come from this source's original independently selected signed roster.
No arbitrary recipient, external SMTP host or remote checkpoint input is exposed.
"""
import hashlib
import json
import time as elapsed_time
from email import policy
from email.parser import BytesParser

from event_encoding import decode_event
from initial_roster import credential, identifier, parse
from initial_roster_lifecycle import canonical
from invitation_mime import select
from mls_mime import package, MAX_WIRE
from passive_discovery import decode_passive_discovery
from sender_association import check_locked
from sender_stream_source import SenderStreamSource, later

KIND = 'configured-stream-submit-v0'


class StreamMailRelease:
    def __init__(self, sender, source):
        if type(source) is not SenderStreamSource or source.identity is not sender.identity or source.db.in_transaction:
            raise ValueError('Shared configured source and sender required')
        self.sender=sender;self.source=source;self.db=source.db
        self.started=None;self.interval=None
        self.db.execute('''CREATE TABLE IF NOT EXISTS stream_mail_prepared(id TEXT PRIMARY KEY,stream TEXT NOT NULL,source_id TEXT NOT NULL,form TEXT NOT NULL,request BLOB NOT NULL,wire BLOB NOT NULL,metadata TEXT NOT NULL,dependencies TEXT NOT NULL,policy_revision INTEGER NOT NULL,envelope TEXT NOT NULL,associations TEXT NOT NULL,evidence TEXT NOT NULL,UNIQUE(stream,source_id,form))''')

    def start_attempt(self, interval):
        from admission_windows import clock
        self.interval=dict(interval);clock(self.interval)
        self.started=elapsed_time.monotonic_ns()

    def effective_time(self):
        if self.started is None:raise ValueError('Attempt clock not started')
        return later(self.interval,self.started)

    def checkpoint_locked(self, delivery):
        if not self.db.in_transaction:raise ValueError('Release transaction required')
        row=self.db.execute('SELECT stream FROM stream_mail_prepared WHERE id=?',(delivery,)).fetchone()
        if row is None:raise ValueError('Unknown stream delivery')
        binding, checkpoint=self.source._live(row[0])
        return binding['group'],canonical(checkpoint)

    def authority_locked(self, metadata, interval, trust):
        if not self.db.in_transaction or trust!='allow-unverified':raise ValueError('Configured authority required')
        binding_row=self.db.execute('SELECT binding FROM stream_source WHERE group_id=?',(metadata['group'],)).fetchone()
        if binding_row is None:raise ValueError('Unknown source authority')
        binding=json.loads(binding_row[0])
        self.source._live(binding['stream'])
        return self.source._current(metadata,binding['owner'],self.effective_time())

    def _routes(self, binding, metadata):
        row=self.db.execute('SELECT request FROM initial_rosters WHERE creation=?',(binding['stream'],)).fetchone()
        if row is None:raise ValueError('Original selected routes required')
        routes={}
        for selected in json.loads(row[0])['selected']:
            decoded=decode_passive_discovery(bytes.fromhex(selected['wrapper']))
            assertion=decoded['assertion'];v=assertion['value'];ident=credential(v)
            if selected['digest']!=assertion['digest'] or selected['mailbox']!=v['mailbox'] or ident in routes:
                raise ValueError('Original route assertion binding')
            routes[ident]=dict(mailbox=selected['mailbox'],generation=selected['generation'],principal=v['principal'],observation=selected['digest'])
        if set(routes)!={m['identity'] for m in metadata['members']}:raise ValueError('Complete original route coverage required')
        own=routes.pop(credential(binding['owner']))
        peers={}
        for ident,target in sorted(routes.items()):
            old=peers.get(target['mailbox'])
            if old and any(old[k]!=target[k] for k in ('principal','generation')):raise ValueError('Conflicting shared mailbox routes')
            peers.setdefault(target['mailbox'],target)
        return own,peers,routes

    def _material(self, stream, source_id, form, binding, metadata, interval):
        own,peers,per_device=self._routes(binding,metadata)
        if form=='initial':
            row=self.db.execute('SELECT wire,target FROM initial_roster_prepared WHERE id=? AND creation=?',(source_id,stream)).fetchone()
            if row is None or row[1] not in per_device:raise ValueError('Exact original invitation required')
            wire=row[0];p=parse(select(wire))
            if p['anchor']!=binding['anchor'] or p['group'].hex()!=binding['group']:raise ValueError('Invitation source binding')
            from admission_windows import clock
            lo,hi=clock(interval)
            if not int(p['value']['notBefore'])<=lo<=hi<=int(p['value']['notAfter']):raise ValueError('Original invitation validity')
            if self.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='sender_attempts'").fetchone() and self.db.execute('SELECT 1 FROM sender_attempts WHERE delivery=? AND kind=?',(source_id,'initial-roster-invitation-v3')).fetchone():raise ValueError('Original invitation already attempted through another adapter')
            targets=[per_device[row[1]]]
            mail=BytesParser(policy=policy.SMTP).parsebytes(wire)
            if str(mail['From'])!=own['mailbox'] or str(mail['To'])!=targets[0]['mailbox']:raise ValueError('Original invitation route mismatch')
            window=[p['value']['notBefore'],p['value']['notAfter']]
            digest=hashlib.sha256(wire).hexdigest()
        elif form=='source':
            row=self.db.execute('SELECT wire,kind FROM stream_source_outbox WHERE stream=? AND id=?',(stream,source_id)).fetchone()
            if row is None or row[1] not in ('root-message','owner-self-update'):raise ValueError('Exact prepared source output required')
            digest=hashlib.sha256(row[0]).hexdigest()
            targets=[peers[name] for name in sorted(peers)]
            window=[]
            # The fixture carrier is deliberately opaque, not the current MIME suite.
            mail=BytesParser(policy=policy.SMTP).parsebytes(package(row[0]))
            mail.replace_header('From',own['mailbox']);mail.replace_header('To',', '.join(t['mailbox'] for t in targets))
            mail['Message-ID']='<'+source_id+'@stream.example.invalid>'
            wire=mail.as_bytes()
        else:raise ValueError('Exact configured mail form required')
        if not targets or len(wire)>MAX_WIRE:raise ValueError('Configured transport bound')
        return own,targets,wire,digest,window

    def _window(self, window):
        # Compare original signed bounds after proof/association work, not only
        # before parsing it. Renewed attempts never reset an invitation deadline.
        if window:
            from admission_windows import clock
            lo,hi=clock(self.effective_time())
            if not int(window[0])<=lo<=hi<=int(window[1]):raise ValueError('Original invitation validity')

    def prepare(self, delivery, stream, source_id, *, time, form='source', crash=None):
        identifier(delivery);identifier(source_id)
        self.start_attempt(time)
        request=canonical(dict(stream=stream,source=source_id,form=form))
        def work():
            old=self.db.execute('SELECT request,wire FROM stream_mail_prepared WHERE id=?',(delivery,)).fetchone()
            if old:
                if old[0]!=request:raise ValueError('Immutable stream mail conflict')
                return old[1]
            binding,checkpoint=self.source._live(stream)
            metadata=self.source._inspect(binding,checkpoint)
            settings=self.db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone()
            if settings is None:raise ValueError('Explicit sender policy required')
            deps=self.source._current(metadata,binding['owner'],self.effective_time())
            own,targets,wire,digest,window=self._material(stream,source_id,form,binding,metadata,self.effective_time())
            current=self.effective_time()
            checked=check_locked(self.sender.associations,targets,metadata,current,'allow-unverified')
            sender_check=check_locked(self.sender.associations,[own],metadata,current,'allow-unverified')
            evidence=dict(window=window,sourceDigest=digest,binding=self.source.db.execute('SELECT reference FROM stream_source WHERE stream=?',(stream,)).fetchone()[0],sender=own,senderEvidence=sender_check)
            envelope=dict(sender=own['mailbox'],recipients=[t['mailbox'] for t in targets])
            associations=dict(mode='selected-association',targets=targets,dependencies=checked)
            self.source._current(metadata,binding['owner'],self.effective_time())
            self._window(window)
            self.db.execute('INSERT INTO stream_mail_prepared VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(delivery,stream,source_id,form,request,wire,canonical(metadata).decode(),canonical(deps).decode(),settings[0],canonical(envelope).decode(),canonical(associations).decode(),canonical(evidence).decode()))
            return wire
        return self.source._transaction(work,crash)

    def validate_locked(self, delivery, interval):
        if not self.db.in_transaction:raise ValueError('Release transaction required')
        row=self.db.execute('SELECT stream,source_id,form,wire,dependencies,evidence FROM stream_mail_prepared WHERE id=?',(delivery,)).fetchone()
        if row is None:raise ValueError('Unknown stream delivery')
        binding,checkpoint=self.source._live(row[0]);metadata=self.source._inspect(binding,checkpoint)
        current=self.effective_time();deps=self.source._current(metadata,binding['owner'],current)
        if canonical(deps).decode()!=row[4]:raise ValueError('Changed source identity dependencies')
        own,targets,material,digest,window=self._material(*row[:3],binding,metadata,current)
        # MIME boundaries are retained from preparation rather than regenerated.
        # Compare its decoded exact payload and frozen routes below for source output.
        if row[2]=='initial':
            if material!=row[3]:raise ValueError('Changed original invitation bytes')
        else:
            from mls_mime import unpack
            source=self.db.execute('SELECT wire FROM stream_source_outbox WHERE stream=? AND id=?',row[:2]).fetchone()
            if source is None or unpack(row[3])!=source[0]:raise ValueError('Changed source bytes')
            mail=BytesParser(policy=policy.SMTP).parsebytes(row[3])
            if str(mail['From'])!=own['mailbox'] or str(mail['To'])!=', '.join(t['mailbox'] for t in targets):raise ValueError('Changed source mail routes')
        current=self.effective_time()
        checked=check_locked(self.sender.associations,targets,metadata,current,'allow-unverified')
        sender_check=check_locked(self.sender.associations,[own],metadata,current,'allow-unverified')
        evidence=json.loads(row[5])
        if evidence['window']!=window or evidence['sourceDigest']!=digest or evidence['sender']!=own or evidence['senderEvidence']!=sender_check or evidence['binding']!=self.db.execute('SELECT reference FROM stream_source WHERE stream=?',(row[0],)).fetchone()[0]:raise ValueError('Changed source release evidence')
        self.source._current(metadata,binding['owner'],self.effective_time())
        self._window(window)
        return dict(binding=evidence['binding'],sourceDigest=digest,sender=sender_check,recipients=checked)
