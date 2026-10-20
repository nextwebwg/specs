---
title: Legacy TLS deprecation audit
sectionNav: true
---

# Legacy TLS deprecation audit

[RFC8996](https://www.rfc-editor.org/rfc/rfc8996.html) explicitly updates RFC6750: the service-answer path must not use or fall back to TLS1.0 or TLS1.1. Statements recommending TLS1.0 for broad interoperability are removed, not preserved as deployment advice. This closes the specific legacy-version issue; it does not finish the service's TLS configuration or OAuth review.

## Service consequences

- RFC8996 raises the legacy floor to TLS1.2. The selected service-answer profile is stricter: its [TLS configuration](tls-configuration.md) and adapter require TLS1.3. Neither permits retrying with TLS1.0/1.1 after failure. The bearer and answer remain unsent when a suitable protected connection cannot be established; no plaintext/email fallback follows automatically.
- A TLS1.2 floor is not evidence that every TLS1.2 cipher/configuration is acceptable. Certificate/server identity checks and current algorithm guidance remain necessary; The [RFC9325 review](tls-configuration.md) supplies the configuration guidance; the older RFC7525 recommendation is not the selected current contract.
- Do not confuse a legacy TLS record-layer version in ClientHello with the negotiated protocol version. Sections4–5 expressly retain acceptance of record-layer {03,XX} values while prohibiting negotiation of TLS1.0/1.1. A packet-prefix check is not a sufficient service-version acceptance test; rely on a correctly configured TLS implementation and validate negotiated outcomes.
- DTLS1.0 is also prohibited, but that does not select DTLS as this HTTPS service's transport. Obsoleting RFC7507 does not authorize removing TLS1.3's independent downgrade defenses or inventing application-level version fallback.

## Evidence

All eighteen pages of base text, complete update lists, quotations, references and end matter reviewed. Official metadata lists no later update or obsoleting document for RFC8996. The returned official errata page (crawl age three days) and captured complete records contain two Verified editorial corrections and one Held editorial correction. This is source review, not executed TLS handshake testing.

| Section | Disposition |
| --- | --- |
| front | Complete abstract/status/copyright/contents/header update list read; BCP195, TLS1.0/1.1 and DTLS1.0 deprecation. |
| 1 | Technical migration rationale and six bullet reasons read; not a complete current cipher-suite selection profile. |
| 1.1 | All update lists and special cases read. Prohibits old-version fallback, raises stated minima to TLS1.2/DTLS1.2, removes old broadest-interoperability claims. RFC6750/RFC6749 explicitly included. Historic/obsoleted protocols remain subject to modern TLS; RFC5469/RFC7507 obsoleted. |
| 1.2 | BCP14 uppercase requirement interpretation preserved. |
| 2 | All NIST quoted rationale and attack references read; no claim of independently reproducing cryptanalysis or auditing linked sources. |
| 3 | SHA1 transcript/signature and downgrade rationale read; upgrade protocol rather than bolt a stronger hash onto legacy versions. |
| 4 | TLS1.0 and its negotiation forbidden. Version-specific Hello refusal rules distinguished from permissive ClientHello record-layer legacy version handling. |
| 5 | TLS1.1 and its negotiation forbidden; same record-layer/version distinction preserved. |
| 6 | Complete RFC7525 edits read: old TLS/DTLS prohibitions strengthened from SHOULD NOT to MUST NOT. Does not itself supply all remaining TLS configuration requirements. |
| 7 | Old-only peers can fail interoperability; operational discussion does not cancel explicit prohibitions or authorize token/plaintext fallback. |
| 8 | Reduced protocol/fallback surface; no new endpoint identity or OAuth proof mechanism. |
| 9 | No IANA actions. |
| 10 | Complete references read. |
| 10.1 | All normative references read; large update catalog does not require importing every protocol into Email Next. |
| 10.2 | All informative references read, including modern TLS references and attack sources; their full contents not reviewed here. |
| Acknowledgements | All acknowledgements read. |
| Authors | Both author/contact sections and end matter read. |

## Errata

[7103](https://www.rfc-editor.org/errata/eid7103), Verified, fixes malformed HTML update links caused by zero-width characters in source metadata. Use clean RFC identifiers; do not mistake broken links for absent updates. [7796](https://www.rfc-editor.org/errata/eid7796), Verified, corrects the cited author's name to Leurent. [7769](https://www.rfc-editor.org/errata/eid7769), Held for Document Update, corrects ServerHello.Random spelling to ServerHello.random. None changes the old-version prohibition.

## Remaining dependencies

The [RFC7525 metadata](https://www.rfc-editor.org/rfc/rfc7525.json) identifies RFC9325 as its successor. Review that current configuration guidance, the selected TLS implementation's behavior, certificate validation and the independent RFC9700 OAuth update before claiming a complete service security profile. Reading the extensive8996 references and update catalog does not audit every referenced protocol or require unrelated SIP, RADIUS, LDAP or DTLS functions in Email Next.

Suggested acceptance evidence: TLS1.0-only and1.1-only endpoints fail without bearer disclosure or application fallback; allowed TLS negotiation still accepts proper legacy record framing; certificate or service-name failure does not send credentials; connection failures preserve the existing submission identity and uncertainty. These are proposed cases, not results from this audit.
