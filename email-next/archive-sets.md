---
title: Complete archive collections
order: 9.4
blurb: signed catalog · complete inventories · atomic historical restore
sectionNav: true
---

# Complete archive collections

A large correspondence backup may need several encrypted files. Successfully decrypting one file does not establish that the complete backup was recovered. The candidate `email2-archive-set-v0` profile adds an encrypted, signed catalog naming every required part and the exact selected record inventory.

Parts retain the [archive-v0 format](encrypted-archives.md). The catalog is a separate format, not a new interpretation of an existing archive. The same independently retained kit decrypts the collection and pins its archive writer. Restoring either format creates historical state only, never live account authority.

## Freeze the collection before uploading

Select each account's retained-history scope from a consistent local source view, assign an immutable selection identifier and record its durable local cutoff sequence. Use `all-retained` for that entire retained view or `selected` for an explicitly selected subset. Freeze the exact selected records before partitioning. Sender dates and remote message counts do not establish this boundary.

For each account, compute the selected entry count and index digest defined below from the frozen source, not from whichever upload parts happen to succeed. Partition those records into self-contained archive parts. Duplicate resource bytes may occur in several parts; contribution/evidence/original entry IDs must remain unique across the collection. Original-mail and evidence relationships must stay with their referenced contribution in the same part; their object bytes and declared resources cannot depend on an unlisted file.

The source account scope is a local exporter claim. A catalog cannot prove that a provider supplied every message ever sent or that an unobserved message did not exist. The interface identifies the retained source and cutoff and reports collection gaps as omissions.

## Catalog protection and identity

The catalog uses the same selected binary age encryption and single recovery recipient as archive-v0. After decryption, its exact structure is eight ASCII octets `EML2SET0`, a four-octet unsigned big-endian JSON length, that many strict UTF-8 JSON octets and a 64-octet Ed25519 signature. No part bytes, filenames, paths, URLs, recursive catalogs or trailing bytes are included.

The signature message is ASCII `email2/archive-set/v0`, one zero octet, then the raw SHA-256 digest of every preceding decrypted catalog octet. Verify with the independently pinned archive-writer key from the kit. Do not trust a verifier supplied by the catalog. This is the same application-signing pattern as archive-v0 with a distinct domain; signatures are not transferable between the formats.

The JSON has the archive-v0 duplicate-name/scalar/number rules, maximum 16,777,216 octets and depth 32. Enforce additional disclosed local record, part, ciphertext, staging and time budgets before processing or allocation. A budget failure is incomplete processing, not permission to omit a part and call the collection complete.

::: {.details summary="Exact catalog schema"}

The catalog has exactly these members:

| Member | Value |
| --- | --- |
| `version` | Exactly `"0"` |
| `purpose` | Exactly `"correspondence-archive-set"` |
| `archive` | Archive ObjectId matching the kit and all parts |
| `set` | Fresh ObjectId for this immutable collection |
| `generation` | Canonical uint64 string, initially `"0"`, incremented for the next collection |
| `previous` | Empty at generation zero, otherwise the preceding completed encrypted catalog's SHA-256 |
| `firstSequence` | Canonical uint64 sequence of the first part |
| `previousPart` | Empty when firstSequence is zero, otherwise the SHA-256 preceding the first part's part-file chain |
| `accounts` | Nonempty array of scope records below, sorted by unique account ID |
| `parts` | Nonempty ordered array of part records below |
| `complete` | Boolean, consistent with collection and part omissions |
| `omissions` | Array of exact `{account,reason}` objects naming a declared account and a nonempty scalar-text reason for a collection-level gap |

Each account scope is exactly `{id,principal,selection,mode,cutoff,entries,digest}`. ID and selection are ObjectIds. Principal retains archive-v0's enp0-or-empty rule. Mode is exactly `all-retained` or `selected`. Cutoff is the canonical uint64 local history sequence for the selected consistent view, not an independently verified time or cryptographic ordering fact. Entries is the canonical uint64 selected-entry count. Digest is its index commitment below. A subset selected by the person must not be labeled all-retained.

Each part record is exactly `{snapshot,sequence,ciphertext,size}`: snapshot ObjectId, canonical uint64 part sequence, complete encrypted part's SHA-256 and canonical uint64 ciphertext size. Sequences are contiguous starting at firstSequence, without overflow; snapshots and ciphertext digests cannot repeat. Their order is numeric sequence order, not lexical decimal-string order. A part's archive, snapshot and sequence must equal the catalog; its previous digest equals previousPart for the first part or the preceding part's ciphertext digest thereafter.

The union of declared part accounts equals the catalog's account set. Repeated account declarations agree on principal. A part is independently a valid signed archive-v0 artifact. Its entry/object closure, original-mail relations, evidence associations, resource sizes and explicit omissions are checked in full.

Collection `complete` is true exactly when collection omissions are empty and every part's coverage is complete. A valid collection with declared omissions may be imported as incomplete history, visibly labeled as such. A missing catalog member is an incomplete transfer and prevents atomic collection import; it is not an implicit omission or an independently complete partial set.

:::

### Account index commitment

For each account, take its selected entry objects from the frozen source. Entries use only the exact archive-v0 entry schemas and their ASCII identifier/encoding values. Sort them by entry ID. Encode each object as JSON with recursively ASCII-sorted object keys, no insignificant whitespace and the existing sorted resource/evidence arrays unchanged. The fields admitted by these entry schemas are ASCII, so this encoding requires no Unicode normalization or number conversion.

Compute SHA-256 over ASCII `email2/archive-set-index/v0`, one zero octet, then, for each encoded entry, its eight-octet unsigned big-endian byte length followed by those bytes. Store that digest and the exact entry count in the account scope. A receiver recomputes them over the union of validated parts. The empty account digest is the hash of the prefix and zero octet alone.

This binds exact event and resource object digests, references and provenance relations through the entry records. It does not collapse two distinct records sharing an event identity, or require resource bytes to be globally deduplicated. Duplicate entry IDs anywhere in the set are invalid even when their bytes match. Bounded disk-backed sorting is permitted; silently dropping records to fit memory is not.

## Publish a single completion result

Retain the frozen selection, exact encrypted part bytes and exact encrypted catalog in a durable local job before transport. Upload immutable digest-addressed parts first. Check their complete returned bytes or an equivalently authenticated storage-integrity mechanism against the frozen descriptors before treating them as retrievable. A successful request or a service-supplied filename alone is insufficient.

Publish the immutable encrypted catalog only after every named part is available under the selected storage contract. Then commit the local completed-set record `{archive,set,generation,ciphertext,size}` and advance its accepted catalog head by comparing the expected predecessor. Part completion may have advanced the archive's part-file counter, but does not advance collection completion by itself. Reaching a uint64 counter limit stops that chain; a fresh archive identifier, keys and kit are required before further exports. Retries preserve original bytes, IDs, generation and selection; they cannot quietly create a new catalog from only successful parts.

On loss of a response, retrieve and compare the original immutable object. On a local race or different bytes under the same set/generation, preserve the conflict and the prior completed head. Do not pick a winner by upload order or overwrite a known good collection. Abandoning a job does not turn its orphaned parts into a completed set. Cleanup follows explicitly selected retention policy and cannot delete a referenced completed collection as a retry shortcut.

Storage may temporarily expose a catalog while one of its parts is unavailable. The reader still checks every part and reports the collection unavailable/incomplete until that changes. The catalog is an atomic completion declaration, not a promise of permanent service availability or a multi-object storage transaction.

## Restore all parts or publish no new collection

1. Select the catalog, recovery kit and available part sources through trusted local input. The catalog cannot choose a filesystem path, URL, credential or verification key. A managed-storage adapter separately authorizes any retrieval; importing does not follow message-supplied links.
2. Fully decrypt and authenticate the catalog into private staging. Check its exact schema, independent signature, counters, part uniqueness and any retained head. Known older/conflicting heads cannot replace a current completed head; explicit historical reading remains possible with that status. Without independent retained head evidence, latest-generation freshness remains unknown.
3. For each descriptor, retain the exact bounded ciphertext bytes in private staging and verify its size and digest. Decrypt that retained copy, not a source path that may have changed after checking. Apply all archive-v0 checks and require the exact archive/snapshot/sequence/predecessor bindings.
4. Keep every accepted part inside this collection's private staging namespace. Check unique entry IDs, account/principal agreement, exact selected counts and index commitments, and the combined complete/omission state. No missing or extra records can be repaired by subject, timestamps, hash lookalikes or record deduplication.
5. Prepare the accepted catalog and completion receipt with the staged history. Publish the historical collection in one local transaction or atomic namespace rename only after every check succeeds. On failure, preserve the previous completed collection and live identity/action state; never activate a subset.
6. Repeating an already accepted exact encrypted catalog returns its retained completion result without duplicating history or actions. That idempotent result is not a new disk-health or latest-snapshot check. A different encrypted digest under the same set identity is a conflict, not another retry.

A process exit before publication leaves no new visible completed collection. A leftover private staging directory remains unaccepted and requires controlled cleanup or full revalidation before use. A process exit after publication resumes from its atomic completion receipt. Import does not install identity pins, keys, MLS checkpoints, votes or outboxes.

## Evidence and boundary

The [collection experiment](evidence/README.md#complete-archive-collection) encrypts a signed catalog and multiple signed archive files with the existing age tool, verifies them in private staging and publishes their history together. It checks actual encrypted-member substitutions and unavailable parts, not just a list of filenames. It is not a real mailbox snapshot exporter, cloud publisher, rich-history renderer or identity-recovery implementation.

The collection format removes the single-manifest whole-collection ambiguity. It does not remove finite processing limits, prove absence of unobserved mail, detect arbitrary whole-machine rollback or provide authorization to transfer the kit or history to another device. The separate history-disclosure contract must authorize that transfer.
