---
title: DKIM errata reconciliation
sectionNav: true
---

# DKIM errata reconciliation

All 23 retrieved [RFC 6376 errata](https://www.rfc-editor.org/errata/rfc6376) were read, including original text, proposed corrections and verifier notes. The complete base text has also been read; its public section ledger is still being assembled. This page does not claim completion of the algorithm updates, registry reconciliation or normative dependency closure.

Verified corrections inform implementation. Held and reported entries are recorded as unresolved source issues; rejected entries do not amend the standard.

| Erratum | Status | Section | Disposition |
| --- | --- | --- | --- |
| [4287](https://www.rfc-editor.org/errata/eid4287) | Verified | 3.6.1 | Correct ASN.1 reference to X.690. |
| [3017](https://www.rfc-editor.org/errata/eid3017) | Held for Document Update | 3.6.1 | SPKI wrapping clarification remains held; do not silently declare the competing encoding text resolved. |
| [3192](https://www.rfc-editor.org/errata/eid3192) | Verified | Appendix A | Remove the extra body space in Appendix A before using its hash vector. |
| [3758](https://www.rfc-editor.org/errata/eid3758) | Rejected | 3.6.1. | Rejected key-version/signature-version conflation. |
| [3759](https://www.rfc-editor.org/errata/eid3759) | Rejected | 3.6.1. | Rejected key hash tag/signature header-selection tag conflation. |
| [4810](https://www.rfc-editor.org/errata/eid4810) | Verified | 3.5 | Encode colon in query-method extension arguments; the copied-header pipe rule is different. |
| [4875](https://www.rfc-editor.org/errata/eid4875) | Held for Document Update | 3.5 | Copied-header name/value folding clarification remains held. |
| [4926](https://www.rfc-editor.org/errata/eid4926) | Verified | A.2, A.3 | Use six continuation spaces in the sample after removing RFC presentation indentation. |
| [5070](https://www.rfc-editor.org/errata/eid5070) | Verified | 3.2 | Correct empty tag-value grammar to prevent adjacent FWS from admitting obsolete all-whitespace lines. |
| [5137](https://www.rfc-editor.org/errata/eid5137) | Verified | 3.6.1 | Correct lowercase k tag octet. |
| [5252](https://www.rfc-editor.org/errata/eid5252) | Verified | 3.7 | Do not append the body hash separately to header-hash input. |
| [5260](https://www.rfc-editor.org/errata/eid5260) | Rejected | 3.5 | Header names are already case-insensitive; no new rule needed. |
| [5551](https://www.rfc-editor.org/errata/eid5551) | Rejected | 6.3. | Rejection leaves the SMTP reply guidance intact. |
| [5713](https://www.rfc-editor.org/errata/eid5713) | Rejected | 2.8 | FWS permits but does not require CRLF. |
| [5839](https://www.rfc-editor.org/errata/eid5839) | Verified | 3.4.2 | Trim the relaxed-header terminal space before final CRLF. |
| [6076](https://www.rfc-editor.org/errata/eid6076) | Verified | .6 | Correct the domain-rule explanatory comment; no address-literal grammar change. |
| [6254](https://www.rfc-editor.org/errata/eid6254) | Held for Document Update | 5.4 | Conflicting informative header-selection advice remains held. |
| [8998](https://www.rfc-editor.org/errata/eid8998) | Reported | 3.7 | Additional hash-input prose report remains unverified; use verified5252 and normative algorithm. |
| [6674](https://www.rfc-editor.org/errata/eid6674) | Reported | Appendix C | Competing RSA public-key encoding correction remains reported, alongside held3017 and reported7001. |
| [6769](https://www.rfc-editor.org/errata/eid6769) | Held for Document Update | 8.2 | MIME/unsigned Content-Type attack clarification remains held; application protection must bind interpretation metadata. |
| [7001](https://www.rfc-editor.org/errata/eid7001) | Reported | 3.6.1 | RSA key wrapper report remains unresolved. |
| [7862](https://www.rfc-editor.org/errata/eid7862) | Rejected | 3.4.2 | Withdrawn/rejected whitespace expansion; do not widen WSP to generic ASCII whitespace. |
| [9038](https://www.rfc-editor.org/errata/eid9038) | Reported | 3.5 | Timestamp calendar estimate report remains unverified; preserve numeric grammar and avoid 32-bit overflow. |

## Consequences for the proposal

The [security contract](../security.md) separates domain authentication from endpoint identity, preserves signed bytes and coverage, and prohibits replay from repeating external effects. The Appendix A vectors require both verified whitespace corrections; an uncorrected example is not evidence that a verifier is broken. The [RSA key compatibility rule](../security.md#domain-signatures-and-algorithm-policy) accepts DER `RSAPublicKey` and RSA `SubjectPublicKeyInfo` explicitly. This profile decision does not approve held3017 or reported6674/7001. Required verification cases include both valid encodings of the same RSA key, the published RFC8463 RSA example, an algorithm identifier other than `rsaEncryption`, absent/non-NULL parameters, malformed DER and trailing data. Ed25519 remains the raw 32-octet form.
