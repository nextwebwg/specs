---
title: Reply content and quotation boundaries
order: 1.2
blurb: new content · quoted passages · Microdata · chunk index
sectionNav: true
---

# Reply content and quotation boundaries

A reply identifies what its author added and what it repeats from earlier messages. Those boundaries are message data, not a convention inferred from indentation, colors or a CSS class.

The structured message contains a **chunk index**. Each entry points to one HTML element, whose Microdata describes the same chunk. A quotation also points back to the exact earlier contribution and passage it represents. The receiver checks the index and markup together before using them to reconstruct the conversation.

> [!ex] Two answers inside one reply
> Alice asks about the meeting day and venue. Bob quotes the first question, writes “Thursday works,” quotes the second, and writes “The library.” His reply contains four ordered chunks: quotation, authored content, quotation, authored content. A client can keep each answer beside its question without classifying Bob's words as Alice's, or retransmitting Alice's entire conversation history.

> [!note] Proposed content profile
> This chapter defines the candidate `reply-parts-v0` content contract and its extraction procedure. Existing operation schemas and negotiated profiles do not acquire this support automatically. The new protected transport/application agreement and renderer integration must be implemented and tested before a client advertises support. The examples specify proposed behavior; they are not evidence of deployed interoperability.

## What a sender includes

A normal reply can contain just its new content and an exact reply reference. Quoted history is not required. When the author includes context, the composer identifies the selected passages separately from new writing and retains their authored order, including interleaved answers.

| Piece | Purpose |
| --- | --- |
| Contribution identity | Identifies this immutable message and its author under the existing event contract |
| Reply reference | Identifies the contribution being answered; it does not copy that contribution |
| Chunk index | Lists this reply's chunks, their order, roles and HTML locations |
| Annotated HTML | Carries readable content with matching Microdata boundaries |
| Quotation source | Identifies an earlier event, its authored chunk or text body, and the selected text range |
| Plain-text alternative | Preserves the new writing and visibly distinguishes included quotations |

The index and annotated HTML belong to the same event and, when protected, the same authentication boundary. For protected delivery, both and the readable alternatives belong inside encryption. Ordinary delivery keeps its actual unprotected status. Recognizing Microdata never authenticates a sender.

The sender does not attach an invisible transcript to make the reply self-contained. Only deliberately included context is copied. Copying source passages and their identifiers follows the existing [history and forwarding rules](messages.md#conversation-history-and-forwarding) and [disclosure policy](delivery-policy.md). A reference cannot authorize fetching or sharing its source.

## Stable chunks, explicit roles

Chunk semantics are declared by fields, not encoded in identifier names. The same vocabulary applies to any sender, topic or writing style: `role` describes whether content is newly authored or quoted, `source` identifies quoted material, and `replyTo` identifies the contribution being answered. A question and its answer do not need specially named chunk types or IDs.

Every chunk has a fresh local identifier in its contribution. Retries retain that identifier and the original event bytes. The identifier is not a global author identity, a timestamp or a hash of the words. Identical words in different authored chunks remain distinct contributions.

The sending app generates each new chunk ID using the existing ObjectId generation rules. When quoting received content, it copies that content's actual event and part reference into `source`; it does not generate a descriptive name for the source. The receiving app resolves those exact references and reads the declared roles. It must not derive roles, authorship or relationships from an identifier's spelling.

Three roles are defined:

- **authored**: content supplied as this contribution's new writing. This label is not a claim of originality, truth or absence of plagiarism.
- **quotation**: a text quotation with an exact structured source reference. The source claim remains unverified until checked against the receiver's independently validated source.
- **unattributed-quotation**: quoted context without a resolvable structured source, such as a passage copied from old email. It remains visible without a verified source attribution.

Imported history alone cannot authenticate a structured quotation source. Follow the [restored-history composition procedure](encrypted-archives.md#replying-after-restoration): use unattributed quotation only within an otherwise valid indexed reply, or compose a rich message with explicitly quoted historical context when no eligible primary target is available. Neither route revives old controls or claims a matched source.

A quotation gets its own chunk ID in the new reply. Its source points to the earlier chunk; reusing the earlier ID as though it were newly authored would conflate those roles. Changing sent content creates a new event. An edit does not silently retarget quotations of the older event.

## Example: the index points into the HTML

This index contains new writing followed by a quotation. The opaque identifiers carry no question, answer or person semantics. The sender generates the two local chunk IDs; the source identity and event ID come from the received message. Here `body` is the defined selector for that earlier message's text, and `0`–`20` selects the quoted passage. The example omits the surrounding operation; its exact schema is in the expandable contract.

```json
{
  "parts": [
    {"id": "ad709f3bed4a06e505cde54b1d203d4c", "element": "en-part-ad709f3bed4a06e505cde54b1d203d4c", "role": "authored", "text": "Thursday works."},
    {
      "id": "b891d5c6b8d2933d1e08cff84675f651",
      "element": "en-part-b891d5c6b8d2933d1e08cff84675f651",
      "role": "quotation",
      "text": "Would Thursday work?",
      "source": {
        "reference": {"principal": "enp0:a4b039fa0beef31b61cf85f9d68f0c3b47f3b954fd2e9805cc628ca28744e20b", "conversation": "16c447bc7aec0726154c1c94b2be88cb", "event": "886f6ef3b708a3d00d1446d67ab44c81"},
        "part": "body", "start": "0", "end": "20"
      }
    }
  ]
}
```

The first entry means “newly authored content” because its `role` is `authored`. The second means “quotation of this exact source passage” because its `role` is `quotation` and it has a `source`. Each `element` locates the corresponding HTML wrapper by its literal ID. Those meanings stay the same for any content or participants. Formatting can change within a supported presentation without changing which chunk an ID identifies; it does not permit changing an already authenticated event on retry.

::: {.details summary="Exact operation and index schema"}

### Candidate operation

The `reply-message` operation has exactly these ten required members. Null values, duplicate decoded JSON names and additional members are invalid.

| Member | Value |
| --- | --- |
| `kind` | Exactly `"reply-message"` |
| `version` | Exactly `"0"` |
| `replyTo` | Array containing exactly one EventReference, following the ordinary same-conversation reply rules, including accepted service-question and hosted-holder-observation targets under their owning bindings |
| `parts` | Nonempty ordered array of chunk records, with at least one authored chunk |
| `text` | The plain-text projection defined below |
| `html` | The complete annotated UTF-8 HTML document represented as a Unicode scalar-value string |
| `presentation` | Exactly `"html-css-reply-v0"` |
| `manifest` | Resource manifest under the rich-message contract |
| `embedded` | Embedded-image role records under the rich-message contract |
| `attachments` | Independent attachment descriptions under the rich-message contract |

The existing [rich-message resource rules](rich-messages.md) govern complete inventory, size/digest checks, scoped Content-IDs and deliberate downloads. An authored chunk can contain supported rich content. Quotation chunks may contain supported rich presentation with resources declared in this contribution. Copying content or resources still requires disclosure authorization. This version verifies the source's text representation; it does not certify that a rich quotation preserves the source's formatting or images, and rich quotations are not eligible for automatic collapsing.

The existing strict JSON, Unicode and common event resource bounds apply to the complete operation, including its HTML and index. Embedded copies do not obtain a second event-size allowance. Empty authored text is structurally permitted, as in an ordinary message; it does not invent visible words or waive meaningful rich-content and accessible-alternative requirements.

### Chunk records

An authored or unattributed-quotation record has exactly `id`, `element`, `role` and `text`. A quotation record has those four members plus required `source`.

- `id` uses the existing nonzero 32-lowercase-hex ObjectId grammar. It is unique within `parts`.
- `element` is exactly `en-part-` followed by `id`. It is a literal HTML ID, without `#`, a URL or a CSS selector.
- `role` is exactly one of the three roles above.
- `text` is a Unicode scalar-value string containing this chunk's readable text representation, without automatically added attribution labels or quotation prefixes.

Chunk identity is scoped to the authenticated contribution identity and its chunk ID. Neither an HTML ID nor a chunk ID alone can reserve another author's namespace. The order of `parts` is the authored order; HTML wrappers must occur in that same order.

### Source selector

`source` has exactly `reference`, `part`, `start` and `end`. `reference` is the existing exact EventReference with `principal`, `conversation` and `event`. It identifies the source event independently of the current reply target.

`part` is either an authored chunk's ObjectId in a source `reply-message`, or the reserved string `body` for the `text` member of a source `message`, `rich-message` or `question`; the [Service actions binding](service-answers.md#current-protected-service-agreement) also permits accepted service-question wording only. `body` cannot select an entire reply transcript. For a question, `body` selects only its wording, not option labels or active controls. This version does not select attachment metadata, arbitrary MIME parts or HTML fragments through `body`; those need an explicitly defined projection before they can become structured quotation sources. Quoting such material without that binding uses unattributed-quotation.

`start` and `end` are canonical unsigned decimal strings: `0`, or a nonzero ASCII digit followed by ASCII digits. They count Unicode scalar values in the selected source text, with an inclusive start and exclusive end. Require `0 <= start <= end <= source length`; do not clamp. No whitespace folding, Unicode normalization, line-ending rewriting or UTF-16 indexing occurs. The quoted `text` must equal that exact slice. The existing source and event size bounds limit usable positions; a large decimal must be rejected by length/value comparison before conversion to an unsafe machine integer.

Noncanonical field spellings or malformed source-object shape violate the operation/index schema. Once those fields are well formed and agree with the HTML metadata, range validity and source authorship are **source-claim** checks: a reversed/out-of-range interval, forbidden self-source, non-authored source chunk or different selected text yields `source-mismatch` when decidable, without deleting new writing or relabeling the quotation as authored. Missing or conflicted evidence retains its specified source status. These failures do not license clamping, a replacement selector or a partial index map.

An authenticated event-namespace conflict prevents a `matched-text` result even if two retained variants happen to contain the same selected words. Do not choose a convenient variant to verify or collapse the quotation. Resolve current conflict/access evidence before matching; incomplete processing remains unavailable, not a successful match.

A source chunk must be authored. It cannot be another quotation, and the source event cannot be the current event. This avoids recursively laundering a copied passage into new authorship. A composer quoting already quoted text must preserve a valid reference to the original authored source or use unattributed-quotation. Source event collisions, missing chunks and invalid ranges never select a nearby passage or newer revision.

:::

## Microdata vocabulary

The candidate uses HTML's `itemscope`, `itemtype` and `itemprop` attributes. Its exact vocabulary is local to this draft, not a claim of HTML-standard or registry adoption. The type identifiers below are identifiers only: parsing them never fetches a schema, source message or web page.

::: {.details summary="Reply and chunk items, permitted attributes and locations"}

### Reply item {#ReplyV0}

The sole content root is a body-level `div` with `id="en-reply"`, `itemscope` and exactly this item type:

```text
https://nextwebwg-site.vercel.app/email-next/reply-content#ReplyV0
```

Its only Microdata property is repeated `part`: one direct child item for each index entry, in order. Each part uses the chunk type below. An authored part's wrapper is `div`; either quotation role uses `blockquote`. All displayed body content must be inside these wrappers' content regions. Whitespace between wrappers is permitted; unindexed text or an extra content item is a mismatch, not content to discard.

### Chunk item {#PartV0}

Each wrapper has its indexed `id`, `itemprop="part"`, `itemscope`, and exactly this item type:

```text
https://nextwebwg-site.vercel.app/email-next/reply-content#PartV0
```

It contains one `meta` for each scalar property and one final `div itemprop="markup"` containing the displayed content. Metadata order is immaterial. Repeated, missing, multi-token or unknown properties are invalid for this vocabulary.

| Microdata property | HTML representation and index value |
| --- | --- |
| `partId` | `meta content` equals `id` |
| `role` | `meta content` equals `role` |
| `text` | `meta content` equals `text`, after HTML character-reference decoding |
| `markup` | The single content-region `div`; its subtree supplies presentation, not a replacement for the indexed text |
| `sourcePrincipal` | Quotation only: `meta content` equals `source.reference.principal` |
| `sourceConversation` | Quotation only: equals `source.reference.conversation` |
| `sourceEvent` | Quotation only: equals `source.reference.event` |
| `sourcePart` | Quotation only: equals `source.part` |
| `sourceStart` | Quotation only: equals `source.start` |
| `sourceEnd` | Quotation only: equals `source.end` |

The scalar-property elements have exactly `itemprop` and `content`. Source properties are forbidden on the other two roles. The metadata is not displayed attribution supplied by the original source author; the current reply author supplies it.

Authored content follows the baseline HTML/CSS vocabulary within its content region, including the rich resource rules. Its indexed text must preserve the HTML's readable meaning and meaningful image alternatives; as in the existing rich-message contract, this authoring obligation is not proven by a simple text comparison. General Microdata extraction returns string values, not authenticated rich content. It cannot replace the indexed text, profile parser or filtered content tree.

A text-only quotation region contains only text nodes and `br` elements. Each `br` represents one LF; concatenate those LFs and decoded text nodes to obtain exactly the indexed text. Generators escape CR as a character reference and use `br` for LF so HTML source newline processing cannot change the intended string. Rich quotation regions follow the same presentation, meaningful-text and resource obligations as authored content, but remain visible: matching their indexed text does not verify formatting, images or other presentation. Present a correction to quoted words as new authored content or an explicitly unmatched quotation rather than silently marking it matched.

Every scalar metadata value must round-trip through HTML parsing exactly. A value that cannot be represented without parser substitution, including U+0000, cannot be authored in this profile; do not silently rewrite it to force agreement. Another supported representation remains available under its own contract.

`html-css-reply-v0` extends the [presentation profile](presentation-profile.md) only with these wrapper IDs, Microdata attributes and scoped metadata elements. It does not permit arbitrary IDs, Microdata or body metadata inside content regions. `itemid` and `itemref` are forbidden throughout this document; content cannot reach outside its own message or redirect property ownership. No other nested item scopes or type values are accepted. Duplicate source attributes, any duplicate document ID, nested part wrappers, parser-reparented wrappers or unknown properties disable structured extraction. Attribute token order is not meaningful, but property names and vocabulary identifiers compare exactly.

The metadata wrappers admit only the attributes specified above; sender formatting belongs inside the content region. Document language/direction and content styling retain the baseline rules. The receiver must extract and validate boundaries from the inert parsed authenticated HTML before generic filtering would remove IDs or metadata. It then carries an internal source map into the fresh filtered rendering tree. Sender IDs and Microdata must not become application DOM IDs, client controls or selectors across message boundaries. Baseline `html-css-v0` remains unchanged and strips these attributes; it does not imply this capability.

:::

::: {.details summary="Complete indexed chunk and its matching Microdata"}

This is one authored chunk from a larger operation. The identifiers satisfy the wire grammar. Its surrounding operation still requires the fields above.

```json
{
  "id": "ad709f3bed4a06e505cde54b1d203d4c",
  "element": "en-part-ad709f3bed4a06e505cde54b1d203d4c",
  "role": "authored",
  "text": "Thursday works."
}
```

Its corresponding HTML wrapper is:

```html
<div id="en-part-ad709f3bed4a06e505cde54b1d203d4c"
     itemprop="part" itemscope
     itemtype="https://nextwebwg-site.vercel.app/email-next/reply-content#PartV0">
  <meta itemprop="partId" content="ad709f3bed4a06e505cde54b1d203d4c">
  <meta itemprop="role" content="authored">
  <meta itemprop="text" content="Thursday works.">
  <div itemprop="markup"><p>Thursday works.</p></div>
</div>
```

For a quotation, the wrapper is `blockquote`, the role is `quotation`, and the six source metadata elements repeat the exact source selector. A text-only quotation region contains the quoted text and line breaks; a rich quotation may preserve supported presentation but remains visible until the reader chooses otherwise. `meta` has no visible text; the quotation remains readable when a legacy client ignores Microdata. A receiver must still check the actual legacy rendering behavior in its client tests.

:::

## Receiver procedure

> [!ex] Keep the writing; withhold the unproven relationship
> Alice sends a notice with no replies. Bob nevertheless sends a valid message pointing at it. His writing remains available, but the client does not install an authorized discussion edge. Likewise, a quotation whose original is missing stays visible as an unverified source claim; a broken image does not change who authored the surrounding text.

The output is a **reply-content map**, retaining the contribution identity, each chunk's role, its index entry, its source DOM region and its quotation-resolution result. It is a derived view; it never replaces original MIME, authenticated event bytes or HTML.

1. Select and decode the carrier under its negotiated profile; validate authentication, identity, audience, event encoding and deduplication before assigning verified meaning. An unsigned event can carry claimed boundaries, but not authenticated authorship or verified quotation provenance.
2. Validate the exact operation/index schemas. Parse `html` inertly with the baseline's selected HTML parser and source diagnostics. Enforce existing input/processing budgets before building unbounded trees. Do not search an outer email, forwarded message, sibling MIME part or application document for a matching ID.
3. Require the sole root and its complete part list. The [ordered acceptance boundaries](rich-messages.md#accept-the-event-check-its-presentation-separately) distinguish an invalid/incomplete index from an accepted map with unavailable source or later display failure. Locate every indexed element by literal ID in this parsed message only. Require exactly one match and exact agreement on role, text, source fields and index/DOM order. Reject partial maps: unindexed content and malformed metadata remain visible in fallback.
4. After the complete map is established, build a fresh allowed content tree for each chunk and retain its source mapping. If this later filtering/layout stage fails, preserve the accepted roles, text and source claims in the simpler diagnostic view; do not erase the map or stop its independent relationship checks merely because rich display is unavailable. Failure of the required inert source parsing in steps2–3 remains an incomplete/invalid map instead. Apply the rich-message resource inventory independently; an ID or Microdata property never authorizes a resource fetch, action, navigation or wider audience.
5. Resolve the primary reply through the existing exact reference rules. Missing/conflicted parents remain explicitly unresolved; do not guess another parent or merge by subject. Keep this message's content visible independently of the target.
6. Resolve each quotation only against independently validated source events the receiver is authorized to access. Compare the exact principal/event/conversation, source kind, authored part and scalar-value range, then compare the quoted text. A signature on the current reply authenticates its author's quotation claim, not the earlier author's words.
7. Assign quotation status: `matched-text` for an independently authenticated exact match; `source-unavailable` when the source is absent or inaccessible; `source-conflict` for a conflicted source identity or event namespace; `source-mismatch` for a resolved invalid selector or different text; `claimed-only` when protection is insufficient; and `unattributed` for the explicit unattributed role. Failure of a source claim never deletes surrounding authored content or silently converts the quotation to newly authored text.
8. Show all authored chunks in their specified order, retaining the included quotation context or an immediate expansion affordance. Only a `matched-text` quotation with the lossless text-only content structure defined above may be collapsed automatically, and only when its source passage is already visible or immediately accessible in the view. Mismatches and uncertain quotations remain visible with client-owned explanation. Matching text does not certify original HTML formatting or the truth of the passage.
9. Recompute affected relationships when source messages arrive or evidence becomes conflicted, preserving expansion choices and reader position where possible. Reconstruction must not fetch remote content, send receipts, submit answers, mutate source messages or create new authorizations.

### Assemble the conversation from contributions

A reply points to one exact earlier contribution. The client builds those links from accepted messages already available to it, including attachment messages. Quotations and interactions have their own relationships; they do not invent extra reply parents or merge audiences.

Missing parents stay unresolved. Invalid links do not hide the message itself. With the same accepted evidence, clients derive the same reply relationships even when mail arrives in a different order.

:::: {.details summary="Primary-reply graph, unresolved states and cycle handling"}

**Inputs.** Use a complete authorized projection of one validated conversation at an accepted local source snapshot. First apply the [global principal/event namespace rules](event-identifiers.md#detect-reuse-across-conversations), preserving accepted duplicate provenance and current conflict flags. A matching conversation identifier alone grants neither context nor access. Inert historical imports, provisional carriers and rejected operation/index bindings are not accepted graph inputs.

The four primary-reply operations are `message`, `attachment-message`, `rich-message` and `reply-message`. The first three permit zero or one `replyTo` reference; `reply-message` version0 requires exactly one under its operation schema. The graph procedure does not relax those admission rules or make an invalid indexed reply into a root. An eligible target is an independently accepted contribution of one of those kinds, a `question`, a `service-question`, or a `hosted-holder-observation`, subject to its owning application, audience and target rules. A hosted observation does not verify its holder. An ordinary reply to a service question does not submit to its endpoint.

1. Index the authorized accepted contributions by full EventReference: principal, conversation and event. Do not use Message-ID, subject, visible words, chunk ID or mail arrival order as the key. Deduplicate original event copies before topology; differing authenticated variants retain their namespace-conflict outcome.
2. For each primary-reply contribution, retain its requested parent separately from any accepted graph edge. An explicit empty `replyTo` admitted by the operation schema has `no-target` status: it is an actual root. Contributions without a primary-reply field have `not-applicable` status and retain their owning interaction relationships; do not invent a parent or a normal-message root for them.
3. If the source event's namespace is conflicted, do not create an outgoing edge. For a nonempty reference, reject a cross-conversation or self reference. Apply the current target namespace-conflict result without exposing foreign-conversation content. An absent or inaccessible target remains pending. A resolved but ineligible kind or invalid target has an invalid relationship, not a guessed alternative. The original requested reference remains available for local explanation.
4. Apply the agreement-specific discussion predicate below before forming an edge. A private/no-replies source or a known unsupported source agreement gives an invalid relationship, not a guessed root. Missing or incomplete source evidence remains pending; conflict retains its conflict outcome. For every otherwise exact, authorized, nonconflicted target, form one candidate edge. Construct the complete **permission-checked** candidate graph before checking cycles. A target's own missing or invalid parent does not invalidate a direct permitted edge to its still-accepted content.
5. Find every directed cycle. Remove exactly the outgoing edges of nodes belonging to a cycle, and mark those relationships invalid. A self reference was already rejected. Keep an edge from a separate reply into a cycle member when that direct target is otherwise eligible; that reply is not itself a cycle member. Preserve all content and the invalid/unresolved markers rather than relabeling removed edges as intentional new roots.
6. Install or refresh the derived graph only while its accepted source snapshot and namespace/conflict dependencies remain current. Recompute affected edges and complete cycle membership when parents, valid variants, conflict evidence or access decisions change. An older in-flight projection cannot overwrite newly learned conflict. If processing is incomplete under a local resource budget, report incomplete reconstruction rather than installing a purportedly complete partial graph.

Apply the selected agreement's discussion predicate to independently accepted source evidence:

| Agreement | Required discussion relationship |
| --- | --- |
| Current authored0 / slot intent1 | Source permits discussion; same exact scope root; the reply's complete intended-slot set equals the source's discussion slots; the author is independently bound to an included author slot. Each actual native audience and slot map passes its separate [delivery checks](event-encoding.md#asynchronous-authored-records-and-deliveries). A smaller ready delivery does not change this intended set. |
| Earlier principal intent0 | Source permits discussion; replier belongs to its declared principal participants; the reply's authenticated principal audience equals that discussion set. |
| An earlier agreement without this reply-intent contract | Retain that agreement's own graph rules. Do not infer an intent record or use them to bypass the current predicate. |

The resulting relationship states are `no-target`, `not-applicable`, `pending`, `conflict`, `invalid` and `target-matched`. They are local derived states, not new wire fields or automatic response messages. Only `target-matched` supplies an established reply edge. Quotation sources and question/reaction/edit targets remain separate; their own authority and effect checks still apply.

An implementation may find cycles with an iterative path walk or an equivalent algorithm. In a path walk, retain visited nodes and their positions, stop at a known completed path or a node without an edge, and mark only the repeated suffix when a node repeats in the current path. Do not use a recursion depth or arrival-order cutoff that silently accepts one member of a cycle. Finish the same complete candidate set, or report incomplete processing.

A display may use a timeline, branches or a focused thread. It may order unrelated contributions by local preferences or observed timestamps, but that order is not authenticated causality. Preserve multiple true roots, unresolved parents, all authored chunks and distinct audience/protection provenance. Derived placement cannot authorize fetching, sharing, answers, service effects or history transfer.

The [topology component](evidence/README.md#primary-reply-topology) checks normalized relationships and can consume a separately validated edge-permission result before cycle detection. Omitting that input exercises topology only, not current reply-policy enforcement. It does not authenticate events, validate indexed HTML, implement the serialized source-snapshot boundary or prove a complete current-suite client.

::::

## A reply while someone is still joining

Alice invites Bob and Carol to one discussion. Bob is ready first; Carol's setup is pending. Bob's reply still names all three intended slots and Alice's logical question. Its first encrypted delivery can contain only the independently eligible Alice and Bob mappings.

| Reply claim | Relationship outcome |
| --- | --- |
| Same scope, intended Alice/Bob/Carol, Bob bound to his author slot; actual eligible delivery Alice/Bob | The pending Carol delivery does not prevent a valid discussion edge. |
| Same source, but intended Alice/Bob only | Invalid discussion relationship: dropping Carol changes the declared destination. |
| Same source, with an added Dana slot or a different scope | Invalid discussion relationship; it requires a separately authorized composition. |
| Correct intended slots, but Bob's author binding or source evidence is not yet accepted | Pending validation; no guessed edge or interaction effect. |

Carol can later receive the same original authored reply through a new eligible delivery. The graph uses its logical identity once. This does not promise that Carol has received it already, authorize Bob to publish Alice's message, or bypass the current release checks.

## Plain text, old clients and forwarding

Generate the plain-text alternative by visiting `parts` in order. Emit authored `text` unchanged. For either quotation role, prefix every line with `> `, including an empty line; split lines on LF only, preserving CR as content. Join the projected chunks with exactly two LFs, without trimming. The operation's `text` must equal this projection; existing MIME text serialization handles wire line endings separately. Whole-message originals remain available independently of this readable projection.

Current indexed replies use [authored0/envelope6/context10 with `mime-suite-v2`](suite-profile.md#asynchronous-protected-agreement): the version0 reply operation belongs to the immutable authored record, and the delivery envelope carries its exact original bytes. The annotated HTML and resources project that authored operation. Earlier [envelope4/context8 with `mime-suite-v0`](suite-profile.md#one-mime-carrier-explicit-operation-dispatch) and [envelope5/context9 with `mime-suite-v1`](reply-intent.md#reply-aware-protected-agreement) retain their own direct-operation carriers. Generated text/HTML alternatives follow their owning MIME serialization and resource rules. There is no separately selected indexed-reply-only carrier, and `mime-rich-v0` is not widened to accept this operation.

An older client can display the text or HTML, but may remove annotations, copy a whole transcript or change markup when replying or forwarding. The next receiver treats that new mail as legacy input unless a valid supported structured carrier establishes otherwise. Preserved-looking markers alone do not establish a contract, and stripping metadata cannot authorize hiding text. The [legacy reconstruction procedure](rendering.md#reconstruction-procedure) remains the reversible heuristic fallback.

Forwarding selected content creates a new contribution under its own author and audience. Raw forwarding can disclose the complete original, including quoted-source identifiers; Microdata is not a non-forwarding field. An automatic quotation projection follows the selected agreement's [source-audience comparison](event-encoding.md#asynchronous-authored-records-and-deliveries): within one current scope, compare complete intended slot sets; across scopes, require the independently accepted bindings and disclosure permission. Earlier agreements compare their authenticated principal audiences. A smaller ready delivery does not enlarge the permitted intended audience. Broader sharing requires separately authorized disclosure covering the content and metadata. A missing source must not trigger automatic history retrieval or copying.

## Reply in a conversation with an older agreement

Seeing identifiable chunks in an email does not mean the conversation can carry indexed replies. Keep the writing and selected context while checking the actual agreement. If it lacks the operation, the client can wait or deliberately establish a supported new context; it cannot switch parsers or change the old agreement behind the scenes.

::: {.details summary="Hold, recompose or establish a new context"}

1. Read the exact application and carrier from accepted cryptographic context and retained device agreements, not HTML attributes, a local feature flag or another stream's support. Require the operation, indexed presentation, envelope, carrier and every intended device's complete signed support under one selected agreement.
2. If the existing context lacks that agreement, hold indexed preparation before creating an application delivery. Preserve the draft, source selection and required protection/reply policy. Do not insert the new operation into an old allowlist, relabel its carrier, strip its index while retaining its event identity or consume a package merely to discover that support is absent.
3. A deliberate new ordinary stream or managed conversation follows the selected admission/migration rules. It has fresh required identities, independent current authority and its exact selected application. Retaining an ordinary conversation grouping requires its separate authorization; it grants no old history or membership. Older context6/7 migration follows the suite's separately admitted new-conversation rule.
4. Recheck primary-parent eligibility and quotation evidence independently. In the reply-aware agreement, an older source with no reply-intent contract cannot supply an authorized discussion edge merely because its text is readable. Version0 indexed replies require one eligible primary target; a missing or unsupported target cannot be replaced with an empty parent. Hold the indexed reply or deliberately compose an authorized `rich-message` root with inert readable quotation under its own rules. Preserve the actual author and disclosure scope.
5. Freeze a new authorized contribution/copy plan only when its complete dependencies hold. A callback for the old agreement cannot activate it. Existing prepared, submitted or uncertain deliveries keep their original bytes and outcomes; migration cannot retransmit them as new events or prove they failed.

A client may deliberately recompose readable content under an independently supported older agreement only when that choice satisfies the actual audience, disclosure, protection and reply-policy requirements. Such content is a new contribution under that agreement, not a valid indexed reply or permission to discard required semantics. Simpler reading views and text compatibility alternatives never negotiate missing support.

:::

## Integration and acceptance

The version0 operation and `html-css-reply-v0` presentation require an exact selected protected agreement and its complete carrier. Existing immutable versioned tuples, operation allowlists and capability signatures must not be widened in place. Both agreements named above bind the operation to their own event, identity, admission and release rules. Merely recognizing Microdata, receiving a familiar media type or adding a dispatcher branch is insufficient. A declared binding does not establish that its joined implementation is complete.

Acceptance cases must cover: authored-only replies; alternating quotations and answers; exact source ranges including supplementary Unicode, CR and LF; duplicate IDs/attributes/properties; missing and extra chunks; contradictory role, text, source and order; malformed HTML that relocates wrappers; stripped metadata; changed quotations; unavailable/conflicted sources and later arrival; self/cyclic reply links; duplicate deliveries and event collisions; resource isolation; unauthorized broader quoting; plain-text projection; and preservation of all new writing in every failure state. Native keyboard/accessibility and actual legacy-client display remain separate observations, not inferred from HTML inspection. Current-agreement acceptance additionally distinguishes complete intended slots from actual delivery membership: a valid partial ready delivery retains its edge, while omitted/added discussion slots, a different scope and a missing author binding do not produce a falsely authorized edge. Preserve distinct addressed alias slots and deduplicate identical authored bytes across later deliveries.

The [selected Microdata source review](audits/reply-microdata.md) records the inherited attribute/value rules and the narrower vocabulary boundaries. No production parser, renderer, provider carriage or independent interoperability claim follows from publishing this contract.
