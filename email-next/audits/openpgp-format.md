---
title: OpenPGP format audit
sectionNav: true
---

# OpenPGP format audit

[OpenPGP](https://www.rfc-editor.org/rfc/rfc9580.html) supplies encrypted message packets, signatures, certificates and authenticated capability preferences. It leaves mailbox ownership, contact discovery, account recovery and conversation membership to the application. Email Next can reuse the cryptographic formats without asking users to manage packet formats or infer trust from a key ID.

The complete RFC9580 text has been read, including all tables, algorithms, examples, references and appendices. All nine records in the captured RFC Editor errata corpus were also read. This is a source review, not a cryptographic implementation or interoperability test. Captured official metadata lists no updating or obsoleting RFC; the live information page confirms Proposed Standard status and the replacement of RFC4880, RFC5581 and RFC6637. The live all-status listing on 20 October 2026 matches all nine captured records in ID, status, original/corrected text and notes; current metadata matches the recorded relationships. Referenced cryptographic dependencies require their own review.

## What this contributes

Self-signatures can authenticate preferences and supported features. Their scope matters: a preference attached to one User ID is not automatically a preference for every identity on that certificate. A valid self-signature also does not prove that the person controlling a mailbox owns the key. Discovery and identity checks remain separate requirements.

The Intended Recipient Fingerprint subpacket helps detect a signed message transplanted into another encrypted context. This is useful for a conversation protocol: signing content alone does not establish who was meant to receive it. Neither this subpacket nor anonymous recipient envelopes conceal the SMTP recipients from the mail infrastructure.

Literal-data filenames and timestamps, armor headers, and unhashed signature annotations are not authenticated application instructions. A client must not use them to authorize a structured reply, change a conversation's membership or select an action endpoint. The [security model](../security) governs those decisions after verification of the protected representation.

## A possible reply shortcut

[Section 13.8](https://www.rfc-editor.org/rfc/rfc9580.html#section-13.8) describes replying with a reused session key and fresh message salt. This can support an encrypted reply when the client lacks recipients' certificates. It is useful prior art for automatic encryption, but it changes access in ways a conversation interface can easily hide.

Someone removed from the visible recipient list can still possess that session key. Someone added later can gain access to earlier ciphertext encrypted with it. Drafts, resuming a conversation on another client, and modified recipient lists introduce further risks. Intended-recipient signatures and recipient consistency checks help, but do not revoke a known key.

This review therefore treats reuse as a research option, not the proposed default. Adopting it would require an explicit application profile covering membership changes, history access, expired or revoked keys, drafts, device changes and user control. Fresh public-key encryption remains the simpler boundary for changing recipients.

## Section review

A row naming a range or “all subparts” applies its disposition to every section in that range, including nested subsections. The source algorithms and wire tables remain authoritative; this table records their effect on Email Next rather than reproducing a cryptographic specification.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1, 1.1 | Scope and terms | Reuse the format and security requirements; do not mistake this format standard for a complete identity or key-management service. |
| 2, 2.1 | Encryption | Separate content encryption from wrapping a session key for each recipient. Reconcile the normal fresh-key model with the explicitly constrained reuse option in 13.8. |
| 2.2 | Signatures | Verification binds bytes to a key; mailbox identity and authority require application policy. |
| 2.3–2.5 | Compression, armor and signature-only use | Compression is optional, armor is a transport representation, and a signature-only subset is not full OpenPGP conformance. |
| 3, 3.1–3.2.1 | Scalars and MPIs | Validate lengths and canonical representation. Native algorithm encodings are not universally big-endian integers. |
| 3.3 | Identifiers | Key IDs need not be unique. Preserve full fingerprints, key versions and identity context. |
| 3.4–3.6 | Text, time and keyrings | Respect UTF-8 and timestamp encoding; storage and account synchronization remain outside this format. |
| 3.7–3.7.1.4 | Passphrase derivation | Apply each S2K generation restriction. Iterated S2K counts octets; Argon2 encodes a memory exponent. Validate resource requirements before allocation. |
| 3.7.2–3.7.2.2 | S2K use | Distinguish encrypted secret-key storage from symmetric message encryption. The secret-key Argon2 requirement does not prohibit Argon2 in a version 4 SKESK. |
| 4, 4.1 | Packet boundaries | Inner lengths cannot escape their enclosing packet. Do not recover malformed data by scanning arbitrary bytes for a convenient packet. |
| 4.2–4.2.3, all subparts | Packet headers and lengths | Implement definite, partial and historical forms with their generation restrictions. Partial lengths are limited to the specified packet types. |
| 4.3 | Criticality | Unknown critical packet types invalidate the sequence; unknown noncritical types are ignored. This differs from an invalid individual signature. |
| 5 | Packet registry | Packet identifiers and their criticality are protocol facts, not freely reusable Email Next extension points. |
| 5.1–5.1.2 | Recipient envelopes | Couple PKESK versions to the encrypted data version. Key version and envelope version are different fields. |
| 5.1.3–5.1.4 | RSA and Elgamal envelopes | Follow wrapping rules and later algorithm restrictions; legacy parsing is not permission to generate new Elgamal ciphertext. |
| 5.1.5–5.1.7 | ECDH and native X25519/X448 | These use distinct encodings and derivation rules. Preserve recipient binding and the version-dependent algorithm octet corrected by erratum 8847. |
| 5.1.8 | Anonymous recipients | Omitting a key identifier requires key trials; it does not hide SMTP addressing. |
| 5.2, 5.2.1 | Signature versions and purposes | Signature type and signing-key authority are both required to interpret a valid signature. |
| 5.2.1.1–5.2.1.3 | Document and standalone signatures | Define exact protected bytes. Text canonicalization differs from binary signing; a standalone signature does not sign adjacent content. |
| 5.2.1.4–5.2.1.7 | Certifications | Certification assurance is an issuer's assertion, not an independently verified mailbox binding. |
| 5.2.1.8–5.2.1.9 | Subkey bindings | Check both binding directions where required, including the signing subkey's back signature. |
| 5.2.1.10–5.2.1.13 | Direct-key and revocation signatures | Verify issuer authority, target and ordering. A revocation of one certification does not have unrestricted scope. |
| 5.2.1.14–5.2.1.16 | Other signature types | A timestamp is not independent trusted time; confirmation signs the specified signature representation. Never generate or validate the reserved type. |
| 5.2.2 | Version 3 signatures | Historical reading only; the short hash prefix is a rejection aid, not verification. |
| 5.2.3 | Versions 4 and 6 | Honor different lengths, salt and native signature encodings; apply erratum 8454. |
| 5.2.3.1–5.2.3.5, including 5.2.3.3.1 | Algorithm-specific signatures | Implement the actual RSA, DSA/ECDSA, legacy EdDSA and native Ed25519/Ed448 formats. Native values are not generic MPIs. |
| 5.2.3.6–5.2.3.9 | Signature subpackets | Validate framing, hashed versus unhashed scope, criticality and repeated-field semantics. An unverified issuer hint cannot choose an identity by itself. |
| 5.2.3.10 | Self-signatures | Use the latest valid self-signature for its object. Version 6 direct-key requirements prevent stripping essential preferences; User ID assertions still need an identity policy. |
| 5.2.3.11–5.2.3.18 | Times and preferences | Require the specified hashed creation time; distinguish key expiry from signature expiry and version 1 cipher preferences from version 2 AEAD pairs. |
| 5.2.3.19–5.2.3.23 | Certification controls and revocation keys | Preserve export restrictions and trust scope. Deprecated designated revokers are not a new account-recovery design. |
| 5.2.3.24 | Notation data | A possible namespaced extension point, with explicit semantics and hashed protection. Generic notation support does not imply understanding every critical notation. |
| 5.2.3.25–5.2.3.28 | Key servers, identity preference and policy URI | These preferences do not authorize arbitrary network fetches or prove the safety of a linked service. |
| 5.2.3.29–5.2.3.30 | Key flags and signer identity | Interpret flags in issuer context. Group/split-key flags are not device enrollment proofs. |
| 5.2.3.31 | Revocation reason | Compromise and ordinary retirement have different effects on earlier signatures. Preserve that distinction in recovery and history views. |
| 5.2.3.32–5.2.3.35 | Features, targets, embedded signatures and issuer fingerprints | Authenticate capability claims and validate their scope and version; do not confuse a fingerprint hint with successful verification. |
| 5.2.3.36 | Intended recipients | Bind the encrypted context to intended primary-key fingerprints, including when a subkey decrypts. This helps resist signed-message transplantation. |
| 5.2.4–5.2.4.1 | Signed representation | Follow version-specific prefixes, lengths, salts and trailers. Do not reconstruct signed bytes from a rendered conversation. |
| 5.2.5 | Invalid or unknown signatures | An unusable signature is not a valid identity claim; it need not invalidate independent signatures. Apply the same established protection expectation to absent and failed signatures. |
| 5.3–5.3.2 | Symmetric envelopes | Keep version 4 and 6 derivation, salts and authenticated wrapping separate. A password path is a separate access path, not automatically equivalent protection. |
| 5.4 | One-pass signatures | Match versions, salts and fingerprints; nested signatures close in reverse order. |
| 5.5–5.5.1.4 | Key packet variants | Distinguish primary/subkey and public/secret material before export or distribution. |
| 5.5.2–5.5.2.3 | Public key versions | Prefer current generation rules; historical support does not authorize new version 3 keys. |
| 5.5.3 | Secret keys | Apply S2K protection rules, public-field binding and strict length validation. Erratum 8465 identifies native secret encodings omitted by generic MPI wording. |
| 5.5.4–5.5.4.3 | Fingerprints | Version 4 and 6 use different hashes, packet prefixes and key-ID portions. Preserve version when storing or comparing identifiers. |
| 5.5.5–5.5.5.10, all subparts | Key algorithm fields | Follow each algorithm's MPI, fixed-width, seed and scalar encoding, including 5.5.5.6.1.1. Legacy Curve25519 representation is not native X25519. |
| 5.6 | Compression | Compress packet sequences. ZLIB retains its framing and checksum; ZIP uses raw DEFLATE, as clarified by erratum 8814. |
| 5.7 | Unauthenticated encrypted data | Do not generate SED. Any permitted legacy reading must retain the missing-integrity warning. The quick check is not authentication. |
| 5.8 | Marker | Ignore the defined marker; do not give it application meaning. |
| 5.9–5.9.1 | Literal data | Filename, format and timestamp are not covered by a document signature. Keep consequential conversation metadata inside the signed representation. |
| 5.10–5.12.1 | Trust, User IDs and attributes | Ignore imported local-trust packets; treat identity strings and images as untrusted until verified under an identity policy. |
| 5.13–5.13.1 | Version 1 integrity protection | Verify MDC before treating plaintext as trustworthy; legacy SHA-1 use is not general permission for new SHA-1 signatures. |
| 5.13.2–5.13.5 | Version 2 AEAD | Validate chunk sizes, per-chunk nonces/tags and final length authentication for EAX, OCB and GCM. A truncated stream is not a complete valid message. |
| 5.14 | Padding | Padding can obscure size; it neither hides mail addressing nor supplies a traffic-analysis policy by itself. |
| 6–6.1.1 | Armor and CRC | CRC is not integrity protection. Apply the rules against rejecting a message for CRC absence or mismatch, and against generating it in specified new contexts. |
| 6.2–6.2.3, all subparts | Armor structure and headers | Armor metadata is unauthenticated. Avoid unnecessary implementation-version disclosure; headers do not authorize application behavior. |
| 7–7.3 | Cleartext signatures | Trailing whitespace handling prevents exact round-trip preservation. Use the MIME profile and an explicit signed-byte representation for structured data. |
| 8 | Regular expressions | Use the specified grammar and Unicode interpretation; do not silently substitute an implementation's unrestricted regex language. |
| 9–9.2.1 | Public-key algorithms and curves | Honor current mandatory algorithms, deprecated generation and version-specific curve/OID encodings; old implementations have different baselines. |
| 9.3–9.4 | Symmetric algorithms and compression | AES-128 and uncompressed processing are baseline requirements; legacy cipher decryption does not permit new encryption with those ciphers. |
| 9.5 | Hashes | Apply separate generation, verification, S2K and legacy-storage restrictions. A signed date alone cannot establish that a weak historical signature is safe. |
| 9.6 | AEAD algorithms | OCB is required by this baseline. Optional EAX/GCM have different nonce lengths; do not substitute a generic AEAD layout. |
| 10–10.1.5 | Transferable public keys | Apply the full version-specific grammar, direct-key signatures, subkey bindings, revocation sequences and padding rules. |
| 10.2 | Transferable secret keys | A public-looking export containing a secret packet is secret material; inspect the sequence before publishing it. |
| 10.3–10.3.2.2, all subparts | Messages and version coupling | Validate nesting and pair encrypted envelope/data versions. Key/signature/one-pass versions must agree under their specified mapping. |
| 10.4 | Detached signatures | Parse the complete allowable signature sequence; independently verify each relevant signature. |
| 11–11.3.2, all subparts | ECC representations | Distinguish SEC1, prefixed native, scalar and octet-string formats. Erratum 8466 limits obsolete universal MPI wording. |
| 11.4–11.5.1 | ECDH derivation and wrapping | Bind curve, algorithms and recipient fingerprint. Use fresh ephemeral material per recipient and the version-specific KDF/wrapping requirements. |
| 12–12.1.3 | PKCS#1 | Use RFC8017 and uniform, constant-time failure handling. A detailed decoding error must not become an oracle. |
| 12.2–12.3.2, all subparts | Algorithm preferences | Select a supported recipient intersection with specified implicit defaults. Algorithm zero for uncompressed preference does not define a compressed packet algorithm. |
| 12.4–12.6 | Legacy public-key algorithms | Enforce RSA size limits and DSA/Elgamal generation/use prohibitions. Retained old decryption needs the prescribed warnings. |
| 12.7 | EdDSA | OpenPGP uses PureEdDSA over its computed digest, not an interchangeable Ed25519ph operation. |
| 12.8–12.11 | Reserved values, CFB and expansion | Private identifiers are not interoperable allocations. Incompatible features require discovery or a justified compatibility argument. |
| 13–13.3 | Hashes, salts and side channels | Use current security guidance, fresh signature salt and resistant implementations; salt does not replace identity authentication. |
| 13.4–13.5 | Decryption oracles | Keep quick-check, padding and integrity failure behavior from leaking secret-dependent distinctions. |
| 13.6 | Fingerprint usability | Prefer reliable mechanical comparison over requiring users to compare long hexadecimal strings. |
| 13.7 | Ciphertext integrity | Do not parse or release AEAD plaintext after tag failure. Authenticated earlier chunks on truncation do not authorize a partial structured event. |
| 13.8 | Session-key reuse | Research only until membership, history, drafts, device changes and user-control rules are defined. Reuse cannot revoke a recipient's known key. |
| 13.9 | Escrowed revocation | Revocation escrow can assist recovery but is not an automatic account-recovery or device-enrollment protocol. |
| 13.10–13.11 | Randomness and traffic analysis | Use established secure randomness; padding only addresses part of observable traffic. |
| 13.12–13.13 | Forwarding and subpacket authority | Use intended-recipient context against transplantation; unhashed annotations cannot supply authenticated capabilities. |
| 13.14 | Malicious compression | Bound resource consumption and nesting; prevent crash reports from leaking decrypted content. |
| 14–14.1 | Implementation and fingerprint migration | Preserve full version 6 identifiers. Do not silently truncate them into old 20-byte fields; MIME armor requirements remain a separate profile obligation. |
| 15–15.6.3.3, all subparts | Registries | Follow each registry's allocation policy and coordinated version changes. This review allocates no Email Next identifier. |
| 16–16.2 | References | Treat cited standards as dependencies, not as reviewed merely because their reference entries were read. |
| Appendix A–A.12.3, all subparts | Test vectors | All key, signature, S2K, wrapping and EAX/OCB/GCM vectors and intermediate values were read. They remain unexecuted acceptance-test inputs; public sample secrets are not credentials. |
| Appendix B, B.1 | Migration and terms | The summary does not weaken generation prohibitions in the main text. Migration changes fingerprints, capabilities and identity handling. |
| Appendix C; end matter | Incorporated old errata and attribution | Historical RFC4880 corrections do not close current RFC9580 errata. Attribution carries no protocol requirements. |

## Errata and source issues

The captured [RFC Editor records](https://www.rfc-editor.org/errata/rfc9580) contain seven Verified, one Held for Document Update and one Reported erratum. Their status matters: a reported alternative is not an adopted correction.

| Record | Status | Disposition |
| --- | --- | --- |
| [8432](https://www.rfc-editor.org/errata/eid8432) | Verified | Repair the broken SP800-56A reference URL; no wire-format change. |
| [8449](https://www.rfc-editor.org/errata/eid8449) | Held for Document Update | The User ID mailbox convention needs broader repair. Neither `name-addr` nor `mailbox` parsing establishes ownership. |
| [8454](https://www.rfc-editor.org/errata/eid8454) | Verified | Signature fields can be native octets, not only MPIs; follow the algorithm-specific encoding. |
| [8465](https://www.rfc-editor.org/errata/eid8465) | Verified | Generic secret-key MPI wording misses native encodings. The replacement is marked TBD; do not present it as a finished replacement rule. |
| [8466](https://www.rfc-editor.org/errata/eid8466) | Verified | Universal EC-point MPI wording is a legacy holdover. Native X25519/X448 and Ed25519/Ed448 formats remain distinct; the replacement is marked TBD. |
| [8814](https://www.rfc-editor.org/errata/eid8814) | Verified | ZLIB includes headers/checksum. Only the ZIP form is raw DEFLATE. |
| [8847](https://www.rfc-editor.org/errata/eid8847) | Verified | The X25519/X448 envelope summary omits the clear symmetric algorithm identifier for version 3. Sections 5.1.6 and 5.1.7 specify it. Registry correction should be checked separately. |
| [9094](https://www.rfc-editor.org/errata/eid9094) | Verified | The PKCS#1 reference is version 2.2, RFC8017. |
| [9218](https://www.rfc-editor.org/errata/eid9218) | Reported | Armor whitespace and the 76-character limit have competing proposed clarifications. Do not select one as an accepted correction. |

Several additional wording or annotation issues need confirmation before implementation: section 9.5 conflates version 4 fingerprint hashing with MDC use; the ECDH synopsis does not express the version-dependent omission of the symmetric algorithm identifier; and some vector annotations describe encoded lengths or memory exponents imprecisely. Use the explicit field definitions when building tests, and report confirmed discrepancies upstream. No new erratum has been submitted by this review.

## Acceptance work still needed

A library-backed implementation needs known-answer tests for the selected algorithms and packet versions, malformed-length and critical-packet tests, certificate/revocation tests, and decryption-failure tests that check both data release and observable error behavior. Run the published vectors rather than treating their presence as validation.

Email Next also needs tests above the cryptographic layer: conflicting capability claims, recipient changes, copied signed content, unsigned metadata, missing or failed signatures, truncated encrypted events and cross-device history reconstruction. Those tests must verify the [delivery policy](../delivery-policy) and [security model](../security), not merely that a cryptographic operation returned success.
