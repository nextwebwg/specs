---
title: Issuing and renewing private delivery routes
order: 6.2
blurb: trusted inbox provider · temporary addresses · offline issuance · accountable delivery
sectionNav: true
---

# Issuing and renewing private delivery routes

The recipient’s Email/2 inbox provider assigns temporary delivery addresses as part of operating that inbox. A device does not approve individual addresses. The provider issues and renews routes under the account’s routing policy, including while the recipient’s devices are offline. Clients continue to compose and display permanent personal addresses; temporary aliases are internal transport information.

> [!ex] The address you use stays the same
> Alice writes to Bob’s personal address. Bob has connected his inbox provider as his receiving service. Once Alice obtains his usable encryption setup, her transport adapter obtains a temporary route from that provider. Bob need not bring a device online to approve the alias. The providers carry encrypted packages, and both clients display the authenticated personal addresses after acceptance. When that route expires, the next new delivery obtains another route automatically.

The service controls delivery, not endpoint encryption identity. It can observe routing metadata, refuse service or misroute ciphertext; it cannot thereby decrypt the package, enroll a device, replace a correspondent’s pin, sign a conversation contribution or disclose history. Those guarantees depend on the complete [Encryption agreement](suite-profile.md), not a route signature.

This chapter owns the current relay descriptor1 and provider-issued route1 contract. Source permissions and delivery proofs retain the explicitly selected version0 shapes below. Internal format numbers identify exact records within the same Email/2 specification. The [retained route experiment](relay-routes-compatibility.md) requires recipient-device alias approvals and is not selected by the current procedure.

> [!note] Defined behavior; joined implementation remains required
> Existing [route component evidence](evidence/README.md#relay-route-authorization) covers the retained device-approved experiment with configured service facts. It does not implement this provider-issued route contract, public account connection, HTTP issuance, SMTP proof extraction or a production mailbox. The acceptance obligations below are required work, not recorded passes.

## Connect the inbox, not each temporary address

The normal receiving service is the recipient’s inbox provider, selected through that account’s domain. An independent receiving relay is a deliberate alternative account selection. It stores the encrypted mailbox and provides authenticated retrieval itself; it does not forward to a personal SMTP recipient. A selected independent relay cannot claim delegation from an unrelated personal mailbox domain.

Normal account connection establishes a finite **receiving-service authorization**. Its original signature binds the selected provider’s service identity to the recipient’s already authorized Email/2 principal. This service association is created during connection under the account’s routing policy; it is not a separate alias-approval dialog. The authorization names no alias, peer or conversation. Contact/admission policy and block lists stay private at the provider and are not copied into a public authorization.

The client and provider retain the account link, OAuth family, account incarnation, exact authorization and accepted identity dependencies. Account login alone cannot replace a linked principal. A routing connection grants no application-message sending, device enrollment, decryption or history authority. Different modules retain their separate [account-link and reset boundaries](provider-grants.md#shared-account-links-separate-module-authority).

The sending side still proves a legitimate service account and possession of a fresh route key. That proof limits who can use a route; it does not ask Bob’s device to approve the address. Forwarding an alias without the authorized key cannot authorize another sender.

## Discover the selected service

Fetch `https://<selected account domain>/.well-known/mail-relay`. Apply the [provider discovery](provider-discovery.md) transport, selected-domain authentication, publication/generation high-water, network-address validation, finite processing and purpose separation: credential-free HTTPS, TLS1.3, no redirects, no compressed bodies and no ambient cookies or client certificate. Do not infer the service from MX, a received URL or an alias. A separately selected relay uses its own account domain.

Descriptor1 has these exact required fields:

| Field | Required value or meaning |
| --- | --- |
| `version`, `purpose` | Strings `"1"`, `"relay-service-discovery"` |
| `domain`, `service` | Selected canonical domain and canonical HTTPS service origin |
| `publication`, `generation` | Original publication identifier and generation under provider-discovery rules |
| `managementPrefix`, `permissionPrefix` | Distinct nonoverlapping same-origin canonical path prefixes, ending in `/` |
| `roles` | Nonempty ASCII-sorted distinct array from `accountability`, `recipient-mask`, `sender-mask` |
| `serviceSigningKey` | Stable service-authority Ed25519 public key, 64 lowercase hex |
| `routeSigningKey` | Currently advertised Ed25519 route-issuance public key, 64 lowercase hex |
| `routeCertificate` | Original signed certificate wrapper defined below |
| `notBefore`, `notAfter` | Original descriptor validity, canonical uint64 epoch-second strings |

Sender-mask requires accountability; recipient masking is independent. Advertise only implemented roles. Every descriptor1 carries the certificate; its domain, issuer and keys match this descriptor exactly. A descriptor is not an account login or a device capability assertion. Reject unsupported versions before parsing their selected operations; no failed validation tries descriptor0.

Own-account connection reuses issuer-bound native registration, authorization-code/S256 PKCE, exact shared callback forms, refresh/revocation and public-client rules from [native provider connection](provider-discovery.md#reuse-sign-in-mechanics-without-sharing-permissions). Select only needed scopes from `mail.relay.link`, `mail.relay.manage`, `mail.relay.submit`; metadata must advertise them. No sender logs into the recipient’s account. Queue/setup credentials do not cross into relay authority.

Relay account links deliberately retain the [exact shared version0 subset](provider-grants.md#shared-account-links-separate-module-authority), including its original literal proof domains and safe-integer timestamps. Its descriptor digest binds the actual selected descriptor1. A protocol version does not reset accounts, families, revocation, source blocks, replay records or budgets.

## Obtain a route while the recipient is offline

1. **Validate encryption setup.** Independently accept the intended recipient’s identity, selected mailbox association and usable device setup. A [bootstrap2 response or publication](bootstrap.md#automatic-setup-for-independently-ready-recipients) can supply its original `relayDomain`. That domain selects an already configured service; it is not an arbitrary callback or OAuth issuer.
2. **Authorize the sending source.** Obtain a source permission for this exact recipient principal, conversation, destination service and fresh route key through the sending account’s own service. Retain the private key locally. A provider never receives that key.
3. **Ask the receiving service.** Send the exact signed route request to the accepted service. It validates live source authority and its own current receiving-service authorization, private account policy and blocks. It allocates the alias without contacting a recipient device.
4. **Inspect the result.** Prove route-key possession to retrieve the original route invitation. Validate its provider signature/certificate, original service authorization, current identity, exact scope and bounds. Then inspect the route’s live activation before release. A signed record alone is not current activation.
5. **Prepare and release.** Encrypt using the independently accepted endpoint setup. Freeze the exact route, envelope, carrier and proof with this delivery. Apply the [address-swap sequence](private-routing.md#when-the-addresses-change) and serialized release checks.

Published setup is not a fresh device response. Offline route issuance does not improve its freshness, independently verify a person or produce missing admission material. Required masking remains pending if routing cannot complete; a failure grants no plaintext or public-address fallback permission.

## Temporary routes, stable conversations

A route has an explicit finite lifetime. It may be coordinated with setup or encryption renewal, but is not automatically tied to a TLS certificate, one MLS epoch or a fixed rotation frequency. Its original interval must fit every source, service, account, certificate and policy limit. Reissuing the same record cannot extend it.

Routine renewal obtains a fresh source permission/key and a newly issued route while the receiving-service authorization and private account policy remain eligible. It requires no recipient-device alias approval. Old and new routes may overlap within their original limits. Aliases are never reassigned, including after account deletion. Blocks and budgets survive new aliases, source account incarnations, protocol versions and known peer service changes.

The application keeps a protected logical destination binding to the intended person, selected account/service and conversation. The transport adapter resolves current route evidence for a new delivery. No new permanent public forwarding address or global correlation handle is introduced. The composer, contacts and normal conversation history MUST NOT substitute the temporary alias for the personal address or ask the person to manage routine alias expiry. Failed renewal is a pending or failed delivery, not an expired contact or a changed encryption identity.

A generic SMTP adapter necessarily knows its exact RCPT TO and proof internally. Provider-originated submission may keep this machinery outside the application UI. A protocol in which even the submitting adapter never learns the physical alias is not selected here: the existing delivery proof binds that exact alias with a client-only key. A provider cannot silently rewrite that proof, obtain the key or claim an undefined logical-to-physical projection authorization.

Historical reading needs no live route. A reply resolves current routes from accepted conversation identities and personal associations. An exact queued or uncertain retry retains its old alias, proof, ciphertext and delivery identity. Expiry holds that attempt; renewal cannot retarget already released bytes or erase uncertainty. A separately authorized replacement follows the owning contribution/delivery conflict rules.

## Exact authority records and provider-key rotation

::: {.details summary="Exact authority records and provider-key rotation"}

### Common wire and signature rules

Relay-specific records use strict UTF-8 JSON under [event encoding](event-encoding.md). Preserve original bytes; reject duplicate decoded names, numbers, null, unknown fields, trailing values and noncanonical encodings. Times, sizes and durations are canonical uint64 decimal strings. ObjectIds are nonzero32 lowercase hex; keys/digests/route/issuance/source IDs are64 lowercase hex. Endpoint references retain `{principal,device,state,binding,key}` and principal identifiers retain nonzero `enp0` encoding. Mailboxes follow the [canonical address contract](mailbox-addresses.md). Duration/interval arithmetic must not wrap.

A signed wrapper has exactly `payload` and `signature`: canonical padded-base64 original payload bytes and128 lowercase-hex Ed25519 signature. New signature input is the exact ASCII domain below, NUL, U32 big-endian original payload length and original bytes. Never verify a reserialization or try another signature kind after failure.

| Record | Domain |
| --- | --- |
| Provider route-key certificate | `mail/relay/route-certificate/v1` |
| Receiving-service authorization | `mail/relay/receiving-service/v1` |
| Sending-device route request | `mail/relay/route-request/v1` |
| Route-key issuance inspection | `mail/relay/route-request-inspect/v1` |
| Provider-issued route | `mail/relay/route-issuance/v1` |

Management/request/result bodies are at most4194304 octets, each signed payload at most262144 with depth32. Inspection and delivery payloads retain the tighter8192-octet/depth16 bounds. Apply identity/certificate-specific bounds too. Services enforce finite work, active-record, rate, byte, lifetime, certificate-chain and retained replay budgets before mutation. Limits are adjustable deployment policy, not user quotas; exhaustion cannot evict live replay protection or expand authority.

HTTP uses application/json, TLS1.3, no 0-RTT, redirects, ambient cookies or response caching. Management requires the exact issuer/audience/client/account/family/incarnation/scope. Errors use exactly `{error}` with the provider error vocabulary; generic401/403 for management authorization,404 for unavailable proof-bound resources,503 for transient dependencies and429 with positive Retry-After for exhausted finite budgets. Do not echo submitted identities, aliases, credentials or detailed block state. No field supplies a callback URL. Discovery, source retrieval and peer operations obey the selected network boundary, including all DNS answers and the connected address.

### Provider route-key certificate

The certificate payload has exactly:

| Field | Required value or meaning |
| --- | --- |
| `version`, `purpose` | `"1"`, `"relay-route-certificate"` |
| `certificate` | Fresh nonzero ObjectId |
| `domain`, `issuer` | Selected service domain and exact HTTPS origin |
| `serviceSigningKey`, `routeSigningKey` | Stable service-authority key and certified issuance key |
| `notBefore`, `notAfter` | Original finite certificate interval |

The stable service key signs the certificate; the certified route key signs issued routes. Neither is an endpoint decryption key. No account, contact list or recipient appears in a certificate. Certificate validity is independent of the HTTPS certificate’s expiry. Descriptor refresh may advertise another certificate under the same stable service key without changing the recipient’s existing service authorization. Preserve original records and their absolute intervals.

A newer descriptor generation must still authorize the same domain/origin, stable service key and recipient-mask role. A client may retain an older certificate/route while those conditions hold, the certificate remains within its original interval and the live service confirms it is not withdrawn. A new descriptor generation does not automatically revoke every older certificate. Withdrawal and new route admission/release serialize at the provider. A compromised/withdrawn route key blocks new use of all its certificates; an accepted exact duplicate can still return its historical outcome without new delivery.

Changing the stable service key or service origin requires a fresh service association during normal account reconnection. There is no unsigned key rollover or automatic credential migration. The service may rotate its certified route keys automatically; this does not grant a new account incarnation or extend existing route validity. TLS validation, provider service-key validation and endpoint identity validation remain separate checks.

### Establish receiving-service authority

`POST /receiving-service/preparations` under managementPrefix requires the recipient’s active own-account relay link and manage scope. Its body is exactly `{version,purpose,request,link,notBefore,notAfter,maxRouteSeconds,maxCarrierBytes}`, version `"1"`, purpose `relay-receiving-service-request`. The service derives the actual account, selected recipient endpoint and incarnation from that authenticated link. Request fields cannot select another account or principal.

The returned prepared authorization payload has exactly:

| Field | Required value or meaning |
| --- | --- |
| `version`, `purpose` | `"1"`, `"relay-receiving-service"` |
| `authorization`, `preparation`, `request`, `nonce` | Fresh authorization/preparation ObjectIds, original request ObjectId and fresh64hex challenge |
| `domain`, `issuer`, `delegation` | Selected service domain/origin and SHA256 of original descriptor1 bytes |
| `recipient` | Exact linked endpoint authorizing the service association |
| `incarnation` | Opaque64hex receiving-account incarnation commitment, not a private account identifier |
| `serviceSigningKey` | Selected stable service-authority public key |
| `notBefore`, `notAfter` | Original finite interval within link/family/device/service authority |
| `maxRouteSeconds`, `maxCarrierBytes` | Positive finite offered limits, bounded by account/service policy |

This record contains no alias, route, peer or conversation. The client checks the selected service/account and actual offered limits during normal account connection, then signs the exact bytes with its linked receive-authorized device. No individual route approval follows. `PUT /receiving-service/preparations/{preparation}` has exactly `{proof}`. Recheck current authority, original preparation, account/family/link/incarnation and service selection under the activation transaction. Return201, or200 for an identical retained retry, with exactly `{authorization,recipientIdentity}`: original signed wrapper and complete recipient identity bundle. Different authenticated bytes under the same request conflict409; invalid signatures cannot reserve that namespace.

Retain the original endpoint/descriptor/signature. For a later unrelated identity or descriptor advance, use [unchanged-binding ancestry](provider-grants.md#retain-an-unchanged-device-binding) for its receive role and the same selected service/stable key/current descriptor authority. Do not demand a signature for each descriptor byte change or alias. Missing ancestry, revoked/changed authorizing binding, conflict, state1 repair, changed principal/incarnation or expired family holds new use until a fresh eligible service association. It cannot repin a correspondent or restore authority from historical archives.

Private account admission/contact/block policy determines which authenticated sources receive routes; no universal allow-all default is implied. Do not disclose that policy’s contact/principal inventory in this public record. `DELETE /receiving-service/{authorization}` requires own-account manage scope, returns204 for own known/unknown IDs and atomically withdraws its routes and unreleased work. Reconnection or refresh-token rotation in the same eligible family cannot extend the original authorization; obtaining a fresh finite authorization is account connection maintenance, never alias consent.

:::

## Exact route issuance, inspection and immutable retries

::: {.details summary="Exact route issuance, inspection and immutable retries"}

### Select the existing source permission

The source preparation/activation/live inspection and exact result `{proof,identity}` use [source-permission0](relay-routes-compatibility.md#source-permission), with its original `email2/relay/source-permission/v0` signature domain and exact schemas. Select it explicitly under descriptor1; do not rename its signed bytes. Its descriptor digest binds the actual selected source descriptor. Sender/account/device/key, recipient principal, conversation, targetService, source/incarnation abuse handles, sender-mode/outerFrom, interval and byte limit retain every original check. The source device independently has current send/receive authority; an account link alone grants no sending authority.

The original source permission stays active at its own service. The destination discovers the declared sourceDomain, validates its current allowed descriptor and exact issuer/delegation, and fetches only the selected permissionPrefix plus expected identifier over authenticated HTTPS. No arbitrary URL, HTTP cache or remembered active boolean substitutes for that live observation. Source outage holds new route work. The original source-account abuse handle remains stable across reset/relink/new aliases; reset rotates a separate incarnation and invalidates permissions.

### Request a provider-issued route

`POST <permissionPrefix>routes` is a public proof-authenticated operation. Body has exactly `{request,sourcePermission}`: original sending-device signed request wrapper and the complete original source permission result. The request payload has exactly:

| Field | Required value or meaning |
| --- | --- |
| `version`, `purpose` | `"1"`, `"relay-route-request"` |
| `request`, `nonce` | Fresh request ObjectId and64hex nonce |
| `issuer`, `delegation` | Exact destination origin and SHA256 of its selected descriptor1 bytes |
| `recipient`, `sender`, `conversation` | Intended recipient principal, original source endpoint and conversation ObjectId |
| `sourceDomain`, `sourceService`, `sourcePermission`, `sourceDigest` | Authorized source domain/origin, permission64hex and SHA256 of original source-permission payload |
| `notBefore`, `notAfter`, `maxCarrierBytes` | Original finite requested interval and positive byte limit |

Authenticate the signature against the exact source endpoint and independently validated complete identity/current authority. Then validate the live source permission, exact destination/recipient/conversation, requested intervals and deployment budgets **before private recipient lookup or authoritative request allocation**. Invalid source signatures cannot reserve a conflict, trigger a private lookup or cause a callback. Previously unknown recipient evidence is not installed as a client identity pin by the service.

For every valid authorized source request, return202 exactly `{issuance,state}`, state `pending`, including unknown, blocked, opted-out or currently unavailable recipient cases. Issuance is64 lowercase hex: SHA256 of ASCII `mail/relay/issuance/v1`, NUL, U16-length-prefixed destination origin, U16-length-prefixed source service origin, raw32-byte sourcePermission, raw16-byte request ObjectId and raw32-byte SHA256 of original request payload. Origin lengths count UTF-8 bytes and must fit U16. Keep the original source/request namespace across versions. Check authenticated different-byte request reuse before deriving/creating another result; it conflicts409 rather than selecting another handle. The committed request’s source identity is `(sourceService,sourcePermission,request)`; a new descriptor/version cannot reset it.

Durably retain the exact request, source evidence, handle and pending receipt before success. A duplicate joins the original work and returns the same receipt without another alias. The HTTP202 response never claims routing readiness or recipient/device presence. Apply the same bounded response shape and finite processing policy across target states; no exact constant-time or invisible successful opt-in claim is made. Live source unavailability before authorization gives generic503, not a guessed target result.

The provider may allocate immediately or later while original request/source bounds remain valid. It derives the recipient account privately from its own current service association and account policy. Check active service authorization/link/family/incarnation, current receive authority, certified provider key, source blocks and per-source/destination limits in the same local serialization boundary as route/alias allocation. Allocate random nonzero64hex route ID and alias `r-<random nonzero ObjectId>@<descriptor domain>`, with128 independent random bits and no personal-address encoding. The alias maps only to this account incarnation; it is never reassigned. No live recipient process or per-alias signature is involved.

### Inspect pending or issued work

`POST <permissionPrefix>issuances/{issuance}/inspect` has exactly `{proof}`. It is signed by the original source permission’s route key. Its payload is exactly `{version,purpose,issuer,issuance,requestDigest,nonce,notBefore,notAfter}`, with `"1"`, `"relay-route-request-inspect"`, exact origin/handle and original request SHA256, fresh64hex nonce and finite interval inside the original request and source permission. A fresh proof cannot refresh either deadline. Validate structure, signature and current source before disclosing a result. Scope the nonce journal to the retained issuance and authorized route key: exact inspection bytes may be retried within their original interval and return the current eligible pending/ready observation; different authenticated bytes under that nonce conflict409. An invalid proof cannot reserve a nonce or an authoritative conflict. Status observations do not activate a route or extend any authority. Invalid/unknown/nonmatching proofs get indistinguishable404 and cannot consume another source’s inspection/replay capacity.

The response is exactly `{issuance,state,invitation}`. Pending has state `pending` and invitation the empty string. Ready has state `ready` and invitation canonical base64 of the original complete invitation1 bytes. Unknown/unavailable/blocked target states remain pending for the authorized source. Recheck original request bounds, live source permission, private disclosure policy and current local dependencies before returning ready. Retain request/inspection conflict and finite nonce-replay state under the existing source authority; exhaustion holds rather than evicting live safety state. GET never mutates authority.

### Validate the issued route

Invitation1 has exactly `{issuance,authorization,certificate,recipientIdentity}`. Issuance is the original provider-signed wrapper, authorization the original receiving-service wrapper, certificate the original provider route-key certificate, and recipientIdentity the complete identity bundle needed to validate the original service association and current recipient authority. There are no OAuth tokens, personal account mappings or contact lists.

The provider-signed issued payload has exactly:

| Field | Required value or meaning |
| --- | --- |
| `version`, `purpose` | `"1"`, `"relay-route-issued"` |
| `issuance`, `request`, `nonce` | Original issuance64hex, request ObjectId and request nonce |
| `issuer`, `delegation`, `authority` | Destination origin, original descriptor1 digest and SHA256 of original receiving-service authorization payload |
| `route`, `alias` | Fresh64hex route ID and this provider’s opaque delivery mailbox |
| `recipient`, `sender`, `conversation` | Recipient principal, exact original source endpoint and conversation ObjectId |
| `sourceDomain`, `sourceService`, `sourcePermission`, `sourceDigest` | Exact original source permission bindings |
| `routeKey` | Original source permission’s fresh route public key |
| `notBefore`, `notAfter`, `maxCarrierBytes` | Actual offered finite interval and positive byte limit |

The sender validates every original signature and commitment, selected expected recipient principal/association and current identity. Authorization/certificate/issued route must agree on service domain/origin and stable service key; certificate supplies the actual issuance key. Require the certificate interval, original service authority, source permission, both required device bindings, link/family/incarnation and current policy. Offered route duration must not exceed maxRouteSeconds; its interval and byte limit fit all authorities. A client checks actual offered limits rather than assuming requested limits were granted. A descriptor generation refresh may preserve this original record only under the service/key continuity rules above; changed scope is a new issuance, never a rewrite.

Live activation inspection uses the exact existing route-key `POST /routes/{route}/inspect` payload/domain from [inspection0](relay-routes-compatibility.md#recipient-route), selected at managementPrefix. It returns this original invitation1 only while current service/account/certificate/route/source authority is active. It cannot extend validity or return a different alias. Source fetching remains origin-selected and bounded. A provider signature or a ready issuance response cannot substitute for this current check.

:::

## Prove a delivery without exposing personal identities

Use the exact [delivery0 proof, SMTP header and opaque carrier](relay-routes-compatibility.md#prove-a-delivery-without-exposing-personal-identities), including the original `Email2-Route-Proof` field and `email2/relay/delivery/v0` signature domain. Descriptor1 explicitly selects this delivery shape with route1. Its route key authenticates only transport scope; source/recipient identities and conversation scope are retained privately at the services, not added to the outer proof. Current application/control carriers remain their independently selected encrypted bytes; an opaque attachment is not proof of encryption.

The source provider’s authenticated submission/status API retains its exact version0 body/receipt/status inventories, immutable accepted outbox and uncertainty semantics. It cannot change the alias or signed carrier after submission. Personal-source mode keeps its independent SMTP account authority. Sender-only masking uses the exact empty destination route/issuer case and cannot claim recipient masking.

## Destination acceptance and retries

For every new delivery, the destination:

1. Selects the local alias/route and enforces exact SMTP/header/MIME/carrier limits, without following message-supplied locations.
2. Validates the original delivery signature and exact issuer/route/alias, sole outer From, actual MAIL FROM, Message-ID and decoded encrypted-carrier commitment.
3. Checks retained `(route,delivery)`. Identical original authenticated proof and carrier bytes return the original SMTP outcome without another insertion; different authenticated bytes conflict. Invalid proofs cannot reserve that identity.
4. Checks current account/link/family/incarnation, service authorization, provider certificate/key, recipient authority, route/source expiry, block policy and byte/rate bounds. It freshly fetches the exact live source permission from its accepted service. Unavailable current evidence holds with temporary SMTP failure.
5. Serializes local dependency recheck, exact proof/carrier/envelope observations, deduplication row and idempotent mailbox-delivery intent in one durable decision before SMTP success.

Mailbox append participates in that decision or consumes its durable intent idempotently. Crash/restart cannot lose an acknowledged delivery or replay its visible application effects. Temporary dependency/resource failure and generic permanent invalid/revoked/unsupported failure follow [SMTP error rules](transport.md), without exposing account existence, block status or detailed crypto failures. Never bounce a decrypted original to a generic relay.

Accepted duplicates can return prior success after expiry or withdrawal because they create no new delivery. Preserve replay evidence through route validity and the retained retry horizon; do not evict live identities to admit more work. Once retired without retained state, expired/revoked traffic cannot become new work. A live source observation is not instantaneous distributed revocation. Downstream copies still need owning application identity/deduplication checks.

## Withdrawal, blocks and account changes

Own-account manage operations retain `DELETE /permissions/{permission}`, `DELETE /routes/{route}`, their whole collections and the source-block create/delete schema from the [retained management subset](relay-routes-compatibility.md#withdrawal-blocking-and-account-changes). Their existing exact source handle/known-principal attribution, idempotent result, account isolation and request-conflict rules remain required. Add the receiving-service withdrawal above. Withdrawal serializes with local admission/release and prevents later new effects; it cannot recall earlier bytes or erase correspondence.

Source-account blocks persist across relinking/reset, new route keys/aliases and source incarnation changes. Authenticated known sender principals stay blocked across service changes. Unblocking one record does not clear another active block. Alias rotation cannot bypass either policy. Provider admission policy does not claim universal real-person identification: a hostile service can issue new accounts, and a person can change both service and identity. No government identity check or central relay allowlist is required.

Deleting/disconnecting/resetting a relay account link or family revokes derived service authorizations, source permissions, routes and unreleased work. Reassignment rotates the account incarnation and never reuses aliases. An unrelated accepted identity advance uses unchanged-binding ancestry; a changed authorizing key/required role, unresolved conflict or state1 repair requires a fresh service association/source permission as appropriate. This is service/account maintenance, not device approval of individual routes. Identity retirement blocks new operational release. Preserve original records, uncertainty and historical identity attribution.

Moving service origin/stable service key requires normal account reconnection and fresh service authority. An independent receiving relay retains direct encrypted-mailbox retrieval under [mailbox integration](mailbox-integration.md); forwarding to a personal SMTP destination is not selected. A future opaque forwarding chain needs a complete per-hop authorization/privacy contract.

## Route-key retirement

The sending route private key is a signing credential, never a decryption or admission key. Keep it only while its source/route scope needs new signatures. Expiry, withdrawal, source reset or local disablement retires it under [secret retirement](setup-secret-retirement.md). Exact precomputed delivery proofs can support authorized retries without retaining that key; renewal creates fresh material. Historical archives exclude live route keys, service-management credentials and outbox authority.

Providers receive no route private key or endpoint decryption key. They hold their own route/service signing keys under operational custody and finite certificate policy. Public evidence may remain for historical interpretation and deduplication. Deleting a row is not proof of physical erasure; platform evidence is separate.

## Acceptance obligations

Demonstrate initial route issuance and renewal with the recipient device process stopped, using actual source, recipient-service association and provider signatures. The client must send/receive a real encrypted message and display personal addresses while raw transport contains only the selected opaque projection. An alias-allocation fixture or configured active flag is insufficient.

Exercise wrong issuer/domain/key/certificate/descriptor/recipient/account, changed stable service key, certificate rotation/withdrawal, absolute expiry, unrelated accepted identity advance, revoked binding, conflict and state1 repair. Prove automatic renewal preserves private blocks/budgets and exact old uncertain attempts. Inspect source/account/role separation, direct independent-relay retrieval, negative personal forwarding, trace/DSN/report/log leakage and current release checks.

Exercise uniform pending admission before any recipient process runs; route-key inspection, invalid-proof non-poisoning, exact replay/conflict across versions, lost responses, concurrent allocation/revoke/reset, durable restart/crash before/after route and inbox commitment, and exhaustion without dropping live safety state. A public service must preserve the complete current discovery/login/account/link/source authority; mocked identities or trusted booleans cannot establish it.

The [synthetic original records](examples/provider-route-records.json) and `evidence/provider-route-records.test.mjs` exercise actual independent signatures, complete field inventories, scope/interval commitments and provider-certified key rotation on constructed inputs. They are not a strict wire decoder, accepted identity journal or runtime provider. Specification compilation and these narrow cases do not prove a provider implementation, native integration, actual SMTP privacy, independently developed interoperability or security assurance. Record each observation at its actual tested scope.
