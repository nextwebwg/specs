---
title: Retained device-approved route experiment
order: 6.25
blurb: accountable services · peer-scoped aliases · delivery proofs · revocation
sectionNav: true
---

# Retained device-approved route experiment


> [!note] Retained experiment only
> This chapter preserves the exact version0 recipient-device approval contract and the scope of its existing component evidence. It is not the current Recipient masking procedure, an optional current security tier or a fallback after a current validation failure. Current clients use [inbox-provider route issuance](relay-routes.md), without device approval of individual aliases. Existing experimental signed bytes and their recorded results retain their original meaning.

Current route1 reuses only the source-permission, inspection, delivery and management subsets it explicitly selects from this chapter. That selection does not enable the retained recipient-device route-preparation or approval procedure.

A private delivery address is a permissioned route to an account, not an anonymous forwarding address. The recipient approves which peer can use it. The sending side proves an accountable service account and possession of a key reserved for this route. The recipient service checks those permissions before accepting a new delivery.

> [!ex] Forwarding an alias does not forward permission
> Bob's service creates a route for Alice in their selected conversation. Alice signs each delivery with the route key that Bob approved. If someone copies the alias from a source email, that person still cannot produce an authorized new delivery. Bob can disable the route or block Alice's source account without deleting correspondence already received.

This chapter defines the provider wire and lifecycle rules used by the independent [Sender masking and Recipient masking modules](modules.md). The [swap sequence](private-routing.md#when-the-addresses-change) owns client-visible behavior; the [inner address record](private-address-presentation.md) owns personal From/To/Cc inside encryption. This is part of the same Email/2 specification, not another edition or encryption tier.

> [!note] Contract and component evidence
> The scoped grant and delivery-proof contract below is proposed. The [local route experiment](evidence/README.md#relay-route-authorization) checks actual device/key signatures and a durable admission/replay boundary using configured account and source-service facts. It does not implement public discovery, browser account linking, provider HTTP issuance, SMTP proof-header carriage or a production mailbox. These are acceptance obligations, not deployed capabilities.

## The three permissions

**An account link** connects an authenticated service account to an authorized Email/2 device. It never supplies mailbox ownership verification, group membership or decryption authority.

**A source permission** is a live record at that account's selected service. It authorizes one current sending device and fresh route public key for one recipient principal and conversation. It also supplies a stable, opaque abuse handle for that service account at the destination service. The service knows the account; an observer of the outer email does not receive that mapping.

**A recipient route** binds the source permission to an opaque alias and the recipient account. The recipient device approves its exact scope; the destination service activates it only under the recipient's account authority. It is not sufficient for either a device or a provider to nominate an arbitrary third-party address alone.

No route credential grants application authorship. A stolen route private key can cause bounded unwanted ciphertext deliveries until withdrawal, but cannot create a valid contribution from a different MLS author. The client must still complete cryptographic and application acceptance before display or effects.

## Set up and authorize

The sending client creates a new Ed25519 route key independently of its identity signing key. Keep its private part in protected local state. Do not publish the identity/device key in an outer email to prove route use. Different unrelated recipient/conversation scopes use different route keys and aliases.

The sender's account service authenticates the account, checks its linked device's current `send` and `receive` authority, then prepares the source permission. The device approves the exact record before activation. Its service may also offer sender masking. An independent service offering account accountability alone can supply source permission while the client continues using an ordinary authenticated SMTP account; that does not claim the ordinary provider upgraded.

The recipient client checks the source permission, selects its known peer/conversation and requests route preparation through its own account service. The service verifies the source's live record directly and creates an alias in a domain it controls. The recipient approves the exact result. Remembered contact/setup policy may authorize these routine approvals without another prompt; incoming mail or a provider boolean cannot create that policy.

The sender receives the recipient-approved route through the authorized setup/control exchange or an already protected conversation. Before using it, the sender validates the expected recipient identity, current authority, original source permission, exact scope and issuer. It then uses its route private key to inspect the active route directly at that issuer. A signature is not proof that the server activated the route.

The alias and route-use proof replace only transport routing. Personal addresses remain in the composer and protected application. A permission for one conversation cannot be reused as an account-wide receiving address, and a new device needs its own permission/key. Delivery to the account is not enrollment of any device.

## Discover a relay service

For a provider-operated service, fetch `https://<selected account domain>/.well-known/mail-relay`. For an independent relay, use the domain of the service account deliberately selected by the person. Do not discover an independent relay from a received URL or infer it from MX. Its ability to attest its own service account does not prove ownership of an unrelated personal mailbox.

Apply the [provider discovery transport and durable publication rules](provider-discovery.md): credential-free HTTPS, authenticated selected domain, no redirects, no compressed bodies, bounded processing, canonical validated domains/origins and explicit local setup purpose. Use a separate retained purpose/namespace for relay setup. The record has exactly:

```
{version,purpose,domain,publication,generation,service,managementPrefix,
 permissionPrefix,roles,notBefore,notAfter}
```

`version` is `"0"`; `purpose` is `"relay-service-discovery"`. Other fields retain the provider-discovery grammars; the two same-origin path prefixes are distinct and nonoverlapping. `roles` is a nonempty ASCII-sorted distinct array from `accountability`, `recipient-mask`, `sender-mask`. Recipient masking is independent of sender masking. Source-permission issuance requires accountability; sender-mask therefore requires accountability as a declared dependency. Accountability-only and recipient-mask-only services are permitted. An unimplemented role must not be advertised. A changed descriptor cannot move credentials or revive old permissions.

Use the same native registration, authorization-code/S256 PKCE, issuer-bound browser response, refresh/revocation and public-client rules as provider discovery, with the scopes `mail.relay.link`, `mail.relay.manage` and `mail.relay.submit` in place of queue scopes. Apply the [shared native connection binding](provider-discovery.md#reuse-sign-in-mechanics-without-sharing-permissions), including its exact shared callback forms, module-separated registration/attempt state and exact requested scope set. Request only scopes needed for selected roles. Metadata must advertise those requested scopes; relay-only implementations need not offer a queue. Registration or metadata does not prove an app brand. The well-known name and fields are experimental and remain in the [registration inventory](registration-inventory.md); no registry assignment is claimed.

Account linking uses the [account-link challenge/proof construction](provider-grants.md#account-linking), under this management prefix and relay-link scope. Its delegation digest names this exact relay descriptor. Keep links, preparations and OAuth families in the relay namespace; a queue link/token is not relay authority. Exact account-incarnation, same-family, device possession, reset, consent and current-state checks apply. Link/reset/disconnect routes have the same suffixes and behavior, but the selected relay scope and namespace. A source permission additionally requires `send`, which linking alone never grants. The [shared-link subset](provider-grants.md#shared-account-links-separate-module-authority) fixes the inherited wire purposes/signature framing, private account-contact meaning and module-local reset boundaries; no queue routes or foreign-domain mailbox authority are inherited.

::: {.details summary="Exact records, signatures and HTTP behavior"}

### Exact records, signatures and HTTP behavior

### Common wire rules

Management requests authenticate the person's own account using issuer/audience/client/family/incarnation/scope checks. Peer requests never receive that token. TLS1.3, no 0-RTT/redirects/ambient cookies, no-store responses and bounded backoff apply. OAuth access is not a cryptographic identity proof.

The relay-specific records below use strict UTF-8 JSON under [event encoding](event-encoding.md): preserve exact bytes, no duplicate decoded names, numbers, null, unknown fields or trailing values. Times, byte limits and generations are canonical unsigned-64 decimal strings. ObjectIds are nonzero32 lowercase hexadecimal; digests, permission/route/source IDs and keys are64 lowercase hexadecimal. Principals and endpoint references use existing `enp0` and `{principal,device,state,binding,key}` encodings. Domain/mailbox spelling follows the selected initial address contract. A credible time interval must fit every applicable interval. The inherited [account-link/reset subset](provider-grants.md#shared-account-links-separate-module-authority) instead retains its own exact schema and safe JSON integer timestamps. This exception does not relax relay source, route, inspection or delivery schemas, and parsing failure cannot switch schemas.

A signed wrapper is exactly `{payload,signature}` with canonical padded base64 original payload and128 lowercase hexadecimal Ed25519 signature. The signature input is ASCII `email2/relay/<kind>/v0`, NUL, u32 big-endian payload byte length, then original payload. The kinds are `source-permission`, `route-approval`, `inspect`, and `delivery`. A signature under another kind is invalid. Endpoints retain original bytes; they never verify a reserialization.

Management bodies are at most4194304 octets, individual signed payloads at most262144 and depth32, with each identity bundle's tighter bounds also applying. Inspection and delivery proofs are at most8192 decoded payload octets and depth16. Descriptor bounds remain those of provider discovery. Services enforce finite work, active-record, rate, byte and lifetime budgets before mutation; negotiated limits are service policy, not user quotas. Exhaustion cannot evict live replay protection or expand authority.

POST/PUT bodies use application/json. DELETE has no body. Error bodies are exactly `{error}` with the existing provider error/status vocabulary. Management authorization failures use401/403 as appropriate. Unavailable public permissions, invalid possession proofs, expired/revoked/unknown routes use indistinguishable404; transient dependency failures use503, exhaustion429 with positive Retry-After. Errors do not echo identities, aliases, tokens or submitted records. GET never mutates authority. No request field supplies a callback to contact.

### Source permission

`POST /permissions/preparations` requires an active relay account link and manage scope. Body is exactly `{version,purpose,request,link,sender,recipient,conversation,routeKey,targetService,senderMode,outerFrom,notBefore,notAfter,maxCarrierBytes}`. Version is `"0"`, purpose `relay-source-request`, sender is the linked endpoint, recipient a principal, conversation an ObjectId, routeKey a fresh Ed25519 public key. Service checks current exact linked state/binding and `send`/`receive`, local account/family authority and intervals before preparing.

SenderMode is `shared-relay` or `personal-source`. Shared-relay requires advertised sender-mask support; outerFrom is the service's authorized common relay mailbox at the descriptor domain. Personal-source uses the normally authorized SMTP account's personal From; the accountability service does not claim to verify ownership of an unrelated mailbox. Its intended From is still bound to the device approval and delivery proof. The client independently checks its actual SMTP source authority.

TargetService is the exact selected destination relay origin. Empty is allowed only for sender-masking delivery to an ordinary destination without a recipient route. Such a permission cannot activate recipient masking. For a nonempty destination, `source` is an opaque random service-account abuse handle scoped to that destination service. It remains stable across relinking, key/identity reset and new aliases for the same continuing service account. `incarnation` is a separate opaque source-account incarnation scoped to the destination; reset rotates it and invalidates permissions but must not reset the abuse handle. Empty-destination permissions use their own scoped source/incarnation values and remain accountable to the originating service.

The prepared payload has exactly:

```
{version,purpose,preparation,request,nonce,permission,domain,issuer,delegation,
 source,incarnation,sender,recipient,conversation,routeKey,targetService,
 senderMode,outerFrom,notBefore,notAfter,maxCarrierBytes}
```

Version is `"0"`, purpose `relay-source-permission`; domain is the selected relay descriptor domain; issuer is this service origin; delegation is descriptor SHA256; preparation/request ObjectIds; nonce64hex. Remaining request values are unchanged. Permission/source/incarnation are service-generated opaque IDs. Its interval and maxCarrierBytes are the explicit offered limits, within device/link/family authority and service policy. A client must approve the offered limits, not assume its requested limits were accepted.

`PUT /permissions/preparations/{preparation}` body `{proof}` signs those exact retained bytes with the sender device binding key. Under one transaction, recheck account/family/link, exact preparation, current state/binding/roles and validity, then activate the permission. Same authorized bytes retry returns the recorded result; different content under an authenticated request namespace conflicts. Result is exactly `{proof,identity}`: original sender proof and complete sender identity bundle. The provider's live HTTPS response supplies service-account activation evidence; the device signature alone does not.

`GET <permissionPrefix><permission>` is credential-free and returns that result only while the permission/account/link/family remains active and exact device authority/interval still applies. There is no public listing or mailbox lookup. The random ID is routing evidence, not a bearer authority. Do not put its URL/ID in the outer message. A recipient service discovers the approved sourceDomain and requires its descriptor service and digest to match the permission's domain/issuer/delegation before fetching the expected source prefix. It fetches only that selected service/prefix, under the discovery network boundary; never follow an arbitrary supplied URL. Validate the returned original payload hash, signature and current source identity independently. Unavailable state holds new use. This read does not disclose the personal account address.

### Recipient route

`POST /routes/preparations` requires the recipient's active link and manage scope. Body is exactly `{version,purpose,request,link,recipient,sender,conversation,sourceDomain,sourceService,sourcePermission,sourceDigest,notBefore,notAfter,maxCarrierBytes}`. Purpose is `relay-route-request`; recipient is the linked endpoint, sender the intended peer endpoint. Both current receive authority and sender send authority must be available; the source permission's exact sender, recipient principal, targetService and conversation must match. Stage previously unknown peer evidence until valid recipient approval under explicit first-contact policy; no request alone installs a trust anchor.

The service directly fetches and validates the live source permission, including the account-scoped abuse handle, and checks block policy. It allocates route64hex and alias `r-<random nonzero ObjectId>@<descriptor domain>`:128 independent random bits, no personal-address encoding. An alias is never reassigned to a different account or route, including after account deletion. Its private mapping is to this account incarnation and link; that mapping is not returned to the sender.

The prepared payload is exactly:

```
{version,purpose,preparation,request,nonce,issuer,delegation,route,alias,
 recipient,sender,conversation,sourceDomain,sourceService,sourcePermission,sourceDigest,
 routeKey,notBefore,notAfter,maxCarrierBytes}
```

Purpose is `relay-route-approval`. Issuer/delegation refer to the recipient relay. Endpoint/scope/routeKey fields must match the source request and live source permission. The offered interval lies within both bindings, source permission, recipient link/family and service policy; byte limit is the explicit minimum offered by those authorities. The service retains account/family/link/incarnation and the original source record as private preparation dependencies.

`PUT /routes/preparations/{preparation}` body `{proof}` is signed by the recipient binding key over exactly the retained preparation. Recheck all local authority and a fresh source read before activation. A changed dependency holds activation, not substitution in place. Activate route/alias and consume preparation atomically. Result/invitation is exactly `{approval,recipientIdentity}`. The sender independently verifies expected peer/current identity and source scope; it does not treat possession of the invitation as route-key possession.

`POST /routes/{route}/inspect` body `{proof}` uses the route key. The inspection payload is exactly `{version,purpose,issuer,route,nonce,notBefore,notAfter}`, purpose `relay-inspect`; nonce64hex and a finite fresh interval inside the route lifetime. The issuer validates key/scope and active local state plus a fresh source permission read before returning the original invitation. No token, private account mapping or new lifetime is returned. A reply cannot extend a stale grant. Unknown/invalid/expired traffic cannot discover a route by comparing outcomes.

POST preparation request IDs are scoped by account/incarnation/family/endpoint. Persist original input/preparation/result before success. Exact retries never allocate a second permission or alias; authenticated different-byte reuse returns409. Invalid proofs cannot reserve an authoritative conflict. Active-result retries still check withdrawal; a retained result does not reactivate anything.

:::

## Prove a delivery without exposing personal identities

When recipient masking is selected, the outer message has exactly one `Email2-Route-Proof` header. It contains canonical base64 of the UTF-8 signed delivery wrapper. Normal header folding is allowed; remove only ASCII folding whitespace before canonical base64 validation. Multiple headers, invalid folding/base64, excessive size or unknown fields prevent route acceptance. This is an experimental header requiring registration; its name is not assigned.

The decoded delivery payload is exactly:

```
{version,purpose,issuer,route,delivery,alias,outerFrom,mailFrom,messageId,
 carrierSha256,carrierBytes,notBefore,notAfter}
```

Version is `"0"`, purpose `relay-delivery`. Issuer/route/alias equal the approved destination route. Delivery is a fresh random nonzero ObjectId per prepared recipient copy; no global conversation/principal ID appears. CarrierSha256 and carrierBytes commit the exact decoded protected carrier bytes under the relay MIME extraction below. Do not hash a guessed part or treat an opaque part as proof that its contents are encrypted. CarrierBytes is positive and within the current permission/route limit. The proof interval lies within the route/source interval and the service's finite delivery-proof policy. Sign with the private route key.

OuterFrom must match the source permission and the sole parsed outer From, without a personal display name in shared-relay mode. Alias must match the actual SMTP RCPT TO. MailFrom binds the actual SMTP reverse path. MessageId binds the sole outer Message-ID. For shared-relay origination use `b-<delivery>@<descriptor domain>` as the opaque reverse path and `<m-<delivery>@<descriptor domain>>` as Message-ID. They expose only this random delivery identifier. The source service atomically reserves their collision-free account/delivery mapping; an authenticated collision holds the new preparation. Personal-source mode retains its ordinary authorized reverse path and opaque Message-ID without claiming sender masking.

### Relay MIME extraction

The relay-originated message is exactly a `multipart/mixed` entity with MIME-Version1.0 and two direct parts: a generic `text/plain; charset=utf-8` notification, then one parameter-free `application/octet-stream` base64 attachment. The notification's decoded UTF-8 text is exactly `Protected Email/2 delivery.\r\n`; it contains no personal metadata. The attachment has exactly one `Content-Disposition: attachment; filename="message.bin"` and no Content-ID. The root Content-Type has exactly one boundary parameter and no other parameter. Preamble and epilogue are empty apart from MIME separator line breaks. Notification part headers are only Content-Type and its single7bit Content-Transfer-Encoding; attachment part headers are only Content-Type, its single base64 Content-Transfer-Encoding and Content-Disposition. No nested multipart, extra resource, forwarded message or external-body is admitted. Use normal MIME base64 folding; reject invalid alphabet, padding or nonzero unused bits. The attachment's exact transfer-decoded octets are the carrier commitment input. Transfer re-encoding can preserve that commitment; replacing decoded bytes cannot.

Duplicate/ambiguous Content-Type, transfer-encoding, disposition or route-proof fields, malformed boundaries, excessive structure or unrecognized layout reject automatic route acceptance. Bound the SMTP input before parsing and the decoded attachment before allocation; enforce the active grant's carrier limit and local configured total-wire/header budgets. Reject incomplete processing rather than delivering a prefix. Source retention follows the mailbox's bounded storage policy.

The client passes these original carrier bytes to the independently selected protected application or control contract; the route proof does not select an older parser or authorize a group transition. Raw JSON containing personal addresses or public identity evidence is not made confidential by wrapping it in an octet-stream attachment. Current-suite control/admission uses the [sealed-control binding](suite-profile.md#confidential-setup-and-control). The independently offered [deletion-control profile](deletion-controls.md) may likewise supply its exact sealed binary only under actual route/account/scope authority; it does not create a new route grant or activate a generic control queue. Its exact encrypted binary is the opaque carrier, and the recipient checks its inner actor/target/conversation against this route after decryption. Unsupported protected-control carriage remains held, not downgraded into a readable attachment. Provider-assisted first-contact traffic keeps its separate setup-metadata boundary.

The originating relay's authenticated `POST /submissions` requires submit scope, an active own-account source permission and device/route-key possession. Body is exactly `{permission,proof,carrier}`; carrier is canonical base64 decoded bytes matching the delivery commitment. For sender-only masking, the same proof has empty issuer/route and a personal recipient as alias; no destination route or proof-header claim is made. The service verifies source account/device and its exact projection, stores an immutable per-account/incarnation/permission/delivery outbox and returns202 only after durable local acceptance. The202 body is exactly `{submission,delivery,state}`, with submission a nonzero ObjectId, delivery the original delivery ID and state `queued`; it is the immutable local acceptance receipt, not current progress. Exact retained retries return that same receipt, not a second send. A changed signed intent under that delivery is409. Current release and DSN/uncertainty rules still apply;202 is not recipient acceptance.

Authenticated `GET /submissions/{submission}` under the same own-account submit authority returns exactly `{submission,delivery,state}` with state `queued`, `released`, `uncertain`, `failed` or `cancelled`. Released means accepted by the selected next transport hop, not read or end-to-end recipient acceptance. Preserve attempt/uncertainty history internally; a status refresh must not manufacture a fresh send or imply recall. Unknown IDs under that account return404. Disconnection/revocation can cancel only unreleased work.

A client using personal-source mode can instead submit through its normally authenticated SMTP provider, retaining the exact proof header/carrier/envelope. Neither path transmits route private keys. A sender-only relay checks its own current permission and normal accountable outbound policy even though the destination does not implement recipient masking.

## Destination acceptance and retries

Before committing a new masked delivery, the receiving relay:

1. Selects the exact local alias/route and checks structural/header/carrier limits without automatic callbacks from message-supplied locations.
2. Verifies the original delivery signature using that route's retained authorized key and matches issuer, alias, sole outer From, actual MAIL FROM, Message-ID and decoded carrier commitment.
3. Checks the retained accepted-delivery key `(route, delivery)`. Identical original signed proof and carrier bytes return the original SMTP acceptance without another mailbox insertion. Different authenticated content under that identity is a conflict. Invalid signatures cannot create one.
4. For a new delivery, checks active recipient account/link/incarnation, local route/device authority, expiry, byte/rate budgets and source-account block policy. It freshly reads the exact source permission over authenticated HTTPS, requiring the original committed bytes and active current state; no HTTP cache or remembered `active:true` can substitute. Transient unavailability holds with temporary SMTP failure.
5. Rechecks local dependencies under the same serialization boundary as its durable acceptance and mailbox-queue commitment. Commit the original proof, carrier, immutable envelope observations and deduplication row together, with an idempotent mailbox-delivery intent. Only then return SMTP success.

Use temporary SMTP failure for unavailable dependencies/resources, permanent generic rejection for invalid/revoked/unsupported authority, under the [SMTP error rules](transport.md). Do not reveal account identity, mailbox existence, block status or detailed cryptographic errors in the reply. Never bounce a decrypted original to the generic relay address.

The accepted-delivery row is not a read receipt. Mailbox append must participate in that transaction or consume the durable intent idempotently. A crash cannot create an acknowledged-but-lost local delivery. Downstream retries may still create physical copies; application/carrier identity handling must not turn them into repeated visible effects. Exact accepted retries can receive the prior success after withdrawal/expiry because no new delivery occurs; this does not reactivate the route.

Retain accepted replay records at least through route validity and the retained retry horizon. Do not evict a live accepted identity to make room for a new delivery. After retirement, missing old replay state must reject expired/revoked traffic, never treat it as new. Provider outages or an unseen remote revocation are not solved by a local transaction: the source fetch proves a live service observation at that check, not instantaneous distributed revocation or independent ownership verification.

## Withdrawal, blocking and account changes

Own-account management can `DELETE /permissions/{permission}`, `DELETE /routes/{route}`, or delete all under either collection. Scope is the authenticated account incarnation; unknown IDs yield the same204. Withdrawal and admission/outbox release serialize locally. A completed delete prevents subsequent new local release/admission, but cannot recall bytes already released or erase received history. Source permission withdrawal makes destination checks fail; destination-local route withdrawal requires no cooperation from the sender.

`POST /blocks` is an authenticated recipient manage operation with exact body `{version,purpose,request,sourceService,source}`, purpose `relay-source-block`. It blocks that source-service/account handle across current and future routes at this destination, revokes its existing local routes and suppresses new preparations. The service derives the handle from retained authenticated source evidence; an arbitrary user-supplied handle must not block another account's unrelated traffic. On success return200 with exactly `{block}`, a retained nonzero ObjectId in this recipient account. Exact request retries return the original block identifier. Unblock requires a separate deliberate own-account decision using `DELETE /blocks/{block}`. The block also retains the sender principals authenticated by this account's routes for that source handle. Those known principals remain blocked if they switch source services. Reset, device change or alias rotation cannot erase either block. Unblocking one record cannot remove another independently active account/peer block.

Deleting/disconnecting/resetting an account link or OAuth family revokes derived permissions, routes and queued unreleased intents. Mailbox/account reassignment rotates the account incarnation and never reuses old aliases. An unrelated accepted identity advance preserves existing permission/route approval only through the [unchanged-binding ancestry checks](provider-grants.md#retain-an-unchanged-device-binding). Preserve original endpoint references and signatures. A changed binding, key, required role or scope requires fresh exact approval; eligible remembered policy may approve that maintenance automatically. No silent peer substitution, account migration or alias retargeting is permitted. Moving service origin requires fresh account connection and new routes; retain uncertainty/history from old delivery attempts.

An independent receiving relay stores the encrypted mailbox itself and provides authenticated retrieval under the [mailbox integration contract](mailbox-integration.md). This baseline does not forward to a personal SMTP address. Multi-provider opaque forwarding chains need their own complete per-hop authorization and privacy binding before support; an arbitrary onward alias is not sufficient. Either mailbox providers or independent relay accounts can implement the defined direct-retrieval path.

A destination also applies its explicitly configured source-service admission and abuse policy. HTTPS establishes control of a service origin, not that its operator is honest or requires costly account creation. A hostile operator can issue new accounts/handles, and a person can change both provider and cryptographic identity. Account/peer blocks, finite issuer/source/destination budgets and deliberate recipient opt-in mitigate that abuse; they are not a universal real-person identity or anti-harassment guarantee. This contract requires no government identity check or central relay allowlist.

## Route-key retirement

A route key is a signing credential, not a message-decryption credential or a one-use MLS admission key. Retain its private part only while that authorized route needs fresh signatures. On expiry, withdrawal, source-account reset or local route disablement, retire it promptly under the [secret-retirement contract](setup-secret-retirement.md). Precomputed exact delivery proofs remain available for permitted retries without retaining the private key; a new route or changed intent needs fresh authorization and a fresh key. Do not retain it indefinitely to inspect old correspondence.

Neither provider receives the private route key. Portable historical archives exclude it with other live credentials. Public grant/signature evidence may remain to interpret history and deduplicate already accepted deliveries. Losing the key cannot change the author of an old message or be repaired by restoring a historical archive. Physical erasure still needs platform evidence; deleting a database field alone is not proof that every copy disappeared.

## Acceptance obligations

Test issuance, exact recipient approval, source live-account evidence, role separation, per-device keys, scope/alias substitution, source/recipient resets, current head changes, known revocation, concurrent revoke/accept, duplicate/conflicting delivery identities, queue/append crash points, lost responses, changed routes during retries and bounds exhaustion. Inspect actual SMTP proof-header/envelope/carrier extraction and account-scoped source blocks across newly created aliases. Include independent relay retrieval and negative personal-forwarding privacy cases.

The local component's signed-grant and durable queue checks do not establish these full public-service, SMTP, OAuth or mailbox outcomes. Public discovery/linking, automatic unknown-peer setup, deployed providers, independent implementations and security review remain separate evidence. Unknown-peer bootstrap must not be claimed complete merely because known approved peers can issue a route.


A [state1 identity repair](identity-state.md#concurrent-administration-and-retirement) is a fresh-authorization boundary for retained endpoint permissions and route grants. Do not keep a route operational by selecting only one parent path through the repaired identity. Obtain a newly scoped approval from the repaired head; preserve earlier proofs and uncertain delivery identities without extending them. Administrative proof exchange does not override route withdrawal, grant expiry or required masking. Identity retirement disables further operational release under that identity; it cannot erase prior deliveries.
