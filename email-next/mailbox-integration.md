---
title: Mailbox integration
order: 6.5
blurb: account access · synchronization · protected message preservation
sectionNav: true
---

# Mailbox integration

A mailbox service stores and delivers messages; Email Next builds the conversation from the contributions inside them. Keeping those roles separate lets clients use an existing account without treating provider folders, threads or record identifiers as proof of authorship.

This chapter defines proposed adapter behavior for IMAP4rev2, JMAP core, JMAP Mail and the reviewed blob and sharing extensions. It does not require a provider to adopt JMAP or replace SMTP. The [transport chapter](transport.md) governs sending and retrying deliveries; this chapter governs access to stored messages and optional mailbox services.

The adapter has four jobs:

- Preserve original message bytes for verification, alongside convenient parsed views.
- Synchronize provider records without duplicating conversation contributions or actions.
- Respect account permissions without turning them into conversation membership.
- Report submission progress without claiming that acceptance proves delivery or reading.

> [!note] Implementation status
> These are proposed integration requirements. The source audits identify inherited behavior and remaining dependencies; a provider adapter and cross-provider acceptance runs remain unfinished. The [adoption plan](adoption.md#email-server-adoption) describes the evidence needed to claim support.

## IMAP access

An IMAP client can retrieve messages and learn about mailbox changes without a server upgrade specific to Email Next. It then verifies contributions locally and reconstructs the conversation. The mailbox remains usable by ordinary clients; IMAP does not supply an invisible control-message format.

> [!ex] A message moves to another folder
> Bob moves an answer from Inbox to a project folder. Its mailbox UID changes, but its authenticated contribution identity does not. The conversation still contains one answer, and moving it does not submit the answer again.

:::: {.details summary="IMAP adapter requirements"}

### Identifiers and synchronization

Scope cached UIDs by server/account, mailbox and UIDVALIDITY. A changed UIDVALIDITY requires resynchronizing that mailbox cache; it MUST NOT erase independently stored contribution identities, conflict evidence or replay protection. Sequence numbers change after expunge and MUST NOT serve as persistent contribution identifiers. A UID operation can succeed without finding a requested UID, so tagged success alone does not prove retrieval or mutation of that record.

Process unsolicited mailbox updates under the protocol's state and command rules. `IDLE` and `NOOP` report mailbox changes, not correspondent presence, message reading or key possession. After a disconnect, reconcile the mailbox before claiming a complete view. Mutable flags such as Seen are account state, not authenticated conversation actions.

### Retrieving verification inputs

Background conversation reconstruction SHOULD use non-marking retrieval such as `BODY.PEEK` so indexing does not itself mark messages read. Obtain the complete protected representation needed by the selected security profile before granting verified attribution or activating structured controls. A header search identifies candidates; substring matches cannot establish exact event identity.

Do not substitute server-parsed ENVELOPE, BODYSTRUCTURE, selected header fields or an incomplete byte range for the original verification input. `BINARY` retrieval decodes content and can normalize text line endings; its offsets are not interchangeable with BODY offsets. Preserve the received representation alongside any convenient decoded views.

### Storage, movement and submission

`APPEND` stores a message without an SMTP envelope and MUST NOT be presented as message delivery. Sending follows the [submission contract](transport.md). A stored Sent copy does not prove that submission succeeded, and its absence does not prove failure.

COPY and MOVE can assign new mailbox UIDs. Deduplicate recovered contributions by their authenticated identity and exact-byte rules, not by provider location. MOVE can partially succeed across a set; reconcile per-message outcomes before retrying. Removing or expunging a mailbox record is not a protocol withdrawal and cannot retract another recipient's copy.

Avoid unintended deletion during synchronization: `CLOSE` can expunge messages marked deleted by another client. Use `UNSELECT` when the intended operation is only deselection, where supported by the negotiated protocol. Do not delete ordinary messages merely because they resemble negotiation traffic.

### Capabilities and compatibility

Refresh capabilities after TLS or authentication changes as required by IMAP. Advertisement and enablement are separate: on a dual rev1/rev2 server, use the required explicit rev2 enablement before depending on its incompatible behavior. An IMAP capability does not establish recipient-device support for Email Next.

A rev1 adapter needs its own compatibility tests; passing rev2 cases is insufficient. Optional QRESYNC, CONDSTORE and OBJECTID support may improve synchronization, but their contracts and dependencies must be implemented separately. The [IMAP audit](audits/imap-access.md) records inherited rules, source discrepancies and required acceptance cases. No provider adapter is certified by this mapping.

::::

## Mailbox records and conversation identity

> [!ex] The same message in two accounts
> Alice keeps a message in her personal mailbox and a copy in a shared project mailbox. The mail service may assign different record identifiers to the copies. That does not create two independently authored contributions or authorize an interaction to run twice.

A mailbox adapter MUST scope a JMAP record identifier by service, account and data type. A record identifier alone is not globally unique. A JMAP account is a collection of data that may be shared by several users; access to that collection MUST NOT be treated as proof that those users are one Email Next principal.

Reconstruct conversation relationships from authenticated event identities and available message records, not from equality of provider record identifiers. Preserve the distinction between removing a mailbox copy and withdrawing a contribution under the conversation protocol.

When the service replaces an account identifier after rebuilding its data, invalidate the affected mailbox cache and resynchronize under the new account identifier. This MUST NOT reset independently maintained replay protection or silently establish a new correspondent identity. Reimporting a previously processed contribution must not repeat its external effects.

These adapter boundaries use the account and record scopes defined in [RFC8620 §§1.2–1.6](https://www.rfc-editor.org/rfc/rfc8620.html#section-1.2). Mailbox access authorization and endpoint-event authorization remain separate.

## Provider capabilities and session changes

A JMAP capability advertisement describes the authenticated service and, where applicable, the particular account. A sender MUST NOT infer recipient-device support, encryption keys or permission to perform a conversation action from a server-level capability. Before using an account method, check that account's advertised capability and opt into the extension in the request's `using` list. Unknown capability properties do not grant additional authority.

Treat the session state as an opaque change indicator. When it changes, refresh the session information and reconcile accessible accounts, permissions and service endpoints. A removed account or reduced permission must not trigger a retry against another account merely because it is marked primary. Primary-account selection is a service default, not a binding between a mailbox and an Email Next principal.

Apply the service's advertised request, upload and concurrency limits to that connection. These limits do not define conversation membership limits or authorize dropping authenticated history. The session and account capability rules are defined in [RFC8620 §2](https://www.rfc-editor.org/rfc/rfc8620.html#section-2).

## Discovering a mailbox service

Discovering a JMAP session URL does not itself authorize sending credentials to that URL. An adapter MUST authenticate the selected HTTPS service and restrict credential use to the endpoints authorized by its account authentication configuration. It MUST NOT copy an authorization header to a different origin solely because a discovery endpoint redirected there. A changed service location must satisfy the same credential-scope and transport requirements as the original location.

JMAP method-call identifiers correlate responses with requests; they are not deduplication tokens for conversation events. A method may emit more than one response with the same call identifier. An adapter MUST NOT interpret response count as the number of new contributions or use a repeated call identifier as proof that a retried mutation had no additional effect.

Service discovery and invocation formats are defined in [RFC8620 §§2.2–3.3](https://www.rfc-editor.org/rfc/rfc8620.html#section-2.2). Credential scoping and separation from event identity are Email Next adapter requirements.

## Partial mailbox operations

A JMAP request is not an all-or-nothing transaction. An HTTP success response can contain failed methods, and later methods still run after an earlier method fails. A method that changes several records can also return separate outcomes for those records. The adapter MUST inspect each applicable result before updating local state or declaring an operation complete.

On `serverPartialFail`, resynchronize the affected data before deciding which changes remain necessary. Preserve uncertainty when the response is lost: absence of a result does not prove absence of a server-side effect. Retry decisions must retain the original event identity and check current authorization rather than create a new contribution merely to repeat a mailbox operation.

Keep request rejection, method failure, individual record failure and unknown transport outcome distinct. A method-level error other than `serverPartialFail` guarantees no externally visible change by that method under the JMAP contract; it does not roll back other methods in the request. These failure scopes are defined in [RFC8620 §3.6](https://www.rfc-editor.org/rfc/rfc8620.html#section-3.6).

## Concurrent mailbox changes

Ordered method calls within one JMAP request do not provide an isolated snapshot. Other requests can change mailbox data between those calls. An adapter MUST NOT infer that a query and a later fetch observed one unchanged mailbox merely because they were sent together.

Use the applicable method's state and change contracts when reconciling results. A provider thread grouping or query order is a retrieval aid, not authenticated conversation membership or causal order. Missing or changed records must be handled without fabricating predecessors, resetting event replay state or assuming that a previously observed authorization still holds.

A JMAP result reference supplies an argument from an earlier response; it is neither an authorization proof nor a lock on that record. These concurrency limits follow [RFC8620 §3.10](https://www.rfc-editor.org/rfc/rfc8620.html#section-3.10).

## Incremental mailbox synchronization

JMAP state tokens identify synchronization states, not timestamps or conversation sequence numbers. A changes response may describe an intermediate state, and several responses may be needed to catch up. The adapter MUST apply each response to its matching local state and follow `hasMoreChanges`; it MUST NOT infer conversational order from the order in which those changes arrive.

Changes are not a complete activity log. A record created and deleted between synchronization points may be absent from the change list. The same record can also appear in more than one change category. Reconcile the resulting mailbox state rather than count each category entry as an independent message or interaction.

A `/get` response may reorder requested records and reports missing records separately. Match returned objects by their scoped identifiers, not array position. On `cannotCalculateChanges`, invalidate and rebuild the affected mailbox cache while retaining the independent event identity and replay safeguards described above. A provider record that is no longer available does not constitute an authenticated withdrawal of its contribution.

These synchronization rules follow [RFC8620 §§5.1–5.2](https://www.rfc-editor.org/rfc/rfc8620.html#section-5.1).

## Retrying mailbox mutations

When a mailbox change depends on previously observed state, supply the applicable `ifInState` precondition. On `stateMismatch`, refresh and reconcile the intended change; do not silently remove the precondition to force an outdated write through. This precondition covers the provider's data type and account, not the conversation's cryptographic identity state.

A JMAP `/set` operation is atomic per record, not across all records in the call. Preserve both successful changes and record-specific failures, including server-computed properties returned with successful updates. Retry only changes still required after reconciliation. A creation identifier is a request-local reference mechanism, not a persistent idempotency key; reusing it in another request does not prove that a create will be deduplicated.

These mutation semantics are defined in [RFC8620 §5.3](https://www.rfc-editor.org/rfc/rfc8620.html#section-5.3). They do not replace the separate atomicity requirements for committing authenticated conversation state and effects.


## Copying between accounts

A mailbox copy can succeed even when deletion of the original fails. Inspect both outcomes before presenting a move as complete. Preserve the new account-scoped record identity and reconcile any remaining source copy; do not treat it as a new authored contribution simply because its provider identifier changed.

Copying a record does not grant the destination account authority over its author or conversation. Access and decryption still depend on the applicable protection profile. A copy followed by deletion is not a transaction across accounts. These boundaries follow [RFC8620 §5.4](https://www.rfc-editor.org/rfc/rfc8620.html#section-5.4).

## Searching and paging through a conversation

A JMAP query state describes the ordered identifiers matching one type, filter and sort. It does not describe every property of those records. An unchanged query state MUST NOT substitute for record synchronization or establish that message content is unchanged.

Keep query caches scoped to the account, type, filter, sort and applicable query options that produced them. For Email/query, preserve the collapseThreads setting when requesting changes; collapsed and uncollapsed results are different views. On a changed query state, refresh the identifier list or apply a valid query change response to the matching prior state. If the server cannot calculate changes, rebuild that query cache. Missing anchors and unsupported filters are retrieval outcomes; they do not establish that the conversation or its messages no longer exist.

A query change may remove and reinsert the same identifier to reflect its changed position. Apply removals before ordered insertions as specified by JMAP. Removal from a search result MUST NOT be treated as deletion of the underlying message, withdrawal of an answer or revocation of a participant. A stable provider sort order likewise does not establish authenticated causal order. If a sparse query cache cannot place a removed identifier, invalidate and rebuild the affected query view rather than retain uncertain positions beyond its gaps. This is an Email Next adapter requirement addressing the ambiguity described in [reported erratum 6604](https://www.rfc-editor.org/errata/eid6604), not a claim that the proposed RFC correction has been approved.

These query rules follow [RFC8620 §§5.5–5.6](https://www.rfc-editor.org/rfc/rfc8620.html#section-5.5). Reconstruct the conversation from validated individual contributions, independently of how the mailbox service pages or sorts their records.


## Mailbox blobs and attachment authority

A JMAP blob identifier denotes immutable bytes within the provider's access model. It does not authenticate an attachment's filename, media type, author or intended audience. The download request supplies the desired filename and media type; verify the attachment against its authenticated contribution binding before presenting those properties as sender claims.

An uploaded blob can expire before it is attached to a mailbox record. Retain the local source until the intended operation succeeds, and reconcile a missing blob before reuploading. A successful upload is not evidence that an email was sent or that another participant can retrieve it. In shared accounts, unreferenced uploads remain accessible only to their uploader under JMAP's contract.

The provider may return a different blob identifier when reusing bytes in another object or copying them to another account. Preserve that mapping without changing the contribution's authenticated resource identity. Reusing existing bytes does not authorize forwarding them or expand their audience. The binary-data rules are defined in [RFC8620 §6](https://www.rfc-editor.org/rfc/rfc8620.html#section-6).


## Waking a client without another email

A JMAP push notification tells a client which account data may need synchronization. It is not a conversation contribution, a delivery receipt or proof that a correspondent is online. The client retrieves changes through its authenticated mailbox connection and validates individual contributions before applying their effects. Dropped, duplicated or coalesced notifications must not lose conversation state.

A push may arrive while a mailbox write is still in progress. Reconcile the returned state and the client's prior state before deciding that a further fetch is unnecessary. A notification state token is not an ordered counter; do not compare tokens numerically or use notification arrival order to choose between competing answers.

For subscriptions through a third-party push service, use the encryption required by JMAP and reject notifications that do not satisfy that protection. Protect subscription URLs and keys as device-private data. Subscription lifetime follows the credentials that created it; revoking those credentials must not leave a live notification channel. Subscription delivery proves neither ownership of an Email Next author identity nor consent to a new conversation participant.

A direct event stream avoids a separate push intermediary where the platform permits a persistent connection. Its reconnect cursor and ping events serve mailbox synchronization and connection health only. Neither is a conversation event identifier or a freshness proof for identity keys. These mechanisms are specified in [RFC8620 §7](https://www.rfc-editor.org/rfc/rfc8620.html#section-7), with third-party encryption requirements in [§8.7](https://www.rfc-editor.org/rfc/rfc8620.html#section-8.7).

An Email Next provider operating push callbacks must constrain outbound destinations and request rates, including verification requests. Verification proves receipt of a challenge, not that the destination is a safe service. Prevent access to internal services through destination resolution or redirects; retain those restrictions on subsequent requests. Push metadata encryption does not conceal traffic timing from observers.


## Optional blob and sharing capabilities

Negotiate JMAP extensions at their defined session and account scopes. Core JMAP support alone does not imply support for inline blob methods or principal-directory methods. A directory principal identifier remains scoped to its containing service and account; an editable name, email substring match or account-owner link cannot substitute for verified Email Next identity binding.

When using [JMAP blob management](https://www.rfc-editor.org/rfc/rfc9404.html), distinguish a complete attachment from a returned range. The returned size describes the whole blob, while a returned digest describes the selected bytes. A partial or truncated response MUST NOT satisfy a full-attachment integrity check. Validate the final assembled bytes against the contribution's authenticated resource binding. Provider-supported digest preferences do not override the selected content-protection profile.

Blob reverse lookup must preserve the protocol's indistinguishable result for inaccessible and nonexistent blobs. Neither finding a containing object nor having provider access grants permission to share its contents with a conversation. Composed uploads must be evaluated as their resulting bytes; validation of the component pieces does not establish safety of their concatenation.

Under [JMAP sharing](https://www.rfc-editor.org/rfc/rfc9670.html), an unsubscribed shared account may disappear from the session and its push updates without loss of access permission. Conversely, a stored sharing notification may outlive the permission it described. Fetch current permissions when the operation needs them, and validate encrypted-conversation membership independently. Dismissing a notification changes neither permission nor group membership.

Sharing notifications can be coalesced, expired, evicted or omitted for groups. They MUST NOT serve as a complete membership history or as proof that rights remained unchanged. Account-owner rights are implicit in JMAP sharing, so a shareWith map alone is not a complete audience. Mapping provider access to an Email Next audience requires an explicit authorized operation; merely discovering existing mailbox access must not add recipients or devices to encrypted content.


## Mail access, sending and new-message signals

JMAP Mail advertises mail access, submission and vacation-response support separately for each account. A client with access to a shared mailbox must not assume it can send as that account. Select the account and its supported submission identity explicitly; mailbox visibility does not authorize an Email Next author identity.

The advertised attachment-size limit measures unencoded attachment bytes. It does not guarantee that the resulting MIME message fits the server's separate message-size limit. Account for message bodies, headers and transfer encoding before submission, and preserve a server rejection without silently removing attachments or weakening protection.

The EmailDelivery push type signals new Email objects added to a store. It is not a delivery receipt from a conversation recipient, and there are no EmailDelivery retrieval methods. Use it to trigger ordinary mailbox synchronization when appropriate. A client that also needs read-state, deletion or other changes must synchronize those through the Email state contract rather than expect new-message notifications to cover them. These distinctions follow [RFC8621 §§1.3–1.5](https://www.rfc-editor.org/rfc/rfc8621.html#section-1.3).


## Provider thread changes and mailbox permissions

A provider's thread is a retrieval grouping, not the authenticated Email Next conversation. JMAP Mail permits different threading algorithms and orders a thread's messages by received date. It may merge threads by deleting and reinserting affected Email records with new identifiers. Preserve event deduplication across those provider-record changes: the same authenticated contribution must not apply an answer or reaction twice merely because it now has another mailbox identifier.

Retain the distinction between mailbox access and conversation authority. JMAP permits fetching an Email when at least one containing mailbox grants read access, while changing seen status or other keywords requires the corresponding permission across all containing mailboxes. Do not infer those write permissions from successful retrieval. Provider read flags and unread counts are display metadata, not signed read receipts or evidence of conversation completeness.

Removing a message from one mailbox does not necessarily delete its other memberships. A mailbox deletion configured to remove its messages can destroy records that have no remaining mailbox. A client must represent the intended mailbox operation accurately and must not translate it into an authenticated conversation withdrawal. These rules follow [RFC8621 §2](https://www.rfc-editor.org/rfc/rfc8621.html#section-2) and [§3](https://www.rfc-editor.org/rfc/rfc8621.html#section-3).


## Parsed mail is not the authenticated original

JMAP exposes useful decoded headers and body projections, but these are not substitutes for original message bytes. Even its raw header string form may replace invalid UTF-8 and must drop NUL octets. Text forms unfold whitespace, decode encoded words and normalize Unicode; address forms can discard comments and groups or recover incomplete addresses.

For checks that cover the original message or MIME representation, retrieve the Email object's raw-message blob and apply the selected verification procedure to those bytes. Do not reconstruct a signed message from parsed fields or feed a normalized display string into a byte-sensitive signature check. Preserve parsed values as display data with their separate provenance.

Individual JMAP header properties select the last matching field unless all instances are requested. A convenience From or Message-ID value therefore does not establish that the original contains only one such field. Checks that depend on uniqueness or header order must inspect all relevant original fields.

A best-effort parsed address may not be syntactically valid for delivery. Validate a proposed destination before sending, and establish identity through the selected security profile. A provider's parsed From value, mailbox keyword or received timestamp does not authenticate an Email Next author. These distinctions follow [RFC8621 §§4.1.1–4.1.2](https://www.rfc-editor.org/rfc/rfc8621.html#section-4.1.1).


## Body previews and interactive content

A JMAP body value can use heuristic charset decoding, normalize line endings and replace malformed text. Its truncation and encoding-problem indicators must remain attached to that projection. A truncated preview is not the complete question, answer, authorization statement or authenticated structured payload.

Before enabling an Email Next control, obtain and validate its complete structured contribution and required readable binding under the selected profile. Do not activate a control inferred from a provider preview, repaired text, attachment flag or flattened body list. A client may show a clearly identified preview while the complete content is unavailable, without presenting omitted content as verified or authorizing an action from it.

Provider textBody and htmlBody lists can contain multiple parts and overlap with the attachment list. Their decomposition algorithm is not mandated by JMAP. Preserve part identity and MIME context when resolving resources; do not duplicate a contribution because one part appears in several projections. A part identifier is local to its Email object. Attached message bodies require separate parsing and must not be merged into the enclosing author's contribution.

Unknown transfer encodings and charset repairs in provider projections do not relax Email Next's strict payload decoding. Use the original representation where those checks require it. These boundaries follow [RFC8621 §§4.1.3–4.2](https://www.rfc-editor.org/rfc/rfc8621.html#section-4.1.3).


## Expanding search results into a conversation

A collapsed JMAP Mail query returns at most one matching Email per provider thread, selected after filtering and sorting. It does not return the complete thread or prove that all conversation contributions are present. Use the representative to retrieve the accessible thread records as needed, then resolve authenticated Email Next relationships independently. Keep missing or inaccessible predecessors explicit.

Provider text search is a discovery aid. Matching rules can include case folding, tokenization, stemming and provider-specific indexing; a matching From search is not exact address verification. Absence from search results is not proof that an authenticated event never existed. A provider cannot be assumed to search plaintext that it cannot decrypt, so encrypted content search requires an explicitly defined client or service mechanism.

Fetching messages may return only some requested records and only the requested projections. Match by scoped identifiers, preserve notFound outcomes, and do not infer completeness from a returned preview or a collapsed result count. These search semantics are specified in [RFC8621 §§4.2–4.5](https://www.rfc-editor.org/rfc/rfc8621.html#section-4.2).


## Creating and importing protected messages

JMAP Email/set can generate MIME encodings and add headers, and an Email/import implementation may repair an invalid message. A successful create or import therefore does not alone prove preservation of a protected representation. Before submission, verify the stored representation required by the selected protection profile; if import returns a changed blob, retrieve it and determine whether the protected bytes and bindings remain valid. Do not silently reuse an authentication result for the original representation after a change.

A provider may reject an import or copy as already existing based on Message-ID alone. Treat the returned existingId as a candidate record to inspect, not proof of identical bytes or authenticated event identity. Retrieve and validate it before using it to satisfy the intended operation. A collision must not cause the client to submit unrelated content or report the intended contribution as delivered.

Email/parse can display an attached message without importing it into the mailbox. Its possible threadId predicts provider grouping; it does not establish that the message was received independently, belongs to the enclosing conversation or was authored by the person forwarding it. Preserve the attachment boundary and apply the normal authentication and action-authorization rules before any structured effects.

These creation, import and parsing behaviors are defined in [RFC8621 §§4.6–4.9](https://www.rfc-editor.org/rfc/rfc8621.html#section-4.6). Importing a message into a mailbox is separate from submitting it for delivery. Saving changed draft content may create a new Email record rather than mutate the original. Preserve the previous draft until creation of its replacement is confirmed; a create and an unconditional destroy in one request are not an all-or-nothing save. Reconcile concurrent draft versions instead of selecting one by response arrival order.


## Search highlights are display data

JMAP search snippets contain provider-generated text with mark elements for matching words. Render them through a restricted highlight parser or equivalent text-and-highlight representation; do not insert the returned string into a privileged application DOM as trusted HTML. No snippet can supply scripts, resource loads, links or action controls.

Associate each snippet using its emailId and account, not response position. A null snippet means no available highlight, not proof that the message lacks the searched content. Snippets can change without a state-update signal and remain separate from the authenticated message. The snippet contract is defined in [RFC8621 §5](https://www.rfc-editor.org/rfc/rfc8621.html#section-5).


## Submission identity and recipient status

A JMAP Identity supplies sending preferences and provider permission, not an Email Next cryptographic identity. Apply its suggested Reply-To, Bcc and signature before finalizing the authorized audience and protected content. An automatic archive Bcc must not silently add a reader after encryption policy has been selected. HTML signatures pass through the same content rules as other composed HTML.

Bind the selected submission envelope to the authorized transport recipients. If relying on provider-generated envelope defaults, verify that they preserve that selection; header-derived defaults and provider identity substitutions must not silently change who receives the contribution. A wildcard send-from permission does not establish a verified key binding for every address in that domain.

Keep submission acceptance, irreversible relay, final delivery and display claims distinct. A queued or unknown recipient status is not delivery confirmation. A provider-reported display status does not prove the recipient read or understood the message, and does not acknowledge a question or authorize an action.

A pending undo status means cancellation may be attempted, not that it will succeed. Show cancellation as confirmed only after the provider accepts it. The disappearance of an EmailSubmission record is not proof of cancellation or failure: providers may discard completed records, including immediately in simple proxy implementations. Preserve known outcomes and uncertainty without creating a fresh submission merely because the old record cannot be fetched.

These identity and status semantics follow [RFC8621 §§6–7](https://www.rfc-editor.org/rfc/rfc8621.html#section-6). DSN and MDN evidence retains its own authentication and interpretation limits.


## Submission side effects and automatic replies

Inspect both the EmailSubmission result and any implicit Email/set result. Sending can succeed while moving the stored message to Sent or clearing its draft flag fails. Retry only the remaining mailbox operation after reconciliation; do not resend a successful submission to repair its local filing state.

Deleting the stored Email or its EmailSubmission record does not cancel an accepted send, including a scheduled send. Use the provider's cancellation operation and inspect its result. A cannotUnsend response must not be presented as successful cancellation.

JMAP submission removes Bcc headers and permits other provider-policy alterations during delivery. Protection profiles must tolerate only their explicitly permitted outer-message changes; stored-byte validation before submission cannot prove that every downstream representation remains unchanged. Receiving clients still validate the delivered contribution independently. A provider alteration never authorizes weakening required encryption or silently changing the protected audience.

A provider vacation response is a separate automated message. It must not be represented as the user's structured answer, a key-verification response or consent to an action. Apply the existing automatic-response loop and disclosure rules. If the provider cannot meet the configured protection policy for automated replies, the client must make that limitation visible when configuring them; account access alone does not authorize release of endpoint encryption keys to generate a response.

Submission effects and vacation behavior are specified in [RFC8621 §§7.5–8](https://www.rfc-editor.org/rfc/rfc8621.html#section-7.5). An ordinary automatic reply does not gain Email Next authentication merely because it was triggered by an encrypted incoming message.


## Partial account views

A shared account can expose only part of its mailbox data. JMAP Mail requires inaccessible records to appear nonexistent, including hidden Email identifiers within Thread results. A client MUST NOT use a missing record to claim that a message was deleted or a participant was removed. Show only what the current access permits; do not fill gaps by probing other accounts or by sending an import designed to test for a hidden Message-ID.

A provider implementing duplicate detection must evaluate its information-disclosure behavior under partial access. An alreadyExists result can reveal a hidden record even when ordinary retrieval correctly hides it. Such a result is neither permission to inspect the record nor proof of a matching authenticated contribution. The partial-access requirement and duplicate-detection concern are documented in [RFC8621 §9.5](https://www.rfc-editor.org/rfc/rfc8621.html#section-9.5).
