---
title: CSS numbers and length units
sectionNav: true
---

# CSS numbers and length units

The sender vocabulary is narrower than CSS. A valid CSS number, unit or equivalent spelling is not automatically a permitted message style. The [presentation profile](../presentation-profile.md) remains the exact allowlist.

The selected source is [CSS Values Level 3, 22 March 2024](https://www.w3.org/TR/2024/CRD-css-values-3-20240322/), a Candidate Recommendation Draft. Reviewed sections cover numeric types, range rejection, dimensions, percentages, lengths, `em`, `rem` and `px`. This is a scoped review, not adoption of every feature in that draft.

`rem` follows the root font size. `em` normally follows the element's font size; on `font-size`, it follows the parent's. Percentages use the reference defined by their property. A CSS pixel need not equal one physical display pixel. Unsupported values are rejected rather than approximated into the sender allowlist.

## Execution evidence

The client baseline check exercises root sizes of 16 and 24 CSS pixels, nested text, root-relative margins, inherited unitless line spacing and the host's percentage-limited pixel canvas. It passes in Chromium 153.0.8010.12. The canvas is client-owned; sender canvas remains prohibited.

Run `css-values-browser-test.mjs` with `EMAIL_NEXT_PLAYWRIGHT_MODULE` set to the installed Playwright module. These checks do not establish other-engine behavior, physical display scaling, native zoom or complete layout conformance. Property-specific percentage rules and the remaining layout modules require their own review.
