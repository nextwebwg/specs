---
title: Mailbox associations
order: 9.5
blurb: exact addresses · first contact · continuity
sectionNav: true
---

# Mailbox associations

A client remembers which cryptographic identity it has associated with an email address. It keeps the evidence behind that decision and checks the identity's current authority before using it. A signed attachment can introduce a candidate; it cannot establish ownership of the address by itself.

> [!ex] A familiar address, a different identity
> Bob has already associated Alice's address with her identity. A new message from that address advertises another identity. Bob's client retains the new claim without replacing the existing association. If Alice has lost her keys—or the address now belongs to someone else—Bob can deliberately establish a new identity. That decision does not give the new identity access to the old conversation.

This chapter proposes the local association behavior. The unverified selection path has an offline reference implementation. The [human-comparison mechanism](#optional-human-comparison) separately confirms the exact mailbox-to-principal claim through an independently trusted conversation. It does not certify provider ownership or exclusive mailbox control. The retained baseline does not select an automated provider-ownership attestation mechanism. The separately proposed [independent mailbox registration](mailbox-registration.md) supplies a narrower mailbox-delivery check through an admitted registrar; it does not establish provider-domain authority or independently verify a person, and its incomplete prerequisites do not become baseline support. A [selected-association sender experiment](evidence/README.md#selected-mailbox-evidence-at-release) integrates the local selection with preparation and loopback release; broader deployment and restore coordination remain incomplete. The storage examples below are reference implementation choices, not an interoperable wire format or a requirement to use SQLite.

## The two decisions

Accepting a self-consistent [identity genesis](identity-state.md#genesis-and-first-contact) establishes a local continuity anchor for a principal. Associating a mailbox with that principal is a second decision. Each has its own evidence and policy; neither is implied by the other.

The association policy is explicitly `allow-unverified` or `require-verification`, supplied from current local configuration. Under the first policy, a sole eligible first-contact candidate may become an unverified association. Under the second, it remains a candidate until an independently accepted verification result exists. Changing policy does not delete evidence or silently promote an ambiguous candidate. A stricter policy holds new operations even if an association was usable earlier.

An unverified association and its authorized identity successors remain unverified. A cryptographic device proof, a matching From address, mailbox login, or successful delivery is not independent verification of the mailbox-to-principal binding. The UI may say “Encrypted to the identity first seen for this address; ownership not independently verified.” It must not summarize that state as verified correspondent identity.

## Select from the evidence currently available

Before making a first-contact decision, evaluate all retained eligible candidates for the exact mailbox under the same current identity, time and policy snapshot. Two eligible principals mean an ambiguous first contact, whichever observation was stored first. Do not process a known batch by pinning its first entry and treating the remaining entries as claims against that new pin. Explicitly resolving the ambiguity selects a principal; it does not independently verify that person's ownership of the address.

There is no way to wait for every claim that might arrive in the future. If a sole eligible candidate is selected under the permitted unverified policy and another unrelated claim arrives later, preserve the established association and retain the new claim separately. This is the stated first-contact substitution risk, not proof that the earlier candidate was genuine. Recheck the actual observation set and association generation at the serialized selection boundary; new evidence arriving before that decision cannot be hidden behind a cached single-candidate result. A received claim cannot supply the local user's ambiguity-resolution or replacement authorization.

## A different claim is not necessarily a different owner

| What changed? | What the client does |
| --- | --- |
| An unrelated identity claims an already associated address | Retain the claim separately. Keep the existing association and its verification status; the claim alone cannot suspend it or become a device of that identity. |
| Two conflicting changes are genuinely authorized by the accepted identity | Hold operations that depend on that identity. Preserve both branches and use the identity lifecycle's actual repair rules; neither arrival order nor a newer date chooses a winner. |
| The person deliberately accepts a new identity for the address | Record a continuity break, even if this is the same person recovering from total key loss. New setup is required; old messages, keys and verification do not transfer. |

A changed name, provider response, protocol version or repeated claim cannot establish which of these happened. An authorized identity conflict is evidence from the existing authority chain; an outsider cannot create one merely by copying public identifiers. Suspected address reassignment remains a candidate until the separately authorized association decision succeeds.

Keep earlier correspondence attributed to its original identity and evidence. A contact name or address reused by a new controller cannot merge the two authors, carry forward a verification badge or quietly reopen the earlier protected conversation. Where the earlier correspondent was unverified, describe an earlier identity rather than asserting a verified person. New writing to the replacement uses its own currently selected identity and admission. Existing drafts retain their former target until deliberately revised; they cannot inherit the replacement through a contact-list refresh.

## Address and observation inputs

For the current agreement, the association key uses the [canonical mailbox-address contract](mailbox-addresses.md): exact preserved local Unicode/case with minimal SMTP quoting and a validated lowercase A-label domain. Header syntax is parsed separately. Equivalent quoted forms enter the same key; visually similar, normalization-different or case-different local parts do not. Earlier ordinary-mail experiments retain their ASCII-only parser and do not implement the full current address/association path.

For an ordinary-mail observation, a trusted mailbox parser, not a received string comparison alone, supplies the outer From result. Exactly one mailbox must be present. Construct the parsed mailbox under the canonical address rules, including equivalent SMTP quoting and domain conversion, then compare it to the already canonical signed assertion mailbox. Never normalize the local Unicode sequence or case. Preserve original header bytes and the parser/profile version as evidence. Reply-To, Sender, Return-Path, a forwarded From, SMTP forwarding information, plus-tag equivalence and local-part case folding cannot substitute for this check.

An ordinary-mail observation is eligible for first-contact selection only after:

1. Carrier and strict assertion parsing succeed under the passive-discovery profile.
2. The assertion's fixed-purpose signature verifies using the named binding key.
3. The locally accepted identity resolves to the assertion principal. Validate the original asserted state/binding and the device's current `receive` authority under the selected assertion's continuity rule below; the original anchor and current accepted head are distinct inputs.
4. The complete current time interval lies inside assertion and binding validity, with the selected freshness policy satisfied.
5. The parsed sole outer From matches the claimed mailbox as specified above.

A `provider-bootstrap` observation instead follows the [automatic setup contract](bootstrap.md): validate the selected target-domain delegation, exact admitted request and source authority, original authorized response/publication, requested mailbox correspondence and the exact assertion evidence selected below. Apply steps2–4 above with that exact assertion and its current identity authority. There is no ordinary-mail carrier or outer From to match. Retain the original descriptors, exchange/source/result bytes, assertion and trusted transport observations as a distinct provenance type; never manufacture header-parser evidence. This path uses the same ambiguity, policy, continuity and atomic selection/release rules and does not imply independent mailbox verification. The existing ordinary-mail reference store does not yet implement this separate observation type.

A `mailbox-setup` observation follows the [ordinary-mail setup contract](mailbox-setup.md#encrypt-the-response-then-establish-the-conversation): validate the exact retained attempt, sealed response and original assertion for the selected agreement, then apply steps2–5 above to the response’s actual outer From and asserted target mailbox. Keep request/capsule/response provenance separately; do not pretend that a machine response was a human-authored passive message. Setup and domain authentication do not confer independent mailbox verification. The ordinary reference store does not yet implement this provenance type.

### First contact through an encrypted invitation

Alice can find Bob’s published setup and send an encrypted invitation before Bob has received any earlier mail from her. Bob’s client can validate the identity evidence inside that invitation under his existing first-contact policy. It does not need to invent an earlier ordinary message or require Alice to be a known contact first.

::: {.details summary="Candidate evidence, local selection and atomic admission"}

The [sealed-control frame](suite-profile.md#confidential-setup-and-control) already carries the original sender identity bundle inside its authenticated encryption. After authenticating the complete AEAD tag under the exact locally retained recipient key, an implementation MAY use that bundle as candidate history to resolve the original control signature and binding. This is not an accepted identity or mailbox association. Validate candidate genesis/history under the configured first-contact policy, preserving existing anchors, conflicts, disabled associations and restore holds. A bundle cannot appoint its own trust policy or replace a retained pin.

An encrypted initial-invitation observation MUST retain distinct provenance: original ciphertext, authenticated original control intent/signature/identity, original initial-admission body and creator assertion, exact own account/key selection and the owning receipt/staging evidence. Validate the selected carrier and original assertion under their own complete formats, current device roles, mailbox namespace, credible time and freshness rules. The creator assertion’s mailbox and actor MUST match the locally selected sender mailbox, sealed sender and actual initial creator. Neither an outer From nor a relay address supplies or overrides that association. An HPKE tag, a signature alone or a caller-supplied principal is insufficient.

Local incoming-invitation policy MUST independently authorize the exact account, creator, context and complete actual cohort before admission. A validated candidate may supply the facts to inspect; received bytes cannot supply that local authorization. A client may apply an already enabled local policy automatically, without another user prompt. Its staged inspection/selection mechanism MUST preserve the original operation and evidence across restart; it cannot manufacture a prior association, choose a new invitation or repeat a consumed native operation to finish the same decision.

Before adopting a first-contact association, evaluate all retained eligible candidates for that exact mailbox under the same current identity, policy, time and association-generation snapshot. A sole eligible candidate under `allow-unverified` may be selected as unverified; `require-verification` still requires its independent verification result. This decision MUST NOT bypass the complete original control, initial-admission, selected-cohort, native-package, recipient custody or final current-authority checks. Provisional history used during validation MUST NOT become an accepted pin or association merely because signature resolution succeeded.

Staging or a valid sender signature alone does not make this provenance eligible. Validate the complete owning invitation, including its actual native Welcome, before counting it as an eligible encrypted-invitation candidate; a proven-invalid Welcome cannot create ambiguity through this source. Missing dependencies remain pending rather than becoming a positive candidate or proof of incompatibility. Preflight validation may prepare an unpublished native successor, but MUST NOT install it, consume the live receiving package or publish membership. It cannot replace the final serialized selection and admission checks. This rule does not add native consumption to the eligibility requirements of other independently valid observation types.

The existing authenticated assertion-record collision and historical-conflict rules MUST cover this provenance and other observation types in both directions. Separate source tables cannot hide unequal authenticated records; expiry cannot erase a retained valid conflict or turn its historical proof into current authority. Invalid variants cannot enter that index merely because they were staged.

Commit any new accepted identity/association only with successful owning admission and its exact retained control/native outcome, after the final checks. On refusal, uncertainty or conflict, preserve required input, negative facts and native-consumption outcomes under their owning rules without committing provisional positive adoption. A malformed invitation, conflicting control or failed final check cannot leave behind a new accepted correspondent association. Exact retries retain the original result and cannot renew a deadline. This path does not independently verify mailbox ownership or authorize replies, broader membership or another device.

:::

### Bind observations to the selected agreement

Association history belongs to the exact mailbox and principal, not to a protocol version. Upgrading support does not create a fresh first-contact opportunity, clear an accepted conflict or reset the association generation, verification scope, disabled state or authenticated record-collision index.

| Independently selected agreement | Required current assertion | Setup provenance |
| --- | --- | --- |
| `mail-conversation-v2` | Original signed assertion10 | Mailbox setup2, bootstrap descriptor2/records2, or independently validated ordinary passive mail under its owning carrier |
| `email2-conversation-v0` | Original signed assertion8 | Mailbox setup0, bootstrap descriptor0/records0, or independently validated ordinary passive mail under its owning carrier |
| `mail-conversation-v1` | Original signed assertion9 | Mailbox setup1, bootstrap descriptor1/records1, or independently validated ordinary passive mail under its owning carrier |

For each row, apply the complete selected acquisition contract before proposing an association observation. Retain its exact agreement, original signed bytes, identity and mailbox evidence, and request/response/descriptor commitments where applicable. The [reply-aware binding](reply-intent.md#reply-aware-protected-agreement) selects assertion9's distinct signature domain and complete tuples; an assertion8 observation cannot be relabeled as that support. The current [asynchronous agreement](suite-profile.md#asynchronous-protected-agreement) requires original assertion10 with its fixed readable application and independent per-device interactions; neither assertion8 nor assertion9 can be relabeled as current support. Unsupported or mixed provenance stays unavailable, without retrying an older parser or manufacturing an outer From.

Known-pair [provider exchanges](provider-control.md) resolve a preexisting association to the independently selected peer and its exact fresh advertisement. Their response cannot replace that principal or initiate a new first-contact association. A new identity still needs its separate continuity-break decision and fresh authority. Earlier passive observation formats retain their historical validation rules; a record that is useful for history cannot silently satisfy a newly selected agreement.

::: {.details summary="Shared continuity and evidence checks across agreements"}

Key authenticated discovery-record reuse by the same `(principal, device, record)` across these versions and provenance types. Different authenticated signed payloads under that identity remain a record collision; the version or acquisition channel does not create a new namespace. A collision makes that record unavailable for operational selection. Preserve the existing association and unrelated independently valid evidence; do not fabricate an identity-state fork or permit unauthenticated variants to poison it. Publication code must use fresh record identities for different signed assertions. Package-reference allocation/consumption is independently governed by its own shared realm; a fresh record cannot make a consumed package reusable.

For current assertion10 and retained assertion9/assertion8, apply the [purpose-specific cached-discovery rule](provider-grants.md#continuity-and-freshness-have-different-scopes): an original accepted ancestor is permitted only while the exact asserted device/binding/key and receive role survive every accepted step through the current head. Preserve the original signed bytes and return/check the current head separately. A binding replacement, even with the same signing key, needs fresh setup evidence. Missing ancestry, an accepted fork, retirement or a repair boundary cannot be skipped. Earlier encodings keep their documented exact-head rule. This exception does not turn cached publication into a fresh challenge response or extend any assertion, package, control-key or account deadline.

Every use still resolves the accepted current identity and required roles, exact selected application, advertisement validity/freshness, mailbox generation and verification policy. A newer assertion can supply current support only after its own checks; it cannot expand a previous verification's mailbox/identity/continuity scope. Configuration import and backup restore do not overwrite a newer local association or reenable a disabled one merely by presenting supported advertisement bytes.

:::

An admission package is not required to record an association. Validating or consuming one is a later dependency of an invitation, not evidence of mailbox ownership. Invalid signatures and malformed carriers do not become association candidates. Missing identity dependencies, unsupported IDNA validation or uncertain time remain pending diagnostics, without automatic network activity.

A replay cannot refresh an observation's signed validity. Message receipt time and Date are provenance only. Old evidence may remain available for history after losing operational eligibility.

::: {.details summary="Reference storage records and atomic decisions"}

### Implemented local selection store

The [Python reference store](evidence/mailbox_association_store.py) shares the existing `IdentityStore` connection and database. Its 15 [focused tests](evidence/test_mailbox_association_store.py) exercise durable selection, restart, concurrent connections, exact retries, atomic rollback, replacement, disable/enable, and advertisement collisions. These are local storage tests; they do not demonstrate safe network release or mailbox ownership.

The store exposes three operations:

| Operation | Implemented boundary |
| --- | --- |
| `observe_validated_batch()` | Retain exact assertion bytes, proof/key variants and source provenance. The caller must already have verified each exact signature and supplied a trusted sole-From parse. This is a local API, not an incoming-mail validation endpoint. |
| `snapshot()` | Read the current association and retained observation references in one transaction. The result is inspection data, not authorization to send. |
| `decide()` | Compare the expected generation, recheck eligible evidence against accepted identity state, and atomically retain the decision and any association change. Exact request retries return their original result. |

The ordinary ingestion path starts with the successful cryptographic verifier for its exact selected assertion profile, including the separate suite8 or suite9 verifiers for their retained assertions. That reference-store ingestion path does not implement current assertion10 merely because the association policy is shared. Older passive formats use their owning verifier; no generic successful-parser flag supplies that result. The store does not perform that signature verification itself. It independently checks identity authority, key, asserted head/binding and validity before admitting a record to its authenticated-record index. `observedAt` is local provenance and a point-time check; callers must already have validated the credible time interval and must not narrow uncertain time to make an assertion pass. Original headers and message retention remain the caller's responsibility; the store retains the source identifier, parsed mailbox and parser revision.

The collision index spans mailboxes and uses authenticated `(principal, device, record)` identities. Different authenticated assertion bytes under one identity prevent selection from that record, even after one assertion expires. Independent records remain eligible. A collision does not delete an established association or suspend its principal. Proof/key variants remain retained: an unauthorized variant cannot block later admission of an authorized proof over the same assertion bytes or overwrite already authenticated evidence. This protection depends on the stated signature-validation boundary; the store is not a substitute for cryptographic verification of network input.

Selection evaluates current identity authority and the full supplied time interval within the same SQLite transaction as the association decision. Multiple eligible initial principals return `ambiguous` under either policy. No eligible candidate returns `pending`; a sole eligible candidate under strict policy returns `verification-required`. Explicit user resolution, replacement and disable/enable are implemented; enabling checks the same principal again and advances the generation. No result grants send authorization. A queued operation must still pass the serialized release checks below; selection alone is insufficient.

Schema initialization refuses an already active caller transaction. The tables are local implementation details: the conceptual records below describe the broader design, including verification evidence and provenance that this bounded store does not implement in full. Existing experimental databases need explicit schema/version migration planning before deployment.

### Reference storage records

The proposed complete design can place these records in the same transactional database as accepted identity heads. Other storage designs can provide the same atomicity and evidence-preservation behavior. These are local records, not received JSON objects or newly registered wire formats. All fields below are required unless expressly optional. Null is not used; an absent optional field is omitted. Timestamps and counters exposed through a JSON diagnostic interface use canonical unsigned-64 decimal strings. Exact payloads remain byte strings in storage.

| Record | Required fields | Meaning and constraints |
| --- | --- | --- |
| Observation | `observationId`, `mailbox`, `principal`, `device`, `stateDigest`, `bindingDigest`, `assertionBytes`, `assertionDigest`, `signature`, `messageSourceId`, `outerFromEvidence`, `parserRevision`, `observedAt` | Local nonzero ObjectId; profile identifiers/digests/proof encodings; retain exact signed bytes and source-message reference. `outerFromEvidence` is local parser output plus a reference to original header bytes, not a sender-supplied trust result. |
| Association decision | `decisionId`, `mailbox`, `generation`, `kind`, `principal`, `identityAnchor`, `observationIds`, `actor`, `policyRevision`, `decidedAt` | Immutable local record. `kind` is `first-contact`, `resolve-first-contact`, `replace-with-continuity-break`, `disable`, or `enable`. Actor is explicit configured policy or a local user action; received mail cannot supply it. `identityAnchor` is the accepted head at decision time, retained as history rather than a future-use head. `observationIds` is a nonempty distinct array for decisions selecting a principal, empty for disable. |
| Current association | `mailbox`, `generation`, `decisionId`, `principal`, `enabled` | Exactly one current row per mailbox; `enabled` is Boolean. Positive generation increases by one per local decision without overflow. Disabled rows retain the previous principal and decision history. No deletion/recreation shortcut resets continuity. Enabling requires a disabled row; disabling requires an enabled row. An exact decision retry returns its original result, while a new request for a transition already satisfied makes no state change. |
| Verification evidence | `evidenceId`, `mailbox`, `principal`, `anchorDigest`, `mechanism`, `mechanismRevision`, `evidenceRef`, `scope`, `continuityScope`, `notBefore`, `notAfter`, `status` | Local verifier result, never accepted directly from a discovery wrapper. `scope` must include `mailbox-principal`; other scopes alone are insufficient. `continuityScope` states whether accepted ordinary descendants of the anchor are covered. `status` is `accepted`, `withdrawn`, or `conflicted`, with immutable evidence plus retained status changes. The optional human-comparison experiment below implements one local mechanism; other mechanisms remain unspecified. |

`messageSourceId` and `evidenceRef` identify retained local evidence; they are not URLs to fetch. Observation storage must not duplicate private message bodies merely to retain a public assertion. A retention implementation must keep enough original bytes and provenance to explain its decisions, and state when a source message is unavailable.

Exact observation retransmissions are idempotent by mailbox, principal and assertion bytes/digest; additional source-message references may be attached as provenance. Distinct exact assertions sharing a remote record identifier remain separately retained. The identity of an observation does not depend on a parsed/re-serialized assertion. A discovered record collision must not overwrite either assertion or acquire the power to suspend an established mailbox association by copying a public identifier.

The local decision ID is an idempotency key for an exact decision request. A retry returns the stored result; reuse with different request content is rejected. Every decision uses compare-and-swap against the expected association generation, including explicit “no row” for first contact. Record the decision and update the current row in one transaction before reporting success.

:::

## State and transition behavior

Do not store a single trusted/untrusted flag. The current row stores the selected principal; derived use-time outcomes combine that row with observations, identity authority, policy and optional verification evidence.

| Situation | Outcome |
| --- | --- |
| No association and no eligible candidate | `pending`, reason `no-eligible-candidate`. |
| No association; eligible observations all name one principal | Under `allow-unverified`, a deliberate first-contact selection transaction may record `associated-unverified`. Under `require-verification`, return `verification-required`. |
| No association; eligible observations name multiple principals | `ambiguous`. No arrival-order, timestamp or provider ranking selects a principal. A later permissive policy does not resolve it. |
| Existing enabled association; new assertion names its principal | Retain the observation. It cannot rewrite the initial evidence, upgrade assurance or bypass current head/validity checks. |
| Existing association; another principal claims the mailbox | Retain as `unlinked-claim`. Do not replace or suspend the established association merely because of this unsolicited claim. Show it on identity inspection without an attacker-triggered modal warning for every message. |
| Existing association; its accepted identity has an authorized branch conflict | Hold operations requiring that identity with `identity-conflicted`. This is distinct from an unrelated self-signed claim. |
| User explicitly selects among ambiguous initial principals | Record `resolve-first-contact`, identifying reviewed candidates and the chosen principal. This remains unverified unless separate accepted evidence supports it. |
| User explicitly replaces the principal | Record `replace-with-continuity-break`; increment generation, preserve the prior principal/history, invalidate queued decisions and require new conversation/admission authorization. No history transfer follows. |
| User disables this association | Record `disable`, preserve history and hold automatic use. Disabling is not key revocation or deletion of decryption history. |
| User enables a disabled association | Record `enable` for the same principal only, after current identity, advertisement and policy checks. Increment generation; earlier queued authorizations do not revive. Another principal requires an explicit continuity break. |
| Current policy becomes stricter, evidence expires or becomes unavailable | Hold the affected use without deleting the association or selecting plaintext fallback. |

Initial selection evaluates all eligible observations already retained in one transaction snapshot, not merely the incoming message. Where a single receive/import operation contains several candidates, store and classify the whole bounded batch before attempting selection. If candidates were committed before first selection, their ambiguity cannot be hidden by choosing one.

A claim arriving after a completed first-contact decision is an unlinked claim, even if delivered concurrently on another connection. This is the existing first-contact limitation: local atomicity prevents inconsistent decisions but cannot reveal an unseen competing claim or resist substitution before the initial pin. An implementation must not claim global first-contact consensus.

Ordinary identity transitions keep the same principal and do not constitute mailbox reassignment. A newly issued advertisement names its accepted identity anchor under its owning contract. Retained assertion10/9/8 evidence may keep its original anchor only while the exact binding survives every accepted step under the continuity rule above; use still resolves the current head independently. No proof format in the current profile authorizes cross-principal succession. Until one is specified, choosing another principal is a recorded continuity break, even when the user believes it is the same person.

## Aliases and reassignment

Each exact mailbox has a separate association row. A principal advertising a new mailbox creates a candidate for that new address; it does not inherit another address's association or verification. The same principal may legitimately be associated with several addresses after their separate decisions. An alias suggestion, forwarding reply or provider-specific delivery equivalence is only routing evidence.

When an address is reassigned, an independently verified new controller still does not acquire the prior endpoint identity or history. Replacing the association requires the explicit continuity-break decision above. Pending messages retain the mailbox, principal and association generation they targeted; they cannot be silently retargeted to the new principal. Historical message attribution continues to refer to the original identity and evidence.

::: {.details summary="Coordinating association, identity and operation release"}

### Atomic use-time authorization

This coordinator remains a proposed integration contract. Expose a coordinator operation rather than allowing callers to combine `lookup_mailbox()` with the current snapshot-only `check_device()` and then send later. The reference design can use a single SQLite transaction for mailbox association, identity checks and the local operation commitment; another implementation may use an equivalent serialization boundary. The coordinator needs transaction-aware identity checks; the existing `check_device()` opens its own transaction and returns a snapshot, not a durable permission.

The coordinator receives the exact destination mailbox, expected association generation, authenticated target device/key, current policy revision, time interval, freshness mode, selected advertisement reference and a caller operation ID with exact operation-input digest. It performs the following in one serialization boundary:

1. Read the enabled association and compare its generation and principal with the queued operation's intended target.
2. Resolve the locally accepted identity head; reject a missing identity or hold an accepted conflict. Verify current `receive` authority, key, binding and validity using retained identity evidence.
3. Recheck the assertion signature against its exact retained bytes and original asserted binding. For current assertion10 and retained assertion9/assertion8, resolve the accepted path from its original anchor to the current head and apply the unchanged-binding rule below; earlier encodings retain their exact-head checks. Recheck the original signed interval and current device authority. The association's historical decision anchor cannot substitute for either the assertion anchor or the current head.
4. Apply current first-contact/verification and freshness policies. If independent verification is required, resolve accepted evidence through the interface below. No input flag supplied by a message can satisfy it.
5. Recheck package, group membership, audience and pending operation dependencies appropriate to this operation. Mailbox association alone cannot add a device or disclose history.
6. Commit a durable local operation intent with mailbox generation, principal, head, binding, policy revision, evidence references and exact intended bytes/digest. An exact operation retry returns the same committed result. Any changed dependency before commitment yields `stale` and requires recomputation; do not overwrite an earlier committed operation.

The commitment is a local authorization point, not proof of SMTP delivery or an indefinitely valid send ticket. A worker performing a later release must re-enter the serialized release protocol and recheck these dependencies immediately before crossing its local release point, as required by the transport contract. Revocation and replacement updates must participate in the same coordinator. A database commit followed by an unrelated socket write is not sufficient to claim that races are solved.

No transaction can recall bytes already released or make an unseen remote revocation locally known. Remote freshness and distributed delivery remain separate. Test and label the exact local release point; the local sender experiment supplies bounded retry/outbox coordination, while deployed transport and restored-state handling remain unvalidated.

:::

## Independent verification remains separate

A local verifier accepts evidence through a selected, versioned mechanism and returns the verification-evidence record only after that mechanism establishes the exact mailbox-to-principal claim. The mechanism must define its authority, authenticated inputs, intended audience/purpose, expiry and revocation, replay handling, privacy cost, identity anchor and applicability to authorized successor states. The caller cannot replace that work with `verified: true`.

An operation requiring verification receives one of `verified-for-use`, `verification-required`, `verification-expired`, `verification-conflicted`, or `unsupported-verification-mechanism`, together with evidence IDs and the exact checked identity head. The result is transaction-scoped. Unsupported evidence is retained as an observation if useful, never interpreted as successful verification. A stricter policy names the mechanisms/assurance scopes it accepts; all successful verifiers are not interchangeable.

Without a selected verifier, an otherwise eligible sole candidate under strict policy returns `verification-required` and verified use remains unavailable. Missing candidates remain pending and competing initial principals remain ambiguous. Verifier integration must explicitly compose identity continuity and mailbox evidence; calling identity checks with `allow-unverified` and relabeling the result is not an implementation of verification. A legitimate composition may reuse the same cryptographic checks, but needs a separate reviewed evidence decision and distinct result provenance.

### Optional human comparison

Normal email and automatic unverified continuity do not require a manual comparison. A user who wants stronger assurance can compare the exact address, principal and identity-state digest with the intended person in person, or through a separate conversation they already trust. The local client records this as **human-confirmed correspondent identity**. It does not certify provider ownership or exclusive control of that mailbox.

The [local comparison experiment](evidence/human_verification.py) requires complete matching data and an explicit independent-channel confirmation. A code supplied by the email being checked, a QR scan alone, a display name or a provider login cannot satisfy it. The [confirmation screen](evidence/human-verification.html) explains this distinction; it receives no sender HTML or script.

Validity and continuity are adjustable client policies. The client can require a fresh comparison for every identity-head change, or allow ordinary account-authorized successors of the compared state. The latter trusts the account's existing device-enrollment authority; it does not grant historical conversation access to a new device. Forks, recovery/reset formats and continuity-break replacement do not inherit the comparison. Expiry or withdrawal holds strict use without deleting accepted history or selecting plaintext fallback.

::: {.details summary="Comparison records and use-time checks"}

### Exact comparison and trusted input

The local comparison object has exactly `version: "0"`, `purpose: "manual-correspondent-comparison"`, `mailbox`, `principal`, `stateDigest` and `stateRevision`. It uses the existing full state digest and identity encodings; it is not a new signature, shortened safety-number algorithm or email wire version. The address preserves its local-part spelling. The peer must confirm that address as well as the identity.

A client-owned session binds the original retained mail, candidate bundle, expected identity head, association generation and session expiry to one local account/profile. A separate trusted user gesture confirms independently obtained matching data. The local transaction rechecks the original cryptographic evidence, installs any first-contact pin, records the comparison and selects the association together. A changed snapshot or failed comparison leaves no partial verification. Exact retries cannot replace the comparison or extend its validity.

### Reuse only within the recorded verification scope

The comparison confirms the exact mailbox/principal claim in its original local account/profile. It is not a transferable login token, enrollment approval, route permission or history-disclosure grant. Changing the comparison's purpose, principal, mailbox, state or version fails the original session match. A received copy, another account's session identifier or a sender-supplied confirmation flag cannot recreate the trusted independent-channel gesture. No wire message carries that local authority.

At use time, resolve the accepted current principal state and the comparison's original anchor separately. With `anchor-only`, require that exact accepted head. With `ordinary-authorized-descendants`, follow the complete independently accepted one-parent chain back to the compared anchor: state0 ordinary successors and state1 `update`/`prune` successors are eligible; missing links, cycles, unsupported transitions, conflicts, `repair` or `retire` do not inherit this mechanism's verification. Do not pick one parent of a repair. The principal and exact mailbox stay fixed; association replacement/disable, evidence withdrawal, expiry and stricter current policy still hold use. A compatible ordinary device addition need not repeat the human comparison. This principal-level assurance does not itself require every old device binding to survive, unlike an advertisement's device-specific unchanged-binding test; every device used for delivery must independently have current authority.

An exact confirmation retry can return its original committed decision after expiry or withdrawal. That result is historical evidence of the completed comparison, not a fresh `verified-for-use` authorization. Recompute current verification in the same serialized authorization boundary as the intended operation. Retrying cannot renew the session, evidence interval or association generation, nor activate a previously held send. Evidence import through an authorized own-device configuration transfer preserves the original scope and dates under that transfer's rules; copying a comparison object alone is not such a transfer.

### Separate assurance and delivery authority

The composed authority adapter preserves the cryptographic device result and adds independent verification provenance. The cryptographic status alone is not evidence that comparison succeeded. Exact routed addresses still require their own verification; evidence for one alias cannot authorize another. The local user's own principal has a distinct client-setup source, and only explicitly configured own addresses can use that source for routing.

The strict initial-roster and ordinary-message adapters bind verification evidence and status revision alongside the existing identity and association dependencies. Preparation, release and the check before SMTP DATA re-evaluate them. Withdrawal, expiry or changed evidence holds the prepared bytes rather than silently selecting replacement verification. The receiver separately checks current effect authority; accepted historical messages do not lose their original attribution when a comparison expires.

The [focused checks](evidence/test_verified_delivery.py) connect signed initial-roster creation, loopback SMTP admission and protected replies through this explicit strict mode. The ordinary unverified path remains separate. Other invitation/control adapters, provider ownership attestations, authenticated introductions, transparency witnesses and independent deployments require their own integration; this mechanism does not make them available automatically.

:::


::: {.details summary="Acceptance scenarios"}

### Acceptance cases

This table covers the full proposed behavior. The local store tests cover selection and persistence; selected-association release races have separate sender tests. The optional human-comparison adapter has local strict-delivery checks. Complete original-header retention, backup reconciliation and independent interoperability remain unvalidated.

| Case | Required observable result |
| --- | --- |
| Sole valid candidate, permissive policy | Genesis acceptance and mailbox decision remain separate; association is durable and visibly unverified after reopen. |
| Sole candidate, strict policy | No usable association authorization; no outgoing mail or weaker fallback merely because verification is absent. |
| Exact replay with another MIME folding/source message | Same signed assertion evidence and same decision; new receipt time does not extend validity. |
| Copied assertion with different From, multiple From values, Reply-To substitution | No automatic association candidate; readable message remains available. |
| Local-part case, plus suffix, dot variation, alias and domain case | Only allowed domain normalization matches; distinct local spellings retain distinct associations. Invalid A-label validation remains pending/unsupported, not accepted by LDH shape alone. |
| Two retained principals before first selection | Ambiguous under both policies; an explicit user resolution records the selected evidence and remains unverified. |
| Concurrent selection on separate connections | Generation comparison permits one local decision; the loser re-evaluates the complete committed state. No last-writer-wins replacement. |
| Unlinked claim after pin | Original association stays usable under its existing policy; claimant cannot force an identity conflict by copying identifiers. |
| Authorized identity fork, device revocation, changed binding or stale advertisement | Use holds or rejects for the specific reason; historical association and source evidence remain intact. |
| Replacement/address reassignment | Explicit continuity break; old queued operations fail their generation check; old history is neither quoted nor re-encrypted automatically. |
| Identity transition between check and operation commitment | Atomic recheck observes the new head or prevents interleaving; no commitment based on stale authority. |
| Transition after intent commit but before transport release | Release coordinator revalidates; intent alone is insufficient permission. |
| Crash before/after decision commit | Before commit leaves no partial mapping; after commit an exact retry returns the same decision. No duplicated operation commitment. |
| Fake, expired, withdrawn or unsupported verification evidence | Cannot satisfy strict policy; no UI claim of verified ownership or continuity. |
| Enable after disable | Require the same principal, fresh eligible evidence and current policy; retain history and advance generation. Revoked, expired or conflicted identity evidence cannot restore use. |
| Disable and restore old backup | Disabling retains history; restored associations cannot overwrite newer generations/revocations without reconciliation. |


:::
