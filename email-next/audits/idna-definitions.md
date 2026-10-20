---
title: IDNA domain-label definitions
sectionNav: true
---

# IDNA domain-label definitions

[RFC5890](https://www.rfc-editor.org/rfc/rfc5890.html) distinguishes a valid A-label from an ASCII string that merely starts with `xn--`. Email Next's discovery and service-origin profiles require validated labels; the current experiments' refusal of A-label hosts remains an implementation limitation.

## What validation means

An A-label is a complete ASCII label that decodes to a valid Unicode U-label and can be reproduced from that U-label. The U-label contains at least one non-ASCII character, is already in NFC, and meets the character, context and bidi requirements. Punycode decoding alone does not establish those properties.

The encoded label must satisfy the 63-octet DNS limit, including the four-octet prefix. U-label storage must allow expansion rather than assuming the ASCII byte length. Other reserved LDH labels with hyphens in positions three and four are not ordinary NR-LDH labels for IDNA-aware processing. Underscore service labels belong to a different naming convention.

Compare A-labels with ASCII case-insensitive comparison; compare validated U-labels exactly. Generation uses lowercase A-labels, consistent with Email Next's narrower canonical domain spelling. Neither comparison nor successful DNS resolution proves ownership. Visual resemblance remains a display-security problem.

IDNA applies to domain-name slots. It does not normalize email local parts, arbitrary message text, identity proofs or authenticated event bytes. NFC validation of a decoded domain label is not permission to normalize the enclosing record.

## Corrections and coverage

The complete 23-page source, figures, references and end matter were reviewed. Seven captured errata matched the live full-record listing on 20 October 2026:

| Status | IDs | Disposition |
| --- | --- | --- |
| Verified | 4695, 4696 | Correct the U-label expansion discussion from characters to octets; do not repeat the erroneous 252-character claim. |
| Verified | 7291 | Records that RFC5890 updates RFC4343; current metadata includes this relationship although the original front matter omits it. |
| Held for Document Update | 4823, 4824 | Proposed tighter expansion bound is not adopted as a new application limit. Validate the actual encoded-label limit and bound allocations independently. |
| Held for Document Update | 5484 | Cross-reference clarification, not a different label grammar. |
| Reported | 9026 | Clarifies that Protocol/Tables references mean RFC5891/RFC5892. No new protocol rule. |

Retrieved metadata lists no later update or replacement. This definitions review does not complete [protocol validation](idna-protocol.md), the derived-property/bidi/Punycode dependencies, Unicode data selection or DNS case-comparison review. No runtime behavior or test result is claimed.

Base-text SHA 256: `24d27002e26fedaec6c9f6479547e9d0855d952bc47d6ce1000851efd70b7430`. Exact reading ranges and section dispositions are retained in the review ledger.
