---
title: Encoded header text audit
sectionNav: true
---

# Encoded header text audit

Encoded words provide readable internationalized display text over older mail infrastructure. They do not encode mailbox identities. Decoding a name before parsing the address can turn display punctuation into an apparent new recipient or author.

**Coverage:** complete 15-page RFC2047, including examples and appendix, and all seven retrieved errata read and individually assessed on 19 October 2026. RFC2231, RFC6532 and field-specific extensions remain separate review items.

Sources: [RFC2047](https://www.rfc-editor.org/rfc/rfc2047.html), [errata](https://www.rfc-editor.org/errata/rfc2047).

| Section | Disposition |
| --- | --- |
| 1 | Inherit encoded-word compatibility design; display decoding does not translate arbitrary 8bit headers to ASCII. |
| 2 | Inherit syntax, case-insensitive charset/encoding tokens, no whitespace within a word, 75-character word and 76-character containing-line generation limits. Apply verified506 restoring backslash in especials. |
| 3 | Inherit registered charset interpretation and independent return to ASCII for stateful charsets per word. Historical ISO-8859 preference is not adopted as the new-profile generation preference; UTF-8 generation awaits the internationalized-header profile. |
| 4 | Inherit support for both Q and B for supported charsets; context restrictions remain applicable. |
| 4.1 | B uses MIME base64, with each encoded word independently complete. |
| 4.2 | Q differs from body quoted-printable: underscore denotes octet20, literal underscore must be encoded, and raw space/tab are prohibited. Hex escapes and context-specific safe characters remain distinct. |
| 5 | Inherit allowed display-text, phrase and comment positions; prohibit use in addr-spec, quoted strings, Received, or MIME parameters absent a field-specific extension. Apply verified504. Whole octets and characters cannot span encoded words. Display controls cannot execute. |
| 6 | Reader requirements reviewed with all subsections. |
| 6.1 | Parse field grammar before recognizing encoded words in allowed positions. MIME-Version is not required. Do not scan every header indiscriminately. |
| 6.2 | Decode after tokenization; never reparse decoded punctuation as address syntax. Ignore separating whitespace only between adjacent encoded words. Unknown encoding/charset has a safe display fallback, not identity inference. |
| 6.3 | Malformed encoded words do not prevent reading or handling the message. Recovery remains presentation-only and is not authenticated source data. |
| 7 | Inherit generator validity and reader Q/B recognition requirements; distinguish compliance from merely accepting a sample. |
| 8 | All examples reviewed, including comment versus unstructured text and adjacent-word whitespace. Samples are not cryptographic canonicalization vectors. |
| 9 | References reviewed; RFC2231 extension and current header grammar remain separate dependencies. |
| 10 | Source explicitly does not discuss security. Proposed parse-before-decode and identity separation address risks visible in the source behavior; they are not attributed to this section. |
| 11 | Acknowledgements reviewed; no protocol behavior. |
| 12 | Contact information reviewed; no protocol behavior. |
| Appendix | All historical changes reviewed, including no encoded words in quoted strings and no assumed reversible conversion to raw headers. |

## Errata

| Record | Status | Disposition |
| --- | --- | --- |
| [504](https://www.rfc-editor.org/errata/eid504) | Verified | Restore missing backslash restriction and sentence in comment Q encoding. |
| [506](https://www.rfc-editor.org/errata/eid506) | Verified | Restore backslash in especials syntax. |
| [2823](https://www.rfc-editor.org/errata/eid2823) | Held | Example introduction grammar only. |
| [3749](https://www.rfc-editor.org/errata/eid3749) | Rejected | Existing §6.2 already covers adjacent encoded-word whitespace; do not adopt a new rule. |
| [4913](https://www.rfc-editor.org/errata/eid4913) | Held | Correct terminology typo to linear-white-space; behavior unchanged. |
| [5469](https://www.rfc-editor.org/errata/eid5469) | Held | Phrase restriction wording concerns encoded-text, with equals followed by hex digits. Record clarification without promoting the held record to a normative update; base encoding rules already constrain equals. |
| [5692](https://www.rfc-editor.org/errata/eid5692) | Held | Appendix spelling correction only. |

## Consequences and acceptance cases

Maintain parsed mailbox syntax, decoded display labels and original bytes separately. A display label containing an encoded comma, colon, angle bracket or address-looking string must never add a mailbox, change an audience, supply a key identifier or become a trusted reply destination.

Recognition depends on the field and position. Identical characters inside a Subject and inside a structured comment can require different display behavior. MIME parameters use their own encoding rules; a permissive filename recovery does not redefine the header grammar.

RFC2557 defines special Content-Location header encoding behavior. That field-specific contract must be implemented deliberately and must not become universal header decoding. The audit of RFC2231 will cover parameter continuations and language tags.

Required fixtures include encoded punctuation in a display name, invalid encoding with readable message retained, adjacent words with ignored separating whitespace, an underscore in Q versus body quoted-printable, a multibyte character illegally split across words, unknown charset fallback, and encoded-word-shaped text inside an addr-spec that is never decoded into a different mailbox. These are proposed cases; no implementation result is claimed.
