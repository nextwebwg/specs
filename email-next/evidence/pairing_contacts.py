"""Apply authenticated own-device setup to real contact and verification stores.

Only a retained, fully staged SetupTransfer can authorize this entry point. Public
peer proofs are revalidated historically under that own-device attestation; no
claim of independent signing time or fresh peer presence follows. Current device
validity, discovery, mailbox access, MLS admission and sending remain separate.
"""
import json
from identity_store import IdentityStore
from identity_bundle import decode_identity_bundle
from event_encoding import encode_event
from pairing_setup import configuration,policy,sha,b64,elapsed_interval
import pairing_setup as setup_clock
from passive_discovery import canonical_base64
from mailbox_association_store import MailboxAssociationStore
from human_verification import HumanVerification,stored_revision
from correspondence_archive import uint


def encoded(v):return json.dumps(v,sort_keys=True,separators=(',',':'))


def public_chain(ids,principal):
    """Export only the pinned genesis and the locally accepted current path."""
    current=ids.current_state(principal)
    if not current['head'] or current['conflicted']:raise ValueError('Accepted unconflicted contact required')
    pin=ids.db.execute('SELECT digest FROM pins WHERE principal=?',(principal,)).fetchone()
    if not pin:raise ValueError('Pinned contact required')
    claim=ids.db.execute('SELECT record FROM claims WHERE principal=? AND digest=?',(principal,pin[0])).fetchone()
    if not claim:raise ValueError('Retained contact anchor missing')
    record=json.loads(claim[0]);states={pin[0]:dict(payload=record['state'],signature=record['stateProof'])}
    bindings={sha(canonical_base64(record['binding'])):dict(payload=record['binding'],authorization=record['authorization'],possession=record['possession'])}
    cursor=current['head'];seen=set()
    while cursor!=pin[0]:
        if cursor in seen or len(seen)>=1024:raise ValueError('Contact ancestry processing held')
        seen.add(cursor)
        row=ids.db.execute('SELECT previous,bundle FROM identity_transitions WHERE principal=? AND digest=? AND accepted=1',(principal,cursor)).fetchone()
        if not row:raise ValueError('Accepted contact predecessor missing')
        bundle=decode_identity_bundle(row[1]);state=next(s for s in bundle['states'] if s['digest']==cursor)
        states[cursor]=dict(payload=b64(state['octets']),signature=state['signature'])
        for ref in state['value']['bindings']:
            binding=next(b for b in bundle['bindings'] if b['digest']==ref['digest'])
            bindings[ref['digest']]=dict(payload=b64(binding['octets']),authorization=binding['authorization'],possession=binding['possession'])
        cursor=row[0]
    raw=encode_event(dict(version='0',purpose='identity-bundle',principal=principal,states=[states[k] for k in sorted(states)],bindings=[bindings[k] for k in sorted(bindings)]))
    return pin[0],current['head'],raw


def validated_history(c):
    """Build a fresh verification sandbox before touching a target's live pin.

    Declared issuance times check historical proof relationships, not current
    authorization or trusted signing time. The authenticated own-device snapshot
    authorizes accepting this history; ordinary received mail cannot call this.
    """
    raw=canonical_base64(c['bundle']);bundle=decode_identity_bundle(raw)
    by_id={s['digest']:s for s in bundle['states']};cursor=c['head'];path=[];seen=set()
    while True:
        if cursor in seen or len(seen)>=1024 or cursor not in by_id:raise ValueError('Complete linear contact history required')
        seen.add(cursor);s=by_id[cursor];path.append(s)
        if cursor==c['anchor']:break
        previous=s['value'].get('previous')
        if not isinstance(previous,list) or len(previous)!=1:raise ValueError('Ordinary contact predecessor required')
        cursor=previous[0]
    if seen!=set(by_id) or path[-1]['value'].get('revision')!='0':raise ValueError('Exact pinned genesis path required')
    path.reverse();root=path[0]
    if len(root['value'].get('bindings',[]))!=1:raise ValueError('Genesis binding required')
    selected=root['value']['bindings'][0]
    binding=next(b for b in bundle['bindings'] if b['digest']==selected['digest'])
    record=dict(state=b64(root['octets']),binding=b64(binding['octets']),stateProof=root['signature'],authorization=binding['authorization'],possession=binding['possession'],time=dict.fromkeys(('earliest','latest'),root['value']['issuedAt']))
    sandbox=IdentityStore(':memory:')
    try:
        if sandbox.observe(record,first_contact_policy='allow-unverified')['status']!='pinned-unverified':raise ValueError('Invalid historical contact anchor')
        for state in path[1:]:
            result=sandbox.accept_successor(raw,candidate_digest=state['digest'],time=dict.fromkeys(('earliest','latest'),state['value']['issuedAt']))
            if result['status']!='accepted-unverified':raise ValueError('Invalid attested contact succession')
    finally:sandbox.close()
    return raw,record,path


class PairedContacts:
    def __init__(self,transfer):
        self.transfer=transfer;self.ids=transfer.ids;self.db=self.ids.db;self.account=transfer.pairing.account
        self.associations=MailboxAssociationStore(self.ids)
        # The local pairing-selected own account is already independently approved.
        self.verifier=HumanVerification(self.ids,account=self.account,local_principal=transfer.device['principal'],local_device=transfer.device['device'])
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS pairing_contact_policies(mailbox TEXT PRIMARY KEY,policy TEXT NOT NULL,origin TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS pairing_contact_origins(decision TEXT PRIMARY KEY,account TEXT NOT NULL,transfer TEXT NOT NULL,mailbox TEXT NOT NULL,source_generation TEXT NOT NULL,response TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS pairing_contact_results(account TEXT NOT NULL,transfer TEXT NOT NULL,mailbox TEXT NOT NULL,result TEXT NOT NULL,PRIMARY KEY(account,transfer,mailbox));
          CREATE TABLE IF NOT EXISTS pairing_contact_evidence_imports(account TEXT NOT NULL,transfer TEXT NOT NULL,mailbox TEXT NOT NULL,origin_device TEXT NOT NULL,origin_id TEXT NOT NULL,record TEXT NOT NULL,PRIMARY KEY(account,transfer,mailbox,origin_device,origin_id));
          CREATE TABLE IF NOT EXISTS pairing_installed_receipts(account TEXT NOT NULL,transfer TEXT NOT NULL,receipt BLOB NOT NULL,PRIMARY KEY(account,transfer));
        ''')

    def set_local_policy(self,mailbox,value):
        """Trusted local settings command, never a received setup record."""
        policy(value)
        self.db.execute('INSERT OR REPLACE INTO pairing_contact_policies VALUES(?,?,?)',(mailbox,encoded(value),'local'))

    def snapshot(self,mailboxes):
        if not isinstance(mailboxes,list) or mailboxes!=sorted(set(mailboxes)):raise ValueError('Selected source contact scope')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            default=self.db.execute("SELECT policy FROM pairing_contact_policies WHERE mailbox='' ").fetchone()
            if not default:raise ValueError('Selected defaults required')
            contacts=[]
            for address in mailboxes:
                a=self.associations._current(address)
                if not a or a.get('held'):raise ValueError('Selected source association unavailable')
                anchor,head,bundle=public_chain(self.ids,a['principal'])
                selected=self.db.execute('SELECT policy FROM pairing_contact_policies WHERE mailbox=?',(address,)).fetchone()
                proofs=[]
                for ident,vanchor,before,after,continuity,status,revision,record in self.db.execute('SELECT id,anchor,not_before,not_after,continuity,status,revision,record FROM human_verification_evidence WHERE account=? AND mailbox=? AND principal=?',(self.account,address,a['principal'])):
                    provenance=json.loads(record)
                    if provenance.get('mechanism')!='human-comparison-v0' or 'originDevice' not in provenance or 'originId' not in provenance:raise ValueError('Original comparison provenance required for transfer')
                    proofs.append(dict(id=provenance['originId'],originDevice=provenance['originDevice'],mechanism='human-comparison-v0',anchor=vanchor,notBefore=before,notAfter=after,continuity=continuity,status=status,revision=str(int(revision))))
                c=dict(mailbox=address,principal=a['principal'],anchor=anchor,head=head,bundle=b64(bundle),generation=a['generation'],enabled=bool(a['enabled']),verification=sorted(proofs,key=lambda p:(p['originDevice'],p['id'])),policy=json.loads(selected[0] if selected else default[0]))
                contacts.append(c)
            value=dict(contacts=contacts,defaults=json.loads(default[0]));configuration(value)
            self.db.execute('COMMIT');return value
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise

    def _staged(self,transfer,time):
        row=self.db.execute('SELECT request,response,configuration,receipt,cancelled FROM pairing_setup WHERE account=? AND transfer=?',(self.account,transfer)).fetchone()
        if not row or row[1] is None or row[2] is None or row[3] is None or row[4]:raise ValueError('Complete active private setup stage required')
        request,reference,pair=self.transfer._request(row[0],time)
        if self.transfer.device['device']!=pair['target']['device']:raise ValueError('Target-only setup installation')
        response,response_ref=self.transfer._verify(row[1],'response',pair['source']['key'])
        receipt,_=self.transfer._verify(row[3],'receipt',pair['target']['key'])
        if response['request']!=reference or receipt['request']!=reference or receipt['response']!=response_ref or receipt['result']!='staged':raise ValueError('Exact staged setup evidence required')
        # Plaintext was committed only after full age authentication by stage().
        selected=json.loads(row[2]);configuration(selected)
        return request,reference,response_ref,selected

    def _verification(self,c,transfer,response_ref):
        records=list(self.db.execute('SELECT id,revision,status,record,mailbox,principal FROM human_verification_evidence WHERE account=?',(self.account,)))
        for proof in c['verification']:
            known=[]
            for ident,revision,status,raw,address,principal in records:
                p=json.loads(raw)
                if (p.get('originDevice'),p.get('originId'))==(proof['originDevice'],proof['id']):
                    if (address,principal)!=(c['mailbox'],c['principal']):raise ValueError('Original comparison mailbox scope cannot change')
                    known.append((ident,int(revision),status,p))
            if len(known)>1:raise ValueError('Ambiguous verification provenance')
            ident=sha(encode_event(dict(principal=self.transfer.device['principal'],originDevice=proof['originDevice'],id=proof['id'])))[:32]
            collision=self.db.execute('SELECT account,mailbox,principal,record FROM human_verification_evidence WHERE id=?',(ident,)).fetchone()
            if collision:
                p=json.loads(collision[3])
                if collision[:3]!=(self.account,c['mailbox'],c['principal']) or (p.get('originDevice'),p.get('originId'))!=(proof['originDevice'],proof['id']):raise ValueError('Verification identifier collision')
            self.db.execute('INSERT OR IGNORE INTO pairing_contact_evidence_imports VALUES(?,?,?,?,?,?)',(self.account,transfer,c['mailbox'],proof['originDevice'],proof['id'],encoded(dict(proof=proof,response=response_ref))))
            if known:
                ident,revision,status,record=known[0]
                # Withdrawal is terminal for an immutable origin decision, even
                # after independent devices advanced bookkeeping differently.
                if status=='withdrawn':continue
                immutable=self.db.execute('SELECT anchor,not_before,not_after,continuity FROM human_verification_evidence WHERE id=?',(ident,)).fetchone()
                if immutable!=(proof['anchor'],proof['notBefore'],proof['notAfter'],proof['continuity']):raise ValueError('Original comparison scope cannot be renewed or replaced')
                if proof['status']=='withdrawn':
                    self.db.execute("UPDATE human_verification_evidence SET status='withdrawn',revision=? WHERE id=?",(stored_revision(max(revision,uint(proof['revision']))),ident))
                    continue
                if revision>uint(proof['revision']):continue
                if revision==uint(proof['revision']):
                    row=self.db.execute('SELECT anchor,not_before,not_after,continuity,status FROM human_verification_evidence WHERE id=?',(ident,)).fetchone()
                    if row!=(proof['anchor'],proof['notBefore'],proof['notAfter'],proof['continuity'],proof['status']):raise ValueError('Conflicting same-revision verification')
                    continue
                self.db.execute('UPDATE human_verification_evidence SET status=?,revision=? WHERE id=?',(proof['status'],stored_revision(uint(proof['revision'])),ident))
                continue
            record=dict(mechanism='human-comparison-v0',scope='mailbox-principal',assurance='human-confirmed-correspondent',originDevice=proof['originDevice'],originId=proof['id'],pairingSetup=dict(transfer=transfer,response=response_ref),attribution='inherited-own-device-comparison')
            self.db.execute('INSERT OR REPLACE INTO human_verification_evidence VALUES(?,?,?,?,?,?,?,?,?,?,?)',(ident,self.account,c['mailbox'],c['principal'],proof['anchor'],proof['notBefore'],proof['notAfter'],proof['continuity'],proof['status'],stored_revision(uint(proof['revision'])),encoded(record)))

    def install_contact(self,transfer,address,*,time,crash=None):
        started=setup_clock.monotonic_ns()
        self.db.execute('BEGIN IMMEDIATE')
        try:
            request,reference,response_ref,selected=self._staged(transfer,time)
            c=next((c for c in selected['contacts'] if c['mailbox']==address),None)
            if c is None:raise ValueError('Contact outside approved setup selection')
            prior=self.db.execute('SELECT result FROM pairing_contact_results WHERE account=? AND transfer=? AND mailbox=?',(self.account,transfer,address)).fetchone()
            if prior and json.loads(prior[0])['status']=='installed':self.db.execute('COMMIT');return json.loads(prior[0])
            self.db.execute('SAVEPOINT contact')
            try:
                raw,record,path=validated_history(c)
                current=self.ids.current_state(c['principal']);pin=self.db.execute('SELECT digest FROM pins WHERE principal=?',(c['principal'],)).fetchone()
                if current['conflicted'] or (pin and pin[0]!=c['anchor']):raise ValueError('Existing peer identity conflict')
                a=self.associations._current(address)
                if a and (a.get('held') or a['principal']!=c['principal'] or bool(a['enabled'])!=c['enabled']):raise ValueError('Existing local association decision differs')
                existing=self.db.execute('SELECT policy FROM pairing_contact_policies WHERE mailbox=?',(address,)).fetchone()
                if existing and existing[0]!=encoded(c['policy']):raise ValueError('Existing local security policy differs')
                default=self.db.execute("SELECT policy,origin FROM pairing_contact_policies WHERE mailbox=''").fetchone()
                if not existing and default and default[1]=='local' and default[0]!=encoded(c['policy']):raise ValueError('Explicit local defaults differ')
                if not pin:
                    if self.ids._observe_locked(record,first_contact_policy='allow-unverified')['status']!='pinned-unverified':raise ValueError('Peer pin unavailable')
                incoming_ids={s['digest'] for s in path}
                if current['head'] and current['head'] not in incoming_ids:
                    # Preserve a locally newer descendant, including its removals.
                    _,_,local=public_chain(self.ids,c['principal'])
                    if c['head'] not in [s['digest'] for s in decode_identity_bundle(local)['states']]:raise ValueError('Divergent contact histories')
                else:
                    for state in path[1:]:
                        if self.ids._accept_locked(raw,c['principal'],state,dict.fromkeys(('earliest','latest'),state['value']['issuedAt']))['status'] not in ('accepted-unverified','already-recorded'):raise ValueError('Contact successor unavailable')
                if not a:
                    decision=sha((reference+'\0'+address).encode())[:32]
                    self.db.execute('INSERT INTO mailbox_associations VALUES(?,?,?,?,?,?)',(address,'1',c['principal'],int(c['enabled']),decision,c['anchor']))
                    self.db.execute('INSERT INTO pairing_contact_origins VALUES(?,?,?,?,?,?)',(decision,self.account,transfer,address,c['generation'],response_ref))
                self._verification(c,transfer,response_ref)
                self.db.execute('INSERT OR IGNORE INTO pairing_contact_policies VALUES(?,?,?)',(address,encoded(c['policy']),'pairing:'+transfer))
                self._staged(transfer,elapsed_interval(time,started))
                if crash:crash('before-contact-commit')
                result=dict(status='installed',mailbox=address,sendAuthorized=False)
                self.db.execute('RELEASE contact')
            except ValueError as error:
                self.db.execute('ROLLBACK TO contact');self.db.execute('RELEASE contact')
                result=dict(status='held',mailbox=address,reason=str(error),sendAuthorized=False)
            self.db.execute('INSERT OR REPLACE INTO pairing_contact_results VALUES(?,?,?,?)',(self.account,transfer,address,encoded(result)))
            self.db.execute('COMMIT');return result
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise

    def finish(self,transfer,*,time,crash=None):
        started=setup_clock.monotonic_ns()
        self.db.execute('BEGIN IMMEDIATE')
        try:
            request,reference,response_ref,selected=self._staged(transfer,time)
            results={m:json.loads(r)['status'] for m,r in self.db.execute('SELECT mailbox,result FROM pairing_contact_results WHERE account=? AND transfer=?',(self.account,transfer))}
            if any(results.get(c['mailbox'])!='installed' for c in selected['contacts']):raise ValueError('Contact setup remains incomplete')
            existing=self.db.execute("SELECT policy FROM pairing_contact_policies WHERE mailbox='' ").fetchone()
            if existing and existing[0]!=encoded(selected['defaults']):raise ValueError('Existing explicit defaults differ')
            prior=self.db.execute('SELECT receipt FROM pairing_installed_receipts WHERE account=? AND transfer=?',(self.account,transfer)).fetchone()
            if prior:self.db.execute('COMMIT');return prior[0]
            self.db.execute('INSERT OR IGNORE INTO pairing_contact_policies VALUES(?,?,?)',('',encoded(selected['defaults']),'pairing:'+transfer))
            receipt=self.transfer._sign('receipt',dict(version='0',purpose='pairing-setup-receipt',transfer=transfer,session=request['session'],pairingResult=request['pairingResult'],request=reference,response=response_ref,result='installed'))
            self.transfer._verify(receipt,'receipt',request['target']['key'])
            self._staged(transfer,elapsed_interval(time,started))
            self.db.execute('INSERT INTO pairing_installed_receipts VALUES(?,?,?)',(self.account,transfer,receipt))
            if crash:crash('before-installed-receipt-commit')
            self.db.execute('COMMIT');return receipt
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
