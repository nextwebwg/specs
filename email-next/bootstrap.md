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

Fetch `https://<selected mailbox domain>/.well-known/email2-bootstrap` using the [provider discovery](provider-discovery.md) transport, selected-domain validation, bounds, retained-publication/high-water rules and explicit purpose separation. The exact descriptor is:

```
{version,purpose,domain,publication,generation,service,managementPrefix,
 sourcePrefix,exchangePrefix,roles,notBefore,notAfter}
```

Version is `"0"`, purpose `"bootstrap-service-discovery"`. Domain/publication/generation/service/time grammars are unchanged. The three canonical same-origin prefixes end in `/` and are pairwise nonoverlapping. Roles is a nonempty ASCII-sorted distinct array from `request-source`, `respond-target`. Each role may be implemented independently. Names are experimental and remain subject to the [registration inventory](design-resolution.md).

For the person's own account only, reuse issuer-bound native registration, authorization-code/S256 PKCE, refresh/revocation and account-link challenge mechanics with bootstrap namespaces and scopes. `email2.bootstrap.link` permits own-account/device linking; `email2.bootstrap.request` permits own source-permission management; `email2.bootstrap.respond` permits the linked device's own control-inbox/publication operations. Request only needed scopes; metadata must advertise them. Queue and relay tokens/links never become bootstrap authority. Account link and reset proofs bind this exact descriptor digest; the [account-link contract](provider-grants.md#account-linking) applies with this module's scope and namespace.

Discovering a recipient service never signs the sender into that service or forwards source account credentials. Its URLs cannot replace the sender's OAuth issuer. Changed origins require the existing reconnection decision; a descriptor alone cannot migrate a token or accepted identity.

## Create a content-free source permission

The client initiates only for a locally selected recipient under enabled automatic-setup policy. Do not probe an address book or trigger the flow from opening mail, HTML or a URL. The source provider derives the account/family/incarnation from its authenticated session, checks the exact sender mailbox against that account, and checks the linked device's current send/receive authority.

The source permission is signed by that device after checking the exact preparation. It binds the intended recipient mailbox/service, conversation identifier, random request nonce and original signed sender capability advertisement. Its fixed deadline is at most600 seconds, also bounded by link/family/device/assertion validity. Retries never refresh it. The source provider activates it only after the approval and its account checks succeed.

A source permission is an invitation to perform this exact setup, not a bearer queue token or authority to send content. Copying it can replay only the same admitted request. Reading the result requires possession of the initiating device key. The source provider exposes a live inspection operation to validate the original permission, not a public mailbox lookup.

## Admit a scoped request

The destination validates the source domain delegation, exact live permission bytes, signature, current source-account authorization and target mailbox/service before accepting a request identity. It applies finite issuer/account/peer/destination/work budgets and its source-admission policy. HTTPS proves control of an origin, not an honest operator or costly account creation.

For every valid source permission, `POST /exchanges` returns the same202 shape with an opaque exchange handle and `pending`, whether the target mailbox exists, is disabled, has no opted-in devices or has no usable publication. Mailbox lookup and eligible recipient work are private asynchronous state. Invalid source authority can fail without consulting the mailbox. There is no public recipient-capability, existence, last-seen or presence endpoint.

Ordinary SMTP rejection and verification behavior can already disclose mailbox existence; [SMTP security guidance](https://www.rfc-editor.org/rfc/rfc5321.html#section-7.3) recognizes this disclosure problem. Automatic setup does not promise to conceal every fact already observable through email. Its restricted requests and uniform pending result avoid adding an unrestricted directory or detailed status interface. Successful opt-in disclosure necessarily reveals usable capability to that authorized requester. Uniform pending failures do not make enumeration by authenticated permitted senders impossible. Recipient opt-in, source-account/peer blocks, admission policy and finite budgets limit this privacy cost; do not describe them as zero-leakage or universal anti-harassment. A fresh device signature shows that a key answered, not that a person was online or read the request.

The provider places eligible work in a separate private control inbox, not an ordinary email message. Legacy clients need not discard, hide or automatically reply to anything. Account-level opt-in and each receiving device's response policy are both required. Incoming request fields cannot enable either policy or enroll a device.

## Answer automatically or use published material

An enabled recipient device validates the exact source scope, source evidence, its own account/mailbox binding and local response policy. A conflicted known identity is not repinned. It prepares one current assertion8 and usable MLS admission package, signs one response bound to the original request digest/nonce, and durably stores the response/package allocation before upload. Exact retries return those original bytes; they do not generate another package or exchange.

An offline device may instead have explicitly published a signed automatic-first-contact record. It names its exact mailbox/service, current endpoint and original advertisement. Both account opt-in and that device publication policy must permit disclosure to the validated source. The provider cannot manufacture a fresh device signature from this publication. Label it `published`, not `challenge-response`, and preserve its original validity.

The provider atomically reserves a published package for one exchange before first disclosure. Exact exchange retries return the same allocation. Once disclosed, a package is never recycled into another exchange, even after cancellation. Provider allocation does not replace MLS validation and recipient single-use enforcement. Publication/KeyPackage secrets retain their own lifecycle and original deadline; the ten-minute request cannot extend or arbitrarily shorten the separately applicable admission lifetime. In-flight admission and retirement follow their owning contracts.

No response causes another response. An exchange cannot become a subscription, automatically enroll all mailbox devices, send a receipt, release history or call an arbitrary callback. A source permission does not authorize a new reply audience.

## Finish private routing in the same handshake

A recipient response or publication includes `relayDomain`: empty when no recipient-masking service is offered, otherwise the domain of that device's already connected receiving-relay account. This is a signed routing proposal, not ownership proof, an OAuth issuer to install or permission to contact an arbitrary URL. The sender validates that domain's relay descriptor under network/selection rules and later requires actual recipient route approval and live activation. The recipient device accepts follow-up only for its own configured relay account.

The initial request cannot name the recipient's principal before learning it. Therefore private routing has an explicit second stage, before human content: the sender validates returned setup, obtains its own [relay source permission](relay-routes.md) for that selected principal/conversation and sends a signed route request through this same bootstrap exchange. The recipient device automatically prepares/approves the alias with its connected relay under its enabled policy, then returns the route invitation. The sender independently validates the invitation and proves route-key possession to inspect its activation.

No source permission is fabricated with a guessed recipient principal, and no alias is silently installed merely because it was returned. If masking is required, content waits for this stage. If remembered policy permits content encryption with public addresses, the client can use that permitted combination with an accurate indicator. A later route upgrade does not recall the earlier exposure.

::: {.details summary="Exact HTTP records and state transitions"}

### Common encoding and authorization

Use the [relay common wire restrictions](relay-routes.md#exact-records-signatures-and-http-behavior): strict string-valued UTF-8 JSON, original-byte retention, bounds, TLS1.3, no redirects/0-RTT/ambient cookies, no-store, canonical same-origin paths and finite deployment budgets. Management bodies are at most4194304 octets, each signed payload262144 and depth32; advertisement/identity decoding independently obeys its tighter bounds. A request exceeding a bound cannot partially create authority. Times are canonical uint64 strings; ObjectIds nonzero32hex; source/exchange/nonce/digests64hex; endpoint references have the existing exact grammar. Mailboxes use the selected initial [address spelling](private-address-presentation.md#mailbox-spelling-and-compatibility).

A proof is exactly `{payload,signature}`, canonical padded base64 original payload and128 lowercase hexadecimal Ed25519 signature. Signature domain is `email2/bootstrap/<kind>/v0`, NUL, u32 big-endian payload length, then original bytes. Kinds are `source`, `inspect`, `cancel`, `response`, `publication`, `route-request`, `route-response`. Cross-kind signatures are invalid. Advertisement is canonical base64 of the original complete signed assertion8 wrapper, preserving the independent assertion payload/signature/identity bytes; it is not a feature boolean.

### Source operations

Under managementPrefix, `POST /sources/preparations` requires own request scope, an active linked device and authoritative mailbox membership. Body is exactly `{version,purpose,request,link,senderMailbox,sender,targetMailbox,targetService,conversation,advertisement,nonce,notBefore,notAfter}`; purpose `bootstrap-source-request`. The service independently validates the full sender advertisement, mailbox/endpoint agreement, current state/binding/roles, time and selected target-domain delegation.

Its200 response is the prepared payload:

```
{version,purpose,preparation,request,source,issuer,delegation,accountSource,
 senderMailbox,sender,targetMailbox,targetService,conversation,advertisement,
 nonce,notBefore,notAfter}
```

Purpose is `bootstrap-source`; preparation/request ObjectIds; source a service-generated random64hex permission identifier; issuer/delegation are this source service and exact descriptor digest. AccountSource is the same stable opaque source-account abuse handle at this target service used across relinks/resets; it never reveals the personal account identifier. Remaining intent fields are unchanged. Offer the exact bounded interval before approval. `PUT /sources/preparations/{preparation}` body `{proof}` signs this exact preparation. Recheck current account/family/link, advertisement, descriptor, scope and interval under one transaction before activating. Return201 on creation or200 identical retry with exactly `{proof}`. Changed authenticated input under the account/family/request namespace is409; invalid proofs cannot reserve a conflict.

`POST <sourcePrefix><source>/inspect` body `{proof}` presents that original source permission. It returns200 `{proof}` only while the original permission, account/family/link and exact device authority remain active, with identical original payload/signature. It introduces no new mailbox information to a holder of that original proof. There is no credential-free GET/listing by mailbox or permission ID. A copy authorizes no new target or scope. Destination services perform a fresh selected-origin inspection, not cached liveness or a message-supplied arbitrary URL.

Own-account `DELETE /sources/{source}` under request scope withdraws the permission; unknown own IDs return204. Disconnect, reset, expiry, descriptor invalidation or known loss of required authority stops new use. It does not recall already disclosed public material. Source inspection never changes the original deadline.

### Public exchange and source possession

Under exchangePrefix, `POST /exchanges` body is exactly `{source}` containing the signed source wrapper. After complete source validation, create or find the immutable exchange. Its handle is SHA256 of ASCII `email2/bootstrap/exchange/v0`, NUL, u32 big-endian byte length of issuer, UTF-8 issuer, then the32 decoded source-ID bytes. Response is always202 with exactly `{exchange,state}`, state `pending`. It reveals no private recipient queue status. Same source ID with different authenticated original bytes is409 only after verifying live source authority; unauthenticated traffic cannot poison that identity.

`POST /exchanges/{exchange}/inspect` body `{proof}` uses the initiating device key. Exact payload is `{version,purpose,issuer,exchange,sourceDigest,nonce,notBefore,notAfter}`, purpose `bootstrap-inspect`; issuer is this destination origin, sourceDigest the original source payload hash, nonce a new random64hex and interval within the original source lifetime. Verify current source liveness and key possession before returning200:

```
{exchange,sourceDigest,state,responses,publications,routes}
```

State is `pending` with all arrays empty, or `ready` with one or more eligible signed results. Responses contain original signed response wrappers; publications original signed publication wrappers; routes contain signed route-response wrappers below. Setup lists are sorted by principal/device/publication-or-response ID, with no duplicate device setup; choose a current fresh response over a publication for that device. Routes are sorted by recipient principal/device/route-request ID, with no duplicate result for a device/request. Unsupported/unavailable recipients remain pending, not a distinct failure. Ready means material is available for validation, not message admission or delivery. Never disclose a device/account list outside this authorized result.

A valid signed `bootstrap-cancel` payload has the same fields as inspect but purpose `bootstrap-cancel`, signed under the cancel domain. `POST /exchanges/{exchange}/cancel` body `{proof}` returns204 after terminal cancellation of future disclosure. It cannot revoke already exposed packages or erase history. Local cancellation immediately gates content release even if this request is lost. Source permission withdrawal and immutable expiry independently stop new work. Cancelled/expired/unavailable exchanges have no ready result for new inspection; valid inspection of a cancelled exchange remains pending until the source interval ends. Invalid/expired source or possession proof receives generic404 without account lookup.

### Recipient control inbox and fresh response

Under managementPrefix, `GET /inbox?cursor=<opaque>` requires own respond scope and the exact linked recipient device. The response is exactly `{items,next}`; items are `{exchange,source,routeRequests}` with the original signed source wrapper and an array of eligible signed route requests/source permissions below; the array is empty before the routing stage. Next is an opaque bounded cursor or empty. Return only opted-in, current, eligible work for that account/device. Cursor progress is local service state, not evidence that a person saw anything. Polling is bounded and never starts from ordinary email rendering.

`PUT /inbox/{exchange}/responses/{device-suffix}` body `{proof}` signs exactly:

```
{version,purpose,response,issuer,exchange,sourceDigest,nonce,mailbox,
 device,advertisement,relayDomain,notBefore,notAfter}
```

Purpose is `bootstrap-response`; response ObjectId; device the linked endpoint; mailbox exactly the requested owned target mailbox; nonce exactly the original source nonce. Issuer/exchange/sourceDigest bind the source preparation and destination. RelayDomain is empty or the canonical domain of that device's connected receiving relay, never a URL or source-supplied callback. The interval fits source request, target device and original advertisement/package. Validate full advertisement/identity/package correspondence, current receive authority, own account policy and fresh source permission before storing. Same exchange/device exact response is200 retry; a new valid response is201; changed authenticated content is409. Return exactly `{responseDigest}`. Wrong-role or foreign-account credentials cannot read or write these slots. Persist acceptance and result atomically; an invalid signature cannot block the legitimate response.

### Publication and offline allocation

`PUT /publications/{publication}` requires own respond scope and device signature over exactly `{version,purpose,publication,issuer,mailbox,device,advertisement,relayDomain,scope,notBefore,notAfter}`. Purpose is `bootstrap-publication`; scope exactly `automatic-first-contact`; issuer/mailbox/device match that account and linked endpoint. Validate the complete original assertion/package and both account/device publication policy. The interval cannot exceed device/assertion/package validity or the selected seven-day admission horizon. Publication identity is scoped to the owning account incarnation/link namespace and linked device. Creation returns201, identical retry200, each exactly `{publicationDigest}`. Changed authenticated bytes under that ID conflict; validity renewal needs a new ID. Validate signatures before reserving a conflict identity. An exact retry after withdrawal reports the retained result without reactivating it. `DELETE /publications/{publication}` returns204 after withdrawal from future allocation and disclosure, including further inspection of an allocated record. Another account cannot withdraw it. No already disclosed material is recalled, and an already exposed package remains reserved.

Allocate only after current source authority, initiating-key possession, recipient account/device policy and source blocking have been checked. Public request admission and private dispatch do not consume the pool. For each eligible device without a current fresh response, select the first eligible publication in ascending ASCII publication-ID order. Atomically bind that original publication to `(exchange, device)` and reserve its package before returning the result. An invalid, expired, withdrawn or already allocated package is not eligible for a new allocation. A pool can contain multiple distinct packages, each in its own signed publication.

An exchange retry retains its original allocation even if another publication becomes available, sorts earlier or has a longer lifetime. Withdrawal, expiry or a device/account/relay change suppresses further disclosure of that allocation; it does not automatically select another pool entry. A newly authorized fresh response or a new bounded exchange is needed for new material. A fresh response takes precedence over a publication for that device in inspection, but does not release any earlier allocation. Current material is returned under its original source classification: a publication never becomes a freshly answered challenge.

Fresh responses and publications share one package-allocation index, so republishing identical package bytes under a new assertion or publication ID cannot allocate them to another exchange. Commit the selected original bytes, allocation and package reservation together before constructing a successful outgoing response. A failed precommit transaction returns no setup and reserves nothing; an uncertain or lost postcommit response retries the committed allocation. Once committed for disclosure, retain the reservation even on cancellation, withdrawal or loss of the HTTP result. Retain allocation/replay protection through the package's applicable lifetime; a restore cannot roll it back. Exhaustion holds rather than evicting an exposed allocation or fabricating a fresh package.

This index prevents reuse within that provider's allocation service. It cannot guarantee exclusive distribution if the same package was also published in ordinary email or at another service. Clients should generate dedicated packages for this pool. The recipient's independent cryptographic validation and atomic MLS single-use admission remain mandatory, and a failed competing admission waits for new eligible material. Providers never acquire a package's private admission key merely by storing its signed public publication.

### Optional route stage after setup

`POST /exchanges/{exchange}/routes/{device-suffix}` body is exactly `{request,sourcePermission}`. Request is a source-device proof under `route-request` over exactly:

```
{version,purpose,request,issuer,exchange,sourceDigest,nonce,recipient,
 relayDomain,sourceDomain,sourceService,sourcePermission,permissionDigest,notBefore,notAfter}
```

Purpose is `bootstrap-route-request`; request ObjectId; issuer this bootstrap destination; recipient the exact endpoint from an eligible disclosed response/publication; nonce the original source nonce. RelayDomain matches that device's signed setup proposal. SourceDomain/sourceService/sourcePermission/permissionDigest identify the independently activated relay source permission; validate that source domain's own descriptor rather than inferring its domain from a personal SMTP From; the body sourcePermission is its complete original signed wrapper. Require the bootstrap initiator key, live source authority and current interval inside the bootstrap request. Decode/validate the relay permission's exact sender, recipient principal, conversation and selected relay origin before privately queuing. The target must match the descriptor of the signed relayDomain; do not fetch a source-supplied arbitrary callback. Successful admission returns202 exactly `{exchange,request,state}`, state `pending`, regardless of current relay availability.

The recipient's private inbox includes `{request,sourcePermission}` for this exact device. Its local account policy must independently permit automatic route creation and the proposed relay must equal its already connected account. It validates fresh original relay source permission and performs the route preparation/approval through its own relay management authority. It does not forward its OAuth token to the bootstrap service, source or another relay.

`PUT /inbox/{exchange}/routes/{request}` body `{proof}` is signed by that recipient device under `route-response` over exactly:

```
{version,purpose,response,issuer,exchange,sourceDigest,requestDigest,nonce,
 device,relayDomain,invitation,notBefore,notAfter}
```

Purpose is `bootstrap-route-response`; response ObjectId; requestDigest SHA256 of original route-request payload; invitation canonical base64 original `{approval,recipientIdentity}` relay invitation. The response interval fits the bootstrap attempt and current device authority. Its route invitation retains its own independently approved lifetime, which may outlive the bootstrap attempt; neither signature refreshes the other. Recheck exact account/device, original source/route request and all correlations before storing. Return201 or200 identical retry with exactly `{responseDigest}`. Invalid signatures cannot reserve conflicts, and different authenticated bytes under an exchange/device/request conflict. An unavailable or invalid relay route remains a held stage, never a guessed alias.

Inspect returns eligible original route-response wrappers in routes. The sender validates the full invitation under relay rules and performs live route-key inspection itself; neither a ready bootstrap response nor an octet string proves relay activation. Current account/device opt-out/revocation, cancellation and source expiry suppress new route disclosure as for setup. Exact retries preserve the original request, route key, permission and route approval. A new device/provider/scope needs fresh authorization, not mutation of these records.

### Own-account source blocking

`POST /blocks` under own respond scope has exactly `{version,purpose,request,exchange}`, purpose `bootstrap-block-source`. Require this account's retained eligible exchange; derive the source issuer/accountSource and known sender principal from its original authenticated record, never caller-supplied identities. Return200 exactly `{block}`, a retained nonzero ObjectId; identical request retries return that identifier. Block future disclosure and private dispatch for that account/source handle or known principal, including new permission IDs and a changed provider with the same principal. This operation requires account management authority, not possession of the blocked peer's key.

`DELETE /blocks/{block}` removes only that own-account block under a deliberate decision; other active blocks remain effective. Public POST still returns uniform pending for a valid blocked source. Blocking stops further setup disclosure, not already disclosed keys, ordinary email or previously delivered content. Relay delivery and mailbox filtering retain their own enforcement boundaries. An account can also withdraw its general automatic-setup permission without deleting history.

### Failure, retention and budgets

Apply the provider HTTP error vocabulary and bearer challenges. Public invalid source/possession/purpose/expired authority uses generic404; transient selected-service failure503; bounded exhaustion429 with positive Retry-After; malformed/oversized representation400/413/415. Error bodies are exactly `{error}` and do not echo records. Do not contact arbitrary URLs, send automatic email, refresh a timeout, replace a pin or authorize fallback because an operation failed.

A fresh source inspection establishes a live service observation at that check, not instantaneous cross-provider revocation. Perform bounded network work outside long-lived local write locks, then recheck local account/device/policy and original observation/deadline dependencies at commitment. Local cancellation/withdrawal serializes with local disclosure; it cannot recall material already observed remotely.

Private journals retain original permissions, identity evidence, exact results and terminal/replay state for their finite supported retry horizon. They exclude human draft content and live bearer tokens. Expiry/cancellation stops new disclosure and retires attempt-bound secrets under [setup retirement](setup-secret-retirement.md), preserving independent admission-package lifecycle. Account/peer blocks and per-source/destination/issuer quotas apply before work and at disclosure; reset cannot clear an account's existing abuse handle. A dishonest operator or entirely new account/identity can still evade identity-based limits; no universal real-person control is claimed.

:::

## Validate the result, then establish encryption

The sender rechecks the original target domain/service and source permission, signed result purpose/digest/nonce/mailbox, device identity/current authority, original assertion8, complete selected application/module agreement, package cryptography/binding/lifetime/single-use scope and required freshness. The [freshness contract](freshness.md) supplies the local operation/policy/creation-time binding for these checks. A published record cannot satisfy a policy requiring a fresh challenge response. Source/target account-provider truth never substitutes for these checks.

Record the provider observation as a distinct `provider-bootstrap` observation: retain exact descriptors, source proof, authorized result bytes, original assertion and transport provenance. The [association eligibility procedure](mailbox-association.md) replaces the ordinary sole-outer-From match only for this explicit observation type with exact requested-mailbox/authorized-provider-result correspondence. Never manufacture an ordinary email From match or reuse an incoming `verified:true` field. Apply the same ambiguity, policy, continuity, generation and serialized release rules. A sole candidate under allow-unverified can be selected without a human email; strict or conflicting policy remains held.

After complete setup validation, perform the owning MLS initial admission and any requested relay-route approval. No human subject/content enters control traffic. Release the first contribution only after all current identity, package, context, recipient, policy and required secret-retirement gates pass. Setting up encryption, material returned, admitted, submitted, accepted and read remain different states.

## Acceptance obligations

The full positive case starts with no recipient association or pair grant, authenticates a real source account, runs the private recipient control inbox without a human reply, validates actual signed assertion/package evidence, selects a common application, establishes MLS and sends the first human message through the real mail path. Repeat with offline publication allocation, the optional private-route follow-up stage and no available material. Inspect all requests, queues, drafts and mailboxes for body/subject/attachment or content-hash leakage.

Negative cases include mailbox spoofing, copied source permission without possession, wrong target/service/nonce, revoked/changed source or recipient, new-identity conflict, invalid package/signature, stale publication called fresh, account enumeration/status differences, invalid-proof collision poisoning, competing package allocation, terminal cancellation, expiry/restart/clock uncertainty, offline allocation through concurrent service connections, fresh/publication package collisions, withdrawal without reallocation, lost replies and crashes at each journal boundary. No ready response alone counts as complete acceptance. Production service, complete assertion8/admission, independent-client and independent security evidence remain unproven until actually exercised.
