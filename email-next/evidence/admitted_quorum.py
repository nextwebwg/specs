"""Quorum installation over the same admitted MLS checkpoint as application traffic.

No discovery acquisition or established-member Welcome admission is inferred.
"""
import hashlib,json
from ordering_mls import JoinedOrdering,candidate_id
from ordering_certificates import Proof,encode
from ordering_scope import scope_digest,decision_identity
from provider_mls import call
from mls_receive import FORMAT
import membership_episodes as episodes
import group_instances

class AdmittedQuorum(JoinedOrdering):
    def __init__(self,receiver,binary,device):
        super().__init__(receiver.identity,binary,device)
        self.receiver=receiver
        from quorum_exchange_support import initialize as exchange_initialize
        exchange_initialize(self.db)
        self.db.execute('CREATE TABLE IF NOT EXISTS qo_stage_revision(candidate TEXT PRIMARY KEY,revision INTEGER NOT NULL)')
    def install_fixture(self,state):raise ValueError('Signed initial roster admission required')
    def configure_support(self,*args):raise ValueError('Signed per-device tuple evidence required')
    def live(self):
        row=self.db.execute('SELECT revision,format,group_id,snapshot FROM mls_checkpoint WHERE id=1').fetchone()
        if not row or row[1]!=FORMAT:raise ValueError('Current checkpoint required')
        current=group_instances.optional_current(self.db,row[2])
        if not current or not self.receiver.configured_quorum_ordering(row[2]):raise ValueError('Signed quorum admission required')
        record=self.db.execute('SELECT previous,context,commitment FROM mls_quorum_admission WHERE instance=?',(current['instance'],)).fetchone()
        inspected=call(self.binary,op='inspect',checkpoint=json.loads(row[3]),group=row[2],key=self.device['key'])
        if (inspected['snapshot']['context'],inspected['snapshot']['predecessor'])!=record[1:]:raise ValueError('Quorum checkpoint binding')
        return record[0],dict(checkpoint=inspected['checkpoint'],snapshot=inspected['snapshot'],revision=row[0])
    def check_support(self,member,application):
        current=group_instances.current(self.db,self.live()[1]['snapshot']['group'])
        agreement=self.receiver.application_agreement.resolve(current['group'],[member],instance=current['instance'])
        if agreement!=application:
            row=self.db.execute('SELECT key,wrapper FROM qo_join_support WHERE identity=?',(member['identity'],)).fetchone()
            if not row or row[0]!=member['key']:raise ValueError('Signed quorum application agreement')
            from passive_discovery import decode_passive_discovery
            from application_support import supports
            if not supports(decode_passive_discovery(row[1])['assertion']['value'],application,'endpoint-quorum-v0'):raise ValueError('Exact joining application agreement')
    def _continue_locked(self,state,result):
        self.db.execute('UPDATE mls_checkpoint SET revision=revision+1,snapshot=? WHERE id=1',(encode(result['continuedCheckpoint']),))
    def stage(self,*args,crash=None,**kwargs):
        if self.db.in_transaction:raise ValueError('stage requires transaction ownership')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            revision=self.live()[1]['revision'];candidate=self._stage_locked(*args,**kwargs)
            self.db.execute('INSERT INTO qo_stage_revision VALUES(?,?)',(candidate_id(candidate),revision))
            if crash:crash('before-commit')
            self.db.execute('COMMIT')
            if crash:crash('after-commit')
            return candidate
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
    def _inspect_candidate_locked(self,candidate,*,time,terminal=False):
        local=self.db.execute('SELECT state FROM qo_staged WHERE candidate=?',(candidate_id(candidate),)).fetchone()
        if local:
            retained=json.loads(local[0]);state=self.live()[1];before=state['snapshot']
            if retained.get('senderContinuity')!='openmls-0.9.1/continued-v1':raise ValueError('Legacy staged sender continuity requires fresh admission')
            binding=dict(library='openmls-0.9.1/staged-v0',candidate=candidate_id(candidate),group=before['group'],predecessor=before['predecessor'],digest=hashlib.sha256(encode(retained.get('localStaged'))).hexdigest())
            if retained.get('localStageBinding')!=binding:raise ValueError('Exact local staged binding required')
            merged=call(self.binary,op='merge-local-staged',checkpoint=state['checkpoint'],group=before['group'],key=self.device['key'],library=binding['library'],predecessor=binding['predecessor'],staged=retained['localStaged'])
            result={**retained,**merged,'wire':candidate['plan']['commit']}
            self.validate(candidate,result,time=time)
        elif terminal:
            state=self.live()[1]
            local=self.db.execute('SELECT state FROM qo_staged WHERE candidate=?',(candidate_id(candidate),)).fetchone()
            result=json.loads(local[0]) if local else call(self.binary,op='receive-quorum',checkpoint=state['checkpoint'],group=state['snapshot']['group'],key=self.device['key'],wire=candidate['plan']['commit'],expectedContext=candidate['plan']['result']['predecessor'])
            result['wire']=candidate['plan']['commit']
            if result.get('selfRemoved'):
                claimed=candidate['plan']['result'];own=self.device['identity']
                if result.get('unsupported') or result.get('terminalPublicFieldsMatch') is not True or own not in {m['identity'] for m in result['before']['members']} or own in {m['identity'] for m in claimed['members']}:raise ValueError('Exact certified terminal result')
                # Only install calls this branch after complete certificate validation.
                # OpenMLS's inactive tree is not a separately verified resulting roster.
                result['after']=claimed;result['selfRemoved']=False
                self.validate(candidate,result,time=time)
                result['selfRemoved']=True
            else:self.validate(candidate,result,time=time)
        else:result=super()._inspect_candidate_locked(candidate,time=time)
        old={(m['identity'],m['key']) for m in result['before']['members']}
        from quorum_join_support import current_added
        current_added(self,[m for m in result['after']['members'] if (m['identity'],m['key']) not in old],time=time)
        from quorum_join_support import check_add_references
        check_add_references(self,result,time=time)
        if self.db.execute('SELECT 1 FROM qo_signed_exchange_support WHERE group_id=?',(result['before']['group'],)).fetchone():
            from quorum_exchange_support import current
            current(self,time=time,context=json.loads(bytes.fromhex(result['after']['context'])))
        return result
    def install(self,candidate,proof_bytes,*,time,crash=None,application_assertions=None,witness_assertions=None,report=False):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            scope=candidate['plan']['scope'];sd=scope_digest(scope);cid=candidate_id(candidate);decision=decision_identity(scope,cid)
            prior=self.db.execute('SELECT candidate,identity FROM qo_decision WHERE scope=?',(sd,)).fetchone()
            signed_mode=self.db.execute('SELECT 1 FROM qo_signed_exchange_support WHERE group_id=?',(scope['group'],)).fetchone() is not None
            if prior:
                if prior!=(cid,decision):raise ValueError('Conflicting decided branch')
                keys={w['principal']+'|'+w['device']:w['signingKey'] for w in scope['ordering']['witnesses']}
                retained_proof=self.db.execute('SELECT proof FROM qo_decision WHERE scope=?',(sd,)).fetchone()[0]
                original=Proof(retained_proof,scope=sd,keys=keys,f=int(scope['ordering']['faultBound']))
                supplied=Proof(proof_bytes,scope=sd,keys=keys,f=int(scope['ordering']['faultBound']))
                if original.result['kind']!='decision' or original.result['candidate']!=cid or supplied.result['kind']!='decision' or supplied.result['candidate']!=cid:raise ValueError('Retained decision proof binding')
                if witness_assertions is not None:
                    retained=json.loads(self.db.execute('SELECT bytes FROM qo_outbox WHERE identity=?',(decision,)).fetchone()[0])
                    if retained.get('witnessAssertions')!=witness_assertions:raise ValueError('Retained witness assertion conflict')
                if application_assertions is not None:
                    retained=json.loads(self.db.execute('SELECT bytes FROM qo_outbox WHERE identity=?',(decision,)).fetchone()[0])
                    if retained.get('applicationAssertions',[])!=application_assertions:raise ValueError('Retained assertion conflict')
                self.db.execute('COMMIT');return {'status':'already-installed','decision':decision} if report else decision
            if scope!=self.scope():raise ValueError('Stale quorum scope')
            witness_digests=None
            if witness_assertions is not None or signed_mode:
                from quorum_exchange_support import current,complete
                resulting_context=json.loads(bytes.fromhex(candidate['plan']['result']['context']))
                if witness_assertions is None:witness_assertions=current(self,time=time,context=resulting_context)
                witness_digests=complete(self.identity,witness_assertions,resulting_context,time=time)
                from quorum_exchange_support import retain_locked
                retain_locked(self.db,scope['group'],witness_assertions,witness_digests)
            proof=Proof(proof_bytes,scope=sd,keys=self.keys(),f=int(scope['ordering']['faultBound']))
            if proof.result['kind']!='decision' or proof.result['candidate']!=cid:raise ValueError('Decision binding')
            if application_assertions is not None:
                before={m['identity'] for m in self.live()[1]['snapshot']['members']}
                added_claims=[m for m in candidate['plan']['result']['members'] if m['identity'] not in before]
                from quorum_join_support import stage_carried_locked
                stage_carried_locked(self,application_assertions,added_claims,time=time)
            result=self.inspect_candidate(candidate,time=time,terminal=True)
            from quorum_join_support import check_add_references
            carried=check_add_references(self,result,time=time)
            old={(m['identity'],m['key']) for m in result['before']['members']}
            added=[m for m in result['after']['members'] if (m['identity'],m['key']) not in old]
            from quorum_join_support import install_support_locked
            install_support_locked(self,added,time=time,decision=decision)
            self.db.execute('INSERT INTO qo_decision VALUES(?,?,?,?)',(sd,cid,decision,proof_bytes))
            episodes.transition(self.db,result,decision)
            self.db.execute('UPDATE mls_checkpoint SET revision=revision+1,snapshot=? WHERE id=1',(encode(result['checkpoint']),))
            current=group_instances.optional_current(self.db,result['after']['group'])
            self.db.execute('UPDATE mls_quorum_admission SET previous=?,context=?,commitment=? WHERE instance=?',(decision,result['after']['context'],result['after']['predecessor'],current['instance']))
            carrier=encode(dict(version='2' if witness_assertions is not None else '1',purpose='quorum-control-experiment',candidate=candidate,proof=proof_bytes.hex(),applicationAssertions=carried,**({'witnessAssertions':witness_assertions} if witness_assertions is not None else {})))
            if witness_assertions is not None:
                from quorum_exchange_support import retain_locked
                retain_locked(self.db,scope['group'],witness_assertions,witness_digests)
            if len(carrier)>1048576:raise ValueError('unsupported-size')
            self.db.execute('INSERT INTO qo_outbox VALUES(?,?)',(decision,carrier))
            self.db.execute('INSERT INTO qo_history VALUES(?,?)',(decision,carrier))
            from quorum_retention import decided_locked
            decided_locked(self.db,group=scope['group'],predecessor=scope['predecessor'],decision=decision)
            if crash:crash('before-commit')
            self.db.execute('COMMIT')
            if crash:crash('after-commit')
            return {'status':'accepted','decision':decision} if report else decision
        except BaseException:
            if self.db.in_transaction:self.db.execute('ROLLBACK')
            raise
