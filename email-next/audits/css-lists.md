---
title: CSS lists audit
sectionNav: true
---

# CSS lists audit

Keep native list elements and their numbering attributes. A styled paragraph with a drawn number does not preserve the same list relationships. The presentation profile permits `ol`, `ul` and `li`, including `start`, `reversed` and item `value`; it does not permit sender counter declarations, marker selectors or list images.

## Selected sources

This scoped review combines the [17 November 2020 CSS Lists Working Draft](https://www.w3.org/TR/2020/WD-css-lists-3-20201117/), the [pinned Editor's Draft](https://github.com/w3c/csswg-drafts/blob/40527902c4d0840cdb7a808c8cd42302be1c3bc8/css-lists-3/Overview.bs), and [HTML's list rendering rules](https://github.com/whatwg/html/blob/e8393694edd92117cfb4886e2fe5dd2897374136/source). The published draft leaves reversed-counter integration unfinished; the pinned editor revision supplies the later algorithm. Neither CSS Lists document is a Recommendation. The selected native counter representations come from [CSS Counter Styles Level 3, 27 July 2021](https://www.w3.org/TR/2021/CR-css-counter-styles-3-20210727/), a Candidate Recommendation Snapshot.

| Reviewed scope | Disposition |
| --- | --- |
| List items, marker creation, inherited text properties and outside positioning | Applies to native lists in the client-owned baseline |
| Counter creation, inheritance, nesting, increments and explicit values | Explains the browser machinery behind retained list attributes; does not enable sender counter CSS |
| Reversed counter initialization and implicit decrement in the pinned editor revision | Relevant to `ol reversed`, with and without `start` |
| HTML default list styles and mappings for `start`, `reversed` and `value` | Governs the retained HTML attributes; the CSS draft's sample stylesheet is informative |
| Decimal digits, negative sign and suffix; cyclic disc/circle/square definitions | Native decimal numbering and bullets; custom styles remain excluded |
| Marker images, arbitrary strings, custom counter styling and marker-side declarations | Reviewed for their boundary; excluded from sender content |

The captured published source SHA-256 is `f898eb5b58818862a598d23d225da2ca3a58396b7bb32c9515c2cc8e31470ccf`. The pinned editor source SHA-256 is `417cec4088605d6c300de17bbac4c2be1ea4c3ce1eaf8d660672a5b91a32d902`. The Counter Styles source SHA-256 is `7d697581c3eb238c3e8d18bcf0c03aa889380041fa208c8bf06c51dd07be9807`. Exact source ranges and dispositions are retained in the review ledger.

## Consequences for the renderer

Retain nested lists and explicit numbering instead of rebuilding markers from visible text. Inherited font and color can affect marker text even though the sender cannot select `::marker`. User contrast enforcement must therefore leave markers readable as well as list content.

Outside markers occupy space beside the list item. Their interaction with overflow is partly unspecified. In the contained Chromium host, outside markers for admitted ten-digit values extended beyond the message's painted edge. The client baseline therefore selects `list-style-position: inside`, keeping the native marker in the item's inline content. Wrapped lines begin at the item content edge; a block child can follow on another line. This is a client layout choice, not an added sender property.

Decimal uses the numeric algorithm with digits zero through nine, a hyphen-minus for negative values and a full stop plus space suffix. Native bullets use a single cyclic symbol. The source permits the browser to substitute a suitable image or font for disc, circle and square, so exact glyph identity is not a cross-platform requirement. Custom counter rules, image symbols and arbitrary counter functions remain excluded.

## Executed checks and limits

The [marker runner](../evidence/README.md#native-list-markers) checks actual generated marker content and inline box bounds in the isolated host. Thirteen fixtures cover ascending and reversed lists, explicit start/value, nesting, native bullets, signed 32-bit extrema in both directions, wrapped text, block children and empty items. All 52 combinations pass in Chromium153.0.8010.12 at a 320px viewport, with 100%/200% root text and forced colors on/off. The existing nineteen host check groups also pass with the new baseline.

These checks use the browser's accessibility tree to obtain native marker text and its layout protocol to measure marker boxes. They do not establish screen-reader announcements, speech synthesis or native browser zoom. The Counter Styles speech rules distinguish spoken numeric values from unordered-list cues; actual assistive-technology behavior remains untested. Broader display/box source coverage and independent engines remain separate work. This review does not claim complete CSS Lists or Counter Styles conformance.
