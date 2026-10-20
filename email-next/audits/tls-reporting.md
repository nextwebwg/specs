---
title: SMTP TLS reporting audit
sectionNav: true
---

# SMTP TLS reporting audit

The complete 1907-line captured text of [RFC8460](https://www.rfc-editor.org/rfc/rfc8460.html), including all grammar, examples, appendices and end matter, has been reviewed with five captured errata. This is a base-document review; normative-reference and registry closure remain open.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Transport diagnostics; no endpoint encryption assurance. |
| 1.1 | Terminology | Policy Domain differs for smarthost and DANE; do not equate it with a conversation participant. |
| 2 | Related Technologies | DANE and MTA-STS dependencies remain separately scoped. |
| 3 | Reporting Policy | DNS selection, concatenation, extension parsing, destination lists and DKIM requirements reviewed. Report delivery exceptions are restricted to diagnostics. |
| 3.1 | Example Reporting Policy | Both publication examples reviewed. |
| 3.1.1 | Report Using MAILTO | Mail destination is an aggregate reporting service, not a hidden client-control channel. |
| 3.1.2 | Report Using HTTPS | HTTPS endpoint is for report submission, not key discovery. |
| 4 | Reporting Schema | I-JSON arrays and overlapping failure categories reviewed; counts are not unique messages. |
| 4.1 | Report Time Frame | Daily aggregation and randomized delay are operational guidance, not online presence. |
| 4.2 | Delivery Summary | Connection summaries do not describe user interaction. |
| 4.2.1 | Success Count | Successful policy-compliant TLS connection is not end-to-end delivery or decryption. |
| 4.2.2 | Failure Count | Failure count does not identify compromised endpoints. |
| 4.3 | Result Types | Extensible result categories require registry interpretation. |
| 4.3.1 | Negotiation Failures | Negotiation categories reviewed; diagnostics remain untrusted content. |
| 4.3.2 | Policy Failures | DANE and MTA-STS failures have separate meanings. |
| 4.3.2.1 | DANE-Specific Policy Failures | Missing mandatory DANE and invalid TLSA/DNSSEC are distinguished. |
| 4.3.2.2 | MTA-STS-specific Policy Failures | Policy fetch, syntax and WebPKI failures are distinct. |
| 4.3.3 | General Failures | Generic failure text must not execute or drive endpoint authorization. |
| 4.3.4 | Transient Failures | Transient errors may be omitted; absence of reports is inconclusive. |
| 4.4 | JSON Report Schema | Every field, numeric count, time, address and A-label requirement reviewed; this is not Email Next event JSON. |
| 4.5 | Policy Samples | TLSA and MTA-STS arrays preserve applied policy, including errors; printed TLSA wrapping is not literal valid JSON. |
| 5 | Report Delivery | SMTP and HTTPS paths are diagnostic transports. |
| 5.1 | Report Filename | Filename is a recommendation and untrusted hint; rejected8582 confirms no semantic authority. |
| 5.2 | Compression | Compression guidance does not establish a universal message-size limit; bound decompression independently. |
| 5.3 | Email Transport | Multipart report structure, required headers, submitter/body relationship, DKIM coverage and subject grammar reviewed. |
| 5.3.1 | Example Report | Illustrative mail contains placeholder data and malformed date spelling; not a wire fixture. TLS-policy exception applies to reports only. |
| 5.4 | HTTPS Transport | HTTPS success acknowledges receipt, not report processing or conversation delivery. |
| 5.5 | Delivery Retry | Optional report retry guidance does not establish reliable control delivery. |
| 5.6 | Metadata Variances | Report payload takes precedence over filename and subject metadata. |
| 6 | IANA Considerations | Registration actions reviewed separately from current registry contents. |
| 6.1 | Message Headers | TLS report headers identify reports, not authenticated devices. |
| 6.2 | Report Type | Report-type registry and initial DSN/MDN/TLS entries reviewed. |
| 6.3 | +gzip Media Type Suffix | Suffix registration reviewed; erroneous Adler-32 statement conflicts with gzip CRC32 and must not guide implementation. |
| 6.4 | application/tlsrpt+json Media Type | JSON media registration supplies no active content or identity authority. |
| 6.5 | application/tlsrpt+gzip Media Type | Gzip media registration supplies no confidentiality or cryptographic authentication. |
| 6.6 | STARTTLS Validation Result Types | Initial result registry and expert-review policy reviewed. |
| 7 | Security Considerations | Flooding, malicious report content, poisoned discovery, interception and third-party destination abuse reviewed. |
| 8 | Privacy Considerations | Diagnostics expose configuration and potential sender characteristics; minimize exported metadata. |
| 9 | References | Complete reference lists and contributor/author end matter reviewed. |
| 9.1 | Normative References | Normative dependencies need separate applicability/closure decisions. |
| 9.2 | Informative References | Informative prior art does not confer endpoint trust. |
| Appendix A | Example Reporting Policy | Both subdomain policy examples reviewed; no mailbox concealment guarantee. |
| A.1 | Report Using MAILTO | Mailto example reviewed separately from main-text example. |
| A.2 | Report Using HTTPS | HTTPS example reviewed separately from main-text example. |
| Appendix B | Example JSON Report | Full example reviewed; mx-host type contradiction, missing fields and invalid wrapped URI prevent treating it as a conforming wire vector. |

## Errata and source discrepancies

- Verified [8070](https://www.rfc-editor.org/errata/eid8070) corrects the actor choosing report destinations to the reporter.
- Held [5889](https://www.rfc-editor.org/errata/eid5889) and reported [8303](https://www.rfc-editor.org/errata/eid8303) identify the missing DKIM service-type registration. The [IANA service-type registry](https://www.iana.org/assignments/dkim-parameters/#dkim-parameters-8), checked on 19 October 2026, lists email and the wildcard, not tlsrpt. Do not claim the registration has been completed.
- Held [6241](https://www.rfc-editor.org/errata/eid6241) identifies the scalar mx-host example despite the array requirement. Its disposition explicitly notes deployed behavior, so an erratum cannot be treated as proof of interoperability.
- Rejected [8582](https://www.rfc-editor.org/errata/eid8582) does not change the filename grammar. Its explanation confirms that filename hints are untrusted and do not determine report semantics.

Section6.3 incorrectly attributes Adler-32 integrity to gzip. [RFC1952 section2.3.1](https://www.rfc-editor.org/rfc/rfc1952.html#section-2.3.1) defines CRC32; neither checksum authenticates a sender. That section's archive/path language must not be mistaken for permission to extract arbitrary files. Parse bounded report data without writing sender-selected paths.

Other discrepancies remain recorded rather than silently repaired: the TXT prefix filtering text is stricter than the field-delimiter whitespace grammar; the email example's Date is not a conforming fixture; the printed JSON examples include wrapped strings, and AppendixB contradicts the mx-host array requirement. The additional-information URI also contains broken wrapping and spaces. The published examples are explanatory material, not validated wire vectors.

## Email Next integration

Diagnostic delivery deliberately tolerates failures that protected conversation delivery cannot. Keep report generation separate from content, key exchange, identity-state changes and hosted-access tokens. Successful report submission means neither successful report analysis nor successful message delivery. Connection totals and overlapping failure categories cannot be converted into per-message receipts.

Required integration cases include optional and missing reports, multiple DNS records, DKIM failure and body-length signatures, report loops, hostile diagnostics/URIs, decompression limits, payload-versus-filename mismatch and privacy minimization. No TLSRPT sender, receiver or live-provider interoperability test is supplied by this audit.
