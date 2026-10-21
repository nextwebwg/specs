---
title: Selected inline alignment and spacing audit
order: 221
blurb: baseline alignment · inherited ratios · client preferences
sectionNav: true
---

# Selected inline alignment and spacing audit

A unitless line height remains a ratio when inherited. It must not be frozen into the parent’s pixel height before a larger child inherits it.

## Source and coverage

This review covers lines 650–940 and 946–1029 of [CSS Inline Layout Level 3 at revision 40527902c4d0840cdb7a808c8cd42302be1c3bc8](https://github.com/w3c/csswg-drafts/blob/40527902c4d0840cdb7a808c8cd42302be1c3bc8/css-inline-3/Overview.bs): the selected baseline metrics, vertical-align and its constituent properties, plus the line-height definition, inheritance example and inline-decoration warning. This Editor’s Draft review does not adopt its other properties or establish complete inline layout conformance.

Source SHA-256: `50efdb1b5d179ea9aafc558ce5a650aba8066ff612aeb89f8e7abaabc06487e3`.

## Selected behavior

| Value | Consequence |
| --- | --- |
| Unitless number | Inherits as a number; each element uses its own font size |
| normal | Uses font metrics; no fixed multiplier is promised |
| Length or percentage | Different inheritance behavior; excluded from sender line-height values |

Line height contributes to line-box sizing; it is not a clipping boundary. Inline borders, padding and backgrounds can overlap adjacent lines. Their visual interaction still needs coverage.

## Selected alignment behavior

The permitted vertical-align values retain their CSS meaning. For inline content, baseline follows the parent’s dominant baseline; middle uses the x-middle baseline in ordinary horizontal text. It does not mean “center this content in its container.” Top and bottom align the aligned subtree to the corresponding line-box edge.

The property is not inherited. A parent’s alignment does not become the child’s specified alignment, although the parent’s position still affects its contents. The draft’s additional longhands and values are not admitted by the Email/2 allowlist.

Table-cell alignment is a separate layout case. The reviewed source maps top, middle and bottom to table-cell content alignment when align-content is normal; it does not justify using the inline x-middle calculation for table cells. The subsequent [table/box audit](css-table-box.md) covers CSS2.1 §17.5.3 baseline and row sizing; browser-dependent portions of that model remain as documented there. The source also retains open issues around vertical writing and the allocation of line-relative values to longhands; no resolution is inferred here.

## Inline boxes can have several fragments

A wrapped `span` still belongs to one inline box. Its fragments do not acquire fresh padding and borders at every line break: the unselected `box-decoration-break` property retains its initial `slice` behavior. Bidirectional reordering can also separate fragments within one line. Their edge decorations follow visual order and the parent’s direction. This is relevant to the existing sender spacing and background vocabulary; it adds no fragmentation controls. [CSS2.1 inline formatting](https://www.w3.org/TR/2011/REC-CSS2-20110607/visuren.html#inline-formatting), [CSS Fragmentation3§5.4](https://www.w3.org/TR/2018/CR-css-break-3-20181204/#break-decoration), [WritingModes4§2.4](https://www.w3.org/TR/2019/CR-css-writing-modes-4-20190730/#bidi-algo).

The [focused host geometry check](../evidence/README.md#inline-fragments-and-bidirectional-text) passes four cases in Chromium 153.0.8010.12: two widths and both parent directions. It checks wrapping, slice edge placement, opposite-direction span fragmentation, isolation and combining-pair line membership. Rectangle measurements do not establish painted border continuity, glyph mirroring or full bidirectional conformance. Pagination, columns and excluded decoration features remain outside this selection.

## Implementation evidence

The [browser host](../evidence/README.md#isolated-browser-rendering) checks inherited ratios with different font sizes and a client-owned spacing override. Invalid preferences preserve the existing view; omission restores sender and baseline styles. This Chromium evidence does not establish vertical-alignment geometry, mixed-script, decoration-overlap or assistive-technology behavior.
