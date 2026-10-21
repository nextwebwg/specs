---
title: Certificate backends and randomness
sectionNav: true
---

# Certificate backends and randomness

A successful RSA fixture does not establish which certificates a TLS adapter accepts. Each adapter records its runtime, cryptographic backend, trust configuration and observed enforcement. RSA and P-256 ECDSA are initial interoperability test targets, not an exhaustive acceptance list. Additional accepted algorithms need their own source mapping and evidence.

The local Python TLS adapter and the certificate-generation library use separate OpenSSL builds. Its explicit choices include TLS 1.3 or later, certificate verification and SAN-only DNS matching. Remaining algorithm choices come from the backend configuration. They must be reported as such rather than presented as a deliberate Email/2 algorithm policy. See [TLS configuration](tls-configuration.md) and [RSA certificate signatures](rsa-certificate-signatures.md).

## Elliptic-curve certificates

EC public keys identify a named curve in their parameters. Missing, implicit and explicitly supplied curve parameters do not meet the selected PKIX encoding. Uncompressed points are required; compressed points are optional; hybrid points are prohibited. Key encoding, point validation and certificate usage are separate checks. [RFC 5480 §§2–4](https://www.rfc-editor.org/rfc/rfc5480.html#section-2)

For ECDSA SHA-2 signatures, the signature AlgorithmIdentifier omits parameters. This differs from the standalone SHA-2 hash identifiers, whose NULL and absent parameters are equivalent. A parser accepting the latter does not justify accepting NULL in the signature identifier. [RFC 5758 §§2–3.2](https://www.rfc-editor.org/rfc/rfc5758.html#section-3.2)

EC certificates cannot assert keyEncipherment or dataEncipherment. This applies to id-ecPublicKey as well as the restricted agreement identifiers. [RFC 8813 §3](https://www.rfc-editor.org/rfc/rfc8813.html#section-3)

Ed25519 and Ed448 certificate identifiers also omit parameters; signatures are carried directly as bytes in the BIT STRING. These signing keys are distinct from X25519/X448 agreement keys. [RFC 8410 §§3–6](https://www.rfc-editor.org/rfc/rfc8410.html#section-3)

The updated usage rules require keyCertSign for a CA when keyUsage is present and prohibit agreement/encipherment uses for EdDSA signing keys. An end-entity usage allowed by that certificate profile is not automatically sufficient for TLS server authentication. [RFC 9295 §3](https://www.rfc-editor.org/rfc/rfc9295.html#section-3)

::: {.details summary="Source corrections and review boundary"}

### Errata dispositions

| Source | Errata | Disposition |
| --- | --- | --- |
| 5480 | 1727, 1728 — held | Editorial wording; no changed encoding |
| 5480 | 4170 — held; 8026 — verified | Historical security-table size/name corrections; no new algorithm policy |
| 5480 | 6670 — verified | Correct nonexistent keyTransport name; apply 8813 usage clarification |
| 5758 | 2013 — held | Missing verb in generation prose; no changed algorithm |
| 8410 | 6738, 6263 — verified | Correct private-key structure quotation/reference to 5958 |
| 8410 | 5459 — held; 8297 — verified | Example PEM delimiter/attribute corrections; examples are not production credentials |
| 8410 | 5696 — held | Apply subsequent 9295 CA usage clarification |
| 8410 | 5707 — held; 7070, 6936, 6229 — reported | Example DER/PEM/authority-identifier concerns; validate generated fixtures independently rather than adopt reported replacements |
| 8410 | 5709 — rejected | Self-issued is not necessarily self-signed; agreement keys cannot verify signing-key signatures |
| 8410 | 7384 — verified | Include missing Ed448 ASN.1 definitions when that algorithm is supported |
| 8410 | 7848 — held | Illustrative field-name correction does not change wire encoding |
| 8410 | 9045 — reported | Agreement-key module/prose discrepancy; retain normative 9295 combinations, not a new accepted erratum |

The selected parameter, signature and usage rules include updates 8813 and 9295; neither had a listed erratum in the captured registry. This is not full closure of every ASN.1 import, curve definition or cryptographic implementation. The selected SEC 1 point/signature ranges and RFC 3279 signature-value encoding are mapped below; this is a range review, not a full review of either publication. Backend tests must distinguish a rejected certificate from a fixture that could not be generated or loaded.

:::

## EC point and signature representation

An EC public key and an ECDSA signature have different encodings. Certificate signatures contain a DER sequence of two integers, `r` and `s`, inside the certificate signature BIT STRING. They are not fixed-width `r || s` bytes. The same two-integer structure applies to DSA. Reading these structures does not select the historical SHA-1 policy in RFC 3279: the SHA-2 identifiers and absent-parameter rules above remain applicable. [RFC 3279 §§2.2.2–2.2.3](https://www.rfc-editor.org/rfc/rfc3279.html#section-2.2.2), [RFC 5758 §§3.1–3.2](https://www.rfc-editor.org/rfc/rfc5758.html#section-3)

Point decoding checks lengths, coordinate ranges and the curve equation. Public-key validation also excludes infinity and checks subgroup membership. For the cofactor-one fixture curves, the subgroup condition follows from the other point checks. ECDSA verification bounds both signature integers, derives the hash integer, computes the verification point and compares its reduced x-coordinate with `r`. A successful fixture is not proof that every malformed input or arithmetic path is handled correctly. [SEC 1 v2 §§2.3, 3.2.2, 4.1.4](https://www.secg.org/sec1-v2.pdf)

::: {.details summary="Selected source ranges, fixture mapping and corrections"}

### Representation and domain parameters

| Source range | Selected meaning |
| --- | --- |
| SEC 1 v1 §§2.3.3–2.3.8; v2 §§2.3.1–2.3.9 | Fixed-width big-endian coordinates; `04` uncompressed, `02`/`03` compressed. RFC 5480 cites v1; the reviewed prime-field conversions agree with v2. The general infinity representation is not an admissible certificate key. |
| SEC 1 v2 §§3.1.1–3.1.1.2.1, 3.2.2–3.2.2.1, 4.1.1–4.1.4 | Domain/key assurance and signature generation/verification; no new curve-generation implementation is selected. |
| SEC 1 v2 Appendix C.5 signature-value paragraphs | General optional acceleration fields and alternative point/integer representation are not inherited into the narrower PKIX two-integer signature structure. |
| SEC 2 v2 §§2.4.2, 2.5.1 | `secp256r1` and `secp384r1` domain tuples, each with cofactor one. RFC 5480 maps these to P-256 and P-384, with OIDs `1.2.840.10045.3.1.7` and `1.3.132.0.34`. |
| RFC 3279 §§2.2.2–2.2.3 and corresponding §3 signature types | Ordered integer-pair signature representation; retain DER rules from the certificate profile. |

Sources: [SEC 1 v1](https://www.secg.org/SEC1-Ver-1.0.pdf), [SEC 1 v2](https://www.secg.org/sec1-v2.pdf), [SEC 2 v2](https://www.secg.org/sec2-v2.pdf), [RFC 5480 §2.1.1.1](https://www.rfc-editor.org/rfc/rfc5480.html#section-2.1.1.1).

`test_certificate_backend.py` generates P-256 and P-384 keys and signs both certificate fixtures with SHA-256. The P-384 fixture therefore does not establish a SHA-384 certificate-signature path. Certificate signatures remain distinct from the negotiated TLS handshake signature scheme. This review maps the source definitions; it neither adds an algorithm allowlist nor independently verifies backend curve arithmetic.

### RFC 3279 updates and errata

The current metadata lists updates 4055, 4491, 5480, 5758 and 8692. For this range, 5480 replaces the old EC public-key parameter profile and 5758 supplies SHA-2 signature identifiers while retaining the signature encoding. The RSA, GOST and SHAKE branches of the other updates do not change this selected SHA-2 ECDSA encoding. Their presence does not enable those branches.

The all-status errata listing captured on 20 October 2026 contains seven records:

| Errata | Disposition for this range |
| --- | --- |
| 307 — verified | Correct the encoding-rules reference to X.690. |
| 2048, 4036 — verified | Binary-field OID and DH subgroup corrections; outside these prime-field signature fixtures. |
| 4102 — verified; 1909 — held | Name and identifier spelling corrections; no signature-value change. |
| 7296 — verified; 6672 — held | Old implicit-parameter wording and usage correction; the selected 5480/8813 profile governs instead. |

[Current RFC metadata](https://www.rfc-editor.org/info/rfc3279), [all-status errata](https://errata.rfc-editor.org/search/?rfc_number=3279&status=any).

SECG lists SEC 1 v2 and SEC 2 v2 as finalized publications; the SEC 2 PDF retains “Draft” running headers. The publisher page provides no all-status errata service comparable to the RFC Editor's. This records the captured versions, not an assertion that no SEC corrections exist. Full SEC documents, all curves, general ASN.1 correctness and exhaustive backend-negative testing are outside this selected-range review.

:::

## Randomness and local vault keys

Use established OS-backed randomness APIs and propagate failure without emitting a credential or committing a cryptographic operation. Platform entropy quality remains a deployment responsibility; these experiments do not establish FIPS validation or entropy-source certification. An API call or a sample without collisions cannot prove those properties.

For the selected random-IV GCM construction, SP 800-38D §8.3 limits encryption invocations to **2³² per key across all instances**, not per database or process. Its random field is at least 96 bits. These are inherited construction requirements, not user quotas. A local counter alone cannot account for a restored or cloned store retaining the same key. Such a deployment needs preserved global accounting or a fresh encryption key before further writes; old keys may remain available for decryption. Immutable ciphertext retries do not require another encryption. The [local writer-owner experiment](../evidence/README.md#local-vault-writer-accounting) reserves invocations independently of application rollback and supports explicit migration; continuity of its separately controlled ledger remains a deployment assumption. [SP 800-38D §§8.1–8.3](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf)

## Enforcement evidence

Current local TLS checks cover SAN matching, trust failure, common-name fallback rejection, wildcard boundaries and rejection of TLS 1.2. Additional local checks cover RSA/P-256, mixed chains, Ed25519/Ed448/P-384, expiry, usage, critical extensions and DNS name constraints. They do not establish the complete certificate matrix above. The adapter additionally checks the original DER from its authenticated chain before returning a service socket. This rejects forbidden parameters on the recognized ECDSA SHA-2, DSA SHA-2 and EdDSA signature identifiers while leaving other algorithms under backend policy. A missing authenticated-chain API fails closed. The returned trust anchor receives an encoding check; its self-signature does not establish trust. Configurable defaults of 32 certificates and 1 MiB per certificate bound this check after backend allocation, not TLS allocation itself.

Validly re-signed ECDSA and Ed25519 fixtures exposed backend acceptance of forbidden NULL parameters; the added check rejects them. The local API preserved their exact DER bytes. RSA-PSS valid signatures, a declared salt-length mismatch, directory-name case/space matching and path-length rejection also have focused evidence. Other adapters must establish their own original-byte preservation and enforcement.

Additional checks must use validly signed negative fixtures where possible, distinguish certificate signatures from TLS handshake signatures, and record backend/version differences. Name constraints, usage, malformed algorithm parameters and accepted additional algorithms require explicit results before an adapter claims them.
