---
title: Hosted bearer access
order: 12.5
blurb: secret links · deliberate retrieval · revocation
sectionNav: true
---

# Hosted bearer access

A sender can authorize a hosting service to make one contribution available through a secret link. The service can read the content. Anyone who obtains the link can use its authority until it expires or is revoked; the link does not establish who that person is.

> [!ex] Open a contribution without a compatible client
> Carol receives a short email containing a link. Opening the page shows an **Open contribution** button. After she presses it, the host supplies the contribution. A reply is identified as coming from a holder of that grant, not as a verified statement by Carol.

> [!note] Configured experimental contract
> This candidate defines bearer access with configured management authority, recipient routing and reply destinations. The configured message and question flows cover explicit author plans, protected declarations, hosted access, durable notification and observer-authored holder replies. Public deployment authorization remains incomplete. Account-bound access and an independently authorized cryptographic endpoint are separate models in [delivery policy](delivery-policy.md#hosted-access-models).

## Grant and management authority

Each recipient receives a separate grant. A grant binds one immutable contribution, its permitted hosted text, one configured recipient and one configured reply destination. It does not grant access to the rest of the conversation. A new contribution or changed disclosure requires a new grant and authorization.

Management credentials and grant credentials have different authority. Management authorization identifies an owner and permits scoped creation, inspection or revocation. A grant bearer permits retrieval and, where configured, a holder reply. It cannot create, revoke or enumerate grants. Request fields cannot select a different management owner.

The sender must authorize the hosting origin, content, recipient, reply destination and expiry before creating a grant. This experiment relies on independently provisioned records binding those choices. Neither an incoming message nor a claimed contribution reference provisions that authority. Hosting does not authenticate the original author's contribution by itself.

Generate the grant credential from 32 random octets supplied by a cryptographic random generator. Encode them as canonical unpadded base64url: exactly 43 ASCII characters, with decode/re-encode equality. A separately generated nonzero ObjectId locates the grant but grants no access. This is the proposed credential-generation profile; a receiver cannot infer randomness merely from a correctly shaped string.

Retain the credential and creation request in protected local storage before transmission. Ordinary logs, diagnostics and general request journals must not contain them. The host may store a credential digest for lookup; retries must still compare the exact original creation request under the idempotency rules below.

## Requests and outcomes

All endpoints use direct HTTPS and `Cache-Control: no-store`. Do not follow redirects. Management requests use their separately configured authorization; retrieval and holder-reply requests use `Authorization: Bearer <grant credential>`. Do not use ambient cookies or credentials. JSON bodies use `application/json`, strict UTF-8 and the existing experimental JSON limits; duplicate, missing or unknown members are invalid. Historical reply exports alone use a 2 MiB encoded-response bound; ordinary requests and events retain the 1 MiB bound.

| Operation | Endpoint | Successful result |
| --- | --- | --- |
| Create | `POST /v0/grants` | HTTP 200 with a bound management receipt |
| Inspect a management operation | `GET /v0/operations/<operation>` | HTTP 200 with its retained management receipt |
| Revoke | `POST /v0/grants/<grant>/revoke` | HTTP 200 with a bound management receipt |
| Inspect a stored reply as manager | `GET /v0/grants/<grant>/reply-records/<operation>` | HTTP 200 with its original holder receipt under current management authorization |
| Export a retained reply as manager | `GET /v0/grants/<grant>/reply-exports/<operation>` | HTTP 200 with exact request bytes, original receipt and configured reply destination |
| Load the entry page | `GET /g/<grant>#<credential>` | Generic application shell; no protected content |
| Retrieve after deliberate interaction | `GET /v0/grants/<grant>/content` | HTTP 200 with the authorized content |
| Store a holder reply | `POST /v0/grants/<grant>/replies` | HTTP 200 with a bound holder receipt |
| Inspect a holder reply | `GET /v0/grants/<grant>/replies/<operation>` | HTTP 200 with its retained holder receipt, while the grant remains authorized |

The fragment in the entry URL is browser-held; it is not part of the HTTP request target. The other requests never put the grant credential in a URL. The management create body contains the new credential and therefore needs the same protection as the credential itself.

Malformed requests fail without an application receipt. Missing or invalid credentials receive 401; insufficient authority receives 403. Responses must not disclose another owner's records. An authorized lookup with no matching operation receives 404. Conflicting operation reuse receives 409. An HTTP error alone does not establish whether an earlier attempt committed; retain any earlier confirmed evidence.

::: {.details summary="Exact request and receipt objects"}

All objects have exactly the listed members. `version` is string `0` except the explicitly selected create-v1 request. ObjectIds are nonzero; principals and EventReferences use the existing identifier contracts. Epochs are canonical unsigned-64 decimal strings. Text is nonblank Unicode scalar-value text. JSON numbers, booleans and null are not used.

| Object | Exact members and fixed values |
| --- | --- |
| Create | `version`, `purpose:"hosted-grant-create"`, `operation`, `grant`, `credential`, `contribution`, `content`, `recipient`, `replyDestination`, `expiry` |
| Create v1 | The create members with `version:"1"`, plus `replyTextLimit` |
| Historical reply export | `version:"0"`, `purpose:"hosted-reply-export"`, `service`, `grant`, `operation`, `request`, `receipt`, `replyDestination` |
| Content | `kind:"text"`, `text` |
| Timestamp expiry | `kind:"at"`, `epoch` |
| Explicit no-expiry | `kind:"none"` |
| Revoke | `version`, `purpose:"hosted-grant-revoke"`, `operation`, `grant` |
| Holder reply | `version`, `purpose:"hosted-holder-reply"`, `operation`, `text` |
| Management receipt | `version`, `purpose:"hosted-management-result"`, `service`, `owner`, `operation`, `grant`, `requestDigest`, `outcome:"confirmed"`, `reason` |
| Holder receipt | `version`, `purpose:"hosted-holder-result"`, `service`, `grant`, `operation`, `requestDigest`, `outcome:"confirmed"`, `reason:"stored"`, `attribution:"grant-holder"` |
| Retrieval result | `version`, `purpose:"hosted-content"`, `grant`, `contribution`, `content`, `attribution:"provider-hosted"` |

`operation`, `grant`, `recipient` and `replyDestination` are ObjectIds. `contribution` is an EventReference. The latter two destination IDs resolve through the owner's independently provisioned configuration; they are not arbitrary addresses. `owner` is an enp0 principal from management authentication. `service` is the exact configured HTTPS origin under the [service URI rules](service-answers.md). `requestDigest` is lowercase SHA-256 of the exact request bytes. Management `reason` is `created` or `revoked`, matching the request purpose.

A client accepts a receipt only from the direct authorized service response and only when all request bindings match. Copied JSON is not transferable authentication evidence. Retrieval excludes the recipient identity, credential and management authority.

:::

## Authorizing the original disclosure

For the configured message and question flows, the local author authorizes exact contribution bytes, hosting origins, external grants, routing, expiry and reply destinations before any hosting request. Its envelope-v1 disclosure union must exactly match the retained plans. A descriptor in received content cannot create that authorization. Protected preparation precedes hosting and commits the local author evidence with the MLS checkpoint; preparation itself sends nothing.

Creating the grant can disclose content to the provider even if subsequent protected delivery is held. The local plan explicitly covers that order. There is no atomic transaction spanning hosting and email delivery, and withdrawing a notification does not erase content already hosted.

Current author, context and policy checks guard grant creation. Protected-original and minimal-notification release both recheck the plan before DATA. A lost creation response remains uncertain until exact-byte retry or authenticated lookup reconciles it. Historical confirmation is not a guarantee of current remote access. Messages retain their exact text. Questions use the existing complete readable projection, including every choice in order, reply instructions and the declared external sharing. Authorization and observer-target checks compare that exact text. A changed formatter or a request exceeding its byte limit holds the operation; it does not truncate choices or substitute the heading.

## Keeping replies representable

Create version 1 adds `replyTextLimit`, a canonical decimal string between 3 and 1048576. The host's independently provisioned grant configuration must agree with it. A reply exceeding this limit receives HTTP 413 before a reply receipt is committed. The browser retains the draft so the holder can shorten it. Version 0 grants retain their earlier behavior and do not acquire this guarantee retroactively.

The sender derives the limit from a complete retained observer-event template, including its protected audience and disclosure list. The template uses the common contribution-envelope version 1 and the `hosted-holder-observation` operation. That operation has exactly `kind`, `text`, `target`, `service` and `attribution:"grant-holder"`; `target` is the original contribution's EventReference. Its actual observer principal must authenticate it. Selecting the operation requires explicit agreement in the verified application context; a provider receipt is not a signed contribution.

::: {.details summary="Exact serialized-text bound"}

Use the same serializer to measure and produce the event. Let `T` be the complete template with empty operation text and a valid fixed-width event ID. Let `S(T)` be its exact serialized bytes, and let `L` be the existing 1048576-byte event limit. The reply limit is `B = L - length(S(T)) + 2`; the two bytes are the empty string's quotation marks. If `B < 3`, reply-enabled creation cannot proceed.

Measure the reply as a complete serialized JSON string, including quotation marks and escapes. Accept it only when that measurement is at most `B` and the exact holder request also fits its existing bound. Replacing the empty text and assigning a fresh event ID of the same width then preserves the event limit. Character counts and unescaped UTF-8 lengths are insufficient.

Retain the template encrypted and immutable before sending creation. Changing its audience, disclosures or other overhead requires new preparation. Current membership or policy may prevent later delivery; hold the observation instead of silently changing its audience. Representability is not a promise of delivery.

:::

The limit reveals envelope-overhead information to the provider and can support size inference. The template and roster identities are not explicitly transmitted as part of the grant request; that does not imply that membership counts cannot be inferred.

A hosted question's reply remains free text from a grant holder. A number or matching option label does not become a structured authenticated `answer`; the observer records it as `hosted-holder-observation` targeting the question. Structured-answer state remains unchanged. The host renders question choices and replies as inert text.

## Exporting historical holder replies

The reply-export route requires current management owner, issuer, audience, time and `read-management` authorization inside its read transaction. It remains available after bearer expiry or revocation. The bearer cannot use it. Authorized owner unknown records return 404; another owner receives no record information.

`request` is canonical unpadded base64url of the exact retained holder-request bytes, including any original whitespace. `receipt` is the original holder receipt, and `replyDestination` is the immutable configured destination. Check the decoded request schema, service, grant, operation, destination and exact request digest before retaining authenticated export evidence. Preserve unknown or contradictory history as a hold; do not infer a mailbox identity from the holder attribution.

The export response permits 2097152 encoded bytes to contain the base64 expansion of a maximum-size request and its bounded receipt. Other event limits do not change. Retain export evidence encrypted, with its provenance and exact request binding committed together. Release into a protected conversation additionally requires a locally authorized observer, the selected operation agreement and the normal current MLS checks.

## Retry and crash boundaries

Retain the exact creation request, including its credential, before sending. Atomically commit the host's grant, immutable content association, exact request and receipt before reporting creation. An owner/operation pair identifies one immutable management request. An identical retry returns its retained receipt; different bytes return 409. A different creation operation cannot reuse an existing grant ID, even for equivalent content.

A lost response is resolved by authorized operation lookup or exact retry. It must not generate a replacement credential or grant automatically. A creation receipt records a historical decision, not proof that the grant is still active. Sending its notification is a separate delivery operation.

Holder replies similarly bind exact bytes to their grant/operation pair. Authorization, stored reply and receipt commit together. The receipt means a local holder-attributed reply was stored under the preauthorized destination. It does not mean email was delivered. Actual conversation delivery needs a separately authorized outbox and reconciliation; no implicit ordinary-email fallback is permitted.

Protect retained credential-bearing requests without weakening exact-byte comparison. A hash alone is not the retained request for this contract. Storage encryption, key custody and restoration must preserve the operation identity; unreadable or lost state cannot be treated as proof that an old request is new.

## Entry page and deliberate retrieval

The entry page must be served directly, without a redirect or tracking intermediary. It contains no contribution, personal title or grant-derived metadata. It reads and validates the fragment, removes it from the displayed URL through history replacement, and retains the credential only in application memory. Reloading requires reopening the invitation; do not persist the credential in browser storage.

Loading the page does not retrieve protected content. Only an explicit **Open contribution** action starts the authorized retrieval request. Scanners that load the page or run its initialization must not consume a grant, send a receipt or change conversation state. A scanner that possesses the bearer and performs the interaction can retrieve content; this cannot be represented as proof of a human read.

Use an isolated hosting origin, restrictive content policy, no third-party resources, `Referrer-Policy: no-referrer`, and no-store responses. Render this profile's text as text. Fetch uses omitted ambient credentials and rejects redirects. Do not transmit secrets through outbound navigation, login return parameters, telemetry or error messages. The hosting operator and its scripts remain trusted with the content and bearer.

A page script cannot stop a redirect that happens before the page loads. The [redirect boundary](delivery-policy.md#hosted-credential-navigation) is a deployment requirement, not protection supplied by removing the fragment afterward.

## Expiry and revocation

Timestamp access is authorized while service time is at most `expiry.epoch`, inclusive, and the grant is not revoked. Creation after that deadline is refused. An explicit no-expiry grant remains usable until revoked; it must not be an invisible default.

Revocation and access decisions share a serialization boundary. Revocation committed first blocks new retrieval or reply authorization. Retrieval already authorized may finish transmitting afterward; revocation cannot erase copies. Materialize the response from its authorized immutable snapshot rather than rereading changed content later.

After expiry or revocation, the bearer cannot retrieve content or reply results. Previously retained client evidence remains valid historical evidence; denial does not mean a reply never committed. Management authority can inspect retained operation receipts. The reply-records endpoint requires current owner authorization and the read-management scope; it returns the original holder receipt even after grant expiry or revocation. It neither reactivates the grant nor changes the reply's attribution. A grant bearer cannot use this endpoint. An authorized owner's missing record returns 404; another owner must not learn whether it exists. Do not erase retry evidence or reopen grant identifiers after state loss. A repeated authorized revoke may confirm the already-revoked state without changing historical receipts.

## Acceptance boundary

The implementation must test exact retries, lost responses, crashes around commits, separate management/grant authority, expiry and revocation races, holder attribution, and fail-closed damaged storage. Browser tests must inspect actual fragments, history, request headers, referrers and persistent storage; no automatic retrieval or reply may occur on entry or scanning. Redirect fixtures must distinguish rejected fetch redirects from unavoidable pre-load navigation leakage.

The [configured hosted experiment](evidence/README.md#configured-hosted-bearer-access) exercises backend transactions, browser entry, authenticated management evidence and encrypted notification release through loopback SMTP. Current local checks do not prove a remote grant is still active, and a historical receipt does not authorize delivery by itself. The joined message and question experiments bind authenticated disclosure to a local author plan and return holder observations through current MLS authorization. Public management authorization, deployed browser trust and credential/key recovery remain required work. No account-bound identity, endpoint-only confidentiality or independent interoperability is claimed.

## Configured HTTP transport evidence

The local HTTPS adapters reject ambiguous framing before application dispatch and require complete, bounded response bodies before recording receipts. They use a restricted fixed-length HTTP subset; they do not claim general HTTP/1.1 server conformance or intermediary-cache coverage. See [HTTP framing and caching](audits/http-framing.md) for the reviewed rules and deployment limits.

The configured clients also verify the selected TLS application protocol before sending HTTP bytes. Absent ALPN uses an explicit HTTP/1.1 fallback; another selected protocol is rejected. [Server-name and protocol negotiation evidence](audits/tls-service-negotiation.md) records the distinction from certificate verification and the remaining no-overlap alert limitation.
