---
title: SMTP registry cleanup audit
sectionNav: true
---

# SMTP registry cleanup audit

**Coverage:** complete eleven-page [registry cleanup draft 03](https://datatracker.ietf.org/doc/html/draft-ietf-emailcore-iana-cleanup-03/), including all three tables, references and end matter. Dated 24 June 2026; Datatracker inspected on 19 October identifies an active working-group draft with IESG state “I-D Exists”. It is not a published RFC or an applied registry change.

| Sections | Disposition |
| --- | --- |
| 1 | Updates existing entries after SMTP revision registry restructuring; does not itself restructure registries. |
| 2 | BCP 14 requirement conventions reviewed. |
| 3–3.1 | Registry edits are an ordered sequence, not new endpoint-capability semantics. |
| 3.1.1 | EXPN/HELP references change; obsolete terminal-delivery and TURN references remain historical. |
| 3.1.2 | EHLO parameter corrections cover DELIVERBY, FUTURERELEASE and LIMITS. The actual extension grammar remains necessary. |
| 3.1.3 | Proposes MAY submission applicability for HELP, BURL, FUTURERELEASE, SMTPUTF8, MT-PRIORITY, RRVS, REQUIRETLS and LIMITS; this explains the current default-column discrepancies. |
| 3.1.4 | Entire verbs and MAIL/RCPT parameter table read. Keep command scope distinct: RRVS and CONNEG use RCPT; many other parameters use MAIL; CHUNKING adds BDAT. Obsolete UTF8SMTP is not SMTPUTF8. |
| 3.1.5 | Entire length table read. Command-length increments are not message-size limits; draft corrections and table defects need source reconciliation before use in conformance tests. |
| 4 | Registry clarification does not directly add message confidentiality or identity assurance. |
| 5–5.2 | Both reference lists reviewed. Table citations include additional standards beyond the bibliography; dependency closure is not established. |
| A and end matter | Acknowledgments and author material read; no additional protocol requirements. |

## Submission discrepancies explained

The draft explicitly proposes correcting the submission column that caused the BURL and FUTURERELEASE discrepancies in the [SMTP revision audit](smtp-revision.md). This provides a documented correction path, not evidence that the live registry has applied it. Email/2 continues to use each applicable extension's defined submission scope and records the inconsistent registry summary separately.

A submission permission of MAY does not require a provider to implement the extension, and does not establish endpoint support for encrypted or interactive messages. Required transport and disclosure policy still governs failed negotiation.

## Length values require careful interpretation

The draft changes SMTPUTF8's increment to 9 and CHECKPOINT's to 89, identifying off-by-one corrections, and gives NO-SOLICITING an increment of 1009. SMTPUTF8 has been checked against RFC 6531 §3.1: the valueless eight-character token plus its preceding space occupies nine octets. The published document nevertheless grants ten extra characters of MAIL command allowance. Actual serialized length and the receiver’s published allowance are separate quantities; the nine-octet calculation does not by itself authorize reducing receiver acceptance. CHECKPOINT and NO-SOLICITING still require independent grammar reconciliation. Proposed corrections are not silently adopted as published updates here.

The length table repeats CONPERM and does not provide a separately labelled CONNEG row. Its NO-SOLICITING explanation points to section 2.3 of “this document”, which does not exist in this draft. Do not infer the missing row's identity or the intended reference. The complete table has been read, but independent recalculation of every listed extension's maximum remains outstanding.

The specification must calculate command lengths from the negotiated extension grammar, retaining the distinction between MAIL and RCPT allowances. A registry increment does not authorize unlimited AUTH mechanism exchanges, message data or renderer resources.

## Remaining work

Reconcile the original extension grammars and errata for the proposed length corrections, track resolution of the table defects, and recheck the live registry before claiming these edits are applied. No external report or registration has been submitted as part of this audit.
