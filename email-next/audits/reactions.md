---
title: Email reactions audit
sectionNav: true
---

# Email reactions audit

**Coverage:** complete RFC9078 and zero matching errata in refreshed dataset, checked19October2026. Status is Experimental. [Source](https://www.rfc-editor.org/rfc/rfc9078.html).

| Section | Disposition |
| --- | --- |
| 1 | Existing reaction semantics, not arbitrary emoji in prose. |
| 2 | Unicode sequence grammar distinct from ABNF; dependency version must be fixed. |
| 3 | text/plain UTF-8, one emoji line, outer body or first multipart part. Invalid candidates may be handled individually; unsupported code points remain displayable placeholders. |
| 4 | Known In-Reply-To target needed; outer-level processing. Wording permits a wider part search than§3placement; generate firstpart and retain ambiguity for received later parts. Nested messages processed independently. |
| 5 | Audience and repeated-reaction UX unspecified; proposal must define them. |
| 5.1 | Example has invalid date and unbracketed IDs; do not copy into fixtures. |
| 5.2 | Displays explicitly untested; no usability evidence claimed. |
| 6 | Social engineering and special processing risks acknowledged; no authentication supplied. |
| 7 | Reaction is used as disposition type despite parameter wording; current registry verification open. |
| 8 | Experimental goals reviewed; publication does not establish adoption. |
| 9 | All normative dependencies reviewed as references; Unicode and architecture audits remain open. |
| Closing | Acknowledgements, contacts and front matter reviewed. |

## Proposed use

Reuse the existing disposition for a legacy-compatible reaction projection. Keep the original message immutable; removal for presentation is a derived view. A reaction is not a form answer or transaction approval. Do not turn an unauthenticated reaction into an authenticated contribution merely because the target is known.

Generate exactly one target and place the reaction first. Include readable explanatory text separately when useful. Unsupported clients may show an attachment or ordinary reply; invisibility is not promised. Removal and replacement semantics need explicit structured events, because this source does not define them.

The [reaction message example](../examples/reaction.eml) uses corrected message syntax and a base64-encoded UTF-8 thumbs-up followed by a readable text part. Its local parser check verifies structure and decoded content, not actual mail-client rendering or end-to-end protection.
