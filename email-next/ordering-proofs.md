---
title: Ordering proofs
order: 11.1
blurb: exact evidence · explicit support · durable state
sectionNav: true
---

# Ordering proofs

This experimental profile binds a membership decision to one authenticated predecessor and one exact MLS candidate. The following formats describe context7 ordering evidence; they do not grant mailbox ownership or replace current device authorization.

Existing canonical encoding is UTF-8 JSON with sorted object keys, no insignificant whitespace, no duplicate keys and no floats; each object has exactly its listed members. Strings are not normalized. Integers on the wire use canonical unsigned decimal strings with no leading zeros except `0`. Hex strings are lowercase and even length; identifiers and signatures have the exact sizes below. Null is never an omitted value. Object-list ordering is specified where material; the existing proof object array does not require hash sorting, although producers use it.

## Scope, candidate and certificate objects

Scope is `{version:"0",purpose:"ordering-scope",conversation,group,predecessor,previousDecision,ordering,slot}`. Conversation is 16 bytes encoded as 32 hex digits; group is nonempty exact MLS group-ID bytes; predecessor is the exact TLS-serialized full MLS GroupContext; previousDecision is literal `genesis` or a 32-byte digest; slot is uint64. Ordering is `{kind:"endpoint-quorum-v0",generation,faultBound,witnesses}`. Generation and faultBound are uint64. Each witness is `{principal,device,signingKey,state,binding}`: existing enp0/end0 identifiers and three 32-byte hex values. Witnesses are sorted by principal with unique principals. Keys/state/bindings must match accepted predecessor authorization, not merely well-shaped strings.

For n witnesses and configured fault bound f, require n >= 3f+1 and q = floor((n+f)/2)+1. Sort witness signer IDs (`principal + "|" + device`); view modulo n selects the coordinator. This is the existing experiment's exact quorum rule.

Candidate is `{plan,approval}`. Plan is `{version:"0",purpose:"ordering-candidate",scope,commit,result,welcomes}`. Commit is exact encrypted MLS PrivateMessage bytes as hex. Result is `{group,epoch,predecessor,context,members}`: exact group ID, uint64 epoch, full resulting GroupContext, exact application-context bytes, and ordered MLS members. Each member is `{index,identity,key}` with uint32 decimal index, exact 85-byte BasicCredential identity and 32-byte signing key. Welcomes is empty or one `{recipients,bytes}` with sorted exact added endpoint identities and exact serialized Welcome. Approval is `{signer,signature}`, using the prior-authorized administrator's exact credential and existing admin-intent signature domain. Actual MLS processing, Add KeyPackageRefs, full resulting context and intended Welcome recipients remain mandatory checks; an approval alone is insufficient.

A signed certificate object is `{body,signature}` with a 64-byte Ed25519 signature. Body contains `{version:"0",kind,scope,view,signer}` plus exactly these fields:

| kind | Additional fields |
| --- | --- |
| proposal | candidate (digest), newView (object hash or empty string) |
| prepare | proposal (object hash) |
| prepared | proposal, prepares (q sorted unique object hashes) |
| commit | prepared (object hash) |
| decision | prepared, commits (q sorted unique object hashes) |
| report | prepared (object hash or empty string) |
| new-view | reports (q sorted unique object hashes) |

Signature input is UTF-8 `email-next/ordering-experiment/<kind>/v0`, NUL, four-byte big-endian canonical-body byte length, and canonical body bytes. A signed object's reference is SHA-256 of its complete canonical signed object. Proof is `{root,objects}`; duplicate hashes, cycles, unknown objects, missing dependencies, invalid signatures, unauthorized signers and invalid unrelated objects reject the whole proof. All embedded certificates validate independently. No partial quorum is accepted.

Scope/candidate/stable-decision commitments use their existing distinct `email-next/ordering-scope/v0`, `email-next/ordering-candidate/v0`, `email-next/ordering-decision/v0` domains followed by NUL, u32 length and canonical object bytes. Stable-decision input is `{scope:<scope digest>,candidate:<candidate digest>}`. Collector and signature-set choice never changes that identity.

View0 proposal has empty newView. Higher-view proposal must carry complete same-view new-view justification and its selected candidate, if any. A report embeds only a prepared certificate from a strictly lower view. New-view selects the highest reported prepared candidate; tied highest views must agree. Prepare/commit quorum members are unique authorized witnesses; commits can reference different independently valid prepared certificates for the same candidate/view. A local higher prepared lock cannot be displaced by lower or absent new-view evidence. Durable vote publication rules remain authoritative.


## Durable witness transitions

A witness stores its minimum permitted view, highest retained prepared certificate, exact signed vote for each `(kind, view)`, and complete public dependencies. It commits these records before publishing the signature. An identical retry returns the retained signed bytes. A different candidate for an already signed prepare or commit at the same view is refused. Restored or missing signing history cannot be treated as an empty new store for the same witness key.

| Requested vote | Required evidence and durable change |
| --- | --- |
| prepare | A valid coordinator proposal and full new-view justification when view is nonzero. The view is at least the persisted minimum. A locally retained prepared certificate must not have a view greater than the proposal's selected prepared view, nor a different candidate at an equal selected view. Retain the exact candidate and proof before publication. |
| commit | A valid prepared certificate and this witness's retained prepare for the same candidate and view. A newer local prepared certificate prevents signing an older commit. Retain this prepared certificate and the exact signed commit before publication. |
| report | A target view strictly above the persisted minimum. Embed the highest retained prepared certificate, if any, and atomically advance the minimum before publishing the report. |

A delayed certificate from a lower view may still establish a decision for its exact predecessor; raising the local minimum prevents new lower-view votes, not verification of a decision that could already exist. Two different valid certified candidates for one predecessor constitute a safety conflict and hold further effects. Current identity or administrative authorization may veto installation even when a certificate is cryptographically valid. A prepared candidate made impermissible by revocation can therefore block progress; a view change does not authorize replacing that prepared value.

## Local candidate installation

Preparing a local candidate encrypts a Commit under the accepted predecessor. Before returning that candidate for voting or transport, atomically retain its exact bytes, its staged transition and the advanced outbound handshake state for that same predecessor. A second candidate, including one prepared after restart, must continue that sender state. The random MLS reuse guard does not replace durable generation continuity. A failed transaction must expose no candidate bytes; retry must not restore sender state from an older candidate checkpoint.

A candidate is not installed by restoring a checkpoint captured before intervening application traffic. A local author may retain a library-owned staged transition, bound to the exact candidate, group, predecessor and implementation format, then merge it into its latest same-predecessor group state using the cryptographic library. Peer-supplied serialized secret state is never an input to this operation. Incoming members process the actual Commit against their current local state. Both paths compare the actual resulting state with the certified result and perform current authorization checks before atomically publishing checkpoint, decision and delivery records.

The OpenMLS 0.9.1 experiment uses `clear_pending_commit` to retain the operational predecessor with its advanced handshake state, and the retained `StagedCommit` for later merge. Candidate retention and sender advancement commit together before candidate bytes return. Tests consume consecutive candidate generations after restart, inject retention failures and process crashes, and preserve caller transaction ownership. Same-predecessor legacy staged records without continuity evidence require fresh admission; already exposed old generations cannot be repaired retrospectively.

The experiment uses this staged merge. Tests advance outbound and inbound application ratchets after preparing the candidate, exercise real process crashes before and after installation, reject a changed local staged-format binding, retry the same decision, and exchange protected application messages afterward. These fixtures use zero retained past epochs; they do not establish delayed old-epoch behavior for every retention policy.

## Complete-input limits

The mail carrier accepts at most 2 MiB of MIME and 1 MiB of canonical JSON. The proof experiment additionally bounds a complete graph to 4,096 objects and a recursion depth of 64; these are adjustable implementation resource defaults. A smaller supported limit may return `unsupported-size` and hold the input. It cannot accept a partial quorum or classify the peer as malicious solely for exceeding a local limit. Nested proofs include all dependencies within the same complete-input budget.
