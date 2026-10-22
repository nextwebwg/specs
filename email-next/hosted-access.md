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

> [!note] Experimental protocol and evidence
> The [public hosting profile](#connect-a-hosting-account) defines account authorization, owner-bound management and reply discovery. Existing configured message/question experiments exercise a historical subset, not that complete public implementation. Account-bound access and an independently authorized cryptographic endpoint are separate models in [delivery policy](delivery-policy.md#hosted-access-models).

## Connect a hosting account

The sender connects a chosen hosting service once, through the system browser. The client links that service account to the sender's current Email/2 identity before uploading a contribution. Opening an email cannot choose a host, start sign-in or authorize an upload. The person receiving a secret link still needs no hosting account.

Hosting permission and a link holder's access are different. Disconnecting the sender's management session stops new management through that session; it does not erase content or revoke links already sent. The client can list and revoke those grants through a newly authorized hosting account. This is provider-hosted data, not recovery of an end-to-end encryption identity.

:::: {.details summary="Public host authorization, owner-bound management and reply discovery"}

### Selected public profile and registration

`hosted-management-v1` selects the public management/acquisition path for the bearer-access model. The configured `/v0` management experiment remains its historical profile; its preprovisioned token is not public account acquisition. This profile retains the existing bearer holder, deliberate entry/retrieval and free-text reply contracts. Account-bound recipient access and a separately authorized cryptographic endpoint remain unsupported by this profile and cannot be presented as equivalent bearer features.

Use the native authorization mechanics in [service-account authorization](service-authorization.md#exact-registration): trusted registration, external browser, literal loopback/ephemeral port, random state and S256 PKCE, exact callback state/issuer, code binding/consumption, same-origin direct TLS token exchange, protected token storage, rotating refresh/reuse detection, uncertain response handling and no public-client secret. These build on [RFC8252](https://www.rfc-editor.org/rfc/rfc8252.html) and the [OAuth security BCP](https://www.rfc-editor.org/rfc/rfc9700.html); this selection is not complete OAuth-server certification. The exact hosting-specific differences below replace the service-action names/scopes; do not reinterpret an existing action token as a hosting token.

A host registration has exactly `{version,purpose,registration,generation,service,issuer,clientId,authorization,token,linkChallenge,linkComplete,unlink,management,redirectPath,scopes}`. Version is `"0"`; purpose `"hosted-authorization-registration"`; registration/generation and client/origin/endpoint grammars are those of the native service registration. Issuer equals service. The five authorization/token/link/unlink endpoints are distinct canonical HTTPS endpoints at that origin. Management is exactly the service origin followed by `/v1/`. RedirectPath is exactly `/mail/oauth/callback`. Scopes is exactly this ASCII-sorted array:

```json
["mail.hosted.create","mail.hosted.link","mail.hosted.read","mail.hosted.revoke"]
```

These are draft operator scope strings, not registered IANA values. Retain the original registration bytes and SHA256 digest; a received URL, email, bearer entry page or service-action descriptor cannot install or alter them. Authorization requests and successful token responses use that exact scope set under the existing native-profile order/duplicate rules. Tokens are opaque and separately bound to this issuer, resource audience, registration/client, internal authenticated account/incarnation, effective scopes, grant family and validity. Registration change invalidates its old token authority and pending authorization/link attempts, without deleting old hosting receipts or making an uncertain upload new. Account authentication/consent is the host's own trusted boundary, not a client-supplied account identifier, email string or OAuth-subject-to-principal conversion.

### Link current sending authority

The link request has exactly `{version,purpose,registrationDigest,principal,device,state,binding}`, with version `"0"` and purpose `"hosted-account-link-request"`. Its token needs `mail.hosted.link`. The account and grant family come only from authenticated service state. Identity fields use the existing identifier/digest grammar and current full identity lifecycle.

The challenge has exactly `{version,purpose,challenge,nonce,issuer,service,clientId,registrationDigest,grantBinding,ownerBinding,principal,device,state,binding,notBefore,notAfter}`. Version is `"0"`, purpose `"hosted-account-link"`; challenge is a fresh ObjectId; nonce a fresh 32-octet lowercase-hex value. GrantBinding is the opaque 32-octet hex family binding. OwnerBinding is a fresh nonzero 32-octet hex opaque owner handle proposed or reused by the service for exactly this internal account-incarnation/principal pair. It is not an account identifier, credential or proof by itself. It remains stable across permitted reconnects for that pair, but is different for another account or incarnation, even for the same principal. Allocate or reuse this proposed handle under a unique account-incarnation/principal constraint before issuing a challenge, so concurrent attempts cannot propose competing handles. An abandoned proposal is not an active link or a visible owner-index entry. Link completion rechecks that retained association inside its transaction.

The service retains original challenge bytes, proposed owner handle, authenticated account/family/client and validity before returning them over direct authenticated TLS. A challenge allocates no live principal mapping. Its interval fits the current authorized send binding and active account/family policy; clocks/uncertainty and explicit finite deployment attempt limits retain the native profile's rules. The client compares every correlation against its original registration, selected own principal/device, current state/binding and account-link intent before signing.

Completion is exactly `{payload,signature,identity}` with canonical padded base64 original challenge bytes, 128 lowercase-hex Ed25519 signature and versioned identity proof bundle. Sign ASCII `email2/hosted-account-link/v0`, NUL, U32 big-endian payload length and original bytes. The service resolves its own retained challenge and active authenticated family/account, verifies current identity/head/binding/send power, and checks the entire credible interval and actual signature before mutation. Incoming proof cannot replace an established pin or manufacture mailbox ownership. First accepted key continuity may be unverified; normal independent-verification policy remains separate.

Commit challenge consumption, the principal/owner association, family/device link, generation allocation and receipt atomically. Competing completions serialize against the retained family mapping; generations never reset on refresh within that family. The receipt is exactly `{version,purpose,challenge,requestDigest,service,principal,ownerBinding,link,generation,outcome}`, with `"0"`, `"hosted-account-link-result"`, SHA256 of original challenge bytes, a fresh ObjectId link, positive canonical uint64 generation and outcome `"linked"`. It is direct authenticated service evidence, not a transferable signature or a bearer credential. Store it with the original proof before reporting connection ready, and check that its link/generation still names the current active mapping. A retained historical receipt does not override a later refresh or unlink.

One family links one selected principal; it cannot silently switch to another. An appropriately authorized fresh challenge can refresh that principal's device/binding, issuing a fresh link and incremented generation without changing its stable owner handle. An unchanged-binding accepted ancestor can retain the prior link under the existing continuity rules; state1 repair or changed binding requires fresh linking. Same-principal renewal need not make contacts repeat independent verification. Known conflict, revocation or missing authority holds new creation. A currently authorized exact payload/signature retry returns its retained link receipt even after the original challenge expired; changed proof bytes cannot use that shortcut or poison the mapping.

Other families may connect separately selected principals in the same hosting account. Their owner handles and stored grants remain distinct. Existing grants never change their original principal because another family connected. Logout/unlink cannot repin an Email/2 identity. `DELETE` to the registered unlink endpoint has no body, requires current link scope and disables that authenticated family/link/access/refresh authority; it returns 204 after commit. A lost result leaves the client disconnected locally rather than retrying content through the uncertain family. A later account sign-in is a new family, not resurrection of old tokens.

### Different operations need different authority

| Operation | Required effective scope and account/device authority |
| --- | --- |
| Create a hosted contribution | `mail.hosted.create`, a live linked principal/device with current send authority, exact owner handle/link/generation and independently approved disclosure plan |
| Inspect retained management operations, owner/grant inventories or holder replies | `mail.hosted.read` and current service-account authority over that retained owner namespace; it grants no current Email/2 sending power |
| Revoke an existing hosted grant | `mail.hosted.revoke` and current service-account authority over that grant's original owner namespace |
| Establish or refresh the principal link | `mail.hosted.link`, the exact signed challenge and current Email/2 send authority |
| Retrieve/reply as a link holder | The separate grant bearer under its original rules; no hosting management scope or identity mapping |

A service account can manage its already hosted records after an original device is lost or a principal is retired, using read/revoke scopes without forging that principal's current signature. The host already processes this plaintext. This narrow management right does not recover archives, enroll an endpoint, create as the old principal, change original attribution or emit a protected Email/2 message. If read/revoke authority itself is unavailable, keep the management operation held. Account deletion/reassignment rotates the incarnation, disables its tokens/owner handles and stops its grants; old handles/credentials are not reassigned or reopened as new objects. Already downloaded copies are not erased.

### Owner-bound creation and receipts

Public management paths are rooted at `/v1/owners/{ownerBinding}/`. The server derives the internal account from current authentication and looks up the owner handle there; the path/body cannot select another account. Grant identifiers remain globally unique at the host so the existing `/g/{grant}` entry and holder endpoints are unambiguous. An unknown/foreign owner or grant returns 404 without exposing the other account. Invalid token is 401 and insufficient effective scope 403. Preserve the existing framing/body/JSON/no-store/no-redirect/error boundaries and transactional current-authority checks.

| Operation | Method and suffix under the owner root |
| --- | --- |
| Create | POST `grants` |
| Inspect management operation | GET `operations/{operation}` |
| Revoke | POST `grants/{grant}/revoke` |
| Read/export one retained holder reply | GET `grants/{grant}/reply-records/{operation}` or `grants/{grant}/reply-exports/{operation}` |
| Enumerate grants or replies | GET `grants` or `grants/{grant}/reply-events` under the feed contract below |

Create uses version `"2"`, the complete create-v1 members including replyTextLimit, and exactly three additional members: `ownerBinding`, `link`, `generation`. They match the path and original link receipt. Contribution principal equals the linked principal. The local author freezes exact content, service, owner/link/generation, grant credential, expiry, actual notification recipient, reply destination and source-disclosure/membership policy before any upload; the host is a content recipient even if later mail is held. A token is not that local disclosure decision.

Recipient and replyDestination in this public profile are fresh or retained owner-scoped opaque ObjectId tags selected in that local plan. The host stores them unchanged as bookkeeping, never interprets them as an email address, URL or permission to contact someone. The client independently maps them to its notification and observation route. There is no preprovisioned host-side message-content record or address-book requirement: current account/link/create authorization permits storing this exact owner's planned request. It permits neither another owner's record nor an arbitrary callback.

The first public profile supports the existing exact text-message and complete question projections, with their original replyTextLimit/size rules. Other content/resource or account-bound-access models need their actual selected contract; do not truncate rich content or claim unsupported resources were hosted. Existing holder retrieval/reply objects and `/v0/grants/{grant}/...` holder paths retain their original meaning; a public-management grant is still opened through the existing deliberate bearer entry page, without account sign-in. The host checks the new grant's immutable metadata at those holder endpoints.

A public management receipt is the existing management receipt with version `"1"` and added ownerBinding. A public historical reply export is the existing export with version `"1"` and added ownerBinding; its underlying holder receipt/request bytes remain original. Validate service/owner/ownerBinding/grant/operation/purpose/requestDigest against the frozen request/path before committing evidence. A receipt never proves current remote access or human reading.

Namespace immutable operation identities by the service's retained account/owner handle and operation ID. Exact currently authorized retries return original results, and changed authenticated bytes conflict. A create with an old link/generation cannot create again after relinking or repair; use read-authorized operation lookup to reconcile a previously committed/uncertain result rather than treating 403 as proof of no upload. A renewed token cannot retarget an old owner handle, change a grant credential or rewrite a submitted plan. Reconnection to another account cannot turn the same principal spelling into permission to reuse its grants.

### Find replies without a callback

Read-scoped native management can enumerate existing owners, grants and holder replies. Receiving or opening a bearer email does not enable this sender-side account activity. The connected account's explicit polling policy is finite and independent of any read/presence claim. No new callback destination is installed by content or by a holder reply.

The owner collection is `GET /v1/owners`; grant and reply collections use the owner-root paths above. Requests have either no paging parameters, one `cursor`, or one `since`; duplicates, other parameters, or both cursor and since are invalid. These are bounded opaque printable ASCII service tokens, not URLs or credentials. Query values use RFC3986 percent encoding and are decoded exactly once; literal plus is not converted to space. An empty cursor/since, malformed escape, non-ASCII byte, or whitespace/control character is invalid. Server-held/MAC-protected state binds each token to exact account incarnation, client/registration, route, owner handle/grant when applicable and retained snapshot/change position. Current read authorization is rechecked on every page; a cursor does not grant it.

Responses have exactly `{version,purpose,service,items,next,checkpoint}`, plus ownerBinding for grant/reply collections and grant for reply collections. Version is `"1"`; purposes are `hosted-owner-index`, `hosted-grant-index` and `hosted-reply-events`. Owner items are exact `{ownerBinding,principal}`. Grant items are exact `{grant,contribution,expiry,state}`, state `"created"` or `"revoked"` as retained management evidence, not a current-access assurance. Reply items are the complete original holder receipts. They disclose no bearer, content, mailbox or callback address. Obtain actual reply bytes separately through the authenticated export and validate its original digest, scope and provenance before deriving an observer contribution. A holder's text never becomes an authenticated structured answer merely through enumeration.

Each enumeration begins a bounded consistent snapshot, including an upper change position. Page original items in retained service order, not participant/time authority order. An initial snapshot includes each visible owner/grant once and each retained holder reply once. Change snapshots include changed owner/grant records and newly committed immutable reply receipts through their fixed upper position; repeated records across snapshots are permitted and use the same exact identities. Revoke changes a grant record, not its immutable contribution or expiry. Account deletion terminates access rather than returning a successful empty feed. Next is empty when done or the opaque next-page cursor; checkpoint is empty until the final page, then the opaque completed change position. A later since query starts a new snapshot of retained changes after that position; it can be empty and still produce a checkpoint. It does not extend the previous snapshot or claim no withheld data. Complete all pages before advancing the local checkpoint. A new owner list or expired bearer does not imply an old reply never existed.

Every response has the existing 1 MiB encoded JSON bound and common depth/strict-scalar rules. The service chooses finite page processing/retention budgets without truncating an item; if a response cannot be produced within them, return an explicit resource failure. Next and checkpoint are strings; the empty string is the sole absent/end sentinel. Items is an array; collection identifiers and each nested reference use the existing ObjectId/principal contracts. Nonempty tokens contain only ASCII bytes 0x21–0x7e and have length at most 2048 octets; it is an implementation-independent wire bound, not a user storage quota. A malformed token is 400, expired/unavailable continuation 410, and foreign scope 404 after authentication. On 410 restart a full enumeration and deduplicate by the exact owner/grant/operation/request identities; never infer deleted content or replay a holder effect. A lost page retries the same cursor and original page bytes while its snapshot is retained. Registration/account changes require reauthorization and new appropriately scoped enumeration, not reuse of another account's cursor.

Persist imported receipts/exports with original service/account-owner provenance and update the completed local cursor atomically with the records it covers. Duplicates create no second observation or service effect. A newer permitted grant state may record revocation; it cannot change immutable grant fields. Inconsistent immutable receipts, owner mappings or grant fields retain conflict evidence. Native delivery of a holder observation into a protected conversation remains a separate current authorized outbox/admission operation. Its actual selected audience and replyDestination are local policy, not a mailbox supplied by the host. Feed polling and entry-page loading send no read receipt and make no remote identity claim.

### Worked wire examples and acceptance boundaries

The [public hosting examples](evidence/hosted-public-examples.json) include an exact create-v2 request and a two-page reply feed. Their repeated hexadecimal identifiers are test placeholders, not meaningful names, keys or production credentials. The local `hosted_public_wire.py` decoder checks the create schema, expected owner/principal binding and feed shape/correlation. It preserves original request bytes for digest comparison. Decoding is not authentication, current identity validation, a live account link, a retained snapshot, or authorization to upload/import.

In addition to the full implementation cases below, exercise these transitions:

| Starting state and event | Required result |
| --- | --- |
| Two challenges for the same account-incarnation/principal | One retained proposed owner handle; each completion still has its own family, challenge and current authority |
| Same principal connected to another hosting account | Different owner handle; no access to the first account's grants or cursors |
| Create committed, response lost, then device link replaced | New creation through stale generation is held; read-scoped lookup can recover the original receipt without a second grant |
| Original device lost or identity retired, hosting account reauthorized | Existing grants remain readable/revocable under that account; no old-principal creation or protected sending power is restored |
| First reply page imported, next page unavailable | Keep the old completed checkpoint and deduplicate a retry; no partial snapshot becomes a completed checkpoint |
| Cursor expired | Explicit 410, full rescan and exact-identity deduplication; no repeated conversation observation |
| Message supplies a different host, callback or action token | No registration, account switch, upload or authorization expansion |

### Availability, revocation and evidence

Access/refresh expiry, active family, link/generation, current local identity, hosting policy and every immutable request remain separate gates. Same-origin HTTPS authorization does not supply per-request sender constraint: a stolen live management bearer can exercise its allowed scopes until revoked. Read/revoke account recovery is not end-to-end content confidentiality. A deployment must state the trust in its hosting operator, authorization code and browser entry scripts; the existing direct-navigation/fragment/scanner isolation rules still apply. OAuth browser redirects to the selected callback are not permission to redirect a secret bearer-entry URL.

Revoking a management session or repairing an identity holds new creation under that session/link; it does not automatically revoke every previously issued bearer or erase content. Enumerate/manage those retained grants under current account authority and report individual revocation outcomes. Do not claim all links disabled when a page or service is unavailable. Original grant expiry is not extended by refresh, reply polling, relink, import or another grant's creation. Source uncertainty, literal holder attribution and no-implicit-fallback rules remain unchanged.

Conformance requires actual native account acquisition/linking with this registration/scopes/domain, wrong-issuer/client/account/owner isolation, code/refresh replay and uncertainty, same-principal different-account attempts, read/revoke after device loss without old-principal sending, state1 repair and stale link/generation, public exact creation/receipts, complete paged reply discovery/export, cursor replay/expiry/account changes, atomic local import and current protected observation release. Test bearer/management/service-action token separation and entry/scanner/no-receipt behavior. Existing configured-host and service-button OAuth tests cover components and analogous mechanisms; they do not implement this public profile or prove deployed browser/login trust, secure platform custody, independent interoperability or security review.

::::

## Grant and management authority

Each recipient receives a separate grant. A grant binds one immutable contribution, its permitted hosted text, one configured recipient and one configured reply destination. It does not grant access to the rest of the conversation. A new contribution or changed disclosure requires a new grant and authorization.

Management credentials and grant credentials have different authority. Management authorization identifies an owner and permits scoped creation, inspection or revocation. A grant bearer permits retrieval and, where configured, a holder reply. It cannot create, revoke or enumerate grants. Request fields cannot select a different management owner.

The sender must authorize the hosting origin, content, recipient, reply destination and expiry before creating a grant. The historical configured experiment relies on independently provisioned records binding those choices; the public profile instead uses its exact current account/link and frozen client disclosure plan. Neither an incoming message nor a claimed contribution reference provisions that authority. Hosting does not authenticate the original author's contribution by itself.

Generate the grant credential from 32 random octets supplied by a cryptographic random generator. Encode them as canonical unpadded base64url: exactly 43 ASCII characters, with decode/re-encode equality. A separately generated nonzero ObjectId locates the grant but grants no access. This is the proposed credential-generation profile; a receiver cannot infer randomness merely from a correctly shaped string.

Retain the credential and creation request in protected local storage before transmission. Ordinary logs, diagnostics and general request journals must not contain them. The host may store a credential digest for lookup; retries must still compare the exact original creation request under the idempotency rules below.

The [endpoint trust rules](security.md#show-the-protection-actually-established) apply to the bearer page and its replies. Identify the host's readable-content access separately from HTTPS, grant possession and any later protected observation. A successful host operation or a protected notification cannot establish that the host or its scripts lacked plaintext access. Revocation stops permitted future access; it does not establish deletion of earlier downloaded or operator-observed content.

## Requests and outcomes

All endpoints use direct HTTPS and `Cache-Control: no-store`. Do not follow redirects. Historical `/v0` management requests use their separately configured authorization; the public profile uses its selected owner-bound `/v1` authorization. Retrieval and holder-reply requests use `Authorization: Bearer <grant credential>` with their independent grant credential. Do not use ambient cookies or credentials. JSON bodies use `application/json`, strict UTF-8 and the existing experimental JSON limits; duplicate, missing or unknown members are invalid. Historical reply exports alone use a 2 MiB encoded-response bound; ordinary requests and events retain the 1 MiB bound.

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

All objects have exactly the listed members. This table describes the historical configured profile; its `version` is string `0` except create-v1. The public profile above explicitly adds create-v2 and version-1 management receipts/exports; holder objects remain version 0. ObjectIds are nonzero; principals and EventReferences use the existing identifier contracts. Epochs are canonical unsigned-64 decimal strings. Text is nonblank Unicode scalar-value text. JSON numbers, booleans and null are not used.

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

`operation`, `grant`, `recipient` and `replyDestination` are ObjectIds. `contribution` is an EventReference. In the historical configured profile the latter two destination IDs resolve through the owner's independently provisioned configuration; in the public profile they are opaque tags retained in the client's disclosure plan. Neither is an arbitrary host-interpreted address. `owner` is an enp0 principal from management authentication. `service` is the exact configured HTTPS origin under the [service URI rules](service-answers.md). `requestDigest` is lowercase SHA-256 of the exact request bytes. Management `reason` is `created` or `revoked`, matching the request purpose.

A client accepts a receipt only from the direct authorized service response and only when all request bindings match. Copied JSON is not transferable authentication evidence. Retrieval excludes the recipient identity, credential and management authority.

:::

## Authorizing the original disclosure

The sender authorizes which content may go to which hosting service before anything is uploaded. That service may receive it before the recipient gets the link email. If the upload times out, the app must remember that it may already have shared the content. A failed notification or missing grant does not prove the content stayed private.

::: {.details summary="Exact disclosure authorization, upload markers and reconciliation"}

For the configured message and question flows, the local author authorizes exact contribution bytes, hosting origins, external grants, routing, expiry and reply destinations before any hosting request. Its envelope-v1 disclosure union must exactly match the retained plans. A descriptor in received content cannot create that authorization. Protected preparation precedes hosting and commits the local author evidence with the MLS checkpoint; preparation itself sends nothing.

Creating the grant can disclose content to the provider even if subsequent protected delivery is held. The local plan explicitly covers that order. There is no atomic transaction spanning hosting and email delivery, and withdrawing a notification does not erase content already hosted.

Current author, context and policy checks guard grant creation. Protected-original and minimal-notification release both recheck the plan before DATA. A lost creation response remains uncertain until exact-byte retry or authenticated lookup reconciles it.

Content exposure is a separate fact. Before the worker can release upload content, durably retain its original operation/account/content scope and mark the content release as potentially exposed. After that boundary, the host may have received submitted bytes even if no grant receipt exists.

A positive response may establish known storage; a negative or missing stored-operation result does not erase possible observation of uploaded bytes. Only trusted evidence that no content crossed the release boundary can establish that this attempt made no such disclosure. Later lookup can resolve stored-operation status without proving that no operator saw those bytes. Preserve known or possible exposure in the [local copy plan](delivery-policy.md#a-waiting-delivery-is-different-from-missing-setup), independently of notification success. Historical confirmation is not a guarantee of current remote access.

Messages retain their exact text. Questions use the existing complete readable projection, including every choice in order, reply instructions and the declared external sharing. Authorization and observer-target checks compare that exact text. A changed formatter or a request exceeding its byte limit holds the operation; it does not truncate choices or substitute the heading.

:::

## Protected observations of hosted replies

A compatible client can bring a link holder's reply back into the encrypted conversation. It says who imported the reply and which contribution it answers. It does not claim that the holder is the person originally invited, and it cannot count the holder's words as that person's authenticated answer.

:::: {.details summary="Current receiving agreement, observation and release"}

### Signed receiving support

Current assertion10/context10 includes `hosted-holder-observation` in its fixed readable vocabulary. The device's `hosted-replies` interaction name selects this module's complete observation processing; simpler readers retain safe attributed text without managing a host, contacting it or installing an unvalidated derived effect. Use authored0/envelope6, mime-suite-v2, both rendering profiles and the current logical-reference/slot-audience binding. A provider receipt is not a participant-authored contribution or current receiving authority.

Hosting-account support, a valid bearer receipt and Answers support cannot supply observer authority. Operating a host, fetching its replies, authoring an observation and safely reading that observation are separate roles. The observer must independently implement and authorize the complete publishing path. Existing contexts keep their exact application; older v1/v0 agreements require their own optional-block support and cannot be relabeled. Missing current agreement support holds the affected protected delivery, not other ready recipients. It does not authorize plaintext fallback or a forged holder identity.

### Exact operation and attribution

The operation has exactly five required members: kind equal to `hosted-holder-observation`; text, a nonblank Unicode scalar-value string; target, an exact EventReference; service, the canonical HTTPS hosting origin under the current service URI rules; and attribution equal to `grant-holder`. No null, extra member, holder principal, claimed mailbox, grant credential or remote callback is permitted. The enclosing principal/device is the actual authenticated observer. Its encrypted address record identifies that observer, never a fabricated holder From address.

The target must name the exact original contribution in this conversation. For local creation/release require the independently accepted nonconflicted target, its exact authorized hosted projection, original grant/disclosure plan and current observer authority. The observer audience must remain within the target's permitted audience and the retained observation plan; a target reference cannot add members or expose another private copy. An unavailable target holds creation/release. A receiving client can retain an otherwise valid authenticated observation while its target is unavailable or conflicted, showing that unresolved relationship without guessing an identity or another target. A known invalid audience/source relationship is inactive under the existing acceptance rules.

Resource-free direct MIME plain/HTML projections show the holder text, its grant-holder attribution, authenticated observer, canonical hosting origin and exact target relationship. They explicitly distinguish holder possession from verified mailbox identity. Escape strings into fresh permitted UTF8 HTML; no live host controls, credentials, hidden grant/export IDs, resource parts or copied history. A readable projection cannot override the authenticated operation. The origin is inert display metadata, not permission to navigate or fetch. Merely receiving, decrypting, displaying or replaying this event makes no hosting request or read receipt.

A hosted question's text reply never enters structured answer state, even when it matches an option label. The observation's target is its owning relationship, not an invented replyTo field. Ordinary/indexed replies may target an independently accepted observation, without verifying its holder. Structured quotation selector body is not defined for observations in this binding: a deliberately composed quotation uses unattributed-quotation and preserves the holder/observer distinction. Existing reaction/edit target rules are unchanged; this module grants neither holder-authored corrections nor a new structured service result.

### Owner-bound import and durable deduplication

Acquire exports through the separately authorized native hosting account, exact service/owner namespace and public feed/export contract. Validate original grant, creation, contribution, replyDestination, holder request bytes and matching receipt/digest. Retain that authenticated response with its service/account-owner provenance; TLS evidence is not a portable host signature or participant identity proof. An envelope signature authenticates the observer's assertion, not independent proof of the holder's identity or the host's historical behavior.

Within the local security profile, key observation import by original service, account-owner namespace, grant and holder-operation identity. Atomically bind the exact request bytes/digest and authenticated evidence to one fresh observer event and its immutable prepared delivery. Concurrent imports, pagination/rescan, lost responses and restart reuse that mapping and exact event bytes; never allocate another event to hide uncertainty. Contradictory bytes under that identity retain conflict evidence and hold further release. A grant or replyDestination alone cannot address a mailbox. Account changes cannot reuse another owner's cursor, evidence or observation mapping.

The local replyDestination mapping and retained plan select the actual audience. Before protected release, recheck current observer principal/device/account authority, exact selected application, source target, disclosure plan, identity heads, associations, privacy routes and native MLS dependencies. Hosting read access after identity/device loss does not restore sending rights. A reply made before grant expiry/revocation remains a historical record; neither importing it nor expiry itself proves present holder access or authorizes delivery. Unsupported, stale or conflicting release stays held with the hosted outcome intact.

Deduplication is scoped to the retained owner import. Independent authorized observers or another device without that retained mapping cannot infer global exactly-once observation from a host receipt. Cross-device coordination needs the same authenticated durable mapping before sharing its event/delivery work; never sync live outbox authority or keys as ordinary configuration. No current cross-device implementation is claimed. New private/audience-changing copies need independent authorized composition and fresh event/conversation references; do not transplant an old observation's active target, grant, owner namespace or callback into the new copy. A deliberate inert quotation can preserve the holder attribution without carrying those active references.

### Size and evidence boundaries

For current creation derive replyTextLimit from the complete retained authored0 template, including the scope, per-message addresses, reply intent and disclosure overhead, using the exact serializer calculation below. Envelope6 is prepared separately under its own size and audience rules. The empty text template is preparation-only; it is not an accepted contribution. Generate the final event from that immutable template and a fresh fixed-width event ID, then run complete current validation before release. Changed overhead requires new preparation, never truncation of an accepted holder reply. Historical envelope4/5 and envelope1 calculations retain their exact own formats. An older template helper does not validate authored0 or public create-v2.

Conformance needs signed module selection, exact current operation/MIME/personal roles, owner-bound public export/import, concurrent and crash/restart deduplication, changed account/current authority, private-copy and outer-byte confidentiality, unresolved/conflicted targets and unchanged ordinary answer state. Existing configured envelope1 observer tests and tuple/signature components establish their recorded boundaries only. Complete current native/public-management/observation integration and independent review remain unproven.

::::

## Keeping replies representable

Create version 1 adds `replyTextLimit`, a canonical decimal string between 3 and 1048576. The historical host's independently provisioned configuration must agree with it; public create-v2 retains the exact client-authorized bound without that provisioning requirement. A reply exceeding this limit receives HTTP 413 before a reply receipt is committed. The browser retains the draft so the holder can shorten it. Version 0 grants retain their earlier behavior and do not acquire this guarantee retroactively.

The sender derives the limit from a complete retained observer-event template, including its protected audience and disclosure list. Current templates use complete authored0 under the protected observation agreement above; delivery-envelope6 is prepared separately and remains subject to its own byte and audience limits. Earlier envelope4/5 and the configured contribution-envelope1 experiment retain their exact format-specific measurement. Both use the `hosted-holder-observation` operation. That operation has exactly `kind`, `text`, `target`, `service` and `attribution:"grant-holder"`; `target` is the original contribution's EventReference. Its actual observer principal must authenticate it. Selecting the operation requires explicit agreement in the verified application context; a provider receipt is not a signed contribution.

::: {.details summary="Exact serialized-text bound"}

Use the same serializer to measure and produce the event. Let `T` be the complete template with empty operation text and a valid fixed-width event ID. Let `S(T)` be its exact serialized bytes, and let `L` be the existing 1048576-byte event limit. The reply limit is `B = L - length(S(T)) + 2`; the two bytes are the empty string's quotation marks. If `B < 3`, reply-enabled creation cannot proceed.

Measure the reply as a complete serialized JSON string, including quotation marks and escapes. Accept it only when that measurement is at most `B` and the exact holder request also fits its existing bound. Replacing the empty text and assigning a fresh event ID of the same width then preserves the event limit. Character counts and unescaped UTF-8 lengths are insufficient.

Retain the template encrypted and immutable before sending creation. Changing its audience, disclosures or other overhead requires new preparation. Current membership or policy may prevent later delivery; hold the observation instead of silently changing its audience. Representability is not a promise of delivery.

:::

The limit reveals envelope-overhead information to the provider and can support size inference. The template and roster identities are not explicitly transmitted as part of the grant request; that does not imply that membership counts cannot be inferred.

A hosted question's reply remains free text from a grant holder. A number or matching option label does not become a structured authenticated `answer`; the observer records it as `hosted-holder-observation` targeting the question. Structured-answer state remains unchanged. The host renders question choices and replies as inert text.

## Exporting historical holder replies

The historical reply-export route requires current management owner, issuer, audience, time and `read-management` authorization inside its read transaction. Public owner-bound exports instead require the current account namespace and `mail.hosted.read` scope defined above; they do not require the original device to remain authorized. It remains available after bearer expiry or revocation. The bearer cannot use it. Authorized owner unknown records return 404; another owner receives no record information.

`request` is canonical unpadded base64url of the exact retained holder-request bytes, including any original whitespace. `receipt` is the original holder receipt, and `replyDestination` is the immutable destination tag from the original grant. Check the decoded request schema, service, grant, operation, destination and exact request digest before retaining authenticated export evidence. Preserve unknown or contradictory history as a hold; do not infer a mailbox identity from the holder attribution.

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

## A pending hosted reply survives a restart

A holder reply uses the same visible sending model as other [queued interactions](client-behavior.md#a-pressed-button-keeps-its-sending-status). Keep the writing and selected action visible while it is queued, in flight or awaiting an unknown result. A matching receipt means the hosting service stored it; it does not mean a conversation message was delivered.

Save the reply before its first submission. Closing the page must not turn an uncertain submission into a fresh reply. The browser entry page still keeps the grant credential only in memory, so reopening may require the original invitation before a saved reply can resume. A saved draft is local correspondence, not a credential, cloud backup or proof that the holder is a particular person.

::: {.details summary="Durable holder intent without persisting the bearer"}

Before showing a reply as queued or attempting its POST, atomically retain its original grant/operation identity, exact request bytes, selected hosting origin, credential binding and known outcome in protected local draft/queue storage. Bind the record to this local browser/client profile and the actual grant context. The credential binding may be a SHA256 digest of the original high-entropy grant credential; it is not the live credential and supplies no service authority. Do not persist the bearer, fragment URL or an equivalent usable capability in browser storage. Protect the retained writing under the client's disclosed local correspondence policy. If durable saving is unavailable, retain the writing in the open editor and report the limitation; do not claim a queued operation or submit an unretained job.

While the original authorized page/session retains an eligible credential, reconnection may resume its previously authorized exact operation under current grant policy. A repeated press exposes or manages that job rather than allocating a duplicate. After reload or restart, hold it for missing authorization until the original invitation/credential is deliberately reopened and matches the retained origin, grant and credential binding. Loading the entry page itself never replays a reply or retrieves its result. Offer an explicit resume action for that retained job; the person need not retype or create another reply.

For an attempted or uncertain job, resume by reconciling its original operation status where currently authorized. A matching stored receipt confirms that original result. An eligible unresolved operation follows the exact-byte retry rules with its original operation ID; no response loss, restart or status error creates a replacement. Distinguish a job known not yet attempted from one that may have reached the service. A missing status or denied/expired credential is not proof of non-commit and cannot authorize a new credential, grant, account, channel or operation. Browser storage loss likewise cannot establish that an earlier submission did not occur.

Cancellation can stop work known unsent. It cannot undo a stored or possibly submitted reply, revoke the grant, erase remote text or mark an uncertain effect as absent. Preserve its original known/unknown outcome under the local retention policy. Expired/revoked bearer access leaves the reply held or unresolved; owner-scoped historical reads retain their separate authority and do not become available to the holder. No automatic acknowledgment, observer event, email fallback or fresh action follows from opening/replaying this local state.

The native observation/outbox stage remains independently authorized. The client may display compact pending/sent/failure indicators, but their accessible meaning must distinguish locally queued, hosting-service stored and separately delivered conversation content. Pending feedback must not impersonate a verified participant or confirmed remote answer.

:::

## Forwarding a secret link shares its access

A bearer invitation is access, not just a pointer to a sign-in page. If Bob forwards Carol the usable invitation, Carol can open the same hosted contribution and submit a holder reply while that grant remains valid. The host cannot distinguish Bob from Carol merely by possession of the link. It must retain grant-holder attribution; a notification address, forwarded From or typed name does not authenticate the holder.

For a recognized invitation, a composing client should identify the usable secret link as included access when reviewing a forward or wider audience. Apply the person's existing disclosure choice to that actual capability; do not present a forwarded invitation as a harmless preview or automatically fetch its content to create one. This does not require opening arbitrary links to classify them. Unrecognized ordinary links retain ordinary mail behavior without an invented security guarantee.

The forwarding client cannot narrow or reissue the original grant on its own. An owner may revoke it or authorize a separate grant under the hosting contract. A forwarded email, browser close, management logout or deleted local invitation revokes neither the original bearer nor a copy already downloaded. A new separately authorized grant has its own immutable credential, operation and disclosure plan; it does not relabel an uncertain old grant as absent. Recipient-bound access requires its own selected authenticated model, not a recipient name added to this bearer profile.

## Expiry and revocation

Timestamp access is authorized while service time is at most `expiry.epoch`, inclusive, and the grant is not revoked. Creation after that deadline is refused. An explicit no-expiry grant remains usable until revoked; it must not be an invisible default.

Revocation and access decisions share a serialization boundary. Revocation committed first blocks new retrieval or reply authorization. Retrieval already authorized may finish transmitting afterward; revocation cannot erase copies. Materialize the response from its authorized immutable snapshot rather than rereading changed content later.

After expiry or revocation, the bearer cannot retrieve content or reply results. Previously retained client evidence remains valid historical evidence; denial does not mean a reply never committed. Management authority can inspect retained operation receipts. The reply-records endpoint requires current owner authorization and the read-management scope; it returns the original holder receipt even after grant expiry or revocation. It neither reactivates the grant nor changes the reply's attribution. A grant bearer cannot use this endpoint. An authorized owner's missing record returns 404; another owner must not learn whether it exists. Do not erase retry evidence or reopen grant identifiers after state loss. A repeated authorized revoke may confirm the already-revoked state without changing historical receipts.

Management result lookup, reply-record reads and reply exports authorize the response snapshot under the current credential's own owner/account, scope and validity rules inside the serialized read transaction. An early credential check can reject work but cannot authorize a later read after connection or lock waits. If expiry, owner/account change or revocation wins that boundary, return no protected receipt or existence information through the stale authority. Materialize an authorized immutable snapshot once; finishing transmission does not reactivate permission for another lookup. Historical inspection does not require the original author's old device to regain live sending authority.

## Acceptance boundary

Exercise management authority changing between preflight and database entry, actual lock contention through expiry, current owner/scope checks for existing and missing operations, and original historical receipts after bearer revocation. Distinguish a configured in-memory authorization fixture from a public account/grant store whose revocation must serialize with the read. For holder queues, exercise offline durable save, restart without a persisted bearer, deliberately reopened matching/wrong invitations, lost POST results, original-ID status/retry, denied status, cancellation and unavailable local storage. A session-only editor is not durable offline evidence.

The implementation must test exact retries, lost responses, crashes around commits, separate management/grant authority, expiry and revocation races, holder attribution, and fail-closed damaged storage. Browser tests must inspect actual fragments, history, request headers, referrers and persistent storage; no automatic retrieval or reply may occur on entry or scanning. Redirect fixtures must distinguish rejected fetch redirects from unavoidable pre-load navigation leakage.

The [configured hosted experiment](evidence/README.md#configured-hosted-bearer-access) exercises backend transactions, browser entry, authenticated management evidence and encrypted notification release through loopback SMTP. Current local checks do not prove a remote grant is still active, and a historical receipt does not authorize delivery by itself. The joined message and question experiments bind authenticated disclosure to a local author plan and return holder observations through current MLS authorization. The selected public management contract still needs its full implementation/acceptance; deployed browser trust and credential/key recovery remain unproven. No account-bound identity, endpoint-only confidentiality or independent interoperability is claimed.

## Configured HTTP transport evidence

The local HTTPS adapters reject ambiguous framing before application dispatch and require complete, bounded response bodies before recording receipts. They use a restricted fixed-length HTTP subset; they do not claim general HTTP/1.1 server conformance or intermediary-cache coverage. See [HTTP framing and caching](audits/http-framing.md) for the reviewed rules and deployment limits.

The configured clients also verify the selected TLS application protocol before sending HTTP bytes. Absent ALPN uses an explicit HTTP/1.1 fallback; another selected protocol is rejected. [Server-name and protocol negotiation evidence](audits/tls-service-negotiation.md) records the distinction from certificate verification and the remaining no-overlap alert limitation.
