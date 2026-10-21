---
title: IDNA Unicode 6 review
sectionNav: true
---

# IDNA Unicode 6 review

[RFC6452](https://www.rfc-editor.org/rfc/rfc6452.html) records the decision to accept three Unicode6 property changes without adding exceptions to RFC5892. It explains why derived-label validity depends on the chosen Unicode data release.

The two Kannada signs U+0CF1 and U+0CF2 changed from symbols to letters and therefore from DISALLOWED to PVALID. New Tai Lue Tham digit one, U+19DA, changed from a decimal digit to another numeric category and therefore from PVALID to DISALLOWED. The underlying IDNA calculation was unchanged.

This decision applies to those changes. It does not authorize every future property change, select Unicode6 for Email/2, or allow a validator to mix data versions. Later review follows [RFC8753](idna-unicode-review.md).

## Evidence

The complete four-page source, references and end matter were reviewed. Retrieved metadata lists no update or replacement. The direct live errata listing contained no records on 20 October 2026. No property table was recalculated and no implementation tests were run.

Base-text SHA 256: `3ef89afc6f34f25b3d9c013a4c136f4a632b59aa05ad31e8a29322dc7cf47605`. Exact LF-based reading ranges and section dispositions are retained in the review ledger.
