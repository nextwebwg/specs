---
title: Future message release audit
sectionNav: true
---

# Future message release audit

**Coverage:** complete eleven-page [RFC 4865](https://www.rfc-editor.org/rfc/rfc4865.html), including all interaction and security requirements and end matter. Verified erratum 2040 reviewed. The [IANA enhanced-status registry](https://www.iana.org/assignments/smtp-enhanced-status-codes/) was checked on 19 October 2026 for the quota-code discrepancy below.

## Finding

Future release lets a submission server hold an accepted message. It specifies neither cancellation nor cryptographic reauthorization at release time. It cannot guarantee delivery at a particular instant.

| Section | Disposition |
| --- | --- |
| 1 | Submission server holds mail until requested future release; this is not scheduled arrival or expiration. |
| 2 | Requirement vocabulary reviewed. |
| 3 | FUTURERELEASE advertises maximum interval and UTC timestamp. Exactly one HOLDFOR/HOLDUNTIL parameter; no parameter means no hold default. Interval1–999999999 seconds. Verified2040 replaces undefined timestamp production with3339 date-time; UTC prose still applies. Submission-only, no new verbs. |
| 4 | Both relative and absolute timing depend on server clocks; supporting both accommodates client limitations. |
| 4.1 | Client verifies support, sends exactly one hold parameter and respects the corresponding advertised maximum. |
| 4.2 | MSA advertises only on submission service, accepts valid requests subject to other errors, never releases early, rejects invalid/excess/duplicate parameters with recommended501/5.5.4. |
| 5 | DSN,DELIVERBY andMDN interactions apply separately. |
| 5.1 | DSN interaction delegates baseline3461/3464 behavior. |
| 5.1.1 | Do not request future release for a DSN. |
| 5.1.2 | Generated DSN includes Arrival-Date and Future-Release-Request with for/until syntax; do not copy a literal invented HOLD parameter. |
| 5.2 | Future release and deliver-by can conflict; no silent choice to ignore one. |
| 5.2.1 | Client makes deliver-by strictly later than release time. |
| 5.2.2 | Server rejects release later than deliver-by; source does not explicitly reject equality although client rule excludes it. Recommended501/5.5.4. |
| 5.3 | MDN interaction is distinct from ordinary mail scheduling. |
| 5.3.1 | Do not request future release for an MDN. |
| 6 | Authentication and quotas mitigate storage abuse; quota detection rejects MAIL. Clocks affect timing, trace fields remain unchanged. Printed X.7.16/X.7.17 quota descriptions conflict with current IANA meanings; do not generate them as new quota codes. |
| 7 | Registers FUTURERELEASE; status-code discrepancy requires registry reconciliation. |
| 8 | Acknowledgements reviewed. |
| 9 | Submission6409,DSN,MDN,3339 andDELIVERBY dependencies remain; SMTP/message-format successors reviewed separately. |
| 10 | 3463 status-code reference remains a dependency. |

| Front/end matter | Abstract, status, copyright, author addresses, IPR and funding acknowledgement reviewed. |

## Registry discrepancy

Section 6 prints X.7.16 and X.7.17 as future-release quota codes. The current registry assigns X.7.16 to a message-size/priority condition and X.7.17 to mailbox ownership change. It contains no matching future-release quota entry. Preserve this discrepancy as unresolved; do not generate conflicting code meanings or invent a replacement registration. Generic applicable storage diagnostics require the status-code baseline review.

## Email/2 consequence

Distinguish a locally scheduled draft from a message already accepted by an MSA for future release. The former can re-evaluate audience, key and policy evidence before submission. The latter has already crossed the submission boundary; this extension cannot recall it or replace its ciphertext when new key information arrives.

A policy requiring fresh authorization at the scheduled instant needs an authorized endpoint capable of performing that check then. Do not promise that property from FUTURERELEASE alone, give an ordinary relay decryption keys to simulate it, or silently send early when scheduling is unavailable.

Required cases include unsupported scheduling, duplicate hold parameters, advertised maximum boundaries, UTC conversion, clock changes, release/delivery-deadline conflict, delayed DSN/MDN attempts, quota exhaustion and key revocation after server acceptance. No scheduler, cancellation API or live MSA test is claimed.
