---
title: Interaction state and conflicts
order: 2
blurb: revisions · duplicate delivery · concurrent answers
sectionNav: true
---

# Interaction state and conflicts

This chapter defines proposed application semantics independently of transport order. It is an editorial design, not an adopted standard. The [experimental form operation schemas](form-operations.md) encode form revisions, submissions and withdrawals. Message edit semantics and the exact operation object are specified here. The explicitly negotiated profile below has a joined authenticated delivery experiment. Neither the schemas nor these state rules establish cryptographic validity or register a media type.

> [!note] First-version interaction scope
> The first version supports [questions with predefined answer buttons](messages.md#questions-and-answer-buttons). General forms, typed fields and multiple-choice sets are deferred. The form revisions, submissions, withdrawals and form receiver algorithm below describe that broader experiment; they are not first-version conformance requirements. The shared immutable-record and authority rules also apply to answer buttons.

## Immutable records and authenticated authority

An interaction record has an event identity, author identity, conversation identity, intended audience, operation and explicit references. Authentication produces an author principal under the selected security profile. Mailbox text alone is not that principal. Key rotation may preserve a principal only through the security profile's verified continuity rules.

The receiver stores the original record and its validation evidence before deriving state. It MUST NOT mutate a received record to make it conform. A local display label, inferred quotation relationship or repaired legacy message does not become an authenticated record.

An event identity is scoped to its authenticated author principal. The [identifier contract](event-identifiers.md) defines the experimental grammar and exact references. The authenticated record must additionally bind its conversation and operation. The receiver MUST NOT deduplicate events solely by a globally supplied identifier: another author could otherwise suppress an event by claiming the same identifier first. An unauthenticated delivery cannot reserve an authenticated author's identity namespace.

Two deliveries with the same scoped identity and identical authenticated record are one event. Two different authenticated records with that identity are an identity conflict. Preserve both, disable effects from that conflicted identity and recompute dependent state. Do not choose the first arrival. Equality is determined by the security profile's authenticated representation, not a normalized display string or the outer MIME transport encoding.

> [!warn] Signature validity is not sufficient authority
> A valid signature identifies a signer under a profile. It does not by itself authorize that signer to revise another person's question, replace another person's answer, or expand an audience.

## Question and form revisions — deferred exploration

A form definition contains stable field identifiers, labels, response types, choice identifiers where applicable, and requiredness. Field identifiers are scoped to that form. A form revision is a complete immutable definition, not a patch applied according to arrival order.

The initial definition establishes its author as the form authority. A subsequent revision MUST name the form and the exact revision or revisions it supersedes, and MUST be authorized by that same principal. Delegated form editing is outside this baseline. A revision that names a revision of another form is invalid.

A new revision cannot reinterpret old values. Renaming a choice label while retaining its identifier affects only submissions targeting the new revision; old submissions retain the label and meaning from their targeted revision. Changing a field's response type requires a new field identifier. Removing a field does not erase earlier answers. A revision must retain the type history of field identifiers from all validated predecessor branches: removing and later reintroducing an identifier does not permit changing its type. If predecessor branches assign different types to the same field identifier, a merge cannot resolve that collision by choosing one type; the author must use a new field identifier.

Concurrent revisions remain separate heads. The receiver MUST NOT select a winner by timestamp, arrival order or lexicographic identifier. A later complete revision may explicitly supersede all heads it resolves. Until then, show the competing definitions and require the user to select an exact revision when answering.

## Submission values

A submission identifies one exact form revision and provides one atomic set of answers. This deferred form experiment supports text, single choice and multiple choice. Each field occurs at most once. Unknown field identifiers, duplicate fields, wrong value types and unknown choice identifiers invalidate structured application of the whole submission; do not partially apply its apparently valid fields.

Text is a string, including the empty string. Single choice is one choice identifier. Multiple choice is a set of choice identifiers; duplicates are invalid and order has no semantic meaning. Absence of a field means unanswered. An empty string or empty set means an intentionally supplied empty answer. A required field must be present; additional non-empty constraints require a separately defined capability. This distinction must appear in the composer before submission.

A submission MUST NOT be automatically redirected to a newer revision. If its target has been superseded, it remains an answer to the older revision and is labeled accordingly. The user may deliberately submit a new answer to the newer revision. A renderer must not silently copy values across revisions and transmit them.

Submission is a deliberate user action. Opening, rendering, scrolling, decrypting or receiving a message MUST NOT submit a form. The confirmation surface identifies the selected form revision, actual recipients and delivery protection. The form author's suggested reply audience is a suggestion, not authority to send data.

## Replacing and withdrawing answers

A replacement is a new complete submission with explicit supersession references. Each referenced submission MUST belong to the same author principal, form and exact form revision. A replacement across form revisions is invalid; answering a new revision is a separate submission. Supersession references may name several concurrent submissions to resolve them together.

A withdrawal is an immutable event referencing one or more of the author's submissions under the same form revision. It removes those submissions from the current answer view while preserving their history. It does not delete copies already delivered. A withdrawal does not withdraw another author's answer and does not revoke any external action already taken in reliance on the answer.

A receiver MUST resolve all references and validate authority before applying a replacement or withdrawal. An unknown referenced submission leaves the operation pending. It must not suppress an event based on an unauthenticated or unresolved reference. Cyclic supersession, self-reference and cross-author references are invalid.

For each author and form revision, current answers are the validated submissions that have neither been superseded by a validated replacement nor targeted by a validated withdrawal. If more than one remains, show a conflict. A withdrawal of an older answer does not implicitly withdraw a later replacement. A later replacement does not resurrect its withdrawn predecessor. To answer again, issue a new submission; its relationship to prior answers must be explicit.

A malformed replacement has no supersession effect. Its valid predecessor stays current. A pending replacement also leaves the predecessor current, with a pending-update indication where useful. The receiver recomputes this view whenever missing dependencies arrive or previously used evidence becomes invalid.

## Message edits

Editing changes the current presentation of a message while retaining its immutable versions. It does not change what an earlier reply, quotation or reaction referred to.

> [!ex] Two edits made offline
> Alice changes “Tuesday” to “Wednesday” on her laptop and to “Thursday” on her phone. Both edits name the original message. When both arrive, neither wins because it arrived later. Alice can resolve the conflict with a complete replacement that explicitly names both edits.

The proposed baseline edits plain-text message content only. Editing a form uses form revision rules; changing an answer uses submission replacement rules. An edit cannot turn a message into another operation, change its author or conversation, replace attachment bytes, or authorize an external action.

::: {.details summary="Edit authority, dependencies and current versions"}

### Root message and exact predecessors

An edit identifies one exact root message and a nonempty set of exact predecessors, then supplies the complete replacement text. The root must be a validated message operation. Each predecessor must be that root or a validated edit of the same root. The root, edit and every predecessor must have the same authenticated author and conversation. A shared mailbox label, matching From field or forwarded copy does not establish that authority.

An initial edit names the root as its predecessor. Later edits name the exact versions they replace. The root reference identifies the message being edited; it does not by itself supersede every known or subsequently discovered version. A conflict resolution names every competing head it intends to resolve. A receiver cannot require reference to a branch the author may not have received.

Self-reference, cyclic dependency, a reference to another root, a different author, or a predecessor of the wrong operation kind makes the edit invalid. Reject scope and self-reference violations visible in the record before resolving their targets; these invalid references must not trigger retrieval of unrelated history. Resolve and validate all dependencies before applying any supersession effect. Missing dependencies leave the edit pending; conflicting identities leave it conflicted. In either case, previously valid versions remain current. An invalid edit has no supersession effect.

### Deriving the current presentation

For one root, current versions are the root and validated edits not superseded by another validated edit. Retain all current heads. One head can be shown as the current version with an edited indicator; more than one requires a visible conflict. Timestamps, identifier sorting and delivery order MUST NOT select a winner. A local list order may organize the competing versions but cannot imply which version is authoritative.

Recompute the view when a dependency arrives or loses validity. An explicit accepted device revocation or identity conflict suspends its derived supersession effects while retaining its record and explanation. Its predecessors may become current again. Do not rewrite the stored text or authentication evidence of any version.

The selected draft policy distinguishes a device identifier in the authenticated cumulative `revoked` set from an ordinary binding replacement. Key rotation, changed roles or validity on a still-present device, advertisement expiry and offline discovery do not retroactively erase accepted edits. Later removal from a conversation likewise preserves accepted edit history. Pending or new edits still require current authority and their original membership instance and episode.

This policy uses evidence actually represented by the identity contract; absence of an old binding does not prove revocation or compromise. It is an application-level draft choice, not a guarantee supplied by MLS. Unknown current identity evidence makes the derived view incomplete or stale. The client must not invent a revocation, present an old view as freshly verified, or erase the immutable original. Explicit revocation suspends the editing effect without asserting that every earlier signature was forged. Retain the author credential and membership evidence that admitted the edit. Another copy of the same event does not replace that provenance or re-authorize its effects; a fresh correction needs a new event identity.

An edit retains the root's reply relationship. It cannot move the message under a different question or alter earlier events' references. A reply or reaction targeting the root continues to target that exact original version; one targeting a particular edit continues to target that edit. Clients may group the versions together, but MUST provide access to the exact referenced version and MUST NOT present an earlier response as acceptance of later text.

### Audience and fallback

Each edit has its own explicitly selected audience and protection policy. Receiving an edit does not grant access to an undisclosed root or predecessor. If those dependencies are missing, show the edit as a readable correction with unresolved context, without replacing another message by guessing from its subject, quoted text or timestamp. Supplying missing history requires its own disclosure authorization.

The composer warns when earlier recipients may retain an older version. Neither successful delivery nor a local current view proves that every recipient received the correction. Existing copies, quotations, downloads and external actions remain outside the edit's control.

The plain-text and HTML projection includes the complete replacement text, a clear correction label and an exact reference to the corrected contribution. Any additional excerpt from an earlier version is separately subject to disclosure policy. A legacy recipient's ordinary reply does not become a structured edit or resolve a conflict through text matching.

:::

### Experimental edit operation

The candidate operation object has exactly four required members; omission, null and additional members are invalid. It follows the strict JSON and scalar-string rules in [Event encoding](event-encoding.md).

| Member | Type and meaning |
| --- | --- |
| `kind` | Exactly `edit` |
| `root` | EventReference naming the original message |
| `predecessors` | Nonempty set of EventReference values naming versions explicitly replaced |
| `text` | Complete replacement plain-text string, including an intentionally empty string |

EventReference uses the exact three-member [identifier contract](event-identifiers.md). Duplicate predecessors are invalid regardless of member ordering. The enclosing event supplies the author, conversation and new immutable event identity; root and predecessors must match that author and conversation and must not reference the edit itself. The new text is literal text, never HTML.

A resolver checks the exact root and every predecessor. Its result is invalid if any required target is invalid, otherwise conflicted if any is conflicted, otherwise pending if any is missing, otherwise target-matched. Reference order does not affect the result. No subset has an effect before the complete operation validates.

The [edit target experiment](evidence/README.md#message-edit-targets) exercises object shape and exact target checks. It relies on a trusted resolver whose valid records have already passed authentication and acyclic dependency validation. It does not implement that graph validation, derive current heads or authorize transmission. The common contribution envelope accepts this candidate shape, and the readable projection checks exact targets before generating a correction. The [joined edit experiment](evidence/README.md#joined-protected-message-edits) supplies those stages for the explicitly negotiated profile below; the target checker alone does not.

### Negotiated protected profile

The implemented candidate selects `edit` explicitly in assertion version 5 and context version 6, with envelope version 3 and `mime-rich-v0`. Every selected device must advertise the operation in its exact signed tuple. Existing signed operation sets and immutable conversation contexts do not acquire edit support automatically. Earlier assertion/context profiles and context 7 do not gain edit support from this selection.

The operation remains exactly the four-field object above; the protected MIME carrier uses the existing readable alternatives and exact event bytes. A rich carrier does not broaden the editable root: only a `message` operation is editable here. Editing rich HTML, attachments, questions or answers is not selected. An edit can have a different explicitly authorized delivery audience without revealing missing history or changing the root's audience.

### Installing a computed edit view

Compute the view from one consistent snapshot of event records, identity conflicts and authentication evidence. Record a source token binding exact event variants, accepted author provenance and relevant current identity evidence with the result. A journal-only token is insufficient because a signed revocation can change eligibility without adding a message. Before installing the result, compare its revision with current storage in the same transaction that replaces the derived view. If relevant evidence changed, discard the candidate result and recompute; do not publish an old result over a newer revocation or conflict.

A local work budget is an implementation setting, not a protocol limit on how many edits an author may make. Exhaustion produces incomplete processing, not an invalid event or an empty conversation. It MUST NOT install partial heads or suppress a predecessor merely because only part of its descendants were examined. Preserve the last committed view with a visible stale or incomplete indication as appropriate, and suspend effects that depend on a current validated view. A changed authorization result must not remain presented as currently verified while recomputation is pending.

The experimental evaluator accepts adjustable record and reference budgets and returns no candidate heads when either is exceeded. A caller may retry against a fresh consistent snapshot with sufficient resources. It does not implement storage transactions or resumable checkpoints. The budget limits traversal work; it does not replace byte limits during parsing or constrain the cost of a resolver supplied by the caller.

### Edit conformance cases

| Input | Required result |
| --- | --- |
| Edit arrives before its root | Pending; readable correction available without guessed replacement |
| Same edit is delivered twice | One immutable version and one supersession effect |
| Two edits name the same predecessor | Both remain current; visible conflict |
| Resolution names both competing edits | One current version after all dependencies validate |
| Resolution names only one branch | The other branch remains current |
| Edit names another author's message | Invalid; target remains unchanged |
| Reply predates an edit | Reply retains its exact original target |
| Edit supplies a different root through a predecessor | Invalid; no partial supersession |
| Previously accepted predecessor becomes conflicted | Recompute dependent edits; preserve evidence and history |
| Only some recipients receive the edit | Local current view makes no global update claim |

These are proposed behavioral requirements. The [edit-state experiment](evidence/README.md#message-edit-state) checks dependency graphs and derives current versions over a supplied authenticated snapshot. The [joined edit experiment](evidence/README.md#joined-protected-message-edits) additionally covers authenticated SMTP delivery, bounded graph processing, durable authority-aware views and readable ordinary corrections. Production and independent-client interoperability remain separate.

## Audience and partial knowledge

The audience belongs to each event, not to a permanently expanding conversation. Replacing an answer does not grant permission to send it to everyone who saw any earlier message. The sender chooses recipients again and is warned when a changed audience means earlier recipients may retain an older answer.

A receiver only knows the events delivered to it. It MUST NOT label its answer view globally complete or claim that a withdrawal reached every earlier recipient without evidence. No hidden recipient is added to public audience metadata to make this bookkeeping easier. Bcc delivery and encrypted recipient enumeration require their own privacy-preserving wire mapping.

A forwarded form can be read without granting its forwarder revision authority. A forwarded answer is not a new answer by the forwarder. A legacy textual reply remains readable and can be positioned locally beside a question, but cannot silently satisfy required fields or replace a structured answer.

## Form receiver algorithm

1. Preserve the received representation and compute parsing, authentication and capability results independently.
2. If required semantics are unsupported or validation fails, offer a safe readable representation with the actual evidence; apply no structured effects.
3. Resolve the scoped event identity. Coalesce a true duplicate; retain and quarantine conflicting authenticated records.
4. Resolve the exact form revision and operation references. Keep unresolved events pending without inventing a target or author.
5. Validate field types, complete-record constraints, authority, scope and acyclic references. Reject the entire operation if any required condition fails.
6. Add the validated event to the immutable event set and derive current form heads and answer heads from explicit references.
7. Commit event storage, duplicate bookkeeping and derived effects atomically. Notifications and any later authorized integrations use durable effect identities so a crash cannot cause a second submission.
8. Recompute affected descendants when dependencies or authentication evidence change. Preserve an explanation of why an event became pending, invalid or conflicted. Recomputing local state cannot undo messages already transmitted or external actions already performed; retain the history of those effects and their changed attribution rather than claiming rollback.

The result must be independent of the order in which the same validated event set arrived. This is a convergence requirement for receivers holding the same evidence, not a promise that every recipient has the same event set.

## Conformance cases

| Input | Required result |
| --- | --- |
| Same submission delivered twice | One answer and one application effect |
| Different authors reuse an event identifier | Separate scoped events; no cross-author suppression |
| Same authenticated author signs conflicting records under one identity | Conflict retained; no winner selected by arrival |
| Answer arrives before its form | Pending until exact form revision is available |
| Replacement arrives before predecessor | Pending; resolves after predecessor validation |
| Two devices answer independently | Both remain current and conflict is visible |
| Later replacement names both concurrent answers | One current answer after all references validate |
| Replacement names another author's answer | Invalid; original answer unaffected |
| Form revision changes a choice label | Old answer retains old revision meaning |
| Answer names obsolete form revision | Valid against that revision; shown as an older-revision answer |
| Submission has one valid and one unknown field | No partial structured application |
| Required text field contains empty string | Present under baseline; no invented non-empty rule |
| Withdrawal targets predecessor only | Later replacement remains current |
| User reads or decrypts form | No submission or external request |
| Recipient receives only an old answer | Local view makes no global completion claim |
| Authentication evidence for a parent becomes invalid | Dependent effects are recomputed and no longer attributed as authorized |

These cases specify expected outcomes. The [answer-state experiment](evidence/README.md) exercises duplicate, replacement, withdrawal and ordering semantics in 14 tests. Exact schema validation, authentication, durable effects and independent implementations remain untested; interoperability is not claimed.

## Deliberate submission and existing mail actions

Rendering, scanning, prefetching or focusing an interaction control MUST NOT create a submission. The user deliberately submits the exact form revision, values and audience; current authorization is checked before transmission. A readable legacy representation must not rely on an automatic network fetch to perform its action.

Existing one-click unsubscribe remains a separate, narrowly defined operation. Its signed headers and fixed POST value do not authorize arbitrary form fields or establish the identity of a person holding the message. Do not reuse that operation to send an Email/2 answer. The [one-click audit](audits/one-click.md) records consent, credential-isolation and redirect rules that inform a future external-action profile.

## Reaction state

The [reaction contract](reactions.md#current-reaction-view) owns additive reaction and explicit withdrawal semantics. Reactions keep their exact version targets when messages are edited. A withdrawal suppresses only fully resolved reactions belonging to its author; it does not erase records, remove later equal reactions or withdraw another operation kind. These operations do not reuse the deferred general-form withdrawal schema.


## Combined suite binding

The separately versioned [required conversation suite](suite-profile.md) defines its new assertion, context, invitation, ordering-wrapper and payload selections. It does not change any older version defined here. Its design is specified separately from implementation and acceptance evidence.
