---
title: Client behavior and conformance
order: -0.5
blurb: required client behavior · protocol bindings · complete conversation flow
sectionNav: true
---

# Client behavior and conformance

An Email/2 client implements a conversation platform, not a collection of unrelated mail extensions. Following this specification should determine how the client receives, reconstructs, displays and answers a conversation, including what happens when delivery, identity or rendering fails.

This chapter defines the proposed observable client contract. The linked chapters own exact schemas, selected protocol versions, algorithms and failure rules. These requirements do not establish that the supplied experiments implement a complete client. Candidate bindings that remain unfinished must be completed before advertising the corresponding support; a requirement here does not silently widen an existing negotiated tuple.

## Base behavior and module-dependent requirements

An Email/2 client implements the Conversations base and identifies the optional [modules](modules.md) it supports. The table below describes the complete protected conversation bundle; interaction and protection rows apply only when the corresponding module is implemented and selected. Omitting an optional module is legitimate. Claiming that module without its required safety behavior is not. Transport providers have separate roles and need not implement a user interface or decrypt messages.

| Component | Required behavior | Authoritative contract |
| --- | --- | --- |
| Existing-mail carriage | Submit, retrieve and retain messages through an existing account integration; preserve protected payloads and report delivery uncertainty | [Transport](transport.md), [messages](messages.md) and each selected MIME carrier |
| Protected event processing (Encryption) | Validate identities, immutable event bytes, exact references, duplicates and collisions before applying effects | [Event identifiers](event-identifiers.md), [encoding](event-encoding.md) and [interaction state](interaction-state.md) |
| Conversation reconstruction | Assemble contributions and branches from exact reply relationships; keep new writing separate from included quotation context | [Reply content](reply-content.md) and [legacy reconstruction](rendering.md) |
| HTML/CSS presentation | Render the mandatory finite vocabulary with resource isolation and accessible client-owned controls | [Required presentation](presentation-profile.md#required-presentation) and [rich messages](rich-messages.md) |
| Composition | Retain an explicit sender, audience, reply target and draft; create a new immutable contribution on send | This chapter, [messages](messages.md) and [reply content](reply-content.md) |
| Conversation interactions (selected modules) | Answers supports questions/answers together; Reactions supports reaction/withdrawal together; Corrections supports the selected plain-message edit. Enable each only in its negotiated agreement | [Messages](messages.md), [reactions](reactions.md) and [interaction state](interaction-state.md) |
| Managed protection (Encryption) | Establish and process the selected MLS conversations, including device and group authority, delayed delivery and recovery outcomes | [Security profile](security-profile.md), [identity lifecycle](identity-lifecycle.md), [groups](group-conversations.md) and their selected bindings |
| Delivery policy | Respect remembered protection requirements and explicit disclosure decisions; accurately distinguish ordinary, hosted and protected copies | [Delivery policy](delivery-policy.md), [private copies](private-copies.md) and [protected labels](managed-presentation.md) |
| Local state | Preserve received originals, accepted events, conflict evidence and unsent drafts across ordinary restart; commit effects under the owning protocol's durable-state rules | [Transport](transport.md), [interaction state](interaction-state.md) and [identity lifecycle](identity-lifecycle.md) |

Provider-assisted discovery/control, hosted-access operation and service-endpoint submissions are separately negotiated extensions. A client that supports one implements its complete authorization, retry and failure contract. A client without it retains the defined unsupported or held state and an available authorized alternative; it must not simulate successful execution. General forms and rich-content editing beyond the selected correction operation remain outside the initial client contract.

The suite selects protocols rather than every possible backend. An account adapter may use an applicable IMAP/submission or JMAP integration without requiring every client to implement both. The adapter must preserve the same observable carriage, storage and authorization behavior. The [protected conversation agreement](suite-profile.md) fixes the protected core and exact shared optional interactions. Public provider discovery has a contract, while public bootstrap/relay integration and joined suite implementation remain separate work identified in [contract coverage](interoperability.md#contract-coverage-and-remaining-decisions).

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

Preserve multiple root contributions and the branches that reply to them. Opening a branch focuses its root and descendants, with a way to return to the broader conversation. It does not move messages to a different audience or rewrite their reply relationships. A missing parent remains unresolved, not a guessed root. Late arrivals and reprocessing preserve the reader's position and expansion choices where practical.

Quoted context follows the explicit verification and collapse rules. All authored chunks remain in order. A collapsed quotation has an immediate expansion affordance, and the complete original is available separately. Legacy quotation detection never destroys the source or hides ambiguous material as if it had been verified.

The HTML/CSS profile is required. Compatibility text and user-selected simpler reading views do not create a text-only conformance class. Unsupported or invalid content follows diagnostic recovery, without active controls or a false claim that the required presentation succeeded.

## Composition and reply targeting

Before send, the composer has explicit local state for sending account, audience, conversation context, reply target or new-thread mode, body, included quotations and applicable protection policy. That state belongs to the draft; switching conversations must not overwrite another unsent draft. Ordinary application restart restores unsent content and its target, subject to the account's local storage protections.

Opening a composer in a focused thread defaults to the latest eligible contribution in that thread's displayed conversation order. Eligible contributions are accepted messages and questions, including rich and indexed replies, whose exact target and applicable reply authority are available. Reactions, control traffic, conflicted records and provisional protected content are not default targets. If no eligible target is available, the client requires an explicit valid target or new-thread mode before sending. The selected target must be visible through a compact excerpt, an author label or another accessible association with the source message. The reader may select an earlier contribution deliberately. New incoming messages must not silently retarget an existing draft. A display-only order never substitutes for the exact authenticated reference placed in the sent event.

**New thread** clears the specific reply target and makes that state visible. It creates a new root contribution under the selected conversation rules; it does not copy earlier history or imply a new cryptographic group. In existing email, generate the ordinary new-message headers rather than retaining stale reply headers. Creating a separate audience or managed conversation requires its own explicit membership and establishment flow. An empty ordinary `replyTo` means no specific parent; it does not by itself reset a conversation.

The sending identity is an inspectable, selectable account control. Changing it retains the unsent writing but invalidates derived sending authorization and requires reevaluating the audience, route, membership, keys and delivery policy. A different From address is not permission to reuse another account's protected session. If the chosen account cannot perform the intended protected send, keep the draft and apply the defined hold or explicitly authorized alternative. Never silently downgrade it.

On send, construct only the new content and deliberately included context, serialize the exact selected operation and carrier, and freeze the contribution identity and bytes for retries. Editing a sent message is a new authorized correction event. It is not mutation of the retained original.

## Answers, reactions and actions

Question controls appear beside their authenticated question and submit the exact selected choice and question revision through the owning answer contract. An ordinary text reply remains text even when it says “yes”. Clicking a conversation answer and submitting to a service are different effects; a service action exposes its destination and uses the [service authorization](service-authorization.md) and [service-answer](service-answers.md) contracts. Merely rendering or opening content performs neither action.

Every displayed contribution exposes a reaction selector associated with that contribution. Selecting an emoji applies the defined reaction operation to that exact version. Selecting the reader's active emoji again withdraws the reader's applicable reaction records through the withdrawal operation; it does not delete other people's reactions. Concurrent additive records and incomplete targets retain the [reaction conflict rules](reactions.md). Aggregate counts and the reader's selected state are derived from accepted events, not optimistically treated as confirmed delivery.

Local interaction feedback distinguishes a queued request, transmitted contribution, accepted conversation effect and confirmed service result. A client may show a pending visual update, but must preserve an actionable failure or unresolved state when the owning operation does not complete. Reopening a view, retrying transport or replaying an event must not repeat a service execution.

A client offering historical archive restoration implements the [archive](encrypted-archives.md) and [complete collection](archive-sets.md) contracts. Their acceptance does not restore live sending authority or prove that a storage service returned the latest backup. [History transfer](history-transfer.md) additionally requires exact source approval and a grant bound to the intended recipient and archive scope.

## Protection and delivery presentation

The [encryption journey](encryption-journey.md) defines the complete setup-to-recovery flow and its required failure outcomes. The client must expose missing identity, discovery or recovery mechanisms rather than substituting a successful-looking state. During [automatic first-contact setup](first-contact-setup.md), retain the human message locally until protected-send requirements pass. Follow [setup-secret retirement](setup-secret-retirement.md): used secrets retire promptly, unused attempts expire, restart cannot revive consumed material, and setup timers do not delete readable correspondence.

Show protection through compact client-owned indicators with accessible names and inspectable details. Verbosity is an interface choice; the distinction between unprotected, authenticated and encrypted content must remain understandable. A missing indicator cannot imply protection, and a protected copy cannot conceal the exposure created by an ordinary or hosted copy of the same contribution.

The sender's selected policy governs incompatible recipients, key changes and discovery failure. Preserve drafts and unresolved sends while awaiting required evidence. Resolve every intended recipient and device under the owning authority rules; aliases, mailbox login and server capability advertisements are not substitutes. Device enrollment, removal, key loss and history restoration use the specified lifecycle, never an invented UI shortcut that reactivates stale keys.

A send result must expose unresolved and failed recipient outcomes. SMTP acceptance does not mean decryption or reading. Do not present “seen” without evidence under an explicitly supported receipt contract. Optional provider upgrades may improve discovery or carriage without changing these meanings.

## Conformance evidence

A complete-bundle acceptance run covers one continuous flow: receive and retain original mail; accept and deduplicate structured events; reconstruct roots and branches; render supported rich content; preserve a draft while switching conversations; send to its displayed target; accept an answer and a reaction withdrawal; survive restart and retry; and apply protection policy when a participant or device cannot continue. Include legacy input, unavailable parents, malformed HTML, conflicting references and failed service execution. Each case checks both visible state and the retained event/effect state.

Base-only and each module combination need their own acceptance runs, including explicit unsupported and policy-held behavior. A base client cannot display an unauthenticated structured event as a protected effect.

Visual styling, brand, exact spacing and animation are not protocol requirements. The observable relationships, defaults, authorization boundaries and failure outcomes above are requirements of the proposed client contract. A different appearance must not change who receives a message, what it answers, what an action does or which content is protected.

The existing [acceptance tools](adoption.md#acceptance-tools-and-interoperability-program) supply selected cases and report formats, not a complete client certification. Required behavior without an integrated test remains an implementation obligation; a successful component experiment does not discharge it. The [coverage table](interoperability.md#contract-coverage-and-remaining-decisions) records remaining bindings and deployment evidence.
