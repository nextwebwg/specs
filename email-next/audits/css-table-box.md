---
title: Table and box layout audit
sectionNav: true
---

# Table and box layout audit

The renderer keeps native tables and ordinary CSS box spacing. Permitting a property does not make it affect every element: a cell's padding creates space, but its margins do not. The presentation vocabulary remains unchanged.

## Selected sources

| Source | Reviewed scope |
| --- | --- |
| [CSS Box Model 3, 11 April 2024](https://www.w3.org/TR/2024/REC-css-box-3-20240411/) | Box edges, physical margin/padding definitions, inheritance and applicability |
| [CSS2.1 margin collapse](https://www.w3.org/TR/2011/REC-CSS2-20110607/box.html#collapsing-margins) | Adjacent block margins and the effect of separating padding/borders |
| [CSS2.1 tables](https://www.w3.org/TR/2011/REC-CSS2-20110607/tables.html), with [applicable errata](https://www.w3.org/Style/css2-updates/REC-CSS2-20110607-errata.html) | Native table structure, captions, columns, sizing, cell alignment and both border models |
| [Backgrounds and Borders 3, 11 March 2024](https://www.w3.org/TR/2024/CRD-css-backgrounds-3-20240311/) | Selected background color/painting defaults and border color, style, width and shorthand behavior |

Box Model 3 is a Recommendation and replaces the older margin/padding definitions, while retaining CSS2.1's collapse algorithm. Backgrounds and Borders is a Candidate Recommendation Draft. This is a selected-source review, not a complete audit of these modules. Exact capture hashes, read ranges and errata dispositions are retained in the review ledger.

## Spacing and borders

Adjoining positive block margins can combine to the larger margin instead of adding. Padding and borders separate content from its surroundings and can prevent parent/child margin collapse. Physical side declarations and the baseline's logical declarations address the same box sides; their mapping is covered by the [selected logical layout review](css-layout-dependencies.md).

The profile's single border value applies to every side. A border style of `none` contributes no border width. Dots and dashes retain browser-defined spacing and corner details. Background color normally paints through the border box, behind the border; margin space stays transparent. Sender images, shadows and rounded corners remain outside the vocabulary.

## Tables

The baseline uses separate borders with 2px spacing and 0.25rem cell padding. Senders may select collapsed borders. In that model, adjoining borders resolve by width, style and element precedence; it is not simply the last CSS declaration. Table padding does not create space in collapsed mode. Internal table margins and row padding do not create layout space.

Captions and retained spans continue to use native table structure. Cell `vertical-align: middle` aligns content within its row span; it differs from inline text's x-height alignment. Automatic table sizing is not fully prescribed by CSS2.1, so equal column widths or identical geometry across browsers are not promised. Wide tables retain the client's labeled, keyboard-scrollable wrapper.

## Executed checks and boundaries

The [table/box runner](../evidence/README.md#table-and-box-layout) passes eight actual-host groups in Chromium153.0.8010.12. It measures spacing, spans and alignment, and samples screenshot pixels to distinguish the winning collapsed border from a separate cell border. No implementation discrepancy requiring a change was found.

This evidence does not establish other engines, fractional display scales or assistive-technology behavior. Broader block sizing/display, logical mapping, containment/overflow and inline fragmentation remain distinct source work. Background images and other excluded features are not required merely because these sources describe them.
