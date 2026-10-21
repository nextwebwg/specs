---
title: Underscored DNS name audit
sectionNav: true
---

# Underscored DNS name audit

Complete fifteen-page [RFC 8553](https://www.rfc-editor.org/rfc/rfc8553.html), all old/new text, tables, examples, references and end matter reviewed. No errata occur in the retrieved corpus. Retrieved metadata lists no successor update. The [RFC8552 registry procedure](underscored-registry.md) has a separate review; live registry reconciliation remains open.

| Section | Disposition |
| --- | --- |
| 1 | Registry model reviewed: uniqueness is RR type plus highest underscored label, closest to DNS root; no software behavior change intended. |
| 2 | RR-type scope reviewed; registry names do not define subordinate labels or record semantics. |
| 2.1 | TXT registration template and all listed specifications reviewed; includes DKIM/SPF/DMARC. |
| 2.2 | SRV protocol-label registration template and all listed specifications reviewed; includes submission/access and tracking. |
| 2.3 | URI protocol or highest Enumservice label registration template reviewed. |
| 3 | All template amendments reviewed. |
| 3.1 | SRV Proto case-insensitivity preserved; globally scoped protocol label SHOULD be registered; RFC8552 reference added. |
| 3.2 | Both URI naming schemes, reversed Enumservice sequence and examples reviewed; global label SHOULD be registered. |
| 3.3 | NULL RR _ta- prefix registration amendment reviewed; not a mail capability signal. |
| 4 | No new registry or procedure introduced by this update itself. |
| 5 | Source states no new security issues; registration is not endpoint authentication. |
| 6 | Complete references read. |
| 6.1 | RFC8552 and service/URI dependencies identified; dependency closure remains open. |
| 6.2 | All informative references read; no claim that every unrelated protocol is audited. |
| Acknowledgments | Acknowledgments read. |
| Author | Author and end matter read. |

## Proposal consequence

A future DNS discovery binding must identify its RR type, global underscored label, subordinate naming rules and applicable registration. An underscore is neither a private namespace reservation nor proof that an endpoint controls a mailbox. Existing `_domainkey` interpretation remains DKIM-specific; a successful lookup does not advertise Email/2 or authorize a correspondent key.

The header/metadata update list includes RFC6733 while the body does not discuss it, and the body expressly amends RFC7553 although that RFC is absent from the header list. This audit follows the explicit body amendments and records the discrepancy without inventing missing protocol requirements.
