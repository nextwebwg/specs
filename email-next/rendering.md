---
title: Rendering and existing email
order: 13
blurb: HTML · CSS · conversation reconstruction
sectionNav: true
navGroup: guide
---

# Rendering and existing email

A conversation view should show what each person added, keep answers near their questions, and make the complete original message available. It should improve old mail as well as render new structured messages.

> [!ex] Keep the answers, collapse the repetition
> Alice asks three questions. Bob replies between the quoted questions. The client shows each answer with enough of its question to make sense, then collapses copies of material already visible in the thread. Expanding a quotation restores it; **View original** shows the complete received message.

This chapter defines two separate behaviors: rendering new messages under a shared HTML/CSS profile, and reconstructing older conversations without changing their source.

## A defined presentation profile

The [presentation profile](presentation-profile.md) defines a finite HTML vocabulary, attributes, CSS properties and values, plus parsing and failure behavior. Its remaining conformance work is explicit. The table below summarizes its scope.

| Area | Defined proposal | Remaining validation |
| --- | --- | --- |
| Text | Finite semantic element and attribute allowlist | Parser recovery, long text and accessibility fixtures |
| Tables | Permitted table structure and bounded spans | Overflow, layout and assistive-technology behavior |
| Images | Bundled PNG/JPEG resources and cid resolution | Decoder limits, malformed images and resource-isolation tests |
| Styling | Inline property/value allowlist; no selectors or resource functions | Complete parsing fixtures, defaults and accessibility overrides |
| Answer buttons | Client-owned controls derived from authenticated question choices; general forms are deferred | Keyboard behavior, accessible labels and confirmed reply or service-submission state |
| External resources | No automatic remote fetch | Redirect, navigation and privacy tests |
| Executable content | No sender scripts, handlers or embedded applications | Inert parser and sanitizer conformance tests |

User accessibility preferences override author presentation where necessary. Responsive layout, bidirectional text, zoom, dark mode, and high contrast need defined expectations. Conformance should measure preserved meaning and specified layout behavior, not identical pixels across fonts and devices.

> [!norm] Content cannot impersonate the client
> Proposed rendering rules isolate message styles from application controls. Sender content cannot restyle the sender identity, security indicator, audience, or submission confirmation. CSS resource-loading features must follow the same resource policy as HTML.

Clients must parse and sanitize under the same declared profile. Unknown features cannot activate broader browser behavior. An Email/2 client must implement the [required baseline presentation](presentation-profile.md#required-presentation). Unsupported optional extensions and malformed input retain their defined safe recovery paths. A diagnostic text view can preserve access to content, but does not establish support for a missing required renderer. Receiving HTML is not permission to execute arbitrary web content.

AMP for Email provides relevant prior art for explicit HTML/CSS restrictions and interactive components.[^1] Its feature set and external-service assumptions are not automatically adopted here.

## Old messages remain original evidence

Legacy reconstruction is a local presentation feature. It may use reply headers, MIME structure, quoting syntax, signature patterns, and text comparison. `format=flowed` supplies useful rules for some plain-text wrapping and quotation depth.[^2]

The proposed client contract is:

- Retain the received message and make the original view available.
- Preserve attribution and each distinct contribution.
- Collapse confidently repeated quotations without deleting the underlying content.
- Preserve inline answers, changed quoted passages, and attachment context.
- Mark inferred relationships as interpretations; never emit them as authenticated statements by the original author.
- Prefer visible ambiguity over silently losing text or assigning it to the wrong person.

Subject equality alone is insufficient to merge conversations. Forwarded text does not make its quoted author a participant. A signature-like passage might contain substantive content and must remain recoverable.

These receiving rules preserve the original for reading. Outgoing composition separately follows [legacy history minimization](messages.md#replying-to-a-legacy-chain-without-carrying-its-history): omitting earlier history from a new delivery is different from deleting or visually hiding received content.

If an implementation uses remote processing to interpret messages, that changes who receives their contents. It cannot claim endpoint-only confidentiality while sending decrypted messages to another service without an explicit disclosure policy. AI processing is not required by this proposal.

## Explicit boundaries in new replies

The [reply-content contract](reply-content.md) defines indexed chunks and matching HTML Microdata for new messages. Its receiver procedure resolves source passages and keeps authored text separate from quoted context. Classes, indentation and copied-looking words do not establish those relationships. Legacy reconstruction below applies when that explicit contract is unavailable.

## Reconstruction procedure

Reconstruction produces a **presentation map**: a record of which source passages are displayed, grouped or collapsed. It never replaces the stored original. Every displayed or collapsed span retains its source message and source range; the original MIME bytes and decoding diagnostics remain available separately.

> [!ex] A changed quotation stays visible
> Bob changes “Tuesday” to “Thursday” inside a quoted passage. Most of the block matches Alice's message, but the change is substantive. The client keeps it visible instead of hiding the entire quotation as repetition.

The procedure below is the proposed receiver contract. Its normalization and matching rules must be declared by each reconstruction profile; they are not permission to guess away uncertain text.
1. Select the usable MIME representation and decode it under the media type's rules. Preserve decoding uncertainty. Interpret flowed text only when its declared format requires it; do not apply fixed-line heuristics to flowed text before resolving its wrapping semantics.
2. Identify candidate earlier messages using explicit reply references where available. Treat missing or conflicting references as uncertainty. A repeated subject or similar wording alone does not authorize merging conversations.
3. Segment the contribution into candidate quotations and intervening authored material. A quote prefix or HTML blockquote is a quotation hint, not proof that another person wrote the enclosed text.
4. Compare each candidate against earlier content with source mapping intact. Exact matching can establish repetition for display; it does not establish authorship or authenticate either copy. Fuzzy matches, changed text and ambiguous multiple matches remain visible unless an explicit user choice changes the view.
5. Collapse only a span whose repeated content and source are resolved under the selected reconstruction profile. Keep intervening inline answers visible in their original order, adjacent to enough question context to understand them. A collapsed span offers immediate expansion and identifies its source without overstating trust.
6. Keep edited quotations visible. Do not discard a whole quoted block because most of it matches. An implementation may separately map exact subspans only if it preserves every changed span and sufficient context.
7. Preserve signature-like text, forwarded headers, attachment references and unknown quotation styles. Hiding a signature is a separate reversible user preference, not proof that its text is irrelevant.
8. Recompute the presentation when a referenced message arrives. Preserve the reader's position and manual expansion choices where possible. Do not send an answer, receipt, reaction or capability response as a side effect of reconstruction.

A reconstruction profile MUST state its input formats, normalization rules, matching criteria and uncertainty behavior. The [fixed-line experiment](evidence/README.md#legacy-quotation-experiment) implements a deliberately narrow baseline: one-level `>` quotations, exact contiguous matches and exactly one source occurrence. It keeps all other text visible. That experiment does not satisfy the full legacy-client requirement: Broader HTML quoting, localized patterns and real-client fixtures still need implementation and audit. The separate [flowed reconstruction experiment](evidence/README.md#flowed-quotation-reconstruction) carries parsed quote depth and per-message wrapping rules into exact paragraph matching.

:::: {.details summary="Flowed text: preserve wrapping and quotation meaning"}

### Flowed text before quotation matching

For declared `text/plain; format=flowed`, count leading quote marks before removing exactly one stuffing space. Then recognize signature separators and trailing-space flow under RFC3676. With `DelSp=yes`, remove exactly the final flow-marker space; retain other content spaces. Missing or unrecognized DelSp means no deletion. Missing or unrecognized Format means fixed text.

Never join across a quote-depth change or signature separator. Body end also terminates an unfinished flowed paragraph. A space-stuffed literal `>` remains content, not quotation. Preserve mappings from each resulting paragraph to its source lines and retain malformed-boundary diagnostics. Authentication does not use the reflowed text. See the [flowed-text audit](audits/flowed-text.md).

### Historical flowed messages

RFC3676 remains the processing authority for flowed plain text, including messages originally generated under RFC2646. Missing DelSp retains the soft-break space; receivers MUST NOT infer DelSp=yes from apparent sender age, language or line length. Current generation MUST use RFC3676's rules rather than the older optional stuffing and line-length advice. Historical source defects do not justify silently removing spaces or joining ambiguous quote depths. See the [historical flowed-text audit](audits/flowed-history.md).

::::

The [local conversation demo](evidence/README.md#inspectable-legacy-conversation-demo) makes the plain-text and narrow HTML experiments inspectable through expandable quotations, source navigation and an Original view. Its synthetic fixtures do not establish general legacy-client compatibility. Fixture IDs, inferred-source labels and source offsets are diagnostic controls in that test harness, not prescribed client wording or a product interface. A client can offer a simple “Show quoted text” disclosure and expose the matching evidence and uncertainty through inspection; collapsing a quotation does not authenticate its author or source relationship.

:::: {.details summary="HTML quotations: map the source before rendering"}

### A narrow source-preserving profile

The [strict HTML experiment](evidence/README.md#strict-html-quotation-mapping) accepts lowercase `p` paragraphs, text-only `div` paragraphs with `br` line breaks, balanced inert `div` wrappers, and one-level `blockquote` containers. It permits quoted `cite`, `type` and `class` attributes on blockquotes and `class` on divs, retaining their source spans without treating attributes as author identity, navigation or evidence of repetition. Unsupported or malformed structure remains visible as original source. A complete quotation collapses only when its paragraph sequence has exactly one matching occurrence in unquoted parent content. Edited and ambiguous quotations stay visible. Localized surrounding text stays visible without becoming an inferred author or reply boundary.

The scanner records half-open UTF-16 code-unit ranges into the original decoded HTML **before** interpreting character references or line endings. These are neither MIME-byte offsets nor RFC5147 character positions. Comparison interprets accepted references and normalizes CRLF/CR to LF; it does not fold other whitespace, normalize Unicode or use fuzzy matching.

Unsupported or malformed input remains fully visible as literal source, with no partial collapsing. Rendering constructs inert elements and text from the accepted structure; repaired browser DOM positions cannot substitute for original-source ranges. Original MIME evidence remains available independently of this presentation map.

::::

## Trust stays visible

A smooth conversation view must not make unrelated or differently protected content look like one verified statement. An attached encrypted message keeps its own sender and protection status. A quoted name does not make that person a participant. A protected reply relationship takes precedence over an unprotected outer header.

These boundaries apply before quotation cleanup. The rules below describe the cases in which a renderer must preserve a separate origin, show provisional placement or refuse an inferred relationship.

:::: {.details summary="Reply placement, protected headers and embedded encryption"}

### Resent history and reply targets

Keep a message's original authorship separate from its resending history. Resent fields describe a user reintroducing the existing message into transport; they do not replace the original From, Reply-To or Message-ID for normal reply processing. Preserve each resent block and its order rather than merging every Resent-From into the conversation's authors or members.

A reply can identify multiple parents through In-Reply-To. Do not force such a reply into a single authenticated parent merely to fit a linear display. A display may choose one visual position while preserving all source relationships; References does not define a general multiple-parent construction algorithm.

For legacy duplicate singleton fields whose interpretation is unspecified, preserve the ambiguity. Do not silently choose the first or last author, reply target or identifier and then treat that choice as verified. Any proposed recipient selection must still be visible before sending, and must satisfy the delivery and identity policy.

Legacy repeated destination fields have a defined interpretation distinct from repeated singleton author or identifier fields: combine the address lists for occurrences of the same destination field. Keep To, Cc and Bcc separate, preserve each source occurrence, and apply blind-copy privacy rules when proposing a reply. This parsing rule does not establish that header recipients equal the actual delivery envelope or the authorized encrypted audience.


### Protected headers and provisional conversation placement

When interpreting an RFC9788 message with header protection, the client MUST use the protected Message-ID, References and In-Reply-To fields for conversation placement. An outer field MUST NOT override a protected field or supply a missing authenticated relationship. While decryption is unavailable, any placement based on outer headers is provisional. Successful decryption can change the displayed subject and conversation placement; the client must retain the original message and its provenance through that change.

A protected From value is not automatically a verified identity. The client must distinguish signature validation from a valid binding between the signing credential and that address. For RFC9788's From-mismatch handling, compare the actual outer From field, not its protected HP-Outer copy. The draft's endpoint trust rules still determine whether a sender is verified. Address comparison used to detect a display mismatch MUST NOT merge account identities or discard local-part distinctions in stored routing addresses.

An RFC9788 legacy display element is removable presentation material only in the qualifying encrypted MIME context described in Sections 4.5.3.1–4.5.3.3. A matching HTML class or a line resembling a header in ordinary mail is insufficient. Removal applies to rendered and reply-derived content; it MUST NOT mutate the preserved signed source. The original remains available through the source view. This differs from heuristic quote collapsing, whose uncertain classifications must remain reversible.

Apply the receiving-side header-protection rules in [RFC9788 §4](https://www.rfc-editor.org/rfc/rfc9788.html#section-4). See the [header-protection audit](audits/header-protection.md) for source interpretation and unresolved dependencies.


### Preserve cryptographic boundaries in conversation views

When a provider supplies several body parts for sequential display, render each part in isolation. Do not concatenate their raw HTML or text into one parser input: an unfinished element in one part can change the interpretation of the next. Preserve those boundaries even when the conversation UI visually groups the parts. This requirement also applies to ordinary unencrypted multipart mail, following [RFC8621 §9.3](https://www.rfc-editor.org/rfc/rfc8621.html#section-9.3).

A clean conversation view MUST NOT merge decrypted content from an embedded encryption layer with surrounding message content into one trusted body. Render that decrypted subtree in an isolated content container with its own provenance. Message text, HTML, CSS and inline controls MUST NOT draw over or modify the client-owned security indicator.

An embedded signature or encryption layer does not upgrade the enclosing message's protection status. A forwarded message/rfc822 or message/global attachment can have its own protection status, clearly tied to that attached message. A mailing-list footer may be shown alongside a signed contribution only when its distinct origin and lack of signature coverage remain clear; a List-ID field alone is not cryptographic evidence that the footer is trusted.

Automatically generated replies MUST NOT quote or attribute decrypted content from an embedded encryption layer outside the enclosing message's cryptographic envelope. This restriction also applies to armored encrypted text embedded within a body. Offering an isolated reading view does not authorize automatic reply extraction from it, even when the reply itself will be encrypted. Preserve the original source and allow the user to inspect the separate content without silently turning it into a conversation event or structured answer.

These boundaries apply before heuristic quote cleanup, threading and rich-message normalization. The visual continuity of a conversation must not erase differences in authorship or authentication scope. They follow [RFC9787 Sections 4.5 and 6.2–6.3](https://www.rfc-editor.org/rfc/rfc9787.html#section-6.2); the [base-document audit](audits/e2e-guidance.md) is complete, while transitive dependency and implementation validation remain open.

::::

:::: {.details summary="Passage navigation is not a structured answer target"}

### Text fragments and inline response targets

A plain-text fragment may locate a passage for reading. It MUST NOT, by itself, identify a structured question, field revision or authorized response operation. A structured answer must use the interaction contract's exact authenticated target identity. Unsupported, invalid or unresolved display fragments leave the complete contribution available; they do not select a different answer target.

A client offering RFC5147 display navigation must retain the referenced MIME entity and its decoding context. Character positions are not byte or UTF-16 code-unit offsets. Reflowing, quote removal, Unicode normalization and charset recovery are presentation transformations; offsets into those views MUST NOT silently replace offsets into the referenced entity. If mapping is uncertain, display the whole relevant contribution and mark the passage reference unresolved.

For Email/2 structured operations, out-of-range or mismatched targets MUST fail resolution rather than clamp to the nearest available field or passage. RFC5147's optional length/MD5 checks MUST NOT substitute for the security profile's authenticated content binding. A selected passage must retain attribution and access to surrounding context so a partial quotation cannot impersonate the whole source. See the [text-fragment audit](audits/text-fragments.md).

::::

## Decoding and legacy controls

Text recovery can make a damaged message readable. It cannot repair the bytes used to authenticate that message. Likewise, a mailing-list control can offer a deliberate action; merely displaying the message cannot execute it.

:::: {.details summary="Character decoding and preserved header source"}

### Character decoding boundary

New-profile readable alternatives declare UTF-8 explicitly and contain valid UTF-8 after transfer decoding. This generation rule does not redefine legacy text/plain's US-ASCII default or the charset rules of other media types.

Contradictory charset declarations or invalid UTF-8 disable new-profile interactive processing. A safe recovered display may remain available with its recovery identified. Do not use guessed or repaired display text as the bytes authenticated by the security profile. MIME transfer decoding precedes character decoding, which precedes HTML parsing and sanitization.

The [presentation profile](presentation-profile.md#processing-order) requires explicit MIME UTF-8, strict decoding and inert HTML document parsing. HTML metadata cannot override the MIME declaration. Conflicting or ambiguous declarations prevent interactive activation. The [charset audit](audits/text-charsets.md) records the inherited media-type rules; broader parser conformance remains part of rendering validation.

### Parsed headers and preserved source

Legacy header interpretation and new-message generation are distinct operations. Recognizing an obsolete address form in an archived message does not authorize generating that form in a new contribution. Preserve the source alongside the parsed result; a display normalization is not a replacement for bytes needed by signature verification.

Apply unfolding, comment parsing and quoted-pair interpretation only in the grammar positions where they are defined. Do not globally remove parentheses, backslashes or whitespace from all header values. In particular, unstructured subject text and structured addresses do not share one comment-removal rule. A header address's liberal syntax also does not establish that it is a valid SMTP envelope destination.

Physical line limits do not bound the total length of an unfolded field. Resource-limit failures must be reported as incomplete processing, rather than silently truncating a value and treating the truncated address or identifier as authoritative. The ongoing emailcore revision review retains these parsing boundaries without changing the published baseline automatically.

::::

:::: {.details summary="Mailing-list grouping and deliberate list actions"}

### Mailing-list organization

A legacy List-Id can organize list mail, but it does not make all messages from the list one conversation. Compare the bracketed identifier case-insensitively and keep the optional descriptive phrase separate. Preserve message-level reply relationships and the original field.

List-Id does not authenticate the author, establish group membership or authorize access to history. Nested lists may preserve a parent's identifier. A changed identifier must not silently transfer the old list's trust or keys. The [mailing-list identity audit](audits/list-identity.md) records syntax corrections and the limited naming contract.

### Existing mailing-list controls

Clients may expose existing List-Help, List-Subscribe, List-Unsubscribe, List-Post, List-Owner and List-Archive fields as list controls. These controls do not establish conversation membership, endpoint identity or administrator authority. A List-Post value of NO disables the list-post action.

Rendering, previewing, focusing or scanning a message MUST NOT execute a list command. Before sending a mail command, provide an opportunity to review the destination, sending account and action, including the generated message. When the applicable sending account is ambiguous, request a choice. Do not interpolate account information into unsupported command templates.

URL alternatives represent alternative ways to perform one command, not a batch of actions. Keep ordinary list URL handling distinct from the authenticated RFC 8058 one-click POST mechanism. The [list-control audit](audits/list-controls.md) records parsing rules and nested-list behavior.

::::

The [presentation failure matrix](presentation-profile.md#when-presentation-cannot-finish) distinguishes invalid carriers, refused rich projections, unavailable individual resources and valid accessibility preferences. A recovered reading view cannot supply missing authorization or silently change quotation/source roles.

## Rendering tests

The profile requires fixtures for nesting, malformed input, unsupported CSS, remote-resource attempts, keyboard-only interaction, screen-reader semantics, long text, right-to-left content, and style isolation. Legacy fixtures should include bottom-posting, top-posting, interleaved replies, localized quotation markers, edited quotations, forwarded messages, and signatures containing meaningful answers.

The [suite agreement](suite-profile.md) selects the exact required presentation profiles and authenticated negotiation. The [acceptance inventory](acceptance-inventory.md) and [interoperability coverage](interoperability.md) distinguish their complete implementation requirements from existing component evidence.

## References

[^1]: [AMP email format](https://amp.dev/documentation/guides-and-tutorials/learn/email-spec/amp-email-format), [supported HTML](https://amp.dev/documentation/guides-and-tutorials/learn/email-spec/amp-email-html), and [supported CSS](https://amp.dev/documentation/guides-and-tutorials/learn/email-spec/amp-email-css).
[^2]: [RFC 3676 — Text/plain format and DelSp parameters](https://www.rfc-editor.org/rfc/rfc3676.html).
