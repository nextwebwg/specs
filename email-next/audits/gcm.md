---
title: GCM authenticated encryption
sectionNav: true
---

# GCM authenticated encryption

The selected suite uses AES-128-GCM with a 12-octet nonce and a 16-octet authentication tag. [NIST SP800-38D](https://doi.org/10.6028/NIST.SP.800-38D) defines GCM's authenticated encryption and decryption. The enclosing MLS and HPKE specifications determine the keys, nonces, associated data and wire framing; this audit does not replace those constructions.

## Encryption and verified decryption

GCM encrypts plaintext and authenticates both the ciphertext and additional authenticated data (AAD). AAD is not encrypted. Its GHASH component is not a standalone cryptographic hash, and its hash subkey and other intermediate values must remain secret.

For a 96-bit nonce, GCM constructs its initial block by appending the specified 32-bit suffix. Encryption uses the incremented counter; authentication covers the padded AAD and ciphertext together with their encoded bit lengths. These are primitive internals, not application serialization rules.

Authenticated decryption first rejects unsupported lengths, including an incorrect tag length. It returns plaintext only when the computed tag matches; otherwise it returns failure. The fact that an implementation may calculate plaintext internally before checking the tag does not authorize exposing that plaintext to the application.

## Limits and nonce lifecycle

| Requirement | Consequence for the selected profile |
| --- | --- |
| Plaintext at most 2³⁹−256 bits per invocation | Equivalent to 2³⁶−32 octets. Smaller protocol and library limits still apply. |
| AAD at most 2⁶⁴−1 bits, with byte-aligned input | Equivalent to at most 2⁶¹−1 whole octets; this is not an Email Next message-size allowance. |
| One fixed supported tag length per key | The selected 128-bit tag is not negotiable down to a short tag by an individual message. |
| Nonce uniqueness across all instances using a key | Device copies, concurrent writers, restore and rollback must not repeat encryption inputs under a previously used nonce and key. |
| Construction-dependent invocation limits | Section 8.3's global 2³² encryption-invocation cap applies unless the implementation exclusively uses the specified deterministic 96-bit IV construction. That exception does not remove the deterministic fields' lifetime limits or other protocol security bounds. |

Section 8 requires the probability of invoking encryption with the same key and IV on distinct input sets to be no greater than 2⁻³². Its deterministic construction assigns distinct context and invocation fields; its random construction requires at least 96 random bits and independent generator instances. These frameworks must not be mixed for the same supported IV length and key. The audit does not establish that the current library integrations satisfy every lifecycle condition merely because their nonces have the right length.

Appendix B also recommends monitoring and, when necessary, limiting failed verification attempts per key, and limiting the total protected data during a key's lifetime. Small individual messages do not establish those aggregate properties. These are source requirements and guidance to map against the actual protocol and deployment; this audit adds no arbitrary application quota.

## What GCM does not establish

Successful decryption does not independently establish a mailbox identity or prevent replay. The enclosing protocol must enforce identity, context and replay rules. Repeating a nonce during encryption can undermine both confidentiality and authentication, including recovery of the GHASH subkey. Restart and backup recovery are therefore security behavior, not just persistence details.

GMAC, alternative IV lengths and the 32/64-bit tag modes were read but are not enabled by this profile. The short-tag tables are not limits for the selected 128-bit tag. Section 9 explicitly distinguishes requirements for validated modules from recommendations available to nonvalidated implementations; the local experiments do not claim NIST module validation.

## Publication and evidence

The [official publication page](https://csrc.nist.gov/pubs/sp/800/38/d/final) identifies the November 2007 edition. Its linked [revision decision](https://csrc.nist.gov/News/2024/nist-to-revise-sp-80038d-gcm-and-gmac-modes) plans to remove tags below 96 bits, clarify IV construction including TLS 1.3, and update references. This announcement does not itself certify the MLS or HPKE implementation. The publication page listed no supplemental material when checked on 20 October 2026; no universal absence-of-errata claim is made.

All 39 PDF pages were read, including every component, both authenticated algorithms, operational constraints, all appendices and bibliography. Visual checks covered PDF pages 16, 20, 21, 23, 25 and 29 for limits and equations. The private ledger records 24 scope dispositions and exact extracted-text reading ranges. PDF page numbers count from the cover; printed page numbers are eight lower in the main text.

- PDF SHA256: `d99f3921ccebca049e7522426553aba071dae14ec3d5b6041e8c111a6cb57bba`.
- Extracted-text SHA256: `ff780336c2797ef48708c5e49aee7f0f72405653677059bdc395260a823b017d`.

No algorithm, attack or vector was executed in this review. The selected [AES/FIPS197](aes.md) and [SHA-512 equations inside Ed25519](sha256.md) have separate source reviews. Current validation guidance and implementation-level nonce/usage evidence remain separate work. This non-RFC audit does not change the RFC inventory count.
