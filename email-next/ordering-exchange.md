---
title: Exchanging ordering evidence
order: 11.2
blurb: exact evidence · explicit support · durable state
sectionNav: true
---

# Exchanging ordering evidence

This experimental extension carries predecision ordering evidence over ordinary email. Implementations must explicitly select support for this wrapper; existing final-control support does not imply it. The local experiment exercises this flow through the durable sender and a loopback SMTP server. It does not establish independent-client interoperability.

## Mail wrapper

The signed-discovery profile uses purpose `quorum-exchange-experiment`, version `1`, with the readable text/plain + application/json attachment arrangement and inherited complete MIME/JSON limits. Its exact JSON object is `{version,purpose,scope,proof,candidates,witnessAssertions}`. Scope is the [complete ordering scope](ordering-proofs.md); proof is hex of complete canonical proof bytes; candidates is a digest-sorted unique array of exact candidate objects. It must contain exactly every candidate referenced by the proof graph, including lower-view prepared dependencies. Report graphs with no candidate have an empty array. Every candidate must bind this exact scope. Missing, extra, conflicting or oversized dependencies prevent accepting the complete exchange; never vote from a partial graph.

`witnessAssertions` contains complete signed assertion7 wrappers for every resulting witness, sorted by principal and device without duplicates or extra wrappers. The root-selected candidate determines the resulting context; a root with no selected candidate uses the predecessor context. Each wrapper must bind that witness's exact principal, device, accepted state, binding and signing key. Validate signatures, current authorization, expiry and the selected application tuple. These assertions establish support; only the certified predecessor policy grants voting authority.
The signed proof root determines the action; there is no unsigned action field. Proposal/prepared/new-view may trigger a local eligible vote after current authorization and durable dependency retention. Prepare/commit/report roots feed local aggregation only. Decision roots enter the existing final installation path with its required current application assertions; the predecision wrapper itself does not bypass final carrier2 support validation. Aggregators have no extra authority.

### Explicit exchange support

The exact signed capability is `orderingExchanges:[{format:"quorum-exchange-experiment",version:"1"}]` in [passive assertion7](passive-discovery.md). It uses the fixed `email-next/passive-discovery/v7` signature domain. Initial invitation7/roster4 and established invitation7 require assertion7 from every admitted device, including non-voters. This selection also denotes reception of final carrier2. It never grants a non-voter voting authority, and support for old context7/carrier1 does not imply either new wrapper.

Retain the authenticated selected assertion bytes and their digest. Enqueuing and every dispatch attempt require current sender and target support, current identity/binding/key and unexpired assertions. Each immutable outbox binds its selected digests; renewed evidence cannot silently change an existing delivery. Missing, expired, withdrawn or mismatched support holds delivery. It does not reduce quorum or downgrade the format. Incoming unsupported mail has no voting or automatic-response effects.

Final carrier2 has the carrier1 fields plus required `witnessAssertions`. Its separate `applicationAssertions` cover exactly the actual MLS Add packages, using assertion7; witness assertions cover every resulting witness even when it was already known locally. Established invitation7 retains each ordering-path edge as exactly `{candidate,proof,applicationAssertions,witnessAssertions}`. Validate complete historical supplemental signatures and certified bindings without treating old expiry as renewed current authority. Final admission and subsequent dispatch independently require current support. The candidate and decision identities remain unchanged: supplemental evidence is independently authenticated, not a new consensus identity.

The older configured experiment remains exact version0 `{version,purpose,scope,proof,candidates}`, selected by trusted local records `{version:"0",purpose:"ordering-exchange-support",principal,device,signingKey,state,binding,format:"quorum-exchange-experiment",formatVersion:"0"}`. It is separate from assertion7 and exchange1, and does not provide automatic discovery. Older assertion6, initial6/roster3, established6 and carrier1 retain their existing strict schemas.
Delivery targets are the exact predecessor witness endpoints using locally accepted current routes; a sender cannot add recipients from untrusted headers. Withdrawal, missing current route, identity conflict or expired support holds dispatch. Each locally produced signed root is enqueued at most once per intended endpoint under `(scope,root,target)`; exact retries have separate attempts and explicit uncertainty authorization. Receiving an identical root neither produces a second vote nor an unbounded response. No DSN, automatic acknowledgment, legacy auto-reply or incoming unsigned request creates voting work. Unupgraded clients may display the readable control note; this format does not promise invisible legacy delivery.

A coordinator reannouncement carries the complete retained candidate/proof graph. This deliberately avoids introducing a separate unauthenticated retrieval service. A participant lacking bytes cannot vote or replace a prepared value; it can obtain the same signed exchange through an explicitly authorized resend. A subsequent version may add authenticated requests, but the selected flow does not depend on one. Mail delivery remains asynchronous, reorderable and duplicate-prone.

## Durability and retention

Before a prepare becomes publishable, retain exact candidate bytes and every proof dependency in durable content-addressed storage, then commit the signing-store vote referencing their manifest. Storage acknowledgment means actual durable commit, not an in-memory cache. With separate databases, write dependencies first; write vote second; create dispatch record last. A restart reconstructs a missing dispatch record from the retained vote. A crash before the vote leaves an unreferenced candidate that can be collected after a local reachability scan; a crash after the vote must never permit collecting its manifest. Missing referenced bytes quarantines signing/publication until restored exactly. Never recreate an allegedly lost voting database and reuse that signing identity automatically.

A [validated proposal observation](group-conversations.md#pause-content-while-a-membership-plan-is-pending) is a separate durable obligation from retaining candidate bytes. Retain that observation before publishing a vote, including when the signing store uses another database; reacquire current scope and authority before signing. Abandoning or collecting an otherwise unreferenced candidate does not remove an observation for the active predecessor epoch. A valid raw wrapper has no such effect until complete MLS and application inspection succeeds.

A validated winning decision permits retiring losing secret candidate checkpoints for that exact predecessor after local installation commits. Retain public candidates and proof dependencies reachable from decisions, prepared locks, signed reports, pending/uncertain outboxes, and offline catch-up history. An unprepared local candidate with no published vote, outbox, or dependency may be explicitly abandoned; absence of a decision is not proof a published prepared candidate is dead. Installing a winning decision retires that slot's private staged secrets, but preserves a compact signed-vote safety record and public decision ancestry. Do not delete safety history merely because a wall-clock timer expires.

Public history retention is bounded by supported offline recovery policy, not silent garbage collection. If an implementation intentionally retires an old public path, record the unavailable range and require a separately authorized fresh admission for endpoints needing it; never skip the gap or pretend continuous membership. Pending invitations and pinned history deliveries block retirement. Full local conversation retirement disables signing and application release before deleting live state, retaining the safety tombstone needed to prevent accidental key/state reuse. Physical erasure remains separate.


## Equivalent proof and cached decision outcomes

Validate every supplied proof graph even for an already installed decision. A valid equivalent proof returns `already-installed`, makes no epoch/application change and does not require replaying consumed Commit keys. Validate against retained authenticated predecessor policy; distinguish this historical result from current authorization to send or install something new. Invalid replacement evidence returns invalid-proof rather than generic accepted.

Retain the first complete valid public candidate under stable decision identity. Additional valid proof graphs for that identical candidate are equivalent evidence, not equivocation and not a reason to fail catch-up. Different candidate bytes under the same claimed digest fail digest validation. Distinct candidates certified for the same slot are a safety conflict and freeze further effects. Serialization differences alone do not create such a conflict. Retain an authoritative complete proof graph, optionally bounded alternatives; never discard dependencies required by a currently retained root.

## Explicit unsupported and terminal outcomes

Context7 continues selected membership and certified ordering-policy changes. It does not silently enable administrator changes, application/delivery changes, ReInit or subgroup admission. An unsupported requested transition produces an explicit unsupported-operation outcome without publishing a vote or mutating the group. Incoming unsupported MLS proposals/Commits remain held with their exact bytes; they do not become a partial membership transition.

Designated-writer profiles do not acquire quorum takeover semantics. Permanent writer/admin loss prevents those privileged transitions; ordinary application use continues only while its existing current authorization permits it. A user may close the local conversation or authorize a separately identified new conversation with fresh admission. Such a conversation is not an authenticated continuation, does not inherit old history access and cannot be represented as successful ReInit. Quorum coordinator succession is supported only while the configured fault bound, available honest quorum and required current authority permit it. Prepared-but-revoked candidates may block progress; ordinary view change does not override that authority veto.


## Implementation evidence

[`quorum_exchange.py`](evidence/quorum_exchange.py) parses the complete wrapper and records explicit target support. `SenderWorker.submit_quorum_exchange` retains immutable MIME and rechecks current authority, routing, policy and support before transport. [`test_quorum_exchange.py`](evidence/test_quorum_exchange.py) covers missing/withdrawn support, exact dependency closure, lost SMTP response and explicit retry, duplicate receipt without MLS effects, prepared/decision mail, and final carrier installation. Receiving exchange evidence alone never installs a transition or automatically generates a response.

The joined vote path persists exact candidate bodies in the durable signing database in the same transaction as its prepare/commit vote. Candidate bodies and proof dependencies can be recovered after reopening that store. After certified installation, `quorum_retention.py` removes local staged secret objects and obsolete candidate checkpoints while retaining public transition records. This is logical retirement; filesystem and backup erasure are not established. The experiment retains public history and voting safety records indefinitely. It does not yet provide bounded public-history pruning; an implementation adding that option must honor the pins and explicit unavailable-range/fresh-admission rules above.

[`test_proposal_observation.py`](evidence/test_proposal_observation.py) checks local and received inline proposals, raw exchange receipt without a hold, authenticated Add/Remove/mixed/context changes, restart, retention rollback, signed-discovery carrier installation, bound ordinary copies and a hold arriving after release but before SMTP DATA. The actual OpenMLS staged proposal list supplies the count. Empty self-update interleaving remains covered by the sender-continuity tests.

Legacy local staged rows without validated observation provenance fail closed. A raw retained exchange cannot reconstruct whether an older peer vote followed complete MLS inspection. Upgrades cannot silently treat that missing provenance as an empty proposal list; the experiment does not provide automatic migration of those older separately stored voting states. Affected deployments require fresh authorized admission.

[`test_quorum_signed_exchange.py`](evidence/test_quorum_signed_exchange.py) exercises signed discovery through actual initial admission, durable exchange1 SMTP delivery, carrier2 installation, and established7 admission followed by protected application traffic. It checks wrong-purpose signatures, expiry, missing/reordered witness evidence, old-version rejection and immutable delivery holds after support renewal. The version0 test also carries a quorum view change over mail and accepts a delayed lower-view decision for the same candidate. These are local experiments, not independent implementation or public deployment results.


## Combined suite binding

The separately versioned [required conversation suite](suite-profile.md) defines its new assertion, context, invitation, ordering-wrapper and payload selections. It does not change any older version defined here. Its design is specified separately from implementation and acceptance evidence.
