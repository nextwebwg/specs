---
title: Reactions and withdrawals
order: 3.7
blurb: emoji · exact targets · reversible presentation
sectionNav: true
---

# Reactions and withdrawals

A reaction expresses sentiment about one contribution. It can appear beside that contribution without copying the conversation into another email. Withdrawing a reaction removes it from the current view while keeping the record of what was sent.

> [!ex] A thumbs-up stays with the words it answered
> Bob reacts 👍 to Alice's “Meet at 3.” Alice later edits the time to 4. Bob's reaction still identifies the original version; it does not become agreement to the new time. Bob can withdraw that reaction or send another one deliberately.

> [!note] Experimental selection
> This chapter proposes one emoji per reaction, explicit withdrawals and additive reaction events. These are editorial profile choices. Local experiments now include authenticated receive, durable presentation and a browser interaction over loopback mail. Independent client interoperability remains untested. The ordinary-email projection below has local packaging and selection tests; interoperability with actual clients remains untested.

## Send a reaction

The sender chooses the reaction audience under the delivery and disclosure policy, independently of the written-reply action. Earlier thread membership does not add recipients. The event carries an exact target reference and one emoji; it does not carry the target's body or history.

A reaction is not a form answer, invitation acceptance, service submission or authorization. Clients must not translate a thumbs-up into one of those actions.

Selecting an emoji visibly marks that choice and queues the authorized reaction durably, including while offline. Keep local pending state distinct from accepted counts and show sending/failure status through the [shared interaction contract](client-behavior.md#a-pressed-button-keeps-its-sending-status). A queued withdrawal also keeps its pending status; it cannot claim removal at recipients before the corresponding evidence. Restart or retry resumes the original operation rather than adding another reaction.

::: {.details summary="Reaction schema, emoji vocabulary and exact targets"}

### Reaction operation

The `reaction` operation has exactly three required members: `kind` equal to `reaction`, `target` containing one EventReference, and `emoji` containing one Unicode scalar-value sequence from the fully-qualified entries in the pinned [Unicode 17.0 emoji data](https://www.unicode.org/Public/17.0.0/emoji/emoji-test.txt). This profile deliberately selects those entries, not the whole RGI property including standalone components.

The vocabulary is fixed for this experimental revision. Preserve code points exactly; do not remove variation selectors, fold skin tones, normalize sequences or substitute platform glyphs in authenticated data. A recognized sequence that the font cannot draw receives a readable unsupported-reaction label and access to its exact value. Do not replace a compound sequence with a misleading base glyph or fetch remote artwork automatically. Localized labels need a separately pinned and reviewed naming catalog and accessibility tests. An unsupported sequence leaves structured processing inactive while retaining readable source. Legacy reaction handling remains independent. A vocabulary extension requires an explicit profile revision.

Under the [current asynchronous agreement](suite-profile.md#asynchronous-protected-agreement), the target must be in the same conversation and resolve to an independently accepted human contribution of one of these kinds:

| Eligible contribution | Exact reaction target |
| --- | --- |
| `message`, `attachment-message`, `rich-message`, `reply-message` | The logical authored version, including its rich/indexed content. A quoted passage is not a separate target. |
| `question`, `service-question`, `answer` | That exact question or answer, without submitting a choice or invoking a service. |
| `edit` | That exact correction version, without retargeting reactions to its original or later text. |
| `hosted-holder-observation` | The accepted observer-authored contribution, retaining its holder-attribution limits; reacting does not verify the holder. |

`recipient-resolution`, reactions and reaction withdrawals are not reaction targets. The target cannot be the reaction itself. A missing, unsupported, rejected or conflicted source retains its owning unresolved/invalid/conflict outcome; visible text alone cannot supply an eligible target.

Earlier principal-envelope agreements retain their original target list: message, attachment-message, question, service-question, answer and edit. They do not gain rich/indexed/holder targets merely because a current client displays those kinds. The operation's exact three-member schema and emoji vocabulary are unchanged; the selected agreement determines target-kind eligibility.

Existing event-envelope, identity, membership, exact-byte authentication and collision rules apply before effects. A MIME reaction marker or matching From field does not establish those checks. The chosen audience may differ from earlier audiences only under the existing delivery policy and deliberate disclosure of the reference. Automatic projection MUST NOT copy target text or other history to that audience.

:::

## Withdraw, or react again

A withdrawal names the author's earlier reactions. It does not delete received messages, reverse an external action or withdraw another person's reaction. An older client may still show the earlier reaction and an ordinary withdrawal message.

Two intentionally sent reactions remain distinct, even if they have the same author and emoji. Sending the same event again as a retry does not add a reaction. Changing an emoji uses a withdrawal and a new reaction; these are separate deliveries, so the change is not atomic.

::: {.details summary="Withdrawal schema and concurrent reactions"}

### Withdrawal operation

The `reaction-withdraw` operation has exactly three required members: `kind` equal to `reaction-withdraw`, `target` containing the original target EventReference, and `reactions` containing a nonempty array of distinct EventReferences. Existing event byte and depth limits apply. This operation is separate from the deferred general-form `withdraw` operation.

Each referenced event MUST be a valid reaction by the withdrawal's authenticated author, in the same conversation, with the same exact target. Duplicate references, self-reference, cross-author references and references to non-reaction events are invalid. The full withdrawal must validate before any referenced reaction is suppressed. For one complete, consistent examination of the original target and every named reaction, aggregate the relationship as invalid if any required relationship is independently invalid; otherwise conflicted if any required identity is conflicted; otherwise pending if any evidence is missing, inaccessible or not yet fully validated; otherwise target-matched. A local unsupported validator leaves validation unavailable with that reason, not proof that the source is invalid. Preserve each dependency's reason; array order cannot select a different outcome. Visible cross-author, self or cross-conversation violations are invalid without fetching their targets. No subset has a withdrawal effect.

### Current reaction view

A current reaction is a validated reaction not named by a fully validated withdrawal visible to the receiver. Repeated withdrawals have the same removal effect while preserving their distinct histories. Withdrawing an earlier reaction does not withdraw a later equal one. A new reaction has a new event identity; it does not restore an old withdrawn record.

A receiver MUST NOT choose an outcome by arrival time. Distinct additive reactions coexist; there is no implicit single reaction per author or last-writer-wins replacement. An event count includes distinct active events. A person count may group those records, but must not imply additional people or erase their contributions.

A withdrawal sent to fewer recipients does not remove other recipients' copies. The view describes locally known evidence, not a globally complete count or universal delivery of the withdrawal.

:::

## Handle delayed or conflicting evidence

If the target has not arrived, keep the reaction readable as an unresolved contribution. Do not attach it to a guessed message. A withdrawal with missing references stays pending and removes nothing until its references and authority can be checked.

::: {.details summary="Snapshot evaluation and durable effects"}

### Receiver evaluation

Resolve references from one consistent authenticated storage snapshot. Every record must already have passed its full envelope and operation schema and its own historical protection/authority checks. Missing references remain pending; authenticated identity conflicts remain conflicted; invalid authority or target relationships remain invalid. No lookup follows a sender-supplied URL or discloses unavailable history.

Apply existing exact-byte deduplication before effects. A new transport identifier or ciphertext generation does not turn the same authenticated event into a new reaction. Different authenticated bytes under one scoped event identity follow collision quarantine. An unauthenticated record cannot reserve the author's namespace or suppress a valid event.

If the client cannot finish the complete dependency examination within its work budget, return incomplete processing and install no partial reaction view. Retain already known diagnostics and the last committed view with its actual stale/incomplete status; a partial scan cannot claim that every required reference matched.

Recompute presentation when evidence changes, comparing the snapshot revision before installation. Local work-budget exhaustion yields incomplete processing with no partial current view. A graph result is not itself a durable storage commit or permission for an external effect. Notification and other effect records must retain replay protection across retries and restarts.

:::

## Every human contribution keeps its own reaction

A current client implementing Reactions provides the same reaction affordance for an accepted rich message or indexed reply as for plain writing. The target is the logical authored identity, so Carol's later delivery does not create another reaction count. The author can react to their own eligible contribution under the same authority and audience rules.

A reaction does not follow the message's written-reply action. No-replies restricts written replies, not independently authorized reactions; a service question's reaction does not call its endpoint. The sender still selects the actual reaction audience under the existing disclosure rules. Missing recipient setup may leave that contribution's delivery pending without converting it to a private written reply or silently deleting intended recipients.

For a hosted-holder observation, retain the actual observer as author and the holder as holder-attributed. An emoji supplies no additional identity evidence. A setup resolution is protocol state and gets no human reaction selector. Unknown-format history and inert archive imports do not gain live controls by being shown beside accepted messages.

## Readable ordinary-email projection

A compatible client should process the structured reaction once. An older client can receive an ordinary reaction or explanatory email. Neither path promises invisible delivery or automatic removal of an earlier badge.

::: {.details summary="Candidate RFC9078 layout and representation deduplication"}

### Reaction projection

Current secured reactions and withdrawals use the exact [mime-suite-v2 carrier](suite-profile.md#asynchronous-protected-agreement), with their readable projections and envelope6/authored0 binding. They add no reaction-disposition part or alternate compound layer. The following RFC9078 layout is a separately authorized ordinary-email projection, not another secured delivery of the authored record.

[RFC9078](https://www.rfc-editor.org/rfc/rfc9078.html#section-3) provides an Experimental UTF-8 text/plain reaction line linked through In-Reply-To. It does not supply this chapter's authenticated event or withdrawal contract. The [reaction audit](audits/reactions.md) records the inherited requirements and placement ambiguity.

For a target with a known local transport mapping to exactly one valid Message-ID, the candidate layout is outer multipart/mixed with exactly two children: first a text/plain; charset=utf-8 part with reaction disposition and base64 encoding of the exact emoji plus CRLF; second the [ordinary authored-carriage alternatives](event-encoding.md#ordinary-authored-carriage): plain text, inert HTML and the complete original authored0 record. Use one In-Reply-To target from that mapping. Never invent a transport Message-ID from an EventReference or guess by subject. The mapping must identify the target representation available to the intended recipient. A Message-ID from a different recipient’s copy is not interchangeable. Retain the association’s source, such as the local delivery record or a trusted mailbox import; a supplied identifier or matching MIME header alone does not prove the association. If the evidence conflicts, omit the reaction-disposition part and use the explanatory alternative, subject to the existing disclosure policy.

The explanatory alternatives include the emoji and exact event reference, not quoted target content. If a usable transport mapping is absent, use that ordinary authored-carriage layout without the reaction-disposition part. An upgraded receiver still has the exact structured target. This layout does not widen a protected agreement's permitted MIME tree. An ordinary projected emoji remains an ordinary disclosure; an outer plaintext reaction part is not an encrypted fallback.

### Withdrawal projection

A withdrawal uses the same ordinary authored-carriage alternatives and no reaction-disposition part. The readable version names the withdrawn event references. Do not express removal as an empty reaction line or a negative emoji. A legacy client can retain its earlier badge and show the withdrawal as an ordinary message.

### One event, two presentations

The candidate generated-layout selector pairs one structured event with its first reaction part within the same compound/protection scope. Its decoded bytes must equal UTF-8 of the structured emoji followed by CRLF. A mismatch produces a projection diagnostic; the first part cannot override the independently authenticated structured event. That event may still be processed with the discrepancy visible.

Once the structured event is processed, its paired reaction part is presentation, not another event. Pending, unsupported, malformed or failed structured processing MUST NOT silently promote the neighboring part into a trusted Email/2 reaction. Legacy-only display retains its actual provenance.

Legacy reactions lacking structured evidence remain separate observations. Emoji equality, From, subject and target alone cannot prove equivalence after a gateway removes structured content. Perfect deduplication after such transformation is not claimed. Ambiguous multiple parts, wrong ordering or scope failures leave this generated-layout selector inactive with the source inspectable. Nested forwarded messages do not act as the enclosing author.

:::

## Every current target kind needs acceptance

Exercise reactions and withdrawals on each of the nine current eligible kinds, including rich content, interleaved indexed replies, exact edit versions and holder observations. Include self-reaction, same logical content through independently ready deliveries, a reaction arriving before its target, later conflict, unsupported/invalid indexed content and withdrawal arriving first. Verify one logical effect per reaction identity, no service submission, no holder-verification upgrade and no reaction on recipient-resolution or another reaction. Include permutations of mixed invalid/conflicted/missing withdrawal dependencies, unavailable local validation, and interruption before the complete snapshot is examined; no prefix may suppress reactions. Earlier agreements must reject the newly eligible kinds under their original rules. Inspect actual current protected MIME for the absence of an extra reaction part; an ordinary RFC9078 packaging pass cannot prove that carrier.

## Implementation evidence and remaining work

The retained experiments below use their earlier profile bindings and six-kind target list. They do not establish the current nine-kind target contract or complete mime-suite-v2 support.

The local `reaction-operations.mjs` and `reaction-state.mjs` experiments check the selected schemas and derive a deterministic snapshot view. Their resolver supplies independently authenticated, authorized, full-schema-validated records; the evaluator does not establish that trust itself. The contribution envelope recognizes both operation kinds, and the readable projector resolves their dependencies without copying target content. The [joined reaction experiment](evidence/README.md#protected-reaction-client-flow) installs accepted reactions and withdrawals durably, using original-instance authority checks and fully authorized targets. Pending answers cannot supply reaction authority. The candidate MIME layout has a local generator and selector, described below.

Twelve focused tests cover pinned-data integrity, emoji forms, exact schemas, duplicate deliveries, intentional equal reactions, reordered withdrawal evidence, missing dependencies, authority failures, target conflicts local work limits, envelope dispatch and readable-projection boundaries. These tests do not establish complete security or interoperability.

The bundled Unicode source, license, hashes and derived vocabulary are under `evidence/unicode-17/`. The test reconstructs the selected vocabulary from the source and checks both source and license hashes. The [Unicode vocabulary audit](audits/emoji-vocabulary.md) covers the selected source and UTS51 revision29. It does not establish complete Unicode display/editing conformance; localized labels, fonts and assistive-technology behavior remain separate work. `reaction_mime.py` generates and selects the candidate compound layout. Six actual-MIME tests use the readable projector and cover exact event bytes, folded transfer encoding, absent mapping, withdrawal fallback, mismatched emoji, malformed/ambiguous structures and forwarded-message isolation. A pairing mismatch retains the untrusted structured bytes for independent verification; it grants no reaction authority. The adapter supports only a narrow ASCII Message-ID spelling and relies on the caller for target mapping and semantic equivalence of supplied readable alternatives.

Real legacy display, complete current secured MIME carriage and transport-ID handling still need integration evidence. The earlier joined path carries exact contribution bytes inside MLS; it does not select an encrypted compound reaction body. Current mime-suite-v2 likewise admits no extra RFC9078 part. Delayed old-epoch delivery also remains bounded by the local secret-retention and historical-context work described in [group conversations](group-conversations.md).
