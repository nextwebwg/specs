---
title: Private snapshot lookup
order: 10.17
blurb: proposed bounded discovery reference
sectionNav: true
---

# Private snapshot lookup

**Proposed bounded reference binding: `mail-private-snapshot-v0`.** This construction works on ordinary hardware. The evaluator sees a blinded element rather than the selected email address. Every querier downloads the same entire encrypted snapshot for its epoch, so no later setup request identifies the matching row. The decrypted row carries the complete bounded original setup and lifecycle evidence.

The cost is linear bandwidth and rebuild work. The authoritative registrar/index sees enrollment publications, and theft of the encrypted snapshot together with the evaluator secret permits offline guessing and decryption of guessed entries. This construction does not meet a combined-operator-compromise objective or prove malicious-index completeness. It must not be marketed as a general production scalability or anonymity solution.

## The lookup in everyday terms

Alice's app downloads the same complete encrypted directory file as every other querier. It asks an evaluator to help calculate a lookup value without showing it Bob's email address. The app verifies that calculation, finds and decrypts the matching row locally, then checks all of Bob's original setup proofs. There is no Bob-specific file request afterward.

This deliberately trades bandwidth for a simple bounded retrieval contract. It is a correctness reference, not a selected scalable production privacy solution. Installation access can link requests to the same installation even while the selected mailbox remains hidden from the blinded calculation.

> [!note] Finding setup is not completing setup
> The result remains an inert candidate. Current identity, mailbox association, application, local policy and Store acceptance checks still apply. Static rows contain no one-use admission package. An authorized allocation is a separate operation, with its own metadata disclosure.

:::: {.details summary="Epoch, checkpoint and full-file format"}

### One sealed snapshot per epoch

Private profile is exactly `mail-private-snapshot-v0`. Strict JSON/wrapper/common types/signature framing follow the realm owner. Each epoch uses a fresh actual RFC 9497 VOPRF key, generated with its maintained key-generation procedure. Never select a key supplied by a lookup response outside the authenticated checkpoint/configuration chain. Epoch is a monotonic global uint64 string within realm, starts 1 and increments1 under the snapshot authority's durable CAS; config changes do not reset it.

One epoch has one immutable context/file/checkpoint, never rebuilt with different rows under the same epoch/key. Failed build discards its private key/context and cannot reuse that epoch as a conflicting signed version; reserve the next monotonic ID and retain failure history. Clients may observe gaps but never lower/equal-conflicting epochs.

Context payload has the following exact required members:

| Member | Contract |
| --- | --- |
| `profile` | Exact profile string selected for this record. |
| `purpose` | Exact purpose string stated below. |
| `realm` | Configured realm ObjectId. |
| `configurationDigest` | SHA256 of the original selected configuration payload. |
| `epoch` | Monotonic global uint64 string. |
| `evaluatorKey` | Canonical base64 RFC 9497 public element. |
| `indexSequence` | Monotonic global uint64 string. |
| `slots` | Configured canonical uint64 slot-count string. |
| `cellBytes` | Configured canonical uint64 cell-size string. |
| `notBefore` | Canonical uint64 Unix-seconds string. |
| `notAfter` | Canonical uint64 Unix-seconds string. |

Its purpose is `snapshot-context`. evaluatorKey is canonical padded base6432-byte RFC 9497 ristretto255 public-element serialization; reject invalid/identity/noncanonical elements by the maintained suite. IndexSequence is the exact serialized mutation cut: the builder includes all eligible admitted records and received safety withdrawals through that cut. slots/cellBytes equal current configuration geometry.

Require notAfter-notBefore <= epochLifetimeSeconds and the complete current clock interval inside both context/checkpoint and current configuration admission. At every new candidate acceptance require currentClockUpper-notBefore <= maxCheckpointAgeSeconds with checked subtraction; polling or an exact cached checkpoint cannot refresh this age. Records have their separate original intervals, checked at use.

Checkpoint payload has the following exact required members:

| Member | Contract |
| --- | --- |
| `profile` | Exact profile string selected for this record. |
| `purpose` | Exact purpose string stated below. |
| `realm` | Configured realm ObjectId. |
| `configurationDigest` | SHA256 of the original selected configuration payload. |
| `epoch` | Monotonic global uint64 string. |
| `predecessor` | Original predecessor payload digest, or the explicitly allowed empty string. |
| `context` | Original context JSON, base64 encoded. |
| `snapshotDigest` | SHA256 of the complete original binary snapshot. |
| `snapshotBytes` | Exact canonical uint64 snapshot-length string. |
| `indexSequence` | Monotonic global uint64 string. |
| `notBefore` | Canonical uint64 Unix-seconds string. |
| `notAfter` | Canonical uint64 Unix-seconds string. |

Its purpose is `snapshot-checkpoint`. context is base64 original context JSON; snapshotDigest is SHA256 of complete original binary file, snapshotBytes equals its exact byte length/config geometry, indexSequence and interval exactly equal context. predecessor hashes the prior original successful checkpoint payload. It is empty only for the first successful checkpoint, whose epoch may be greater than 1 if initial reservations failed. The authenticated complete chain and retained history must establish that this is the first success. Every later successful checkpoint names the last successful checkpoint; failed reservations consume epoch IDs without supplying a checkpoint or resetting history. Sign by current configuration's checkpointKey, domain mail/realm/checkpoint/v0. Context is authenticated through those original checkpoint bytes, not independently self-trusted. Changes require a new epoch/key/file; mirrors cannot edit them.

Binary file is exactly ASCII `MAILSNAP0` (9 bytes), raw 32-byte SHA256 context digest, U64BE slots, U64BE cellBytes, then slots rows. Each row is raw tag32 || nonce12 || ciphertext(cellBytes) || authenticationTag16. Total length57 + slots*(60+cellBytes), checked before allocation, must exactly match checkpoint/config. Rows strictly increase lexicographically by tag; reject duplicates, trailing bytes, wrong lengths and oversized counts before cryptographic work.

The builder pads to exactly slots rows and exactly cellBytes encrypted plaintext per row. No compression, variable recipient-specific segment download, selected-row GET or range fetch exists.

Every canonical mailbox has one real row containing all its complete bounded publication entries/tombstones, not one row per device or an address-prefix shard. Dummy tags/nonces/ciphertexts/authentication tags are random of the same lengths; reject tag collision and regenerate dummy rows during the one original build. The index may know real membership; public mirrors receive only the same encrypted file/checkpoint. Public geometry conceals actual member/record length only within that geometry, not the realm size class or traffic timing.

### Publishing safely across an interruption

A directory rebuild must not become a different directory under an already used epoch number. Readers see either the previously committed publication or the complete new one. A half-written file, a checkpoint without its file, or a file without its matching evaluator cannot become the new publication.

| Authority state | What may happen next |
| --- | --- |
| Epoch reserved durably | Build one fresh context and key for that reservation. The reservation remains consumed even if the process stops. |
| Build staged privately | Validate the complete file, checkpoint and matching evaluator custody. Staged data is not a published result. |
| Publication committed | Serve its exact original artifacts, subject to current configuration and expiry checks. A retry cannot replace them. |
| Reservation failed or abandoned | Retain the consumed epoch and failure state. A replacement build reserves a new epoch. |

The publication transaction compares the reserved predecessor and configuration against the authority's current state. It commits the original context/file/checkpoint, recoverable custody of the matching evaluator key and new successful head together, or commits none of that publication. A competing publisher, later successful head or configuration change cannot let an older reservation overwrite current state. Index sequence cannot decrease across successful publications. Configuration changes do not reset the realm's reservation or successful-checkpoint history.

After restart, a reservation with no complete committed publication is not a successful checkpoint. Recovery may finish the exact retained staged build if its original reservation and all current publication checks still hold, or abandon it. It must not generate a replacement key, context or dataset under that same epoch. Failed reservations do not become predecessors; the next successful checkpoint names the last successful original checkpoint payload.

Private evaluator-key persistence belongs to the protected authority-storage adapter. Restoring a key must verify that it matches the original checkpoint's authenticated context and file before evaluation is possible. Storage encryption does not establish operating-system key protection or make old copies on backups or storage media disappear. Retirement must stop new evaluations under an expired or otherwise ineligible context; cached artifacts and a successful restart cannot extend its original interval.

Acceptance evidence must exercise interruption after reservation and before publication, restart with a consumed failed epoch, concurrent publishers, a configuration change during a build, nondecreasing successful index cuts, exact retries, mismatched or damaged restored key/file/checkpoint custody, and refusal of expired evaluation, including an expired observation followed by an older clock reading or restart. Verify both retained history and the actual artifacts an evaluator serves. A one-shot builder value or an in-memory lock is insufficient evidence of these durable properties.

### Row content and currentness

Cell plaintext is U32BE length, that many original UTF-8 cell bytes, then random padding to cellBytes. Length must fit cellBytes-4; no truncation/spillover allowed. Cell strict JSON exactly `{profile,purpose,realm,mailbox,entries}`, purpose snapshot-cell. Entries is a sorted bounded array of tagged objects:

- `{kind:"active",chain,bundle,receipt}`: chain contains all original signed directory-publication wrappers from initial generation through this current active head; bundle is base64 complete original current static bundle; receipt original index commit wrapper for head. Every predecessor/device/mailbox/bundle/interval and original signature is checked, with historical chain records validated as history and the selected active head/current setup checked at the actual current credible clock. Expired predecessor payloads may establish continuity but cannot supply current keys or readiness. Multiple distinct eligible principals remain ambiguous, not a chosen newest record.
- `{kind:"withdrawn",record,evidence,receipt}`: original directory-withdrawal wrapper, its exact withdrawal evidence and index commit receipt. It supplies only negative/safety evidence, never new setup. A valid safety stop does not require treating missing positive history as identity continuity.
- `{kind:"migrated",chain,record,evidence,receipt}`: source directory chain through predecessor, original migration wrapper, complete destination/handover evidence and source index receipt. A distinct active destination entry must also carry its complete original bundle/chain/receipt; following a URL is forbidden. If both cannot fit, no new positive migration commits into this bounded profile.
- `{kind:"association-withdrawn",association,source,receipt}`: complete original association publication, original signed registrar source tombstone and original association-safety index receipt from the realm owner. No directory/device signature is invented by the index. All affected old assurance is ineligible.

Sort entries by `(publication ID, kind)` for directory entries, and by association publication ID after directory entries for association-withdrawn; unique terminal/head key. Chains preserve ascending generations. A complete build cannot omit a received valid safety stop through indexSequence. Positive capacity limits never justify publishing known-withdrawn setup; stop the new epoch instead. No list says that a missing entry means the address is unassigned or cannot encrypt elsewhere.

For historical checkpoints, authenticate each original wrapper/context under the exact verified configuration named by its original digest, including its key, role and geometry. The checkpoint and that historical configuration need an eligible interval intersection, not whole-interval containment. The earliest intersection point must satisfy the original checkpoint age bound; disjoint intervals or an already-ineligible age do not establish eligible history. This verifies possible historical eligibility and signed continuity, not the actual time a signer published it or global currentness. Along the successful checkpoint chain, referenced configuration generations may stay equal or advance but cannot decrease; a transition does not reset global epoch or index-sequence history. Builder-generated epochs may use the stricter contained interval. The selected operational head must still name the current configuration and satisfy the complete actual current clock, age and all original admission rules; expired historical authority cannot supply a current head.

The client retains validated realm/config/checkpoint/index high-water under a witnessed local transaction before using newly acquired evidence. Higher epoch with lower indexSequence, lower epoch, equal epoch unequal original checkpoint, missing known config history or previously known tombstone revival is conflict/held. Exact known file/checkpoint may be cached and reused only within all original validity/current local policy.

A new client without history trusts the configured index/checkpoint authority; a malicious valid signer can fork or withhold. This profile has no independent witness, global latest-proof or registration nonmembership proof. Currentness means authenticated eligible evidence within bounded freshness and retained history, not instantaneous global revocation.

::::

:::: {.details summary="Intact VOPRF and row encryption"}

### RFC 9497 operation and input

Use RFC 9497 **VOPRF mode**, suite `ristretto255-SHA512`, without changing its HashToGroup, blinding, DLEQ proof, evaluation, unblinding or Finalize algorithms. One deliberately selected canonical mailbox produces exactly one RFC input. This profile does not splice RFC output into APSI or label an ordinary mailbox hash private.

Input bytes are ASCII `mail/realm/lookup/v0`, NUL, raw 16-byte realm ID, raw 32-byte contextDigest, U16BE canonical mailbox UTF-8 byte length, canonical mailbox UTF-8 bytes. Enforce RFC input-length and containing mailbox bounds; received signed addresses remain their exact canonical mailbox-owner spelling. The context digest binds selected epoch/config/public key/geometry. Blind using a fresh cryptographic random scalar through the maintained client primitive.

Verify returned proof under the exact checkpoint evaluatorKey before Finalize; do not accept successful decoding as a valid proof. The resulting RFC output is64 bytes; the evaluator sees neither clear input nor this finalized output under the construction assumptions. [RFC 9497](https://www.rfc-editor.org/rfc/rfc9497.html)

Use existing HKDF-SHA256: PRK = HKDF-Extract(salt=raw contextDigest, IKM=64-byte RFC output). Derive tag = HKDF-Expand(PRK, ASCII `mail/realm/entry-tag/v0`,32) and key = HKDF-Expand(PRK, ASCII `mail/realm/entry-aead-key/v0`,32). These are exact separate purposes; no Unicode/JSON/hex-text conversion enters this input. This is a proposed application composition of maintained primitives, not a new RFC 9497 algorithm or an already-audited security proof. [HKDF](https://www.rfc-editor.org/rfc/rfc5869.html)

Real row uses AEAD_AES_256_GCM with this32-byte key, fresh random 12-byte nonce, AAD raw contextDigest || raw tag (64 bytes), cellBytes plaintext and 16-byte authentication tag. Build each mailbox row once per fresh key/context, never re-encrypt/rewrite the sealed epoch. Builder enforces nonce uniqueness if a derived key unexpectedly repeats and treats duplicate real tag/input as an error rather than merging unequal data. No private message/init key is derived or placed here. [AEAD](https://www.rfc-editor.org/rfc/rfc5116.html)

Client verifies complete file signature/hash/geometry/order first, locates its locally derived tag, and decrypts only the matching row using maintained AEAD. Matching tag with failed AEAD/length/schema/exact mailbox/realm checks is invalid/unknown, not an empty result. Successful row decryption still requires every original registration/identity/publication/assertion/service/lifecycle check and local pins.

Every index receipt must verify under its exact historically admitted index key, match the original mutation/head/lineage/generation/realm/configuration, and have indexSequence no greater than the selected checkpoint cut. A receipt from a newer cut cannot be smuggled into an older context; receipt success alone does not authenticate its bundle or subject. No matched row means no usable entry in this authenticated file, not proof unsupported, unassigned or offline. Do not fetch another address-specific object after any outcome.

### Exact public acquisition routes

All are relative to the configured role prefix, without target-address query parameters or redirects. The deployed profile uses [installation admission](realm-access.md): background own-installation enrollment, exact per-origin resource scopes and signed POST /operations. The table below defines logical role handlers and complete result bytes; it is not an additional anonymous deployed interface.

The access operation binds the original evaluate/body or whole snapshot epoch request, performs work admission first and returns exact complete bytes in its bounded result envelope. Direct server-authenticated anonymous calls to these logical paths remain a comparative/local-test mode only. They cannot be advertised as the default abuse-protected profile or silently reuse the old /mail/access/query parser.

Access tokens and per-origin installation keys can link queries while VOPRF still hides their target input; no unlinkable-credential or hardware requirement is implied.

| Role/route | Exact request | Successful response |
| --- | --- | --- |
| Mirror GET /current | no body/query |200 `{profile,checkpoint}` original signed current checkpoint |
| Mirror GET /checkpoints | no body/query |200 `{profile,chain}` all original successful checkpoint wrappers from the first successful epoch to current within maxChainEntries |
| Mirror GET /snapshots/{epoch} | canonical uint epoch, no query/body/Range |200 application/octet-stream exact full immutable file named by selected checkpoint |
| Evaluator POST `/evaluate` | `application/json`; exact evaluation request below | HTTP 200 exact evaluation response below |

The evaluation request contains exactly `profile`, `request`, `checkpointDigest`, `contextDigest` and `element`. The response contains exactly those members plus `proof`:

| Member | Request | Response |
| --- | --- | --- |
| `profile` | `mail-private-snapshot-v0` | Same exact profile |
| `request` | Request ObjectId | Exact request ObjectId |
| `checkpointDigest` | SHA256 of the selected original checkpoint payload | Exact requested digest |
| `contextDigest` | SHA256 of the selected original context payload | Exact requested digest |
| `element` | Canonical padded base64 of the 32-byte blinded element | Canonical padded base64 of the 32-byte evaluation element |
| `proof` | Absent | Canonical padded base64 of the 64-byte RFC proof |

The request ID is an ObjectId. The element and proof byte encodings must match the table above. Validate with suite deserializers and reject identity/invalid encodings; body budgets apply first. Evaluator serves only its exact retained sealed checkpoint/context/key within original interval/current configuration admission.

It cannot change public key, expose private key, answer an unrelated realm or infer a target from a clear address field. Exact repeated request/body may be re-evaluated or return its retained identical cryptographic evaluation, with fresh valid proof randomness allowed; proof original bytes are retained by that client attempt, not a new authoritative dataset. Unequal body under a retained authenticated request ID409; invalid input never burns a durable ID. No directory mutation occurs.

The client obtains/validates the common checkpoint chain as needed, downloads the same complete snapshot (or uses its complete validated cache), then evaluates its selected address. Order of those two public network operations may be reversed without sending selected-row hints. It verifies proof and full setup locally before committing an eligible candidate. All logical file/metadata selections in the deployed signed operations identify only a global realm epoch/chain, never the matching row, service locator, address or device.

Normalizing/telemetry headers must not reintroduce a clear address. A bounded client unable to retrieve the entire file cannot use a partial file or selected-range fallback.

Checkpoint chain retrieval detects rollback against retained history; it does not make an unknown current head globally trustworthy. If the full required chain exceeds local maxChainEntries, hold this reference path rather than silently reset high-water. Each new successful epoch extends the predecessor chain; failed reserved epochs can be skipped. Poll no faster than configured pollSeconds; source transport/backoff/local original query deadline bound retries, never extend original human setup/send policy.

Unknown/expired/missing epoch 404, invalid group/proof/context400, configured admission401/403, bounds413, media415, conflict 409, rate429+positive Retry-After, unavailable503, same exact `{error}` grammar as realm owner. A valid proof from a retired context is not current setup.

Before final candidate use recheck current configuration/checkpoint/high-water/time and original local association/pin/restore constraints. If a newer configuration/checkpoint becomes known concurrently, validate under it or hold/restart a separately bounded query; no mutation of old input/blind state or deadline. Blind state is sensitive transient local state. Persist only under protected owning retry storage when supported, otherwise a lost state requires fresh blinding within original policy; no fake unblinding from retained server output.

Stop/delete transient state when its attempt ends. Typing/presence/recipient inbox mail never follows from lookup.

::::

## What each operator can learn or lose

| Component | Honest exposure and compromise limit |
| --- | --- |
| Registrar | Knows enrolled mailbox, device and chosen home; mailbox-control email may be retained by ordinary providers. |
| Authoritative index/builder | Receives plaintext signed registrations/static bundles and current ordering. Its database alone can expose enrollment. Do not call that database confidential merely because public mirrors are encrypted. |
| Evaluator | Sees blinded elements, epoch, timing/admission identity and network address; normal RFC execution does not expose clear queried mailbox. Its key enables offline evaluation of guessed inputs. |
| Public mirror artifact alone | Encrypted fixed rows/geometry/checkpoints; does not contain clear mailbox mapping, absent leaked builder/log state or evaluator secret. This is narrower than “any DB compromise is safe.” |
| Mirror file plus evaluator secret | Guesses can derive tags/row keys and decrypt guessed membership/setup. No combined-compromise resistance claim. Historical stolen keys remain dangerous for historical files despite later rotation. |
| Malicious index/checkpoint authority | Can withhold/fork/stale/omit publications within trusted-authority/freshness limits. Original subject signatures still prevent it minting another device's valid setup; first-use currentness/completeness remains a trust assumption. |
| Authorized querier | Can query guessed selected inputs and learns returned setup; this protocol does not cryptographically stop chosen-address enumeration. Admission/metering/abuse limits add cost with stated privacy tradeoffs. |

One selected recipient may be queried automatically under enabled account policy; no whole-contact-list upload or realm crawl is part of this profile. The reference avoids specialized hardware and target-specific retrieval, but bandwidth, operator knowledge, traffic analysis, access-token linkability and unavailable/latest-proof limits remain explicit. Production scaling, combined-compromise privacy and stronger consistency need separate maintained constructions and measured evidence; this bounded reference does not discharge those full-goal requirements.
