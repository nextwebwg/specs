---
title: CSS cascade and inheritance audit
order: 219
blurb: inline precedence · protected overrides · inheritance
sectionNav: true
---

# CSS cascade and inheritance audit

Normal sender inline styles override normal client stylesheet rules. Enforcing user preferences therefore requires rules that actually outrank those declarations on the affected elements. A later stylesheet, named layer or parent-only preference does not establish that behavior.

## Source and coverage

This scoped review uses [CSS Cascading and Inheritance Level 5 at revision 40527902c4d0840cdb7a808c8cd42302be1c3bc8](https://github.com/w3c/csswg-drafts/blob/40527902c4d0840cdb7a808c8cd42302be1c3bc8/css-cascade-5/Overview.bs), an Editor's Draft. It covers 1,146 source lines in seven ranges. It does not adopt the complete draft or claim browser conformance.

| Source lines | Reviewed behavior |
| --- | --- |
| 1–123 | Scope and module interactions |
| 318–386 | Shorthand expansion |
| 444–729 | Reset boundaries and value processing |
| 900–1303 | Filtering, cascade order, origins, importance and layers |
| 1509–1615 | Layer ordering |
| 1742–1875 | Presentational hints, defaulting and inheritance |
| 2208–2230 | Privacy and security considerations |

The source SHA-256 is `c2433a793927a74ae8583760ead21494de32a89a3bdd0222cbdb95f4ab900298`. Imports, layer syntax, rollback keywords, property aliases and fragmentation are outside this review. Individual property modules remain separate dependencies.

## Consequences for the profile

| Source rule | Profile consequence |
| --- | --- |
| Unsupported declarations do not supply a declared value | A rejected later declaration leaves an earlier accepted value available |
| Shorthands expand to longhands in place | The current filter's per-name selection depends on excluding independently accepted overlapping longhands; adding them requires ordered expansion |
| Origin and importance precede specificity and source order | Last-valid selection is only one stage, not a complete cascade |
| Inline declarations beat same-importance selector rules | Normal client styles cannot enforce accessibility preferences against sender inline styles |
| User-important rules outrank author-important rules | Client-owned important rules can defeat sender declarations, whose important flag is prohibited, while preserving genuine user-important precedence |
| Inheritance applies when no cascaded value is supplied | A parent font/color preference cannot replace a child's explicit value; enforced preferences must reach affected descendants |
| Children inherit computed values | Preserve projected parent relationships rather than copying raw style strings |
| Initial values differ from HTML user-agent defaults | A blanket reset can remove native display behavior and is not a complete isolation policy |

The [presentation profile](../presentation-profile.md#client-owned-baseline-styles) requires effective accessibility overrides. That is stronger than ordinary normal-origin CSS precedence. The renderer must implement this requirement explicitly.

## Implementation boundary

The declaration filter performs admission and last-accepted selection; the browser computes the cascade, inheritance and layout. The baseline stylesheet and inert serializer alone do not implement protected overrides.

The separate [browser host](../evidence/README.md#isolated-browser-rendering) applies important client rules to descendant colors in forced-colors mode, link affordances and image bounds. It also provides an optional all-descendant generic font preference. Named/custom fonts and other user preferences remain incomplete. Its Chromium checks do not establish other engines, genuine user-origin stylesheet behavior, native zoom or assistive-technology support.

Font, color, text, decoration, writing-mode, box, table and logical-property definitions still require their selected semantics to be reviewed. This audit does not close those dependencies.
