---
title: IDNA validation and lookup
sectionNav: true
---

# IDNA validation and lookup

[RFC5891](https://www.rfc-editor.org/rfc/rfc5891.html) separates registration from lookup. Email Next's requirement for a validated A-label must not be satisfied by merely accepting an opaque `xn--` string under the protocol's more permissive lookup options.

## Applying the protocol

Full label validation checks NFC, prohibited and unassigned code points, hyphen placement, leading combining marks, contextual conditions and applicable bidi rules. A valid U-label and its A-label must round-trip. A domain combines independently encoded labels under the applicable DNS and application length rules.

Registration checks both CONTEXTJ and CONTEXTO conditions. Lookup requires CONTEXTJ evaluation, but may check only that a CONTEXTO rule exists; lookup bidi checking is a SHOULD with stated exceptions. RFC5891 §5.3 also permits opaque handling of apparent A-labels. These allowances explain why ordinary lookup success is weaker evidence than complete A-label validation. They are not an exemption from Email Next's expressly selected validated-label contract.

The Unicode unassigned list must match the version used for the other validation requirements. This differs from ordinary event text, where an unassigned scalar is not malformed UTF-8. IDNA's NFC requirement is scoped to domain labels; it does not introduce message normalization or local-part case folding.

The protocol leaves local input preparation outside its core and does not mandate a compatibility mapping. This review selects neither UTS46 nor an IDNA2003 fallback. Browser navigation and service/certificate domain validation retain separate parsing contracts.

## Remaining dependencies

| Source | Required scope before claiming complete validation |
| --- | --- |
| RFC5892 and its metadata-listed update RFC8753 | [Character/context rules](idna-properties.md) and [Unicode review procedure](idna-unicode-review.md) reviewed; selected Unicode data and later review records remain open. |
| RFC5893 | [Bidi domain/label rules](idna-bidi.md) reviewed; selected Bidi_Class data and Unicode algorithm provenance remain open. |
| RFC3492 | [Punycode algorithms](punycode.md), failure/overflow and round-trip behavior reviewed. Runtime/data validation remains separate. |
| Unicode normalization and character properties | Pin the chosen NFC/property data and applicable rules, including combining-mark definitions. No new data version is selected here. |
| DNS sources and RFC4343 | Label/domain wire constraints and ASCII case equivalence, scoped to reached behavior. |

RFC5894 provides rationale; optional mapping guidance does not silently become a mandatory preprocessing profile. Registry-specific acceptance policies are separate from client validation.

## Review evidence

All 17 source pages, including the IDNA2003 comparison appendix, references and end matter, were reviewed. Held erratum3969 matched the live record on 20 October 2026: it questions the combining-mark definition reference. Its verifier calls for broader clarification; it does not remove the leading-mark prohibition.

Retrieved metadata records replacement of RFC3490/RFC3491, an update to RFC3492, and no later update or replacement. No IDNA implementation or interoperability tests were run. Current experimental A-label refusal remains in place while these dependencies and their data-version contract are completed.

Base-text SHA 256: `c9b898f6214c2241b25e4697d6b928ea805099bb136f0e92c48a531490672cda`. Exact reading ranges and section dispositions are retained in the review ledger.
