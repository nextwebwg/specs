---
title: DMARC failure reporting audit
sectionNav: true
---

# DMARC failure reporting audit

The complete [RFC9991](https://www.rfc-editor.org/rfc/rfc9991.html), including its complete multipart message example, references and end matter, has been read. No RFC9991 entries occur in the captured full errata corpus; this is not a fresh live-status assertion. It updates RFC6591 and participates in replacing RFC7489. Dependency closure and registry verification remain open.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Detailed failures can contain entire messages and personal data; reporting is optional and privacy-dependent. |
| 1.1 | Terminology | All imported DMARC/ARF terminology and requirement keywords read. |
| 1.2 | Document Status | Part of replacement of RFC7489; updates RFC6591. |
| 2 | DMARC Failure Reports | ruf/fo, each-destination attempts, external verification, PSD restriction and mandatory outgoing rate limits reviewed. |
| 3 | Other Failure Reports | Underlying DKIM/SPF reports may replace or accompany DMARC reports under receiver policy; not duplicate conversation events. |
| 4 | Reporting Format Update | All augmented ARF fields and Identity-Alignment ABNF read; method list denotes failures, none means all attempted methods succeeded. |
| 5 | Verifying External Destinations | RFC9990 Section 4 applies with ruf substituted for rua; recipient consent does not authorize content disclosure. |
| 5.1 | Transport | Reports SHOULD be DMARC-aligned; unaligned reports can generate loops; no claim of guaranteed suppression. |
| 6 | IANA Considerations | Registry action reviewed; live verification remains open. |
| 6.1 | Feedback Report Header Fields Registry Update | Identity-Alignment is non-repeating, auth-failure-related and lists failed methods. |
| 7 | Privacy Considerations | Minimization, controlled destinations, secure channels and limited diagnostics reviewed. |
| 7.1 | Data Exposure Considerations | Reports can expose full content, mailing-list membership and previously hidden forwarding destinations. |
| 7.2 | Report Recipients | Internal-looking address can forward externally; destination validation does not prove final custody. |
| 7.3 | Additional Damage | Reports can redistribute phishing/malware; redaction and isolated consumption discussed, not an executable sanitization profile. |
| 8 | Security Considerations | Cross-referenced security/privacy dependencies retained. |
| 8.1 | Denial of Service | Incident consolidation and rate limiting reduce amplification; reports need not enumerate every failure. |
| 9 | References | All references read. |
| 9.1 | Normative References | ARF, redaction, authentication-failure and source-port dependencies remain open. |
| 9.2 | Informative References | Independent DKIM/SPF report requests and historical DMARC dependencies identified. |
| Appendix A | Example Failure Report | Entire multipart example and redaction notes read; illustrative headers are not verified cryptographic or canonical syntax vectors. |

## Boundaries that affect Email/2

Failure reports are potentially a second delivery of the original content. Their destination authorization checks prevent unwanted report traffic; they do not prove that every conversation participant approved disclosure to that destination. Mailing-list member addresses and forwarding destinations can be exposed even when the original author did not know them. An apparently internal report address can itself forward elsewhere.

The [security contract](../security.md) therefore prohibits automatic disclosure of decrypted content, private audience data and access secrets. Report generation must not expose decrypted equivalents through canonicalized-body fields or diagnostic excerpts. Delivery of a report is not a conversation contribution, capability response or confirmation that a participant read the original message.

The Identity-Alignment field is easy to misread: listed methods failed to authenticate an aligned identity; none means all attempted methods succeeded. It is not a list of trusted methods or an encryption-status field. The optional and potentially consolidated nature of reports prevents their use as a complete per-message event log.

Section 2 forbids considering ruf with psd=y absent specific agreements. This receiver-side exception must be read alongside RFC9989's prohibition on multi-organizational PSDs publishing ruf. Email/2 does not infer any such agreement from DNS presence alone.

## Example limitations

Appendix A illustrates format and information exposure. It is not a verified DKIM vector: example domains provide no validation keys, and its displayed results are assertions. Its outer From and Message-Id lines contain trailing semicolons, its trace chronology is inconsistent, and the displayed Ed25519 key-size description must not be adopted as a cryptographic requirement. Redacting local parts alone is not proof of anonymity; identifiers, trace fields, subject and body can disclose sensitive data through other paths. The example's text/rfc822-headers alternative is relevant when omitting the original body.

RFC5965, RFC6590, RFC6591 and RFC6692 need separate full review before an ARF processing implementation is claimed. No numeric rate limit or production redaction algorithm is established by this audit.

## Historical interpretation boundary

RFC7489 Section 7.3.1 assigns the opposite polarity to `Identity-Alignment`: its list names methods that produced aligned identities, with `none` when no method did. Importing historical reports therefore requires specification provenance. The [security contract](../security.md#historical-report-interpretation) preserves ambiguous fields without silently converting their meaning. This is a source-level compatibility discrepancy, not an assertion that a date or the generic ARF version reliably identifies deployed producer behavior.
