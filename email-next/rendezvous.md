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

The records below do not yet supply a complete interoperable service. The [independent native-module binding](provider-discovery.md#independent-registrar-and-home-connections) defines this module's sign-in selection, but still requires actual implementation and acceptance evidence. The account-link routes, [reset and inspection binding](#reset-the-home-connection) and [answer-preparation operation](#prepare-the-exact-answer) below select their management records and routes. The [home-installation routes](#install-the-home-authorization) below select installation, inspection and withdrawal. The [pending-offer reader](#read-pending-connection-requests) selects pagination and cursor recovery. Actual joined service owners and acceptance evidence remain required. Existing provider-grant profiles, signature purposes and integer timestamps cannot be relabeled as these string-timestamp records.

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

Use a new `mail-rendezvous-v0` account-link challenge and completion. Reuse the [shared account-link owner](provider-grants.md#shared-account-links-separate-module-authority)'s transaction, possession proof, identity-bundle validation, retry, reset and revocation rules, with the following exact account-link records. The [reset and inspection selection](#reset-the-home-connection) is separate; an old proof cannot be relabeled:

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

### Account-link routes and deadlines

Append these suffixes to the original selected home descriptor's `prefix`,
removing the leading slash and preserving its path. Reject a suffix that escapes
that canonical same-origin prefix, a query or a redirect.

| Operation | Required authority and response |
| --- | --- |
| `POST /links/challenges` | Current `mail.rendezvous.link` grant and the exact challenge request above; 200 retained prepared challenge. |
| `PUT /links/challenges/{challenge}` | Same account incarnation and original family, current link grant and exact completion above; 201 newly committed link or 200 identical retained retry. |
| `DELETE /links/{link}` | Current link grant for the same account incarnation and continuing owner; no body; 204 after disabling the owned link and its derived positive permissions. |

Parameters are the original nonzero ObjectIds. JSON requests and responses use
`application/json`; 204 has no body. Challenges and link results are bare JSON;
the completion contains the original signed `proof` wrapper and complete original
`identity` bundle. The result's `requestDigest` is SHA256 of the exact original
prepared challenge payload. Inherit the shared owner's authentication, no-store,
finite admission, error and original-byte retry rules. Unsupported methods on
these routes return 405 with `Allow`. Account/reset routes and their exact records
are selected [below](#reset-the-home-connection); no provider queue route is inherited.

Configure positive finite local account-link, reset-preparation and fresh-UI
lifetimes independently of offer, cursor and polling policy. None of those
descriptor limits selects an account lifetime. State each
selected preparation interval before approval. A link preparation fits the
descriptor, actual original family and local link policy. Completion additionally
checks that the entire original challenge interval fits the accepted device
binding, and validates the original endpoint and current RECEIVE authority under
the owning identity rules. A successful result retains that original
interval; it cannot be shortened or renewed during completion. Missing evidence
at preparation supplies no device authority. An access refresh does not extend
the family, link challenge or device binding.

Reset and its single-use fresh-UI approval fit their actual original family,
descriptor and respective finite local policies. Apply exclusive `notAfter` and
the full credible clock interval to these rendezvous records. The service's
advertised retention also covers accepted account preparations, completions and
supported uncertain-outcome recovery; refuse an unsupported interval before
issuing it. Never evict an accepted outcome or silently alter its deadline.

Deleting a link atomically disables its dependent home authorizations, pending
offers/answers, dispatch permissions and derived rendezvous grants. Retain their
required negative state and uncertain outcomes. The link's historical retry
cannot reactivate those permissions. Deletion does not rotate the account
incarnation, recall disclosed material, revoke contact identity or affect another
module.

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
| `pendingPageSize` | Positive canonical uint64 maximum pending entries per page. |
| `cursorLifetimeSeconds` | Positive canonical uint64 maximum pending-cursor interval in seconds. |
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

### Install the home authorization

The app sends its signed delegation to its own home service after linking the
device. Installation enables that exact delegation at the service. It does not
publish it to a directory, contact another service, or establish a connection.
The app keeps the original request before sending it so a lost response can be
recovered without creating another authorization.

Append the following suffixes to the selected descriptor's full `prefix`,
preserving its path. Use a current own-account native access token with
`mail.rendezvous.manage`. No incoming account string, mailbox, device key or
public directory result can select the authenticated internal owner.

| Operation | Request and result |
| --- | --- |
| `PUT /home-authorizations/{authorization}` | Exact installation object below; 201 for a newly committed authorization, 200 for an eligible identical retained retry. Returns the retained installation receipt. |
| `GET /home-authorizations/{authorization}` | No body or query; 200 current inspection below, or 404 when no record is available to this original account incarnation and family. |
| `DELETE /home-authorizations/{authorization}` | No body or query; 204 after withdrawing the owned authorization and its derived positive permissions. Unknown or unavailable-to-this-owner identifiers also return 204 without creating a record. |

The path parameter is the original authorization ObjectId. Installation is
`application/json` with exactly these members:

| Member | Type and binding |
| --- | --- |
| `proof` | Original device-signed home-authorization wrapper defined above. |
| `identity` | Complete original identity bundle under the owning identity rules. |

All three routes require the record's original account incarnation and native
family. A new login cannot inherit a previous family's delegation. Account reset
and link deletion retain their separate account-owner revocation authority.

The authenticated native module, continuing internal owner generation, account
incarnation and authorization ObjectId select one installation namespace. The
signed `account` must equal that authenticated incarnation's opaque account
binding. Its `link` belongs to the same account and original native family;
its endpoint belongs to that link. Its `authorization` equals the path parameter.
The descriptor digest, service, prefix and service key match the original
selected descriptor exactly. A proof cannot select another account, link,
descriptor, module or origin.

Before first installation, validate the actual device signature and identity
bundle, the original linked endpoint, independently accepted identity history
and current RECEIVE authority. The entire requested home interval fits the
original descriptor, link, native family and device binding, and contains the
complete credible current clock interval. Keep the exact requested interval;
do not shorten it to make an otherwise invalid authorization fit. Recheck all
local dependencies at the atomic commit. Unavailable authority holds the operation.

Retain the exact installation request, proof, original dependency bindings and
receipt atomically before replying. The advertised retention must cover the
accepted home interval and supported uncertain-outcome recovery; reject an
unsupported interval before installation rather than evicting an accepted
outcome. Invalid proofs and foreign bindings cannot occupy the namespace. Different valid installation bytes under an occupied
namespace return 409; that includes changing its link or replacing the identity
bundle. An identical eligible retry returns the same receipt bytes, without
renewing any deadline or reactivating withdrawn authority. The original identity
bundle remains evidence; current authority is resolved independently rather than
requiring a rewritten retry body.

### Installation receipt

The bare service-authenticated receipt has exactly the following members. It is
not a signed transferable delegation and cannot replace the device's proof.

| Member | Type and binding |
| --- | --- |
| `profile` | Exactly `mail-rendezvous-v0`. |
| `purpose` | Exactly `rendezvous-home-installed`. |
| `authorization` | Original home-authorization ObjectId. |
| `authorizationDigest` | SHA256 of the original home-authorization payload bytes. |
| `link` | Original linked device's ObjectId. |
| `notBefore` | Exact original home-authorization inclusive time string. |
| `notAfter` | Exact original home-authorization exclusive time string. |

This receipt records installation, not continuing availability. An eligible
historical retry can recover it after expiry or withdrawal while the caller
still has current management access under that original owner, incarnation and
family. It cannot restore a retired family or bypass account reset/reassignment.
A client with an uncertain installation inspects the original identifier; it
does not allocate a replacement merely because a response was lost.

### Inspect or withdraw the delegation

Inspection returns bare JSON with exactly `profile`, `purpose`, `authorization`,
`authorizationDigest` and `state`. Their values are `mail-rendezvous-v0`,
`rendezvous-home-state`, the original ObjectId, the original payload digest, and
exactly `active` or `inactive`. The original account incarnation and native
family must match. Foreign, reset and unknown records have the same 404 result.
A missing response or 404 cannot prove that installation never happened.

`active` requires the installed, unwithdrawn original authorization and all
current local descriptor, account, family, link, identity and interval checks.
Known expiry, withdrawal or invalidation yields `inactive`; unavailable current
evidence yields 503 instead of guessing. Recheck before disclosing this result.
An inspection is an observation, not a lease or a credential. Its response
cannot authorize a later operation after a dependency changes.

Withdrawal serializes against installation, offer dispatch/admission, answer
activation and commands under the same authoritative account state. It disables
all positive permissions derived from this authorization, retains required
negative state and uncertain outcomes, and never withdraws a different module
or account. An accepted authorization identifier cannot be reused to replace
that retired authorization. A racing installation retry cannot reactivate it.
Work already disclosed cannot be recalled; required remote invalidations stay
durably queued under the existing account/link invalidation rules.

All three operations inherit this chapter's exact management TLS, no-redirect,
no-0-RTT, credential separation, representation, finite admission and no-store
rules. Unsupported methods return 405 with `Allow: GET, PUT, DELETE` and no
body. Missing
credentials are 401, insufficient scope 403, malformed proof or body 400,
unsupported media 415 and oversized bodies 413. Admission exhaustion returns
429 with positive `Retry-After` seconds; unavailable current authority returns
503. Apply descriptor payload/submission/depth limits before allocation. Error
bodies are exactly `{error}` with the shared values: 400 `invalid`, 401 and 403
`unauthorized`, 404 `notFound`, 409 `conflict`, 413 `tooLarge`, 415
`unsupportedRepresentation`, 429 `rateLimited`, and 503 `unavailable`. Errors
never echo records or tokens. Successful inspections use `application/json`;
204 has no body.
These results authorize neither a plaintext fallback nor a new send.

A home authorization's endpoint state is its original accepted anchor. At use, the offer endpoint must retain the same principal, device, binding and key, with an independently validated accepted path from that anchor to the current head. Do not require raw state-digest equality for binding-continuity use and do not replace the original home proof. The exact target-state challenge rule below applies separately to the live offer.

A new device needs its own link and authorization. Delegating a home service neither enrolls that device nor gives the service a device signing key. An origin/key/account change needs a fresh authorization under an already eligible remembered policy or account reconnection; no credential migrates automatically.

::::

## Reset the home connection

A reset disconnects this account's rendezvous permissions. It stops new connection
requests and use of the account's existing rendezvous grants. It does not change
the person's encryption identity, erase messages, or disconnect their mailbox,
registrar or another home account. An independently eligible encrypted email can
still be delivered through its mailbox path.

The service explains those consequences and names the selected home account
before confirmation. Opening the confirmation page alone does nothing. After a
lost response, the app reconnects and checks the original reset; it does not ask
the person to repeat the reset or assume that their old permissions still work.

:::: {.details summary="Exact account records, reset transaction and recovery"}

### Account management selection

This selection reuses the shared owner's [reset and continuing-owner semantics](provider-grants.md#inspect-a-reset-after-reconnecting).
It selects new rendezvous records, not a renamed provider parser. Every record
below is a strict JSON object with exactly the listed members. The profile is
`mail-rendezvous-v0`. Times are canonical unsigned-64 Unix-second strings under
this chapter's common grammar; retained provider JSON integer times are invalid
here. These records are bare management JSON, without a signed wrapper. A
response authenticates the service-account operation, not a mailbox claim or an
encryption identity.

Append these suffixes to the originally selected descriptor's `prefix`,
preserving its path. Do not resolve a suffix outside that canonical same-origin
prefix. The authenticated module, internal account owner, current incarnation
and original family select the namespace. A submitted address, account string,
preparation identifier or principal cannot select another owner.

| Operation | Required authority and result |
| --- | --- |
| `GET /account` | Current `mail.rendezvous.link` grant; 200 current-account record. |
| `POST /account-reset/preparations` | Current link grant and exact reset request; 200 retained preparation. |
| `PUT /account-reset/preparations/{preparation}` | Original family and link grant, plus fresh server-held account-UI approval; no request body; 204 after the atomic reset. |
| `GET /account-reset/preparations/{preparation}` | Current link grant for the same module and continuing internal owner; 200 retained reset state. A new family can inspect but cannot complete the old family's preparation. |

These account routes inherit the shared owner's TLS, no-redirect,
no-ambient-credential, representation, no-store, status/error, finite admission,
original-byte retry and retention rules. GET has no body or query; route
parameters are original nonzero ObjectIds. Other methods on these routes return
405 with Allow. No account route accepts a token from another module or confers
mailbox, content-delivery, relay, archive or device-enrollment authority.

### Exact records

| Record | Required members | Purpose |
| --- | --- | --- |
| Reset request | `profile`, `request` | No purpose member. |
| Prepared reset | `profile`, `purpose`, `preparation`, `account`, `family`, `nonce`, `confirmation`, `notBefore`, `notAfter` | `rendezvous-account-reset` |
| Current account | `profile`, `purpose`, `account`, `family`, `principal` | `rendezvous-account-state` |
| Retained reset state | `profile`, `purpose`, `preparation`, `outcome`, `account` | `rendezvous-account-reset-state` |

`request` and `preparation` are nonzero ObjectIds. `account` is the selected
account incarnation; `family` is the authenticated OAuth family. Both are exactly
64 lowercase hexadecimal characters. `nonce` is 32-byte lowercase hex.
`principal` is the current linked nonzero `enp0:` principal, or the empty string
when unlinked. None is an address or a credential accepted from client input.

`confirmation` is a canonical same-origin HTTPS URL for the separate account UI,
with no credentials in the URL. Management credentials do not enter that view;
its cookies do not enter the management API. `notBefore < notAfter`. The entire
credible time interval must fit the original preparation interval, current
account/family authority and the service's explicit finite preparation policy.

### Commit once under fresh account approval

The preparation retry namespace is the authenticated module, account, family,
route and request. Retain the original request bytes, preparation and result
before replying. An exact retry returns that preparation without extending its
deadline; different authenticated bytes in that namespace return 409.

The separate account UI requires fresh authentication of the same account and
explicit CSRF-protected confirmation. Its single-use approval binds the exact
preparation, nonce, family, module, incarnation and original expiry. Ordinary
sign-in, a device signature or a submitted consent boolean cannot replace that
approval. A different family cannot complete the preparation.

Completion atomically consumes the approval, rotates this module's account
incarnation, revokes its old families and device links, and disables its home
authorizations, pending offers/answers, dispatch permissions and derived
rendezvous grants. Retain the immutable completed reset result in that same
transaction. Serialize reset with account linking, home authorization,
offer admission, dispatch, answer activation, commands and reads: work admitted
before reset cannot obtain fresh authority after it. Account reassignment or
reprovisioning applies the same invalidation under a new internal owner
generation.

Where an owning operation requires notification or publication to another
service, retain that pending work durably in the local transition. Network
delivery is asynchronous and cannot be part of the local atomic commit. A 204
confirms local reset, not that every remote service has already learned of it or
that disclosed information was recalled. A service that knows the reset blocks
fresh effects immediately; other services retain their current-authority,
inspection and expiry checks. Missing transport bindings remain implementation
prerequisites, not permission to omit required invalidation work.

If the complete bounded local reset cannot commit, none of its local effects
commits. Admission failure cannot evict retained outcomes or report success.
Historical link, home or answer receipts remain historical: replaying them
cannot reactivate a disabled permission. A later connection needs current
native authorization and the actual device/home checks.

### Recover an uncertain result

`outcome` is exactly `pending`, `completed` or `expired`. Pending retains only
the original family's completion authority and deadline. Expired cannot later
complete, including after family withdrawal or an incompatible incarnation
change. For completed, `account` is the immutable resulting incarnation of that
exact reset; otherwise it is the original preparation's incarnation. Read
eligibility under the same transaction boundary as completion. Completed cannot
become pending or expired, or change its recorded resulting incarnation.

After an uncertain completion, disable the old local rendezvous permissions.
Reconnect through fresh native authorization and inspect both the current
account and original preparation. These are separate observations, not an
atomic snapshot. A completed historical result does not install its incarnation
as current or restore a grant. A new family may inspect only for the same
continuing internal owner and module; account reassignment does not transfer
access to the previous owner's outcomes.

Unknown, foreign-owner and garbage-collected preparations return the same 404.
A 404, missing inspection or network failure does not prove the reset failed.
Preserve the original uncertainty and any known completed result. A different
resulting incarnation for the same completed preparation is a conflict and holds
affected operations. Do not reset again automatically, reuse the old family,
restore old permissions from backup or change a contact's saved identity.

### Acceptance boundary

Exercise original-byte retries and changed-byte conflicts; wrong module,
family and owner; absent, expired or replayed UI approval; credible-clock
uncertainty; concurrent linking, offers, reads and reset; crash before and after
commit; retained completion after later resets; account reassignment; unavailable
inspection; and failed remote notification. Defining these records supplies no
runtime evidence. Native authorization, account state, device/home authority,
network release and remote effects each require their own joined acceptance
cases.

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

## Read pending connection requests

The receiving app reads connection requests from its own home service. Reading
never accepts a request or removes it from the queue. The app validates each
original request before deciding whether to answer. If it stops midway through
a page, it can read that page again; receiving the same request twice does not
create a second connection.

:::: {.details summary="Pending pages, opaque cursors and current disclosure checks"}

### Request and response

Use `POST /offers/pending` under the selected descriptor's full `prefix`, with
current own-account `mail.rendezvous.manage` access. This is a nondestructive
read, not an offer submission or an account mutation. Its strict JSON request
has exactly the following members:

| Member | Type and binding |
| --- | --- |
| `profile` | Exactly `mail-rendezvous-v0`. |
| `descriptorDigest` | SHA256 of the original selected descriptor bytes. |
| `link` | Original active target device-link ObjectId. |
| `cursor` | Empty string to begin a scan; otherwise the exact opaque cursor returned by this reader. |

The authenticated module, continuing internal owner, current account incarnation,
original native family, exact link and accepted descriptor select the reader.
The link belongs to that account and family and retains current RECEIVE
authority. A submitted account or mailbox cannot select a queue. No query,
callback, cookie, peer access token, arbitrary URL or public device-listing route
exists. `/offers/pending` is a literal route, not an offer ObjectId.

A successful response is 200 `application/json` with exactly these members:

| Member | Type and binding |
| --- | --- |
| `profile` | Exactly `mail-rendezvous-v0`. |
| `entries` | Ordered array of zero through `pendingPageSize` entries defined below. |
| `cursor` | Empty string if this scan is exhausted; otherwise a nonzero random 32-byte lowercase-hex opaque continuation. |
| `notBefore` | Original scan's inclusive canonical uint64 Unix-seconds string. |
| `notAfter` | Original scan's exclusive canonical uint64 Unix-seconds string. |

Each entry is exactly `{submissionBytes,dispatchBytes}`. Both values are canonical
padded base64: the complete original immutable submission bytes and the complete
original source-signed dispatch wrapper bytes, respectively. Decoding yields the
existing strict records, not a replacement signature format. Preserve all
original bytes, including the submission's identity/evidence bundles and both
home authorizations. Never reconstruct a submission from a summary or return
only the public offer identifier.

The app independently validates those records under the existing offer and
admission rules. It retains the qualified source home, initiator principal/device,
offer payload digest and dispatch payload digest. Equal public offer IDs from
different admitted sources remain distinct. A page is not proof of a known
correspondent, current connection, message delivery or encryption capability.

### Keep one bounded scan

On the first read, the home freezes an ordered set of references to this link's
admitted, unanswered offers. Use the stable total order persisted at original
admission, never a sender-supplied date, claimed sequence or public identifier.
New offers admitted after this cut wait for the next scan. Retain the original
qualified references and cursor state durably before disclosing a continuation;
a service restart cannot reuse a cursor for a different scan or account.

Each cursor binds that scan, its next unexamined reference position, retained
deferred references, selected descriptor, module, continuing owner, account
incarnation, original family and exact link.
Its value reveals none of those fields. Possession supplies no authority without
the same current management connection and local checks. Do not put a cursor in
a URL, forward it to another home or accept it as an access token.

The original scan interval fits the selected descriptor, original family and
link intervals and the descriptor's `cursorLifetimeSeconds`. It contains the
complete credible clock interval at creation. Every continuation retains these
exact bounds. Reading, retrying, refresh-token rotation and service restart do
not extend them. Unavailable time holds disclosure. A cursor's lifetime never
extends any offer, dispatch, home authorization, device binding or local send
policy.

Advance through the retained references in order. Return only entries that are
still admitted, unanswered and eligible for disclosure to this exact device.
Known closed, expired, answered or withdrawn entries may be skipped. Unavailable
per-offer evidence is not a closed entry: retain that qualified reference as
deferred, without disclosing its bytes, and continue to other references within
the work allowance. It must not block independently eligible requests. An entry
admitted after the scan cut cannot be inserted into an older page.

The continuation preserves both the next unexamined position and every unresolved
deferred reference. Examine unexamined references before retrying deferred ones,
so repeated failure at an earlier source cannot starve later requests. Pages may
therefore disclose a later ready request before an earlier deferred request;
this is discovery order, not conversation-message order.

A bounded work allowance may stop scanning early, including an empty page with a
nonempty continuation. Such a continuation must advance the unexamined position
or resolve at least one deferred reference. Moving a newly examined unavailable
reference into the retained deferred set advances the position; repeatedly
moving an already deferred reference does not. If only unavailable deferred
work remains, return 503 with no successful advancement rather than manufacturing
an unproductive continuation. An empty cursor is permitted only after all scan
references are closed or disclosed and no unresolved reference remains. It says
nothing about offers admitted after the cut.

### Recheck before releasing a page

Before disclosing an entry, perform the existing signed source-dispatch inspection
at its already admitted origin. Do network work outside the local account writer.
A closed inspection prevents disclosure; an unreachable or unavailable inspection
holds that entry in the deferred set while other eligible entries can proceed.
Unavailable own-account or scan authority holds the whole page with 503. No page
request selects a new source origin, registrar, realm root or inspection callback.

Recheck the current local account, family, link, identity, installed target home,
offer/cancellation state, original intervals and scan interval at the page's local
commit and actual response-release fences. Serialize those decisions against
answer activation, withdrawal, reset and block changes. If a page cannot still be
released, keep its original scan position available for an eligible retry rather
than reporting successful advancement. This is not an atomic transaction with a
foreign service; the existing source-inspection revocation boundary still applies.

Re-reading a cursor re-evaluates current disclosure authority at the same scan
position. It may omit entries that have since closed or been answered; it must
not return newly admitted offers or revive old permissions. Page observations
need not be byte-identical. The embedded submission and dispatch bytes remain
immutable. Do not reuse a cached positive page after current authority is lost.

### Recover without consuming requests

The client retains received original entries and its next continuation durably
before moving to that continuation. On a lost response or interrupted save, it
reads the previous cursor again. Deduplicate by the qualified offer/dispatch
binding, not the public identifier. Reading or saving a page does not acknowledge,
answer, cancel, consume or extend an offer; those effects use their existing
separately authorized operations.

After restoring a deferred source, recheck its full current authority; a previous
failed inspection is neither a permanent rejection nor permission to disclose.
The client may begin a new scan under current polling policy to find newer offers
while an older scan still holds deferred references. Retain and deduplicate both
until their original bounds or existing cancellation policy end them.

Unknown, expired, foreign-scope, reset and unavailable-to-this-family cursors have
the same 404 `notFound` result after current own authentication. A service that
lost its retained scan must fail this way rather than bind that cursor to a new
scan. The app can begin a new bounded scan under current policy while retaining
already accepted entries and existing send/setup deadlines. A missing page is
not evidence that no request exists or that encryption is unsupported.

New scans and retries honor the selected home's `pollSeconds`; continuation reads
also respect that minimum and any positive `Retry-After`. Cursor retention and
admission policy must support the advertised paging and uncertain-response
recovery. Do not admit work that the service cannot retain and expose within its
supported bounds. Reject new work or a new scan before allocation instead of
evicting a live cursor or an accepted request to make room.

### Bound the complete representation

Each original submission and original dispatch wrapper in this reader fits
`maxSubmissionBytes`; validate this before admitting an offer into this reader.
Their signed payloads also obey `maxPayloadBytes` and strict records obey
`maxDepth`. The page has no more than `pendingPageSize` entries.

The complete encoded JSON page is at most
`512 + pendingPageSize * (64 + 8 * ceil(maxSubmissionBytes / 3))` octets.
The fixed allowance covers the outer fields and each entry's names, quotes and
separators; both base64 values count in the variable allowance. Use checked
integer arithmetic and apply smaller finite local body/allocation limits before
reading or parsing. A service must be able to emit at least one eligible admitted
entry within its actual configured page limit. Never truncate an entry, omit a
signature or silently increase a published bound to fit it.

Requests use `application/json` and fit `maxSubmissionBytes` and `maxDepth`.
Inherit this chapter's TLS, no-redirect, no-0-RTT, no ambient credentials, no
compressed bodies, no-store and shared exact `{error}` rules. Unsupported methods
return 405 with `Allow: POST` and no body. Malformed input is 400 `invalid`, absent
credentials 401 `unauthorized`, insufficient scope 403 `unauthorized`, unsupported
media 415 `unsupportedRepresentation`, and oversized bodies 413 `tooLarge`.
Admission/work exhaustion uses 429 `rateLimited` with positive `Retry-After`
seconds or 503 `unavailable`. No error consumes queue entries, changes membership,
starts an email exchange or permits an automatic plaintext downgrade.

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

### Prepare the exact answer

The receiving app asks its own home service to prepare the answer. The service
returns the exact unsigned bytes the device will sign. Preparation alone does
not activate a grant or tell the sender that the recipient is connected.

Append `offers/{id}/answer-preparations` to the originally selected descriptor's
full `prefix`, preserving that prefix path. `{id}` is the original offer ObjectId.
Use `POST` with the exact answer-preparation request table above as the complete
`application/json` body. There is no query string, callback URL, cookie or
submitted account selector. Use the receiving account's current rendezvous
management access token with `mail.rendezvous.manage`; never send that token to
the initiating service.

| Result | Meaning |
| --- | --- |
| 200 with `application/json` | The exact original unsigned answer payload from the prepared-answer table above. Creation and an eligible identical retry use the same representation. |
| 404 | No eligible retained retry or answerable offer is available under this account, link and exact offer/dispatch pair. Unknown, foreign-account and closed offers without an eligible retained retry have the same result. |
| 409 | A valid request changes the retained request bytes under the same preparation-request namespace. It cannot replace the original preparation. |
| 405 with `Allow: POST` | This preparation route does not support the requested method. |

Inherit the shared management owner's TLS, credential separation, authentication
errors, finite admission and `Cache-Control: no-store` rules for every response.
Do not redirect. Bound the complete request by `maxSubmissionBytes`, the prepared
payload by `maxPayloadBytes`, and strict JSON nesting by `maxDepth`. Enforce any
smaller local processing bounds before allocating retained work. Exhaustion
does not create a preparation, evict an existing outcome or imply that encryption
is unsupported. Errors use the shared exact `{error}` representation: malformed
requests are 400 `invalid`, unsupported media types are 415
`unsupportedRepresentation`, and excessive bodies are 413 `tooLarge`. Deployment
admission exhaustion is 429 `rateLimited` with positive `Retry-After` seconds.
An unavailable source inspection or unavailable current authority is 503
`unavailable`; neither authorizes a replacement operation or a plaintext send.

### Select one admitted offer

The path's public `{id}` is insufficient to select a request. Before creating
work, the service joins all of the following:

- The authenticated internal owner, current account incarnation and original
  native family.
- The request's active target `link`, owned by that account and family, with its
  exact target device and current RECEIVE authority.
- The retained admitted offer, identified by `{id}`, `offerDigest` and
  `dispatchDigest`. Both digests must name the original payloads in that same
  retained submission; the request body's `id` must equal the path parameter.
- The offer's exact target endpoint and both original home authorizations,
  descriptors and identities under this chapter's admission rules. A different
  current target state needs a new offer; it cannot be substituted into this one.

Before a new preparation, perform the required signed source-dispatch inspection
under the existing admitted-source policy. No incoming request selects a new
inspection origin. Do network inspection outside the local account writer, then
recheck the current local account, family, link, identity, home, offer and
cancellation state at commitment. An unavailable or closed inspection holds
creation; a cached active observation is not a permanent authorization.

The complete credible clock interval must fit the requested interval. The entire
requested interval must also fit every original offer, dispatch, home, family,
link, descriptor and participating device-binding interval. Preserve the exact
requested `notBefore` and `notAfter`, with an exclusive upper endpoint. Refuse an interval
that cannot be honored and retained; do not shorten it or extend an older offer.

### Recover preparation without activating it

The preparation-request namespace is the rendezvous module, continuing internal
owner generation, account incarnation, original family, exact target link and
request ObjectId. Validate the authenticated account and admitted offer before
reserving that namespace. Invalid or foreign requests cannot occupy it.

Retain the original request bytes and complete prepared payload atomically before
responding. Under that namespace, an identical request recovers the same
preparation, grant, nonce, endpoints, digests and interval. Different valid bytes
conflict, including an attempt to move the same request to another offer. A lost
response must not generate another preparation or reset its deadline.

An eligible retry may return a retained preparation as historical data after it
has expired or become unusable. The caller still needs current management access
for the same original owner, incarnation and family to recover it. Returning
those bytes does not reactivate a link, reverse cancellation, prove current
source authority or make the answer eligible for activation. A reset, family
withdrawal or owner reassignment never gains fresh authority from a historical
retry. If the original outcome is no longer inspectable, keep uncertainty rather
than treating absence as proof that preparation never occurred.

Bob signs those exact prepared bytes. `PUT /offers/{id}/answer` with `{proof}` atomically checks the same linked account/family, retained preparation, exact signature, all current authorities and intervals, then activates the request-bound grant and records the immutable answer. Creation returns 201, identical retry 200, different valid bytes 409. Invalid answers leave the slot and preparation available. A signed answer is evidence of a device response, not MLS key confirmation.

Activation resolves the offer by the signed answer's original offer and dispatch
digests as well as the path identifier. It consumes only its exact retained
preparation. Concurrent preparations do not create multiple answer slots: the
first valid committed answer wins under the destination's qualified offer
namespace, and a different valid answer conflicts. Recheck current source
inspection and local authority at activation; a previously prepared or signed
answer cannot bypass a later cancellation, reset, expiry or identity hold.

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
