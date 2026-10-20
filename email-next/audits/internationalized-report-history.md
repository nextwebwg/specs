---
title: Historical internationalized reports audit
sectionNav: true
---

# Historical internationalized reports audit

The complete base text of [RFC5337](https://www.rfc-editor.org/rfc/rfc5337.html), including grammar, registration templates, references and end matter, has been reviewed. The captured corpus contains three verified errata and one held for document update. RFC6533 replaces this Experimental document; see the [current report audit](internationalized-reports.md). Dependency closure is separate.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Historical Experimental internationalized reports; RFC6533 is the replacement baseline. |
| 2 | Conventions Used in This Document | ABNF and requirement conventions reviewed. |
| 3 | UTF-8 Address Type | Three historical address encodings and decode order reviewed; paired alternate-address syntax is obsolete and does not establish identity continuity. |
| 4 | UTF-8 Delivery Status Notifications | Global report parts permit internationalized data and mixed report representations; verified1513 corrects ASCII comment, held1514 concerns terminology. Historical diagnostic grammar conflicts with UTF-8 prose and is not current parsing authority. |
| 4.1 | Additional Requirements on SMTP Servers | Returned undeliverable internationalized content is transfer-encoded for a 7-bit path rather than semantically downgraded under this experiment. |
| 5 | UTF-8 Message Disposition Notifications | Global MDNs carry internationalized recipient and diagnostic data; verified1515 clarifies header-field terminology. Reports are not structured answers or authenticated user actions. |
| 6 | IANA Considerations | Registration templates reviewed; live registry state remains separate. |
| 6.1 | UTF-8 Mail Address Type Registration | Historical UTF-8 address registration repeats contextual forms; its ORCPT case wording must not override current RFC6533. |
| 6.2 | Update to 'smtp' Diagnostic Type Registration | SMTP diagnostic codes retain meaning while global-report prose allows UTF-8 explanatory text. |
| 6.3 | message/global-headers | Global headers retain UTF-8 without a charset parameter; transfer encoding is distinct from charset conversion. |
| 6.4 | message/global-delivery-status | Global delivery-status is the report's machine-readable component; media-type selection does not authenticate its claims. |
| 6.5 | message/global-disposition-notification | Global disposition notification is a separate report type, not proof of reading or consent. |
| 7 | Security Considerations | Forged positive and negative reports can mislead or cause denial of service; message-ID correlation is not cryptographic proof. Bound parsing and preserve actual evidence level. |
| 8 | References | All reference lists reviewed; successor and normative-reference closure remain separate. |
| 8.1 | Normative References | Historic SMTP/EAI/MDN references are not current profile choices; language, UTF-8 and ABNF dependencies remain scoped separately. |
| 8.2 | Informative References | MIME references and historical downgrade draft reviewed as citations; no revival of obsolete downgrade authority. |
| Appendix A | Acknowledgements | Acknowledgments, author addresses and complete copyright/IPR end matter reviewed. |

## Errata

- Verified [1512](https://www.rfc-editor.org/errata/eid1512) adds RFC3462 to the updated-document list. Its note's RFC3642 spelling does not change the corrected heading's RFC3462 target.
- Verified [1513](https://www.rfc-editor.org/errata/eid1513) corrects text-fixed's comment to US-ASCII rather than Unicode; it does not itself change Diagnostic-Code to use utf8-text.
- Held [1514](https://www.rfc-editor.org/errata/eid1514) proposes media-type terminology; it is not a verified wire-format correction.
- Verified [1515](https://www.rfc-editor.org/errata/eid1515) clarifies individual header-field terminology.

## Historical inconsistencies

Section3's description of both escaped forms as 7-bit safe is broader than its QUCHAR production, which admits multibyte UTF-8. Its six-digit code-point branch uses an open-ended repetition after 10, despite describing a maximum of six digits. Section4's Diagnostic-Code grammar uses ASCII text-fixed while its prose permits UTF-8. These observations are recorded source discrepancies, not newly approved errata. New generation and interpretation use RFC6533; historical recovery must retain ambiguity rather than copy contradictory grammar into the current protocol.

## Conversation boundary

A report can help correlate a delivery attempt and display a diagnostic. It cannot authenticate a principal's key, submit a form, withdraw an answer or prove that a person read a contribution. A legacy parser must not reinterpret an address decoded from an old report as a replacement recipient identity. Transfer decoding also does not authorize rewriting signed returned content.
