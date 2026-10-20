---
title: Legacy TLS client signatures audit
sectionNav: true
---

# Legacy TLS client signatures audit

RFC9963 permits an optional exception for legacy client certificate keys that cannot produce TLS-compatible RSA-PSS signatures. It does not remove general RSA-PSS implementation support or permit legacy signatures in the server's CertificateVerify. This resolves the practical support-versus-use question raised by RFC9846's change summary without declaring a source defect.

## Precise reconciliation

RFC9846§9.1's mandatory-to-implement rsa_pss_rsae_sha256 support can coexist with RFC9963's optional choice of a different signature for a particular legacy client key. RFC9963§4 explicitly retains RSA-PSS for TLS1.3 servers using RSA keys. Its new codes are only for client CertificateVerify; they are neither server handshake signatures nor the existing rsa_pkcs1_* certificate-signature codes.

The broad sentence in RFC9846§1.2 must therefore not be read as abolishing all PSS requirements. The operative interpretation is the limited client-key exception defined by9963. No erratum adjudicating that summary is claimed. Email Next's configured bearer service does not select client-certificate authentication, so this exception need not be enabled.

## If a future client-certificate profile selects it

Servers may offer0420/0520/0620 in CertificateRequest and must reject any such algorithm not offered. Clients must not advertise them in ClientHello or accept them in server CertificateVerify. PSS-capable keys should not choose them, subject to the source's key-capability probing caveat. Implementations should disable them by default. Selected implementations must enforce strict PKCS#1v1.5 encoding, including mandatoryNULL DigestInfo parameters and validDER; use reviewed crypto libraries, not a new signature implementation.

## Coverage

All272lines/6pages, complete codepoints/table/examples/references/end matter read. Official metadata lists no updates or replacements. Live official errata search returned no matching records; full returned text read. No cryptographic, TLS, browser or deployment tests performed. The three current IANA entries are reconciled below. The selected RSA/DER/hash reviews remain separate from optional TPM support.

The separate [TLS 1.3 audit](tls13.md) records the current RFC9846 errata and the signature-rule reconciliation.

| Section | Disposition |
| --- | --- |
| front | Fullabstract/status/copyright/contents read. |
| 1 | Legacy hardware client keys motivate optional client CertificateVerify algorithms; no blanket TLS1.3 or PQ guarantee. |
| 2 | BCP14 conventions read. |
| 3 | All three codes0420/0520/0620 and context restrictions read. Forbidden ClientHello advertisement/server CertificateVerify; server MAY offer in CertificateRequest and MUST reject unoffered. Client SHOULD NOT choose for PSS-capablekeys; disabledefault SHOULD. |
| 4 | RSA server signatures continue requiringPSS. Strict8017§8.2 DER and mandatoryNULL DigestInfo required for selectedlegacyclientmode. |
| 5 | All three live IANA entries match the names, codepoints and Recommended=N values below. |
| 6 | Entire references read. |
| 6.1 | All eight normative entries read;8446 successor9846 alreadyreviewed;8017/X690/SHS/TPM sourcecontents notrecursively reviewed. |
| 6.2 | Every informativeentry read;9954 hybridkeyexchange notselectedbythis client-signatureextension. |
| Acknowledgements | Completeacknowledgements read. |
| Authors | Bothauthorrecords/end read. |

Sources: https://www.rfc-editor.org/rfc/rfc9963.txt ; https://www.rfc-editor.org/rfc/rfc9963.json ; https://errata.rfc-editor.org/search/?rfc_number=9963 ; https://errata.rfc-editor.org/search/?rfc_number=9846

## Selected current SignatureScheme entries

The [IANA TLS SignatureScheme registry](https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml#tls-signaturescheme) records the following entries, all referencing RFC9963:

| Value | Name | Recommended |
| --- | --- | --- |
| `0x0420` | `rsa_pkcs1_sha256_legacy` | `N` |
| `0x0520` | `rsa_pkcs1_sha384_legacy` | `N` |
| `0x0620` | `rsa_pkcs1_sha512_legacy` | `N` |

This 20 October 2026 check confirms the selected registry fields. It does not enable client-certificate authentication or override the RFC's role and offer restrictions.
