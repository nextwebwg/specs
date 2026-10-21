---
title: Presentation profile 1
order: 14
blurb: permitted HTML · CSS values · isolation
sectionNav: true
---

# Presentation profile 1

This is a proposed interoperable rendering vocabulary for newly generated Email/2 messages. It is an editorial draft, not a registered profile or a claim of implementation conformance. Legacy display uses a separate compatibility path and preserves the received source.


## Required Email/2 presentation {#required-presentation}

The defined HTML/CSS presentation is a required part of the Email/2 client baseline. A conforming reading client MUST implement `html-css-v0` as specified in this chapter, including parsing, filtering, resource handling, client-owned styles and failure behavior. A composing client MUST generate supported HTML whenever it supplies an HTML body. There is no text-only Email/2 client conformance class: substituting a plain-text alternative because the client lacks the required renderer does not satisfy this requirement. A transport-only server does not need to render messages.

HTML/CSS is the shared presentation format, not an optional enhancement that each client may approximate differently. This does not require arbitrary web content, identical pixels or an HTML body on every protocol event. Text-bearing operations and client-owned interaction controls retain their exact schemas; their readable presentation is constructed under the selected presentation contract. The separately versioned reply-content extension is not enabled merely by baseline support.

Plain-text MIME alternatives remain compatibility representations for existing email clients. Existing carriers that require them still require them. Structured `text` fields remain available for matching, indexing, accessible reading and explicit text views; they do not provide an alternative route to client conformance. This requirement does not remove text fields or change an immutable wire schema.

A reader may choose a simpler text view, and accessibility preferences may override sender styling. Malformed content, failed authentication, unavailable resources and processing limits retain their specified safe handling. A client may expose a diagnostic text view or the original when rich presentation fails, but MUST NOT treat that recovery as successful rendering of a conforming HTML/CSS message. An unsupported optional extension stays unsupported; no such failure authorizes interactive effects or weakened delivery protection.

## Processing order

Transfer-decode the selected MIME entity, require an explicit UTF-8 charset, then validate UTF-8. Parse the resulting HTML as an inert HTML document with scripting disabled and no network loader. Use the HTML Standard's document parsing algorithm; do not substitute XML parsing or regular-expression sanitization. The renderer uses standards mode irrespective of a missing legacy doctype. New generators emit `<!doctype html>`.

The parser must not execute scripts, upgrade custom elements, fetch resources or submit forms while constructing the tree. Create a fresh allowed tree after parsing; never attach the unfiltered tree to the application. The [HTML parsing audit](audits/html-parsing.md) records the selected recovery rules, element semantics and implementation limits. Transfer only permitted nodes, attributes and parsed style values. A final permitted tree is a rendering projection, not a replacement for the authenticated original.

This draft uses the reproducible HTML source revision identified in the [parsing audit](audits/html-parsing.md) and the CSS declaration-list rules identified in the [syntax audit](audits/css-syntax.md). HTTP(S) navigation uses the selected URL rules and source snapshot in the [navigation audit](audits/service-uris.md#browser-parser-review). Record reference changes with the profile version and its conformance cases; upgrading a runtime alone does not change the profile. The source pins make comparison reproducible, but do not establish parser conformance.

## Encoding declaration consistency

The selected MIME charset for this generation profile MUST be explicitly `utf-8`, compared ASCII case-insensitively after MIME parameter parsing. This profile does not infer that declaration from HTML metadata or accept a missing MIME charset merely because the bytes happen to decode. Transfer-decoded bytes MUST pass strict UTF-8 validation before HTML parsing.

A permitted HTML encoding declaration contains only the `charset` attribute with value `utf-8`, compared ASCII case-insensitively. An unsupported meta form, including http-equiv encoding declarations, is nonconforming in newly generated profile content. No metadata changes how the already validated Unicode input is interpreted. A receiver may retain a recovered readable projection, but MUST prevent interactive activation when encoding declarations conflict or are ambiguous.

Duplicate source attributes cannot be assessed only from the final DOM, because parsing can discard a competing value. The parser adapter MUST preserve relevant source diagnostics before filtering. Consistency must be assessed from the competing declarations, not merely the surviving attribute. A consistent encoding result is only one prerequisite, not proof of sanitizer or interaction conformance.

## Elements

Only elements in the HTML namespace are eligible. The permitted body vocabulary is:

`a abbr b bdi blockquote br caption code col colgroup dd del div dl dt em h1 h2 h3 h4 h5 h6 hr i img li ol p pre s small span strong sub sup table tbody td th thead tfoot tr u ul wbr`

Document wrappers `html`, `head` and `body` are structural. Only `meta charset="utf-8"` is permitted in the head; it cannot override the MIME encoding. A conflicting encoding declaration makes the message nonconforming for this profile and disables interactive activation. The head has no displayed content.

Remove comments. Remove these elements with their subtrees: `script style template iframe frame frameset object embed applet noscript textarea select option button input video audio source track canvas` and all foreign-namespace subtrees. They cannot supply hidden required meaning. Remove any other unlisted wrapper while retaining and recursively filtering its children. In particular, an imported `form` wrapper cannot submit anything; its surviving text may remain readable. New generators emit only the allowed vocabulary.

A plain-text compatibility alternative must contain every substantive contribution. It does not replace the required Email/2 HTML/CSS presentation. If discarded content carries indispensable meaning, the authoring client must correct the message before sending; a receiver can expose the readable alternative and a nonconformance notice.

## Prohibited-container recovery policy

For a valid body-level noscript container, remove its parsed subtree as specified above while retaining surrounding content. For malformed head-level noscript content that triggers recovery into ordinary body content, the receiver MUST refuse the rich projection and expose the separately handled readable alternative with a nonconformance diagnostic. It MUST NOT present the relocated content as though prohibited-container filtering had succeeded.

This distinction requires parser state and recovery diagnostics; substring matching is insufficient. Each parser adapter must identify the equivalent recovery condition. Missing or insufficient diagnostics cannot establish conformance.

The [parser-adapter evidence](evidence/README.md#parse5-projection-adapter) records tested behavior and implementation limits. A parser that cannot distinguish these cases must refuse the rich projection; retaining the original and readable alternative remains required.

## Attributes

The common permitted attributes are `lang`, `dir`, `title` and `style`. `dir` accepts only `ltr`, `rtl` or `auto`. Language handling follows the rule below. Titles are supplementary: required instructions cannot exist only in a tooltip. Preserve effective inherited titles across removed wrappers and document containers, including an explicit empty title that cancels ancestor advice. Discarded subtrees do not supply advisory information to surviving siblings.

### Language labels

Generators MUST emit a valid RFC5646 language tag or an empty `lang` value. Validity includes registry and structural checks; matching the grammar alone is insufficient. Deprecated tags remain permitted. Base validity checks allocated extension singletons and their syntax; this profile does not claim extension-specific semantic validation. See the [language-tag audit](audits/language-tags.md).

Validate generated labels against locally installed IANA Language Subtag and Extension Registry snapshots. Conformance reports MUST identify each snapshot's File-Date and content digest. The [authoring experiment](evidence/README.md#language-tag-authoring-validation) supplies reproducible datasets; implementations may use newer identified snapshots. A label unavailable in the installed data produces an authoring diagnostic, not a guessed replacement language. The empty unknown-language value remains permitted.

Registry updates are client maintenance, separate from message processing. Obtain them through an authenticated software or data update path using configured trusted registry sources. Check the dataset structure and its declared version and digest before activation; retain the previous usable snapshot if an update is unavailable or invalid. A received message MUST NOT select an update URL or trigger a registry fetch. Installing new data never rewrites existing messages or their authenticated labels.

Receivers preserve the parsed `lang` value in the rendering projection. An empty value explicitly means unknown language; omission inherits from the parent. An unrecognized value remains an unknown language with that label, rather than being guessed, translated into another naming system, or discarded so that a different ancestor language takes over. This follows [HTML language handling](https://html.spec.whatwg.org/multipage/dom.html#the-lang-and-xml:lang-attributes). Preserving a received label is not certification of authoring conformance.

Language processing MUST NOT fetch registry data in response to a message, rewrite authenticated source bytes, or change text direction by inference. The message's language context must remain isolated from the application's interface language. Projection must preserve effective language across removed wrappers. The tree experiment carries inherited labels onto retained elements and wraps affected bare text in inert language-bearing spans. Its standalone preview has no host-application ancestor or default language. Reparse fixtures cover nested overrides, unknown language, text following a removed wrapper and table whitespace; assistive-technology behavior remains untested.

### Element-specific attributes

| Element | Additional attributes |
| --- | --- |
| a | href |
| img | src, alt, width, height |
| ol | start, reversed |
| li | value |
| td, th | colspan, rowspan |
| th | scope: row, col, rowgroup, colgroup |
| col, colgroup | span |

The separately proposed [reply-content presentation](reply-content.md#microdata-vocabulary) permits only its scoped Microdata, wrapper IDs and metadata under a new profile. It does not widen this baseline or allow a renderer to claim support before implementing that profile.

No other baseline attributes survive, including event handlers, custom data attributes, IDs, classes, ARIA overrides, hidden, tabindex, contenteditable, download, target, ping and srcset. Native semantic elements supply accessibility roles. Client-rendered interaction controls are outside this sender-authored tree.

Integer-valued table spans accept decimal integers1–1000; rowspan zero is not supported. Image width/height accept decimal integers1–4096 as preferred CSS-pixel dimensions, bounded further by the available viewport. List counters accept signed decimal integers in the range−2147483648…2147483647. These are proposed profile limits, not inherited HTML limits. Invalid attributes are discarded with a recorded diagnostic.

`img` requires alt text and a `cid:` source resolved through the message resource rules. A missing resource shows its alt text. The baseline image types are static PNG and JPEG; animation, SVG, remote images and data URLs are outside this profile. The [image interpretation rules](audits/image-formats.md) define required PNG depths/types/interlace, common JPEG interchange, primary-image orientation and color conversion. These requirements preserve the intended image rather than treating unmanaged pixel extraction as complete support.

This profile uses explicit positive finite client-local budgets for encoded data, dimensions, decoded pixels/output, metadata expansion, memory and processing time; it defines no universal attachment-size guarantee. Check limits before allocation where possible, during expansion and again after transforms. Resource failure retains the alternative text and a client-owned explanation. Conformance reports state their budgets and exercise required image cases within them; a resource rejection cannot be misreported as absence of format support. These are resource-policy rules of the proposed profile.

::: {.details summary="Decoding an image resource"}
Authenticate and resolve the resource within its selected message before decoding it. A matching Content-ID alone is insufficient. Check the declared format against the decoder's detected format, reject animation, and bound encoded bytes, dimensions, pixel count and decoded output. A decode failure leaves the alternative text available; it must not initiate a remote fetch.

The [image decoder experiment](evidence/README.md#isolated-image-decoding) returns tightly packed RGBA pixels from a separate process. It tests PNG/JPEG input, format mismatch, malformed data, animation and adjustable resource limits. CPU, wall-time and output controls apply before decoding; a resident-memory watchdog also observes work before dimensions are known. The tested macOS watchdog is not a hard allocation ceiling or a security sandbox. Hard memory enforcement on supported platforms still needs validation. The host must not hand the original encoded file to another unrestricted decoder after these checks.

A [scoped image adapter](evidence/README.md#scoped-resource-to-pixel-integration) connects resource scope, size and digest checks to decoding, using a manifest and compound selection authenticated by its caller. It does not perform upstream signature verification or browser display. The [image-format audit](audits/image-formats.md) maps selected standards and corrections. The decoder has focused evidence for primary orientation, color conversion and high-depth sample handling; comprehensive codec coverage, independent color-management agreement, assistive-technology behavior and hard decoder containment remain unproven.
:::

`a` permits absolute HTTPS and HTTP navigation only. No relative URLs, credentials in URLs, automatic navigation or sender-controlled target browsing context. The client exposes the destination before deliberate navigation, opens it outside the message context and sends no message-origin referrer. Additional link schemes, including mailto and mid, require distinct client navigation handlers rather than passing arbitrary schemes to a browser. Text remains when a link is rejected.

A relative link such as `../account` needs a base URL. The message profile supplies none: the client must not borrow the webmail page, local preview address, sender domain or a discarded HTML `base` element to invent its destination. Rejected links remain readable text. Relative links can be valid in other document formats; this restriction makes a message’s navigation independent of where the client displays it.

## Navigation URL processing

After HTML attribute decoding, reject navigation values containing literal U+0000–U+0020, U+007F, a backslash or a non-scalar code point. Require an ASCII-case-insensitive `http://` or `https://` prefix and a nonempty authority. Reject an authority containing `@`, including empty user information. These are profile input restrictions, not claims that the URL Standard rejects all such strings.

Parse remaining candidates using the [WHATWG URL parser](https://url.spec.whatwg.org/#api) without a base URL. Reject parse failures, missing hosts, non-HTTP(S) schemes and nonempty parsed credentials. Retain the serialized parsed destination for the client navigation handler and destination display. Do not perform percent-decoding or HTML decoding again. A valid destination is not proof that its site is safe or that displayed link text accurately describes it.

Browser navigation uses the URL Standard’s web-compatible host processing, not the strict IDNA rules used for mailbox identities. A successful parse is therefore not an IDNA2008 validity result. The client displays the parsed destination, including any host conversion, rather than treating the sender’s original spelling as the destination.

Validation MUST NOT fetch, preload, resolve for preview, open, or send a receipt. Navigation remains a deliberate user action outside the message's context with no message-origin referrer. The [navigation experiment](evidence/README.md#navigation-url-validation) implements this decision using the runtime URL API; pinning its standard snapshot and testing browser/IDNA differences remain required conformance work.

## Link integration boundary

A parser adapter may retain an HTML-decoded link value as inert intermediate data while validating the rest of the tree. It MUST NOT assign that candidate directly to a live DOM attribute. The navigation stage consumes the candidate and either produces a client-owned destination record or removes the relationship while retaining link text. Sender target, ping and event-handler attributes remain prohibited regardless of destination validity.

The [HTML/navigation integration experiment](evidence/README.md#html-navigation-integration) connects HTML entity decoding to URL validation, checks rejected-link text preservation and removes raw candidates from the resulting data. The separate [browser host](evidence/README.md#isolated-browser-rendering) exercises deliberate keyboard activation, destination disclosure and an external browsing context without referrer or opener. Native link behavior and assistive-technology checks remain incomplete; a destination record alone cannot enforce navigation policy.

## CSS

Only inline declarations are accepted. There are no author stylesheets, selectors, at-rules, custom properties, URL values, functions, escapes in property names, vendor extensions or `!important`. Use the [reviewed declaration-list syntax](audits/css-syntax.md) and parse declarations before validation; discard a rejected declaration as a whole. Unknown properties cannot be forwarded to a browser for opportunistic support.

| Properties | Accepted values |
| --- | --- |
| color, background-color, border-color | #rgb or #rrggbb hexadecimal; transparent additionally for background-color |
| font-family | serif, sans-serif, monospace |
| font-size | 0.75rem, 0.875rem, 1rem, 1.125rem, 1.25rem, 1.5rem, 2rem |
| font-style | normal, italic |
| font-weight | normal, bold, 400, 700 |
| line-height | normal, 1, 1.25, 1.5, 1.75, 2 |
| text-align | start, end, left, right, center |
| text-decoration-line | none, underline, line-through |
| white-space | normal, pre-wrap |
| overflow-wrap | normal, anywhere |
| margin-top, margin-right, margin-bottom, margin-left | 0, 0.25rem, 0.5rem, 1rem, 1.5rem, 2rem |
| padding-top, padding-right, padding-bottom, padding-left | same spacing values as margin |
| border-width | 0, 1px, 2px, 3px |
| border-style | none, solid, dashed, dotted |
| border-collapse | separate, collapse |
| vertical-align | baseline, top, middle, bottom |

Keywords and hexadecimal letters are ASCII case-insensitive. A hash token is checked after CSS escape decoding: it must contain exactly three or six hexadecimal digits, and the output is rebuilt as lowercase literal hexadecimal. This does not permit escapes in property names. Numeric spellings in this table are literal permitted tokens; equivalent alternate numeric spellings are outside the generation profile. Each accepted value is exactly one non-whitespace, non-comment CSS token. Keyword escapes are decoded before matching; an escaped identifier that decodes to a number is not a numeric token and is rejected. Numeric values must use the exact spelling and unit shown in the table. Whitespace and comments are handled by CSS parsing. The explicitly listed border-width, border-style and border-color properties apply uniformly to all four sides; no other shorthand is accepted. Multiple decoration keywords are outside this profile. Global keywords, unlisted shorthand declarations, positioning, floats, transforms, opacity, visibility and display changes are excluded. The last valid declaration for a property wins. Inheritance uses the property definition; user accessibility rules always override author rules.

The [selected font-property audit](audits/css-fonts.md) records inheritance, generic fallback and the limits of predictable typography. The [inline alignment and spacing audit](audits/css-inline.md) records the permitted alignment meanings and why unitless line height must retain its inherited ratio. In inline text, vertical-align: middle uses the x-middle baseline; it is not general container centering. Table-cell alignment follows the table layout rules. The [table and box audit](audits/css-table-box.md) explains margin collapse, property applicability and separate versus collapsed borders. Accepted cell margins and row padding do not create layout space; collapsed tables do not use table padding. Automatic table widths can vary by browser.

These restrictions are proposed to make support testable. They are not a claim that every CSS feature omitted is unsafe. Richer layout can be a later negotiated profile with its own complete vocabulary and tests.

## Layout and accessibility

The client sets the root font size from user preferences. Sender `rem` lengths follow that root; CSS pixels describe CSS layout units, not a promise of one physical screen pixel. See the [selected number and unit rules](audits/css-values.md). Message content occupies its own formatting context and cannot overlap trusted identity, audience or protection controls. Images shrink proportionally to the available inline size. The pixel host enforces border-box sizing on image canvases so their preferred width and maximum inline size include retained padding and borders; see the [selected layout rules](audits/css-layout-dependencies.md). Long text wraps when the selected wrapping rule permits it. Unbroken content, preformatted blocks and wide tables remain reachable through labeled, keyboard-accessible scrolling without widening the application viewport. Wrapping and scrolling do not change retained text; see the [text-processing rules](audits/css-text.md) and [scroll-container rules and evidence limits](audits/css-overflow.md).

Headings, lists, quotations and table headers retain native semantics. High-contrast mode may replace colors; zoom and user fonts remain effective. Bidi text uses permitted HTML direction attributes and isolation at the message boundary. Sender formatting cannot reorder application controls. No content becomes interactive merely because it visually resembles a button.

## Client-owned baseline styles

The [baseline stylesheet](evidence/README.md#presentation-default-styles) selects explicit initial typography and spacing for the allowed tree. Body text uses the user's root font size, sans-serif family and a 1.5 line height. Heading sizes are 2rem, 1.5rem, 1.25rem, 1.125rem, 1rem and 1rem respectively. Paragraphs and block structures have a 1rem trailing margin. Lists use 2rem logical indentation and native inside markers so large ordinals remain within the contained message; wrapped text follows inside-marker layout. Quotations use a 1rem logical inset and a visible leading rule. Code and preformatted content use monospace; preformatted text wraps by default.

This stylesheet is client-owned and may use features outside the sender CSS allowlist. Its use of system colors, logical properties, isolation and subscript positioning does not authorize equivalent sender declarations. Apply approved sender declarations over the baseline, then enforce containment and accessibility overrides with client-owned rules that outrank sender declarations on each affected element. This is an enforcement boundary, not merely a named CSS layer; the [cascade audit](audits/css-cascade.md) explains the required precedence. In particular, sender styles cannot defeat image viewport bounds, user contrast or readable link affordances. A literal stylesheet alone does not establish that cascade boundary.

The baseline uses native HTML display semantics and system Canvas, CanvasText and LinkText colors. It does not pin platform fonts or require pixel-identical results. Native list numbering, table semantics, direction handling and keyboard focus must remain intact. The [lists audit](audits/css-lists.md) explains the retained numbering attributes and the separate need to test marker visibility under containment and accessibility overrides. Wide-table scroll regions need client-created accessible labels and keyboard handling; the stylesheet cannot supply those semantics. The Chromium host check focuses its named table region and uses an actual ArrowRight keypress to verify horizontal scrolling while retaining the native table. This checks keyboard interaction, not screen-reader output. The proposed CSS file records the baseline for implementation and visual fixtures, and has limited Chromium checks for layout, forced colors and enlarged root text. Native browser zoom and assistive-technology checks remain outstanding.

The [isolated browser experiment](evidence/README.md#isolated-browser-rendering) accepts a client-owned root font size and keeps sender `rem` values relative to it. Chromium tests cover nested sizes and spacing, preference changes and overflowing content contained within the message frame. This is implementation evidence for root sizing, not evidence of native zoom, minimum-font restrictions or assistive-technology behavior.

## Implementation evidence and limits

The evidence implements parts of this contract, not a conforming renderer. The current boundaries are:

| Stage | Executable evidence | Remaining work |
| --- | --- | --- |
| CSS declarations | Thirteen declaration-filter tests cover parsing, allowed values, escaping and last-valid selection | Broader cross-engine cascade and layout coverage |
| HTML projection | Thirty-one Python HTML-stage tests cover element/attribute filtering, encoding diagnostics, URL integration, serialization and recovery cases | Authoring-client language integration, broader malformed-input corpus and browser differential checks; image/resource integration has separate evidence below |
| Parser execution | Disposable html5lib worker and explicit parse5 adapter with input, CPU, wall-time and output limits; resident-memory watchdog | Hard allocation containment on tested macOS, Linux enforcement validation, complete parser migration and broader recovery fixtures |
| Language labels | Received labels and inherited language survive projection; a standalone authoring validator uses pinned registry snapshots | Authoring-client and authenticated update-path integration, plus assistive-technology behavior |
| Images | Scoped Content-ID validation, isolated PNG/JPEG decoding and client-owned pixel display | OS memory containment, independent color-management agreement and broader decoder coverage |
| Navigation | URL and HTML integration checks plus deliberate browser navigation without referrer or opener | Native link behavior, broader browser coverage and accessibility |
| Presentation | Client-owned baseline, inert serializer and isolated Chromium host with bounded input and lifecycle checks | Native zoom, other engines, broader layout and assistive-technology validation |

The [CSS experiment](evidence/README.md#inline-css-declaration-filtering), [HTML projection](evidence/README.md#inert-html-element-projection), [navigation integration](evidence/README.md#html-navigation-integration), [serializer](evidence/README.md#fresh-html-serialization) and [parse5 adapter](evidence/README.md#parse5-projection-adapter) document their commands and assumptions. Counts overlap where stages are integrated and must not be added as independent coverage.

The [isolated parsing experiment](evidence/README.md#isolated-html-parsing) applies resource controls before parser work and returns a typed failure instead of a partial projection. Receiving clients retain the readable alternative; authoring rejects a failed rich projection. The memory watchdog on tested macOS can overshoot its threshold and is not a hard allocation ceiling. Implementation limits are configurable and do not establish shared wire limits.

The default html5lib 1.1 path refuses template and noscript contexts because it does not establish the required recovery behavior. The explicitly selected parse5 path correctly contains the tested template fixture, removes valid body noscript and refuses malformed head noscript recovery. Both paths remain experimental. Parser comparisons and corrections are retained in the evidence documentation rather than treated as successive versions of the normative rule.

The serializer consumes the internal filtered tree and emits a fresh preview wrapper with client-owned CSP. Same-parser round trips are useful regression evidence but do not prove browser isolation or mutation-XSS resistance. The preview intentionally omits active navigation and image loading; it MUST NOT be advertised as support for those required features. Original authenticated content remains separate from every projection.

## Conformance still to establish

The vocabulary, source references, language-data policy, image interpretation and baseline styles are specified. Implementation conformance remains unproven. Evidence still needed includes authoring-client language/update integration, broader decoder and parser corpora, hard resource containment, independent color-management agreement, cross-engine navigation and layout, native accessibility, and real-client legacy rendering. The local experiments establish their recorded cases; they do not authorize a claim of complete profile support.

## Direction after projection

Preserve direction boundaries rather than copying `dir` onto every descendant. The local projection retains explicit `html` and `body` direction as nested message-only containers, so client-generated titles cannot determine `auto` direction. A direction-bearing form in supported body-flow contexts becomes one inert block boundary; its trailing text stays outside. A `bdi` with omitted direction retains its automatic behavior.

Automatic direction applies to filtered message content. This is a proposed projection policy, not a promise to preserve the source document's computed direction after removing content. Other removed direction-bearing wrappers produce a diagnostic until a context-safe replacement is defined. A Chromium geometry check verifies that a Hebrew paragraph in `pre dir="auto"` reads right to left and a following Latin paragraph reads left to right, with the newline preserved. This is one actual layout case, not complete bidi coverage. Nested mixed-direction text, malformed table reparsing, other engines and assistive-technology output still need validation.
