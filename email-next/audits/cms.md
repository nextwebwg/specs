---
title: CMS content protection audit
sectionNav: true
---

# CMS content protection audit

CMS defines the protected containers used by S/MIME. Correct parsing is only the first step: receivers must verify the exact protected bytes, certificate authority and application meaning separately. The Email/2 MLS experiment is not a CMS or S/MIME implementation.

RFC8933 updates the signature rules to require the same digest algorithm for content and signed attributes, and recommends protecting algorithm identifiers. RFC9629 adds optional KEM recipient information; it does not make every CMS implementation quantum-safe or change the selected MLS suite.

## Review coverage

Complete base texts, numbered sections, modules where present, references and end matter were reviewed: [RFC5652](https://www.rfc-editor.org/rfc/rfc5652.html), [RFC8933](https://www.rfc-editor.org/rfc/rfc8933.html), [RFC9629](https://www.rfc-editor.org/rfc/rfc9629.html). Official metadata lists RFC8933 and RFC9629 as updates to RFC5652 and no updates to RFC8550. Source review does not establish implementation, ASN.1 compiler or interoperability conformance.

::: {.details summary="RFC5652 section dispositions"}

| Section | Disposition |
| --- | --- |
| 1 — Introduction | CMS evolution, recipient extension mechanisms and multiple-signature clarification reviewed; historical algorithms are not selected by syntax compatibility. |
| 1.1 — Evolution of the CMS | CMS evolution, recipient extension mechanisms and multiple-signature clarification reviewed; historical algorithms are not selected by syntax compatibility. |
| 1.1.1 — Changes Since PKCS #7 Version 1.5 | CMS evolution, recipient extension mechanisms and multiple-signature clarification reviewed; historical algorithms are not selected by syntax compatibility. |
| 1.1.2 — Changes Since RFC 2630 | CMS evolution, recipient extension mechanisms and multiple-signature clarification reviewed; historical algorithms are not selected by syntax compatibility. |
| 1.1.3 — Changes Since RFC 3369 | CMS evolution, recipient extension mechanisms and multiple-signature clarification reviewed; historical algorithms are not selected by syntax compatibility. |
| 1.1.4 — Changes Since RFC 3852 | CMS evolution, recipient extension mechanisms and multiple-signature clarification reviewed; historical algorithms are not selected by syntax compatibility. |
| 1.2 — Terminology | Requirement terminology and lowest syntax-compatible version reviewed; version is not security capability negotiation. |
| 1.3 — Version Numbers | Requirement terminology and lowest syntax-compatible version reviewed; version is not security capability negotiation. |
| 2 — General Overview | ContentInfo dispatch, required CMS content types and id-data octets reviewed. BER streaming does not remove DER requirements for protected attributes. |
| 3 — General Syntax | ContentInfo dispatch, required CMS content types and id-data octets reviewed. BER streaming does not remove DER requirements for protected attributes. |
| 4 — Data Content Type | ContentInfo dispatch, required CMS content types and id-data octets reviewed. BER streaming does not remove DER requirements for protected attributes. |
| 5 — Signed-data Content Type | Independent signers, per-signer success policy, version decision tree, optional certificate/revocation collections and unknown-algorithm graceful failure reviewed. |
| 5.1 — SignedData Type | Independent signers, per-signer success policy, version decision tree, optional certificate/revocation collections and unknown-algorithm graceful failure reviewed. |
| 5.2 — EncapsulatedContentInfo Type | Detached content and zero-signer certificate transport distinguished from verified content. PKCS#7 non-data wrapping can hash different bytes; compatibility fallback is explicit. |
| 5.2.1 — Compatibility with PKCS #7 | Detached content and zero-signer certificate transport distinguished from verified content. PKCS#7 non-data wrapping can hash different bytes; compatibility fallback is explicit. |
| 5.3 — SignerInfo Type | Signer identifiers, DER SET OF signature input, independently recomputed content digest and matching content type reviewed; apply RFC8933 same-hash update. |
| 5.4 — Message Digest Calculation Process | Signer identifiers, DER SET OF signature input, independently recomputed content digest and matching content type reviewed; apply RFC8933 same-hash update. |
| 5.5 — Signature Generation Process | Signer identifiers, DER SET OF signature input, independently recomputed content digest and matching content type reviewed; apply RFC8933 same-hash update. |
| 5.6 — Signature Verification Process | Signer identifiers, DER SET OF signature input, independently recomputed content digest and matching content type reviewed; apply RFC8933 same-hash update. |
| 6 — Enveloped-data Content Type | Random shared content key, per-recipient wrapping, exact version branches and unknown recipient alternatives reviewed; encrypted content does not authenticate origin. |
| 6.1 — EnvelopedData Type | Random shared content key, per-recipient wrapping, exact version branches and unknown recipient alternatives reviewed; encrypted content does not authenticate origin. |
| 6.2 — RecipientInfo Type | Random shared content key, per-recipient wrapping, exact version branches and unknown recipient alternatives reviewed; encrypted content does not authenticate origin. |
| 6.2.1 — KeyTransRecipientInfo Type | Key transport requires correct recipient identifier/version and keyEncipherment when key usage is present. |
| 6.2.2 — KeyAgreeRecipientInfo Type | Key agreement originator alternatives, UKM, multiple recipients, keyAgreement usage and recipient-key identification reviewed; uncertified originator key can be anonymous. |
| 6.2.3 — KEKRecipientInfo Type | Previously distributed KEKs, password-derived/external keys and extension dispatch are distinct mechanisms; optional support is not assumed. |
| 6.2.4 — PasswordRecipientInfo Type | Previously distributed KEKs, password-derived/external keys and extension dispatch are distinct mechanisms; optional support is not assumed. |
| 6.2.5 — OtherRecipientInfo Type | Previously distributed KEKs, password-derived/external keys and extension dispatch are distinct mechanisms; optional support is not assumed. |
| 6.3 — Content-encryption Process | Content-key generation, unambiguous block padding including aligned inputs, block-size restriction and key-value wrapping reviewed. |
| 6.4 — Key-encryption Process | Content-key generation, unambiguous block padding including aligned inputs, block-size restriction and key-value wrapping reviewed. |
| 7 — Digested-data Content Type | Unkeyed digest is not sender authentication; EncryptedData has no recipient/key-distribution mechanism and requires externally managed keys. |
| 8 — Encrypted-data Content Type | Unkeyed digest is not sender authentication; EncryptedData has no recipient/key-distribution mechanism and requires externally managed keys. |
| 9 — Authenticated-data Content Type | MAC recipient keys, version branches, paired digestAlgorithm/authAttrs presence and mandatory content-type/digest attributes reviewed. |
| 9.1 — AuthenticatedData Type | MAC recipient keys, version branches, paired digestAlgorithm/authAttrs presence and mandatory content-type/digest attributes reviewed. |
| 9.2 — MAC Generation | DER SET OF MAC input and independently recomputed MAC/digest/type checks reviewed; Verified6250 corrects the calculation name. |
| 9.3 — MAC Verification | DER SET OF MAC input and independently recomputed MAC/digest/type checks reviewed; Verified6250 corrects the calculation name. |
| 10 — Useful Types | AlgorithmIdentifier types and parameter roles reviewed; historical examples do not establish currently acceptable algorithms. |
| 10.1 — Algorithm Identifier Types | AlgorithmIdentifier types and parameter roles reviewed; historical examples do not establish currently acceptable algorithms. |
| 10.1.1 — DigestAlgorithmIdentifier | AlgorithmIdentifier types and parameter roles reviewed; historical examples do not establish currently acceptable algorithms. |
| 10.1.2 — SignatureAlgorithmIdentifier | AlgorithmIdentifier types and parameter roles reviewed; historical examples do not establish currently acceptable algorithms. |
| 10.1.3 — KeyEncryptionAlgorithmIdentifier | AlgorithmIdentifier types and parameter roles reviewed; historical examples do not establish currently acceptable algorithms. |
| 10.1.4 — ContentEncryptionAlgorithmIdentifier | AlgorithmIdentifier types and parameter roles reviewed; historical examples do not establish currently acceptable algorithms. |
| 10.1.5 — MessageAuthenticationCodeAlgorithm | AlgorithmIdentifier types and parameter roles reviewed; historical examples do not establish currently acceptable algorithms. |
| 10.1.6 — KeyDerivationAlgorithmIdentifier | AlgorithmIdentifier types and parameter roles reviewed; historical examples do not establish currently acceptable algorithms. |
| 10.2 — Other Useful Types | Revocation and certificate alternatives may be incomplete or unrelated; supplied certificates do not create trusted roots. Obsolete formats retain explicit compatibility status. |
| 10.2.1 — RevocationInfoChoices | Revocation and certificate alternatives may be incomplete or unrelated; supplied certificates do not create trusted roots. Obsolete formats retain explicit compatibility status. |
| 10.2.2 — CertificateChoices | Revocation and certificate alternatives may be incomplete or unrelated; supplied certificates do not create trusted roots. Obsolete formats retain explicit compatibility status. |
| 10.2.3 — CertificateSet | Revocation and certificate alternatives may be incomplete or unrelated; supplied certificates do not create trusted roots. Obsolete formats retain explicit compatibility status. |
| 10.2.4 — IssuerAndSerialNumber | Issuer/serial identity, syntax version, UKM and additional key-attribute identifiers reviewed; selection metadata is not independent authority. |
| 10.2.5 — CMSVersion | Issuer/serial identity, syntax version, UKM and additional key-attribute identifiers reviewed; selection metadata is not independent authority. |
| 10.2.6 — UserKeyingMaterial | Issuer/serial identity, syntax version, UKM and additional key-attribute identifiers reviewed; selection metadata is not independent authority. |
| 10.2.7 — OtherKeyAttribute | Issuer/serial identity, syntax version, UKM and additional key-attribute identifiers reviewed; selection metadata is not independent authority. |
| 11 — Useful Attributes | Protected content-type and digest attributes have exact placement, single-value and duplicate restrictions. |
| 11.1 — Content Type | Protected content-type and digest attributes have exact placement, single-value and duplicate restrictions. |
| 11.2 — Message Digest | Protected content-type and digest attributes have exact placement, single-value and duplicate restrictions. |
| 11.3 — Signing Time | Signing-time encoding and cardinality reviewed; a signed claimed time is not a trustworthy clock or independent timestamp. |
| 11.4 — Countersignature | Countersignature covers signature-value octets, excludes content-type, permits multiple/nested values and does not itself prove original content was examined. |
| 12 — ASN.1 Modules | Both complete ASN.1 modules reviewed, including obsolete compatibility types; Verified6546 fixes the import comment. No compiler conformance claim. |
| 12.1 — CMS ASN.1 Module | Both complete ASN.1 modules reviewed, including obsolete compatibility types; Verified6546 fixes the import comment. No compiler conformance claim. |
| 12.2 — Version 1 Attribute Certificate ASN.1 Module | Both complete ASN.1 modules reviewed, including obsolete compatibility types; Verified6546 fixes the import comment. No compiler conformance claim. |
| 13 — References | All references read; certificate, algorithm and ASN.1 dependencies require separate applicability review. |
| 13.1 — Normative References | All references read; certificate, algorithm and ASN.1 dependencies require separate applicability review. |
| 13.2 — Informative References | All references read; certificate, algorithm and ASN.1 dependencies require separate applicability review. |
| 14 — Security Considerations | Key protection, randomness, weakest algorithm, MAC shared-recipient impersonation and countersigning context risks reviewed. |
| 15 — Acknowledgments | Acknowledgements read; no processing requirements. |

:::

::: {.details summary="RFC8933 section dispositions"}

| Section | Disposition |
| --- | --- |
| 1 — Introduction | Algorithm-substitution threat and terminology reviewed. |
| 2 — Terminology | Algorithm-substitution threat and terminology reviewed. |
| 3 — Required Use of the Same Hash Algorithm | Content and signed-attribute digests must use the same algorithm; recipients recompute rather than trust transmitted digest values. |
| 3.1 — RFC 5652, Section 5.3 | Content and signed-attribute digests must use the same algorithm; recipients recompute rather than trust transmitted digest values. |
| 3.2 — RFC 5652, Section 5.4 | Content and signed-attribute digests must use the same algorithm; recipients recompute rather than trust transmitted digest values. |
| 3.3 — RFC 5652, Section 5.6 | Content and signed-attribute digests must use the same algorithm; recipients recompute rather than trust transmitted digest values. |
| 3.4 — Backward Compatibility Considerations | Mixed-digest legacy signatures become invalid; timestamp token internal hashing is distinct from the embedded original MessageImprint algorithm. |
| 3.5 — Timestamp Compatibility Considerations | Mixed-digest legacy signatures become invalid; timestamp token internal hashing is distinct from the embedded original MessageImprint algorithm. |
| 4 — Recommended Inclusion of the CMSAlgorithmProtection Attribute | CMSAlgorithmProtection is recommended for signed/authenticated attributes; RFC6211 defines the attribute and remains a separate dependency. |
| 4.1 — RFC 5652, Section 14 | CMSAlgorithmProtection is recommended for signed/authenticated attributes; RFC6211 defines the attribute and remains a separate dependency. |
| 5 — IANA Considerations | No IANA actions. |
| 6 — Security Considerations | Algorithm protection does not extend to enveloped, digested, encrypted or authenticated-enveloped data merely because this update is applied. |
| 7 — References | All references and end matter read; timestamp/algorithm-specific dependencies not blanket-selected. |
| 7.1 — Normative References | All references and end matter read; timestamp/algorithm-specific dependencies not blanket-selected. |
| 7.2 — Informative References | All references and end matter read; timestamp/algorithm-specific dependencies not blanket-selected. |

:::

::: {.details summary="RFC9629 section dispositions"}

| Section | Disposition |
| --- | --- |
| 1 — Introduction | Optional CMS KEM extension, terminology, encoding and lowest-version rule reviewed; store-and-forward operation does not require both parties online. |
| 1.1 — Terminology | Optional CMS KEM extension, terminology, encoding and lowest-version rule reviewed; store-and-forward operation does not require both parties online. |
| 1.2 — ASN.1 | Optional CMS KEM extension, terminology, encoding and lowest-version rule reviewed; store-and-forward operation does not require both parties online. |
| 1.3 — CMS Version Numbers | Optional CMS KEM extension, terminology, encoding and lowest-version rule reviewed; store-and-forward operation does not require both parties online. |
| 2 — KEM Processing Overview | Per-recipient encapsulation and KDF produce wrapping keys for a shared content key; complete sender/recipient procedures reviewed. |
| 3 — KEM Recipient Information | Exact KEMRecipientInfo fields, version0, recipient identifiers, keyEncipherment, wrap-consistent KEK length and unsupported UKM failure reviewed. |
| 4 — KEM Algorithm Identifier | Exact KEMRecipientInfo fields, version0, recipient identifiers, keyEncipherment, wrap-consistent KEK length and unsupported UKM failure reviewed. |
| 5 — Key Derivation | DER context binds wrap algorithm, output length and optional UKM; every supplied KDF input must influence output. |
| 6 — ASN.1 Modules | Both complete ASN.1 modules and imports reviewed; compilation and algorithm instantiation not tested. |
| 6.1 — KEMAlgorithmInformation-2023 ASN.1 Module | Both complete ASN.1 modules and imports reviewed; compilation and algorithm instantiation not tested. |
| 6.2 — CMS-KEMRecipientInfo-2023 ASN.1 Module | Both complete ASN.1 modules and imports reviewed; compilation and algorithm instantiation not tested. |
| 7 — Security Considerations | Reusable-key IND-CCA security, fresh per-recipient encapsulation, shared-secret discard, comparable algorithm strength and absent origin authentication reviewed. |
| 8 — IANA Considerations | Three OID assignments recorded from source; current complete registry audit is not claimed. |
| 9 — References | All references and end matter read; optional KEM algorithms and module dependencies are not automatically selected for Email/2. |
| 9.1 — Normative References | All references and end matter read; optional KEM algorithms and module dependencies are not automatically selected for Email/2. |
| 9.2 — Informative References | All references and end matter read; optional KEM algorithms and module dependencies are not automatically selected for Email/2. |

:::

## Errata and update boundary

RFC5652 has six captured errata, reconciled with the live all-status records. **Verified6250** corrects the authenticated-attribute calculation to say MAC; **Verified6546** corrects an ASN.1 import comment. **Held2026** corrects “SignerData”, **Held7863** clarifies the omitted `eContent` field, and **Held3867** concerns digest-algorithm wording. Its older discussion must be read with RFC8933’s later normative same-hash requirement. **Rejected5331** does not change EncryptedData nesting. No errata were returned for RFC8933 or RFC9629.

The [RFC6211 algorithm-protection audit](cms-algorithm-protection.md) covers the updated recommendation’s attribute dependency and records its published-OID/registry discrepancy. Algorithm profiles, external ASN.1 standards, optional attribute certificates and KEM implementations require their own applicable evidence; this audit does not close those dependencies.
