---
title: HMAC authentication
sectionNav: true
---

# HMAC authentication

The selected MLS suite uses HMAC-SHA256. [RFC2104](https://www.rfc-editor.org/rfc/rfc2104.html) defines the HMAC construction; RFC9420 selects its hash and protocol use. HMAC authenticates bytes under a shared secret. It does not encrypt them or independently establish a mailbox owner's identity.

## What implementations retain

HMAC hashes the key first when it exceeds the hash's block length, pads the resulting key to that block length, and performs the specified inner and outer hash operations. The two fixed pads and ordering are part of the construction. The held proposal to prohibit long keys is not an adopted correction.

MLS and HKDF determine the keys, input bytes and output use for their respective operations. RFC2104's generic truncation discussion does not authorize shortening an MLS tag or replacing HKDF's output rules. Likewise, its general key-refresh advice does not define a new Email/2 rotation interval. Precomputed inner and outer hash states must receive the same secrecy protection as keys.

RFC2104's MD5 and SHA-1 examples are historical. The [RFC6151 update](hmac-md5-update.md) discourages HMAC-MD5 in new designs. Neither those examples nor algorithm-replacement discussion permits unilateral changes to the selected suite.

## Separate primitive dependencies

| Selected operation | Authoritative source identified | Remaining review |
| --- | --- | --- |
| HMAC construction | RFC2104, updated by RFC6151 | Base and update reviewed here; implementation assurance remains separate. |
| SHA256 for MLS/HKDF | RFC9420 references FIPS180-4, August 2015; RFC5869's older reference is FIPS180-3 | The [selected SHA-256 requirements](sha256.md) are reviewed; broader guidance and implementation validation remain separate. The current NIST landing page identifies the 2015 edition and a planned revision. |
| AES-128-GCM | RFC9180 selects 16-octet key, 12-octet nonce, 16-octet tag and references SP800-38D, November 2007 | The [GCM algorithm and constraints](gcm.md) are reviewed; underlying [AES](aes.md) is reviewed separately; implementation assurance remains open; NIST lists a planned revision. The RFC5116 interface audit is not this review. |
| Underlying AES | FIPS197, updated May 2023 | The [AES source review](aes.md) covers the selected forward cipher and key expansion. NIST describes the 2023 update as editorial, with no algorithm change. |

These publication-status observations come from the [hash](https://csrc.nist.gov/pubs/fips/180-4/upd1/final), [GCM](https://csrc.nist.gov/pubs/sp/800/38/d/final) and [AES](https://csrc.nist.gov/pubs/fips/197/final) landing pages. Reading those pages does not review the standards themselves or establish NIST validation. Other applicable NIST HMAC guidance must also be assessed before making any NIST-conformance claim.

## Evidence and corrections

The complete 619-line RFC2104 source, all sample code, three MD5 vectors, references and backmatter were read; 11 dispositions retain exact ranges. Source SHA256: `64d5245a9101929025336e470e3737f118704001249d503c85a86e19fe9fbb01`. No sample or vector was executed in this audit. The existing HKDF library harness is separate, bounded evidence.

Seven captured errata matched the live listing on 20 October 2026: Verified501 supplies a missing sample-code semicolon; Held2794 supplies an omitted example key length,3694 corrects a reference title and4809 proposes the unadopted long-key restriction; Rejected4459 reverses copy arguments incorrectly,8185 misreads the truncation variable and8296 proposes deleting a historical link. Metadata identifies an Informational RFC from February 1997, updated by RFC6151.
