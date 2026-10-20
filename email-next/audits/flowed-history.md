---
title: Historical flowed text audit
sectionNav: true
---

# Historical flowed text audit

The complete base text of [RFC2646](https://www.rfc-editor.org/rfc/rfc2646.html), including syntax, examples, references, acknowledgments and end matter, has been reviewed. No entries for this RFC occur in the captured full errata corpus. This does not establish dependency closure or live registry verification.

| Section | Topic | Disposition |
| --- | --- | --- |
| 1 | Abstract | Historical compatible reflow proposal; RFC3676 replaces this document for current processing. |
| 2 | Conventions Used in this Document | Requirement-keyword conventions reviewed. |
| 3 | The Problem | Fixed text preserves line boundaries; historical line-limit prose is not the current SMTP sizing authority. |
| 3.1 | Paragraph Text | Paragraph display differs from fixed-line layout; do not infer a flowed declaration merely from visual wrapping. |
| 3.2 | Embarrassing Line Wrap | Repeated quoting can corrupt visual attribution; quote depth is display evidence, not authenticated authorship. |
| 3.3 | New Media Types | Readable fallback motivated the parameter; no guarantee that new media types stay invisible in old clients. |
| 4 | The Format Parameter to the Text/Plain Media Type | Format is case-insensitive and defaults to fixed; this is a wire format, not a local storage format. |
| 4.1 | Generating Format=Flowed | Historical generation wraps after existing spaces and preserves them; 79-character advice and optional stuffing are superseded by RFC3676 rules. QP is discouraged except necessity or cryptographic protection. |
| 4.2 | Interpreting Format=Flowed | Quote detection precedes one-space unstuffing; flowed trailing spaces remain content. This version has no DelSp deletion option. |
| 4.3 | Usenet Signature Convention | Optionally quoted signature separator is fixed despite its final space. |
| 4.4 | Space-Stuffing | Remove one stuffing space after quote recognition; literal leading angle brackets must not be reclassified as quote depth afterward. |
| 4.5 | Quoting | Only contiguous initial angle brackets establish depth; depth changes end paragraphs under recommended error recovery. |
| 4.6 | Digital Signatures and Encryption | Cryptography protects the appropriate wire representation before display reflow; historical blanket ordering language does not replace the selected MIME security protocol's encoding boundaries. |
| 4.7 | Line Analysis Table | Four-way quote/flow classification is read together with signature exceptions, not as a standalone parser. |
| 4.8 | Examples | All paragraph and quoted-dialogue examples reviewed; markers in explanatory examples are not literal wire syntax. |
| 5 | ABNF | Historical ASCII grammar is not the current parser authority; RFC3676 corrects and extends the definition, including empty lines and non-ASCII text. |
| 6 | Failure Modes | Transport changes can corrupt reflow metadata. |
| 6.1 | Trailing White Space Corruption | Stripped spaces destroy flow markers; added spaces may join lines wrongly. No authenticated repair can be inferred from layout alone. |
| 7 | Security Considerations | Read with cryptographic processing discussion; no claim that quote reconstruction establishes authenticity. |
| 8 | IANA Considerations | Requests text/plain registration reference; current registry verification remains separate. |
| 9 | Internationalization Considerations | Bidi and charset-sensitive wrapping require care; historical internationalization limits help explain replacement DelSp support. |
| 10 | Acknowledgments | Acknowledgments reviewed. |
| 11 | References | All references reviewed; historical SMTP, ABNF and HTML references are not adopted as current Email Next baselines. |
| 12 | Editor's Address | Editor contact end matter reviewed; no protocol requirements. |
| 13 | Full Copyright Statement | Copyright and closing acknowledgment reviewed; no additional wire semantics. |

## Compatibility decision

RFC3676 obsoletes this standard. Its default DelSp=no preserves the older convention of retaining the space at a soft line break. Receivers must not infer DelSp=yes from a sender's age, language or apparent line length. Current generation uses RFC3676; historical review does not create a separately negotiated parser version.

The older grammar and optional generation guidance must not override current handling of empty lines, non-ASCII text, quote-depth boundaries or signature separators. Preserve the original MIME entity for authentication and display reconstruction. Trailing-space corruption cannot be reliably repaired from visual layout alone.
