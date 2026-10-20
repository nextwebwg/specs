---
title: Base encodings audit
sectionNav: true
---

# Base encodings audit

[RFC4648](https://www.rfc-editor.org/rfc/rfc4648.html) supplies the byte encodings used inside discovery and identity records. It does not replace MIME transfer encoding.

## Application to Email Next

Discovery payloads use padded base64 without whitespace. Reject alternate alphabets, misplaced padding and nonzero unused bits. MIME folding is removed by the outer transfer decoder; it is not permitted inside these JSON strings. These are the profile's existing strict decoding choices.

Hexadecimal identifiers retain the profile's lowercase spelling. No base32 field is selected. Encoding provides no confidentiality.

## Section dispositions

| Section | Disposition |
| --- | --- |
| Front matter | Scope reviewed |
| 1–2 | Terminology inherited |
| 3, 3.1–3.5 | Explicit alphabet, padding and canonical decoding |
| 4–5 | Distinguish base64 and base64url |
| 6–7 | Base32 not selected |
| 8 | Profile fixes hexadecimal case |
| 9–10 | Octet examples checked |
| 11 | External code not adopted |
| 12 | Strict decoding; no encryption claim |
| 13–16.2, end matter | History, licensing and references reviewed |

## Errata and evidence

The complete 18-page base text and six errata were reviewed. The 20 October 2026 [errata listing](https://errata.rfc-editor.org/search/?rfc_number=4648) matches the captured set: Verified 2837, 5855, 7514, 9030; Reported 4889, 8669. Verified corrections cover a reference link, input-octet interpretation and grammar. Reported changes are not adopted as corrections.

Metadata lists no successor or updates. RFC3548 is obsolete history, outside this review. Dependencies and deployed decoder behavior remain separate.
