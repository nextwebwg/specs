---
title: HMAC legacy-hash update
sectionNav: true
---

# HMAC legacy-hash update

[RFC6151](https://www.rfc-editor.org/rfc/rfc6151.html) updates RFC2104's historical HMAC-MD5 security discussion. New protocol designs should not include HMAC-MD5. Email Next's selected MLS suite uses HMAC-SHA256 and does not enable MD5 by referencing the generic HMAC construction.

The update distinguishes collision resistance, preimage resistance and keyed authentication. Its analysis of MD5, NMAC related-key attacks and HMAC-MD5 does not establish a corresponding weakness in the selected SHA256 construction. Conversely, its historical statement that removing HMAC-MD5 from existing protocols was not urgent is not permission to introduce it here. A shared-key MAC remains distinct from a public-key signature and from encryption.

## Review coverage

All 395 lines were read, including the complete attack discussion, every reference and backmatter; nine dispositions retain exact ranges. Source SHA256: `4e5599d99a0d335560c0a47a959e91469ee47d49edcd224aa2b7b0b0a6b8588d`. No attack, sample or primitive implementation was executed.

Captured metadata identifies an Informational RFC from March 2011 updating RFC1321 and RFC2104, with no listed successor. The captured errata set is empty and the live listing reported no matching errata on 20 October 2026. This closes the identified RFC2104 update review, not the separate SHA256, AES, GCM or cryptographic implementation reviews.
