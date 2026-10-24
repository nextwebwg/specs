---
title: Home-service rendezvous
order: 10.166
blurb: proposed request-bound connection control
sectionNav: true
---

# Connect through two home services

**Proposed binding: `mail-rendezvous-v0`.** This chapter defines a connection request containing no message content. Each app uses its own home service; the receiving app answers automatically under its enabled policy. An answer authorizes this connection attempt only. It does not authorize sending content, admitting an MLS member, revealing presence publicly or managing relay addresses.

The selected path here uses the home services. Direct WebRTC requires an additional authenticated signaling-carriage binding; it must not be advertised merely because this request/answer binding exists.

## What a person experiences

Alice selects Bob. Her app uses accepted setup and a service location it is permitted to use. Her home service forwards one signed request to Bob's home service. Bob's permitted device can answer in the background. Alice's app verifies that answer and can use the agreed service connection.

A missing answer does not stop independently eligible encrypted mailbox delivery. It does not mean Bob is offline, does not exist or cannot encrypt. Both apps can keep their ordinary email providers. Their home services can be independent operators.

The first request does not require a pre-existing provider-queue grant. It requires the new home-account authorization and destination admission policy below. The receiving device's answer creates an exact request-bound rendezvous grant. It does not convert an old queue grant into a federation permission.

## Implementation prerequisites

The records below do not yet supply a complete interoperable service. The [independent native-module binding](provider-discovery.md#independent-registrar-and-home-connections) defines this module's sign-in selection, but still requires actual implementation and acceptance evidence. Exact module-specific account inspection/reset records and pending-offer retrieval, cursor and answer-preparation route bindings still need their own complete wire definitions. Existing provider-grant profiles, signature purposes and integer timestamps cannot be relabeled as these string-timestamp records.

First-contact admission also requires the complete [mailbox registration](mailbox-registration.md) owner and its actual registrar/native validation. [Service federation](service-federation.md) defines the architecture; it cannot substitute for a missing record parser or permission. Until these dependencies are implemented and tested, this chapter does not authorize advertising interoperable rendezvous support.

## Actors and authority

| Actor or record | What it authorizes | What it cannot authorize |
| --- | --- | --- |
| Own-account native login | Management at the selected home origin under the rendezvous module | Mailbox ownership, a peer account, identity enrollment or content release |
| Device-signed home authorization | One accepted device delegates the declared service key and opaque home account for this rendezvous role | Ownership of a foreign email domain; another device or a different service key |
| Source service dispatch | The active source account/link released this exact device request to the exact destination | A device signature, recipient identity, a live recipient or decryption |
| Destination admission policy | Bounded storage/processing of a request under an enabled account policy | An authenticated device answer or acceptance of an unknown correspondent identity |
| Target-device answer/grant | This exact pair and request may use the selected rendezvous path until expiry | Message-delivery custody, read receipt, MLS admission or an account-wide device roster |
| Mailbox-association evidence | The declared registrar verified current control of the selected mailbox under its stated method | Independent human identity or replacement of an existing correspondent pin |

Installation attestation, API keys and computational puzzles may support admission and budgets. They supply none of the identity or delegated-service authority in this table.

:::: {.details summary="Bind the home account once"}

### Bind the home account once

The client selects and authorizes its own home origin through account configuration or an accepted domain delegation. A recipient lookup never starts this login. For an independent service, explicit own-account configuration supplies service-location trust; it does not inherit authority over the mailbox domain.

The new module is `rendezvous`. Its exact native scope set is `mail.rendezvous.link mail.rendezvous.manage`. Reuse [native connection mechanics](provider-discovery.md#reuse-sign-in-mechanics-without-sharing-permissions), exact issuer/origin checks, external-browser authorization-code/S256 PKCE, shared callback forms, refresh handling and module-separated storage. A distinct module registration and grant are required. Existing provider, relay and setup tokens do not gain these scopes. Existing bearer-token limitations remain.

Use a new `mail-rendezvous-v0` account-link challenge and completion. Reuse the [shared account-link owner](provider-grants.md#shared-account-links-separate-module-authority)'s transaction, possession proof, identity-bundle validation, retry, reset and revocation rules, with the following exact account-link records. The account-reset and inspection substitutions remain separate prerequisites; an old proof cannot be relabeled:

### Challenge request

| Member | Type and binding |
| --- | --- |
| `profile` | Exact `mail-rendezvous-v0` literal. |
| `request` | Nonzero random 16-byte lowercase-hex ObjectId, with its exact retained binding. |
| `descriptorDigest` | SHA256 of the original selected service descriptor. |
| `device` | Exact endpoint object under the common identity rules. |

### Prepared challenge

| Member | Type and binding |
| --- | --- |
| `profile` | Exact `mail-rendezvous-v0` literal. |
| `purpose` | Exact purpose stated below. |
| `challenge` | Nonzero random 16-byte lowercase-hex ObjectId, with its exact retained binding. |
| `request` | Nonzero random 16-byte lowercase-hex ObjectId, with its exact retained binding. |
| `nonce` | Fresh random 32-byte lowercase hex. |
| `descriptorDigest` | SHA256 of the original selected service descriptor. |
| `service` | Exact selected canonical HTTPS service origin. |
| `account` | Opaque 64-lowercase-hex service-account binding. |
| `family` | Opaque 64-lowercase-hex OAuth-family binding. |
| `device` | Exact endpoint object under the common identity rules. |
| `notBefore` | Inclusive canonical uint64 Unix-seconds string. |
| `notAfter` | Exclusive canonical uint64 Unix-seconds string. |

Purpose is `rendezvous-account-link`.

### Completion

| Member | Type and binding |
| --- | --- |
| `proof` | Original device-signed wrapper over the exact prepared link challenge. |
| `identity` | Complete original identity bundle under the current identity owner. |

### Result

| Member | Type and binding |
| --- | --- |
| `profile` | Exact `mail-rendezvous-v0` literal. |
| `purpose` | Exact purpose stated below. |
| `challenge` | Nonzero random 16-byte lowercase-hex ObjectId, with its exact retained binding. |
| `requestDigest` | SHA256 of the named original payload bytes. |
| `link` | Exact active device-link ObjectId. |
| `account` | Opaque 64-lowercase-hex service-account binding. |
| `device` | Exact endpoint object under the common identity rules. |
| `notBefore` | Inclusive canonical uint64 Unix-seconds string. |
| `notAfter` | Exclusive canonical uint64 Unix-seconds string. |

Purpose is `rendezvous-account-linked`.

There is deliberately no `mailbox` field. This link authorizes a service account and device, not an email-address claim. The server derives account and family from its own authentication. It must not accept a submitted account identifier instead. Current receive authority is required; first observation remains explicitly unverified when the owning identity policy permits it. The result is service-authenticated local state, not transferable evidence of mailbox ownership.

The home service descriptor has the following exact required members.

| Member | Type and binding |
| --- | --- |
| `profile` | Exact `mail-rendezvous-v0` literal. |
| `purpose` | Exact purpose stated below. |
| `publication` | Service-descriptor publication ObjectId under the common record-ID grammar. |
| `generation` | Canonical unsigned-64 decimal generation string. |
| `service` | Exact selected canonical HTTPS service origin. |
| `prefix` | Full canonical same-origin HTTPS URL ending in `/`. |
| `serviceKey` | Lowercase 64-hex Ed25519 public key. |
| `limits` | Exact positive-bound object listed immediately below. |
| `notBefore` | Inclusive canonical uint64 Unix-seconds string. |
| `notAfter` | Exclusive canonical uint64 Unix-seconds string. |

Its purpose is `rendezvous-service`. The descriptor is obtained through the selected authenticated own-account configuration or its exact future domain-discovery binding. `prefix` is at `service`; serviceKey is Ed25519. Publication/generation decisions retain the provider-discovery high-water, equal-generation conflict and origin-change rules. Descriptor updates cannot edit an existing authorization. Limits has exactly the following required members, all positive canonical unsigned-64 decimal strings.

| Member | Type and binding |
| --- | --- |
| `maxPayloadBytes` | Positive canonical uint64 maximum original signed-payload bytes. |
| `maxSubmissionBytes` | Positive canonical uint64 maximum complete immutable submission bytes. |
| `maxDepth` | Positive canonical uint64 strict-object nesting limit. |
| `pendingPageSize` | Positive canonical uint64 maximum pending entries per page; retrieval wire remains a separate prerequisite. |
| `cursorLifetimeSeconds` | Positive canonical uint64 maximum pending-cursor interval in seconds; cursor wire remains a separate prerequisite. |
| `pollSeconds` | Positive canonical uint64 minimum polling interval in seconds. |
| `retentionSeconds` | Positive canonical uint64 retention interval covering the accepted offer and supported uncertain-outcome recovery. |

These are published adjustable deployment bounds, not user-mandated quotas. A client unable to support the complete descriptor holds this path. Requests must fit both selected homes' limits; validate before release and again before parsing/allocating under each server's local hard bounds. A descriptor cannot compel allocation beyond a receiver's configured ceiling. Poll no faster than either selected minimum pollSeconds. RetentionSeconds must cover the originally accepted offer interval plus supported uncertain-outcome recovery; reject an interval that cannot be retained rather than silently shortening it.

After linking, the device signs a home authorization exactly:

| Member | Type and binding |
| --- | --- |
| `profile` | Exact `mail-rendezvous-v0` literal. |
| `purpose` | Exact purpose stated below. |
| `authorization` | Home-authorization ObjectId. |
| `descriptorDigest` | SHA256 of the original selected service descriptor. |
| `service` | Exact selected canonical HTTPS service origin. |
| `prefix` | Full canonical same-origin HTTPS URL ending in `/`. |
| `serviceKey` | Lowercase 64-hex Ed25519 public key. |
| `account` | Opaque 64-lowercase-hex service-account binding. |
| `link` | Exact active device-link ObjectId. |
| `device` | Exact endpoint object under the common identity rules. |
| `notBefore` | Inclusive canonical uint64 Unix-seconds string. |
| `notAfter` | Exclusive canonical uint64 Unix-seconds string. |

Purpose is `rendezvous-home-authorization`. The service atomically installs it only under the same active linked account/family and exact retained descriptor. Its interval fits the descriptor, link, family and device binding. The device may publish the original signed authorization alongside its independently authenticated setup. An untrusted directory cannot manufacture or broaden it. For a known correspondent, this device delegation can name an independent home; it needs no claim that the home controls the correspondent's mailbox domain.

A home authorization's endpoint state is its original accepted anchor. At use, the offer endpoint must retain the same principal, device, binding and key, with an independently validated accepted path from that anchor to the current head. Do not require raw state-digest equality for binding-continuity use and do not replace the original home proof. The exact target-state challenge rule below applies separately to the live offer.

A new device needs its own link and authorization. Delegating a home service neither enrolls that device nor gives the service a device signing key. An origin/key/account change needs a fresh authorization under an already eligible remembered policy or account reconnection; no credential migrates automatically.

::::

:::: {.details summary="Strict records and signature domains"}

### Strict records and signature domains

All payloads use profile `mail-rendezvous-v0`. JSON is strict UTF-8: reject duplicate, missing and unknown members. No null, booleans, floating point or JSON numeric values occur in this binding. Times and generations are canonical unsigned-64 decimal strings. Arrays have the exact permitted values/order below. No omitted defaults or extension bag exists.

Account and OAuth-family bindings are opaque64-lowercase-hex values; link and authorization identifiers use the16-byte record-ID grammar. A service key is64-lowercase-hex Ed25519. Enrollment attestation fields retain their separately owned grammars.

An endpoint is exactly `{principal,device,state,binding,key}`, using the existing principal/device grammars and lowercase 64-hex state/binding/Ed25519-key fields. A digest is SHA256 of the original payload bytes unless explicitly called a wrapper digest. Nonces are random 32-byte lowercase hex; record IDs are random nonzero 16-byte lowercase hex. Services use the existing exact canonical HTTPS origin grammar. Every prefix is a full same-origin HTTPS URL ending in `/` under the [realm prefix rules](discovery-realms.md#exact-configuration-chain). Append displayed route suffixes without their leading slash to preserve the selected prefix path. A path-only prefix or root-relative resolution is invalid. Reject noncanonical input; do not repair it. The complete credible clock interval must fit every applicable interval; unavailable time holds new effects.

A signed wrapper is exactly `{payload,signature}`: canonical padded base64 original payload bytes and a lowercase 128-hex Ed25519 signature. Sign the purpose-specific ASCII domain, NUL, U32 big-endian original byte length and those original bytes. Never verify a reserialized object.

| Purpose | Signature domain | Signer |
| --- | --- | --- |
| rendezvous-account-link | mail/rendezvous/account-link/v0 | Linked device |
| rendezvous-home-authorization | mail/rendezvous/home-authorization/v0 | Delegating device |
| rendezvous-offer | mail/rendezvous/offer/v0 | Initiating device |
| rendezvous-dispatch | mail/rendezvous/dispatch/v0 | Delegated source service key |
| rendezvous-answer | mail/rendezvous/answer/v0 | Exact target device |
| rendezvous-command | mail/rendezvous/command/v0 | Initiating device |
| rendezvous-forward | mail/rendezvous/forward/v0 | Delegated source service key |
| rendezvous-inspect | mail/rendezvous/inspect/v0 | Delegated target service key |

These are new purpose-separated uses of existing Ed25519 and byte framing, not a new cryptographic algorithm. Existing retained domains remain exact.

::::

:::: {.details summary="Offer, dispatch and admission"}

### Offer, dispatch and admission

The initiating client durably freezes one offer before release:

| Member | Type and binding |
| --- | --- |
| `profile` | Exact `mail-rendezvous-v0` literal. |
| `purpose` | Exact purpose stated below. |
| `id` | Nonzero random 16-byte lowercase-hex ObjectId, with its exact retained binding. |
| `nonce` | Fresh random 32-byte lowercase hex. |
| `sourceHome` | SHA256 of the original source home-authorization payload. |
| `targetHome` | SHA256 of the original target home-authorization payload. |
| `initiator` | Exact initiating endpoint object. |
| `target` | Exact target endpoint object. |
| `authority` | Exact tagged known-peer or first-contact object defined below. |
| `paths` | Exactly `["home-ciphertext"]`. |
| `notBefore` | Inclusive canonical uint64 Unix-seconds string. |
| `notAfter` | Exclusive canonical uint64 Unix-seconds string. |

Purpose is `rendezvous-offer`; sourceHome/targetHome are payload digests of the exact original signed home authorizations. Initiator and target are exact endpoints. `paths` is exactly `["home-ciphertext"]` in v0. No body, subject, content digest, audience list, SDP, ICE candidates, IP address, relay mailbox or private key is included. This record requests a connection; it is not a message packet.

Authority is one of these exact tagged forms:

- `{kind:"known-peer"}`: the initiator retains its independently accepted mailbox/principal association locally. The destination evaluates its own corresponding accepted peer policy. An assertion that a peer is known cannot install recipient trust.
- `{kind:"first-contact",sourceEnrollment,targetEnrollment}`: both values are payload digests of the independently authorized mailbox-association attestations defined in the prerequisite owner below. This shape is unavailable until that complete owner is selected and implemented. It must not accept a self-signed mailbox claim or a generic provider login in place of those attestations.

The complete immutable submission has exactly these required members:

| Member | Type and binding |
| --- | --- |
| `offer` | Original signed wrapper. |
| `sourceHome` | Original signed wrapper. |
| `targetHome` | Original signed wrapper. |
| `sourceDescriptor` | Canonical padded base64 of complete original strict descriptor bytes. |
| `targetDescriptor` | Canonical padded base64 of complete original strict descriptor bytes. |
| `initiatorIdentity` | Complete original identity bundle. |
| `targetIdentity` | Complete original identity bundle. |
| `associationEvidence` | Exact tagged known-peer or first-contact evidence object defined below. |

 Offer and home values are original signed wrappers. Descriptor values are canonical padded base64 of their exact original strict JSON payload bytes; their SHA256 digests must match the corresponding home authorization and their service/prefix/key fields must match it. Receivers retain those original bytes, validate the full descriptor and current authorization, and do not fetch an arbitrary descriptor URL from a request. Identity values are complete owning identity bundles, not caller-ready booleans. associationEvidence has exactly `{kind:"known-peer"}` or `{kind:"first-contact",sourceEnrollment,targetEnrollment}`, matching offer.authority; Each enrollment value here is the complete original [registration publication](mailbox-registration.md#publish-a-bounded-attestation), exactly `{attestation,challenge,proof,identity,home}` with that owner's original member types. Each receiver independently validates its admitted registrar, original descriptor/key/method, full publication, current subject/device/home and intervals under its already configured policy. A submission cannot install a new realm root, registrar admission or callback. An unconfigured or incomplete enrollment is held rather than fetched from an arbitrary URL. Their digests must match. Clients validate the locally selected recipient and preserve the original evidence separately from current local decisions.

Alice submits that object at her own `POST /offers` with her rendezvous management token. The source service verifies the device signature, current active account/family/link/home authorization, selected identities, intervals and its release policy. It must not insert a different destination or narrow a requested interval silently. It freezes a dispatch:

| Member | Type and binding |
| --- | --- |
| `profile` | Exact `mail-rendezvous-v0` literal. |
| `purpose` | Exact purpose stated below. |
| `id` | Nonzero random 16-byte lowercase-hex ObjectId, with its exact retained binding. |
| `offerDigest` | SHA256 of the named original payload bytes. |
| `sourceHome` | SHA256 of the original source home-authorization payload. |
| `targetHome` | SHA256 of the original target home-authorization payload. |
| `initiator` | Exact initiating endpoint object. |
| `target` | Exact target endpoint object. |
| `service` | Exact selected canonical HTTPS service origin. |
| `account` | Opaque 64-lowercase-hex service-account binding. |
| `link` | Exact active device-link ObjectId. |
| `nonce` | Fresh random 32-byte lowercase hex. |
| `notBefore` | Inclusive canonical uint64 Unix-seconds string. |
| `notAfter` | Exclusive canonical uint64 Unix-seconds string. |

Purpose is `rendezvous-dispatch`. Service/account/link match the source authorization. Its interval is contained in the offer and source authorization intervals. Source dispatch and account reset serialize in one transaction. Equal request ID and equal original submission recover the same dispatch; unequal bytes conflict. An invalid signature cannot occupy the collision key.

The destination checks its own blocks and admitted source-origin policy before doing source inspection or allocating peer work. A device-signed home record cannot add an origin to that operator admission policy or override its network egress restrictions.

The source forwards exactly `{submission,dispatch}` to target-prefix `POST /offers`; no OAuth, mailbox password, refresh token, queue bearer or installation credential crosses services. The destination validates both home authorizations and exact source dispatch signature using the delegated source serviceKey. It independently applies current own-account/link status, endpoint authority, admitted source-origin policy, intervals and destination disclosure/admission policy. TLS authenticates the endpoint; it does not supply these permissions.

A publicly discovered home authorization is a locator and constrained device delegation, not permission for arbitrary request volume. Destination account policy must explicitly enable this request class and decide admitted sources. The service applies finite deployment budgets and source accounting before persistent work. Numeric quotas are deployment policy, not requirements invented here.

Before admitting a new request, activating an answer, resuming a grant or disclosing a new status result, the destination checks that the exact source release remains active. It sends a signed inspection to the already delegated source prefix, never a caller-selected callback. The inspection payload has exactly these required members:

| Member | Type and binding |
| --- | --- |
| `profile` | Exact `mail-rendezvous-v0` literal. |
| `purpose` | Exact `rendezvous-inspect` literal. |
| `request` | Fresh inspection request ObjectId. |
| `id` | Original offer ObjectId, qualified by the retained authority namespace. |
| `dispatchDigest` | SHA256 of the exact original source dispatch payload. |
| `sourceHome` | SHA256 of the original source home-authorization payload. |
| `targetHome` | SHA256 of the original target home-authorization payload. |
| `nonce` | Fresh random 32-byte lowercase hex. |
| `notBefore` | Inclusive canonical uint64 Unix-seconds string. |
| `notAfter` | Exclusive canonical uint64 Unix-seconds string. |

 The target home signs with the serviceKey in the exact target authorization. `POST /dispatches/{id}/inspect` body is `{proof}`. The source validates the frozen target key, exact dispatch and interval, then under its own account authority returns TLS-authenticated `{profile,id,state}` with state `active` or `closed`. Unknown or retired releases return closed after valid scoped authorization; an invalid proof has no account-specific result. There is no public GET or account query. Unreachable inspection leaves the attempted new effect held; it does not mean unsupported encryption.

Inspection is an observation, not a cross-provider distributed transaction. If source revocation committed first, inspection must return closed. If revocation happens after a successful inspection, it cannot retract bytes already disclosed. The destination rechecks at each new effect; no lease may extend the offer interval. The sender independently checks current own authority before further content release. A service must not promise instantaneous global revocation or use an earlier active result as permanent account authority.

A valid transport submission receives `202 {profile,id,state:"pending"}`. This says only that the request was processed under the private admission boundary. It does not distinguish a missing, blocked, disabled or currently disconnected destination. A destination may retain a bounded negative replay receipt without creating a device queue entry. A later identical retry cannot turn this receipt into a fresh admitted request. No automatic email is generated.

::::

:::: {.details summary="The answer is the new exact grant"}

### The answer is the new exact grant

Bob's app reads his admitted pending offers through its own management connection. A connected device can answer automatically under its already enabled policy. It validates the original request, known-contact association or eligible first-observation enrollment, both current identity paths, exact target state, current homes and every original interval. A directory match alone is insufficient.

For a valid offer, Bob requests an answer preparation with exactly these required members:

| Member | Type and binding |
| --- | --- |
| `profile` | Exact `mail-rendezvous-v0` literal. |
| `request` | Fresh answer-preparation request ObjectId. |
| `link` | Exact active target device-link ObjectId. |
| `id` | Original offer ObjectId under its qualified authority namespace. |
| `offerDigest` | SHA256 of the original offer payload. |
| `dispatchDigest` | SHA256 of the original dispatch payload. |
| `notBefore` | Requested inclusive canonical uint64 Unix-seconds string. |
| `notAfter` | Requested exclusive canonical uint64 Unix-seconds string. |

His service returns retained original bytes for:

| Member | Type and binding |
| --- | --- |
| `profile` | Exact `mail-rendezvous-v0` literal. |
| `purpose` | Exact purpose stated below. |
| `preparation` | Nonzero random 16-byte lowercase-hex ObjectId, with its exact retained binding. |
| `request` | Nonzero random 16-byte lowercase-hex ObjectId, with its exact retained binding. |
| `grant` | Nonzero random 16-byte lowercase-hex ObjectId, with its exact retained binding. |
| `id` | Nonzero random 16-byte lowercase-hex ObjectId, with its exact retained binding. |
| `nonce` | Fresh random 32-byte lowercase hex. |
| `offerDigest` | SHA256 of the named original payload bytes. |
| `dispatchDigest` | SHA256 of the named original payload bytes. |
| `sourceHome` | SHA256 of the original source home-authorization payload. |
| `targetHome` | SHA256 of the original target home-authorization payload. |
| `initiator` | Exact initiating endpoint object. |
| `target` | Exact target endpoint object. |
| `path` | Exactly `home-ciphertext`. |
| `operations` | Exactly `["connection-resume","status-read"]`. |
| `notBefore` | Inclusive canonical uint64 Unix-seconds string. |
| `notAfter` | Exclusive canonical uint64 Unix-seconds string. |

Purpose is `rendezvous-answer`; preparation/request/grant are fresh IDs. `path` is exactly `home-ciphertext`. `operations` is exactly `["connection-resume","status-read"]`. These permit connection rendezvous only, not ciphertext upload, archive access or mailbox-copy suppression. The interval fits all original offer/dispatch/home/account/device intervals. The server may reject an unsuitable requested interval; it cannot silently change approved bytes.

Bob signs those exact prepared bytes. `PUT /offers/{id}/answer` with `{proof}` atomically checks the same linked account/family, retained preparation, exact signature, all current authorities and intervals, then activates the request-bound grant and records the immutable answer. Creation returns 201, identical retry 200, different valid bytes 409. Invalid answers leave the slot and preparation available. A signed answer is evidence of a device response, not MLS key confirmation.

If Bob was offline and never prepared an answer, no answer is manufactured by his home service. Existing published setup can still enable first-message encryption; the connection grant is not an encryption prerequisite.

::::

:::: {.details summary="Status, resume and cancellation"}

### Status, resume and cancellation

Alice signs a command exactly:

| Member | Type and binding |
| --- | --- |
| `profile` | Exact `mail-rendezvous-v0` literal. |
| `purpose` | Exact purpose stated below. |
| `command` | Nonzero random 16-byte lowercase-hex ObjectId, with its exact retained binding. |
| `id` | Nonzero random 16-byte lowercase-hex ObjectId, with its exact retained binding. |
| `action` | Exactly `status`, `resume` or `cancel`. |
| `offerDigest` | SHA256 of the named original payload bytes. |
| `dispatchDigest` | SHA256 of the named original payload bytes. |
| `answerDigest` | Original answer payload digest for resume; empty string for status/cancel. |
| `sourceHome` | SHA256 of the original source home-authorization payload. |
| `targetHome` | SHA256 of the original target home-authorization payload. |
| `initiator` | Exact initiating endpoint object. |
| `target` | Exact target endpoint object. |
| `nonce` | Fresh random 32-byte lowercase hex. |
| `notBefore` | Inclusive canonical uint64 Unix-seconds string. |
| `notAfter` | Exclusive canonical uint64 Unix-seconds string. |

Purpose is `rendezvous-command`; action is `status`, `resume` or `cancel`. For `status` and `cancel`, answerDigest is exactly the empty string; for `resume`, it is the original answer payload digest and the active grant must exist. Each command has its own immutable ID and bounded interval within the original offer. Resume does not produce a new grant or answer and does not claim that an endpoint remains connected.

The client sends `{proof}` to its own `POST /offers/{id}/commands`. The source service verifies current own authority and exact device signature, then signs:

| Member | Type and binding |
| --- | --- |
| `profile` | Exact `mail-rendezvous-v0` literal. |
| `purpose` | Exact purpose stated below. |
| `forward` | Nonzero random 16-byte lowercase-hex ObjectId, with its exact retained binding. |
| `id` | Nonzero random 16-byte lowercase-hex ObjectId, with its exact retained binding. |
| `commandDigest` | SHA256 of the named original payload bytes. |
| `dispatchDigest` | SHA256 of the named original payload bytes. |
| `sourceHome` | SHA256 of the original source home-authorization payload. |
| `targetHome` | SHA256 of the original target home-authorization payload. |
| `service` | Exact selected canonical HTTPS service origin. |
| `account` | Opaque 64-lowercase-hex service-account binding. |
| `link` | Exact active device-link ObjectId. |
| `notBefore` | Inclusive canonical uint64 Unix-seconds string. |
| `notAfter` | Exclusive canonical uint64 Unix-seconds string. |

Purpose is `rendezvous-forward`; forward is a fresh ID. It forwards exactly `{command,forward}` to destination `POST /offers/{id}/commands`. The destination verifies both signatures, frozen homes/participants/dispatch, current authority, operation scope and intervals before any read or mutation. A forwarded request cannot select another origin or account. The target service never follows a caller-supplied callback URL.

A successful command returns exactly `{profile,id,state,answer}`. `state` is `pending`, `answered` or `closed`; answer is an empty object for pending/closed and the original signed wrapper for answered. An answered response remains historical after answer expiry, but cannot activate/resume a path outside the original validity. On revocation, subsequent disclosure closes even if the response had previously been answered. Retain the internal cause and previously returned evidence; do not rewrite history. The same response shape does not assert that a device is online.

Valid signatures prove the recorded signing act, not continuous possession at every retransmission. A copied valid command/forward pair may replay the **same** authorized status request within its original interval. It cannot select a new action, recipient, interval or destination. Keep these proofs private under HTTPS and private storage; this profile must not claim session-bound proof or confidentiality against the authorized home services. A stronger sender-constrained HTTP binding is a separate choice, not silently supplied by Ed25519.

Use existing provider-control HTTPS, no-redirect, no-0-RTT, content-coding, no-store and error rules, under this new prefix and profile. Both own and destination routes use strict JSON. Invalid proofs return 400; absent own credentials 401; insufficient own scope 403; a valid altered collision 409; size/media/admission exhaustion use 413/415/429/503. Invalid destination authorization does not expose account-specific state. Public GET, account listing, peer-device enumeration and arbitrary polling-by-address do not exist. The exact selected descriptor limits apply; inherited queue numeric limits are not implicit defaults. A server may impose stricter transient work limits with429/503 without changing retained record identity or deadline.

::::

:::: {.details summary="Ordering, failure and several devices"}

### Ordering, failure and several devices

The source dispatch/replay namespace is `(rendezvous module, authenticated own account incarnation, exact initiating device/link, offer id)`. Equal original submission bytes recover the retained result; different authenticated bytes under that same key conflict. A public offer ID alone cannot select an account or reserve that namespace.

The destination namespace is `(rendezvous module, target account incarnation, original sourceHome payload digest, exact initiator principal/device, offer id)`. A valid request from a different qualified source has a separate namespace even if it reuses an observed ID. The remaining frozen bindings, including targetHome, endpoints, original submission and dispatch commitments, must match the retained record; a changed binding under one qualified key conflicts.

Use this same qualified destination key for offer admission, negative replay receipts, answer preparations/activation, commands, cancellation and inspection linkage. Every route carrying `{id}` must additionally match its authenticated original proof/digest bindings; the path ID alone cannot select or authorize another source's retained state. Pending-offer retrieval must preserve the qualifying original source/offer/dispatch bindings rather than collapsing records by ID.

Each target account serializes offer admission, answer activation, cancellation, device/link revocation and block updates against the same authoritative account incarnation and request namespace. Concurrent valid answers from the **same exact device** cannot replace each other. The first valid commit wins; equality means original bytes, not equivalent JSON. A cancel or revocation committed before answer activation prevents it. If answer activation commits first, cancellation stops future use/disclosure but cannot erase an already disclosed answer.

Identity receive-binding continuity permits a home authorization to remain eligible across unrelated accepted head advances under provider-grants' existing continuity rules. A live offer requests the exact target state named in its endpoint: a different target head requires a newly authorized offer after independently accepting that head. Repair, binding replacement, role removal, account reset or family retirement invalidate new use. No unsigned high revision or incoming record may overwrite a pin.

One offer names one exact target device. A sender may issue independently scoped offers to selected eligible devices; it cannot infer a wildcard roster. Different answers remain distinct. A response from one device neither unblocks another nor proves account-wide capability. Local UI may use one usable connection while retaining independently pending required devices. This rendezvous race never allocates or consumes an MLS package.

Before release, save the immutable request and original attempt deadline. A network timeout retains outcome uncertainty. Retry exact bytes or inspect with a new bounded status command; neither operation renews expiry, resurrects a grant, consumes a new package or restarts the human send. Loss of the fast path leaves already authorized encrypted mailbox delivery available. It never triggers plaintext downgrade. A new attempt requires an eligible local retry policy and new records while retaining the old uncertainty; it cannot extend the original send/setup policy silently.

::::

## Boundaries still owned elsewhere

This binding has no content upload route. A separate exact fast-delivery owner must bind the selected rendezvous transcript to packet transport, durable mailbox custody, endpoint acceptance and authenticated deduplication. A connection answer cannot suppress an SMTP copy or become a sent/read indicator. Same Message-ID alone is not authenticated duplicate evidence.

Direct WebRTC also remains unavailable until its exact protected signaling carrier, SDP/candidate encoding, authenticated DTLS fingerprint, privacy policy and ICE restart binding are specified. Existing provider queues and sealed-control/MLS operation parsers do not accept arbitrary new record kinds. Putting SDP on those paths without amending their owners is not an implementation of this proposal.
