---
title: Certificate paths and revocation audit
sectionNav: true
---

# Certificate paths and revocation audit

RFC 5280 supplies the certificate-path and CRL foundation for Email/2's HTTPS services. It does not establish which service may receive a button answer, which trust roots a client should install, or whether a service accepted that answer. Those remain separate application decisions.

**Review status:** The complete 151-page base document, including all ASN.1 modules, diagrams, four annotated examples, references and end matter, has been read. Current RFC Editor metadata and all 23 live errata records have been reviewed. The base review is complete; the current certificate profile is not closed because implementation evidence and underlying dependency reviews remain open. The local handshake experiment does not establish full path-validation conformance.

## Consequences for service clients

A client needs a valid certificate path to an independently trusted anchor **and** the RFC 9525 match against the service's independently selected DNS reference identifier. A received certificate, AIA URL, mailbox address or message-supplied CA file cannot establish its own trust. Path construction is outside RFC 5280's validation algorithm; accepting a downloaded issuer certificate as a trust anchor would confuse those two operations. See §§6.1–6.2.

Validation checks certificate signatures, validity times, issuer chaining, name constraints, CA authorization, path length, policy constraints and critical extensions. Unknown or unprocessable critical extensions fail validation. Constraints apply to the relevant subject names, not just whichever SAN happens to match the requested HTTPS host. Self-issued intermediate exceptions and the distinction between a trust anchor and an in-path certificate must be preserved. The implementation may use another algorithm if its external results are equivalent. See §§4.2, 4.2.1.9–4.2.1.14 and 6.

Key usage and extended key usage restrict use independently. A service certificate's allowed uses must accommodate the selected TLS authentication operation; `emailProtection` does not substitute for TLS server authentication. Verified errata 5802 removes the misleading “WWW” qualification, and 6414 clarifies that suitable key-usage bits can be combined. These examples do not re-enable RSA key transport in the TLS 1.3 service profile. See §4.2.1.12 and the selected TLS profile.

**Revocation is an unresolved implementation boundary.** Section 6.1.3(a)(3) requires the certificate not to be revoked at the current time; CRLs, other status information or out-of-band mechanisms may provide that determination. Section 8 explicitly describes the reduced assurance of omitting revocation checks. The current Python TLS experiment does not supply CRLs, implement OCSP, establish a platform revocation policy, or test revoked certificates. Its successful handshakes therefore do not prove full RFC 5280 behavior. The [RFC9608 update](no-revocation.md) defines an explicit revocation exception with mandatory rejection rules for conflicting extensions; missing status URLs alone do not establish that exception.

If CRLs are selected, freshness, signer authorization, scope, reason coverage and signatures all matter. A certificate absent from an arbitrary CRL is not necessarily unrevoked. The §6.3 algorithm can return `UNDETERMINED`; it must not be converted into affirmative evidence merely because the initial state is `UNREVOKED`. Delta and indirect CRLs are optional support choices with explicit processing requirements when supported. The [RFC10007 review](crl-key-usage.md) requires Key Usage with cRLSign for a version 3 CRL signer; existing TLS tests do not establish that processing.

The base issuance profile is **not** a universal certificate-linting rejection policy. Section 6.1 explicitly distinguishes its validation algorithm from the issuance restrictions in §§4–5 and recommends against adding blanket profile-conformance checks. For example, serial-number issuance rules, extension inclusion requirements and legacy receiver tolerance cannot be flattened into one rejection list.

## What this dependency does not select

Email/2 does not acquire a CA enrollment, certificate backup, cross-certification, LDAP directory, timestamp service, X.400 identity or certificate policy OID merely by referencing RFC 5280. Optional extensions still need correct handling if present and relevant; unsupported critical extensions cannot simply be ignored.

The legacy RSA/DSA, 1024-bit and SHA-1 examples in Appendix C demonstrate encodings, not current service cryptographic defaults. SHA-1 examples for key identifiers likewise do not approve SHA-1 certificate signatures. Selected certificate algorithms and their parameter encodings remain library and algorithm-profile dependencies.

RFC 5280 leaves wildcard identity semantics to applications. Email/2's HTTPS DNS-ID matching follows RFC 9525. Its base internationalization text still references IDNA2003; it must not be copied over the current internationalization updates. A service certificate's other names do not change the application-selected endpoint or establish a mailbox/device binding.

AIA and distribution-point URLs locate potential certificate/status data; their contents still require validation. Section 8 also discusses malformed retrieval data and recursive HTTPS dependencies. A future network implementation needs bounded retrieval and an explicit network-destination policy. The existing service TLS helper performs no such retrieval.

## Current corrections

The official errata search returned six Verified, eleven Held for Document Update, six Rejected and no Reported records. All originals, proposed corrections and verifier notes were read. Held proposals are recorded as issues, not silently promoted to normative replacements; Rejected proposals are not applied.

| Status | IDs | Disposition |
| --- | --- | --- |
| Verified | 5802, 6414 | TLS EKU purpose and compatible key-usage wording, applicable to services. |
| Verified | 5938 | Path validation binds subject DN and/or SAN; application identity selection remains separate. |
| Verified | 7661 | Remove misleading cross-certificate private signing-key wording; certificates do not carry that private key. |
| Verified | 3579, 7658 | ASN.1 type capitalization and the RFC 4518 whitespace-processing hyperlink. |
| Held | 3200 | Positive/nonnegative serial wording; preserve issuance/receiver distinction. |
| Held | 3986, 7634 | Signature versus signatureValue field names; no invented encoding change. |
| Held | 5876 | IP address SAN type clarification; current service host grammar excludes IP references. |
| Held | 5997 | DNS name-constraint leading-dot ambiguity and implementation disagreement; not closed by hostname tests. |
| Held | 8561 | Nonstandard normative “RECOMMENDS” wording. |
| Held | 3466, 3674, 3754, 4274, 4847 | SAN terminology, distributionPoint field name, ISO/DirectoryString/OID comments. |
| Rejected | 1774 | Proposed missing CRL mask step already exists. |
| Rejected | 3693 | Proposed subject-DN DNS constraints change was not accepted; RFC 9525 SAN-only matching remains the selected application rule. |
| Rejected | 5967, 6830 | AIA issuer interpretation and buffer-wording changes not applied. |
| Rejected | 7164 | Proposed CRL scope removal not applied. |
| Rejected | 3085 | Proposed IMPLICIT tag is inappropriate for the untagged CHOICE. |

## Update review coverage

Current metadata lists nine update records. Reading their metadata establishes their relationship, not their requirements. The current update documents are reviewed separately below; historical predecessor scope and implementation evidence remain distinct.

| RFC | Follow-up |
| --- | --- |
| 6818 | [General certificate-profile corrections reviewed](certificate-corrections.md); implementation evidence remains open. |
| 8399 → 9549 | [Current internationalized-name rules reviewed](certificate-internationalization.md); superseded8399 excluded from current profile. |
| 8398 → 9598 | [Current certificate mailbox rules reviewed](certificate-mailbox-names.md); superseded8398 excluded from current profile. |
| 9608 | [No Revocation Available extension reviewed](no-revocation.md); explicit exception and forbidden combinations, not blanket omission of status checks. |
| 9618 | [Updated policy validation reviewed](policy-validation.md); use the policy graph/output guidance and critical-extension rejection rules. |
| 9925 | [Unsigned certificate containers reviewed](unsigned-certificates.md); no unsigned path-signature exception. |
| 10007 | [CRL key-usage update reviewed](crl-key-usage.md); signer authorization is separate from ordinary service leaf usage. |

Further dependency work includes selected algorithm identifiers and parameter rules, ASN.1/DER, DN string preparation and current internationalization rules. OCSP and certificate retrieval protocols become implementation dependencies if selected. Merely reading the references does not close those reviews or prove the TLS library implements them correctly.

## Source trace

- Base: [RFC 5280](https://www.rfc-editor.org/rfc/rfc5280.html), 8,459 newline-delimited source lines, 151 pages.
- Metadata: [RFC Editor metadata](https://www.rfc-editor.org/rfc/rfc5280.json), Proposed Standard, May 2008; obsoletes RFCs 3280, 4325 and 4630; no replacement listed.
- Corrections: [official errata search](https://errata.rfc-editor.org/search/?rfc_number=5280), retrieved successfully on 20 October 2026 and read through the footer.
- Private evidence: `rfc5280-review-candidate.json` contains 114 explicit section/end-matter dispositions, exact source line spans, complete reading ranges and source SHA-256. `rfc5280-errata-selected.json` preserves the 23 records matched against the live page.

The existing eight local handshake tests remain narrow observations about the tested Python/OpenSSL runtime. They do not establish certificate-policy, name-constraint, revocation, internationalization, parser or complete path-validation conformance.
