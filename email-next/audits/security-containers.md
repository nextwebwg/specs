---
title: MIME security containers audit
sectionNav: true
---

# MIME security containers audit

**Coverage:** complete11-page RFC1847 including both examples, processing descriptions and front/end matter; zero matching errata in refreshed dataset checked19October2026. [RFC1847](https://www.rfc-editor.org/rfc/rfc1847.html).

| Section | Disposition |
| --- | --- |
| 1 | Framework only: recognizing containers is not implementing a security protocol. Exactly two parts and required protocol dispatch. Unknown protocol cannot be processed as protected content. |
| 2 | Signed places control second; encrypted places control first. Descriptive processing stages defer exact algorithms to protocol profile. |
| 2.1 | Signed requires boundary/protocol/micalg and exactly two parts. Signature covers first part including its MIME headers, not enclosing headers or external references. Control type matches protocol. Conflicting micalg and control algorithm is an error. Signed container stays opaque in transit; transfer re-encoding invalidates protection. SMTP-compatible signed generation uses7bit-safe encodings. Verify profile-defined bytes before displaying authenticated content. |
| 2.2 | Encrypted requires boundary/protocol and exactly two parts: control first and application/octet-stream ciphertext second. Inner MIME headers encrypted with content. Do not render ciphertext or failed decryption output as a MIME message. Encryption alone does not establish sender authentication or integrity; selected protocol must define those. |
| 3 | Protocol specification must precisely define control media type, contents and processing. MIME registration alone is not a crypto suite. |
| 4 | Key request/response body parts are an optional distribution design, not a defined exchange, authentication scheme or invisible delivery guarantee. |
| 5 | Security considerations refer to entire framework; modern threat analysis and algorithm selection remain separate. |
| 6 | Acknowledgement reviewed. |
| 7 | Historical822/1521 dependencies mapped to current5322 and MIME2045/2046 families; their base reviews recorded, full successors/dependencies still open. |
| 8 | Author contact information reviewed; no additional message requirements. |

| Front matter | Status, abstract and contents reviewed; no algorithm or key-management guarantee implied. |

## Protected composition

If an Email Next security profile selects these containers, the protected object must include the complete contribution: readable alternatives, structured representation and all resources or attachments whose protection is claimed. An independent outer attachment remains outside that claim. A signed HTML root does not authenticate a resource merely because it references it.

The receiver reports which entity was protected. Successful verification of one nested body part must not decorate the enclosing message's unauthenticated author, audience or attachments with the same badge. Protected header semantics require a separate binding profile.

Required cases include wrong part count/order, control/protocol mismatch, conflicting algorithm indication, unsupported protocol, rewritten transfer encoding, substituted resource, modified outer author, partial nesting, failed decryption and plaintext sibling disclosure. No cryptographic implementation is tested by this audit.
