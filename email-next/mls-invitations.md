---
title: Invitations to protected conversations
order: 8.5
blurb: ordinary mail carriage · encrypted membership tree · atomic admission
sectionNav: true
---

# Invitations to protected conversations

A compatible client can invite another device into a new protected conversation through ordinary email. The receiving client verifies the invitation, device identities and MLS Welcome before joining. Reading or forwarding the email does not accept it.

> [!ex] An invitation reaches two clients
> Bob opens the email in an ordinary client and sees a short notice. His upgraded client can inspect the attached invitation and join if its identity and local policy checks succeed. The notice itself neither enrolls a device nor proves that Bob has joined.

> [!note] Experimental creation profiles
> Versions 0–2 start with two devices. The version-3 roster below starts with an explicitly selected set of devices and accounts. Established-group invitations use a separate membership decision. These carriers remain experimental and their media types are unregistered.

The [security profile](security-profile.md) owns device credentials, package validity and authenticated conversation context. [Group conversations](group-conversations.md) owns membership authority; [transport](transport.md) owns release and retry. This chapter supplies the proposed initial-invitation carrier without replacing those rules.

## New-conversation boundary

The version-0 carrier starts a conversation between two devices: the creator's and the invited recipient's. It cannot add someone to an existing conversation or enroll another device for an account. Those operations need their own membership authorization.

A conflicting invitation cannot replace an already accepted conversation merely because it arrives later.

::: {.details summary="Initial group, administrator and epoch constraints"}

The creator must be the sole member and administrator before its initial admission commit. The proposed supported transition adds exactly the named target device; no removals, updates, external join, PSK, resumption, branching, reinitialization or simultaneous additions are supported. The resulting epoch is 1. Its roster has exactly the creator and target account/device/key pairs, with no additional participant inferred from missing information. The authenticated conversation context has exactly the selected existing schema, the named conversation, profile `mls-1-0001` and the creator principal as its sole administrator.

The creator durably accepts this initial local transition, stores its resulting group state and immutable invitation delivery, then applies the normal serialized release check. With no other pre-existing member, this narrow creation path has no distributed prior-epoch race to resolve. Once created, it does not authorize further membership changes. A receiver with an already accepted mapping of this conversation to another MLS group must hold the conflicting invitation; it cannot replace that mapping on arrival order.

:::

## Invitation data

The signed invitation names its creator, intended device and new conversation. Its proof is separate from the MLS checks: both must succeed.

::: {.details summary="Exact object schema and signature"}

Use strict UTF-8 JSON under the event encoding rules: unique decoded member names, strings instead of JSON numbers, no unknown members, bounded input/depth, original bytes retained. This is a control object, not an application contribution or answer.

Outer wrapper has exactly `{payload,signature,identity}`. Payload is canonical padded base64 of the signed record. Signature is 128 lowercase hexadecimal characters encoding Ed25519. Identity is the existing creator-principal identity proof bundle. No target secrets or TLS bearer tokens are carried. The identity bundle supplies candidates; it cannot reset a retained pin or establish mailbox ownership.

The version-0 signed payload has exactly these fields:

| Field | Required value |
|---|---|
| version | `0` |
| purpose | `mls-new-conversation-invitation` |
| invitation | Nonzero ObjectId generated once before preparation, stable on retry |
| profile | `mls-1-0001` |
| conversation | Nonzero existing conversation ObjectId |
| creator | Exact `{principal,device,state,binding}` |
| target | Exact `{principal,device,state,binding,mailbox}` |
| group | Canonical base64 of nonempty MLS GroupId bytes |
| epoch | Canonical uint64 string `1` |
| keyPackageRef | Canonical base64 of MLS's own KeyPackageRef bytes, never a JSON hash |
| notBefore, notAfter | Canonical unsigned-64 UTC-second strings, ordered |
| context | Canonical base64 of the exact existing conversation-context extension bytes |
| welcome | Canonical base64 of exact TLS-serialized MLSMessage with Welcome wire format |


Principal/device/digest spellings reuse the current identity profile. Target mailbox uses the passive discovery profile's narrow mailbox representation. It is a claimed intended routing destination, not ownership proof. GroupId and reference lengths are checked using the selected MLS decoder/profile; do not hard-code a guessed reference hash length. The decoded Welcome, including its encrypted GroupInfo/tree, has a proposed 1 MiB implementation ceiling; decoded signed payload at most 2 MiB, outer decoded wrapper at most 4 MiB, JSON depth at most 32, and MIME wire at most 6 MiB. These are editorial resource limits for this carrier, not MLS normative maxima. Check aggregate limits as well as per-field limits before allocation and cryptographic processing. These sizes deliberately differ from the ordinary 1 MiB event payload limit: this control object contains protocol state, not an event. A shared implementation must explicitly parameterize the decoder rather than silently bypassing bounds.

The signature input is ASCII `email-next/mls-new-conversation-invitation/v0`, one zero octet, four-octet unsigned big-endian signed payload length and exact payload bytes. Use the creator's independently accepted binding signing key, matching its MLS leaf key. This is an application signature, not a replacement for MLS signature labels, confirmation tags or tree validation. An equivalent reserialization changes signed bytes and is not an exact retry.

This profile requires the ratchet tree inside the encrypted GroupInfo's `ratchet_tree` extension in the Welcome. There is no external-tree JSON field, MIME sibling, cache URL or fallback tree source. Missing embedded tree is a rejected invitation. Unknown outer fields, including `tree` or `ratchetTree`, fail the exact schema. The receiver passes no external tree to the MLS library. This uses MLS's existing confidential tree distribution; it adds no encryption construction. The clear signed manifest still exposes its explicit creator, target, conversation/group identifiers and context, and does not claim metadata confidentiality. Later revisions may minimize that manifest independently.

:::

## Starting with an agreed application profile

Version `1` lets the same initial two-device invitation establish the application agreement needed for questions and answer buttons. Both devices must have independently signed support for the complete selected operation set. The invitation cannot combine one device's question support with another device's answer support and claim that both support the exchange.

> [!note] Explicit version boundary
> Version `0` keeps its existing schema, signature domain and context-version-0 behavior. Version `1` selects the exact context-version-2 profile below. Receiving an unknown version never enables a configured-context flag or weakens delivery policy.

::: {.details summary="Version-1 schema, proof references and acceptance"}

### Exact signed references

The version-1 wrapper has exactly `payload`, `signature`, `identity` and `applicationAssertions`. The first three retain their existing encodings. The last is an array of exactly two existing [signed passive-discovery wrappers](passive-discovery.md), one for the creator device and one for the target, ordered by principal then device. Each assertion must use passive-discovery version `1`.

The signed invitation payload retains every version-0 field, changes `version` to `1`, and adds `applicationAssertions`. This field contains exactly two reference objects in the same order. Each has exactly `principal`, `device`, `digest` and `signature`: the device identity, lowercase SHA-256 of the original decoded assertion bytes, and its exact lowercase hexadecimal Ed25519 signature. The outer proof wrappers must match these references one-to-one and their state/binding must match the corresponding invitation participant. Missing, duplicate, changed or additional proofs are rejected.

The invitation signature domain is ASCII `email-next/mls-new-conversation-invitation/v1`, followed by a zero octet, four-octet unsigned big-endian payload length and exact payload bytes. The creator's independently accepted signing key must also match its authenticated MLS leaf key. A version-0 signature cannot authenticate this payload.

Reserializing a separately signed identity bundle in the outer proof transport does not change assertion identity. Changing assertion payload bytes or its signature does change the signed reference. Neither kind of bundle can reset a retained identity pin.

### Context and local authority

The exact context has version `2`, the named conversation and profile, the creator as sole administrator, the selected application object, and ordering exactly `{"kind":"fixed-roster-v0"}`. The application selects envelope version `1` and a nonempty sorted subset of `answer`, `message`, `question`, `reaction`, `reaction-withdraw`. Each device's current signed advertisement must support every selected operation and this ordering mode. Hosted observer support and designated-member ordering are not inferred from other local capabilities.

Both devices' identity heads, bindings and selected mailbox associations must already be accepted under local policy. The creator also needs current send authority. Locally selected mailbox generations and policy decisions are not supplied authoritatively by the received wrapper. Missing evidence holds admission without automatic fetching or mailbox selection.

The target assertion must contain the exact retained target KeyPackage. Validate its actual MLS lifetime across the invitation interval; do not infer that lifetime from the advertisement. Invitation expiry cannot extend either assertion, either binding or the target package. Existing aggregate carrier bounds still apply to the additional proof material.

### Atomic admission and retry

Require the existing embedded-tree-only Welcome checks, exact two-leaf roster, epoch `1`, selected context and named GroupInfo signer. Commit package consumption, checkpoint, initial membership episodes, immutable signed application evidence, established agreement and accepted invitation together. A failed check or precommit process exit consumes nothing.

Accepted replay compares the exact invitation payload and signature and requires the supplied assertions to match its retained signed references. A changed proof cannot poison the accepted invitation. An exact accepted retry may return its recorded result after advertisement expiry; new admission may not use expired evidence. Once established, agreement is not retroactively removed when its discovery advertisement expires.

:::

## Delivery through email

::: {.details summary="MIME layout and legacy behavior"}

Proposed unregistered media type: `application/vnd.email-next.mls-invitation+json`, no parameters. Top-level `multipart/mixed` has exactly two immediate children: first a `text/plain; charset=utf-8` notice, second the invitation object with `Content-Disposition: attachment` and canonical MIME base64. Use ordinary CRLF, header and MIME rules. No alternative copies of the invitation and no sibling resources, HTML control, executable URL, nested message activation or remote retrieval.

Readable notice states that this is a request to start a protected conversation, that a compatible configured client is needed to accept it, and that reading/replying to the notice does not join. It contains no history or application message requiring encryption. It must not say the recipient has joined, verified ownership or received a protected user message. Display names and claims in this unprotected notice remain unverified; the upgraded UI derives its actual invitation summary from verified payload and local identity records. No automatic reply, MDN or DSN is requested as an acceptance signal.

An upgraded selector inspects only this exact outer scope. Duplicate candidates, ambiguous singleton headers, malformed transfer encoding, unexpected layout, excessive size and forwarded/nested invitation objects cannot trigger admission. Preserve ordinary viewing/original source where safe. MIME transfer re-encoding may preserve the decoded wrapper; identity and collision comparisons use retained decoded payload/signature, not transport folding. A legacy client may show the JSON attachment; invisibility is not promised.

Submit one delivery to the independently selected target mailbox, scoped to this target device. No Bcc, alias expansion assumption, reply-all enrollment or shared multi-recipient invitation delivery. Another client using that mailbox may see the notice but cannot claim target authority. Only possession of the corresponding private package plus current accepted identity authority can permit admission. Forwarding cannot substitute another principal/device.

:::

## Accepting an invitation

A client checks who is inviting it, which device was invited and whether the resulting group matches that invitation. It saves successful admission and package consumption together. A failed check must not spend the package.

::: {.details summary="Validation order and atomic admission"}

1. Parse bounded direct-scope carrier and exact wrapper. Before expensive work, check that target and package reference plausibly name locally held material; this is a resource filter, not an identity decision. No missing evidence causes network fetching or machine email automatically.
2. Check for an already accepted exact invitation under `(creator principal, invitation ID)` and retained payload digest. An accepted replay fast path requires equality of both original signed payload octets and signature octets with the retained accepted pair. It returns the recorded outcome, including after expiry, without decrypting again. Equal payload with a different signature is not a replay: validate that signature independently before classifying it, and never report success for an invalid signature. Identity-bundle bytes and outer wrapper/MIME serialization are not part of invitation identity; reordering or retransmitting candidate identity evidence must not poison an accepted invitation. Any newly supplied identity evidence is separately validated under identity-state rules, never installed through the replay fast path. Different bytes under that key are only an authoritative collision after the incoming creator proof and authority have independently passed. Unauthenticated garbage cannot poison a valid record.
3. Resolve creator identity evidence against retained state and mailbox association policy. Validate signature, current state/binding, send authority and the explicit local policy allowing this creator to invite the target into a new conversation. Sender self-assertion, matching From, SMTP acceptance and merely naming itself administrator do not supply that policy. First-contact decisions remain explicit and may remain unverified. An unfamiliar or conflicted association stays pending; no default provider trust is introduced.
4. Resolve the local target's current identity state and receiving binding; require exact target identifiers/state/binding and local mailbox association. Check complete local clock-uncertainty interval inside invitation, binding and package validity. Invitation notAfter may not extend any of those signed lifetimes; this candidate additionally caps its own interval at the existing seven-day admission horizon. Expired mail needs a new authorized invitation and fresh material where required, never plaintext retry by implication.
5. In a disposable staging provider, exact-decode the Welcome with no trailing data and require its embedded ratchet-tree extension. Supply no external tree. Validate selected MLS version/suite, correct package reference/recipient secret selection, GroupInfo signature, confirmation tag, tree hash/parent hashes/leaf credentials and all library-required checks. Require the GroupInfo signer to be the named creator leaf; a merely valid signature from another roster member is insufficient for this creation profile. No external PSKs or unsupported extensions may be fetched/guessed. Validate the target leaf identity/key against the published package and accepted current binding.
6. Compare actual authenticated group ID, epoch, context extension, exactly two member credentials/keys and sole administrator with the signed invitation and local acceptance policy. All peer device bindings must be available and accepted. The target's own records supply its evidence; creator bundle supplies candidate creator evidence. No third participant is inferred from headers. No history keys or prior transcripts are imported.
7. Serialize current identity/policy recheck, package single-use decision, conversation→group conflict check, staged group installation and accepted-invitation record in one local transaction. Invalid or unauthorized input does not consume the package. Same accepted invitation returns the recorded outcome; a different admission using consumed material fails. Package reuse records survive restart and require restore reconciliation.

The received invitation's signature authenticates its creator's intent, not a transferable proof that every relevant party accepted a group change. Scope to initial two-device creation is essential. An ordinary email reply or reaction is never join confirmation. The first successfully validated protected application exchange may demonstrate functioning keys under the application profile; its precise UI claim must not exceed what was checked.

:::

## Sender release and retry

Prepare once and durably retain invitation ID, exact payload/signature pair and prepared wrapper, target mailbox/device, package reference, resulting group/epoch and authorization dependencies. Release only after the initial membership transition is accepted locally and the ordinary outbox release transaction rechecks current creator/target authority. SMTP uncertainty preserves the same delivery and invitation identity. A changed target, package, group, context or payload is a new separately authorized invitation, not a mutation under the old identifier.

A delayed invitation may arrive after a newer authorized account state or a competing invitation. It cannot roll back either identity or accepted conversation mapping. Abandonment does not make a previously published package reusable. Sender success means transport handoff only; it does not prove target acceptance or decryption.


## Privacy and protocol inheritance

The membership tree travels inside the encrypted Welcome GroupInfo using [RFC 9420 §12.4.3.3](https://www.rfc-editor.org/rfc/rfc9420.html#section-12.4.3.3). This avoids exposing a separate public tree attachment. The clear signed invitation still exposes its named participants, group/conversation identifiers and context. It does not promise confidential email metadata.

The application proof uses the existing identity signing key and exact-byte framing. It supplements MLS authorization checks; it does not replace MLS signatures, confirmation or tree validation. The [MLS audit](audits/mls.md) records inherited protocol behavior and the separate dependency boundaries.

## Media-type registration candidate

The invitation type is separate from the [contribution event type](media-type-registration.md): accepting an invitation installs protocol state rather than applying a conversation contribution. The following is an unsubmitted vendor-tree candidate. Its name is not reserved, and no registration authority or responsible contact is implied.

::: {.details summary="Registration template"}

| Field | Proposed value |
| --- | --- |
| Type name | application |
| Subtype name | vnd.email-next.mls-invitation+json |
| Required / optional parameters | None |
| Encoding considerations | Binary; a strict UTF-8 JSON wrapper, with MIME base64 supplied by this carrier |
| Security considerations | Untrusted input can request admission; signature, current identity, local policy, MLS validation and atomic single-use checks are required. Parsing or displaying the object cannot itself authorize joining. The clear manifest is not confidential. |
| Interoperability considerations | An explicit supported initial-invitation version, original signed bytes and the embedded-tree path are required. Unknown fields, parameters and unsupported versions cannot trigger admission. |
| Published specification | This chapter and its linked security/identity contracts; a stable public revision is required before submission |
| Applications | Experimental clients and acceptance tools; no deployed support claimed |
| Fragment identifiers | No additional semantics beyond applicable generic +json rules; fragments cannot authorize admission |
| Deprecated aliases / magic numbers / file extensions / Macintosh codes | None |
| Contact | Unassigned; nomination required before submission |
| Intended usage | LIMITED USE for agreed experiments |
| Restrictions | New-conversation creation only; not an event, arbitrary MLS packet or established-group invitation carrier |
| Author / change controller | To be nominated before submission; this draft makes no appointment |
| Provisional registration | Not requested; the RFC 6838 provisional mechanism does not apply to this vendor-tree candidate |

The [media registration audit](audits/media-registration.md) and [structured suffix audit](audits/structured-suffixes.md) supply the inherited registration rules. Submission also requires a stable specification, responsible contact and applicable review. The JSON suffix does not grant generic processors permission to execute this object's state changes.

:::

## Acceptance and remaining work

Acceptance cases must cover exact schema/signature and MIME round trips, duplicate headers or parts, forwarded invitation inertness, modified target/reference/context/Welcome, missing or conflicting identity evidence, wrong GroupInfo signer, extra members or administrators, missing embedded trees, expired invitations and packages, and invalid attempts leaving packages unconsumed. Durable cases include competing admissions, exact accepted replay after expiry, restart, process exit around commit and release after an identity change. Ordinary-client display requires a real-client observation.

The [initial invitation experiment](evidence/README.md#initial-invitation-carrier) implements the signed carrier, direct MIME selection, embedded-tree and signer checks, and atomic target installation in a configured single-group store. Its MIME generator uses synthetic addresses. The version-0 carrier does not implement the complete sender-release or mailbox-onboarding workflow. The version-1 flow below adds durable sending. Public onboarding, restore reconciliation, physical secret-erasure assurance and independent interoperability remain unfinished; the separate retention experiment covers logical retirement of known live checkpoint copies.

Established-group invitations need authenticated prior membership and administrator-transition evidence. The [established invitation flow](evidence/README.md#durable-established-welcome-delivery) uses a separate signed contract and accepted membership decision. This creation carrier cannot substitute for that evidence. A client must also have an explicit local invitation-acceptance policy; a valid signature does not settle human intent or mailbox ownership.


The [version-1 initial invitation experiment](evidence/README.md#version-1-initial-invitation-and-durable-submission) joins durable creator preparation, fixed ordinary-mail submission, signed application admission and a subsequent protected contribution. It remains a two-device fixed-roster implementation stage; established-group invitations, additional devices and independent implementations have their own acceptance requirements.

### Explicit payload and membership mode at creation

The experimental version-2 initial invitation selects the conversation mode when creating a new group. Its context-2 branch selects designated membership ordering using version-1 capability assertions. Its context-3 branch selects fixed or designated ordering and an explicit payload format using version-2 capability tuples. The recipient independently selects the expected exact context before admission. This does not convert an existing fixed-roster group or import its history into a new mode.

The [signed tuple invitation experiment](evidence/README.md#signed-payload-tuple-invitations) joins actual local SMTP admission, a protected MIME message, a membership addition and a separate established invitation to a third device. Every selected device must cover the exact application combination; signature validity alone cannot fill a missing payload capability. Current authority and package consumption remain independently enforced.

Version 2 retains its two-device schema. Version 3 below supplies a separate initial-roster contract; it does not reinterpret existing version-2 invitations. The separately negotiated [private-copy profile](private-copies.md) supplies private-recipient handling. Independent peer implementations remain required interoperability evidence.


## Starting with several devices

A new conversation can include your laptop and phone, another person's two devices, and a third participant. The creator selects the intended accounts **and** their device inventory before creating the group. An incoming capability advertisement cannot silently add another account or make an incomplete inventory complete.

Version 3 gives every joining device the same signed roster and MLS Welcome, together with a separate invitation naming that device's package and mailbox. All devices derive the same creation identifier from the exact signed roster. Each invitation has its own delivery outcome: one device's successful handoff does not cancel another device's temporary failure, and an uncertain handoff requires an explicit retry decision.

> [!ex] A phone joins later
> Alice creates a conversation containing six devices. One phone is offline while Alice adds another participant. Its client later receives the original invitation, joins the original epoch, and processes the retained membership updates in order. Sending those updates does not prove that the phone has processed them.

The full roster and capability-proof mailbox claims are visible to the invited participants. This profile does not hide Bcc membership or account-device relationships. A client must select a separate, explicitly authorized delivery plan when that disclosure is unacceptable; it must not silently place a hidden recipient in this group.

::: {.details summary="Version-3 roster, signatures and exact application branches"}

### One common signed roster

The outer wrapper has exactly `{payload,signature,identity,roster,applicationAssertions}`. `roster` has exactly `{payload,signature}`. Both payloads use canonical padded base64; both signatures use 128 lowercase hexadecimal characters. Original bytes are retained under the existing strict JSON and signature-framing rules.

The common payload has exactly `{version,purpose,creation,profile,conversation,creator,intendedPrincipals,group,epoch,context,applicationContextDigest,members,notBefore,notAfter,welcome,resultGroupContextDigest}`. Its version is `"0"`, purpose is `"mls-initial-roster"`, profile is `"mls-1-0001"`, and resulting epoch is `"1"`. The creator is `{principal,device,state,binding}`. `intendedPrincipals` is the sorted unique set of selected principals. The group, application context and Welcome are base64-encoded exact bytes. The two digests bind the exact application-context bytes and the full finalized MLS GroupContext bytes respectively; they are not interchangeable.

Members are sorted uniquely by principal and device. Every member has exactly `{kind,principal,device,signingKey,state,binding,assertion}`; a joiner additionally has `{keyPackageRef,keyPackageDigest}`. `assertion` is `{digest,signature}`, binding the exact independently signed capability payload and its signature. Exactly one member has kind `"creator"`; all others have kind `"joiner"`. Each joiner has a distinct package reference. The complete independently selected local inventory must match this list.

The targeted payload has exactly `{version,purpose,invitation,creation,rosterDigest,rosterSignature,creator,target,notBefore,notAfter}`. Its version is `"3"` and purpose is `"mls-new-conversation-invitation"`. `target` is exactly `{principal,device,mailbox,keyPackageRef}`. It must name a joiner in the common roster and that device's signed mailbox claim. The common and targeted validity intervals are identical. The full interval must fit every capability assertion, device binding and joining package.

The common signature domain is `email-next/mls-initial-roster/v0`; the targeted signature domain is `email-next/mls-new-conversation-invitation/v3`. Both use the existing domain, null separator, unsigned 32-bit payload length and exact payload signature framing. `rosterDigest` is SHA-256 of the exact common payload; `rosterSignature` must equal its exact signature.

### Shared creation identifier

The creation anchor is SHA-256 of `email-next/initial-roster-anchor/v0`, a null byte, an unsigned 64-bit big-endian common-payload length, the exact common payload, an unsigned 64-bit big-endian signature length of 64, and the exact 64 signature bytes. It does not depend on which targeted invitation arrives first.

### Application branches

Context 3 requires version-2 capability assertions and its exact selected application tuple. Context 4 requires version-3 assertions and the exact `mime-rich-v0` tuple. Each device must cover the selected envelope, payload, operations and ordering combination. The initial ordering is either fixed roster or designated membership with the creator device designated. The creator principal is the sole initial administrator. A mismatched context/assertion version is rejected; existing versions 0–2 keep their earlier schemas.

:::

::: {.details summary="Atomic installation, targeted delivery and delayed joining"}

### Installation

The creator commits the resulting MLS checkpoint, exact signed common roster, device agreements, initial membership periods, package reservations and every targeted immutable MIME message together. A repeated preparation returns those retained messages. No partially committed roster can be released.

A recipient independently authorizes the expected creator, principals, device inventory, context and local mailbox selections. It verifies every original capability proof and current key authority. Before consuming a package, it checks that the Welcome reference set matches the complete signed joiner set and that exactly one locally stored matching package is the named target. After joining, the actual signer, group, epoch, application context, finalized GroupContext and full roster must match. State installation, proof retention and package consumption commit together; a failed attempt leaves the package available. Exact accepted replay returns the retained result.

### Delayed delivery

Ordinary initial release holds when the group has advanced. The separate delayed-release path requires a retained catch-up plan connecting the signed original GroupContext to the current accepted tip. The target must remain continuously present under the same key and membership period. Current full-roster authority, original identity dependencies, original route generation and invitation expiry still apply.

The delayed release and ordinary release share one target's delivery history. They cannot bypass an earlier accepted or uncertain outcome by changing submission mode. The checked history tip and path are checked again before DATA; a new transition requires a new review of the retained plan. Catch-up retains exact accepted membership messages, and completing or cancelling its plan preserves the public messages and attempt evidence before releasing retention pins. Cancellation does not assert non-delivery.

:::

The local experiment exercises three principals with two devices each, separate target SMTP outcomes, atomic rollback and context-3 delayed admission followed by an actual retained Add. Context-4 creation also accepts the exact rich-body agreement. This is not a claim of automatic device discovery, hidden-recipient support, distributed writer failover or deployed interoperability. [Rich membership transitions](group-conversations.md#membership-in-rich-conversations) use a separate established-invitation contract.

## Protected presentation at admission

The [protected presentation profile](managed-presentation.md) uses initial invitation `5` and common roster `2` for exact context `6`, envelope `3` and signed assertion `5` support. It retains the preceding multi-device roster, target-specific package, exact signature-reference and admission transaction rules. It does not reinterpret an invitation from an older version.
