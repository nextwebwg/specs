---
title: Answers sent to a service
order: 3.5
blurb: HTTPS buttons · service receipts · safe retries
sectionNav: true
---

# Answers sent to a service

A question can offer buttons that send an answer to a named HTTPS service. The client shows where the answer goes, submits only the declared choice, and keeps the service's result separate from the person's answer.

> [!ex] Choose a meeting day
> An invitation offers **Tuesday** and **Thursday**, with a scheduling service named as the destination. Bob presses Thursday. His client sends the selected option and the identifiers needed to authorize that answer; it does not send the email body or earlier conversation.
>
> If the connection drops, the client shows that confirmation is missing. It checks or retries the same submission instead of choosing a new identity or sending an email that could perform the action twice.

> [!warn] Experimental configured-deployment profile
> Version 0 specifies a candidate wire contract for an explicitly configured experiment. It is not a complete cross-provider authorization standard, and the local parser experiment does not implement service authorization or execution. The service-question operation below defines descriptor carriage. The separate configured execution experiment covers authenticated local requests, effects and receipts. The joined signed-mail experiment now connects an accepted question to a deliberate service action and matching HTTPS receipt. The separate [service-account authorization profile](service-authorization.md) defines native sign-in and a device-signed principal link; deployed account integration and independent interoperability remain unproven. Supporting ordinary conversation buttons does not imply support for this service capability.

## Before a button can submit

A service-question contribution contains the action descriptor that binds its exact question to a service origin, submission URI, status URI prefix and validity interval. Authentication covers the descriptor together with the question text and choices. Ordinary conversation questions keep their existing schema and behavior.

The service separately holds the action's allowed choices and answering principals. A question can propose a destination but cannot grant authority there. The client also needs an independently established configuration and a service-specific bearer access token. A forwarded invitation supplies neither.

If configuration or authorization is unavailable, the service action waits. Ordinary contact or separately chosen website navigation can remain available; receiving mail must not trigger a search for credentials at a sender-supplied URL.

## The service question

A service question offers the same predefined choices as a conversation question, but sends the selected answer to the named service. An ordinary email reply can still contact the author; it does not confirm a service action. A client without service support shows the readable invitation and leaves the service control unavailable.

::: {.details summary="Service-question operation and authenticated self-reference"}

### Service-question schema

The existing contribution envelope accepts a distinct operation with exactly four required members:

| Member | Value |
| --- | --- |
| `kind` | Exactly `service-question` |
| `text` | Nonblank Unicode scalar-value string, using the ordinary question rules |
| `options` | Nonempty ordered array of exact `{id, label}` objects; unique nonzero ObjectIds and nonblank scalar-value labels |
| `serviceAction` | The complete action descriptor defined below |

The descriptor's question reference MUST exactly equal the enclosing event's principal, conversation and event identifiers. Check this at envelope validation, after validating both shapes. A descriptor naming another event, author or conversation invalidates the binding. Allocate identifiers before serialization; the self-reference names identifiers, not a content digest, so it introduces no hash cycle.

Serialize the complete event once. Its authenticated octets cover text, options and the nested descriptor together. Re-serializing the descriptor alone cannot recover its original authenticated representation. Changing an endpoint or option mapping under the same event identity creates conflicting event bytes; it does not update the question. New arrangements require a new question and independently authorized service action record.

Existing conversation answer events resolve only to ordinary question operations. They MUST NOT enter a service question into the conversation answer graph. A service selection produces a service submission identity under this chapter; its replacement reference is a service submission identifier, not an EventReference. Deliberately sending an ordinary message about a service question remains separate from service execution.

Before enabling the control, validate the enclosing event's protection, author, audience, identity continuity and the separate service authorization. Receiving, storing or projecting the event performs no request, token acquisition or registration. An encrypted contribution keeps the descriptor inside the same protected boundary as its question.

:::

### Readable invitation

Both readable alternatives contain the question, every choice in authored order and the exact service origin. They explain that direct submission needs a compatible configured client, that an ordinary email reply contacts the sender without confirming service execution, and that opening the message submits nothing. Generated HTML escapes these values as inert text; client-owned controls appear only after authorization.

Do not turn the submit or status endpoint into a browser answer-page link. This schema defines no public website fallback URL. It does not copy credentials, request bodies or conversation history into the invitation. Ordinary contact and separately chosen navigation remain available under their existing rules.

::: {.details summary="Action descriptor schema and exact HTTPS destinations"}

### Binding the action to the service

The serviceAction member contains one descriptor within the original authenticated contribution bytes. It has no separately signed JSON serialization. An unsigned MIME header, mutable webpage or inferred domain cannot provide or replace this binding.

Descriptor members are exactly:

| Member | Required value |
| --- | --- |
| `version` | String `0` |
| `purpose` | String `service-answer-action` |
| `action` | Nonzero ObjectId allocated by the service |
| `question` | Exact EventReference to the immutable question |
| `service` | HTTPS origin serialized as specified below |
| `submit` | Exact absolute HTTPS URI for POST |
| `statusPrefix` | Absolute HTTPS URI ending in `/`; append only the submission ObjectId for GET |
| `notBefore`, `retryUntil` | Canonical unsigned-64 UTC epoch-second strings; retryUntil is not earlier than notBefore |

Both URIs must have exactly the service origin, no userinfo, query or fragment, and a nonempty absolute path. The v0 experimental URI spelling is ASCII: lowercase DNS host with validated A-labels, no trailing dot or IP literal; port omitted for 443, otherwise canonical decimal 1–65535. Paths use `/`, ASCII unreserved characters and percent-encoded octets with uppercase hex; reject dot segments, percent-encoded slash/backslash and percent encodings of unreserved characters. No parser normalization or redirect may select another endpoint. This deliberately narrow spelling needs shared parser fixtures; it is a profile restriction, not the full HTTPS URI grammar. The `service` value is `https://` plus host and optional port, without a final slash.

**Why exact spelling matters.** Two URLs can identify the same resource without carrying the same authorization. A client must not repair a received endpoint, follow a redirect or infer permission for a neighboring path. The service and any reverse proxy must preserve the authorized endpoint through routing: splitting components precedes decoding, and repeated decoding must not turn path data into new separators. For example, `%252F` is not permission to route to `/`. These restrictions build on the parsing and comparison rules in [RFC 3986 §§2.4, 6.2 and 7.3](https://www.rfc-editor.org/rfc/rfc3986.html#section-2.4); ordinary website navigation does not grant service-action authority.

**Provider-controlled paths.** The provider chooses `submit` and `statusPrefix`; `/submit` and `/status/` in examples reserve no paths. A client uses the supplied, authorized values and never guesses endpoints from a hostname or path name. Appending a submission identifier is allowed only beneath the provider-selected `statusPrefix`. This follows [RFC 8820 §2.3](https://www.rfc-editor.org/rfc/rfc8820.html#section-2.3): an application can define resources beneath a deployment-controlled prefix.

The action author can propose where the answer should go, but cannot grant authority at that service. The service independently holds an action record mapping `action` to the exact question, allowed option identifiers, authorized answering principals, lifetime and replacement policy. A request cannot create that record. The client displays the bound service origin before the user presses a button. No user-facing display name substitutes for that origin.

An existing trusted configuration must bind the client to this service and credential audience. Received metadata cannot establish a new credential issuer, token endpoint, OAuth client registration or mailbox-principal mapping. If that configuration or credential is unavailable, hold the service action and offer ordinary contact or separately chosen website navigation; do not probe arbitrary token URLs from mail.

:::

::: {.details summary="Bearer credential and principal-authorization requirements"}

### Credential baseline and authority boundary

For an isolated v0 deployment, use an existing service-specific bearer access token in the HTTP Authorization header, under a separately established authorization arrangement. Require the service to validate its intended resource/audience, validity, issuer and operation scope, and map the authenticated subject to the exact enp0 principal used by this action. If the token format does not encode those properties, the service's authoritative token record must provide them. Token possession alone does not allow the request body to choose an arbitrary principal.

No token is included in the question, action descriptor, request JSON, status URL or conversation receipt. A forwarded message must not carry the grant. Do not send mailbox passwords, ambient browser cookies, ambient HTTP authentication, client certificates selected from ambient identity, or tokens for another service. The initial configuration supports only this explicit bearer mechanism; provider-specific tokens are not automatically compatible. Browser cookies are omitted even on a same-origin request. Token renewal preserves the original submission bytes and identity.

Generate `Authorization: Bearer <token>` with one ASCII space. Keep the token opaque; its grammar is not a requirement for canonical base64 decoding. Missing or unusable credentials require a Bearer `WWW-Authenticate` challenge. Distinguish malformed requests, invalid tokens and insufficient scope using the existing challenge/error rules. Challenge text cannot authorize a broader grant or redirect credential acquisition. Token expiry is separate from submission retry validity; renewal preserves the exact submission. These requirements use [RFC6750 §§2–3](https://www.rfc-editor.org/rfc/rfc6750.html#section-2), together with the reviewed TLS and OAuth security updates.

This uses existing HTTPS and bearer-token concepts rather than a new cryptographic protocol. The [bearer-token audit](audits/bearer-token-usage.md) and [OAuth security update audit](audits/oauth-security.md) define the applicable resource-access boundaries. The [selected native authorization profile](service-authorization.md) defines credential acquisition and principal association. Sender-constraint integration and production platform browser authorization remain separate boundaries; a local implementation does not establish cross-provider support. A preprovisioned test token can exercise the wire contract without resolving those issues.

:::

## Protect the service credential

The service checks the token's audience, resource and permitted action on every submission and status request. A matching client-side destination is not a substitute for those checks. Principal mapping must distinguish the person authorizing an answer from a software client's identity; a client-controlled identifier cannot claim another person's Email Next principal.

The configured experiment uses an ordinary bearer token. Anyone who steals it may exercise its grant. Submission deduplication prevents repeating one retained operation; it does not stop a thief from allocating a new submission. Current [OAuth security guidance](audits/oauth-security.md) recommends sender-constrained access tokens. This experiment does not implement that recommendation and must not claim full current OAuth security conformance. An Email Next event signature does not by itself bind a service token to its sender. A production profile needs a selected, audited binding such as DPoP or mutual-TLS token binding, or an explicit deployment assessment of the remaining bearer risk.

Keep access tokens out of logs and unprotected persistent storage or backend links. A TLS-terminating proxy must discard untrusted security headers before providing its authenticated context to the service, and protect its backend connection from disclosure, injection and replay. Access-token expiry, action expiry and submission-result retention are separate lifetimes.

Credential acquisition must not use the resource-owner-password grant. The selected native authorization-code client requires S256 PKCE and its downgrade protections; public-client refresh tokens require rotation or sender constraint. The separate authorization chapter owns the selected grant and mapping contract. The action descriptor cannot provide a new authorization issuer, expand a grant, or replace an independently configured identity mapping.

## Establish the protected connection

The service path requires support for TLS 1.3 and selects it as the default, following [RFC9852 §§4–5](https://www.rfc-editor.org/rfc/rfc9852.html#section-4) for new protocols. This version defines no TLS 1.2 compatibility mode. A failed connection cannot trigger transmission of the credential or answer over an older protocol or plaintext. This service-only requirement does not change ordinary email transport. A version choice alone does not establish correct certificate validation, service identity or implementation configuration; those checks remain mandatory.

Version checks apply to the negotiated protocol, not a packet-prefix guess. Compatibility values in a ClientHello record header do not permit negotiation of a prohibited version. Test both failed old-only endpoints and accepted connections through the selected TLS implementation before claiming this behavior.

The client validates the intended service hostname and certificate chain before sending credentials or application data. Construct one DNS-ID reference from the independently authorized service origin’s host and match a dNSName subjectAltName in the server certificate under [RFC9525](audits/service-identity.md). Common Name fallback is forbidden. Do not substitute a CNAME, resolved IP address, mailbox domain or certificate-selected name. This DNS-host-only service profile does not use IP-ID, SRV-ID or URI-ID; an HTTPS URL does not require URI-ID matching. A certificate match does not authorize the path, port, action or token audience. SNI alone does not establish service identity. The service uses the selected HTTP protocol's ALPN behavior; this profile allocates no new ALPN identifier. Equivalent identity and protection requirements apply across load balancers and backend instances, as described in the [TLS configuration audit](audits/tls-configuration.md).

Certificate wildcards follow RFC9525: one complete leftmost label, matching exactly one label. Ignore invalid wildcard identifiers. Compare ASCII labels without case differences after validated IDNA processing; an arbitrary `xn--` spelling is not a validated A-label. Name mismatch or certificate-validation failure leaves the service submission unsent; this profile offers no click-through override for credentialed requests. Certificate-path validation, validity, name constraints, usage and revocation policy remain required independently of name matching.

::: {.details summary="Certificate paths and revocation"}
The service client validates a path to an independently trusted anchor, including applicable signature, validity, name-constraint, CA, path-length, policy, usage and critical-extension checks. Downloading an issuer certificate does not make it a trust anchor. A certificate or message cannot supply its own trusted root. Subject and authority key identifiers help locate candidate keys; they are not authentication proofs. See the [certificate-path audit](audits/certificate-path.md) and [profile corrections](audits/certificate-corrections.md).

Revocation processing must account for explicit standards-defined exceptions. Under [RFC9608](audits/no-revocation.md), a valid `noRevAvail` extension skips the revocation-status step for that certificate; it does not skip other validation or checks on the rest of the path. The client rejects a certificate combining this extension with CA status, CRL Distribution Points, Freshest CRL or an AIA OCSP access method. Missing status URLs alone are not an equivalent assertion. `ocsp-nocheck` belongs to the separately specified OCSP responder context and is not a general HTTPS leaf exemption.

Certificate status follows the two modes, freshness rules and backend requirements below. The [OCSP and certificate-status audit](audits/certificate-status.md) records their selected source basis. The existing TLS helper does not yet implement this complete status contract.

Certificate-domain processing follows the [current internationalization update](audits/certificate-internationalization.md): retain A-labels for validation and constraints; Unicode display conversion is separate. Selecting a DNS-ID for HTTPS does not remove applicable constraints on other certificate names, including [internationalized mailbox names](audits/certificate-mailbox-names.md). A certificate email name does not establish an Email Next device or replace the service reference host. The TLS experiment accepts A-label hosts only with the explicitly configured coherent Unicode provider; [setup and validation](evidence/IDNA17.md) are separate from certificate-path assurance.

Certificate-policy processing follows [RFC5280 as updated by RFC9618](audits/policy-validation.md). Prefer the bounded policy graph and constrained policy-set outputs; reconstructing every path to produce the old tree can reintroduce excessive work. Disabling policy checking does not permit ignoring critical policy extensions: reject them in that configuration.

If CRLs provide status, apply the [RFC10007 signer-authorization update](audits/crl-key-usage.md). A version 3 CRL issuer certificate must contain Key Usage asserting `cRLSign`, with its path validated to the same trust anchor as the target certificate. The explicit version 1/2 exception does not waive path or signature checks. This is a CRL-signer rule, not a requirement for the service's HTTPS leaf to sign CRLs.

Certificate and handshake signature requirements are specified below; the [RSA certificate review](audits/rsa-certificate-signatures.md) records selected verification dependencies.

Path validation is not blanket enforcement of every certificate-issuance recommendation. Apply the updated validation rules rather than converting all issuer guidance into client rejection conditions. Root-constraint processing and current policy-validation updates also need explicit implementation evidence.
:::

This profile does not send submissions, status requests or credentials as TLS early data (0-RTT). Wait for the authenticated handshake to complete. This is an Email Next restriction: the general TLS guidance allows application-specific early-data analysis, while this profile defines no such replay contract. Application deduplication is not a substitute for that analysis. Session resumption must meet the certificate-status and reuse restrictions below, preserving service identity and current credential policy with protected ticket state. No connection failure permits inventing a new submission identity. Keep resumption tickets within their authenticated service and deliberately isolated application context. A TLS key update is not recovery from a compromised traffic secret. Transport closure, a TLS alert or a completed handshake does not establish the outcome of a submission; only the matching application result can do that. The [current TLS 1.3 audit](audits/tls13.md) separates these application boundaries from the TLS library’s protocol obligations.

### Certificate algorithms and validation backend

Use a maintained certificate-validation backend with an explicitly selected, versioned security policy and independently configured trust anchors. The same authenticated connection that passed validation must carry the request. A separate successful connection or a parsed certificate supplied by the application is not sufficient. Complete the certificate, service-name, status-mode and negotiated-protocol checks before transmitting application bytes; never send these requests as early data.

The service interoperability baseline supports RSA certificate signatures using SHA-256 or stronger SHA-2 with PKCS #1 v1.5 or RSASSA-PSS, and ECDSA certificate signatures with SHA-256 or stronger SHA-2 using P-256 or P-384. RSA keys must have at least 2048 bits. Backends may support additional modern schemes under their documented policy, including Ed25519. SHA-1 and MD5 certificate or status signatures are not accepted. This restriction does not prohibit SHA-1 as an OCSP certificate identifier or responder key identifier: those fields identify an object and are not signatures. Trust-anchor authentication comes from configured trust, not the root's self-signature; a weak self-signature alone is not a reason to reject an otherwise independently trusted anchor.

These certificate capabilities do not select the TLS handshake signature scheme. TLS 1.3's negotiated signature rules still apply, including RSA-PSS for handshake RSA signatures. Algorithm identifiers, parameters, key restrictions and signature encodings must be validated by the backend under their defining standards. A backend that cannot enforce the selected policy is unsupported for that mode; a private RSA-only test environment does not establish ordinary-Web interoperability.

### Select a certificate-status mode

The client selects one mode before opening the connection. `web-compatible` is the default; `fresh-status-required` is an explicit local or organizational assurance choice. Neither the endpoint nor a network failure can lower that choice. Both modes reject independently established revocation or distrust, failed path/name checks, and failed mandatory certificate-feature requirements.

In `web-compatible`, the client uses its maintained backend's configured revocation/distrust service, validates supplied OCSP evidence, and may consult authorized OCSP or CRL sources. If usable status remains unavailable or unknown, it may connect after the other checks pass, retaining the result as **status indeterminate**, never “confirmed unrevoked.” This permits services whose CA does not publish usable per-certificate status. It also means an attacker who blocks status retrieval can prevent discovery of revocation that is not already known to the client. The mode and limitation must be visible in deployment documentation and diagnostic records; do not silently present this as strict status assurance.

In `fresh-status-required`, every non-anchor certificate in the selected path must have fresh, authenticated, sufficiently scoped good status, or a valid standards-defined per-certificate exception. Unknown, unavailable, stale or invalid evidence holds the connection without sending the request. A failure may trigger another authorized status source or a later retry, but never a downgrade to `web-compatible`. Deployments choosing this mode must accept that some ordinary public-Web services will be unavailable.

A valid `noRevAvail` assertion invokes RFC9608's per-certificate exception in both modes. Reject its prohibited CA/CRLDP/FreshestCRL/AIA-OCSP combinations. It conveys issuer policy, not evidence that a key is uncompromised, and does not exempt other certificates. `ocsp-nocheck` applies only to the authorized OCSP responder certificate in RFC6960's context. Neither exception is inferred from missing URLs. An implementation unable to recognize and enforce an encountered exception must hold rather than approximate it by disabling revocation globally.

### Accept status evidence

For OCSP, validate the exact certificate identifier, signature, authorized responder, applicable extensions and times under RFC6960 with its verified corrections. A supplied responder certificate is not a trust anchor. A good response does not prove certificate issuance, validity, hostname or authorization. Unsigned OCSP error responses and `unknown` are not good status. An authenticated applicable `revoked` result rejects the connection; a conflicting good result must not erase retained revocation without a separately defined administrative recovery procedure.

Request TLS `status_request`. For a certificate requiring it through the TLS Feature extension, require a valid current staple on that handshake; no unavailable-status allowance or alternative-source exception applies. This is an intentional stricter service-profile choice. In TLS 1.3 the response belongs to the corresponding CertificateEntry; do not use deprecated `status_request_v2` or assume a TLS 1.2 CertificateStatus message. Every supplied peer staple must validate; malformed, unrelated, stale or otherwise unacceptable supplied staples reject in both modes. This follows RFC6066 §8, incorporated by RFC9846 §4.5.1.1, and does not substitute an alternate source to excuse an invalid peer staple. Missing required staples also reject. Unsolicited external retrieval failures are status unavailability, not authenticated good evidence.

The common freshness policy is: at decision time `t`, require `thisUpdate <= t + 300 seconds`, `producedAt <= t + 300 seconds`, and `t - thisUpdate <= 7 days`. When `nextUpdate` is present require `thisUpdate <= nextUpdate` and `t < nextUpdate`, with no stale grace period. When absent the seven-day age bound still applies. Apply the applicable CRL validity/scope rules and the same maximum age to CRLs; future issuance tolerance is at most 300 seconds. Seven days permits multi-day cached responses while bounding replay; 300 seconds tolerates modest clock skew without extending nextUpdate. These editorial defaults are maximum tolerances, not instructions to cache for that long. Stricter configured bounds are permitted. An untrustworthy clock prevents ordinary certificate validity checking and holds both modes; compatible mode cannot bypass certificate validity through its unavailable-status allowance. This finite window limits replay but does not ensure immediate discovery of a new revocation.

For direct OCSP requests using a nonce, generate a fresh cryptographically random 32-octet value under RFC9654. A returned nonce must match. A missing nonce may be processed only as time-bounded cached evidence, never as proof of a live response to this request; it does not waive freshness checks. Staples are time-bounded signed evidence and need no per-client nonce. No custom OCSP cryptography or certificate parser is required by this specification; use established validation APIs.

### Connection reuse and resumption

Bind any retained validation decision to the exact service identity, certificate path, trust-policy revision, algorithm policy, status mode, evidence and expiry. Recheck it before sending each request on a pooled or resumed connection. Expiry is no later than the earliest certificate validity end, accepted status `nextUpdate`, accepted evidence maximum age, or a locally imposed shorter lifetime. Refresh or reconnect when that authorization is no longer usable. New known revocation or distrust invalidates it immediately when learned.

A resumed handshake does not supply new certificate-status evidence merely because the handshake succeeded. The client must recover and reevaluate the original authenticated path and status context, obtain new evidence if required, or perform a full handshake. For required-staple certificates this profile disables session resumption and requires a full handshake with a valid staple. An already established connection may be pooled only within its retained validated expiry; pooling does not extend that expiry. Tickets and cached decisions stay within the same service and isolation context. Policy changes, missing state or unsupported backend evidence cause a hold/full handshake, never assumed continuity.



## Submit one answer

Pressing the button creates one submission identity and one retained JSON request. Every retry uses those exact bytes, even after token renewal. Choosing a different option creates a separate authorized replacement; it is not a retry of the first answer.

The request contains the action, question, answering principal, option and optional predecessor submission. It contains no labels, email body, attachments or headers. The service validates both the request and its authority before execution.

::: {.details summary="POST headers, strict JSON and request schema"}

### POST request

Use the exact `submit` URI, `Content-Type: application/json`, `Accept: application/json`, and `Cache-Control: no-store`. No content coding is selected. Use HTTPS POST, no redirects and no implicit credential retry that changes the target. The JSON body follows the existing strict event rules, including exact UTF-8 bytes, unique decoded names, no numbers/null, maximum 1,048,576 octets and depth 32. Serialize once and retain those exact bytes before transmission.

The request has exactly these members:

| Member | Required value |
| --- | --- |
| `version` | String `0` |
| `purpose` | String `service-answer-submit` |
| `submission` | New nonzero ObjectId, stable for every retry |
| `action` | Descriptor's exact action ObjectId |
| `question` | Descriptor's exact EventReference |
| `principal` | Answering enp0 principal independently mapped from the credential |
| `option` | One option ObjectId from the service's exact question record |
| `replaces` | Empty array, or one previous submission ObjectId owned by this principal for this action/question |

EventReference has exactly `principal`, `conversation`, `event`; identifiers use their existing grammars. Submission IDs identify service operations, not conversation events. Do not insert them into EventReference or impersonate a conversation contribution. Version 0 supports replacement of at most one previous confirmed submission. Replacing several competing answers needs a later profile. All fields are required; unknown fields and enum values are invalid. No email body, labels, text, attachments or headers are sent.

The service authenticates before disclosing submission status. It validates the complete request and action scope before execution. Missing or ambiguous question data cannot be repaired by client-supplied labels. Define `requestDigest` as lowercase SHA256 of the exact received request bytes. A parsed/reencoded object cannot replace those bytes for deduplication. This is a content identifier inside authenticated transport, not a MAC or proof of requester identity.

:::

## Read the service's result

A receipt binds the result to the exact retained request. The client accepts it only through the bound service's direct authenticated HTTPS response to the submission or its status request. A successful HTTP status alone is not confirmation that the answer was applied.

| Valid receipt | Meaning |
| --- | --- |
| Pending | The service durably recorded the submission but has not established a final result |
| Confirmed | The service applied the answer and any permitted replacement |
| Rejected | This submission did not and will not apply the action, including through an earlier attempt |

> [!note] A service statement, not transferable signed proof
> HTTPS authenticates the service origin for the client making the request. This profile adds no receipt signature that another participant can independently verify. A copied JSON receipt is not proof of the service's action, and a malicious service can lie about its effect.

A missing, malformed or mismatched receipt leaves the application result unconfirmed. A later pending response cannot replace a retained terminal result. Incompatible terminal receipts remain a visible conflict rather than causing another submission.

::: {.details summary="Receipt schema, result reasons and response authentication"}

### Receipt schema

A valid application response is one strict JSON object, with exactly:

| Member | Required value |
| --- | --- |
| `version` | String `0` |
| `purpose` | String `service-answer-result` |
| `service` | Exact descriptor service origin |
| `action`, `submission`, `question`, `principal`, `option`, `replaces` | Exact values from the retained request |
| `requestDigest` | SHA256 of the retained request bytes |
| `outcome` | `pending`, `confirmed` or `rejected` |
| `reason` | String from the outcome's exact set below |

For `pending`, reason is `processing` or `reconciling`. Either means the service durably recorded this exact authorized submission but has not established a terminal result. For `confirmed`, reason is exactly `applied`: this service applied the selected answer and any permitted replacement. For `rejected`, reason is exactly one of `action-expired`, `option-not-allowed`, `replacement-not-current`, or `not-applied`. Rejected means this submission did not and will not apply an action, including via an earlier attempt; it cannot be emitted merely because the latest HTTP attempt failed.

There are no timestamps, changing display strings, access tokens, status URLs, business payloads or signed-proof fields in this version. Terminal comparison uses the complete decoded object after strict parsing, not HTTP Date, JSON member order or whitespace. Every request binding must match before a result affects local state. Repeated semantically identical receipts do not create conflicts. A terminal change in outcome or reason is a conflict. Two differing pending reasons remain pending; no ordering is inferred.

Accept receipts only from a direct authenticated HTTPS response to this submission's exact POST or derived GET URL, with the expected TLS service origin, valid response schema and matching request bindings. An HTTP Location field, an emailed JSON object, cached response or unrelated TLS connection is insufficient. Service TLS termination is part of the service trust boundary; this contract adds no end-to-end proof beyond it. A malicious service can lie about its effect.

:::

## Retry and check status

A status check reads the existing result; it cannot execute an answer. The client uses the authenticated status destination and the same authorized principal. “Not found” means status is unavailable, not that the action never happened.

Neither submission nor status requests follow redirects, even to the same origin. Requests omit ambient browser and account credentials. Polling belongs to an authorized pending-submission workflow or a deliberate user check, never to rendering or scanning an email.

::: {.details summary="HTTP statuses, no-store responses, redirects and bounded polling"}

### HTTP results and polling

All profile requests and responses include `Cache-Control: no-store`; local deliberate evidence retention is separate. Success responses use `application/json` and the same byte/depth bounds. Version 0 sends no compressed payload; unsupported Content-Encoding is not decoded optimistically.

POST or GET returns 200 with a terminal receipt, or 202 with a pending receipt. Another status or a missing/malformed/mismatched receipt is not application confirmation. Preserve the per-attempt meanings of 401, 408 and 421 without inferring what happened on earlier attempts. A 401 may permit independently configured credential renewal; a retry retains the exact request and submission. Redirects are never followed, including same-origin 307/308. An origin move needs a new authenticated migration profile; v0 holds the existing submission.

GET uses `statusPrefix + submission` with no body. The submission identifier is a locator, not access authorization. The service scopes lookup to the authenticated principal and bound action behind the prefix. A 404 yields “status unavailable,” never proof of nonexecution. No GET/HEAD request, preview, link scan or status poll executes, replaces or withdraws an answer.

For canonical authenticated requests, 409 with an empty body indicates the submission identifier was already recorded with different request bytes; the service neither overwrites nor executes the new bytes. Preserve the original request and query its status. This attempt-level conflict is distinct from conflicting terminal receipts. Other HTTP errors do not carry an implicitly trusted result object.

Polling is user-triggered or part of an already authorized pending-submission workflow, never a side effect of rendering mail. Allow only one in-flight request per local submission. A valid Retry-After can postpone a poll but cannot grant permission, change the endpoint or extend retryUntil. Without one, the implementation uses documented bounded backoff with jitter and a finite budget; reaching that budget leaves the result pending/uncertain and allows an explicit later check. Backoff values are local scheduling policy, not wire semantics or a claimed user constraint. Status authorization and retention may outlast retryUntil; after the deadline no new POST execution is allowed, but GET may retrieve retained evidence.

:::

## Apply once, including after a crash

The service retains one execution decision for each authenticated principal, action and submission identity. Repeating the same request returns that operation's recorded outcome. Reusing the identity with different bytes does not overwrite it.

Replacing an answer requires the principal's current confirmed predecessor. Two replacements racing for the same answer cannot both silently win. An unresolved pending answer must be reconciled before dependent work executes.

If the service cannot establish whether an external effect happened, it retains an uncertain result. A timeout or database loss cannot turn an old submission into a new action. The client does not automatically switch to email delivery after uncertain HTTPS execution.

::: {.details summary="Durable execution, expiry, deduplication and replacement rules"}

### Durable execution and replacement

Deduplication key is `(authenticated principal, action, submission)`. The service compares exact request bytes, not just the client-provided fields or digest, and durably associates that key with one result lifecycle. Concurrent byte-identical retries share one execution decision. An identifier reused with different bytes gets 409 without changing the stored outcome. Other principals cannot inspect or interfere with that record.

Before first application, the service's current time must satisfy `notBefore <= now <= retryUntil`. Both endpoints are inclusive. The client also refuses a new POST unless its entire credible time interval fits those bounds: its earliest possible time is at least notBefore and its latest possible time is at most retryUntil. The service rechecks time and authorization at the transaction that decides to apply the effect, including after waiting for another transaction. If a pending operation cannot be completed before retryUntil, the service must reconcile whether it already applied; it cannot initiate a new effect afterward. Exact duplicate requests may retrieve an already retained outcome after expiry without re-executing it. A new expired request gets a durable rejected/action-expired receipt only after the service establishes no previous application for that deduplication key.

The service retains all accepted deduplication/result evidence through retryUntil and must not execute an old key after garbage collection. This is safe because execution for the entire action has closed; reopening the business question requires a new action identifier. A lost database must not be treated as proof that an old submission is new. If recoverable state is insufficient, refuse execution and report uncertainty.

For an initial answer, `replaces` is empty and the principal must have no current confirmed answer or unresolved pending submission for that action. If a confirmed answer exists, reject a second initial answer with `replacement-not-current`; if an earlier submission is unresolved, keep the new submission pending without executing until that dependency is reconciled. For a change, it identifies this principal's current confirmed answer. The service atomically checks that relationship and commits both the new answer and the prior answer's supersession. Two replacements racing for one predecessor cannot both silently win: one may apply, and the other gets a stable rejected/replacement-not-current result. The earlier receipt remains confirmed for its original operation; it is not rewritten. Replacing a pending or unknown submission is disallowed because its effect is unresolved.

Deduplication and business effect must commit atomically, or an equivalent durable recovery protocol must prevent duplicate effects. An external service call without such a recovery protocol cannot support confirmed/rejected receipts reliably: preserve pending/reconciling until reconciliation. An HTTP timeout, queue acknowledgment or in-memory cache is insufficient. No automatic fallback sends an email copy after uncertain HTTPS delivery.

:::

## Keep the conversation record honest

The intended answer, transmitted request and service receipts are distinct records. Sharing the result with conversation participants creates a separate contribution under the chosen audience and protection policy. It describes what the client observed; it does not make the service receipt a statement authored by the answering person.

Email and HTTPS remain alternative delivery paths unless a future authenticated cross-channel contract connects their duplicate handling. The mere availability of both paths does not make switching between them safe.

::: {.details summary="Conflicting receipts and sharing an observed result"}

### Conflicting results and conversation records

Pending cannot overwrite terminal. A failed later attempt cannot erase confirmation. Two incompatible verified terminal receipts produce a retained conflict, with no automatic re-execution or new submission identifier. Version 0 has no reconciliation wire operation; offer contact with the named service and preserve the evidence. A later business correction requires a new authorized operation rather than rewriting the original receipt.

Store the person's intended answer, the outgoing request bytes and observed service receipts separately. A service receipt is not authored by the answering principal. Sharing a local account of the result into the conversation requires a distinct contribution under its audience/protection policy and must describe it as the client's observation; another client cannot independently validate the HTTPS transcript merely from copied receipt JSON. Email and endpoint delivery remain alternatives unless a future cross-channel authenticated deduplication profile connects them.

:::

## What remains before interoperability

The proposed request and receipt schemas can be exercised with preconfigured test credentials. The joined experiments cover protected service-question authentication and the selected sign-in/principal-link path. Public interoperability still needs independent implementations, production account integration, service provisioning, shared URI parsing and deployed execution evidence. Browser/network restrictions and the bearer-authorization dependencies also require review.

The candidate uses registered `application/json` and ordinary HTTP fields; it does not allocate a new media type or header. Its version and purpose values identify this experiment, not a public capability negotiation mechanism.

::: {.details summary="Required acceptance cases and specification dependencies"}

### Implementation and specification prerequisites

Focused fixtures should cover exact-byte retries across token renewal; altered payload under the same ID; concurrent duplicate and replacement transactions; crash before/after business commit; authenticated not-found; pending after terminal; incompatible terminal reasons; wrong origin/question/principal/digest; unsolicited receipts; redirects; ambient credential omission; stale grants; expiry during execution; and oversized/duplicate-name JSON. The [configured execution experiment](evidence/README.md#configured-service-execution) covers a subset using local transactional effects; it does not establish the entire acceptance set.

Public interoperability still requires deployed implementation of the [selected account-link profile](service-authorization.md); independent service action provisioning and authorization; URI/A-label parser agreement; browser/network endpoint restrictions; durable execution and retention implementation; and review of OAuth bearer/audience standards. This candidate uses registered application/json and ordinary HTTP fields, so it does not require a new media type or header to test the wire format. The new purpose/version strings belong to this experimental application profile. The selected protected binding negotiates the exact `service-question` operation as described below; this does not negotiate service credentials. Any later vendor media type, discovery metadata or OAuth resource parameter requires its own applicable registration/review. None is silently allocated here.

:::


## From an accepted question to a service action

The selected joined binding is assertion5, context6, envelope3 and payload `mime-rich-v0`, with `service-question` explicitly present in every admitted device’s exact operation tuple. Ordinary `question` support does not imply it. Previously signed operation lists are unchanged, and a partial intersection cannot supply this capability. Older contexts and the separate context7 ordering experiment do not acquire it implicitly.

The client derives the control from one accepted event and its exact retained carrier in the active membership instance. It displays the question, choices and destination service. A deliberate click supplies a choice and a snapshot token to the trusted client; the browser does not supply the endpoint, principal, action or credential. Viewing the message and replying by ordinary email do not execute the service action.

An independent local service registration binds the exact origin, action, submit/status paths, answering principal and credential handle. Its generation changes when its authorization changes. Before retaining a request and again before transport, the client rechecks that registration, the accepted source, the current membership instance and the answering device’s current send authority. A valid message cannot create this registration or acquire credentials.

The client retains the submission identity and exact request bytes before network activity. A restart or credential renewal retries those bytes. The request contains the defined identifiers and option, not the question text or conversation history. Only the existing direct HTTPS adapter admits a matching receipt to the result journal; it does not manufacture a conversation answer. A lost response remains uncertain. Withdrawal holds further execution without erasing that uncertainty; status reconciliation still requires authorization.

The [joined service control experiment](evidence/README.md#joined-service-question-control) exercises signed discovery, ordinary SMTP carriage, trusted activation, TLS, a transactional service effect and a bound receipt. That original fixture uses preconfigured credentials. The separate [account-link experiment](evidence/README.md#service-account-authorization-and-linking) exercises the selected acquisition contract with simulated trusted account consent and actual TLS exchanges; it does not supply a production login website. Local checks before transport do not make authorization withdrawal and a remote business commit one atomic transaction; the service must independently enforce its grant at execution.

## Request and result parser experiment

The [local parser experiment](evidence/README.md#service-answer-request-and-result-binding) checks strict request/result bytes, identifier shapes, exact retained-request digests and matching result fields. Five tests cover valid unverified binding, every request relationship, alternate request serialization, malformed receipts and invalid request identities. A successful result is explicitly `bound-unverified`: it does not verify HTTPS, bearer credentials, descriptor authority or service execution.


The service-question experiment validates the nested descriptor and its enclosing-event reference, and produces inert readable alternatives. It checks the selected ASCII origin/path spelling but explicitly refuses A-label hosts pending complete IDNA support; that limitation is not a change to the profile. Two MIME tests preserve exact event bytes and service/choice wording, exclude protocol endpoints from the readable invitation, and reject a wrong self-reference. Ordinary conversation answers still reject service questions as targets. These carriage tests do not establish service credentials or execute a request; configured execution is tested separately.

## Local TLS evidence

The [TLS adapter experiment](evidence/README.md#https-certificate-identity-and-tls-minimum) tests actual local handshakes for SAN matching, rejected Common Name fallback, wildcard boundaries and the TLS1.3 minimum. Its successful handshake does not authorize an answer or establish a service result. IDNA and certificate-revocation deployment remain incomplete. The configured execution experiment separately joins this TLS helper to bearer checks, HTTP requests and local durable effects.

## Configured HTTP transport evidence

The local HTTPS adapters reject ambiguous framing before application dispatch and require complete, bounded response bodies before recording receipts. They use a restricted fixed-length HTTP subset; they do not claim general HTTP/1.1 server conformance or intermediary-cache coverage. See [HTTP framing and caching](audits/http-framing.md) for the reviewed rules and deployment limits.

The configured clients also verify the selected TLS application protocol before sending HTTP bytes. Absent ALPN uses an explicit HTTP/1.1 fallback; another selected protocol is rejected. [Server-name and protocol negotiation evidence](audits/tls-service-negotiation.md) records the distinction from certificate verification and the remaining no-overlap alert limitation.
