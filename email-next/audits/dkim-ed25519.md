---
title: DKIM Ed25519 update audit
sectionNav: true
---

# DKIM Ed25519 update audit

**Coverage:** Complete seven-page RFC 8463, including all Appendix A key and message examples; rejected erratum 7930 reviewed. [RFC 8463](https://www.rfc-editor.org/rfc/rfc8463.html). Base DKIM and cryptographic dependencies remain open.

| Section | Disposition |
| --- | --- |
| 1 | Adds Ed25519-based DKIM to the RSA baseline; selected message fields/body are hashed, not arbitrary application state. |
| 2 | BCP14 and ABNF extension vocabulary reviewed. |
| 3 | Compute DKIM SHA256 hash then sign that digest with PureEdDSA Ed25519. Do not substitute Ed25519ph or sign the canonicalized headers directly. DNS key type is ed25519. |
| 4 | Extends signature and key tag syntax; all other DKIM parsing/canonicalization still applies. |
| 4.1 | Adds ed25519 algorithm token, forming ed25519-sha256. |
| 4.2 | p= carries raw256-bit public key in Base64,44 encoded octets; not an RSA ASN.1 key structure. |
| 5 | Signers SHOULD implement and verifiers MUST implement Ed25519-SHA256. This does not authorize historical RSA-SHA1. |
| 6 | Multiple algorithms use distinct selectors, each with a single DNS key record; same d=/i= may remain. Do not mistake TXT string chunks for separate key records. |
| 7 | Base DKIM security advice plus8032 Ed25519 considerations remain applicable. |
| 8 | Registry update specified in8.1. |
| 8.1 | Adds active ed25519 key type; current registry state still needs independent check. |
| 9 | References reviewed; full base and primitive audits remain open. |
| 9.1 | 6376,8017,8032,SHA256 and syntax dependencies identified. |
| 9.2 | 3447 is historical, superseded by8017. |
| Appendix A | Published dual signatures use independent selectors; all key and message examples read. Rejected7930 would change a correct signature after applying a different algorithm. |
| A.1 | Published example private keys are test material only, never deployment credentials. |
| A.2 | Example raw Ed25519 and multi-string RSA TXT records reviewed. |
| A.3 | Exact indentation, header continuation, DKIM oversigning list and body blank line matter. The fixed published Ed25519 vector is reproduced by the linked experiment; general parsing and canonicalization remain untested. |

| Front/end matter | Abstract, status, copyright, acknowledgements where present, and author address reviewed. |

## Email Next consequence

DKIM evidence must retain the signing domain, validated signature coverage and applicable algorithm policy. Do not convert a domain signature into proof that a person owns a particular encryption key. One-click actions still require the relevant headers to be covered by a valid acceptable signature.

Algorithm support and trust are separate: a supported algorithm can produce an invalid signature, and a valid signature can cover insufficient fields for the intended action. Historical RSA-SHA1 cannot satisfy the current DKIM validity requirement. A new Ed25519 selector does not itself rotate a correspondent's end-to-end identity.

Required cases include historic algorithms, undersized RSA keys, stronger local policy, mismatched key and signature types, dual signatures under separate selectors, missing required header coverage, and correct Ed25519 signing of the DKIM digest rather than the raw canonicalized input. No complete verifier or cryptographic interoperability result is claimed.

## Executed example evidence

The [published-vector experiment](../evidence/README.md#published-dkim-ed25519-vector) reproduces the Appendix A Ed25519 signature with a fixed canonical input and checks three related boundaries. Four tests pass. It verifies the digest/signature construction for this example, not general DKIM header selection, DNS processing or the RSA signature.
