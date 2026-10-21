---
title: Historical MIME parameter audit
sectionNav: true
---

# Historical MIME parameter audit

The complete base text of [RFC2184](https://www.rfc-editor.org/rfc/rfc2184.html), including grammar, examples, references and end matter, has been reviewed. The captured corpus contains three verified errata, all reviewed below. RFC2231 obsoletes this document and remains the current authority; see the [MIME parameter audit](mime-parameters.md). Dependency closure remains separate work.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Abstract | Introduces parameter charset, language and continuation support; superseded by RFC2231 for current use. |
| 2 | Introduction | RFC2047 encoded words are not a parameter-value encoding; display language and charset are distinct metadata. |
| 2.1 | Requirements notation | Requirement-keyword conventions reviewed. |
| 3 | Parameter Value Continuations | Continuation indexes begin at zero without gaps or leading zeroes; reconstruct by index rather than header order, removing syntactic quoting. |
| 4 | Parameter Value Character Set and Language Information | Star suffix selects extended syntax, apostrophes delimit charset/language, percent escapes represent octets; empty metadata is not an assigned default. |
| 4.1 | Combining Character Set, Language, and Parameter Continuations | Mixed encoded/unencoded continuation segments are allowed; only the first supplies charset/language. Verified erratum2808 corrects example indexes to zero-based. |
| 5 | Language specification in Encoded Words | Language follows charset with an asterisk in encoded words; display labels do not change mailbox identity. |
| 6 | IMAP4 Handling of Parameter Values | Historical IMAP BODY/BODYSTRUCTURE continuation decoding advice is not a substitute for authenticating original MIME headers. |
| 7 | Modifications to MIME ABNF | Verified errata484 and841 restore the encoding component and zero-based continuation grammar. Current parsing uses RFC2231 rather than known-defective historical grammar. |
| 8 | Character sets which allow specification of language | Discussion anticipates inline language labels; it does not select a new Email/2 charset or identity normalization scheme. |
| 9 | Security Considerations | Historical lack of new security considerations does not justify using filenames as paths or treating decoded metadata as authenticated identity. |
| 10 | References | All references reviewed; old IMAP, language-tag, registration and message-format citations are not current profile selections. |
| 11 | Authors' Addresses | Author end matter reviewed; no additional protocol requirements. |

## Errata and compatibility

- Verified [erratum2808](https://www.rfc-editor.org/errata/eid2808) changes the example's continuation indexes from 1/2/3 to 0/1/2.
- Verified [erratum484](https://www.rfc-editor.org/errata/eid484) restores the encoding field and its delimiter in the extended encoded-word grammar.
- Verified [erratum841](https://www.rfc-editor.org/errata/eid841) corrects the initial continuation index and subsequent index range. Its corrected text still carries an unmatched closing parenthesis; use the replacement specification's grammar rather than copying that transcription as executable syntax.

The original Section 7 also refers to extended-value where its definition is named extended-initial-value. This review records the source inconsistency without claiming an additional approved erratum. Historical discrepancies do not create permission to guess missing segments or reinterpret an ambiguous security-bearing parameter. Receivers may present a conservative fallback label, retaining the original header and diagnostic; they must not use a guessed filename or charset to authorize an operation.
