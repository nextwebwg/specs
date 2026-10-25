---
title: Offline setup packages
order: 10.167
blurb: proposed one-use package allocation
sectionNav: true
---

# Offline setup packages

An app can obtain Bob's public encryption setup while his devices are offline.
His chosen service reserves one public package for Alice's setup attempt before
returning it. Bob's private admission key stays on his device.

**Proposed binding: `mail-package-allocation-v0`.** This chapter supplies the
independent allocator referenced by [discovery realms](discovery-realms.md).
It reuses the [single-use and custody rules](security-profile.md#publish-replacements-without-disturbing-in-flight-mail),
but defines new records and permissions. Older bootstrap publication records do
not acquire these meanings by changing their profile.

## What happens for Alice and Bob

1. Bob's app connects a package service, delegates that role and uploads signed
   public packages whose private keys it has already protected locally.
2. Alice obtains Bob's signed directory setup and verifies its original proofs.
   That setup names the exact allocator Bob authorized.
3. Her app signs one bounded allocation request. The service checks its admission
   policy, source possession and Bob's current delegation before reserving a package.
4. Alice's app validates the original returned package and current setup. It can
   then prepare encrypted mail through the normal sending workflow.

An empty pool leaves Bob pending; it does not mean he cannot encrypt. A timeout
leaves the same attempt uncertain. Retrying it never frees the reserved package
or silently substitutes another one. Allocation is not message delivery, personal
identity verification or permission to add someone to a conversation.

## Service selection and privacy

Bob selects his own service through trusted own-account configuration or an
actually supported accepted delegation. He connects its package module and signs
the authorization below. His home and package services may share an operator,
login and underlying account, but their module grants and permissions remain separate.

Alice validates that original device delegation through Bob's accepted identity,
mailbox registration and directory evidence. She need not preconfigure Bob's
service or log into Bob's account. A carried descriptor cannot authorize itself;
the eligible device delegation supplies this recipient-resource location. It does
not install an own-account service, transfer a token or authorize another origin.
Apply the existing HTTPS, resolved-address egress and bounded-work rules before
contacting it. Missing authority holds this path without following another URL.

Allocation is a separate privacy boundary from private directory lookup. The
allocator learns the selected recipient authorization, requested static assertion,
source principal/device, network address, timing and retry identity. This binding
sends no source email address, address book, message content, subject, recipient
list or conversation identifier. Source key possession is not proof of the source
person's identity or mailbox ownership. Do not describe allocation as anonymous.

::: {.details summary="Original records, descriptor and device delegation"}

### Original record rules

Apply the [registration record grammar](mailbox-registration.md): strict original
JSON, exact required members, no duplicates or unknown members, canonical padded
base64 child bytes, nonzero ObjectIds, lowercase hex digests/keys and canonical
unsigned-64 string times/generations. Endpoints are exactly
`{principal,device,state,binding,key}`. A complete credible clock interval must fit
every applicable original interval. All records in this chapter use inclusive
`notBefore` and exclusive `notAfter`, with `notBefore < notAfter`; equality at the
end is outside the interval. Missing credible time holds new effects.

Signed wrappers are exactly `{payload,signature}`. Sign Ed25519 over the stated
ASCII domain, NUL, U32 big-endian original payload length and those exact bytes.
All records here use profile `mail-package-allocation-v0`. Bare requests have no
purpose member unless one is explicitly listed. Parsing proves no authority.

### Service descriptor

The descriptor is strict bare JSON with exactly:

| Member | Contract |
| --- | --- |
| `profile`, `purpose` | This profile, `package-service`. |
| `publication`, `generation` | Stable descriptor ObjectId and canonical uint64 generation. |
| `service`, `prefix` | Canonical HTTPS origin and full same-origin HTTPS prefix ending in `/`. |
| `serviceKey` | Ed25519 allocation-receipt key, 64 lowercase hex. |
| `realm`, `access` | Configured discovery realm ObjectId and exact per-origin resource-admission mapping below. |
| `limits` | Exact bound object below. |
| `notBefore`, `notAfter` | Inclusive start and exclusive end; start strictly precedes end. |

`limits` is exactly `{maxBodyBytes,maxDepth,maxRows,maxStoredBytes,maxPackages,requestLifetimeSeconds,retentionSeconds}`.
Every value is a positive canonical uint64 string, an adjustable operator bound.
They are not user quotas. Enforce smaller local allocation ceilings before parsing.
`retentionSeconds` must cover each accepted request's original lifetime and the
service's declared uncertain-outcome recovery; refuse work that cannot be retained.
Never evict an exposed reservation to admit another request.

Apply the existing [service-prefix and transport rules](discovery-realms.md#exact-configuration-chain).
The descriptor identifies this role, not a foreign mailbox-domain delegation.
Own selection retains original descriptor bytes and publication/generation
high-water: equal generation requires identical bytes, a lower generation holds,
and a different publication requires the owning explicit reconnection decision.
Changing any bytes, including limits or validity, requires a higher generation.
Descriptor updates cannot rewrite old operations, authorizations or promises.
These selection high-water rules apply to accepting a descriptor as a new
selection; they do not relabel retained original operations with its successor.
Continued use still needs the actual owning current policy and original authority.

### Device authorization

The device-signed authorization has exactly:

| Member | Contract |
| --- | --- |
| `profile`, `purpose` | This profile, `package-authorization`. |
| `authorization` | Nonzero authorization ObjectId; immutable within its account incarnation/link. |
| `descriptorDigest` | SHA256 of the exact original selected descriptor bytes. |
| `service`, `prefix`, `serviceKey` | Exact original descriptor values. |
| `account`, `link` | Opaque service account-incarnation binding and active package-module link. |
| `mailbox`, `device` | Exact registered mailbox and authorized endpoint. |
| `associationDigest` | SHA256 of the original registrar attestation payload. |
| `sourcePolicy` | Exactly `admitted-installations`. |
| `notBefore`, `notAfter` | Original bounded authorization interval. |

Its signature domain is `mail/packages/authorization/v0`. The account binding is
64 lowercase hex and the link is an ObjectId. The service installs this delegation
only under that actual current linked own account/family and management grant.
Validate the original registrar publication, admitted issuer, mailbox, home and
current accepted device Receive authority before installation. The complete
interval fits descriptor, association, link, family and device authority. Its
notAfter must be numerically no greater than the original registrar attestation's
notAfter, even though that older owner has a closed endpoint. Do not add a second
or widen an original promise when checking this containment. A publication
interval also fits its static assertion, native package publication
lifetime and all current delegated device dependencies; a receiving-only deadline
does not extend publication eligibility.

`sourcePolicy` explicitly permits bounded automatic first contact by eligible
installations. It is enabled under Bob's account policy when publishing; it does
not require him to approve each sender. An operator may refuse an abusive source
under its current blocking/admission policy. Possession of an authorization ID,
relay address, API key or package does not itself authorize an allocation.

An ordinary accepted identity descendant may preserve this original endpoint
anchor only with unchanged principal, device, binding and key. Fork, repair,
revocation, replaced binding and role barriers retain their owning effects.
Changed service/key/account requires a new delegation, never edited original bytes.

:::

::: {.details summary="Own-account connection, admission and exact operation bindings"}

### Account and request admission

The new native module is `packages`; its exact scopes are
`mail.packages.link mail.packages.manage`. Select this module using the
[independent native-connection mechanics](provider-discovery.md#independent-registrar-and-home-connections).
It has a distinct module registration and grant, even when the same host can reuse
an existing account sign-in. Existing association, rendezvous, provider and relay
grants do not acquire package permissions.

Use the [association account-link member matrix](mailbox-registration.md#link-the-account-without-asserting-mailbox-ownership)
and its shared owning transactions, with this profile and these exact selections:

| Record or operation | Package selection |
| --- | --- |
| Prepared link challenge purpose | `package-account-link`. |
| Link result purpose | `package-account-linked`. |
| Device link signature domain | `mail/packages/account-link/v0`. |
| Current account purpose | `package-account-state`. |
| Prepared reset purpose | `package-account-reset`. |
| Retained reset-state purpose | `package-account-reset-state`. |
| Link/reset permission | Current `mail.packages.link` grant only. |
| Positive resource management | Current `mail.packages.manage` grant and matching active link/device. |
| Negative withdrawal | Fresh current management grant for the exact continuing account owner; retained ownership, not the original expired positive link/device. |

The challenge request, challenge, completion and result have exactly the same
member inventories and types as that string-time matrix, with the profile and
purpose selections above. Reset request/preparation/current-account/retained-state
use exactly the [association reset member inventories](mailbox-registration.md#reset-this-connection-without-replacing-a-contacts-identity)
with these package purposes and scopes. Apply original-family completion,
continuing-owner inspection, separate fresh account-UI approval, atomic incarnation
rotation, retained negative state and uncertainty rules. A reset disables this
module's delegations/publications/allocations, not correspondent identity or another
module. It must not reactivate or return an exposed package to the pool.

### Account routes at the selected package service

Account management uses the same selected package service as the resource pool,
with its separate native package grant. Append these suffixes to the descriptor's
original `prefix`, removing the suffix's leading slash. Preserve that prefix's
path; reject a suffix that escapes it, a redirect or a query.
For example, prefix `https://packages.example/mail/packages/` places the link
challenge route at `https://packages.example/mail/packages/links/challenges`.

| Operation | Required authority and response |
| --- | --- |
| `GET /account` | Current package link grant; 200 current-account record. |
| `POST /links/challenges` | Current package link grant; challenge request from the member matrix above; 200 retained prepared challenge. |
| `PUT /links/challenges/{challenge}` | Same authenticated account incarnation and original family, current link grant and exact device completion; 201 newly committed link or 200 exact retained retry. |
| `DELETE /links/{link}` | Current package link grant for the same account incarnation and continuing owner; no body; 204 after disabling the owned link and its derived positive permissions. |
| `POST /account-reset/preparations` | Current package link grant and exact reset request; 200 retained preparation. |
| `PUT /account-reset/preparations/{preparation}` | Original family and current link grant, plus fresh server-held account-UI approval; no body; 204 after the atomic reset. |
| `GET /account-reset/preparations/{preparation}` | Current package link grant for the same continuing internal owner; 200 retained reset state. A fresh family may inspect but cannot complete the old family's preparation. |

Here, a package link grant has scope `mail.packages.link`; resource management
still requires `mail.packages.manage`. Object parameters are the original
nonzero ObjectIds. GET has no body. JSON requests and responses use
`application/json`; 204 has no body. Prepared challenges, link results, account
records and reset records are bare JSON. The completion contains the original
device-signed `proof` wrapper and complete original `identity` bundle. A link
result's `requestDigest` is SHA256 of the exact original prepared challenge
payload, not the initial request or completion container.

Apply the shared owner's exact HTTP authentication, error, no-store, finite
admission and original-byte retry rules. Unsupported methods on a known route
return 405 with `Allow`. Account, family, module and descriptor come from the
authenticated selected connection. An address, ObjectId, body field or signature
cannot choose another account. Queue, relay and registrar routes are not inherited.

Deleting a link disables its dependent delegations and undisclosed positive work
in the same owning transaction. It cannot restore an exposed or reserved native
package to an unused pool. Retain the original outcomes, spent-reference history
and required negative work. A retained retry reports its historical result; it
cannot recreate the link or its derived permissions. Deleting one link does not
rotate the account incarnation or revoke another module's authority.

### Account deadlines and retention

The service configures positive finite account-link, reset-preparation and fresh
account-UI lifetimes as local deployment policy. It states each selected
preparation interval in the returned record before approval. These are not new
descriptor members or fixed user quotas. `requestLifetimeSeconds` bounds the
allocation and inspection requests defined below; it does not select an account
link or reset lifetime.

A prepared link fits the selected descriptor, its actual original family and the
local link policy. Completion additionally requires that the entire original
challenge interval fit the accepted device binding, with the original endpoint
and current RECEIVE authority validated through the owning identity rules.
Missing device evidence at preparation cannot be treated as accepted
authority; a completion that cannot satisfy these checks is held. A successful
link result retains that challenge interval. Do not silently shorten or renew it.
An access-token refresh does not extend the family, challenge or device binding.

Reset preparation and its single-use fresh-UI approval fit their actual original
family, descriptor and respective local policies. The whole credible clock
interval must fit every required interval, with exclusive `notAfter` throughout
these package records. Reading a historical completed result grants no fresh
positive permission.

The advertised `retentionSeconds` also covers the accepted account preparations,
original completions and supported uncertain-outcome recovery. Reject an interval
the service cannot retain before issuing it. Capacity pressure cannot evict an
accepted retry, reset outcome or spent package reference to make room for another
operation. A changed descriptor or policy cannot edit an original promise.

### Resource admission without another account login

Source admission uses a new `mail-package-access-v0` selection of the
[installation access owner](realm-access.md), separately from the source device
proof. It requires no source login to Bob's account and no per-contact approval.

The descriptor's `realm` must equal the already selected directory realm. `access`
is exactly one [access mapping object](realm-access.md),
with its complete `{service,prefix,policyGeneration,apps,assurances,limits}` inventory
and existing types, positive bounds and app/assurance policies. Its service equals
this descriptor's service. Its access prefix is distinct from the resource prefix
and does not overlap it by path-segment containment. Apps may grant only the exact
scope `mail.packages.allocate`. No directory evaluate/snapshot/publish permission
is inherited. Snapshot geometry and directory-role work charges do not apply;
request, stored-result, worker and replay budgets still apply to this service.

This mapping is authorized as Bob's recipient resource by his eligible device
delegation and original descriptor, not installed as a realm configuration entry
or a new configuration trust root. A client must validate that delegation before
contacting the issuer. Use a separate actual installation key/token for this
origin/realm/purpose; never forward directory, mailbox or own-account credentials.
A descriptor cannot require a client to trust new platform-vendor roots or weaken
its retained assurance. Unavailable required platform support holds this path.

At that access prefix, use exactly the access owner's `/challenges`, `/enroll` and
`/operations` routes, challenge/credential member inventories, protected custody,
actual vendor evidence, canonical SPKI and token/nonce encodings, RFC9421 covered
components/order, request digest, current-policy checks and durable replay/work
reservation rules. Substitute profile `mail-package-access-v0` and the package
scope throughout these new messages; old directory tokens/proofs remain invalid.
The prepared challenge purpose is `package-access-enrollment`. The prepared
challenge and credential realm equals the selected descriptor realm.
This is an explicit new selection, not reinterpretation of an old signed message.

Enrollment request replaces the inherited `configurationDigest` member with
required `descriptorDigest`: SHA256 of the original selected allocator descriptor.
It otherwise retains exactly `{profile,realm,app,publicKey,scopes}`. Prepared
challenge and returned credential each add this required `descriptorDigest` to
their inherited exact inventories. Their signatures/digests cover those original
new bytes; descriptorDigest is not a realm configuration digest. Client checks
it against its retained eligible recipient delegation and descriptor selection.

The server derives its deployed current descriptor and admission mapping from
privileged configuration, requires that exact digest in enrollment, and retains
it with the challenge/installation/credential. Recheck it and current policy at
issuance and every outer execution. A client-supplied descriptor cannot replace
that configuration. A changed descriptor requires a fresh eligible selection and
background same-installation enrollment under current policy; renewal cannot
silently migrate credentials or reset installation counters. The server may
inspect an old inner attempt through a currently eligible new outer selection at
the same authorized service; that does not revive the inner positive authority.

The `/operations` envelope is exactly
`{profile,purpose,request,realm,descriptorDigest,scope,operation}`. Profile is
`mail-package-access-v0`, purpose `package-operation`, request an outer execution
ObjectId, realm this selected realm and descriptorDigest the original currently
selected allocator descriptor hash. Scope is exactly `mail.packages.allocate`.
Operation is exactly `{kind,authorization,body}`: kind `allocate` or `inspect`,
authorization the target authorization ObjectId and body canonical padded base64
of the original complete corresponding resource JSON below. The outer ID is
separate from the inner immutable allocation attempt. Admission reserves work
before interpreting an operation; the source/device proof is still required
before any package reservation. One execution performs only that inner operation.

The result uses exactly the access owner's `{profile,request,requestDigest,scope,status,contentType,result}`
inventory with the new profile, matching outer request/scope, SHA256 of the full
original outer envelope, `application/json` and base64 original inner bytes.
Logical status allows 200/201 and the existing 400/403/404/409/413/415/429/503 errors,
plus this binding's 410 signed historical-status result. Ordinary errors use exact
`{error}` bytes under the existing error-code grammar; 410 instead carries the
complete signed `package-allocation-status` wrapper defined below. Outer 200 does
not mean that the inner operation succeeded. No anonymous direct route bypasses
this owner.

The local request commitment uses domain `mail/packages/access/request/v0` with
the access owner's exact signature-base/length/signature framing. Current own
service descriptor/delegation and admission policy replace the directory role
mapping; no realm configuration role is silently added. A new outer execution
may recover the same original inner allocation after outer uncertainty without
reserving another package. Before releasing a cached positive outer result,
recheck its actual inner account, identity, delegation, publication and original
intervals. If disclosure is now suppressed, return the current signed 410 status
without rewriting the immutable original positive result. Cached bytes do not
bypass withdrawal. Honour backoff without resetting the human-send deadline.

All resource routes below are relative to the selected descriptor prefix. Append
suffixes without their displayed leading slash. JSON requests/responses have
`application/json`, no-store caching, no query, redirect, ambient credential,
content encoding or 0-RTT. Enforce original descriptor and local bounds before
allocation; responses must fit the complete encoded limit before commitment.

### Install a delegation

`PUT /authorizations/{authorization}` takes exactly `{authorization,association,identity}`.
`authorization` is the original signed wrapper; `association` and `identity` are
base64 original complete registrar publication and current identity inventory.
Require matching own-account management and current accepted identity. Retain the
original request and result atomically. Return 201 initially or 200 for identical
retry, each exactly `{authorizationDigest}` with the original authorization payload
hash. Changed authenticated bytes under this account/link/ID return 409. Invalid
proofs cannot occupy an authoritative conflict slot.

`DELETE /authorizations/{authorization}/{authorizationDigest}` under current own
management atomically withdraws that exact delegation and suppresses all dependent
new disclosure/allocation. The digest is SHA256 of the original signed authorization
payload, in 64 lowercase hexadecimal characters. This request has no body.
Return 204 for the matching retained target, including an already withdrawn target.
The authenticated continuing account owner may perform this negative operation
after the original device/family expires; it grants no positive role.
Exact installation retries after withdrawal may recover their historical result
under the historical acknowledgement rules below. Keep the terminal marker across
restart and reset. New delegation uses a fresh ID within its account-incarnation/link
namespace and independently eligible authority. Another account incarnation or link
may use the same route ID; it does not replace or reactivate the earlier delegation.

Both withdrawal routes in this section identify an exact original resource by its
route ID **and payload digest**. Find the retained original account incarnation,
link and resource under the authenticated continuing internal owner; do not infer
the target from the current link, mailbox spelling or route ID alone. Withdrawing
one target MUST NOT withdraw another same-ID resource. A matching digest is a
selector, never account authorization. For a currently authenticated managing owner,
no matching accessible retained target returns 404 without changing any resource.
That response does not prove that the resource never existed. A current management
grant remains required; the digest does not revive an expired bearer.

### Recover an installation receipt

An exact retry of a delegation installation, static assertion installation or
package publication may return its original 200 acknowledgement after that
resource becomes inactive. This receipt confirms the original operation; it does
not establish that its authority is still usable.

The service MUST authenticate a current managing connection belonging to the same
continuing internal account owner. It MUST match the complete retained request
bytes and original account incarnation, link and resource ID before returning the
immutable stored result. A reused mailbox name or account identifier does not
establish continuing ownership. Reassigning the account to another owner MUST NOT
give that owner access to the former owner's receipts.

The original device, link, grant family, delegation or descriptor may have expired.
A reset may have changed the account incarnation. A successor descriptor may have
been activated for the same publication, origin and path prefix. These changes do
not prevent the continuing owner from recovering an exact receipt through a
currently authorized managing connection. They MUST NOT make an old bearer valid,
rewrite the retained request or extend its original intervals. Selecting a
different publication, origin or path prefix does not transfer receipt access.

Returning a receipt MUST NOT reactivate the resource, clear a terminal marker,
install a new permission or disclose a package. Any subsequent resource use MUST
independently satisfy its current authorization and lifetime checks. Clients MUST
NOT treat a successful installation retry as evidence of current usability.

### Install the static assertion

`PUT /authorizations/{authorization}/{authorizationDigest}/assertions/{assertionDigest}` takes exactly
`{assertion,identity}`, both canonical padded base64 original complete assertion10
wrapper and current identity inventory. Require current own management, the same
active account/link and exact installed delegation. The authorization digest selects
the original installed delegation payload, as in the withdrawal route; it does not
replace those positive checks. The assertion digest is SHA256 of the original
assertion payload. Both digests use 64 lowercase hexadecimal characters. Validate the original device/native signature,
exact delegated mailbox/endpoint, current accepted ancestry, applications and real
public control descriptor. It must contain `keyPackage:[]` and
`keyPackageReceiveUntil:null`; removing fields from an existing signed wrapper is
invalid. Its original interval and authority remain separate from delegation expiry.

Retain exact request/assertion bytes and result atomically before reply. Return
201 initially or 200 for identical retained retry, exactly `{assertionDigest}`.
Changed authenticated bytes under that path return 409; invalid proofs cannot
reserve it. Current identity updates use their actual journal, not replacement
of a retained signed assertion. Installing a static assertion allocates no package.

### Publish a package

`PUT /publications/{publication}` takes exactly `{record,advertisement,identity}`.
`advertisement` and `identity` are base64 original complete assertion10 wrapper and
current identity inventory. `record` is a device-signed payload wrapper with exactly:

| Member | Contract |
| --- | --- |
| `profile`, `purpose` | This profile, `package-publication`. |
| `publication` | Original route ObjectId; immutable within account incarnation/link. |
| `authorizationDigest` | Exact original installed authorization payload digest. |
| `staticAssertionDigest` | Original package-free assertion10 payload digest selected by directory setup. |
| `advertisementDigest` | SHA256 of the original package-bearing assertion10 payload. |
| `packageReference` | Original native MLS KeyPackageRef, canonical padded base64. |
| `notBefore`, `notAfter` | Original interval fitting all publication dependencies. |

Signature domain is `mail/packages/publication/v0`. The original static assertion
must already be installed as exact bytes in the authorization's package namespace
under the operation below. A digest cannot stand in for those bytes.

Validate both genuine assertion10 records, their device/native signatures, exact
mailbox/principal/device/binding, original offers and public control descriptor.
The package-bearing assertion has a distinct record ObjectId. Its mailbox,
principal, device, binding, features, applications, orderingExchanges and public
controlKey values exactly match the installed static assertion. Its publication
interval is contained in the static interval. Each original state anchor must
connect to the accepted current head with the same binding/key and no owning
barrier; raw state-digest equality is not required. Its one genuine native package
and explicit receiving promise retain their separate native/lifetime checks. The publisher already holds the private initialization material and
immutable receiving promise locally. The service obtains public bytes only.

Atomically bind the actual native reference to one service/account-incarnation/
device allocation namespace before exposing it. All publications and fresh
responses in that namespace share this reference ledger. Its native-reference
index also retains the original namespace across this service's account-incarnation,
link and authorization changes: reset cannot create a fresh unused slot for a
known reference. A new wrapper, ID, assertion, account or authorization cannot
recycle it. Validate actual native ownership before occupying that index; an
invalid foreign upload cannot poison it by naming another person's reference.
Other independent services are not assumed to share this transaction. The
publisher's protected issuance journal enforces its one-authority promise, and
the receiver retains its independent single-use check. Return 201 initially,
200 for exact retained retry, each exactly `{publicationDigest}`. Changed valid
bytes return 409. Invalid signatures cannot reserve an ID or reference.

`DELETE /publications/{publication}/{publicationDigest}` uses the same
continuing-owner negative withdrawal exception as delegation deletion and has no
body. The digest is SHA256 of the original signed publication payload, in 64
lowercase hexadecimal characters. Return 204 for the matching retained target,
including an already withdrawn target. It checks exact retained account ownership
with a fresh current management grant, without requiring the expired original
link/device or renewing positive authority. It
stops further disclosure/allocation. It preserves terminal reservation evidence;
it cannot recall bytes already exposed. Exact upload retries recover their
historical acknowledgement without reactivation. Historical inspection is metadata
only. Neither deletion invalidates separately cached setup globally; current
identity/binding changes retain that distinct authority.

### Allocate for one setup attempt

`POST /authorizations/{authorization}/allocations` takes exactly `{request,identity}`.
`identity` is base64 complete current source identity inventory. `request` is the
source-device signed wrapper with exactly:

| Member | Contract |
| --- | --- |
| `profile`, `purpose` | This profile, `package-allocation-request`. |
| `request` | Nonzero setup-attempt ObjectId retained before release. |
| `descriptorDigest`, `authorizationDigest` | Exact selected descriptor bytes and target authorization payload digests. |
| `staticAssertionDigest` | Exact selected original package-free assertion payload digest. |
| `initiator`, `target` | Exact source and recipient endpoints. |
| `notBefore`, `notAfter` | Bounded original attempt interval. |

The request span `notAfter - notBefore` must not exceed the selected descriptor's
`requestLifetimeSeconds`, using checked unsigned arithmetic. Its interval fits
the original descriptor, target delegation/static assertion and initiating device
authority. Candidate package selection may only narrow the result interval.

Signature domain is `mail/packages/request/v0`. Validate source possession and
actual accepted source identity/Receive authority, original target delegation,
current account/link/identity state, admission/blocking policy and all intervals.
First source identity acceptance here supplies no mailbox or personal identity
assurance and cannot replace a remembered pin or known safety state.

Select the first eligible publication in ascending ASCII publication-ID order
for this exact authorization/static assertion/device. In one durable transaction,
reserve its native reference and retain the original result before disclosure.
The collision namespace includes allocator account incarnation, authorization,
source principal/device/binding/key and request ID. Identical retries recover that
same result; changed authenticated bytes return 409. Invalid source proofs cannot
consume an ID or reserve a package. Concurrent distinct attempts cannot obtain the
same reference. Exhaustion refuses new work rather than evicting retained evidence.

The signed result payload has exactly `{profile,purpose,requestDigest,authorizationDigest,staticAssertionDigest,state,publication,publicationDigest,packageReference,publicationBundle,notBefore,notAfter}`.
Purpose is `package-allocation-result`; domain `mail/packages/result/v0`.
`requestDigest` hashes the original source request payload. State is exactly
`allocated` or `depleted`. For allocated, publication is the selected ObjectId,
its payload digest/reference are exact, and publicationBundle is base64 original full
package-publication request bytes. For depleted, those four fields are empty
strings. Result notBefore is the maximum original start, and notAfter the minimum
original end, across request and all applicable positive dependencies, including
the chosen publication/package for allocated results. Refuse if the interval is
empty or the complete current credible interval does not fit. Depleted results
use the same rule without a chosen package. This interval does not create a new
receiving promise or change the retained request deadline.

Return 201 for the first committed result and 200 for its eligible identical retry.
A depleted result is terminal for this request; later pool uploads do not change
it. An empty inspection with no committed result is not depletion. A separately
eligible new attempt may obtain fresh material under the original human-send policy
and finite local retry budget; an automatic loop cannot reset that policy/deadline.

A lost result leaves the attempt uncertain. Cancellation, loss, withdrawal or
expiry never unspends its reference. The sender validates original service/device
proofs and actual native package before accepting setup. Allocation alone cannot
prepare or release human content.

### Inspect after uncertainty

The logical inspection operation is POST
`/authorizations/{authorization}/allocations/{request}/inspection`, carried only
through an admitted `inspect` outer operation. Its resource body is exactly
`{proof,identity}`. Identity is base64 complete original source inventory. Proof
is the original source-key signed wrapper over exactly:

| Member | Contract |
| --- | --- |
| `profile`, `purpose` | This profile, `package-allocation-inspection`. |
| `inspection` | Nonzero ObjectId for this exact retained inspection. |
| `allocationRequest` | Base64 original source-signed allocation-request wrapper. |
| `notBefore`, `notAfter` | Original bounded inspection interval. |

The inspection span must not exceed `requestLifetimeSeconds` under checked
arithmetic. It fits the currently selected descriptor and actual admission proof;
its original start/end are fixed before release. An expired allocation request
does not extend or remove this new bounded inspection requirement.

Signature domain is `mail/packages/inspection/v0`. Derive the original initiator,
request ID, descriptor and target from the fully validated original allocation
request. They must match the route and the actual retained namespace. Verify
possession of that exact original source key, original identity evidence and
known safety state. A caller's ID, account login or another device cannot select
this namespace. An inspection cannot change the allocation, spend a package,
replace source identity or reactivate expired source permission.

For metadata-only recovery, original source binding/request expiry does not by
itself erase the retained result. The new inspection must have current credible
time, the selected descriptor/admission policy and original source-key possession.
This narrowly scoped historical read grants no new Receive role or positive setup
use. An operator may deny a compromised/revoked source under current safety policy;
that denial leaves uncertainty, never a claim that no allocation occurred.

The signed status payload has exactly
`{profile,purpose,requestDigest,authorizationDigest,state,resultDigest,publicationDigest,packageReference,notBefore,notAfter}`.
Purpose is `package-allocation-status`; domain `mail/packages/status/v0`.
`requestDigest` names the original allocation payload. State is exactly `pending`,
`allocated`, `depleted`, `withdrawn`, `expired` or `disabled`. Pending means no
committed allocation result is present in this current owning namespace; it is
not proof that an uncertain in-flight worker cannot still commit. Depleted is
only an actually committed depleted result. Withdrawn/expired/disabled describe
current suppression of a previously committed result. Those suppressions never
return an exposed reference to the pool or rewrite the original result.

`resultDigest` hashes the original signed result payload, empty only while pending.
Publication digest and native reference retain their original allocated values,
or are empty when no allocation result exists or the retained result was depleted.
They remain empty for suppressed depletion, including expired/withdrawn/disabled
statuses. A suppressed committed depleted result still has its nonempty original
resultDigest. Status notBefore is the maximum, and notAfter the minimum, of the current
inspection, selected descriptor and admission intervals. Require a nonempty
interval containing the complete credible current time. These times do not
extend any original publication, result or receiving promise. Return 200 for the authenticated status.
Invalid, foreign or unavailable namespaces return generic 404 without a package,
address-existence claim or assertion that no previous result was committed.

Inspection returns metadata only. Original POST retry can recover the retained
complete result while current source/recipient/delegation/publication authority
still permits re-disclosure. If a committed result is now suppressed, return 410
with that signed current status. A currently eligible depleted retry returns its
original result. Never expose package bytes through a diagnostic/status path.
A caller that lost those bytes and cannot recover them holds the original send;
a later separately authorized attempt requires genuinely eligible fresh material.

### Transactions and final output

Serialize publication, source/blocking policy, accepted identity, account/link/
family, delegation, reset, package reservation and immutable result under their
actual owning transactions. Recheck current dependencies and the complete clock
interval at the final bounded output boundary; time spent validating or writing
can expire permission. Reserve response storage before a positive commit. Do no
network work under database writers. A failure after an inner commit remains
uncertain across an outer admission journal; retain the inner original result for
reconciliation rather than claiming cross-database atomicity.

Publications and requests that cannot be retained within configured bounds hold
without partial authoritative mutation. Preserve signed withdrawals, spent native
references and conflict/high-water evidence for their owning supported replay
window. Expired public data may be retired under that explicit policy, but restore
cannot resurrect it as unused. Whole-machine rollback and remote copied packages
retain their existing limits; recipient-side actual atomic MLS admission remains
mandatory even after a valid allocator receipt.

:::

## Acceptance obligations

This proposed wire binding is not implementation or interoperability evidence.
Complete current native/account, installation admission, protected custody and
stateful package owners must pass their acceptance paths before a service
advertises this module. An unavailable owner holds its dependent operation.

Exercise real current identity and independently keyed service/device signatures,
protected private custody, actual native reference validation, concurrent uploads
and allocation, same-reference aliases, invalid-proof collision attempts, empty
pools, lost responses, restart, revocation/reset, changed descriptor generations,
whole credible clocks, final release after expiry, and source/recipient privacy.
No parser, supplied ready flag or same-code happy path proves the whole module.
