---
title: Enhanced-status registry audit
sectionNav: true
---

# Enhanced-status registry audit

**Coverage:** complete eleven-page [RFC 5248](https://www.rfc-editor.org/rfc/rfc5248.html), including all initial table entries and end matter. Reported erratum 8207 reviewed from the retrieved RFC Editor dataset; it is not an accepted correction. The underlying RFC 3463 semantics and related extension dependencies remain open.

## Finding

The registry prevents code collisions. Its associated basic SMTP codes are examples of usual associations, explicitly non-exclusive. A mismatch with that column alone does not prove that a protocol-specific basic reply is invalid. A conflict in the meaning assigned to the same enhanced code is a different issue and needs resolution.

| Section | Disposition |
| --- | --- |
| 1 | Creates collision-avoidance registry for enhanced class.subject.detail codes; X/XXX/YYY are table wildcards, not wire digits. |
| 2 | Registry process, not a new SMTP command or security protocol. |
| 2.1 | Three tables: classes, subjects and enumerated subject/detail pairs. Associated basic status codes are explicitly non-exclusive; unspecified does not mean forbidden. Descriptions and reference status matter. |
| 2.2 | Specification Required registration; accessible non-standards documents possible. Do not self-assign public codes. |
| 2.3 | Standards updates control standards entries; non-standards controllers may update description/references but not code/text. Exceptional IESG correction possible. |
| 2.4 | Initial class2/4/5 and subject0–7 entries plus detailed mapping reviewed. X.7.8 retains authentication meaning; BURL trust failure moves toX.7.14. X.7.10 asks for authentication privacy layer, not end-to-end content encryption. X.7.13 disabled account differs from wrong password. Reported8207 proposes451→452 forX.5.3; not accepted correction. |
| 3 | Detailed security errors can reveal internal implementation or account existence; new diagnostics need exposure controls. |
| 4 | Acknowledgements reviewed. |
| 5 | References reviewed, dependency closure incomplete. |
| 5.1 | 3463/3886/4468/4954 need their own audits;5321 successor already reviewed. |
| 5.2 | 1893 historical predecessor and5226 registration-process successor chain remain distinct. |

| Front/end matter | Abstract, status, author details, copyright and intellectual-property notices reviewed. |

## Interpretation and registration

Reported erratum 8207 proposes changing the X.5.3 basic-code association from 451 to 452 for excessive recipients. Preserve its reported status. RFC 5321's explicit recipient-limit rule governs that condition; the non-exclusive registry table is not grounds to substitute 451 for a mandated 452.

The term “Encryption Needed” for X.7.10 concerns a privacy layer for authentication. It is not evidence that a recipient supports an Email Next cryptographic suite. “Trust relationship required” for X.7.14 concerns submission-server access to third-party content, not proof that a human correspondent has verified an endpoint key.

Do not allocate new public enhanced status numbers merely by using them in this proposal. Proposed registrations need exact semantics, scope, reference, change controller and review. Local application errors remain separate from SMTP replies.

## Required verification

Exercise unknown detail codes without discarding the basic reply; distinguish disabled-account and incorrect-credential diagnostics; preserve recipient-specific failure state; and ensure no transport diagnostic enrolls a key, changes group membership or bypasses a required protection policy. No live SMTP implementation test is claimed.
