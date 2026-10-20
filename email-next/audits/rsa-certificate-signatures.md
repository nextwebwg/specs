---
title: RSA certificate signatures
sectionNav: true
---

# RSA certificate signatures

The local HTTPS fixtures use RSA certificates signed with SHA-256 and PKCS #1 v1.5. That observation does not define the algorithms a deployed service accepts. The helper delegates certificate and handshake signatures to its TLS library; these are separate selections.

See [certificate backends and randomness](certificate-backends.md) for the portable adapter boundary, EC/EdDSA certificate profiles and local vault nonce lifecycle.

## Verify the complete signature encoding

Verification checks signature length and the representative's range, performs the RSA public operation, and compares the recovered encoding with the expected encoding of the message. Comparing only a recovered digest is insufficient unless the alternative verifier also enforces the encoding. The selected encoding includes the hash identifier, DER DigestInfo and padding. Historical BER compatibility is not equivalent to satisfying the DER form. [RFC 8017 §§5.2.2, 8.2.2 and 9.2](https://www.rfc-editor.org/rfc/rfc8017.html#section-8.2.2)

The SHA-256 certificate-signature identifier is `1.2.840.113549.1.1.11`. Verified erratum 5154 corrects the adjacent SHA-224 table label, not this identifier. [RFC 8017 Appendix A.2.4](https://www.rfc-editor.org/rfc/rfc8017.html#appendix-A.2.4), [erratum 5154](https://www.rfc-editor.org/errata/eid5154)

## RSA-PSS in TLS

PSS verification also checks the encoded size, trailer, unused high bits, padding, salt and recomputed hash. MGF1 produces its mask from the seed and four-byte counters. These parameters belong to the selected signature scheme; generic library defaults cannot replace them. [RFC 8017 §§8.1.2, 9.1 and B.2.1](https://www.rfc-editor.org/rfc/rfc8017.html#section-8.1.2)

TLS 1.3 requires MGF1 to use the selected digest and the salt length to equal that digest’s output length. Its RSAE and PSS variants have different certificate public-key identifiers; PSS certificate parameters have additional matching constraints. A PKCS #1 v1.5 certificate signature therefore does not describe the handshake signature. [RFC 8446 §4.2.3](https://www.rfc-editor.org/rfc/rfc8446.html#section-4.2.3)

## Certificate parameters have their own rules

A PSS-restricted public key is usable only for PSS. Its key parameters may be absent; signature parameters must be present. Where key restrictions exist, the certificate profile compares the signature parameters with them, including its salt-length minimum. Apply the additional TLS constraints when selecting a TLS signature scheme. [RFC 4055 §§1.2 and 3](https://www.rfc-editor.org/rfc/rfc4055.html#section-3), [RFC 5756 §2](https://www.rfc-editor.org/rfc/rfc5756.html#section-2)

Do not turn an encoding rule for issuers into a stricter verifier rule. For SHA-2 PKCS #1 v1.5 certificate signatures, the profile requires validators to accept both absent and NULL parameters. Its hash-identifier rules also accept both forms. [RFC 4055 §§2.1 and 5](https://www.rfc-editor.org/rfc/rfc4055.html#section-5)

These historical documents do not authorize SHA-1 or small RSA keys in the selected TLS profile. Current TLS policy remains applicable. OAEP key transport is outside this selection. The review includes the applicable RFC 5756 parameter-placement update and captured errata dispositions; the live all-status listings for RFC8017, RFC4055 and RFC5756 were reconciled on 20 October 2026, matching captured IDs, statuses, original/corrected text and notes.

## DER is a precise encoding

The selected certificate structures use DER, not every encoding that a BER decoder can read. DER requires minimal definite lengths, primitive string encodings, canonical true values, zero unused bits, omitted default-valued components and ordered sets. Integers retain minimal signed representation; object-identifier components use minimal encodings. Sequence order, explicit versus implicit tags, and the distinction between SET and SET OF remain significant. [X.690 (2021), §§8.1–8.3, 8.6–8.15, 8.19, 10 and 11](https://www.itu.int/rec/T-REC-X.690-202102-I/en)

Character strings retain their declared type. DER time encodings include seconds and UTC notation; certificate profiles may impose further restrictions. Do not normalize signed certificate bytes into a different representation before verification. The 2021 erratum corrects Figure 4's high-tag continuation bit, consistently with the textual rule. [X.690 §§8.23, 8.25 and 11.7–11.8](https://www.itu.int/rec/T-REC-X.690-202102-I/en), [Erratum 1](https://www.itu.int/rec/T-REC-X.690-202109-I!Err1/en)

ASN.1 types also carry meaning beyond their tag bytes. An omitted DEFAULT has its specified value; it is not an absent or null value. Named-bit strings have special trailing-zero semantics, which must not be applied to arbitrary signature bits. SET OF can contain repeated values. Explicit and implicit tagging follow the module and type rules; an untagged CHOICE cannot simply acquire implicit tagging. These distinctions matter when interpreting certificate structures. [X.680 (2021), §§22, 25, 28–29 and 31](https://www.itu.int/rec/T-REC-X.680-202102-I/en)

These selected encoding and type rules do not complete the ASN.1 schema, legacy name-comparison or malformed-certificate implementation review. Module tagging defaults do not reinterpret imported types. PrintableString is a defined restricted repertoire, not arbitrary printable ASCII; BMPString and UTF8String remain distinct types. These definitions must be preserved when reading certificate names. [X.680 §§13 and 41](https://www.itu.int/rec/T-REC-X.680-202102-I/en)

Size constraints count the units of the declared type: characters, octets, bits or component values. A character limit is not an encoded-byte limit, and a collection bound differs from a bound on each element. [X.680 §§49–51.8](https://www.itu.int/rec/T-REC-X.680-202102-I/en)

Legacy character repertoire dependencies and the concrete certificate module imports remain separate work.

## Read the module with its corrections

The certificate modules describe names, validity, key information and extensions; successful decoding does not establish certificate-path validity. Their extension criticality constraint is not fully enforced by the module declaration. Apply the certificate profile's rules as well. [RFC 5912 §§2 and 14](https://www.rfc-editor.org/rfc/rfc5912.html#section-14)

For the `rsaEncryption` public-key identifier, verified erratum 6806 changes the module's parameters from absent to required NULL. This concerns the public key, not the SHA-2 certificate-signature rule that accepts absent or NULL parameters. [Erratum 6806](https://www.rfc-editor.org/errata/eid6806)

PSS uses different parameter rules for keys and signatures: key parameters may be absent, while signature parameters are required. Inside PSS parameters, omitted fields mean SHA-1, MGF1 with SHA-1, a 20-byte salt and trailer field 1. They do not inherit the negotiated TLS signature scheme. MGF1 itself carries a nested hash identifier. A validator must interpret those values before checking the selected scheme. [RFC 5912 §8](https://www.rfc-editor.org/rfc/rfc5912.html#section-8)

The captured corrections also restore `anyPolicy`, use the named CRLNumber type, include authority-information access among CRL extensions, and reuse the declared name-attribute types. Rejected reports are not amendments. This selected module review does not implement OCSP, certificate management or X.400 mail delivery. The selected information-object rules are explained below. The RFC 5912 errata set contains eight Verified corrections and two Rejected reports. Its CMP module updates do not change this selected certificate-validation branch; OCSP processing is covered by the [certificate-status audit](certificate-status.md). [RFC 5912 errata](https://www.rfc-editor.org/errata/rfc5912), [RFC 9810 Appendix F](https://www.rfc-editor.org/rfc/rfc9810.html#appendix-F)

## Coverage boundary

This review covers public-key representation, the verification primitive, PKCS #1 v1.5 verification and encoding, RSA-PSS verification and encoding, MGF1, their selected ASN.1 declarations, and the selected certificate parameter rules in RFC 4055 as updated by RFC 5756. Earlier integer/octet conversion coverage remains applicable. It does not cover all certificate algorithms, full ASN.1/DER validation, key generation or implementation resistance to attacks. The errata disposition remains scoped to the reviewed algorithms. Current metadata confirms RFC5756 updates RFC4055; RFC8017 and RFC5756 list no further updates or replacements.

The [service contract](../service-answers.md) still needs a deployment algorithm policy and revocation binding. Local certificate success does not close those requirements or prove a complete certificate validator.

## Algorithm tables and open types

The module's algorithm identifier selects both an identifier and its associated parameter type. ASN.1 open types are not arbitrary bytes with an implied tag: they cannot be implicitly tagged, and their encoding must allow other fields to be decoded without knowing the selected type. Object-set extensibility does not automatically make the containing type extensible. These rules describe schema interpretation; they do not authorize an unknown algorithm or override certificate-extension policy. [X.681 (2021), §§9 and 12–14](https://www.itu.int/rec/T-REC-X.681-202102-I/en)

A component-relation constraint ties parameters to the row selected by the algorithm identifier. But an absent optional component satisfies that constraint: the generic `AlgorithmIdentifier` structure cannot by itself enforce an algorithm's requirement that parameters be present. Apply the selected algorithm's presence rule as well. A parameterized type also retains the actual parameter's original naming and tagging environment; it is not textual substitution. [X.682 §10](https://www.itu.int/rec/T-REC-X.682-202102-I/en), [X.683 §§8–9](https://www.itu.int/rec/T-REC-X.683-202102-I/en), [RFC 5912 §3](https://www.rfc-editor.org/rfc/rfc5912.html#section-3)

The selected schema rules are reviewed. Their enforcement by a particular certificate backend still needs implementation evidence; this review does not certify a decoder or the complete ASN.1 standards.
