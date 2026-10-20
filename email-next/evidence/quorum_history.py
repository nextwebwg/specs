"""Bounded local certificate ancestry retrieval; never grants membership."""
import base64,json
from ordering_certificates import encode
from ordering_mls import candidate_id
from ordering_scope import decision_identity
from initial_roster import credential
from quorum_join import verify_path
import group_instances

class QuorumHistory:
    def __init__(self,group,*,max_bytes=1048576):
        if type(max_bytes) is not int or max_bytes<1:raise ValueError('Local history bound')
        self.group=group;self.db=group.db;self.max_bytes=max_bytes
    def path_locked(self,start,*,target_identity,target_key,time):
        if not self.db.in_transaction:raise ValueError('Caller transaction required')
        tip,state=self.group.live();current=group_instances.current(self.db,state['snapshot']['group'])
        row=self.db.execute('SELECT roster FROM qo_genesis WHERE instance=?',(current['instance'],)).fetchone()
        if not row:raise ValueError('Retained genesis required')
        roster=json.loads(row[0]);reverse=[];seen=set();cursor=tip;size=0
        while cursor!='genesis':
            if cursor in seen:raise ValueError('History cycle')
            seen.add(cursor);row=self.db.execute('SELECT carrier FROM qo_history WHERE decision=?',(cursor,)).fetchone()
            if not row:raise ValueError('History gap')
            size+=len(row[0])
            if size>self.max_bytes:raise ValueError('unsupported-size')
            value=json.loads(row[0]);candidate=value['candidate']
            if decision_identity(candidate['plan']['scope'],candidate_id(candidate))!=cursor:raise ValueError('History decision mismatch')
            reverse.append(dict(decision=cursor,carrier=row[0],candidate=candidate,proof=base64.b64encode(bytes.fromhex(value['proof'])).decode()))
            cursor=candidate['plan']['scope']['previousDecision']
        edges=list(reversed(reverse))
        if not edges:raise ValueError('No retained transitions')
        verified=verify_path(self.group.identity,roster,[{k:e[k] for k in ('candidate','proof')} for e in edges],time=time)
        if verified['decision']!=tip or edges[-1]['candidate']['plan']['result']['predecessor']!=state['snapshot']['predecessor']:raise ValueError('History tip binding')
        before={credential(m):m['signingKey'] for m in roster['members']};chosen=[];started=False;ended=False
        author=self.group.device['identity'];author_key=self.group.device['key']
        for edge in edges:
            plan=edge['candidate']['plan'];after={m['identity']:m['key'] for m in plan['result']['members']}
            if plan['scope']['predecessor']==start:
                if started:raise ValueError('Ambiguous history start')
                started=True
            if started:
                if before.get(author)!=author_key or after.get(author)!=author_key:raise ValueError('Historical sender membership gap')
                if not ended:
                    if before.get(target_identity)!=target_key:raise ValueError('Recipient membership gap')
                    terminal=target_identity not in after
                    if not terminal and after.get(target_identity)!=target_key:raise ValueError('Recipient key change')
                    chosen.append(dict(edge,terminal=terminal));ended=terminal
                elif target_identity in after:raise ValueError('Recipient rejoined; old terminal route held')
            before=after
        if not started or not chosen:raise ValueError('Unknown history predecessor')
        if not ended:self.group.current({'identity':target_identity,'key':target_key},'receive',time)
        self.group.current({'identity':author,'key':author_key},'send',time)
        return chosen
