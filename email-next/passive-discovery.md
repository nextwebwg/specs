---
title: Experimental passive discovery binding
order: 10.5
blurb: ordinary email · signed advertisements · first contact
sectionNav: true
---

# Experimental passive discovery binding

A normal email can introduce the sending device's encryption capabilities. This experimental format carries that introduction in a signed attachment beside the readable message. A later human reply can carry the other device's introduction. Receiving one does not send mail, open a URL or create a conversation.

> [!ex] Learn about encryption while exchanging ordinary mail
> Alice sends Bob a message with an `email-next-discovery.json` attachment. Bob's upgraded client can examine the device's signed capabilities and identity evidence. His older client may simply show the attachment.
>
> When Bob writes a reply, his client can include its own advertisement. Neither the attachment's signature nor a matching From address proves mailbox ownership. Each client still applies its identity and first-contact policy before using the material.

The advertisement describes **one device**, optionally supplying **one MLS admission package**. The current [assertion8 agreement](suite-profile.md) selects the broader [canonical address contract](mailbox-addresses.md); this chapter’s earlier experimental encodings and parser retain their stated narrower mailbox grammar. It is not an account-wide promise that every client can decrypt. This first format supports a narrow set of ASCII mailbox spellings and the `mls-1-0001` feature only; it does not advertise rich rendering or answer buttons.

> [!warn] Experimental binding
> This is an unregistered candidate format with partial parsing experiments, not a complete secure bootstrap protocol. Mailbox ownership verification, full MLS admission and acceptance tests remain prerequisites.

## Sending and recognizing an advertisement

The discovery attachment accompanies the human-readable body rather than replacing it. Automatic discovery examines only its defined position in the outer message; it does not search forwarded messages, archives or quoted text for something that looks like an advertisement.

An invalid or ambiguous attachment leaves discovery inactive without preventing the person from reading the email. Previously accepted identity evidence remains intact. There is no promise that a legacy client will hide the attachment.

::: {.details summary="MIME placement, headers and transfer decoding"}

### Carrier

Use a direct child of the outer `multipart/mixed`, after the normal readable body (which may itself be `multipart/alternative`). If the message already uses mixed, append that child. The proposed content type is `application/vnd.threadlabs.email-next-discovery+json`, with no parameters; this name is unregistered and requires an isolated experiment agreement until registration. Use `Content-Transfer-Encoding: base64` and `Content-Disposition: attachment; filename="email-next-discovery.json"`. Normal MIME-Version remains 1.0. No new header, MIME parameter or Content-ID carries security authority.

The part is independent metadata, not an alternative rendering of the author's prose. Do not put it inside multipart/alternative, preamble, epilogue, external-body or a header comment. Legacy clients may show it as an attachment; there is no promise of invisibility. Use normal 76-column MIME base64 encoding. MIME transfer decoding precedes strict JSON interpretation and signature verification; transfer re-encoding that preserves decoded octets is harmless.

Automatic discovery scans only the direct discovery child of the received message's outer mixed body. It does not recursively activate attachments inside forwarded message/rfc822 or message/global content, nested archives, arbitrary mixed descendants or quoted prose. Multiple discovery children leave automatic discovery inactive for that message; they do not erase previously accepted evidence. A separately protected S/MIME or MLS carrier needs its own placement rule; this initial carrier is ordinary readable mail only. Do not place an otherwise private identity bundle outside encryption merely to satisfy this carrier.

The receiver requires one MIME-Version value of `1.0` on the outer mixed message and unambiguous Content-Type fields. The discovery part requires one parameter-free discovery Content-Type, one base64 transfer encoding and one attachment disposition. The suggested filename is advisory: it neither selects nor authenticates a part. MIME base64 folding whitespace is permitted, but invalid alphabet, padding or nonzero unused pad bits leaves discovery inactive. Resource-limit failures likewise do not partially install identity evidence. These failures affect discovery processing, not access to the human-readable message.

The sender emits at most one such part per ordinary message. The attachment does not authenticate the surrounding message, its From, Subject, recipients or body. A copied attachment remains the same signed assertion, not proof that the copying sender owns its key. Forwarding clients should omit this locally generated discovery attachment when creating a new forward and may attach their own; nonconforming clients may forward everything. Public identity/device relationships can therefore escape the original audience.

:::

## What the device signs

The outer JSON wrapper carries the original assertion bytes, their signature and an identity-evidence bundle. The assertion names the device, its claimed mailbox, its current identity state, the advertised feature and its validity interval. The signature binds those values together; it does not authenticate the surrounding email.

The exact formats below keep MIME decoding, JSON parsing and signature verification separate. Changing line folding in MIME can preserve the signed bytes; parsing and reserializing the signed JSON cannot substitute for retaining them.

::: {.details summary="Wrapper schema and parsing limits"}

### Wrapper schema

The transfer-decoded body is strict UTF-8 JSON under the [strict JSON rules](event-encoding.md): no BOM, duplicate decoded names, numbers, null, unknown fields or trailing values. Maximum body size is 1,048,576 octets and maximum container depth 32, including wrapper and encoded evidence. The inner assertion and every decoded identity payload independently obey the same byte and depth bounds; encoded strings do not exempt their decoded contents. Total carrier bounds apply before allocation.

Exactly three required members:

| Member | Value |
| --- | --- |
| `payload` | Standard canonical padded base64 of the original signed assertion bytes |
| `signature` | 128 lowercase hexadecimal characters encoding its Ed25519 signature |
| `identity` | An identity-bundle object under the [identity bundle contract](identity-state.md#identity-proof-bundle), with its existing exact payload/proof encoding |

Base64 fields inside JSON use the identity-bundle rule: standard alphabet, required padding, zero unused pad bits and no whitespace; decoding and re-encoding must reproduce the string. This is distinct from MIME base64 line folding. [RFC4648 §§3–5](https://www.rfc-editor.org/rfc/rfc4648.html#section-3) permits a referring profile to require canonical decoding; this profile does so to avoid multiple field spellings for the same bytes. See the [encoding audit](audits/base-encodings.md). Reject malformed wrapper/schema as a unit without partial identity installation. Once syntax succeeds, enclosed identity records remain independently signed evidence; their validation does not depend on trusting the advertisement signature.

:::

::: {.details summary="Signed fields, mailbox spelling, validity and signature input"}

### Signed assertion schema

Version 0 advertises encryption support. Version 1 also describes which conversation operations the device can receive. The decoded payload is a strict JSON object with the following required members; versions 1 and 2 additionally require `applications` as defined below. Version 2 binds operations to an exact payload and ordering combination.

| Member | Value |
| --- | --- |
| `version` | String `0`, `1` or `2` |
| `purpose` | String `passive-discovery` |
| `record` | Nonzero ObjectId, retained with original bytes across retransmission |
| `principal` | enp0 account identifier |
| `device` | end0 identifier of the asserting device |
| `state` | Lowercase SHA256 digest of the referenced identity-state payload |
| `binding` | Lowercase SHA256 digest of this device's binding payload in that state |
| `mailbox` | Exact mailbox claim under the narrow spelling below |
| `notBefore`, `notAfter` | Canonical unsigned-64 decimal strings of UTC epoch seconds |
| `features` | Distinct strings, sorted by ASCII, from the exact set below; empty permitted |
| `keyPackage` | Empty array, or an array containing one canonical base64-encoded TLS-serialized MLSMessage with wire format mls_key_package |

Candidate feature set: only `mls-1-0001`. This token advertises MLS support by this device, not every client at the mailbox. It does not by itself advertise support for conversation operations. Unknown tokens invalidate structured advertisement interpretation. A nonempty keyPackage requires that token. An empty package array means no admission material supplied, not withdrawal or permission to reuse previously consumed packages.

The experimental expiry bound is `notAfter >= notBefore` and at most 604800 seconds apart, matching the experimental admission horizon for operational simplicity. This seven-day bound is a profile choice; MLS does not require it. The complete local current-time uncertainty interval must fit inside the signed interval for new use. The advertisement cannot extend binding or package validity. Receipt time, message Date, or retransmission does not refresh it.

The initial mailbox spelling is deliberately narrow: ASCII RFC5321 Mailbox without angle brackets, an unquoted Dot-string local-part and a DNS domain using ordinary LDH labels (including already validated A-labels). No address literal, comment, display name, route, whitespace, trailing domain dot or local-part escape. Domain letters are lowercase; local-part spelling is preserved exactly. No plus-tag stripping, local-part case folding or alias inference. Parse the domain's DNS label limits and RFC5321 path/mailbox limits; do not approximate with a permissive email regex. Internationalized and quoted local-parts remain unsupported by these earlier encodings; the current assertion8 agreement explicitly selects the [canonical address representation](mailbox-addresses.md). This restriction affects discovery automation, not ordinary mail delivery.

The signature input starts with ASCII `email-next/passive-discovery/v0` for version 0 or `email-next/passive-discovery/v1` for version 1 or `email-next/passive-discovery/v2` for version 2, followed by one zero octet, the four-octet unsigned big-endian payload byte length, then the exact original payload bytes. Use Ed25519 with the binding's signing key. Do not parse and reserialize before verification. The signature covers mailbox, state, binding, lifetime, feature list and exact encoded package. It does not confer independently verified mailbox ownership.

:::

## Advertising conversation support

A version 1 assertion includes a required `applications` array. An empty array advertises no conversation application. Otherwise, the array contains exactly one object with these required members and no others:

| Member | Value |
| --- | --- |
| `envelopeVersion` | String `1` |
| `operations` | Nonempty, ASCII-sorted, unique subset of `answer`, `message`, `question`, `reaction`, `reaction-withdraw` |
| `ordering` | Nonempty, ASCII-sorted, unique subset of `designated-member-v0`, `fixed-roster-v0` |

A nonempty `applications` array requires the `mls-1-0001` feature. Unknown operations, ordering modes, envelope versions or members invalidate the assertion's structured interpretation. The signature covers the complete descriptor. Version 0 has no `applications` member and cannot establish this agreement. A client that implements only version 0 cannot use a version 1 assertion as evidence of compatible conversation support.

Before creating a group, select one operation set and one ordering mode supported by **every intended receiving device**. Complementary capabilities on different devices do not add up to shared support. Bind that selection in the authenticated application context; retain the signed evidence and its identity and mailbox-association dependencies with admission. Recheck those dependencies when admission commits. Missing evidence follows the sender's delivery policy; it never authorizes an automatic downgrade.

Expiry prevents using an advertisement for a new admission. It does not erase an established group agreement or change how previously authenticated messages are interpreted. Changing an established agreement requires an explicit group transition.

::: {.note}
The [signed-admission experiment](evidence/README.md#signed-application-agreement-at-admission) verifies each selected device’s actual signature and support, then commits its evidence, group agreement and MLS admission together. The [version-1 invitation flow](evidence/README.md#version-1-initial-invitation-and-durable-submission) connects that agreement to signed invitation carriage, loopback SMTP submission and atomic admission. Public account onboarding and independent implementations remain separate requirements. The browser conversation demonstration still uses explicitly configured agreements.
:::

### Version 2: exact supported combinations

Version 2 uses the same signed fields and wrapper, but replaces the version-1 application descriptor with an array of exact combinations. Empty still means no application support. Each entry has exactly these fields:

| Member | Value |
| --- | --- |
| `envelopeVersion` | String `1` |
| `payload` | `raw-event-v0` or `mime-contribution-v0` |
| `ordering` | `fixed-roster-v0` or `designated-member-v0` |
| `operations` | Nonempty, ASCII-sorted, unique operation names supported together for this combination |

The raw-event vocabulary is `answer`, `message`, `question`, `reaction`, `reaction-withdraw`. MIME additionally permits `attachment-message`. An implementation advertises only operations whose complete receiving path it supports. Attachment parsing alone is insufficient.

Sort entries lexicographically by `(envelopeVersion, payload, ordering)`. Duplicate keys, unknown members or values, and unsorted entries invalidate structured interpretation. The selected vocabulary permits at most four different keys; there are no omitted or null defaults. A nonempty array requires the `mls-1-0001` feature.

Select one exact key present for every intended device, then intersect its operation sets. Never combine entries to manufacture support for an unadvertised combination. Bind the selected payload and operations in the conversation agreement, retaining the original signed device evidence. Old assertions retain their original schema; a version-2 descriptor cannot be processed as version 1.

> [!note] Implementation boundary
> The tuple validator checks the separate version-2 signature domain. The [joined invitation flow](evidence/README.md#signed-payload-tuple-invitations) also retains the accepted agreement and dispatches protected payloads. A schema check alone does not demonstrate support for a receiving path.

### Version 6: endpoint quorum combination

The configured endpoint-quorum experiment uses assertion version `6` and the fixed signature domain `email-next/passive-discovery/v6`. It keeps the exact signed assertion fields and wrapper. Each `applications` entry selects exactly `envelopeVersion: "3"`, `payload: "mime-rich-v0"` and `ordering: "endpoint-quorum-v0"`. Its nonempty sorted operation set may contain `answer`, `attachment-message`, `message`, `question`, `reaction`, `reaction-withdraw` and `rich-message`. It does not advertise service questions. The same uniqueness, ordering and feature-dependency rules apply; there is only one possible tuple key.

This version selects [conversation context7](group-conversations.md#endpoint-quorum-comparison). Older assertion versions do not gain quorum support. Current device authority, actual admission-package validation and explicit conversation admission are still required. The local experiment exercises signed initial admission and proof-aware established joining; it does not establish public mailbox ownership or automatic acquisition of a conversation trust anchor.

## Deciding whether to use it

A valid signature is one check, not the decision. The client also resolves the identity evidence, checks current receiving authority, and applies its policy for associating a mailbox with an account identity.

> [!ex] A familiar address advertises an unfamiliar identity
> Bob already has an identity pinned for Alice. Another message from her address advertises a different principal. A matching From field cannot replace that pin. The new claim remains unlinked unless a separately authorized identity change establishes it.

An advertisement must refer to the locally accepted identity-state head before operational use. A later accepted head makes the old advertisement stale, even when the device itself remains authorized. Missing evidence leaves work pending rather than triggering a lookup or automatic reply.

::: {.details summary="Identity validation, receiving authority and first-contact policy"}

### Identity and authority checks

Resolve the identity bundle using its existing rules and local retained evidence. Every record must name the assertion principal. The named state must reference the named device/binding digest, and all required chains, signatures, possession proofs, validity and policy checks must succeed. Missing evidence leaves the assertion pending, without network retrieval or an automatic mail response.

For this discovery binding, a device with `receive` authority may advertise only its own receiving features and its own admission material. This does not give receive devices enroll/revoke rights or authorize account-wide assertions. This extends the [device role contract](security-profile.md#device-binding-record-schema) only for discovery assertions. An advertiser also sending human contributions needs send authority for those contributions independently.

For operational use, require the asserted state to be the locally accepted head and binding to remain current under that head. A later accepted state makes this advertisement stale for new use even if the device survives unchanged; it can issue a fresh advertisement bound to the new head. This conservative rule removes ambiguity about whether an old account snapshot still justifies a new operation. Invalid or unlinked incoming claims cannot replace or suspend a pin. Authorized competing successors follow existing branch-conflict handling. Independently valid transition evidence in the bundle can still advance state even when the advertisement is unusable, but only through the identity validator's atomic acceptance rules.

First contact has two separate local decisions: accepting the self-consistent identity genesis and associating its claimed mailbox with that principal. Neither follows from the signature alone. To offer an automatic first-contact candidate, require exactly one parsed outer From mailbox and an exact match to the advertisement mailbox after the narrowly defined domain normalization. A matching From is only a routing consistency check; spoofed mail can satisfy it. Multiple From addresses, Reply-To, Sender, Return-Path and forwarded originals do not supply alternative bootstrap authority.

If configured policy permits unverified first contact, record the mailbox association and genesis explicitly as unverified. A policy requiring independent verification must hold until an independent mechanism supplies it; this candidate defines none. Simultaneous competing first-contact claims remain ambiguous. Once a mailbox is associated with a pinned principal, a different principal is an unlinked claim requiring a separately authorized identity change. A known principal advertising a new mailbox does not silently create a new address association. Replies to another destination require independent mapping and discovery. Retain the evidence and policy decision separately from immutable account identifiers.

:::

## Using the optional admission package

An advertisement may carry one package for inviting this device into an MLS conversation. Publishing that package in email does not reserve it for one inviter: another recipient or forwarded copy can race to use it. The joining device must accept and consume it under the admission rules.

If another valid invitation has already consumed the package, the failed inviter waits for fresh material through a human message or an authorized service. Receiving the advertisement does not start a “send more keys” email exchange.

::: {.details summary="Package validation, single-use admission and other devices"}

### MLS admission material

Decode the package as the selected MLS protocol's exact wire representation, rejecting trailing data and other message types. Validate MLS version1, suite0x0001, package signature, lifetime, required extension capabilities and BasicCredential. Credential principal/device must equal the assertion; the leaf signing key must equal the accepted binding. Check current receive authority independently. Compute the package reference using MLS's own prescribed construction, not an invented JSON digest.

A package carried in ordinary mail is public reusable distribution of single-use admission material, not an atomic exclusive allocation. Another recipient or a forwarded copy can race an invitation. The inviting client records use locally, but the joining device must atomically validate and accept one authorized admission and consume the package with group installation. Invalid Welcomes cannot burn the package. Another otherwise valid admission using consumed material fails; the failed inviter must wait for fresh material through a human message or separately authorized service. No automatic “send more keys” email is generated.

This assertion covers one device. Other account devices require their own authenticated receiving capability/admission evidence or a future delegated aggregate format. An account-level encryption plan still obeys its authorized device-target policy. Missing evidence for required devices leaves that plan pending rather than assuming every roster device supports MLS.

:::

## Repeated and changing advertisements

Delivering the same advertisement again does not renew it. A stored validation result is checked against current time and identity state before use. Two authenticated assertions that reuse the same record identity with different bytes are a conflict; an unauthenticated imitation cannot disable established authority.

This version has no last-writer-wins rule. An empty feature list, a missing attachment or an expired assertion is not permission to weaken protection. The lifecycle rules below specify how advertisements coexist and become stale.

::: {.details summary="Duplicate, collision and withdrawal rules"}

### Duplicate, conflict and removal handling

Index exact assertion bytes by SHA256 and authenticated `(principal, device, record)`. Repeat bytes return the stored validation outcome without resetting lifetime, allocating another package or sending a response. Revalidate use against current state/time; a formerly usable stored result is not permanent authorization. Two different authenticated assertions under the same key are a record collision; hold the disputed advertisement use, preserve both and retain independent identity evidence. An unauthenticated collision does not disable established authority.

Version0 deliberately has no last-writer-wins sequence. Distinct valid advertisements may coexist for the same current device/binding; each proves only its own positive features during its interval. Empty features, an absent attachment or expiry do not withdraw another assertion or relax protection. Immediate withdrawal requires an authorized identity change making prior state-bound assertions stale; feature-only withdrawal needs a future separately authenticated ordering contract. Once a new head is accepted, replay cannot restore an older head or its advertisement usability.

:::

## Implementation status

The standalone carrier, signature and package experiments check separate boundaries. The [client-only onboarding flow](evidence/README.md#client-only-ordinary-mail-onboarding) joins ordinary-mail evidence, durable mailbox association, signed invitation admission and protected replies between fresh endpoint stores. Its unverified-continuity policy does not independently prove mailbox ownership. Transactional admission, package races and restart have local tests; observed legacy-client display, deployed providers and independent implementations remain unverified.

::: {.details summary="Required acceptance cases and remaining integration work"}

### Acceptance work

Required focused tests: round-trip exact signed bytes through MIME re-encoding; legacy attachment display; duplicate/multiple parts; nested forwarded discovery ignored; strict inner/wrapper parsing and bounds; signature and purpose substitution; stripped evidence; forged From; ambiguous genesis; mailbox/principal substitution; unsupported mailbox spelling; role misuse; expiry under uncertain time; delayed old state; state advancement invalidating cached assertions; exact retries and authorized collisions; foreign-device KeyPackages; consumed package races and restart; no SMTP/HTTP activity caused by receiving any fixture.

The local experiments include durable mailbox-association selection, atomic signed invitation admission and retained submission/retry state. Remaining work includes media-type registration and an interoperability agreement, deployed first-contact acquisition, complete account/device inventory discovery, independently validated ownership, live-state restore and rollback assurance, deployment resource-exhaustion evaluation, and real legacy-client/provider delivery observations. The already specified application-context and required-capability extension uses an experimental private-use identifier and still needs its interoperability agreement. This draft does not solve those prerequisites by advertising a feature token.

:::

::: {.details summary="What the MIME extraction experiment establishes"}

### Carrier experiment

The [local MIME extractor](evidence/README.md#passive-discovery-carrier) checks direct-child placement, duplicate candidates, unambiguous headers, transfer encoding and bounds. It returns original decoded candidate bytes only. It does not authenticate the assertion or sender, install identity state, parse an MLS package or generate network traffic. The extractor itself supplies no end-to-end bootstrap; the separate invitation flows integrate signed evidence and atomic admission under their stated local trust assumptions.

:::

### Signature and current-device experiment

The [signature and identity experiment](evidence/README.md#passive-discovery-signature-and-identity-check) verifies the assertion’s Ed25519 signature and compares its device, receive role, state and binding against an already accepted identity-store snapshot. It does not install the enclosed identity bundle, establish a mailbox association or validate a KeyPackage. Its result expires as authorization evidence when relevant state changes; the standalone check does not itself commit delivery or admission. The invitation flows separately recheck these dependencies inside their admission and release boundaries.


### Joined package check

The [joined discovery experiment](evidence/README.md#joined-passive-discovery-and-mls-package-experiment) uses one real device key for the accepted identity, signed advertisement and MLS package. It rejects a substituted package and a modified assertion. Identity acceptance remains explicitly unverified, and the checks use separate snapshots. This isolated check does not establish mailbox ownership, single-use admission or permission to send after identity state changes. The later invitation and sender-release experiments add package-consumption and current-authority checks; they do not supply independently verified mailbox ownership.

## Signed ordering exchange support

Assertion7 selects the existing context7/envelope3/rich-MIME application tuple and adds the required exact member `orderingExchanges:[{format:"quorum-exchange-experiment",version:"1"}]`. Its signature uses the fixed `email-next/passive-discovery/v7` domain. Unknown, additional or differently versioned exchange claims are rejected by this experimental schema. Older assertion versions remain unchanged.

Initial invitation7/roster4 and established invitation7 require this assertion from every admitted device. The selection includes reception of final carrier2; it does not make every device a witness. Current witness authorization still comes from the certified ordering policy. Complete current witness assertions accompany exchange1 and final carrier2, independently of Add-package assertions. See [ordering exchanges](ordering-exchange.md) for exact coverage, immutable delivery dependencies and compatibility with configured version0.


## Combined suite binding

The separately versioned [required conversation suite](suite-profile.md) defines its new assertion, context, invitation, ordering-wrapper and payload selections. It does not change any older version defined here. Its design is specified separately from implementation and acceptance evidence.
