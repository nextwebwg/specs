---
title: Identity-state records
order: 9
blurb: device roster · authority · continuity
sectionNav: true
---

# Identity-state records

An identity state names the device bindings an account currently authorizes. A directory distributes these records; it does not acquire permission to change them. This chapter selects the experimental record format and ordinary transition rules. The [device lifecycle](identity-lifecycle.md) defines their user-visible meaning, and the [security profile](security-profile.md#device-binding-record-schema) owns the referenced binding and proof formats.

> [!warn] Experimental protocol boundary
> This is a proposed application protocol, not an implemented authentication service. State signatures are exercised independently; persistent transition validation, freshness exchange and recovery must be integrated and tested before these records authorize interoperable MLS enrollment.

## Identity proof bundle

The version-0 exchange object is strict UTF-8 JSON under the event encoding rules, with exactly five members: version (`0`), purpose (`identity-bundle`), principal (an enp0 account identifier), states (an array) and bindings (an array). At least one array is nonempty. Every enclosed record must name that principal. Array order has no authority or processing-order meaning.

Each states entry has exactly payload and signature. Each bindings entry has exactly payload, authorization and possession. Payload is the original record bytes encoded with the standard base64 alphabet, required padding and zero unused pad bits, without whitespace. Re-encoding decoded bytes must reproduce that string exactly. Proofs are 128 lowercase hexadecimal characters representing the Ed25519 signatures defined by their respective purpose. A state's payload must identify version0 and purpose identity-state; a binding's must identify version0 and purpose device-binding. Full record-schema validation remains mandatory after strict decoding.

The complete decoded bundle is limited to1048576 octets and the event encoding's nesting bound. This includes the base64 strings and proof overhead; it is not a separate allowance for every entry. Local allocation limits may cause incomplete processing under the existing resource-limit rules. Each embedded payload is also independently subject to strict UTF-8, duplicate-name, scalar-value and nesting checks. Duplicate exact payload digests within either collection make that bundle invalid. No partial effects are permitted on malformed bundles.

The wrapper is not signed as a unit. Signatures and references cover the enclosed original record bytes, so whitespace or member-order changes in the wrapper preserve those proofs. The principal field is an indexing hint checked against every payload, never standalone authority. Removing a record can make validation pending; it cannot make a required proof optional. Adding a record cannot grant a role without its complete chain and applicable policy. Unknown members are rejected rather than treated as unsigned extensions with hidden security meaning.

Bundles may contain a partial history or records in arbitrary dependency order. Receivers resolve references by exact payload digest across supplied and previously stored evidence. They must not infer that the bundle is a complete roster, the newest state or proof of absence of revocation. A first-contact genesis claim needs its state and binding, all three proofs, configured policy and applicable time checks. Neither an empty collection nor a missing predecessor requests deletion of stored state.

This selects the application carrier. MIME media-type registration, its ordinary-mail packaging and discovery-service request/response binding remain required integration work; the bundle's purpose string is not a registered content type or an instruction to hide mail in legacy clients. These records contain public keys and authorization evidence, never private keys or historical message secrets. They can still expose device relationships and must follow the discovery privacy policy.

## Exact state payload

A state payload is strict UTF-8 JSON under the [event encoding rules](event-encoding.md). It has exactly the following members. No member is optional, and null is not a value.

| Member | Type and constraint |
| --- | --- |
| version | String `0` |
| purpose | String `identity-state` |
| principal | Account identifier with the enp0 encoding |
| record | Nonzero ObjectId, stable for retries of these exact bytes |
| revision | Canonical unsigned-64 decimal string |
| previous | Empty array for genesis; otherwise an array containing exactly one lowercase SHA256 digest |
| issuedAt | Canonical unsigned-64 decimal string of UTC epoch seconds |
| bindings | Nonempty array of binding references as defined below |
| revoked | Array of distinct device identifiers, sorted by exact ASCII spelling |
| signer | Device identifier of the state authorizer |

A binding reference is exactly an object with device and digest members. Device uses the end0 encoding; digest is the lowercase hexadecimal SHA256 of the exact referenced binding payload bytes. Bindings are sorted by device identifier and contain no repeated device. A device cannot occur in both bindings and revoked. Sorted arrays make equivalent rosters easy to compare; they do not canonicalize the payload or change the exact-byte signature rule.

The state digest is SHA256 over the original payload bytes, excluding its detached proof. References and signatures MUST NOT be computed from a reconstructed JSON object. A proof wrapper must retain the exact payload. Unknown versions, members and enum values cannot be silently ignored.

Revision zero is genesis and requires an empty previous array and an empty revoked array. Every other revision requires one previous digest. Revision is a chain counter, not a timestamp, voting weight or preference among competing branches. A successor's revision MUST equal its predecessor's revision plus one, without unsigned overflow. issuedAt MUST NOT precede its predecessor's issuedAt; a later timestamp never resolves a fork or supplies a trusted clock.

## State proof

The detached state signature uses Ed25519 and the ASCII domain `email-next/identity-state/v0` followed by one zero octet, the four-octet unsigned big-endian payload length and the original payload bytes. The experimental payload bound is 1048576 octets. Keys and signatures have the lowercase hexadecimal encodings selected for device-binding proofs. This signature domain is distinct from binding authorization, device possession and MLS signatures.

For genesis, verify the proof under its sole binding's signing key after validating that binding's self-binding and possession proofs. For a successor, resolve signer exclusively in the predecessor's accepted bindings, then verify under that binding's key and authority. A newly proposed key MUST NOT authorize its own insertion by appearing as signer in the successor. If a key changes during a transition, the state proof still uses the predecessor's authorized key.

## Genesis and first contact

Genesis has exactly one binding reference, whose device equals signer. The referenced binding must name the same principal, carry first-contact authority and pass both proof checks. Its roles must include enroll and revoke so the identity can administer its initial roster. A client may offer recover authority separately; listing it must reflect the user's configured recovery arrangement rather than silently creating a provider recovery right.

For initial use, distinguish an interval wholly after binding expiry (`not-current`, expired), wholly before validity (`not-current`, not-yet-valid), and an uncertain interval crossing either boundary (pending). A proof can remain cryptographically valid in all three cases. None permits initial pinning or restores a revoked role. Re-observing expired material must not erase a previously recorded pin or historical evidence; using that pin for new operations still requires current validity and policy checks.

Acceptance of a genesis record follows first-contact policy and remains distinct from verified ownership of a mailbox. Genesis cannot replace an established principal or add a device to it. When no genesis has been accepted and multiple self-consistent claims are available, first contact is ambiguous: arrival order or a later issuedAt does not establish ownership. Once a genesis is pinned under the configured first-contact policy, another self-signed genesis is an unlinked claim. Preserve it as untrusted competing evidence, but do not replace or suspend the pin merely because the claim names the same public principal. Anyone can copy that identifier. This differs from two conflicting successors whose authorization both traces to the accepted identity. A permissive first-contact pin remains vulnerable to substitution before it is established; this rule does not upgrade it to verified identity.

## Ordinary transition

A receiver resolves and validates the predecessor before considering the proposed state. A missing predecessor leaves the transition pending. A rejected predecessor cannot authorize a successor. The predecessor must belong to the same principal and satisfy the revision relationship. Each referenced binding must resolve to a valid payload for the named device and principal; a digest match alone establishes none of its authorization.

Compare the proposed roster with the predecessor:

| Change | Required predecessor authority |
| --- | --- |
| Add a device binding | Signer has enroll |
| Replace a binding, including validity, key or role changes | Signer has enroll; an authorized device replacement follows lifecycle checks |
| Remove a device | Signer has revoke |
| Add or replace and remove in one transition | Signer has both enroll and revoke |
| Change administrative roles | Signer has enroll and every role being granted |

For this first configuration, a signer may grant only roles contained in its own predecessor binding. There is no implicit administrative superuser. All newly added or replaced bindings must name this exact predecessor digest as their state authority, carry a binding authorization proof made by this state signer, and carry the proposed device's possession proof. Unchanged references retain their original authorization evidence; they need not be reissued for each successor.

Revoked is cumulative. Every removed device must be added, previous entries must remain, and no entry may be deleted. A new revocation entry must identify a device removed from the predecessor roster; this configuration does not preemptively revoke unknown device identifiers. An identifier in this set cannot be re-enrolled; a returning device obtains a fresh device identifier and an authorized new binding. Revocation does not erase the retained binding or historical attribution. A key or role replacement for a still-present device does not by itself add its identifier to revoked; the old binding becomes superseded for future operations when the transition is accepted.

The proposed roster must retain at least one device with enroll and revoke roles in the same valid binding. This configuration does not define an account-retirement transition. A deliberate loss of all administration is not expressible as a misleading usable state; it requires a separately specified retirement or new-identity procedure. Administrative validity is checked at transition acceptance time, with uncertain time holding the operation. If time is represented as an uncertainty interval, the signer, each newly granted binding and at least one retained administrator must each be valid throughout that interval; different administrators valid only at opposite endpoints do not satisfy this requirement. These rules do not extend an expired binding.

A signed state with an unchanged roster and revoked set is allowed as a continuity checkpoint. It still requires an enroll-authorized signer, the exact predecessor, the next revision and ordinary proof validation. Such a checkpoint proves only that an authorized key signed that state. It does not prove that the receiver has learned every later transition.

## Persistence, replays and branches

Persist the accepted payload, its exact digest, binding evidence, proof and predecessor relationship before exposing newly granted authority. Installation must compare the predecessor against the durable current head atomically. If another successor won that comparison, retain the candidate for branch evaluation instead of applying it over the new head.

Exact-byte retries return the stored result. Different authorized payload bytes using the same record identifier are a conflict within that authority history. An unlinked self-signed claim does not acquire authority to create such a conflict by copying the identifier. A historical valid state can support historical verification but cannot roll back the accepted head, remove revocation evidence or reauthorize a superseded binding. Backup restoration follows the same rule.

Two independently valid successors of one predecessor constitute a branch conflict. Arrival order, revision, timestamp, provider ranking and number of relays MUST NOT select a winner. Hold new operations whose authority depends on the competing states and retain both paths. Already disclosed messages cannot be recalled; historical reading remains available.

This version does not encode a multi-parent merge or authorize automatic conflict recovery. A recovery extension must define a proof accepted by the relevant prior authority and how it handles revocation on competing branches before it can claim continuity. Until that extension is selected, deliberate creation and verification of a new identity is a continuity break, not a repaired chain. The client must not present this exceptional outcome as routine device enrollment.

## Freshness and recovery boundary

A state can be cryptographically valid and stale. The state format cannot prove absence of a later revocation, and issuedAt is not such proof. The [freshness contract](freshness.md) selects cached continuity for ordinary asynchronous use, defines explicit recent-checkpoint age of the current state's claimed issuance time, and binds live confirmation to the original authorized device challenge. Cached continuity has no independent proof of unseen remote changes; signed binding and capability validity still limit use. A recent declared issuance time is not trusted signing time or live presence, and fresh device evidence cannot override a known removal. The selected age, whole credible clock interval and held unavailable outcome apply at release. A cached state alone MUST NOT support an instantaneous-global-revocation claim. No plaintext fallback is implied by unresolved freshness.

The recover role records a separately granted capability; it does not grant an exception to ordinary transition rules in this configuration. The initial suite does not select an emergency override: after loss of every authorized device, it requires an explicit new identity. [Archive recovery](encrypted-archives.md) can restore historical reading without changing that identity outcome. A recovery construction needs its own authenticated operation, state-transfer channel, replay handling and history-access policy. Mailbox login, password reset, a directory response or possession of an old backup is insufficient. Existing authorized devices can perform ordinary enroll/revoke operations when their bindings permit them; that is different from using an emergency recovery authority.

## Current device authorization

A use-time authorization check resolves the device from the locally accepted head, not from an incoming binding or a caller-selected historical digest. The caller supplies the authenticated credential identity and signature key, the operation (`send` or `receive`), the current time uncertainty interval and the current trust policy. A receiver MUST hold a missing identity or unresolved accepted conflict. An unverified pin and its successors cannot satisfy a policy requiring independent verification.

The selected device must remain in the accepted roster and outside its cumulative revoked set. Its exact binding digest must resolve to retained accepted evidence. The authenticated leaf signing key must match that binding, the operation must be among its roles, and the binding must be valid throughout the time interval. A wholly expired or not-yet-valid interval is not current; a crossing or unavailable interval is pending. Successful checks return the accepted head and binding digests as dependencies of the decision.

This result is a snapshot, not a reusable delivery permission. The [transport release boundary](transport.md#local-authorization-and-release) must recheck and serialize those dependencies before release, together with the [group requirements](group-conversations.md#applying-account-changes-to-an-mls-group). A newer local head or conflict invalidates a prior decision; stronger remote-freshness policy remains separately applicable. Historical bindings remain evidence but cannot substitute for the current head.

## Conformance evidence

The [experiment reference](evidence/README.md) records executable checks for this chapter. The following layers compose into the local identity pipeline; passing one layer does not establish the prerequisites of another.

| Layer | Evidence | Limit |
| --- | --- | --- |
| Payload schema | Exact fields, counters, identifiers and roster structure | No proof or authority established by syntax |
| Detached proofs | Actual Ed25519 signatures and separation of binding, possession and state purposes | No mailbox ownership or freshness established |
| Identity bundle | Strict decoding, exact payload references, partial dependencies and scope checks | No claim that the received collection is complete or current |
| First-contact verification | Genesis relationship, three proofs, roles and time interval | Successful claim remains unverified |
| First-contact storage | Retry/reopen, explicit policy, ambiguity and unlinked-claim handling | No independent identity verification or mailbox mapping |
| Successor verification | Trusted predecessor anchor, changed-binding proofs and role policy | Result remains uncommitted until the database transaction succeeds |
| Successor storage | Atomic head updates, retained authorized forks, revocation replay resistance, record collisions and process exit before commit | No distributed freshness, branch repair, backup rollback protection or outgoing MLS coordination |
| Current device authorization | Snapshot of accepted head, roster, key, operation role, validity and trust policy; revocation persists through reopen and replay | Decision is not atomically coupled to transport release |

The [successor storage tests](evidence/README.md#durable-successor-acceptance) exercise separate concurrent database connections and an actual child-process exit after writes but before commit. The latter demonstrates rollback and successful retry after reopening, not resilience to power loss, disk corruption or restored historical snapshots.

An unverified first-contact pin remains unverified through authorized transitions. A stricter current verification policy still applies. Unlinked genesis claims cannot suspend the pin; authorized successor conflicts hold affected operations. These experiments implement local evidence handling, not a complete authentication service or independently interoperable MLS client. A schema-valid result MUST NOT be exposed as an accepted identity state, and a locally accepted state MUST NOT be presented as globally current merely because its signatures verify.
