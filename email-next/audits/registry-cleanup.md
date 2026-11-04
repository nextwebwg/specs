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

The draft proposes increments of 9 for SMTPUTF8, 89 for CHECKPOINT and 1009 for NO-SOLICITING. Serialized grammar and published receiver allowance are separate quantities:

| Extension | Serialized increment | Published source discrepancy |
| --- | --- | --- |
| SMTPUTF8 | Eight-character valueless token plus preceding space: 9 octets | RFC6531 §3.1 grants 10 additional characters; calculating 9 does not authorize reducing receiver acceptance. |
| CHECKPOINT | Space, seven-character `TRANSID`, equals sign and value of at most80 characters: 89 octets | RFC1845 §2 items4–5 bounds the value including angle brackets but grants only88 additional characters. |
| NO-SOLICITING | Space plus `SOLICIT=` occupies9 octets; adding the grammar/registration maximum1000 gives1009 | RFC3865 §4.1 grants1007. Its §2.2 prose also says the keyword set is strictly shorter than1000, which would instead give a maximum1008. The grammar/registration and prose boundaries disagree. |

The CHECKPOINT calculation follows [RFC1845 §§2–3](https://www.rfc-editor.org/rfc/rfc1845.html#section-2). The NO-SOLICITING discrepancy follows [RFC3865 §§2.2–2.3,4.1 and AppendixA](https://www.rfc-editor.org/rfc/rfc3865.html#section-2.2). The draft's1009 does not resolve that source's prose boundary or amend the published1007 allowance. These are scoped grammar findings, not complete audits of either extension. Neither extension is selected as an Email/2 retry, consent or key-discovery mechanism. Proposed corrections are not silently adopted as published receiver requirements.

The length table repeats CONPERM and does not provide a separately labelled CONNEG row. Its NO-SOLICITING explanation points to section 2.3 of “this document”, which does not exist in this draft. Do not infer the missing row's identity or the intended reference. The complete table has been read, but independent recalculation of every listed extension's maximum remains outstanding.

The specification must calculate command lengths from the negotiated extension grammar, retaining the distinction between MAIL and RCPT allowances. A registry increment does not authorize unlimited AUTH mechanism exchanges, message data or renderer resources.

## Remaining work

The CHECKPOINT and NO-SOLICITING source calculations above retain their published conflicts. A future adapter selecting either extension must define its sender/receiver interoperability policy explicitly; the general Email/2 profile does not depend on them. Track resolution of the NO-SOLICITING boundary and draft table defects, and recheck the live registry before claiming proposed edits are applied. Recalculation of other optional extensions remains separately scoped. No external report or registration has been submitted as part of this audit.
