---
title: DKIM algorithm requirements audit
sectionNav: true
---

# DKIM algorithm requirements audit

**Coverage:** Complete five-page RFC 8301; no entries in the retrieved errata dataset. [RFC 8301](https://www.rfc-editor.org/rfc/rfc8301.html). Base DKIM and cryptographic dependencies remain open.

| Section | Disposition |
| --- | --- |
| 1 | Deprecates SHA1 for DKIM; historical deployment limitations are context, not new DNS limits. |
| 2 | BCP14 requirement vocabulary reviewed. |
| 3 | Updates6376 algorithm/key sections while retaining extensibility. Apply alongside8463 rather than treating RSA as the only current algorithm. |
| 3.1 | RSA-SHA256 signing/verifying required under this update; RSA-SHA1 must not be used and has permanently failed evaluation. |
| 3.2 | RSA signing minimum1024 bits, recommended2048+; verifiers implement1024–4096 and may support larger. Under1024 cannot validate. Stronger local policy is allowed; these are DKIM requirements, not Email Next encryption-key choices. |
| 4 | Reduces weak-cryptography risk; does not replace DKIM security model or address sender identity by itself. |
| 5 | Marks sha1 historic in hash registry. |
| 6 | References reviewed; base DKIM and crypto dependencies remain pending. |
| 6.1 | 6376 and8017 require separate audit; keyword references reviewed as vocabulary. |
| 6.2 | SHA1 analysis and vulnerability note supply rationale, not new normative profiles. |

| Front/end matter | Abstract, status, copyright, acknowledgements where present, and author address reviewed. |

## Email Next consequence

DKIM evidence must retain the signing domain, validated signature coverage and applicable algorithm policy. Do not convert a domain signature into proof that a person owns a particular encryption key. One-click actions still require the relevant headers to be covered by a valid acceptable signature.

Algorithm support and trust are separate: a supported algorithm can produce an invalid signature, and a valid signature can cover insufficient fields for the intended action. Historical RSA-SHA1 cannot satisfy the current DKIM validity requirement. A new Ed25519 selector does not itself rotate a correspondent's end-to-end identity.

Required cases include historic algorithms, undersized RSA keys, stronger local policy, mismatched key and signature types, dual signatures under separate selectors, missing required header coverage, and correct Ed25519 signing of the DKIM digest rather than the raw canonicalized input. No complete verifier or cryptographic interoperability result is claimed.
