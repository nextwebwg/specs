---
title: Discovery realms
order: 10.16
blurb: proposed bounded discovery reference
sectionNav: true
---

# Discovery realms

A **realm** is a shared directory that helps an app find someone's chosen Email/2 service before sending a message. Alice and Bob can keep their existing mailboxes and use different companion services. Their apps need a realm they already know how to trust; an email address alone cannot reveal an independent companion.

This chapter proposes `mail-realm-v0`, a bounded reference binding within the Email/2 draft. It defines directory configuration, publication and withdrawal. [Private snapshot lookup](private-snapshot.md) defines acquisition, and [installation access](realm-access.md) defines background admission to the services. These new records do not add fields to existing provider, registrar or rendezvous descriptors.

## What happens for Alice and Bob

1. **Bob connects once.** An admitted registrar verifies control of his own mailbox. His authorized device publishes the original proof, its current public identity, static setup and signed service locations.
2. **Alice adds Bob as a recipient.** Her app looks up that selected address through a realm configured for her account.

It does not upload her address book, crawl other directories or send an encryption probe into Bob's inbox.
3. **Her app checks the evidence.** It retrieves the complete bounded setup, validates each original proof and applies its existing identity and mailbox-association rules.
4. **Setup continues under its own rules.** A directory result is a candidate, not permission to send. A separately authorized allocator must supply any one-use package needed for encryption.

> [!warn] What the directory does and does not protect
> The registrar and authoritative index learn enrollment information. The encrypted public snapshot hides the selected lookup from its evaluator under the reference construction's assumptions, but theft of both that snapshot and the evaluator secret enables guessing and decryption of guessed entries. Signatures do not prove that a malicious index included everyone or announced its newest snapshot.
>
> A missing or failed result means **unknown**. It never proves that an address cannot encrypt, replaces a remembered identity, silently downgrades a message or triggers unsolicited setup email.

## Authority and implementation boundaries

A realm is not the authority for Bob's mailbox domain or personal identity. Its index orders publications; the original registrar and device proofs establish their own narrower claims. Mailbox control remains distinct from [independent correspondent verification](mailbox-association.md#independent-verification-remains-separate).

[Independent mailbox registration](mailbox-registration.md) defines the proposed registrar descriptor and registration records used below. Its native-module metadata, reset wire selection and independently eligible home-authorization prerequisites remain incomplete. The rendezvous, offline-allocation and live-locator records referenced below also require their complete owning bindings. Existing [provider discovery](provider-discovery.md) does not supply them. Until those bindings and the joined Store acceptance path are complete, these chapters cannot establish interoperable or native-ready discovery. The exact record names below identify those prerequisites; they are not permission to invent a generic descriptor or reuse an old parser.

:::: {.details summary="Configure the realm before lookup"}

### Strict types and initial trust

New profile is `mail-realm-v0`; private acquisition is separately selected as `mail-private-snapshot-v0`. These records do not extend any retained provider/registrar/rendezvous descriptor. Strict UTF-8 JSON rejects duplicate/missing/unknown members, null, JSON numbers/booleans and trailing data. Uint values/times are canonical unsigned-64 decimal strings, times Unix seconds. ObjectId is nonzero random 16-byte lowercase hex; digest/nonce/Ed25519 key is32-byte lowercase hex. Complete credible time must fit every original interval, with checked arithmetic. Missing credible time holds new effects.

Signed wrapper is exactly `{payload,signature}`, canonical padded base64 original UTF-8 payload bytes and 128-lowercase-hex Ed25519 signature. Sign ASCII purpose domain, NUL, U32BE original payload length, original bytes. Verify original bytes, never a reserialized object. Every digest below hashes the named original decoded payload bytes with SHA256, except explicit snapshot-file hashes. Encoded original objects use canonical padded base64. Existing original child wrappers/signature inputs remain unchanged.

Own application/account/enterprise configuration pins exactly `{realm,configurationOrigin,bootstrapDigest,configurationKey}` before a recipient lookup. realm is an ObjectId; origin is canonical HTTPS. BootstrapDigest pins the original initial configuration payload, signed by the pinned key. An incoming email, locator, redirect, failed lookup or other realm cannot install these values.

Two independently configured realms require separately authorized shared publication or an already accepted locator; no address broadcasting or implicit trust graph is defined here. Replacing the pin is an explicit local configuration operation, not a network update. Presets may make routine use automatic; no per-contact ceremony is introduced.

### Exact configuration chain

Configuration payload has the following exact required members:

| Member | Contract |
| --- | --- |
| `profile` | Exact profile string selected for this record. |
| `purpose` | Exact purpose string stated below. |
| `realm` | Configured realm ObjectId. |
| `configuration` | Stable configuration ObjectId. |
| `generation` | Canonical uint64 string; lineage rules below apply. |
| `predecessor` | Original predecessor payload digest, or the explicitly allowed empty string. |
| `configurationKey` | Ed25519 configuration-signing key. |
| `nextConfigurationKey` | Authorized next Ed25519 key, or the explicitly allowed empty string. |
| `index` | Exact index role object defined below. |
| `registrars` | Sorted admitted-registrar array defined below. |
| `retrieval` | Exact private-acquisition role object defined below. |
| `access` | Exact per-origin access array defined in installation access. |
| `limits` | Exact finite bound object defined below. |
| `notBefore` | Canonical uint64 Unix-seconds string. |
| `notAfter` | Canonical uint64 Unix-seconds string. |

Its purpose is `realm-configuration`. configuration ObjectId remains stable across its chain, initial generation 0/predecessor empty, successors increment 1 and predecessor hashes the exact prior configuration payload. configurationKey is the signer, initially pinned; successor uses the parent's nonempty nextConfigurationKey or unchanged parent configurationKey when nextConfigurationKey is empty. No other key is accepted. A transition does not reset realm/configuration/epoch/index/publication high-water.

New key possession is demonstrated by its actual next configuration signature. Compromise of the current root permits malicious root updates; this is not threshold governance or independent transparency.

Index is exactly `{service,prefix,key}`: canonical HTTPS origin, canonical same-origin federation path prefix and Ed25519 mutation-receipt key. Registrars is a unique origin-sorted array of `{registrar,descriptor,method}`. Descriptor is original complete `mail-association-service-v0` descriptor bytes, not a URL to fetch; registrar equals its service origin and method exactly mailbox-delivery. Its original key/interval and the realm admission must both be eligible. The descriptor's own signature/self-description cannot admit itself. A later configuration can stop admitting an issuer without rewriting its old proofs.

Retrieval is exactly `{profile,evaluator,mirrors,checkpointKey}`, profile mail-private-snapshot-v0; evaluator exactly `{service,prefix}`, mirrors unique origin/prefix-sorted array of `{service,prefix}`, checkpointKey Ed25519. The required access array selects the exact new issuer/scopes/policy/operation carriage in [installation admission](realm-access.md). These are explicit new role mappings; legacy `/.well-known/mail-provider` bytes acquire no directory fields.

Every role `prefix` is a full canonical absolute HTTPS URL at its exact `service` origin, ending in `/`, using the [existing service-prefix grammar](provider-discovery.md). For example, service `https://directory.example` can select prefix `https://directory.example/mail/index/`; path-only `/mail/index/` is invalid. Logical route tables show suffixes with a leading `/` for readability. Append the suffix without that leading slash to the configured prefix; never replace the prefix path through root-relative URL resolution. Reject overlapping role/access prefixes at the same origin by segment containment.

Services/prefixes use existing canonical HTTPS spelling, TLS 1.3/no redirect/no 0-RTT/no ambient credential forwarding and actual resolved-address egress checks. Configuration, index, evaluator and mirror roles may share an operator, but different process names do not establish noncollusion.

Limits has the following exact required members:

| Member | Contract |
| --- | --- |
| `maxConfigurationBytes` | Positive canonical uint64 string. Maximum decoded original configuration payload bytes. |
| `maxChainEntries` | Positive canonical uint64 string. Maximum entries in either complete chain response. |
| `maxMutationBytes` | Positive canonical uint64 string. Maximum complete original HTTP mutation bytes. |
| `maxBundleBytes` | Positive canonical uint64 string. Maximum decoded original bundle bytes. |
| `maxCellBytes` | Positive canonical uint64 string. Fixed encrypted cell plaintext bytes; must exceed 4. |
| `maxDevicesPerMailbox` | Positive canonical uint64 string. Maximum admitted devices represented for one mailbox. |
| `maxPublicationHistory` | Positive canonical uint64 string. Maximum retained publication history represented in a cell. |
| `maxDepth` | Positive canonical uint64 string. Maximum strict-object nesting depth, checked before unbounded allocation. |
| `slots` | Configured canonical uint64 slot-count string. |
| `snapshotBytes` | Exact canonical uint64 snapshot-length string. |
| `maxCheckpointAgeSeconds` | Positive canonical uint64 string. Maximum current-checkpoint age in seconds. |
| `epochLifetimeSeconds` | Positive canonical uint64 string. Maximum epoch interval in seconds. |
| `pollSeconds` | Positive canonical uint64 string. Minimum interval between polls. |
| `retentionSeconds` | Positive canonical uint64 string. Configured retention; cannot shorten existing safety obligations. |

All bounds are positive strings; `maxCellBytes` must be greater than 4. They are explicit adjustable finite reference/deployment bounds, not user quotas.

Geometry must obey snapshotBytes =57 + slots*(60 + maxCellBytes), using the binary header defined in the private profile, and fit local allocation/network ceilings. maxConfigurationBytes bounds each decoded original configuration payload; maxChainEntries bounds both complete chain responses; maxMutationBytes bounds original complete HTTP mutation bytes; maxBundleBytes bounds decoded original bundle; maxDepth applies at every nested strict object before unbounded allocation. A configuration exceeding local capacity is held before allocation.

Resource-overflow arithmetic is rejected, never saturated. No implicit download of an oversized setup or recipient-specific spillover URL is allowed.

At `configurationOrigin`, use GET `/mail-realm/configuration` with no query/body. HTTP 200 exactly `{profile,chain}`, chain the complete original signed configuration wrappers from pinned bootstrap to the advertised current head. This account-global response is identical regardless of selected recipient. Client verifies bounded chain, exact predecessor/key transitions and retained high-water before committing it.

Historical chain signatures/declared authorization transitions remain historical evidence; the selected current head must cover the complete current credible clock.

Sample the actual current credible clock after original-chain verification and again under the owning acceptance lock before commit or use. A time snapshot passed in before verification or lock waiting cannot authorize a later effect. Retain the observed credible lower bound as the clock floor, not its possible future upper bound. Overlapping intervals such as `[10,12]` followed by `[11,13]` are not rollback; a new lower bound below the retained floor holds the operation. The complete current interval must still fit the selected head.

Expired historical configurations are not silently promoted to current authority, nor discarded merely because their signatures authenticate retained history. Equal generation unequal bytes is conflict; rollback or missing retained ancestor holds.

If the complete chain no longer fits this bounded reference, hold pending a separately authorized configuration procedure rather than silently trusting a new root. An honest current-head service returns its current chain; an old still-valid response can be withheld/replayed by a malicious authority within the stated freshness limits.

Only configurations admitted in that pinned history can authenticate original records. New uses also require the current configuration to continue admitting the exact issuer/service role and original evidence not expired/withdrawn. Removed keys or origins do not move automatically to replacements. Configuration expiry/root change cannot reset an original send/setup deadline or a remembered identity pin.

::::

:::: {.details summary="Publish all static setup with its original proofs"}

### One independently authorized device publication

A directory publication payload has the following exact required members:

| Member | Contract |
| --- | --- |
| `profile` | Exact profile string selected for this record. |
| `purpose` | Exact purpose string stated below. |
| `realm` | Configured realm ObjectId. |
| `configurationDigest` | SHA256 of the original selected configuration payload. |
| `publication` | Directory publication ObjectId. |
| `generation` | Canonical uint64 string; lineage rules below apply. |
| `predecessor` | Original predecessor payload digest, or the explicitly allowed empty string. |
| `mailbox` | Exact canonical mailbox spelling. |
| `device` | Exact authorized device identity. |
| `associationDigest` | SHA256 of the original registrar attestation payload. |
| `bundleDigest` | SHA256 of the original complete bundle bytes. |
| `notBefore` | Canonical uint64 Unix-seconds string. |
| `notAfter` | Canonical uint64 Unix-seconds string. |

Its purpose is `directory-publication`. It is signed by that exact accepted device. Initial generation 0/predecessor empty; successors increment 1 and name the exact previous directory-publication payload digest. Publication identity is `(realm,publication)` and cannot change mailbox/principal/device/binding/key. New devices require their own registration/publication; mailbox address equality uses canonical mailbox-addresses rules, including exact Unicode/local spelling. No lowercasing, alias inference, plus stripping or predictable address hash substitutes.

The strict JSON bundle has the following exact required members:

| Member | Contract |
| --- | --- |
| `profile` | Exact profile string selected for this record. |
| `purpose` | Exact purpose string stated below. |
| `association` | Original complete registration publication, base64 encoded. |
| `identity` | Original complete current identity inventory, base64 encoded. |
| `assertions` | Nonempty sorted array of original assertion wrappers. |
| `services` | Sorted array of exact service-role objects. |

Its purpose is `directory-static-setup`; profile mail-realm-v0. The full bundle is carried as original base64 bytes and bundleDigest hashes those original bytes.

- association is base64 of the original complete registration publication `{attestation,challenge,proof,identity,home}`. It retains all original registrar/device proof bytes but no consumed secret. associationDigest hashes the original attestation payload inside it. Validate its registrar/method/realm admission/mailbox/device/home/digests and all original intervals under the [independent registration owner](mailbox-registration.md).
- identity is base64 of the complete current owning identity inventory. Preserve the registration's original inventory too; current accepted ancestry must connect its unchanged device/key/binding anchor to this inventory, with Receive authority, no fork/restore/role barrier. A directory signature cannot repair native evidence or prove absence of withheld revocations.
- assertions is a nonempty array of base64 original complete assertion10 wrappers, sorted by original payload digest, no duplicates. Each uses the selected exact mailbox/principal/device/binding/current accepted ancestry and original valid applications/control key. Static wrappers MUST have `keyPackage:[]` and `keyPackageReceiveUntil:null`; no native one-use package bytes enter this snapshot. Validate original native/device signatures and actual public control descriptor under the existing owner; a structural zero proof or made-up control key is not complete setup. Do not rewrite a package-bearing wrapper to remove its package.
- services is a role-sorted unique array of `{role,descriptor,authorization,locator}`; all three object values are base64 original strict bytes, locator empty only where defined below. Allowed role set is exactly rendezvous, package-allocation and live-transport. rendezvous is required and exactly matches the registration's original signed home and its descriptor; locator empty. package-allocation carries its exact new descriptor and device-signed allocator authorization, associationDigest bound to this original registrar attestation, and locator empty. live-transport carries its exact descriptor/home and original signed same-device live-locator linking the original rendezvous home/association to it. Unknown roles or a generic future service bag are rejected in this profile. Each optional role uses its complete owning candidate schema, independently selected; absence means no evidence for that role, never unsupported encryption globally.

For this complete offline-setup reference, package-allocation is also required: it supplies the authorized offline pool location while the static assertion supplies capabilities/control. This describes the complete static acquisition boundary. It does not assert that a pool has a package left or allocate/consume one. An application needing a one-use package must continue through the exact stateful allocation owner, with its metadata/privacy limits and current identity/attempt constraints. Original package/private init/message keys, account tokens and mailbox credentials are excluded.

Whole publication interval fits association/assertions/home/allocator/device/config admission intervals. The binding cannot silently shorten an already committed receiver promise; unsuitable evidence is rejected/held. Services and bundle bytes are preserved; a URL pointing to more setup is not a complete bundle. Existing application negotiation/current Store checks remain necessary before preparing a message.

### Mutation transport and ordering

Publication is authorized by the original admitted registrar evidence plus the exact device signature; an index-specific account login is not needed to invent mailbox authority. The app can submit the immutable mutation through the exact installation-admission outer operation, or its independently admitted chosen service can forward it only under its own equivalent current installation admission. No inbound HTTP header bypasses the [access binding](realm-access.md). Admission tokens/API keys prove only permitted resource use, not mailbox control, identity or publication truth. No mailbox/OAuth secret crosses to the index.

The logical configured-index handler is POST `/mutations`, application/json body exactly `{record,bundle,evidence}`. record is an original signed directory-publication, directory-withdrawal or directory-migration wrapper. bundle is base64 complete static bundle for publish/migration destination, or empty for withdrawal. evidence is exactly the tagged form for that purpose below. The service validates size/strictness/signatures/current admitted issuer/accepted identity before authoritatively occupying the collision key.

The publication update transaction uses expected generation/predecessor CAS, immutable source bytes and the index's retained current registrar/identity safety state. Replayed older association cannot bypass its retained withdrawal/tombstone or create another publication alias for that same revoked assurance.

Publish evidence exactly `{kind:"publication"}`; the complete association is already in the signed bundle. Source/current interval is rechecked at commit. First valid commit retains the original record/bundle, advances one global indexSequence and stores a signed receipt; equal original retry returns that receipt without another sequence/version. Unequal authenticated same publication/generation conflicts 409; invalid input cannot burn it. A later generation without exact retained predecessor conflicts 409.

A directory lineage closed by withdrawal/migration never accepts a positive successor; a separately authorized new registration/publication retains the old safety history and cannot restore revoked association evidence. Multiple valid eligible distinct principals for one address are retained as ambiguity, never newest-wins. Valid device/identity revocations stop new positive use under their own evidence owner; an index receipt cannot replace that owner.

Receipt payload has the following exact required members:

| Member | Contract |
| --- | --- |
| `profile` | Exact profile string selected for this record. |
| `purpose` | Exact purpose string stated below. |
| `realm` | Configured realm ObjectId. |
| `configurationDigest` | SHA256 of the original selected configuration payload. |
| `mutationDigest` | SHA256 of the original mutation payload. |
| `publication` | Directory publication ObjectId. |
| `generation` | Canonical uint64 string; lineage rules below apply. |
| `indexSequence` | Monotonic global uint64 string. |
| `headDigest` | SHA256 of the original mutation payload. |
| `notBefore` | Canonical uint64 Unix-seconds string. |
| `notAfter` | Canonical uint64 Unix-seconds string. |

Its purpose is `directory-committed`;  signed by selected index key. MutationDigest/headDigest hash the original mutation payload (not HTTP body or bundle); publication/generation bind its affected directory lineage. IndexSequence is monotonic global uint64, never reset by configuration/epoch rotation. Receipt201 first or200 equal retry body exactly `{profile,receipt}`. It proves index commit, not inclusion in an already issued snapshot or encryption readiness.

A later snapshot checkpoint with indexSequence at least this sequence is required before an honest index claims this update is visible. Lost response retains uncertainty; exact original retry recovers it and never sends another mailbox challenge. No separate recipient-status GET exists.

Index configuration may rotate index key only through authenticated root history. Retain old receipt evidence/sequence; older key cannot issue fresh commits after its current admission closes. Index validation and native identity/currentness remain bounded by actually received authenticated evidence, not omniscient revocation. The trusted index must process received valid withdrawals before subsequent positive mutations and snapshot builds in one serialized order.

::::

:::: {.details summary="Withdrawal, reassignment, migration and capacity"}

Withdrawal payload has the following exact required members:

| Member | Contract |
| --- | --- |
| `profile` | Exact profile string selected for this record. |
| `purpose` | Exact purpose string stated below. |
| `realm` | Configured realm ObjectId. |
| `configurationDigest` | SHA256 of the original selected configuration payload. |
| `publication` | Directory publication ObjectId. |
| `generation` | Canonical uint64 string; lineage rules below apply. |
| `predecessor` | Original predecessor payload digest, or the explicitly allowed empty string. |
| `mailbox` | Exact canonical mailbox spelling. |
| `associationDigest` | SHA256 of the original registrar attestation payload. |
| `actor` | Exact tagged actor object defined below. |
| `reason` | One of the exact reasons listed below. |
| `notBefore` | Canonical uint64 Unix-seconds string. |
| `notAfter` | Canonical uint64 Unix-seconds string. |

Its purpose is `directory-withdrawal`. actor is `{kind:"device",device}` or `{kind:"registrar",registrar,key}`. Device is the unchanged original accepted device and signs mail/directory/withdrawal/v0; registrar is the admitted issuer of the original mailbox association and signs mail/directory/registrar-withdrawal/v0. Reasons withdrawn, account-reset, mailbox-reassigned or migrated. Both can retract this exact publication's positive use; neither can install another principal or withdraw a foreign registrar's proof. Generation advances1 from the exact directory head under CAS.

A registrar need not know every independently uploaded directory publication ID or its latest directory generation to retract its own assurance. The logical index POST `/association-withdrawals` has exactly `{profile,configurationDigest,association,source}`. association is base64 original complete registration publication; source its original signed registrar withdrawal wrapper. Verify the exact original registrar key/realm admission, association/publication/mailbox/predecessor rules and source signature.

Existing valid historical issuer authority may supply deny-only evidence even after expiry; it supplies no new positive identity/key authority. Derive all affected directory lineages from retained state, never from a caller mailbox list. Atomically retain the original source tombstone, association-level high-water/deny state and one global sequence before processing any later positive update. An original signed registrar safety stop does not need a device signature.

Source replay returns the original result; unequal authenticated same source generation conflicts, invalid input cannot occupy it. Response201 first/200 exact is `{profile,receipt}`; receipt payload has the following exact required members:

| Member | Contract |
| --- | --- |
| `profile` | Exact profile string selected for this record. |
| `purpose` | Exact purpose string stated below. |
| `realm` | Configured realm ObjectId. |
| `configurationDigest` | SHA256 of the original selected configuration payload. |
| `associationDigest` | SHA256 of the original registrar attestation payload. |
| `sourceDigest` | SHA256 of the original registrar withdrawal payload. |
| `indexSequence` | Monotonic global uint64 string. |
| `notBefore` | Canonical uint64 Unix-seconds string. |
| `notAfter` | Canonical uint64 Unix-seconds string. |

Its purpose is `association-safety-committed`; index signature domain mail/directory/association-safety/v0. associationDigest hashes original attestation, sourceDigest original source withdrawal payload. This receipt asserts ordering only. Later snapshots include the original source proof in an association-withdrawn cell entry and exclude affected positives. It never fabricates a registrar-signed directory tombstone.

Withdrawal evidence exactly `{kind:"withdrawal",association,source}`: association original complete registration publication bytes, source base64 original signed registrar mailbox-association-withdrawal or empty for a current device's own withdrawal. A registrar actor requires its actual source tombstone, exact association/mailbox/current generation, admitted original registrar key and source reason. If device private state is lost, registrar withdrawal can still stop its own assurance.

Index also maintains association-level denial/high-water from that original source tombstone, so a copied old attestation cannot republish under a fresh directory ID. Directory withdrawal never rewrites the registrar's signed generation or resets contact pins.

Migration first creates an independently authorized destination registration/bundle/publication preserving the same accepted principal. The source device signs a payload with the following exact required members:

| Member | Contract |
| --- | --- |
| `profile` | Exact profile string selected for this record. |
| `purpose` | Exact purpose string stated below. |
| `realm` | Configured realm ObjectId. |
| `configurationDigest` | SHA256 of the original selected configuration payload. |
| `publication` | Directory publication ObjectId. |
| `generation` | Canonical uint64 string; lineage rules below apply. |
| `predecessor` | Original predecessor payload digest, or the explicitly allowed empty string. |
| `mailbox` | Exact canonical mailbox spelling. |
| `device` | Exact authorized device identity. |
| `sourceAssociationDigest` | Original source association digest. |
| `destinationPublication` | Independently authorized destination publication ID. |
| `destinationDigest` | SHA256 of the original destination publication payload. |
| `destinationBundleDigest` | SHA256 of the original destination bundle. |
| `notBefore` | Canonical uint64 Unix-seconds string. |
| `notAfter` | Canonical uint64 Unix-seconds string. |

Its purpose is `directory-migration`; domain mail/directory/migration/v0. destinationDigest hashes original destination directory-publication payload. Evidence exactly `{kind:"migration",destination,associationMigration}`, destination original signed destination publication, associationMigration base64 complete original registration-owner migration result including its signed handover and source withdrawal. The submitted bundle is the original destination bundle; its bytes/digests and principal/device/home bindings are checked.

The index retains destination commit first, then CAS-marks the source lineage migrated with its exact handover evidence and one new sequence/receipt. Within one index this is transactional; different realm publication is not globally atomic and requires separately configured trust, not automatic following. Old home/grants/allocator packages never transfer. Lost response preserves both old uncertainty and destination evidence; retry original bytes only. Different principal is reassignment/continuity break, not migration.

Snapshots retain per-mailbox complete current publication entries plus necessary directory predecessor chains and original proofs, within maxDevicesPerMailbox/maxPublicationHistory/maxCellBytes. A known client never accepts an active head across a missing required predecessor as if continuity were proved; full cell/history must provide its required original path. No unique follow-up GET obtains missing history.

If a new positive version cannot fit the reference geometry/history, reject/hold new positive publication before commit rather than truncate setup or lie about completeness. An old version can remain only within its original eligible interval.

Safety withdrawals must remain representable: reserve the bounded latest tombstone slot for each admitted lineage when admitting its positive record. A withdrawal may replace its positive setup/history cell entry with the original terminal tombstone and registrar source evidence. A valid authenticated tombstone for the same lineage/association can conservatively stop positive use even if the receiver lacks intermediate positive history; it never authorizes a new identity or positive successor.

A new client seeing only tombstones gets no usable result. Reference capacity exhaustion cannot justify retaining a known withdrawn positive result or suppressing a received identity revocation. If full terminal evidence cannot fit an existing geometry, do not publish a new checkpoint containing that unsafe positive entry: hold the epoch, let its original checkpoint expire, and issue a newly configured larger bounded geometry or stop this path. This is a reference availability limit, not a production compaction proof.

Address reassignment requires fresh independent control evidence and new identity history. The index can withdraw its old assurance and publish a distinct valid candidate, but a known correspondent's old pin remains a visible conflict/continuity break. Expiry is not a withdrawal signature and does not erase pins. Retain authoritative association/directory denial and generation high-water at least through every old positive evidence/cache/checkpoint/retry validity obligation; do not erase them to fit a newly advertised shorter retentionSeconds.

Reject new obligations or stop the path when their full safe retention cannot be supported. Device/key/home changes require exact existing identity/delegation rules and new publication evidence; directory generation alone supplies no encryption authority.

::::

## HTTP results and unknown outcomes

The fixed public configuration bootstrap GET and signed acquisition metadata use no-store for signed control metadata; immutable snapshot files may use their exact digest-keyed cache policy. JSON errors exactly `{error}`:400 invalid,401/403 unauthorized resource admission,404 notFound for unknown opaque epoch handles,405 methodNotAllowed with Allow,409 conflict,413 tooLarge,415 unsupportedRepresentation,429 rateLimited with positive decimal-seconds Retry-After,503 unavailable. Error bodies never echo mailbox/bundle/credentials.

No invalid proof can create an authoritative conflict or trigger verification mail. The logical role handlers described here are invoked only through [installation access](realm-access.md)'s deployed signed POST /operations; their direct anonymous HTTP forms are comparative/local-test mode, not additional advertised endpoints.

Signature purposes/domains: realm-configuration → mail/realm/configuration/v0; directory-publication → mail/directory/publication/v0; directory-committed → mail/directory/committed/v0; withdrawal/migration as specified above. Configuration signs authority; registrar/device sign subject/setup; index signs ordering; checkpoint signs immutable dataset. None substitutes for the others. Their exact scopes and failure states remain distinct.
