---
title: Certificate-profile corrections audit
sectionNav: true
---

# Certificate-profile corrections audit

RFC 6818 updates RFC 5280's trust-anchor explanation, certificate-policy notice encoding, internationalized domain-component conversion and security considerations. These corrections do not establish a new Email Next certificate issuance program.

**Review:** Complete 451-line, eight-page base text read, including every original/replacement paragraph, references and end matter; 15 explicit dispositions recorded. Current metadata identifies a January 2013 Proposed Standard updating RFC 5280, with no later update or replacement listed for RFC 6818 itself. The live official errata search reports no matching records.

## Consequences for service TLS

**Keep trust-anchor policy explicit.** A self-signed certificate supplied as trusted CA information can carry additional constraints, but the base algorithm does not prescribe their processing. Section 4 retains implementation discretion and points to RFC 5914's trust-anchor formats and RFC 5937's example of using constraints to initialize validation. Merely loading a root file does not prove that every restriction encoded in that root is enforced. Neither referenced document was fully reviewed in this pass.

**Do not turn a self-signed leaf into an automatic exception.** Section 2 states that self-issued/self-signed certificates issued by non-CAs, and how relying parties authenticate with them, are outside RFC 5280's scope. They are not thereby forbidden in every possible application, but their presence is not a standards-defined substitute for the selected HTTPS trust path.

**Do not use key identifiers as security proofs.** Section 6 explains that the security properties of one-way hashes are not required when generating authority/subject key identifiers. Those identifiers aid selection; they do not replace chain signature validation or establish trusted identity. This clarification does not relax certificate-signature algorithms or Email Next's cryptographic hashes. The same section explains that CA/RA workstation compromise can enable unauthorized issuance even without extracting the CA private key. Comparing issuer names and serial numbers alone cannot defend against that attack.

**Apply current text to policy notices.** Section 3 changes `explicitText` issuance guidance: UTF8String is preferred; VisibleString and BMPString are acceptable but less preferred; IA5String is prohibited. NFC guidance applies to UTF8String and BMPString. This corrects the base text's opposite treatment of those alternatives. Preserve RFC 5280's distinction between issuance-profile rules and client path-validation rejection rules.

**Keep internationalization work open.** Section 5 adds `UseSTD3ASCIIRules` to the base IDNA2003 domain-component conversion. It does not complete the current IDNA profile. The current [RFC9549 rules](certificate-internationalization.md) replace RFC8399; [RFC9598](certificate-mailbox-names.md) separately replaces RFC8398. Full IDNA dependency and implementation coverage remain open.

## Remaining evidence

No implementation files changed. Existing local TLS tests establish neither root-constraint processing nor notice encoding, DN preparation, policy processing or full PKIX conformance. The [base audit](certificate-path.md) links the current update reviews; the [RFC9608 audit](no-revocation.md) covers the revocation exception. RFC 5914 is a newly explicit normative dependency for trust-anchor representation; RFC 5937 supplies optional initialization guidance. Neither reference should be described as implemented merely because a platform trust store is used.

Sources: [RFC 6818](https://www.rfc-editor.org/rfc/rfc6818.html), [metadata](https://www.rfc-editor.org/rfc/rfc6818.json), [current errata](https://errata.rfc-editor.org/search/?rfc_number=6818). Private ledger: `rfc6818-review-candidate.json`, with source SHA-256 and 15 section/end-matter dispositions. Metadata and errata read on 20 October 2026.
