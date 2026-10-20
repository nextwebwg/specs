---
title: AES block cipher
sectionNav: true
---

# AES block cipher

The selected AES-128-GCM suite uses the forward AES-128 cipher defined by [FIPS197, updated May 2023](https://doi.org/10.6028/NIST.FIPS.197-upd1). AES transforms one 16-octet block under a 16-octet key. GCM supplies the authenticated-encryption construction; AES alone is not a message format or authentication mechanism.

## Selected requirements

AES-128 uses ten rounds and a fixed key expansion producing 44 words. The state maps input bytes by column. Its byte substitution, row shifts, column mixing and round-key addition use the specified finite-field arithmetic and constants. The last round omits column mixing. Equivalent implementations must produce the same output for the same key and input; application code should use established cryptographic libraries rather than reproduce these internals.

GCM uses the forward block cipher for both authenticated encryption and authenticated decryption. The inverse cipher, other Rijndael block sizes and AES-192 or AES-256 do not become selected MLS algorithms through this review. Separate local-storage uses of AES-256 also do not change the negotiated MLS suite.

The [GCM review](gcm.md) owns nonce, tag, input-length and usage constraints. The AES block size does not set the application's message limit. Section 6.4 warns that equivalent outputs alone do not address implementation attacks, including cache timing and fault injection. Key generation, entropy, platform protections and validation remain separate assurance requirements.

## Publication and review scope

The [official publication page](https://csrc.nist.gov/pubs/fips/197/final) identifies the May 2023 edition as an editorial update without technical changes to the algorithm. Appendix D records those changes. The page listed no supplemental material when checked on 20 October 2026; that observation is not a guarantee that no issue exists elsewhere.

All 46 PDF pages were read as extracted text, including inverse algorithms, examples, references and the change log. Selected forward-cipher equations, the substitution table and AES-128 key expansion were checked visually on PDF pages 14 and 16–27, counting from the cover. Other variants and examples were read for scope; their complete formula/table validation is not claimed. The private ledger records 14 dispositions and exact text ranges.

- PDF SHA 256: `62c86eb567f13edb8f71826e985da870b04ef6381634f303cdb16e84d47becd1`.
- Extracted-text SHA 256: `9e940d7fa3041fb7444724ea115276bf6b3138dacee78b1d177ee364bdeb8c9e`.

No vectors or algorithms were executed in this review. NIST validation, library correctness and side-channel resistance are not established. SP800-133 Rev.2 key-generation guidance and applicable deployment assurance remain separate dependencies. This non-RFC source does not increase the RFC audit count.
