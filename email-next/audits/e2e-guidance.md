---
title: End-to-end email implementation audit
sectionNav: true
---

# End-to-end email implementation audit

The complete text of [RFC9787](https://www.rfc-editor.org/rfc/rfc9787.html), including every example, reference and appendix, has been reviewed. The [RFC Editor errata listing](https://www.rfc-editor.org/errata/rfc9787) contains no matching records as of 20 October 2026. RFC9787 is Informational guidance, not a new wire protocol.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Implementation guidance, not a new transport or cryptographic wire protocol. |
| 1.1 | Terminology | Vocabulary separates agents, messages and cryptographic operations. |
| 1.1.1 | Structural Header Fields | MIME-Version and Content-prefixed fields are structural; cannot be copied as arbitrary protected headers. |
| 1.1.2 | User-Facing Header Fields | User-visible and implicitly rendered fields require protection; transit-origin Resent fields need origin distinctions. |
| 2 | Usability | Usability is part of the security model. |
| 2.1 | Simplicity | Avoid exposing cryptographic machinery as routine user decisions. |
| 2.2 | Email Users Want a Familiar Experience | Preserve familiar composition and reading operations without concealed disclosure. |
| 2.3 | Warning About Failure vs. Announcing Success | Security expectations determine useful warnings; cannot infer success from absent errors. |
| 3 | Types of Protection | Integrity, identity and confidentiality are distinct properties. |
| 3.1 | Simplified Mental Model | Four simplified states reviewed; signature failure does not authorize plaintext replies. |
| 3.2 | One Cryptographic Status per Message | Recommends uniform protection across copies; user-authorized mixed delivery is an explicit proposal departure. |
| 4 | Cryptographic MIME Message Structure | MIME placement determines the scope of cryptographic claims. |
| 4.1 | Cryptographic Layers | Layer recognition does not itself establish identity or confidentiality. |
| 4.1.1 | S/MIME Cryptographic Layers | S/MIME layer variants reviewed separately. |
| 4.1.1.1 | S/MIME Multipart Signed Cryptographic Layer | Detached signature covers the signed entity, not surrounding outer headers. |
| 4.1.1.2 | S/MIME PKCS #7 signed-data Cryptographic Layer | Opaque signed-data requires decoding and signature validation. |
| 4.1.1.3 | S/MIME PKCS #7 enveloped-data Cryptographic Layer | Enveloped-data alone does not authenticate authorship. |
| 4.1.1.4 | S/MIME PKCS #7 authEnveloped-data Cryptographic Layer | Authenticated encryption integrity is not sender identity. |
| 4.1.1.5 | PKCS #7 Compression is NOT a Cryptographic Layer | Compression is not a cryptographic layer. |
| 4.1.2 | PGP/MIME Cryptographic Layers | PGP/MIME packet processing remains a separate dependency. |
| 4.1.2.1 | PGP/MIME Signing Cryptographic Layer (multipart/signed) | Detached OpenPGP signature scope follows the MIME entity. |
| 4.1.2.2 | PGP/MIME Encryption Cryptographic Layer (multipart/encrypted) | Actual packets determine protection; obsolete malleable forms must not be generated. |
| 4.2 | Cryptographic Envelope | Envelope includes contiguous outer cryptographic layers only. |
| 4.3 | Cryptographic Payload | Payload is the entity inside that envelope. |
| 4.4 | Types of Cryptographic Envelope | Envelope classification depends on layer composition. |
| 4.4.1 | Simple Cryptographic Envelopes | Simple envelopes give the baseline interoperable composition model. |
| 4.4.2 | Multilayer Cryptographic Envelopes | Additional layers complicate interpretation rather than automatically adding useful assurance. |
| 4.5 | Errant Cryptographic Layers | Nested errant layers cannot authenticate the enclosing message. |
| 4.5.1 | Mailing List Wrapping | Mailing-list wrapping requires separate treatment of wrapper and original contribution. |
| 4.5.2 | A Baroque Example | Complete nested example reviewed; layer scope must remain explicit. |
| 4.6 | Cryptographic Summary | Summary must reflect evaluated envelope and payload scope. |
| 5 | Message Composition | Composition must produce a comprehensible protected message. |
| 5.1 | Message Composition Algorithm | Algorithm reviewed including protected headers and payload construction. |
| 5.2 | Encryption Outside, Signature Inside | Sign inside encryption for the recommended composition path. |
| 5.3 | Avoid Offering Encrypted-Only Messages | Do not offer encryption-only composition as the normal secure mode. |
| 5.4 | Composing a Reply Message | Reply quotation must not silently disclose protected material. |
| 6 | Message Interpretation | Interpretation cannot rely on MIME appearance alone. |
| 6.1 | Rendering Well-Formed Messages | Well-formed status applies to the authenticated scope. |
| 6.2 | Errant Cryptographic Layers | Errant layers require constrained interpretation. |
| 6.2.1 | Errant Signing Layer | An embedded signature does not verify the whole message. |
| 6.2.1.1 | Exception: Mailing List Footers | List footer exception must visually distinguish unsigned content; List-ID alone is not trust. |
| 6.2.2 | Errant Encryption Layer | Isolate decrypted subtrees from surrounding attacker-controlled HTML. |
| 6.2.2.1 | Replying to a Message with an Errant Encryption Layer | Do not automatically quote errant decrypted content, even into an encrypted reply. |
| 6.2.3 | Avoiding Non-MIME Cryptographic Mechanisms | Inline armor is not equivalent to MIME protection. |
| 6.2.3.1 | Do Not Validate Non-MIME Signatures | Do not validate inline signatures under the described rendering guidance. |
| 6.2.3.2 | Skip or Isolate Non-MIME Decryption When Rendering | Skip inline decryption or isolate its output. |
| 6.2.3.3 | Do Not Decrypt Non-MIME Decryption When Replying | Do not extract inline-decrypted content into replies. |
| 6.3 | Forwarded Messages with Cryptographic Protection | An attached protected message has its own security scope. |
| 6.4 | Signature Failures | Missing and failed signatures receive equivalent ordinary presentation; established protection expectations apply equally. See the security contract’s author-verification rules. |
| 6.5 | Weak Encryption | Weak historical encryption needs warnings and restricted reply behavior; dates alone are not authority. |
| 7 | Reasoning about Message Parts | Body and attachment selection affects security. |
| 7.1 | Main Body Part | First-child simplification conflicts with RFC2387 start-selected roots; proposal explicitly honors selected root on receipt. |
| 7.2 | Attachments | Attachments belong inside the protected payload; independent envelopes do not authenticate collection membership. |
| 7.3 | MIME Part Examples | Both MIME-tree examples reviewed. |
| 8 | Certificate Management | Key discovery, lifecycle and identity binding remain essential. |
| 8.1 | Peer Certificates | Peer certificates are candidates, not automatically trusted identities. |
| 8.1.1 | Peer Certificate Selection | Address matching, expiry, revocation, key usage and encryption suitability reviewed; internationalized X.509 names depend on RFC9598. |
| 8.2 | Local Certificates | Local signing and encryption credentials have different roles. |
| 8.2.1 | Getting Certificates for the User | Provisioning must avoid unnecessary manual key management. |
| 8.2.1.1 | User Certificates for S/MIME | Distinct S/MIME signing and encryption keys supported; ACME issuance is a dependency, not implemented here. |
| 8.2.1.2 | User Certificates for PGP/MIME | OpenPGP certificates may contain distinct functional subkeys. |
| 8.2.1.3 | Generate Secret Key Material Locally | Generate secrets locally rather than through an untrusted provider. |
| 8.2.2 | Local Certificate Maintenance | Maintain credentials and consolidate actionable expiry warnings. |
| 8.2.3 | Shipping Certificates in Outbound Messages | Advertising certificates is separate from trusting them. |
| 8.2.3.1 | Shipping Certificates in S/MIME Messages | Ship appropriate certificates in protected S/MIME structures; exclude hidden-recipient disclosure. |
| 8.2.3.2 | Shipping Certificates in PGP/MIME Messages | OpenPGP certificate advertisement and gossip require separate trust rules. |
| 9 | Common Pitfalls and Guidelines | Operational pitfalls are part of the implementation contract. |
| 9.1 | Reading Sent Messages | Sender archive and recipient retry ciphertext serve different purposes. |
| 9.2 | Reading Encrypted Messages after Certificate Expiration | Certificate expiry does not prevent decryption of old messages. |
| 9.3 | Unprotected Message Header Fields | Header protection requires RFC9788 rather than body-only assurances. |
| 9.4 | Composing an Encrypted Message with Bcc | Bcc requires both envelope and payload privacy analysis. |
| 9.4.1 | Simple Encryption with Bcc | Describes distinct hidden-recipient deliveries; not automatically adopted as the complete Email Next profile. |
| 9.4.1.1 | Rationale | Recipient-key identifiers and gossip can expose Bcc membership. |
| 9.5 | Draft Messages | Drafts are author-only working state; do not apply replayable outbound signatures before Send. |
| 9.6 | Composing a Message to Heterogeneous Recipients | Uniform fallback recommendation differs from explicitly authorized mixed delivery; disclosure must remain accurate. |
| 9.7 | Message Transport Protocol Proxy: A Dangerous Implementation | Naive transport proxies lack necessary client context. |
| 9.7.1 | Dangers of a Submission Proxy for Message Composition | Submission needs recipient intent, inherited confidentiality and key lifecycle context beyond ordinary SMTP. |
| 9.7.2 | Dangers of an IMAP Proxy for Message Rendering | Verification results require authenticated provenance and exact message binding; RFC9219 is narrower than a full proxy contract. |
| 9.7.3 | Who Controls the Proxy? | Provider-controlled decryption is not confidentiality from that provider. |
| 9.8 | Intervening MUAs Do Not Handle End-to-End Cryptographic | Intervening MUAs cannot preserve original authorship by adding their own protection after modification. |
| 9.9 | External Subresources in MIME Parts Break Cryptographic | External resources can leak reading activity or plaintext; replies must not fetch original resources automatically. |
| 10 | IANA Considerations | No IANA registrations requested. |
| 11 | Security Considerations | Security discussion spans the whole document and underlying dependencies. |
| 12 | References | Complete references reviewed, without treating citation review as dependency review. |
| 12.1 | Normative References | RFC9598, S/MIME and header protection remain separately tracked dependencies. |
| 12.2 | Informative References | Research, implementations and draft versions are prior art rather than normative implementation closure. |
| A.1 | Webmail Threat Model | Adversarial webmail hosting is explicitly unresolved by this guidance. |
| A.2 | Test Vectors | Proposes future valid and malformed test vectors; no supplied complete test suite. |
| A.3 | Further Guidance on Peer Certificates | Peer credential management has unresolved policy questions. |
| A.3.1 | Certificate Discovery from Incoming Messages | Incoming certificate cache management is future work. |
| A.3.2 | Certificate Directories | Directory selection and conflicting evidence are future work. |
| A.3.3 | Checking for Certificate Revocation | Revocation checks must consider privacy leakage. |
| A.3.4 | Further Peer Certificate Selection | Multiple acceptable keys and absent usage constraints need explicit selection rules. |
| A.3.5 | Human-Readable Names in Peer Certificates, Header Fields, and | Display names are not globally unique identities; avoid misleading name verification. |
| A.4 | Further Guidance on Local Certificates and Secret Keys | Local multi-device credential management remains open. |
| A.4.1 | Cross-MUA Sharing of Local Certificates and Secret Keys | Cross-device secret transfer and renewal are not specified. |
| A.4.2 | Use of Smart Cards or Other Portable Secret Key Mechanisms | Hardware token interaction and bulk decryption need usability design. |
| A.4.3 | Active Local Certificate Maintenance | Automatic certificate maintenance is future work. |
| A.5 | Certification Authorities | CA selection, intermediate caching and shared trust stores are unresolved. |
| A.6 | Indexing and Search of Encrypted Messages | Plaintext search indexes disclose content and require protection. |
| A.7 | Cached Signature Validation | Cached historical verification and current revocation status must be distinguished. |
| A.8 | Aggregate Cryptographic Status | Conversation-level cryptographic summaries are outside the document's single-message model. |
| A.9 | Expectations of Cryptographic Protection | No general protection-expectation protocol is supplied. |
| A.10 | Secure Deletion | Long-lived decryption keys defeat secure deletion of retained ciphertext; MLS retention requires separate design. |
| A.11 | Interaction with Opportunistic Encryption | Opportunistic encryption and cleartext-copy interactions are future work. |
| A.12 | Split Attachments | Split attachments trade bandwidth for additional metadata and integrity risks. |
| A.13 | Proxy Extensions | A safe proxy API remains future work, not an inherited standard. |
| A.14 | Mailing Lists | List membership, archive access and redistribution authority complicate endpoint guarantees. |

## Proposal consequences

The [security contract](../security.md) specifies isolated decryption, private draft state, archive/retry separation and authenticated delegated results. The [message contract](../messages.md) reconciles related-root selection with RFC2387. The [delivery policy](../delivery-policy.md) deliberately permits sender-selected mixed-recipient fallback, with an accurate disclosure boundary; this departs from Sections 3.2 and 9.6 rather than claiming their endorsement.

Appendix A identifies open questions that Email Next must answer itself: discovery, device enrollment, trust continuity, protection expectations, conversation status, search, proxy integration and mailing-list behavior. Reading this guidance does not resolve those designs or certify an implementation. CMS, OpenPGP, S/MIME, PKI, internationalized certificate names and cited discovery mechanisms remain separate dependency work.

## Departure rationale locations

| RFC9787 guidance | Email Next behavior and rationale |
| --- | --- |
| Sections 3.2 and 9.6: uniform cryptographic protection | [Mixed delivery](../delivery-policy.md) permits explicit per-recipient fallback to support incremental adoption. Its rationale covers broader disclosure, legacy presentation limits and a fresh protection decision for each reply. |
| Sections 5.2–5.3: signature inside encryption; no encryption-only composition | [Managed-profile framing](../security-profile.md#relationship-to-encrypted-email-guidance) uses MLS PrivateMessage, whose encrypted content includes the signature authentication data. This is a different wire protocol that preserves those goals, not an exemption from authenticating the author. |
| Sections 5.1 and 9.3: protected user-facing headers | [Managed framing](../security-profile.md#relationship-to-encrypted-email-guidance) authenticates selected application fields, not arbitrary outer mail headers. The [negotiated presentation profile](../managed-presentation.md) adds protected subject, date and recipient roles using semantic MLS fields, deliberately without RFC9788 wire compatibility. The legacy S/MIME path retains RFC9788 rather than inheriting a blanket exception. |
| Section 9.4.1: certificate-based blind-copy construction | [Managed-group blind copies](../delivery-policy.md#why-the-managed-group-model-differs-from-rfc-9787) cannot add hidden recipients to a member-visible MLS roster. The separately negotiated [private-copy binding](../private-copies.md) gives each blind principal an independent protected conversation with the originator. Its rationale explains why named recipients do not gain access to that copy or its replies. |
| Section 7.1: first-child multipart traversal | [Related-root traversal](../messages.md) honors an explicit multipart/related root on receipt, to avoid rendering a resource as the body. New composition puts the root first to satisfy both approaches. |

The [transport-secret and archive rules](../security.md#delayed-delivery-and-retained-history) extend the lifecycle model discussed in Section 9.2 and Appendix A.10. MLS deletes consumed transport secrets to limit later compromise; a separately protected readable archive preserves received history. Some delayed ciphertext can become unreadable after its permitted retention window. This is a consequence of secret deletion, not a restriction based solely on certificate expiry, and it never authorizes an automatic plaintext resend.

The [author-verification rules](../security.md#when-the-author-cannot-be-verified) align with Section 6.4: absent and failed signatures receive equivalent ordinary presentation and action restrictions. A warning based on an established protection expectation applies equally to both. The rationale explains that distinction and preserves confidentiality for decrypted but unverified content. This resolves the presentation contract; implementation acceptance evidence remains required.

These comparisons are not an exhaustive conformance claim. The protected presentation and private-copy chapters define selected departures; their local experiments do not establish deployed interoperability. Appendix A's broader design areas require their own selected profiles before support can be claimed. An unimplemented integration is not an approved exception.
