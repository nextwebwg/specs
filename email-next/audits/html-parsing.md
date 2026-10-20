---
title: HTML parsing and retained semantics audit
sectionNav: true
---

# HTML parsing and retained semantics audit

Parse the message before filtering it. HTML recovery can move text out of a table, reconstruct formatting elements, and change which namespace an element belongs to. Removing forbidden tag names from source text cannot reproduce those rules.

The [presentation profile](../presentation-profile.md) therefore requires an inert parser followed by a fresh permitted tree. The recovered tree is a readable projection of the original message; it does not replace its authenticated bytes.

## What the source review covers

This review uses [WHATWG HTML revision e8393694](https://github.com/whatwg/html/blob/e8393694edd92117cfb4886e2fe5dd2897374136/source), source SHA-256 `9c4e7371b2ed1f59e4a713828e8f766a972f17a7a695dfa4d32dad8ff0a58551`. It covers the parser's algorithm text and selected retained-element definitions, not the entire HTML standard or every browser subsystem.

| Reviewed source | Consequence for this profile |
| --- | --- |
| Parsing model, errors and byte-stream handling; source lines 140888–142599 | Validate UTF-8 before parsing. General HTML encoding sniffing and replacement decoding are not the selected message contract. Conflicting metadata cannot reinterpret validated text. |
| Parser state and all tokenizer states; 142600–145854 | Attribute duplicates and character-reference recovery need parser diagnostics. A final DOM cannot reveal every competing source value. |
| Tree construction, all insertion modes, formatting recovery and foreign content; 145855–150637 | Filter the recovered namespace-aware tree. Even elements that will be removed can affect parsing first. |
| Parser completion, speculative parsing and recovery examples; 150638–151377 | Parsing must have no script execution, custom-element upgrades or resource loading. Merely calling a browser parser “inert” is insufficient evidence of these properties. |
| Serialization and fragment parsing; 151378–151931 | Reusing markup in a different context can change its tree. Constructing the isolated host DOM and serializing a standalone preview are different boundaries. |
| Named-reference table description; 151939–151976 | The generated entity table is a separate data dependency; its mapping comparison is reported below. |

The retained-element review covers headings, paragraphs, quotation, lists, description lists, inline semantics, breaks, tables and their grid/header model. It also covers selected image alternative-text and dimension rules, advisory titles, inline styles and integer attributes. The exact per-element source ranges are retained in the private review ledger. General image fetching, author scripting APIs and the rest of the platform are outside this scoped review.

## Preserve meaning through projection

`em` and `strong` retain emphasis and importance; `i` and `b` have different semantics. Likewise, `s` marks content that is no longer relevant, while `del` marks a document removal. These distinctions survive even when client styling makes them look similar.

List order, starting values, explicit item values and reversed numbering matter. Table headers, row groups, column groups and spans establish relationships beyond their visual borders. The profile's restricted integer spellings and span limits are deliberate profile choices. In particular, HTML also permits `rowspan="0"` and row spans above 1000; this profile does not. It must not describe those exclusions as HTML requirements.

Image `alt` text replaces the image; `title` supplies supplementary information. Neither title tooltips nor image availability can be the only way to obtain required instructions. Direction and language have their own [reviewed projection rules](html-direction.md).

## Preview serialization corrections

HTML consumes one immediate leading line feed in a `pre` element. The standalone preview serializer now adds one compensating line feed when the projected `pre` text begins with one. It does not add one before a child element or to ordinary paragraphs.

A carriage return introduced by a character reference survives HTML parsing. Writing that return literally into a new HTML document would turn it into a line feed on the next parse. The preview serializer now writes carriage returns as numeric references in text and attributes. Escaping still preserves a literal ampersand sequence as text.

Eighteen focused serializer and tree tests pass, including exact roundtrips for leading preformatted line feeds and carriage returns adjacent to line feeds and ampersands. This evidence concerns the standalone preview boundary; the isolated browser host constructs its message DOM separately.

The separately captured [named-reference JSON](https://html.spec.whatwg.org/entities.json) contains 2,231 entries. Every name and decoded character sequence matches the html5lib 1.1 entity map; code-point arrays also match their character strings. Its SHA-256 is `d741d877ac77c4194c4ad526b5b4a19aef8dfe411ab840a466891cdbb9f362e6`. This exhaustive data comparison does not execute every tokenizer context.

## Implementation boundaries

The established parser adapters are not certified against every rule in this source revision. The captured standard includes newer select and processing-instruction behavior, so a package version alone cannot establish agreement. Eleven focused fixtures compare html5lib 1.1 with Chromium 153.0.8010.12. Three raw select trees differ, but those differences are confined to discarded select content; all eleven filtered trees agree. The processing-instruction cases use legacy comment recovery in both engines, including a quoted `>` case that differs from the newer source algorithm. Agreement between these engines therefore does not establish conformity to every rule in the captured revision. Broader malformed-formatting, table, foreign-content and serialization cases remain outside this corpus.

The default html5lib experiment refuses template and noscript contexts that it cannot safely project, and retains duplicate-attribute diagnostics. Its node and depth checks occur after parsing; they do not establish a bound on parser allocation.

Effective advisory titles survive removed wrappers and the `html`/`body` boundary. Explicit empty titles cancel inherited advice. Bare text receives an inert title-bearing span when needed; whitespace alone does not create invalid table children. Discarded subtrees do not contribute titles, and trailing text retains its original parent context. Focused tests include exact preview roundtrips. Host DOM insertion behavior, image decoding and assistive-technology output remain separate implementation checks. None of these limitations changes the recorded source-reading scope into a whole-platform conformance claim.
