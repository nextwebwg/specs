---
title: Certificates without revocation information audit
sectionNav: true
---

# Certificates without revocation information audit

RFC 9608 defines an explicit exception to RFC 5280's revocation-status step. A conforming `noRevAvail` extension means the issuer will not publish revocation information for that end-entity certificate. It does not mean the certificate's key is known to be uncompromised.

**Review:** Complete base text, ASN.1 module, registration table, references and end matter read: 477 lines, 10 pages, 18 section dispositions. Current metadata identifies a June 2024 Proposed Standard updating RFC 5280, with no later update or replacement listed. The live errata page contains one Held editorial record, 8012, correcting an abstract grammar error; no protocol change.

## Changes needed in the service TLS section

State the revocation rule with its exception. RFC 9608 §4 skips RFC 5280 §6.1.3(a)(3) when `noRevAvail` is present; otherwise revocation status is determined. It also names `ocsp-nocheck`, whose legitimate context is an OCSP responder certificate, not a general HTTPS leaf exemption. The [selected OCSP review](certificate-status.md) covers that responder-certificate distinction.

The `noRevAvail` extension is OID `2.5.29.56`, with a NULL value (`05 00` in DER), and conforming issuers mark it noncritical. It must not occur in CA certificates. A relying party must reject a certificate that combines it with any of:

- Basic Constraints `cA = TRUE`;
- CRL Distribution Points;
- Freshest CRL;
- an AIA `id-ad-ocsp` access method.

AIA issuer-certificate retrieval is not categorically prohibited. An absent OCSP URL or distribution-point extension is not equivalent to an explicit `noRevAvail` assertion. The exception skips that certificate's revocation step; it does not skip signature, validity, path, purpose or service-name checks, or the applicable checks on other certificates in its path.

The RFC sets no numerical definition of “short-lived.” Its rationale compares lifetime with the time needed to detect, report and distribute a revocation. Do not invent an approved number of days. Its long-lived factory-device example does not require Email/2 to accept never-expiring service certificates. Any additional service issuance/acceptance constraint would be a separate proposal.

## Implementation and dependency boundaries

The existing TLS handshake experiment does not test `noRevAvail` parsing, conflicting extensions, CA misuse or revocation-exception handling. Standard hostname and chain checks are not evidence that these rules are enforced. The [separate extension experiment](../evidence/README.md#explicit-no-revocation-certificate-extension) checks a legitimate end-entity assertion and each forbidden combination with generated certificates. It is not integrated into TLS and does not establish complete revocation processing.

The security trade-off is explicit: missing revocation information prevents certificate-specific revocation notice. The RFC requires appropriate CA issuance practices and describes revocation of the CA as remediation for misuse. It does not authorize disabling all revocation checks in the TLS context.

Current RFC 5280 follow-ups remain separate: internationalization (9549 and 9598, replacing 8399 and 8398), policy validation (9618), unsigned certificate contexts (9925), and CRL key usage (10007). The [RFC6818 audit](certificate-corrections.md) covers general base corrections. The [base audit](certificate-path.md) links the completed update reviews; implementation coverage remains separate. The selected OCSP/status rules are covered by the [certificate-status audit](certificate-status.md); complete optional OCSP features and backend integration remain separate. ASN.1/X.509 and imported module assurance are not established by retrieval or reference enumeration.

Sources: [RFC 9608](https://www.rfc-editor.org/rfc/rfc9608.html), [metadata](https://www.rfc-editor.org/rfc/rfc9608.json), [current errata](https://errata.rfc-editor.org/search/?rfc_number=9608). Private ledger: `rfc9608-review-candidate.json`; source SHA-256, exact reading span and 18 dispositions recorded. Live metadata and errata read on 20 October 2026.
