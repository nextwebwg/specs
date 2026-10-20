---
title: Message-tracking response audit
sectionNav: true
---

# Message-tracking response audit

Complete eleven-page [RFC 3886](https://www.rfc-editor.org/rfc/rfc3886.html) and four retrieved errata reviewed. Metadata lists no successors. Query/model dependencies remain open.

| Section | Disposition |
| --- | --- |
| 1 | Format scope reviewed; query protocol separate. |
| 2 | Inherited DSN rules and lexical references reviewed. |
| 3 | Response body correction218 applied; related container and chaining reviewed. |
| 3.1 | Seven-bit format and block/boundary grammar reviewed;217 editorial correction applied. |
| 3.1.1 | Inherited conventions reviewed; xtext reference discrepancy recorded. |
| 3.1.2 | Typed fields reviewed. |
| 3.2 | Required singleton fields reviewed. |
| 3.2.1 | Original envelope identifier required. |
| 3.2.2 | Reporting agent required. |
| 3.2.3 | Arrival time required. |
| 3.3 | Recipient block grammar reviewed. |
| 3.3.1 | Original recipient required. |
| 3.3.2 | Final recipient required. |
| 3.3.3 | All seven actions reviewed; no identity or presence authority. |
| 3.3.4 | New status and relayed-only constraint reviewed. |
| 3.3.5 | Remote field restrictions reviewed. |
| 3.3.6 | Attempt-time conditions reviewed; do not invent an explicit opaque prohibition absent from prose. |
| 3.3.7 | Retry-time scope reviewed. |
| 3.4 | Extension inheritance reviewed. |
| 3.5 | Tracking-aware local delivery transfer reviewed. |
| 4 | Threat scope reviewed. |
| 4.1 | Server forgery reviewed. |
| 4.2 | Both forwarding privacy mechanisms and list traversal prohibition reviewed. |
| 5 | Verified216 corrects registration type. |
| 6 | Acknowledgments read. |
| 7 | References read. |
| 7.1 | Query/model dependencies remain open. |
| 7.2 | Informational dependencies reviewed. |
| 8 | Author material read. |
| 9 | Copyright, IPR and acknowledgment read. |

## Errata and unresolved references

Verified216 corrects MIME registration wording; verified217 removes an extra word; verified218 identifies a response, not a request. Held689 removes stray reference wording without changing wire behavior.

Section3.1.1 points to RFC3464 for xtext although its definition is in RFC3461. The action prose inherits RFC3464 syntax while adding transferred and opaque. An implementation needs a combined grammar rather than an unchanged DSN parser.

The [transport contract](../transport.md) preserves tracking privacy and evidence boundaries. No query implementation, endpoint verification or presence guarantee is claimed.
