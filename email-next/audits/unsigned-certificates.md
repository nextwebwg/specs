---
title: Unsigned certificate boundaries audit
sectionNav: true
---

# Unsigned certificate boundaries audit

[RFC9925](https://www.rfc-editor.org/rfc/rfc9925.html) permits unsigned certificate containers where authentication comes from elsewhere. It never permits substituting them for signatures in a certificate path. Email/2 therefore gains no unsigned HTTPS authentication exception.

Complete base, examples, registrations, references and ASN.1 module reviewed. Nineteen dispositions are recorded; the live official errata search returned none. Imported modules and registry state remain separate dependencies.

No implementation test establishes unsigned-certificate handling. Configured trust-anchor formats remain distinct from incoming service certificates. Missing signatures cannot create trust.
