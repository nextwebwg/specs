---
title: SPF errata reconciliation
sectionNav: true
---

# SPF errata reconciliation

All 17 retrieved [RFC7208 errata](https://www.rfc-editor.org/errata/rfc7208) were read in full. The complete 64-page base text has been read; its section ledger is being assembled. Dependency and live registry closure remain open.

| Erratum | Status | Section | Disposition |
| --- | --- | --- | --- |
| [4453](https://www.rfc-editor.org/errata/eid4453) | Held for Document Update | 5.6.  "ip4" | Numeric CIDR ranges remain constrained by comments; proposed stricter ABNF is held, not a new accepted grammar. |
| [4001](https://www.rfc-editor.org/errata/eid4001) | Held for Document Update | A.4 | Appendix A.4 uses obsolete SPF RR type; normative TXT-only requirement remains authoritative. |
| [4081](https://www.rfc-editor.org/errata/eid4081) | Rejected | 8.4 | Rejected status-code substitution; consult the separately reviewed RFC7372 update. |
| [4082](https://www.rfc-editor.org/errata/eid4082) | Rejected | 8.7 | Rejected status-code substitution; do not apply proposed5.7.8. |
| [6433](https://www.rfc-editor.org/errata/eid6433) | Reported | 3 | SPF/SRV placement comparison reported as wrong; use explicit SPF owner-name rule. |
| [4751](https://www.rfc-editor.org/errata/eid4751) | Reported | 5.5 | PTR subdomain direction contradiction remains reported. |
| [4841](https://www.rfc-editor.org/errata/eid4841) | Reported | 3.5. | Wildcard example lacks absolute-target trailing dots; report remains unresolved. |
| [5227](https://www.rfc-editor.org/errata/eid5227) | Reported | 5.5 | PTR validation-order optimization proposed, not adopted. |
| [5228](https://www.rfc-editor.org/errata/eid5228) | Reported | 5.5 | PTR performance rationale challenged; publication discouragement and required verifier support remain. |
| [5436](https://www.rfc-editor.org/errata/eid5436) | Verified | GLOBAL | Verified Received-SPF grammar permits result/comment with no trailing whitespace and optional key/value list. |
| [5550](https://www.rfc-editor.org/errata/eid5550) | Reported | 2.3. | Malformed HELO policy criticism does not change none into pass. |
| [5843](https://www.rfc-editor.org/errata/eid5843) | Reported | 9.1 | Reported example mechanism value needs quoting under published dot-atom grammar. |
| [6216](https://www.rfc-editor.org/errata/eid6216) | Reported | A.4 | Appendix A.4 PTR target differs after recursion; proposed explicit target remains reported. |
| [6432](https://www.rfc-editor.org/errata/eid6432) | Rejected | 4.4 | CNAME question rejected as inappropriate errata; DNS dependency still needs review. |
| [6595](https://www.rfc-editor.org/errata/eid6595) | Reported | 4.6.4 | Void-lookup limits can affect multiple exists terms; report does not remove the limits. |
| [6721](https://www.rfc-editor.org/errata/eid6721) | Verified | 8.4 | Verified multiline SMTP example needs hyphens on continuation lines. |
| [8596](https://www.rfc-editor.org/errata/eid8596) | Reported | 5.5 | PTR filtering/order and subdomain-direction proposal remains reported. |

Verified corrections are distinguished from held, reported and rejected entries. Examples do not override the published protocol; unresolved PTR and grammar issues require an explicit implementation decision and interoperability evidence.
