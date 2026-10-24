---
title: Provider control wire profile
order: 10.3
blurb: configured grants · signed records · HTTP exchanges
sectionNav: true
---

# Provider control wire profile

This experimental profile carries a signed challenge and one signed device response through an authorized provider service. It gives implementers a common request format, retry behavior and division of responsibility. The [provider negotiation chapter](provider-negotiation.md) explains the user-facing behavior and privacy limits.

> [!ex] A response is lost
> Bob's client saves its signed response before uploading it. When the connection closes without a result, it uploads the same bytes again. The provider returns the saved exchange; Bob does not generate another key package, and neither client sends an automatic email.

> [!note] Configured experimental profile
> The identifier `en-provider-control-0` is local to this draft and unregistered. Account/service bindings, participant verification keys and distinct role credentials are provisioned through a trusted test configuration. The separate [public discovery profile](provider-discovery.md) selects domain delegation and native client registration. The separate [public grant profile](provider-grants.md) defines account/device links and queue-credential issuance; joined public deployment remains unimplemented. No complete service implementation or independent interoperability is claimed.

The profile transports discovery evidence, not message content. The initiator must independently validate the returned advertisement and any MLS admission material, then follow the security profile. A successful HTTP exchange is never key confirmation.

The [current Encryption baseline](suite-profile.md#current-client-baseline) uses [provider control2](#obtain-asynchronous-device-evidence) when this capability is offered. Current exchanges retain their original required agreement and assertion10. Retained version0/1 records remain exact; no old response is relabeled and no complete implementation follows from these bindings.

## Configuration and participant credentials

::: {.details summary="Configuration and participant credentials: implementation rules"}

Two distinct local authorizations are required:

1. An authenticated account configuration binds a service HTTPS origin and path prefix to a particular mailbox-service account. For the first experiment this binding is installed by an operator through the same trusted configuration channel used to provision a synthetic account. No inference from MX, From, DKIM, SMTP greetings or an unsolicited URL is permitted. A later JMAP capability/session extension can carry this binding only after its own schema and authorization profile is defined.
2. The service provisions one shared exchange grant for the exact account and ordered initiator/target device pair. Both devices retain its identifier and immutable configuration. It issues distinct per-participant bearer credentials, each bound to that shared grant and exactly one role (`initiator` or `target`). A credential never carries both roles. The service authenticates the token and resolves its role from server-side provisioning, never from a request field. It must not accept the mailbox password or a token intended for another origin. Peer credentials are supplied through configured provisioning in this experiment; no endpoint acquires them from email automatically.

A provider account administrator can authorize queue access but cannot thereby enroll an endpoint device in an Email/2 identity. Both clients already have the peer mailbox association and accepted identity state, including device receive authority; providers never replace these checks. The first experiment permits only one exact peer-device pair per grant and no wildcard recipients. A second device needs a distinct grant and validation. Mailbox reassignment/reprovisioning rotates the service account identifier and revokes old grants, without repinning the Email/2 identity.

For different providers, the initiator directly uses the target's configured service with its target-service grant; replies stay in that same exchange resource. No server federation, arbitrary callback URL, forwarding chain or credential forwarding is introduced. This is deployable in two controlled accounts, although convenient cross-provider grant acquisition remains a separate adoption problem.

The separate [service-federation architecture](service-federation.md) assigns
home-to-home rendezvous and fast delivery their own future exact bindings.
Existing queue credentials and endpoints cannot acquire those permissions merely
because two services support this control profile.

### Provisioning and role scope

The shared grant is immutable and identified by a random 64-lowercase-hex `grant` ID. Its service account ID is another opaque 64-lowercase-hex ID, not an email address or JMAP identifier. Configuration replacement requires a new grant ID; revocation prevents all subsequent access, including reads. Token renewal may preserve the grant and role but cannot change participants, origin, prefix, limits or expiry. Each token has its own expiry no later than the grant's expiry; tokens never appear in signed payloads or responses.

Role operation sets are exact: initiator `["configuration-read","request-write","exchange-read"]`; target `["configuration-read","pending-read","exchange-read","response-write"]`. These arrays use that order with no omissions, additions or duplicates in version 0. The role-specific configuration response exposes only the current credential's role and operation set. Storage keys are `(account,grant,id)`; an ID in a different grant cannot retrieve or collide with this grant's exchange. Separate credentials do not create separate exchange namespaces.

Provisioning also gives the service each participant's Ed25519 public key and its exact state/binding digests, obtained through the configured deployment's independently validated identity material. The service authenticates possession against these frozen verification inputs; it does not claim to follow the global identity chain. Clients still check their current accepted head and authority. An identity-state change requires a new configured grant in this initial profile. An old grant cannot bypass client checks even if the provider has not learned of revocation.

:::

## HTTP routes and representations

::: {.details summary="HTTP routes and representations: implementation rules"}

All routes below are suffixes appended to the configured `prefix`, which ends in `/`; remove the table's leading `/` before concatenation. No URI-reference resolution or normalization is performed. Reuse the service-answer contract's exact ASCII HTTPS origin/path spelling, TLS 1.3 baseline, DNS-ID certificate validation, no 0-RTT and credential isolation. HTTPS only, valid service identity, no redirects, no ambient cookies, no HTTP credentials from another account, no compressed representations in version 0. UTF-8 application/json, strict duplicate-key rejection and exact schemas; request/response Cache-Control: no-store. Each request includes Authorization: Bearer with the configured service-specific token. URLs have no mailbox address or secret token in them. IDs are 64 lowercase hexadecimal characters generated from 32 random bytes. Binary fields use the existing canonical padded base64 rule. Server must fully parse and authorize before mutation.

| Route | Access and behavior |
|---|---|
| GET /configuration | Either participant retrieves its shared immutable grant configuration plus its own role and exact allowed operations. Does not list other accounts or peers. |
| PUT /exchanges/{id}/request | Initiator only. Creates exact immutable signed request; 201 on creation, 200 on byte-identical retry, 409 on different bytes for the same grant/id. |
| GET /pending?after={cursor} | Target-device grant only. Returns bounded pending request IDs and next opaque cursor, without consuming them. No waiting or presence parameter. Cursors scoped to grant and account. |
| GET /exchanges/{id} | Either authorized participant. Returns immutable request, optional immutable response, and service lifecycle status. Unknown, unauthorized and expired nonretained IDs return the same 404 shape. |
| PUT /exchanges/{id}/response | Target device only. Commits one exact signed response; 201 first, 200 identical retry, 409 different response. No further exchange is created. |

All fields below are required; unknown members, missing members, wrong types and unknown enum values are invalid. Successful GET and identical PUT retry return 200; new PUT returns 201. Each successful PUT returns the same exchange representation as GET after the transaction. No request body is allowed on GET; PUT body is exactly the wrapper. Other methods return 405 with Allow. Unsupported media type or content coding returns 415. Error bodies have exactly `{error}`. The strings `invalid`, `unauthorized`, `notFound`, `conflict`, `tooLarge`, `unsupportedRepresentation`, `rateLimited`, `unavailable` map to 400,401,404,409,413,415,429,503. A malformed HTTP message may be rejected by the HTTP stack before this JSON contract applies.

Missing/invalid bearer credentials use RFC6750's applicable WWW-Authenticate challenge; a valid token lacking operation scope uses 403 and its insufficient_scope challenge, with `{error:"unauthorized"}`. Only authorized operations proceed to resource lookup; unknown/out-of-grant resources then return indistinguishable 404. Challenges cannot select a new credential destination. Errors never echo submitted content. HTTP 202 is not success. A timeout leaves outcome unknown; exact retry or GET resolves it.

Configuration exact object:

| Field | Meaning |
| --- | --- |
| `profile` | The exact profile identifier specified below. |
| `grant` | The immutable pair-grant identifier. |
| `account` | The configured provider account identifier; its owning account grammar applies. |
| `service` | The exact selected service origin. |
| `prefix` | The canonical configured control-service prefix. |
| `initiator` | The initiating device endpoint reference. |
| `target` | The target device endpoint reference. |
| `initiatorState` | Digest of the accepted initiator state named by the configuration. |
| `initiatorBinding` | Digest of that initiator device binding. |
| `targetState` | Digest of the accepted target state named by the configuration. |
| `targetBinding` | Digest of that target device binding. |
| `role` | The exact configured participant role. |
| `operations` | The exact operations allowed for that role. |
| `notBefore` | The start of the validity interval, using this record’s time grammar. |
| `notAfter` | The end of the validity interval, using this record’s time grammar. |
| `limits` | The complete limits object under the queue contract. |

`profile` is `en-provider-control-0`; IDs and digest fields have their declared 64-lowercase-hex syntax. Participant is exactly `{principal,device}` under existing identity grammars. `role` and `operations` obey the role sets above. All times are nonnegative safe JSON integers (at most 9007199254740991), and notBefore <= notAfter. Unlike the string-only event schema, this control schema deliberately uses integer timestamps/limits and the explicitly allowed null fields below; booleans and fractional numbers are never accepted. Depth is counted with root container at one.

`service` is the canonical HTTPS origin defined in service-answers.md: lowercase validated DNS host, no IP literal or trailing dot, omitted 443 port, otherwise canonical decimal port 1–65535, and no final slash. `prefix` is an absolute URI with exactly that origin and a nonempty path ending in `/`, no userinfo/query/fragment. Apply the same path rules: slash and ASCII unreserved characters, uppercase percent hex, no dot segments, encoded slash/backslash or encoding of unreserved characters. Reject noncanonical input rather than repairing it. Neither certificate identity nor a shared hostname authorizes another prefix or port. Implementations unable to validate an A-label hold configuration rather than accepting an arbitrary xn-- spelling.

Pending response is exactly `{profile,ids,next}`: ids is an array of distinct exchange IDs of length at most pendingPageSize; next is null or a 64-lowercase-hex opaque random cursor. Initial request is `pending` with no query. Subsequent request has exactly `?after=` followed by that cursor, without percent encodings or other parameters. Cursors are server-stored, bound to account/grant/target role, expire after cursorLifetimeSeconds, and contain no plaintext account data. The server paginates a snapshot of pending IDs taken on the first request; skip records no longer pending, return each surviving ID at most once in the snapshot. Each cursor identifies an immutable page position and stable successor cursor. Retrying it returns the same page, except that now-terminal entries may be omitted; retrieval never consumes or advances that cursor. New arrivals appear on the next fresh enumeration. A final null requires starting a new enumeration after the polling interval, not interpreting the queue as permanently empty. Expired or unknown cursors return 400 invalid without exposing another grant's cursor.

Exchange response is exactly `{profile,id,request,response,status}`; response is a wrapper or null, status is `pending`, `responded`, or `expired`. Pending and expired have null response; responded has the immutable response. Once responded, status remains responded even after evidence expires; use-time validity is checked separately. Successful exchange bodies must contain the exact stored request/response wrappers, although outer JSON serialization may differ. Clients compare wrapper payload/signature fields and retain received original bytes. Resource status is not signed device evidence.

GET responses and lifecycle status authenticate only the service origin. They are not transferable proof of device state. Pending cursors are pagination hints, not complete historical logs. Expired cursor returns 400 invalid; client restarts bounded pagination and deduplicates by ID. A service must keep all outstanding pending entries enumerable by a fresh snapshot until response/expiry, including across cursor restart.

:::

## Signed challenge and response records

::: {.details summary="Signed challenge and response records: implementation rules"}

Request and response wrappers each have exact fields `{payload,signature}`. `payload` is canonical base64 of original strict UTF-8 JSON octets; signature is the 128-character lowercase hexadecimal encoding of a 64-byte Ed25519 signature. Each payload is verified over ASCII `email-next/provider-control/v0`, one zero octet, four-octet big-endian payload length, and exact payload bytes. Record kind and participants provide additional purpose separation. Do not reserialize before verification.

Request exact fields:

| Field | Meaning |
| --- | --- |
| `profile` | The exact profile identifier specified below. |
| `kind` | The record kind specified below. |
| `id` | The exchange identifier; it must match the route. |
| `service` | The exact selected service origin. |
| `prefix` | The canonical configured control-service prefix. |
| `grant` | The immutable pair-grant identifier. |
| `account` | The configured provider account identifier; its owning account grammar applies. |
| `initiator` | The initiating device endpoint reference. |
| `target` | The target device endpoint reference. |
| `initiatorState` | Digest of the accepted initiator state named by the configuration. |
| `initiatorBinding` | Digest of that initiator device binding. |
| `targetState` | Digest of the accepted target state named by the configuration. |
| `targetBinding` | Digest of that target device binding. |
| `nonce` | The random challenge nonce, under the exact grammar below. |
| `notBefore` | The start of the validity interval, using this record’s time grammar. |
| `notAfter` | The end of the validity interval, using this record’s time grammar. |
| `purpose` | The exact purpose specified below. |

`profile` is `en-provider-control-0`; kind `challenge`; purpose `fresh-device-discovery`; service and prefix equal the configured origin and absolute prefix exactly; grant and account equal the shared configuration. State and binding fields are existing lowercase SHA256 payload digests. nonce is fresh 32-byte random lowercase hex. Times are integer Unix seconds under the existing uncertainty-interval rule. Request ID must equal route ID. Request signer must be the initiator device binding named under its accepted state and currently authorized to receive; this is a new narrow discovery-signing use of receive authority, consistent with passive discovery, not enroll/revoke/send authority.

Response exact fields:

| Field | Meaning |
| --- | --- |
| `profile` | The exact profile identifier specified below. |
| `kind` | The record kind specified below. |
| `id` | The exchange identifier; it must match the route. |
| `service` | The exact selected service origin. |
| `prefix` | The canonical configured control-service prefix. |
| `grant` | The immutable pair-grant identifier. |
| `account` | The configured provider account identifier; its owning account grammar applies. |
| `requestHash` | SHA256 of the original signed request payload bytes. |
| `initiator` | The initiating device endpoint reference. |
| `target` | The target device endpoint reference. |
| `nonce` | The random challenge nonce, under the exact grammar below. |
| `notBefore` | The start of the validity interval, using this record’s time grammar. |
| `notAfter` | The end of the validity interval, using this record’s time grammar. |
| `advertisement` | The target device’s complete original signed capability advertisement. |

kind is `device-evidence`. requestHash is SHA256 of the exact signed request payload bytes. All common binding values equal the request. For the version0 exchange defined in this section, advertisement is the complete original assertion8 wrapper under the [suite binding](suite-profile.md), with canonical mailbox spelling and the exact supported application offers, signed by the target device. A KeyPackage is optional for refreshing an established conversation; new admission requires its own usable package.

Earlier configured experiments use older nested advertisements and do not establish current-suite support. Response signer is that same target device. The advertisement's principal/device must equal target; mailbox must equal the independently configured target mailbox association; state/binding must equal the request's targetState/targetBinding and the target's current accepted head/binding.

The response interval must be nonempty: request notBefore <= response notBefore <= response notAfter <= request notAfter. Its notAfter also cannot exceed advertisement, binding or supplied package expiry. At response creation and new admission the entire trusted local clock interval must fit within both request and response intervals. Request interval must fit inside the configured grant interval; equal endpoints are permitted syntactically but cannot be used unless the full clock interval fits. No generic `supported:true`, account device list or service-signed substitute is allowed.

The initiator verifies its locally outstanding exact request, response signature, current device authority, request hash, nonce, purpose and complete current uncertainty interval inside both validity intervals. It then independently validates the advertisement, identity and package through existing validators. A provider replay cannot satisfy a new challenge. A provider signature or TLS connection cannot replace the device signature. Invalid or different unsolicited replies do not cancel a valid outstanding request or poison an established identity.

If the target has moved to another accepted state, it must not sign evidence for the requested old state. This version leaves the challenge unanswered until expiry; normal independent identity evidence can advance the initiator and permit a separately authorized new challenge. If the configured grant freezes the former target state, this also requires a fresh exact pair grant/configuration approved under its own policy; preserving an old grant’s unchanged-binding authority does not edit its requested state or produce a live target response. The [purpose-specific continuity rules](provider-grants.md#continuity-and-freshness-have-different-scopes) distinguish original evidence from that new live authorization. No in-band replacement-key shortcut. This conservative choice trades progress for a small auditable first contract.

:::

## Validation and transaction order

::: {.details summary="Validation and transaction order: implementation rules"}

**Service request admission:**

1. Enforce HTTP framing/body/header limits and authenticated TLS
2. Authenticate token, expiry, role and configured grant, then rate limits
3. Parse bounded wrapper and payload, reject duplicate decoded names and invalid exact schemas/encodings
4. Compare route ID, account, grant, origin/prefix, participants, purpose, state/binding and interval to immutable provisioning
5. Verify Ed25519 using the provisioned initiating key
6. Atomically check retained exact wrapper identity, lifetime and all admission budgets, then create or return the unchanged stored record.

Signature-valid does not mean the provider verified mailbox ownership. No credential holder can enqueue unsigned traffic for the peer to verify later.

Exact retry means byte-identical original PUT wrapper body, not merely equal parsed JSON; clients retain that body. Collision is checked only after authentication, schema and signature checks, so an invalid forgery cannot cause an authoritative conflict. A retained identical request may be retrieved after expiry while the credential/grant still permits access, but cannot be enqueued again. New expired requests are rejected. Records lost in a service restore must not be treated as absent: disable writes for affected grants until reconciliation or revoke them and provision new grants.

**Target client:** retrieve through its configured service; retain candidates without effects; validate wrapper/schema/context, initiating signature and current accepted initiator state/binding/receive authority independently of service admission; validate its own current target state/binding and all times. Check that the exact request is locally authorized and not already answered. Construct fresh passive evidence and optional package, independently validate them, sign and durably record the exact response before upload. Recheck current authority immediately before signing. An invalid request produces no protocol response. Service omission or forged lifecycle metadata cannot compel a response.

**Service response admission:** repeat transport/token/role/bounds checks, resolve existing request in the same account/grant, parse exact response and require requestHash and all shared context to match. Verify response with provisioned target key; validate its lifetime and nested advertisement's wrapper/schema, target signature and named fixed state/binding. The provider does not validate or consume MLS KeyPackages and cannot assert their suitability. Atomically commit one response only while request is pending and usable; exact retained retries return the stored result after expiry, different authenticated responses yield 409 without replacement. Unknown requests produce 404 and expired unanswered ones yield 409 without transition. A malformed nested advertisement cannot occupy the one response slot.

**Initiator client:** compare result with its durably retained outstanding request, including exact payload hash and wrapper; verify target response signature with current accepted binding, all context/nonce/time fields and identity state. Independently run passive advertisement and MLS package validators, treating evidence bundles under their own identity rules. Check current authority again at protected-send/admission transaction. A valid earlier response is not refreshed by retrieval, replay or service time. Do not use service status, request admission or provider key pinning as a substitute for these endpoint checks.

:::

## Limits, retries and retention

::: {.details summary="Limits, retries and retention: implementation rules"}

States are pending → responded or pending → expired. Responded is immutable; expiry prevents new use but does not turn prior evidence into a new response. Device validation results are local and distinct from service status. Retry of an admitted request never extends notAfter, enqueues it again, mints another admission package or generates another response. Responders durably retain the exact response before PUT so a lost HTTP reply cannot cause new package generation. Duplicate response does not produce an acknowledgement.

The configuration's `limits` object has exactly the fields below, all positive safe JSON integers. Values shown are editorial experiment defaults, not user requirements or universal email quotas. Each grant freezes its selected values. There are no implicit omitted defaults. The client rejects internally inconsistent limits or a configuration that cannot carry its evidence.

| Field | Proposed value | Meaning |
|---|---:|---|
| maxWrapperBytes | 262144 | Exact UTF-8 PUT wrapper body, before JSON decoding |
| maxResponseBytes | 1048576 | Entire configuration/pending/exchange HTTP response body |
| maxJsonDepth | 32 | Every parsed wrapper, payload and response |
| pendingPageSize | 32 | Maximum returned IDs |
| maxPendingPerGrant | 8 | Pending exchanges, atomically enforced |
| maxRequestLifetimeSeconds | 120 | notAfter minus notBefore |
| maxClockUncertaintySeconds | 5 | Maximum width of local trusted clock interval |
| newRequestsPerMinute | 10 | New admitted requests per shared grant, rolling 60 seconds |
| requestsPerMinute | 60 | All authenticated HTTP requests per credential, rolling 60 seconds |
| minPollIntervalSeconds | 5 | Minimum gap between starts of fresh pending enumerations |
| cursorLifetimeSeconds | 120 | Snapshot cursor lifetime, never extended by use |
| retentionSeconds | 86400 | Exact records/tombstones retained after request notAfter |
| maxActiveCursorsPerGrant | 8 | Concurrent enumeration snapshots, not individual page tokens |
| maxPendingPerAccount | 64 | Aggregate pending across grants |
| newRequestsPerAccountPerMinute | 100 | Aggregate new admissions across grants |
| maxPendingPerService | 1024 | Aggregate deployment pending |
| newRequestsPerServicePerMinute | 1000 | Aggregate deployment admissions |
| failedAuthenticationPerSourcePerMinute | 30 | Failed authentication attempts per server-observed source IP; not untrusted forwarded headers |

The service may configure other finite values before issuing a grant. Account/deployment aggregate values must agree across its active grants; changing them requires reissuing affected configurations. Limits apply before allocation whenever possible; total wire bodies are bounded before parsing, then decoded payload and depth checked before cryptography. Canonical base64 ensures a decoded payload cannot exceed maxWrapperBytes. maxResponseBytes must accommodate two maximum wrappers plus 4096 bytes of exchange overhead; otherwise provisioning fails. Each cursor snapshot contains no more than maxPendingPerGrant IDs.

Return 429 with Retry-After as positive decimal seconds for exhausted rate, pending or cursor budgets; select the earliest known opportunity, or minPollIntervalSeconds if release depends on other work. Clients wait at least that value, may add bounded local jitter, and do not auto-create a replacement exchange. Local request authorization and expiry still bound retries. Token failures are accounted before signature work; deployments also need finite transport connection/header budgets configured in their HTTP server. Those HTTP implementation limits are not wire-level negotiation fields. Retention storage follows maximum admitted exchanges over the lifetime-plus-retention window; provision enough capacity or reject new admissions rather than evicting replay records. Poll page requests consume request budgets but do not reset the fresh-enumeration timer.

Server rejects expired creation and any request extending beyond grant expiry. After response or expiry, keep immutable bytes and replay tombstones until retentionSeconds after request expiry; afterwards reject all attempts with that ID carrying its expired signed times. Durable local initiator/responder records prevent reusing an ID/nonce for a new exchange. Bound tombstone storage by admission quotas; never evict pending replay protection to accept more work. Disconnection, service restart and timeout preserve the last accepted identity and existing protection policy.

There is no online/offline field, last-seen timestamp, delivery/read receipt, public lookup, callback or peer-push subscription. A valid device response inevitably reveals to the authorized initiating device that the signing device processed this challenge within its validity window; grant UI must explain that narrow disclosure. Polling alone must not reveal it to peers. Services see account pairs, timings, public evidence and response size; this version does not hide metadata or public discovery records from providers. Do not put user message text, contact lists or private keys in this channel. Revoking a grant stops future control access without retracting an already obtained response or authorizing plaintext fallback.

The service queue is separate storage, never a mailbox folder or message subject convention. Receiving arbitrary email cannot create a grant or initiate a challenge. Unknown/invalid requests never trigger mail, HTTP callbacks or third-party requests. A responder makes at most one response to a locally authorized pending challenge; a response is never itself eligible for response. Thus the two-message state machine terminates without relying on legacy client suppression behavior.

:::

## Implementation and acceptance boundary

The [record validator experiment](evidence/README.md#configured-provider-record-validation) checks configuration and actual signatures, with use-time validity separate from retained-record inspection. The [durable exchange store](evidence/README.md#durable-provider-exchange-storage) additionally tests immutable requests/responses and retries across restart. Neither component implements an HTTP service or establishes endpoint authority; The [local HTTPS adapter](evidence/README.md#configured-provider-https-adapter) joins configured bearer roles to the validator and store, including HTTP request budgets. Public queue-credential issuance/revocation is [specified separately](provider-grants.md) but not joined to this adapter; retention cleanup and restore handling remain unfinished; [domain delegation and public native-client registration](provider-discovery.md) have a separate proposed contract and bounded validation evidence. The store tests admission quotas and bounded snapshot pagination.

A reference service must preserve grants, immutable exchanges, responses and replay state across restart. Two client processes must demonstrate exact retries after lost replies, role separation, response-before-request rejection, expiry, account reassignment, bounded pagination and resource exhaustion. Invalid records must not cause mailbox messages, callbacks or credential forwarding.

The positive integration test uses a real validated KeyPackage from a response in the existing MLS invitation flow. Admission, protected delivery and confirmation must succeed independently of the provider's HTTP status. The queue does not reserve or consume the package. A competing invitation must still respect single-use admission.

Public deployments additionally need integration of the selected [queue-grant lifecycle](provider-grants.md) and [service discovery binding](provider-discovery.md). The [automatic first-contact exchange](bootstrap.md) defines separate unknown-peer authority; this pair-grant protocol cannot authorize an unknown sender by itself. [Freshness policy](freshness.md) binds a validated current-suite response to its original local operation, age anchor and release checks; older nested-advertisement experiments are not that complete adapter. The configured bearer mechanism inherits the [service-answer credential limitations](service-answers.md): token theft is not prevented by response deduplication, and this selected bearer profile does not supply sender-constrained credentials. Any future sender-constrained capability requires its own exact binding; it cannot be inferred from a device signature or deduplicated response. The [TLS 1.3](audits/tls13.md), [service identity](audits/service-identity.md), [HTTP](audits/http-semantics.md) and [automatic-response](audits/automatic-responses.md) audits describe related inherited boundaries; their existence is not implementation evidence.


## Reply-aware known-pair exchanges

A known-pair provider exchange can obtain the exact device evidence needed for a declared reply policy. Both sides retain the requested agreement throughout the exchange. Provider acceptance still does not establish encryption, human verification or delivery of a human message.

::: {.details summary="Exact successor configuration, proofs and device checks"}

The profile is `mail-provider-control-v1`, selected only through [descriptor1](provider-discovery.md#reply-aware-queue-discovery) or independently trusted exact configuration. Configuration has exactly the profile0 fields plus required `agreement`, with agreement `"mail-conversation-v1"`. Its profile is the new literal. Initiator/target roles, exact operation arrays, account/grant/device/state/binding/limits, safe integer times, prefixes and authoritative active-account/family checks remain unchanged. Old and new grants remain immutable; allocate a fresh grant/configuration for a profile change rather than editing a retained pair.

Challenge and device-evidence payloads each have exactly their profile0 member inventory plus required `agreement`, and profile equal to the new literal. Agreement is exactly `"mail-conversation-v1"` and equals the current immutable configuration. Their signature domain is `mail/provider-control/v1`, using the unchanged Ed25519 NUL/U32-length/original-byte framing. Wrappers remain exactly payload/signature. The request's original context, nonce, target state, interval and source role bind the response as before.

The response advertisement is exactly one original assertion9 wrapper. Independently validate its signature/domain, current accepted target identity/receive authority, mailbox association, exact requested state/binding, original validity/control-key promises and complete reply-aware operation offers. It must contain the selected context9 application before it can supply receiving support. A package remains optional for capability refresh; admission still needs its own usable material. No tuple from assertion8, provider status or remembered boolean can supply assertion9 support.

HTTP methods, suffixes, no-store representations, bounded work, pending/response states, immutable exact PUT retry and original requestHash correlation retain their meanings. Configuration and exchange responses use the new profile literal; the exchange representation otherwise keeps exactly its existing fields. No additional agreement field is inserted into the unsigned exchange wrapper: its immutable request/response and active configuration bind that value. Select the exact profile before parsing or signature verification; never try profile0 after a failed profile1 check.

Every queue mutation/read retains current token/account/grant/role and device checks. Reset, unlink, family revocation, expiry, source blocking and restored-store uncertainty cannot be bypassed by switching profile. A target-head change requires the original protocol's fresh evidence/new authorized pair preparation, not reinterpretation of cached support as a live response. Exact lost-result retrieval never refreshes the original proof interval.

After validation, run the [reply-aware handoff](first-contact-setup.md#reply-aware-acquisition-and-handoff) with every intended assertion9, current authority and original local intent revision. The queue result cannot release content, promote identity verification, change reply intent or invent group membership. Complete successor account/pair authorization, HTTP and admission integration remain implementation/acceptance obligations.

:::


## Obtain asynchronous device evidence

The known-pair queue can request the asynchronous agreement without waiting for every invitee. Each exchange concerns its exact known target device. A valid result can help one actual delivery progress while other recipients remain pending.

::: {.details summary="Exact control2 records, evidence and retry boundaries"}

Select `mail-provider-control-v2` through [descriptor2](provider-discovery.md#discover-the-asynchronous-agreement) or independently trusted exact configuration. Configuration has exactly control1's member inventory, with profile `"mail-provider-control-v2"` and agreement `"mail-conversation-v2"`. All original service/prefix/account/grant, endpoint/state/binding, role/operation, limits and safe JSON integer time rules apply. A fresh exact configuration/grant is required; no retained grant is edited into this profile.

Challenge and device-evidence payloads have exactly their control1 member inventories, including required agreement. Profile and agreement use those same two literals. Sign the exact original payload bytes under `mail/provider-control/v2`, followed by NUL and the existing U32 big-endian payload length/original-byte framing. Wrappers remain exactly payload/signature. Purpose, current receive-role signing, request ID, requestHash, target state/binding, nonce, interval and grant/role correlation retain their original requirements.

The response advertisement is one complete original assertion10 wrapper under its independent `mail/passive-discovery/v10` signature. Validate current target identity/receive authority, exact configured canonical mailbox, request state/binding, original validity/control-key promises, package material and the complete [assertion10 offers](suite-profile.md#asynchronous-protected-agreement). Its chosen ordering must project to the fixed context10 application. Retain the device's interactions; do not apply the older optional-block intersection. A missing package may suffice for capability refresh, but not admission requiring a package. No earlier assertion, provider status or remembered capability supplies this evidence.

HTTP routes/methods and bounded no-store representations retain their exact control1 shapes. Configuration and exchange representations use profile mail-provider-control-v2 wherever their owning schema has a profile. The unsigned exchange wrapper gains no agreement field: the active configuration and original signed request/response already bind it. Parse only the selected branch; failed control2 verification cannot activate an older branch.

Current token/account/family/grant/device/role checks and serialized revocation apply to each operation. Target-head change cannot be answered as the old head; independently obtain current evidence and authorize any required new pair. Version does not reset request/conflict namespaces, source blocks, limits, deadlines, restored-store holds or uncertain results. An exact response retry returns its retained bytes, not a new package or fresh timestamp.

Pass accepted evidence to the [per-delivery handoff](first-contact-setup.md#acquisition-for-independently-ready-deliveries). The result does not bind an unresolved invitation slot, alter the authored audience, install native membership, satisfy human verification or release content. Other pending exchanges do not block an independently eligible delivery under the selected progression policy.

:::
