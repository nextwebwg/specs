---
title: Authorized history transfer
order: 9.5
blurb: exact recipient · approved history · fresh archive · no live authority
sectionNav: true
---

# Authorized history transfer

Adding a device permits future participation, not automatic access to every old message. A history transfer is a separate disclosure: a recipient requests it, the source approves an exact retained-history scope, and a fresh archive collection is encrypted specifically for that recipient.

The candidate `email2-history-transfer-v0` contract also permits deliberate history sharing with another principal under the existing disclosure policy. This is a forward by the sharing person, not a new statement or audience grant from every historical author. Neither route transfers live identity keys, conversation checkpoints, membership, votes or queued actions.

## Establish the participants first

The endpoints need independently accepted identity anchors and current device bindings before processing transfer records. A new history disclosure needs current `send` authority at the source and current `receive` authority at the target. A terminal result or cancellation checks its own actor's applicable current authority and its exact previously accepted parents; it does not need new permission from a peer whose binding has been revoked. Enrollment or group membership alone does not authorize history disclosure. An incoming record cannot install its own identity anchor or mailbox association.

The target creates and retains a separate native age X25519 identity for this transfer. Its public recipient is bound into the signed request. The source never obtains that private identity or reuses an old archive's recovery kit. It creates a fresh archive identifier and writer key, prepares the authorized history using [archive-v0](encrypted-archives.md) and [archive-set-v0](archive-sets.md), and encrypts every file to the requested recipient. The target combines its own private identity with the archive identifier and verifier from the accepted grant when interpreting that collection.

This recipient-selected setup is an explicit transfer binding of the existing file formats. It does not give the source a recipient decryption key or make the transfer identity an account credential. Retaining or retiring it is a historical-storage decision: deleting it does not erase already imported history, and keeping it permits reading the already released encrypted collection.

> [!ex] A new phone gets selected history
> The phone is already enrolled, but has no old conversations. The laptop recognizes its authorized device request and approves a selected account's history. The phone imports that correspondence from a recipient-specific encrypted collection. It still needs normal group admission for future traffic; the history files carry no account-administration or live conversation keys.

## One request, one approved grant, one result

| State | Required behavior |
| --- | --- |
| Requested | Target durably retains its private key, exact signed request and intended source. Requested account IDs constrain a proposal; an empty list asks the source to propose a scope and grants no disclosure permission. |
| Prepared | Source validates the request and current endpoint authority, selects a consistent scope and prepares fresh immutable archive files. Nothing is disclosed merely by receiving the request. |
| Approved | A local decision or explicitly applicable remembered policy covers the exact target, requested recipient, scope, metadata, catalog and external disclosure. Retain the signed grant and exact prepared bytes atomically with that decision. |
| Grant accepted | Target matches its retained request, validates the source and proposed scope, and pins the archive verifier only for this transfer. Acceptance follows the target's local storage/receiving policy; it does not change live identity pins. |
| Released/receiving | Before each new file handoff, source rechecks current authority, policy, validity and the immutable plan. Target checks exact descriptors in the accepted grant/catalog; unlisted files and arbitrary destinations cannot enter the transfer. |
| Imported | All collection checks and the complete historical publication succeed. Retain a local completion result before creating the signed result receipt. |
| Reported complete | Source validates the receipt against its exact retained grant. This means a client reports completed historical import, not that a person read the messages. No acknowledgement response follows. |

An account or device change that retains an accepted binding may preserve eligibility. A revoked binding, role loss, identity conflict or unresolved required evidence holds new release. A later timestamp or newer directory entry cannot authorize a substitution.

## Approve the exact disclosure

The source reviews the selected records and all included resource and original-mail metadata, including private-recipient information in originals. The approval may come from an already configured policy whose scope genuinely covers this transfer; a new dialog is not required for every retry. A request, a matching address or the recipient's possession of a key cannot supply source approval.

For another device of the same principal, permission to enroll and permission to transfer history remain separate. For another principal, apply the [forwarding/history rules](messages.md#conversation-history-and-forwarding) and actual new audience policy. Original author claims and protected historical context remain inspectable as historical evidence; the archive's writer signature does not independently authenticate every original person to the new reader.

The source validates its frozen plaintext inventory and selected records before encryption, retaining that binding through the export job. Receiver rejection after decryption cannot undo an accidental over-disclosure by a buggy exporter. Do not fetch new remote resources merely to make a historical export appear complete.

## Signed control records

The transfer identity is `(target principal, target device, transfer ID)`, scoped to the local source/target endpoint journal. Another authenticated requester cannot reserve or cancel that namespace by copying the ObjectId. Resolve the retained request under that identity, then compare its exact participants and signed-record references; a matching transfer ID alone is insufficient.

A record wrapper is exactly `{payload,signature}`. Payload is canonical padded base64 of the original strict UTF-8 JSON; signature is 128 lowercase hexadecimal characters encoding Ed25519. Decoded payloads are limited to 1,048,576 octets; encoded wrappers to 2,097,152 octets, both with maximum JSON depth 32 and the common scalar/duplicate-name rules. Bound the base64 input before decoding. Verify the original payload bytes, never a reserialization.

Signature input is ASCII `email2/history-transfer/<kind>/v0`, one zero octet, four-octet unsigned big-endian payload length and the original payload. Kind is exactly `request`, `grant`, `receipt` or `cancel`. A record reference is SHA-256 of that same framed input followed by the raw 64 signature octets. Wrapper whitespace or member order does not change the reference; changed signed bytes do.

An endpoint reference is exactly `{principal,device,state,binding,key}`: existing enp0/end0 identifiers, accepted identity-state digest, binding digest and raw Ed25519 signing key as lowercase hex. The last three encode 32 bytes. These are claims resolved against accepted local authority, not credentials by themselves. The referenced state must be an authenticated ancestor of the accepted current nonconflicted head, and the binding/key and required role must still be current. Bounded ancestry processing may hold use; it may not guess continuity.

::: {.details summary="Exact request, grant and receipt schemas"}

Each payload contains exactly its listed members. All ObjectIds use the nonzero 32-lowercase-hex grammar; all times are canonical uint64 epoch-second strings. The complete credible time interval must fit the request/grant interval for new authorization. Their intervals must fit the relevant binding validity; uncertainty holds rather than extending them.

| Kind | Exact members |
| --- | --- |
| Request | `version`, `purpose`, `transfer`, `source`, `target`, `recipient`, `accounts`, `receipt`, `notBefore`, `notAfter` |
| Grant | `version`, `purpose`, `transfer`, `request`, `source`, `target`, `scope`, `archive`, `set`, `verificationKey`, `catalog`, `complete`, `notBefore`, `notAfter` |
| Receipt | `version`, `purpose`, `transfer`, `grant`, `source`, `target`, `catalog`, `result`, `notBefore`, `notAfter` |
| Cancel | `version`, `purpose`, `transfer`, `request`, `grant`, `source`, `target`, `by`, `notBefore`, `notAfter` |

Version is `"0"`; purpose is `history-transfer-request`, `history-transfer-grant`, `history-transfer-receipt` or `history-transfer-cancel`. Transfer is the same fresh ObjectId throughout. Source and target endpoint references match the request exactly; their historical state references do not exempt current authority checks.

Request is signed by target. Recipient is one valid native age X25519 public recipient. Accounts is a sorted unique array of requested source account ObjectIds; empty means a scope proposal, not approval to share everything. Receipt is exactly `"import-result"`, explicitly selecting one result report for this flow rather than a general read receipt.

Grant is signed by source. Request is the exact signed-request reference. Scope is a nonempty sorted array of the archive-set account-scope records, with their exact selected entry counts/index digests. If requested accounts was nonempty, actual account IDs must be a subset of it. Archive and set bind the fresh collection; verificationKey pins its archive writer, not a live device. Catalog is exactly `{sha256,size}` for the complete encrypted catalog. Complete equals that catalog's complete flag. Grant validity must be contained in request validity. A grant cannot extend an expired request or change its recipient by omission.

Receipt is signed by target. Grant is the exact signed-grant reference. Catalog is its encrypted catalog digest. Result is exactly `"imported"` or `"imported-incomplete"`, matching the accepted catalog's completeness. Receipt validity is contained in grant validity. Only the target is the new actor: source resolves the request and grant from its already authenticated outbox, verifies their retained signatures and exact correlation, and checks the target's current authority. This can report an already completed import after the source binding was revoked, without permitting any new source release. The receipt is retained before upload and is terminal; a duplicate never generates another response.

Cancel is signed by the endpoint selected by `by`, exactly `source` or `target`. It names the retained request reference and either its exact retained grant reference or empty when stopping before the grant is known. The caller resolves these parents from its authenticated local journal, not from the cancellation message. An empty grant reference does not assert that a remote commit never occurred. Its interval is contained in the request interval. Cancellation checks the actor's current role and binding, not permission from a peer whose authority has been revoked; it can stop future access but cannot authorize new disclosure.

Each actor retains one immutable cancellation for this transfer. Concurrent valid cancellations have the same stop-future-release outcome and require no response. A terminal cancellation prevents a later arriving grant from reopening the request. Restarting requires a new transfer ID and request-specific recipient. An already completed import remains historical evidence; a cancellation cannot delete it or rewrite its result.

:::

## Carriage and file retrieval

Control records can travel through an explicitly enabled account-control channel or a selected local file exchange. A mail binding uses one direct `application/json` control attachment after a readable body in outer multipart/mixed, canonical base64 transfer encoding, and a filename used only as a hint. Do not search forwarded mail, quoted text or arbitrary descendants. Multiple candidate control parts leave automatic handling inactive. Legacy clients may display the attachment; there is no promise of invisible control mail.

Machine-sent grant/receipt/cancel responses use the applicable `Auto-Submitted: auto-replied` convention and this exact state machine. Unknown automatic traffic cannot start a request. Each valid request permits at most one immutable grant, and each admitted grant one retained result. Duplicate processing may retrieve an already retained record, but does not automatically send it again. Retransmission follows an explicit authorized retry, not a reply loop. A human-initiated file exchange has no automatic email semantics.

Endpoint addresses and any managed object-storage service are selected through already authorized local account configuration. None of these signed records contains a callback URL, mailbox password, service credential or retrieval endpoint. A terminal report may use an already authorized source route only while that retained mailbox association remains enabled at the selected generation; a revoked source device does not authorize sending even metadata to a reassigned mailbox. A storage adapter must authorize retrieval separately, confine it to the accepted transfer objects and retain immutable byte identities. This profile supplies the signed control and data formats; it does not reinterpret the configured public-evidence provider queue as permission to carry private history.

The target obtains the exact encrypted catalog named in the grant, verifies/decrypts it, then retrieves only its named parts. Check descriptors on retained ciphertext before decryption and import. Network transports may resume immutable objects under their own authenticated contract. If mail or storage limits prevent carriage, hold or choose another explicitly authorized transport; do not truncate, re-encrypt under the same identity, send plaintext or place a secret recovery kit in a notification.

## Import, interruption and revocation

Before publication, require exact agreement between grant and catalog on archive, set, account scope, completeness and encrypted catalog descriptor. Every part then follows full collection acceptance. Matching only account names or record counts is insufficient; compare the frozen entry commitments and exact resources.

Record target state as importing before attempting historical publication. If a process exits after archive-set publication but before the transfer journal records completion, a retry must reconcile the exact existing collection receipt and finish the journal without duplicate import or effects. Do not send an import receipt until that journal commit succeeds. A destination path is trusted local configuration, never a field taken from the control record.

Grant admission while current and valid establishes permission for this fixed historical artifact, not an ongoing subscription to future content. Later expiry or revocation stops new source handoffs and service retrieval under the grant; it cannot recall already released files or prevent reading previously admitted and retained history. Local processing of already retained bytes may finish under that admitted immutable grant without reactivating old identity authority. A late new grant cannot admit itself using expired evidence.

A newly generated or first-accepted result report still needs applicable current signature/authority and interval checks. If confirmation cannot be delivered before the control interval closes, source ends as expired without confirmation; target may still have readable imported history. Replaying a previously accepted exact receipt returns its historical result without renewing authority. A missing report proves neither a failed import nor human reading. A result report, whether present or absent, does not authorize deleting source history or the only remaining recovery material; deletion needs its separately applicable retention authorization.

Cancellation before source commit prevents a new grant. A cancellation arriving after commit cannot promise the grant or files were never released; stop future handoffs and record that uncertainty. Withdrawing an admitted grant revokes future service access and release, not downloaded plaintext. An unrelated signed identity claim cannot replace a participant or redirect a transfer. Authenticated ID collisions retain both records, hold the disputed transition and never overwrite a completed result.

## Evidence and acceptance

The [history-transfer experiment](evidence/README.md#authorized-history-transfer) checks original-byte control signatures, current identity-store authorization, explicit source approval, exact request/grant correlation, grant admission and recipient-bound collection import. Its release check is a local authorization transaction, not a production transport gate; actual final file handoff must recheck in its own serialized release path.

Acceptance must include same-principal device migration and explicitly authorized cross-principal disclosure; wrong recipient/key, scope or catalog; forged/replayed records; expired/uncertain intervals; role loss and revoked devices; changed identity branches; missing source approval; conflicting IDs; interruption before and after historical publication; exact retry; and the complete/omitted-history distinction. A successful transfer never installs identity pins, private account keys, MLS state or queued actions. Independently reviewed endpoint security and deployed mail/storage adapters remain separate evidence.
