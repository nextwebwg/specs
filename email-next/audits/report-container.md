---
title: Administrative report container audit
sectionNav: true
---

# Administrative report container audit

**Coverage:** complete nine-page [RFC 6522](https://www.rfc-editor.org/rfc/rfc6522.html), including registrations, references and end matter. No entries occur in the retrieved errata dataset. Delivery-status semantics and internationalized report extensions remain separate pending reviews.

## Finding

A report container supplies structure, not authenticity. It may be nested inside forwarded mail, so recognizing a report anywhere in a MIME tree is insufficient authority to alter the delivery state of a locally sent message.

| Section | Disposition |
| --- | --- |
| 1 | Removes the global outermost-only restriction; reports may be nested or forwarded. Individual report applications can impose their own constraints. |
| 2 | Requirement vocabulary reviewed. |
| 3 | Requires boundary and report-type. Exactly two or three ordered parts: human-readable explanation, machine report whose subtype matches report-type, optional returned content. Human part may itself use alternatives. Default full-content return recommendation and seven-bit conversion alternatives need protected-content and DSN policy reconciliation. |
| 4 | Header-only returns use text/rfc822-headers rather than representing an incomplete object as message/rfc822. Includes original fields before the blank separator, including MIME fields; quoted-printable is permitted when needed. Internationalized report extensions require separate review. |
| 5 | A new report media type should declare suitability as the second report part in its registration. No new Email/2 report type is registered here. |
| 6 | Updates multipart/report and text/rfc822-headers registrations; historic3462 is superseded. |
| 7 | Unauthenticated positive or negative reports can mislead senders or trigger denial of service. A whole-container signature is suggested, but no authentication protocol is specified. |
| 8 | Reference classification reviewed; report-container review does not complete DSN semantics. |
| 8.1 | 5322,2045 and2046 base reviews exist; registration successor6838 remains pending. |
| 8.2 | 3461 and3464 remain necessary DSN dependencies; obsolete3462 is historical context. |
| Appendix A | Acknowledgements reviewed; no normative behavior. |

| Front and end matter | Abstract, standards status, copyright and author address reviewed. |

## Email/2 consequence

Parse report structure independently from its authority. Preserve human-readable explanations, machine-readable fields and returned material as distinct components. Returned headers or content are diagnostic material, not a fresh authored contribution or a newly received interaction.

Require the relevant report profile's authentication, correlation and recipient scope before applying application effects. A forwarded report may be shown as evidence without acquiring the authority of the forwarding author. An ordinary delivery report cannot establish decryption, reading, form acceptance or membership change.

A reporting service must not decrypt protected material to generate a returned-content part. Preserve the protected representation, or use the applicable header-only reporting path when necessary. Do not place recovered plaintext or hidden recipient information into a broader report audience. The precise DSN return request and internationalized header contracts depend on the pending DSN audits.

Required cases: nested and forwarded reports, mismatched report-type, missing machine part, four-part malformed report, forged positive/negative results, returned content containing an old interaction, and a protected message returned without plaintext disclosure. No report-authentication implementation has been validated here.
