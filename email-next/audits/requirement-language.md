---
title: Requirement language audit
order: 221
blurb: requirement levels · capitalization · optional features
sectionNav: true
---

# Requirement language audit

[RFC2119](https://www.rfc-editor.org/rfc/rfc2119.html) and its update [RFC8174](https://www.rfc-editor.org/rfc/rfc8174.html) define the requirement vocabulary used by this draft. Both complete base texts, including front matter and closing material, were reviewed. They establish interpretation conventions; they do not confer standards status on Email/2.

| Source section | Disposition |
| --- | --- |
| RFC2119 introduction and §§1–2 | Uppercase mandatory terms express requirements or prohibitions within the specification's scope. |
| RFC2119 §§3–4 | Recommended behavior permits justified exceptions only after understanding their implications. It is not equivalent to an arbitrary implementation preference. |
| RFC2119 §5 | An optional feature still needs defined interoperability with implementations that omit it. Unsupported optional protection does not authorize bypassing a sender's required-protection policy. |
| RFC2119 §6 | Use requirement keywords for interoperability or harm prevention, not to impose unnecessary implementation architecture. |
| RFC2119 §7 | Explain the security consequences of departing from requirements or recommendations. |
| RFC2119 §§8–9 | Acknowledgments and author contact; no additional protocol behavior. |
| RFC8174 §§1–2 | Special keyword meanings apply only to uppercase spellings. Normative requirements can also be expressed without those keywords. |
| RFC8174 §§3–5 and closing material | No registry action or new security mechanism; RFC2119 is the normative dependency. |

## Captured errata

The retained full errata corpus contains 15 RFC2119 records and two RFC8174 records. This review covers their original text, proposed corrections, status and notes; it is not a live freshness guarantee.

| Records | Treatment |
| --- | --- |
| 493, 494, 495, 496, 498, 499, 500, 5101 — Verified | Grammar, punctuation, spelling and the omitted NOT RECOMMENDED keyword; consistent with the updated vocabulary. |
| 2969, 5206 — Held for Document Update | Do not remove the published synonyms based on a held proposal; the grammar issue does not alter protocol requirements. |
| 497, 6773, 6954 — Rejected | Do not adopt the proposed weakening or editorial substitutions. |
| 8849, 8850 — Reported | Unapproved proposed changes to wording; do not treat them as adopted requirements. |
| RFC8174 5022 — Held for Document Update; 6878 — Rejected | Grammar and historical URL presentation; no change to uppercase interpretation. |

## Source identity and limits

RFC2119 base-text SHA-256: `3c2ceb7bfc84cd34720f4a5271338ab9d8280d34bdd1eb250c64306202f2ed8b`.

RFC8174 base-text SHA-256: `5ca0e2f90be0bc5928ee465f76518fee316dfa775aed885658a29a419cc293b7`.

These requirement-language dependency reviews are included in the source inventory. Retrieved publication metadata identifies RFC8174 as an update to RFC2119; neither lists a replacement. Live errata freshness remains separate from the captured review. No implementation-wide keyword or exception audit is claimed. The [conformance chapter](../conformance.md#reading-requirements) states the adopted interpretation.
