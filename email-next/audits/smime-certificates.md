---
title: S/MIME certificate handling audit
sectionNav: true
---

# S/MIME certificate handling audit

A certificate received in email is evidence to validate, not a new trusted authority. S/MIME requires certificate-path and revocation checks before key use, and treats certificate discovery, address association and signature verification as separate steps.

These are legacy S/MIME compatibility requirements. They do not replace Email Next principal/device identity, exact-mailbox association or MLS authorization. In particular, S/MIME’s address-comparison rules must not silently become Email Next identity normalization.

## Review coverage

Complete base texts, numbered sections, modules where present, references and end matter were reviewed: [RFC8550](https://www.rfc-editor.org/rfc/rfc8550.html). Official metadata lists RFC8933 and RFC9629 as updates to RFC5652 and no updates to RFC8550. Source review does not establish implementation, ASN.1 compiler or interoperability conformance.

::: {.details summary="RFC8550 section dispositions"}

| Section | Disposition |
| --- | --- |
| 1 — Introduction | S/MIME requires PKIX validation plus its own certificate rules; requirement modifiers retain their stated present-day strength. |
| 1.1 — Definitions | S/MIME requires PKIX validation plus its own certificate rules; requirement modifiers retain their stated present-day strength. |
| 1.2 — Conventions Used in This Document | S/MIME requires PKIX validation plus its own certificate rules; requirement modifiers retain their stated present-day strength. |
| 1.3 — Compatibility with Prior Practice of S/MIME | Historical version changes are distinguished from current requirements; weak legacy algorithms are for historical artifacts, not new generation. |
| 1.4 — Changes from S/MIME v3 to S/MIME v3.1 | Historical version changes are distinguished from current requirements; weak legacy algorithms are for historical artifacts, not new generation. |
| 1.5 — Changes from S/MIME v3.1 to S/MIME v3.2 | Historical version changes are distinguished from current requirements; weak legacy algorithms are for historical artifacts, not new generation. |
| 1.6 — Changes since S/MIME 3.2 | Historical version changes are distinguished from current requirements; weak legacy algorithms are for historical artifacts, not new generation. |
| 2 — CMS Options | S/MIME CMS options include v1/v2 CRL reception and RFC5280 revocation checking; a cached CRL is not automatically current. |
| 2.1 — Certificate Revocation Lists | S/MIME CMS options include v1/v2 CRL reception and RFC5280 revocation checking; a cached CRL is not automatically current. |
| 2.2 — Certificate Choices | X.509 v1/v3 reception and recommended v2 attribute certificates reviewed; PKCS#6 can be parsed without being used, and v1 attribute certificates are not sent. |
| 2.2.1 — Historical Note about CMS Certificates | X.509 v1/v3 reception and recommended v2 attribute certificates reviewed; PKCS#6 can be parsed without being used, and v1 attribute certificates are not sent. |
| 2.3 — Included Certificates | Unordered, unrelated and multiple chains must not be mistaken for trust. Sender-supplied self-signed certificates need an independent trust decision. |
| 3 — Using Distinguished Names for Internet Mail | Address-free certificates remain possible; address association, ASCII/internationalized matching, From/Sender comparison and visible certificate identity are distinct checks. This does not change Email Next exact-address identity rules. |
| 4 — Certificate Processing | Retrieval, caching, certs-only import/export, overlapping CA certificates and fresh revocation evidence reviewed; discovery is not trust. |
| 4.1 — Certificate Revocation Lists | Retrieval, caching, certs-only import/export, overlapping CA certificates and fresh revocation evidence reviewed; discovery is not trust. |
| 4.2 — Certificate Path Validation | Path validation precedes key use; ESS certificate-binding attributes and encryption-key preference control certificate selection when present. |
| 4.3 — Certificate and CRL Signing Algorithms, and Key Sizes | Required certificate/CRL algorithms and RSA-size ranges reviewed with historical exceptions; this source alone is not a current global cryptographic policy. |
| 4.4 — PKIX Certificate Extensions | Extension processing follows RFC5280 with S/MIME constraints; issuer conformance and receiver treatment must remain distinct. |
| 4.4.1 — Basic Constraints | Extension processing follows RFC5280 with S/MIME constraints; issuer conformance and receiver treatment must remain distinct. |
| 4.4.2 — Key Usage Extension | Present keyUsage must permit digitalSignature or nonRepudiation for message signatures; absent keyUsage has explicitly specified interpretation. |
| 4.4.3 — Subject Alternative Name | ASCII rfc822Name and internationalized otherName encodings depend on RFC5280/RFC8398; multiple addresses are possible. |
| 4.4.4 — Extended Key Usage Extension | Key usage and extended usage intersect; interpersonal S/MIME checks emailProtection or anyExtendedKeyUsage when EKU is present. |
| 5 — IANA Considerations | No IANA actions. |
| 6 — Security Considerations | Visible validation failure, freshest CRL, reliable validation time, attacker-controlled AIA/CDP retrieval and weak-key warnings reviewed; claimed signingTime cannot revive revoked keys. |
| 7 — References | Reference conventions and complete bibliographies read; body numbering is used because the contents listing differs. |
| 7.1 — Reference Conventions | Reference conventions and complete bibliographies read; body numbering is used because the contents listing differs. |
| 7.2 — Normative References | Reference conventions and complete bibliographies read; body numbering is used because the contents listing differs. |
| 7.3 — Informative References | Reference conventions and complete bibliographies read; body numbering is used because the contents listing differs. |
| A — Historic Considerations | Historical revocation evidence can disappear; weak signature artifacts need distinct treatment. S/MIMEv2 historic status does not authorize weak new messages. |
| A.1 — Signature Algorithms and Key Sizes | Historical revocation evidence can disappear; weak signature artifacts need distinct treatment. S/MIMEv2 historic status does not authorize weak new messages. |
| B — Moving S/MIME v2 Certificate Handling to Historic Status | Historical revocation evidence can disappear; weak signature artifacts need distinct treatment. S/MIMEv2 historic status does not authorize weak new messages. |

:::

## Errata and remaining evidence

The live all-status search returned no RFC8550 errata. The body’s reference headings are 7.1, 7.2 and 7.3; the contents listing differs, so the section ledger follows the body.

Concrete S/MIME tests remain necessary for certificate substitution, address mismatch, unrelated chains, expired or revoked keys, stale CRLs and attacker-controlled retrieval URLs. Reading RFC5280 elsewhere does not establish an implemented S/MIME path validator. Algorithm, internationalized-address and optional attribute-certificate dependencies remain separately tracked.
