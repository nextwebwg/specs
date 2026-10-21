---
title: Stored-content submission audit
sectionNav: true
---

# Stored-content submission audit

Complete fourteen-page [RFC 4468](https://www.rfc-editor.org/rfc/rfc4468.html), all examples, grammar, references and end matter reviewed. Both retrieved errata are verified. RFC5248 is the listed update; URLAUTH and current IMAP dependency closure remain open.

| Section | Disposition |
| --- | --- |
| 1 | Stored-content submission optimization reviewed. |
| 2 | Vocabulary and grammar conventions reviewed. |
| 3 | Extension scope reviewed. |
| 3.1 | Submission-only advertisement, post-authentication capabilities and recipient prerequisite reviewed. |
| 3.2 | Whole-message and mixed-chunk transactions reviewed; failed fetch aborts transaction; LAST completion gates next transaction. |
| 3.3 | URLAUTH and trusted-host forms differ; submit+ identity matching and credential scope reviewed. |
| 3.4 | All success/failure examples read, including restricted AUTH pipelining. |
| 3.5 | Complete command and capability ABNF reviewed. |
| 4 | Conversion permissions reviewed; protected-byte preservation is an additional Email/2 requirement. |
| 5 | Both status additions reviewed; verified895 changes trust code toX.7.14. |
| 6 | Every response example reviewed; intermediate success not durable acceptance; verified896 corrects example to5545.7.14. |
| 7 | BURL registration and enhanced status codes reconciled below; registry column inconsistency preserved. |
| 8 | All confidentiality, credential, parser and resource threats reviewed. |
| 9 | References read. |
| 9.1 | Current URLAUTH/IMAP dependencies remain open. |
| 9.2 | Informative references read. |
| A | Acknowledgments read. |
| Author | Author material read. |
| Copyright | Copyright, IPR and final acknowledgment read. |

## Proposal consequence

BURL can avoid transferring stored content through the client twice. It does not itself guarantee that protected bytes survive submission. The [transport contract](../transport.md) therefore requires a suitable preservation arrangement, stable referenced content, confidential credentials and correct final-acceptance handling before using this optimization for protected delivery.

Verified errata895 and896 distinguish the trust-relationship diagnostic from the originally printed code. The selected registry entries are reconciled below; implementation tests remain outstanding. No BURL client, URLAUTH service or encrypted interoperability result is claimed.

## Selected current registry entries

The [SMTP registry](https://www.iana.org/assignments/mail-parameters/mail-parameters.xhtml#smtp-service-extensions) lists `BURL` as Remote Content, with permitted URL prefixes as its EHLO parameter and RFC4468 as its reference. Its note restricts use to submission, not port25. However, its “Message Submission Use and Values” cell says `MUST NOT`, contradicting that note and RFC4468 §7. This audit records the inconsistency; it does not reinterpret the extension as a port25 facility or claim the registry has been corrected. An implementation must retain the source-defined submission scope.

The [enhanced-status registry](https://www.iana.org/assignments/smtp-enhanced-status-codes/smtp-enhanced-status-codes.xhtml) assigns `X.6.6` to Message content not available (basic code554, RFC4468) and `X.7.14` to Trust relationship required (535/554, RFC5248). The latter explicitly replaces the earlier `X.7.8` use for this condition, consistent with the reviewed correction. The 20 October 2026 capture covers these entries only.
