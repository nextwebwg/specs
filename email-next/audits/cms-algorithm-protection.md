---
title: CMS algorithm protection audit
sectionNav: true
---

# CMS algorithm protection audit

A valid signature must not be reinterpreted using a substituted algorithm. RFC6211 protects copies of the digest and signature or MAC identifiers inside authenticated attributes, then requires the receiver to compare them with the outer identifiers. RFC8933 recommends using this attribute; it separately requires the same content and signed-attribute digest algorithm.

This is a S/MIME/CMS compatibility dependency. It does not change Email/2's MLS encoding or establish a CMS implementation.

## Comparison and placement

Include exactly one signature-or-MAC identifier alongside the digest identifier, with the associated parameters. The attribute belongs in signed or authenticated attributes, never an unprotected location, with one instance and one value. A mismatch fails verification. Compare the algorithm's meaning, including defaulted parameters; a byte comparison alone is insufficient. RFC6211 leaves some NULL-versus-absent parameter comparisons to the implementation, so a concrete algorithm profile must resolve them.

## Identifier discrepancy

The published body and module identify the attribute under `1.2.840.113549.1.9.52`. The selected [IANA S/MIME attribute registry](https://www.iana.org/assignments/smi-numbers/smi-numbers.xhtml#security-smime-2) instead assigns `id-aa-cmsAlgorithmProtect` to entry 52 under `1.2.840.113549.1.9.16.2`, yielding `1.2.840.113549.1.9.16.2.52`. Reported errata [9144](https://errata.rfc-editor.org/eid9144/) and [9145](https://errata.rfc-editor.org/eid9145/) flag this discrepancy and identifier spelling. They remain Reported, not verified amendments. This audit records the registry evidence without claiming the published text was corrected or silently accepting both identifiers. A CMS adapter must specify and test its identifier policy before claiming interoperability.

## Coverage

The complete [RFC6211 base](https://www.rfc-editor.org/rfc/rfc6211.html), including the ASN.1 module, references and end matter, was reviewed. Official metadata lists no updates or replacement. Both captured errata were read and reconciled against the live all-status ID/status set and original/corrected text. The selected IANA entry was checked; no complete registry audit, ASN.1 compilation or independent implementation test is claimed.

::: {.details summary="Section dispositions"}

| Section | Disposition |
| --- | --- |
| 1 — Introduction | Algorithm substitution, protected/unprotected SignerInfo fields and limits of countersigning reviewed; historical same-hash convention is superseded by RFC8933. |
| 1.1 — Notation | Requirement terminology reviewed. |
| 2 — Attribute Structure | Exact digest plus one signature-or-MAC algorithm, parameters, protected placement and single attribute/value restrictions reviewed. Published OID conflict remains explicitly qualified by two Reported errata. |
| 3 — Verification Process | Compare algorithm semantics including defaulted parameters; raw encoded-byte comparison is insufficient. NULL-versus-absent handling remains algorithm/profile-dependent. |
| 3.1 — Signed Data Verification Changes | Digest and signature identifiers must match protected copies modulo permitted encoding differences; mismatch fails signature validation. |
| 3.2 — Authenticated Data Verification Changes | Digest and MAC identifiers must match protected copies modulo permitted encoding differences; mismatch fails authentication. |
| 4 — IANA Considerations | S/MIME OID assignment reviewed; selected current IANA attribute52 checked separately, not the full registry. |
| 5 — Security Considerations | Attribute only protects algorithms when itself signed/authenticated; unprotected placement has no security benefit. |
| 6 — References | Complete reference list reviewed; scope-specific algorithm and ASN.1 dependencies remain separate. |
| 6.1 — Normative References | CMS/ESS reviewed separately; RFC5912 module and selected ASN.1 rules have scoped evidence, not whole-standard closure. |
| 6.2 — Informative References | Algorithm examples and randomized-hash experiment are not automatic new selected algorithms. |
| A — 2008 ASN.1 Module | Full 2008 ASN.1 module reviewed, including imports, tags and exclusive alternatives; Reported9144 flags OID inconsistency. No module compilation claim. |

:::
