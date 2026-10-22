---
title: Authorized history transfer
order: 9.5
blurb: exact recipient · approved history · fresh archive · no live authority
sectionNav: true
---

# Authorized history transfer

Adding a device permits future participation, not automatic access to every old message. A history transfer is a separate disclosure: a recipient requests it, the source approves an exact retained-history scope, and a fresh archive collection is encrypted specifically for that recipient.

The candidate `email2-history-transfer-v0` contract also permits deliberate history sharing with another principal under the existing disclosure policy. This is a forward by the sharing person, not a new statement or audience grant from every historical author. Neither route transfers live identity keys, conversation checkpoints, membership, votes or queued actions.

The [offline delivery contract](suite-profile.md#unread-mail-and-long-offline-periods) may offer this flow when a delayed encrypted delivery is no longer decryptable. The source must actually retain the requested historical content, and its exact source approval and current recipient checks remain required. Fresh enrollment, an old To address or an undecryptable attachment is not that approval. Import remains historical, not a replay of the unavailable live message.

## Recover an unopened delivery

If the original setup key is gone, the client may have only an opaque attachment. It can identify those exact bytes without knowing the message's author, conversation or text. After the reader selects an independently trusted source, a confidential history request can ask that source to find its own retained copy of that delivery.

The source shares only the matching retained content it separately authorizes. A copied attachment does not entitle its holder to the message, the rest of the conversation or anyone else's history. If the source cannot match the delivery safely, recovery waits or ends as unavailable. Fresh setup does not decrypt the old attachment.

::: {.details summary="Exact opaque-delivery selectors and source matching"}

A request's required `deliveries` array is empty for the ordinary account-history flow. Otherwise it contains one or more exact descriptors `{sha256,size}` for original sealed-control binary attachments: hash the complete MIME-transfer-decoded sealed binary, including its fixed header, encapsulated key and ciphertext. Do not hash MIME base64 text, headers, a whole email, parsed/reencoded data or a guessed inner event. The same binary delivered through an authorized relay has the same descriptor. Do not unwrap nested or forwarded messages to initiate recovery. Missing or evicted original bytes cannot yield a fabricated selector.

Each digest is lowercase SHA256; size is a positive canonical uint64 decimal string. Sort descriptors by digest, then numeric size; duplicates are invalid. Apply the signed request's existing total byte/depth and local processing bounds. The descriptors travel only inside the existing confidential signed history request; no new clear header, mailbox probe, public hash directory or callback is defined. The digest is a locator, not a signature or secret access token. A recipient must obtain current source identity, device, control key and route independently; the opaque attachment and its outer From or relay address cannot supply them. If no trusted source is known or no eligible confidential path exists, retain the unavailable delivery and offer independent contact instead of guessing a recovery destination.

The source matches every requested descriptor against its own immutable original prepared-delivery records, comparing both digest and exact byte count. Those records must bind the actual original sealed binary to the locally retained content inventory and the originally authorized recipient principal. Incoming ciphertext, an email header, a matching subject or caller-supplied event IDs cannot populate that index. Later repacking has different binary bytes and needs its own source-owned mapping. A missing, inconsistent or ambiguous mapping holds this targeted recovery; do not substitute all account history. Matching bytes establish no new authority.

For same-principal recovery, independently establish continuity from the originally authorized recipient principal to the current requesting principal and require the current target's receiving authority. A newly enrolled device still needs the source's exact disclosure approval; enrollment alone is insufficient. A different principal, including a newly created identity at the same mailbox, cannot use this targeted path as automatic continuity. Any deliberate cross-principal sharing requires its own separately approved ordinary history request with empty deliveries and explicit scope; do not silently relax the original targeted request.

A nonempty deliveries array narrows the export to the union of the matched original content entries and only their required retained resources and provenance. It never selects later conversation traffic, other recipients' copies, unrelated messages, live setup secrets or queued effects. Nonempty accounts is an additional account constraint, not an alternative that widens selection. Every requested delivery must match; otherwise hold this request rather than silently dropping a selector. Freeze the selected entry inventory, original mappings and target binding with the source approval and compare the exact archive scope/index commitments before release. A changed mapping, content inventory or target needs a fresh approval and immutable grant under the owning rules.

The grant's exact signed-request reference binds these selectors without adding them to each archive entry. The target checks that reference and the exact grant/catalog scope as usual, but cannot independently prove a plaintext-to-ciphertext relationship when its original key is gone. Show the result as a historical copy supplied by that source, preserving independently verifiable original signatures where present; matching a selector does not authenticate the unavailable original's author, thread or content. Historical import stays inert. If the original later becomes genuinely verifiable, apply existing exact-event commitment/conflict rules; neither the selector nor a source assertion permits duplicate live effects.

:::

## Establish the participants first

The endpoints need independently accepted identity anchors and current device bindings before processing transfer records. A new history disclosure needs current `send` authority at the source and current `receive` authority at the target. A terminal result or cancellation checks its own actor's applicable current authority and its exact previously accepted parents; it does not need new permission from a peer whose binding has been revoked. Enrollment or group membership alone does not authorize history disclosure. An incoming record cannot install its own identity anchor or mailbox association.

The target creates and retains a separate native age X25519 identity for this transfer. Its public recipient is bound into the signed request. The source never obtains that private identity or reuses an old archive's recovery kit. It creates a fresh archive identifier and writer key, prepares the authorized history using [archive-v0](encrypted-archives.md) and [archive-set-v0](archive-sets.md), and encrypts every file to the requested recipient. The target combines its own private identity with the archive identifier and verifier from the accepted grant when interpreting that collection.

This recipient-selected setup is an explicit transfer binding of the existing file formats. It does not give the source a recipient decryption key or make the transfer identity an account credential. Retaining or retiring it is a historical-storage decision: deleting it does not erase already imported history, and keeping it permits reading the already released encrypted collection.

> [!ex] A new phone gets selected history
> The phone is already enrolled, but has no old conversations. The laptop recognizes its authorized device request and approves a selected account's history. The phone imports that correspondence from a recipient-specific encrypted collection. It still needs normal group admission for future traffic; the history files carry no account-administration or live conversation keys.

## One request, one approved grant, one result

| State | Required behavior |
| --- | --- |
| Requested | Target durably retains its private key, exact signed request and intended source. Requested account IDs constrain a proposal; with empty deliveries, empty accounts asks the source to propose a scope and grants no disclosure permission. Nonempty deliveries restricts recovery to exact source-matched content. |
| Prepared | Source validates the request and current endpoint authority, selects a consistent scope and prepares fresh immutable archive files. Nothing is disclosed merely by receiving the request. |
| Approved | A local decision or explicitly applicable remembered policy covers the exact target, requested recipient, scope, metadata, catalog and external disclosure. Retain the signed grant and exact prepared bytes atomically with that decision. |
| Grant accepted | Target matches its retained request, validates the source and proposed scope, and pins the archive verifier only for this transfer. Acceptance follows the target's local storage/receiving policy; it does not change live identity pins. |
| Released/receiving | Before each new file handoff, source rechecks current authority, policy, validity and the immutable plan. Target checks exact descriptors in the accepted grant/catalog; unlisted files and arbitrary destinations cannot enter the transfer. |
| Imported | All collection checks and the complete historical publication succeed. Retain a local completion result before creating the signed result receipt. |
| Reported complete | Source validates the receipt against its exact retained grant. This means a client reports completed historical import, not that a person read the messages. No acknowledgement response follows. |

An account or device change that retains an accepted binding may preserve eligibility. A revoked binding, role loss, identity conflict or unresolved required evidence holds new release. A later timestamp or newer directory entry cannot authorize a substitution.

## Identity changes do not renew a history grant

A routine update affecting another device need not interrupt a transfer. Replacing a participant's binding, repairing a conflict or retiring an identity is different: an old request or grant cannot authorize a new history disclosure through that change. The participants must establish a fresh transfer from their currently accepted authority where the operation remains permitted.

Already admitted files retained by the recipient keep their historical-reading permission. They do not become live identity state, and a missing completion report does not mean import failed.

::: {.details summary="Authority paths and phase-specific continuation"}

For each new effect, resolve the original signed endpoint and current accepted nonconflicted head under one owning authority snapshot. Apply the [unchanged-binding procedure](provider-grants.md#retain-an-unchanged-device-binding): the complete accepted one-parent path back to the original anchor must preserve the exact device, binding digest, key and required role, with no revocation. State0 ordinary successors and state1 update/prune may preserve that evidence. A missing path, key/role/binding change, conflict, exhausted processing budget or crossing a repair/retirement boundary holds it. A fresh endpoint anchored at an accepted repaired head may obtain new authorization there; the prohibition concerns carrying earlier authority across that boundary. Do not choose a repair parent, substitute a current binding into an old signed endpoint or use delayed-control same-key renewal as a new history-disclosure permission. Original intervals, participants, recipient, scope and signatures remain immutable.

| Phase | Required continuation |
| --- | --- |
| New request/grant approval, grant admission or source file handoff | Both participants meet their applicable current send/receive and exact unchanged-binding path checks. Repair or binding replacement requires a fresh request/transfer/recipient and separately approved exact grant; eligible remembered disclosure policy may apply. Reusing the old identifier or archive kit is not that authorization. |
| Processing an admitted artifact already retained by the target | The admitted immutable grant and retained exact catalog/parts remain historical authority for local verification/import under the existing interruption/cancellation rules. No new source handoff, service retrieval, live identity or action permission follows. Missing bytes remain missing; admission alone does not claim they were retained. |
| New receipt or cancellation | Only its actual actor needs the applicable current role and unchanged-binding path, with original parent/interval checks. The peer's retained request/grant can remain historical evidence after peer revocation or repair; it grants no new disclosure. The independent confidential recipient key, association and route may nevertheless make delivery unavailable. An actor's own repair or changed binding cannot be bypassed by signing with an old key or rewriting the frozen endpoint. Retain the local outcome/stop and report it undelivered if no eligible terminal report can be issued. |
| Exact previously accepted result retrieval | Return only the original historical outcome under actual local/transport access permission. It does not extend a grant, re-import history, refresh authority or establish present storage health. |

Recheck relevant current heads, original path, source approval, transfer state and deadlines at final file/control release, not just when the grant was prepared. Preserve released or uncertain outcomes and the old transfer's evidence when starting any fresh independently approved transfer. Neither repair nor a new grant recalls previously disclosed bytes. Expired or unavailable reporting ends without confirmation rather than inventing success/failure, issuing an automatic replacement report or deleting source history.

:::

## Approve the exact disclosure

The source reviews the selected records and all included resource and original-mail metadata, including private-recipient information in originals. The approval may come from an already configured policy whose scope genuinely covers this transfer; a new dialog is not required for every retry. A request, a matching address or the recipient's possession of a key cannot supply source approval.

For another device of the same principal, permission to enroll and permission to transfer history remain separate. For another principal, apply the [forwarding/history rules](messages.md#conversation-history-and-forwarding) and actual new audience policy. Original author claims and protected historical context remain inspectable as historical evidence; the archive's writer signature does not independently authenticate every original person to the new reader.

The source validates its frozen plaintext inventory and selected records before encryption, retaining that binding through the export job. Receiver rejection after decryption cannot undo an accidental over-disclosure by a buggy exporter. Do not fetch new remote resources merely to make a historical export appear complete.

## Select messages without silently selecting the conversation

A history share transfers exact retained records. Selecting Bob's answer does not also select Alice's earlier question, every person in the original audience or the rest of the discussion. If the selected record already contains a quotation, an audience list or other metadata, those bytes are part of the disclosure. An exporter cannot hide them from the new reader by hiding them in its preview.

If sharing the original record would reveal too much, omit it or deliberately compose a new forward containing only authorized passages and resources. Do not edit an original signed contribution, retain its old identity and present the result as an exact historical copy. A new forward is attributed to its actual sender. The [new-audience reply rules](reply-intent.md#change-the-audience-while-writing) apply independently of history transfer.

::: {.details summary="Frozen selection, dependency closure and preflight"}

Apply this selection procedure before approving the grant or handing plaintext to encryption or transport:

1. Select entries from one consistent retained source view. Freeze the exact entry IDs, account scope and original object bytes. A partial selection is `selected`, not `all-retained`. Do not interpret a conversation identifier, reply parent, source chunk reference or matching subject as a request to include another message.
2. Include the selected entries' exact object bytes and explicitly selected resource mappings. For a supported operation, validate its complete resource inventory and every included digest/size; unavailable or deliberately excluded declared resources require explicit omissions. Unsupported records remain opaque: their writer-associated objects require disclosure review, and an unfamiliar field cannot supply trusted chunk boundaries or select active semantics.
3. Resolve archive entry dependencies explicitly. Each retained evidence reference must name an included evidence entry in the same account. Each retained original-mail relation must name an included contribution in that account, or be empty when no relation is claimed. Do not discover and append every original-mail entry merely because it points at a selected contribution. If the proposed selection lacks a required dependency, hold that proposal for an explicitly authorized closure or prepare a new archive-entry association that truthfully omits it. Changing an archive-writer association is not permission to modify the original event or claim verification that the omitted evidence would have supplied.
4. Review the complete resulting disclosure, including dependency objects, original MIME headers/bodies, quoted passages, source audience and private-recipient metadata, file metadata and omission reasons. A minimal rendered preview cannot authorize undisplayed original bytes. If policy does not permit those exact bytes, narrow the proposal or hold it; do not silently broaden a requested scope to make the archive valid. Admission proofs are separately covered by the [membership disclosure contract](group-conversations.md#membership-evidence-is-also-a-disclosure).
5. Freeze that approved selection and its exact entry/object/index commitments before partitioning, signing or encryption. Validate all selected object integrity, contribution references and supported resource bindings at the source, not only on import. A changed source view, dependency or object cannot reuse the previous approval or grant. An exact retry uses the retained original artifacts; an independently authorized revised selection needs a fresh transfer and grant.

For asynchronous messages, select the original authored record through the [authored-history mapping](encrypted-archives.md#preserve-messages-that-have-several-deliveries). A delivery selector can locate that record through the source-owned prepared-delivery index; it does not make the delivery event the contribution identity. Separately selected delivery evidence and original mail remain part of the exact disclosure review.

The closure is the approved archive inventory, not a recursive conversation walk. It grants no fetch permission for absent messages or resources. Archive signing proves the selected writer's representation; it does not prove original-author acceptance, completeness of unselected history or consent from each historical participant. Receiver checks remain required even after source preflight.

:::

## Signed control records

The transfer identity is `(target principal, target device, transfer ID)`, scoped to the local source/target endpoint journal. Another authenticated requester cannot reserve or cancel that namespace by copying the ObjectId. Resolve the retained request under that identity, then compare its exact participants and signed-record references; a matching transfer ID alone is insufficient.

A record wrapper is exactly `{payload,signature}`. Payload is canonical padded base64 of the original strict UTF-8 JSON; signature is 128 lowercase hexadecimal characters encoding Ed25519. Decoded payloads are limited to 1,048,576 octets; encoded wrappers to 2,097,152 octets, both with maximum JSON depth 32 and the common scalar/duplicate-name rules. Bound the base64 input before decoding. Verify the original payload bytes, never a reserialization.

Signature input is ASCII `email2/history-transfer/<kind>/v0`, one zero octet, four-octet unsigned big-endian payload length and the original payload. Kind is exactly `request`, `grant`, `receipt` or `cancel`. A record reference is SHA-256 of that same framed input followed by the raw 64 signature octets. Wrapper whitespace or member order does not change the reference; changed signed bytes do.

An endpoint reference is exactly `{principal,device,state,binding,key}`: existing enp0/end0 identifiers, accepted identity-state digest, binding digest and raw Ed25519 signing key as lowercase hex. The last three encode 32 bytes. These are claims resolved against accepted local authority, not credentials by themselves. The referenced state must be an authenticated ancestor of the accepted current nonconflicted head through the [purpose-specific unchanged-binding path](#identity-changes-do-not-renew-a-history-grant), and the binding/key and required role must still be current. Finding the digest somewhere in a repair DAG is insufficient. Bounded ancestry processing may hold use; it may not guess continuity.

::: {.details summary="Exact request, grant and receipt schemas"}

Each payload contains exactly its listed members. All ObjectIds use the nonzero 32-lowercase-hex grammar; all times are canonical uint64 epoch-second strings. The complete credible time interval must fit the request/grant interval for new authorization. Their intervals must fit the relevant binding validity; uncertainty holds rather than extending them.

| Kind | Exact members |
| --- | --- |
| Request | `version`, `purpose`, `transfer`, `source`, `target`, `recipient`, `accounts`, `deliveries`, `receipt`, `notBefore`, `notAfter` |
| Grant | `version`, `purpose`, `transfer`, `request`, `source`, `target`, `scope`, `archive`, `set`, `verificationKey`, `catalog`, `complete`, `notBefore`, `notAfter` |
| Receipt | `version`, `purpose`, `transfer`, `grant`, `source`, `target`, `catalog`, `result`, `notBefore`, `notAfter` |
| Cancel | `version`, `purpose`, `transfer`, `request`, `grant`, `source`, `target`, `by`, `notBefore`, `notAfter` |

Version is `"0"`; purpose is `history-transfer-request`, `history-transfer-grant`, `history-transfer-receipt` or `history-transfer-cancel`. Transfer is the same fresh ObjectId throughout. Source and target endpoint references match the request exactly; their historical state references do not exempt current authority checks.

Request is signed by target. Recipient is one valid native age X25519 public recipient. Accounts is a sorted unique array of requested source account ObjectIds. Deliveries is the required descriptor array defined above: empty selects ordinary account-history negotiation; nonempty selects exact opaque-delivery recovery, additionally constrained by any requested accounts. Empty accounts alone never authorizes all history. Omitting deliveries is not a current request: retain the original as unsupported rather than inserting a default under its existing signature. Receipt is exactly `"import-result"`, explicitly selecting one result report for this flow rather than a general read receipt.

Grant is signed by source. Request is the exact signed-request reference. Scope is a nonempty sorted array of the archive-set account-scope records, with their exact selected entry counts/index digests. If requested accounts was nonempty, actual account IDs must be a subset of it. Archive and set bind the fresh collection; verificationKey pins its archive writer, not a live device. Catalog is exactly `{sha256,size}` for the complete encrypted catalog. Complete equals that catalog's complete flag. Grant validity must be contained in request validity. A grant cannot extend an expired request or change its recipient by omission.

Receipt is signed by target. Grant is the exact signed-grant reference. Catalog is its encrypted catalog digest. Result is exactly `"imported"` or `"imported-incomplete"`, matching the accepted catalog's completeness. Receipt validity is contained in grant validity. Only the target is the new actor: source resolves the request and grant from its already authenticated outbox, verifies their retained signatures and exact correlation, and checks the target's current authority. This can report an already completed import after the source binding was revoked, without permitting any new source release. The receipt is retained before upload and is terminal; a duplicate never generates another response.

Cancel is signed by the endpoint selected by `by`, exactly `source` or `target`. It names the retained request reference and either its exact retained grant reference or empty when stopping before the grant is known. The caller resolves these parents from its authenticated local journal, not from the cancellation message. An empty grant reference does not assert that a remote commit never occurred. Its interval is contained in the request interval. Cancellation checks the actor's current role and binding, not permission from a peer whose authority has been revoked; it can stop future access but cannot authorize new disclosure.

Each actor retains one immutable cancellation for this transfer. Concurrent valid cancellations have the same stop-future-release outcome and require no response. A terminal cancellation prevents a later arriving grant from reopening the request. Restarting requires a new transfer ID and request-specific recipient. An already completed import remains historical evidence; a cancellation cannot delete it or rewrite its result.

:::

## Carriage and file retrieval

Current Email/2 history-transfer controls use the [sealed control carrier](suite-profile.md#confidential-setup-and-control) below. The source and target retain the original signed records inside it. A readable notification contains no participant names, account scope, archive verifier, transfer reference or history details. Encrypted archive files remain separate from control records and never contain live enrollment authority.

::: {.details summary="Current encrypted control and archive-file carriage"}

### Exact control dispatch

The sealed intent kind determines one original signed history record and actor:

| Intent kind | Original record | Sender and required role | Recipient |
| --- | --- | --- | --- |
| history-request | request | target, receive | source device |
| history-grant | grant | source, send | target device |
| history-receipt | receipt | target, receive | source device |
| history-source-cancel | cancel with by:source | source, send | target device |
| history-target-cancel | cancel with by:target | target, receive | source device |

Body is the complete original strict JSON wrapper `{payload,signature}`, in canonical padded base64 in the intent. Preserve its bytes, signature domain and record reference. Source/target endpoint references and cancellation by must agree with this table; the sealed sender principal/device/state/binding and its accepted signing key match the original record's actual actor. The selected control-key owner, independent recipient and sealed recipient match the other exact endpoint. Check those bindings before encryption, not only after disclosure. A valid sealed signature cannot substitute for the original history signature or its owning validator.

The credible creation/release interval fits both the original record interval and selected key/actor authority. Repacking or renewing a control key does not extend request/grant/receipt/cancel deadlines, change participants or revive an expired transfer. Re-encrypting one original signed record to fresh eligible material for the same exact intended device follows sealed-control preparation and immutable-record deduplication. Another device needs its own approved transfer, not substitution of its key into an old grant.

Every current mailed control uses the existing two-part sealed-control MIME layout: generic notice, then one canonical-base64 application/vnd.email2.sealed-control attachment, without a filename or a second clear proof. Apply current selected sender/recipient masking and exact source route authorization. No clear application/json sibling, multipart alternative, callback, subject hint or automatically reflected mailbox advertisement is permitted. A control attached to forwarded mail, quoted text or an arbitrary descendant cannot activate this flow. Multiple candidate controls remain inactive. Legacy clients may display the opaque attachment; invisible protocol mail is not promised.

After full HPKE/final intent-signature validation, invoke only the selected history validator on the original wrapper. It must check the original history signature, current applicable actor authority, independently retained participants, exact retained request/grant parents, source disclosure approval and journal state before an effect. Bind sealed acceptance and history transition identities atomically with the owning effect or retained pending job. Neither HPKE success nor a transport receipt approves history, installs a verifier globally, advances a transfer or reports import. Different capsules of one exact original history record do not create another grant/import/result. Conflicting authenticated records remain conflict evidence under the original transfer namespace.

The outer carrier needs its own eligible recipient control key, association, route and current authority. The terminal-record exception above removes the need for new peer permission in the history state machine; it cannot bypass a revoked/expired recipient key or route. If no eligible confidential return carrier exists, retain the result/cancellation locally and report it as undelivered. An independently authorized confidential local file exchange may carry the original record; a missing network path never authorizes a clear mailed substitute. No automatic response follows a terminal record.

### Encrypted file handoff

The accepted grant names one exact encrypted catalog; that catalog names the encrypted part descriptors. Transfer one complete ciphertext object per mail using outer multipart/mixed with a generic text notice followed by exactly one application/octet-stream attachment, canonical MIME base64, no filename, personal subject, clear archive/scope metadata or recovery kit. The transfer decoder applies mailbox/transport processing bounds before allocation. Select the exact expected object through retained local transfer work and compare both ciphertext digest and byte count before decryption; MIME headers or a sender-chosen name cannot select a new transfer, verifier, destination path or live authority. If more than one retained transfer names identical bytes, one immutable stored object may satisfy each independently admitted reference; it does not merge grants or scopes.

Unrequested objects, unmatched/oversized bytes, multiple attachments and nested candidates cannot start automatic decryption/import or an answer. Retain or reject them under local mailbox policy without emitting a receipt. An incomplete transport object is not an accepted prefix. For each new file handoff the source uses the immutable grant-approved bytes and rechecks current authority, original deadlines, selected destination/account generation, disclosure and route policy at the [final body-release boundary](transport.md#the-final-body-release-decision), including after intervening transport waits. Transport uncertainty resumes the same object/work identity; it does not regenerate an archive or declare an import complete. Receiving retained bytes after grant expiry follows the admitted-artifact boundary below, never admission of a new expired grant.

A separately enabled account-control service, managed object store or confidential local file exchange may carry exact controls/ciphertexts under its own independently authorized transport. This specification adds no generic provider-control upload endpoint. Mail size limits can hold delivery or lead to an explicitly selected supported transport. Content must not be truncated or converted to plaintext. Archive encryption hides contents, not ciphertext length/timing, transport addressing or the fact that files are exchanged; address masking has its own provider-boundary limits.

:::

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

Targeted recovery acceptance additionally covers MIME line-ending/base64 wrapping changes versus changed sealed bytes; a copied ciphertext requested by another principal; a new device without source approval; missing/ambiguous original mappings; matching digest with wrong size; multiple selectors with one missing; unexpected account scope; source content no longer retained; fresh setup with original keys gone; unknown source/relay address; independently pinned source provenance; and an eventual original arriving after historical import. Parser and trusted-index selection checks alone do not establish a complete current-suite recovery journey.

Acceptance must include same-principal device migration and explicitly authorized cross-principal disclosure; wrong recipient/key, scope or catalog; forged/replayed records; expired/uncertain intervals; role loss and revoked devices; changed identity branches; missing source approval; conflicting IDs; interruption before and after historical publication; exact retry; and the complete/omitted-history distinction. A successful transfer never installs identity pins, private account keys, MLS state or queued actions. Independently reviewed endpoint security and deployed mail/storage adapters remain separate evidence.
