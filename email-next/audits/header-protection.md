---
title: Protected email headers audit
sectionNav: true
---

# Protected email headers audit

The complete prose, algorithms, tables, figures, examples and end matter of [RFC9788](https://www.rfc-editor.org/rfc/rfc9788.html) have been reviewed. Encoded example data was retained and checked programmatically; ciphertext character inspection is not treated as cryptographic verification. The [RFC Editor errata listing](https://www.rfc-editor.org/errata/rfc9788) contains no matching records as of 20 October 2026. The document updates RFC8551; dependency and live-registry closure remain open.

The [vector experiment](header-vector-checks.md) records exact verification scope: signed layers, header mutations, exposed-header consistency and decoration placement were checked. Outer-envelope decryption, certificate trust, deployed rendering and a production sanitizer were not checked.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Introduction | Whole-message protections address contextual attacks on unprotected author and subject fields. |
| 1.1 | Update to RFC 8551 | Supersedes the final two paragraphs of RFC8551 Section 3.1 with direct protected payload headers. |
| 1.1.1 | Problems with RFC 8551 Header Protection | Nested message/rfc822 rendering and reply leaks motivate the replacement; receive compatibility remains distinct. |
| 1.2 | Risks of Header Protection for Legacy MUA Recipients | Legacy crypto clients may hide protected subjects; decorative display or reduced header confidentiality has explicit tradeoffs. |
| 1.3 | Motivation | Body-only authenticity does not authenticate its displayed context. |
| 1.3.1 | Backward Compatibility | Capability cannot be assumed across every recipient device; legacy rendering remains relevant. |
| 1.3.2 | Deliverability | Complete header hiding can impair delivery; header confidentiality is distinct from content encryption. |
| 1.4 | Other Protocols to Protect Email Header Fields | Domain-based DKIM/DMARC protection does not replace endpoint authentication or encryption. |
| 1.5 | Applicability to PGP/MIME | Applicable in principle to PGP/MIME; S/MIME analysis does not settle every OpenPGP divergence. |
| 1.6 | Requirements Language | Requirement keywords reviewed. |
| 1.7 | Terms | All terms reviewed; RFC9787 supplies essential structural and usability definitions. |
| 1.8 | Document Scope | Composing and receiving guidance assumes the referenced security model. |
| 1.8.1 | In Scope | Single signature and sign-then-encrypt cases are the intended scope. |
| 1.8.2 | Out of Scope | Encryption-only, multiple signatures, triple wrapping and outside signatures excluded from composition guidance. |
| 1.9 | Example | Complete MIME tree, inner/outer fields and legacy display example reviewed. |
| 2 | Internet Message Format Extensions | Extensions preserve ordinary message transport; no new SMTP capability is defined. |
| 2.1 | Content-Type Parameters | Two parameters have separate scopes and meanings. |
| 2.1.1 | Content-Type Parameter: hp | hp only at protected payload root; clear/cipher express author intent, not proof of an encryption layer. |
| 2.1.2 | Content-Type Parameter: hp-legacy-display | Legacy display marker belongs to eligible plain/HTML leaf parts, including a single-part payload. |
| 2.2 | HP-Outer Header Field | HP-Outer records author-exposed nonstructural fields inside encryption; mutable outer headers cannot replace it. |
| 2.2.1 | HP-Outer Header Field Definition | Repeated field ABNF and first-colon split reviewed; obsolete unstructured form excluded. |
| 3 | Header Confidentiality Policy | HCP governs confidentiality only; policy name never appears on the wire. |
| 3.1 | HCP Definition | Case-insensitive field-name mapping returns unchanged value, null, or constrained ASCII replacement. |
| 3.1.1 | HCP Avoids Changing addr-spec of From Header Field | Preserve From addr-spec absent coordinated additional identity knowledge. |
| 3.2 | Initial Registered HCPs | Three policy definitions compared; example hide-cc policy is not registered. |
| 3.2.1 | Baseline Header Confidentiality Policy | Baseline obscures Subject and removes Comments/Keywords; selected default for legacy S/MIME path. |
| 3.2.2 | Shy Header Confidentiality Policy | Shy strips selected display names and normalizes date zone; mailbox-list parsing limits matter. |
| 3.2.3 | No Header Confidentiality Policy | No confidentiality is not the unconfigured default. |
| 3.3 | Default Header Confidentiality Policy | Default must protect Subject without forcing ordinary users to choose a technical policy. |
| 3.4 | HCP Evolution | More ambitious policies need explicit definitions and deployment evidence. |
| 3.4.1 | Offering More Ambitious Header Confidentiality | Hiding audience/thread headers needs delivery and rendering evaluation. |
| 3.4.2 | Expert Guidance for Registering Header Confidentiality Policies | Registry guidance requires stable name, pseudocode, differentiation and deployment rationale. |
| 4 | Rendering Guidance (Receiving Side) | Protected values govern rendering with a specific From exception; outer-only fields are not silently authenticated. |
| 4.1 | Identifying That a Message Has Header Protection | Recognize clear/cipher at payload root only; ignore hp elsewhere. |
| 4.2 | Extracting Protected Header Fields From an Encrypted Message | Derive protected and author-exposed lists from authenticated payload, not observed outer headers. |
| 4.2.1 | HeaderSetsFromMessage | Complete list algorithm reviewed; repeated fields preserved, HP-Outer split on first colon. |
| 4.3 | Updating the Cryptographic Summary | Field-level status can differ from body status; internal distinctions need not burden the main interface. |
| 4.3.1 | HeaderFieldProtection | All steps reviewed; actual encryption, author intent and signature validity are independent inputs. |
| 4.4 | Handling Mismatch of From Header Fields | Rendering an inner From under outer-domain trust can enable spoofing. |
| 4.4.1 | Definitions | Mismatch and missing correctly bound signature are separate conditions. |
| 4.4.1.1 | From Header Field Mismatch | Mismatch uses actual outer From, not its HP-Outer record. |
| 4.4.1.2 | No Valid and Correctly Bound Signature | Valid signature alone does not establish certificate-to-address binding. |
| 4.4.2 | Warning for From Header Field Mismatch | Mismatch plus absent valid binding warrants showing both addresses and a warning. |
| 4.4.3 | From Header Field Rendering | MTA-reliant display may prefer outer From under those conditions; not endpoint verification. |
| 4.4.4 | Handling the Protected From Header Field When Responding | Replies still derive recipients only from protected fields, despite display exception. |
| 4.4.5 | Matching addr-specs | IDNA/domain comparison reviewed; suggested local-part folding is not general account identity canonicalization. |
| 4.5 | Rendering a Message with Header Protection | Render protected fields and the payload itself when header protection is recognized. |
| 4.5.1 | Example Signed-Only Message | Signed-only example protects fields but gives no confidentiality or legacy decoration. |
| 4.5.2 | Example Signed-and-Encrypted Message | Encrypted example compares each protected field with HP-Outer records; exposed copies remain visible in transit. |
| 4.5.3 | Do Not Render Legacy Display Elements | Suppress decorations for rendering/reply derivation without changing preserved signed source. |
| 4.5.3.1 | Identifying a Part with Legacy Display Elements | Requires an encrypting envelope and marked plain/HTML part; marker alone is insufficient. |
| 4.5.3.2 | Omitting Legacy Display Elements from text/plain | Plain-text removal ends at first entirely blank line and depends on charset decoding. |
| 4.5.3.3 | Omitting Legacy Display Elements from text/html | Remove body divs with the designated class; CSS hiding alone is insufficient for semantic reply cleanup. |
| 4.6 | Implicitly Rendered Header Fields | Threading and reply fields are implicitly rendered and must use protected values. |
| 4.7 | Handling Undecryptable Messages | Undecryptable placement is provisional; metadata caching must not defeat MLS secret deletion. |
| 4.8 | Guidance for Automated Message Handling | Automated control messages require authenticated semantic inputs. |
| 4.8.1 | Only Interpret Protected Header Fields | Actions must use protected control headers, never substitute outer fields. |
| 4.8.2 | Ignore Legacy Display Elements | Remove qualifying decorative content before interpreting body commands. |
| 4.9 | Affordances for Debugging and Troubleshooting | Retain original source and offer protected payload source separately when available. |
| 4.10 | Handling RFC8551HP Messages (Backward Compatibility) | Do not generate RFC8551HP; limited receiving compatibility permitted. |
| 4.10.1 | Identifying an RFC8551HP Message | All four structural recognition conditions reviewed; not arbitrary nested message promotion. |
| 4.10.2 | Rendering or Responding to an RFC8551HP Message | Legacy confidentiality inference depends on mutable outer fields and lacks modern intent guarantees. |
| 4.11 | Rendering Other Schemes | Other schemes need explicit interpretation; shape alone does not establish equivalent protection. |
| 5 | Composing Guidance (Sending Side) | Composition should apply header protection; hp belongs only at payload root. |
| 5.1 | Composing a Cryptographically Protected Message Without Header | Legacy body-only composition reviewed for comparison; origheaders excludes withheld Bcc. |
| 5.1.1 | ComposeNoHeaderProtection | Protect body then add outer fields leaves those fields outside endpoint signature. |
| 5.2 | Composing a Message with Header Protection | All inputs reviewed; legacy capability determination intentionally unspecified by RFC. |
| 5.2.1 | Compose | Every step reviewed; local-only decoration calculation differs from inherited-confidentiality worked example. |
| 5.2.2 | Adding a Legacy Display Element to a text/plain Part | Plain decoration is header lines plus blank delimiter; charset and newline injection handling apply. |
| 5.2.3 | Adding a Legacy Display Element to a text/html Part | HTML decoration must represent hidden user-facing fields with escaped values. |
| 5.2.3.1 | Step-by-Step Example for Inserting a Legacy Display Element | Non-normative pre/div insertion sequence reviewed; use parsed HTML rather than unescaped concatenation. |
| 5.2.4 | Only Add a Legacy Display Element to Main Body Parts | Attachments must remain unchanged; first-child related rule needs reconciliation with selected-root semantics. |
| 5.2.5 | Do Not Add a Legacy Display Element to Other Content-Types | Do not generalize decoration insertion to arbitrary MIME types. |
| 6 | Replying and Forwarding Guidance | Reply/forward operations can disclose protected headers or send to unintended recipients. |
| 6.1 | Avoid Leaking Encrypted Header Fields in Replies and Forwards | Preserve confidentiality of inherited values even when local default would expose them. |
| 6.1.1 | The Respond Function | Respond function differs by reply/reply-all/forward and is reused for both header views. |
| 6.1.2 | ReferenceHCP | Exact tuple map reviewed; partial user edits evade it, explicitly illustrated in Appendix D. |
| 6.2 | Avoid Misdirected Replies | Injected outer Cc/Reply-To must not change reply audience, even if its key is known. |
| 7 | Unprotected Header Fields Added in Transit | Transit-field exception requires specific knowledge; does not confer endpoint author authority. |
| 7.1 | Mailing List Header Fields: List-* and Archived-At | List controls may be shown as transit-origin information without implying author signature coverage. |
| 8 | Email Ecosystem Evolution | Migration suggestions are not deployed capabilities or registered negotiation formats. |
| 8.1 | Dropping Legacy Display Elements | Dropping decorations requires recipient support; signal syntax/semantics are not defined here. |
| 8.2 | More Ambitious Default HCP | More private header policies require coordination and delivery evidence; signal remains unspecified. |
| 8.3 | Deprecation of Messages Without Header Protection | Future deprecation suggestions do not justify declaring historical mail insecure solely by age. |
| 9 | Usability Considerations | Usability motivates mechanisms, not an extra wire protocol. |
| 9.1 | Mixed Protections Within a Message Are Hard to Understand | Mixed field/body protections need comprehensible summaries; example UI choices are not mandatory designs. |
| 9.2 | Users Should Not Have to Choose a Header Confidentiality Policy | Implementer chooses a sensible default; ordinary users should not define HCPs. |
| 10 | Security Considerations | Underlying CMS/S/MIME/OpenPGP security considerations remain dependencies. |
| 10.1 | From Address Spoofing | Inner-address spoofing can evade domain-level checks; signature binding is essential. |
| 10.1.1 | From Rendering Reasoning | All malicious-client/transit cases reviewed; outer fallback retains MTA filtering but is not proof of sender identity. |
| 10.2 | Avoid Cryptographic Summary Confusion from the hp Parameter | Never upgrade confidentiality based only on hp or transit-added encryption. |
| 10.3 | Caution About Composing with Legacy Display Elements | Unfold/decode safely, strip newline injection and HTML-escape decoration values. |
| 10.4 | Plaintext Attacks | Known/chosen plaintext must be supported by the actual encryption mechanism. |
| 11 | Privacy Considerations | Header protection does not eliminate disclosure to recipients or metadata observers. |
| 11.1 | Leaks When Replying | Reply leakage governed by Section 6 and stronger proposal provenance tracking. |
| 11.2 | Encrypted Header Fields Are Not Always Private | Encrypted copies do not make exposed or inferable values private. |
| 11.2.1 | Encrypted Header Fields Can Leak Unwanted Information to the | Filter original header audience before encryption; User-Agent, IDs and Bcc can leak to recipients. |
| 11.2.2 | Encrypted Header Fields Can Be Inferred from External or | Mailboxes, recipient cryptographic identifiers and trace fields can reveal hidden addresses. |
| 11.2.3 | Encrypted Header Fields May Not Be Fully Masked by HCP | Partial date/address masking preserves some information; no anonymity claim. |
| 11.3 | A Naive Recipient May Overestimate the Cryptographic Status of a | Use protected exposure records; stripped outer fields do not retrospectively become confidential. |
| 11.4 | Privacy and Deliverability Risks with Bcc and Encrypted Messages | Baseline preserves supplied Bcc; recipient isolation must happen before HCP application. |
| 12 | IANA Considerations | All registration actions read; live registry verification remains open. |
| 12.1 | Registration of the HP-Outer Header Field | HP-Outer permanent mail field registration reviewed. |
| 12.2 | Reference Update for the Content-Type Header Field | Content-Type references extended for both parameters. |
| 12.3 | New Mail Header Confidentiality Policies Registry | Three HCP entries and recommendation-change policies reviewed; names are documentation identifiers. |
| 13 | References | Complete reference list reviewed. |
| 13.1 | Normative References | RFC9787, CMS, algorithm and framework dependencies remain separately scoped work. |
| 13.2 | Informative References | Historical schemes and draft revisions are not current-version endorsements. |
| Appendix A | Table of Pseudocode Listings | Every pseudocode cross-reference checked against the reviewed algorithms. |
| Appendix B | Possible Problems with Legacy MUAs | All list-view, rendering and reply failure cases reviewed as client-test requirements. |
| Appendix C | Test Vectors | All prose, structures and plaintext reviewed; encoded bytes retained and signed layers checked; outer decryption not tested. |
| Appendix D | Composition Examples | All worked steps and interfaces reviewed; edited-subject leak and decorative-list discrepancy explicitly recorded. |
| Appendix E | Rendering Examples | Both single-part suppression examples reviewed; no executable sanitizer claim. |
| Appendix F | Other Header Protection Schemes | All three historical scheme descriptions reviewed; pEp shape alone is not identification and old schemes lack modern exposure records. |

## Resulting proposal choices

The [transport contract](../transport.md) adopts baseline subject confidentiality for the legacy S/MIME composition path. The [rendering contract](../rendering.md) uses protected fields for threading while keeping sender signature validity separate from address binding. The [delivery policy](../delivery-policy.md) preserves inherited confidentiality through edits and derives decorative display content after final exposure decisions.

Those last two composition choices are explicit proposal behavior. Appendix D.2.2 acknowledges that its exact-value ReferenceHCP mapping leaks an edited subject under a no-confidentiality local policy. Appendix D.2.2.1 includes a decoration that Section 5.2.1's earlier local-policy-only calculation would omit. Email/2's reconciliation is not an approved correction to the RFC.

## Remaining source reconciliation

Section 5.2.4 excludes parts not descending through the first child of a multipart/related ancestor, whereas RFC2387 can designate a different related root through start. The [message profile](../messages.md) resolves receiving traversal in favor of RFC2387 selected-root semantics and requires newly composed roots to be first; an executable general traversal remains to be validated. HeaderSetsFromMessage is introduced with an encrypted-message precondition but invoked by a broader protection-status algorithm; input qualification must be explicit. ASCII HP-Outer grammar and unchanged internationalized values also need a precise SMTPUTF8 integration rule. None of these points permits guessing missing authentication.

The source's local-part comparison suggestion is scoped to From display matching and is not adopted as a universal mailbox normalization rule. RFC9787 supplies essential payload, structural-field and UI terminology; its [separate audit](e2e-guidance.md) records the reviewed guidance and departure rationale. That review does not establish implementation conformance. CMS, S/MIME, OpenPGP, PKI, IDNA, registry and historical-scheme dependencies remain separate work.

## Managed conversation mapping

The separately negotiated [protected presentation profile](../managed-presentation.md) protects subject, author-stated date and principal recipient roles inside MLS. Its semantic fields and conversation reply authority differ from RFC9788 protected MIME headers and `HP-Outer`; it does not claim wire compatibility. The legacy composition contract retains this audit’s inherited rules.
