---
title: Messages and interactions
order: 1
blurb: conversations · answer buttons · fallback
sectionNav: true
---

# Messages and interactions

A question can offer predefined answers as buttons. Pressing a button sends an answer that identifies the question and selected choice. A client can then show the conversation without asking readers to untangle a stack of quotations.

> [!ex] One question, two ways to answer
> Alice asks **Which day works?**, with **Tuesday** and **Thursday** as choices. Bob selects Thursday in an upgraded client. Carol reads the same choices in ordinary email and replies, “Thursday works for me.”
>
> Bob's reply carries an explicit reference to the question and its Thursday option. Carol's reply carries her words. Alice's client can suggest where Carol's answer belongs, but cannot turn that suggestion into a verified button answer.

This chapter defines that distinction, the readable email fallback, and the handling of attachments. The detailed schemas and inherited MIME rules are available alongside the behavior they support.

> [!note] Draft contract
> These are proposed requirements for Email/2. The experimental encoding defines text messages, first-version button questions and answers, plain-message edits, and independent attachments. General-purpose forms remain deferred. Selected protected profiles have joined message, edit, button, reaction and rich-resource experiments; these do not establish deployed or independent-client interoperability. The [event media type](media-type-registration.md) is a candidate, not a registered type.

## Contributions and replies

A **contribution** is one authored message or interaction. Its encoded record is an **event**. Once sent, an event is immutable: changing an answer creates another event that refers to the earlier answer. It does not rewrite the received original.

| Part of a contribution | What it tells the client |
| --- | --- |
| Conversation | Where the contribution belongs; the identifier alone proves no membership |
| Event identity | Which contribution this is, so a retry does not apply it twice |
| Author | Who claims to have sent it, together with the available authentication evidence |
| Audience | Who this contribution is intended for, independently of earlier participants |
| References | Which earlier contribution, question, field or answer it addresses |
| Content | What the reader should see, and any structured interaction it describes |
| Required capabilities | What a client must understand before applying that interaction |

A `From` header alone does not authenticate the author. Timestamps alone do not establish reply order. Repeated text alone does not identify a duplicate: two intentionally sent messages saying “Thanks” remain two contributions.

The [reply-content contract](reply-content.md) separately defines authored chunks, quoted context, a structured chunk index and matching HTML Microdata. Ordinary `message` and `rich-message` schemas below remain unchanged; they do not acquire that new operation by implication.

The [identifier contract](event-identifiers.md) defines exact references. The [encoding contract](event-encoding.md) defines the envelope and its UTF-8 JSON representation. The following operation schema adds ordinary text replies to that envelope.

:::: {.details summary="Text-message schema and reply resolution"}

### Experimental text-message operation

The contribution envelope accepts an ordinary text message with exactly three required operation members:

| Member | Value |
| --- | --- |
| `kind` | Exactly `message` |
| `text` | Unicode scalar-value string, interpreted as plain text |
| `replyTo` | Array containing zero or one exact EventReference |

Text is preserved without trimming, Unicode normalization or markup interpretation. An empty string is valid data; clients may show an accessible empty-message label without inventing sender content. HTML-looking text is displayed as text. Rich HTML uses the separate [rich-message operation](rich-messages.md), which binds its readable text, HTML and resources; it cannot appear as an unrecognized extra member here.

An empty replyTo array means this contribution has no specific reply target. It does not create a new conversation or reset existing history. One reference identifies the exact contribution being answered, which may be an accepted `message`, `attachment-message`, `rich-message`, `reply-message` or `question`, including an independently accepted service-question under the [current service binding](service-answers.md#current-protected-service-agreement). It may also target an independently accepted hosted-holder-observation under its [owning binding](hosted-access.md#protected-observations-of-hosted-replies), without verifying the holder. A text reply to a question does not become a structured answer, consent or selected choice.

The target must be in the enclosing event's conversation. Resolve its complete authenticated principal/event/conversation identity; neither subject matching nor repeated words can substitute. Missing or conflicted targets leave the relationship pending or conflicted. The authenticated message text remains visible as its own contribution with an unresolved-reply indication; it MUST NOT be attached to an alternative guessed parent. A resolved wrong identity or cross-conversation target invalidates the relationship and prevents presenting it as a verified reply. This does not license discarding the original received material.

Reply relationships do not expand audience or disclose target content. A recipient lacking access to the target receives no automatic fetch, quoted text or attributed summary. The message's own author and protection status remain separate from the target's. Copies and retries deduplicate under the enclosing event identity, not text equality. Two intentionally sent equal strings with different event identifiers remain two contributions.

This operation adds ordinary text conversation to the experimental envelope. Rich HTML uses the [rich-message contract](rich-messages.md) with the defined [presentation profile](presentation-profile.md); reactions use their [operation and protected-carriage contract](reactions.md). Edits use the [explicitly negotiated edit profile](interaction-state.md#negotiated-protected-profile) and are not enabled merely by negotiating ordinary messages; independent attachments use the attachment-message operation below; implementations MUST NOT reinterpret unknown operation kinds as messages. The [message experiment](evidence/README.md#text-message-operations) exercises shape and exact-target handling, not cryptographic authentication or a complete client renderer.

::::

## Questions and answer buttons

The complete [button question](examples/button-question.eml) and [selected answer](examples/button-answer.eml) show the proposed message format. Each contains readable text and HTML alongside the structured contribution. The answer carries the question wording and selected choice, without bundling the original email or other answers. These unencrypted examples use synthetic identities; they do not demonstrate authenticated delivery or endpoint submission.

The first version supports a question with predefined answer buttons. Pressing a button sends that answer as a contribution to the conversation; there is no separate form-submission step. For example, “Which day works?” can offer **Tuesday** and **Thursday**. Free-text answers remain ordinary replies.

Each question and option has an identifier. The answer refers to the exact question revision and selected option, so the client can show it beside the question. Button labels are readable text, and the client makes clear that pressing a button sends the displayed answer to the conversation's specified audience. Opening, previewing or scanning a message never sends an answer.

The selected button visibly changes on activation and keeps a compact queued/pending, sent or failure indication under the [shared interaction status contract](client-behavior.md#a-pressed-button-keeps-its-sending-status). Save the authorized answer durably even while offline; reconnect and restart resume eligible delivery without another press. A pending choice does not count as a confirmed conversation answer. A retry retains the same answer event identity. If two devices send different answers, retain both events; only an explicit replacement by the same authenticated author supersedes an earlier answer. Arrival order does not decide which answer the person intended.

Older clients receive the question and readable choices, with instructions to reply normally. Their text replies are not silently converted into authenticated button presses. A forwarded question does not automatically authorize its new recipient to submit into the original conversation.

General-purpose forms, free-text input controls, multiple-field submissions and multi-select controls are deferred beyond the first version. The existing [form schemas](form-operations.md) and [interaction state experiments](interaction-state.md) provide exploratory work on exact targets, replacements and duplicate handling; they are not requirements for first-version clients. The candidate button-only objects below are independent of those broader schemas; [joined protected delivery and durable state](evidence/README.md#joined-question-and-ordinary-reply) have local experimental evidence.

:::: {.details summary="Candidate question and answer objects"}

### Question object

A question operation has exactly three required members. Omitted, null and additional members are invalid.

| Member | Value |
| --- | --- |
| `kind` | Exactly `question` |
| `text` | The question as a nonblank Unicode scalar-value string |
| `options` | A nonempty ordered array of option objects |

Each option has exactly `id` and `label`. Its `id` uses the [object identifier grammar](event-identifiers.md) and is unique within this question. Its `label` is a nonblank Unicode scalar-value string. Both question text and labels are plain text, not HTML. Preserve their original spelling and whitespace; the nonblank check rejects strings consisting entirely of ECMAScript trim whitespace. Clients must make the choices distinguishable to readers; opaque identifiers cannot compensate for indistinguishable labels.

The enclosing event identifies the exact immutable question. A changed question or changed option label is a new event; an earlier answer continues to refer to the earlier wording. This candidate does not define automatic question replacement or transfer answers to a revised question.

### Answer object

An answer operation has exactly four required members:

| Member | Value |
| --- | --- |
| `kind` | Exactly `answer` |
| `question` | An exact EventReference to the question event |
| `option` | One option identifier from that exact question |
| `replaces` | An array of distinct exact EventReferences; empty for an answer with no explicit replacements |

The answer and question belong to the same conversation. Every replacement reference belongs to the answer's authenticated author and conversation, identifies another answer to the same exact question, and must not identify the new answer itself. Replacements do not erase the original records. A malformed or unresolved replacement has no supersession effect. Concurrent answers remain separate until an authorized answer explicitly replaces them. Cycle detection, identity-conflict handling and durable deduplication are required before applying effects; matching references alone is insufficient. The [button graph experiment](evidence/README.md#button-answer-graph) evaluates transitive replacements and cycles from an authenticated snapshot; the [receive-preparation experiment](evidence/README.md#preparing-a-received-button-answer) combines that graph with context and audience checks. The [joined client flow](evidence/README.md#joined-question-and-ordinary-reply) exercises authenticated MLS carriage and durable receive state; the graph helper alone does not establish those properties.

An unknown question or replacement target leaves the answer pending. A conflicted target leaves its relationship conflicted. A resolved target with a mismatched author, event identity or conversation is invalid. An option absent from the exact question is invalid even if another question offers that option identifier. Neither label matching nor an ordinary text reply can substitute for these references.

The readable question lists every choice and invites an ordinary email reply. The readable answer includes the selected label and exact question reference, without the conversation transcript. Automatic copying of question text and labels into an answer follows the [selected agreement's source-audience comparison](event-encoding.md#asynchronous-authored-records-and-deliveries). Within one current scope, compare complete intended slot sets; across scopes require independently accepted bindings and the owning disclosure permission. A smaller ready delivery is not the question's entire intended audience. Earlier agreements compare their authenticated principal audiences. Sharing that context more widely requires a separately authorized sharing operation, outside this projection algorithm.

A current answer keeps the question's logical authored reference across all its deliveries. If Carol's answer arrives before her copy of the question, retain it with a pending exact target and apply no guessed choice label or supersession. Once the source and every replacement dependency independently validate, derive its one logical effect. Later copies of the same authored answer do not add another submission. A narrower answer does not claim that excluded participants saw it; a service submission remains a separate endpoint operation.

These objects do not select a delivery endpoint, authorize a recipient or authenticate an author. Those checks belong to the enclosing contribution and delivery profile. The standalone [button experiment](evidence/README.md#answer-button-objects) checks object shape and exact references. The experimental contribution envelope accepts these kinds and generates readable text/HTML projections. This does not establish complete delivery or durable-state handling; clients must not advertise interoperable support on the strength of this experiment.

::::

### Where a button sends its answer

A button can propose either a conversation reply or submission to an HTTPS service. Both use the same simple question-and-choice interface. Endpoint submission is an optional capability; supporting answer buttons does not require a general-purpose form engine or sender-supplied scripts.

For a conversation answer, show the actual intended destination before activation. The default is the question's complete intended audience under the selected protection policy, including pending slots in the current agreement; one ready encrypted delivery does not silently narrow it. A deliberately selected narrower audience follows its own composition, disclosure and native-delivery checks and remains visibly distinct. Written-reply intent does not choose or authorize this structured answer destination. For a service submission, the client identifies the receiving service and sends only the declared answer data. A service receiving plaintext is a recipient of that data; encryption of the surrounding conversation does not conceal the answer from the service.

> [!ex] Answering a scheduling service
> An invitation offers **Tuesday** and **Thursday**. An upgraded client can submit Thursday directly to the scheduling service and show its acknowledgement. An older client can send an ordinary reply to a service mailbox, which the service processes separately, or follow a link to answer on its website.

The ordinary `Reply-To` header contains email addresses, not web endpoints. An email-to-service gateway can accept those replies and pass them to an application. An HTTPS submission target needs separate structured metadata understood by upgraded clients. Gmail's [one-click actions](https://developers.google.com/workspace/gmail/markup/reference/one-click-action) and Outlook's [actionable messages](https://learn.microsoft.com/en-us/outlook/actionable-messages/get-started) provide prior art; neither defines this draft's cross-provider protocol.

Opening or scanning a message must not perform an action. A readable fallback link opens an answer page; fetching that link must not itself submit the answer. Forwarding a question does not establish the forward recipient's authority to act as the original recipient.

The [service-answer contract](service-answers.md) owns request and receipt schemas, destination binding, original retry identities and failure handling. The service-question operation carries its authenticated descriptor; [native service authorization](service-authorization.md) defines public acquisition and signed principal linking. Those selected protocols still require complete implementation and acceptance before a client advertises support. A client must distinguish a pending or uncertain service result from a confirmed answer. Sending both an email and a service request is not an atomic operation; any combined mode must specify how it avoids duplicate effects and reconciles partial success. The button-operation experiment currently covers conversation answers only.


:::: {.details summary="Service responses, retries and acknowledgements"}

### What the sender authorizes

The proposed service-response profile binds the question, available choices, exact HTTPS destination and requested answer data in authenticated action metadata. A mutable page, unsigned message header or redirect cannot replace that destination. The client identifies the service before the user presses a button. An answer sent to a service does not include conversation history, attachments, mailbox credentials or unrelated message headers.

The service verifies the answering principal and that principal's authority for this action. Possession of a forwarded message or a question identifier is insufficient. The current contract uses the separately authorized [native account/link acquisition](service-authorization.md), service-specific bearer credentials and direct HTTPS-origin-authenticated responses. Earlier configured experiments use provisioned credentials and do not prove that public acquisition. Neither path makes copied receipt JSON a portable proof or an unrelated provider token valid at this service. The client must not send its mailbox password, ambient browser cookies or unrelated bearer tokens to an action endpoint.

### Submission and status requests

The experimental service profile selects HTTPS POST for submitting an answer. The answer and submission identity belong in the request body, not in a URL query or fragment. GET and HEAD retrieve information only; they MUST NOT create, replace or withdraw an answer. This keeps email previews, link scanners and ordinary navigation from executing an action. POST's HTTP semantics alone do not make retries safe; the durable submission identity below supplies the application-level duplicate protection.

Submission requests MUST target the exact authenticated action URI. Clients MUST NOT automatically follow an HTTP redirect for a submission, even when the redirect preserves the method or stays on the same origin. A redirect is not authorization to send the answer or credential to another resource. The client retains the unresolved submission and obtains an authenticated destination update or contacts the service. A destination update must define how an existing submission's identity and result are recovered before it permits another execution attempt.

Status retrieval uses HTTPS GET with no request body and performs no action. Its URI must be bound to the submission by authenticated action metadata or a verified service acknowledgement; a bare Location header is insufficient. Status requests also MUST NOT automatically follow redirects; a new status URI needs the same authenticated binding. Status access requires authorization for that submission. A hard-to-guess identifier is not a substitute for this check. Submission and status requests MUST NOT carry ambient browser cookies or credentials belonging to another service.

Requests and responses in this profile MUST include `Cache-Control: no-store`. The client keeps its intentional local answer and acknowledgement records separately from the HTTP cache. A status response must not be reused as the result of a different request or principal. This caching directive does not prevent a recipient from retaining disclosed content, authenticate a result, or make an untrusted intermediary safe.

These are proposed application restrictions on [HTTP semantics](audits/http-semantics.md), not changes to HTTP itself. HTTP permits redirects and some POST caching; this profile narrows those options to preserve the authorized destination and avoid reuse of private action results. The [service-answer chapter](service-answers.md) owns the exact payload and acknowledgement bindings; common credential acquisition and integrated service-question authentication remain prerequisites.

### One answer, one submission identity

The client records a submission identity and the exact authorized answer before transmission. Every retry of that submission uses the same identity and answer. Choosing a different option creates a new answer with an explicit replacement relationship; it is not a retry.

The service scopes deduplication to the authenticated principal and action. It durably records the submission identity, validated answer and result. Repeating the same submission returns its recorded outcome without applying the action again. Reusing its identity with different answer data is a conflict, not an update. Concurrent duplicates must share one execution decision.

Recording a deduplication entry and performing the service's state change must be atomic, or the service must use an equivalent recoverable operation. If an external dependency prevents that guarantee, the service must report a pending or uncertain outcome and reconcile it before executing again. An in-memory cache alone does not provide this behavior across crashes.

### What the client shows

| Outcome | Conversation presentation |
| --- | --- |
| Answer recorded locally, not transmitted | Queued |
| Request transmitted, no trustworthy outcome received | Awaiting confirmation; the action may already have happened |
| Service acknowledges durable receipt but has not completed the action | Received by service; pending |
| Service confirms the action's result | Confirmed, with the service's result |
| Service confirms rejection without applying the action | Rejected, with an actionable explanation |
| Conflicting results or reused identity with different content | Conflict; do not invent a successful result |

An acknowledgement identifies the submission, question, selected option, answering principal, receiving service and outcome. The client verifies those bindings before attaching it to the answer. An HTTP success status without the required acknowledgement is not confirmation of the application action. A lost connection, missing response or generic server failure leaves the application outcome uncertain. Preserve the meaning of a specific trustworthy HTTP response rather than treating every error as the same outcome.

For example, [RFC9110](https://www.rfc-editor.org/rfc/rfc9110.html) defines 401 as a request not applied for lack of valid credentials, 408 as an incomplete request, and 421 as a misdirected request that may be retried over another connection. These describe the particular HTTP attempt. They do not prove that an earlier attempt with the same submission identity was never applied. A 202 response is noncommittal acceptance, not a completed action.

A client can use those distinctions to correct authentication or connection handling, but must preserve the submission identity and exact answer when retrying. Credentials may change as required by the authorization exchange; the action data may not silently change. The configured-deployment profile accepts a bound result only from the direct HTTPS response to its exact submission or status request. An intermediary-generated response is not automatically a receipt from the action service.

### Delayed and conflicting acknowledgements

The client derives the submission's state from retained, verified service acknowledgements. Arrival order does not select the winner. These rules apply only after the acknowledgement's service authority and exact submission bindings have passed validation; an unrelated or unauthenticated response cannot create a conflict for someone else's submission.

| Retained evidence for one submission | Derived state |
| --- | --- |
| No verified application acknowledgement | Queued or awaiting confirmation, according to local transmission evidence |
| Durable-receipt acknowledgement, without a terminal result | Received by service; pending |
| Confirmed terminal result, with any earlier or later pending acknowledgements | Confirmed |
| Rejected terminal result explicitly asserting no application, with any pending acknowledgements | Rejected |
| Incompatible terminal results, including both confirmed and rejected | Conflict |

A pending acknowledgement received after a terminal result MUST NOT roll the answer back to pending. A failed later HTTP attempt likewise does not erase an earlier confirmed application result. Repeated copies of the same verified result do not produce another notification or service effect.

The service's terminal result is immutable for that submission. A correction, reversal or later business-state change requires a separately identified authorized operation that references the earlier result; it does not rewrite the receipt to pretend the original action never happened. The [receipt encoding](service-answers.md#receipt-schema) compares the stable decoded result and excludes transmission timestamps and credentials, so different transmission times or renewed credentials do not create false conflicts.

Conflicting terminal results remain a conflict until an authenticated reconciliation mechanism explicitly resolves them. This initial service profile defines no such mechanism, so clients preserve the evidence and offer contact with the service rather than automatically resubmitting. A status response saying “not found” is not proof that the action never occurred and MUST NOT erase a retained receipt or authorize a new submission identity. The service may have lost state or the query may have addressed the wrong scope.

The service publishes an authenticated retry-validity bound for the action. It retains deduplication evidence for accepted submissions throughout that interval and rejects new execution after expiry. If a client cannot establish that retry remains safe, it keeps the result uncertain and offers a status check or ordinary contact with the service. It must not silently switch to email delivery and risk performing the same action twice.

### Keeping a conversation record

The client retains the submitted answer and any verified acknowledgement as distinct records. Service confirmation does not impersonate the answering person. Sharing a receipt with other conversation participants requires the selected audience; an endpoint response is not automatically broadcast to everyone who received the question.

A mailbox gateway may accept legacy replies, but free-text interpretation is separate from authenticated button submission. Deduplication across email and HTTPS requires a common authenticated submission identity understood by both paths. Without it, the two paths are alternatives, not an automatic failover pair.

The [configured-deployment contract](service-answers.md) selects application/json requests and receipts, service-specific bearer authorization, direct HTTPS response authentication and a bound status-URI prefix. The service-question operation defines descriptor carriage; the [native service authorization contract](service-authorization.md) now defines acquisition and signed principal linking, with account-safe reconnect and retained-link authority. Full production login/current-suite execution integration remains unproven. Copied receipt JSON is not independently verifiable evidence for another participant.

::::


## Editing a message

An edit supplies a new version of the author's words. The original remains available, and replies continue to identify the version their authors actually saw.

> [!ex] Correcting the meeting time
> Alice sends “Let's meet at 3” and Bob replies “See you then.” Alice corrects her message to “Let's meet at 4.” Her client marks it as edited; Bob's reply still points to the original 3 o'clock message. It does not become agreement to the new time.

The [original meeting message](examples/meeting-original.eml) and [correction email](examples/meeting-correction.eml) show the complete proposed MIME layout. They are unencrypted examples with synthetic principal identifiers, not authenticated correspondence.

Only the original authenticated author can edit a message. Two devices can produce competing edits; show both until that author explicitly resolves them. An ordinary follow-up that says “I meant 4” remains a follow-up unless it carries an authorized edit operation.

An edit's readable email includes the replacement text and says which earlier message it corrects. Older recipients can read the correction without needing their client to modify mail already received. Sending an edit to fewer people does not retract the original from anyone else.

The [edit state rules](interaction-state.md#message-edits) define these proposed semantics. The [joined edit experiment](evidence/README.md#joined-protected-message-edits) authenticates explicit edit support, delivers corrections over SMTP, preserves immutable versions and derives conflict-aware views. Only devices that negotiate the selected edit operation may apply it; independent-client interoperability remains untested.

## Reactions

A reaction expresses sentiment about one exact contribution. It is not a button answer, invitation acceptance or authorization. The sender chooses its audience through the ordinary reply controls; past thread membership does not add recipients.

The [reaction contract](reactions.md) defines the candidate `reaction` and `reaction-withdraw` operations, exact targets, pinned emoji vocabulary and current-view rules. Retrying one event does not count twice; intentionally sending another equal reaction creates a distinct contribution. An explicit withdrawal changes the current view while retaining history.

Local schema, snapshot and readable-projection experiments exist. The proposed RFC9078-compatible layout and its representation-deduplication rules remain candidate integration work. The [legacy reaction example](examples/reaction.eml) is still an unencrypted legacy-only fixture, not an authenticated structured reaction.

## Readable email fallback

A rich question still needs to be a useful email. Its plain-text and HTML versions include the question, choices and context. A submitted answer includes the selected values. A fallback can explain how to reply; it cannot assume that an older client will execute an HTML form.

> [!ex] What an older client can show
> **Which day works?**
> Choose Tuesday or Thursday. Reply with your choice.
>
> **Bob's answer:** Thursday.

An upgraded client chooses one usable representation; it does not display all copies of the same content. A reader can still choose plain text. If a required rich feature is unsupported, the interaction stays inactive and a supported readable version remains available.

> [!norm] The versions must mean the same thing
> The structured payload cannot turn an innocuous visible message into a different action. Authentication failure must remain visible; selecting a readable version cannot make failed verification appear successful.

For an encrypted delivery, the readable versions belong **inside** encryption. An ordinary copy for another recipient is a separate delivery governed by [fallback policy](delivery-policy.md), not plaintext beside ciphertext in the same protected message.

:::: {.details summary="MIME layout and complete readable examples"}

### MIME and readable alternatives

MIME `multipart/alternative` can carry equivalent representations of a contribution.[^1] For a contribution without embedded resources or independent attachments, the proposed packaging is one `multipart/alternative` entity containing, in order:

1. `text/plain`, with the question, choices or submitted values expressed as readable text.
2. `text/html`, expressing the same contribution within the defined rendering profile.
3. A versioned structured application representation using the [candidate event media type](media-type-registration.md) and supported operation schema. The type is not registered; complete MIME/security integration remains under development.

This selects the arrangement for the simplest profile; it does not register a media type. Related resources and independent attachments follow the composition rules below; protected envelopes still require their security-profile composition rules. They must not be added as arbitrary sibling alternatives, because an attachment is not another representation of the contribution.

::: {.details summary="Inherited: alternative representations — RFC 2046 §5.1.4"}
The source defines ordered alternatives for the same information, with the preferred representation last. Email/2 proposes new structured semantics without changing that ordering rule. Selection must still leave a supported readable alternative available. The resource composition below nests an HTML compound object as one alternative. Independent attachment references use the experimental binding below; embedded rich-body references use the separately negotiated [rich-message contract](rich-messages.md).

The source also distinguishes the identifiers of an alternative container and its representations. Those identities must be considered in the event mapping. See the [MIME audit findings](baseline.md).
:::

A conforming upgraded client selects one usable alternative under local preferences. It does not automatically display all versions. If the user chooses plain text, that choice remains available even when the structured type is understood. An unsupported required rich capability makes the rich alternative unusable for interactive processing, so the receiver selects an earlier supported representation.

All important human-readable content belongs in the alternatives themselves. Preambles and epilogues may be ignored or discarded by MIME processors; the profile does not use them for required context, capabilities, keys or controls. Non-Content headers inside body parts are likewise not a dependable channel for essential metadata.

If an encrypted or authenticated rich representation fails validation, the client must not silently present an unauthenticated alternative as though it passed. Any available readable fallback is labeled according to its actual protection and provenance. A known signature or encryption failure remains visible even if the message can be read.

The readable alternatives must preserve the question, choices, submitted answers, and context necessary to understand the contribution. They need not reproduce the same controls. A fallback form can list its fields and explain how to reply; it cannot assume legacy clients execute HTML forms.

> [!norm] Equivalent meaning
> The proposed contract requires alternatives to describe the same contribution. A structured payload must not turn an innocuous visible message into a different action. Unknown required features leave the interaction inactive and expose the readable representation.

In an encrypted delivery, sensitive alternatives belong inside the encrypted envelope. A readable copy for an incompatible recipient is a distinct delivery under the sender’s fallback policy, not a plaintext alternative beside ciphertext in the same protected message.

### Readable question and reply examples

The exploratory general-form [question message](examples/question.eml) and [answer message](examples/answer.eml) are complete unencrypted MIME examples with plain-text and HTML alternatives. They illustrate readable compatibility for the deferred form design, not the first-version button wire format. Both representations preserve the choices, the selected answer and the distinction between an unanswered optional field and an intentionally supplied value. The answer references the question through ordinary reply headers.

These examples demonstrate readable compatibility only. They contain no structured application part, signature or key advertisement, and do not authorize machine interpretation as a verified button answer. The first-version [button question](examples/button-question.eml) and [button answer](examples/button-answer.eml) separately include the candidate structured representation; their protection envelope still requires the selected security profile. The [fixture checks](evidence/README.md#readable-mime-fixtures) validate MIME structure, line endings and matching visible content; no legacy-client delivery is claimed.

::::

:::: {.details summary="How the experimental readable projection is generated"}

### Readable projection experiment

The [readable projection experiment](evidence/README.md#readable-contribution-projections) generates plain text and inert HTML for ordinary messages, button questions and answers, candidate edits, and independent attachments. It also retains exploratory form, submission and withdrawal projections; those broader forms are not first-version client requirements. Both representations contain the same textual content. Author strings are escaped before insertion into a fresh HTML document; no sender-authored HTML, form controls, URLs or external resources are activated by this generator.

For the deferred general-form experiment, a submission projection resolves the exact form revision before using labels or choices. Missing or conflicting revisions do not permit substitution of a newer form. Unknown fields or choices invalidate the complete projection. Unanswered fields, intentionally empty text and an empty choice selection remain distinguishable. Choice display follows the referenced definition's order. Reply and replacement references remain explicit rather than silently disappearing from the fallback.

This is candidate content generation, not permission to transmit. The sender's delivery policy still controls whether a recipient receives plaintext, hosted access or encrypted alternatives. For protected delivery these readable alternatives belong inside the protected object. The projector generates readable content; it does not itself authenticate the event, retrieve attachment bytes or establish rendering/accessibility conformance across clients. Edit projections and generated MIME examples are implemented locally. The attachment operation separately defines structured display authority and resource validation below. The [joined protected-carrier experiment](evidence/README.md#joined-protected-carriers-and-deliberate-attachment-download) supplies authenticated MIME integration for its selected message, button, reaction and attachment operations. The [joined edit experiment](evidence/README.md#joined-protected-message-edits) supplies authenticated processing, durable views and separately authorized ordinary corrections for plain-message edits; independent-client interoperability remains untested.

::::

## Attachments and embedded content

An attachment is a file accompanying the contribution. An embedded resource, such as an image used in its body, is part of its presentation. Neither is another version of the message.

> [!ex] A file's label and bytes must agree
> Alice sends “Here is the agenda” with `agenda.pdf`. An upgraded client gets the attachment's name, description and expected bytes from the authenticated contribution. A different filename in a neighboring MIME part cannot rename it as a trusted executable. Missing or altered bytes leave an unavailable attachment beside the still-readable message.

The experimental attachment operation binds each file's description to its complete bytes. It checks size and digest before releasing a resource to a renderer. The client still applies its own type, decoding and execution restrictions: authentic bytes can be unsafe to open.

Resources are scoped to their contribution. A missing image or file never authorizes searching another conversation, fetching a guessed URL or revealing content from a cache. Unlisted files can remain available in the original-message view, but cannot acquire the contribution's verified-author indication.

:::: {.details summary="Attachment operation, descriptions and integrity manifest"}

### Attachment-message operation

The contribution envelope also accepts `attachment-message`, with exactly five required members: `kind` equal to `attachment-message`, `text`, `replyTo`, `manifest`, and `attachments`. Text and reply references follow the ordinary message operation's rules. The manifest and attachment descriptions follow the representations above. At least one attachment is required, and every manifest entry MUST have exactly one attachment description. This operation has no hidden or embedded-body resources. Attachment order comes from the descriptions array, independently of manifest order.

All five members are part of the same authenticated event content. Receivers validate the complete schema before processing any resource. Resource failure does not erase independently authenticated message text, but MUST be reflected on the affected attachment; no placeholder or substituted file may be presented as verified bytes. Reply resolution uses the same exact-reference and audience rules as ordinary messages.

Readable fallback includes the message text followed by attachment names, descriptions, claimed media types, byte lengths and resource identifiers. These labels remain inert author text. The fallback MUST NOT claim that listing a resource establishes its availability or integrity. Actual attachment parts follow the bundled-resource mapping and ordinary MIME attachment presentation. Protected delivery keeps both readable fallback and resources within the protected boundary. Sending policy remains independent of projection generation.

This selects composition for independent attachments. Rich HTML bodies, embedded media and their authenticated representations use the separate [rich-message profile](rich-messages.md); `attachment-message` MUST NOT be advertised as complete rich-body support. The [attachment-operation experiment](evidence/README.md#attachment-message-composition) connects schema validation to readable projection without claiming MIME or encryption interoperability.

### Authenticated attachment descriptions

An attachment description has exactly four required string members: `resource`, `name`, `description` and `mediaType`. `resource` names an entry in the same event's resource manifest. Each resource appears at most once in the attachment-description array; array order is the author's presentation order. An empty array means no independent attachments. Resources used only for a rich body need not appear in this array.

`name` and `description` are Unicode scalar-value strings. Empty strings are allowed and receive neutral client labels where necessary. Their values are author-supplied display text, not markup, a filesystem path, a trusted security message or permission to execute content. Receivers MUST escape them for their display context and apply platform-safe filename generation when saving, independently of the original display name. They MUST NOT silently rewrite the authenticated value in stored event content.

`mediaType` contains a lowercase ASCII MIME type and subtype separated by one slash. Both components use nonempty MIME token spelling; whitespace and parameters are forbidden in this field. This identifies claimed content type only. A receiver MUST apply the rendering profile's media allowlist and decoder limits independently, and MUST NOT execute a resource merely because its claimed type is recognized. Unknown types remain downloadable attachments subject to user action and local policy. This field does not define text character encoding; any future inline text-resource feature must specify it separately.

These descriptions MUST be authenticated with the manifest and enclosing operation. For profile-generated MIME, attachment Content-Type and filename parameters are projections of this metadata, using applicable MIME parameter encoding. A conflicting unprotected MIME label cannot override the authenticated description. Receivers preserve such discrepancies as diagnostics rather than granting the substituted label authority. A valid description does not make missing or invalid resource bytes available.

The [attachment metadata experiment](evidence/README.md#attachment-metadata) validates this component. The attachment-message operation below selects its placement for independent attachments; existing text-message operations retain their exact three-member schema.

### Resource manifest representation

The proposed resource manifest is an array of objects, each containing exactly `id`, `size` and `sha256`. `id` uses the nonzero, lowercase, 128-bit ObjectId spelling defined by the event encoding profile and MUST be unique within the manifest. `size` is a string containing the canonical decimal representation of an unsigned 64-bit integer: zero is `"0"`; other values have no leading zero, sign, fraction, exponent or whitespace. `sha256` is the lowercase 64-character hexadecimal SHA256 digest of the complete resource bytes. Unknown members invalidate this version of the manifest. An empty array means no resources.

The digest and length cover resource plaintext after transfer decoding and successful decryption, before character decoding, image decoding, newline conversion or other presentation transformations. Content-transfer encoding and ciphertext framing do not contribute to these values. A resource MUST NOT be released to a renderer until its complete length and digest match. Matching a digest does not make the media safe to execute or decode without bounds.

The manifest MUST be carried within the authenticated event content that references it. A resource's identity is the containing event's complete authenticated reference plus its manifest-local `id`; the ID alone is not a cross-message lookup key. The same bytes may have different resource IDs. Receivers MUST NOT use a matching digest to disclose another event's content or bypass its access policy. For encrypted delivery the manifest remains inside the encrypted content, avoiding publication of plaintext fingerprints in outer MIME headers.

Location, media type, display name and embedded-versus-attachment role are not encoded by this integrity manifest. Independent attachments use their owning descriptions; [rich messages](rich-messages.md) and [indexed replies](reply-content.md) define their separate embedded/download role inventories. The manifest does not select a carrier, extend an envelope or authorize unknown members. Complete resource support requires the current owning envelope, operation, role, carrier and safe-resource acceptance rules; manifest validation alone is insufficient.

A receiver MUST compare the wire length against its local limits before allocation or conversion to a narrower numeric representation. A valid length larger than local processing capacity yields an unavailable-resource diagnostic, not a rounded length. The [manifest experiment](evidence/README.md#resource-manifest-boundary) validates this representation and feeds bounded expectations to the assembly model; it does not authenticate the enclosing event.

### Attachment-message display authority

For an upgraded attachment-message view, the receiver MUST derive text and attachment descriptions from the validated structured operation. A neighboring text/html alternative MUST NOT replace that view's content or supply active behavior merely because it shares a MIME container. The original alternatives remain available under the ordinary message inspection interface with their actual protection status. Schema validity alone does not establish author identity: until cryptographic verification succeeds, regenerated content remains unverified.

Resource integrity is independent of readable projection. A receiver MUST retain each resource's validation outcome and display an unavailable or invalid attachment when bytes do not match, even when regenerating the text succeeds. A successful projection MUST NOT conceal resource failures or assert that the complete contribution is authenticated. Protection status belongs to the independently verified event and its exact bytes, not to a caller-provided label or a reconstructed JSON serialization.

This rule applies to the text-and-independent-attachments operation. It does not settle rich HTML body equivalence or authenticate a legacy alternative for a client that cannot read structured events. Those still require the complete protected MIME boundary and rendering profile.

::::

:::: {.details summary="MIME resource layout and binding"}

### Embedded resources and attachments

In the retained general MIME generation example, embedded HTML uses `multipart/related; type="text/html"` with an explicit `start` naming the first HTML root's Content-ID, followed by its resources. The structured representation remains the final alternative. This is not the exact current protected carrier: [mime-suite-v2](suite-profile.md#asynchronous-protected-agreement) uses the strict direct rich structure, whose related entity has its HTML root first and **no `start` parameter**. Select the complete owning carrier before generating or accepting its headers.

Independent attachments wrap the complete alternative entity in `multipart/mixed`: the contribution is first and its attachments follow. An attachment is not an alternative rendition. This arrangement is a proposed generation profile; receivers still need to interpret other valid legacy arrangements.

::: {.details summary="Inherited: related roots and content references — RFC2387 and RFC2392"}
Multipart/related chooses its root using start, or the first part when start is absent. The type parameter describes that root. Content-ID URLs connect parts; multipart/alternative selection can legitimately leave multiple representations sharing one Content-ID before selection. These mechanisms do not authenticate content or confer permission to fetch it.
:::

An upgraded renderer resolves embedded resources as follows:

1. Determine the selected related object and its root. A missing, ambiguous or type-mismatched root disables rich processing of that object; a safe diagnostic view remains available.
2. Select usable alternatives within that object before resolving identifiers shared by alternative representations. Respect the user's representation preference.
3. Parse each cid reference and decode its percent escapes once. Match the resulting identifier within the selected object using the identifier rules; do not apply mailbox aliasing or provider-specific address normalization.
4. Require exactly one eligible match. A missing or ambiguous match yields a missing-resource indication. It must not trigger network retrieval, message-store search or a search through other conversations.
5. Apply the rendering profile's permitted resource types and protection checks. A filename is a display hint, never a filesystem path. A nested related object has its own lookup scope; its resources are not implicitly exported to the outer object.

These rules define new-profile generation and rendering. Legacy MHTML has a broader local lookup model: an inner related object can reference resources in an enclosing related object. A compatibility renderer may implement that same-message lookup without exporting resources into other messages or a general web cache. It preserves Content-Location labels and their base-resolution rules; these labels are not evidence of a web origin. New-profile bundled resources use cid references and do not depend on Content-Location or HTML base elements.

Content-Location matching and cid conversion are different operations. For legacy locations, remove MIME/header encodings and resolve relative references, but do not percent-decode URI strings for comparison. For cid conversion, decode percent escapes once and match Content-ID only; a cid-valued Content-Location does not supply the target. See the [HTML aggregation audit](audits/html-aggregation.md).

A mid reference is navigation, not an embedded-resource channel. Resolve deliberate navigation under the user's local access policy without exposing inaccessible messages. The profile does not use either scheme to discover keys or capabilities.

The protected delivery must bind the compound content used by the renderer. A valid root document must not lend its authentication badge to substituted resources. The independent-attachment profile below specifies its protected boundary, canonical resource identifiers and scoped lookup. The [rich-message profile](rich-messages.md) separately defines the protected compound body and embedded-image roles; receivers still enforce applicable processing limits.

Sources: [related-parts audit](audits/related-parts.md), [content-identifier audit](audits/content-identifiers.md).

### Bundled resource binding

For the retained experimental structured-resource profile described here, each manifest entry maps to one MIME body part within the same selected compound object. Its generated Content-ID is `<resource.event@resources.email-next.invalid>`, with `resource` replaced by the entry's ObjectId and `event` by the enclosing contribution's ObjectId. The angle brackets are MIME header syntax; they are not part of the identifier returned by a MIME parser. This is a proposed local identifier convention, not a resolvable host or a service discovery address.

Current mime-suite-v2 instead uses `<resource-id.authored-event-id@resources.mail.invalid>`, with the resource ID and logical authored event ID from its original authored operation. A delivery event or outer Message-ID cannot replace that identity. Earlier carriers retain their literal resource namespace; similar text or matching resource bytes cannot authorize a cross-carrier substitution. The [current suite](suite-profile.md#asynchronous-protected-agreement) owns this exact adaptation.

An adapter MUST parse MIME header syntax and transfer encoding before binding. Within this profile it compares the resulting identifier exactly to the canonical lowercase generated form. It MUST require exactly one matching eligible body part within that compound's resource scope. Identical duplicate matches are still ambiguous. A matching part outside the scope, including an attachment's nested message, MUST NOT satisfy the reference. No lookup may fall back to Content-Location, filename, a remote URL, another message, or an unscoped cache.

The manifest's size and digest apply to the selected part's complete transfer-decoded plaintext bytes. A missing part remains unavailable. Duplicate matches remain ambiguous. A length or digest failure makes the selected resource unusable; it MUST NOT inherit the enclosing event's protection indication. These outcomes do not change a protected contribution into an unprotected one or authorize resending its content in plaintext. Clients may display the independently validated contribution with an explicit unavailable-resource indication where its operation permits incomplete presentation; an interaction requiring the unavailable resource cannot be executed.

The compound object and its structured event MUST be inside the same protected-content boundary for encrypted delivery. Outer unprotected MIME parts cannot supply protected resources. This rule binds bytes, not MIME labels: media type, filename, accessibility description and display role require authenticated operation metadata before a renderer can use them as author-supplied claims. Independent attachments use the description schema below. Header fields alone supply no such authority.

The [bundled-resource experiment](evidence/README.md#bundled-resource-binding) integrates manifest shape, scoped identifier selection and complete-byte assembly using already parsed parts. It does not parse MIME, perform decryption or establish that a caller chose the correct compound scope. Those remain adapter responsibilities and required interoperability work.

### Attachment metadata

New-profile generators use ordinary unsplit boundary and charset parameters. Non-ASCII human-readable parameter values use RFC2231 with an explicit UTF-8 charset. They do not use RFC2047 encoded words as MIME parameter values or generate competing forms of the same parameter.

A receiver reconstructs numbered continuations by numeric index, independently of parameter order. It decodes escapes only in encoded segments, once, and interprets the combined octets using the declared charset. Missing or repeated indices, leading-zero indices and conflicting forms are not silently resolved into authoritative metadata. An ambiguous filename produces a neutral attachment label while the original metadata remains available. No filename selects a filesystem path or grants permission to execute content.

Independent attachments use attachment disposition. Unknown disposition types receive attachment handling; they are not hidden or discarded. Opening an attachment permits presentation, not automatic execution or form submission. For attached multipart containers, deliberate opening precedes child presentation; related-aware resource handling follows the compound-object rules instead.

File creation, modification and read dates are attachment metadata, not conversation ordering, presence or read receipts. The size parameter is approximate; receivers enforce limits against actual processed content. See the [content-disposition audit](audits/content-disposition.md).

See the [MIME parameter audit](audits/mime-parameters.md) for inherited rules, corrections and proposed failure handling.

### MIME filename projection

The authenticated attachment name is display data and can contain characters unsuitable for a MIME header. For this generation profile, replace each U+0000–U+001F character and U+007F with one underscore when deriving the MIME filename parameter; if the resulting string is empty, use `attachment`. Encode the resulting parameter with the applicable MIME parameter rules. This projection MUST NOT replace the original `name` in the structured event or change its authenticated bytes.

An expected difference caused by this specified projection is not itself a metadata-substitution diagnostic. Other discrepancies remain subject to the attachment metadata rules. This transformation only makes the projected value suitable for header serialization; it does not make it a safe filesystem path or eliminate misleading Unicode. Saving a file still requires independent platform-safe naming and explicit overwrite handling.

### Composite files as opaque attachments

In the attachment-message generation profile, a resource whose authenticated claimed media type has top-level `message` or `multipart` MUST use `application/octet-stream` for its outer resource-part Content-Type. Preserve the original claimed media type in the authenticated attachment description. This explicit projection keeps nested message headers, multipart boundaries and related-resource scopes inside the attached file rather than interpreting them as structure of the enclosing contribution.

The resource digest continues to cover the exact original file bytes. A receiver MUST NOT parse, normalize or reserialize the nested document before validating those bytes. Deliberate opening may invoke a separately bounded viewer appropriate to the claimed type, but that viewer MUST retain a distinct origin and protection context. Nested senders, subjects, signatures and resource identifiers do not acquire authority over the enclosing conversation. This rule does not alter how an ordinary legacy message/rfc822 attachment is received outside this generation profile.

The specified application/octet-stream projection is an expected metadata difference, not evidence by itself of substitution. It carries no claim about whether the attached document is safe, authentic or well-formed. Other media types use their claimed bare type in this experimental generator, subject to the rendering profile's independent handling rules.

### Unlisted MIME resources

An attachment-message receiver MUST compare the selected MIME resource inventory with the authenticated manifest. Missing entries, repeated matches and unlisted parts are distinct diagnostics. Repeated matches remain ambiguous even if their bytes are identical. An unlisted part MUST NOT be inserted into the structured attachment list, acquire the event's verified-author indication or be passed to an embedded renderer through that event's resource namespace.

A receiver MAY retain unlisted parts for ordinary raw-message inspection under their actual protection context. It MUST NOT silently discard the evidence or describe the package as an exact manifest match. Independently validated listed attachments and message text can remain available with the inventory discrepancy shown; their validation does not authenticate the extra parts. Matching the inventory is only a structural check and does not establish resource integrity or authorship.

::::

:::: {.details summary="Retrieving and assembling resource bytes"}

### Provider blob retrieval

A JMAP blob ID or lookup result MUST NOT substitute for an authenticated Email/2 resource reference. Preserve the provider/account context, enforce access permissions and validate the final resource under the selected content-binding profile. A server-supplied digest alone does not establish authorship.

For Blob/get, the size field describes the whole blob while returned data and digests describe the selected range. A truncated or partial response MUST NOT satisfy a full-resource integrity check. Reassembly must preserve exact byte offsets and complete coverage before full-resource validation. Invalid UTF-8 in binary content MUST NOT be repaired into substitute authenticated bytes. No renderer may activate an unvalidated partial resource. See the [JMAP blob audit](audits/jmap-blobs.md).

### Complete-resource assembly evidence

The [resource assembly experiment](evidence/README.md#complete-resource-assembly) demonstrates exact-byte reconstruction before release to a renderer. It permits out-of-order chunks and identical overlaps, rejects conflicting overlaps and out-of-range spans, and withholds bytes until coverage and the expected whole-resource digest match. Splitting a UTF-8 character across chunks does not permit text replacement or per-chunk character decoding.

The expected length and digest must come from the selected authenticated resource-binding mechanism; copying them from the same untrusted download does not establish authenticity. The experiment uses caller-supplied SHA256 fixture expectations, with the proposed manifest adapter below providing wire-shape validation. Its caller-provided size limit is local policy rather than a universal attachment cap. The model also requires explicit chunk-count and cumulative-input-byte limits, including repeated overlaps, before allocating the output. Production processing-time, allocation and streaming-storage policies remain necessary.


A resource receiver MUST bound both output size and work spent on incoming fragments. Repeated identical bytes still consume processing resources; empty fragments still consume indexing and request overhead. A final-size check alone is insufficient. Exceeding a local processing limit leaves the resource unavailable with an incomplete-processing diagnostic; it MUST NOT produce a truncated replacement resource or authorize a protection downgrade.

::::

## Threading and mixed participants

Preserve ordinary `Message-ID`, `In-Reply-To`, and `References` relationships for legacy interoperability.[^2] The [mail identity and one-parent projection contract](event-identifiers.md#map-contributions-to-ordinary-mail) maps actual per-copy mail versions to contributions and retains their identifiers across exact retries; independent recipient-specific versions need not share an outer identifier.

::: {.details summary="Inherited: message identity and replies — RFC 5322 §3.6.4"}
A message identifier denotes a particular message version. Adding ordinary trace headers does not require a new identity. Replies may have multiple parent identifiers in `In-Reply-To`, but the source does not define a general multi-parent construction of `References`. The structured graph uses its selected single primary parent for the legacy projection; quotations and replacement dependencies do not become additional legacy parents.

The authenticated event identity remains necessary because one accepted contribution can have several independently prepared mail representations and an outer identifier does not authenticate authorship. The [exact mapping](event-identifiers.md#map-contributions-to-ordinary-mail) preserves Message-ID as a mail-version identity, not a delivery-attempt identifier. Private-copy and masked-delivery rules suppress public links where required.
:::

An ordinary inline reply remains an ordinary message. A client may infer its relationship to a question, but must not manufacture an authenticated structured answer from that inference. The [rendering chapter](rendering.md) defines this distinction.

Adding a recipient does not automatically disclose previous history. Forwarding is a new disclosure to a new audience. Bcc recipients must not be exposed through shared membership records, key lists, or capability advertisements. Mailing lists and aliases require explicit analysis before claims of transparent encrypted compatibility.

## Conversation history and forwarding

> [!ex] Forwarding an answer without the whole conversation
> Bob receives “Thursday works” with the question “Which day works?” as context. Earlier discussion remains in his mailbox. When he forwards that answer from an older client, those earlier messages are not bundled into the email he forwards.

> [!norm] A conversation is assembled from individual messages
> Each delivery carries the current contribution and the context needed to understand it. Relationship metadata identifies earlier contributions; it does not carry a hidden transcript. An upgraded client builds the conversation view from messages available to that account.

The ordinary readable reply body SHOULD show these two contributions, in order:

1. The new response.
2. The message it answers, with that message's inherited quoted or forwarded chain omitted.

> [!ex] A rolling two-contribution window
> Bob's reply carries Bob's response followed by a preview of Alice's message. Carol replies to Bob: her new email carries Carol's response followed by Bob's contribution, without the previous preview of Alice's message. A subsequent reply repeats the same rule; previews do not accumulate into a transcript.

The copied parent is its contribution, not its entire previously delivered body. Exclude that parent's own appended reply-context preview when constructing the next reply. This changes the new outgoing projection only; it does not delete earlier received messages or erase deliberately authored quotations and interleaved answers. Where the selected format supplies explicit boundaries, use them. A legacy heuristic must not treat every blockquote as a disposable preview or silently remove authored text. If a previous preview cannot be separated reliably, omit the automatic preview or let the sender select a passage instead of recursively copying the whole body.

The second contribution is the selected reply target, even when the author answers an older message rather than the latest arrival. It is context for this reply, not a recursively copied transcript. A question's wording or selected passage may supply sufficient context; an interleaved answer keeps the authored order needed to understand it. Missing context, uncertain legacy boundaries or disclosure restrictions can require a new-content-only reply.

Choose and encode that context during composition under the selected content/carrier contract, before freezing, signing or encrypting the new contribution. Do not append unindexed or unauthenticated context after preparation, widen a retained profile or claim that a reference alone carries its source.

Generating a readable fallback does not append the conversation transcript, place it in custom headers, hide it in HTML, or include it as an undisplayed MIME part. Quoted context is still disclosed content: it must be appropriate for the delivery's audience and visible in the readable representation. An answer may need its question or selected option label, but not every preceding message.

An upgraded client's **Forward this message** action shares the selected contribution and its displayed context. Sharing additional history is a separate selection, with the included messages and destination audience visible before sending. Conversation membership, private recipient lists, access credentials and unrelated event metadata are not copied merely because they are present in the client's local conversation state. Forwarded content retains its distinction from a newly authored contribution and does not imply the original author's authorization of the new audience.

A selected file or embedded resource is disclosed as the exact bytes included in the new delivery. Those bytes can contain metadata that is not visible in the message preview. A client must not describe an unchanged original file as a metadata-free or pixels-only share. A deliberately generated replacement is a new resource with its own bytes, identifiers and integrity commitments; it cannot retain the original resource's identity while changing its contents. Original controls, credentials and source-event references do not become active in the new audience merely because their visible labels were copied.

A missing predecessor MUST NOT prevent the client from displaying an independently authenticated, self-contained contribution. Show that its referenced context is unavailable rather than inventing quoted text or treating arrival order as conversation order. Operations that depend on the missing event—such as applying an edit or resolving a button answer—remain pending until their own validation requirements are satisfied. Reading a message and applying its effects are separate decisions.

Missing history remains missing unless it is already available locally or obtained through a separately authorized retrieval mechanism. A message identifier or relationship reference is not an access credential. A client must not automatically fetch a sender-supplied history URL or transmit account credentials to it. The [authorized history-transfer contract](history-transfer.md) supplies one explicit request, approval and historical-import path, including unavailable content and interrupted delivery. It is not automatic relationship retrieval; any additional retrieval mechanism needs its own authorization, unavailable/deleted-history and offline rules.

::: {.details summary="What existing email can and cannot preserve"}

`In-Reply-To` and `References` describe relationships without embedding earlier message bodies. They can still reveal relationship metadata; placing information in a header does not make it private.

Existing forwarding has no universal metadata-removal contract. A new inline forward may omit fields, while an attached original message can preserve its headers and MIME parts. Redirecting or resending can preserve the original message as well. Consequently, neither a custom header nor a MIME presentation hint can guarantee that an older client will omit hidden history when forwarding. See [RFC5322 §3.6.6](https://www.rfc-editor.org/rfc/rfc5322.html#section-3.6.6) and [RFC2046 §5.2.1](https://www.rfc-editor.org/rfc/rfc2046.html#section-5.2.1).

Keeping the transcript outside the individual delivery prevents that delivery from accidentally carrying it onward. It does not prevent a recipient from deliberately copying other messages they can access. A raw-message export or forward-as-attachment also requires its own complete-content disclosure; the selected-contribution action must not silently substitute either operation.

:::

### Replying to a legacy chain without carrying its history

> [!ex] Adding Carol without copying Alice and Bob's earlier discussion
> Bob replies to Alice and adds Carol. His app sends his new writing to the selected audience. It does not automatically append the earlier chain that happened to be inside Alice's message. Bob can deliberately include a relevant passage, with its audience and protection checked separately.

A client SHOULD compose replies to legacy mail using the two-contribution layout above: its new response followed by the immediate parent contribution. Remove the parent's older quoted or forwarded history from that outgoing copy by default; do not recursively copy the complete received body or the conversation view. Older material may appear above, below or between the parent's own words, so position alone is not a reliable boundary. The sender may omit, reduce or deliberately extend the selected context, subject to the same disclosure rules. [Legacy reconstruction](rendering.md#old-messages-remain-original-evidence) may help locate passages, but its uncertain classifications are not authority to discard inline answers or rewrite the received original.

Adding a recipient, expanding a list or alias, moving a private reply into a discussion, forwarding to another audience or changing to a less protected delivery requires a fresh disclosure check for every included source passage and resource. The client MUST NOT automatically carry earlier history into that changed audience or weaker delivery merely because it was present in the reply draft. Keep the sender's new writing. Reassess the immediate parent as well as older quotations: omit copied material not authorized for the changed audience or weaker delivery, and make deliberate inclusion inspectable against the final recipients and per-copy protection. Permission to send new unencrypted writing does not itself authorize copying earlier protected or private content into it.

Omission must apply to the actual outgoing representations: plain text, HTML including hidden/collapsed regions, copied MIME parts and inline resources. A visually collapsed quotation is still disclosed if its bytes are sent. Do not carry a raw original or an attached transcript as an invisible substitute. A deliberate forward-as-attachment or raw export remains a separate complete-content disclosure under the complete-content rules above.

When a legacy boundary is uncertain, keep the received source intact and offer deliberate passage selection or a new-content-only reply. Do not claim that a heuristic extraction is a verified or complete account of the latest author's contribution. The composer must let the sender inspect exactly what copied context and resources will leave; presentation cleanup alone does not establish safe disclosure. This minimizes new copies; it cannot withdraw history already received by earlier participants or their services.

Acceptance cases must cover the normal response-then-parent layout, omission of the parent's older chain, three or more successive replies whose context window remains two contributions, preservation of deliberately authored quotations, an explicitly selected earlier reply target, adding a recipient after drafting, switching a copied passage to ordinary delivery, top-posted and interleaved history, changed quoted passages, hidden HTML and alternative MIME copies, ambiguous source boundaries, and deliberate forwarding of a complete original. Check the bytes actually sent as well as the composer preview; source preservation and reduced outgoing disclosure are separate outcomes.

## Failure behavior

| Condition | Proposed outcome |
| --- | --- |
| Target arrives later | Preserve the event; show it independently until the relationship can be resolved |
| Duplicate event | Do not apply it twice |
| Same identifier, conflicting content | Preserve conflict evidence; do not silently overwrite |
| Invalid structured representation | Render a safe readable alternative; do not execute the interaction |
| Authentication failure | Do not attribute an authorized action to the claimed author |
| Recipient capabilities differ | Select compatible delivery per recipient, subject to security policy |

## Processing existing email

Existing mail remains readable even when it cannot become a structured interaction. Clients preserve its original bytes and keep recovery, display interpretation and verified authorship distinct. These parsing rules support that boundary; they do not require users to understand MIME before reading a conversation.

:::: {.details summary="MIME transfer decoding and character interpretation"}

### MIME decoding boundary

An Email/2 generator uses `MIME-Version: 1.0`. The rich-content profile carries its own version. Changing the MIME version is not a way to advertise a new interaction or encryption protocol.

A receiver processes each selected MIME entity through these distinct stages:

1. Parse its MIME headers using their defined grammar, including permitted comments and quoting. Preserve case where a parameter's definition requires it; multipart boundaries are not case-folded.
2. Identify the entity's transfer encoding. Missing encoding means `7bit`; an unknown encoding leaves the entity opaque, treated as `application/octet-stream` under the inherited MIME rule. Do not activate its claimed HTML or structured semantics.
3. Decode the transfer representation into octets. Transfer decoding must precede character decoding. A quoted-printable soft line break is not a displayed line break; base64 wrapping is not part of the decoded content.
4. Interpret those octets using the selected media type's charset and syntax rules. Absent or invalid MIME typing does not authorize sniffing for executable interactions. A safe local legacy-text view may still be offered.
5. Validate the rich profile and its authentication requirements before applying structured behavior. Successful MIME decoding alone is not validation of an answer, service submission or key advertisement.

A receiver may recover malformed legacy text for display while retaining its original and identifying the recovery. The recovered display text must not replace the bytes used for a security decision. The selected security profile defines exactly which representation is authenticated and how it is obtained.

Unknown MIME parameters are ignored under the base MIME rules. A new interaction therefore cannot make an optional, unfamiliar MIME parameter the sole carrier of a required semantic restriction. The rich representation must independently identify its required profile and capabilities; a receiver that does not support them leaves its actions inactive.

Content-ID identifies a MIME entity. It is neither a cryptographic author identity nor permission to fetch arbitrary external content. Content-Description is human-readable description, not a hidden command channel.

Source: [RFC 2045 audit](audits/mime-format.md). Full multipart composition and later encoding updates remain separate review items.

::::

:::: {.details summary="Address, header and internationalized-message handling"}

### Receiving existing message formats

The following are proposed receiver requirements, derived from the [message-format audit](audits/message-format.md). They preserve the difference between interpreting received mail and authorizing a rich interaction.

A receiver parses current and documented obsolete syntax with the applicable verified corrections. A generator emits current syntax. Receiving an obsolete form does not authorize emitting it in a new message. Parsing must guarantee progress, handle nested comments and quoted delimiters, and apply declared local resource limits without claiming those limits come from the message-format standard.

The receiver retains the original message when rich interpretation fails. It exposes a safe fallback and the reason rich processing is unavailable. It must not execute control characters when presenting raw headers or body content. Stored originals and derived visual projections are distinct objects.

Parse address structure before decoding encoded words in permitted display-text positions. Decoded commas, angle brackets or address-looking names must not be reparsed into mailboxes. Keep the parsed mailbox, display label and original header distinct. Malformed or unknown encoded text leaves a safe readable fallback; it does not prevent reading the message or authorize guessed identity bindings. MIME parameter and field-specific encoding rules remain distinct from encoded-word display handling. See the [header-text audit](audits/header-text.md).

Author, transmitting agent, reply destination and transport trace remain separate roles. A valid address group may provide no individual mailbox. Repeated originator fields, multiple authors, ambiguous obsolete local parts and empty originator groups do not produce an automatic cryptographic identity. Until an authenticated binding resolves the ambiguity, key advertisements and structured actions remain unverified. This does not prohibit reading or manually replying to the message.

A receiver must not globally strip plus tags, remove local-part dots or fold local-part case to determine key ownership. Provider-specific equivalences need authenticated evidence and an explicit scope. A display name never supplies that evidence.

Missing `Message-ID` does not make an otherwise valid legacy message unreadable. Any local identifier assigned for display remains local and unauthenticated. Repeated destination fields are combined according to the obsolete receiving rules; that rule must not be generalized into first-wins or last-wins processing for repeated author fields.

::: {.details summary="Inherited: resending, forwarding and trace"}
RFC 5322 §3.6.6 defines resent fields as informational records prepended in blocks. Resending preserves the original authorship context; forwarding introduces a different operation. Resent fields do not determine ordinary reply processing. The obsolete `Resent-Reply-To` field is therefore not authority for an automatic answer or key exchange.

Trace-field syntax comes from §§3.6.7 and 4.5.7, with verified erratum 3979. Operational SMTP semantics are separate. Neither the presence of trace fields nor a resent sender establishes cryptographic authorship.
:::

Delivery attempts and application effects are separate. The [transport chapter](transport.md) specifies per-recipient failure state and atomic duplicate suppression.

### Internationalized messages

Generate ASCII Message-IDs for mixed-client interoperability; retain valid received internationalized IDs and their references. Native UTF-8 header values require SMTPUTF8 when sent via SMTP, including when only body-part headers contain non-ASCII text. Ordinary MIME-encoded UTF-8 body content is a separate case. Field names remain ASCII.

Never invent an ASCII alias or transliterate a mailbox to bypass missing SMTPUTF8 support. A compatible outer message can carry a suitably encoded message/global attachment, but that does not make the embedded message's internationalized recipient routable over an ASCII-only path. Unaware clients may treat that attachment as opaque.

Validate UTF-8 and count line limits in octets where required. Preserve original protected bytes and mailbox identities; display normalization must not rewrite either. New message generation follows the source's NFC recommendation without applying compatibility normalization to received identities. See the [internationalized-header audit](audits/internationalized-headers.md).

::::

:::: {.details summary="Selecting the body of a protected legacy message"}

### Related-root traversal for protected legacy messages

When identifying a main body within multipart/related, a receiver MUST follow the unique root selected by the valid `start` parameter, or the first child when `start` is absent, as defined by RFC2387. It MUST NOT replace that selection with a blanket first-child rule. Missing, ambiguous or type-mismatched roots retain the diagnostic behavior above. The other children are related resources, not additional main bodies merely because they have a text media type.

This receiver behavior deliberately differs from [RFC9787 Section 7.1](https://www.rfc-editor.org/rfc/rfc9787.html#section-7.1), which traverses the first child of a multipart other than multipart/alternative. The reason is interoperability with existing multipart/related messages: a valid explicit root can occur later in the child list. Ignoring it can select a resource instead of the intended body. The tradeoff is an additional root-resolution step, with ambiguous or invalid selections reported rather than guessed.

New messages use their selected carrier's exact generation rule. Current mime-suite-v2 puts the related HTML root first without `start`; the retained general generation example above puts it first with explicit `start`. Both put the root first for the simplified traversal described in RFC9787 Section 7.1 and RFC9788 Section 5.2.4. The current strict carrier does not accept `start` merely because a legacy receiver can interpret it. Any reordering during new composition occurs before signing or encryption. Receivers MUST NOT reorder preserved signed input to make it fit that generation profile.

For receiving and replying to legacy mail, eligible main-body traversal follows the selected related root while preserving attachment and cryptographic boundaries. Header-protection decoration handling must never modify an independent attachment or treat a resource as user-authored body content. This is an explicit reconciliation of the related-root standard with the later simplified guidance, not a claim that the guidance already describes every valid MIME layout.

::::

## References

[^1]: [RFC 2046 — MIME media types](https://www.rfc-editor.org/rfc/rfc2046.html).
[^2]: [RFC 5322 — Internet Message Format](https://www.rfc-editor.org/rfc/rfc5322.html).
