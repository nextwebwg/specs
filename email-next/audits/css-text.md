---
title: Text wrapping and alignment
sectionNav: true
---

# Text wrapping and alignment

Wrapping changes presentation, not the retained message text. The profile permits `normal` and `pre-wrap` whitespace handling; neither permits a renderer to rewrite authenticated content.

[CSS Text Level 3](https://www.w3.org/TR/2026/CRD-css-text-3-20260814/) defines the selected whitespace, overflow-wrapping and alignment rules. `normal` collapses display whitespace. `pre-wrap` preserves spaces and line breaks while allowing wrapping; trailing spaces can hang outside the measured line. Preserved tabs follow tab stops.

`overflow-wrap: anywhere` permits emergency breaks without inserting hyphens or splitting grapheme clusters. `normal` can leave a long word unbroken. Clients must keep that overflow reachable inside the message view. Logical `start` and `end` follow text direction; alignment is relative to the line box, not the application window.

DOM carriage returns and line feeds are distinct: CSS treats carriage returns like spaces. A preview serializer must preserve that distinction when reparsed.

## Inherited layout choices

Preserved tabs use the initial `tab-size: 8`: eight space advances from the nearest block container, including its spacing. This is a font-relative measure, not eight literal spaces inserted into the message. Hanging trailing glyphs do not contribute to the same measurements as ordinary glyphs; conditionally hanging whitespace contributes to max-content but not min-content sizing. [CSS Text §§4.2 and 8.2](https://www.w3.org/TR/2026/CRD-css-text-3-20260814/#tab-size-property).

The selected defaults retain `word-break: normal`, `line-break: auto` and manual hyphenation. Languages can require dictionaries or orthographic analysis. CSS requires a fallback when the browser lacks that analysis, and requires joining forms to survive emergency breaks within shaping scripts. Inline boundaries do not themselves create break opportunities. Shaping must continue across boundaries with no effective formatting change, but must break at specified boundaries such as bidi isolation or nonzero inline-axis padding. [CSS Text §§5 and 7.3](https://www.w3.org/TR/2026/CRD-css-text-3-20260814/#line-breaking).

The profile inherits CSS's documented discretion. It does not require identical line breaks or glyph shapes across fonts and engines. In particular, CSS Text Level 3 leaves which element's `overflow-wrap` controls a break opportunity between boxes undefined. Nested inline styles remain supported; this uncertainty does not authorize rewriting text, splitting a typographic character unit or hiding overflow. [CSS Text §5.5](https://www.w3.org/TR/2026/CRD-css-text-3-20260814/#line-break-details).

## Evidence and remaining scope

The browser-host check uses a narrow frame to compare emergency wrapping with unbroken-word overflow, preserves preformatted text, and checks keyboard scrolling inside a labeled message region. The host retains its fixed width.

This scoped source review does not establish every language's line-breaking behavior. Selected tab metrics, cross-element shaping constraints and hanging measurements are covered above. The [inline/bidi review](css-inline.md) covers the selected bidi interaction. The selected Unicode break/segmentation rules and intrinsic-size definitions are mapped below. Native assistive-technology behavior and complete cross-engine layout remain execution boundaries. The source itself leaves some segment-break transformations to browsers; identical line endings across all engines are not promised.

::: {.details summary="Selected source mapping and version boundaries"}

### Unicode layout dependencies

CSS Text §1.4 requires extended grapheme clusters as the basis for typographic character units, with operation-specific tailoring. A cluster divided by markup can have implementation-dependent rendering. This is distinct from authorizing a soft break inside the resulting typographic unit.

The captured layout references are [UAX #14 revision 57](https://www.unicode.org/reports/tr14/tr14-57.html) and [UAX #29 revision 49](https://www.unicode.org/reports/tr29/tr29-49.html), both for Unicode 18. They do not replace the separately pinned Unicode 17 IDNA or bidi evidence, or establish which Unicode version a browser implements.

| Source selection | Disposition for this renderer |
| --- | --- |
| UAX #14 §§4–4.1 | Distinguish default conformance, tailoring and higher-level overrides. CSS whitespace and emergency wrapping supply higher-level behavior. The algorithm identifies opportunities, not the final width-dependent choice. |
| UAX #14 §6, LB1–LB31; §8–8.1 | Reviewed ordered rules, combining sequences, hard breaks, joiners, spaces, punctuation, numbers, syllables and emoji sequences. Tailoring is explicit; no independent line-break engine is implemented here. |
| UAX #29 §2; §§3.1–3.1.1, GB1–GB999 | Reviewed extended-cluster properties and ordered rules, including controls, Hangul, combining marks, Indic conjuncts, emoji joiners and regional indicators. Word/sentence segmentation is not selected merely because it shares this source. |
| Unicode 18 property data | Captured LineBreak, GraphemeBreakProperty, DerivedCoreProperties, emoji-data, EastAsianWidth and UnicodeData files. They identify algorithm inputs; capture does not validate every property assignment or a browser's internal tables. |

The captured Unicode 18 errata index lists no current errata. This is a dated observation, not a permanent guarantee. Language dictionaries and optional locale tailorings are browser dependencies; this profile does not select a complete CLDR implementation.

### Intrinsic measurements

[CSS Sizing Level 3, 4 September 2026](https://www.w3.org/TR/2026/WD-css-sizing-3-20260904/) §§2.1–2.3 and 5.1–5.2.1 define the selected min/max-content concepts, outer-size contributions and cyclic percentages. Min-content normally considers all permitted soft wraps; max-content normally considers none. Hanging whitespace and emergency-wrap rules modify those measurements as specified by CSS Text. Cyclic percentage contributions are treated separately from final used sizes; a percentage does not acquire a definite basis merely because it appears in an accepted declaration.

The sizing source delegates detailed float/display layout and explicitly does not fully specify every intrinsic-contribution calculation. The existing [layout dependency audit](css-layout-dependencies.md) and [table audit](css-table-box.md) cover the selected layout modes. Sender intrinsic-size keywords, flex and grid are not added by following these dependencies.

### Review scope

Exact snapshot hashes and inclusive source ranges are retained in the private review ledger. This is a review of the selected algorithms and their boundaries, not a complete review of Unicode, every script's shaping system, every CSS module or the platform's font implementation. No new browser execution is implied by this source mapping.

:::
