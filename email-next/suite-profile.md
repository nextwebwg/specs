---
title: Protected conversation agreement
order: -0.4
blurb: exact baseline · signed agreement · indexed replies · version boundaries
sectionNav: true
---

# Protected conversation agreement

Email/2's Encryption module uses one exact protected conversation agreement, `email2-conversation-v0`. It requires a protected core and allows the independent Answers, Reactions and Corrections modules. Each conversation selects an explicit common operation set from signed device support. Providers and base conversation clients need not implement every module.

This is part of the one unpublished Email/2 specification. Earlier experimental encodings retain their recorded schemas and test scope; they are not separate editions of Email/2. The [module framework](modules.md) owns adoption and indicator semantics. The complete protected conversation bundle means all three interaction modules together; it is not a prerequisite for every role or implementation. Joined implementation and acceptance evidence remain required before advertisement.

## Exact selection

| Component | Selected value |
| --- | --- |
| MLS protocol | Version 1, RFC9420 |
| MLS cipher suite | `0x0001`, `MLS_128_DHKEMX25519_AES128GCM_SHA256_Ed25519` |
| Credential, account and device encodings | Existing [security-profile](security-profile.md) encodings and identity-state authorization |
| Contribution envelope | Version `4`, including encrypted personal From/To/Cc, protected presentation and disclosure/delivery semantics |
| Application context | Version `8`, defined below |
| Application payload | `mime-suite-v0`, defined below |
| Ordering | `endpoint-quorum-v0`, with the existing certified witness-policy and authority checks |
| Passive assertion | Version `8` |
| Initial invitation / common roster | Version `8` / version `5` |
| Established invitation | Version `8` |
| Ordering exchange / final control carrier | Version `2` / version `3` |
| Baseline presentation | `html-css-v0`, mandatory |
| Indexed-reply presentation | `html-css-reply-v0`, mandatory |
| Indexed-reply operation version | `0` under [reply-parts-v0](reply-content.md) |

## Module agreement and common operation selection

Every Encryption implementation supports this protected core, including both required HTML/CSS presentation profiles:

```json
["attachment-message","message","reply-message","rich-message"]
```

Optional interaction modules add complete operation blocks:

| Module | Operations added together |
| --- | --- |
| Answers | `answer`, `question` |
| Reactions | `reaction`, `reaction-withdraw` |
| Corrections | `edit` |

A selected operation array is the distinct ASCII-sorted union of the core and zero or more complete blocks. These are exactly eight possible sets. A missing core operation, partial block, unknown operation or unsorted/duplicate array is invalid. The complete bundle selects:

```json
["answer","attachment-message","edit","message","question","reaction","reaction-withdraw","reply-message","rich-message"]
```

Each assertion8 advertises all eight-or-fewer application tuples generated from every subset of the optional modules that device actually supports, including the core-only tuple. Each tuple has exactly `envelopeVersion: "4"`, `payload: "mime-suite-v0"`, its operation array and `ordering: "endpoint-quorum-v0"`. The applications array contains no duplicates and is ordered lexicographically by its operation arrays using ASCII comparison, with a proper prefix before a longer sequence. The array must be exactly that subset closure of its maximal module set. No extra `modules` field or feature boolean is needed to interpret it.

For initial establishment, resolve one exact current valid signed assertion8 per intended device under the existing identity, association, freshness and package rules. Include the sender's participating devices. Recover each assertion's maximal supported optional module set; intersect those sets across all selected devices. The selected context application is the protected core plus that intersection. Freeze the exact selected assertions and application in the preparation. Every device's advertisement must contain that exact tuple. Missing evidence or an unsupported dependency holds establishment; remembered capability booleans cannot substitute for signatures.

A user can disable use of an optional module locally without changing its wire meaning. A product must not offer an operation absent from the conversation's selected agreement. Unsupported operations cannot be repaired by silently changing them into another operation. Ordinary-mail/hosted alternatives follow the independent disclosure policy; semantic conversion requires its own deliberate composition.

An established context retains its exact operation set. Newly available module support can be selected for the next new conversation; it cannot edit an existing GroupContext in place. Adding a device requires its signed support for the existing agreement. If it cannot meet that agreement, hold that addition or deliberately establish a new compatible conversation; never silently lower the old agreement.

Service-question operations, arbitrary forms, rich-content edits, presence and read receipts are not part of these eight combinations. Service actions need their own explicit owning agreement; an HTTPS link cannot imply support. Provider discovery, relay support and verification are separately negotiated capabilities, not operation blocks in this application object.

The [encrypted personal-address record](private-address-presentation.md) is required in every contribution of this Encryption agreement. Provider relay services have their own capabilities/authorization; lack of a relay does not remove personal addresses from the encrypted record. The selected identity and membership contracts apply in full, including conflicts, revocation, enrollment, removal, historical contexts, package use and send-time authority. An application tuple does not authenticate a mailbox association or bypass first-contact policy.

## Context and signed receiving agreement

Context `8` has the exact context7 field set and value grammars, with its `version` set to `"8"`. Its application object has exactly `envelopeVersion`, `payload` and `operations`, selected as above. For the complete bundle it is:

```json
{
  "envelopeVersion": "4",
  "payload": "mime-suite-v0",
  "operations": ["answer","attachment-message","edit","message","question","reaction","reaction-withdraw","reply-message","rich-message"]
}
```

Its ordering object selects `endpoint-quorum-v0`; the proof, witness-policy, administrator, delivery and private-copy constraints from context7 apply unchanged. Other context fields do not acquire new defaults. Exact full GroupContext bytes bind the context8 agreement into ordering scopes and candidate commitments. A proof from a different predecessor or application agreement cannot be transplanted even when its witness names match.

Assertion8 retains the assertion7 field set, wrapper, identity bundle, validity and package rules, with `version: "8"`. Its mailbox uses the required [canonical address contract](mailbox-addresses.md), including internationalized/quoted local parts. This same address grammar applies to current invitation/roster target mailboxes, mailbox associations, provider account bindings and encrypted personal addresses; older experimental ASCII-only validators do not establish current-suite support. Its `applications` array is the exact module-subset closure specified above, rather than assertion7's one-entry restriction. Its `features` must include `mls-1-0001`. Its required `orderingExchanges` is exactly `[{"format":"quorum-exchange-experiment","version":"2"}]`. Only the selected module application combinations and that one exchange entry are admitted in assertion8. Its signature domain is `email-next/passive-discovery/v8`, using the existing NUL and length framing.

Every intended receiving device must have its own current valid assertion8 containing the exact selected combination. A device that supports some operations under assertion5 and other operations under assertion7 does not support assertion8. Current identity authority, exact key/package binding, applicable freshness and mailbox association are rechecked at admission and release under their owning contracts. Retain original signed evidence; never synthesize an assertion from remembered feature booleans.

The selected presentation profiles are fixed implications of this exact suite tuple, not optional attributes inferred from message content. Advertising assertion8 requires complete receiving support for both. A later profile requiring a different presentation needs another explicit versioned binding.

## Initial and established admission

Initial invitation8 and roster5 inherit the complete initial invitation7/roster4 field sets, validation dependencies and atomic admission procedure, with their own versions `"8"` and `"5"`. They require assertion8 for every admitted device, context8 and the exact selected application. Their signature domains are `email-next/mls-new-conversation-invitation/v8` and `email-next/mls-initial-roster/v5`, with the existing signature framing. References and embedded signed objects name those original new-version bytes; replacing a version number in an old signature is invalid.

Established invitation8 inherits established invitation7's field set, genesis anchoring, contiguous certified ordering path, complete supplemental assertion objects, package selection and atomic Welcome processing. It requires context8, assertion8 and final carrier3 evidence. Its signature domain is `email-next/mls-established-membership-invitation/v8`. Unknown/mixed versions hold admission; no version7 fallback is attempted after version8 validation fails.

Neither first-contact genesis nor a valid invitation installs an unreviewed trust anchor merely by being received. The existing independent anchor and mailbox-association rules apply. Initial admission establishes the generation-zero witness policy rather than claiming a quorum certificate already exists for it.

## Ordering exchange and final delivery

Exchange2 has the exact exchange1 field set, kind/purpose, canonical encoding, candidate/proof dependency rules and durable vote behavior, with `version: "2"`. Its supplied `witnessAssertions` are complete assertion8 wrappers; their selected application must match context8. Exchange2 does not add an `applicationAssertions` member; Add-package evidence belongs to the final carrier. Only the certified witness policy grants voting authority. A receiving device's exchange-support claim does not make it a witness.

Final carrier3 has the exact final carrier2 field set with `version: "3"`, complete `applicationAssertions` for the actual Add packages, and complete `witnessAssertions` for every resulting witness, all using assertion8. Established invitation8 retains the same four-member path-edge objects as established7, using the new assertion wrappers. Missing, extra, stale-at-use or substituted authority evidence holds the complete transition.

The ordering scope, candidate and certificate object versions, hashes and signature domains remain those of [ordering proofs](ordering-proofs.md). They already commit the exact full predecessor GroupContext and resulting application context. Reusing their encoding does not authorize a context change: validation must require context8 at the suite boundary and the exact result authorized by the selected transition. Supplemental assertion bytes remain independently authenticated evidence, not a second consensus identity.

The existing control MIME placement, decoded/control byte limits, immutable transport retry, terminal-only notification and atomic catch-up rules apply to exchange2/carrier3. A wrapper-version failure cannot be repaired by dropping supplemental fields or trying exchange1/carrier2. Receipt of an exchange alone never installs a transition. After complete proof, authority, dependency and support validation, an eligible proof root may authorize the specific durable local vote defined by the ordering-exchange state machine. Unknown or invalid traffic cannot trigger a response, and a vote is not an automatic email reply.

## One MIME carrier, explicit operation dispatch

`mime-suite-v0` is one complete MIME entity inside MLS application data, not an enclosing mail message. Use the [rich-carrier direct structure](rich-messages.md#exact-direct-structure), header/transfer-encoding rules and resource limits: plain-text projection first, HTML projection second (with its related resources when applicable), exact envelope bytes third, and declared independent attachments in the specified outer mixed structure.

Select this carrier only from the authenticated context8 application agreement. Validate the complete required personal-address record and role/audience binding as well as the operation. Validate its bounded direct framing and extract its exact event alternative, then strictly decode envelope4 and the selected operation. The authenticated operation kind determines the following validation branch. This is dispatch within one agreed carrier, not payload sniffing or trying several parsers until one accepts.

| Operation | HTML and text projection | Resources |
| --- | --- | --- |
| `rich-message` | Its exact `html` and `text`, under `html-css-v0` and existing MIME text serialization | Complete rich-message manifest and role records |
| `reply-message` | Its exact annotated `html` and specified ordered `text` projection, under `html-css-reply-v0` and existing MIME text serialization | Complete indexed-reply manifest and role records |
| `attachment-message` | Existing message/attachment readable projection | Existing complete attachment binding |
| `message`, `question`, `answer`, `reaction`, `reaction-withdraw`, `edit` | Existing operation-owned readable projection; edit text stays literal text, never sender HTML | No resource parts |

For the two rich operations, use their complete manifest, embedded and attachment contracts. For `attachment-message`, use its existing complete attachment binding. The other operations permit no resource parts and no invented manifest fields. Every alternative must obey its owning readable-content obligations; disagreement is retained and reported as a projection discrepancy and never replaces accepted authenticated event meaning. An operation with a malformed required representation does not acquire effects through a different representation.

For resource-free non-rich projections, generate a fresh `<!doctype html>` document with explicit UTF-8 metadata and only the baseline permitted elements. Escape authored strings as text and preserve meaningful line breaks. Interaction controls are derived by the client after authentication, not embedded sender controls. Source-preserving diagnostic access remains distinct from successful required rendering.

Both rich and indexed replies retain their original event and HTML bytes. The client validates the indexed reply's complete index/Microdata agreement before carrying source mappings into a fresh filtered tree. Choosing `reply-message` does not relax baseline resource isolation, principal/audience authority, disclosure rules or cycle handling. Invalid or unresolved quotation evidence has the exact visible outcomes defined in the reply-content contract.

## Release, migration and failure

A sender may prepare suite traffic only after all intended device agreements and authorities resolve. Apply the [freshness contract](freshness.md) per intended device, with cached continuity as the asynchronous default. Current known-pair and bootstrap responses carry assertion8; a recent timestamp, offline publication or provider status cannot substitute for a required live device response. The existing release transaction and immediate pre-DATA checks cover the immutable context, operation, disclosure plan, identity heads, recipient associations and package/membership dependencies. Changing sender or audience requires reevaluation, not reuse of another account's plan.

An existing context6 or context7 conversation cannot be changed in place by editing its local application record. This version selects fresh conversation establishment with fresh authorized admission for migration. The new conversation has its own identity and does not inherit old group authority or history rights. A client may associate the views locally but must preserve the distinct protocol contexts. ReInit and authenticated in-place application migration remain unsupported unless separately specified.

An unsupported peer follows the sender's selected delivery policy. Do not remove required operations to keep the suite name, reinterpret a protected body as ordinary content, or weaken encryption after a timeout. Unsupported suite traffic remains retained and inactive, with safe diagnostic access. Established older agreements continue under their own exact rules.

## Acceptance obligations

Before advertising an Encryption/module combination, exercise assertion8 signing, complete subset-closure validation and common operation selection; initial8/roster5 and established8 admission; exchange2/carrier3 membership, removal and catch-up; every operation in the selected agreement under envelope4; both required presentation profiles; source-index extraction; immutable retries; restart; and actual resource retrieval. Include mixed-version, omitted-operation, changed-context, package-substitution, malformed-carrier, duplicate-ID and unavailable-source cases, plus missing/unsupported addresses, address/role mismatch, private-copy address leakage and conflicting mailbox-association display.

A complete-bundle positive run must send a rich message, indexed reply, predefined answer, reaction/withdrawal and plain-message correction between retained independent endpoint stores; then add and remove a device and repeat delivery after restart. It must demonstrate actual encryption and decryption through the mail path, not just parse the new descriptors. Also run core-only and every optional-module combination, including endpoints with different maximal support, no-common optional modules and attempted unsupported operations. Independent implementations and security review remain external evidence. No current reference experiment is claimed to pass the joined suite. The [module-selection component](evidence/README.md#protected-module-selection) covers only the bounded operation/offer algorithm.
