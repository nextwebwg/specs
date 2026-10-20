---
title: S/MIME message format audit
sectionNav: true
---

# S/MIME message format audit

[S/MIME 4.0](https://www.rfc-editor.org/rfc/rfc8551.html) already carries signed capability advertisements and preferred encryption certificates in ordinary messages. These mechanisms are useful prior art for automatic discovery. They do not establish device enrollment, hide negotiation traffic from older clients, or make successful decryption proof of who sent a message.

The complete RFC8551 base text, examples, tables, ASN.1 module, references and end matter have been read. This is a document review, not an S/MIME implementation or cryptographic conformance result. The [official status page](https://www.rfc-editor.org/info/rfc8551/) identifies RFC9788 as an update; its [header-protection review](header-protection.md) covers the replacement for the last two paragraphs of Section 3.1. No RFC8551 entries occur in the captured errata corpus; the live all-status listing on 20 October 2026 explicitly reports no matching errata, and current metadata confirms the RFC9788 update.

## Section review

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | MIME protection can cross transports and serve automated agents; it is not restricted to a human mail client. Historical dependencies are intentional, not current algorithm endorsements. |
| 1.1 | Specification overview | CMS and algorithm dependencies remain necessary. Sending and receiving requirements differ; successful reception does not prove composition support. |
| 1.2 | Definitions | Distinguish encoded transport representation, MIME content, sender/receiver roles and cryptographic services. |
| 1.3 | Conventions | SHOULD+, SHOULD- and MUST- preserve their present requirement level; the suffix predicts possible future changes rather than applying them. |
| 1.4 | Compatibility | Version-specific behavior requires explicit compatibility profiles, not one generic S/MIME-support flag. |
| 1.5 | Version 3 to 3.1 changes | Historical migration context; do not copy old algorithm requirements into new composition. |
| 1.6 | Version 3.1 to 3.2 changes | Section numbers refer to the earlier specification. Historical requirements are not substitutes for the current sections. |
| 1.7 | Version 4 changes | AuthEnvelopedData, modern algorithm support and archive compatibility are separate changes. |
| 2 | CMS options | The interoperability baseline depends on CMS and algorithm specifications beyond this document. |
| 2.1 | Digests | Message digest and signature digest are separate selections; SHA-256 and SHA-512 are required by this base document. |
| 2.2 | Signatures | Receiver support is broader than the minimum sender choice. Algorithm names, curve and mode must identify the exact operation. |
| 2.3 | Key encryption | P-256 and X25519 agreement have specified derivations; key wrapping and content encryption must follow the required algorithm/strength relationship. |
| 2.4 | General syntax | Data, signing, enveloping, authenticated enveloping and compression have different semantics. |
| 2.4.1 | Data | Protected MIME content is carried with the specified id-data identifier; detached signatures omit encapsulated content. |
| 2.4.2 | SignedData | Certificate-only SignedData is a degenerate case, not evidence of a signature. |
| 2.4.3 | EnvelopedData | Confidentiality requires recipient keys; this container alone does not establish integrity or sender identity. |
| 2.4.4 | AuthEnvelopedData | Integrity protection still does not identify the author. |
| 2.4.5 | CompressedData | Compression provides none of the listed cryptographic assurances. |
| 2.5 | SignerInfo attributes | Preserve signed/unsigned distinction, multiplicity and exact attribute meanings. Unknown attributes must not become application authority. |
| 2.5.1 | Signing time | Time is a signer assertion, not an independent timestamp or global event order. UTCTime and GeneralizedTime have defined boundaries. |
| 2.5.2 | Capabilities | Signed, single-valued attribute supplies a partial preference list. Absence from the list is not proof of non-support. Exact OID parameter encoding matters. |
| 2.5.3 | Encryption preference | Signed certificate preference can differ from the signing certificate. Valid signature, freshness and certificate validity remain necessary. |
| 2.5.3.1 | Recipient certificate selection | Preference, subject matching and other discovery paths do not replace certificate validation or Email Next identity continuity. |
| 2.6 | Signer identifier | Both identifier forms are supported. A subjectKeyIdentifier can match multiple certificates; it is not a globally unique principal. |
| 2.7 | Content encryption | AES-GCM and AES-CBC requirements differ; the optional ChaCha20-Poly1305 path needs a CMS-specific algorithm dependency check. |
| 2.7.1 | Selection and caching | Authenticate capability updates and check signer time; future-skew and failed signatures cannot update the cache. Refusing weak encryption overrides preference selection. |
| 2.7.1.1 | Known capabilities | Choose a supported recipient preference within the sender's acceptable algorithm policy. |
| 2.7.1.2 | Unknown capabilities | The base fallback selection does not prove the recipient supports S/MIME or authorize Email Next downgrade. |
| 2.7.2 | Weak encryption | A compatibility choice must not misrepresent protection strength. New-message policy remains distinct from historical decryption. |
| 2.7.3 | Multiple recipients | Separate copies can be required for incompatible algorithms; the weakest exposed copy limits content confidentiality. |
| 3 | Message creation | Canonical MIME content is secured before the outer MIME wrapper is added. |
| 3.1 | Preparing MIME | Protection covers the selected entity. Original message/rfc822 header-wrapping advice is superseded by RFC9788 for new composition. |
| 3.1.1 | Canonicalization | Apply media-specific canonicalization before protection; text uses CRLF and charset rules. Display normalization is not verification input. |
| 3.1.2 | Transfer encoding | Inner and outer encoding are independent. Binary-inside support needs recipient knowledge; unknown recipients retain the conservative encoding path. |
| 3.1.3 | Detached-signature encoding | Seven-bit transport requires a seven-bit-safe signed entity. Recoding after signing invalidates protection. |
| 3.1.4 | Canonical example | This is MIME preparation, not a cryptographically protected test message. CRLF and trailing whitespace matter. |
| 3.2 | PKCS7 MIME | The outer type carries CMS objects. An outer encoding change is different from modifying protected inner bytes. |
| 3.2.1 | Names and filenames | Filename hints help gateways but cannot replace media-type processing or prove cryptographic content. |
| 3.2.2 | smime-type | A claimed operation is a parsing/display hint, not a verified protection result. Registry closure remains necessary. |
| 3.3 | Enveloped-only creation | Unauthenticated encryption can be malleable. Including the originator's encrypted key supports sent-message access, not author authentication. |
| 3.4 | Authenticated enveloping | Recipients possessing the content key can replace content. Integrity alone cannot authorize a named author's structured actions. |
| 3.5 | Signed-only creation | Both opaque and detached formats must be receivable under this baseline. |
| 3.5.1 | Format choice | Detached signatures preserve ordinary readable MIME; opaque signing protects against benign rewriting but needs a capable reader. |
| 3.5.2 | Opaque signing | Required CMS and MIME wrapping reviewed; embedded example is not independently verified here. |
| 3.5.3 | Detached signing | Exactly two multipart parts: unchanged signed entity and detached CMS signature. |
| 3.5.3.1 | Signature media type | ContentInfo contains SignedData with absent encapsulated content; signerInfos carries the signatures. |
| 3.5.3.2 | Multipart construction | Required protocol and digest parameters do not replace actual signature checks; multiple digest names use the defined list syntax. |
| 3.5.3.3 | Multipart example | Source supplies claimed digest bytes and encoded signature; no cryptographic verification is claimed by this reading. |
| 3.6 | Compression | Recipient support is separately advertised. The encoded example needs correction before use as a CMS fixture; see source issues below. |
| 3.7 | Multiple operations | Nesting is supported within resource limits. Order changes the claim being signed; an outer ciphertext signature does not establish authorship of plaintext. |
| 3.8 | Certificate management | No encapsulated content and empty signerInfos are required. Such a message transports certificates/CRLs without authenticating itself as a conversation action. |
| 3.9 | Registration requests | No single certificate-request mechanism is mandated; issuance and identity policy remain independent work. |
| 3.10 | Identification | Media types and fallback filename clues can identify candidates for parsing, never verified protection. |
| 4 | Certificate processing | Retrieval is required but certificate validation is delegated. Suggested certificate-request email does not define loop suppression or invisible legacy delivery. |
| 4.1 | Key generation | Entropy and private-key protection are required; new RSA key generation cannot use the old small-key floor. |
| 4.2 | Signature generation | Generation limits differ from historical verification support; curve selections fix EC key sizes. |
| 4.3 | Signature verification | Required supported RSA sizes do not mean every certificate or signature using them is trusted. |
| 4.4 | Encryption | New encryption follows the selected key-establishment algorithm and policy, not archival exceptions. |
| 4.5 | Decryption | Old small-key decryption permission does not authorize generating new mail with those keys. |
| 5 | Registrations | Media registrations and smime-type additions reviewed; live registry reconciliation remains separate. |
| 5.1 | pkcs7-mime registration | No mandatory parameters; optional operation/name hints do not prove content type or protection. |
| 5.2 | pkcs7-signature registration | Detached signature type has no defined parameters; filename is not a security boundary. |
| 5.3 | Authenticated-envelope registration | authEnveloped-data is the registered operation hint defined here. |
| 5.4 | Reference updates | Registry references are redirected from RFC5751; current registry state is not proven by this instruction. |
| 6 | Security | Resource exhaustion, weak historical keys, mixed strengths, authenticated-encryption limits, length/compression leakage and isolated MIME origins all affect adoption. Integrity checks precede effects. |
| 7 | References | Full reference list read; listed documents are not thereby individually audited. |
| 7.1 | Reference conventions | Some historical version aliases disagree with Section 1.4; resolve numbered documents explicitly. |
| 7.2 | Normative references | CMS, certificate handling, ASN.1, randomness and algorithm specifications require separate dependency review. |
| 7.3 | Informative references | Historical algorithms and research inform compatibility/security; they are not new-message recommendations. |
| Appendix A | ASN.1 module | Legacy module, identifiers, CHOICE tags and absent preferBinaryInside parameters reviewed. Modern ASN.1 module is a separate dependency. |
| Appendix B | Historical mail | Archive access must remain distinct from new-message generation and present-day verification claims. |
| B.1 | Historical digests | Old hashes may explain archived material; they do not become acceptable current signing choices. |
| B.2 | Historical signatures | Expired certificates, missing old revocation evidence and weakened hashes limit retrospective assurance. Local possession history differs from an asserted old date. |
| B.3 | Historical encryption | RC2/40 and TripleDES compatibility is for decrypting old mail, not composing new mail. |
| B.4 | Historical key encryption | Historical key sizes may permit recovery of old content without weakening future delivery. |
| Appendix C | Version 2 status | Historical-status action does not remove the need to handle existing archives carefully. |

## Consequences for Email Next

Use signed capability and preferred-certificate exchange as prior art, with explicit boundaries for the [discovery](../capability-discovery.md) and [identity lifecycle](../identity-lifecycle.md) designs. A partial algorithm advertisement is not a full client-feature announcement. A later signing timestamp must not silently enroll a new device or replace an established identity.

The [security contract](../security.md) already separates confidentiality, author verification and action authorization. S/MIME reinforces that separation: neither authenticated enveloping nor a certificate-only message authorizes an answer, edit or key transition. Its recommendation to isolate protected MIME parts also supports the [rendering contract](../rendering.md); raw concatenation across protection boundaries is unsafe.

The [delivery policy](../delivery-policy.md) must continue to explain mixed-copy disclosure. S/MIME's ability to send different algorithm versions to different recipients does not make the strongest copy a confidentiality guarantee for the whole message.

## Source issues and remaining evidence

The Section 3.6 base64 example decodes to a zlib stream beginning `78 da`, which decompresses to the sample sentence. It lacks the CMS ContentInfo/CompressedData wrapper required by the preceding construction steps. This was checked by decoding and decompressing the bytes; it is a source inconsistency, not an asserted verified erratum. Do not use it as a passing CMS fixture.

Section 7.1 swaps the historical version groups relative to Section 1.4, and Appendix A labels RFC5751 as SMIMEv2. Section 4 points to RFC5750 even though RFC8550 is included in the normative references. Follow actual numbered documents and review current certificate requirements independently. Section 2.7's ChaCha20-Poly1305 reference describes TLS suites; an implementation still needs the applicable CMS algorithm definition.

Algorithm-specific capability parameter encodings also need dependency checks: Section 2.5.2's SHA256-with-RSA example includes NULL, while its general rule omits parameters without differentiating information. An implementer must not replace algorithm-specific encoding requirements with a blanket NULL rule.

No certificate chains, encrypted examples, detached signatures, historical archives or client interfaces were validated by this review. Required acceptance evidence includes malformed attribute multiplicity, ambiguous key identifiers, stale capability replay, absent/failed signatures, unknown binary-inside support, altered signed MIME, recipient-forged authenticated envelopes and isolated rendering. Dependency closure and live errata verification remain open.
