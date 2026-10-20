"""Local reference store; not a mailbox verifier or transport authorization API.

observe_validated_batch requires caller-verified assertion signatures and trusted
outer-From parsing. Syntax checks here cannot establish either prerequisite.
No boolean or incoming verification claim can enable verified association.
Selection rechecks accepted identity authority in the SAME SQLite transaction.
"""
import json
from passive_discovery import decode_assertion, mailbox_syntax, hexadecimal, uint64


def _id(value):
    return hexadecimal(value, 32) and value != '0'*32


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


class MailboxAssociationStore:
    def __init__(self, identity_store):
        self.identity = identity_store
        self.db = identity_store.db  # Caller owns connection and lifetime.
        if self.db.in_transaction:
            raise ValueError('Cannot initialize inside caller transaction')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS mailbox_observations (
            mailbox TEXT NOT NULL, digest TEXT NOT NULL, principal TEXT NOT NULL,
            assertion BLOB NOT NULL, signature BLOB NOT NULL, signing_key BLOB NOT NULL,
            PRIMARY KEY(mailbox,digest));
          CREATE TABLE IF NOT EXISTS mailbox_observation_variants (
            mailbox TEXT NOT NULL,digest TEXT NOT NULL,assertion BLOB NOT NULL,
            signature BLOB NOT NULL,signing_key BLOB NOT NULL,source TEXT NOT NULL,
            PRIMARY KEY(mailbox,digest,signature,signing_key,source));
          CREATE TABLE IF NOT EXISTS mailbox_authenticated_records (
            principal TEXT NOT NULL,device TEXT NOT NULL,record TEXT NOT NULL,digest TEXT NOT NULL,
            PRIMARY KEY(principal,device,record,digest));
          CREATE TABLE IF NOT EXISTS mailbox_sources (
            mailbox TEXT NOT NULL,digest TEXT NOT NULL,source TEXT NOT NULL,
            PRIMARY KEY(mailbox,digest,source));
          CREATE TABLE IF NOT EXISTS mailbox_associations (
            mailbox TEXT PRIMARY KEY,generation TEXT NOT NULL,principal TEXT NOT NULL,
            enabled INTEGER NOT NULL,decision_id TEXT NOT NULL,identity_anchor TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS mailbox_decisions (
            decision_id TEXT PRIMARY KEY,request TEXT NOT NULL,result TEXT NOT NULL);
        ''')

    def _transaction(self, operation):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            result = operation()
            self.db.execute('COMMIT')
            return result
        except BaseException:
            self.db.execute('ROLLBACK')
            raise

    def observe_validated_batch(self, observations):
        return self._observe_batch(observations,locked=False)

    def _observe_validated_batch_locked(self,observations):
        if not self.db.in_transaction:raise ValueError('Transaction required')
        return self._observe_batch(observations,locked=True)

    def _observe_batch(self, observations, *,locked):
        """Local trusted input, NOT network input. Whole batch syntax-checks first.

        Required dict keys: assertion/signature/signingKey bytes, outerFrom list
        of parsed normalized mailbox strings, sourceId/parserRevision/observedAt.
        Caller must verify the exact assertion/signature/signingKey proof, as in
        verify_passive_discovery; a successful snapshot-authorized-unverified result
        is the normal ingestion path. No caller authentication boolean is accepted.
        This store rechecks identity authority at observedAt before indexing a
        record as authenticated. observedAt is a local point timestamp, not a
        replacement for the credible interval already validated by the caller;
        callers must not narrow uncertain time merely to pass these checks.
        Caller owns trusted parser provenance. No identity is
        installed. A-labels require the explicitly configured Unicode17 acceptance provider.
        """
        checked = []
        for item in observations:
            if set(item) != {'assertion','signature','signingKey','outerFrom','sourceId','parserRevision','observedAt'}:
                raise ValueError('Invalid local observation fields')
            if not isinstance(item['assertion'], bytes):
                raise ValueError('Expected original assertion bytes')
            parsed = decode_assertion(item['assertion'])
            v = parsed['value']
            if parsed['mailbox_syntax'] != 'syntax-valid':
                raise ValueError('A-label validation unavailable')
            if item['outerFrom'] != [v['mailbox']]:
                raise ValueError('Sole parsed outer From must exactly match')
            for key, length in [('signature',64),('signingKey',32)]:
                if not isinstance(item[key],bytes) or len(item[key]) != length:
                    raise ValueError('Invalid proof/key bytes')
            if any(not isinstance(item[k],str) or not item[k] for k in ['sourceId','parserRevision']):
                raise ValueError('Missing local provenance')
            uint64(item['observedAt'])
            source = _json({k:item[k] for k in ['sourceId','parserRevision','observedAt','outerFrom']})
            checked.append((v, parsed['digest'], bytes(item['assertion']), bytes(item['signature']), bytes(item['signingKey']), source))
        def store():
            results=[]
            for v,digest,raw,sig,key,source in checked:
                prior=self.db.execute('SELECT assertion,signature,signing_key FROM mailbox_observations WHERE mailbox=? AND digest=?',(v['mailbox'],digest)).fetchone()
                self.db.execute('INSERT OR IGNORE INTO mailbox_observation_variants VALUES(?,?,?,?,?,?)',
                    (v['mailbox'],digest,raw,sig,key,source))
                self.db.execute('INSERT OR IGNORE INTO mailbox_sources VALUES(?,?,?)',(v['mailbox'],digest,source))
                observed_at=json.loads(source)['observedAt']
                authority=self.identity._check_device_locked(v['principal'],v['device'],key,'receive',
                    {'earliest':observed_at,'latest':observed_at},'allow-unverified')
                authorized=(authority.get('status')=='authorized-unverified' and authority['head']==v['state']
                        and authority['binding']==v['binding']
                        and int(v['notBefore'])<=int(observed_at)<=int(v['notAfter']))
                authenticated=self.db.execute('SELECT 1 FROM mailbox_authenticated_records WHERE principal=? AND device=? AND record=? AND digest=?',
                    (v['principal'],v['device'],v['record'],digest)).fetchone()
                if prior is None or (authorized and not authenticated):
                    self.db.execute('INSERT OR REPLACE INTO mailbox_observations VALUES(?,?,?,?,?,?)',
                        (v['mailbox'],digest,v['principal'],raw,sig,key))
                if authorized:
                    self.db.execute('INSERT OR IGNORE INTO mailbox_authenticated_records VALUES(?,?,?,?)',
                        (v['principal'],v['device'],v['record'],digest))
                current=self._current(v['mailbox'])
                results.append({'digest':digest,'status':'unlinked-claim' if current and current['principal']!=v['principal'] else 'observed-caller-validated'})
            return results
        return store() if locked else self._transaction(store)

    def _current(self,mailbox):
        row=self.db.execute('SELECT generation,principal,enabled,decision_id,identity_anchor FROM mailbox_associations WHERE mailbox=?',(mailbox,)).fetchone()
        return dict(zip(['generation','principal','enabled','decisionId','identityAnchor'],row)) if row else None

    def snapshot(self,mailbox):
        return self._transaction(lambda:{'association':self._current(mailbox),
            'observations':self.db.execute('SELECT principal,digest FROM mailbox_observations WHERE mailbox=? ORDER BY principal,digest',(mailbox,)).fetchall()})

    def eligible_observation_locked(self, mailbox, digest, time):
        """Transaction-scoped retained evidence; caller owns commit and policy.

        Reuses the ingestion trust boundary, not a new proof or ownership verifier.
        """
        if not self.db.in_transaction:raise ValueError('Caller transaction required')
        row=self.db.execute('SELECT assertion,signing_key FROM mailbox_observations WHERE mailbox=? AND digest=?',(mailbox,digest)).fetchone()
        if not row:return None
        raw,key=row;parsed=decode_assertion(raw);v=parsed['value']
        if parsed['digest']!=digest or v['mailbox']!=mailbox:return None
        records=self.db.execute('SELECT digest FROM mailbox_authenticated_records WHERE principal=? AND device=? AND record=?',(v['principal'],v['device'],v['record'])).fetchall()
        if records != [(digest,)]:return None
        if int(time['earliest'])<int(v['notBefore']) or int(time['latest'])>int(v['notAfter']):return None
        checked=self.identity._check_device_locked(v['principal'],v['device'],key,'receive',time,'allow-unverified')
        if checked.get('status')!='authorized-unverified' or checked['head']!=v['state'] or checked['binding']!=v['binding']:return None
        return {'assertion':v,'key':key.hex(),'head':checked['head'],'binding':checked['binding']}

    def decide(self,**options):
        return self._decide(locked=False,**options)

    def _decide_locked(self,**options):
        if not self.db.in_transaction:raise ValueError('Transaction required')
        return self._decide(locked=True,**options)

    def _decide(self, *, locked, decision_id, mailbox, expected_generation, kind, principal,
               actor, policy_revision, trust_policy, time):
        """Local caller requests a decision; actor is NOT a remote authentication claim.

        expected_generation is None for absent row, otherwise canonical decimal.
        Exact decision retries return stored results, including held/stale results.
        A new attempt after changed inputs requires a new decision ID.
        """
        if not _id(decision_id) or mailbox_syntax(mailbox)!='syntax-valid':
            raise ValueError('Invalid decision identity/mailbox')
        if expected_generation is not None:uint64(expected_generation)
        if kind not in ('first-contact','resolve-first-contact','replace-with-continuity-break','disable','enable'):
            raise ValueError('Unknown decision kind')
        if actor not in ('configured-policy','local-user') or (kind!='first-contact' and actor!='local-user'):
            raise ValueError('Explicit local user decision required')
        if trust_policy not in ('allow-unverified','require-verification') or not isinstance(policy_revision,str) or not policy_revision:
            raise ValueError('Explicit local policy required')
        if not isinstance(principal,str) or not principal.startswith('enp0:') or not hexadecimal(principal[5:],64) or principal[5:]=='0'*64:
            raise ValueError('Invalid principal')
        if not isinstance(time,dict) or set(time)!= {'earliest','latest'} or uint64(time['earliest'])>uint64(time['latest']):
            raise ValueError('Expected time interval')
        request=_json(dict(mailbox=mailbox,expectedGeneration=expected_generation,kind=kind,principal=principal,actor=actor,policyRevision=policy_revision,trustPolicy=trust_policy,time=time))
        # Freeze input shared by the serialized request and transaction checks.
        time=json.loads(request)['time']
        def select():
            prior=self.db.execute('SELECT request,result FROM mailbox_decisions WHERE decision_id=?',(decision_id,)).fetchone()
            if prior:
                if prior[0]!=request:raise ValueError('Decision ID reused with different input')
                return json.loads(prior[1])
            def finish(result):
                self.db.execute('INSERT INTO mailbox_decisions VALUES(?,?,?)',(decision_id,request,_json(result)))
                return result
            current=self._current(mailbox)
            if (current['generation'] if current else None)!=expected_generation:
                return finish({'status':'stale'})
            if kind in ('first-contact','resolve-first-contact') and current:
                return finish({'status':'existing-association'})
            if kind in ('replace-with-continuity-break','disable','enable') and not current:
                return finish({'status':'pending','reason':'existing-association'})
            if kind in ('disable','enable') and principal!=current['principal']:
                return finish({'status':'invalid','reason':'principal'})
            if kind=='replace-with-continuity-break' and principal==current['principal']:
                return finish({'status':'invalid','reason':'replacement-must-change-principal'})
            if kind in ('disable','enable') and bool(current['enabled']) == (kind=='enable'):
                return finish({'status':'no-change','generation':current['generation'],'sendAuthorized':False})
            eligible={}
            if kind!='disable':
                for (digest,) in self.db.execute('SELECT digest FROM mailbox_observations WHERE mailbox=?',(mailbox,)):
                    evidence=self.eligible_observation_locked(mailbox,digest,time)
                    if evidence:eligible.setdefault(evidence['assertion']['principal'],[]).append((digest,evidence['head']))
                if kind=='first-contact' and len(eligible)>1:
                    return finish({'status':'ambiguous'})
                if principal not in eligible:
                    return finish({'status':'pending','reason':'no-eligible-candidate'})
                if trust_policy=='require-verification':
                    return finish({'status':'verification-required'})
            generation=str(int(expected_generation or '0')+1)
            uint64(generation)
            selected=sorted(eligible.get(principal,[]))
            anchor=current['identityAnchor'] if kind=='disable' else selected[0][1]
            self.db.execute('INSERT OR REPLACE INTO mailbox_associations VALUES(?,?,?,?,?,?)',(mailbox,generation,principal,int(kind!='disable'),decision_id,anchor))
            return finish({'status':'disabled' if kind=='disable' else 'associated-unverified',
                'generation':generation,'principal':principal,'identityAnchor':anchor,
                'observations':[x[0] for x in selected], 'reviewedCandidates':sorted(eligible),
                'continuityBreak':kind=='replace-with-continuity-break','sendAuthorized':False})
        return select() if locked else self._transaction(select)
