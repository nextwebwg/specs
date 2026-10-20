"""Private joined MLS ordering experiment with configured initial trust/support.

Does not install through existing application SenderRelease/MlsReceive. Its own
checkpoint/decision/outbox transaction is tested; public context7 admission and
application sending are deliberately not inferred from this comparison.
"""
import hashlib,json,subprocess,re
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from provider_mls import call,sign as provider_sign
from mls_receive import LockedIdentity
from ordering_certificates import Proof,encode,domain
from ordering_scope import scope_object,scope_digest,decision_identity,commitment,octets

class ProviderKey:
    def __init__(self,binary,device):self.binary=binary;self.device=device
    def public_key(self):return Ed25519PublicKey.from_public_bytes(bytes.fromhex(self.device['key']))
    def sign(self,framed):
        d,rest=framed.split(b'\0',1)
        if not d.startswith(b'email-next/ordering-experiment/') or len(rest)<4 or int.from_bytes(rest[:4],'big')!=len(rest[4:]):raise ValueError('fixed signature frame')
        return bytes.fromhex(provider_sign(self.binary,self.device,d.decode(),rest[4:]))

def snapshot(s):
    return {**s,'members':[{**m,'index':str(m['index'])} for m in s['members']]}
def candidate_id(candidate):return commitment(b'email-next/ordering-candidate/v0',candidate)
def admin_material(plan):
    raw=encode(plan);return domain('admin-intent')+len(raw).to_bytes(4,'big')+raw

def context_valid(context):
    # Real shared schema; no generic designated-writer bypass.
    source=Path(__file__).with_name('conversation-context.mjs')
    if not source.exists():source=Path(__file__).resolve().parents[2]/'outputs/email-next/evidence/conversation-context.mjs'
    module=source.as_uri()
    script="import {validateConversationContext} from '"+module+"';import {readFileSync} from 'node:fs';const c=JSON.parse(readFileSync(0,'utf8'));process.stdout.write(validateConversationContext(c,{configuredQuorumOrdering:true,configuredApplication:c.application})?'valid':'invalid');"
    r=subprocess.run(['node','--input-type=module','-e',script],input=encode(context),capture_output=True,check=True)
    if r.stdout!=b'valid':raise ValueError('context7')

class JoinedOrdering:
    def __init__(self,identity,binary,device):
        self.identity=identity;self.db=identity.db;self.binary=Path(binary);self.device=device
        self.db.executescript('''CREATE TABLE IF NOT EXISTS qo_checkpoint(id INTEGER PRIMARY KEY, previous TEXT NOT NULL, state BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS qo_staged(candidate TEXT PRIMARY KEY,state BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS qo_support(identity TEXT,key TEXT,application BLOB,PRIMARY KEY(identity,key));
        CREATE TABLE IF NOT EXISTS qo_decision(scope TEXT PRIMARY KEY, candidate TEXT NOT NULL, identity TEXT NOT NULL, proof BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS qo_outbox(identity TEXT PRIMARY KEY, bytes BLOB NOT NULL);''')
        from proposal_observation import initialize
        initialize(self.db)
    def install_fixture(self,state):
        context_valid(json.loads(bytes.fromhex(state['snapshot']['context'])))
        self.db.execute('INSERT INTO qo_checkpoint VALUES(1,?,?)',('genesis',encode(state)))
        application=json.loads(bytes.fromhex(state['snapshot']['context']))['application']
        for member in state['snapshot']['members']:self.configure_support(member['identity'],member['key'],application)
    def configure_support(self,identity,key,application):
        """Explicit local fixture agreement; never called by incoming control parsing."""
        self.db.execute('INSERT OR REPLACE INTO qo_support VALUES(?,?,?)',(identity,key,encode(application)))
    def live(self):
        row=self.db.execute('SELECT previous,state FROM qo_checkpoint WHERE id=1').fetchone()
        if not row:raise ValueError('missing checkpoint')
        return row[0],json.loads(row[1])
    def scope(self):
        previous,state=self.live();s=state['snapshot'];ctx=json.loads(bytes.fromhex(s['context']))
        return scope_object(conversation=ctx['conversation'],group=s['group'],predecessor=s['predecessor'],previous_decision=previous,ordering=ctx['ordering'],slot=str(int(s['epoch'])+1))
    def keys(self):return {w['principal']+'|'+w['device']:w['signingKey'] for w in self.scope()['ordering']['witnesses']}
    def current(self,member,role,time):
        status=LockedIdentity(self.identity).check_device(bytes.fromhex(member['identity']),bytes.fromhex(member['key']),role=role,time=time,trust_policy='allow-unverified')
        if status.get('status')!='authorized-unverified':raise ValueError('current account authority')
        return status
    def stage(self,*args,crash=None,**kwargs):
        """Return wire bytes only after candidate and sender advancement commit.

        Public stage owns its transaction. Callers needing additional atomic writes
        must use _stage_locked and retain ownership until their commit succeeds.
        """
        if self.db.in_transaction:raise ValueError('stage requires transaction ownership')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            candidate=self._stage_locked(*args,**kwargs)
            if crash:crash('before-commit')
            self.db.execute('COMMIT')
            if crash:crash('after-commit')
            return candidate
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def _continue_locked(self,state,result):
        self.db.execute('UPDATE qo_checkpoint SET state=? WHERE id=1',(encode(dict(snapshot=state['snapshot'],checkpoint=result['continuedCheckpoint'])),))
    def _stage_locked(self,admin,*,time,packages=(),new_context=None,removals=()):
        if not self.db.in_transaction:raise ValueError('stage transaction required')
        previous,state=self.live();args=dict(checkpoint=state['checkpoint'],key=self.device['key'],group=state['snapshot']['group'])
        for row in self.db.execute('SELECT state FROM qo_staged'):
            retained=json.loads(row[0])
            if retained['before']['predecessor']==state['snapshot']['predecessor'] and retained.get('senderContinuity')!='openmls-0.9.1/continued-v1':
                raise ValueError('Legacy staged sender continuity requires fresh admission')
        if new_context and (packages or removals):raise ValueError('Context transition separate from membership')
        mixed=bool(packages and removals)
        result=call(self.binary,op='quorum-context-candidate' if new_context else 'quorum-mixed-candidate' if mixed else 'remove' if removals else 'quorum-candidate',**args,**({'context':encode(new_context).hex()} if new_context else {'indices':list(removals),'packages':list(packages)} if mixed else {'indices':list(removals)} if removals else {'packages':list(packages)}))
        before=result['before'];after=result['after'];added=sorted(m['identity'] for m in after['members'] if m['identity'] not in {x['identity'] for x in before['members']})
        plan=dict(version='0',purpose='ordering-candidate',scope=self.scope(),commit=result['wire'],result=snapshot(after),welcomes=[{'recipients':added,'bytes':result['welcome']}] if added else [])
        approval={'signer':admin.device['identity'],'signature':admin.sign(admin_material(plan)).hex()}
        candidate={'plan':plan,'approval':approval}
        self.validate(candidate,result,time=time)
        if 'localStaged' in result:
            result['localStageBinding']=dict(library='openmls-0.9.1/staged-v0',candidate=candidate_id(candidate),group=before['group'],predecessor=before['predecessor'],digest=hashlib.sha256(encode(result['localStaged'])).hexdigest())
        from proposal_observation import observe_locked,PROVENANCE
        observe_locked(self.db,candidate_id(candidate),result)
        result['proposalObservation']=PROVENANCE
        result['senderContinuity']='openmls-0.9.1/continued-v1'
        self._continue_locked(state,result)
        del result['continuedCheckpoint']
        self.db.execute('INSERT INTO qo_staged VALUES(?,?)',(candidate_id(candidate),encode(result)))
        return candidate
    def validate(self,candidate,result,*,time):
        if set(candidate)!={'plan','approval'}:raise ValueError('candidate shape')
        plan=candidate['plan'];approval=candidate['approval'];before=result['before'];after=result['after']
        if set(plan)!={'version','purpose','scope','commit','result','welcomes'} or plan['version']!='0' or plan['purpose']!='ordering-candidate':raise ValueError('plan shape')
        if plan['scope']!=self.scope() or plan['commit']!=result['wire'] or plan['result']!=snapshot(after):raise ValueError('exact actual transition')
        if result.get('unsupported') or result.get('selfRemoved'):raise ValueError('unsupported transition')
        if before['predecessor']!=plan['scope']['predecessor'] or after['group']!=before['group'] or int(after['epoch'])!=int(before['epoch'])+1:raise ValueError('predecessor')
        oldctx=json.loads(bytes.fromhex(before['context']));newctx=json.loads(bytes.fromhex(after['context']));context_valid(newctx)
        for field in ('version','purpose','conversation','profile','administrators','application','delivery'):
            if newctx[field]!=oldctx[field]:raise ValueError('unselected application/admin change')
        oldorder=oldctx['ordering'];neworder=newctx['ordering']
        if oldorder!=neworder and int(neworder['generation'])!=int(oldorder['generation'])+1:raise ValueError('handoff generation')
        if set(approval)!={'signer','signature'} or not isinstance(approval['signature'],str) or not re.fullmatch('[0-9a-f]{128}',approval['signature']):raise ValueError('approval shape')
        author=next((m for m in before['members'] if m['identity']==approval['signer']),None)
        if not author or 'enp0:'+author['identity'][42:106] not in oldctx['administrators']:raise ValueError('predecessor administrator')
        try:Ed25519PublicKey.from_public_bytes(bytes.fromhex(author['key'])).verify(bytes.fromhex(approval['signature']),admin_material(plan))
        except Exception as e:raise ValueError('administrator signature') from e
        self.current(author,'send',time)
        sender=next((m for m in before['members'] if m['identity']==result['sender']),None)
        if sender is None:raise ValueError('committer')
        self.current(sender,'send',time)
        principals={'enp0:'+m['identity'][42:106] for m in after['members']}
        if not set(newctx['administrators']).issubset(principals):raise ValueError('administrator absent')
        if len({m['identity'] for m in after['members']})!=len(after['members']):raise ValueError('duplicate member')
        from private_copy import check_roster
        check_roster(newctx,sorted(principals))
        for member in after['members']:
            self.current(member,'receive',time)
            self.check_support(member,newctx['application'])
        for w in neworder['witnesses']:
            ident=(b'email-next/device/v0\0'+bytes.fromhex(w['principal'][5:])+bytes.fromhex(w['device'][5:])).hex()
            member=next((m for m in after['members'] if m['identity']==ident and m['key']==w['signingKey']),None)
            if member is None:raise ValueError('witness roster')
            status=self.current(member,'receive',time)
            if status['head']!=w['state'] or status['binding']!=w['binding']:raise ValueError('witness binding')
        added=sorted(m['identity'] for m in after['members'] if m['identity'] not in {x['identity'] for x in before['members']})
        ws=plan['welcomes']
        if added:
            if not isinstance(ws,list) or len(ws)!=1 or set(ws[0])!={'recipients','bytes'} or ws[0]['recipients']!=added or not isinstance(ws[0]['bytes'],str):raise ValueError('welcome recipients')
            octets(ws[0]['bytes'])
            if result.get('welcome') is not None and ws[0]['bytes']!=result['welcome']:raise ValueError('welcome bytes')
        elif ws!=[]:raise ValueError('unexpected welcome')
    def check_support(self,member,application):
        support=self.db.execute('SELECT application FROM qo_support WHERE identity=? AND key=?',(member['identity'],member['key'])).fetchone()
        if support!=(encode(application),):raise ValueError('configured context7 support required')
    def inspect_candidate(self,candidate,*,time,**options):
        owned=not self.db.in_transaction
        if owned:self.db.execute('BEGIN IMMEDIATE')
        try:
            result=self._inspect_candidate_locked(candidate,time=time,**options)
            from proposal_observation import observe_locked
            observe_locked(self.db,candidate_id(candidate),result)
            if owned:self.db.execute('COMMIT')
            return result
        except BaseException:
            if owned and self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def _inspect_candidate_locked(self,candidate,*,time):
        previous,state=self.live();ident=candidate_id(candidate)
        local=self.db.execute('SELECT state FROM qo_staged WHERE candidate=?',(ident,)).fetchone()
        if local:
            retained=json.loads(local[0]);state=self.live()[1];before=state['snapshot']
            if retained.get('senderContinuity')!='openmls-0.9.1/continued-v1':raise ValueError('Legacy staged sender continuity requires fresh admission')
            binding=dict(library='openmls-0.9.1/staged-v0',candidate=ident,group=before['group'],predecessor=before['predecessor'],digest=hashlib.sha256(encode(retained.get('localStaged'))).hexdigest())
            if retained.get('localStageBinding')!=binding:raise ValueError('Exact local staged binding required')
            merged=call(self.binary,op='merge-local-staged',checkpoint=state['checkpoint'],group=before['group'],key=self.device['key'],library=binding['library'],predecessor=binding['predecessor'],staged=retained['localStaged'])
            result={**retained,**merged}
        else:result=call(self.binary,op='receive-quorum',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.device['key'],wire=candidate['plan']['commit'])
        result['wire']=candidate['plan']['commit']
        self.validate(candidate,result,time=time);return result
    def vote(self,store,kind,proof_bytes,candidate,*,time,candidate_dependencies=None,before_vote=None):
        """Hold identity DB authorization stable while separate vote DB commits.

        Identity transaction retains validated proposal observations; its rollback cannot undo a durable vote.
        Every retry therefore preserves that vote, even if later authority holds.
        """
        self.db.execute('BEGIN IMMEDIATE')
        try:
            if store.scope!=scope_digest(self.scope()) or store.keys!=self.keys() or store.signer!=self.device['principal']+'|'+self.device['device']:raise ValueError('vote store scope')
            self.current({'identity':self.device['identity'],'key':self.device['key']},'send',time)
            self.inspect_candidate(candidate,time=time)
            parsed=Proof(proof_bytes,scope=store.scope,keys=store.keys,f=store.f)
            if parsed.result['candidate']!=candidate_id(candidate):raise ValueError('vote candidate')
            # A separate vote DB can commit even if this DB's later commit fails.
            # Make the validated observation durable before any vote is published,
            # then reacquire authority and scope under the existing write lock.
            self.db.execute('COMMIT');self.db.execute('BEGIN IMMEDIATE')
            if store.scope!=scope_digest(self.scope()) or store.keys!=self.keys():raise ValueError('vote store scope')
            self.current({'identity':self.device['identity'],'key':self.device['key']},'send',time)
            self.inspect_candidate(candidate,time=time)
            if before_vote is not None:before_vote()
            output=store.vote(kind,proof_bytes,authority=lambda:True,candidate_bytes=[encode(c) for c in (candidate_dependencies if candidate_dependencies is not None else [candidate])])
            self.db.execute('COMMIT');return output
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def release(self,decision,*,time):
        """Fixed current-state outbox release; caller must recheck immediately pre-DATA.

        This is not an atomic database/SMTP transaction or historical retransmitter.
        """
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row=self.db.execute('SELECT bytes FROM qo_outbox WHERE identity=?',(decision,)).fetchone()
            if row is None:raise ValueError('unknown decision')
            carrier=json.loads(row[0]);result=carrier['candidate']['plan']['result']
            current=self.live()[1]['snapshot']
            if current['predecessor']!=result['predecessor']:raise ValueError('stale decided outbox')
            for member in current['members']:self.current(member,'receive',time)
            self.current({'identity':self.device['identity'],'key':self.device['key']},'send',time)
            self.db.execute('COMMIT');return row[0]
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def install(self,candidate,proof_bytes,*,time,crash=None):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            scope=candidate['plan']['scope'];sd=scope_digest(scope);cid=candidate_id(candidate);decision=decision_identity(scope,cid)
            prior=self.db.execute('SELECT candidate,identity FROM qo_decision WHERE scope=?',(sd,)).fetchone()
            if prior:
                if prior!=(cid,decision):raise ValueError('conflicting decided branch')
                self.db.execute('COMMIT');return decision
            if scope!=self.scope():raise ValueError('stale scope')
            proof=Proof(proof_bytes,scope=sd,keys=self.keys(),f=int(scope['ordering']['faultBound']))
            if proof.result['kind']!='decision' or proof.result['candidate']!=cid:raise ValueError('decision binding')
            result=self.inspect_candidate(candidate,time=time)
            state={'snapshot':result['after'],'checkpoint':result['checkpoint']}
            self.db.execute('INSERT INTO qo_decision VALUES(?,?,?,?)',(sd,cid,decision,proof_bytes))
            self.db.execute('UPDATE qo_checkpoint SET previous=?,state=? WHERE id=1',(decision,encode(state)))
            carrier=encode({'version':'0','purpose':'quorum-control-experiment','candidate':candidate,'proof':proof_bytes.hex()})
            if len(carrier)>1048576:raise ValueError('unsupported-size')
            self.db.execute('INSERT INTO qo_outbox VALUES(?,?)',(decision,carrier))
            if crash:crash('before-commit')
            self.db.execute('COMMIT')
            if crash:crash('after-commit')
            return decision
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
