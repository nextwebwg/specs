---
title: Security gateways audit
sectionNav: true
---

# Security gateways audit

**Coverage:** complete six-page RFC2480; zero errata in refreshed dataset. [Source](https://www.rfc-editor.org/rfc/rfc2480.html). Metadata checked19October2026 lists no updates or replacements.

| Section | Disposition |
| --- | --- |
| 1 | Scope: security multiparts crossing non-MIME gateways. |
| 2 | Requirement vocabulary reviewed. |
| 3 | Whole-object protection, format conversion and end-to-end security can conflict. |
| 4 | Gateways provide unchanged tunneling where MIME support is possible and signed-content conversion with invalid-signature warning; per-user selection recommended. Gateway cryptography is optional and disabled by default. |
| 5 | Security considerations cover the whole document. |
| 6 | MIME dependencies reviewed separately; host requirements remain open. |
| 7 | Author information reviewed. |
| 8 | Copyright terms reviewed. |

## Email/2 decision

Preserving signed content and converting it are distinct modes. Email/2's protected route requires unchanged carriage. A conversion route must report lost protection and satisfy the sender's fallback policy; gateway compliance alone does not establish end-to-end confidentiality.

Test unchanged tunneling, intentional conversion, invalid-signature presentation and disabled-by-default gateway cryptography. No gateway implementation has been tested.
