---
title: Sieve rejection audit
sectionNav: true
---

# Sieve rejection audit

The complete base text of [RFC5429](https://www.rfc-editor.org/rfc/rfc5429.html), including examples, registration templates, references and end matter, has been reviewed. The captured corpus contains one erratum: [5159](https://www.rfc-editor.org/errata/eid5159), held for document update, correcting ASCII spelling. It does not change protocol semantics. Dependency and current-registry closure remain separate work.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Protocol-time rejection reduces forged-sender backscatter; suppressing a later report is discretionary and not an invisible-control guarantee. |
| 1.1 | Conventions Used in This Document | Requirement conventions reviewed; spam/virus classification is outside this document. |
| 2 | Sieve "reject" and "ereject" Extensions | Reject and ereject are distinct capabilities with different preferences. |
| 2.1 | Action ereject | Ereject cancels implicit keep and chooses protocol refusal before DSN fallback; it is unavailable where protocol rejection cannot be supported. |
| 2.1.1 | Rejecting a Message at the SMTP/LMTP Protocol Level | Prefer550 when rejecting at SMTP/LMTP level; non-ASCII reasons require negotiated support or an ASCII replacement. Held5159 corrects spelling only. |
| 2.1.2 | Rejecting a Message by Sending a DSN | Mixed accepted/refused SMTP recipients require acceptance and recipient-specific DSNs; LMTP can reject individually. Null reverse paths prohibit DSN generation. |
| 2.2 | Action reject | Reject preserves reason text and permits protocol rejection only with compatible text encoding and recipient outcomes. |
| 2.2.1 | Rejecting a Message by Sending an MDN | MDN fallback targets the envelope sender, not a forged visible From; null reverse paths prohibit it. Automatic deleted disposition is not a user-read acknowledgment. |
| 2.3 | Silent Upgrade from "reject" to "ereject" | Interpreters must not silently replace reject with ereject; script-generator migration has explicit environmental and user-understanding constraints. |
| 2.4 | Compatibility with Other Actions | Multiple rejections and vacation combinations are prohibited; delivery combinations are discouraged. Body edits must not alter returned report content. |
| 2.5 | Details of Protocol-Level Refusal | Multiline reasons obey reply length and enhanced-status formatting; an initial4xx deferral is not final rejection or capability loss. |
| 3 | Changes from RFC 3028 | Changes from3028 reviewed: implicit keep cancellation, protocol-level refusal and ereject preference. |
| 4 | Security Considerations | False-positive suppression can hide legitimate failure; autoresponder and base Sieve security dependencies still apply. |
| 5 | IANA Considerations | Registration templates reviewed; live registry verification remains separate. |
| 5.1 | "reject" Extension Registration | Reject registration preserves exact reason preference. |
| 5.2 | "ereject" Extension Registration | Ereject registration favors early protocol rejection and may replace non-ASCII reasons. |
| 6 | References | Complete references reviewed. |
| 6.1 | Normative References | DSN, LMTP, enhanced replies, MDN, multipart reports, Sieve, SMTP, UTF-8 and vacation dependencies remain separately scoped. |
| 6.2 | Informative References | Historical Sieve, responder guidance, spam tests and drafts do not establish current Email Next encryption fallback policy. |
| Appendix A | Acknowledgements | Acknowledgments reviewed. |
| Appendix B | Contributors | Contributors and author end matter reviewed; no additional wire requirements. |

## Email Next consequences

Failure is recipient-specific. A successful SMTP transaction with mixed downstream acceptance cannot be projected as universal delivery, while one rejection cannot mark all recipients failed. A4xx deferral retains retry semantics; it does not establish that encryption is unsupported.

Neither a protocol rejection nor a later DSN/MDN authorizes changing the intended principal, revealing protected content or replacing end-to-end protection with hosted or plaintext delivery. Those remain sender-policy decisions. A report reason is diagnostic text, not a command. Report suppression may prevent a notification from arriving and therefore cannot serve as a reliable control-channel acknowledgment.

The historical MDN reference must be reconciled with its successor rules before generating reports. The [IMAP-event audit](sieve-imap-events.md) also matters: reject and ereject are not applicable in that execution context, even when advertised by a delivery-time Sieve implementation.
