---
title: Selected CSS font properties audit
order: 220
blurb: generic families · inherited values · user preferences
sectionNav: true
---

# Selected CSS font properties audit

The profile's four font properties form a deliberately narrow CSS subset. They do not guarantee a particular installed font, glyph coverage or identical appearance across platforms. The admitted values match the selected property definitions; rendering and preference coverage remain separate.

## Source and coverage

This scoped review uses [CSS Fonts Level 4 at revision 40527902c4d0840cdb7a808c8cd42302be1c3bc8](https://github.com/w3c/csswg-drafts/blob/40527902c4d0840cdb7a808c8cd42302be1c3bc8/css-fonts-4/Overview.bs), an Editor's Draft. It covers 1,146 lines across the following ranges, including textual examples. Embedded specimen images were not inspected and support no appearance claim here.

| Lines | Reviewed scope |
| --- | --- |
| 1–55 | Source metadata |
| 87–428 | Introduction, value conventions, family definition and grammar |
| 478–650 | Selected generic families and partial system-ui discussion |
| 855–1035 | Weight definition and missing-weight behavior |
| 1208–1602 | Style and size definitions and textual examples |

Source SHA-256: `33f3137b356687cc08d2500366125c6f28325a1535fd77a23ebb9f4983c74cd9`. Complete matching, cluster shaping, synthesis controls, variable fonts, font loading, CSSOM serialization and the module's security/privacy appendices are outside this review. The [cascade audit](css-cascade.md) separately covers inheritance and override precedence.

## Inherited behavior and selected restrictions

| Property | CSS behavior | Email/2 selection |
| --- | --- | --- |
| font-family | Inherited; generics can map to different fonts by language, platform and preferences. Quoted names are distinct from unquoted generics. | One of serif, sans-serif or monospace for sender content; no named fonts, lists or quoted family names |
| font-weight | Inherited; normal corresponds to 400 and bold to 700. Missing faces can require fallback or synthesis. | Normal, bold, literal 400 or literal 700 |
| font-style | Inherited; italic may use an oblique fallback and does not guarantee a particular slant or authentic italic face | Normal or italic |
| font-size | Inherited; scales the font's EM and computes to an absolute length, but does not fix visible glyph height | The profile's seven explicit rem values |

Generic monospace does not guarantee equal widths for every fallback glyph or cluster across scripts. Preserve language metadata and allow the renderer to resolve missing glyphs. The client baseline's heading sizes, sans-serif body, monospace code and emphasis defaults are profile choices, not mandated CSS typography.

The rem values and the baseline's em and percentage values also depend on CSS Values and Units. Computing an absolute size is not permission to replace user-relative sizing with fixed pixels before preferences apply. Glyph ink can extend beyond the EM box; a size limit alone does not establish containment.

## Implementation boundary

The declaration filter admits the selected families, styles, weights and size spellings. No additional value-admission mismatch was found by source inspection. This review ran no new tests and does not establish visual conformance.

The [browser host](../evidence/README.md#isolated-browser-rendering) implements an optional generic font preference on all descendants using client-owned important rules. Its system-ui option belongs to client configuration and does not broaden the sender vocabulary. Arbitrary named fonts, native zoom and complete mixed-script fallback remain unverified.

The host now exposes an optional client-owned root-size preference. Its Chromium checks exercise nested `rem` sizes and spacing without compounding, inherited text, preference changes, reset and overflow containment; [the experiment notes](../evidence/README.md#isolated-browser-rendering) give the API and adjustable defaults. Omission still uses the browser’s initial root size. Minimum-font restrictions, native zoom, mixed-script fallback and assistive-technology behavior remain unverified; these focused checks do not establish complete presentation support.

## Selected length-unit rules

The [CSS Values and Units Level 4 source at the same revision](https://github.com/w3c/csswg-drafts/blob/40527902c4d0840cdb7a808c8cd42302be1c3bc8/css-values-4/Overview.bs) defines the units used by the profile. This additional scoped review covers lines 1875–1930 (font-relative introduction, em and rem), 2078–2138 (resolution and user restrictions), and 2429–2547 (absolute units and the reference pixel): 236 source lines. The first range includes the opening of the ex definition without reviewing that unit in full. Image assets and referenced tests were not inspected or run.

Source SHA-256: `2004252d1473a1b6b3d72f0a7fcda4ff4e6821d774a1f4d7c0dc82ba220cdf46`. This is a selected-source review, not a complete Values and Units audit.

| Unit or preference | Consequence for this profile |
| --- | --- |
| rem | Resolves from the root element's computed font size. Nested sender font sizes do not compound rem spacing or sizes. The isolated message document therefore needs the client's chosen root size. |
| em in client-owned defaults | Resolves from the element's computed font size, with parent/initial metrics used where required to avoid circular font-size dependencies. It is not an additional sender-authorized unit. |
| px | Denotes a CSS pixel, not necessarily one device pixel. Accepted border widths do not promise identical physical thickness across screens or zoom levels. |
| Minimum-font restrictions | Apply to used values without changing font-relative unit resolution in properties. Increasing a minimum readable size is distinct from selecting the root font size. |

These rules do not authorize replacing relative dimensions with fixed device-pixel values. The profile still requires effective user font and zoom preferences. Percentage resolution, other relative units, mathematical functions and the remainder of the module are outside this scoped review. Browser checks must separately establish root-size propagation, nested rem behavior and containment when user preferences enlarge text.
