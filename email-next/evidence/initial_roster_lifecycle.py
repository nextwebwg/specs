"""Atomic initial3 roster creation/admission; SMTP dispatch is a separate adapter."""
import base64
import json
import uuid
from pathlib import Path
from email import policy
from email.parser import BytesParser
from event_encoding import encode_event
from initial_roster import parse,anchor,sha,credential
from application_agreement import profile
from application_support import supports
from provider_mls import Admission,call,sign
from passive_discovery import decode_passive_discovery,uint64
from passive_discovery_verify import verify_passive_discovery
from passive_discovery_package import validate_package
from mls_receive import LockedIdentity,MlsReceive,FORMAT
from sender_association import check_locked
from invitation_mime import package
import group_instances as instances
import membership_episodes as episodes

def b64(raw):return base64.b64encode(raw).decode()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def initialize(db):
    if db.in_transaction:raise ValueError('Initialize outside transaction')
    instances.initialize(db)
    from quorum_exchange_support import initialize as exchange_initialize
    exchange_initialize(db)
    db.executescript('''
    CREATE TABLE IF NOT EXISTS initial_rosters(creation TEXT PRIMARY KEY,request BLOB NOT NULL,roster_payload BLOB NOT NULL,roster_signature TEXT NOT NULL,anchor TEXT NOT NULL,context BLOB NOT NULL,role TEXT NOT NULL,result BLOB NOT NULL);
    CREATE TABLE IF NOT EXISTS initial_roster_members(creation TEXT NOT NULL,credential TEXT NOT NULL,key TEXT NOT NULL,package_ref TEXT,proof BLOB NOT NULL,agreement TEXT NOT NULL,episode TEXT NOT NULL,PRIMARY KEY(creation,credential));
    CREATE TABLE IF NOT EXISTS initial_roster_packages(reference TEXT PRIMARY KEY,creation TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS initial_roster_prepared(id TEXT PRIMARY KEY,creation TEXT NOT NULL,target TEXT NOT NULL,wire BLOB NOT NULL,metadata TEXT NOT NULL,dependencies TEXT NOT NULL,policy_revision INTEGER NOT NULL,envelope TEXT NOT NULL,associations TEXT NOT NULL,evidence TEXT NOT NULL,UNIQUE(creation,target));
    CREATE TABLE IF NOT EXISTS initial_roster_catchup(delivery TEXT PRIMARY KEY,plan TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS initial_roster_received(creator TEXT NOT NULL,id TEXT NOT NULL,payload BLOB NOT NULL,signature TEXT NOT NULL,creation TEXT NOT NULL,result BLOB NOT NULL,PRIMARY KEY(creator,id));
    ''')
def expected(principals,devices,values):
    if not isinstance(principals,list) or principals!=sorted(set(principals)) or not isinstance(devices,list):raise ValueError('Independent intended selection')
    if any(not isinstance(d,dict) or set(d)!={'principal','device'} for d in devices):raise ValueError('Independent device selection')
    pairs=[(d['principal'],d['device']) for d in devices]
    if pairs!=sorted(set(pairs)) or pairs!=[(v['principal'],v['device']) for v in values] or principals!=sorted({v['principal'] for v in values}):raise ValueError('Intended principal/device coverage')
def check_proofs(identity,binary,decoded,context,creator,interval,trust,*,verification=False):
    authority=LockedIdentity(identity)
    if verification:
        from human_verification import HumanVerifiedIdentity
        authority=HumanVerifiedIdentity(identity)
    result=[]
    for d in decoded:
        a=d['assertion'];v=a['value'];raw=encode_event(d['wrapper']) if 'wrapper' in d else None
        # Original wrapper is explicitly attached by the caller; never synthesized.
        if raw is None:raise ValueError('Original proof wrapper required')
        verified=verify_passive_discovery(raw,authority,time=interval,trust_policy=trust)
        if verified.get('status')!='snapshot-authorized-unverified':raise ValueError('Current roster device authority')
        binding=next(b['value'] for b in d['identity']['bindings'] if b['digest']==v['binding']);key=binding['signingKey'];ident=credential(v)
        if not supports(v,context['application'],context['ordering']['kind']):raise ValueError('Exact roster tuple intersection')
        if not uint64(binding['notBefore'])<=uint64(interval['earliest'])<=uint64(interval['latest'])<=uint64(binding['notAfter']):raise ValueError('Roster binding interval')
        if ident==creator:
            if authority.check_device(bytes.fromhex(ident),bytes.fromhex(key),role='send',time=interval,trust_policy=trust).get('status')!='authorized-unverified':raise ValueError('Creator send authority')
        else:
            payload=a['key_package_octets']
            if payload is None or validate_package(payload,principal=v['principal'],device=v['device'],accepted_signing_key=bytes.fromhex(key),earliest=interval['earliest'],latest=interval['latest'],executable=Path(binary).with_name('validate-discovery-package'))!={'status':'package-valid'}:raise ValueError('Roster package interval/key')
        result.append(dict(identity=ident,key=key,principal=v['principal'],device=v['device'],state=v['state'],binding=v['binding'],decoded=d))
    from private_copy import check_roster
    check_roster(context,[r['principal'] for r in result])
    if context.get('delivery',{}).get('kind')=='private-copy-v0' and context['delivery']['originator']!='enp0:'+bytes.fromhex(creator)[21:53].hex():raise ValueError('Private copy originator must create group')
    from application_payload import selected_format
    selected_format(context,context['application'],configured_ordering=True,configured_quorum_ordering=context['version']=='7')
    if context['version']=='7':
        from quorum_admission import check_initial_witnesses
        check_initial_witnesses(context,[dict(principal=r['principal'],device=r['device'],signingKey=r['key'],state=r['state'],binding=r['binding']) for r in result])
    return result

def install(db,joined,instance,roster,proofs,*,role):
    if db.execute('SELECT 1 FROM mls_checkpoint').fetchone() or db.execute('SELECT 1 FROM mls_group_instances').fetchone():raise ValueError('Existing conversation/instance')
    admission='initial-roster:'+instance;group=joined['group'];application=profile(json.loads(base64.b64decode(roster['context']))['application'])
    db.execute('INSERT INTO mls_checkpoint VALUES(1,0,?,?,?)',(FORMAT,group,canonical(joined['checkpoint'])))
    db.execute('INSERT INTO mls_group_instances VALUES(?,?,?,?,?,NULL)',(instance,group,admission,'signed-initial-roster','active'));db.execute('INSERT INTO mls_checkpoint_instance VALUES(1,?)',(instance,))
    episodes.install(db,dict(joined,epoch='1'),admission)
    for m,proof in zip(roster['members'],proofs):
        ident=credential(m);db.execute('INSERT INTO mls_episode_instance VALUES(?,?,?,?,?)',(group,ident,m['signingKey'],admission,instance))
        db.execute('INSERT INTO mls_instance_agreements VALUES(?,?,?,?,?,?)',(instance,ident,m['signingKey'],application,'signed-initial-roster',roster['creation']))
        db.execute('INSERT INTO initial_roster_members VALUES(?,?,?,?,?,?,?)',(roster['creation'],ident,m['signingKey'],base64.b64decode(m['keyPackageRef']).hex() if m['kind']=='joiner' else None,canonical(proof),application,admission))
    context=json.loads(base64.b64decode(roster['context']))
    if context['version']=='7':
        from quorum_admission import install_initial
        install_initial(db,instance,roster,joined)
        if roster['version']=='4':
            from quorum_exchange_support import retain_locked
            selected=list(proofs)
            retain_locked(db,group,selected,[decode_passive_discovery(encode_event(p))['assertion']['digest'] for p in selected])
    if context['ordering']['kind']=='designated-member-v0':db.execute("INSERT INTO mls_configured_context VALUES(?,'configured-endpoint-v0')",(group,))
    db.execute('INSERT INTO mls_instance_schema VALUES(1,1) ON CONFLICT(id) DO UPDATE SET version=1')

class InitialRosterRelease:
    def __init__(self,sender,history=None,catchup_plan=None):
        self.sender=sender;self.db=sender.db;self.history=history;self.catchup_plan=catchup_plan
        if history is not None:
            from commit_history import CommitHistory
            if type(history) is not CommitHistory or history.db is not self.db:raise ValueError('Shared accepted history required')
        initialize(self.db)
    def prepare(self,creation,*,device,selected,intended_principals,intended_devices,context,not_before,not_after,time,crash=None):
        MlsReceive._policy(time,'allow-unverified')
        interval=dict(earliest=not_before,latest=not_after)
        if not uint64(not_before)<=uint64(time['earliest'])<=uint64(time['latest'])<=uint64(not_after):raise ValueError('Creation interval')
        request=canonical(dict(creation=creation,creator=device['identity'],key=device['key'],selected=[dict(c,wrapper=c['wrapper'].hex()) for c in selected],principals=intended_principals,devices=intended_devices,context=context,notBefore=not_before,notAfter=not_after))
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT request FROM initial_rosters WHERE creation=?',(creation,)).fetchone()
            if old:
                if old[0]!=request:raise ValueError('Creation request conflict')
                result=dict(self.db.execute('SELECT id,wire FROM initial_roster_prepared WHERE creation=? ORDER BY target',(creation,)));self.db.execute('COMMIT');return result
            if self.db.execute('SELECT 1 FROM mls_checkpoint').fetchone():raise ValueError('Existing conversation')
            setting=self.db.execute('SELECT revision,policy FROM sender_policy WHERE id=1').fetchone()
            if not setting:raise ValueError('Configure sender policy')
            trust=json.loads(setting[1])['trustPolicy'];decoded=[]
            for c in selected:
                if set(c)!={'wrapper','mailbox','generation','digest'}:raise ValueError('Selected route fields')
                d=decode_passive_discovery(c['wrapper']);d['wrapper']=json.loads(c['wrapper']);a=d['assertion']
                if c['mailbox']!=a['value']['mailbox'] or c['digest']!=a['digest']:raise ValueError('Selected route proof')
                decoded.append(d)
            rows=check_proofs(self.sender.identity,self.sender.binary,decoded,context,device['identity'],interval,trust,verification=self.sender._verification_enabled())
            ordered=sorted(zip(rows,selected),key=lambda pair:(pair[0]['principal'],pair[0]['device']));rows=[r for r,c in ordered];selected=[c for r,c in ordered]
            expected(intended_principals,intended_devices,rows)
            if sum(r['identity']==device['identity'] for r in rows)!=1 or next(r['key'] for r in rows if r['identity']==device['identity'])!=device['key']:raise ValueError('Exact creator')
            packages=[r['decoded']['assertion']['key_package_octets'].hex() for r in rows if r['identity']!=device['identity']]
            staged=call(self.sender.binary,op='create-initial-roster',checkpoint=device['checkpoint'],key=device['key'],identity=device['identity'],context=encode_event(context).hex(),packages=packages)
            if sorted((r['identity'],r['key']) for r in rows)!=sorted((m['identity'],m['key']) for m in staged['members']):raise ValueError('Actual roster mismatch')
            members=[];proofs=[]
            for r in rows:
                d=r['decoded'];a=d['assertion'];m=dict(kind='creator' if r['identity']==device['identity'] else 'joiner',**{k:r[k] for k in ('principal','device','state','binding')},signingKey=r['key'],assertion=dict(digest=a['digest'],signature=d['signature'].hex()))
                if m['kind']=='joiner':
                    ref=call(self.sender.binary,op='package-reference',checkpoint=device['checkpoint'],key=device['key'],package=a['key_package_octets'].hex())['reference']
                    if self.db.execute('SELECT 1 FROM initial_roster_packages WHERE reference=?',(ref,)).fetchone():raise ValueError('Reserved package')
                    if self.db.execute("SELECT 1 FROM sqlite_master WHERE name='initial_application_packages'").fetchone() and self.db.execute('SELECT 1 FROM initial_application_packages WHERE reference=?',(ref,)).fetchone():raise ValueError('Previously used initial package')
                    m.update(keyPackageRef=b64(bytes.fromhex(ref)),keyPackageDigest=sha(a['key_package_octets']));self.db.execute('INSERT INTO initial_roster_packages VALUES(?,?)',(ref,creation))
                members.append(m);proofs.append(d['wrapper'])
            creator=next(m for m in members if m['kind']=='creator');context_raw=encode_event(context)
            exchange_enabled=context['version']=='7' and any(d['assertion']['value']['version']=='7' for d in decoded)
            if exchange_enabled and any(d['assertion']['value']['version']!='7' for d in decoded):raise ValueError('Lifecycle7 requires assertion7 for every device')
            roster=dict(version='4' if exchange_enabled else '3' if context['version']=='7' else '2' if context['version']=='6' else '1' if context['version']=='5' else '0',purpose='mls-initial-roster',creation=creation,profile='mls-1-0001',conversation=context['conversation'],creator={k:creator[k] for k in ('principal','device','state','binding')},intendedPrincipals=intended_principals,group=b64(bytes.fromhex(staged['group'])),epoch='1',context=b64(context_raw),applicationContextDigest=sha(context_raw),members=members,notBefore=not_before,notAfter=not_after,welcome=b64(bytes.fromhex(staged['welcome'])),resultGroupContextDigest=sha(bytes.fromhex(staged['groupContext'])))
            roster_raw=encode_event(roster);roster_sig=sign(self.sender.binary,device,'email-next/mls-initial-roster/v'+roster['version'],roster_raw);instance=anchor(roster_raw,bytes.fromhex(roster_sig))
            install(self.db,staged,instance,roster,proofs,role='creator')
            metadata=call(self.sender.binary,op='inspect-send',checkpoint=staged['checkpoint'],key=device['key'],group=staged['group'])['metadata'];dependencies=self.sender._authority(metadata,interval,trust)
            routes=[dict(mailbox=c['mailbox'],generation=c['generation'],principal=r['principal'],observation=c['digest']) for r,c in zip(rows,selected)]
            route_checks=check_locked(self.sender.associations,routes,metadata,interval,trust,verification=self.sender._verification_enabled())
            result={}
            for m,r,c,route,checked in zip(members,rows,selected,routes,route_checks):
                if m['kind']=='creator':continue
                ident=uuid.uuid4().hex;value=dict(version='7' if exchange_enabled else '6' if context['version']=='7' else '5' if context['version']=='6' else '4' if context['version']=='5' else '3',purpose='mls-new-conversation-invitation',invitation=ident,creation=creation,rosterDigest=sha(roster_raw),rosterSignature=roster_sig,creator=roster['creator'],target=dict(principal=m['principal'],device=m['device'],mailbox=c['mailbox'],keyPackageRef=m['keyPackageRef']),notBefore=not_before,notAfter=not_after)
                raw=encode_event(value);outer=encode_event(dict(payload=b64(raw),signature=sign(self.sender.binary,device,'email-next/mls-new-conversation-invitation/v'+value['version'],raw),identity=next(r['decoded']['wrapper']['identity'] for r in rows if r['identity']==device['identity']),roster=dict(payload=b64(roster_raw),signature=roster_sig),applicationAssertions=proofs));parse(outer)
                mime=BytesParser(policy=policy.SMTP).parsebytes(package(outer));mime.replace_header('From',next(c['mailbox'] for r,c in zip(rows,selected) if r['identity']==device['identity']));mime.replace_header('To',c['mailbox']);mime['Message-ID']='<'+ident+'@roster.example.invalid>';wire=mime.as_bytes()
                self.db.execute('INSERT INTO initial_roster_prepared VALUES(?,?,?,?,?,?,?,?,?,?)',(ident,creation,r['identity'],wire,canonical(metadata).decode(),canonical(dependencies).decode(),setting[0],canonical(dict(sender=mime['From'],recipients=[c['mailbox']])).decode(),canonical(dict(mode='selected-association',targets=[route],dependencies=[checked])).decode(),canonical(dict(anchor=instance,interval=interval,target=r['identity'],initialGroupContext=staged['groupContext'])).decode()));result[ident]=wire
            public=dict(group=staged['group'],instance=instance,epoch='1')
            self.db.execute('INSERT INTO initial_rosters VALUES(?,?,?,?,?,?,?,?)',(creation,request,roster_raw,roster_sig,instance,context_raw,'creator',canonical(public)))
            if crash:crash('before-commit')
            self.db.execute('COMMIT');return result
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise

    def validate_locked(self,delivery,time):
        if not self.db.in_transaction:raise ValueError('Caller transaction required')
        row=self.db.execute('SELECT wire,evidence,dependencies,associations FROM initial_roster_prepared WHERE id=?',(delivery,)).fetchone()
        if not row:raise ValueError('Roster invitation not prepared')
        from invitation_mime import select
        p=parse(select(row[0]));evidence=json.loads(row[1]);v=p['value']
        if not uint64(v['notBefore'])<=uint64(time['earliest'])<=uint64(time['latest'])<=uint64(v['notAfter']):raise ValueError('Roster invitation expired')
        current=instances.current(self.db,p['group'].hex())
        if current['instance']!=evidence['anchor'] or current['status']!='active':raise ValueError('Changed creation instance')
        for d,w in zip(p['proofs'],p['outer']['applicationAssertions']):d['wrapper']=w
        setting=json.loads(self.db.execute('SELECT policy FROM sender_policy WHERE id=1').fetchone()[0])
        check_proofs(self.sender.identity,self.sender.binary,p['proofs'],p['context'],credential(v['creator']),time,setting['trustPolicy'],verification=self.sender._verification_enabled())
        result=dict(contract='initial-roster-invitation-v3',invitation=v['invitation'],anchor=p['anchor'],payload=sha(p['raw']))
        if self.history is not None:
            from group_transitions import ids
            for dependency in json.loads(row[2]):
                principal,device=ids(dependency['identity'])
                checked=self.sender.identity._check_device_locked(principal,device,bytes.fromhex(dependency['key']),dependency['role'],time,setting['trustPolicy'])
                if any(checked.get(k)!=dependency[k] for k in ('status','head','binding','role')):raise ValueError('Changed original roster identity')
            initial=evidence['initialGroupContext']
            if sha(bytes.fromhex(initial))!=p['roster']['resultGroupContextDigest']:raise ValueError('Original finalized context binding')
            target=p['roster']['members'][p['target_index']]
            from transition_support import episode
            if episode(self.db,p['group'].hex(),credential(target),target['signingKey'])!='initial-roster:'+p['anchor']:raise ValueError('Initial target membership ended')
            path=self.history.path_locked(initial,target_identity=credential(target),target_key=target['signingKey'],time=time,trust_policy=setting['trustPolicy'])
            if not isinstance(self.catchup_plan,str):raise ValueError('Retained catch-up plan required')
            plan=self.db.execute('SELECT request,state,items FROM historical_plans WHERE id=?',(self.catchup_plan,)).fetchone()
            if not plan or plan[1]!='active':raise ValueError('Active retained catch-up plan required')
            request=json.loads(plan[0])
            if (request['start'],request['targetIdentity'],request['targetKey'])!=(initial,credential(target),target['signingKey']):raise ValueError('Catch-up target/ancestry mismatch')
            if request['mailbox']!=v['target']['mailbox'] or request['associationTargets']!=json.loads(row[3])['targets']:raise ValueError('Catch-up original route mismatch')
            steps=[json.loads(self.db.execute('SELECT evidence FROM historical_prepared WHERE id=?',(item,)).fetchone()[0])['decision'] for item in json.loads(plan[2])]
            if steps!=[s['decision'] for s in path['steps']]:raise ValueError('Catch-up plan does not reach checked tip')
            prior=self.db.execute('SELECT plan FROM initial_roster_catchup WHERE delivery=?',(delivery,)).fetchone()
            if prior and prior[0]!=self.catchup_plan:raise ValueError('Retained catch-up plan changed')
            self.db.execute('INSERT OR IGNORE INTO initial_roster_catchup VALUES(?,?)',(delivery,self.catchup_plan))
            result.update(tip=path['tip'],path=steps,catchupPlan=self.catchup_plan)
        return result

class InitialRosterAdmission(Admission):
    def __init__(self,identity,binary,*,verification_mechanism=None):
        super().__init__(identity,binary)
        from mailbox_association_store import MailboxAssociationStore
        if verification_mechanism not in (None,'human-comparison-v0'):raise ValueError('Verification mechanism')
        self.verification=verification_mechanism=='human-comparison-v0'
        self.associations=MailboxAssociationStore(identity);initialize(self.db)
    def accept_message(self,octets,*,target,mailbox,allow_creator,intended_principals,intended_devices,expected_context,selections,time,trust_policy,crash=None):
        if self.db.in_transaction:raise ValueError('Initial admission requires transaction ownership')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            result=self._accept_message_locked(octets,target=target,mailbox=mailbox,allow_creator=allow_creator,intended_principals=intended_principals,intended_devices=intended_devices,expected_context=expected_context,selections=selections,time=time,trust_policy=trust_policy,crash=crash)
            self.db.execute('COMMIT');return result
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def _accept_message_locked(self,octets,*,target,mailbox,allow_creator,intended_principals,intended_devices,expected_context,selections,time,trust_policy,crash=None):
        """Retain admission under the caller's larger atomic installation.

        This seam verifies the original signed octets itself. It accepts neither
        caller-asserted parsed proof objects nor peer-supplied secret checkpoints.
        The caller owns commit/rollback and must not publish the result early.
        """
        if not self.db.in_transaction:raise ValueError('Initial admission transaction required')
        MlsReceive._policy(time,trust_policy);p=parse(octets);v=p['value'];roster=p['roster'];outer=p['outer']
        if expected_context!=p['context_raw'] or allow_creator!=v['creator']['principal']:raise ValueError('Independent context/creator selection')
        expected(intended_principals,intended_devices,roster['members'])
        if any(v['target'][k]!=target[k] for k in ('principal','device')) or mailbox!=v['target']['mailbox']:raise ValueError('Local target mismatch')
        old=self.db.execute('SELECT payload,signature,result FROM initial_roster_received WHERE creator=? AND id=?',(allow_creator,v['invitation'])).fetchone()
        if old:
            if old[:2]!=(p['raw'],outer['signature']):raise ValueError('Target invitation collision')
            return json.loads(old[2])
        if not uint64(v['notBefore'])<=uint64(time['earliest'])<=uint64(time['latest'])<=uint64(v['notAfter']):raise ValueError('Invitation validity')
        interval=dict(earliest=v['notBefore'],latest=v['notAfter']);decoded=p['proofs']
        for d,w in zip(decoded,outer['applicationAssertions']):d['wrapper']=w
        rows=check_proofs(self.identity,self.binary,decoded,p['context'],credential(v['creator']),interval,trust_policy,verification=self.verification)
        reference=base64.b64decode(v['target']['keyPackageRef']).hex()
        local=self.db.execute('SELECT device,invitation FROM provider_mls_admission WHERE reference=?',(reference,)).fetchone()
        if not local or local[1] is not None:raise ValueError('Package unavailable or consumed')
        device=json.loads(local[0])
        if device['identity']!=target['identity'] or device['key']!=target['key']:raise ValueError('Local package identity/key')
        for member,proof in zip(roster['members'],decoded):
            if member['kind']=='joiner':
                actual=call(self.binary,op='package-reference',checkpoint=device['checkpoint'],key=device['key'],package=proof['assertion']['key_package_octets'].hex())['reference']
                if actual!=base64.b64decode(member['keyPackageRef']).hex():raise ValueError('Exact member package reference')
        joined=call(self.binary,op='join-initial-roster',checkpoint=device['checkpoint'],key=device['key'],identity=device['identity'],reference=reference,references=p['references'],welcome=p['welcome'].hex())
        creator=next(r for r in rows if r['identity']==credential(v['creator']))
        if joined['signerIdentity']!=creator['identity'] or joined['signerKey']!=creator['key'] or joined['group']!=p['group'].hex() or joined['epoch']!='1' or bytes.fromhex(joined['context'])!=p['context_raw'] or sha(bytes.fromhex(joined['groupContext']))!=roster['resultGroupContextDigest'] or sorted((m['identity'],m['key']) for m in joined['members'])!=sorted((r['identity'],r['key']) for r in rows):raise ValueError('Actual Welcome roster/context binding')
        if not isinstance(selections,list) or len(selections)!=len(rows):raise ValueError('Local selection coverage')
        routes=[]
        for r in rows:
            matches=[s for s in selections if isinstance(s,dict) and set(s)=={'principal','device','mailbox','generation'} and (s['principal'],s['device'])==(r['principal'],r['device'])]
            if len(matches)!=1:raise ValueError('Local device selection')
            s=matches[0];routes.append(dict(mailbox=s['mailbox'],generation=s['generation'],principal=r['principal'],observation=r['decoded']['assertion']['digest']))
        route_evidence=check_locked(self.associations,routes,dict(members=joined['members']),interval,trust_policy,verification=self.verification)
        install(self.db,joined,p['anchor'],roster,outer['applicationAssertions'],role='recipient')
        result=dict(status='admitted-unverified',group=joined['group'],instance=p['anchor'],invitation=v['invitation'],mailbox_verified=False)
        if trust_policy=='require-verification' and self.verification:result.update(status='admitted-human-verified',verification=[r['verification'] for r in route_evidence],verificationScope='human-confirmed-correspondent')
        public={k:value for k,value in joined.items() if k!='checkpoint'};public['privateState']='retired'
        self.db.execute('UPDATE provider_mls_admission SET invitation=?,joined=? WHERE reference=?',(canonical(dict(payload=outer['payload'],signature=outer['signature'])),canonical(public),reference))
        self.db.execute('INSERT INTO initial_rosters VALUES(?,?,?,?,?,?,?,?)',(v['creation'],octets,p['roster_raw'],outer['roster']['signature'],p['anchor'],p['context_raw'],'recipient',canonical(result)))
        self.db.execute('INSERT INTO initial_roster_received VALUES(?,?,?,?,?,?)',(allow_creator,v['invitation'],p['raw'],outer['signature'],v['creation'],canonical(result)))
        if crash:crash('before-commit')
        return result
