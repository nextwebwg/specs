---
title: Encrypted delivery through homes
order: 10.167
blurb: sealed packets · service custody · one mailbox history
sectionNav: true
---

# Deliver encrypted mail through two homes

**Proposed binding: `mail-home-data-v0`.** Alice sends an already prepared encrypted
mail through her home to Bob's home. Bob can receive it promptly while ordinary
mailbox history remains intact. The services handle sealed bytes and never obtain
the content-decryption keys. This optional module is part of Email/2.

> [!ex] Both paths arrive
> Bob's app receives the fast packet, authenticates the native message and admits
> the contribution. A later SMTP copy adds its real provenance to that same
> contribution. A mailbox-owning provider can additionally store those two
> physical arrivals as one mailbox item, preserving both originals.

Connecting the delivery account enables a bounded Device-approved data-home role
under existing account policy. Sending needs no per-packet or per-route approval
prompt. Endpoint-acceptance sharing is off unless the recipient explicitly enables
that delivery/privacy signal. Acceptance, service custody and reading stay distinct.

The companion baseline keeps the separately authorized SMTP history copy. The
optional [mailbox-stitch module](#optional-provider-mailbox-stitching) joins arrivals
only under actual mailbox ownership and atomic backend authority. It does not give
an independent companion implicit mailbox access.

These are proposed protocol allocations, not an implementation or interoperability
claim. A [rendezvous answer](rendezvous.md#the-answer-is-the-new-exact-grant) still
permits only connection-resume and status-read. Existing provider queue grants and
rendezvous credentials do not authorize this module. Independently admitted data
homes and their current account, route and Device permissions authorize content
carriage. Rendezvous can assist connection establishment; no rendezvous exchange,
answer or current control record is a prerequisite for data upload or admission.

## Prepare and release one packet

Obtain real setup, one-use allocation where required, current receiving support
and native membership through their existing owners. Validate the complete
mail-conversation-v2 content and prepare the [opaque application mail](application-carriage.md).
Atomically retain the native successor and exact prepared bytes. Neither a data
home nor a successful connection exchange supplies native admission or sending
permission.

Upload that complete original mail under the selected own delivery account. Its
current native login, installed submit role and independently accepted current
Send/cohort/audience/disclosure authority govern release. Source custody means the
source durably stored that exact packet, not that Bob's service or Device received it.
The source forwards eligible identical metadata and sealed bytes to the configured
destination. No password, refresh token or management credential crosses homes.

Destination custody requires a valid source-signed release, independently admitted
source-origin policy, current own receiving data role and original admission bounds.
It uses no mandatory live source-inspection round trip per packet. Source logout
or cancellation blocks new source-controlled release when it wins that local order;
a complete packet already released may still enter custody before its original
deadline. This preserves [in-flight uncertainty](transport.md#changes-after-local-release),
not a claim of globally simultaneous revocation.

## Retrieve and assemble normally

An offline app can later retrieve the exact custodied packet through its own
current delivery-account read authority. The app uses the maintained opaque
selector and [application-only native receive boundary](application-carriage.md#authenticate-before-assembling-the-conversation).
It validates the real sender, cohort, current account, receiving promise, epoch,
inner MIME, envelope6/authored0 and scope. Native consumption and its application
outcome commit durably; a held application outcome cannot unconsume native state.

Only the recipient Device's actual durable application Accepted outcome can
produce an enabled endpoint-acceptance receipt. Equal native bytes, mailbox
insertion, a structural parser, custody or native-pending alone prove none of that.
No receipt here implies reading, presence, another Device's acceptance or delivery
to every intended recipient.

## Preserve history and original outcomes

Exact retry preserves packet identity, every signed child and all original bytes.
A lost result remains uncertain; a status observation cannot renew permission or
make an old preparation unsent. Cancellation stops future controlled work and
retains prior possible exposure. It does not delete recipient messages.

The baseline leaves SMTP history scheduled under its existing authority. Native
and application dedup retain the fast and mailbox provenance while assembling one
contribution. A provider implementing the optional stitching module can avoid a
second mailbox item. Message-ID alone never authorizes either operation.

## Data role and wire reference

::: {.details summary="Separate native module, account links and data homes"}

### Separate native module, account links and data homes

The native module is `delivery`; its exact scope set is
`mail.delivery.link mail.delivery.manage`. Reuse the [native connection owner](provider-discovery.md#independent-registrar-and-home-connections),
including the same RFC8414 metadata location, issuer/origin, public registration,
external-browser S256 PKCE, callback forms, refresh and revocation rules. Register
the module separately. A shared operator, issuer or callback merges no permissions.

Use the complete [rendezvous account-link and reset record inventories](rendezvous.md#bind-the-home-account-once)
and their routes/lifecycle, with only these selected literal substitutions:

| Existing literal | Delivery literal |
| --- | --- |
| Profile `mail-rendezvous-v0` | `mail-home-data-v0` |
| `rendezvous-account-link` | `home-data-account-link` |
| `rendezvous-account-linked` | `home-data-account-linked` |
| `rendezvous-account-state` | `home-data-account-state` |
| `rendezvous-account-reset` | `home-data-account-reset` |
| `rendezvous-account-reset-state` | `home-data-account-reset-state` |
| Link completion signature domain | `mail/home-data-account-link/v0` |

No old challenge/proof is rewritten. The actual login supplies account/family,
not a submitted address or identifier. Link scope owns account/link/reset;
manage scope owns home-role and packet operations subject to their additional
permissions. Current Receive is required for linking. A submit role additionally
requires current Send. Reset, native family closure, link withdrawal and known
incompatible identity changes invalidate derived data roles through that actual
owner. They do not erase correspondence or reset another module.

A data-home installation is exactly two required members:

| Member | Type | Rule |
| --- | --- | --- |
| `proof` | Signed wrapper | The complete original data-home authorization below. |
| `identity` | Identity-bundle object | Complete original bundle validated by the current identity owner. |

The service installs the role only when its account, **explicit family**, link and
exact Device match the actual authenticated owner's current records. Its entire
interval fits descriptor, family, link and Device-binding intervals. Submit/read
operations use the same current owner; a stored proof is not a live grant.
A same-Device ordinary binding path uses existing identity continuity rules.
A repair, binding replacement, account change or new Device needs its own actual
authorization, not a relabeled old proof.

Role setup can occur in the background as part of ordinary selected account setup.
It is not repeated for every route, correspondent or packet. The receiving account
still applies its enabled correspondent/source policy.

Installation returns the complete bare [installation-receipt inventory](rendezvous.md#installation-receipt)
with profile `mail-home-data-v0` and purpose `home-data-installed`. No family or
account is selected from that receipt; they remain the original installed role's
actual owner dependencies. Inspection has exactly these required members:

| Member | Type | Rule |
| --- | --- | --- |
| `profile` | String | Exactly `mail-home-data-v0`. |
| `purpose` | String | Exactly `home-data-state`. |
| `authorization` | ObjectId | Original role identifier. |
| `authorizationDigest` | Digest | SHA256 of its original signed payload. |
| `state` | String | Exactly `active` or `inactive` under current owning checks. |

Current account/original family must match; foreign/reset/unknown records have
uniform 404. An eligible historical installation retry can return its original
receipt after role expiry/withdrawal under the original current owner/family;
that fact does not reactivate the role. Delete returns 204 and disables new use,
retaining negative/factual state.
:::

::: {.details summary="Data service descriptor"}

### Data service descriptor

All listed members are required. No member has an implicit default.

| Member | Type | Rule |
| --- | --- | --- |
| `profile` | String | Exactly `mail-home-data-v0`. |
| `purpose` | String | Exactly `home-data-service`. |
| `publication` | ObjectId | Original publication identity. |
| `generation` | Uint string | Original publication generation, including zero. |
| `service` | HTTPS origin | Independently selected exact canonical origin. |
| `prefix` | HTTPS prefix | At service; canonical path ending in `/`. Active module prefixes at an origin must not overlap by segment containment. |
| `serviceKey` | Key | 32-byte Ed25519 key in 64 lowercase hex; delegated specifically for this role. |
| `mailboxMode` | String | Exactly `smtp-copy` or `mailbox-stitch-v0`; the latter requires the optional actual provider-owned module. |
| `limits` | Object | Exact limits below. |
| `notBefore` | Uint string | Inclusive original interval start. |
| `notAfter` | Uint string | Exclusive original interval end. |

Obtain this descriptor from explicit own configuration or independently admitted
data-role delegation. It is not an extra field in retained discovery descriptors.
A known-peer locator is exactly `descriptorBytes` and `homeBytes`, both complete
original records in canonical padded base64. These are candidates, never installed
role or native-readiness evidence. Automatic publication/private lookup requires
its own complete adopted binding. An absent common data profile leaves this path
unavailable; it does not downgrade encryption.

Limits has exactly these required positive uint-string members:

| Member | Meaning |
| --- | --- |
| `maxPacketBytes` | Complete original mail bound before allocation. |
| `maxRequestBytes` | Whole encoded request/response record bound. |
| `maxDepth` | JSON structural depth bound. |
| `pageSize` | Maximum inbox entries in one page. |
| `cursorLifetimeSeconds` | Maximum original inbox-scan interval. |
| `retentionSeconds` | Maximum original interval from upload `notBefore` through `retainUntil`, checked separately against each selected descriptor. |

There are no numeric defaults. Hosts may enforce stricter transient work limits
with 429/503, never change retained bytes or shorten an issued obligation silently.

:::

::: {.details summary="Data-home authorization payload"}

### Data-home authorization payload

All listed members are required. No member has an implicit default.

| Member | Type | Rule |
| --- | --- | --- |
| `profile` | String | Exactly `mail-home-data-v0`. |
| `purpose` | String | Exactly `home-data-authorization`. |
| `authorization` | ObjectId | Fresh original role identifier. |
| `descriptorDigest` | Digest | Complete original selected data descriptor. |
| `service` | HTTPS origin | Exact selected service. |
| `prefix` | HTTPS prefix | Exact selected data prefix. |
| `serviceKey` | Key | Exact selected delegated data key. |
| `account` | Opaque64 | Actual delivery account incarnation. |
| `family` | Opaque64 | Actual original native family owning the referenced link. |
| `link` | ObjectId | That actual current accepted delivery link. |
| `device` | Endpoint | Exact principal/device/state/binding/key object; never a bare ObjectId. |
| `operations` | String array | Nonempty filtered fixed order `["packet-submit","packet-read"]`; no additions, duplicates or permutation. |
| `receipts` | String array | Required explicit array: `[]` unless recipient account/privacy policy explicitly enables `["endpoint-accepted"]`. Omission is invalid; default-off is client policy, not an omitted-field wire default. |
| `notBefore` | Uint string | Inclusive original interval start. |
| `notAfter` | Uint string | Exclusive original interval end. |

Device signature domain is `mail/home-data-authorization/v0`. The signer owns
this actual Device; service installation independently establishes accepted identity,
Receive, and Send for submit. A read role also delegates bounded service ingress
under current receiving/source policy. It supplies no mailbox ownership, MLS
membership or permission to send another contribution.

:::

::: {.details summary="Upload original"}

### Upload original

All listed members are required. No member has an implicit default.

| Member | Type | Rule |
| --- | --- | --- |
| `profile` | String | Exactly `mail-home-data-v0`. |
| `id` | ObjectId | The original packet identifier in its qualified namespace. |
| `sourceDescriptor` | Original bytes | Encoded complete source data descriptor. |
| `targetDescriptor` | Original bytes | Encoded complete target data descriptor. |
| `sourceHome` | Original bytes | Encoded complete source installation, including proof and identity. |
| `targetHome` | Original bytes | Encoded complete target installation. |
| `carriage` | String | Exactly `opaque-mls-application-v0`. |
| `packetLength` | Positive uint string | Exact complete original mail byte count. |
| `packetDigest` | Digest | SHA256 of all complete original mail bytes, before SMTP framing. |
| `nativeDigest` | Digest | SHA256 of the complete transfer-decoded MLSMessage bytes. |
| `notBefore` | Uint string | Inclusive original interval start. |
| `notAfter` | Uint string | Exclusive original interval end. |
| `retainUntil` | Uint string | Original exclusive custody-retention deadline. |
| `packet` | Original bytes | Encoded complete original prepared RFC5322 mail; no reserialization or native fragment. |

The credible release/admission clock fits the entire original packet interval.
That interval is contained in original source and target data-home/descriptor bounds.
`retainUntil` is at least `notAfter` and fits both data-home/descriptor ends and
published retention policy: after validating `notBefore < notAfter <= retainUntil`,
checked subtraction must give `retainUntil - notBefore` no greater than each
selected descriptor's `retentionSeconds`. Retry, custody commit and query time do
not replace that original start or renew the interval. There is no numeric default.
An unsuitable request is rejected, not silently changed.
Storage does not promise that a native receiving/epoch window remains usable.

The Source namespace is delivery module, authenticated account incarnation, actual
linked source Device and id. Destination namespace is delivery module, target
account incarnation, source principal/Device and id. Link/family/home changes are
dependencies, not namespace resets. Exact equality is original upload-byte equality.
No authenticated collision can overwrite it; unauthenticated input reserves nothing.

:::

::: {.details summary="Source release payload"}

### Source release payload

All listed members are required. No member has an implicit default.

| Member | Type | Rule |
| --- | --- | --- |
| `profile` | String | Exactly `mail-home-data-v0`. |
| `purpose` | String | Exactly `home-data-release`. |
| `id` | ObjectId | The original packet identifier in its qualified namespace. |
| `uploadDigest` | Digest | SHA256 of the complete original upload bytes. |
| `sourceHomeDigest` | Digest | Original source data-home payload digest. |
| `targetHomeDigest` | Digest | Original target data-home payload digest. |
| `carriage` | String | Exactly `opaque-mls-application-v0`. |
| `packetLength` | Positive uint string | Exact complete original mail byte count. |
| `packetDigest` | Digest | SHA256 of all complete original mail bytes, before SMTP framing. |
| `nativeDigest` | Digest | SHA256 of the complete transfer-decoded MLSMessage bytes. |
| `releasedFrom` | Uint string | Earliest credible local release-authorization time. |
| `releasedUntil` | Uint string | Latest bound of that same credible interval. |
| `notBefore` | Uint string | Inclusive original interval start. |
| `notAfter` | Uint string | Exclusive original interval end. |

Source-service signature domain is `mail/home-data-release/v0`. Both clock bounds
fit the original upload window and actual source dependencies. `notBefore` and
`notAfter` are byte-identical to the upload strings, not new intervals. The source retains
this proof privately; its own custody receipt cannot be replayed as peer release.
The destination verifies this signature with the exact source data-descriptor key
independently admitted for that origin and delegated by sourceHome. It checks all
upload/digest/length/carriage/endpoint bindings, target data-role/account/link and
original admission bounds. No source credential is accepted or requested.

:::

::: {.details summary="Peer forward"}

### Peer forward

All listed members are required. No member has an implicit default.

| Member | Type | Rule |
| --- | --- | --- |
| `upload` | Original bytes | Complete original upload bytes. |
| `release` | Original bytes | Complete original source-signed release wrapper. |

Both are canonical padded base64. Possession allows only bounded exact replay of
this original packet, not new content, another destination or a changed deadline.
This is not sender-constrained HTTP or proof against the authorized homes.

The source retains one original signed release for an upload before any peer
output. Later eligible local attempts reuse that release and the upload's original
bytes; they do not mint a new release-time statement. Current local permission is checked
again for each attempt. The retained statement describes its original
release-authorization time, while the upload's original `notAfter` remains the
admission deadline.

At the destination, compare the complete decoded upload original and the release's
exact signed payload and signature bytes. A different valid upload or signed
release in the same qualified namespace is a 409 conflict; it cannot replace the
first custody proof or receipt. Validate issuer policy, signatures and bindings
before treating a record as an authorized collision. Formatting differences in
the unsigned release-wrapper JSON or outer Forward JSON do not create a new
operation. An otherwise eligible replay with identical signed children returns
the first retained receipt and preserves its original proof bytes. Canonical
base64 and the common exact-member rules still apply.

:::

::: {.details summary="Custody receipt payload"}

### Custody receipt payload

All listed members are required. No member has an implicit default.

| Member | Type | Rule |
| --- | --- | --- |
| `profile` | String | Exactly `mail-home-data-v0`. |
| `purpose` | String | Exactly `home-data-custody`. |
| `stage` | String | Exactly `source` or `destination`. |
| `custody` | ObjectId | Fresh service-local resource identifier. |
| `id` | ObjectId | The original packet identifier in its qualified namespace. |
| `uploadDigest` | Digest | SHA256 of the complete original upload bytes. |
| `releaseDigest` | Digest or empty string | Empty for source custody, because no peer release is asserted; exact original release payload digest for destination custody. |
| `carriage` | String | Exactly `opaque-mls-application-v0`. |
| `packetLength` | Positive uint string | Exact complete original mail byte count. |
| `packetDigest` | Digest | SHA256 of all complete original mail bytes, before SMTP framing. |
| `nativeDigest` | Digest | SHA256 of the complete transfer-decoded MLSMessage bytes. |
| `sourceHomeDigest` | Digest | Original source data-home payload digest. |
| `targetHomeDigest` | Digest | Original target data-home payload digest. |
| `account` | Opaque64 | Source account for source stage; target account for destination stage. |
| `descriptorDigest` | Digest | The corresponding issuing data descriptor. |
| `acceptedFrom` | Uint string | Earliest bound of the credible commit-time interval. |
| `acceptedUntil` | Uint string | Latest bound of that same credible interval. |
| `retainUntil` | Uint string | Original exclusive custody-retention deadline. |

Signature domain is `mail/home-data-custody/v0`. A source-stage receipt verifies
under the original source descriptor key and sourceHome account; destination stage
verifies under the original target descriptor key and targetHome account. Verify
that stage, issuer delegation, account, all original packet/upload/home digests and
retention equal the actual selected request, not a caller-selected receipt slot.
The commit-time interval fits original authority/admission bounds.

Only exact durable storage plus the stated retrieval/retention obligation permits
a positive receipt. In mailbox-stitch mode the destination additionally commits
the optional module's mailbox history/source facts before releasing that receipt.
A receipt is a signed service claim, not independent proof of disk durability.
An explicitly authorized recipient deletion can limit future retrieval; sender
cancellation cannot. A receipt never reports that deletion or current presence.

Receipt verification is historical: later time need not fit its past commit window.
Verify the original admitted issuer/delegation and complete commit-time containment.
Key expiry does not make an already accepted fact a new grant or current-storage
claim. Expired/unaccepted original issuer evidence cannot be installed from a
receipt. Fresh queries and payload access have their separate current checks.

:::

::: {.details summary="Peer custody query payload"}

### Peer custody query payload

All listed members are required. No member has an implicit default.

| Member | Type | Rule |
| --- | --- | --- |
| `profile` | String | Exactly `mail-home-data-v0`. |
| `purpose` | String | Exactly `home-data-query`. |
| `query` | ObjectId | Fresh immutable query ID. |
| `id` | ObjectId | The original packet identifier in its qualified namespace. |
| `uploadDigest` | Digest | SHA256 of the complete original upload bytes. |
| `releaseDigest` | Digest | The exact original source-release payload digest. |
| `sourceHomeDigest` | Digest | Original source data-home payload digest. |
| `targetHomeDigest` | Digest | Original target data-home payload digest. |
| `notBefore` | Uint string | Inclusive original interval start. |
| `notAfter` | Uint string | Exclusive original interval end. |

Source-service signature domain is `mail/home-data-query/v0`. Its carrier has
exactly these required members, each encoded complete original bytes:

| Member | Meaning |
| --- | --- |
| `sourceDescriptor` | Original source data descriptor. |
| `sourceHome` | Original source data installation. |
| `targetHome` | Original target data installation. |
| `proof` | Complete original signed query wrapper. |

The query issuer must be the currently admitted original source service/key, with
the entire current clock inside the query and descriptor intervals. Home signatures
and named original namespace are verified; they are not new content authority.
The destination's current metadata-disclosure policy must allow this source and
original namespace. It returns only the matching retained receipt. A retired or
unavailable namespace can refuse uniformly; never substitute another account.
No packet is returned. An expired/withdrawn home is not revived by a metadata query.
No new key, origin, account, role or interval is inferred from retained history.
An original expired data home may name historical metadata; it cannot authorize
new payload effects. The original source key must nevertheless have current,
independently admitted data-origin authority for a fresh query. A later accepted
delegation for that same origin/key can supply that current issuer evidence;
carried old records cannot install it. A new key/origin cannot query old history
without an independently selected compatible migration permission. The query's
whole credible clock interval fits its original bounds and that current issuer
admission. No query extends receipt or payload retention.

When an already admitted issuer has unavailable/expired current evidence, return
503 before account lookup, uniformly for every queried id. An unknown/unadmitted
issuer or disallowed historical namespace returns uniform 404; malformed/signature-
invalid proof is 400. Neither refusal proves non-commit. A retired target home can
name retained facts only where the current metadata-disclosure owner still permits
that original namespace. It cannot address a replacement account or expose its
state. Historical receipt validation uses its past commit interval; a fresh query
always uses current query authority. Keep local facts/uncertainty when that new
authority is unavailable.

:::

::: {.details summary="Peer custody observation"}

### Peer custody observation

All listed members are required. No member has an implicit default.

| Member | Type | Rule |
| --- | --- | --- |
| `profile` | String | Exactly `mail-home-data-v0`. |
| `state` | String | Exactly `custodied` or `unknown`. |
| `receipt` | Original bytes or empty string | Original signed destination receipt for custodied; exactly empty for unknown. |
| `endpointReceipt` | Original bytes or empty string | Original enabled Device acceptance wrapper, or exactly empty under the disclosure rules below. |

The response is authenticated by the actual configured peer TLS exchange and
bound to the exact original query/connection, not a generic 200/body. The signed
custody receipt is independently verified as above. A nonempty endpointReceipt
requires state `custodied` and that matching original custody receipt. Unknown
requires both receipt fields to be exactly empty. Unknown is not proof that no earlier
effect occurred. Restore/unavailable state produces 503 rather than fabricated
unknown. Query results cannot overwrite a previously retained positive receipt.

Return endpointReceipt only when the original target data-home authorization
enables `endpoint-accepted` and the recipient's current receipt-sharing policy
still permits disclosure to this original source and namespace. Recheck that policy
before each bounded physical output. Otherwise return exactly empty, including
when the service has a retained acceptance. Enabling sharing later does not widen
an original role that omitted this permission. Empty carries no acceptance,
absence, reading or presence inference. Withdrawal stops fresh disclosure; it
cannot recall already disclosed originals.

Before first retention the source verifies the Device signature, independently
accepted Device identity and original protected audience, and exact selected
query/upload/id/custody/packet/native/target-home bindings. The returned custody
identifier must equal the endpoint receipt's custody. Validate its credible
acceptance interval under the actual original receiving authority, not the query
clock. Publish the first verified original only in the same durable transaction
that compares retained results; changed originals conflict, and later empty
observations or closed errors never erase it. The source may report that retained
historical fact through its own authorized observation after future sharing is
disabled. No new delivery or reading claim follows from recovering that history.

:::

::: {.details summary="Own source observation"}

### Own source observation

All listed members are required. No member has an implicit default.

| Member | Type | Rule |
| --- | --- | --- |
| `profile` | String | Exactly `mail-home-data-v0`. |
| `id` | ObjectId | The original packet identifier in its qualified namespace. |
| `state` | String | One of source-custody, uncertain, destination-custody, endpoint-accepted, stopped, retention-expired. |
| `sourceReceipt` | Original bytes or empty string | Required nonempty original source receipt for this committed server resource. A local prepared Client operation is not this HTTP resource. |
| `destinationReceipt` | Original bytes or empty string | Retained original destination receipt, or exactly empty. |
| `endpointReceipt` | Original bytes or empty string | Retained enabled Device acceptance, or exactly empty. |

Current own native module/account/linked-Device authority selects the namespace;
the id alone cannot select a foreign account or Device. Current manage authority
can inspect its historical local facts without reviving an expired submit role.
Fresh network reconciliation separately needs the exact current query authority.

The own-account client verifies the source receipt against its original Upload.
It can also verify a destination receipt without obtaining the source service's
private Release. In that case it checks the complete destination receipt schema,
original upload/id, packet/native/home/account/descriptor and retention bindings,
the past credible custody interval, and the signature under the independently
admitted original destination service key. It preserves `releaseDigest` as the
canonical 32-byte digest asserted by that destination. This establishes the
signed historical custody claim for that Upload, not that the client has checked
the private Release's signature or current source output permission. Do not expose
the private Release merely to make this observation readable.

An actor that owns the exact Release, including the source handling its peer
response or query result, still compares `releaseDigest` with that original
Release payload digest. A client without it must not manufacture an exact-Release
binding from the receipt, the state label or an HTTP success. Keep these two
validation scopes distinct. An optional endpoint receipt still requires the
matching destination custody id and all original packet/native/target bindings,
plus the separate Device identity, protected audience and original receiving-
authority checks; destination signature verification cannot replace them.

Retain first-success original bytes under the final Client Vault writer; compare
again there against concurrent in-flight observations. Different valid receipts
for the same immutable slot conflict. Later errors/uncertainty cannot erase facts.

`state` summarizes current local work, not historical receipt truth. Derive it in
this exact first-matching order under the same snapshot:

1. If credible current time is unavailable or straddles a boundary needed below,
   return 503 rather than inventing a state.
2. At or after `retainUntil`, use `retention-expired`.
3. If the source work is explicitly stopped, its release window definitely ended,
   or an original dependency is definitively retired/disabled, use `stopped`.
4. With a verified retained endpoint receipt, use `endpoint-accepted`.
5. Otherwise with a verified retained destination receipt, use `destination-custody`.
6. Otherwise with unresolved possible peer output, use `uncertain`.
7. Otherwise use `source-custody`.

The source receipt is always present for a returned committed resource; unknown
or merely staged input is 404 or its actual unavailable 503, not a fabricated
source-custody record. Receipts remain present even when a higher-priority stopped
or expired state applies. Temporary local authority unavailability is 503, not a
permanent stop. Clients report past accepted/custody facts from independently
verified receipts rather than interpreting state as a global delivered/read flag.

:::

::: {.details summary="Inbox request"}

### Inbox request

All listed members are required. No member has an implicit default.

| Member | Type | Rule |
| --- | --- | --- |
| `profile` | String | Exactly `mail-home-data-v0`. |
| `authorization` | ObjectId | Current owned read-role selection. |
| `cursor` | String | Empty for a new cut; otherwise exact nonzero random 32-byte lowercase-hex continuation. |

The role's actual account and linked principal/Device scope the scan. Role renewal
may read still-retained custody for that same account/Device under current read
permission; it cannot reassign old custody to another account or create native keys.
Account-incarnation reset retains old history privately, not as a grant to the new
incarnation. Independently authorized mailbox history remains separate.

:::

::: {.details summary="Inbox page"}

### Inbox page

All listed members are required. No member has an implicit default.

| Member | Type | Rule |
| --- | --- | --- |
| `profile` | String | Exactly `mail-home-data-v0`. |
| `entries` | Array of original bytes | Zero through pageSize complete destination custody receipts in retained admission order. |
| `cursor` | String | Exact opaque continuation or empty only when this cut is exhausted. |
| `notBefore` | Uint string | Inclusive original interval start. |
| `notAfter` | Uint string | Exclusive original interval end. |

This reader uses the following complete scan contract, not rendezvous's
per-entry source-inspection rule. The first empty-cursor read freezes the ordered
set of locally custodied eligible references at one admission cut. Persist the cut,
qualified references and position before disclosing a continuation. Newer arrivals
wait for another scan. Opaque random cursors bind module, descriptor, continuing
owner, account incarnation, original family/link/read Device, scan and position;
they are private lookup selectors, not credentials or encoded claims.

Its original interval fits descriptor/family/link/current read-role and
cursorLifetimeSeconds. Refresh, retry and restart do not extend it. Current read,
account, privacy/deletion and retention policy is checked at page commit and each
bounded output; network waits stay outside writers. Closed/deleted/ineligible
entries can be omitted. Local unavailability is 503 without successful advancement.
An empty continuation means only that cut is exhausted, not a global empty inbox.

A lost nonempty cursor request retries the identical cursor. The app saves entries
and next cursor durably before advancing and deduplicates qualified custody
references. A lost first page permits a new empty-cursor cut, not a reconstructed
old scan. Unknown/expired/foreign/reset/lost cursors return the same authenticated
404. No cursor enters a URL or peer request. Payload fetch is separate and its
complete packet digest/length is checked against the retained receipt.

:::

::: {.details summary="Endpoint acceptance payload"}

### Endpoint acceptance payload

All listed members are required. No member has an implicit default.

| Member | Type | Rule |
| --- | --- | --- |
| `profile` | String | Exactly `mail-home-data-v0`. |
| `purpose` | String | Exactly `home-data-accepted`. |
| `custody` | ObjectId | Original target custody resource. |
| `id` | ObjectId | The original packet identifier in its qualified namespace. |
| `uploadDigest` | Digest | SHA256 of the complete original upload bytes. |
| `packetDigest` | Digest | SHA256 of all complete original mail bytes, before SMTP framing. |
| `nativeDigest` | Digest | SHA256 of the complete transfer-decoded MLSMessage bytes. |
| `targetHomeDigest` | Digest | Original target data-home payload digest. |
| `device` | Endpoint | Exact actual accepting Device endpoint object. |
| `acceptedFrom` | Uint string | Earliest bound of the credible commit-time interval. |
| `acceptedUntil` | Uint string | Latest bound of that same credible interval. |

Device signature domain is `mail/home-data-accepted/v0`. It is emitted only under
current explicitly enabled receipt-sharing policy after actual durable application
Accepted. The local receipt owner binds it to the exact original target custody,
native/preparation, selected account and protected audience. The sender verifies
that Device against its independently accepted identity and actual retained
prepared audience, plus every original receipt/packet/native digest. Full packet
and native equality bind the protected preparation including its audience; no
plaintext subject/content/roster digest is exposed separately. A later native-
pending/rejected observation cannot be relabeled accepted. Service signatures
cannot manufacture this receipt. The default is no endpoint acceptance sharing.
The recipient uploads it through its current own acceptance route; the service
returns the exact original only through the sharing-gated peer custody observation.
The upload acknowledgment alone does not assert that the source received it.

:::

::: {.details summary="Common representation and signature rules"}

### Common representation and signature rules

Each listed inventory is exact; missing/unknown/duplicate decoded members, null,
JSON numbers and booleans are rejected. Uint string means canonical unsigned-64
Unix seconds/count, with no sign, leading zero or implicit default. ObjectId is
nonzero 16-byte lowercase hex; Opaque64 is opaque 32-byte lowercase hex, not a
credential. Digest is 32-byte SHA256 lowercase hex. Key is a 32-byte Ed25519 key.
Endpoint is exactly the existing principal/device/state/binding/key object; Device
identifiers use `end0:` grammar inside it, never an ObjectId interchangeably.

Original bytes use canonical padded base64. Every signed wrapper is exactly
payload and signature under the existing encoding: encoded original payload and
128 lowercase hexadecimal signature characters. The fixed-purpose signature
input is its stated ASCII domain, NUL, U32BE payload byte length and exact payload.
Use maintained primitives/decoders; never reconstruct signed children. New domains
start with `mail/`. Inherited child records retain their original domains unchanged.

Before relevant allocation, apply whole request, depth, encoded/decoded packet and
native work limits independently. Packet is one complete original current opaque
mail, not bare MLS ciphertext, concatenated native objects or operation JSON.
Its exact full-mail hash is custody identity. Its exact native-wire hash is the
separate protected-object equality used for authorized stitching. Equality of
either hash establishes no successful application acceptance or recipient reading.
:::

::: {.details summary="Exact HTTP routes and result categories"}

### Exact HTTP routes and result categories

Suffixes append to the selected data prefix without URI-reference resolution or
redirect. Own and peer routes are distinct and parsed once. Require HTTPS with
accepted server identity, no 0-RTT/content coding/ambient cookies, no-store, bounded
representations and independent credential origin/module binding. A failed role,
authentication, signature or parser never falls through to another owner.

| Route | Authority and result |
| --- | --- |
| `PUT /homes/{authorization}` | Own manage and actual linked account/family/Device; 201 install, 200 identical current retry, 409 changed collision. |
| `GET /homes/{authorization}` | Own manage; 200 historical/current home observation with its separate active flag. |
| `DELETE /homes/{authorization}` | Own manage; 204 after disabling this original role. |
| `POST /uploads` | Own manage, current submit role and original source dependencies; 201 source custody, 200 identical retained custody, 409 changed original. |
| `GET /uploads/{id}` | Own manage and current linked source Device select this account/Device namespace; 200 local factual observation, not payload release. |
| `DELETE /uploads/{id}` | Same actual owner; 204 stop future source-controlled work, preserving possible release/facts. Lost Device recovery uses actual owner reset, not a forged Device claim. |
| `POST /ingress` | Credential-free configured peer; exact Forward, current target ingress and original bounds; 201 destination custody, 200 identical retained original, 409 authorized changed collision. |
| `POST /ingress/status` | Credential-free exact signed query/current admitted issuer and metadata policy; 200 bounded observation only. |
| `POST /inbox` | Own manage and current read role; 200 account-private InboxPage. |
| `GET /inbox/{custody}` | Current own read role for the actual account/Device; 200 exact original packet as application/octet-stream, not a naked MLS object. No charset/newline transformation. |
| `PUT /inbox/{custody}/acceptance` | Same own read authority, enabled privacy policy and exact actual Device acceptance; 201 commit, 200 identical retry, 409 different valid record. |

For `GET /inbox/{custody}`, the authenticated actual account and custody id select
the retained recipient principal and Device. The service selects an installed
READ role in that same account and current credential family whose principal and
Device match the retained recipient, and verifies its current Receive authority.
No additional role header, query parameter or GET body is used. A renewed role may
authorize this read without changing the original upload or custody receipt.
If multiple roles match, selection MUST be deterministic. Each selected role must
pass the complete current checks; a failed role cannot be treated as accepted
evidence for another. No eligible role gives 404; unavailable current evidence
gives 503. The chosen role and retained packet remain dependencies of each bounded
physical response action. Their selection alone is not later output permission.

Account/link/reset routes retain their exact inherited methods and scopes under
this data prefix. No management credential is sent to a peer path. Any Authorization
or cookie on peer routes is a closed 400; it never retries management admission.
Own authentication precedes full record/proof processing after bounded common
framing/media/size checks. Decoded overflow under authenticated owning authority
is 413, not owner exhaustion 429.

Successful record/page/error representations are application/json, no-store; fetch
is application/octet-stream. Unsupported methods return 405 with exact Allow and
no body. Other errors are exactly one `error` member:

| Status | Value and meaning |
| --- | --- |
| 400 | invalid: malformed record/proof; no echoed details. |
| 401 | unauthorized: absent/invalid actual own native credential. |
| 403 | unauthorized: actual valid own credential lacks required scope. |
| 404 | notFound: unknown/foreign/ineligible object or namespace, without account detail. |
| 409 | conflict: different valid original in the qualified immutable namespace. |
| 413 | tooLarge: representation/decoded size overflow. |
| 415 | unsupportedRepresentation. |
| 429 | rateLimited, with positive permitted Retry-After seconds. |
| 503 | unavailable: current time/authority/storage/source evidence unavailable. |

An actually expired own native credential is 401. Expired/unavailable current
issuer/delegation evidence for an otherwise known trusted actor is 503 before
resource lookup. Definite expired/withdrawn content admission is uniform 404,
while a metadata query naming old facts follows its separate current query rules.
A historical receipt is not rejected merely because its past commit interval ended.
A local inner hold is not automatically an actual native 401. Authentication,
namespace, body mutation and physical response release retain distinct owners.
After commit or possible output, failure withholds bytes and preserves uncertainty;
it cannot turn an uncertain effect into a fresh negative or synthetic success.
:::

::: {.details summary="Source release, custody, offline retrieval and retention"}

### Source release, custody, offline retrieval and retention

Freeze the upload and exact prepared delivery before I/O. Existing canonical
Store/witness/native state and worker ownership govern client content release.
The source service separately checks actual data family/role/resource state,
accepted peer/origin/route/key policy and current original bounds under its own
serialized owner before each bounded physical action. Do not put permission or
state mutations in clock callbacks. Waits/connect/handshake/reads/session cleanup
stay outside writers and shared host locks.

Source custody commits exact sealed bytes and retrieval/retention facts before its
receipt. It never promises target acceptance. Source receipt and eligible peer work
have separate ownership; an uncertain final response write cannot undo custody or
necessarily prevent eligible egress. Prefer attempting that response before target
network waits. Every attempt retains finite original bounds; later explicit retry
or independently eligible service work is not a fresh packet or encryption.

The peer release is private source-owned work, not returned with source custody.
It records a current local release authorization, not continuous key possession
or a global cutoff. A source-signed release plus admitted source-origin policy and
current own target ingress is sufficient for data admission; do not import
rendezvous's fresh-source-query requirement per content packet. Source logout or
cancellation blocks future output when installed locally; already released complete
bytes may arrive before their original admission deadline. Copied authorized
forwards only replay identical bounded bytes. End-to-end sender/cohort/current
native checks remain independent. A compromised source can lie about its own act;
querying it again supplies no independent honesty proof.

Offline app custody is allowed while the target's delegated receiving role remains
eligible. Fetch requires current own read authority; original expired ingress is
not a fresh upload grant. Already retrieved/accepted messages follow the existing
application/history owner. Retention expiry, an explicit recipient-owned deletion,
or current read-policy loss can stop future retrieval without disclosing its cause
to the sender. Stopping a data upload does not delete recipient mail. Rendezvous
cancellation changes its own connection work, not independently authorized data
work; data-role withdrawal and packet stop have their separate owning effects.

Keep payloads until retainUntil subject to that explicit recipient deletion/read
policy. Retain compact original receipt/digest/conflict tombstones for the actual
account incarnation; never create a permanent global identifier ledger. Retirement
preserves its owned uncertainty and disables new operations. Account reassignment
cannot read the previous owner's history. A missing/restored index is unavailable,
not authenticated absence or permission to forget a collision. Local capacity is
adjustable admission policy, not silent eviction or a new protocol quota.

Status reconciles facts only. When current query authority expires or a response
is lost, retain uncertainty and already verified originals. Never resend content
to learn whether it arrived, reuse a historical signature as a new grant, or rebind
old work to a new account/key/profile. Current allowed exact retry is a new local
attempt against the same immutable original. It cannot renew the preparation,
receiving window or authored event.
:::

## Optional provider mailbox stitching

A companion retains SMTP history and uses ordinary native/application dedup. An
actual mailbox-owning provider can additionally select `mailbox-stitch-v0` to
append fast and SMTP physical provenance to one mailbox item. This optional module
belongs to this same specification; it is not another Email/2 edition or content
profile. It does not authorize a sender to cancel its SMTP obligation.

::: {.details summary="Mailbox ownership, preauthorization and exact matching"}

### Mailbox ownership, preauthorization and exact matching

Advertising/using mailbox-stitch mode requires an actual authorized mailbox backend
and current mapping from the installed data account to that provider-owned recipient
account/incarnation and selected mailbox subject. Native delivery login, Device
signature, registrar mailbox-control proof, a domain name, data custody or an email
address alone establishes none of this. An independent companion receives no
silent IMAP/JMAP password, session or permission. A provider/plugin needs its actual
owned backend authority; an unauthorized remote adapter cannot claim this mode.

Before suppressing a new mailbox insertion, validate and retain an eligible source
release, exact upload packet/native/carriage commitments, current target data
permission and actual mailbox integration binding. These authorize this one
recipient namespace. Incoming To, Message-ID, an address hash or a received flag
cannot create a stitch reservation. SMTP-first digest indexes are untrusted lookup
hints until this data authorization is verified.

The exact key is the tuple below; it is written only by that authorized decision.

| Component | Binding |
| --- | --- |
| Mailbox authority | Actual provider/backend authority, independently selected. |
| Recipient scope | Actual mailbox account incarnation and selected mailbox subject, derived from its owner, not an incoming address. |
| Carriage | Exactly the selected current opaque-mail carriage profile. |
| Native digest | SHA256 of the complete decoded original MLSMessage bytes. |

Retain the native length and actual bytes and compare them on every key match.
Hashes alone cannot excuse missing/different stored bytes. Store data-home,
source-release, original upload, ownership and policy-generation references as
its authorization evidence; rotating a link/role does not create a fresh duplicate
namespace. Different accounts/subjects never merge merely because they share a
principal, backend login or alias spelling. Folder UID/UIDVALIDITY changes are
locators, not account reassignment or permission to clear collision evidence.

The full packet hash and native hash have different jobs. A data custody receipt
commits every byte of that upload's full original mail. SMTP-added trace fields or
permitted base64 refolding can change that full-mail hash while preserving exact
native bytes and the selected carrier. Those arrivals may stitch only after the
prior data authorization and actual recipient scope above are established. Different
ciphertext never matches, even if its outer Message-ID or later authored identity
is the same. Malformed/truncated/ambiguous MIME, trailing native objects and prefix
hashes cannot reserve a key or suppress delivery. Their ordinary mail disposition
remains with the actual mailbox policy, not this dedup path.
:::

::: {.details summary="One atomic mailbox effect and unchanged user state"}

### One atomic mailbox effect and unchanged user state

Under the actual mailbox owner's serialized transaction/commit boundary, perform:

1. Recheck the data authorization for fast ingress and actual mailbox binding.
   Normal SMTP arrival retains its own mailbox authority; an already authorized
   stitch record is historical match evidence, not a new data grant.
2. Select the exact qualified key and byte equality. If absent, create one mailbox
   item and authorized key together. If SMTP came first, attach to its uniquely
   matching retained original only after verifying the prior data authorization.
3. Durably retain the full arriving original and its actual physical provenance,
   including account, carrier path, body digest and source/custody or SMTP receipt
   references. Preserve all earlier originals without rewriting their headers,
   folding, timestamps or bodies.
4. Commit the item/key/source facts and declared custody/history receipt obligation
   atomically before returning positive destination custody or SMTP acceptance.
   Storage/body durability is not inferred from a successful parser or index write.

Concurrent fast/SMTP arrivals serialize into the same item. A backend that cannot
atomically own that effect, or safely recover its exact durable result, must not
claim stitching success. A separate sidecar best-effort update is insufficient.
Temporary failure retains uncertainty and returns its actual refusal; do not
silently report the companion baseline under a different declared mode.

If several unclaimed SMTP items match before an authorized key exists, do not pick
an ordinal, delete one or overwrite state. Retain the new original/custody and the
ambiguity without suppressing an independently required history item. Any repair
needs the actual mailbox owner's explicit merge rules; this module does not claim
to heal arbitrary historical duplicates.

Appending provenance does not generate another UID/item, arrival/unread event or
application effect. Preserve the existing item's seen/read, flags, labels, moves,
thread placement and user deletion state. Native/application acceptance is not a
Seen change. A deleted-item tombstone prevents the same authorized native object
from resurrecting an item; retain the additional physical fact without exposing a
recipient deletion reason. A new different ciphertext cannot use that tombstone
to disappear. Explicit recipient retention/deletion remains its separate authority.

Actual endpoint native/app dedup still runs. A mailbox provider comparing sealed
bytes has not verified native sender, protected audience, application scope or
reading. The recipient retains fast/SMTP transport provenance alongside its one
actual native consume and accepted/held/rejected outcome. No mailbox index can
supply those cryptographic/app facts.
:::

::: {.details summary="Required stitching acceptance cases"}

### Required stitching acceptance cases

Evidence must use the actual authorized mailbox backend plus real SMTP and fast
service ingress. Require fast-first, SMTP-first, simultaneous arrival, lost reply,
process restart and restored-state refusal. Added Received/Return-Path trace and
legal base64 refolding must preserve one item with both complete originals. A
malformed frame or a distinct authenticated ciphertext sharing Message-ID must not
suppress a new item. Foreign accounts/subjects, uninstalled/withdrawn role, absent
mailbox authority, wrong packet/native digest, ambiguous prior items, partial
storage/index failure and account reassignment must not reserve or reuse a key.

Verify no overwrite, Seen reset, relabel, deletion resurrection, second native
consume or duplicate application effect. A real recipient must reconstruct the
human contribution through its actual Store/MLS/admission owner. Endpoint-only
MIME/native dedup evidence does not establish service mailbox atomicity or actual
fast-transport provenance. An integrated provider must qualify both.
:::

## Privacy and implementation status

The complete selected packet may expose unmasked outer routing addresses, length,
timing and stable packet/native digests to the homes. Body, protected subject,
resources and intended scope remain inside MLS. URLs contain no personal address.
Masking needs its actual separately authorized route/privacy owner and compatible
carrier; the first direct-account demonstration cannot advertise masked fast
support. No roster, address search, public presence or automatic read indicator is
introduced. Endpoint-acceptance sharing stays off until explicitly enabled.

Before advertising the proposed data profile, qualify actual independent services
and Devices: genuine separate native setup/role, source and target custody, offline
retrieval, native/setup before human content, exact retry/status/restart, changed
collision, source revoke before output and in-flight arrival after source logout,
target withdrawal, expiry, malformed/partial body, wrong key/origin/scope/account,
restore, receipt immutability/privacy and later mailbox dedup. Independent
interoperability, OS key custody and security review remain separate evidence.

