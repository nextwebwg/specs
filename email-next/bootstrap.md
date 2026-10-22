---
title: Automatic first-contact exchange
order: 10.28
blurb: authenticated requesting account · private control inbox · automatic device response
sectionNav: true
---

# Automatic first-contact exchange

The Auto setup module lets a client obtain a new recipient's public encryption setup before sending the human message. The requester proves an authorized sending account through its own provider. The recipient's provider accepts a content-free request, and an enabled device answers automatically—or the provider supplies eligible material that device published earlier.

The writing stays on the sending device. Nothing in this exchange contains its subject, body, quotations, attachments or a digest of those values. A successful exchange supplies candidates for the existing identity, association, capability and MLS admission checks; it does not itself authorize content release.

> [!ex] A setup request, then the message
> Alice presses Send to Bob. Her account provider activates a narrowly scoped setup permission for Bob's exact mailbox and service. Bob's service checks that permission and places the request in its separate control inbox. Bob's enabled client returns its signed setup without asking him to write a reply. Alice validates the result, establishes the encrypted conversation and only then submits her message.

This is the provider binding for [encrypting the first message](first-contact-setup.md), within the same Email/2 specification. It does not widen the [known-pair queue](provider-control.md) or grant it authority over unknown recipients. [Relay routes](relay-routes.md) can be established after the intended identities are available; they are not a prerequisite for a content-encrypted first message.

> [!note] Proposed contract; joined implementation remains required
> The [bootstrap component](evidence/README.md#automatic-first-contact-authorization) checks account/device proof scope, uniform pending admission and signed-response correlation using configured service facts. It does not implement public provider login, network discovery, complete assertion8/package validation or the full first-message journey. Those remain acceptance obligations.

The [current Encryption baseline](suite-profile.md#current-client-baseline) uses [bootstrap2](#automatic-setup-for-independently-ready-recipients) when this capability is offered. Retained version0/1 records remain exact for earlier acquisition. Version2 preserves shared account/family, source permission and package-allocation authority; it does not relabel old results or establish a complete implementation.

## Account proof, device proof and verification

The source provider must be delegated by the sender mailbox's domain and authenticate that mailbox as belonging to the signed-in account. A self-signature or an unrelated relay account is insufficient to assert that mailbox. A provider statement proves only that this provider authorized its account/device link; it does not independently identify the human or defeat a dishonest provider substituting the first identity.

The destination service must likewise be delegated by the requested recipient mailbox domain. It routes only to an opted-in account it controls. An independent relay can support this flow for its own account domain, or when the personal mailbox domain delegates this service. It cannot publish a descriptor for an unrelated address merely because it forwards mail.

Normal first-contact policy remains explicit: allow an unverified initial association, or require a selected independent verification mechanism. Provider-account authentication does not silently satisfy human comparison or mark a correspondent independently verified. Existing pins, ambiguous claims and continuity breaks retain their own outcomes.

## Who may ask for what

Authentication establishes which account, device or service is acting. Authorization limits what that actor may do. Email/2 checks both; a valid certificate, device signature or provider descriptor is not blanket permission.

| Actor | Required evidence | Permitted request | What it cannot obtain |
| --- | --- | --- | --- |
| Client managing its own account | Issuer-bound account login, limited OAuth scope and current account/device link | Prepare or withdraw its own source permission; manage its own receiving policy | Another account's management access |
| Sending device requesting first contact | Domain-delegated source service, live source-account approval and exact signed device permission | Request setup for the named recipient/service and conversation, within the original deadline | A mailbox directory, presence, message history or content |
| Initiating device retrieving the result | Original admitted permission, current source authority and a fresh signature proving initiating-key possession | Retrieve eligible setup for that exact exchange | Other exchanges, other recipients or account management |
| Recipient device answering | Its own linked receiving account, current device authority and enabled automatic-response policy | Publish or answer with its own signed setup; approve permitted route follow-up | Enroll another device, widen the sender's audience or release human content |
| Source or destination service | Delegation from its selected mailbox domain and validated peer evidence | Perform the bounded control operation under account and recipient policy | Substitute provider identity for independent correspondent verification |

The baseline is open to independently operated and self-hosted providers. It does not require membership in a central provider registry. A destination applies its own admission, abuse and recipient policies to authenticated requests; authenticating a new domain does not oblige it to disclose material. No operator may claim authority over unrelated mailbox domains. A dishonest provider can attest falsely about accounts it controls, so this authentication remains separate from independent verification of the first correspondent identity.

The underlying distinction is established prior art. [OAuth scopes](https://www.rfc-editor.org/rfc/rfc6749.html#section-3.3) limit delegated access. [OAuth mutual TLS](https://www.rfc-editor.org/rfc/rfc8705.html) authenticates clients and can bind tokens to their certificate. [XMPP server federation](https://www.rfc-editor.org/rfc/rfc6120.html#section-6) distinguishes authentication and authorization identities across domains. Email/2 reuses the account authorization machinery specified below and defines its own exact cross-provider setup permission. These precedents do not make an arbitrary OAuth token acceptable at another provider, and mutual TLS is not an additional baseline requirement here.

## Discover and connect

Fetch `https://<selected mailbox domain>/.well-known/mail-setup` using the [provider discovery](provider-discovery.md) transport, selected-domain validation, bounds, retained-publication/high-water rules and explicit purpose separation. The exact descriptor is:

| Field | Required value or meaning |
| --- | --- |
| `version` | Exactly `"0"`. |
| `purpose` | Exactly `bootstrap-service-discovery`. |
| `domain` | The selected mailbox domain, under the provider-discovery grammar. |
| `publication` | This publication identifier, under its owning grammar. |
| `generation` | The descriptor generation, under the shared discovery grammar. |
| `service` | The canonical HTTPS service origin. |
| `managementPrefix` | The same-origin prefix for own-account management. |
| `sourcePrefix` | The same-origin prefix for source-permission inspection. |
| `exchangePrefix` | The same-origin prefix for public exchanges. |
| `roles` | Nonempty, distinct, ASCII-sorted roles: `request-source`, `respond-target`, or both. |
| `notBefore` | Start of this record’s validity interval, as a canonical uint64 epoch-second string. |
| `notAfter` | End of this record’s original validity interval, in the same time grammar. |

Version is `"0"`, purpose `"bootstrap-service-discovery"`. Domain/publication/generation/service/time grammars are unchanged. The three canonical same-origin prefixes end in `/`. Their paths must not overlap. Roles is a nonempty ASCII-sorted distinct array from `request-source`, `respond-target`. Each role may be implemented independently. Names are experimental and remain subject to the [registration inventory](design-resolution.md).

For the person's own account only, reuse issuer-bound native registration, authorization-code/S256 PKCE, refresh/revocation and account-link challenge mechanics with bootstrap namespaces and scopes. `mail.setup.link` permits own-account/device linking; `mail.setup.request` permits own source-permission management; `mail.setup.respond` permits the linked device's own control-inbox/publication operations. Apply the [shared native connection binding](provider-discovery.md#reuse-sign-in-mechanics-without-sharing-permissions): exact shared callback forms, own-account module separation and exact selected scope set. Request only needed scopes; metadata must advertise them. Queue and relay tokens/links never become bootstrap authority. Account link and reset proofs bind this exact descriptor digest; the [account-link contract](provider-grants.md#account-linking) applies with this module's scope and namespace. The [shared-link subset](provider-grants.md#shared-account-links-separate-module-authority) fixes the inherited schemas, literal proof domains and module-local lookup/reset boundary. This service still needs delegation from each selected sender/recipient mailbox domain.

Discovering a recipient service never signs the sender into that service or forwards source account credentials. Its URLs cannot replace the sender's OAuth issuer. Changed origins require the existing reconnection decision; a descriptor alone cannot migrate a token or accepted identity.

## Create a content-free source permission

The client initiates only for a locally selected recipient under enabled automatic-setup policy. Do not probe an address book or trigger the flow from opening mail, HTML or a URL. The source provider derives the account/family/incarnation from its authenticated session, checks the exact sender mailbox against that account, and checks the linked device's current send/receive authority.

The source permission is signed by that device after checking the exact preparation. It binds the intended recipient mailbox/service, conversation identifier, random request nonce and original signed sender capability advertisement. Its fixed deadline is at most 600 seconds, also bounded by link/family/device/assertion validity. Retries never refresh it. The source provider activates it only after the approval and its account checks succeed.

A source permission is an invitation to perform this exact setup, not a bearer queue token or authority to send content. Copying it can replay only the same admitted request. Reading the result requires a valid inspection proof signed by the initiating device key, under the bounded replay rules below. The source provider exposes a live inspection operation to validate the original permission, not a public mailbox lookup.

## Admit a scoped request

The destination validates the source domain delegation, exact live permission bytes, signature, current source-account authorization and target mailbox/service before accepting a request identity. It applies finite issuer/account/peer/destination/work budgets and its source-admission policy. HTTPS proves control of an origin, not an honest operator or costly account creation.

For every valid source permission, `POST /exchanges` returns the same 202 shape with an opaque exchange handle and `pending`, whether the target mailbox exists, is disabled, has no opted-in devices or has no usable publication. Mailbox lookup and eligible recipient work are private asynchronous state. Invalid source authority can fail without consulting the mailbox. There is no public recipient-capability, existence, last-seen or presence endpoint.

Ordinary SMTP rejection and verification behavior can already disclose mailbox existence; [SMTP security guidance](https://www.rfc-editor.org/rfc/rfc5321.html#section-7.3) recognizes this disclosure problem. Automatic setup does not promise to conceal every fact already observable through email. Its restricted requests and uniform pending result avoid adding an unrestricted directory or detailed status interface. Successful opt-in disclosure necessarily reveals usable capability to that authorized requester. Uniform pending failures do not make enumeration by authenticated permitted senders impossible. Recipient opt-in, source-account/peer blocks, admission policy and finite budgets limit this privacy cost; do not describe them as zero-leakage or universal anti-harassment. A fresh device signature shows that a key answered, not that a person was online or read the request.

The provider places eligible work in a separate private control inbox, not an ordinary email message. Legacy clients need not discard, hide or automatically reply to anything. Account-level opt-in and each receiving device's response policy are both required. Incoming request fields cannot enable either policy or enroll a device.

## Answer automatically or use published material

An enabled recipient device validates the exact source scope, source evidence, its own account/mailbox binding and local response policy. A conflicted known identity is not repinned. Under this retained version0 binding it prepares one assertion8 and usable MLS admission package, signs one response bound to the original request digest/nonce, and durably stores the response/package allocation before upload. Exact retries return those original bytes; they do not generate another package or exchange.

An offline device may instead have explicitly published a signed automatic-first-contact record. It names its exact mailbox/service, current endpoint and original advertisement. Both account opt-in and that device publication policy must permit disclosure to the validated source. The provider cannot manufacture a fresh device signature from this publication. Label it `published`, not `challenge-response`, and preserve its original validity.

The provider atomically reserves a published package for one exchange before first disclosure. Exact exchange retries return the same allocation. Once disclosed, a package is never recycled into another exchange, even after cancellation. Provider allocation does not replace MLS validation and recipient single-use enforcement. Publication/KeyPackage secrets retain their own lifecycle and original deadline; the ten-minute request cannot extend or arbitrarily shorten the separately applicable admission lifetime. In-flight admission and retirement follow their owning contracts.

No response causes another response. An exchange cannot become a subscription, automatically enroll all mailbox devices, send a receipt, release history or call an arbitrary callback. A source permission does not authorize a new reply audience.

## Finish private routing in the same handshake

A recipient response or publication includes `relayDomain`: empty when no recipient-masking service is offered, otherwise the domain of that device's already connected receiving-relay account. This is a signed routing proposal, not ownership proof, an OAuth issuer to install or permission to contact an arbitrary URL. The sender validates that domain's relay descriptor under network/selection rules and later requires actual recipient route approval and live activation. The recipient device accepts follow-up only for its own configured relay account.

The initial request cannot name the recipient's principal before learning it. Therefore private routing has an explicit second stage, before human content: the sender validates returned setup, obtains its own [relay source permission](relay-routes.md) for that selected principal/conversation and sends a signed route request through this same bootstrap exchange. The recipient device automatically prepares/approves the alias with its connected relay under its enabled policy, then returns the route invitation. The sender independently validates the invitation and proves route-key possession to inspect its activation.

If setup is interrupted, resume the [same retained route operation](#resume-the-same-relay-operation) instead of requesting another alias. The sender still checks actual activation before sending.

No source permission is fabricated with a guessed recipient principal, and no alias is silently installed merely because it was returned. If masking is required, content waits for this stage. If remembered policy permits content encryption with public addresses, the client can use that permitted combination with an accurate indicator. A later route upgrade does not recall the earlier exposure.

::: {.details summary="Exact HTTP records and state transitions"}

### Common encoding and authorization

For bootstrap-specific records, use the [relay common wire restrictions](relay-routes.md#exact-records-signatures-and-http-behavior): strict string-valued UTF-8 JSON, original-byte retention, bounds, TLS 1.3, no redirects/0-RTT/ambient cookies, no-store, canonical same-origin paths and finite deployment budgets. Apply these processing bounds before creating authority:

| Input | Bound |
| --- | --- |
| Management body | 4194304 octets |
| One signed payload | 262144 octets |
| JSON nesting | 32 levels |
| Advertisement or identity evidence | Its independently tighter decoding bounds |

A request exceeding a bound cannot partially create authority. Times are canonical uint64 strings; ObjectIds nonzero 32-hex; source, exchange, nonce and digest values have 64 hexadecimal digits; endpoint references have the existing exact grammar. Mailboxes use the selected initial [address spelling](private-address-presentation.md#mailbox-spelling-and-compatibility).

The inherited [account-link/reset subset](provider-grants.md#shared-account-links-separate-module-authority) retains its exact provider-grant schema, including safe JSON integer timestamps. Select it only for those authenticated management routes, not as a fallback parser for an invalid bootstrap record.

A proof has exactly two fields:

| Field | Value |
| --- | --- |
| `payload` | Canonical padded base64 of the original payload bytes |
| `signature` | Ed25519 signature, encoded as 128 lowercase hexadecimal characters |

The field tables in this chapter list complete required member sets. Row order is for reading; signatures cover the original serialized bytes. Signature domain is `email2/bootstrap/<kind>/v0`, NUL, u32 big-endian payload length, then original bytes. Kinds are `source`, `inspect`, `cancel`, `response`, `publication`, `route-request`, `route-response`. Cross-kind signatures are invalid. Advertisement is canonical base64 of the original complete signed assertion8 wrapper, preserving the independent assertion payload/signature/identity bytes; it is not a feature boolean.

### Source operations

Under managementPrefix, `POST /sources/preparations` requires own request scope, an active linked device and authoritative mailbox membership. The request body has these required fields:

| Field | Required value or meaning |
| --- | --- |
| `version` | Exactly `"0"`. |
| `purpose` | Exactly `bootstrap-source-request`. |
| `request` | The request ObjectId. |
| `link` | The current own-account/device link. |
| `senderMailbox` | The exact sender mailbox authorized by the source account. |
| `sender` | The sending device’s exact endpoint reference. |
| `targetMailbox` | The exact selected recipient mailbox. |
| `targetService` | The recipient’s domain-delegated bootstrap service. |
| `conversation` | The conversation identifier for this setup attempt. |
| `advertisement` | Canonical base64 of the original complete signed assertion8 wrapper. |
| `nonce` | The original source request’s random 64-hex nonce. |
| `notBefore` | Start of this record’s validity interval, as a canonical uint64 epoch-second string. |
| `notAfter` | End of this record’s original validity interval, in the same time grammar. |

The service independently validates the full sender advertisement, mailbox/endpoint agreement, current state/binding/roles, time and selected target-domain delegation.

Its HTTP 200 response is the prepared payload:

| Field | Required value or meaning |
| --- | --- |
| `version` | Exactly `"0"`. |
| `purpose` | Exactly `bootstrap-source`. |
| `preparation` | The preparation ObjectId. |
| `request` | The request ObjectId. |
| `source` | The source permission’s random 64-hex identifier. |
| `issuer` | This source service’s canonical origin. |
| `delegation` | Digest of the source service’s exact descriptor. |
| `accountSource` | Stable opaque source-account abuse handle at this target service; not a personal account identifier. |
| `senderMailbox` | The exact sender mailbox authorized by the source account. |
| `sender` | The sending device’s exact endpoint reference. |
| `targetMailbox` | The exact selected recipient mailbox. |
| `targetService` | The recipient’s domain-delegated bootstrap service. |
| `conversation` | The conversation identifier for this setup attempt. |
| `advertisement` | Canonical base64 of the original complete signed assertion8 wrapper. |
| `nonce` | The original source request’s random 64-hex nonce. |
| `notBefore` | Start of this record’s validity interval, as a canonical uint64 epoch-second string. |
| `notAfter` | End of this record’s original validity interval, in the same time grammar. |

Purpose is `bootstrap-source`; preparation/request ObjectIds; source a service-generated random 64-hex permission identifier; issuer/delegation are this source service and exact descriptor digest. AccountSource is the same stable opaque source-account abuse handle at this target service used across relinks/resets; it never reveals the personal account identifier. Remaining intent fields are unchanged.

Offer the exact bounded interval before approval. `PUT /sources/preparations/{preparation}` body `{proof}` signs this exact preparation. Recheck current account/family/link, advertisement, descriptor, scope and interval under one transaction before activating. Return 201 on creation or 200 identical retry with exactly `{proof}`. Changed authenticated input under the account/family/request namespace is 409; invalid proofs cannot reserve a conflict.

`POST <sourcePrefix><source>/inspect` body `{proof}` presents that original source permission. It returns 200 `{proof}` only while the original permission, account/family/link and exact device authority remain active, with identical original payload/signature. It introduces no new mailbox information to a holder of that original proof. There is no credential-free GET/listing by mailbox or permission ID. A copy authorizes no new target or scope. Destination services perform a fresh selected-origin inspection, not cached liveness or a message-supplied arbitrary URL.

Own-account `DELETE /sources/{source}` under request scope withdraws the permission; unknown own IDs return 204. Disconnect, reset, expiry, descriptor invalidation or known loss of required authority stops new use. It does not recall already disclosed public material. Source inspection never changes the original deadline.

### Public exchange and source possession

Under exchangePrefix, `POST /exchanges` body is exactly `{source}` containing the signed source wrapper. After complete source validation, create or find the immutable exchange. Its handle is SHA256 of ASCII `email2/bootstrap/exchange/v0`, NUL, u32 big-endian byte length of issuer, UTF-8 issuer, then the 32 decoded source-ID bytes. Response is always 202 with exactly `{exchange,state}`, state `pending`. It reveals no private recipient queue status. Same source ID with different authenticated original bytes is 409 only after verifying live source authority; unauthenticated traffic cannot poison that identity.

`POST /exchanges/{exchange}/inspect` body `{proof}` uses the initiating device key. The signed inspection payload has these required fields:

| Field | Required value or meaning |
| --- | --- |
| `version` | Exactly `"0"`. |
| `purpose` | Exactly `bootstrap-inspect`. |
| `issuer` | This destination service’s origin. |
| `exchange` | The exact exchange handle. |
| `sourceDigest` | SHA256 of the original source payload. |
| `nonce` | A fresh random 64-hex nonce for this inspection request. |
| `notBefore` | Start of this record’s validity interval, as a canonical uint64 epoch-second string. |
| `notAfter` | End of this record’s original validity interval, in the same time grammar. |

The inspection interval must fit within the original source lifetime. Verify current source liveness and key possession before returning 200:

| Field | Required value or meaning |
| --- | --- |
| `exchange` | The exact exchange handle. |
| `sourceDigest` | SHA256 of the original source payload. |
| `state` | `pending` or `ready`, under the rules below. |
| `responses` | Eligible original signed device-response wrappers. |
| `publications` | Eligible original signed publication wrappers. |
| `routes` | Eligible original signed route-response wrappers. |

State is `pending` with all arrays empty, or `ready` with one or more eligible signed results. Responses contain original signed response wrappers; publications original signed publication wrappers; routes contain signed route-response wrappers below.

Setup lists are sorted by principal/device/publication-or-response ID, with no duplicate device setup; choose a current fresh response over a publication for that device. Routes are sorted by recipient principal/device/route-request ID, with no duplicate result for a device/request. Unsupported/unavailable recipients remain pending, not a distinct failure.

Ready means material is available for validation, not message admission or delivery. Never disclose a device/account list outside this authorized result.

A valid signed `bootstrap-cancel` payload has the same fields as inspect but purpose `bootstrap-cancel`, signed under the cancel domain. `POST /exchanges/{exchange}/cancel` body `{proof}` returns 204 after terminal cancellation of future disclosure. It cannot revoke already exposed packages or erase history. Local cancellation immediately gates content release even if this request is lost. Source permission withdrawal and immutable expiry independently stop new work. Cancelled/expired/unavailable exchanges have no ready result for new inspection; valid inspection of a cancelled exchange remains pending until the source interval ends. Invalid/expired source or possession proof receives generic 404 without account lookup.

### Signed request replay and disclosure bounds

A signed request can be retried. Someone who obtains a complete valid copy can also replay it, within the same authorization limits.

The signature proves that the device key signed the declared operation. It does not prove that the device still holds that private key at every HTTP retry. This baseline does not bind the proof to one TLS session or add a one-time challenge for each retry.

| Copied material | What the copy permits |
| --- | --- |
| Source permission alone | Neither reading the result nor cancelling the exchange; each needs its own signed proof |
| Complete, valid inspect proof | The same inspection, while its original interval, source/account/device authority and recipient disclosure policy remain valid |
| Complete, valid cancel proof | Repeating that already authorized cancellation |

A copy reveals no private key. It authorizes no different recipient, exchange, purpose or interval. It grants no permission to send a human message, install an identity pin or disclose history.

**Check every retry.**

Each replay rechecks the current disclosure gates. It cannot:

- Extend the proof interval or the original source lifetime.
- Allocate another package for an exchange/device that already has one.
- Reactivate a withdrawn publication or reverse cancellation.
- Bypass expired, withdrawn or revoked authority, or local cancellation.

A request that previously returned pending may later return ready under the existing allocation rules. The HTTP response is not an immutable cached authorization result.

A new inspect nonce does not refresh the recipient’s signed response. It cannot turn a published record into a live response.

**Protect retained requests.**

Create a fresh random nonce for a new logical inspect or cancel request. Retain that request’s exact signed payload and signature for retries, in protected attempt storage.

Keep these proofs out of ordinary logs, telemetry, forwarded email and public caches. TLS protects them in transit; local custody protects the retained copy.

### Recipient control inbox and fresh response

Under managementPrefix, `GET /inbox?cursor=<opaque>` requires own respond scope and the exact linked recipient device. The response is exactly `{items,next}`; items are `{exchange,source,routeRequests}` with the original signed source wrapper and an array of eligible signed route requests/source permissions below; the array is empty before the routing stage. Next is an opaque bounded cursor or empty.

Return only opted-in, current, eligible work for that account/device. Cursor progress is local service state, not evidence that a person saw anything. Polling is bounded and never starts from ordinary email rendering.

`PUT /inbox/{exchange}/responses/{device-suffix}` body `{proof}` signs exactly:

| Field | Required value or meaning |
| --- | --- |
| `version` | Exactly `"0"`. |
| `purpose` | Exactly `bootstrap-response`. |
| `response` | A response ObjectId. |
| `issuer` | This bootstrap destination’s origin. |
| `exchange` | The exact exchange handle. |
| `sourceDigest` | SHA256 of the original source payload. |
| `nonce` | The original source request’s random 64-hex nonce. |
| `mailbox` | The exact target mailbox owned by the linked account. |
| `device` | The linked recipient device’s endpoint reference. |
| `advertisement` | Canonical base64 of the original complete signed assertion8 wrapper. |
| `relayDomain` | Empty, or the canonical domain of that device’s connected receiving relay; never a URL. |
| `notBefore` | Start of this record’s validity interval, as a canonical uint64 epoch-second string. |
| `notAfter` | End of this record’s original validity interval, in the same time grammar. |

Issuer/exchange/sourceDigest bind the source preparation and destination. RelayDomain is empty or the canonical domain of that device's connected receiving relay, never a URL or source-supplied callback. The interval fits source request, target device and original advertisement/package. Validate full advertisement/identity/package correspondence, current receive authority, own account policy and fresh source permission before storing.

Same exchange/device exact response is HTTP 200 on retry; a new valid response is 201; changed authenticated content is 409. Return exactly `{responseDigest}`. Wrong-role or foreign-account credentials cannot read or write these slots. Persist acceptance and result atomically; an invalid signature cannot block the legitimate response.

### Publication and offline allocation

`PUT /publications/{publication}` requires own respond scope and a device signature over the following required fields:

| Field | Required value or meaning |
| --- | --- |
| `version` | Exactly `"0"`. |
| `purpose` | Exactly `bootstrap-publication`. |
| `publication` | This publication identifier, under its owning grammar. |
| `issuer` | This recipient service’s origin. |
| `mailbox` | The exact target mailbox owned by the linked account. |
| `device` | The linked recipient device’s endpoint reference. |
| `advertisement` | Canonical base64 of the original complete signed assertion8 wrapper. |
| `relayDomain` | Empty, or the canonical domain of that device’s connected receiving relay; never a URL. |
| `scope` | Exactly `automatic-first-contact`. |
| `notBefore` | Start of this record’s validity interval, as a canonical uint64 epoch-second string. |
| `notAfter` | End of this record’s original validity interval, in the same time grammar. |

The issuer, mailbox and device must match that account and linked endpoint. Validate the complete original assertion/package and both account/device publication policy.

The interval cannot exceed device/assertion/package validity; actual package use also applies the receiver’s configured [admission lifetime policy](security-profile.md#experimental-admission-lifetime). Publication has no separate mandatory seven-day cap.

Publication identity is scoped to the owning account incarnation/link namespace and linked device. Creation returns 201, identical retry 200, each exactly `{publicationDigest}`. Changed authenticated bytes under that ID conflict; validity renewal needs a new ID. Validate signatures before reserving a conflict identity. An exact retry after withdrawal reports the retained result without reactivating it.

`DELETE /publications/{publication}` returns 204 after withdrawal from future allocation and disclosure, including further inspection of an allocated record. Another account cannot withdraw it. No already disclosed material is recalled, and an already exposed package remains reserved.

Allocate only after current source authority, initiating-key possession, recipient account/device policy and source blocking have been checked. Public request admission and private dispatch do not consume the pool. For each eligible device without a current fresh response, select the first eligible publication in ascending ASCII publication-ID order. Atomically bind that original publication to `(exchange, device)` and reserve its package before returning the result. An invalid, expired, withdrawn or already allocated package is not eligible for a new allocation. A pool can contain multiple distinct packages, each in its own signed publication.

An empty pending inspection before any allocation commits can later obtain the first eligible publication while the original source/inspection bounds remain valid. It is not the immutable terminal depleted outcome of a separate completed allocation operation. Once an allocation exists, an exchange retry retains it even if another publication becomes available, sorts earlier or has a longer lifetime. Withdrawal, expiry or a device/account/relay change suppresses further disclosure of that allocation; it does not automatically select another pool entry.

A newly authorized fresh response or a new bounded exchange is needed for new material. A fresh response takes precedence over a publication for that device in inspection, but does not release any earlier allocation. Current material is returned under its original source classification: a publication never becomes a freshly answered challenge.

Fresh responses and publications share one package-allocation index, so republishing identical package bytes under a new assertion or publication ID cannot allocate them to another exchange. Commit the selected original bytes, allocation and package reservation together before constructing a successful outgoing response. A failed precommit transaction returns no setup and reserves nothing; an uncertain or lost postcommit response retries the committed allocation.

Once committed for disclosure, retain the reservation even on cancellation, withdrawal or loss of the HTTP result. Retain allocation/replay protection through the package's applicable lifetime; a restore cannot roll it back. Exhaustion holds rather than evicting an exposed allocation or fabricating a fresh package.

This index prevents reuse within that provider's allocation service. It cannot guarantee exclusive distribution if the same package was also published in ordinary email or at another service. Clients should generate dedicated packages for this pool. The recipient's independent cryptographic validation and atomic MLS single-use admission remain mandatory, and a failed competing admission waits for new eligible material. Providers never acquire a package's private admission key merely by storing its signed public publication.

### Optional route stage after setup

`POST /exchanges/{exchange}/routes/{device-suffix}` body is exactly `{request,sourcePermission}`. Request is a source-device proof under `route-request` over exactly:

| Field | Required value or meaning |
| --- | --- |
| `version` | Exactly `"0"`. |
| `purpose` | Exactly `bootstrap-route-request`. |
| `request` | The request ObjectId. |
| `issuer` | This bootstrap destination’s origin. |
| `exchange` | The exact exchange handle. |
| `sourceDigest` | SHA256 of the original source payload. |
| `nonce` | The original source request’s random 64-hex nonce. |
| `recipient` | The exact endpoint from an eligible disclosed response or publication. |
| `relayDomain` | Empty, or the canonical domain of that device’s connected receiving relay; never a URL. |
| `sourceDomain` | The independently selected relay source domain. |
| `sourceService` | The relay source service. |
| `sourcePermission` | The relay source-permission identifier; the outer request also carries its full signed wrapper. |
| `permissionDigest` | Digest identifying the independently activated relay source permission. |
| `notBefore` | Start of this record’s validity interval, as a canonical uint64 epoch-second string. |
| `notAfter` | End of this record’s original validity interval, in the same time grammar. |

Purpose is `bootstrap-route-request`; request ObjectId; issuer this bootstrap destination; recipient the exact endpoint from an eligible disclosed response/publication; nonce the original source nonce. RelayDomain matches that device's signed setup proposal. SourceDomain/sourceService/sourcePermission/permissionDigest identify the independently activated relay source permission; validate that source domain's own descriptor rather than inferring its domain from a personal SMTP From; the body sourcePermission is its complete original signed wrapper.

Require the bootstrap initiator key, live source authority and current interval inside the bootstrap request. Decode/validate the relay permission's exact sender, recipient principal, conversation and selected relay origin before privately queuing. The target must match the descriptor of the signed relayDomain; do not fetch a source-supplied arbitrary callback.

Successful admission returns HTTP 202 exactly `{exchange,request,state}`, state `pending`, regardless of current relay availability.

The recipient's private inbox includes `{request,sourcePermission}` for this exact device. Its local account policy must independently permit automatic route creation and the proposed relay must equal its already connected account. It validates fresh original relay source permission and performs the route preparation/approval through its own relay management authority. It does not forward its OAuth token to the bootstrap service, source or another relay.

`PUT /inbox/{exchange}/routes/{request}` body `{proof}` is signed by that recipient device under `route-response` over exactly:

| Field | Required value or meaning |
| --- | --- |
| `version` | Exactly `"0"`. |
| `purpose` | Exactly `bootstrap-route-response`. |
| `response` | A response ObjectId. |
| `issuer` | This bootstrap destination’s origin. |
| `exchange` | The exact exchange handle. |
| `sourceDigest` | SHA256 of the original source payload. |
| `requestDigest` | SHA256 of the original route-request payload. |
| `nonce` | The original source request’s random 64-hex nonce. |
| `device` | The linked recipient device’s endpoint reference. |
| `relayDomain` | Empty, or the canonical domain of that device’s connected receiving relay; never a URL. |
| `invitation` | Canonical base64 of the original `{approval,recipientIdentity}` relay invitation. |
| `notBefore` | Start of this record’s validity interval, as a canonical uint64 epoch-second string. |
| `notAfter` | End of this record’s original validity interval, in the same time grammar. |

The response interval fits the bootstrap attempt and current device authority.

Its route invitation retains its own independently approved lifetime, which may outlive the bootstrap attempt; neither signature refreshes the other.

Recheck exact account/device, original source/route request and all correlations before storing. Return 201 or 200 identical retry with exactly `{responseDigest}`. Invalid signatures cannot reserve conflicts, and different authenticated bytes under an exchange/device/request conflict. An unavailable or invalid relay route remains a held stage, never a guessed alias.


Inspect returns eligible original route-response wrappers in routes. The sender validates the full invitation under relay rules and performs live route-key inspection itself; neither a ready bootstrap response nor an octet string proves relay activation. Current account/device opt-out/revocation, cancellation and source expiry suppress new route disclosure as for setup. Exact retries preserve the original request, route key, permission and route approval. A new device/provider/scope needs fresh authorization, not mutation of these records.

### Resume the same relay operation

A bootstrap route request and each relay management operation have different identities. Retain their exact relationship before any remote mutation; replaying the parent must not invent another child request.

| Before this boundary | Required retained work |
| --- | --- |
| Source permission preparation | The selected own relay account/module/incarnation/family, local send-intent revision, intended peer/conversation, generated route-key custody and original relay preparation request ID/bytes |
| Bootstrap route-request submission | The original active source permission/proof, bootstrap exchange/source/nonce/agreement, selected recipient device/relay and exact signed route-request ID/bytes |
| Recipient relay preparation | The independently validated original bootstrap route request and digest, selected own recipient account/device, its enabled route policy and exact relay preparation request ID/bytes |
| Relay approval submission | The original returned preparation, actual offered scope/limits, route/alias, current authorization dependencies and exact signed approval bytes |
| Bootstrap route-response submission | The retained original invitation and exact signed response, correlated to that same parent request; an active route is still independently checked by the sender |

These are protected local journal records, not additional bootstrap or relay wire members. Exact request bytes here mean protocol bodies/proofs, not an Authorization header; live tokens remain in their own protected credential store. The selected protocol is an immutable dependency, not a new namespace that resets shared request, conflict, allocation or block state. Scope the journal to the actual local account/device, selected protocol/module, service and original parent identifiers/bytes. The incoming request cannot choose an own account, supply a local policy decision or turn an unrelated pending job into this one. The source keeps human draft content out of these control records. A route key is private source custody, never sent to the recipient or bootstrap service.

A duplicate parent joins the retained work. A restart reconciles its stored result or retries the same eligible POST/PUT with the original request and approval bytes under the relay's existing idempotency rules. Retain remote results before advancing the local stage. A response loss, missing local result, deadline or denied credential is not proof that preparation or activation never occurred. Do not generate a replacement child ID, route key or alias merely to make retry succeed.

Recheck current account/family/link, device authority, block/disclosure policy, original parent deadline, exact source permission and retained preparation before every new mutation or disclosure. A newly authorized account session does not inherit another family's pending child operation. If original authority or outcome cannot be reconciled, hold that work and preserve its uncertainty. After an independently authorized replacement decision, use a fresh bootstrap route request and its own child mapping while the owning source attempt is still eligible, or establish a fresh authorized setup attempt. Preserve the old attempt/result; do not alter an already submitted route-response or extend a timer. A remembered eligible policy may authorize maintenance, but received traffic or failed authentication cannot supply it.

Cancellation, source blocking or opt-out prevents further local preparation/disclosure under that job. If an alias or permission may already have activated, retain that outcome and use the actual relay-management withdrawal when currently authorized. Local cancellation does not remotely revoke a route, erase its retained result or authorize an invented cancellation message. Existing accepted retries can return historical outcomes without reactivating anything.

The sender validates the exact route invitation and performs its own current route-key inspection before protected content release, even after a ready bootstrap response or a resumed child succeeds. A prepared or signed route is not necessarily active. Do not report recipient masking as achieved from the existence of a journal row, alias string or bootstrap acknowledgment.

### Own-account source blocking

`POST /blocks` uses the selected own-account management prefix and requires current `mail.setup.respond` authority for that account. Its strict JSON body has exactly these members:

| Member | Required value or meaning |
| --- | --- |
| `version` | String `"0"`, `"1"` or `"2"`, exactly matching the bootstrap descriptor-bound route selected before parsing. |
| `purpose` | String `"bootstrap-block-source"`. |
| `request` | A nonzero ObjectId, retained for retries of these exact request bytes. |
| `exchange` | The 64 lowercase hexadecimal exchange handle from this account’s retained authenticated exchange. |

No agreement member or device signature is added to this account-management body. The inherited account-link/reset subset retains its separately selected literal version; it is not selected by this block request’s version. Unknown members, wrong types and route/version mismatches are invalid, with no fallback parser.

Authenticate the management account and scope, then validate the full body and that account’s retained exchange before reserving a request identity or reporting a conflict. Derive the source issuer/accountSource and known sender principal from the exchange’s original authenticated evidence, never caller-supplied identities. The evidence must remain attributable to this account; the peer’s permission need not remain live merely to block future attempts. Missing retained attribution cannot be replaced by a guessed source or principal.

Return 200 exactly `{block}`, a retained nonzero ObjectId. The request identity uses the same own-account bootstrap management namespace across supported route versions. Identical original request bytes return the retained identifier without creating another block; different authenticated bytes under that request identity conflict with 409, including a changed version or exchange. A new deliberate block operation uses a fresh request identity. A later exact retry of a removed block returns its historical result without recreating the block.

Block future disclosure and private dispatch for that account/source handle or known principal, including new permission IDs and a changed provider with the same principal. The block applies across bootstrap versions. This operation requires account management authority, not possession of the blocked peer’s key.

`DELETE /blocks/{block}` removes only that own-account block under a deliberate decision; other active blocks remain effective. Public POST still returns uniform pending for a valid blocked source. Blocking stops further setup disclosure, not already disclosed keys, ordinary email or previously delivered content. Relay delivery and mailbox filtering retain their own enforcement boundaries. An account can also withdraw its general automatic-setup permission without deleting history.

### Failure, retention and budgets

Apply the provider HTTP error vocabulary and bearer challenges:

| Condition | Response |
| --- | --- |
| Invalid public source, possession proof or purpose; expired authority | Generic 404 |
| Transient selected-service failure | 503 |
| Bounded exhaustion | 429 with a positive `Retry-After` |
| Malformed, oversized or unsupported representation | 400, 413 or 415, as applicable |

Error bodies are exactly `{error}` and do not echo records.

Do not contact arbitrary URLs, send automatic email, refresh a timeout, replace a pin or authorize fallback because an operation failed.

A fresh source inspection establishes a live service observation at that check, not instantaneous cross-provider revocation. Perform bounded network work outside long-lived local write locks, then recheck local account/device/policy and original observation/deadline dependencies at commitment. Local cancellation/withdrawal serializes with local disclosure; it cannot recall material already observed remotely.

Private journals retain original permissions, identity evidence, exact results and terminal/replay state for their finite supported retry horizon. They exclude human draft content and live bearer tokens. Expiry/cancellation stops new disclosure and retires attempt-bound secrets under [setup retirement](setup-secret-retirement.md), preserving independent admission-package lifecycle. Account/peer blocks and per-source/destination/issuer quotas apply before work and at disclosure; reset cannot clear an account's existing abuse handle. A dishonest operator or entirely new account/identity can still evade identity-based limits; no universal real-person control is claimed.

:::

## Validate the result, then establish encryption

The sender rechecks the original target domain/service and source permission, signed result purpose/digest/nonce/mailbox, device identity/current authority, original assertion8, complete selected application/module agreement, package cryptography/binding/lifetime/single-use scope and required freshness. The [freshness contract](freshness.md) supplies the local operation/policy/creation-time binding for these checks. A published record cannot satisfy a policy requiring a fresh challenge response. Source/target account-provider truth never substitutes for these checks.

Record the provider observation as a distinct `provider-bootstrap` observation: retain exact descriptors, source proof, authorized result bytes, original assertion and transport provenance. The [association eligibility procedure](mailbox-association.md) replaces the ordinary sole-outer-From match only for this explicit observation type with exact requested-mailbox/authorized-provider-result correspondence. Never manufacture an ordinary email From match or reuse an incoming `verified:true` field. Apply the same ambiguity, policy, continuity, generation and serialized release rules. A sole candidate under allow-unverified can be selected without a human email; strict or conflicting policy remains held.

After complete setup validation, perform the owning MLS initial admission and any requested relay-route approval. No human subject/content enters control traffic. Release the first contribution only after all current identity, package, context, recipient, policy and required secret-retirement gates pass. Setting up encryption, material returned, admitted, submitted, accepted and read remain different states.

## Complete setup locally

A valid response or publication supplies setup evidence, not a ready-to-send message. The [common setup handoff](first-contact-setup.md#finish-setup-for-one-intended-send) independently selects the actual device receiving assertions/application and admission, preserves the frozen local intent revision, completes required retirement and activates each eligible scoped copy’s retained protected outbox set under the unchanged parent send plan. Pending responses cannot send a cancelled or edited revision. Bootstrap acceptance, local outbox activation, SMTP handoff and recipient admission remain separate outcomes.

## Acceptance obligations

The full positive case starts with no recipient association or pair grant, authenticates a real source account, runs the private recipient control inbox without a human reply, validates actual signed assertion/package evidence, selects a common application, establishes MLS and sends the first human message through the real mail path. Repeat with offline publication allocation, the optional private-route follow-up stage and no available material. Inspect all requests, queues, drafts and mailboxes for body/subject/attachment or content-hash leakage.

Negative cases include mailbox spoofing, copied source permission without possession, copied complete inspect/cancel proofs under their exact bounded scope, retry versus new poll and no added package allocation/deadline or freshness, wrong target/service/nonce, revoked/changed source or recipient, new-identity conflict, invalid package/signature, stale publication called fresh, account enumeration/status differences, invalid-proof collision poisoning, competing package allocation, terminal cancellation, expiry/restart/clock uncertainty, offline allocation through concurrent service connections, fresh/publication package collisions, withdrawal without reallocation, lost replies and crashes at each journal boundary. No ready response alone counts as complete acceptance. Production service, complete assertion8/admission, independent-client and independent security evidence remain unproven until actually exercised.

Source-block acceptance must exercise each selected route version, reject a mismatched body version before effects, and prove that an unauthorized request cannot reserve another account’s request identity. Retry the exact request across restart, then submit changed authenticated bytes under the same identity and require conflict without changing the block. A block must suppress disclosure through every supported bootstrap version while public admission remains uniformly pending. Also block a retained authenticated exchange after its peer permission expires, remove that block deliberately, and retry the original creation: the historical result must not reactivate it. Missing exchange attribution cannot create a caller-named block.

An assertion8 response may allocate a package with the [separate receiving-only deadline](suite-profile.md#creating-a-delivery-and-receiving-it-later). That role must be recorded before publishing the response. The bootstrap request and source creation authorization still expire at their original deadlines; a later Welcome cannot reactivate either. The allocation stays single-use and cannot be republished or moved to another attempt.


## Accepted identity advances

The [purpose-specific continuity rules](provider-grants.md#continuity-and-freshness-have-different-scopes) distinguish retained source permission and offline publication from live target evidence. Original source preparations and offline publications can survive an independently accepted state advance only for the same exact device/binding/key and required role. Every account, attempt, allocation and validity check remains effective. Original signed bytes do not change when the trusted local account slot learns a newer head. A live response instead needs the exact current target head; reclassifying an older response or publication cannot satisfy a live policy. Required recent-checkpoint checks evaluate the current accepted state's signed issuance time separately from either original anchor.


After a [state1 repair](identity-state.md#concurrent-administration-and-retirement), retained pre-repair source preparations, device links, offline publications and live freshness results cannot cross the repair using unchanged-binding ancestry. Reconnect/reprove applicable links and obtain new appropriately scoped setup from the repaired head under current account policy. Preserve original package allocations, deadlines and uncertain attempts; no repair rewrites them or makes an older response live. Administrative proof circulation is its separate narrow purpose and does not implicitly extend this bootstrap API.


The [renewal/publication algorithm](security-profile.md#publish-replacements-without-disturbing-in-flight-mail) binds a native package reference to one independent allocation authority before publication. A new provider/account allocation scope uses fresh material; changing a publication ID does not move a reserved reference. Pool replenishment never changes a retained exchange allocation or releases an earlier fresh-response reservation. Public copying is not covered by a provider's local exclusivity claim, and recipient single-use acceptance remains independent.

## Provider setup for declared reply policies

A provider can help two clients discover the support needed for a message's reply policy. The initiating client names the required agreement before requesting setup. The source provider and recipient service must preserve that choice through authorization, device responses and offline publication. A successful provider request does not mean the message was sent or that either person's identity was independently verified.

This successor uses the same account login, recipient opt-in, content-free request and bounded disclosure model. It does not give the sender access to the recipient's account. If the provider path is unavailable, keep the draft and its policy; the separately defined [ordinary-mail setup1 path](mailbox-setup.md#set-up-the-declared-reply-policy) may be selected only under the existing acquisition-path and disclosure rules.

::: {.details summary="Exact bootstrap1 discovery, permissions and signed records"}

**Descriptor.** Bootstrap descriptor1 has exactly descriptor0's complete member inventory plus required `agreement`, with version `"1"` and agreement exactly `"mail-conversation-v1"`. Its purpose, well-known path `/.well-known/mail-setup`, canonical selected mailbox domain, publication/generation, service origin, roles, three nonoverlapping same-origin prefixes and original validity intervals retain their existing grammars. The descriptor must select only version1 operations below at those prefixes. Active version0 and version1 prefixes at one service must not overlap by segment containment; do not choose a parser by trying another version after failure.

Apply the unchanged retained-domain/purpose/publication/generation high-water, original-byte commitment and current transport/delegation rules. An update requires a new accepted generation, never rewriting an accepted response. Version is not a new publication or account namespace. A client unable to validate descriptor1 reports this path unavailable; it does not reinterpret it as version0, install an unsolicited alternate endpoint or remove a required reply policy. Existing version0 grants and results retain their original routes and deadlines while independently eligible.

Own-account native login scopes remain the exact selected subset of mail.setup.link, mail.setup.request and mail.setup.respond. The existing shared account-link/reset subset retains its literal profile, schemas, proof domains and integer time grammar, binding the exact descriptor1 digest under the bootstrap module. It grants no queue/relay access. Descriptor1 cannot trigger sender sign-in to a recipient service or move an existing token to another origin. Refresh, unlink, reset, family/incarnation changes and serialized revocation retain their existing boundaries.

**Source preparation.** The unsigned bootstrap-source-request has its exact version0 fields plus required `agreement` and `targetDelegation`. The prepared bootstrap-source payload likewise has its version0 fields plus those two required members. Version is `"1"`; agreement is exactly `"mail-conversation-v1"`; targetDelegation is the SHA256 digest, encoded as 64 lowercase hexadecimal characters, of the complete original accepted descriptor1 bytes for the selected recipient mailbox domain. The initiating client freezes that record and digest before preparation. Source-provider validation independently obtains and validates that exact destination descriptor, its target service, agreement, respond-target role and original interval; a changed digest holds preparation for a newly selected, separately authorized attempt. It is not a callback permission from arbitrary request text.

The source's existing delegation field remains the digest of its own accepted descriptor1. It must have request-source authority for the sender domain and current authoritative sender-account/mailbox membership. The original source approval binds both descriptor choices, all intent fields, exact assertion9 and the unchanged finite source interval. Neither a changed generation nor protocol upgrade refreshes its deadline or permits different content/audience.

**Signed records.** Every signed source, inspect, cancel, response, publication, route-request and route-response payload has exactly its version0 member set plus required `agreement`, with version `"1"` and the fixed agreement above. Source alone additionally has targetDelegation as specified. All advertisements are the complete original assertion9 wrapper, with its independent signature, current accepted identity/role, canonical mailbox, original package and control-key checks. Payloads have no new extension bag. Purpose, field types, complete member inventories, bounds, canonical encodings, interval rules and original byte/digest commitments otherwise remain unchanged.

Their signature domains are exactly `mail/bootstrap/source/v1`, `mail/bootstrap/inspect/v1`, `mail/bootstrap/cancel/v1`, `mail/bootstrap/response/v1`, `mail/bootstrap/publication/v1`, `mail/bootstrap/route-request/v1` and `mail/bootstrap/route-response/v1`. Retain NUL, U32 big-endian payload length and exact original payload bytes. A correctly signed record under another kind, version or agreement is not a compatible substitute. Wrappers remain exactly payload/signature; HTTP wrapper bodies such as proof/source retain their original shapes and route-specific authority.

**Exchange and correlation.** Use exchange-ID domain `mail/bootstrap/exchange/v1` with the original issuer-length/issuer/source-ID construction. The new domain prevents interpreting an old handle as a new one; it does not create another source permission. Source permission/account/device IDs, immutable original source bytes, targetDelegation and agreement remain tied together. Inspect, cancel, response and route records must match the retained source's exact agreement, issuer/exchange, sourceDigest and original nonce/deadline where required by their purpose. A fresh inspect nonce cannot refresh a response or create live freshness.

The target service accepts only a source whose current origin-selected inspection returns that exact original version1 proof under active source-account/device authority. It validates both selected descriptor1 records, targetDelegation and agreement before any private lookup or allocation. Unsupported or unavailable recipients remain uniformly pending; invalid/expired source proof retains the existing generic failure. No new endpoint lists accounts, devices or presence.

:::

::: {.details summary="Allocation, route follow-up and first-message handoff"}

**Fresh and offline results.** Recipient fresh responses and publications carry their own exact assertion9 and agreement. The required complete per-ordering operation closure is independently validated. A response key is still not a human-verification certificate or a sender release grant. Publications keep their existing automatic-first-contact scope, opt-in, current source authorization, single-exchange allocation, immutable recipient/device result and original withdrawal/deadline rules. Publication cannot satisfy a live challenge policy merely because it was retrieved recently.

Package-reference custody, allocation realm and consumed/terminal records are shared across supported acquisition versions for the actual issuing device. Publishing version0 and version1 wrappers around one package cannot allocate it twice. Source/account abuse handles, blocked sources/known principals, account incarnation, request conflict evidence and cancellation are not reset by a new version or path prefix. Apply the owning serialized current-authority checks on every retry and disclosure, including a formerly pending inspect that later becomes ready.

**Routing.** Route-request1 and route-response1 preserve the agreement and original source/request commitments. The [retained parent/child operation procedure](#resume-the-same-relay-operation) applies with those exact original version1 records; changing protocol version cannot create another retry namespace. Existing independently authorized relay-source permission and route invitation formats remain unchanged: they bind actual source/recipient identities and conversation, not the bootstrap record version. Validate the selected relay domains/services, current account/device authority, exact opaque scope and actual activation under the relay contract. No bootstrap service can manufacture a relay grant, forward OAuth credentials or call an arbitrary source-supplied URL.

A relay's opaque-v0 commitment covers the exact selected sealed-control-v1 or protected application bytes; it must not parse, rewrite or substitute context8 for context9. The source still independently checks exact route scope, current route/key status and recipient authority. Missing relay support or activation holds a required masking stage; a ready setup result cannot downgrade it or display an inaccurate identity-protection indicator.

**Handoff.** Independently validate every intended original assertion9 and select the complete [reply-aware agreement](reply-intent.md#reply-aware-protected-agreement). Preserve the exact local send-intent revision, required reply policy, selected agreement, intended devices and scoped copy plan. Apply the same separate creator receiving evidence, current identity/association/freshness, native package/admission, checkpoint/retirement, non-releasable outbox and final content-release boundaries as the [common handoff](first-contact-setup.md#finish-setup-for-one-intended-send), using context9/initial9/roster6/established9, successor controls and mime-suite-v1. A fetched response is neither protected admission nor permission to send the current editor contents.

Existing grant intervals and package receiveUntil promises remain independently bounded; bootstrap expiry cannot recreate a retired key, recall earlier disclosure or extend publication/admission authority. Reset, cancellation, expiry, verification holds, unknown/conflicting identities, lost outcomes, restore/rollback and local path switching keep their original safe outcomes. Provider omission can prevent progress; it cannot authorize unencrypted content or a different reply mode.

:::

The version1 binding is a proposed protocol definition, not a deployed service or certification. Claims require the exact new descriptor/permission/result records, real account/provider authority, source inspection, opt-in and allocation serialization, all signed device/package checks and actual first-message handoff. Isolated signature or correlation tests do not establish those outcomes. Earlier version0 component results retain their exact original scope.


## Automatic setup for independently ready recipients

Alice can obtain Bob's setup and start their intended conversation while Carol is still pending. Each provider request asks only for its named recipient's setup. It contains no human writing or group roster, and its success does not turn pending invitees into encryption members.

The selected binding is bootstrap2 for [mail-conversation-v2](suite-profile.md#asynchronous-protected-agreement). Its source and recipient policies, uniform pending responses, optional offline publication and independently authorized routing retain their existing meanings. The [ordinary-mail setup2 path](mailbox-setup.md#set-up-an-asynchronous-delivery) is separately selectable when its policy and disclosure requirements allow it.

::: {.details summary="Exact descriptor2, source permission and signed records"}

Bootstrap descriptor2 has exactly bootstrap descriptor1's member inventory, with version `"2"` and agreement `"mail-conversation-v2"`. Purpose, `/.well-known/mail-setup`, selected domain, publication/generation, service origin, roles, three prefixes, strict transport/parsing and validity rules remain unchanged. It selects only bootstrap2 operations at those prefixes. Active prefixes across bootstrap versions cannot overlap by segment containment. The [synthetic descriptor](examples/async-bootstrap-descriptor.json) illustrates that shape, not an active delegation.

Apply the same domain/purpose/publication high-water across versions. A byte change requires a new generation; an incoming version is not a fresh history, reset or grant. Freeze exact source and target descriptor2 bytes before source preparation. Unsupported descriptor2 leaves this path unavailable without changing the required agreement or discovering another endpoint by guesswork.

Native login uses the existing selected subset of mail.setup.link, mail.setup.request and mail.setup.respond. Own-account shared-link/reset proofs keep their existing literal schemas/domains and bind the actual descriptor2 digest under the bootstrap module. No sender login at the recipient service, token migration, new callback or account-membership claim is introduced. Already accepted same-service/account/device links remain subject to their original module/family authority and current delegation checks; a changed protocol record does not require disconnecting a healthy link or relabeling its historical proof. It cannot preserve a revoked link or migrate one to a new origin.

The unsigned bootstrap-source-request and prepared signed source have exactly their bootstrap1 inventories, including agreement and targetDelegation. Version is `"2"`; agreement is mail-conversation-v2. TargetDelegation is SHA256 of the complete original accepted target descriptor2 bytes, as 64 lowercase hexadecimal characters. Delegation remains the digest of the source's own accepted descriptor2. The source service independently validates both exact domain delegations, current mailbox/account membership, request-source/respond-target roles and original credible intervals. A changed selection needs a separately authorized preparation; it cannot edit retained source bytes or refresh their deadline.

Every signed source, inspect, cancel, response, publication, route-request and route-response payload keeps its exact bootstrap1 inventory, with version2 and the same required agreement. All advertisements are complete original assertion10 wrappers under their independent signatures and owning identity/package/control-key checks. Other purpose/member/type, canonical encoding, byte/depth, time and original commitment rules are unchanged. Wrappers remain exactly payload/signature; unsigned HTTP proof/source bodies keep their existing route-specific shapes.

| Signed record | Signature domain |
| --- | --- |
| Source | `mail/bootstrap/source/v2` |
| Inspect | `mail/bootstrap/inspect/v2` |
| Cancel | `mail/bootstrap/cancel/v2` |
| Response | `mail/bootstrap/response/v2` |
| Publication | `mail/bootstrap/publication/v2` |
| Route request | `mail/bootstrap/route-request/v2` |
| Route response | `mail/bootstrap/route-response/v2` |

Framing remains NUL, U32 big-endian original payload length and exact original bytes. Exchange IDs use `mail/bootstrap/exchange/v2` with the existing issuer-length/issuer/source-ID construction. Version is part of the immutable exchange selection, not a fresh source permission or conflict namespace. Reject cross-version/purpose/agreement substitution before effects; no failed branch falls through to an older parser.

Before private lookup/allocation, the target service validates the original source through its origin-selected current inspection, both descriptor2 commitments, exact target/service/agreement and current source account/device authority. Inspect/cancel/response/route proofs match the original issuer/exchange, sourceDigest, nonce and fixed deadline wherever their purpose requires. A fresh inspect proof cannot refresh a device response. Unavailable recipients remain uniformly pending, without exposing existence, device counts or presence.

:::

::: {.details summary="Independent results, allocations, privacy routes and handoff"}

Fresh responses and offline publications carry their own original assertion10 and agreement. Validate its fixed readable application and each device's independent interactions under the chosen ordering; the older optional-subset closure is not applied. Publication remains cached evidence, not a live challenge or permission to release content. A fresh device response qualifies for live use only under the exact retained attempt and [freshness rules](freshness.md#freshness-for-asynchronous-deliveries).

The actual issuing device's package custody, allocation realm and consumed/terminal state remain shared across acquisition versions and eligible mailbox aliases. Wrapping one native KeyPackageRef in different assertion/publication versions cannot allocate it twice. Scope/account/source blocks, account incarnation, recipient opt-in, original intervals, withdrawal, response identities and serialized current-authority checks remain in force. Different aliases do not transfer an allocation or credential between account namespaces. A published package must be valid for the exact actual acquisition and admission that use it.

Route-request2/response2 preserve the source/agreement and original parent/request commitments. The retained parent/child retry procedure applies to the exact version2 bytes. Existing relay-source permission and route invitation formats retain their own independent authorization, identity and actual conversation scope. Opaque relay layout carries the exact selected sealed2 or protected application bytes without parsing/relabeling them. Source/recipient masking still waits for the required active route; setup success cannot downgrade it. No service follows an arbitrary callback or forwards another origin's credentials.

Each result enters the [per-delivery handoff](first-contact-setup.md#acquisition-for-independently-ready-deliveries) for its exact local intent revision and selected mailbox/account. It does not resolve someone else's unknown scope slot, authorize automatic historical disclosure or make another device ready. Ready eligible deliveries may progress under the frozen send plan while the remaining intended slots retain explicit pending states. Cancellation, supersession and expiry stop their owning pending operations; neither a new acquisition path nor a fresh result revives the old intent. Native admission and final content release remain separate current checks.

:::
