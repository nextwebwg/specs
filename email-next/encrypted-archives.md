---
title: Encrypted correspondence archives
order: 9.3
blurb: portable history · recovery material · complete resources · inert restoration
sectionNav: true
---

# Encrypted correspondence archives

An encrypted archive preserves correspondence after a device is lost: original mail, accepted contributions, reply relationships and included resources. The same portable format works with storage managed by the person or by a service. Decrypting a downloaded archive does not require a subscription or a billing-service connection.

An archive preserves correspondence its authorized source actually decoded and exported. It cannot recover an unopened delivery whose necessary transport keys were lost before processing; merely backing up the ciphertext is insufficient. The [offline delivery contract](suite-profile.md#unread-mail-and-long-offline-periods) defines that boundary.

An archive restores historical reading, not a live encryption identity. Importing it cannot authorize sending, enroll a device, reinstate a revoked key or replay an answer. Those actions continue to use current identity and conversation authority.

> [!note] Candidate archive profile
> `email2-archive-v0` defines a signed history container protected by an existing file-encryption format. The reference experiment tests container integrity, resource preservation and encryption through an installed age implementation. It does not establish production storage, secure device-key custody, comprehensive parser containment or independently reviewed recovery assurance.

## Create a recovery kit before relying on backup

For a normal backup, the first exporting device creates an archive identifier, an independent archive-encryption identity and an independent archive signing key. The [history-transfer binding](history-transfer.md) instead authenticates a recipient-selected encryption identity while retaining these exact file formats; it never sends the original backup kit. These are not device-binding, account-administration or MLS keys. The signing key is local to this archive's writer; it grants no live account authority.

The recovery kit contains the archive identifier, archive-decryption identity and trusted public archive-signature verification key. Store it separately from the archive and the device being backed up, through an explicitly chosen password manager, offline copy or another independently recoverable destination. Show what possession allows: reading every snapshot encrypted to that identity. Anyone holding the kit can read those archives; mailbox-password reset cannot reconstruct it.

Before reporting recovery setup complete, decrypt and verify a test snapshot using the retained kit through the selected independent destination. This checks the available recovery route at setup time, not that the person will never lose it. A second copy solely on the same device or inside its own locked archive is insufficient.

::: {.details summary="Exact recovery-kit object and selected protection"}

The kit is strict UTF-8 JSON with exactly `version`, `purpose`, `archive`, `ageIdentity` and `verificationKey`. Version is `"0"`; purpose is `"archive-recovery-kit"`; archive uses the nonzero ObjectId grammar. `ageIdentity` is a valid native age X25519 secret identity. `verificationKey` is the 32-byte Ed25519 public key encoded as 64 lowercase hexadecimal characters. Unknown members, duplicate decoded names, nulls and malformed encodings are rejected. A kit is secret material, never a discovery advertisement, email notification, support log or billing record.

The encrypted file selects the binary age v1 format and native X25519 recipient from the pinned [C2SP age v1.1.0 specification](https://c2sp.org/age@v1.1.0). Generate exactly one native X25519 recipient stanza, for this archive's recovery identity. Inert extension stanzas whose type ends in `-grease`, as emitted by maintained age implementations, may accompany it. Readers ignore those extension stanzas when selecting the native identity. Additional X25519 recipient stanzas and other recipient types fail this profile. Armor, password recipients and service-held decryption recipients are outside this profile. Use an age implementation and its parsed stanza interface; do not replace its header parsing, encryption or final-authentication rules. This selection is not post-quantum protection.

Structured recipient and identity fields use age's original Bech32 checksum, not Bech32m. Require the canonical public spelling `age1…` and secret spelling `AGE-SECRET-KEY-1…`, containing exactly 32 decoded octets: 52 data symbols and six checksum symbols, with zero padding in the last symbol. Reject mixed case, incorrect checksum, excess or nonzero padding, and wrong decoded lengths. A human-entry adapter may accept a uniformly cased checksum-valid spelling and canonicalize it before freezing a new object; it must not rewrite an already signed object. The public and secret strings are respectively 62 and 74 ASCII characters. A checksum detects some entry errors; it does not prove ownership or trust.

Age uses the IETF ChaCha20-Poly1305 construction with different key and nonce bindings for wrapping and payload encryption. Native X25519 wrapping derives a fresh key from the ephemeral exchange and both public keys; the all-zero AEAD nonce is valid only under that one-time wrapping-key contract. The payload instead derives its key using a fresh 16-octet salt and uses age's 88-bit chunk counter plus final-chunk flag. Neither binding can be replaced with TLS 1.3's record nonce construction. Follow the pinned format's authenticated header, complete final chunk, EOF and trailing-data checks. Stage the entire authenticated plaintext privately before accepting an archive; a valid prefix is not a recovered snapshot.

The archive signature binds origin separately: anyone knowing an encryption recipient can encrypt a replacement file. Decryption success alone cannot authenticate the archive's writer. Pin the verification key from the independently retained kit, never from an untrusted archive or storage response.

:::

## Freeze one snapshot

Export from a consistent retained-history view. Do not mix records from before and after a concurrent edit, resource update or account change without reporting that boundary. Freeze the manifest and object bytes before signing. A snapshot identifies the selected accounts, omissions and exact object inventory; it does not claim that the service possesses every message ever sent to those accounts.

Before handing an export to encryption or transport, validate the frozen selected objects, contribution references and supported resource bindings. Do not rely on the recipient rejecting an invalid archive after the bytes have already been disclosed. A cross-principal share additionally follows the [history-selection and dependency procedure](history-transfer.md#select-messages-without-silently-selecting-the-conversation); backup completeness is not permission to disclose a whole conversation.

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

A contribution's event bytes must agree with its reference's principal, conversation and event. Resources refer to the exact included resource bytes. For an operation with a manifest, included mappings and explicit resource omissions together cover that manifest exactly, without overlap; included digests and sizes must match it. Other operation-specific resource inventories retain their owning binding. Unknown envelope/operation versions and kinds can be preserved as [opaque historical records](#restored-does-not-always-mean-understood); their associated objects remain archive-writer associations, not verified operation resource semantics or actions.

Each referenced evidence entry exists in the same account. An original-mail relation is explanatory provenance, not proof that the original MIME authenticated the referenced event. Contradictory event identities and differing original representations remain separately retained entries; import never deduplicates away conflict evidence by principal/event alone.

Every object is referenced by at least one entry or included resource mapping. No referenced object is absent; no unreferenced object is smuggled into the archive. Identical bytes can share one digest-addressed object. Object lengths determine exact concatenation boundaries, and each object's bytes must match its SHA-256. Zero-length objects are valid only with the corresponding digest. Reject malformed sizes before integer conversion or allocation.

:::

## Preserve messages that have several deliveries

One message can arrive through several encrypted deliveries. A backup preserves its original authored content once in the historical conversation, while retaining the separate evidence of how copies arrived. Delivery identifiers must not become extra messages, reply targets or proof that everybody received the same history.

The selected asynchronous agreement uses the existing archive container and entry schemas. Its contribution object is the complete original authored record. This does not reinterpret older event formats or turn archive evidence into current encryption authority.

::: {.details summary="Exact authored0 history mapping and inert assembly"}

Apply this mapping only when implementing [authored0 and envelope6](event-encoding.md#asynchronous-authored-records-and-deliveries):

| Archive component | Asynchronous representation |
| --- | --- |
| Contribution entry `object` | Digest-addressed complete original authored0 UTF-8 bytes, without a new wrapper, reserialization or delivery envelope. |
| Contribution entry `reference` | That authored record's exact principal, conversation and logical event. Never envelope6's delivery event. |
| Contribution entry `resources` | Included decoded resource objects, mapped by the authored operation's resource IDs. Validate its exact manifest, roles, lengths and digests; declared omissions retain the existing coverage rules. |
| Evidence entry | Separately retained original public evidence or complete delivery-envelope bytes, associated by this archive writer. It is not a second contribution, a live acceptance receipt or a secret-state snapshot. |
| Original-mail entry | Exact original retained mail with an optional relation to its contribution entry. Preserve each selected mail representation separately; headers do not independently prove native authorship. |

Strictly select the supported record's top-level purpose and version before applying its complete schema. The authored record has purpose `authored-contribution` and version `"0"`; an older contribution envelope has its own purpose, version and grammar. A field named `operation`, `manifest` or `authored` cannot select this interpretation. Known-format malformed records fail validation; unsupported formats remain opaque under the existing rule. Do not decode envelope6 as a historical authored contribution or silently extract a purported authored record from unvalidated evidence bytes.

Source preflight validates the exact supported authored grammar and operation-specific resources before disclosure. The authored record's one-mebibyte/depth bounds apply independently of archive manifest and aggregate limits. An evidence object can retain a larger selected delivery wrapper under its own grammar and local archive budgets; that does not enlarge authored-record limits. Import rechecks these boundaries. Missing original authored bytes cannot be repaired from visible MIME projections, quoted history or a digest.

For one selected retained authored record, use one contribution entry with all deliberately selected evidence associations. Preserve distinct archive entry IDs when the source retained separate observations or conflicting variants; the catalog's exact counts/index commitment cannot collapse them. Equal original authored bytes may share one object digest. A historical view may display one message with several provenance observations, but the retained collection inventory still accounts for every entry. Different bytes under one claimed author/logical identity remain distinct historical variants, never an arrival-selected winner.

The [two typed namespace ledgers](event-identifiers.md#keep-delivery-identity-separate-from-message-identity) do not become one archive deduplication key. If the source retained several delivery variants under one delivery ID, preserve each selected variant as separate evidence with its original association. If their authored bytes differ under one claimed logical identity, retain the selected authored variants as separate contribution entries. A shared delivery ID cannot suppress one variant or relabel it as an exact retry. Historical grouping may explain the writer's recorded conflict, but cannot independently authenticate that conflict, settle transport uncertainty or install either live ledger. Native proof material and original mail are retained only within the deliberately selected archive scope; missing material remains unavailable rather than reconstructed.

Reconstruct historical relationships through exact logical references within the authorized imported content. An existing-scope reference with no selected definition remains unresolved; a missing parent or question likewise remains missing. Selecting a reply does not automatically select its scope root, parent or the rest of the conversation. The history-selection contract decides whether to include them. Do not claim that a retained intended-slot list proves current membership, slot resolution, delivery success or another person's view.

Archive authentication proves this writer's snapshot, not independent original-author authentication. Keep writer-attested historical relationships and conflicts separate from the live namespace. An imported root, resolution, binding ledger, delivery envelope or author claim cannot reserve a live event ID, install a scope definition, resolve an invitation slot, enroll a peer or create an outbox. Own-device scope setup uses its separate current administrative transfer and reconciliation contract.

If the exact message later arrives through a fully accepted native delivery, the live path independently checks its author, scope, original bytes, resources and target rules. Only that acceptance can supply live namespace evidence. The interface may associate the byte-identical historical projection with the accepted message while retaining both provenances. Do not convert other writer-attested variants into authenticated conflicts merely because their claimed ID matches. Independently authenticated conflicting variants still follow the global namespace rules. Reading or associating the historical copy never runs an interaction; processing a genuine accepted delivery applies its owning once-only local effect and pending-dependency rules. It cannot recreate an outgoing service request from imported history.

The archive-v0 entry and archive-set index schemas remain unchanged. An older reader may preserve authored0 as opaque history without claiming to understand its resources or relationships. These mappings neither add optional members to signed manifests nor relabel a signed artifact. Historical import remains useful even when no current native stream or original transport secrets survive.

:::

## Publish and resume

Write to a private staging destination, finish encryption, verify its completed artifact, then atomically publish the file or immutable storage object. Persist its exact encrypted bytes and a local completion record before reporting success. An interrupted upload retries those bytes; it does not increment the sequence or replace a completed snapshot. A storage acknowledgement without completed local verification is not a recoverability result.

The completion record is exactly `{archive,snapshot,sequence,ciphertext,size}`: the three manifest identifiers/counter, SHA-256 of the complete encrypted file, and its canonical uint64 size. It contains no archive secrets. Advance the writer's accepted head transactionally, comparing the expected predecessor. Concurrent writes that used the same predecessor conflict; do not choose a winner by storage arrival time. This profile has one writer per archive. Another exporting device starts a separate archive unless it uses a separately authorized writer-transfer contract.

A storage transport can carry these opaque files without reading the manifest. Account authentication authorizes retrieval or deletion; it does not decrypt the archive. A downloaded file and its kit remain usable offline independently of storage, account or subscription availability. Availability, pricing, cloud retention and service deletion promises are not cryptographic properties of the format.

## Recover history without claiming account recovery

An archive answers “Can I read this saved correspondence?” It does not answer “Can I act as my old encryption identity?” After total device loss, a person may recover their history using the archive and kit, then establish a new identity through the explicit continuity-break procedure. Correspondents still decide whether to replace their old association; the archive cannot approve that change for them.

A remaining send/receive-only device may keep performing the operations its current authority allows. It cannot promote itself to administrator or approve a replacement merely because it can display old messages. If an eligible administrator is only temporarily unavailable, wait for it. See the [access distinctions](identity-lifecycle.md#know-what-each-kind-of-access-unlocks) and [administrative-loss procedure](identity-lifecycle.md#when-administrative-devices-are-unavailable).

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

## Restored does not always mean understood

A verified archive can preserve a message this client does not yet understand. Keep its exact bytes and archive provenance, label the unsupported format, and offer inert source inspection or export. Do not guess its meaning, execute a stored action or fetch a plugin or remote content to make it appear supported.

“Complete” describes the selected retained byte inventory, not universal readability or fresh verification of every correspondent. Missing files and unsupported formats are different outcomes. The client must show both accurately rather than silently dropping an unfamiliar message or calling it a verified conversation contribution.

::: {.details summary="Opaque records, resource associations and restoration outcomes"}

For a supported envelope/operation version, apply its owning resource inventory and availability rules. For an unknown envelope, operation kind or operation version, preserve the original event as opaque historical data under the archive's existing byte, signature, reference and object-inventory checks. Do not invoke a known operation parser merely because a field is named manifest, text, replyTo or serviceAction. Unknown data cannot select a parser fallback or an active control.

Resource mappings retained for an unsupported record are archive-writer associations to included, integrity-checked objects, not independently verified original-author resource declarations. Preserve them without active rendering, external fetches or claims of a matched quotation/source. Missing retained bytes still need the existing explicit omissions. Do not invent resource coverage for semantics the client cannot interpret. Later support may deliberately produce a validated historical projection under its own parser and safe resource rules; it still cannot promote the record into live authority or effects.

| Restore result | Permitted presentation |
| --- | --- |
| Missing/invalid archive proof or object integrity | Failed/unaccepted import; no trusted partial publication |
| Valid selected collection with omissions | Historical import with explicit incomplete coverage |
| Valid selected bytes in an unsupported format | Retained opaque history with unsupported-format status; no semantic or action claim |
| Supported historical content and safe verified resources | Readable historical projection with its actual archive/source provenance, not new live acceptance |
| Exact target independently validated through its owning live path | Eligible for the separately authorized current reply/action only if its target, actor and audience rules also pass |

These statuses are separate: a complete selected inventory can contain unsupported records, and readable historical text can lack independently verifiable author or live-target evidence. Keep local history links distinct from sent protocol references. Never revive an imported queue to make the view look complete.

:::

## Replying after restoration

Restored history can help you write a new message. It does not reactivate old buttons, service actions or sending credentials. Before sending, the app needs a currently authorized identity and a deliberately selected current audience.

> [!ex] An old question stays readable without becoming a live button
> Alice restores Bob's old meeting question, including a Tuesday button. Opening it sends nothing. After selecting Bob's current address and completing current protection setup, she can write “Are we still meeting Tuesday?” and deliberately quote the old wording as historical context. Without separately validated target evidence, this is a new message, not an answer submitted to the old question.

:::: {.details summary="Historical sources, live references and new composition"}

1. Keep the imported contribution and its archive provenance in the historical namespace. Do not reserve a live author's event identifier, accept its old interaction effects or install a contact pin merely because the archive signature verifies.
2. Establish current sending authority through eligible surviving-device enrollment or the explicit new-identity procedure. Resolve current recipient associations and protected delivery independently of the imported address book or message headers. Preserve identity-change holds.
3. If the reply's exact target has separately passed its owning live carrier, author, content, audience and target-eligibility checks, use the normal reply procedure. The imported copy alone is not that validation. If those checks cannot be completed, offer a newly composed contribution without an authenticated parent reference, or hold a specifically required reply/action. A local link back to imported history remains local provenance, not a sent EventReference.
4. Include only historical passages and resources deliberately selected for disclosure to the actual current audience. Use the core composition and quotation rules, preserving source availability and verification limits. When exact original source verification is unavailable, do not claim a matched structured source. An otherwise valid indexed reply may use its unattributed-quotation role; that does not supply a missing valid primary reply target. If no eligible primary target is available, a deliberately composed rich-message with empty replyTo may include an inert historical blockquote under the required rendering profile, clearly distinguished from new writing and without a structured source claim. Unsupported original records cannot supply trusted chunk boundaries or automatic resource selection. A quotation does not become newly verified just because it is inside a newly encrypted message. Do not automatically attach the restored conversation or copy old recipients.
5. Freeze a fresh contribution and current delivery plan. Leave imported outboxes, service submissions, answers, reactions and corrections inert. Creating a new message is separate from retrying or cancelling an old uncertain operation; retain the latter's uncertainty without reissuing it.

A new identity cannot answer an old question or edit an old author's message merely because the person recognizes it. Any supported structured action still needs its own exact target and current actor authorization. Reopening history or clicking an unsupported old control sends nothing. A client may guide the person into an independently authorized new composition; it must not report the old action as completed.

::::

## Preserve honored deletion during restoration

An archive may contain a message that the recipient's system later removed.
Restoring that archive does not override a retained deletion disposition or turn
its target into a new message. Apply the [suppression and restoration rules](delivery-policy.md#retain-suppression-for-as-long-as-the-original-can-return)
before promoting historical material into ordinary conversation presentation.
Historical inspection does not establish that every exported copy was erased.

## Rotation, compromise and rollback

Changing the archive-encryption recipient or writer starts a new archive identifier, independent keys and kit, and a new sequence-zero chain. Re-encrypt selected historical content only with explicit scope authorization and verify the new recoverable snapshot before retiring local old keys. The old kit still unlocks old exported files; rotation does not recall them. A compromised writer or stolen kit requires disclosure of that exposure, not a claim that rotation erases it.

The kit deliberately contains no archive-writer signing secret. After total writer loss, it verifies and decrypts historical snapshots; fresh exports start a new archive. This does not break an account identity because the archive writer was never that identity's authority.

Signed content detects unauthorized replacements when the independent verification key remains trusted. The previous-file chain and retained head detect conflicting or rolled-back snapshots relative to evidence the reader actually retains. They do not prove that a service returned the latest snapshot, survive arbitrary rollback of the entire machine or repair a compromised signing endpoint. Do not promise those properties without an additional independent checkpoint mechanism.

An archive is retained readable history. Its compromise exposes that history even when transport epoch secrets were deleted. Archive encryption therefore does not preserve transport forward secrecy against later compromise of archive-unlocking material, nor upgrade the original conversation's cryptographic suite.

## Evidence and acceptance

The [archive experiment](evidence/README.md#encrypted-correspondence-archive) exercises the bounded container, independent writer signature, resource checks, private staging, offline encryption/decryption and negative cases. It uses the existing age tool instead of implementing file cryptography. It is not yet a full application exporter/importer, managed storage adapter or complete rich-history renderer.

Before a client advertises archive support, additionally exercise complete mailbox snapshot selection, declared attachment inventories, crash/retry publication and actual renderer integration. For current authored history, include same-delivery-ID variants, equal authored bytes through different preparations and unequal bytes under one claimed authored identity; check exact entry/object retention and inert restoration, not just the number of displayed messages. Include lost kits, swapped verifier keys, signatures from another archive, duplicate JSON names, enormous sizes, missing and changed resources, truncated encryption and container data, final authentication failure, unknown operations, conflicting heads, incomplete coverage and restoration with no billing/network connection. Verify that every attempted restore leaves live identity and action state untouched.

## Relay credentials are not history

Live [relay route signing keys](relay-routes.md#route-key-retirement), relay management/submission tokens and active routing authority are excluded from historical archives. Public route/proof evidence may be retained as historical provenance, without reactivating it during restore.
