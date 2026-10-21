---
title: Punycode domain encoding
sectionNav: true
---

# Punycode domain encoding

[RFC3492](https://www.rfc-editor.org/rfc/rfc3492.html) defines the reversible encoding used inside an A-label. Successful Punycode decoding is not proof of a valid internationalized domain: scalar validity, NFC, character/context/bidi rules, the `xn--` prefix and DNS length limits belong to the surrounding [IDNA validation](idna-protocol.md).

## What the encoding preserves

Punycode copies basic ASCII characters in their original order and represents other code points with an adaptive sequence of integer differences. Its parameters are fixed; generic Bootstring alternatives are not additional Email/2 encodings. Input consists of code points, not UTF-16 code units.

A decoder recognizes uppercase and lowercase forms of encoded digits. Literal ASCII case is copied; optional mixed-case annotations are separate from the decoded code points. Those annotations are not used by IDNA. Email/2's canonical lowercase A-label spelling remains a higher-layer requirement, not evidence that all the RFC's mixed-case examples are erroneous.

## Fail safely

The decoding procedure rejects invalid digits, premature end of input and arithmetic overflow. Output allocation and Unicode scalar checks remain necessary. The source discusses delayed overflow detection by re-encoding within the older IDNA ToUnicode pipeline; that is not permission to expose unchecked intermediate output or use unsafe arithmetic. Complete A-label validation retains its own round-trip and validity checks.

The original references to Nameprep describe IDNA2003. RFC5891 updates the surrounding protocol; this review does not restore Nameprep, add UTS46 mapping or normalize authenticated bytes. The sample wrapper's buffer sizes are examples, not Email/2 limits.

## Evidence and errata

All 35 pages were read, including the examples, both encoding/decoding traces, license, complete C sample and test wrapper. None was compiled or executed. Retrieved metadata lists RFC5891 as the update and no replacement.

The direct live listing matched three captured records on 20 October 2026:

| Status | Record | Treatment |
| --- | --- | --- |
| Verified | 265 | Use the corrected definition of `maxint`: the integer variable's maximum value. |
| Held for Document Update | 3026 | Russian example's encoded annotation case is questioned; not a changed decoding algorithm or executed vector result. |
| Rejected | 9167 | Proposed lowercasing of the Czech example's literal `P` is not adopted. |

No runtime behavior or IDNA implementation conformance is established by this source review.

Base-text SHA 256: `d1848b1b4f01e20708a64f42394e5f4b840141935bed7f09ad7baeb6693b8772`. Exact LF-based reading ranges and section dispositions are retained in the review ledger.
