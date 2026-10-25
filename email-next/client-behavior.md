---
title: Client behavior and conformance
order: -0.5
blurb: required client behavior · protocol bindings · complete conversation flow
sectionNav: true
---

# Client behavior and conformance

An Email/2 client implements a conversation platform, not a collection of unrelated mail extensions. Following this specification should determine how the client receives, reconstructs, displays and answers a conversation, including what happens when delivery, identity or rendering fails.

This chapter defines the proposed observable client contract. The linked chapters own exact schemas, selected protocol versions, algorithms and failure rules. These requirements do not establish that the supplied experiments implement a complete client. Candidate bindings that remain unfinished must be completed before advertising the corresponding support; a requirement here does not silently widen an existing negotiated tuple.

A client claiming Encryption follows the [current asynchronous baseline](suite-profile.md#current-client-baseline), including explicit slot-based reply intent, fixed readable contributions and independent delivery outcomes. Older envelope4/5 descriptions retain their exact compatibility scope. Provider carriage and optional interaction roles keep their own obligations.

## Base behavior and module-dependent requirements

An Email/2 client implements the Conversations base and identifies the optional [modules](modules.md) it supports. The table below describes the complete protected conversation bundle; interaction and protection rows apply only when the corresponding module is implemented and selected. Omitting an optional module is legitimate. Claiming that module without its required safety behavior is not. Transport providers have separate roles and need not implement a user interface or decrypt messages.

| Component | Required behavior | Authoritative contract |
| --- | --- | --- |
| Existing-mail carriage | Submit, retrieve and retain messages through an existing account integration; preserve protected payloads and report delivery uncertainty | [Transport](transport.md), [messages](messages.md) and each selected MIME carrier |
| Protected event processing (Encryption) | Validate identities, immutable event bytes, exact references, duplicates and collisions before applying effects | [Event identifiers](event-identifiers.md), [encoding](event-encoding.md) and [interaction state](interaction-state.md) |
| Conversation reconstruction | Assemble contributions and branches from exact reply relationships; keep new writing separate from included quotation context | [Reply content](reply-content.md) and [legacy reconstruction](rendering.md) |
| HTML/CSS presentation | Render the mandatory finite vocabulary with resource isolation and accessible client-owned controls | [Required presentation](presentation-profile.md#required-presentation) and [rich messages](rich-messages.md) |
| Composition | Retain an explicit sender, audience, reply target and draft; freeze an immutable send intent on Send and finalize each planned scoped contribution once under its selected agreement | This chapter, [messages](messages.md) and [reply content](reply-content.md) |
| Conversation interactions (selected modules) | Answers supports questions/answers together; Reactions supports reaction/withdrawal together; Corrections supports the selected plain-message edit. Enable each only in its negotiated agreement | [Messages](messages.md), [reactions](reactions.md) and [interaction state](interaction-state.md) |
| Conversation protection (Encryption) | Establish and process the selected MLS conversations, including device and group authority, delayed delivery and recovery outcomes | [Security profile](security-profile.md), [identity lifecycle](identity-lifecycle.md), [groups](group-conversations.md) and their selected bindings |
| Delivery policy | Respect remembered protection requirements and explicit disclosure decisions; accurately distinguish ordinary, hosted and protected copies | [Delivery policy](delivery-policy.md), [private copies](private-copies.md) and [protected labels](managed-presentation.md) |
| Local state | Preserve received originals, accepted events, conflict evidence and unsent drafts across ordinary restart; commit effects under the owning protocol's durable-state rules | [Transport](transport.md), [interaction state](interaction-state.md) and [identity lifecycle](identity-lifecycle.md) |

Provider-assisted discovery/control, hosted-access operation and service-endpoint submissions are separately negotiated extensions. A client that supports one implements its complete authorization, retry and failure contract. A client without it retains the defined unsupported or held state and an available authorized alternative; it must not simulate successful execution. General forms and rich-content editing beyond the selected correction operation remain outside the initial client contract.

The suite selects protocols rather than every possible backend. An account adapter may use an applicable IMAP/submission or JMAP integration without requiring every client to implement both. The adapter must preserve the same observable carriage, storage and authorization behavior. The [protected conversation agreement](suite-profile.md) fixes the protected core, common readable application and each device’s independent interactive capabilities. Public provider discovery has a contract, while public bootstrap/relay integration and joined suite implementation remain separate work identified in [contract coverage](interoperability.md#contract-coverage-and-remaining-decisions).

## Receive once, derive views

On receipt, the client retains the original and runs the selected carrier, authentication, identity, audience and event-validation procedures before enabling structured effects. Parse failures and unauthenticated claims remain distinguishable from accepted contributions. Delivery, successful decryption, accepted application state and human reading are separate facts.

The accepted event store is the source for derived conversation, answer and reaction views. Repeated delivery of the same accepted event does not create another visible contribution or repeat an external action. Conflicting bytes under an authenticated event identity retain conflict evidence and follow the owning conflict rules. Missing dependencies remain pending and are recomputed when valid evidence arrives.

The conversation view shows each contribution's own content. It does not need a transcript copied into the newest email. Source quotations, reply-parent edges and interaction targets remain separate relationships. The [assembly procedure](reply-content.md#assemble-the-conversation-from-contributions) determines exact structured relationships; the [legacy procedure](rendering.md#reconstruction-procedure) supplies reversible, visibly uncertain interpretation of older email. Neither subject similarity nor matching words establishes protected identity or authority.

## People and conversation lists

The default conversation list identifies people rather than using a workspace channel model. A locally known participant uses the reader's contact name. A conversation with several participants shows a list of participant names; the full audience remains inspectable when space requires truncation. For an unknown participant, show an available name with its address or identity accessible for inspection. A sender-supplied display name cannot establish contact status or override an authenticated principal.

The default list provides separate **Contacts** and **Other** views. A conversation belongs in Contacts only when every other participant is associated with a local contact through the identity or mailbox evidence applicable to that conversation. Otherwise it belongs in Other. Local contact association is not cryptographic verification; a legacy contact remains an ordinary-email identity. Unknown or unresolved associations must not borrow protected identity from a similarly spelled address or name.

Conversation lists put the most recently active conversation first. Default activity is the local acceptance of a new visible message, question, answer or correction, or a new local send of such a contribution. Reactions, retries, background control records, historical backfill and duplicate receipt do not independently promote a conversation. Record a durable local activity sequence, with a stable conversation-key tie-breaker, so reopening the application does not reshuffle equal entries. Sender dates do not control this sequence. Local list order is not a claim of authenticated causal order and need not be identical across devices.

A client may expose other sorting and grouping preferences. Those preferences must not change conversation identity, audience, membership or interaction targets.

## Reading conversations and branches

Render messages in an open content layout that accommodates the permitted rich content. Each contribution has a client-owned author header, an inspectable protection state and an accessible reaction affordance associated with that exact contribution when Reactions is selected. Unsupported interactions must not appear usable. Repeated author headers may be visually compacted, but authorship and message boundaries remain recoverable. Sender-authored HTML cannot supply these controls or restyle identity and protection labels.

Protection inspection follows the [endpoint trust procedure](security.md#show-the-protection-actually-established): distinguish cryptographic acceptance, known service access, unknown runtime properties and independent identity/address assurances. Identify a known decrypting or readable-hosting service without suggesting that every relay has plaintext. Sender-authored labels cannot hide this client-owned state. A hosted-holder observation carried later in a protected conversation remains an observation of a host-mediated reply; its new encryption does not erase the host's earlier access or verify the link holder.

Preserve multiple root contributions and the branches that reply to them. Opening a branch focuses its root and descendants, with a way to return to the broader conversation. It does not move messages to a different audience or rewrite their reply relationships. A missing parent remains unresolved, not a guessed root. Late arrivals and reprocessing preserve the reader's position and expansion choices where practical.

Quoted context follows the explicit verification and collapse rules. All authored chunks remain in order. A collapsed quotation has an immediate expansion affordance, and the complete original is available separately. Legacy quotation detection never destroys the source or hides ambiguous material as if it had been verified.

The HTML/CSS profile is required. Compatibility text and user-selected simpler reading views do not create a text-only conformance class. Unsupported or invalid content follows diagnostic recovery, without active controls or a false claim that the required presentation succeeded.

## Declared reply intent

An explicit reply contract tells the reader whether the selected contribution invites discussion, private replies or no replies. The sender need not encode that decision in a mailbox name such as `no-reply`. To/Cc roles alone do not establish this contract.

| Declared intent | Client behavior |
| --- | --- |
| Discussion | Offer a reply to the explicitly declared discussion participants. A separate private reply is available only when the contract permits it. |
| Private replies | Offer a reply to the declared eligible person, without Reply all. Keep the resulting exchange private. |
| No replies | Offer neither a private nor group reply action for this contribution. Explain the absence when needed without presenting a disabled control as usable. |

Reply intent governs composition. An independently authorized answer button, reaction or service action retains its own operation rules; no-replies does not silently disable or authorize it. A no-replies contribution does not revoke group membership, disable earlier messages or erase existing conversations. It cannot prevent someone from deliberately composing a separate message through another path.

> [!note] Observable contract; authenticated binding required
> The current [authored-record binding](event-encoding.md#asynchronous-authored-records-and-deliveries) carries slot reply-intent1; the [reply-intent contract](reply-intent.md) defines its written-response behavior and retained intent0/envelope5 compatibility. Current [acquisition](first-contact-setup.md#acquisition-for-independently-ready-deliveries) and [delivery lifecycle](delivery-policy.md#complete-a-pending-delivery) are specified separately. These contracts do not establish a complete implementation. Do not infer intent from To/Cc, outer Reply-To or a familiar mailbox; private-audience separation remains mandatory.

## Private exchanges beside a group discussion

A private reply belongs to its actual audience, even when it concerns a message in a group discussion. A client may open a separate personal conversation or show a private branch beside the discussion. In either layout, keep the private exchange visibly separate from the shared timeline. Its presence must not imply that other discussion participants received it, can read it or see the same conversation view.

The private branch has its own audience heading and composer. Identify the actual people, such as **Only you and Alice**, rather than relying on a lock, color or a small “Private” badge. A lock describes protection; it does not identify who receives the writing. When the composer opens, show its destination before typing. Retain that destination across arrival of group messages, selection changes and draft restoration. Subsequent replies stay in the private exchange until a separately authorized audience change is deliberately chosen.

> [!ex] One topic, two exchanges
> Alice writes to Bob and Carol. Bob chooses to contact Alice privately. Bob's writing appears in the Alice–Bob exchange, with an Alice–Bob composer. Carol's view contains neither the private message nor a placeholder revealing that it exists. If Alice answers Bob there, the answer stays with Bob; receiving another group message does not switch her private draft back to the group.

A local connection to the source discussion may help the person who already has access find the context. It is not a shared reply edge, permission to fetch the source or authorization to copy it into a different audience. The current [primary-reply graph](reply-content.md#assemble-the-conversation-from-contributions) rejects cross-conversation parents. Starting a separate private conversation therefore creates a root under its own context; it must not transmit the old group's EventReference as an ordinary reply parent. Deliberately included quotation follows the existing disclosure rules. Do not automatically copy a full transcript, participant list, group subject, identifiers, attachments or active controls merely to explain the local connection.

Legacy mail does not establish a group-discussion contract merely by listing several To/Cc recipients. Keep the actual recipients and the difference between Reply and Reply all inspectable. Subject grouping and quotation cleanup cannot turn an inferred audience into authenticated reply authority. Current slot reply-intent1 supplies the explicit signal under its authenticated authored-record contract. The earlier envelope4 has no such field, and clients must not claim that it disables Reply all at another endpoint.

## Composition and reply targeting

Preserve the selected [To, Cc and Bcc roles](private-address-presentation.md#to-cc-and-bcc-remain-different). To/Cc remain inspectable per contribution and draft; Bcc creates separate protected private copies and cannot be exposed through a shared recipient list. A conversational grouping does not grant a blanket Reply all audience. A private-copy reply stays private unless a new disclosure is deliberately authorized.

Before send, the composer has explicit local state for sending account, audience, conversation context, reply target or new-thread mode, body, included quotations and applicable protection policy. That state belongs to the draft; switching conversations must not overwrite another unsent draft. Ordinary application restart restores unsent content and its target, subject to the account's local storage protections. For a send awaiting secure setup, the [intent/revision and handoff contract](first-contact-setup.md#finish-setup-for-one-intended-send) freezes the authorized snapshot, blocks cancelled/superseded revisions and prevents late setup from sending newer editor contents.

Opening a composer in a focused thread defaults to the latest eligible contribution in that thread's displayed conversation order. Eligible contributions are the independently accepted primary-reply targets defined by the [assembly procedure](reply-content.md#assemble-the-conversation-from-contributions), including attachment messages and supported question/observation kinds, whose exact target and applicable reply authority are available. Service questions do not turn text composition into endpoint submission, and a hosted observation does not establish holder identity. Reactions, control traffic, conflicted records and provisional protected content are not default targets. If no eligible target is available, the client requires an explicit valid target or new-thread mode before sending. The selected target must be visible through a compact excerpt, an author label or another accessible association with the source message. The reader may select an earlier contribution deliberately. New incoming messages must not silently retarget an existing draft. A display-only order never substitutes for the exact authenticated reference placed in the sent event.

**New thread** clears the specific reply target and makes that state visible. It creates a new root contribution under the selected conversation rules; it does not copy earlier history or imply a new cryptographic group. In existing email, generate the ordinary new-message headers rather than retaining stale reply headers. Creating a separate audience or managed conversation requires its own explicit membership and establishment flow. An empty ordinary `replyTo` means no specific parent; it does not by itself reset a conversation.

The sending identity is an inspectable, selectable account control. Changing it retains the unsent writing but invalidates derived sending authorization and requires reevaluating the audience, route, membership, keys and delivery policy. A different From address is not permission to reuse another account's protected session. If the chosen account cannot perform the intended protected send, keep the draft and apply the defined hold or explicitly authorized alternative. Never silently downgrade it.

On send, construct only the new content and deliberately included context, serialize the exact selected operation and carrier, and freeze the contribution identity and bytes for retries. Editing a sent message is a new authorized correction event. It is not mutation of the retained original.

## Change the sender without changing who can read the draft

The sender picker changes who will send the next authorized contribution. It does not move the draft to another account's server, expose it to that account's other devices or authorize sharing the earlier conversation.

> [!ex] A personal reply becomes a work message
> Carol starts a private reply from her personal account and then selects her work account. Her writing stays available locally. The app checks whether the work identity may reply to the source and share the included context. It does not upload that draft to the work server or reuse her personal account's group keys. If the work identity was not in the original audience, Carol can deliberately compose a new message with authorized context instead of pretending it is the old discussion reply.

Keep the actual sender, destination and reply/new-message choice visible. A change to the effective audience requires a deliberate destination choice; a change to protection must show the resulting exposure. Switching back to an earlier account does not restore a superseded send authorization. Already submitted or uncertain work keeps its original account, bytes and status, separately from the editable draft.

::: {.details summary="Account and protection changes before release"}

1. Preserve the unsent writing and exact source selection as local draft state. Record the chosen account separately from the draft's existing storage/disclosure scope. Do not retain an actionable reply label when the chosen principal lacks the source's audience or reply permission.
2. Resolve the selected account's actual principal, authorized device and From association. An alias of the same principal may keep an otherwise eligible conversation relationship, but still needs its own account, routing and policy checks. A different principal does not inherit source access, membership, comparison results or credentials merely because the same person operates both accounts.
3. Recompute the reply action and actual audience under the [reply-intent procedure](reply-intent.md#resolve-a-reply-destination). If that action is unavailable, hold it or deliberately start a new root under independently authorized audience/disclosure/admission rules. Retaining writing is not permission to transmit protected quotations, identifiers, subject text, files or private-recipient metadata through the new account.
4. Reevaluate the selected sender's complete copy/protection plan. Ordinary-delivery permission does not grant hosted-upload permission; either final-delivery choice does not grant draft synchronization. Apply the [private working-state rules](security.md#drafts-are-private-working-state) before any remote save, including one triggered by an account picker or autosave timer.
5. Supersede any still-unreleased send revision whose account, audience, target or protection dependencies changed. Retain its exact prepared artifacts, consumed-package/cleanup obligations and possible-release evidence. A late setup completion may finish its required cleanup but cannot activate the new draft. Only a new Send under the selected plan authorizes the revised contribution; automatic retries use the old contribution only under its original still-valid authority.
6. Recheck the selected revision and all current dependencies at preparation, activation and final release. If earlier work may already have been released, keep that uncertainty visible. Another account or weaker protection cannot serve as an automatic retry of it. Starting a new send does not prove that the old one failed or was recalled.

These are local draft and authorization transitions, not a new email header or a request for an additional confirmation on every edit. Remembered policies may authorize their own exact scopes. No interoperability claim for remote draft synchronization follows from implementing these local transitions.

:::

## Keeping simpler clients in the conversation

Clients SHOULD support the [simpler-client procedure](suite-profile.md#joining-with-a-simpler-client). Under the current agreement, every admitted device reads the same fixed contribution vocabulary. A recipient without Answers can read the original question and compose a permitted ordinary reply; another recipient can use its independently implemented answer control. Different interaction lists alone require neither a different message nor a new stream. Do not show a usable-looking control on a client that cannot perform its complete operation.

Keep the draft, selected account, full intended audience, exact reply context and required protection. Every device selected in the actual delivery still needs complete current support and native admission. A changed actual ordinary audience requires the owning fresh-stream procedure; missing receiving evidence remains a hold. Lacking an optional interaction is not missing baseline support. If the local client cannot perform an exact action the person selected, preserve that action as unavailable rather than silently turn it into prose or claim it succeeded.

Earlier agreements that negotiate optional operations as shared blocks retain their own compatible-composition and migration rules. A separately authorized new composition under those rules preserves the required audience, reply policy and protection. Neither timeout nor a failed signature permits changing the agreement, stripping a question or interpreting an unknown capability as an empty interaction list.

In the ordinary conversation view, combine accepted contributions under their actual reply relationships while retaining each stream's audience and protection provenance. Do not suggest that a new device received earlier correspondence merely because the view has the same conversation name. Historical content, unresolved parents and unavailable interactions keep their own visible outcomes. Managed migrations remain separate conversations even if the interface associates them.

## Answers, reactions and actions

Question controls appear beside their authenticated question and submit the exact selected choice and question revision through the owning answer contract. An ordinary text reply remains text even when it says “yes”. Clicking a conversation answer and submitting to a service are different effects; a service action exposes its destination and uses the [service authorization](service-authorization.md) and [service-answer](service-answers.md) contracts. Merely rendering or opening content performs neither action.

When Reactions is implemented and independently authorized, expose a reaction selector for every eligible accepted human contribution, including rich messages, indexed replies and holder observations under the [current target-kind contract](reactions.md#every-human-contribution-keeps-its-own-reaction). Protocol controls and unvalidated historical text do not acquire a live selector. Selecting an emoji applies the defined reaction operation to that exact version. Selecting the reader's active emoji again withdraws the reader's applicable reaction records through the withdrawal operation; it does not delete other people's reactions. Concurrent additive records and incomplete targets retain the [reaction conflict rules](reactions.md). Aggregate counts and the reader's selected state are derived from accepted events, not optimistically treated as confirmed delivery.

### A pressed button keeps its sending status

Choosing an answer or reaction changes its control immediately. Keep the selected choice visible beside its question or message, with a compact pending indication until there is sending evidence. Service buttons follow the same interaction even though they use HTTPS rather than email. The reader must not have to press an unchanged button again to find out whether the first press registered.

These interactions work offline: save the authorized operation durably, show it as queued, and resume eligible work when connectivity returns. If local saving fails, show that failure rather than claiming it was queued. Sending status survives closing and reopening the app. A pending selection is local feedback, not a confirmed answer or reaction from the conversation.

| What happened | What the control communicates |
| --- | --- |
| Saved locally, waiting for connectivity or a required dependency | The selected choice with a queued/pending indication and its relevant waiting reason |
| A request is in flight, or its response was lost | The selection remains pending; expose uncertainty when the outcome is unknown |
| The mail transport accepted the contribution | Sent for that delivery scope; no claim of reading or remote application acceptance |
| A matching service receipt says pending | Sent to the service, still awaiting its result |
| A matching service receipt says confirmed | The selected answer was applied by that service |
| A definite rejection, expired unsent operation or unrecoverable local failure | A visible failure/held state with an appropriate recovery action; do not silently restore the untouched control |

The exact icons and labels are implementation choices. Selection and progress must be distinguishable without color alone and have accessible names/status announcements. A checkmark that means applied must not appear merely because a POST started. Failures, conflicts and partial delivery remain inspectable without adding permanent explanatory text to every button.

::: {.details summary="Durable interaction queue, retry authority and repeated presses"}

Before showing an interaction as queued, atomically retain its original operation identity, exact target/question/option or emoji, actor/account scope, authorized audience or service destination, required immutable payload, dependencies, cancellation state and known outcomes. An operation waiting for preparation remains distinguishable from prepared delivery. Resume the owning operation after restart; do not allocate a fresh answer, reaction or service submission just because the app or connection restarted. Preserve each protocol's exact-byte, crypto-state and delivery-identity rules.

Reconnect resumes only previously authorized work. Before an external attempt, recheck the owning contract's current authority, account incarnation, target, policy, validity interval and dependency rules. Missing permission or expired execution authority holds or stops that work; it cannot retarget the action, switch accounts, extend a deadline, substitute email for HTTPS or broaden disclosure. Use the owning transport's bounded retry/backoff and concurrency rules. Offline time does not extend a service action's retryUntil. If expiry happens before any possible submission, report unsent expiry; if an earlier attempt may have executed, retain uncertainty and reconcile its original status where authorized.

Repeated activation of the same pending selection must reveal or manage that existing operation rather than create another identical intent. A deliberate change, withdrawal or replacement uses its owning contract and a distinct operation where required. Canceling work proven unsent can stop its future submission; canceling a local job after a possible remote effect does not undo that effect or erase uncertainty. Distinguish queued withdrawal from a confirmed removal, preserving accepted reaction counts and provenance. Do not collapse two separately authorized, intentionally distinct reactions merely because their emoji match.

For HTTPS service actions, retain the original submission and exact request bytes before the first POST; a lost response follows the service's [status and retry rules](service-answers.md#retry-and-check-status). A retry cannot become a new business action. Keep the service result separate from participant-authored conversation events. For conversation answers and reactions, retain accepted versus local-pending state and each delivery scope; transport acceptance cannot fabricate remote acceptance or a read receipt. Reopening or replaying content creates no new work.

:::


For composition from restored history, follow [the post-restore procedure](encrypted-archives.md#replying-after-restoration). Current sending authority does not authenticate an imported parent or reactivate its old controls. Preserve the historical source and guide an independently authorized new composition when exact reply/action validation is unavailable.

A client offering historical archive restoration implements the [archive](encrypted-archives.md) and [complete collection](archive-sets.md) contracts. Their acceptance does not restore live sending authority or prove that a storage service returned the latest backup. [History transfer](history-transfer.md) additionally requires exact source approval and a grant bound to the intended recipient and archive scope.

## Offline work keeps its own meaning

A pending indicator means work is saved, not that every step has succeeded. Keep the reason and actual outcome available without asking the person to manage keys or press the same button again. Reconnecting resumes eligible saved work; it does not create new permission.

| Work | What is saved or waiting | What reconnect may do |
| --- | --- | --- |
| A reply or conversation answer | The selected sender, exact target/audience and authorized draft or immutable send revision | Continue its own setup/preparation/delivery. A mail handoff does not prove reading or application of an answer. |
| Adding a device | Original independent confirmation, request, proofs and any committed result | Retrieve/resume the original work while its route and authority remain eligible. An expired relay lease or lost response does not prove enrollment failed. |
| Removing a device | The local sending hold, separate signed-revocation state and publication/membership progress | Distribute eligible retained updates. Local commitment does not mean removed everywhere; a missing administrator remains a wait. |
| A service button or hosted reply | Exact authorized request, operation identity and known/unknown outcome | Check or retry the original action under its own credential and deadline. A restarted bearer page may need the original invitation before it can resume. |

::: {.details summary="Operation-specific resume, uncertainty and cancellation"}

Save each operation under its actual account, target, dependencies and original immutable protocol identities before claiming queued progress. Distinguish draft, waiting for authorization/preparation, ready for an attempt, possible submission, acknowledged pending, confirmed and held/terminal results where the owning contract defines them. These are local presentation categories, not a shared remote state enum or an invented acknowledgement.

On reconnect, reload the original journal and reevaluate current identity/roles, account/association, protection/disclosure policy, local cancellation/hold, original deadlines, current route and actual dependency state. Resume independent ready work without pretending held peers are complete. Missing local work is not proof of remote non-execution. Ordinary restart cannot erase a prior uncertain attempt or select a fresh business-action identifier as a retry.

Pairing and configuration use the [transport's fixed session/lease rules](pairing-transport.md#expiry-disconnect-and-readiness) and [current configuration3 staging/readiness boundary](paired-configuration.md#transfer-asynchronous-scope-metadata), or the exact earlier configuration binding selected by that pairing. No automatic renewal of the QR, lease, request or recipient is permitted. A retained committed enrollment result is historical evidence requiring current target acceptance, not another approval or a claim of email readiness. When no eligible route remains, preserve progress and expose the actual next step.

Removal follows its [local hold and committed-revocation procedure](identity-lifecycle.md#request-removal-while-offline). Service actions use their [original submission/status and retryUntil rules](service-answers.md#retry-and-check-status). Hosted replies use [durable intent without a persisted bearer](hosted-access.md#a-pending-hosted-reply-survives-a-restart): an open authorized page may resume with its live credential; after restart require deliberate restoration of the matching invitation before access. A saved credential digest is not that credential. Do not persist a usable bearer to make automatic resume appear seamless.

Cancellation stops only the future work it actually controls. It does not retract a committed enrollment, signed revocation, downloaded disclosure or uncertain service effect. A changed answer, new device request or new send is distinct authorized work under the owning contract, preserving the prior result. An offline timer, failed lookup or automatic response cannot grant weaker protection or replace an unavailable administrator.

:::

## Protection and delivery presentation

The [encryption journey](encryption-journey.md) defines the complete setup-to-recovery flow and its required failure outcomes. The client must expose missing identity, discovery or recovery mechanisms rather than substituting a successful-looking state. During [automatic first-contact setup](first-contact-setup.md), retain the human message locally until protected-send requirements pass. Follow [setup-secret retirement](setup-secret-retirement.md): used secrets retire promptly, unused attempts expire, restart cannot revive consumed material, and setup timers do not delete readable correspondence.

Show protection through compact client-owned indicators with accessible names and inspectable details. Verbosity is an interface choice; the distinction between unprotected, authenticated and encrypted content must remain understandable. A missing indicator cannot imply protection, and a protected copy cannot conceal the exposure created by an ordinary or hosted copy of the same contribution.

The sender's selected policy governs incompatible recipients, key changes and discovery failure. Preserve drafts and unresolved sends while awaiting required evidence. Resolve each actual selected delivery's recipients and devices under the owning authority rules, while retaining other intended slots and their independent pending obligations; aliases, mailbox login and server capability advertisements are not substitutes. Device enrollment, removal, key loss and history restoration use the specified lifecycle, never an invented UI shortcut that reactivates stale keys.

A send result must expose unresolved and failed recipient outcomes. SMTP acceptance does not mean decryption or reading. Do not present “seen” without evidence under an explicitly supported receipt contract. Optional provider upgrades may improve discovery or carriage without changing these meanings.

## What a status can tell you

“Sent” does not mean “read.” A provider may accept mail while a recipient's device is offline. A device may process a message in the background without its owner opening it. A service may confirm an answer without anyone reading the conversation.

Email/2 keeps those facts separate. This version does not provide a read-receipt, typing or online-presence module. Deleting a message from your view also does not erase someone else's copy or withdraw an answer you already sent.

Present [Undo send, local deletion and provider recall](delivery-policy.md#undo-send-deletion-and-recall)
as distinct actions. During an Undo send hold, show that delivery is still queued.
After release, show a supported recall as pending until its authenticated result
arrives, and retain any unsupported, failed or unknown recipients. Confirmed
removal by a service must not be presented as proof that the message was never
seen or that every copy disappeared. A local Delete action affects the person's
own selected copy and does not silently request recall.

:::: {.details summary="Evidence-bound status, local deletion and retained safety state"}

### Status is scoped evidence, not one universal progress ladder

Retain the contribution, exact prepared delivery, recipient/device scope, attempt identity, evidence source and historical versus current meaning for each outcome. Evidence from one copy, provider or operation cannot upgrade another. For the current agreement retain the logical authored identity, typed delivery identity, intended addressed-slot obligations and each actual delivery mapping separately. Distinct eligible aliases do not collapse their addressed obligations into one recipient result. A [delivery-key conflict](event-identifiers.md#keep-delivery-identity-separate-from-message-identity) cannot identify one frozen preparation or establish a successful retry by that key alone. Compact indicators and labels are client-owned; the distinctions below are required, not one mandatory interface layout.

| Available evidence | Supported claim and limit |
| --- | --- |
| Saved draft or prepared protected bytes | Locally saved/prepared only. No transport attempt or recipient access follows. |
| Queued, waiting for setup, held policy or unavailable dependency | Waiting, with the actual relevant scope/reason. No submission or encryption downgrade is inferred. |
| Transport attempt began but its decisive result is unknown | Uncertain for that attempt's actual recipient scope. A missing reply, crash or later failed query is not proof of nonexecution. |
| Matching final SMTP/provider acceptance | The named transport accepted responsibility for the stated scope. This is not endpoint decryption, application acceptance or human reading. |
| Validly correlated delivery/failure report | A report attributed to its validated source with its precise reported outcome. It does not prove endpoint key possession, readable-content acceptance, consent or comprehension. Conflicting evidence stays visible. |
| Local owning-validator acceptance | This particular local membership/profile accepted the exact control/contribution. It does not establish that a remote device accepted it. |
| Service result accepted under its HTTPS/action/account contract | Pending, confirmed, rejected or conflicting for that exact service submission. It is not a participant-authored conversation answer, transferable signed proof or a mail/read receipt. |
| Hosted management/holder receipt | The specific host stored/revoked a grant or stored a holder-attributed reply under its contract. It does not identify the holder or prove that a person opened/read the contribution. |
| Live setup response, mailbox push, IMAP IDLE, synchronized Seen flag or provider display status | Their scoped setup/mailbox observations only. No online-person, typing or Email/2 read claim. |

A local “read” marker may track the reader's own view; it remains private client/account state under the selected sync policy. Merely opening, focusing, rendering, scrolling, reconstructing, fetching resources or refreshing a view sends no Email/2 read/presence event. Readable HTML cannot add one. Legacy MDN requests and provider read markers retain their separately authorized contracts and cannot be repurposed as new Email/2 receipts. The current application operation set rejects unknown read/presence operations rather than treating them as an optional semantic extension.

Preserve already confirmed historical evidence when a later poll is pending, a receipt is unavailable or an attempt fails. A later valid failure report can qualify the relevant transport delivery without changing a confirmed service effect or another recipient's result. Never aggregate partial acceptance into universal success, or another recipient's success into proof that an uncertain recipient failed. Derive plan-wide status only from the [complete copy/outcome snapshot](delivery-policy.md#a-waiting-delivery-is-different-from-missing-setup); missing planned state is incomplete, and collective local activation is not atomic remote delivery. A status check may reconcile retained evidence; it cannot allocate a new action/submission or silently resend through another channel.

### Deletion, withdrawal, revocation and cancellation are distinct

| Requested operation | Actual scope |
| --- | --- |
| Hide, archive, mute or delete from a local view | Local presentation/account operation. It sends no conversation withdrawal and proves no remote erasure. |
| Remove/expunge a provider record | Provider mailbox operation under current permissions, with its own partial/retry semantics. Other locations, recipients and accepted conversation state may remain. |
| Withdraw an own reaction, correct a message or replace an answer | Its explicitly supported authenticated operation and exact target rules. It changes the relevant current view/result while retaining provenance; it does not delete original bytes everywhere. |
| Cancel an unsent attempt | Stops only work still within the client's cancellation boundary. Already submitted or uncertain work retains its real outcome; deleting a draft/Sent/submission record is not cancellation evidence. |
| Revoke a grant, route, device or membership | Its owning authority/lifecycle contract. It stops specified future use once enforced; it does not erase downloads or recall accepted mail. |
| Retire a local membership or destroy a local security profile | Stops that exact live authority under its lifecycle. It is not a global closing message or proof that all copies/keys disappeared. |

Deleting visible correspondence must not remove the safety state required to continue the same live security/membership context. A client offering content purge retains protected minimal tombstones sufficient for original accepted event identity/content commitments, carrier/input replay receipts, membership periods, unresolved/conflicting outcomes and already applied operation identifiers. Keep the owning protocol's vote, nonce, package-consumption, source and uncertain-send records while their live authority depends on them. Tombstones and recipient metadata can themselves be sensitive; protect them as local security state rather than sending them to correspondents or an analytics service.

The storage layout is local, not a new network deletion message. Purge commits atomically with its tombstones, hidden/content-unavailable state and affected job references. Garbage collection cannot race a pending release/history-transfer/archive job into using missing bytes or forgetting an uncertain result. If required bytes are no longer available, hold that dependent work under its owning contract; never reconstruct a guessed message, invent an answer target or weaken protection to finish it.

A tombstone is a do-not-reapply marker, not a new signature or proof that incoming bytes equal deleted originals. If exact original comparison is no longer possible, retain the historical-unavailable/conflicting outcome rather than treating the identifier as unseen. A digest cannot reconstruct a deleted immutable request or receipt for a retry; hold that retry or use its independently authorized status/recovery mechanism without allocating a new operation.

A later duplicate or mailbox rescan consults those retained records. It cannot reapply an answer, restore consumed keys, produce another service effect or automatically restore a deliberately hidden contribution. Explicitly authorized historical restoration may make content readable again with its original provenance, but does not replay live effects. If purging a question/source removes information needed to validate a new dependent operation, keep that operation unresolved until authorized evidence is available; do not infer that the old answer was withdrawn or that no answer existed.

If the user deliberately destroys the safety state as well as content, stop and retire the affected live contexts before that state is lost. They cannot resume from an empty database using the same old checkpoints/keys as if nothing had been processed. The actual account/device/group lifecycle determines whether a fresh membership, fresh stream or new identity is needed. This is a security consequence to explain, not a new universal confirmation dialog, backup subscription or retention quota. Erasing a local file does not establish physical erasure from journals, device snapshots, provider storage, exported archives or another person's device.

### Acceptance requirements and current limits

Exercise acceptance followed by crash, missing final transport reply, mixed recipient results, later provider failure, pending after service confirmation, conflicting terminal receipts, duplicate processing and status lookup unavailable. Verify no path labels another person's message seen/online from setup, mailbox activity or absence of a bounce. Opening and reconstruction must produce no receipt/service submission.

For content deletion test purge before/after its transaction, rescan/reimport, a late duplicate carrier, delayed answer/reaction, unresolved send, pinned transfer/archive job, restore of historical content and intentional loss of safety state. Keep old effects and uncertainty stable while dependent work becomes explicitly unavailable. Include provider-record deletion/partial failure separately from local content purge. Current journal/transport/service regressions cover selected durability/status mechanics, not a complete purge/tombstone implementation, cross-device read semantics, physical erasure or whole-client conformance.

::::

## Conformance evidence

A complete-bundle acceptance run covers one continuous flow: receive and retain original mail; accept and deduplicate structured events; reconstruct roots and branches; render supported rich content; preserve a draft while switching conversations; send to its displayed target; accept an answer and a reaction withdrawal; survive restart and retry; and apply protection policy when a participant or device cannot continue. Include legacy input, unavailable parents, malformed HTML, conflicting references and failed service execution. Each case checks both visible state and the retained event/effect state.

Base-only and each module combination need their own acceptance runs, including explicit unsupported and policy-held behavior. A base client cannot display an unauthenticated structured event as a protected effect.

Visual styling, brand, exact spacing and animation are not protocol requirements. The observable relationships, defaults, authorization boundaries and failure outcomes above are requirements of the proposed client contract. A different appearance must not change who receives a message, what it answers, what an action does or which content is protected.

The existing [acceptance tools](adoption.md#acceptance-tools-and-interoperability-program) supply selected cases and report formats, not a complete client certification. Required behavior without an integrated test remains an implementation obligation; a successful component experiment does not discharge it. The [coverage table](interoperability.md#contract-coverage-and-remaining-decisions) records remaining bindings and deployment evidence.


## Concurrent administration and retirement

Follow the [complete state1 lifecycle](identity-state.md#concurrent-administration-and-retirement) for authenticated administrator conflicts. Hold affected operational work while retaining history; expose actual proposed roster/permission changes and distinguish incomplete proof collection from installed repair. Required approval/possession or transport unavailability remains a wait, not permission to select a winning branch, omit an administrator or send public proofs as fallback. After repair, obtain permitted fresh setup/grants and reevaluate current MLS state without duplicating uncertain content. Only an explicit separately signed retirement ends identity authority; inactivity and billing do not. No surviving authority means the existing explicit new-identity outcome rather than a password/archive override.
