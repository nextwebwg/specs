---
title: Sieve body matching audit
sectionNav: true
---

# Sieve body matching audit

Complete RFC5173 read; no errata in refreshed dataset on19October2026. [Source](https://www.rfc-editor.org/rfc/rfc5173.html).

| Section | Disposition |
| --- | --- |
| 1 | Purpose reviewed. |
| 2 | Argument ordering inherited. |
| 3 | Capability body. |
| 4 | Header-only message yields no matches. |
| 5 | Default text transform. |
| 5.1 | Raw body, undecoded. |
| 5.2 | Recursive per-part matching; no cross-part match; decoded octets. |
| 5.3 | Best-effort text is implementation-dependent. |
| 6 | No wildcard match-variable assignment. |
| 7 | Registration reviewed. |
| 8 | Resource bounds; matches are not security validation. |
| 9 | Acknowledgements reviewed. |
| 10 | References reviewed. |
| 10.1 | Base Sieve/MIME dependencies open. |
| 10.2 | Variables update tracked. |
| Closing material | Contacts, copyright and IPR reviewed. |

## Proposed consequence

Body matching cannot authenticate a control message. A sender can imitate visible markers. Recipient-configured filtering remains separate from validated protocol processing. Best-effort extracted text must not define signed bytes or structured-event identity.
