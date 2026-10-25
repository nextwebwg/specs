---
title: Mailbox registration
order: 10.165
blurb: proposed independent registrar binding
sectionNav: true
---

# Register your existing address with a connection service

An email app can use an independent discovery and connection service while keeping its existing mailbox. The service checks that the person can receive mail at their address and records which authorized encryption device chose that service. This happens when the person enables the service, rather than sending setup requests to everyone they contact.

The app can retrieve the verification message from its already connected mailbox and finish automatically. An ordinary email provider needs no new code. The verification message is addressed only to the registering person; receiving arbitrary mail cannot start registration or a reply loop.

> [!note] An address check is not an identity check
> The registrar confirms control of a mailbox under its stated method. It does not independently establish the person's identity, control the mailbox's domain or replace an encryption identity already remembered by a correspondent.

This chapter proposes the independent registrar module `mailbox-association`, using `mail-association-service-v0` and `mail-mailbox-association-v0`. It does not change the retained provider-domain setup or local association contracts. Its requirements apply only when this candidate is selected.

This capability cooperates with private discovery, offline setup and live connections within Email/2. It supplies mailbox-association evidence and an authorized service location. It does not allocate a one-use encryption package, authorize a message audience or grant live-connection access.

## Connect once, then verify the mailbox

1. The app connects its selected service account and proves possession of its own currently authorized device key. The service derives the account from authentication.
2. The app selects one of its connected mailbox addresses and starts one retained registration attempt. The registrar sends a random challenge to that exact address.
3. The app retrieves the original verification message through its authorized mailbox connection. It accepts the challenge only for its own pending attempt and signs the exact mailbox, device and service binding.
4. The registrar checks that proof and the secret delivered in the mailbox, then atomically records one completed association. An exact retry retrieves that result.
5. The app publishes the completed evidence through its selected private discovery realm. Another app can use it under its enabled first-contact policy, while preserving existing identity pins and required verification.

If delivery, retrieval or completion is uncertain, the app retains the original attempt. It can inspect or retry within the original deadline. It cannot report an encryption-ready contact merely because registration began or an email server accepted the verification message.

## What still needs a complete binding

This chapter specifies the registrar descriptor and registration records. It does not yet establish an interoperable end-to-end service. In particular:

| Dependency | Owning contract and boundary |
| --- | --- |
| Native sign-in | The [shared native connection mechanics](provider-discovery.md#reuse-sign-in-mechanics-without-sharing-permissions) supply issuer checks, authorization-code/S256 PKCE, public-client authentication, exact callbacks and isolated attempts. The [independent-module selection](provider-discovery.md#independent-registrar-and-home-connections) fixes this module's exact scopes, descriptor, metadata and registration binding. Implement and test that selection explicitly; an earlier native-flow implementation does not acquire it automatically. |
| Account reset and inspection | The [shared account-link/reset owner](provider-grants.md#shared-account-links-separate-module-authority) supplies transaction, continuing-owner and uncertainty semantics. Its retained provider-specific profile, purposes and integer timestamps are not automatically renamed. The association-link and reset/inspection records below select this module's exact wire format. Implement the continuing-owner, atomic reset and uncertain-outcome rules explicitly; defining the records does not establish runtime support. |
| Independent home authorization | [Service federation](service-federation.md#connect-through-the-services-first) owns the architecture. The proposed [rendezvous owner](rendezvous.md#bind-the-home-account-once) defines an independent descriptor and device-signed home authorization, while its native-module/reset and management-route prerequisites remain incomplete; domain-delegated bootstrap evidence cannot be substituted for them. |
| Identity and setup | [Identity state](identity-state.md), [mailbox associations](mailbox-association.md) and the selected setup owner retain their current authority. This registration cannot manufacture a current receive role, native assertion/control descriptor, one-use package allocation or live answer. |
| Realm acceptance | [Discovery realms](discovery-realms.md) admit registrar evidence. A runtime accepting an opaque descriptor or decrypted snapshot cell has not validated this descriptor, complete publication or the joined Store decision. |

These gaps hold dependent operations. They do not permit generic proof objects, parser fallbacks or a claimed encryption-ready result.

:::: {.details summary="Service selection, account linking and registrar authority"}

### Select the registrar under its own authority

The registrar origin is selected through own-account configuration or an accepted mailbox-domain delegation. The selected federation realm must separately admit that exact registrar origin, descriptor digest, signing key, mailbox-control method and validity interval. A registrar cannot admit itself through an incoming lookup result. A mirror or home service cannot replace the admitted issuer key.

The configuration owner supplies the initial realm root through application/account configuration or an explicitly accepted local enterprise configuration. Updates follow that root's authenticated history and retained generation high-water marks. A new root is a local configuration change. This is not a universal permission to follow signed links between arbitrary realms. Two independently configured realms require deliberate shared publication or an already accepted locator; clients do not broadcast the selected address across registrars.

Provider-domain delegation and independent enrollment remain distinct authority paths. A domain's HTTPS delegation can locate its service, as permitted by the existing provider-discovery contract and [RFC8615](https://www.rfc-editor.org/rfc/rfc8615.html). An independent registrar's account login or challenge result cannot satisfy bootstrap2's domain-delegation condition.

### Exact service descriptor

The descriptor has exactly these required fields; there are no omitted defaults or extension members:

| Field | Type and meaning |
| --- | --- |
| profile | Literal `mail-association-service-v0` |
| purpose | Literal `mailbox-association-service` |
| publication, generation | Existing publication ObjectId and canonical unsigned-64 generation string |
| service, managementPrefix | Exact selected canonical HTTPS origin and full canonical same-origin HTTPS prefix ending in `/` |
| serviceKey | Lowercase 64-hex Ed25519 public key; independently admitted by the realm |
| methods | Exactly `["mailbox-delivery"]` for this binding |
| limits | Exact deployment-bound object below |
| notBefore, notAfter | Canonical unsigned-64 decimal Unix-second strings |

Limits has exactly the members in the **descriptor limits record** below with positive canonical unsigned-64 strings. The descriptor advertises adjustable finite deployment policy, not user-mandated quotas. Account/family/device rate controls can impose additional local admission limits without silently changing an already accepted deadline. Retention must cover the original challenge and supported uncertain-outcome recovery; reject an unsupported interval before beginning it. The client applies its own allocation/network ceilings before parsing.

### Descriptor limits members

The record has exactly these required members; the surrounding rules define their values and bindings. No member may be omitted or added.

| Member | Type or binding |
| --- | --- |
| `maxBodyBytes` | Positive canonical unsigned-64 maximum request/body byte count. |
| `maxDepth` | Positive canonical unsigned-64 object nesting limit. |
| `challengeLifetimeSeconds` | Positive canonical unsigned-64 maximum challenge interval in seconds. |
| `associationLifetimeSeconds` | Positive canonical unsigned-64 maximum association interval in seconds. |
| `retentionSeconds` | Positive canonical unsigned-64 retention interval, covering required recovery. |
| `pollSeconds` | Positive canonical unsigned-64 polling interval in seconds. |

For example, service `https://registrar.example` may select managementPrefix `https://registrar.example/mail/association/`; a path-only prefix is invalid. Append each logical route suffix without its leading slash to this prefix, preserving its path. Reject a suffix or URL resolution that escapes the selected prefix.

The descriptor follows [provider discovery](provider-discovery.md) origin/path/TLS/no-redirect/no-ambient-credential and generation-conflict rules. Descriptor bytes are original immutable bytes. A change cannot edit a retained attempt or migrate its credentials. A descriptor is obtained from selected authenticated own-account configuration or accepted delegation; its serviceKey does not self-authenticate it.

### Link the account without asserting mailbox ownership

The new module is `mailbox-association`; its exact native scope set is `mail.association.link mail.association.manage`. Reuse the [existing native authorization-code/S256 PKCE flow](provider-discovery.md#reuse-sign-in-mechanics-without-sharing-permissions), issuer checks, external browser, exact shared callback forms, revocation and module-separated storage. [RFC8252](https://www.rfc-editor.org/rfc/rfc8252.html) supplies the native-app authorization precedent. A provider/relay/setup/rendezvous token never acquires association scope.

Use the new association record profile below. Reuse the [shared-link transaction semantics](provider-grants.md#shared-account-links-separate-module-authority) with the following exact association-link substitution. The reset and inspection binding below selects its own records; retained provider records do not become valid association records:

| Record | Exact purpose |
| --- | --- |
| Challenge request | No purpose member. |
| Prepared link challenge | `association-account-link` |
| Link completion | No purpose member. |
| Link result | `association-account-linked` |

Each record has exactly the required members listed below. A dash means that member is absent, not optional.

| Member | Challenge request | Prepared challenge | Completion | Result |
| --- | --- | --- | --- | --- |
| `profile` | Required | Required | — | Required |
| `request` | Required | Required | — | — |
| `descriptorDigest` | Required | Required | — | — |
| `device` | Required | Required | — | Required |
| `purpose` | — | Required | — | Required |
| `challenge` | — | Required | — | Required |
| `nonce` | — | Required | — | — |
| `service` | — | Required | — | — |
| `account` | — | Required | — | Required |
| `family` | — | Required | — | — |
| `notBefore` | — | Required | — | Required |
| `notAfter` | — | Required | — | Required |
| `proof` | — | — | Required | — |
| `identity` | — | — | Required | — |
| `requestDigest` | — | — | — | Required |
| `link` | — | — | — | Required |

There is no mailbox field in this link. Authenticate the same own account, current incarnation, OAuth family, original descriptor and current device receive authority; consume the exact challenge atomically. A self-consistent first own identity may remain unverified under enabled local policy. Account access cannot replace an already linked principal or enroll a device. A reset affects this module's account permissions/publications; it does not reset correspondent pins or another module.

### Reset this connection without replacing a contact's identity

A reset disconnects this module's account links and withdraws its mailbox associations. It does not change the person's encryption identity, erase correspondence or replace an identity remembered by a contact. Before confirmation, the service names the selected registrar and explains those consequences. Opening the confirmation page alone performs no reset.

The following selection reuses the shared owner's [reset transaction and continuing-owner rules](provider-grants.md#inspect-a-reset-after-reconnecting). It selects exact association records, rather than trying a retained provider parser. All records below are strict JSON objects: every listed member is required and no other member is allowed. Profile is `mail-mailbox-association-v0`. Times are canonical unsigned-64 Unix-second strings under this chapter's common types; safe JSON integer times from retained provider records are not accepted here. These four records travel as bare management JSON, without a `{payload,signature}` wrapper. Their authenticated responses are not signed mailbox or endpoint-identity evidence.

| Operation under the selected management prefix | Required authorization and result |
| --- | --- |
| `GET /account` | Current `mail.association.link` grant; 200 current-account record below. |
| `POST /account-reset/preparations` | Current link grant; exact request below; 200 retained reset preparation. |
| `PUT /account-reset/preparations/{preparation}` | Original family and link grant, plus server-retained fresh account-UI approval; no request body; 204 after the atomic reset. |
| `GET /account-reset/preparations/{preparation}` | Current link grant for the same continuing internal account owner and module; 200 retained reset-state record below. A fresh family can inspect but cannot complete the old family's preparation. |

Route parameters are the original nonzero ObjectIds. GET has no body or query. These routes inherit the shared owner's exact representation, status/error, no-store, finite admission, exact-request retry and retention rules. They acquire no queue, setup, relay or rendezvous scopes. Descriptor, service, module and authenticated internal account select the namespace; an incoming mailbox or identifier cannot select another owner.

| Record | Exact required members | Purpose |
| --- | --- | --- |
| Reset request | `profile`, `request` | No purpose member. |
| Prepared reset | `profile`, `purpose`, `preparation`, `account`, `family`, `nonce`, `confirmation`, `notBefore`, `notAfter` | `association-account-reset` |
| Current account | `profile`, `purpose`, `account`, `family`, `principal` | `association-account-state` |
| Retained reset state | `profile`, `purpose`, `preparation`, `outcome`, `account` | `association-account-reset-state` |

`request` and `preparation` are nonzero ObjectIds. `account` is the selected account incarnation and `family` the authenticated OAuth family, each exactly 64 lowercase hexadecimal characters under the shared owner. `nonce` is 32-byte lowercase hex. `principal` is the current linked nonzero `enp0:` principal, or the empty string when unlinked. `confirmation` is a canonical same-origin HTTPS URL for the service's separate account UI, with no credentials in the URL. Do not copy management credentials into that view or its cookies into management requests. `notBefore < notAfter`; the whole credible clock interval must fit the retained original preparation interval, current account/family authority and explicit finite operator reset-preparation policy.

The preparation request uses the authenticated module/account/family/route/request retry namespace and retains the exact original bytes, preparation and result. An exact retry does not issue another preparation or extend its deadline. Different authenticated bytes in that namespace return 409. The separate service UI requires fresh account authentication and CSRF-protected explicit confirmation. Its single-use server-held approval binds the exact preparation, nonce, family, module, account incarnation and original expiry. No JSON consent boolean, device signature or successful ordinary sign-in replaces that approval.

Reset completion atomically consumes the approval, rotates the module's account incarnation, revokes its old families, links and pending registration authority, and retains the immutable completed reset result. In that same local transaction, record an `account-reset` withdrawal under each affected association's existing generation/CAS rules, together with durable pending publication work. If the complete bounded reset cannot commit, none of those local changes commits; admission failure cannot evict retained outcomes or report success. Registrations, renewals, withdrawals and reset serialize against this account transition. A previously completed registration result remains historical; it cannot reactivate the withdrawn association.

Delivering those withdrawals to an external index is asynchronous. A 204 confirms the registrar's local reset and retained withdrawal work, not atomic withdrawal from every mirror or a recall of evidence already disclosed. Known reset/withdrawal evidence blocks fresh use immediately at the owner that has it; remote clients retain their independent currentness, high-water and expiry checks. Reset cannot delete another registrar's evidence, another module's authority or a correspondent's saved identity.

`outcome` is exactly `pending`, `completed` or `expired`. For `completed`, `account` is the immutable resulting incarnation of that exact reset; otherwise it is the original preparation's incarnation. Pending retains only the original completion authority and interval. Expired cannot later complete, including after original-family withdrawal or an incompatible incarnation change. Completed cannot later become pending/expired or change its resulting incarnation. Retain and read these states under the same transaction boundary as completion and the shared continuing-owner rule. Reassignment/reprovisioning starts a new internal owner generation; a later owner cannot inspect earlier outcomes merely because a mailbox or internal identifier was reused.

After an uncertain completion, disable the old local module permissions, reconnect through fresh native authorization and inspect both the current account and original preparation. These are separate read transactions, not one atomic snapshot. A historical completed result does not install its incarnation as current. Unknown, foreign-owner and garbage-collected preparations have the same 404 response. Neither 404 nor a network failure proves the reset failed. Preserve the original uncertainty and any known completed result; do not reset again automatically, restore the old grant or change a contact's identity pin.

Acceptance must exercise original-byte retries, changed-byte conflicts, wrong module/family/owner, missing or replayed UI approval, expiry/clock uncertainty, simultaneous registration and reset, crash before/after commit, retained completion after later resets, account reassignment, unavailable inspection and external-index publication failure. Wire selection, account safety and actual mailbox/index transports require separate runtime evidence.

::::

:::: {.details summary="Exact registration records and verification email"}

### Common types and signatures

Registration payloads use profile `mail-mailbox-association-v0`. Apply the existing strict original-byte wrapper: exactly `{payload,signature}`, canonical padded base64 payload, lowercase 128-hex Ed25519 signature, signed purpose-specific ASCII domain, NUL, U32 big-endian byte length and original payload bytes. Reject duplicate, missing or unknown members, invalid UTF-8, null and JSON numeric values. Times/generations are canonical unsigned-64 strings. IDs are nonzero random 16-byte lowercase hex; digests/nonces use 32-byte lowercase hex. An endpoint is exactly `{principal,device,state,binding,key}` under the [existing identity grammars](identity-state.md). Mailboxes use the [canonical address owner](mailbox-addresses.md); preserve local-part spelling and do not infer aliases.

Association-owned descriptor, link, reset-preparation, verification-challenge and association-publication intervals are closed: require `notBefore < notAfter` and `notBefore <= earliest <= latest <= notAfter` for the complete credible clock interval. An exact endpoint is eligible only while every other required authority also remains eligible. This convention does not extend an OAuth credential/family, device binding, home authorization or realm configuration beyond its owning rules; for example, the realm configuration's strict upper bound still applies. Unavailable or contradictory credible time holds new effects.

Boundary tests must distinguish equality at each association endpoint, one second outside, an interval straddling an endpoint, and a still-eligible association whose independent authority has already expired. Historical inspection and retained exact retries keep their specified rules; reading an old completed result does not make it current authority.

| Purpose | Signature domain | Signer |
| --- | --- | --- |
| association-account-link | mail/association/account-link/v0 | Current linked device |
| mailbox-association-challenge | mail/association/challenge/v0 | Admitted registrar key |
| mailbox-association-proof | mail/association/proof/v0 | Exact registration device |
| mailbox-association | mail/association/attestation/v0 | Admitted registrar key |
| mailbox-association-withdrawal | mail/association/withdrawal/v0 | Registrar withdrawing its own evidence |
| mailbox-association-migration | mail/association/migration/v0 | Current authorized identity device |

These are purpose-separated uses of existing Ed25519 and framing, not new cryptography. They do not relabel retained provider-grant or bootstrap records.

### Retain the registration before sending anything

The registration request is the exact **registration request record** below. homeAuthorization is the digest of the original device-signed home authorization under the separately negotiated [rendezvous owner](service-federation.md#connect-through-the-services-first). First [install the original home evidence](#install-the-home-evidence); a digest alone is not evidence. The service derives account/family from authentication and requires that same current module link/device. The home authorization must name the chosen current device and an independently eligible service, without claiming control of a foreign mailbox domain.

### Install the home evidence

Before verifying the mailbox, the app supplies the signed home authorization and
its original descriptor. This lets the registrar check which device chose that
home. It does not give the registrar access to messages or prove that the home
service is online.

Use `POST /home-authorizations` under the selected registrar management prefix.
Require a current `mail.association.manage` grant and the same active
association-module account/device link. The request is strict bare JSON with
exactly these members:

| Member | Required value |
| --- | --- |
| `profile` | `mail-mailbox-association-v0`. |
| `request` | Caller-generated nonzero ObjectId for this exact installation. |
| `link` | The active association-module link under the authenticated account/family. |
| `home` | Original device-signed `rendezvous-home-authorization` wrapper, with its own `mail-rendezvous-v0` payload and signature domain. |
| `identity` | Complete original identity bundle under the current identity owner. |
| `descriptor` | Canonical padded base64 of the original strict home-service descriptor bytes. |

The descriptor must exactly match an independently accepted home selection for
this own account: original service origin, publication/generation, descriptor
digest, prefix, key, limits and interval. The selection comes from trusted
own-account service configuration or an actually supported accepted delegation,
with its original provenance and owning high-water/conflict rules. This POST
cannot install that trust, follow a submitted URL, fetch metadata, start login or
infer a domain delegation. A supplied descriptor or its key cannot admit itself.
An unavailable selection holds installation. Configuring a destination supplies
neither device authority nor evidence that a remote home account is active.

Validate the original home wrapper and its purpose-separated signature, exact
descriptor binding, interval and endpoint. Independently validate the complete
identity through the accepted journal, current RECEIVE role, selected principal
and same active association link. The home endpoint is its original identity
anchor. An accepted descendant may preserve it only with the same principal,
device, binding and key and a validated accepted path from that anchor to the
current head. Do not require raw state-digest equality or rewrite the original
proof. A fork, repair boundary, retired/replaced binding or unavailable path holds
installation and use.

Serialize installation with the actual native account/family, association
incarnation/link, accepted identity and selected configuration owners. Retain the
exact request, original home wrapper, descriptor, identity evidence and original
result before replying. The retry namespace is account incarnation, family,
route and request. Return 201 for the first commit, 200 for an identical retained
retry and 409 for changed authenticated bytes. Invalid proofs cannot consume a
request or create an authoritative conflict. Apply the same finite admission,
no-store and error rules as the registration routes; no network work runs inside
these writers.

The authenticated result is bare JSON with exactly:

| Member | Required value |
| --- | --- |
| `profile`, `purpose` | `mail-mailbox-association-v0`, `association-home-installed`. |
| `request`, `link` | Original request and association-link ObjectIds. |
| `homeAuthorization` | SHA256 of the original signed home-authorization payload. |
| `descriptorDigest` | SHA256 of the original home-service descriptor bytes. |
| `device` | The original home authorization's endpoint, including its anchor state. |
| `notBefore`, `notAfter` | Exact original home-authorization times, as canonical uint64 strings. |

These echoed times keep the home's exclusive upper endpoint; the receipt grants
no new interval. It is a local authenticated installation result, not signed
mailbox evidence, home-service permission, presence or proof that the remote home
accepted an account/link. The home service's own [atomic authorization
installation](rendezvous.md#bind-the-home-account-once) remains separately required.
The registrar neither needs nor obtains the person's home-management credential
and does not query an arbitrary remote status endpoint to make this receipt.

Registration and renewal resolve the installed original home payload digest under
the same account, original family/link and exact device binding. Recheck current
selection, accepted identity continuity, required roles and all original
intervals when preparing, completing or releasing a result. Source-owned
descriptor, account/link or family changes cannot retarget this evidence. Reset,
reassignment and withdrawal serialize with these checks and disable dependent
authority in their owning transaction. An exact historical receipt may remain
inspectable; replay cannot reinstall or reactivate it.

The complete publication below intentionally carries the home wrapper but not its
descriptor. Its receiver must already possess an independently accepted matching
descriptor under the owning home-selection rules; a matching digest or incoming
URL cannot supply that authority. Missing evidence holds the dependent operation.

Acceptance includes changed original bytes, malformed wrappers, wrong native
module/account/family/link, unaccepted or conflicting descriptor selection,
valid signatures with absent current RECEIVE authority, accepted descendants and
replaced bindings, uncertain clocks, exact retries after restart, concurrent
reset/configuration changes and failure after an inner commit. A wire definition
alone establishes none of those runtime outcomes.

### Registration request members

The record has exactly these required members; the surrounding rules define their values and bindings. No member may be omitted or added.

| Member | Type or binding |
| --- | --- |
| `profile` | Literal `mail-mailbox-association-v0` for registration records. |
| `request` | Caller-generated ObjectId for this exact operation. |
| `link` | Current association-module account/device link. |
| `mailbox` | Exact canonical mailbox; no inferred aliases. |
| `device` | Exact current endpoint object under the identity grammar. |
| `homeAuthorization` | SHA256 of the original signed home-authorization payload. |

The registrar atomically retains the exact request, random challenge ID and random 32-octet secret, original interval, current account-incarnation/family/link/device dependencies and one prepared verification-message job. The secret is never returned over the management API. Job retries retain the same secret/message identity and bounded interval; duplicate delivery cannot allocate another registration. SMTP acceptance is only custody evidence, not successful mailbox control. A permanent delivery failure or timeout does not prove the address does not exist.

The signed challenge has exactly:

| Field group | Required members |
| --- | --- |
| Format and identity | profile, purpose=`mailbox-association-challenge`, challenge, request |
| Issuer binding | registrar, descriptorDigest, registrarKey |
| Subject binding | association, publication, predecessor, mailbox, device, homeAuthorization |
| Secret and time | nonceDigest, notBefore, notAfter |

nonceDigest is SHA256 of the delivered 32 raw secret octets. For initial registration, association/publication are newly allocated ObjectIds and predecessor is empty. A renewal freezes the existing identifiers and exact expected predecessor. The private service row additionally binds account/family/link; these private management identifiers need not be published with the attestation.

### Carry the secret through ordinary email

The registrar sends one normal readable verification message with a direct child of outer multipart/mixed whose proposed parameter-free content type is `application/mail-association-challenge+json`. This media type is an unregistered allocation proposal: experiments must select it explicitly until registration. The part uses base64 transfer encoding and contains exactly `{challenge,nonce}`: the original registrar-signed challenge wrapper and canonical padded base64 of the 32 secret octets. The readable body explains that this verifies the person's own configured service; it contains no automatic callback or bearer URL. The outer message may use an empty SMTP reverse path and Auto-Submitted semantics appropriate to a generated notification, but neither header authenticates the challenge or instructs legacy clients to hide it.

The registering app scans only that direct part in its own authorized mailbox acquisition, never nested forwarded messages, archives, quoted text or arbitrary attachments. Require exactly one matching part, unambiguous MIME fields and strict base64/JSON under the selected body/depth budgets. Require exact pending request/challenge/registrar/descriptor/mailbox/device/home-authorization bindings, registrar signature and interval, then compare nonceDigest. Unknown, unsolicited or malformed challenges are inert: they cannot start registration, sign-in, HTTP discovery or an automatic email reply.

The local proof-preparation owner obtains the original message from a current authorized mailbox source and retains its exact source incarnation, acquisition generation, input identity and original-byte digest. It must match the own-account mailbox selected before registration. Source access, original input and current device authority are rechecked before releasing proof. An arbitrary caller-supplied string, a From header or a claimed source ID is insufficient. Standard authorized IMAP/JMAP retrieval remains a local mailbox boundary; the registrar does not receive the person's mailbox credentials. [RFC7628](https://www.rfc-editor.org/rfc/rfc7628.html) is an existing OAuth/SASL mechanism for IMAP-style access, not transferable evidence of mailbox identity.

The device signs the exact **device proof record** below with purpose `mailbox-association-proof`. challengeDigest binds the original signed challenge payload, not a reserialized object. Completion is exactly `{challenge,proof,nonce}`. The server checks the exact retained preparation, same authenticated account/family/link, both original signatures and current device authority, secret in constant time and the complete credible clock interval. Invalid proofs cannot consume the challenge or install a pin. Account/link withdrawal or descriptor incompatibility blocks new completion. One transaction consumes the challenge and records its immutable result before replying. Delete the retained raw secret and unreleased verification-job copies after completion/expiry; retain its non-secret digest and exact original outcome for retry. Never log the raw secret. A mailbox provider may retain the delivered message; the consumed secret authorizes no future registration and this protocol promises no erasure of those independent copies.

### Device proof members

The record has exactly these required members; the surrounding rules define their values and bindings. No member may be omitted or added.

| Member | Type or binding |
| --- | --- |
| `profile` | Literal `mail-mailbox-association-v0` for registration records. |
| `purpose` | Exact purpose for this record, specified in its defining rules. |
| `challengeDigest` | SHA256 of the original signed challenge payload. |
| `mailbox` | Exact canonical mailbox; no inferred aliases. |
| `device` | Exact current endpoint object under the identity grammar. |
| `homeAuthorization` | SHA256 of the original signed home-authorization payload. |
| `nonceDigest` | SHA256 of the delivered 32 raw secret octets. |

### Publish a bounded attestation

The registrar signs the exact **attestation record** below. Purpose is `mailbox-association`; method is `mailbox-delivery`. Initial generation is `"0"` and predecessor is the empty string; a successor has the same association/publication and previous original attestation payload digest. The interval fits the selected verification policy and all device/home/descriptor/registrar authority. It cannot extend a current key or home authorization.

### Attestation members

The record has exactly these required members; the surrounding rules define their values and bindings. No member may be omitted or added.

| Member | Type or binding |
| --- | --- |
| `profile` | Literal `mail-mailbox-association-v0` for registration records. |
| `purpose` | Exact purpose for this record, specified in its defining rules. |
| `association` | Stable association ObjectId. |
| `publication` | Stable publication ObjectId. |
| `generation` | Canonical unsigned-64 generation string. |
| `predecessor` | Previous original attestation payload digest, or the permitted initial empty string. |
| `registrar` | Exact independently admitted registrar origin. |
| `descriptorDigest` | SHA256 of the original selected descriptor payload. |
| `registrarKey` | Exact admitted Ed25519 signing key. |
| `mailbox` | Exact canonical mailbox; no inferred aliases. |
| `device` | Exact current endpoint object under the identity grammar. |
| `homeAuthorization` | SHA256 of the original signed home-authorization payload. |
| `challengeDigest` | SHA256 of the original signed challenge payload. |
| `proofDigest` | SHA256 of the exact original device-proof payload. |
| `method` | Literal `mailbox-delivery`. |
| `notBefore` | Canonical unsigned-64 Unix-second start of the original interval. |
| `notAfter` | Canonical unsigned-64 Unix-second end of the original interval. |

The complete publication contains exactly `{attestation,challenge,proof,identity,home}` with original signed wrappers and identity bundle. It excludes the raw secret, management tokens, account passwords, message content and one-use package private keys. The client independently checks all exact subject/device/home/digest bindings. The registrar attests actual secret completion; the device proof attests the named mailbox/home choice. A registrar can lie about delivery, and a malicious mailbox provider can intercept it. Neither signature turns this into independent human verification.

::::

:::: {.details summary="Routes, retries, withdrawal and migration"}

All routes are suffixes of the selected full managementPrefix. The leading `/` below is notation only: append the suffix without it; do not resolve a root-relative URL. Apply the existing native HTTP TLS/origin/strict-body/no-store/error rules, with this module's credentials and descriptor limits. Account IDs come from authentication. Exact retries are scoped by account incarnation, family, route and caller request ID. Foreign/unknown handles are indistinguishable 404 after authentication; body errors do not echo secrets.

| Route | Authority and exact result |
| --- | --- |
| Shared /account, /links/challenges, /links/{link}, /account-reset/preparations subset | Association link scope; the exact association link/reset/inspection schemas and shared transaction rules above only |
| POST /home-authorizations | Association manage scope and same active account/family/link; the exact home-evidence request and authenticated 201/200 installation result above |
| POST /registrations | Association manage scope and active link; exact registration request; 202 `{profile,request,registration,outcome,notBefore,notAfter}` with outcome `pending` |
| POST /associations/{association}/renewals | Same active original account/link under manage scope; `{profile,request,link,expected,device,homeAuthorization}`; subject mailbox and publication derive from the exact owned association; same pending-registration result as initial creation |
| GET /registrations/{registration} | Same account-owner generation and module; 200 `{profile,registration,outcome,publication}`; outcome pending, completed or expired; publication is empty string unless completed, then the original complete publication object |
| PUT /registrations/{registration} | Same active original family/link plus exact completion; 201 complete publication for first commit, 200 identical retained retry |
| GET /associations/{association} | Same current account owner and module manage scope; 200 `{profile,association,current}`, where current is this publication's exact signed attestation or withdrawal wrapper; this is authenticated account inspection, not an independent freshness proof |
| POST /associations/{association}/withdrawals | Same module account owner, manage scope; `{profile,request,expected}` where expected is current original attestation/tombstone payload digest; 201 signed tombstone or 200 retained exact result |
| POST /associations/{association}/migrations | Current original link and exact device-signed migration proof under manage scope; `{profile,request,expected,proof,destination}`; 201 new migration result or 200 exact retained retry |
| GET /associations/{association}/migrations/{request} | Same continuing account-owner generation and module manage scope; 200 exact retained migration result, or indistinguishable 404 for unavailable/foreign handles |

No public address/association/status enumeration route exists. An enrollment challenge is sent only after an authenticated own registration request and its local enabled policy. Deployment limits and backoff must prevent repeated challenge mail; retries cannot resend indefinitely or reset the original interval. A GET or lost PUT response never allocates another challenge. An expired challenge or one invalidated by withdrawal cannot later complete. A completed registration result remains completed with its original publication after later withdrawal; inspect current association state separately, and never use a historical success to reactivate it. A lost completion remains uncertain until the original retained result is inspected; absence is not proof of failure. Same request with changed authenticated bytes returns 409; unauthenticated or invalid signatures cannot create authoritative conflicts.

Withdrawal produces the exact signed **withdrawal record** below. Purpose is `mailbox-association-withdrawal`; reason is exactly `withdrawn`, `account-reset`, `mailbox-reassigned` or `migrated`. It advances this publication's generation under expected-current-digest CAS. The registrar may retract its own assurance under account security policy even if the device was lost; it cannot replace the principal or withdraw another registrar's publication. Preserve tombstones and high-water evidence. Expiry alone is not a signed withdrawal or permission to erase pins.

### Withdrawal members

The record has exactly these required members; the surrounding rules define their values and bindings. No member may be omitted or added.

| Member | Type or binding |
| --- | --- |
| `profile` | Literal `mail-mailbox-association-v0` for registration records. |
| `purpose` | Exact purpose for this record, specified in its defining rules. |
| `association` | Stable association ObjectId. |
| `publication` | Stable publication ObjectId. |
| `generation` | Canonical unsigned-64 generation string. |
| `predecessor` | Exact predecessor payload digest under the required current-generation CAS. |
| `registrar` | Exact independently admitted registrar origin. |
| `registrarKey` | Exact admitted Ed25519 signing key. |
| `mailbox` | Exact canonical mailbox; no inferred aliases. |
| `reason` | One of the exact withdrawal reasons stated above. |
| `notBefore` | Canonical unsigned-64 Unix-second start of the original interval. |
| `notAfter` | Canonical unsigned-64 Unix-second end of the original interval. |

Renewal requires a new locally enabled verification attempt and new mailbox secret. Its completed attestation preserves association/publication and advances the exact expected predecessor under CAS. A withdrawal, incompatible renewal or reassignment between preparation and completion holds the renewal rather than resurrecting a superseded publication. It is an own-account maintenance operation, not a probe sent when a contact is selected. No indefinite renewal follows from possession of old signed evidence. Routine retrieval may be automatic; normal clients are not required to understand or discard these verification messages.

For migration, first complete independently admitted destination registration and home authorization. The outgoing device signs the exact **migration proof record** below; purpose `mailbox-association-migration`. It requires current unchanged device receive authority, accepted identity continuity and exact subject equality. Destination evidence must preserve the same accepted principal; a different principal is a continuity break, not migration. The migration request destination is the complete original destination publication object, never a callback URL. The outgoing registrar retains the original proof and destination evidence, CAS-withdraws its own publication as migrated and returns the exact **migration result record** below: purpose `mailbox-association-migrated`, sourceWithdrawal the original signed tombstone, and both digests SHA256 of the exact original proof/destination attestation payload. It commits that result with the withdrawal before replying; inspection through the continuing account owner cannot reactivate the old record. Completion is not globally atomic across services. A lost result preserves both possible publications until reconciled; it cannot silently select a different identity or erase the old locator.

### Migration result members

The record has exactly these required members; the surrounding rules define their values and bindings. No member may be omitted or added.

| Member | Type or binding |
| --- | --- |
| `profile` | Literal `mail-mailbox-association-v0` for registration records. |
| `purpose` | Exact purpose for this record, specified in its defining rules. |
| `request` | Caller-generated ObjectId for this exact operation. |
| `proofDigest` | SHA256 of the exact original device-proof payload. |
| `sourceWithdrawal` | Original signed outgoing withdrawal wrapper. |
| `destinationDigest` | SHA256 of the exact original destination attestation payload. |

### Migration proof members

The record has exactly these required members; the surrounding rules define their values and bindings. No member may be omitted or added.

| Member | Type or binding |
| --- | --- |
| `profile` | Literal `mail-mailbox-association-v0` for registration records. |
| `purpose` | Exact purpose for this record, specified in its defining rules. |
| `request` | Caller-generated ObjectId for this exact operation. |
| `association` | Stable association ObjectId. |
| `sourcePublication` | Original outgoing publication ObjectId. |
| `sourceDigest` | SHA256 of its exact original attestation payload. |
| `destinationRegistrar` | Exact admitted destination registrar origin. |
| `destinationAssociation` | Destination association ObjectId. |
| `destinationDigest` | SHA256 of the exact original destination attestation payload. |
| `device` | Exact current endpoint object under the identity grammar. |
| `notBefore` | Canonical unsigned-64 Unix-second start of the original interval. |
| `notAfter` | Canonical unsigned-64 Unix-second end of the original interval. |

Multiple current devices require separate device/home proofs; an attestation for one device cannot enroll another. Concurrent renewals, withdrawals and migrations use publication generation plus expected predecessor CAS. Equal-generation unequal records are conflict, not newest-wins. Realm/index high-water records are distinct from service-account generations and identity heads.

::::

:::: {.details summary="Accept first contact without inventing a verified identity"}

A discovery result supplies candidate evidence. Before accepting it, the client validates the selected realm's registrar admission, complete publication and original signatures, exact mailbox spelling, device/home binding, current identity graph, required roles, intervals and publication high-water state. Its original evidence and source classification must remain inspectable.

The Store owner must retain a dedicated registrar-observation variant. It must not fabricate an ordinary message From field or bootstrap response to reuse a different source's authority. Batch validation retains the complete eligible candidate set under the selected query/realm snapshot. A malformed object cannot install a partial principal; a valid known-identity revocation may remain as safety evidence under its own accepted rules.

The first-contact decision then commits, under the same witnessed transaction, the exact mailbox association, accepted identity anchor, originating registrar evidence digests, selected realm/configuration high-water, expected local association generation and local decision ID. This is enabled local first-observation policy, not a network-supplied ready flag. Multiple eligible distinct principals hold as ambiguous. Missing expected current evidence holds; no arbitrary newest-timestamp winner is selected.

Use the existing [allow-unverified/require-verification policy boundary](mailbox-association.md#the-two-decisions). Registrar validation never creates a HumanComparison record. An existing mailbox pin must already match or advance through accepted identity continuity; a new mailbox challenge cannot repin it. Mailbox reassignment remains a visible continuity break with separate old/new histories. Known forks, revoked devices, restored state and independently verified identity requirements retain their current hold outcomes.

The resulting association enables the next owner's setup/capability checks only. Offline published setup still needs authenticated current material and exclusive one-use package allocation. Presence requires the separate request-bound rendezvous answer. Fast delivery requires separate ciphertext custody and authenticated dedup. A locator or successful registration proves none of those by itself.

The registrar necessarily sees the enrolled mailbox and account/device association. Private retrieval can protect later queries and mirror data under its selected construction; it cannot retroactively hide registration from its issuer. Do not replicate plaintext address mappings or predictable email hashes to mirrors. Database and evaluator-key compromise, malicious dataset evaluation and rollback remain full private-discovery obligations. This chapter does not silently replace that goal with a weaker privacy claim.

::::

## Acceptance obligations

Support for this candidate requires the complete joined registration and mailbox-association path. Parser checks or a signature fixture alone do not establish these outcomes.

:::: {.details summary="Registration, races and first-contact acceptance cases"}

| Case | Required observation |
| --- | --- |
| Unchanged legacy mailbox provider + independent registrar | Normal SMTP verification mail and authenticated IMAP/JMAP retrieval complete association; provider needs no Email/2 code |
| Management API response secret leakage | Pending/status/link responses contain no raw nonce; knowing request/challenge IDs does not complete registration |
| Sender SMTP250 only, no mailbox retrieval | Remains pending; no attestation or ready contact |
| Valid spoofed From / copied subject | No authority without exact admitted signed challenge and locally pending binding |
| Message forwarded/nested or second matching MIME part | Inert; no proof release, sign-in or callback |
| Wrong mailbox case/plus alias/source account | No alias inference; wrong actual selected source cannot release proof |
| Disabled source after parse before proof release | Final source/current-authority gate refuses |
| Wrong nonce / bad signature / stale link | No consumption and no identity pin; authenticated abuse accounting may change under its own policy |
| Exact completion retry after response loss | One original attestation; no duplicate registration, fresh secret or renewed interval |
| Restart between delivery job and SMTP acknowledgment | Same prepared message/challenge; duplicate delivery cannot allocate another association |
| Challenge/family/descriptor expiry | Cannot complete; bounded retry cannot extend original interval |
| Two devices finish different challenges | Independent authorized device records, not automatic enrollment or newest-principal-wins |
| Renewal and withdrawal race | Expected predecessor CAS permits one current effect; withdrawn evidence cannot resurrect |
| Reset/reassigned account | Module publications withdrawn; new owner cannot inspect prior owner-generation outcomes or inherit correspondent identity |
| Fresh registrar evidence for already pinned different principal | Holds continuity break; does not repin or merge histories |
| Two eligible registrars return distinct principals | Full candidate set is ambiguous, regardless generation/timestamp |
| Required independent verification | Mailbox-control attestation alone cannot satisfy it or insert HumanComparison |
| Equal-generation unequal attestation | Conflict retained; no timestamp selection |
| Old mirror/old realm epoch | High-water refusal; origin failover cannot reset configuration or epoch |
| Real migrated destination and outgoing uncertainty | Same principal/home proof required; retain old possible state and inspect original result, no automatic credentials transfer |
| Arbitrary forged directory registrar key | Not admitted by configured realm; no network-enrollment side effect |
| Current device revoked between prepare and commit | Final owning transaction holds; old valid signatures do not revive authority |
| Fresh private result without native package reservation | Association only; not first-message admission readiness |
| Registrar evidence + answered rendezvous but lost packet | No content delivery/read receipt; ordinary fallback retains its separate authorization |

::::

A malicious authenticated account may request verification mail for an address it does not control. The registrar cannot establish ownership before the challenge completes. Account/device admission, installation-bound credentials, optional platform evidence, rate/work limits and bounded delivery jobs must constrain this abuse. Eliminating automatic contact probes does not eliminate verification-mail abuse.
