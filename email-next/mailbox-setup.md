---
title: Setting up through ordinary email
order: 7.17
blurb: first-message encryption · existing accounts · bounded automatic replies
sectionNav: true
---

# Setting up through ordinary email

Two compatible clients can arrange encryption through their existing mailboxes before sending the first human message. The sender transmits a small setup request containing public device information. An enabled recipient client returns its setup information encrypted to that device. The sender validates the response, establishes the protected conversation and releases the writing only after the normal protected-send checks pass.

> [!ex] Alice writes; the clients handle setup
> Alice writes to Bob and presses Send. Her writing stays on her device. A separate setup email reaches Bob’s existing mailbox. Bob’s compatible client checks it and his response policy, then returns encrypted setup information. Alice’s client establishes the conversation and sends her encrypted message. Neither person has to compose a handshake reply.
>
> If Bob uses an older client, he may see a short setup notice instead. Alice’s writing remains private while her client explains that setup has not completed.

The original optional carrier `mailbox-setup-v0` and its [reply-aware version1 binding](#set-up-the-declared-reply-policy) are part of the same Email/2 specification. Encryption clients SHOULD implement the carrier version required by each protected agreement they advertise, alongside passive discovery; enabling automatic requests and enabling responses are separate, visible, revocable local policies. Provider-assisted [automatic setup](bootstrap.md) remains preferable when available because it avoids mailbox control traffic and supports separately authorized offline publication. For current setup3, ordinary mailbox setup can use authenticated account retrieval and locally verified request authentication. A trusted receiving service can instead supply direct-delivery evidence. Submission, retrieval and the selected receive-authorization checks must all be usable.

The selected opaque application carrier uses [mailbox-setup-v3](#set-up-the-opaque-application-carrier) when this capability is offered. It binds original assertion10 and signed carrier support to the exact pending attempt. Setup0/1/2 retain their original meanings and cannot complete a version3 attempt. Automatic setup and actual joined implementation remain separate policy and acceptance obligations.

## Choose an allowed path

When ordinary disclosure is actually authorized, a real message can instead carry the separate [automatic-upgrade invitation](automatic-upgrade.md). Its durable invitation, receiving offer and terminal confirmation all travel as email attachments. They do not widen this chapter’s content-free carrier, extend its 600-second active request or authorize fallback from a protected send.

A local send intent to a selected recipient authorizes the client to consider setup. It does not authorize address-book scanning, an email’s requested callback, or disclosure of the draft. Use valid cached evidence first, then an authorized provider path or this enabled carrier. An implementation chooses one active acquisition path per send attempt; switching paths closes or records the earlier attempt, keeps its uncertainty and starts separately authorized work rather than racing two package allocations or sending duplicate content.

The initial request exposes its addressing and the initiating device’s public identity/capabilities to mail infrastructure. It contains no human subject, body, attachment, quotation or digest of that writing. It cannot satisfy a policy requiring concealed personal addresses during setup. Such a policy uses a suitable existing private path or holds the send; it is never silently weakened to try this carrier.

A recipient may allow compatible setup from domain-authenticated senders, restrict it to remembered contacts, or require local approval. That disclosure policy is separate from the sender’s `allow-unverified` or `require-verification` identity-association policy. No message can enable either policy. An unsolicited request naming another principal cannot replace an existing association or suspend it merely by arriving.

## Send one content-free request

The client sends one setup request and keeps your writing private. Retrying that request does not create another handshake or restart its timer.

::: {.details summary="Request preparation, mail placement and signed records"}

Before submission, durably retain the local send intent, selected mailbox/account, request and nonce, original signed bytes, original deadline, exact initiating assertion and control-key custody, policy/association generations and outbox identity. Select a fresh dedicated control key for this attempt. Its publication and receiving deadlines equal the request deadline; it carries no MLS package. This temporary assertion does not replace a separately published ordinary receiving assertion. The [setup handoff](first-contact-setup.md#finish-setup-for-one-intended-send) requires the creator to select its separate ordinary receiving assertion for the actual roster. Its lifetime is at most the existing [600-second setup bound](setup-secret-retirement.md#fixed-deadlines-including-unused-setup), and may be shorter.

Retain the request as one immutable mail submission. A transport retry preserves its signed bytes and original Message-ID; SMTP uncertainty is not permission to allocate another request or extend the deadline. Account submission authority and the final pre-DATA checks remain required. The sender’s ordinary address is the actual source mailbox; account login and a device signature are distinct authorities.

### Exact request carrier

The outer message is one `multipart/mixed` with exactly two direct children: a `text/plain; charset=utf-8` notice, then one `application/vnd.threadlabs.mail-setup+json` attachment without media parameters. The notice is exactly `A compatible email app has requested encryption setup.` followed by CRLF. The attachment uses canonical MIME base64, `Content-Disposition: attachment; filename="mail-setup.json"`, and the strict wrapper below. Normal MIME-Version is exactly 1.0. Reject duplicate singleton headers, extra parts, ambiguous MIME, nesting and invalid transfer encoding for automatic processing. Preserve the original for inspection; do not search forwards or quoted material for a request.

Emit Subject `Secure email setup` and exactly one `Auto-Submitted: auto-generated`, one Message-ID, one From mailbox equal to signed `source`, and one To mailbox equal to signed `target`. Normal Date and transport-added trace fields retain their usual meanings. There is no Cc, Bcc, Sender, Reply-To, Resent-* field, List-* field, receipt request or external resource. These omissions are required before automatic response. Exactly one recipient is selected in the SMTP envelope; its reverse-path is the source mailbox, not null. Request NOTIFY=NEVER when DSN is supported. The trusted-delivery response path requires the actual delivered account and authoritative envelope reverse-path. Current setup3 can separately select the client-mailbox authorization defined below. Copied header text cannot establish envelope facts for either path.

The candidate media type is unregistered. Agreed draft experiments may use it; a filename or media label establishes no authority. The signed purpose selects only this protocol, never a human message or a provider operation. Maximum transfer-decoded wrapper is 4,194,304 octets, each original payload 262,144, advertisement wrapper 1,048,576 and JSON container depth 32. Bound total carrier/header work before decoding; a smaller local budget yields an explicit processing limitation without accepting a prefix.

### Wrapper and signature

Request and decrypted response wrappers have exactly three fields:

| Field | Required value |
| --- | --- |
| `payload` | Canonical padded standard base64 of original strict UTF-8 JSON payload bytes |
| `signature` | 128 lowercase hexadecimal characters, an Ed25519 signature |
| `advertisement` | Canonical padded standard base64 of one original assertion8 discovery wrapper, including its identity evidence |

Apply the existing strict JSON and canonical base64 rules. Wrapper and payload have no numbers, null, duplicate decoded names, unknown fields or trailing data. The encoded advertisement retains assertion8’s own exact null exceptions. The signature is over ASCII `mail/setup-request/v0` or `mail/setup-response/v0`, NUL, U32 big-endian original payload length and those exact bytes. Verify with the advertised device’s current authorized binding key. Original assertion8 signatures, identity validation, native package checks and current `receive` authority are independently required; this wrapper cannot replace them.

Both payloads have the following fields; the response alone additionally requires `requestDigest`.

| Field | Required value |
| --- | --- |
| `version` | String `0` |
| `purpose` | Exactly `mailbox-setup-request` or `mailbox-setup-response`, matching the selected route/kind |
| `request` | Initiator-generated nonzero ObjectId, retained unchanged in the response |
| `nonce` | 64 lowercase hexadecimal characters from 32 cryptographically random octets, echoed unchanged |
| `source`, `target` | Distinct canonical mailbox strings: initiating mailbox and intended receiving mailbox, unchanged in the response |
| `assertion` | SHA256 of the original advertisement-wrapper bytes,64 lowercase hexadecimal characters |
| `notBefore`, `notAfter` | Canonical uint64-string epoch seconds with `notBefore <= notAfter`; full credible creation/use time must fit |
| `requestDigest` (response only) | SHA256 of the original signed request payload bytes, not a reserialization or the surrounding mail |

A request’s assertion mailbox equals `source`; it has no MLS package, `keyPackageReceiveUntil:null`, and a nonnull fresh dedicated control key. Its signed assertion interval covers the whole request interval; its control-key `notAfter` and `receiveUntil` both equal the request’s `notAfter`. The response assertion mailbox equals `target`, and supplies an independently valid unused MLS package and nonnull control key under the current suite. Response creation bounds fit the original request, the response assertion and both current device-authority intervals. The responder retains original publication/receiving promises; the request cannot extend them.

Request identity is `(initiating principal, initiating device, request)`. Response identity is `(initiating principal, initiating device, request, responding principal, responding device)`. Authenticated unequal bytes under one identity are a conflict. Invalid or unauthenticated variants cannot create conflict tombstones. No arrival order, fresh envelope or new signature refreshes a retained request’s deadline.

:::

## Decide whether to answer

An enabled client answers a valid request addressed to its selected mailbox after checking authentication and the person’s disclosure policy. Current setup3 supports a client reading an ordinary mailbox, as well as a trusted receiving-service adapter. Neither path independently verifies the sender’s personal identity.

::: {.details summary="Receive authentication, response reservation and multiple devices"}

**Trusted delivery.** This path retains the direct-delivery contract for every selected carrier version. The receiving client first checks direct delivery to its selected local mailbox, with the exact carrier and singleton source/target headers above. The sole From, trusted envelope reverse-path and signed source must match canonically; the sole To, actual delivered mailbox and signed target must also match. Forwarding, list expansion and aliases without independently authorized exact mailbox selection cannot supply that proof. Do not infer address equivalence from plus tags, domain alignment or case folding.

Automatic response also requires a current trusted DKIM verification for signing domain exactly equal to the source domain. It must cover the complete body without an `l=` body-length tag, and the actual sole From field under the [existing coverage rules](security.md#domain-signatures-and-algorithm-policy). A client can perform that verification, or use a configured trusted receive producer that supplies those exact coverage facts. Other outer headers still obey the exact carrier checks; they need not all be included in the provider’s DKIM header list. The device-signed source, target, purpose and nonce bind the security-critical setup data. An altered Message-ID cannot create a new request identity, and an altered To cannot override the signed target or independently selected local mailbox. A downloaded `Authentication-Results: dkim=pass` string is insufficient. SPF alone, relaxed alignment, a self-signed device claim or a copied verification result cannot satisfy this gate. Missing required DKIM coverage holds either path. Missing envelope evidence holds the trusted-delivery path; local approval cannot supply that evidence. A current setup3 client can use the separately configured client-mailbox path below. Failure of a trusted-delivery check cannot select that other path.

DKIM supplies a domain accountability signal, not proof of the source mailbox local part or an independently verified human. The request still follows current identity/pin/conflict and disclosure policy. A domain operator or compromised sending account may generate abusive valid requests. Enforce finite configured per-source-domain, source-address, principal/device, target-account and total-work budgets before expensive processing and before outbound work. Shared account services coordinate their budgets where available; per-device controls do not claim to prevent aggregate abuse from many devices or domains.

### Client-mailbox authorization for setup3

With this path, Bob connects his existing account to an Email/2 client. The client checks the signed request and its domain signature, then sends one encrypted setup response to the signed source address. The mail provider continues normal SMTP and IMAP service.

Select this local receive-authorization policy before processing a request. It is available only for setup3; versions0,1 and2 retain their trusted-delivery rules. The setup3 wire records, signing domains and agreement stay unchanged. A request cannot select the receiver’s policy, and a failure under one policy cannot trigger another.

| Check | Required evidence |
| --- | --- |
| Local account and target | Exact original bytes acquired from the independently authorized account/source, with retained source generation, UIDVALIDITY, UID and digest. The locally selected eligible mailbox equals the signed target and sole To. Canonical aliases require independent exact authorization. |
| Source and request | Complete setup3 validation, sole From equal to signed source, independent current device signatures and exact-domain/full-body DKIM as above. The client verifies DKIM itself or uses a separately trusted exact-byte verifier. |
| Policy | Current response-disclosure and identity/pin policy, local spam/quarantine rules, eligible own receiving device and custody. Unknown or conflicting principals cannot displace an existing association. |
| Durable response | Original request identity/deadline, one responding-device allocation, one encrypted response identity and retained exact retry/uncertainty state. Moving or importing bytes supplies no new identity. |

Authenticated retrieval establishes where the client obtained the bytes. It does not establish the SMTP reverse-path or direct delivery. A Return-Path, Received or Authentication-Results field copied into those bytes supplies no missing authority. Store this authorization as client-mailbox evidence, separately from a trusted-delivery receipt; do not manufacture a producer grant or relabel unavailable ingress.

A still-current target-bound request obtained through forwarding or IMAP APPEND can satisfy this path when all checks above pass. That is an intentional authenticated-request replay, not evidence of direct delivery. An identical request imported under another UID, UIDVALIDITY or account source recovers its existing shared identity and outcome; it cannot allocate again, reset its deadline/budgets or automatically resend an already submitted/uncertain response. A different target, unapproved alias or unsigned/malformed variant cannot obtain that authority. Preserve independently trusted contradictory delivery evidence: known reverse-path/target mismatch, rejected direct-delivery provenance or a configured producer that has become unavailable cannot be bypassed by selecting client-mailbox processing for the same authenticated request. Retain that adverse evidence under the independently authorized target mailbox/responding principal, authenticated initiating principal/device/request identity and signed request-payload digest, with the complete trusted proof. Removing unsigned trace fields, changing the complete-message digest, moving/importing the request or reconnecting its account source cannot clear it. Only independently authenticated trusted-producer facts may establish this hold; an invalid request, copied trace header or unverifiable producer claim cannot poison the namespace.

This is domain accountability and unverified first-contact device evidence. A domain signer may sign an arbitrary same-domain From. The client therefore does not infer source-account ownership, independently verified contact status or permission to send human content from a request. Existing `require-verification`, known-pin, ambiguity and block checks still hold. The sender must validate the encrypted response and complete actual package/Initial admission before human content can be released.

Apply finite configured intake and response-work limits before expensive processing and outbound work. Client-mailbox response policy additionally sets a finite maximum complete response size and total outbound response octets per work window; charge the actual complete carrier, not just its JSON payload. An oversized response remains held without partial disclosure or a larger retry. Invalid requests cannot create authenticated conflict/deny records or charge authenticated request identities. Limits bound reflection; they do not prove individual source-account ownership or eliminate abuse by a domain operator. No request can raise those limits.

Before each allocation and final release, repeat the same selected account/source, exact original, request identity, authentication, policy, device and custody checks. Preserve applicable DKIM key/freshness policy and known revocation/conflict evidence. Missing or changed evidence holds the retained response. A more recent fetch, new signature, mode change or repeated approval cannot refresh its original request deadline or create a second response identity. A change to receive authorization invalidates unreleased old-mode work unless its owning policy explicitly revalidates the same retained result; it never supplies a fresh allocation or clears uncertainty.

Persist a validated request before preparing a response. Under a serialized current authority/policy check, reserve one response identity and one exact package publication/allocation for this responding device. Durably retain its signed response, original sealed ciphertext, deadline and outbox state before submission. A duplicate may recover that stored outcome; it must not allocate another package, create another signed response or automatically submit another outgoing email after an already submitted or uncertain result. A locally authorized retry uses the original bytes under the existing bounded transport policy.

Several authorized devices at Bob’s mailbox may each respond once. No unimplemented cross-client lock promises exactly one account-wide response. Each response names its actual device; Alice validates every intended recipient independently and selects a complete permitted device audience under the suite. Different initial principals remain ambiguous under the association rules. Devices cannot borrow each other’s response authorization, receipt state or admission package.

:::

## Encrypt the response, then establish the conversation

The response is encrypted to the device that made the request. After validating it, the sender’s client establishes the normal protected conversation. Setup success alone never means the human message has been sent.

::: {.details summary="Exact encrypted response and association checks"}

Use [sealed-control-v0](suite-profile.md#confidential-setup-and-control), exact kind `mailbox-setup-response`, with the original response wrapper as its body. The sender is the responding assertion’s device; the recipient and selected key are exactly the initiating assertion’s device and its dedicated control key. The sealed-intent signature uses the responder’s current `receive` authority and its interval fits the original request. It authorizes this setup response only, never application-message sending. Recheck disclosure policy and independently selected recipient/key before encryption and release.

Use the defined two-part sealed-control mail placement, Subject `Secure email setup`, Auto-Submitted `auto-replied`, From equal to target, To equal to source, no additional recipients/Reply-To/list/receipt fields, and a null SMTP reverse-path. When supported request NOTIFY=NEVER. The original request’s Message-ID is included as the sole In-Reply-To value for local explanation; it is not security correlation. This response is never itself a request and elicits no automatic acknowledgment, error, key refresh or cancellation mail.

At the initiator, locate the exact locally retained pending attempt and control key. Fully decrypt and validate the capsule before interpreting the response. Match its recipient/key to the local attempt; then require exact request ID, original request digest, nonce, source/target, response-assertion digest and responder actor across the original response, assertion and sealed intent. Apply this version0 binding’s full assertion8/native package, identity, association, ambiguity and freshness rules; the retained version1 binding separately requires original assertion9; current version2 requires original assertion10 under its own exact request/response binding. A valid HPKE tag or DKIM result alone cannot select a correspondent or establish a conversation.

For ordinary-mail association, retain the actual sole response From parse and original mail evidence; it must equal the target assertion mailbox. Keep the original request/capsule/response and receipt provenance as setup evidence, not a fabricated human-authored passive advertisement. A verification-required policy holds until independent evidence exists. An allow-unverified policy may establish continuity under the retained version0/1/2 rules; those exchanges do not defeat active first-contact identity substitution. Current setup3 additionally requires the recipient authentication below. That check still does not defeat a compromised source domain or establish a human identity.

Once enough valid recipient-device evidence exists, execute the existing suite selection, MLS invitation/admission, current-authority, secret-retirement and final-release algorithms. The request or response is not an MLS acknowledgment. Apply the [common setup handoff](first-contact-setup.md#finish-setup-for-one-intended-send). When protected delivery is durably ready and required setup-secret retirement has completed, atomically finish the applicable local setup stage and transfer its retained intent revision and eligible scoped copy into the protected outbox. Preserve the authorized copy plan: private copies have their own contribution identities and separate outcomes. Save each planned contribution once and use its existing outbox retry behavior; several setup responses cannot create an unplanned duplicate. A completed setup attempt’s later deadline cannot reopen it or cancel an independently authorized established conversation. The protected outbox still performs its own final current-authority and delivery checks. Readable history is not sent as part of setup.

:::

## Set up the declared reply policy

A message with an explicit reply policy needs devices that understand that policy. The setup request names the required agreement before any human writing leaves the sender's device. The response must match it. An older client's setup information cannot silently turn a private-only or no-replies message into an unrestricted discussion.

The reply-aware mailbox carrier is `mailbox-setup-v1`. It uses the same content-free request, direct-delivery authentication, disclosure policy, bounded automatic response, retry and cancellation rules as version0. A person with an older client may still see the same short notice. The sender retains the writing and chosen reply policy while unsupported setup remains unavailable.

::: {.details summary="Exact version1 records, response encryption and handoff"}

**Selection.** Version1 selects exactly [mail-conversation-v1](reply-intent.md#reply-aware-protected-agreement), assertion9/context9/envelope5/mime-suite-v1. Select it from the frozen local send intent before allocating an attempt. The earlier sections define version0 unless this section explicitly changes a field or binding. Version0 remains assertion8-only; its parsers, signatures and original records are not widened. A failed version1 check does not fall through to version0.

**Request and response.** The three-member wrapper is unchanged: `payload`, `signature`, `advertisement`. Advertisement contains the canonical padded base64 of one complete original assertion9 wrapper. The exact request payload has `version`, `purpose`, `agreement`, `request`, `nonce`, `source`, `target`, `assertion`, `notBefore` and `notAfter`. The exact response payload has those ten members plus `requestDigest`. Unknown, missing, duplicate or null members fail. Version is the string `"1"`; agreement is exactly `"mail-conversation-v1"`; purpose remains mailbox-setup-request or mailbox-setup-response as appropriate. All other identifier, address, digest, nonce, credible-time, byte/depth and original-wrapper commitment rules remain unchanged.

Sign original payload bytes with `mail/setup-request/v1` or `mail/setup-response/v1`, followed by NUL and the unchanged U32 big-endian length/original-byte framing. The assertion9 has its own independent `mail/passive-discovery/v9` signature and current identity/package checks. A signature under an older or opposite-purpose domain cannot satisfy this branch. Both the request and response independently bind the same exact agreement; a provider response or remembered capability cannot replace it.

**Request carriage and processing.** Keep the exact existing two-part setup MIME type, notice, filename, singleton headers and SMTP envelope restrictions. Decode only the bounded direct wrapper/payload, select its explicit version and purpose, and validate that complete branch before any response. A filename, content-type label or successfully parsed version grants no authority. The same trusted actual-envelope, complete-body/exact-domain DKIM, enabled response policy, current identity/association and abuse-budget checks apply. The request exposes only the setup metadata described above, never human writing or its content digest.

The initiating assertion9 is attempt-only, with no MLS package, null package receiving deadline and the fresh dedicated control key whose publication/receiving deadline equals the request's original deadline. The response assertion9 has an independently valid unused package and its own control key/receiving promise. The request interval remains at most600seconds under the existing bound. No new version, retry or publication resets a deadline or makes a consumed package reusable.

**Response carriage.** Select [sealed-control-v1](reply-intent.md#reply-aware-protected-agreement), exact kind mailbox-setup-response, only for a complete version1 response wrapper. This is the seventh allowed kind of that control profile. Sender, current receive-role authority and identity equal the responder in assertion9. Recipient and key equal the actual original attempt assertion9 device and dedicated key. Preserve the response's original bytes, source/target, agreement, nonce, request ID, requestDigest and original advertisement commitment across the sealed intent and local pending-attempt checks.

Use the same response mail headers, actual source/destination, generic subject, Auto-Submitted auto-replied, null reverse-path, no additional recipients and no response-to-response behavior. Its body uses the successor sealed magic, intent/signature/info domains and candidate mail-control media type. The initial request's Message-ID remains explanatory In-Reply-To only. Version0 sealed responses do not answer version1 requests, and version1 responses cannot activate version0 attempts.

**Durable identity and retries.** Keep the existing principal/device/request and responding-device response identities across both versions. Version/required agreement belong to the immutable retained attempt, not a new namespace that permits a second result for the same ID. Authenticated unequal variants retain conflict evidence; unauthenticated variants cannot poison it. Freeze the original intent revision, selected agreement, exact signed request/advertisement and attempt-key custody before submission. A repeated response neither allocates another package nor causes another human send. Switching acquisition paths preserves old uncertainty and needs its separately authorized attempt; it cannot silently change the agreement.

**Conversation handoff.** Independently select assertion9 for every intended conversation device, including a separate ordinary creator receiving assertion9. Do not promote the attempt-only control key into ordinary receiving authority. The actual context9 application is the common reply-aware tuple selected from all original device assertions, retaining the required reply-intent record even when optional interactions are absent. Use initial9/roster6 or established9, the selected successor ordinary/managed controls, sealed-control-v1 and mime-suite-v1 under their owning rules.

The [common handoff](first-contact-setup.md#finish-setup-for-one-intended-send) retains its complete current-authority, draft-revision, copy-plan, package-allocation, staged-checkpoint, secret-retirement and non-releasable-outbox transaction boundaries. Version1's typed evidence replaces only the old selected suite at those boundaries; it does not weaken them or give an old response permission to send the latest editor contents. Freeze the selected agreement and reply-intent record as dependencies of each scoped copy. A private copy has its own context and outcomes; neither setup nor success of another copy widens its audience. Before the first human body bytes are released, recheck the exact destination and source reply contract as well as account, identity, route, policy, membership and current credible time.

:::

## A fresh response can satisfy a stricter policy

The signed response can supply [live device confirmation](freshness.md#live-confirmation-through-existing-mailboxes) for its exact retained send attempt. Validate the complete original exchange and current target state, then apply the sender's original age bound. A successfully delivered email or cached advertisement alone does not qualify. Each intended device needs its own eligible response; retries do not restart the timer. This keeps stronger freshness possible over existing mailboxes without turning opening a message into a probe.

## Close attempts without sending more mail

| Event | Required behavior |
| --- | --- |
| Request or response invalid, spam-classified, unauthenticated, out of policy or over budget | No automatic reply or network callback; preserve bounded diagnostics without poisoning authenticated identities |
| Duplicate request | Recover the retained local outcome; no fresh response, package or automatic resubmission |
| Response, bounce, receipt or unrelated automatic email arrives | Never answer it through this protocol |
| Setup unavailable, legacy client or timeout | Keep the human writing private; explain the held state and offer only separately authorized alternatives |
| Request cancelled or deadline reached before completion | Stop future response preparation/content release, close this attempt and retire its dedicated secret under the existing lifecycle |
| A submitted control or human message has uncertain delivery | Keep its original outbox identity and uncertainty; neither cancellation nor timeout proves recall |
| Another device answers | Validate that device’s own evidence; never change an existing principal pin or infer support by every device |

The responder need not receive cancellation mail: its original finite request deadline bounds pending work. It retains any independently published receiving material under its own signed receiving promise; cancelling a request does not silently withdraw that promise. Retain consumed-package records, request/response identities, conflicts and original results through the owning validity/retention windows. Garbage collection cannot recreate authority or reset a timer. Restart reconciles stored work and credible time before any new release. Known restore/rollback disables uncertain local operational permissions until reconciled; it does not resend setup from absence.

::: {.details summary="Recover an interrupted response check"}

Bob sends two signed, unequal responses to the same setup request. If both are valid, a restart must not erase their conflict when a package expires.

An authenticated encrypted control may be durably staged before its setup response is accepted. Staging alone supplies neither a valid response nor a conflict. Recovery that derives a conflict from that staged input MUST:

1. Verify independently retained original receipt evidence, its credible observation interval, the complete original control signature and the exact pending-request correlation. Incoming bytes or a sender-stated time cannot establish earlier receipt.
2. Apply the complete owning response checks at that original observation interval: body, request, identity/account authority, binding, cryptographic native-package proof and original bounds. Use the retained carrier version's own contract. A control signature alone cannot make an invalid response trustworthy.
3. Compare only that fully validated original response with the retained outcome and install only the resulting negative fact. Preserve the original retention, uncertainty and retirement rules; expiry cannot erase a valid conflict or renew a deadline.

Missing or ambiguous provenance stays held. This historical check cannot accept a new response, acquire or consume a package, restore a retired secret, install native state or authorize content release. Those operations still require their independent current checks. Recovery does not reopen the retired setup key to decrypt the control again.

:::

A compatible client can classify accepted controls in its protocol activity view, while keeping them inspectable. Malformed or unsupported mail remains available as received mail. This protocol never tells a legacy client to discard a message, hides human writing inside a control, or marks a draft as sent before protected transport handoff.

## Why the automatic-response exception is narrow

[RFC3834 §2](https://www.rfc-editor.org/rfc/rfc3834.html#section-2) discourages answering automatic messages to avoid loops and abuse. This carrier deliberately permits one response identity per valid, enabled, independently authorized setup request and responding device. Terminal responses have a distinct sealed kind and cannot trigger another response. The request is `auto-generated`; the response is `auto-replied` under [§5.2](https://www.rfc-editor.org/rfc/rfc3834.html#section-5.2). Trusted delivery retains the original nonnull request reverse-path check. The current client-mailbox path is an explicitly requested setup service: [RFC3834 §4](https://www.rfc-editor.org/rfc/rfc3834.html#section-4) permits a precisely specified service responder to use a request-payload destination. That destination is exactly the signed source, never Reply-To or an arbitrary callback. Every response uses a null reverse-path. These choices limit reflection and loops without claiming to eliminate spam or prove personal identity.

[RFC3834 §2](https://www.rfc-editor.org/rfc/rfc3834.html#section-2) also recommends avoiding large service responses without assurance that the destination account holder authorized them. A client-mailbox request supplies a signed protocol request and domain accountability, but not that source-account assurance. A complete identity/package/carrier response can exceed a few kilobytes, so this path intentionally permits a larger response only within the receiver’s finite configured carrier-size and actual outbound-byte budgets. This avoids adding a prerequisite challenge round trip or provider extension. Clients SHOULD choose conservative limits for unknown correspondents. Domain-signed source impersonation and bounded reflection remain risks; do not label those limits as proof of account ownership or absence of amplification.

The stronger DKIM coverage requirement is this protocol’s automatic-disclosure gate. It builds on [RFC6376](https://www.rfc-editor.org/rfc/rfc6376.html) and the [trusted-result boundary](security.md#provider-configuration-and-boundary-processing), not a new use of DKIM as a mailbox-ownership certificate. Provider-assisted setup retains its separate domain/source authorization and avoids this ordinary-mail exception.

## Acceptance boundary

A complete positive test starts with no peer association or provider bootstrap service. Two enabled compatible clients use actual authenticated mailbox submission/retrieval, carry only setup metadata, automatically respond, validate the current suite, admit the intended devices and exchange the first encrypted human message. Repeat with multiple receiving devices and a strict verification hold. Inspect original outgoing MIME and server drafts for human content leakage; exercise legacy display separately.

Run the current positive journey with two clients and unchanged authenticated SMTP/IMAP providers, without a receive-producer extension. Record client-mailbox authorization and unavailable ingress separately. Also run the trusted-delivery journey under its own selected policy. Neither observation certifies the other.

Negative/restart tests cover copied authentication results; truncated DKIM coverage; forged/duplicate From/To/Auto-Submitted; absent or mismatched envelope facts on the trusted path; bypass attempts using the client path after a trusted rejection; exact valid APPEND/forwarding replays without a second allocation; wrong-account/target imports; same-domain signed source-account impersonation and its unverified-status limit; response byte-budget exhaustion; aliases, forwarding and lists; spam and exhausted budgets; wrong target, nonce, request digest, assertion, responder or control key; unknown kind; response-to-response loops; duplicate/concurrent receipt; lost control and human-send results; package races; policy/pin changes; cancellation; expiration/uncertain time; restart and restored journals. An isolated signature or HPKE test does not establish these mailbox, policy, persistence or complete encryption-journey behaviors.


## Set up an asynchronous delivery

A content-free ordinary email can obtain setup for an independently ready delivery. Bob's compatible client answers automatically; Alice can then prepare Bob's delivery while Carol remains pending. The human writing stays local until the delivery's own encryption, identity and disclosure checks pass.

This selects mailbox-setup-v2 for [mail-conversation-v2](suite-profile.md#asynchronous-protected-agreement). It uses the same enabled-request/response policies, direct-delivery authentication, abuse limits, generic notice and no-response-loop rules. Legacy clients may show the setup notice; the protocol does not ask them to silently discard it. Required address masking may make this carrier unsuitable; it cannot claim to hide personal addresses that its actual request exposes.

::: {.details summary="Exact setup2 payloads, encrypted response and retained attempt"}

Select the exact version from the frozen local required agreement before allocating an attempt. The wrapper has exactly payload/signature/advertisement, as in setup1. Advertisement is canonical padded base64 of one complete original assertion10 wrapper. Both payloads use version `"2"` and agreement `"mail-conversation-v2"`.

The request has exactly the first ten members below. The response additionally requires requestDigest. Unknown, missing, duplicate, null or wrongly typed members fail.

| Member | Required meaning |
| --- | --- |
| `version` | String `"2"`. |
| `purpose` | mailbox-setup-request or mailbox-setup-response, according to the record. |
| `agreement` | String `"mail-conversation-v2"`. |
| `request` | Original request ObjectId. |
| `nonce` | Original random challenge nonce, under the existing exact grammar. |
| `source` | Original initiating mailbox, unchanged in the response. |
| `target` | Original intended receiving mailbox, unchanged in the response. |
| `assertion` | SHA256 commitment to this wrapper's complete original advertisement bytes. |
| `notBefore` | Original interval start, a canonical uint64 decimal string. |
| `notAfter` | Original interval end, in the same time grammar. |
| `requestDigest` | Response only: SHA256 of the original signed request payload bytes; never the wrapper or a reserialization. |

Purpose remains mailbox-setup-request or mailbox-setup-response. Source/target canonical mailbox, request/nonce/digest, uint64 string times, credible intervals, exact-original advertisement commitment, strict JSON/member rules and byte/depth bounds retain setup1's meanings. No subject, writing, quotation, attachment, authored-message digest, intended-slot list or visible group roster enters these records.

Sign original payload bytes with `mail/setup-request/v2` or `mail/setup-response/v2`, NUL and the existing U32 big-endian length/original-byte framing. Independently verify the assertion10 under `mail/passive-discovery/v10` and its complete schema/identity/association rules. Both payloads bind the same original agreement. A valid older signature, relabeled assertion or provider status cannot satisfy setup2.

The initiating assertion10 is attempt-only: no MLS package, null package receiving deadline, fresh dedicated control key and original publication/receiving deadline equal to the request deadline. Its fixed readable offers are not ordinary ongoing creator receiving evidence. Response assertion10 has its own unused eligible package, independent control key and receiving promise. The request interval retains its existing maximum 600 seconds and all shorter authority/receiving bounds. Retries or another version do not renew it.

Request MIME structure/type/notice/filename, singleton headers, SMTP envelope and exact-domain/full-body DKIM/direct-delivery evidence are unchanged. Select the explicit bounded version/purpose before full branch validation; recognizing a media type or a filename grants no response authority. Current recipient opt-in/device policy, mailbox association and bounded response rules still apply before preparation.

Encrypt a complete setup2 response wrapper using sealed-control-v2, exact kind mailbox-setup-response. This is that sealed profile's seventh selected kind. Actual sender and current receive-role identity equal the response assertion10 device; recipient and key equal the original pending request's initiating device and dedicated key. Preserve exact original response bytes, request/requestDigest, source/target, agreement, nonce and advertisement commitment across the sealed intent and local attempt checks. Valid HPKE or DKIM alone cannot create an outstanding attempt or select a new identity.

Use the existing response headers, actual source/destination, generic subject, Auto-Submitted auto-replied, null reverse-path and no additional recipients. Request Message-ID is only explanatory In-Reply-To. The exact selected sealed magic/domains and parameter-free control media type apply. A response never triggers another automatic response. Setup0/1 responses cannot activate setup2 attempts, and setup2 cannot activate theirs.

Keep principal/device/request and responding-device outcome namespaces shared across versions; agreement/version belong to the immutable retained attempt. Authenticate before installing conflict facts. Duplicate exact requests/results retain their recorded outcome, package, original age and uncertainty. A version/path change cannot reset a block, budget, key promise, cancellation or consumed allocation. Switching paths needs its separately authorized attempt and preserves any previous uncertain submission.

A valid response can qualify for [live confirmation](freshness.md#freshness-for-asynchronous-deliveries) only for its exact retained attempt, current target head/binding and original age window. Ordinary receipt, offline publication and another device's response cannot do so. Retire attempt-only secrets under their existing schedule; their continued custody is not a substitute for a separate creator receiving assertion10.

Pass each qualified original assertion to the [per-delivery handoff](first-contact-setup.md#acquisition-for-independently-ready-deliveries). Required reply/private/no-replies semantics remain frozen in the authored record; capability discovery cannot change them. Actual native admission uses context10/initial10/roster7/established10 and the selected owning controls/carrier. Missing invitees remain pending rather than joining a fictitious native roster or blocking an otherwise eligible delivery.

:::

## Set up the opaque application carrier

When ordinary-mail setup is independently enabled, a content-free request can obtain the device's complete receiving bundle before releasing the human message. Its automatic response is encrypted. Legacy clients may show the request notice; this protocol cannot make it invisible or assume that every recipient allows automatic setup.

::: {.details summary="Exact setup3 request, response and pending attempt"}

Select mailbox-setup-v3 before allocating the immutable local attempt. Its strict wrapper is exactly `{payload,signature,receiving}`. Receiving is canonical padded base64 of the complete original receiving-bundle0. The request payload has exactly setup2's ten members with version3 and member **assertion** replaced by **receiving**. In that payload, receiving is SHA256 of the complete original bundle bytes, not the wrapper, nested advertisement or reserialization. The response additionally has original requestDigest, unchanged in meaning. Agreement remains mail-conversation-v2.

For both setup3 wrappers, the existing 1,048,576-octet decoded advertisement-wrapper ceiling applies to the **complete receiving-bundle0 bytes** in `receiving`, not only to an embedded advertisement. The 4,194,304-octet complete-wrapper ceiling, 262,144-octet original-payload ceiling and depth-32 ceiling remain; independently apply every nested record’s own bound. This receiving-field ceiling belongs to this mailbox carrier and does not impose a new limit on bundles acquired through another protocol.

All other original purpose, source/target canonical address, request ObjectId, nonce, credible interval, byte/depth and commitment rules remain. Sign original request/response payload with `mail/setup-request/v3` or `mail/setup-response/v3`, NUL, U32BE original length and original bytes. Validate each embedded original device signature and its exact current authority independently. Missing/unknown/duplicate/null/wrongly typed fields fail without activating an earlier attempt.

The initiating actual assertion10 is attempt-only: empty package, null package receiving deadline and fresh dedicated control key with the original request deadline. Its offer references that same original assertion and explicitly promises sealed-control-v3 for the key, with durable custody before request exposure. It is not ongoing creator receiving evidence or permission to import a package/native group. The responding bundle has actual eligible native admission material, its independent control key and a genuine carrier offer. Native handoff separately obtains the creator's ordinary complete receiving bundle.

Keep request MIME type/placement/notice/filename, singleton headers, submission envelope and exact-domain/full-body DKIM unchanged. Receive authorization is explicitly either the existing trusted-delivery path or [current client-mailbox authorization](#client-mailbox-authorization-for-setup3); preserve that selected provenance through intake, allocation and release. Both retain the bounded disclosure/abuse policy. Version/purpose selects3 before full validation; type/filename alone cannot request a response. Preserve the original maximum request interval and shorter authority/custody bounds. Another retry/path/version cannot extend it or restart a block/consumed allocation.

:::

::: {.details summary="Sealed3 response, privacy and loop prevention"}

Encrypt the complete original setup3 response wrapper through [sealed-control-v3](suite-profile.md#complete-application-carrier-selection), only kind mailbox-setup-response. All other control kinds retain their separately selected original versions. Actual sender is the response's authenticated current Receive-authorized device; recipient/key are exactly the initiating bundle/offer and its locally retained pending attempt. Require its explicit sealed3 promise and all original publication/receiving intervals before preparing/releasing a response.

At receipt, first validate complete selected sealed3 framing and retained own key/promise, then authenticate/decrypt under the existing HPKE owner. Validate the exact response/pending request, requestDigest, request/nonce, source/target, agreement, bundle digest, original signer and current identity/account association. A provider boolean, DKIM result or AEAD success cannot create an outstanding attempt. Failed3 never tries2/1/0 or installs another selected source.

### Authenticate the setup3 answer

Alice also checks who answered. A matching request ID and a decryptable response prove correlation with her request; they do not prove that Bob’s mailbox supplied the response. Before selecting a new responder identity or releasing human content, current setup3 requires one of these independent foundations:

| Foundation | Required check |
| --- | --- |
| Recipient continuity | An independently established eligible recipient association selected and retained **before this attempt**. The actual response signer continues that same principal under the existing current device/identity, verification and conflict rules. Its prior assurance level is preserved. |
| First-contact domain authentication | Live trusted DKIM for signing domain exactly equal to the pending attempt’s target domain, covering the complete response body without `l=` and the actual sole From. It binds the exact authorized-account original and selected pending attempt; the sole From equals that attempt’s target. |

Select the expected domain from the actual retained attempt, not an arbitrary incoming From. Preserve request, source/account generation, original bytes/digest and current configuration across asynchronous verification. A copied Authentication-Results field, a fresh self-asserted device history or a signature over the public initiating request cannot supply either foundation. Missing proof holds the response without installing a new association, choosing its package or releasing the writing; failure cannot activate an earlier carrier or plaintext fallback.

Capture recipient continuity as immutable local evidence before preparing the request. The response itself, another candidate processed alongside it or an association created during this attempt cannot create its own continuity exemption. Old retained records without that snapshot or an actual verified-domain receipt cannot be inferred to have one. Independently authorized user verification retains its own explicit flow.

For domain authentication, retain the actual verification receipt with its observed credible time, exact original/target/attempt binding and original freshness/expiry limits. Perform initial verification while those limits permit it. Revalidation and first native handoff preserve that receipt and the same authenticated principal; altered or missing provenance holds the work. Do not relabel the receipt as a fresh DNS lookup or refresh the request deadline. Once acquisition has been accepted and the peer is established, its original domain receipt remains historical evidence while the ordinary current identity/pin/verification and native-admission rules govern later delivery. Routine DKIM key rotation or an elapsed DNS cache TTL does not turn an established encrypted conversation into plaintext or require its retired attempt key again. Known identity revocation/conflict and stricter independent verification policy retain their normal holds.

This additional check closes substitution by an observer who knows a public request but cannot authenticate mail for the target domain and has no prior selected recipient key. A domain operator or same-domain signer may still impersonate a local part; the resulting first contact remains unverified as a person/account holder. Earlier retained unverified history is not retroactively domain-verified.

Use unchanged automatic response headers, null reverse-path, generic subject, exact intended destination and no extra recipients. Original request Message-ID remains explanatory In-Reply-To only. No human writing, authored digest, group roster or clear support proof accompanies the sealed response. A response never causes another response; invalid requests do not erase previous identity or valid pending work.

This request still exposes the personal addressing/setup metadata its actual ordinary carrier contains. Required Identity Protection or an opaque route can make it unsuitable; hold and use an independently permitted private path. Never add a real-address-bearing sibling to a masked opaque copy. Retire attempt-only secrets under their original schedule; expiry, cancellation, consumed/unknown results and restored-store holds keep their owning semantics.

:::
