---
title: Encrypted correspondence archives
order: 9.3
blurb: portable history · recovery material · complete resources · inert restoration
sectionNav: true
---

# Encrypted correspondence archives

An encrypted archive preserves correspondence after a device is lost: original mail, accepted contributions, reply relationships and included resources. The same portable format works with storage managed by the person or by a service. Decrypting a downloaded archive does not require a subscription or a billing-service connection.

An archive restores historical reading, not a live encryption identity. Importing it cannot authorize sending, enroll a device, reinstate a revoked key or replay an answer. Those actions continue to use current identity and conversation authority.

> [!note] Candidate archive profile
> `email2-archive-v0` defines a signed history container protected by an existing file-encryption format. The reference experiment tests container integrity, resource preservation and encryption through an installed age implementation. It does not establish production storage, secure device-key custody, comprehensive parser containment or independently reviewed recovery assurance.

## Create a recovery kit before relying on backup

For a normal backup, the first exporting device creates an archive identifier, an independent archive-encryption identity and an independent archive signing key. The [history-transfer binding](history-transfer.md) instead authenticates a recipient-selected encryption identity while retaining these exact file formats; it never sends the original backup kit. These are not device-binding, account-administration or MLS keys. The signing key is local to this archive's writer; it grants no live account authority.

The recovery kit contains the archive identifier, archive-decryption identity and trusted public archive-signature verification key. Store it separately from the archive and the device being backed up, through an explicitly chosen password manager, offline copy or another independently recoverable destination. Show what possession allows: reading every snapshot encrypted to that identity. Anyone holding the kit can read those archives; mailbox-password reset cannot reconstruct it.

Before reporting recovery setup complete, decrypt and verify a test snapshot using the retained kit through the selected independent destination. This checks the available recovery route at setup time, not that the person will never lose it. A second copy solely on the same device or inside its own locked archive is insufficient.

::: {.details summary="Exact recovery-kit object and selected protection"}

The kit is strict UTF-8 JSON with exactly `version`, `purpose`, `archive`, `ageIdentity` and `verificationKey`. Version is `"0"`; purpose is `"archive-recovery-kit"`; archive uses the nonzero ObjectId grammar. `ageIdentity` is a valid native age X25519 secret identity. `verificationKey` is the 32-byte Ed25519 public key encoded as 64 lowercase hexadecimal characters. Unknown members, duplicate decoded names, nulls and malformed encodings are rejected. A kit is secret material, never a discovery advertisement, email notification, support log or billing record.

The encrypted file selects the binary age v1 format and native X25519 recipient from the pinned [C2SP age v1.1.0 specification](https://c2sp.org/age@v1.1.0). Generate one recipient stanza, for this archive's recovery identity. Additional recipient types, armor, password recipients and service-held decryption recipients are outside this profile. Use an age implementation; do not replace its encryption or final-authentication rules. This selection is not post-quantum protection.

The archive signature binds origin separately: anyone knowing an encryption recipient can encrypt a replacement file. Decryption success alone cannot authenticate the archive's writer. Pin the verification key from the independently retained kit, never from an untrusted archive or storage response.

:::

## Freeze one snapshot

Export from a consistent retained-history view. Do not mix records from before and after a concurrent edit, resource update or account change without reporting that boundary. Freeze the manifest and object bytes before signing. A snapshot identifies the selected accounts, omissions and exact object inventory; it does not claim that the service possesses every message ever sent to those accounts.

For rich and indexed replies, preserve the original event bytes and all available declared resource bytes. Preserve original MIME separately where retained. The event's exact references and authored/quotation boundaries remain in those bytes; no text-only reconstruction replaces them. Source references whose history was not retained remain unresolved after restore.

A missing attachment, unavailable original or incomplete collection is an explicit omission. The export may finish as an incomplete archive, but cannot display a complete-backup result. Local source messages and the last completed archive are not overwritten by a failed export.

## Signed container

The decrypted container is eight ASCII octets `EML2ARC0`, a four-octet unsigned big-endian manifest length, that many UTF-8 manifest octets, the object bytes in manifest order, and a final 64-octet signature. The container has no extraction filenames or paths, archive-level compression, executable directives, alignment bytes, recursive containers or trailing bytes. Original attachment bytes may themselves be compressed or executable file content; they remain opaque historical data and are never activated by import.

The unsigned content is every container octet before the final signature. The signature uses plain Ed25519 over ASCII `email2/archive-content/v0`, one zero octet, and the 32 raw octets of SHA-256 of that unsigned content. This domain-separated content commitment is the message being signed; it is not Ed25519ph. Verification uses the trusted kit key. The existing [Ed25519 rules](audits/ed25519.md) apply.

The manifest follows the event contract's strict JSON/scalar/duplicate-name rules, with a separate maximum of 16,777,216 octets and the same maximum nesting depth of 32. These are archive-profile limits, not mailbox storage quotas. Larger collections can be split into separately identified complete scopes; a partial scope must not masquerade as a whole-mailbox snapshot. A local implementation may impose additional disclosed processing limits and report incomplete processing without truncating or activating partial state. This version defines each artifact's scope. The separate [archive-set profile](archive-sets.md) supplies the signed multi-artifact catalog, frozen record inventory and atomic complete-collection acceptance. A client splitting an export must use that complete-collection contract before claiming that all selected parts were recovered.

::: {.details summary="Manifest, entry and object schemas"}

The manifest has exactly these members:

| Member | Value |
| --- | --- |
| `version` | Exactly `"0"` |
| `purpose` | Exactly `"correspondence-archive"` |
| `archive` | Archive ObjectId matching the trusted kit |
| `snapshot` | Fresh ObjectId for this immutable snapshot; retained on exact retry |
| `sequence` | Canonical uint64 decimal string; starts at `"0"` |
| `previous` | Empty for sequence zero; otherwise the preceding completed encrypted file's SHA-256 as 64 lowercase hexadecimal characters |
| `createdAt` | Canonical uint64 epoch-seconds string, an exporter claim rather than independent time evidence |
| `accounts` | Nonempty array of exact `{id,principal}` objects, sorted by unique account ObjectId; principal is an enp0 identifier or empty for a legacy-only account |
| `coverage` | Exact `{complete,omissions}`; complete is boolean; omissions is an array described below |
| `entries` | Array of entry records sorted by unique entry ObjectId |
| `objects` | Array of exact `{sha256,size}` records sorted by unique SHA-256 digest; size is a canonical uint64 decimal string |

Each omission is exactly `{account,entry,resource,reason}`. Account names a declared account; entry is empty for a collection gap or names an existing entry of that account. Resource is empty or a resource ObjectId under that contribution. Reason is nonempty scalar text, rendered inertly. Nonempty resource requires a contribution entry. `complete` is true exactly when omissions is empty; an empty omission list does not independently prove that the selected source collection was exhaustive.

Entry objects have their common `id`, `account`, `kind` and `object` fields. ID is an ObjectId; account names a declared account; object names an inventoried SHA-256 digest. Their exact additional fields are:

| Kind | Additional members and meaning |
| --- | --- |
| `contribution` | `reference`, `resources`, `evidence`: exact EventReference; array of `{resource,object}` mappings sorted by unique resource ObjectId; sorted unique array of evidence-entry IDs |
| `original-mail` | `contribution`: empty or the ID of a contribution entry in the same account |
| `evidence` | None; original public proof/verification evidence retained only for historical inspection |

A contribution's event bytes must agree with its reference's principal, conversation and event. Resources refer to the exact included resource bytes. For an operation with a manifest, included mappings and explicit resource omissions together cover that manifest exactly, without overlap; included digests and sizes must match it. Other operation-specific resource inventories retain their owning binding. Unknown operations can be preserved as opaque historical records, but cannot acquire a verified projection or actions.

Each referenced evidence entry exists in the same account. An original-mail relation is explanatory provenance, not proof that the original MIME authenticated the referenced event. Contradictory event identities and differing original representations remain separately retained entries; import never deduplicates away conflict evidence by principal/event alone.

Every object is referenced by at least one entry or included resource mapping. No referenced object is absent; no unreferenced object is smuggled into the archive. Identical bytes can share one digest-addressed object. Object lengths determine exact concatenation boundaries, and each object's bytes must match its SHA-256. Zero-length objects are valid only with the corresponding digest. Reject malformed sizes before integer conversion or allocation.

:::

## Publish and resume

Write to a private staging destination, finish encryption, verify its completed artifact, then atomically publish the file or immutable storage object. Persist its exact encrypted bytes and a local completion record before reporting success. An interrupted upload retries those bytes; it does not increment the sequence or replace a completed snapshot. A storage acknowledgement without completed local verification is not a recoverability result.

The completion record is exactly `{archive,snapshot,sequence,ciphertext,size}`: the three manifest identifiers/counter, SHA-256 of the complete encrypted file, and its canonical uint64 size. It contains no archive secrets. Advance the writer's accepted head transactionally, comparing the expected predecessor. Concurrent writes that used the same predecessor conflict; do not choose a winner by storage arrival time. This profile has one writer per archive. Another exporting device starts a separate archive unless it uses a separately authorized writer-transfer contract.

A storage transport can carry these opaque files without reading the manifest. Account authentication authorizes retrieval or deletion; it does not decrypt the archive. A downloaded file and its kit remain usable offline independently of storage, account or subscription availability. Availability, pricing, cloud retention and service deletion promises are not cryptographic properties of the format.

## Restore into historical state

1. Select the archive and kit through trusted local input. Received email, a web page or an archive field must not supply an arbitrary path, kit or trust anchor.
2. Enforce disclosed ciphertext, header, time and storage limits. Decrypt through the selected age implementation into private staging. Do not publish any output before the entire encrypted file and its final authentication have succeeded.
3. Require exact container framing, strict manifest schema, account/entry references, object closure and lengths. Hash objects while copying bounded chunks; never allocate a declared object length as one buffer. Verify the final archive signature with the kit key and reject trailing bytes.
4. Validate contribution references and operation-specific included/omitted resources. Retain the original bytes. Invalid required index or integrity checks reject the snapshot import as a unit; do not activate a subset.
5. Compare any independently retained completion/head evidence. A different encrypted digest under the same snapshot is a conflict; an older sequence is not silently installed over a known later one. Without a retained head, a valid old snapshot remains readable but freshness is unknown.
6. Commit the complete history import in a separate historical namespace. Repeating the same snapshot/content identity is idempotent; a conflicting snapshot remains separate evidence. Preserve the existing live account unchanged on any failure.
7. Reconstruct historical relationships from retained content. Mark imported provenance and unavailable dependencies. Rich content still uses the required inert parser, sanitizer and resource isolation. Legacy source retains its reversible interpretation rules. Authenticating an archive does not independently reverify every original author.
8. Establish current account use separately through surviving-device enrollment or explicit new identity. Imported keys, identity pins, device grants, MLS checkpoints, votes, outboxes and action queues must never enter live authority tables.

An implementation may retain a failed staging artifact for explicit local diagnosis under its storage protections, but must not display it as a completed import. It must clean up abandoned staging and explain incomplete processing rather than silently skipping content. A storage service cannot repair a lost kit; support must not imply that billing or mailbox login bypasses encryption.

## Rotation, compromise and rollback

Changing the archive-encryption recipient or writer starts a new archive identifier, independent keys and kit, and a new sequence-zero chain. Re-encrypt selected historical content only with explicit scope authorization and verify the new recoverable snapshot before retiring local old keys. The old kit still unlocks old exported files; rotation does not recall them. A compromised writer or stolen kit requires disclosure of that exposure, not a claim that rotation erases it.

The kit deliberately contains no archive-writer signing secret. After total writer loss, it verifies and decrypts historical snapshots; fresh exports start a new archive. This does not break an account identity because the archive writer was never that identity's authority.

Signed content detects unauthorized replacements when the independent verification key remains trusted. The previous-file chain and retained head detect conflicting or rolled-back snapshots relative to evidence the reader actually retains. They do not prove that a service returned the latest snapshot, survive arbitrary rollback of the entire machine or repair a compromised signing endpoint. Do not promise those properties without an additional independent checkpoint mechanism.

An archive is retained readable history. Its compromise exposes that history even when transport epoch secrets were deleted. Archive encryption therefore does not preserve transport forward secrecy against later compromise of archive-unlocking material, nor upgrade the original conversation's cryptographic suite.

## Evidence and acceptance

The [archive experiment](evidence/README.md#encrypted-correspondence-archive) exercises the bounded container, independent writer signature, resource checks, private staging, offline encryption/decryption and negative cases. It uses the existing age tool instead of implementing file cryptography. It is not yet a full application exporter/importer, managed storage adapter or complete rich-history renderer.

Before a client advertises archive support, additionally exercise complete mailbox snapshot selection, declared attachment inventories, crash/retry publication and actual renderer integration. Include lost kits, swapped verifier keys, signatures from another archive, duplicate JSON names, enormous sizes, missing and changed resources, truncated encryption and container data, final authentication failure, unknown operations, conflicting heads, incomplete coverage and restoration with no billing/network connection. Verify that every attempted restore leaves live identity and action state untouched.

## Relay credentials are not history

Live [relay route signing keys](relay-routes.md#route-key-retirement), relay management/submission tokens and active routing authority are excluded from historical archives. Public route/proof evidence may be retained as historical provenance, without reactivating it during restore.
