"""Trusted local comparison decisions. Incoming mail/QR alone grants no verification."""
import hashlib,json,uuid
from passive_discovery import decode_passive_discovery,uint64
from discovery_mime import extract_discovery
from client_onboarding import ClientOnboarding

MECHANISM='human-comparison-v0'
def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def interval(time):
    if not isinstance(time,dict) or set(time)!={'earliest','latest'} or uint64(time['earliest'])>uint64(time['latest']):raise ValueError('Credible time interval')

def resolve_locked(identity,mailbox,principal,time,*,evidence_id=None):
    """Compose only independent evidence here; device role checks remain separate."""
    db=identity.db;interval(time)
    if not db.in_transaction:raise ValueError('Verification transaction required')
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='human_verification_config'").fetchone():return dict(status='verification-required')
    config=db.execute('SELECT account,local_principal FROM human_verification_config WHERE id=1').fetchone()
    current=identity.current_state(principal)
    if not current['head'] or current['conflicted']:return dict(status='verification-conflicted')
    # Own-account authority comes from explicit client setup, not an email claim.
    if config[1]==principal and db.execute('SELECT 1 FROM human_verification_own_mailboxes WHERE account=? AND mailbox=?',(config[0],mailbox)).fetchone():return dict(status='verified-for-use',mechanism='local-owned-account',account=config[0],mailbox=mailbox,head=current['head'])
    rows=db.execute("SELECT id,anchor,not_before,not_after,continuity,status,revision FROM human_verification_evidence WHERE account=? AND mailbox=? AND principal=? ORDER BY id",(config[0],mailbox,principal)).fetchall()
    for ident,anchor,before,after,continuity,status,revision in rows:
        if evidence_id is not None and evidence_id!=ident:continue
        if status!='accepted' or not int(before)<=uint64(time['earliest'])<=uint64(time['latest'])<=int(after):continue
        cursor=current['head'];seen=set()
        while cursor!=anchor and continuity=='ordinary-authorized-descendants':
            if cursor in seen:break
            seen.add(cursor);row=db.execute('SELECT previous,bundle FROM identity_transitions WHERE principal=? AND digest=? AND accepted=1',(principal,cursor)).fetchone()
            if not row:break
            from identity_bundle import decode_identity_bundle
            bundle=decode_identity_bundle(row[1]);state=next((s['value'] for s in bundle['states'] if s['digest']==cursor),None)
            ordinary={'version','purpose','principal','record','revision','previous','issuedAt','bindings','revoked','signer'}
            if state is None or set(state)!=ordinary or state['version']!='0' or state['purpose']!='identity-state' or state['principal']!=principal or state['previous']!=[row[0]]:break
            cursor=row[0]
        if cursor==anchor:return dict(status='verified-for-use',mechanism=MECHANISM,account=config[0],mailbox=mailbox,principal=principal,head=current['head'],evidence=ident,revision=str(revision),scope='human-confirmed-correspondent')
    return dict(status='verification-required')

class HumanVerification:
    def __init__(self,identity,*,account,local_principal,own_mailboxes=None):
        if not isinstance(account,str) or not account or not isinstance(local_principal,str) or not local_principal.startswith('enp0:'):raise ValueError('Explicit local account setup')
        self.identity=identity;self.db=identity.db;self.onboarding=ClientOnboarding(identity)
        if self.db.in_transaction:raise ValueError('Initialize outside transaction')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS human_verification_config(id INTEGER PRIMARY KEY CHECK(id=1),account TEXT NOT NULL,local_principal TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS human_verification_own_mailboxes(account TEXT NOT NULL,mailbox TEXT NOT NULL,PRIMARY KEY(account,mailbox));
          CREATE TABLE IF NOT EXISTS human_verification_sessions(id TEXT PRIMARY KEY,account TEXT NOT NULL,request TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS human_verification_evidence(id TEXT PRIMARY KEY,account TEXT NOT NULL,mailbox TEXT NOT NULL,principal TEXT NOT NULL,anchor TEXT NOT NULL,not_before TEXT NOT NULL,not_after TEXT NOT NULL,continuity TEXT NOT NULL,status TEXT NOT NULL,revision INTEGER NOT NULL,record TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS human_verification_decisions(id TEXT PRIMARY KEY,request TEXT NOT NULL,result TEXT NOT NULL);
        ''')
        prior=self.db.execute('SELECT account,local_principal FROM human_verification_config WHERE id=1').fetchone()
        if prior and prior!=(account,local_principal):raise ValueError('Different local account requires separate store')
        self.db.execute('INSERT OR IGNORE INTO human_verification_config VALUES(1,?,?)',(account,local_principal));self.account=account
        if own_mailboxes is not None:
            from passive_discovery import mailbox_syntax
            if not isinstance(own_mailboxes,list) or any(mailbox_syntax(m)!='syntax-valid' for m in own_mailboxes):raise ValueError('Explicit own mailbox configuration')
            previous=[r[0] for r in self.db.execute('SELECT mailbox FROM human_verification_own_mailboxes WHERE account=? ORDER BY mailbox',(account,))]
            if previous and previous!=sorted(set(own_mailboxes)):raise ValueError('Own mailbox change requires separate migration')
            self.db.executemany('INSERT OR IGNORE INTO human_verification_own_mailboxes VALUES(?,?)',[(account,m) for m in own_mailboxes])

    def begin(self,source,*,time,session_expires):
        interval(time)
        if uint64(session_expires)<uint64(time['latest']):raise ValueError('Session expiry')
        db=self.db;db.execute('BEGIN IMMEDIATE')
        try:
            row=db.execute('SELECT wire FROM onboarding_sources WHERE digest=?',(source,)).fetchone()
            if not row:raise ValueError('Retained original mail required')
            extracted=extract_discovery(row[0],max_wire_bytes=len(row[0]),max_parts=64)
            if extracted['state']!='candidate':raise ValueError('Candidate required')
            raw=extracted['octets'];decoded=decode_passive_discovery(raw);v=decoded['assertion']['value']
            from email.parser import BytesParser
            from email import policy
            parsed=BytesParser(policy=policy.default).parsebytes(row[0]);headers=parsed.get_all('From',[])
            if len(headers)!=1 or headers[0].defects or len(headers[0].addresses)!=1:raise ValueError('Sole From required')
            address=headers[0].addresses[0]
            if address.username+'@'+address.domain.lower()!=v['mailbox']:raise ValueError('Address mismatch')
            head=self.identity.current_state(v['principal']);association=self.onboarding.associations._current(v['mailbox'])
            if head['conflicted']:raise ValueError('Identity conflict')
            db.execute('SAVEPOINT comparison')
            checked=self.onboarding._install(decoded,time)
            if checked['status']!='snapshot-authorized-unverified':raise ValueError('Current candidate authority')
            state=next(s['value'] for s in decoded['identity']['states'] if s['digest']==v['state'])
            comparison=dict(version='0',purpose='manual-correspondent-comparison',mailbox=v['mailbox'],principal=v['principal'],stateDigest=v['state'],stateRevision=state['revision'])
            db.execute('ROLLBACK TO comparison');db.execute('RELEASE comparison')
            request=dict(source=source,wrapper=raw.hex(),comparison=comparison,expectedHead=head['head'],expectedGeneration=association['generation'] if association else None,expires=session_expires)
            ident=uuid.uuid4().hex;db.execute('INSERT INTO human_verification_sessions VALUES(?,?,?)',(ident,self.account,encoded(request)));db.execute('COMMIT')
            return dict(session=ident,comparison=comparison,assurance='human-confirmed-correspondent',deviceCount=len(state['bindings']))
        except BaseException:
            if db.in_transaction:db.execute('ROLLBACK')
            raise

    def confirm(self,decision,session,comparison,*,channel,time,not_before,not_after,continuity,crash=None):
        """Trusted local UI command. Never expose as an incoming-mail verifier."""
        interval(time)
        if channel not in ('in-person','preauthenticated-independent-channel'):raise ValueError('Independent comparison required')
        if continuity not in ('anchor-only','ordinary-authorized-descendants'):raise ValueError('Configured continuity policy')
        if not uint64(not_before)<=uint64(time['earliest'])<=uint64(time['latest'])<=uint64(not_after):raise ValueError('Evidence interval')
        request=encoded(dict(account=self.account,session=session,comparison=comparison,channel=channel,time=time,notBefore=not_before,notAfter=not_after,continuity=continuity))
        db=self.db;db.execute('BEGIN IMMEDIATE')
        try:
            prior=db.execute('SELECT request,result FROM human_verification_decisions WHERE id=?',(decision,)).fetchone()
            if prior:
                if prior[0]!=request:raise ValueError('Immutable decision conflict')
                db.execute('COMMIT');return json.loads(prior[1])
            row=db.execute('SELECT request FROM human_verification_sessions WHERE id=? AND account=?',(session,self.account)).fetchone()
            if not row:raise ValueError('Local comparison session required')
            expected=json.loads(row[0])
            if comparison!=expected['comparison']:raise ValueError('Full comparison mismatch')
            if uint64(time['latest'])>uint64(expected['expires']):raise ValueError('Comparison session expired')
            mailbox,principal=comparison['mailbox'],comparison['principal'];head=self.identity.current_state(principal);association=self.onboarding.associations._current(mailbox)
            if head['conflicted'] or head['head']!=expected['expectedHead'] or (association['generation'] if association else None)!=expected['expectedGeneration']:raise ValueError('Comparison snapshot changed')
            decoded=decode_passive_discovery(bytes.fromhex(expected['wrapper']));checked=self.onboarding._install(decoded,time)
            if checked['status']!='snapshot-authorized-unverified' or self.identity.current_state(principal)['head']!=comparison['stateDigest']:raise ValueError('Compared identity no longer current')
            v=decoded['assertion']['value'];binding=next(b for b in decoded['identity']['bindings'] if b['digest']==v['binding'])
            self.onboarding.associations._observe_validated_batch_locked([dict(assertion=decoded['assertion']['octets'],signature=decoded['signature'],signingKey=bytes.fromhex(binding['value']['signingKey']),outerFrom=[mailbox],sourceId=expected['source'],parserRevision='human-comparison-v0',observedAt=time['earliest'])])
            evidence=uuid.uuid4().hex;record=dict(mechanism=MECHANISM,scope='mailbox-principal',assurance='human-confirmed-correspondent',comparison=comparison,channel=channel,acceptedAt=time,source=expected['source'],session=session)
            db.execute('INSERT INTO human_verification_evidence VALUES(?,?,?,?,?,?,?,?,?,?,?)',(evidence,self.account,mailbox,principal,comparison['stateDigest'],not_before,not_after,continuity,'accepted',1,encoded(record)))
            if association:
                if association['principal']!=principal or not association['enabled']:raise ValueError('Separate association replacement or enable required')
            else:
                selected=self.onboarding.associations._decide_locked(decision_id=uuid.uuid4().hex,mailbox=mailbox,expected_generation=None,kind='resolve-first-contact',principal=principal,actor='local-user',policy_revision='human-comparison-v0',trust_policy='allow-unverified',time=time)
                if selected['status']!='associated-unverified':raise ValueError('Association selection failed')
            result=resolve_locked(self.identity,mailbox,principal,time,evidence_id=evidence)
            if result['status']!='verified-for-use':raise ValueError('Verification composition failed')
            result=dict(result,sendAuthorized=False)
            db.execute('INSERT INTO human_verification_decisions VALUES(?,?,?)',(decision,request,encoded(result)))
            if crash:crash('before-commit')
            db.execute('COMMIT')
            if crash:crash('after-commit')
            return result
        except BaseException:
            if db.in_transaction:db.execute('ROLLBACK')
            raise

    def withdraw(self,evidence_id,*,expected_revision):
        """Local user withdrawal; retained evidence is never deleted or renewed."""
        db=self.db;db.execute('BEGIN IMMEDIATE')
        try:
            row=db.execute('SELECT revision,status FROM human_verification_evidence WHERE id=? AND account=?',(evidence_id,self.account)).fetchone()
            if not row or row[0]!=expected_revision:raise ValueError('Stale verification revision')
            if row[1]=='accepted':db.execute("UPDATE human_verification_evidence SET status='withdrawn',revision=revision+1 WHERE id=?",(evidence_id,))
            db.execute('COMMIT')
        except BaseException:
            if db.in_transaction:db.execute('ROLLBACK')
            raise


def principal_locked(identity,principal,time):
    """Identity scope only: callers separately verify every exact routed mailbox."""
    db=identity.db
    if not db.in_transaction:raise ValueError('Verification transaction required')
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='human_verification_config'").fetchone():return dict(status='verification-required')
    config=db.execute('SELECT local_principal FROM human_verification_config WHERE id=1').fetchone()
    if config[0]==principal:
        current=identity.current_state(principal)
        return dict(status='verified-for-use',mechanism='local-owned-account',scope='principal-only',head=current['head']) if current['head'] and not current['conflicted'] else dict(status='verification-conflicted')
    for mailbox, in db.execute("SELECT DISTINCT mailbox FROM human_verification_evidence WHERE principal=? ORDER BY mailbox",(principal,)):
        result=resolve_locked(identity,mailbox,principal,time)
        if result['status']=='verified-for-use':return result
    return dict(status='verification-required')

class HumanVerifiedIdentity:
    """Explicit local opt-in. Crypto outcome and independent provenance stay separate."""
    def __init__(self,identity):self.identity=identity
    def check_device(self,credential,key,*,role,time,trust_policy):
        from mls_receive import LockedIdentity
        if trust_policy!='require-verification':return LockedIdentity(self.identity).check_device(credential,key,role=role,time=time,trust_policy=trust_policy)
        cryptographic=LockedIdentity(self.identity).check_device(credential,key,role=role,time=time,trust_policy='allow-unverified')
        if cryptographic.get('status')!='authorized-unverified':return cryptographic
        verified=principal_locked(self.identity,'enp0:'+credential[21:53].hex(),time)
        if verified['status']!='verified-for-use':return verified
        return dict(cryptographic,verification=verified)
