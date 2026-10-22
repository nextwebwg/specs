---
title: Retiring setup secrets
order: 7.2
blurb: erase after use · expire abandoned setup · retain readable history
sectionNav: true
---

# Retiring setup secrets

Temporary setup secrets must stop being useful after their job is finished. Clients retire each secret after successful use, on cancellation, or when that secret's fixed role deadline ends. Published admission material may have a separately declared receiving-only window; publication expiry never makes it usable for new setup. A completed MLS admission must not leave an old private admission key that can later unlock a recorded setup exchange and recover conversation secrets.

The [unread and offline-delivery contract](suite-profile.md#unread-mail-and-long-offline-periods) separates background processing from human reading and defines historical recovery when every receiving copy stayed unavailable beyond expiry. Fresh setup alone does not recover such ciphertext.

Readable correspondence has a different lifetime. Clients preserve it through separately protected historical storage, not by keeping consumed transport keys. Public signatures, package-consumption records and replay-prevention evidence remain available without the deleted secrets.

> [!ex] Setup is abandoned
> Alice starts secure setup, but no usable response arrives. When that attempt expires, her client closes it and retires its temporary secrets. Her writing remains private and queued. A later attempt has a new identifier, fresh temporary material and its own lifetime; it does not revive the expired attempt or silently send plaintext.

This chapter specifies lifecycle requirements, not a claim that the experiments securely erase memory, SSD pages, backups or hardware key slots. The MLS requirements remain authoritative: [RFC9420 §9.2](https://www.rfc-editor.org/rfc/rfc9420.html#section-9.2) requires deletion of consumed secrets and their recoverable ancestors; [§16.8](https://www.rfc-editor.org/rfc/rfc9420.html#section-16.8) addresses one-time admission packages. The Email/2 baseline excludes reusable last-resort packages.

## Delete the temporary secret, retain the right state

| Material | Retirement boundary |
| --- | --- |
| Private KeyPackage initialization key and other admission-only secret material | Retire when the selected admission is durably accepted. At signed publication expiry, stop new setup use; current assertion10 and retained assertion9/assertion8 each retain unused material only until the original explicit receiving deadline, while older encodings retire it at package expiry. Explicit withdrawal/revocation may retire it earlier. Keep the consumed-package tombstone. A new member's leaf private key needed by its active group is transferred to live MLS state, not indiscriminately erased with the admission-only key. |
| Consumed MLS message keys/nonces, ratchet ancestors and superseded tree/path secrets | Delete under the MLS dependency/deletion schedule as soon as consumed or superseded. A timer cannot justify retaining an already consumed ancestor. Do not reconstruct it from a saved older checkpoint. |
| Unconsumed keys retained for delayed ciphertext | Apply the separate [bounded transport-retention policy](security.md#delayed-delivery-and-retained-history); they are not an exemption for consumed keys. |
| Attempt-specific ephemeral private keys and exported handshake-only secrets | Retire on successful completion of their last required cryptographic use, cancellation or fixed deadline, whichever first makes them unnecessary. The dedicated initiating mailbox-setup control key has this attempt-only role; it is separate from the selected ordinary receiving key in the [setup handoff](first-contact-setup.md#finish-setup-for-one-intended-send). An HTTP success or unsigned `ready` flag cannot establish that boundary. |
| Advertisements, identity evidence and transcript hashes | Not decryption secrets. Keep the exact minimum evidence needed for continuity, collisions, retries and explanation under bounded retention. A publicly verifiable signature is not permission to publish its mailbox/relationship metadata. Privacy policy may remove excess metadata without removing necessary replay protection. |
| Signed inspect/cancel proofs and other scoped authorization requests | Not decryption keys, but still security-sensitive while their owning authorization can be replayed. Keep exact retry payload/signature in protected attempt storage, not public transcripts, logs or archives. Apply the [bootstrap proof boundary](bootstrap.md#signed-request-replay-and-disclosure-bounds): expiry, cancellation and current authority stop future use; they do not make an earlier disclosure disappear. Preserve necessary historical correlation/replay evidence under bounded private retention. |
| Queue/OAuth bearer credentials, PKCE verifier and refresh tokens | Follow their own authorization lifecycle. Discard one-use verifiers after completed or abandoned authorization; expire/revoke credentials under their grants. A queue token is not an MLS content-decryption key. An active, separately authorized grant may remain useful after one handshake. Never copy tokens into public transcripts or archives. |
| Long-term device signing keys and current MLS group secrets | Retain only while their authorized live role requires them; apply rotation, group updates, removal and compromise recovery. Completing one setup does not mean these keys are unused. |
| Readable history and archive/recovery keys | Follow the separate [archive contract](encrypted-archives.md) and user retention decision. No setup timer deletes correspondence or a user's independently retained recovery kit. |

Deleting old keys provides forward secrecy only for the cryptographic material actually retired. A stolen unlocked endpoint or its readable archive may still expose retained messages. Removing a handshake secret does not erase delivered plaintext, recall a message or undo a disclosure. Future protection after compromise also requires appropriate fresh MLS updates and accepted authority, not deletion alone.

## Fixed deadlines, including unused setup

The public first-contact bootstrap uses a maximum request lifetime of **600 seconds**. This is an editorial protocol parameter, not a user-supplied quota or an MLS requirement. A local policy may choose a shorter attempt; a later profile change needs a new version. Its [signed bootstrap permission](bootstrap.md#create-a-content-free-source-permission) carries the original validity interval; the provider enforces this bound before activation. Existing configured provider challenges retain their own shorter, explicitly configured limits; this chapter does not rewrite them.

Persist an attempt's immutable deadline and local retirement state before releasing its first control request. The effective deadline is the earliest of the request expiry, required grant/binding/package validity and any shorter local attempt limit. It is not restarted by retries, polling, network activity, response retrieval, process restart or receipt of an old advertisement. A response cannot extend it. Independently published unused KeyPackages have their own [signed expiry and configurable lifetime policy](security-profile.md#experimental-admission-lifetime); a ten-minute request does not give a package a new lifetime.

Stop using attempt-bound secrets when the credible clock interval can no longer establish that use precedes the deadline. Retire expired or cancelled attempt material promptly through the same retirement process as successful setup. During a running process, track a monotonic elapsed-time bound as well as the retained wall-clock deadline; wall-clock rollback cannot buy extra lifetime. Persisted clock high-water evidence detects known rollback. On restart, recheck credible time and pending retirement before use. Unknown time holds use; if the original deadline cannot be safely re-established, abandon that attempt and retire its temporary material rather than resetting its timer.

A timer cannot execute on a powered-off device. Before using keys after startup, resume pending retirement and reject expired work. At-rest protection remains necessary while the device is off. A claim that secrets become inaccessible at an exact wall-clock instant even on a stopped device requires a separately demonstrated trusted-clock/key-expiry mechanism; ordinary scheduled cleanup does not supply it.

Automatic new attempts require a separately enabled, finite retry policy that bounds attempts and elapsed work. Keep the draft when that policy runs out. Do not silently restart forever, reuse the old nonce/package allocation or take expiry as permission for a fallback. Publication pools, pending setup, credentials and transport-delay secrets have distinct timers and cannot extend one another. A current assertion10 package, or a retained assertion9/assertion8 package, published with a receiving deadline has an independently committed receiving-only role after creation use ends. Closing its bootstrap request does not reopen that request or any grant; it also does not silently shorten the already-declared receiving deadline. Explicit cancellation/withdrawal and consumed-key retirement remain effective. The [current-suite receiving contract](suite-profile.md#creating-a-delivery-and-receiving-it-later) owns that bounded role.

## Commit retirement before reporting completion

Admission and message processing must preserve both safe restart and secret deletion. Deleting keys before any recoverable acceptance state can lose the conversation; saving every old secret as a retry convenience defeats forward secrecy.

The logical acceptance transaction records the accepted checkpoint, consumed-package/replay outcome and required retirement intent together. Keep the resulting state inaccessible for new application release while a required secret-retirement step remains incomplete. Complete the crypto engine's deletion schedule, retire obsolete storage keys/copies as the storage design requires, and durably record the retirement result before reporting setup complete or releasing the first human contribution. On restart, pending retirement resumes before that release. A failed erasure step holds the affected operation; it cannot roll the group back to a previously consumed checkpoint or republish the package.

An exact retry uses retained non-secret outcome/ciphertext records and the current accepted state. It does not re-decrypt a Welcome with retired admission material, recover an ancestor ratchet secret or roll back a committed key update. If the necessary acceptance state is irrecoverably lost, follow the selected fresh-admission/recovery path; do not resurrect a stale secret from an application archive.

The same requirement applies to staged candidate groups, abandoned invitations and failed tentative processing. Distinguish a candidate secret still required for a valid pending operation from a superseded or consumed one. The ordering profile owns when a candidate becomes obsolete. This timer cannot invent a different accepted commit or erase the public safety proof needed to reject one.

## Include stored copies in the erasure design

Removing a row or dropping an object reference is logical deletion. It does not establish erasure from memory copies, database WAL/journals, allocator copies, temporary exports, crash dumps, swap, filesystem snapshots, device backups or restored machines. Production engines must document the applicable platform guarantees and keep admission/transport secrets out of logs and historical exports.

Use appropriately protected cryptographic memory and storage. Where old ciphertext copies are retained, meaningful cryptographic erasure requires destroying the last recoverable wrapping secret for those copies; re-encrypting a new database while keeping an old wrapping key is insufficient. Do not promise cryptographic erasure from a general vault key that is also retained in backups. A hardware or external key-retirement mechanism must state its rollback, recovery, deletion-confirmation and cache behavior. No particular platform API is certified by this draft.

The acceptance evidence must distinguish logical retirement, disappearance from the crypto engine's active state, recoverability from retained encrypted storage, and any claimed physical/platform erasure. Run crash/restart checks between checkpoint acceptance, retirement intent, key destruction and completion; inspect relevant original/checkpoint/WAL/export artifacts. Test success, cancellation, timeout, clock rollback/uncertainty, stale retries and restored snapshots. A test that an API refuses an old package is useful replay evidence, but does not prove its private key disappeared from storage.

## Relay signing credentials

The [relay route-key lifecycle](relay-routes.md#route-key-retirement) is separate from one-use setup/admission secrets. A route signing key remains live only for its authorized route, retires on withdrawal/expiry/reset and is excluded from historical archives. Exact retained delivery proofs can support authorized retries without that private key. It is never a correspondence-decryption key.


## Dedicated control-encryption keys

[Sealed controls](suite-profile.md#confidential-setup-and-control) use a separately generated recipient key with an immutable publication interval and receiving deadline. One Welcome consumes its MLS initialization key, not this independently scoped control key: several separately encapsulated controls can use it until retirement. Renewal uses new material and a new ID; retransmission retains original ciphertext and cannot extend a promise. Keep it outside correspondence archives, pairing configuration and credential-sync enrollment authority. Expiry enforcement, current authorization, protected local custody and actual erasure limits remain separate obligations.


## Account repair and retirement

The [state1 lifecycle](identity-state.md#concurrent-administration-and-retirement) keeps key custody distinct from authority. Repair neither extends a published setup/control-key deadline nor restores a consumed secret. Acquire new permitted publication/grant evidence across its fresh-authorization boundary. Explicit identity retirement records the terminal proof and invalidates operational grants/work before reporting retirement complete; prepare any permitted immutable notice before retiring unneeded signing keys. Actual erasure and ciphertext/history retention remain their own boundaries. Inactivity, password reset and billing cannot trigger that signed retirement by inference.


The [publication-renewal contract](security-profile.md#publish-replacements-without-disturbing-in-flight-mail) keeps new generation, uncertain upload, provider withdrawal, local key retirement and global identity authority distinct. Replacement publication does not shorten an old receiving promise or unspend an allocation. A restored snapshot cannot call previously issued material unused. Provider deletion stops its future disclosures, while still-valid cached setup requires the existing binding/device authority change for remote invalidation once learned.
