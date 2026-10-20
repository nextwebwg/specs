"""Transactional successor experiment. Freshness and MLS effects are not implemented."""
import base64
import json
import hashlib
import re
from event_encoding import decode_event
from genesis_store import GenesisStore
from identity_bundle import decode_identity_bundle,verify_successor_bundle

class IdentityStore(GenesisStore):
    def __init__(self,path):
        super().__init__(path)
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS identity_heads (
            principal TEXT PRIMARY KEY,digest TEXT NOT NULL,conflicted INTEGER NOT NULL DEFAULT 0);
          CREATE TABLE IF NOT EXISTS identity_transitions (
            principal TEXT NOT NULL,digest TEXT NOT NULL,previous TEXT NOT NULL,
            record_id TEXT NOT NULL,accepted INTEGER NOT NULL,bundle BLOB NOT NULL,
            PRIMARY KEY(principal,digest));
        ''')

    def accept_successor(self,octets,*,candidate_digest,time):
        decoded=decode_identity_bundle(octets)
        candidate=next((s for s in decoded['states'] if s['digest']==candidate_digest),None)
        if candidate is None:return {'status':'pending','reason':'state'}
        principal=decoded['principal']
        self.db.execute('BEGIN IMMEDIATE')
        try:
            result=self._accept_locked(octets,principal,candidate,time)
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise
        return result

    def _accept_locked(self,octets,principal,candidate,time):
        pin=self.db.execute('SELECT digest FROM pins WHERE principal=?',(principal,)).fetchone()
        if not pin:return {'status':'pending','reason':'accepted-genesis'}
        self.db.execute('INSERT OR IGNORE INTO identity_heads(principal,digest) VALUES(?,?)',(principal,pin[0]))
        head,conflicted=self.db.execute('SELECT digest,conflicted FROM identity_heads WHERE principal=?',(principal,)).fetchone()
        if conflicted:return {'status':'conflicted','head':head}
        digest=candidate['digest']
        known=self.db.execute('SELECT accepted FROM identity_transitions WHERE principal=? AND digest=?',(principal,digest)).fetchone()
        if known:return {'status':'already-recorded','head':head}
        previous=candidate['value'].get('previous')
        if not isinstance(previous,list) or len(previous)!=1 or not isinstance(previous[0],str):
            return {'status':'invalid','reason':'predecessor'}
        previous=previous[0]
        trusted=previous==pin[0] or self.db.execute('SELECT 1 FROM identity_transitions WHERE principal=? AND digest=? AND accepted=1',(principal,previous)).fetchone()
        if not trusted:return {'status':'pending','reason':'accepted-predecessor'}
        # Validation runs inside the write transaction in this bounded experiment.
        # This avoids a head change between the trusted-anchor lookup and installation.
        checked=verify_successor_bundle(octets,accepted_digest=previous,candidate_digest=digest,time=time)
        if checked['status']!='transition-valid-uncommitted':return checked
        record_id=candidate['value']['record']
        root_record=json.loads(self.db.execute('SELECT record FROM claims WHERE principal=? AND digest=?',(principal,pin[0])).fetchone()[0])
        root_id=json.loads(base64.b64decode(root_record['state']))['record']
        collision=record_id==root_id or self.db.execute('SELECT 1 FROM identity_transitions WHERE principal=? AND record_id=?',(principal,record_id)).fetchone()
        conflict=previous!=head or bool(collision)
        self.db.execute('INSERT INTO identity_transitions VALUES(?,?,?,?,?,?)',(principal,digest,previous,record_id,int(not conflict),octets))
        if conflict:
            self.db.execute('UPDATE identity_heads SET conflicted=1 WHERE principal=?',(principal,))
            return {'status':'conflicted','head':head}
        self.db.execute('UPDATE identity_heads SET digest=? WHERE principal=?',(digest,principal))
        return {'status':'accepted-unverified','head':digest}

    def current_state(self,principal):
        row=self.db.execute('SELECT digest,conflicted FROM identity_heads WHERE principal=?',(principal,)).fetchone()
        if row:return {'head':row[0],'conflicted':bool(row[1])}
        pin=self.db.execute('SELECT digest FROM pins WHERE principal=?',(principal,)).fetchone()
        return {'head':pin[0] if pin else None,'conflicted':False}


    def check_device(self, credential, signing_key, *, role, time, trust_policy):
        """Snapshot authorization only; caller must serialize release with later changes."""
        if role not in ('send','receive') or trust_policy not in ('allow-unverified','require-verification'):
            raise ValueError('Explicit operation and trust policy required')
        if not isinstance(credential,bytes) or len(credential)!=85 or credential[:21]!=b'email-next/device/v0\0' or not isinstance(signing_key,bytes) or len(signing_key)!=32:
            return {'status':'invalid','reason':'credential'}
        principal='enp0:'+credential[21:53].hex()
        device='end0:'+credential[53:].hex()
        if principal=='enp0:'+'0'*64 or device=='end0:'+'0'*64:
            return {'status':'invalid','reason':'credential'}
        self.db.execute('BEGIN')
        try:
            result=self._check_device_locked(principal,device,signing_key,role,time,trust_policy)
            self.db.execute('COMMIT')
            return result
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def _check_device_locked(self,principal,device,signing_key,role,time,trust_policy):
        current=self.current_state(principal)
        head=current['head']
        if not head:return {'status':'pending','reason':'accepted-identity'}
        if current['conflicted']:return {'status':'conflicted','head':head}
        if trust_policy=='require-verification':return {'status':'verification-required','head':head}
        transition=self.db.execute('SELECT bundle FROM identity_transitions WHERE principal=? AND digest=? AND accepted=1',(principal,head)).fetchone()
        if transition:
            bundle=decode_identity_bundle(transition[0])
            state=next(s['value'] for s in bundle['states'] if s['digest']==head)
            bindings={b['digest']:b['value'] for b in bundle['bindings']}
        else:
            row=self.db.execute('SELECT record FROM claims WHERE principal=? AND digest=?',(principal,head)).fetchone()
            if not row:return {'status':'pending','reason':'stored-state','head':head}
            record=json.loads(row[0])
            state=decode_event(base64.b64decode(record['state'],validate=True))['value']
            raw=base64.b64decode(record['binding'],validate=True)
            bindings={hashlib.sha256(raw).hexdigest():decode_event(raw)['value']}
        if device in state['revoked']:return {'status':'unauthorized','reason':'revoked','head':head}
        selected=next((b for b in state['bindings'] if b['device']==device),None)
        if not selected:return {'status':'unauthorized','reason':'device-not-current','head':head}
        binding=bindings.get(selected['digest'])
        if binding is None:return {'status':'pending','reason':'stored-binding','head':head}
        if binding['signingKey']!=signing_key.hex():return {'status':'unauthorized','reason':'signing-key','head':head}
        if role not in binding['roles']:return {'status':'unauthorized','reason':'role','head':head}
        def u64(value):return isinstance(value,str) and re.fullmatch(r'(0|[1-9][0-9]{0,19})',value) and int(value)<2**64
        if not isinstance(time,dict) or not u64(time.get('earliest')) or not u64(time.get('latest')) or int(time['earliest'])>int(time['latest']):
            return {'status':'pending','reason':'time','head':head}
        earliest,latest=int(time['earliest']),int(time['latest'])
        before,after=int(binding['notBefore']),int(binding['notAfter'])
        if earliest>after or latest<before:return {'status':'not-current','reason':'binding-validity','head':head}
        if earliest<before or latest>after:return {'status':'pending','reason':'binding-validity','head':head}
        return {'status':'authorized-unverified','head':head,'binding':selected['digest'],'role':role}
